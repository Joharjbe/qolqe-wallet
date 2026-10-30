"""Escribe en el resumen del job una tabla con los resultados de uno o más JUnit XML.

Uso: resumen.py "Etiqueta" archivo.xml ["Etiqueta" archivo.xml ...]
"""
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def contar(ruta: Path) -> tuple[int, int, int, int, float]:
    if not ruta.exists():
        return 0, 0, 0, 0, 0.0
    casos = list(ET.parse(ruta).getroot().iter("testcase"))
    fallidos = sum(1 for c in casos if c.find("failure") is not None or c.find("error") is not None)
    esperados = sum(1 for c in casos if c.find("skipped") is not None and "xfail" in c.find("skipped").get("type", ""))
    omitidos = sum(1 for c in casos if c.find("skipped") is not None) - esperados
    return len(casos), fallidos, esperados, omitidos, sum(float(c.get("time", 0)) for c in casos)


def main() -> None:
    filas = ["| Suite | Total | Pasan | Fallos esperados | Omitidas | Fallan | Tiempo |", "|---|---:|---:|---:|---:|---:|---:|"]
    argumentos = sys.argv[1:]
    for etiqueta, ruta in zip(argumentos[::2], argumentos[1::2]):
        ruta = Path(ruta)
        if not ruta.exists():
            filas.append(f"| {etiqueta} | sin reporte | | | | | |")
            continue
        total, fallidos, esperados, omitidos, tiempo = contar(ruta)
        filas.append(f"| {etiqueta} | {total} | {total - fallidos - esperados - omitidos} | {esperados} | {omitidos} | {fallidos} | {tiempo:.1f} s |")
    texto = "\n".join(filas) + "\n"
    print(texto)
    destino = os.environ.get("GITHUB_STEP_SUMMARY")
    if destino:
        with open(destino, "a", encoding="utf-8") as archivo:
            archivo.write(texto)


if __name__ == "__main__":
    main()
