"""Escribe en el resumen del job una tabla con los resultados de uno o más JUnit XML.

Uso: resumen.py "Etiqueta" archivo.xml ["Etiqueta" archivo.xml ...]
"""
import os
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from casos import estado_testcase  # noqa: E402


def contar(ruta: Path) -> tuple[Counter, float]:
    casos = list(ET.parse(ruta).getroot().iter("testcase"))
    return Counter(estado_testcase(c) for c in casos), sum(float(c.get("time", 0) or 0) for c in casos)


def main() -> None:
    filas = [f"Evidencia: **{os.environ.get('EVIDENCIA', 'sin-imagenes')}**\n",
             "| Suite | Total | Pasan | Fallos esperados | Inestables | Omitidas | Fallan | Tiempo |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    argumentos = sys.argv[1:]
    for etiqueta, ruta in zip(argumentos[::2], argumentos[1::2], strict=True):
        ruta = Path(ruta)
        if not ruta.exists():
            filas.append(f"| {etiqueta} | sin reporte | | | | | | |")
            continue
        conteo, tiempo = contar(ruta)
        filas.append(f"| {etiqueta} | {sum(conteo.values())} | {conteo['passed']} | {conteo['xfailed']} | {conteo['flaky']} "
                     f"| {conteo['skipped']} | {conteo['failed']} | {tiempo:.1f} s |")
    texto = "\n".join(filas) + "\n"
    print(texto)
    destino = os.environ.get("GITHUB_STEP_SUMMARY")
    if destino:
        with open(destino, "a", encoding="utf-8") as archivo:
            archivo.write(texto)


if __name__ == "__main__":
    main()
