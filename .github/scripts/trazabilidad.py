"""Une las etiquetas de los .feature (@HU, @CA, @CP, @DEF, @tecnico) con los JUnit XML del pipeline.

Salidas de un run: la matriz HU → caso → resultado (Markdown y portada HTML de GitHub Pages), un JUnit
canónico con un caso por CP (lo importa Kiwi TCMS), run.json y las capturas de evidencia por CP.
Con --solo-historial suma un run.json al historial acumulado (historial.json y historial.html).
Con --verificar revisa las etiquetas sin ejecutar nada (job estatico).
"""
import argparse
import html
import json
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from itertools import pairwise
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from casos import (
    CP_CONTRATO,
    ESTADOS,
    GRUPO_JUNIT,
    MODULOS,
    caso_contrato,
    hu_de_operacion,
    leer_casos,
    leer_criterios,
    leer_defectos,
    leer_historias,
    leer_resultados,
    metadatos_run,
    resultados_por_caso,
    resumen_estados,
)

NIVELES = ["api", "web", "contrato"]
ESTILO = """
:root{--texto:#1f2933;--suave:#616e7c;--borde:#e4e7eb;--fondo:#fff;--cabecera:#f5f7fa;--ok:#17693a;--xf:#9a5b00;--mal:#b42318;--enlace:#1d4ed8}
@media (prefers-color-scheme: dark){:root{--texto:#e4e7eb;--suave:#9aa5b1;--borde:#3e4c59;--fondo:#1f2933;--cabecera:#323f4b;--ok:#6fcf97;--xf:#f2c94c;--mal:#ff8a80;--enlace:#93c5fd}}
a{color:var(--enlace)}td:first-child{white-space:nowrap}
body{font:15px/1.5 system-ui,sans-serif;margin:0 auto;max-width:1200px;padding:24px 16px;color:var(--texto);background:var(--fondo)}
h1{margin-bottom:0}nav a{display:inline-block;margin:12px 8px 12px 0;padding:8px 14px;border:1px solid var(--borde);border-radius:6px;text-decoration:none;color:inherit}
.tabla{overflow-x:auto}table{border-collapse:collapse;width:100%}th,td{border-bottom:1px solid var(--borde);padding:6px 8px;text-align:left;vertical-align:top}th{background:var(--cabecera)}
.passed{color:var(--ok);font-weight:600}.xfailed{color:var(--xf);font-weight:600}.failed,.flaky{color:var(--mal);font-weight:600}.skipped,.sin{color:var(--suave);font-weight:600}
.celda{display:inline-block;width:1.4em;text-align:center}small{color:var(--suave)}
"""
SIMBOLO = {"passed": "✓", "xfailed": "◐", "flaky": "≈", "failed": "✗", "skipped": "–", "sin ejecutar": "·"}


def texto_resultado(caso: dict, datos: dict) -> str:
    estado, total = datos["estado"], datos["ejecuciones"]
    if estado == "sin ejecutar":
        return estado
    if estado in ("failed", "flaky"):
        return f"{estado} ({datos['fallaron']}/{total})"
    if estado == "xfailed":
        return f"xfailed → {', '.join(caso['defectos']) or 'fallo esperado'}"
    return estado if estado == "skipped" else f"passed ({total}/{total})"


def verificar(casos: dict, problemas: list[str], historias: dict, defectos: dict, criterios: dict) -> int:
    errores, avisos = list(problemas), []
    for id_caso, c in sorted(casos.items()):
        donde = f"{c['archivo']}:{c['linea']} {id_caso}"
        if id_caso[-1].isalpha():
            avisos.append(f"{donde}: el ID tiene sufijo de letra; conviene renumerarlo")
        if not c["hu"]:
            errores.append(f"{donde}: falta la etiqueta @HU")
        for hu in c["hu"]:
            if historias and hu not in historias:
                errores.append(f"{donde}: @{hu} no existe en docs/requisitos.md")
        if not c["ca"]:
            (avisos if c["tipo"] == "técnico" else errores).append(f"{donde}: falta la etiqueta @CA")
        for par in c["hu_ca"]:
            hu, _, ca = par.rpartition(":")
            if not hu:
                errores.append(f"{donde}: @{ca} va antes de cualquier @HU")
            elif hu in criterios and ca not in criterios[hu]:
                errores.append(f"{donde}: @{hu} no tiene {ca} en docs/requisitos.md (cada @CA va después de sus @HU)")
        if c["nivel"] == "web" and c["falla_esperada"] and not c["defectos"]:
            errores.append(f"{donde}: @fail sin @DEF-xx que explique el fallo esperado")
        if c["nivel"] == "web" and c["defectos"] and not c["falla_esperada"]:
            avisos.append(f"{donde}: @DEF sin @fail (en la web el fallo esperado se marca con @fail)")
        for d in c["defectos"]:
            if d not in defectos:
                avisos.append(f"{donde}: @{d} todavía no está en docs/defectos.md")
    for hu in historias:
        if not any(hu in c["hu"] for c in casos.values()):
            avisos.append(f"{hu}: la historia no tiene casos")
    for a in avisos:
        print(f"::warning::{a}")
    for e in errores:
        print(f"::error::{e}")
    print(f"Trazabilidad: {len(casos)} casos, {len(errores)} errores, {len(avisos)} avisos.")
    return 1 if errores else 0


def tabla_md(cabecera: list[str], filas: list[list[str]]) -> str:
    return "\n".join(["| " + " | ".join(cabecera) + " |", "|" + "---|" * len(cabecera)] + ["| " + " | ".join(f) + " |" for f in filas])


def tabla_html(cabecera: list[str], filas: list[list[str]]) -> str:
    def clase(celda: str) -> str:
        estado = next((e for e in ESTADOS if celda.startswith(e)), None)
        return f' class="{estado.split()[0]}"' if estado else ""
    cuerpo = "".join("<tr>" + "".join(f"<td{clase(c)}>{html.escape(c)}</td>" for c in f) + "</tr>" for f in filas)
    return f"<table><thead><tr>{''.join(f'<th>{html.escape(c)}</th>' for c in cabecera)}</tr></thead><tbody>{cuerpo}</tbody></table>"


def filas_resumen(casos: dict, por_caso: dict) -> list[list[str]]:
    grupos = Counter()
    for id_caso, c in casos.items():
        grupos[(c["modulo"], c["nivel"], c["tipo"], por_caso[id_caso]["estado"])] += 1
    filas = []
    for modulo in MODULOS:
        for nivel in NIVELES:
            for tipo in ("funcional", "técnico"):
                cuenta = [grupos[(modulo, nivel, tipo, e)] for e in ESTADOS]
                if sum(cuenta):
                    filas.append([modulo, nivel, tipo, str(sum(cuenta)), *map(str, cuenta)])
    return filas


def filas_cobertura(casos: dict, por_caso: dict, historias: dict) -> list[list[str]]:
    filas = []
    for hu, nombre in historias.items():
        de_hu = [c for c in casos.values() if hu in c["hu"]]
        por_nivel = [str(sum(c["nivel"] == n for c in de_hu)) for n in NIVELES]
        estados = Counter(por_caso[c["id"]]["estado"] for c in de_hu)
        filas.append([hu, nombre, *por_nivel, str(sum(c["tipo"] == "técnico" for c in de_hu)),
                      ", ".join(f"{n} {e}" for e, n in estados.most_common()) or "sin casos"])
    return filas


def filas_casos(casos: dict, por_caso: dict, modulo: str) -> list[list[str]]:
    filas = []
    for id_caso, c in sorted(casos.items(), key=lambda par: (min(par[1]["hu"], default="~"), par[0])):
        if c["modulo"] == modulo:
            filas.append([", ".join(c["hu"]) or "—", ", ".join(c["ca"]) or "—", id_caso, c["titulo"],
                          c["nivel"], c["tipo"], texto_resultado(c, por_caso[id_caso])])
    return filas


def filas_contrato(operaciones: dict) -> list[list[str]]:
    return [[op, ", ".join(hu_de_operacion(op)) or "—", estado] for op, estado in operaciones.items()]


def filas_defectos(casos: dict, por_caso: dict) -> list[list[str]]:
    por_def = {}
    for id_caso, c in sorted(casos.items()):
        for d in c["defectos"]:
            por_def.setdefault(d, []).append(f"{id_caso} ({por_caso[id_caso]['estado']})")
    return [[d, ", ".join(v)] for d, v in sorted(por_def.items())]


def encabezado(run: dict) -> str:
    sha = run["sha"][:7] or "sin commit"
    texto = (f"Run **#{run['numero']}** (intento {run['intento']}) · commit `{sha}` · {run['evento']}"
             f"{' · ' + run['rama'] if run['rama'] else ''} · evidencia: {run['evidencia']} · "
             f"veredicto: **{run.get('conclusion') or '—'}** · {run['fecha'][:16].replace('T', ' ')} (hora de Lima)")
    if not run["run_id"]:
        # Una corrida local no es evidencia del pipeline: el job reportes vuelve a generar la matriz en cada run.
        texto += (" · **corrida local, fuera de GitHub Actions**: el job `reportes` del pipeline genera esta matriz"
                  " en cada run (artefacto `trazabilidad`)")
    return texto + (f" · [ver run]({run['url']})" if run["url"] else "")


def md_a_html(texto: str) -> str:
    texto = html.escape(texto)
    texto = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", texto)
    texto = re.sub(r"`(.+?)`", r"<code>\1</code>", texto)
    return re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', texto)


CABECERAS = {
    "resumen": ["Módulo", "Nivel", "Tipo", "Casos", *ESTADOS],
    "cobertura": ["HU", "Historia", "API", "Web", "Contrato", "Técnicos", "Resultados"],
    "casos": ["HU", "CA", "Caso", "Título", "Nivel", "Tipo", "Resultado"],
    "contrato": ["Operación", "HU", "Resultado"],
    "defectos": ["Defecto", "Casos (estado en este run)"],
}
NOTA = ("Los casos web se ejecutan 3 veces seguidas: `passed (3/3)` indica las tres pasadas. Un esquema de escenario "
        "cuenta cada ejemplo. `xfailed → DEF-xx` es un fallo esperado enlazado a `docs/defectos.md`. `flaky` alternó entre "
        "pasar y fallar. `sin ejecutar` es un caso diseñado que no corrió en este run.")


def escribir_matriz(ruta: Path, run: dict, secciones: dict) -> None:
    partes = ["# Matriz de trazabilidad · núcleo y G4\n",
              "Generada por `.github/scripts/trazabilidad.py` a partir de las etiquetas de `features/` y los JUnit XML del pipeline.\n",
              f"{encabezado(run)}\n"]
    for titulo, clave, filas in secciones["orden"]:
        partes.append(f"## {titulo}\n\n{tabla_md(CABECERAS[clave], filas) if filas else '_Sin datos en este run._'}\n")
    partes.append(NOTA + "\n")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("\n".join(partes), encoding="utf-8")


def pagina(titulo: str, cuerpo: str) -> str:
    return (f'<!doctype html>\n<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f"<title>{html.escape(titulo)}</title><style>{ESTILO}</style></head><body>{cuerpo}</body></html>\n")


def escribir_sitio(sitio: Path, reportes: Path, run: dict, secciones: dict) -> None:
    sitio.mkdir(parents=True, exist_ok=True)
    for origen, destino in ((reportes / "web" / "html", "web"), (reportes / "contrato" / "html", "contrato")):
        if origen.exists():
            shutil.copytree(origen, sitio / destino, dirs_exist_ok=True)
    if (reportes / "api" / "reporte.html").exists():
        (sitio / "api").mkdir(exist_ok=True)
        shutil.copy(reportes / "api" / "reporte.html", sitio / "api" / "index.html")
    contrato_html = sorted((sitio / "contrato").rglob("index.html"))
    ruta_contrato = contrato_html[0].relative_to(sitio).as_posix() if contrato_html else "contrato/"
    nav = (f'<nav><a href="web/">Reporte web (Playwright)</a><a href="api/">Reporte API (pytest-bdd)</a>'
           f'<a href="{ruta_contrato}">Reporte de contrato (Schemathesis)</a><a href="historial.html">Historial de ejecuciones</a>'
           f'<a href="trazabilidad.md">Matriz en Markdown</a><a href="junit-cp.xml">JUnit por caso</a><a href="run.json">run.json</a></nav>')
    cuerpo = [f"<h1>Qolqe · Núcleo y G4 · Reportes del pipeline</h1><p>{md_a_html(encabezado(run))}</p>{nav}"]
    for titulo, clave, filas in secciones["orden"]:
        cuerpo.append(f"<h2>{html.escape(titulo)}</h2><div class=\"tabla\">{tabla_html(CABECERAS[clave], filas)}</div>")
    cuerpo.append(f"<p><small>{md_a_html(NOTA)}</small></p>")
    (sitio / "index.html").write_text(pagina("Qolqe · Reportes del pipeline", "".join(cuerpo)), encoding="utf-8")


def copiar_evidencias(destino: Path, evidencias: dict, reportes: Path) -> dict[str, list[str]]:
    """Capturas del JUnit web copiadas como evidencias/CP-W01_r0.png; el reporte de API va completo."""
    copiadas = {}
    destino.mkdir(parents=True, exist_ok=True)
    for id_caso, archivos in sorted(evidencias.items()):
        for i, archivo in enumerate(archivos):
            nombre = f"{id_caso}_r{i}.png"
            shutil.copy(archivo, destino / nombre)
            copiadas.setdefault(id_caso, []).append(f"{destino.name}/{nombre}")
    if (reportes / "api" / "reporte.html").exists():
        shutil.copy(reportes / "api" / "reporte.html", destino / "api-reporte.html")
    return copiadas


def escribir_junit_cp(ruta: Path, casos: dict, por_caso: dict, resultados: dict, run: dict, evidencias: dict) -> None:
    """Un <testcase> por CP. failed/flaky → failure; xfailed → skipped type="xfail" (WAIVED en Kiwi, con su DEF);
    sin ejecutar → skipped type="sin-ejecutar"; passed → sin hijos. classname = módulo.nivel."""
    raiz = ET.Element("testsuites", name=f"Qolqe · run #{run['numero']}.{run['intento']}")
    suites = {}
    for id_caso, c in sorted(casos.items()):
        grupo = f"{GRUPO_JUNIT[c['modulo']]}.{c['nivel']}"
        suite = suites.get(grupo)
        if suite is None:
            suite = suites[grupo] = ET.SubElement(raiz, "testsuite", name=grupo)
        datos = por_caso[id_caso]
        ejecuciones = resultados["ejecuciones"].get(id_caso, [])
        tiempo = sum(e["tiempo"] for e in ejecuciones)
        caso = ET.SubElement(suite, "testcase", classname=grupo, name=f"{id_caso} {c['titulo']}", time=f"{tiempo:.3f}")
        propiedades = ET.SubElement(caso, "properties")
        valores = [("hu", ", ".join(c["hu"])), ("ca", ", ".join(c["hu_ca"] or c["ca"])), ("defecto", ", ".join(c["defectos"])),
                   ("modulo", c["modulo"]), ("nivel", c["nivel"]), ("tipo", c["tipo"]), ("estado", datos["estado"]),
                   ("ejecuciones", f"{datos['pasaron']}/{datos['ejecuciones']}"), ("archivo", f"{c['archivo']}:{c['linea']}")]
        valores += [("evidencia", e) for e in evidencias.get(id_caso, [])]
        for nombre, valor in valores:
            if valor:
                ET.SubElement(propiedades, "property", name=nombre, value=valor)
        estado = datos["estado"]
        if estado in ("failed", "flaky"):
            mensaje = (f"Inestable: falló {datos['fallaron']} de {datos['ejecuciones']} ejecuciones" if estado == "flaky"
                       else f"Fallaron {datos['fallaron']} de {datos['ejecuciones']} ejecuciones")
            ET.SubElement(caso, "failure", message=mensaje, type=estado).text = "\n".join(
                f"{e['estado']}: {e['nombre']} {e['detalle']}".strip() for e in ejecuciones if e["estado"] in ("failed", "flaky"))
        elif estado == "xfailed":
            ET.SubElement(caso, "skipped", type="xfail", message=f"Defecto conocido {', '.join(c['defectos']) or ''} (fallo esperado)".replace("  ", " "))
        elif estado in ("skipped", "sin ejecutar"):
            ET.SubElement(caso, "skipped", type=estado.replace(" ", "-"), message=f"{estado} en este run")
        if id_caso == CP_CONTRATO:
            detalle = "\n".join(f"{op}: {e}" for op, e in resultados["operaciones"].items())
        else:
            detalle = "\n".join(f"{e['estado']}: {e['nombre']}" for e in ejecuciones)
        if detalle:
            ET.SubElement(caso, "system-out").text = detalle
    for suite in suites.values():
        hijos = list(suite)
        suite.set("tests", str(len(hijos)))
        suite.set("failures", str(sum(h.find("failure") is not None for h in hijos)))
        suite.set("skipped", str(sum(h.find("skipped") is not None for h in hijos)))
        suite.set("errors", "0")
    ET.indent(raiz)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(raiz).write(ruta, encoding="utf-8", xml_declaration=True)


def armar_run(run: dict, casos: dict, por_caso: dict) -> dict:
    por_modulo = {}
    for id_caso, c in casos.items():
        grupo = por_modulo.setdefault(c["modulo"], dict.fromkeys(ESTADOS, 0))
        grupo[por_caso[id_caso]["estado"]] += 1
    return {**run, "totales": resumen_estados(por_caso), "por_modulo": por_modulo, "casos": {
        id_caso: {**por_caso[id_caso], "titulo": c["titulo"], "modulo": c["modulo"], "nivel": c["nivel"],
                  "tipo": c["tipo"], "hu": c["hu"], "defectos": c["defectos"]}
        for id_caso, c in sorted(casos.items())}}


def leer_historial(rutas: list[Path]) -> list[dict]:
    """Une los historiales previos (el de Pages y el de la caché) por id de run; un archivo ausente o roto cuenta como vacío."""
    runs = {}
    for ruta in rutas:
        try:
            datos = json.loads(ruta.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for r in datos.get("runs", []) if isinstance(datos, dict) else []:
            runs[r["id"]] = r
    return list(runs.values())


def clave_run(r: dict) -> tuple:
    numero = int(r["numero"]) if str(r["numero"]).isdigit() else 0
    return (numero, int(r.get("intento", 1)), r.get("fecha", ""))


def clasificar_cambios(ultimos: list[dict]) -> tuple[bool, str | None]:
    """Separa un caso inestable de una regresión (o una corrección) que cambió el resultado una sola vez.

    Inestable: fue flaky en algún run, el mismo commit dio a la vez un resultado esperado y uno fallido (por ejemplo, un
    re-run), o alternó dos o más veces. Un único cambio entre esperado (passed/xfailed) y fallido devuelve el run del cambio.
    """
    if any(u["estado"] == "flaky" for u in ultimos):
        return True, None
    secuencia = [u for u in ultimos if u["estado"] in ("passed", "xfailed", "failed")]
    por_commit = {}
    for u in secuencia:
        if u.get("sha"):
            por_commit.setdefault(u["sha"], set()).add(u["estado"] == "failed")
    if any(len(v) > 1 for v in por_commit.values()):
        return True, None
    cambios = [b for a, b in pairwise(secuencia) if (a["estado"] == "failed") != (b["estado"] == "failed")]
    if len(cambios) >= 2:
        return True, None
    if cambios:
        u = cambios[0]
        return False, f"#{u['run']}" + (f".{u['intento']}" if int(u.get("intento", 1)) > 1 else "")
    return False, None


def etiqueta_run(r: dict) -> str:
    if str(r["numero"]).isdigit():
        return f"#{r['numero']}" + (f".{r['intento']}" if int(r.get("intento", 1)) > 1 else "")
    return f"{r['numero']} {r.get('fecha', '')[11:16]}"


def armar_historial(runs: list[dict], maximo: int) -> dict:
    runs = sorted(runs, key=clave_run)[-maximo:]
    casos = {}
    for r in runs:
        for id_caso, datos in r["casos"].items():
            c = casos.setdefault(id_caso, {"conteo": dict.fromkeys(ESTADOS, 0), "ultimos": []})
            c.update({k: datos.get(k) for k in ("titulo", "modulo", "nivel", "tipo", "hu", "defectos")})
            c["conteo"][datos["estado"]] += 1
            c["ultimos"].append({"id": r["id"], "run": r["numero"], "intento": r.get("intento", 1), "sha": r.get("sha", ""),
                                 "estado": datos["estado"]})
            if datos["estado"] != "sin ejecutar":
                c.setdefault("primera_vez", {"run": r["numero"], "fecha": r["fecha"]})
                c["ultima_vez"] = {"run": r["numero"], "fecha": r["fecha"]}
    for c in casos.values():
        ejecutados = sum(v for k, v in c["conteo"].items() if k not in ("sin ejecutar", "skipped"))
        esperados = c["conteo"]["passed"] + c["conteo"]["xfailed"]
        c["estabilidad"] = round(100 * esperados / ejecutados, 1) if ejecutados else None
        c["inestable"], c["cambio_en"] = clasificar_cambios(c["ultimos"])
    resumen = [{k: r.get(k, "") for k in ("id", "numero", "intento", "sha", "rama", "evento", "evidencia", "conclusion", "fecha", "url")}
               | {"totales": r["totales"]}
               for r in runs]
    return {"maximo": maximo, "runs": runs, "resumen": resumen, "casos": dict(sorted(casos.items()))}


def escribir_historial(sitio: Path, historial: dict, columnas: int = 15) -> None:
    sitio.mkdir(parents=True, exist_ok=True)
    (sitio / "historial.json").write_text(json.dumps(historial, ensure_ascii=False, indent=1), encoding="utf-8")
    ultimos = historial["runs"][-columnas:]
    cab_runs = "".join(f'<th title="{html.escape(r["fecha"][:16])} · {html.escape(r["sha"][:7])}">{html.escape(etiqueta_run(r))}</th>'
                       for r in ultimos)
    filas = []
    for id_caso, c in historial["casos"].items():
        # Cada intento es su propia columna: un re-run no reemplaza al intento anterior.
        por_run = {u.get("id") or (u["run"], u["intento"]): u["estado"] for u in c["ultimos"]}
        estados = [por_run.get(r["id"], por_run.get((r["numero"], r.get("intento", 1)), "sin ejecutar")) for r in ultimos]
        celdas = "".join(f'<td><span class="celda {e.split()[0]}">{SIMBOLO[e]}</span></td>' for e in estados)
        conteo = c["conteo"]
        estabilidad = "—" if c["estabilidad"] is None else f"{c['estabilidad']} %"
        primera, ultima = c.get("primera_vez", {}), c.get("ultima_vez", {})
        marca = (' <span class="flaky">inestable</span>' if c["inestable"]
                 else f' <span class="xfailed">cambió en {html.escape(c["cambio_en"])}</span>' if c.get("cambio_en") else "")
        filas.append(
            f"<tr><td>{html.escape(id_caso)}</td><td>{html.escape(c['titulo'] or '')}</td><td>{html.escape(c['modulo'] or '')}</td>"
            f"<td>{html.escape(c['nivel'] or '')}</td><td>{html.escape(c['tipo'] or '')}</td>{celdas}"
            f"<td>{conteo['passed']}/{conteo['failed']}/{conteo['xfailed']}/{conteo['flaky']}</td><td>{estabilidad}{marca}</td>"
            f"<td>#{primera.get('run', '—')} · #{ultima.get('run', '—')}</td></tr>")
    leyenda = " · ".join(f'<span class="{e.split()[0]}">{SIMBOLO[e]}</span> {e}' for e in ESTADOS)
    cuerpo = (
        f"<h1>Historial de ejecuciones · núcleo y G4</h1><p>Últimos {len(historial['runs'])} runs publicados (máximo {historial['maximo']}); "
        f"la grilla muestra los últimos {len(ultimos)}. <a href=\"index.html\">Volver a la portada</a> · "
        f"<a href=\"historial.json\">historial.json</a></p><p>{leyenda}</p><div class=\"tabla\"><table><thead><tr>"
        f"<th>Caso</th><th>Título</th><th>Módulo</th><th>Nivel</th><th>Tipo</th>{cab_runs}"
        f"<th>pasó/falló/xfail/flaky</th><th>Estabilidad</th><th>Primera · última vez</th></tr></thead>"
        f"<tbody>{''.join(filas)}</tbody></table></div>"
        "<p><small>Cada intento de un run es una columna (#N.2 es el re-run de #N): un re-run no borra el intento anterior. "
        "Estabilidad: porcentaje de ejecuciones con el resultado esperado (passed o xfailed con su DEF). "
        "<em>inestable</em>: fue flaky en algún run, el mismo commit pasó y falló (por ejemplo, en un re-run) o alternó dos o "
        "más veces. <em>cambió en #N</em>: un solo cambio entre esperado y fallido, típico de una regresión o de una "
        "corrección.</small></p>")
    (sitio / "historial.html").write_text(pagina("Qolqe · Historial de ejecuciones", cuerpo), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--features", default="features", type=Path)
    parser.add_argument("--requisitos", default="docs/requisitos.md", type=Path)
    parser.add_argument("--defectos", default="docs/defectos.md", type=Path)
    parser.add_argument("--reportes", default="reportes", type=Path, help="Carpeta con api/, web/ y contrato/ (cada uno con junit.xml)")
    parser.add_argument("--matriz", default="docs/trazabilidad.md", type=Path)
    parser.add_argument("--sitio", type=Path, help="Carpeta del sitio de GitHub Pages")
    parser.add_argument("--junit-cp", type=Path, help="JUnit canónico: un caso por CP")
    parser.add_argument("--run-json", type=Path, help="Datos del run (salida; entrada con --solo-historial)")
    parser.add_argument("--evidencias", type=Path, help="Carpeta donde copiar las capturas por CP")
    parser.add_argument("--conclusion", default="", help="Resultado de las etapas de prueba (success o failure)")
    parser.add_argument("--verificar", action="store_true", help="Solo revisa las etiquetas; sale con 1 si hay errores")
    parser.add_argument("--solo-historial", action="store_true", help="Suma --run-json al historial y escribe historial.*")
    parser.add_argument("--historial-previo", nargs="*", default=[], type=Path)
    parser.add_argument("--historial-max", default=30, type=int)
    args = parser.parse_args()

    if args.solo_historial:
        run = json.loads(args.run_json.read_text(encoding="utf-8"))
        historial = armar_historial([*[r for r in leer_historial(args.historial_previo) if r["id"] != run["id"]], run], args.historial_max)
        escribir_historial(args.sitio, historial)
        print(f"Historial: {len(historial['runs'])} runs, {len(historial['casos'])} casos.")
        return

    casos, problemas = leer_casos(args.features)
    historias = leer_historias(args.requisitos)
    defectos = leer_defectos(args.defectos)
    if args.verificar:
        sys.exit(verificar(casos, problemas, historias, defectos, leer_criterios(args.requisitos)))

    resultados = leer_resultados(args.reportes)
    casos[CP_CONTRATO] = caso_contrato(list(resultados["operaciones"]))
    por_caso = resultados_por_caso(casos, resultados)
    run = metadatos_run(conclusion=args.conclusion)
    secciones = {"orden": [
        ("Resumen por módulo, nivel y tipo", "resumen", filas_resumen(casos, por_caso)),
        ("Cobertura por historia", "cobertura", filas_cobertura(casos, por_caso, historias)),
        ("Núcleo: HU → caso → resultado", "casos", filas_casos(casos, por_caso, "núcleo")),
        ("G4: HU → caso → resultado", "casos", filas_casos(casos, por_caso, "G4")),
        (f"Contrato ({CP_CONTRATO}): operación → resultado", "contrato", filas_contrato(resultados["operaciones"])),
        ("Defectos → casos", "defectos", filas_defectos(casos, por_caso)),
    ]}
    escribir_matriz(args.matriz, run, secciones)
    evidencias_dir = args.evidencias or (args.sitio / "evidencias" if args.sitio else None)
    evidencias = copiar_evidencias(evidencias_dir, resultados["evidencias"], args.reportes) if evidencias_dir else {}
    if args.sitio:
        escribir_sitio(args.sitio, args.reportes, run, secciones)
    if args.junit_cp:
        escribir_junit_cp(args.junit_cp, casos, por_caso, resultados, run, evidencias)
    if args.run_json:
        args.run_json.parent.mkdir(parents=True, exist_ok=True)
        args.run_json.write_text(json.dumps(armar_run(run, casos, por_caso), ensure_ascii=False, indent=1), encoding="utf-8")
    totales = resumen_estados(por_caso)
    print("Trazabilidad: " + ", ".join(f"{v} {k}" for k, v in totales.items() if v))
    if resultados["sin_cp"]:
        print(f"::warning::{len(resultados['sin_cp'])} resultados de JUnit sin CP reconocible, por ejemplo: {resultados['sin_cp'][0]}")


if __name__ == "__main__":
    main()
