"""Modelo de trazabilidad compartido: casos de los .feature, resultados de los JUnit y datos del run.

Lo usan .github/scripts/trazabilidad.py (pipeline) y scripts/kiwi_sincronizar.py (Kiwi TCMS).
"""
import os
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

LIMA = timezone(timedelta(hours=-5))
# Reconoce el CP en un título ("CP-NW16 ...") y en un nombre de pytest ("test_cpna52_consultar_mi_saldo").
# Acepta un sufijo de una letra (CP-NA18b) para no perder el caso, aunque --verificar avisa que rompe la numeración.
ID_CASO = re.compile(r"(?<![a-z])cp[-_]?([a-z]{1,2})[-_]?(\d{2,3})([a-z]?)(?![a-z\d])", re.IGNORECASE)
CP_TAG = re.compile(r"CP-[A-Z]{1,2}\d{2,3}[a-z]?")
HU_TAG = re.compile(r"HU-(?:N|G\d)-\d{2}")
CA_TAG = re.compile(r"CA\d+")
DEF_TAG = re.compile(r"DEF-[\w-]+")
ESCENARIO = re.compile(r"(?:Escenario|Esquema del escenario|Ejemplo): ?(.*)")
# CP-T04 no tiene escenario Gherkin: es la corrida de Schemathesis contra el contrato OpenAPI.
CP_CONTRATO = "CP-T04"
# Historias que cubre cada operación del contrato (docs/requisitos.md).
HU_POR_OPERACION = [
    (r"^POST /api/contactos$", ["HU-G4-01"]),
    (r"^GET /api/contactos$", ["HU-G4-02"]),
    (r"^PUT /api/contactos/", ["HU-G4-03"]),
    (r"^DELETE /api/contactos/", ["HU-G4-04"]),
    (r"^POST /api/solicitudes$", ["HU-G4-06"]),
    (r"^GET /api/solicitudes$", ["HU-G4-07"]),
    (r"/aceptar$", ["HU-G4-08"]),
    (r"/rechazar$", ["HU-G4-09"]),
    (r"/cancelar$", ["HU-G4-10"]),
    (r"^POST /api/usuarios$", ["HU-N-01"]),
    (r"^POST /api/auth/login$", ["HU-N-02"]),
    (r"^POST /api/auth/logout$", ["HU-N-03"]),
    (r"^GET /api/seguridad/sesiones$", ["HU-N-02", "HU-N-03"]),
    (r"^GET /api/cuentas/me(/saldo)?$", ["HU-N-04"]),
    (r"^PUT /api/cuentas/me$", ["HU-N-05"]),
    (r"^POST /api/cuentas/me/cierre$", ["HU-N-06"]),
    (r"^POST /api/transferencias$", ["HU-N-07", "HU-N-08", "HU-G4-05"]),
    (r"^GET /api/transferencias/comision$", ["HU-N-09"]),
]
ESTADOS = ["passed", "xfailed", "flaky", "failed", "skipped", "sin ejecutar"]


def modulo_de(id_caso: str) -> str:
    return "núcleo" if id_caso.startswith("CP-N") else "G4"


def normalizar_cp(texto: str) -> str | None:
    m = ID_CASO.search(texto)
    return f"CP-{m[1].upper()}{m[2]}{m[3].lower()}" if m else None


def leer_historias(requisitos: Path) -> dict[str, str]:
    """Títulos de las HU del núcleo y de G4, tal como están en docs/requisitos.md."""
    historias = {}
    if requisitos.exists():
        for m in re.finditer(r"^### (HU-(?:N|G4)-\d{2}) · (.+?) ·", requisitos.read_text(encoding="utf-8"), re.MULTILINE):
            historias[m[1]] = m[2]
    return historias


def leer_defectos(defectos: Path) -> dict[str, str]:
    """DEF-xx → ancla de su sección en docs/defectos.md (el slug que genera GitHub para el título)."""
    resultado = {}
    if defectos.exists():
        for m in re.finditer(r"^## (DEF-[\w-]+): (.+)$", defectos.read_text(encoding="utf-8"), re.MULTILINE):
            titulo = f"{m[1]}: {m[2]}".lower()
            resultado[m[1]] = re.sub(r"[^\w\- ]", "", titulo).replace(" ", "-")
    return resultado


def _pares_hu_ca(etiquetas: list[str]) -> list[str]:
    """Cada @CA va con las @HU que lo preceden: "@HU-G4-07 @CA2 @HU-G4-08 @CA4" → HU-G4-07:CA2, HU-G4-08:CA4."""
    pares, grupo, recien_ca = [], [], False
    for e in etiquetas:
        if HU_TAG.fullmatch(e):
            grupo = [e] if recien_ca else [*grupo, e]
            recien_ca = False
        elif CA_TAG.fullmatch(e):
            pares += [f"{hu}:{e}" for hu in grupo] or [e]
            recien_ca = True
    return list(dict.fromkeys(pares))


def leer_casos(carpeta: Path, raiz: Path | None = None) -> tuple[dict[str, dict], list[str]]:
    """Casos por CP a partir de las etiquetas de los .feature. Devuelve también los problemas de estructura."""
    raiz = raiz or carpeta.parent
    casos, problemas = {}, []
    for feature in sorted(carpeta.rglob("*.feature")):
        nivel = "web" if "web" in feature.relative_to(carpeta).parts[:-1] else "api"
        archivo = feature.relative_to(raiz).as_posix() if feature.is_relative_to(raiz) else feature.as_posix()
        de_feature, pendientes, actual = [], [], None
        for numero, linea in enumerate(feature.read_text(encoding="utf-8").splitlines(), 1):
            texto = linea.strip()
            if texto.startswith("@"):
                pendientes += [e.lstrip("@") for e in texto.split() if e.startswith("@")]
                continue
            if texto.startswith("Característica:"):
                de_feature, pendientes = pendientes, []
            elif m := ESCENARIO.match(texto):
                etiquetas = list(dict.fromkeys(de_feature + pendientes))
                pendientes = []
                id_titulo = (m[1].split() or [""])[0]
                cps = [e for e in etiquetas if CP_TAG.fullmatch(e)]
                id_caso = cps[0] if cps else (id_titulo if CP_TAG.fullmatch(id_titulo) else None)
                donde = f"{archivo}:{numero}"
                if not id_caso:
                    problemas.append(f"{donde}: el escenario no tiene @CP ni CP en el título")
                    actual = None
                    continue
                if len(cps) > 1:
                    problemas.append(f"{donde}: más de una etiqueta @CP ({', '.join(cps)})")
                if id_titulo != id_caso:
                    problemas.append(f"{donde}: el título empieza con {id_titulo or '(nada)'} pero la etiqueta es @{id_caso}")
                if id_caso in casos:
                    problemas.append(f"{donde}: {id_caso} repetido (ya está en {casos[id_caso]['archivo']}:{casos[id_caso]['linea']})")
                tipo = "técnico" if "tecnico" in etiquetas or id_caso.startswith("CP-T") else "funcional"
                actual = casos[id_caso] = {
                    "id": id_caso, "titulo": m[1][len(id_titulo):].strip() if id_titulo == id_caso else m[1],
                    "nivel": nivel, "modulo": modulo_de(id_caso), "tipo": tipo,
                    "hu": [e for e in etiquetas if HU_TAG.fullmatch(e)],
                    "ca": [e for e in etiquetas if CA_TAG.fullmatch(e)],
                    "hu_ca": _pares_hu_ca(etiquetas),
                    "defectos": [e for e in etiquetas if DEF_TAG.fullmatch(e)],
                    "falla_esperada": "fail" in etiquetas,
                    "etiquetas": etiquetas, "archivo": archivo, "linea": numero, "pasos": [],
                }
            elif texto.startswith(("Ejemplos:", "Escenarios:", "Regla:", "Antecedentes:")):
                pendientes = []
                if not texto.startswith("Ejemplos:"):
                    actual = None
            elif actual is not None and texto and not texto.startswith("#"):
                actual["pasos"].append(texto)
    return casos, problemas


def caso_contrato(operaciones: list[str]) -> dict:
    hu = sorted({h for op in operaciones for patron, hus in HU_POR_OPERACION if re.search(patron, op) for h in hus})
    return {
        "id": CP_CONTRATO, "titulo": "Contrato OpenAPI del núcleo y de G4 con casos generados (Schemathesis)",
        "nivel": "contrato", "modulo": "G4", "tipo": "técnico", "hu": hu, "ca": [], "hu_ca": [], "defectos": [],
        "falla_esperada": False, "etiquetas": ["tecnico"], "archivo": "scripts/correr-contrato.sh", "linea": 1,
        "pasos": ["Schemathesis genera casos desde /openapi.json para las operaciones del núcleo y de G4",
                  "Checks y exclusiones documentados en schemathesis.toml y scripts/contrato_hooks.py"],
    }


def hu_de_operacion(operacion: str) -> list[str]:
    return sorted({h for patron, hus in HU_POR_OPERACION if re.search(patron, operacion) for h in hus})


def estado_testcase(caso: ET.Element) -> str:
    if caso.find("failure") is not None or caso.find("error") is not None:
        return "failed"
    omitido = caso.find("skipped")
    if omitido is not None:
        return "xfailed" if "xfail" in (omitido.get("type", "") + omitido.get("message", "")).lower() else "skipped"
    if caso.find("flakyFailure") is not None or caso.find("flakyError") is not None:
        return "flaky"
    # Playwright no marca un test.fail() cumplido: queda como pasado con la anotación "fail".
    if any(p.get("name") == "fail" for p in caso.iter("property")):
        return "xfailed"
    return "passed"


def buscar_junit(reportes: Path) -> dict[str, list[Path]]:
    """JUnit por nivel. Sirve para reportes/ del pipeline y para los artefactos viejos (reportes-api/api/junit.xml)."""
    por_nivel = defaultdict(list)
    for ruta in sorted(reportes.rglob("junit.xml")):
        nivel = ruta.parent.name
        if nivel in ("api", "web", "contrato"):
            por_nivel[nivel].append(ruta)
    return por_nivel


def leer_resultados(reportes: Path) -> dict:
    """Ejecuciones por CP (cada ejemplo y cada repetición web es una), operaciones del contrato y evidencias."""
    ejecuciones, sin_cp, evidencias = defaultdict(list), [], defaultdict(list)
    junit = buscar_junit(reportes)
    for nivel in ("api", "web"):
        for ruta in junit.get(nivel, []):
            for caso in ET.parse(ruta).getroot().iter("testcase"):
                nombre = caso.get("name", "")
                id_caso = normalizar_cp(nombre)
                if not id_caso:
                    sin_cp.append(nombre)
                    continue
                estado = estado_testcase(caso)
                salida = "".join(t.text or "" for t in caso.iter("system-out"))
                # Sin includeRetries (runs viejos), un flaky queda como pasado con la captura de su intento fallido.
                if estado == "passed" and "test-failed-" in salida:
                    estado = "flaky"
                detalle = next((caso.find(t).get("message", "") for t in ("failure", "error", "skipped", "flakyFailure")
                                if caso.find(t) is not None), "")
                ejecuciones[id_caso].append({"estado": estado, "nivel": nivel, "nombre": nombre,
                                             "tiempo": float(caso.get("time", 0) or 0), "detalle": detalle[:300]})
                for adjunto in re.findall(r"\[\[ATTACHMENT\|(.+?)\]\]", salida):
                    archivo = ruta.parent / adjunto
                    if archivo.suffix == ".png" and archivo.exists():
                        evidencias[id_caso].append(archivo)
    operaciones = {}
    for ruta in junit.get("contrato", []):
        for caso in ET.parse(ruta).getroot().iter("testcase"):
            operaciones[caso.get("name", "")] = estado_testcase(caso)
    return {"ejecuciones": ejecuciones, "operaciones": operaciones, "sin_cp": sin_cp, "evidencias": evidencias,
            "niveles": sorted(junit)}


def consolidar(estados: list[str]) -> str:
    if not estados:
        return "sin ejecutar"
    for estado in ("failed", "flaky"):
        if estado in estados:
            return estado
    if all(e == "skipped" for e in estados):
        return "skipped"
    return "xfailed" if "xfailed" in estados else "passed"


def resultados_por_caso(casos: dict, resultados: dict) -> dict[str, dict]:
    """Estado consolidado de cada CP del run, con el conteo de sus ejecuciones."""
    por_caso = {}
    for id_caso in casos:
        if id_caso == CP_CONTRATO:
            estados = list(resultados["operaciones"].values())
            estados = [e for e in estados if e != "skipped"] or estados
        else:
            estados = [e["estado"] for e in resultados["ejecuciones"].get(id_caso, [])]
        estado = consolidar(estados)
        por_caso[id_caso] = {
            "estado": estado, "ejecuciones": len(estados),
            "pasaron": sum(e in ("passed", "xfailed") for e in estados),
            "fallaron": sum(e in ("failed", "flaky") for e in estados),
        }
    return por_caso


def metadatos_run(**valores) -> dict:
    """Datos del run desde las variables de GitHub Actions. Los valores explícitos (kiwi_sincronizar) mandan."""
    entorno = os.environ
    numero = valores.get("numero") or entorno.get("GITHUB_RUN_NUMBER", "local")
    intento = int(valores.get("intento") or entorno.get("GITHUB_RUN_ATTEMPT", 1))
    run_id = str(valores.get("run_id") or entorno.get("GITHUB_RUN_ID", ""))
    repo = valores.get("repo") or entorno.get("GITHUB_REPOSITORY", "")
    servidor = entorno.get("GITHUB_SERVER_URL", "https://github.com")
    fecha = valores.get("fecha") or datetime.now(LIMA).isoformat(timespec="seconds")
    return {
        "id": f"{run_id or 'local'}-{intento}", "run_id": run_id, "numero": numero, "intento": intento,
        "sha": (valores.get("sha") or entorno.get("GITHUB_SHA", ""))[:40],
        "rama": valores.get("rama") or entorno.get("GITHUB_HEAD_REF") or entorno.get("GITHUB_REF_NAME", ""),
        "evento": valores.get("evento") or entorno.get("GITHUB_EVENT_NAME", "local"),
        "evidencia": valores.get("evidencia") or entorno.get("EVIDENCIA") or "sin-imagenes",
        "conclusion": valores.get("conclusion", ""),
        "fecha": fecha, "repo": repo,
        "url": f"{servidor}/{repo}/actions/runs/{run_id}" if repo and run_id else "",
    }


def resumen_estados(por_caso: dict[str, dict]) -> dict[str, int]:
    conteo = dict.fromkeys(ESTADOS, 0)
    for datos in por_caso.values():
        conteo[datos["estado"]] += 1
    return {"casos": len(por_caso), **conteo}
