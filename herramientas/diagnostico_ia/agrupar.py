"""Agrupación de fallos parecidos. Determinista, de código, SIN IA.

Por qué la agrupación no la hace el modelo: una agrupación hecha por un LLM
cambiaría entre corridas con la misma entrada (no determinismo, clase 15). Un
reporte que agrupa distinto cada vez no sirve para comparar dos runs ni para
revisar lo que hizo la herramienta. Aquí la agrupación sale de una firma
calculada con hash: misma entrada, mismos grupos, siempre.

Lo único que la IA aporta sobre un grupo es el nombre y la clasificación; si el
modelo se cae o se rechaza su respuesta, los grupos siguen estando.

Firma de un fallo = tipo de error + archivo (sin número de línea) + mensaje
normalizado. El mensaje se normaliza porque los números, las rutas y las marcas
de tiempo cambian entre corridas y partirían un mismo fallo en varios grupos.
"""

from __future__ import annotations

import hashlib
import re

MARCA_DE_TIEMPO = re.compile(r"\d{4}-\d{2}-\d{2}[t ]\d{2}:\d{2}:\d{2}[.\d+:-]*")
RUTA_DE_MAQUINA = re.compile(r"/(?:users|home|private|opt|tmp|var)/[\w./-]*")
ARCHIVO = re.compile(r"(?:[\w.-]+/)*[\w.-]+\.(?:py|js|ts|xml|html|log|feature|json|md)\b")
IDENTIFICADOR_HEX = re.compile(r"\b[0-9a-f]{8,}\b")
DEFECTO = re.compile(r"\bdef-\d+\b")
NUMERO = re.compile(r"\d+")
HUECO_DEFECTO = "«def»"

# Tipos de error, en el orden en que se prueban. El tipo es la primera parte de
# la firma: dos fallos de distinto tipo nunca son el mismo grupo.
SENAS_POR_TIPO = (
    ("tiempo_de_espera", ("timeout", "timed out", "tiempo de espera", "waiting for")),
    ("conexion", ("connection refused", "econnrefused", "connectionerror", "max retries", "no se pudo conectar")),
    ("http_5xx", (" 500 ", "500 internal", "internal server error", "502 ", "503 ")),
    ("asercion", ("assertionerror", "assert ", "expected", "se esperaba")),
)


def normalizar(texto: str) -> str:
    """Quita lo que cambia entre corridas y deja lo que identifica al fallo."""
    t = (texto or "").lower()
    t = MARCA_DE_TIEMPO.sub("«fecha»", t)
    t = RUTA_DE_MAQUINA.sub("«ruta»", t)
    t = ARCHIVO.sub("«archivo»", t)
    t = IDENTIFICADOR_HEX.sub("«id»", t)
    # El identificador del defecto es un nombre, no un número: se guarda antes
    # de borrar las cifras y se devuelve después, porque DEF-01 y DEF-02 son
    # fallos distintos aunque el resto del mensaje sea idéntico.
    defectos = DEFECTO.findall(t)
    t = DEFECTO.sub(HUECO_DEFECTO, t)
    t = NUMERO.sub("#", t)
    for defecto in defectos:
        t = t.replace(HUECO_DEFECTO, defecto, 1)
    return re.sub(r"\s+", " ", t).strip()


def tipo_de_error(fallo: dict) -> str:
    """Clasifica la forma del error (no su causa: eso es lo que se le pide a la IA)."""
    estado = fallo.get("estado", "")
    if estado == "sin ejecutar":
        return "no_ejecutado"
    if estado == "flaky":
        return "inestable"
    if estado == "xfailed":
        return "fallo_esperado"
    texto = f"{fallo.get('mensaje', '')} {fallo.get('salida', '')}".lower()
    for tipo, senas in SENAS_POR_TIPO:
        if any(sena in texto for sena in senas):
            return tipo
    return "desconocido"


def archivo_sin_linea(fallo: dict) -> str:
    return (fallo.get("archivo") or "").rsplit(":", 1)[0]


def firma(fallo: dict) -> str:
    """Hash corto y estable de la firma del fallo."""
    partes = [tipo_de_error(fallo), archivo_sin_linea(fallo), normalizar(fallo.get("mensaje", ""))]
    crudo = "|".join(partes)
    return hashlib.sha1(crudo.encode("utf-8")).hexdigest()[:12]


def agrupar(fallos: list[dict]) -> list[dict]:
    """Agrupa los fallos con la misma firma. Los grupos salen en el orden en que
    aparece su primer fallo, así que G1..Gn no dependen del diccionario."""
    por_firma: dict[str, dict] = {}
    for fallo in fallos:
        clave = firma(fallo)
        grupo = por_firma.get(clave)
        if grupo is None:
            grupo = {
                "id": f"G{len(por_firma) + 1}",
                "firma": clave,
                "tipo_error": tipo_de_error(fallo),
                "archivo": archivo_sin_linea(fallo),
                "mensaje_normalizado": normalizar(fallo.get("mensaje", "")),
                "defectos_declarados": [],
                "casos": [],
                # Un CP parametrizado deja un <testcase> por ejemplo en el JUnit
                # crudo: los casos van sin repetir y los ejemplos se cuentan.
                "ejemplos": 0,
                "nombre": "",
            }
            por_firma[clave] = grupo
        grupo["ejemplos"] += 1
        if fallo["caso"] not in grupo["casos"]:
            grupo["casos"].append(fallo["caso"])
        declarado = fallo.get("defecto_declarado", "")
        if declarado and declarado not in grupo["defectos_declarados"]:
            grupo["defectos_declarados"].append(declarado)
    return list(por_firma.values())


def fallos_del_grupo(grupo: dict, fallos: list[dict]) -> list[dict]:
    """Los fallos de un grupo, en el orden del artefacto."""
    casos = set(grupo["casos"])
    vistos: set[str] = set()
    del_grupo = []
    for f in fallos:
        if f["caso"] in casos and firma(f) == grupo["firma"] and f["caso"] not in vistos:
            vistos.add(f["caso"])
            del_grupo.append(f)
    return del_grupo
