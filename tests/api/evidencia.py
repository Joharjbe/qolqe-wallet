"""Evidencia de la API en el reporte de pytest-html: las peticiones y respuestas de cada escenario.

EVIDENCIA=con-imagenes adjunta las de todos los casos. Sin la variable, o con sin-imagenes, solo las de los
fallos y las de los defectos conocidos (xfail con su DEF). Se anota lo que ocurre durante los pasos del
escenario; la preparación de los fixtures (reiniciar datos y reloj) no es evidencia del caso.
"""
import html
import json
import os

import httpx
import pytest
from pytest_html import extras

EVIDENCIA = os.environ.get("EVIDENCIA", "sin-imagenes")
CON_IMAGENES = EVIDENCIA == "con-imagenes"
LARGO_MAXIMO = 4000
_CLAVE = pytest.StashKey[list]()
_intercambios: list[dict] | None = None
_enviar_original = httpx.Client.send


def _legible(contenido: bytes | str) -> str:
    texto = contenido.decode("utf-8", "replace") if isinstance(contenido, bytes) else contenido
    try:
        datos = json.loads(texto)
    except ValueError:
        return texto[:LARGO_MAXIMO]
    if isinstance(datos, dict) and "access_token" in datos:
        datos = {**datos, "access_token": "***"}
    return json.dumps(datos, ensure_ascii=False, indent=2)[:LARGO_MAXIMO]


def _enviar_y_anotar(cliente, peticion, **opciones):
    respuesta = _enviar_original(cliente, peticion, **opciones)
    if _intercambios is not None and not opciones.get("stream"):
        cabeceras = {k: ("Bearer ***" if k.lower() == "authorization" else v) for k, v in peticion.headers.items()
                     if k.lower() in {"authorization", "content-type"}}
        _intercambios.append({
            "peticion": f"{peticion.method} {peticion.url.raw_path.decode()}",
            "cabeceras": cabeceras,
            "cuerpo": _legible(peticion.content) if peticion.content else "",
            "estado": respuesta.status_code,
            "respuesta": _legible(respuesta.content),
        })
    return respuesta


httpx.Client.send = _enviar_y_anotar


def _html(intercambios: list[dict]) -> str:
    bloques = []
    for i, x in enumerate(intercambios, 1):
        detalle = (f"{x['peticion']}\n{json.dumps(x['cabeceras'], ensure_ascii=False)}\n{x['cuerpo']}\n\n"
                   f"→ {x['estado']}\n{x['respuesta']}")
        bloques.append(f"<details><summary>{i}. {html.escape(x['peticion'])} → {x['estado']}</summary>"
                       f"<pre>{html.escape(detalle)}</pre></details>")
    return f"<div><strong>Peticiones y respuestas ({len(intercambios)})</strong>{''.join(bloques)}</div>"


@pytest.hookimpl(wrapper=True)
def pytest_runtest_call(item):
    global _intercambios
    _intercambios = item.stash.setdefault(_CLAVE, [])
    try:
        return (yield)
    finally:
        _intercambios = None


@pytest.hookimpl(wrapper=True)
def pytest_fixture_setup(fixturedef, request):
    """pytest-bdd prepara los fixtures (como `s`) dentro de la llamada: esa preparación no se anota."""
    global _intercambios
    en_curso, _intercambios = _intercambios, None
    try:
        return (yield)
    finally:
        _intercambios = en_curso


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    reporte = yield
    intercambios = item.stash.get(_CLAVE, None)
    fallo_o_defecto = reporte.failed or hasattr(reporte, "wasxfail")
    if reporte.when == "call" and intercambios and (CON_IMAGENES or fallo_o_defecto):
        reporte.extras = [*getattr(reporte, "extras", []), extras.html(_html(intercambios))]
    return reporte


@pytest.hookimpl(optionalhook=True)
def pytest_html_report_title(report):
    report.title = f"Qolqe · API · evidencia: {EVIDENCIA}"


__all__ = ["pytest_fixture_setup", "pytest_html_report_title", "pytest_runtest_call", "pytest_runtest_makereport"]
