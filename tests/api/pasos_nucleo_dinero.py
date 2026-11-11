"""Pasos de pytest-bdd del núcleo: cierre de cuenta, transferencias y comisión (HU-N-06 a HU-N-09)."""
import json
import re
import threading
import time
from datetime import datetime, timedelta
from decimal import Decimal

import conftest  # Helpers compartidos: URL, USUARIOS, Sesiones.
import httpx
import jwt
from pytest_bdd import given, parsers, then, when

CCI_PRUEBA = "00219300123456789012"
PIN_CARGA = "2580"  # Usuarios de carga de la semilla: celulares 900000001 a 900000200.
CERRADAS = {"Fabián": ("934567812", "6029")}  # Cuenta CERRADA de la semilla.
RESOLVER = {"RECHAZADA": "rechazar", "CANCELADA": "cancelar", "ACEPTADA": "aceptar"}
MONTOS = r"(?P<montos>\d+\.\d\d(?:, \d+\.\d\d)*)"
DESTINO = r'(?P<destino>"[^"]*"|su contacto "[^"]*"(?: indicando también el celular "[^"]*")?|[^\s"]+)'


# ---------- Helpers ----------

def _celular(quien):
    """Nombre de la semilla o, para los usuarios de carga, su propio celular."""
    if quien in conftest.USUARIOS:
        return conftest.USUARIOS[quien][0]
    return CERRADAS.get(quien, (quien,))[0]


def _pin(quien):
    if quien in conftest.USUARIOS:
        return conftest.USUARIOS[quien][1]
    return CERRADAS.get(quien, (None, PIN_CARGA))[1]


def _ingresar(s, quien):
    r = s.cliente.post("/api/auth/login", json={"celular": _celular(quien), "pin": _pin(quien)})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _token(s, quien):
    if quien not in s.tokens:
        s.tokens[quien] = _ingresar(s, quien)
    return s.tokens[quien]


def _pedir(s, metodo, ruta, quien, **opciones):
    s.respuesta = s.cliente.request(metodo, ruta, headers=_token(s, quien), **opciones)
    return s.respuesta


def _comprobantes(s):
    return vars(s).setdefault("comprobantes", [])


def _transferir(s, emisor, cuerpo):
    r = _pedir(s, "POST", "/api/transferencias", emisor, json=cuerpo)
    if r.status_code == 201:
        _comprobantes(s).append(r.json())
        s.emisor = emisor
    return r


def _contacto_id(s, alias, quien):
    pagina = 1
    while True:
        datos = s.cliente.get("/api/contactos", headers=_token(s, quien), params={"pagina": pagina}).json()
        for c in datos["contactos"]:
            if c["alias"] == alias:
                return c["id"]
        assert pagina < datos["total_paginas"], f"{quien} no tiene el contacto {alias}"
        pagina += 1


def _destino_qolqe(s, emisor, destino):
    if m := re.fullmatch(r'su contacto "([^"]*)"(?: indicando también el celular "([^"]*)")?', destino):
        cuerpo = {"contacto_id": _contacto_id(s, m[1], emisor)}
        if m[2] is not None:
            cuerpo["celular_destino"] = m[2]
        return cuerpo
    if destino.startswith('"'):
        return {"celular_destino": destino.strip('"')}
    return {"celular_destino": _celular(destino)}


def _saldo(s, quien):
    return Decimal(s.cliente.get("/api/cuentas/me/saldo", headers=_token(s, quien)).json()["saldo"])


def _ultimo_movimiento(s, quien):
    r = s.cliente.get("/api/movimientos/recientes", headers=_token(s, quien), params={"limite": 1})
    assert r.status_code == 200, r.text
    return r.json()[0]


def _fijar_reloj(s, momento):
    r = s.cliente.put("/api/pruebas/reloj", json={"ahora": momento})
    assert r.status_code == 200, r.text


def _hoy(s):
    """Fecha de Qolqe al empezar el escenario (el fixture deja el reloj en la hora real)."""
    if "hoy_qolqe" not in vars(s):
        s.hoy_qolqe = datetime.fromisoformat(s.cliente.get("/api/pruebas/reloj").json()["ahora"]).date()
    return s.hoy_qolqe


def _credencial(s, credencial):
    """Cabeceras para los casos de autenticación."""
    if credencial == "ningún token":
        return {}
    if credencial == "un token inválido":
        return {"Authorization": "Bearer abc"}
    if credencial == "el esquema Basic":
        return {"Authorization": "Basic YW5hOjQ4MjY="}
    if credencial == "un token firmado con otra clave":
        contenido = {"sub": "1", "jti": "falso", "exp": int(time.time()) + 600}
        return {"Authorization": f"Bearer {jwt.encode(contenido, 'otra-clave-de-32-caracteres-o-mas!', 'HS256')}"}
    if m := re.fullmatch(r"el token vencido de (\S+)", credencial):
        cabeceras = _ingresar(s, m[1])
        assert s.cliente.put("/api/pruebas/reloj", json={"avanzar_minutos": 30}).status_code == 200
        s.tokens.clear()  # Todos los tokens vencieron: los pasos siguientes vuelven a ingresar.
        return cabeceras
    m = re.fullmatch(r"el token de (\S+)", credencial)
    assert m, f"Credencial desconocida: {credencial}"
    return _token(s, m[1])


def _cuerpo(texto):
    if texto is None or texto == "(ninguno)":
        return {}
    if texto == "(JSON malformado)":
        return {"content": b"{malo", "headers": {"Content-Type": "application/json"}}
    return {"json": json.loads(texto)}


def _simultaneas(s, pedidos):
    """Envía los POST a la vez: un cliente por hilo, con la conexión abierta antes de la barrera."""
    barrera = threading.Barrier(len(pedidos))
    respuestas = [None] * len(pedidos)

    def enviar(i, cabeceras, cuerpo):
        with httpx.Client(base_url=conftest.URL, timeout=30) as cliente:
            cliente.get("/api/salud")
            barrera.wait(timeout=30)
            respuestas[i] = cliente.post("/api/transferencias", headers=cabeceras, json=cuerpo)

    hilos = [threading.Thread(target=enviar, args=(i, *pedido)) for i, pedido in enumerate(pedidos)]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()
    assert all(respuestas), "Algún hilo no recibió respuesta"
    s.simultaneas = respuestas


def _estado_cuenta(s, quien):
    cabeceras = _token(s, quien)
    return {
        "saldo": s.cliente.get("/api/cuentas/me/saldo", headers=cabeceras).json(),
        "movimientos": s.cliente.get("/api/movimientos/recientes", headers=cabeceras, params={"limite": 20}).json(),
        "usado_hoy": s.cliente.get("/api/limites", headers=cabeceras).json()["usado_hoy"],
        "sms": s.cliente.get("/api/pruebas/notificaciones", params={"celular": _celular(quien)}).json(),
    }


# ---------- Dado ----------

@given(parsers.re(r'(?:que )?el saldo de (?P<quien>\S+) se ajusta a "(?P<saldo>[^"]*)"'))
def ajusta_saldo(s, quien, saldo):
    r = s.cliente.put("/api/pruebas/saldo", json={"celular": _celular(quien), "saldo": saldo})
    assert r.status_code == 200, r.text


@given(parsers.re(r"(?:que )?(?P<quien>\S+) ya cerró su cuenta con su PIN"))
def ya_cerro(s, quien):
    r = _pedir(s, "POST", "/api/cuentas/me/cierre", quien, json={"pin": _pin(quien)})
    assert r.status_code == 204, r.text


@given(parsers.re(r"(?P<quien>\S+) abrió una segunda sesión"))
def segunda_sesion(s, quien):
    _token(s, quien)
    s.segunda_sesion = _ingresar(s, quien)


@given(parsers.re(r"(?P<quien>Ana|Bruno|Carla|Diego) (?P<tiene>tiene|no tiene) solicitudes pendientes"))
def pendientes_segun_tabla(s, quien, tiene):
    """Deja al usuario con o sin solicitudes pendientes (enviadas o recibidas), según la columna de la tabla."""
    cabeceras = _token(s, quien)
    datos = s.cliente.get("/api/solicitudes", headers=cabeceras, params={"estado": "PENDIENTE"}).json()
    if tiene == "tiene" and not datos["enviadas"] + datos["recibidas"]:
        otro = "Ana" if quien != "Ana" else "Bruno"
        registro_solicitud(s, otro, "1.00", quien)
    elif tiene == "no tiene":
        for accion, lista in (("cancelar", datos["enviadas"]), ("rechazar", datos["recibidas"])):
            for solicitud in lista:
                r = s.cliente.post(f"/api/solicitudes/{solicitud['id']}/{accion}", headers=cabeceras)
                assert r.status_code == 200, r.text
    datos = s.cliente.get("/api/solicitudes", headers=cabeceras, params={"estado": "PENDIENTE"}).json()
    assert bool(datos["enviadas"] + datos["recibidas"]) == (tiene == "tiene"), datos


@given(parsers.re(r'el límite diario de (?P<quien>\S+) es "(?P<limite>\d+\.\d\d)"'))
def limite_diario_es(s, quien, limite):
    r = s.cliente.get("/api/limites", headers=_token(s, quien))
    assert r.status_code == 200, r.text
    assert r.json()["limite_diario"] == limite, r.text


@given(parsers.re(r"(?:que )?(?P<solicitante>\S+) registró una solicitud pendiente de (?P<monto>\S+) para (?P<destinatario>\S+)"))
def registro_solicitud(s, solicitante, monto, destinatario):
    celular = _celular(destinatario)
    cabeceras = _token(s, solicitante)
    contactos = s.cliente.get("/api/contactos", headers=cabeceras).json()["contactos"]
    contacto = next((c for c in contactos if c["celular"] == celular), None)
    if contacto is None:
        contacto = s.cliente.post("/api/contactos", headers=cabeceras, json={"celular": celular, "alias": f"Contacto {celular}"}).json()
    r = s.cliente.post("/api/solicitudes", headers=cabeceras,
                       json={"contacto_id": contacto["id"], "monto": monto, "motivo": "Prueba de cierre"})
    assert r.status_code == 201, r.text
    s.solicitud = r.json()
    s.solicitud_id = s.solicitud["id"]


@given(parsers.re(r'(?P<quien>\S+) resuelve la solicitud como "(?P<estado>RECHAZADA|CANCELADA|ACEPTADA)"'))
def resuelve_solicitud(s, quien, estado):
    r = _pedir(s, "POST", f"/api/solicitudes/{s.solicitud_id}/{RESOLVER[estado]}", quien, json={})
    assert r.status_code == 200, r.text
    assert r.json()["estado"] == estado


@given(parsers.re(r"el reloj se ubica (?P<horas>\d+):(?P<minutos>\d\d):(?P<segundos>\d\d) después de creada la solicitud"))
def reloj_tras_solicitud(s, horas, minutos, segundos):
    plazo = timedelta(hours=int(horas), minutes=int(minutos), seconds=int(segundos))
    _fijar_reloj(s, (datetime.fromisoformat(s.solicitud["creada_en"]) + plazo).isoformat())
    s.tokens.clear()


@given(parsers.re(r'la única solicitud de (?P<quien>\S+) figura como "(?P<estado>[A-Z]+)"'))
def unica_solicitud(s, quien, estado):
    datos = s.cliente.get("/api/solicitudes", headers=_token(s, quien)).json()
    assert [x["estado"] for x in datos["enviadas"] + datos["recibidas"]] == [estado], datos


@given(parsers.re(r'(?:que )?el reloj de Qolqe marca (?P<dia>hoy|mañana) a las "(?P<hora>\d\d:\d\d:\d\d)"'))
def reloj_marca(s, dia, hora):
    fecha = _hoy(s) + timedelta(days=1 if dia == "mañana" else 0)
    _fijar_reloj(s, f"{fecha.isoformat()}T{hora}")
    s.tokens.clear()


@given(parsers.re(r"el reloj de Qolqe avanza (?P<minutos>\d+) minutos"))
def reloj_avanza(s, minutos):
    assert s.cliente.put("/api/pruebas/reloj", json={"avanzar_minutos": int(minutos)}).status_code == 200
    s.tokens.clear()


@given("el reloj de Qolqe vuelve al segundo de la última transferencia")
def reloj_vuelve(s):
    # Retroceder menos de un segundo no vence los tokens.
    _fijar_reloj(s, _comprobantes(s)[-1]["fecha"])


@given(parsers.re(rf"(?P<emisor>\S+) ya hizo transferencias Qolqe a {DESTINO} de {MONTOS}"))
def ya_hizo_qolqe(s, emisor, destino, montos):
    for monto in montos.split(", "):
        r = _transferir(s, emisor, {"tipo": "QOLQE", "monto": monto, **_destino_qolqe(s, emisor, destino)})
        assert r.status_code == 201, r.text


@given(parsers.re(rf"(?P<emisor>\S+) ya hizo transferencias interbancarias de {MONTOS}"))
def ya_hizo_interbancarias(s, emisor, montos):
    for monto in montos.split(", "):
        r = _transferir(s, emisor, {"tipo": "INTERBANCARIA", "monto": monto, "cci": CCI_PRUEBA})
        assert r.status_code == 201, r.text


@given(parsers.re(r'(?P<quien>\S+) (?P<accion>redujo|pidió subir) su límite diario a "(?P<limite>\d+)"'))
def cambia_limite(s, quien, accion, limite):
    r = _pedir(s, "PUT", "/api/limites", quien, json={"limite_diario": limite})
    assert r.status_code == 200, r.text
    assert r.json()["aplicacion"] == ("INMEDIATA" if accion == "redujo" else "PROGRAMADA")


@given(parsers.re(r'se registró la cuenta "(?P<nombres>[^"]+)" con el celular "(?P<celular>\d+)"'))
def registro_cuenta(s, nombres, celular):
    r = s.cliente.post("/api/usuarios", json={"dni": "11223344", "nombres": nombres, "celular": celular, "pin": "4826"})
    assert r.status_code == 201, r.text


@given(parsers.re(r"(?:que )?se anotan el saldo, los movimientos, el límite usado y los SMS de (?P<quien>\S+)"))
def anota_estado(s, quien):
    s.estado_anotado = _estado_cuenta(s, quien)


# ---------- Cuando ----------

@when(parsers.re(rf'(?P<emisor>\S+) hace una transferencia Qolqe de (?P<monto>\S+) a {DESTINO}'
                 r'(?: con la descripción "(?P<descripcion>[^"]*)")?'))
def transferencia_qolqe(s, emisor, monto, destino, descripcion):
    cuerpo = {"tipo": "QOLQE", "monto": monto, **_destino_qolqe(s, emisor, destino)}
    if descripcion is not None:
        cuerpo["descripcion"] = descripcion
    _transferir(s, emisor, cuerpo)


@when(parsers.re(rf'(?P<emisor>\S+) hace una transferencia Qolqe de (?P<monto>\S+) a {DESTINO} '
                 r'con una descripción de (?P<largo>\d+) caracteres "(?P<caracter>.)"'))
def transferencia_con_largo(s, emisor, monto, destino, largo, caracter):
    s.descripcion_enviada = caracter * int(largo)
    _transferir(s, emisor, {"tipo": "QOLQE", "monto": monto, "descripcion": s.descripcion_enviada,
                            **_destino_qolqe(s, emisor, destino)})


@when(parsers.re(r'(?P<emisor>\S+) hace una transferencia Qolqe de (?P<monto>\S+) con el contacto "(?P<alias>[^"]+)" de (?P<dueno>\S+)'))
def transferencia_contacto_ajeno(s, emisor, monto, alias, dueno):
    _transferir(s, emisor, {"tipo": "QOLQE", "monto": monto, "contacto_id": _contacto_id(s, alias, dueno)})


@when(parsers.re(r'(?P<emisor>\S+) hace una transferencia interbancaria de (?P<monto>\S+) al CCI "(?P<cci>[^"]*)"'
                 r'(?: con la descripción "(?P<descripcion>[^"]*)")?'))
def transferencia_interbancaria(s, emisor, monto, cci, descripcion):
    cuerpo = {"tipo": "INTERBANCARIA", "monto": monto, "cci": cci}
    if descripcion is not None:
        cuerpo["descripcion"] = descripcion
    _transferir(s, emisor, cuerpo)


@when(parsers.re(r'llega un pedido (?P<metodo>[A-Z]+) a "(?P<ruta>[^"]*)" con (?P<credencial>.+?)(?: y el cuerpo (?P<cuerpo>.+))?'))
def llega_pedido(s, metodo, ruta, credencial, cuerpo):
    opciones = _cuerpo(cuerpo)
    cabeceras = {**_credencial(s, credencial), **opciones.pop("headers", {})}
    s.respuesta = s.cliente.request(metodo, ruta, headers=cabeceras, **opciones)
    if ruta == "/api/transferencias" and s.respuesta.status_code == 201:
        _comprobantes(s).append(s.respuesta.json())


@when(parsers.re(r'(?P<quien>\S+) pide cerrar su cuenta con el PIN "(?P<pin>[^"]*)"(?: (?P<veces>\d+) veces)?'))
def pide_cierre(s, quien, pin, veces):
    s.respuestas_cierre = [_pedir(s, "POST", "/api/cuentas/me/cierre", quien, json={"pin": pin})
                           for _ in range(int(veces or 1))]


@when(parsers.re(r'se intenta ingresar como (?P<quien>\S+) con el PIN "(?P<pin>[^"]*)"'))
def intenta_ingresar(s, quien, pin):
    s.respuesta = s.cliente.post("/api/auth/login", json={"celular": _celular(quien), "pin": pin})


@when(parsers.re(r'se registra una cuenta nueva con el celular "(?P<celular>[^"]*)"'))
def registra_con_celular(s, celular):
    s.respuesta = s.cliente.post("/api/usuarios", json={"dni": "12345679", "nombres": "Otra Persona",
                                                        "celular": celular, "pin": "4826"})


@when(parsers.re(r"(?P<quien>\S+) consulta el movimiento por el código de la última transferencia"))
def consulta_por_codigo(s, quien):
    _pedir(s, "GET", f"/api/movimientos/{_comprobantes(s)[-1]['codigo_operacion']}", quien)


@when(parsers.re(r"(?P<emisor>\S+) lanza (?P<cantidad>\d+) transferencias Qolqe simultáneas de (?P<monto>\S+) a (?P<destino>\S+)"))
def lanza_simultaneas(s, emisor, cantidad, monto, destino):
    s.simultaneas_datos = {"emisor": emisor, "destino": destino, "monto": Decimal(monto),
                           "saldos": {emisor: _saldo(s, emisor), destino: _saldo(s, destino)}}
    cuerpo = {"tipo": "QOLQE", "monto": monto, "celular_destino": _celular(destino)}
    _simultaneas(s, [(_token(s, emisor), cuerpo)] * int(cantidad))


@when(parsers.re(r"(?P<uno>\S+) y (?P<otro>\S+) se envían (?P<cantidad>\d+) transferencias simultáneas de (?P<monto>\S+) cada uno"))
def cruzadas_simultaneas(s, uno, otro, cantidad, monto):
    ida = (_token(s, uno), {"tipo": "QOLQE", "monto": monto, "celular_destino": _celular(otro)})
    vuelta = (_token(s, otro), {"tipo": "QOLQE", "monto": monto, "celular_destino": _celular(uno)})
    _simultaneas(s, [ida, vuelta] * int(cantidad))


@when(parsers.re(r'(?P<quien>\S+) simula una transferencia de "(?P<monto>[^"]*)" de tipo "(?P<tipo>[^"]*)"(?: (?P<veces>\d+) veces)?'))
def simula(s, quien, monto, tipo, veces):
    parametros = {}
    if monto != "(sin monto)":
        parametros["monto"] = monto
    if tipo != "(por defecto)":
        parametros["tipo"] = tipo
    s.simulaciones = [_pedir(s, "GET", "/api/transferencias/comision", quien, params=parametros)
                      for _ in range(int(veces or 1))]
    s.simulacion = s.respuesta


# ---------- Entonces ----------

@then(parsers.re(r'la operación termina con "(?P<estado>\d{3})(?: (?P<codigo>[A-Z_]+))?"'))
def termina_con(s, estado, codigo):
    assert s.respuesta.status_code == int(estado), s.respuesta.text
    if codigo:
        cuerpo = s.respuesta.json()
        assert cuerpo["codigo"] == codigo, cuerpo
        assert cuerpo["detail"], "Todo error debe incluir un mensaje"
    if estado == "204":
        assert s.respuesta.content == b"", s.respuesta.content


@then(parsers.re(r'el error de validación está en "(?P<campo>[^"]*)"'))
def error_en_campo(s, campo):
    assert s.respuesta.json()["errores"][0]["campo"] == campo, s.respuesta.text


@then(parsers.re(r'el detalle del error dice "(?P<detalle>[^"]*)"'))
def detalle_error(s, detalle):
    assert s.respuesta.json()["detail"] == detalle, s.respuesta.text


@then("la respuesta exige autenticación Bearer")
def exige_bearer(s):
    assert s.respuesta.headers.get("WWW-Authenticate") == "Bearer", s.respuesta.headers


@then(parsers.re(r'la cuenta de (?P<quien>\S+) figura como "(?P<estado>ACTIVA|CERRADA)"'))
def cuenta_figura(s, quien, estado):
    r = s.cliente.post("/api/auth/login", json={"celular": _celular(quien), "pin": _pin(quien)})
    if estado == "CERRADA":
        assert (r.status_code, r.json()["codigo"]) == (401, "CUENTA_CERRADA"), r.text
        return
    assert r.status_code == 200, r.text
    perfil = s.cliente.get("/api/cuentas/me", headers={"Authorization": f"Bearer {r.json()['access_token']}"})
    assert perfil.json()["estado"] == "ACTIVA", perfil.text


@then(parsers.re(r'todos los intentos de cierre responden "(?P<codigo>[A-Z_]+)"'))
def intentos_cierre(s, codigo):
    assert [(r.status_code, r.json()["codigo"]) for r in s.respuestas_cierre] == [(422, codigo)] * len(s.respuestas_cierre)


@then(parsers.re(r"ninguna de las dos sesiones de (?P<quien>\S+) sigue vigente"))
def sesiones_cerradas(s, quien):
    for cabeceras in (s.tokens[quien], s.segunda_sesion):
        r = s.cliente.get("/api/cuentas/me", headers=cabeceras)
        assert (r.status_code, r.json()["codigo"]) == (401, "NO_AUTENTICADO"), r.text


@then(parsers.re(r'el comprobante es de tipo "(?P<tipo>[A-Z]+)" por "(?P<monto>[^"]+)"'))
def comprobante_tipo(s, tipo, monto):
    c = _comprobantes(s)[-1]
    assert (c["tipo"], c["monto"]) == (tipo, monto), c


@then(parsers.re(r'el comprobante cobra una comisión de "(?P<comision>[^"]+)" y un total de "(?P<total>[^"]+)"'))
def comprobante_comision(s, comision, total):
    c = _comprobantes(s)[-1]
    assert (c["comision"], c["total"]) == (comision, total), c


@then(parsers.re(r'el comprobante informa el saldo "(?P<saldo>[^"]+)"'))
def comprobante_saldo(s, saldo):
    assert _comprobantes(s)[-1]["saldo"] == saldo, _comprobantes(s)[-1]


@then(parsers.re(r'el comprobante muestra monto "(?P<monto>[^"]+)", comisión "(?P<comision>[^"]+)", '
                 r'total "(?P<total>[^"]+)" y saldo "(?P<saldo>[^"]+)"'))
def comprobante_montos(s, monto, comision, total, saldo):
    c = _comprobantes(s)[-1]
    assert (c["monto"], c["comision"], c["total"], c["saldo"]) == (monto, comision, total, saldo), c
    assert Decimal(c["total"]) == Decimal(c["monto"]) + Decimal(c["comision"])


@then(parsers.re(r'el comprobante identifica al destinatario como "(?P<nombre>[^"]+)" con celular "(?P<celular>\d+)"'))
def comprobante_destinatario(s, nombre, celular):
    assert _comprobantes(s)[-1]["destinatario"] == {"nombre": nombre, "celular": celular, "cci": None}


@then(parsers.re(r'el comprobante identifica el destino solo por el CCI "(?P<cci>[^"]+)"'))
def comprobante_cci(s, cci):
    assert _comprobantes(s)[-1]["destinatario"] == {"nombre": None, "celular": None, "cci": cci}


@then('el comprobante tiene un código de operación "TRF" seguido de 17 dígitos')
def comprobante_codigo(s):
    assert re.fullmatch(r"TRF\d{17}", _comprobantes(s)[-1]["codigo_operacion"]), _comprobantes(s)[-1]


@then(parsers.re(r'la fecha del comprobante es hoy a las "(?P<hora>\d\d:\d\d)"'))
def comprobante_fecha(s, hora):
    # El reloj fijado sigue avanzando: se compara hasta el minuto.
    assert _comprobantes(s)[-1]["fecha"].startswith(f"{_hoy(s).isoformat()}T{hora}"), _comprobantes(s)[-1]


@then(parsers.re(r'el último movimiento de (?P<quien>\S+) tiene la descripción "(?P<descripcion>[^"]*)"'))
def ultimo_descripcion(s, quien, descripcion):
    assert _ultimo_movimiento(s, quien)["descripcion"] == descripcion


@then(parsers.re(r"(?P<uno>\S+) y (?P<otro>\S+) ven en su último movimiento la descripción enviada"))
def ven_descripcion(s, uno, otro):
    for quien in (uno, otro):
        movimiento = _ultimo_movimiento(s, quien)
        assert (movimiento["codigo_operacion"], movimiento["descripcion"]) == (
            _comprobantes(s)[-1]["codigo_operacion"], s.descripcion_enviada), movimiento


@then(parsers.re(r'el último movimiento de (?P<quien>\S+) es "(?P<tipo>[A-Z_]+)" por "(?P<importe>[^"]+)" '
                 r'con contraparte "(?P<contraparte>[^"]+)"'))
def ultimo_movimiento(s, quien, tipo, importe, contraparte):
    m = _ultimo_movimiento(s, quien)
    assert (m["tipo"], m["importe"], m["contraparte"]) == (tipo, importe, contraparte), m


@then(parsers.re(r'el último movimiento de (?P<quien>\S+) registra la comisión "(?P<comision>[^"]+)" y el importe "(?P<importe>[^"]+)"'))
def ultimo_comision(s, quien, comision, importe):
    m = _ultimo_movimiento(s, quien)
    assert (m["comision"], m["importe"]) == (comision, importe), m


@then(parsers.re(r"el último movimiento de (?P<uno>\S+) y el de (?P<otro>\S+) llevan el código y la fecha del comprobante"))
def mismo_codigo(s, uno, otro):
    c = _comprobantes(s)[-1]
    for quien in (uno, otro):
        m = _ultimo_movimiento(s, quien)
        assert (m["codigo_operacion"], m["fecha"]) == (c["codigo_operacion"], c["fecha"]), m


@then(parsers.re(r'el SMS de "(?P<celular>\d+)" incluye el código de operación del comprobante'))
def sms_con_codigo(s, celular):
    mensajes = s.cliente.get("/api/pruebas/notificaciones", params={"celular": celular}).json()
    assert _comprobantes(s)[-1]["codigo_operacion"] in mensajes[0]["mensaje"], mensajes


@then(parsers.re(r'(?P<quien>\S+) ve usado hoy "(?P<usado>[^"]+)" y disponible "(?P<disponible>[^"]+)"'))
def usado_hoy(s, quien, usado, disponible):
    limites = s.cliente.get("/api/limites", headers=_token(s, quien)).json()
    assert (limites["usado_hoy"], limites["disponible_hoy"]) == (usado, disponible), limites


@then("las dos últimas transferencias tienen la misma fecha y códigos de operación distintos")
def codigos_distintos(s):
    anterior, ultima = _comprobantes(s)[-2:]
    assert anterior["fecha"] == ultima["fecha"], (anterior, ultima)
    assert anterior["codigo_operacion"] != ultima["codigo_operacion"], ultima["codigo_operacion"]


@then(parsers.re(r'las (?P<cantidad>\d+) transferencias simultáneas terminan con "201"'))
def todas_aceptadas(s, cantidad):
    assert [r.status_code for r in s.simultaneas] == [201] * int(cantidad), [r.text for r in s.simultaneas]


@then(parsers.re(r'como máximo (?P<maximo>\d+) de las transferencias simultáneas terminan con "201"'))
def como_maximo(s, maximo):
    aceptadas = [r for r in s.simultaneas if r.status_code == 201]
    assert len(aceptadas) <= int(maximo), f"{len(aceptadas)} aceptadas de {len(s.simultaneas)}"


@then(parsers.re(r'las demás transferencias simultáneas terminan con "422 (?P<codigo>[A-Z_]+)"'))
def demas_rechazadas(s, codigo):
    rechazadas = [r for r in s.simultaneas if r.status_code != 201]
    assert all((r.status_code, r.json()["codigo"]) == (422, codigo) for r in rechazadas), [r.text for r in rechazadas]


@then("los códigos de operación de las transferencias simultáneas son todos distintos")
def simultaneas_codigos(s):
    codigos = [r.json()["codigo_operacion"] for r in s.simultaneas]
    assert len(set(codigos)) == len(codigos), codigos


@then("los saldos cuadran con las transferencias simultáneas aceptadas")
def saldos_cuadran(s):
    datos = s.simultaneas_datos
    movido = datos["monto"] * sum(r.status_code == 201 for r in s.simultaneas)
    final_emisor = _saldo(s, datos["emisor"])
    assert final_emisor >= 0, f"Saldo negativo: {final_emisor}"
    assert final_emisor == datos["saldos"][datos["emisor"]] - movido
    assert _saldo(s, datos["destino"]) == datos["saldos"][datos["destino"]] + movido


@then(parsers.re(r"lo usado hoy por (?P<quien>\S+) no supera su límite diario"))
def no_supera_limite(s, quien):
    limites = s.cliente.get("/api/limites", headers=_token(s, quien)).json()
    assert Decimal(limites["usado_hoy"]) <= Decimal(limites["limite_diario"]), limites


@then(parsers.re(r'el movimiento consultado es "(?P<tipo>[A-Z_]+)" por "(?P<importe>[^"]+)"'))
def movimiento_consultado(s, tipo, importe):
    m = s.respuesta.json()
    assert (m["tipo"], m["importe"]) == (tipo, importe), m


@then("ninguna respuesta sobre la última transferencia muestra el CCI completo")
def sin_cci_completo(s):
    comprobante = _comprobantes(s)[-1]
    cabeceras = _token(s, s.emisor)
    cuerpos = [
        json.dumps(comprobante),
        s.cliente.get("/api/movimientos/recientes", headers=cabeceras, params={"limite": 20}).text,
        s.cliente.get(f"/api/movimientos/{comprobante['codigo_operacion']}", headers=cabeceras).text,
    ]
    for cuerpo in cuerpos:
        assert not re.search(r"\d{20}", cuerpo), cuerpo


@then(parsers.re(r'la simulación muestra monto "(?P<monto>[^"]+)", comisión "(?P<comision>[^"]+)" y total "(?P<total>[^"]+)"'))
def simulacion_muestra(s, monto, comision, total):
    assert s.simulacion.json() == {"monto": monto, "comision": comision, "total": total}, s.simulacion.text


@then(parsers.re(r"las (?P<cantidad>\d+) simulaciones responden lo mismo"))
def simulaciones_iguales(s, cantidad):
    cuerpos = [(r.status_code, r.json()) for r in s.simulaciones]
    assert len(cuerpos) == int(cantidad) and all(c == cuerpos[0] for c in cuerpos), cuerpos


@then(parsers.re(r"el saldo, los movimientos, el límite usado y los SMS de (?P<quien>\S+) no cambiaron"))
def estado_sin_cambios(s, quien):
    assert _estado_cuenta(s, quien) == s.estado_anotado


@then("la comisión y el total del comprobante coinciden con la simulación")
def simulacion_coincide(s):
    simulacion, comprobante = s.simulacion.json(), _comprobantes(s)[-1]
    assert (simulacion["comision"], simulacion["total"]) == (comprobante["comision"], comprobante["total"])
