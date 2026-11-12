"""Ejecuta los bloques "-- @nombre" de un .sql (leído de stdin) sobre la base de Qolqe y devuelve JSON.

Corre DENTRO del contenedor de Qolqe (la base vive en el volumen /data y la imagen trae Python con sqlite3),
en modo solo lectura (PRAGMA query_only). Lo invoca verificar.py:
  docker exec -i qolqe-perf python -c "<este archivo>" --bd /data/qolqe.db [--antes /data/base_perf.db] < x.sql
"""
import argparse
import json
import re
import sqlite3
import sys
import time

MAX_FILAS = 50  # filas que se devuelven por bloque (el total siempre se informa)


def bloques(sql: str) -> list[tuple[str, str]]:
    partes = re.split(r"^-- @(\w+).*$", sql, flags=re.MULTILINE)
    return list(zip(partes[1::2], partes[2::2], strict=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bd", required=True)
    parser.add_argument("--antes", help="base de referencia; se adjunta como 'a' (inmutable)")
    parser.add_argument("--inmutable", action="store_true", help="abrir --bd como archivo que no cambia")
    args = parser.parse_args()

    uri = f"file:{args.bd}?mode=ro&immutable=1" if args.inmutable else f"file:{args.bd}"
    con = sqlite3.connect(uri, uri=True, timeout=30)
    con.execute("PRAGMA query_only = ON")
    if args.antes:
        con.execute("ATTACH DATABASE ? AS a", (f"file:{args.antes}?mode=ro&immutable=1",))

    resultado = {}
    for nombre, consulta in bloques(sys.stdin.read()):
        inicio = time.perf_counter()
        cursor = con.execute(consulta)
        filas = cursor.fetchall()
        resultado[nombre] = {
            "columnas": [c[0] for c in cursor.description],
            "filas": [list(f) for f in filas[:MAX_FILAS]],
            "total": len(filas),
            "segundos": round(time.perf_counter() - inicio, 3),
        }
    print(json.dumps(resultado))


main()
