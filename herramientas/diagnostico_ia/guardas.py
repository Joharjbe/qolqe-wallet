"""Guardas (guardrails) sobre lo que responde el modelo.

Ninguna respuesta se escribe en el reporte sin pasar por las cuatro guardas.
Una respuesta rechazada no se corrige ni se vuelve a pedir: se descarta y se
cuenta. El número de rechazos es una métrica del reporte, porque mide cuántas
veces el modelo dijo algo que no se podía sostener.

Cada guarda responde a un riesgo de la clase 15:
  1. guarda_esquema          → salida no estructurada: el modelo contesta en
                               prosa o inventa campos, y el reporte se rompe.
  2. guarda_defecto_conocido → alucinación: propone un DEF-xx que no existe en
                               docs/defectos.md.
  3. guarda_caso_del_run     → alucinación y oráculo débil: habla de un caso que
                               no está en el run, o la evidencia que cita no es
                               texto del artefacto (la inventó).
  4. guarda_sin_datos_sensibles → privacidad: rutas de la máquina, claves o
                               datos personales en un reporte que se publica.
"""

from __future__ import annotations

import re
from pathlib import Path

# Esquema estricto de la clasificación de un fallo: ni un campo más.
# El mismo diccionario se le muestra al modelo como forma esperada.
ESQUEMA_FALLO = {
    "caso": "CP-xx",
    "grupo": "G1",
    "clase": "defecto_real|prueba_inestable|error_entorno",
    "defecto": "DEF-xx o null",
    "confianza": "alta|media|baja",
    "razon": "1-2 frases",
    "evidencia": "una línea copiada del mensaje, de la salida o del .feature",
}
CAMPOS = tuple(ESQUEMA_FALLO)
CLASES = ("defecto_real", "prueba_inestable", "error_entorno")
CONFIANZAS = ("alta", "media", "baja")
LARGO_MAXIMO_RAZON = 400

DEFECTO = re.compile(r"\bDEF-\d+\b")

# Patrones de dato sensible, con el motivo que se escribe en el rechazo.
PATRONES_SENSIBLES = (
    (re.compile(r"/(?:Users|home|private)/[\w./-]+"), "ruta de la máquina"),
    (re.compile(r"\b(?:sk-ant|AIza|ghp_|gho_)[\w-]{6,}"), "posible clave o token"),
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]{2,}\b"), "correo electrónico"),
    (re.compile(r"\d{9,}"), "posible dato personal (celular o documento)"),
)


def cargar_defectos(ruta_defectos: Path) -> set[str]:
    """Los DEF-xx que existen de verdad, leídos de docs/defectos.md."""
    ruta_defectos = Path(ruta_defectos)
    if not ruta_defectos.is_file():
        raise FileNotFoundError(f"No se encontró el reporte de defectos: {ruta_defectos}")
    return set(DEFECTO.findall(ruta_defectos.read_text(encoding="utf-8")))


def material_del_run(fallos: list[dict]) -> dict[str, str]:
    """Todo el texto que se le mandó al modelo, por caso. Es contra esto que se
    comprueba la evidencia: si no está aquí, el modelo no lo leyó, lo inventó."""
    material: dict[str, str] = {}
    for fallo in fallos:
        texto = " ".join(str(fallo.get(campo, "")) for campo in
                         ("titulo", "archivo", "estado", "ejecuciones", "defecto_declarado", "mensaje", "salida"))
        material[fallo["caso"]] = material.get(fallo["caso"], "") + " " + texto
    return material


def guarda_esquema(objeto: object) -> list[str]:
    """Riesgo: salida no estructurada. Esquema estricto, ni un campo de más."""
    if not isinstance(objeto, dict):
        return ["la respuesta no es un objeto JSON"]
    motivos = []
    faltan = [campo for campo in CAMPOS if campo not in objeto]
    sobran = [campo for campo in objeto if campo not in CAMPOS]
    if faltan:
        motivos.append(f"faltan campos: {', '.join(faltan)}")
    if sobran:
        motivos.append(f"campos que no van: {', '.join(sobran)}")
    if objeto.get("clase") not in CLASES:
        motivos.append(f"clase inválida: {objeto.get('clase')!r}")
    if objeto.get("confianza") not in CONFIANZAS:
        motivos.append(f"confianza inválida: {objeto.get('confianza')!r}")
    defecto = objeto.get("defecto")
    if defecto is not None and not (isinstance(defecto, str) and DEFECTO.fullmatch(defecto)):
        motivos.append(f"defecto mal formado: {defecto!r}")
    for campo in ("caso", "grupo", "razon", "evidencia"):
        valor = objeto.get(campo)
        if not isinstance(valor, str) or not valor.strip():
            motivos.append(f"{campo} vacío o no es texto")
    razon = objeto.get("razon")
    if isinstance(razon, str) and len(razon) > LARGO_MAXIMO_RAZON:
        motivos.append(f"razon demasiado larga ({len(razon)} caracteres)")
    return motivos


def guarda_defecto_conocido(objeto: dict, defectos: set[str]) -> list[str]:
    """Riesgo: alucinación. Un DEF-xx que no está en docs/defectos.md no existe,
    y un número inventado en un reporte de defectos es peor que no decir nada."""
    defecto = objeto.get("defecto")
    if defecto is None:
        return []
    if defecto not in defectos:
        return [f"{defecto} no existe en docs/defectos.md"]
    return []


def guarda_caso_del_run(objeto: dict, material: dict[str, str]) -> list[str]:
    """Riesgo: alucinación y oráculo débil. El caso tiene que ser uno del run y
    la evidencia tiene que ser texto del propio artefacto, no una frase bonita."""
    motivos = []
    caso = objeto.get("caso")
    if caso not in material:
        return [f"el caso {caso!r} no está en este run"]
    evidencia = _aplanar(objeto.get("evidencia", ""))
    if evidencia and evidencia not in _aplanar(material[caso]):
        motivos.append("la evidencia no aparece en el material del caso")
    return motivos


def guarda_sin_datos_sensibles(objeto: dict) -> list[str]:
    """Riesgo: privacidad. El reporte se publica como artefacto del pipeline."""
    texto = " ".join(str(objeto.get(campo, "")) for campo in ("razon", "evidencia"))
    motivos = []
    for patron, motivo in PATRONES_SENSIBLES:
        encontrado = patron.search(texto)
        if encontrado:
            motivos.append(f"{motivo} en el texto: {encontrado.group(0)[:20]}…")
    return motivos


def validar(objeto: object, *, material: dict[str, str], defectos: set[str]) -> tuple[bool, list[str]]:
    """Pasa las cuatro guardas en orden. Devuelve (aceptada, motivos del rechazo)."""
    motivos = guarda_esquema(objeto)
    if motivos:
        return False, motivos
    assert isinstance(objeto, dict)
    motivos += guarda_defecto_conocido(objeto, defectos)
    motivos += guarda_caso_del_run(objeto, material)
    motivos += guarda_sin_datos_sensibles(objeto)
    return (not motivos), motivos


ESQUEMA_RESUMEN = {"resumen": "3 o 4 frases sobre el run", "riesgo": "el riesgo principal, en una frase"}


def validar_resumen(objeto: object) -> tuple[bool, list[str]]:
    """El resumen del run pasa por la forma y por la guarda de privacidad.

    No pasa por las guardas 2 y 3 porque un resumen no propone un DEF ni cita un
    caso: lo que diga de más queda a la vista del tester que lee el reporte.
    """
    if not isinstance(objeto, dict):
        return False, ["el resumen no es un objeto JSON"]
    motivos = [f"{campo} vacío o no es texto" for campo in ESQUEMA_RESUMEN
               if not isinstance(objeto.get(campo), str) or not str(objeto.get(campo)).strip()]
    sobran = [campo for campo in objeto if campo not in ESQUEMA_RESUMEN]
    if sobran:
        motivos.append(f"campos que no van: {', '.join(sobran)}")
    motivos += guarda_sin_datos_sensibles({"razon": objeto.get("resumen", ""), "evidencia": objeto.get("riesgo", "")})
    return (not motivos), motivos


def blindar_datos(texto: str) -> str:
    """Prepara un texto NO CONFIABLE para meterlo en el prompt.

    Riesgo de la clase 15: inyección de prompts. Un log o un mensaje de error
    puede traer texto que parezca una orden para el modelo («ignora las
    instrucciones anteriores»), porque la app bajo prueba recibe lo que escriben
    las pruebas. Aquí se rompe el cierre del bloque de datos para que el
    contenido no pueda salirse de él, y el prompt dice que lo de adentro son
    datos. El modelo igual puede equivocarse: por eso están las guardas y por
    eso el reporte lo revisa una persona.
    """
    limpio = (texto or "").replace("<<<", "<·<·<").replace(">>>", ">·>·>")
    return limpio.replace("```", "`·`·`")


def _aplanar(texto: str) -> str:
    return re.sub(r"[\s\"'`]+", " ", (texto or "").lower()).strip()
