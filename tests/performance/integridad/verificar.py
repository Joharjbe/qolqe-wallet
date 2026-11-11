"""Verificación del dinero antes y después de una corrida (U-07, diseño §5.5) y huella de la base (V-05).

U-07: "ninguna operación de dinero puede quedar a medias ni aplicarse dos veces" → descuadres = 0 en C1 a C6.
"Antes" es base_perf.db, porque correr.sh la restaura antes de cada corrida (S-09); "después" es qolqe.db sin
tráfico. Los chequeos SQL corren dentro del contenedor (verificar_bd.py); aquí se concilian con k6 (C6).

Uso:
  python verificar.py foto [--bd /data/qolqe.db] [--inmutable]          huella en JSON (V-05)
  python verificar.py comparar [--antes /data/base_perf.db] [--despues /data/qolqe.db]
                               [--k6 resultados/.../muestras.csv.gz] [--esperado transferencias=3,recargas=1]
                               [--salida verificacion_dinero.txt]
Código de salida de comparar: 0 = PASA (0 descuadres), 1 = FALLA, 2 = error al verificar.
"""
import argparse
import csv
import gzip
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
TIPOS = ("transferencias", "recargas", "pagos")
# POST que mueven dinero (M-07) → tipo de fila en la BD. Se identifican por método y ruta, no por etiqueta,
# para no depender de los nombres de etiqueta del script de k6.
POST_DINERO = {"/api/transferencias": "transferencias", "/api/recargas": "recargas", "/api/servicios/pagos": "pagos"}
RUTA_API = re.compile(r"/api/[^?\s]*")


def en_contenedor(sql: Path, *argumentos: str) -> dict:
    """Ejecuta verificar_bd.py en el contenedor de Qolqe con el .sql por stdin y devuelve su JSON."""
    contenedor = os.environ.get("CONTENEDOR", "qolqe-perf")
    orden = ["docker", "exec", "-i", contenedor, "python", "-c", (AQUI / "verificar_bd.py").read_text(), *argumentos]
    salida = subprocess.run(orden, input=sql.read_text(), capture_output=True, text=True, check=False)
    if salida.returncode != 0:
        sys.exit(f"verificar: falló la consulta en {contenedor}:\n{salida.stderr}")
    return json.loads(salida.stdout)


def foto(bd: str, inmutable: bool) -> dict:
    argumentos = ["--bd", bd] + (["--inmutable"] if inmutable else [])
    bloque = en_contenedor(AQUI / "foto.sql", *argumentos)["foto"]
    return dict(zip(bloque["columnas"], bloque["filas"][0], strict=True))


def contar_k6(muestras: Path) -> dict:
    """Respuestas de k6 a los POST de dinero: 201 = confirmada; 0 = sin respuesta (timeout o conexión). Además, los POST
    enviados (dinero_intentos de k6/operaciones.js): los que no tienen ninguna respuesta registrada quedaron en vuelo
    cuando k6 cortó la sesión (gracefulStop, fin de la demo o humo) y su resultado es desconocido, como un timeout."""
    conteo = {"confirmadas": Counter(), "sin_respuesta": Counter(), "otras": Counter(), "intentos": Counter(), "logins_ok": 0}
    abrir = gzip.open if muestras.suffix == ".gz" else open
    with abrir(muestras, "rt", newline="") as f:
        for fila in csv.DictReader(f):
            if fila["metric_name"] == "dinero_intentos":
                ruta = RUTA_API.search(fila["name"] or "")
                tipo = POST_DINERO.get(ruta.group(0) if ruta else "")
                if tipo:
                    conteo["intentos"][tipo] += round(float(fila["metric_value"] or 1))
                continue
            if fila["metric_name"] != "http_reqs" or fila["method"] != "POST":
                continue
            # La ruta sale de la columna url, que k6 reemplaza por la etiqueta name si el script la fija
            # ("POST /api/transferencias"); por eso se busca "/api/…" en el texto y no se parsea como URL.
            ruta = RUTA_API.search(fila["url"] or fila["name"])
            ruta, estado = (ruta.group(0) if ruta else ""), fila["status"]
            if ruta == "/api/auth/login" and estado == "200":
                conteo["logins_ok"] += 1
            tipo = POST_DINERO.get(ruta)
            if tipo:
                clave = "confirmadas" if estado == "201" else "sin_respuesta" if estado == "0" else "otras"
                conteo[clave][tipo] += 1
    return conteo


def conciliar(bd: dict, referencia: dict | None) -> list[dict]:
    """C6: filas nuevas en la BD contra lo confirmado. 0 ≤ BD − confirmadas ≤ sin respuesta + cortadas en vuelo (S-09:
    k6 no reintenta, así que una fila de más sin ninguna respuesta perdida que la explique solo puede ser un duplicado)."""
    filas = []
    for tipo in TIPOS:
        fila = {"tipo": tipo, "bd": bd[tipo]}
        if referencia is not None:
            confirmadas = referencia["confirmadas"][tipo]
            sin_respuesta = referencia["sin_respuesta"].get(tipo, 0)
            registradas = confirmadas + sin_respuesta + referencia.get("otras", Counter()).get(tipo, 0)
            cortadas = max(0, referencia.get("intentos", Counter()).get(tipo, 0) - registradas)
            diferencia = bd[tipo] - confirmadas
            fila.update(confirmadas=confirmadas, sin_respuesta=sin_respuesta, cortadas=cortadas, diferencia=diferencia,
                        ok=0 <= diferencia <= sin_respuesta + cortadas)
            if diferencia < 0:
                fila["explicacion"] = "confirmadas por la API y no guardadas (riesgo DEF-07)"
            elif diferencia > sin_respuesta + cortadas:
                fila["explicacion"] = "aplicadas de más: no hay respuestas perdidas que las expliquen (duplicado)"
            elif diferencia > 0:
                fila["explicacion"] = ("aplicadas sin confirmación: el cliente no recibió la respuesta (timeout o sesión "
                                       "cortada por k6 con la petición en vuelo)")
        filas.append(fila)
    return filas


def cent(valor) -> str:
    return "—" if valor is None else f"S/ {valor / 100:,.2f}"


def informe(r: dict, c6: list[dict], origen_c6: str, args) -> tuple[str, bool]:
    c1 = dict(zip(r["C1_conservacion"]["columnas"], r["C1_conservacion"]["filas"][0], strict=True))
    resultados = {
        "C1 Conservación del dinero": (c1["descuadre_cent"] == 0 and c1["descuadre_libro_cent"] == 0,
                                       f"descuadre {c1['descuadre_cent']} cént.; libro {c1['descuadre_libro_cent']} cént."),
        "C2 Libro mayor por usuario": (r["C2_libro_mayor"]["total"] == 0, f"{r['C2_libro_mayor']['total']} usuarios con descuadre"),
        "C3 Operación ↔ movimientos": (r["C3_operacion_movimientos"]["total"] == 0,
                                       f"{r['C3_operacion_movimientos']['total']} filas"),
        "C4 Pagos de deudas": (r["C4_pagos"]["total"] == 0, f"{r['C4_pagos']['total']} filas"),
        "C5 Reglas (DEF-21)": (r["C5_reglas"]["total"] == 0, f"{r['C5_reglas']['total']} filas"),
        "C6 Conteos y conciliación": (all(f.get("ok", True) for f in c6), origen_c6),
    }
    pasa = all(ok for ok, _ in resultados.values())
    # Descuadres = problemas encontrados: cada saldo global que no cuadra, cada fila de C2 a C5 y cada tipo de C6
    # que no se explica. Va en la línea "TOTAL descuadres: N" que lee analisis/ para U-07.
    descuadres = ((c1["descuadre_cent"] != 0) + (c1["descuadre_libro_cent"] != 0)
                  + sum(r[n]["total"] for n in ("C2_libro_mayor", "C3_operacion_movimientos", "C4_pagos", "C5_reglas"))
                  + sum(not f.get("ok", True) for f in c6))
    lineas = [
        "Verificación del dinero antes y después (U-07: descuadres = 0, diseño §5.5)",
        f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}   Contenedor: {os.environ.get('CONTENEDOR', 'qolqe-perf')}",
        f"Antes: {args.antes}   Después: {args.despues}",
        "",
        (f"Saldos: antes {cent(c1['antes_cent'])}, después {cent(c1['despues_cent'])}. Salidas: recargas "
         f"{cent(c1['recargas_cent'])}, pagos {cent(c1['pagos_cent'])}, comisiones {cent(c1['comisiones_cent'])}, "
         f"interbancarias {cent(c1['interbancarias_cent'])}. Movimientos nuevos (neto): {cent(c1['movimientos_neto_cent'])}."),
        "",
    ]
    lineas += [f"{nombre:<30} {'PASA' if ok else 'FALLA':<6} {detalle}" for nombre, (ok, detalle) in resultados.items()]
    lineas += ["", ("C6 por tipo (BD = filas nuevas; confirmadas = 201 recibidos; sin respuesta = status 0; cortadas = "
                    "enviadas sin ninguna respuesta registrada porque k6 cortó la sesión):")]
    for f in c6:
        if "confirmadas" in f:
            lineas.append(f"  {f['tipo']:<15} BD {f['bd']:>6}   confirmadas {f['confirmadas']:>6}   sin respuesta "
                          f"{f['sin_respuesta']:>4}   cortadas {f['cortadas']:>4}   diferencia {f['diferencia']:>4}   "
                          f"{'ok' if f['ok'] else 'FALLA'}"
                          + (f"   ({f['explicacion']})" if "explicacion" in f else ""))
        else:
            lineas.append(f"  {f['tipo']:<15} BD {f['bd']:>6}   (sin referencia para conciliar)")
    c6_bd = dict(zip(r["C6_conteos"]["columnas"], r["C6_conteos"]["filas"][0], strict=True))
    lineas.append(f"  logins nuevos (sesiones): {c6_bd['logins']}   movimientos nuevos: {c6_bd['movimientos']}")
    for nombre in ("C2_libro_mayor", "C3_operacion_movimientos", "C4_pagos", "C5_reglas"):
        if r[nombre]["total"]:
            lineas += ["", f"Detalle {nombre} (primeras {len(r[nombre]['filas'])} de {r[nombre]['total']}):",
                       "  " + " | ".join(r[nombre]["columnas"])]
            lineas += ["  " + " | ".join(str(v) for v in fila) for fila in r[nombre]["filas"]]
    lineas += ["", f"TOTAL descuadres: {descuadres}", f"Resultado U-07: {'PASA' if pasa else 'FALLA'}"]
    return "\n".join(lineas) + "\n", pasa


def comparar(args) -> int:
    r = en_contenedor(AQUI / "verificar_dinero.sql", "--bd", args.despues, "--antes", args.antes)
    c6_bd = dict(zip(r["C6_conteos"]["columnas"], r["C6_conteos"]["filas"][0], strict=True))
    referencia, origen = None, "sin referencia (solo conteos)"
    if args.k6:
        k6 = contar_k6(Path(args.k6))
        referencia, origen = k6, f"conciliado con k6 ({Path(args.k6).name})"
    elif args.esperado:
        esperado = Counter({t: int(n) for t, n in (p.split("=") for p in args.esperado.split(","))})
        referencia, origen = {"confirmadas": esperado, "sin_respuesta": Counter()}, f"conciliado con --esperado {args.esperado}"
    c6 = conciliar(c6_bd, referencia)
    texto, pasa = informe(r, c6, origen, args)
    print(texto, end="")
    if args.salida:
        Path(args.salida).write_text(texto)
        datos = {"pasa": pasa, "chequeos": r, "c6": c6,
                 "k6_logins_ok": referencia.get("logins_ok") if referencia else None}
        Path(args.salida).with_suffix(".json").write_text(json.dumps(datos, indent=1, default=str))
    return 0 if pasa else 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="orden", required=True)
    p_foto = sub.add_parser("foto")
    p_foto.add_argument("--bd", default="/data/qolqe.db")
    p_foto.add_argument("--inmutable", action="store_true")
    p_comp = sub.add_parser("comparar")
    p_comp.add_argument("--antes", default="/data/base_perf.db")
    p_comp.add_argument("--despues", default="/data/qolqe.db")
    p_comp.add_argument("--k6", help="muestras.csv(.gz) de k6 (--out csv) para conciliar C6")
    p_comp.add_argument("--esperado", help="conteos confirmados a mano, p. ej. transferencias=3,recargas=1,pagos=1")
    p_comp.add_argument("--salida", help="archivo de texto; también escribe el .json al lado")
    args = parser.parse_args()
    if args.orden == "foto":
        print(json.dumps(foto(args.bd, args.inmutable)))
    else:
        sys.exit(comparar(args))


if __name__ == "__main__":
    main()
