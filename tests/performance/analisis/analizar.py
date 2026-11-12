"""Análisis de una corrida: veredicto U/V, tablas y datos por ventana (diseño §7 y §8).

Uso:
  .venv/bin/python tests/performance/analisis/analizar.py <carpeta_corrida> [<carpeta_corrida> …]

<carpeta_corrida> = tests/performance/resultados/<escenario>/<marca-de-tiempo>/. Escribe ahí:
  peticiones.csv.gz y metricas_k6.csv.gz   versión compacta de las muestras de k6 (se versiona)
  ventanas.csv, errores_datos_ventanas.csv  métricas por ventana (1 min carga, 30 s pico y estrés, 5 min resistencia)
  tabla_resumen.md/.csv                     formato de S14 por endpoint
  veredicto.md/.csv                         cada V y cada U con lo medido, el umbral y si pasa
  tabla_estres.md/.csv                      (estrés) un momento cada 100 usuarios, ejercicio 3 de S14
  calibracion.json                          (calibración) D_sesión, L_sat y TOP (M-14)
Los gráficos los hace graficos.py, que usa este mismo análisis.
"""
import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from capacidad import tabla_momentos
from corrida import Corrida, cargar
from informe import escribir_tabla_estres, escribir_tabla_resumen, escribir_veredicto
from ventanas import tabla_ventanas
from veredicto import evaluar


@dataclass
class Analisis:
    corrida: Corrida
    ventanas: pd.DataFrame
    errores_datos: pd.DataFrame
    evaluacion: dict
    tabla_resumen: pd.DataFrame
    momentos: pd.DataFrame | None = None


def analizar(carpeta: Path, ventana_s: float | None = None) -> Analisis:
    c = cargar(Path(carpeta))
    v, errores_datos = tabla_ventanas(c, ventana_s or c.perfil.ventana_s)
    v.to_csv(c.carpeta / "ventanas.csv", index=False, float_format="%.3f")
    errores_datos.to_csv(c.carpeta / "errores_datos_ventanas.csv", index=False)
    ev = evaluar(c, v)
    resumen = escribir_tabla_resumen(c)
    escribir_veredicto(c, ev)
    momentos = None
    if c.escenario == "estres":
        momentos = tabla_momentos(v, escala=c.perfil.escala)
        escribir_tabla_estres(c, momentos, ev["extra"]["capacidad"])
    if c.escenario == "calibracion" and ev["extra"].get("calibracion"):
        (c.carpeta / "calibracion.json").write_text(json.dumps(ev["extra"]["calibracion"], indent=2), encoding="utf-8")
    return Analisis(c, v, errores_datos, ev, resumen, momentos)


def linea_resumen(a: Analisis) -> str:
    estados = ", ".join(f"{f.id} {f.resultado}" for f in a.evaluacion["umbrales"] if f.resultado != "NO APLICA")
    invalida = [f.id for f in a.evaluacion["validez"] if f.decide and f.resultado == "FALLA"]
    ensayo = f" · ENSAYO ×{a.corrida.perfil.escala:g}" if a.corrida.perfil.escala != 1 else ""
    return (f"{a.corrida.nombre}: {estados or 'sin umbrales'}" + (f" · NO VÁLIDA ({', '.join(invalida)})" if invalida else "")
            + ensayo)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("carpetas", nargs="+", type=Path, help="carpetas resultados/<escenario>/<marca>/")
    parser.add_argument("--ventana", type=float, help="ancho de ventana en s (por defecto, el del diseño §7.2)")
    args = parser.parse_args(argv)
    for carpeta in args.carpetas:
        print(linea_resumen(analizar(carpeta, args.ventana)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
