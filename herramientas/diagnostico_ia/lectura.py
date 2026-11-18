"""Lectura de los artefactos del run. Nada de IA en este módulo.

Entrada preferida: `junit-cp.xml`, el JUnit por caso que arma
`.github/scripts/trazabilidad.py`. Trae un <testcase> por CP con sus
<property> (hu, ca, defecto, modulo, nivel, tipo, estado, ejecuciones,
archivo), que es exactamente el contexto que el diagnóstico necesita.

Entrada alternativa: los `junit.xml` crudos de cada job (pytest en `api/`,
Playwright en `web/`, Schemathesis en `contrato/`). Traen menos información
—hay que deducir el ID del caso del nombre de la prueba— y se usan cuando se
descargan los artefactos de un run sin pasar por `trazabilidad.py`.

Qué cuenta como fallo: todo caso cuyo estado no es `passed` ni `skipped`.
En este proyecto un `xfailed` es un fallo que reprodujo un defecto conocido
(xfail estricto), así que es un fallo a diagnosticar; `skipped` es un caso que
se decidió no ejecutar y no aporta nada al diagnóstico.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

# Estados del JUnit por caso que se consideran fallo. Ver docstring del módulo.
ESTADOS_DE_FALLO = ("failed", "flaky", "xfailed", "sin ejecutar")

# Recorte de la salida. Mandar un log entero a un modelo es caro y empeora la
# respuesta: se queda con las últimas líneas, que son las del error.
LINEAS_DE_SALIDA = 10
LARGO_DE_LINEA = 240

# Líneas que valen la pena cuando hay que elegir dentro de una salida larga.
SENAS_DE_ERROR = ("error", "assert", "fail", "traceback", "exception", "timeout", "expected", "refused", " 5")

CASO_LITERAL = re.compile(r"\bCP-([A-Z]+\d+)")
CASO_PYTEST = re.compile(r"^test_cp([a-z]+?)(\d+)")
DEFECTO = re.compile(r"\bDEF-\d+\b")


def leer_fallos(carpeta_run: Path) -> list[dict]:
    """Devuelve un fallo por caso, en el orden del artefacto (lectura determinista)."""
    carpeta_run = Path(carpeta_run)
    junit_por_caso = _buscar(carpeta_run, "junit-cp.xml")
    if junit_por_caso:
        return _fallos_del_junit_por_caso(junit_por_caso)
    crudos = sorted(p for p in carpeta_run.rglob("junit*.xml") if p.name != "junit-cp.xml")
    if not crudos:
        raise FileNotFoundError(f"No hay junit-cp.xml ni junit.xml dentro de {carpeta_run}")
    fallos: list[dict] = []
    for ruta in crudos:
        fallos.extend(_fallos_del_junit_crudo(ruta, carpeta_run))
    return fallos


def origen(carpeta_run: Path) -> str:
    """Qué artefacto se leyó, para que el reporte lo diga."""
    carpeta_run = Path(carpeta_run)
    por_caso = _buscar(carpeta_run, "junit-cp.xml")
    return "junit-cp.xml (un caso por CP, con trazabilidad)" if por_caso else "junit.xml crudos de cada job"


def leer_lineas_de_log(carpeta_run: Path, maximo: int = 8) -> list[str]:
    """Últimas líneas con señas de error de los logs del run (uvicorn, etc.).

    Se usan solo para el resumen del run, nunca como evidencia de un caso: una
    línea de log suelta no prueba nada sobre un caso en particular.
    """
    lineas: list[str] = []
    for ruta in sorted(Path(carpeta_run).rglob("*.log")):
        try:
            texto = ruta.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        del_archivo = [linea.strip() for linea in texto.splitlines() if _parece_error(linea)]
        lineas.extend(f"{ruta.name}: {linea[:LARGO_DE_LINEA]}" for linea in del_archivo[-maximo:])
    return lineas[-maximo:]


def recortar(texto: str) -> str:
    """Deja las últimas líneas útiles de una salida larga."""
    lineas = [linea.strip() for linea in (texto or "").splitlines() if linea.strip()]
    if not lineas:
        return ""
    if len(lineas) > LINEAS_DE_SALIDA:
        con_error = [linea for linea in lineas if _parece_error(linea)]
        lineas = (con_error or lineas)[-LINEAS_DE_SALIDA:]
    return "\n".join(linea[:LARGO_DE_LINEA] for linea in lineas)


def _parece_error(linea: str) -> bool:
    bajo = linea.lower()
    return any(sena in bajo for sena in SENAS_DE_ERROR)


def _buscar(carpeta: Path, nombre: str) -> Path | None:
    directo = carpeta / nombre
    if directo.is_file():
        return directo
    return next(iter(sorted(carpeta.rglob(nombre))), None)


def _fallos_del_junit_por_caso(ruta: Path) -> list[dict]:
    raiz = ET.parse(ruta).getroot()
    fallos = []
    for caso in raiz.iter("testcase"):
        propiedades = {p.get("name"): p.get("value") or "" for p in caso.iter("property")}
        estado = propiedades.get("estado", "")
        if estado not in ESTADOS_DE_FALLO:
            continue
        nombre = caso.get("name") or ""
        id_caso, titulo = _partir_nombre(nombre)
        mensaje, salida = _mensaje_y_salida(caso)
        declarado = _defecto_declarado(caso, propiedades)
        fallos.append({
            "caso": id_caso,
            "titulo": titulo,
            "hu": propiedades.get("hu", ""),
            "ca": propiedades.get("ca", ""),
            "modulo": propiedades.get("modulo", caso.get("classname", "")),
            "nivel": propiedades.get("nivel", ""),
            "tipo": propiedades.get("tipo", ""),
            "estado": estado,
            "ejecuciones": propiedades.get("ejecuciones", ""),
            "archivo": propiedades.get("archivo", ""),
            "defecto_declarado": declarado,
            "mensaje": mensaje,
            "salida": recortar(salida),
        })
    return fallos


def _fallos_del_junit_crudo(ruta: Path, carpeta_run: Path) -> list[dict]:
    raiz = ET.parse(ruta).getroot()
    nivel = _nivel_por_carpeta(ruta, carpeta_run)
    fallos = []
    for caso in raiz.iter("testcase"):
        estado, mensaje, salida = _estado_crudo(caso)
        if estado not in ESTADOS_DE_FALLO:
            continue
        declarado = _defecto_declarado(caso, {})
        nombre = caso.get("name") or ""
        id_caso, titulo = _partir_nombre(nombre)
        fallos.append({
            "caso": id_caso,
            "titulo": titulo,
            "hu": "",
            "ca": "",
            "modulo": "",
            "nivel": nivel,
            "tipo": "",
            "estado": estado,
            "ejecuciones": "",
            # En el JUnit crudo de pytest el atributo file apunta a pytest_bdd,
            # no a la prueba: el classname identifica mejor el archivo.
            "archivo": caso.get("classname") or "",
            "defecto_declarado": declarado,
            "mensaje": mensaje,
            "salida": recortar(salida),
        })
    return fallos


def _estado_crudo(caso: ET.Element) -> tuple[str, str, str]:
    """Traduce un <testcase> crudo al vocabulario de estados del proyecto."""
    fallo = caso.find("failure") if caso.find("failure") is not None else caso.find("error")
    if fallo is not None:
        return "failed", fallo.get("message") or "", fallo.text or ""
    omitido = caso.find("skipped")
    if omitido is not None:
        tipo = (omitido.get("type") or "").lower()
        mensaje = omitido.get("message") or ""
        # pytest escribe type="pytest.xfail" en los fallos esperados; cualquier
        # otro skipped es un caso que no se quiso ejecutar y no es un fallo.
        if "xfail" in tipo or DEFECTO.search(mensaje):
            return "xfailed", mensaje, omitido.text or ""
        return "skipped", mensaje, ""
    salida = "".join(nodo.text or "" for nodo in caso.iter("system-out"))
    # Heurística para Playwright: un caso marcado test.fail queda como passed en
    # el JUnit, pero deja adjunto el error-context del fallo esperado. Es una
    # deducción, no un dato: junit-cp.xml es la fuente confiable del estado.
    if "error-context" in salida:
        return "xfailed", "fallo esperado de Playwright (adjunto error-context)", salida
    return "passed", "", salida


def _mensaje_y_salida(caso: ET.Element) -> tuple[str, str]:
    partes = []
    for etiqueta in ("failure", "error", "skipped"):
        for nodo in caso.iter(etiqueta):
            partes.append(nodo.get("message") or "")
            partes.append(nodo.text or "")
    salida = "".join(nodo.text or "" for nodo in caso.iter("system-out"))
    mensaje = " ".join(parte.strip() for parte in partes if parte.strip())
    return mensaje[:LARGO_DE_LINEA * 2], salida


def _partir_nombre(nombre: str) -> tuple[str, str]:
    """Separa el ID del caso de su título. Acepta las tres formas del proyecto."""
    literal = CASO_LITERAL.search(nombre)
    if literal:
        id_caso = f"CP-{literal.group(1)}"
        titulo = nombre[literal.end():].strip(" ·›-") or nombre.strip()
        return id_caso, titulo
    pytest = CASO_PYTEST.match(nombre)
    if pytest:
        id_caso = f"CP-{pytest.group(1).upper()}{pytest.group(2)}"
        titulo = nombre[pytest.end():].strip("_").replace("_", " ").strip()
        return id_caso, titulo or nombre
    return nombre.strip() or "sin-id", nombre.strip()


def _defecto_declarado(caso: ET.Element, propiedades: dict[str, str]) -> str:
    """El DEF-xx que el run declara para el caso, solo de fuentes confiables.

    Confiable = la <property> defecto que escribe trazabilidad.py a partir de las
    etiquetas del escenario, o el atributo message del <skipped> que escribe
    pytest desde el marcador xfail de la prueba.

    NO se lee del cuerpo del <failure>: ahí va la salida de la aplicación bajo
    prueba, y un texto que viene de la app no puede decidir a qué defecto
    corresponde un fallo. Si una prueba imprimiera «DEF-99», el reporte
    propondría un defecto que nadie reportó.
    """
    de_propiedad = _primer_defecto(propiedades.get("defecto", ""))
    if de_propiedad:
        return de_propiedad
    for omitido in caso.iter("skipped"):
        del_mensaje = _primer_defecto(omitido.get("message") or "")
        if del_mensaje:
            return del_mensaje
    return ""


def _primer_defecto(texto: str) -> str:
    encontrado = DEFECTO.search(texto or "")
    return encontrado.group(0) if encontrado else ""


def _nivel_por_carpeta(ruta: Path, carpeta_run: Path) -> str:
    try:
        relativa = ruta.relative_to(carpeta_run)
    except ValueError:
        return ""
    return relativa.parts[0] if len(relativa.parts) > 1 else ""
