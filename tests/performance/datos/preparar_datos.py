"""Genera los datos de las pruebas de rendimiento y la base que se restaura antes de cada corrida (diseño §5.2).

Uso: python preparar_datos.py [--n 3000] [--url http://127.0.0.1:8090] [--hilos 6]
                              [--csv usuarios.csv] [--informe ../resultados/entorno/preparacion.json]
Requiere Qolqe en Docker con QOLQE_MODO_PRUEBA=1 (lo arranca preparar.sh) y el contenedor $CONTENEDOR.

Pasos (§5.2): 1 reiniciar (semilla: 200 usuarios de carga, D2) · 2 registrar 201..N por la API ·
3 saldo de S/ 10,000 a todos (PUT /api/pruebas/saldo, D2) · 4 login + 5 contactos por usuario por la API ·
5 SQL de lo que la API no permite (historial y 30 deudas, preparar_bd.sql) · 6 verificación (conteos e
integrity_check) · 7 respaldo base_perf.db + huella (V-05) · 8 usuarios.csv (un usuario distinto por VU, C4).
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PERF = AQUI.parent
CONTENEDOR = os.environ.get("CONTENEDOR", "qolqe-perf")

USUARIOS_SEMILLA = 200        # semilla.py USUARIOS_DE_CARGA: 900000001..900000200, ids 7..206
PIN = "2580"                  # semilla.py PIN_USUARIOS_DE_CARGA (cumple RN-03); el mismo para los nuevos
SALDO = "10000"               # §5.1 Saldo: S/ 10,000 > gasto del peor caso por VU en 62 min (≈ S/ 2,000)
CONTACTOS = 5                 # §5.1 Contactos: anillo i → i+1..i+5 (máximo permitido 15, R-G4-03)
DEUDAS = 30                   # preparar_bd.sql: 30 deudas pendientes por usuario (§5.1)
MOVIMIENTOS = 1000            # historial de la semilla por usuario de carga (semilla.py)

CONTEOS_SQL = """
-- @conteos
SELECT (SELECT COUNT(*) FROM usuarios WHERE estado = 'ACTIVA' AND celular BETWEEN '900000001' AND '900099999') AS usuarios_carga,
       (SELECT COUNT(*) FROM contactos c JOIN usuarios u ON u.id = c.usuario_id
         WHERE u.celular BETWEEN '900000001' AND '900099999') AS contactos_carga,
       (SELECT COUNT(*) FROM deudas WHERE estado = 'PENDIENTE' AND length(suministro) = 10 AND suministro LIKE '5%') AS deudas_carga,
       (SELECT COUNT(*) FROM cuentas c JOIN usuarios u ON u.id = c.usuario_id
         WHERE u.celular BETWEEN '900000001' AND '900099999' AND c.saldo_cent <> 1000000) AS saldos_distintos,
       (SELECT MIN(n) FROM (SELECT COUNT(m.id) AS n FROM usuarios u LEFT JOIN movimientos m ON m.usuario_id = u.id
         WHERE u.celular BETWEEN '900000001' AND '900099999' GROUP BY u.id)) AS min_movimientos_por_usuario,
       (SELECT COUNT(*) FROM movimientos) AS movimientos
-- @integridad
PRAGMA integrity_check
"""
EJECUTAR_SQL = "import sqlite3,sys; c=sqlite3.connect(sys.argv[1],timeout=60); c.executescript(sys.stdin.read()); c.commit(); c.close()"
RESPALDAR = ("import sqlite3,os; d='/data/base_perf.db'; t=d+'.tmp'; s=sqlite3.connect('/data/qolqe.db',timeout=60); "
             "b=sqlite3.connect(t); s.backup(b); b.close(); s.close(); os.replace(t,d)")


def celular(n: int) -> str:
    return f"9{n:08d}"  # como la semilla: 900000001, 900000002, …


class Cliente:
    def __init__(self, url: str):
        self.url = url

    def pedir(self, metodo: str, ruta: str, cuerpo=None, token=None, esperado=(200,)):
        cabeceras = {"Content-Type": "application/json"} | ({"Authorization": f"Bearer {token}"} if token else {})
        datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
        peticion = urllib.request.Request(self.url + ruta, data=datos, method=metodo, headers=cabeceras)
        try:
            with urllib.request.urlopen(peticion, timeout=120) as r:
                estado, texto = r.status, r.read()
        except urllib.error.HTTPError as e:
            estado, texto = e.code, e.read()
        if estado not in esperado:
            raise RuntimeError(f"{metodo} {ruta}: {estado} {texto[:300]!r}")
        return json.loads(texto) if texto else None


def en_contenedor(codigo: str, *argumentos: str, entrada: str = "") -> str:
    orden = ["docker", "exec", "-i", CONTENEDOR, "python", "-c", codigo, *argumentos]
    salida = subprocess.run(orden, input=entrada, capture_output=True, text=True, check=False)
    if salida.returncode != 0:
        raise RuntimeError(f"falló en el contenedor {CONTENEDOR}:\n{salida.stderr}")
    return salida.stdout


def consultar(sql: str, *argumentos: str) -> dict:
    lector = (PERF / "integridad" / "verificar_bd.py").read_text()
    return json.loads(en_contenedor(lector, *argumentos, entrada=sql))


def en_paralelo(funcion, elementos, hilos: int) -> list:
    with ThreadPoolExecutor(hilos) as pool:  # un usuario por tarea: nunca dos hilos sobre el mismo (DEF-14)
        return list(pool.map(funcion, elementos))


def paso(informe: dict, nombre: str, funcion, cantidad: int | None = None):
    print(f"  {nombre} …", end="", flush=True)
    inicio = time.perf_counter()
    resultado = funcion()
    segundos = time.perf_counter() - inicio
    informe["pasos"][nombre] = {"segundos": round(segundos, 2)}
    if cantidad:
        informe["pasos"][nombre] |= {"cantidad": cantidad, "ms_por_unidad": round(segundos * 1000 / cantidad, 1)}
    print(f" {segundos:.1f} s" + (f" ({cantidad} → {segundos * 1000 / cantidad:.1f} ms c/u)" if cantidad else ""))
    return resultado


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--n", type=int, default=3000, help="usuarios de carga (M-16: 3,000)")
    parser.add_argument("--url", default=os.environ.get("BASE_URL", "http://127.0.0.1:8090"))
    parser.add_argument("--hilos", type=int, default=6)
    parser.add_argument("--csv", default=str(AQUI / "usuarios.csv"))
    parser.add_argument("--informe", default=str(PERF / "resultados" / "entorno" / "preparacion.json"))
    args = parser.parse_args()
    if args.n <= CONTACTOS:
        sys.exit(f"--n debe ser mayor que {CONTACTOS} (anillo de contactos)")

    api = Cliente(args.url)
    n_api = max(0, args.n - USUARIOS_SEMILLA)
    informe = {"fecha": date.today().isoformat(), "n": args.n, "creados_por_api": n_api, "hilos": args.hilos,
               "cpus_preparacion": os.environ.get("CPUS_PREPARACION"), "carga_equipo_inicio": os.getloadavg(),
               "pasos": {}}
    print(f"Preparando {args.n} usuarios de carga en {args.url} (contenedor {CONTENEDOR}, {args.hilos} hilos)")
    inicio_total = time.perf_counter()

    # 1) Semilla (D2). Reloj en hora real: los vencimientos y la ventana de 30 días dependen de la fecha (§5.2).
    api.pedir("DELETE", "/api/pruebas/reloj")
    paso(informe, "1_reiniciar", lambda: api.pedir("POST", "/api/pruebas/reiniciar"))

    # 2) Registro de 201..N por la API: DNI sintético único, nombre "Carga NNNN", PIN 2580 (§5.2).
    def registrar(n: int):
        api.pedir("POST", "/api/usuarios", {"dni": f"7{n:07d}", "nombres": f"Carga {n:04d}",
                                            "celular": celular(n), "pin": PIN}, esperado=(201,))
    nuevos = range(USUARIOS_SEMILLA + 1, args.n + 1)
    if n_api:
        paso(informe, "2_registrar", lambda: en_paralelo(registrar, nuevos, args.hilos), n_api)

    # 3) Saldo de S/ 10,000 para todos con el endpoint de soporte (D2).
    def fijar_saldo(n: int):
        api.pedir("PUT", "/api/pruebas/saldo", {"celular": celular(n), "saldo": SALDO})
    paso(informe, "3_saldo", lambda: en_paralelo(fijar_saldo, range(1, args.n + 1), args.hilos), args.n)

    # 4) Login y 5 contactos por usuario, por la API, para que respeten las reglas por construcción (§5.2).
    def contactos(n: int) -> dict:
        sesion = api.pedir("POST", "/api/auth/login", {"celular": celular(n), "pin": PIN})
        ids, alias = [], []
        for k in range(1, CONTACTOS + 1):
            m = (n - 1 + k) % args.n + 1  # anillo: n+1 … n+5, y vuelve al inicio
            contacto = api.pedir("POST", "/api/contactos", {"celular": celular(m), "alias": f"Amigo {m:04d}"},
                                 token=sesion["access_token"], esperado=(201,))
            ids.append(contacto["id"])
            alias.append(contacto["alias"])
        return {"vu": n, "usuario_id": sesion["usuario"]["id"], "contactos": ids, "buscar": alias[0]}
    filas = paso(informe, "4_login_y_contactos",
                 lambda: en_paralelo(contactos, range(1, args.n + 1), args.hilos), args.n)

    # 5) Historial clonado y 30 deudas por usuario: lo que la API no permite (preparar_bd.sql).
    sql = (AQUI / "preparar_bd.sql").read_text()
    paso(informe, "5_sql_historial_y_deudas", lambda: en_contenedor(EJECUTAR_SQL, "/data/qolqe.db", entrada=sql), args.n)

    # 6) Verificación de conteos e integridad de la base (§5.2, paso 7).
    r = paso(informe, "6_verificacion", lambda: consultar(CONTEOS_SQL, "--bd", "/data/qolqe.db"))
    conteos = dict(zip(r["conteos"]["columnas"], r["conteos"]["filas"][0], strict=True))
    integridad = r["integridad"]["filas"][0][0]
    esperado = {"usuarios_carga": args.n, "contactos_carga": CONTACTOS * args.n, "deudas_carga": DEUDAS * args.n,
                "saldos_distintos": 0}
    errores = [f"{k}: {conteos[k]} (esperado {v})" for k, v in esperado.items() if conteos[k] != v]
    if conteos["min_movimientos_por_usuario"] < MOVIMIENTOS:
        errores.append(f"min_movimientos_por_usuario: {conteos['min_movimientos_por_usuario']} (< {MOVIMIENTOS})")
    if integridad != "ok":
        errores.append(f"integrity_check: {integridad}")
    informe |= {"conteos": conteos, "integrity_check": integridad}
    if errores:
        sys.exit("Verificación fallida:\n  " + "\n  ".join(errores))

    # 7) Respaldo consistente (API de backup de SQLite) y su huella, para restaurar y comprobar en cada corrida.
    paso(informe, "7_respaldo_base_perf", lambda: en_contenedor(RESPALDAR))
    huella = consultar((PERF / "integridad" / "foto.sql").read_text(), "--bd", "/data/base_perf.db", "--inmutable")
    huella = dict(zip(huella["foto"]["columnas"], huella["foto"]["filas"][0], strict=True))
    meta = {"fecha": informe["fecha"], "n": args.n, "huella": huella}
    subprocess.run(["docker", "exec", "-i", CONTENEDOR, "sh", "-c", "cat > /data/base_perf.json"],
                   input=json.dumps(meta), text=True, check=True)
    tamano = en_contenedor("import os; print(os.path.getsize('/data/base_perf.db'))").strip()
    informe |= {"huella_base_perf": huella, "tamano_base_perf_MB": round(int(tamano) / 1e6, 1)}

    # 8) usuarios.csv: VU n → fila n (exec.vu.idInTest), su suministro propio y los ids de sus contactos.
    with open(args.csv, "w") as f:
        f.write("vu,celular,pin,usuario_id,suministro,contactos,buscar\n")
        for fila in filas:
            suministro = f"5{fila['usuario_id']:09d}"  # el mismo printf('5%09d', id) de preparar_bd.sql
            f.write(f"{fila['vu']},{celular(fila['vu'])},{PIN},{fila['usuario_id']},{suministro},"
                    f"{'|'.join(map(str, fila['contactos']))},{fila['buscar']}\n")

    informe["segundos_total"] = round(time.perf_counter() - inicio_total, 1)
    Path(args.informe).parent.mkdir(parents=True, exist_ok=True)
    Path(args.informe).write_text(json.dumps(informe, indent=1))
    print(f"Listo en {informe['segundos_total']} s: {conteos['usuarios_carga']} usuarios, {conteos['contactos_carga']} "
          f"contactos, {conteos['deudas_carga']} deudas, {conteos['movimientos']:,} movimientos, base "
          f"{informe['tamano_base_perf_MB']} MB.\n  CSV: {args.csv}\n  Informe: {args.informe}")


if __name__ == "__main__":
    main()
