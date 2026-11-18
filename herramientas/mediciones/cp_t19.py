"""CP-T19: aceptar frente a cancelar o rechazar la misma solicitud a la vez. Solo biblioteca estándar.

Qué mide. Diego le solicita S/ 25.00 a Bruno (la misma solicitud de CP-T17). En cada ronda salen a la vez,
sincronizadas con threading.Barrier, dos peticiones sobre esa solicitud:
  - modo cancelar: Bruno la acepta y Diego, el solicitante, la cancela;
  - modo rechazar: Bruno la acepta y Bruno la rechaza.
Las tres operaciones exigen que la solicitud esté PENDIENTE (HU-G4-08 CA4, HU-G4-09 CA1 y HU-G4-10 CA1), así que
solo una de las dos puede ganar. Una ronda es correcta en dos casos:
  - aceptar responde 200, la otra 409 ESTADO_INVALIDO, la solicitud queda ACEPTADA y el dinero se movió una vez
    (Bruno S/ 775.00, Diego S/ 2,525.00);
  - la otra responde 200, aceptar 409 ESTADO_INVALIDO, la solicitud queda CANCELADA o RECHAZADA y no se movió
    dinero (Bruno S/ 800.00, Diego S/ 2,500.00).
Cualquier otra combinación es incorrecta, y la salida dice cuál fue. Junto a cada 200 se imprime el estado que
trae el cuerpo de la respuesta, que es lo que la aplicación le dijo a ese usuario.

Por qué así.
- Cada ronda empieza con el reloj real y POST /api/pruebas/reiniciar, como el fixture `s` de tests/api/conftest.py:
  una ronda no hereda saldos ni solicitudes de la anterior.
- Cada hilo abre su propia conexión y la calienta con GET /api/salud antes de la barrera, como `_a_la_vez` en
  tests/api/pasos_g4_extra.py, el ayudante de CP-T17: así el saludo TCP no separa las dos peticiones. Por eso la
  ráfaga usa http.client (la capa sobre la que está urllib.request), que deja la conexión abierta; urllib.request
  abre y cierra una conexión por petición, y queda para la preparación.
- Además del estado y los saldos se cuentan los SMS que recibe Diego, porque son lo que vería el solicitante.

Uso, con Qolqe levantado en modo prueba (QOLQE_MODO_PRUEBA=1). Reinicia los datos en cada ronda: no se corre
contra la base de la demo.
  python herramientas/mediciones/cp_t19.py --url http://127.0.0.1:8765 --rondas 40
  python herramientas/mediciones/cp_t19.py --rondas 5 --detalle     # además, una línea por ronda
Sale con 0 si todas las rondas fueron correctas y con 1 si alguna no lo fue.
"""

from __future__ import annotations

import argparse
import http.client
import json
import platform
import statistics
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime
from urllib.parse import urlsplit

# Usuarios de la semilla (qolqe/semilla.py, USUARIOS_BASE): celular, PIN y saldo inicial.
BRUNO = ("912345678", "7391")
DIEGO = ("998877665", "3604")
MONTO = "25.00"
SALDOS_SIN_PAGO = ("800.00", "2500.00")  # (Bruno, Diego) si nadie movió dinero
SALDOS_CON_PAGO = ("775.00", "2525.00")  # (Bruno, Diego) si la solicitud se pagó una vez
ESTADO_FINAL = {"cancelar": "CANCELADA", "rechazar": "RECHAZADA"}
QUIEN = {"cancelar": "Diego cancela", "rechazar": "Bruno rechaza"}


def pedir(url, metodo, ruta, token=None, cuerpo=None):
    """Petición simple con urllib.request. Devuelve (estado HTTP, cuerpo JSON)."""
    datos = None if cuerpo is None else json.dumps(cuerpo).encode()
    cabeceras = {} if datos is None else {"Content-Type": "application/json"}
    if token:
        cabeceras["Authorization"] = f"Bearer {token}"
    peticion = urllib.request.Request(url + ruta, data=datos, method=metodo, headers=cabeceras)
    try:
        with urllib.request.urlopen(peticion, timeout=30) as respuesta:
            return respuesta.status, json.loads(respuesta.read() or b"null")
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read() or b"null")


def exigir(condicion, mensaje):
    if not condicion:
        raise RuntimeError(f"Precondición no cumplida: {mensaje}")


def ingresar(url, usuario):
    estado, cuerpo = pedir(url, "POST", "/api/auth/login", cuerpo={"celular": usuario[0], "pin": usuario[1]})
    exigir(estado == 200, f"ingreso de {usuario[0]} respondió {estado}")
    return cuerpo["access_token"]


def saldo(url, token):
    estado, cuerpo = pedir(url, "GET", "/api/cuentas/me/saldo", token)
    exigir(estado == 200, f"saldo respondió {estado}")
    return cuerpo["saldo"]


def sms_a_diego(url):
    estado, cuerpo = pedir(url, "GET", f"/api/pruebas/notificaciones?celular={DIEGO[0]}")
    exigir(estado == 200, f"notificaciones respondió {estado}")
    mensajes = [n["mensaje"] for n in cuerpo]
    return (sum("aceptó tu solicitud" in m for m in mensajes), sum("rechazó tu solicitud" in m for m in mensajes))


def preparar(url):
    """Datos semilla, sesiones nuevas y una solicitud PENDIENTE de S/ 25.00 de Diego a Bruno."""
    exigir(pedir(url, "DELETE", "/api/pruebas/reloj")[0] == 200, "no se pudo volver al reloj real")
    exigir(pedir(url, "POST", "/api/pruebas/reiniciar")[0] == 200, "no se pudieron reiniciar los datos")
    bruno, diego = ingresar(url, BRUNO), ingresar(url, DIEGO)

    contacto_id, pagina = None, 1
    while contacto_id is None:
        estado, datos = pedir(url, "GET", f"/api/contactos?pagina={pagina}", diego)
        exigir(estado == 200, f"contactos de Diego respondió {estado}")
        contacto_id = next((c["id"] for c in datos["contactos"] if c["celular"] == BRUNO[0]), None)
        if pagina >= datos["total_paginas"]:
            break
        pagina += 1
    if contacto_id is None:
        estado, datos = pedir(url, "POST", "/api/contactos", diego, {"celular": BRUNO[0], "alias": "Bruno"})
        exigir(estado == 201, f"alta del contacto Bruno respondió {estado}")
        contacto_id = datos["id"]

    estado, datos = pedir(url, "POST", "/api/solicitudes", diego,
                          {"contacto_id": contacto_id, "monto": MONTO, "motivo": "Medicion CP-T19"})
    exigir(estado == 201, f"crear la solicitud respondió {estado}")
    exigir((saldo(url, bruno), saldo(url, diego)) == SALDOS_SIN_PAGO, "los saldos iniciales no son los de la semilla")
    return bruno, diego, datos["id"]


def a_la_vez(url, peticiones):
    """Envía las peticiones a la vez, un hilo y una conexión por petición, sincronizados con una barrera."""
    partes = urlsplit(url)
    barrera = threading.Barrier(len(peticiones))
    resultados = [None] * len(peticiones)

    def enviar(i, metodo, ruta, token, cuerpo):
        conexion = http.client.HTTPConnection(partes.hostname, partes.port, timeout=30)
        try:
            conexion.request("GET", "/api/salud")
            conexion.getresponse().read()
            cabeceras = {"Authorization": f"Bearer {token}"}
            datos = None
            if cuerpo is not None:
                datos = json.dumps(cuerpo).encode()
                cabeceras["Content-Type"] = "application/json"
            barrera.wait(timeout=30)
            salida = time.perf_counter()
            conexion.request(metodo, ruta, body=datos, headers=cabeceras)
            respuesta = conexion.getresponse()
            cuerpo_respuesta = json.loads(respuesta.read() or b"null")
            llegada = time.perf_counter()
            campos = cuerpo_respuesta if isinstance(cuerpo_respuesta, dict) else {}
            # Un 200 devuelve la solicitud: su estado es lo que se le dijo al usuario. Un error trae su código.
            resultados[i] = {"estado": respuesta.status, "codigo": campos.get("codigo"), "solicitud": campos.get("estado"),
                             "salida": salida, "ms": (llegada - salida) * 1000}
        except (OSError, http.client.HTTPException, ValueError, threading.BrokenBarrierError) as error:
            # Red, HTTP, JSON o barrera rota: el hilo no debe morir en silencio, se informa abajo.
            resultados[i] = {"error": repr(error)}
        finally:
            conexion.close()

    hilos = [threading.Thread(target=enviar, args=(i, *p)) for i, p in enumerate(peticiones)]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()
    for resultado in resultados:
        exigir(resultado is not None and "error" not in resultado, f"un hilo no recibió respuesta: {resultado}")
    return resultados


def respuesta_texto(r):
    return f"{r['estado']} {r['solicitud']}" if r["estado"] == 200 else f"{r['estado']} {r['codigo']}"


def ronda(url, modo):
    bruno, diego, solicitud_id = preparar(url)
    sms_antes = sms_a_diego(url)
    otra = ("POST", f"/api/solicitudes/{solicitud_id}/cancelar", diego, None) if modo == "cancelar" else \
           ("POST", f"/api/solicitudes/{solicitud_id}/rechazar", bruno, {"motivo": "Medicion CP-T19"})
    aceptar, contraria = a_la_vez(url, [("POST", f"/api/solicitudes/{solicitud_id}/aceptar", bruno, None), otra])

    estado, datos = pedir(url, "GET", "/api/solicitudes", bruno)
    exigir(estado == 200, f"listar solicitudes respondió {estado}")
    final = next(s["estado"] for s in datos["recibidas"] if s["id"] == solicitud_id)
    saldos = (saldo(url, bruno), saldo(url, diego))
    sms_despues = sms_a_diego(url)
    sms = (sms_despues[0] - sms_antes[0], sms_despues[1] - sms_antes[1])

    gana_aceptar = (aceptar["estado"] == 200 and (contraria["estado"], contraria["codigo"]) == (409, "ESTADO_INVALIDO")
                    and final == "ACEPTADA" and saldos == SALDOS_CON_PAGO)
    gana_otra = (contraria["estado"] == 200 and (aceptar["estado"], aceptar["codigo"]) == (409, "ESTADO_INVALIDO")
                 and final == ESTADO_FINAL[modo] and saldos == SALDOS_SIN_PAGO)
    veredicto = "correcta, gana aceptar" if gana_aceptar else f"correcta, gana {modo}" if gana_otra else "INCORRECTA"
    combinacion = (f"aceptar {respuesta_texto(aceptar)} · {modo} {respuesta_texto(contraria)} · estado {final} · "
                   f"Bruno {saldos[0]} · Diego {saldos[1]} · SMS a Diego: {sms[0]} «aceptó», {sms[1]} «rechazó»")
    return {"veredicto": veredicto, "combinacion": combinacion, "ms_aceptar": aceptar["ms"], "ms_otra": contraria["ms"],
            "desfase": abs(aceptar["salida"] - contraria["salida"]) * 1000}


def medir(url, modo, rondas, detalle):
    print(f"\nModo {modo}: Bruno acepta y {QUIEN[modo]} la misma solicitud, {rondas} rondas")
    filas = []
    for n in range(1, rondas + 1):
        fila = ronda(url, modo)
        filas.append(fila)
        if detalle:
            print(f"  ronda {n:02d} · {fila['combinacion']} · {fila['ms_aceptar']:.1f} ms / {fila['ms_otra']:.1f} ms"
                  f" · desfase {fila['desfase']:.2f} ms → {fila['veredicto']}")
    veredictos = Counter(f["veredicto"] for f in filas)
    correctas = veredictos["correcta, gana aceptar"] + veredictos[f"correcta, gana {modo}"]
    print(f"  correctas: {correctas} de {rondas} (gana aceptar {veredictos['correcta, gana aceptar']}, "
          f"gana {modo} {veredictos[f'correcta, gana {modo}']}) · incorrectas: {veredictos['INCORRECTA']}")
    print("  combinaciones observadas:")
    for combinacion, veces in Counter(f["combinacion"] for f in filas).most_common():
        print(f"    {veces:>3} × {combinacion}")
    print(f"  duración mediana: aceptar {statistics.median(f['ms_aceptar'] for f in filas):.1f} ms · "
          f"{modo} {statistics.median(f['ms_otra'] for f in filas):.1f} ms · desfase de salida máximo "
          f"{max(f['desfase'] for f in filas):.2f} ms")
    return veredictos["INCORRECTA"]


def main():
    argumentos = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argumentos.add_argument("--url", default="http://127.0.0.1:8765", help="Qolqe en modo prueba")
    argumentos.add_argument("--rondas", type=int, default=40, help="rondas por modo")
    argumentos.add_argument("--modo", choices=["cancelar", "rechazar", "ambos"], default="ambos")
    argumentos.add_argument("--detalle", action="store_true", help="una línea por ronda")
    opciones = argumentos.parse_args()

    try:
        estado, salud = pedir(opciones.url, "GET", "/api/salud")
    except urllib.error.URLError:  # Nada escucha en esa URL: se informa con el mismo mensaje.
        estado, salud = None, {}
    exigir(estado == 200 and salud.get("modo_prueba"), f"Qolqe no responde en {opciones.url} o no está en modo prueba")
    inicio = time.perf_counter()
    print(f"CP-T19 · {datetime.now():%Y-%m-%d %H:%M:%S} · {opciones.url} · Qolqe {salud['version']} · "
          f"Python {platform.python_version()} · {platform.system()} {platform.machine()}")
    modos = ["cancelar", "rechazar"] if opciones.modo == "ambos" else [opciones.modo]
    incorrectas = sum(medir(opciones.url, modo, opciones.rondas, opciones.detalle) for modo in modos)
    print(f"\nTotal: {incorrectas} rondas incorrectas de {opciones.rondas * len(modos)} · "
          f"{time.perf_counter() - inicio:.1f} s")
    return 1 if incorrectas else 0


if __name__ == "__main__":
    sys.exit(main())
