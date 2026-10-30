"""Une las etiquetas de los .feature (@HU, @CA, @CP, @DEF) con los JUnit XML del pipeline.

Genera la matriz HU -> caso -> resultado en Markdown y la portada HTML de GitHub Pages.
"""
import argparse
import html
import os
import re
import shutil
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ID_CASO = re.compile(r"cp[-_]?([awt])[-_]?(\d+)", re.I)
HISTORIAS = {
    "HU-G4-01": "Agregar un contacto", "HU-G4-02": "Ver y buscar mis contactos", "HU-G4-03": "Editar un contacto",
    "HU-G4-04": "Eliminar un contacto", "HU-G4-05": "Transferir a un contacto", "HU-G4-06": "Solicitar dinero a un contacto",
    "HU-G4-07": "Ver mis solicitudes", "HU-G4-08": "Aceptar una solicitud recibida",
    "HU-G4-09": "Rechazar una solicitud recibida", "HU-G4-10": "Cancelar una solicitud enviada",
}


def leer_casos(carpeta: Path) -> dict[str, dict]:
    casos = {}
    for feature in sorted(carpeta.rglob("*.feature")):
        nivel = "web" if feature.parent.name == "web" else "api"
        etiquetas: list[str] = []
        for linea in feature.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if linea.startswith("@"):
                etiquetas = [e.lstrip("@") for e in linea.split()]
            elif m := re.match(r"(?:Escenario|Esquema del escenario): (CP-\w+) (.+)", linea):
                casos[m[1]] = {
                    "titulo": m[2], "nivel": nivel,
                    "hu": [e for e in etiquetas if e.startswith("HU-")],
                    "ca": [e for e in etiquetas if re.fullmatch(r"CA\d+", e)],
                    "defecto": next((e for e in etiquetas if e.startswith("DEF-")), None),
                }
    return casos


def leer_resultados(*rutas: Path) -> dict[str, list[str]]:
    resultados = defaultdict(list)
    for ruta in rutas:
        if not ruta.exists():
            continue
        for caso in ET.parse(ruta).getroot().iter("testcase"):
            m = ID_CASO.search(caso.get("name", ""))
            if not m:
                continue
            omitido = caso.find("skipped")
            if caso.find("failure") is not None or caso.find("error") is not None:
                estado = "failed"
            elif omitido is not None:
                estado = "xfailed" if "xfail" in omitido.get("type", "") else "skipped"
            else:
                estado = "passed"
            resultados[f"CP-{m[1].upper()}{m[2]}"].append(estado)
    return resultados


def resultado(caso: dict, estados: list[str]) -> str:
    if not estados:
        return "sin ejecutar"
    if "failed" in estados:
        return f"failed ({estados.count('failed')}/{len(estados)})"
    if "skipped" in estados:
        return "skipped"
    if "xfailed" in estados:
        return f"xfailed → {caso['defecto']}"
    return f"passed ({len(estados)}/{len(estados)})"


def contrato(ruta: Path) -> str:
    if not ruta.exists():
        return "sin ejecutar"
    casos = list(ET.parse(ruta).getroot().iter("testcase"))
    fallos = sum(1 for c in casos if c.find("failure") is not None or c.find("error") is not None)
    return f"failed ({fallos}/{len(casos)})" if fallos else f"passed ({len(casos)}/{len(casos)})"


def construir_filas(casos: dict, resultados: dict, ruta_contrato: Path) -> list[list[str]]:
    filas = []
    for id_caso, caso in sorted(casos.items(), key=lambda par: (min(par[1]["hu"], default=""), par[0])):
        hu = ", ".join(caso["hu"]) or "—"
        ca = ", ".join(caso["ca"]) or "técnico"
        filas.append([hu, ca, id_caso, caso["titulo"], caso["nivel"], resultado(caso, resultados.get(id_caso, []))])
    filas.append(["HU-G4-01 a HU-G4-10", "técnico", "CP-T04", "Contrato OpenAPI generado con Schemathesis", "api", contrato(ruta_contrato)])
    return filas


def construir_cobertura(casos: dict) -> list[list[str]]:
    filas = []
    for hu, nombre in HISTORIAS.items():
        de_hu = [c for c, d in sorted(casos.items()) if hu in d["hu"]]
        api = [c for c in de_hu if casos[c]["nivel"] == "api"]
        web = [c for c in de_hu if casos[c]["nivel"] == "web"]
        filas.append([hu, nombre, str(len(api)), str(len(web))])
    return filas


def tabla_md(cabecera: list[str], filas: list[list[str]]) -> str:
    return "\n".join(["| " + " | ".join(cabecera) + " |", "|" + "---|" * len(cabecera)] + ["| " + " | ".join(f) + " |" for f in filas])


def tabla_html(cabecera: list[str], filas: list[list[str]]) -> str:
    def clase(celda: str) -> str:
        for estado in ("passed", "xfailed", "failed", "skipped", "sin ejecutar"):
            if celda.startswith(estado):
                return f' class="{estado.split()[0]}"'
        return ""
    cuerpo = "".join("<tr>" + "".join(f"<td{clase(c)}>{html.escape(c)}</td>" for c in f) + "</tr>" for f in filas)
    return f"<table><thead><tr>{''.join(f'<th>{html.escape(c)}</th>' for c in cabecera)}</tr></thead><tbody>{cuerpo}</tbody></table>"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", default="features", type=Path)
    parser.add_argument("--reportes", default="reportes", type=Path)
    parser.add_argument("--matriz", default="docs/trazabilidad.md", type=Path)
    parser.add_argument("--sitio", type=Path)
    args = parser.parse_args()

    casos = leer_casos(args.features)
    resultados = leer_resultados(args.reportes / "api" / "junit.xml", args.reportes / "web" / "junit.xml")
    filas = construir_filas(casos, resultados, args.reportes / "contrato" / "junit.xml")
    cobertura = construir_cobertura(casos)

    lima = datetime.now(timezone(timedelta(hours=-5)))
    run = os.environ.get("GITHUB_RUN_NUMBER", "local")
    sha = os.environ.get("GITHUB_SHA", "")[:7] or "sin commit"
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    id_run = os.environ.get("GITHUB_RUN_ID", "")
    enlace = f"https://github.com/{repo}/actions/runs/{id_run}" if repo and id_run else ""
    datos = f"Run **#{run}** · commit `{sha}` · {lima:%Y-%m-%d %H:%M} (hora de Lima)" + (f" · [ver run]({enlace})" if enlace else "")

    cabecera = ["HU", "CA", "Caso", "Título", "Nivel", f"Resultado (run #{run})"]
    cabecera_cobertura = ["HU", "Historia", "Casos API", "Casos web"]
    args.matriz.parent.mkdir(parents=True, exist_ok=True)
    args.matriz.write_text(
        "# Matriz de trazabilidad · G4\n\n"
        "Generada por `.github/scripts/trazabilidad.py` a partir de las etiquetas de `features/` y los JUnit XML del pipeline.\n\n"
        f"{datos}\n\n## Cobertura por historia\n\n{tabla_md(cabecera_cobertura, cobertura)}\n\n"
        f"## HU → caso → resultado\n\n{tabla_md(cabecera, filas)}\n\n"
        "Los casos web se ejecutan 3 veces seguidas: `passed (3/3)` indica las tres pasadas. "
        "`xfailed → DEF-xx` es un fallo esperado enlazado a `docs/defectos.md`.\n",
        encoding="utf-8",
    )

    if args.sitio:
        args.sitio.mkdir(parents=True, exist_ok=True)
        for origen, destino in ((args.reportes / "web" / "html", "web"), (args.reportes / "contrato" / "html", "contrato")):
            if origen.exists():
                shutil.copytree(origen, args.sitio / destino, dirs_exist_ok=True)
        if (args.reportes / "api" / "reporte.html").exists():
            (args.sitio / "api").mkdir(exist_ok=True)
            shutil.copy(args.reportes / "api" / "reporte.html", args.sitio / "api" / "index.html")
        contrato_html = sorted((args.sitio / "contrato").rglob("index.html"))
        ruta_contrato = contrato_html[0].relative_to(args.sitio).as_posix() if contrato_html else "contrato/"
        datos_html = re.sub(r"\[ver run\]\((.+?)\)", r'<a href="\1">ver run</a>',
                            re.sub(r"`(.+?)`", r"<code>\1</code>", re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", datos)))
        (args.sitio / "index.html").write_text(f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Qolqe G4 · Reportes del pipeline</title>
<style>
body{{font:15px/1.5 system-ui,sans-serif;margin:0 auto;max-width:1100px;padding:24px 16px;color:#1f2933}}
h1{{margin-bottom:0}}nav a{{display:inline-block;margin:12px 8px 12px 0;padding:8px 14px;border:1px solid #cbd2d9;border-radius:6px;text-decoration:none}}
.tabla{{overflow-x:auto}}table{{border-collapse:collapse;width:100%}}th,td{{border-bottom:1px solid #e4e7eb;padding:6px 8px;text-align:left;vertical-align:top}}th{{background:#f5f7fa}}
.passed{{color:#17693a;font-weight:600}}.xfailed{{color:#9a5b00;font-weight:600}}.failed{{color:#b42318;font-weight:600}}.skipped,.sin{{color:#616e7c;font-weight:600}}
</style></head><body>
<h1>Qolqe G4 · Contactos y solicitudes de dinero</h1>
<p>{datos_html}</p>
<nav><a href="web/">Reporte web (Playwright)</a><a href="api/">Reporte API (pytest-bdd)</a><a href="{ruta_contrato}">Reporte de contrato (Schemathesis)</a><a href="trazabilidad.md">Matriz en Markdown</a></nav>
<h2>Cobertura por historia</h2><div class="tabla">{tabla_html(cabecera_cobertura, cobertura)}</div>
<h2>HU → caso → resultado</h2><div class="tabla">{tabla_html(cabecera, filas)}</div>
</body></html>
""", encoding="utf-8")


if __name__ == "__main__":
    main()
