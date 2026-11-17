"""Los cuatro backends del diagnóstico. Solo biblioteca estándar.

  anthropic  → modelo de Anthropic por HTTPS (urllib).
  google     → modelo de Google por HTTPS (urllib).
  grabado    → respuestas guardadas de una corrida real, para que el reporte se
               pueda regenerar igual sin gastar llamadas ni depender de la red.
  lineabase  → clasificador por reglas, SIN IA. Es el CONTROL del experimento:
               si las reglas aciertan lo mismo que el modelo, la IA no aporta
               nada en esta tarea. Comparar contra la línea base es parte de la
               validación, no un adorno.

No hay SDK ni requests a propósito: el proyecto no agrega dependencias y así se
ve exactamente qué se manda y qué se recibe. La clave sale de un .env local
(está en .gitignore) y nunca del repositorio ni de los secretos de GitHub: lo
que se publica es el reporte, no la llave.

Si falta la clave, el backend FALLA con un mensaje claro. Nunca devuelve una
respuesta inventada: un número que no se midió no sirve para sustentar nada.
"""

from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

BACKENDS = ("anthropic", "google", "grabado", "lineabase")

URL_ANTHROPIC = "https://api.anthropic.com/v1/messages"
VERSION_ANTHROPIC = "2023-06-01"
MODELO_ANTHROPIC = "claude-opus-5-5"
URL_GOOGLE = "https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
MODELO_GOOGLE = "gemini-2.5-flash"
MAXIMO_DE_SALIDA = 2000
ESPERA = 120

# Casos que la documentación del proyecto declara inestables: no dan el mismo
# resultado en todas las corridas. CP-T20 reproduce DEF-26 solo a veces y
# CP-NA69 y CP-T19 quedaron como evidencia manual por lo mismo
# (docs/defectos.md, «Regla para la concurrencia», y docs/alcance-y-casos.md).
# Si esa lista cambia en los documentos, se actualiza aquí.
CASOS_INESTABLES_DOCUMENTADOS = ("CP-T20", "CP-NA69", "CP-T19")

TIPOS_DE_ENTORNO = ("conexion", "tiempo_de_espera", "http_5xx", "no_ejecutado")


class SinClave(RuntimeError):
    """No hay clave de API para el backend pedido."""


class RespuestaInvalida(RuntimeError):
    """El backend contestó algo que no se pudo leer como JSON."""


def responder(sistema: str, prompt: str, esquema: dict, *, backend: str = "lineabase",
              contexto: dict | None = None, raiz: Path | None = None,
              carpeta_grabados: Path | None = None) -> dict:
    """Una respuesta en JSON para un prompt.

    `contexto` son los mismos datos del grupo que viajan dentro del prompt; solo
    lo usa 'lineabase', que no lee prosa sino los campos del artefacto.
    """
    if backend not in BACKENDS:
        raise ValueError(f"Backend desconocido: {backend}. Elegibles: {', '.join(BACKENDS)}")
    if backend == "lineabase":
        if contexto is None:
            raise ValueError("El backend 'lineabase' necesita el contexto, no el prompt")
        if contexto.get("tarea") == "resumen":
            return resumir_por_reglas(contexto)
        return clasificar_por_reglas(contexto)
    peticion = _texto_de_la_peticion(prompt, esquema)
    if backend == "grabado":
        return _leer_grabado(sistema, peticion, carpeta_grabados)
    if backend == "anthropic":
        crudo = _pedir_a_anthropic(sistema, peticion, raiz)
    else:
        crudo = _pedir_a_google(sistema, peticion, raiz)
    return extraer_json(crudo)


def clave_de_peticion(sistema: str, prompt: str) -> str:
    """Identificador estable de una petición, para guardar y recuperar respuestas."""
    return hashlib.sha1(f"{sistema}\n---\n{prompt}".encode()).hexdigest()[:16]


def guardar_respuesta(carpeta: Path, sistema: str, prompt: str, esquema: dict, respuesta: dict) -> Path:
    """Guarda una respuesta REAL para poder repetir el reporte sin volver a pagar.

    Solo se llama con lo que de verdad contestó un modelo. Grabar respuestas
    escritas a mano haría que el reporte mintiera.
    """
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    peticion = _texto_de_la_peticion(prompt, esquema)
    ruta = carpeta / f"{clave_de_peticion(sistema, peticion)}.json"
    ruta.write_text(json.dumps(respuesta, ensure_ascii=False, indent=2), encoding="utf-8")
    return ruta


def leer_clave(nombre: str, raiz: Path | None = None) -> str:
    """Lee la clave del entorno o del .env local. Nunca del repositorio."""
    del_entorno = os.environ.get(nombre)
    if del_entorno:
        return del_entorno.strip()
    for ruta in _rutas_env(raiz):
        if not ruta.is_file():
            continue
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            if clave.strip() == nombre:
                return valor.strip().strip("'\"")
    raise SinClave(
        f"Falta {nombre}. Copia ejemplo.env a .env en la raíz del repositorio y pon la clave ahí "
        f"(.env está en .gitignore), o exporta {nombre} en la terminal. "
        f"Para correr sin clave: --modelo lineabase (reglas, sin IA) o --modelo grabado."
    )


def extraer_json(texto: str) -> dict:
    """Saca el primer objeto JSON del texto.

    No se usa prefill ni se confía en que el modelo devuelva JSON limpio: puede
    venir con explicación alrededor. Si no hay JSON, es un error, no un 'más o
    menos'. Que el JSON tenga los campos correctos lo decide guardas.py.
    """
    inicio = texto.find("{")
    while inicio != -1:
        profundidad, en_texto, escapado = 0, False, False
        for posicion in range(inicio, len(texto)):
            caracter = texto[posicion]
            if en_texto:
                if escapado:
                    escapado = False
                elif caracter == "\\":
                    escapado = True
                elif caracter == '"':
                    en_texto = False
                continue
            if caracter == '"':
                en_texto = True
            elif caracter == "{":
                profundidad += 1
            elif caracter == "}":
                profundidad -= 1
                if profundidad == 0:
                    try:
                        return json.loads(texto[inicio:posicion + 1])
                    except json.JSONDecodeError:
                        break
        inicio = texto.find("{", inicio + 1)
    raise RespuestaInvalida(f"La respuesta no trae un objeto JSON: {texto[:200]!r}")


def clasificar_por_reglas(contexto: dict) -> dict:
    """LÍNEA BASE, sin IA: reglas sobre los campos del artefacto.

    Sirve de control. Las reglas están en orden y la primera que aplica gana;
    cada una dice de dónde sale. La última es la debilidad conocida de la línea
    base: cuando ninguna regla aplica, supone la clase más frecuente.
    """
    grupo = contexto["grupo"]
    clasificaciones = []
    for fallo in contexto["fallos"]:
        clase, defecto, confianza, razon = _regla(fallo, grupo)
        clasificaciones.append({
            "caso": fallo["caso"],
            "grupo": grupo["id"],
            "clase": clase,
            "defecto": defecto,
            "confianza": confianza,
            "razon": razon,
            "evidencia": _evidencia(fallo),
        })
    return {"grupo": grupo["id"], "nombre": _nombre_del_grupo(grupo), "fallos": clasificaciones}


def resumir_por_reglas(contexto: dict) -> dict:
    """LÍNEA BASE del resumen del run: cuentas, sin IA y sin adjetivos."""
    totales = contexto["totales"]
    por_clase = contexto["por_clase"]
    resumen = (
        f"{totales['fallos']} fallos en {totales['grupos']} grupos. "
        f"Por clase: " + ", ".join(f"{n} {c}" for c, n in sorted(por_clase.items())) + "."
    )
    mayor = max(por_clase.items(), key=lambda par: (par[1], par[0]))[0] if por_clase else "sin fallos"
    return {"resumen": resumen, "riesgo": f"La clase más frecuente en este run es {mayor}."}


def _regla(fallo: dict, grupo: dict) -> tuple[str, str | None, str, str]:
    estado = fallo.get("estado", "")
    declarado = fallo.get("defecto_declarado") or None
    if estado == "flaky":
        return "prueba_inestable", None, "alta", "El run la marcó flaky: alternó entre resultado esperado y fallo."
    pasaron, total = _ejecuciones(fallo)
    if total > 1 and 0 < pasaron < total:
        return "prueba_inestable", None, "alta", f"Resultado mezclado en el mismo run: {pasaron} de {total} ejecuciones."
    if fallo.get("caso") in CASOS_INESTABLES_DOCUMENTADOS:
        return ("prueba_inestable", declarado, "media",
                "La documentación del proyecto declara este caso inestable: no da el mismo resultado en todas las corridas.")
    if grupo.get("tipo_error") in TIPOS_DE_ENTORNO or estado == "sin ejecutar":
        return "error_entorno", None, "media", f"El tipo de error del grupo es {grupo.get('tipo_error')}: apunta al entorno, no a la app."
    if estado == "xfailed" and declarado:
        return "defecto_real", declarado, "alta", f"Fallo esperado que reprodujo {declarado}, ya documentado en docs/defectos.md."
    if estado == "failed" and grupo.get("tipo_error") == "asercion":
        return "defecto_real", declarado, "baja", "Falló una aserción: la app no cumplió el oráculo del caso."
    return ("defecto_real", declarado, "baja",
            "Ninguna regla aplicó; la línea base supone defecto real porque es la clase más frecuente.")


def _ejecuciones(fallo: dict) -> tuple[int, int]:
    crudo = (fallo.get("ejecuciones") or "").split("/")
    try:
        return int(crudo[0]), int(crudo[1])
    except (IndexError, ValueError):
        return 0, 0


def _evidencia(fallo: dict) -> str:
    """Una línea copiada del artefacto. La línea base nunca escribe evidencia nueva."""
    for campo in ("mensaje", "salida", "titulo", "archivo"):
        valor = (fallo.get(campo) or "").strip()
        if valor:
            return valor.splitlines()[0][:200]
    return fallo.get("caso", "")


def _nombre_del_grupo(grupo: dict) -> str:
    archivo = (grupo.get("archivo") or "sin archivo").split("/")[-1]
    defectos = ", ".join(grupo.get("defectos_declarados") or []) or "sin defecto declarado"
    return f"{grupo.get('tipo_error')} en {archivo} ({defectos})"


def _texto_de_la_peticion(prompt: str, esquema: dict) -> str:
    """El prompt más la forma exacta que se espera de vuelta."""
    return (
        f"{prompt}\n\n"
        f"Responde SOLO con un objeto JSON, sin texto alrededor y sin ```.\n"
        f"Forma exacta esperada:\n{json.dumps(esquema, ensure_ascii=False, indent=2)}"
    )


def _leer_grabado(sistema: str, peticion: str, carpeta: Path | None) -> dict:
    if carpeta is None:
        raise SinClave("El backend 'grabado' necesita la carpeta de respuestas grabadas")
    ruta = Path(carpeta) / f"{clave_de_peticion(sistema, peticion)}.json"
    if not ruta.is_file():
        raise SinClave(
            f"No hay respuesta grabada para esta petición ({ruta.name}). La carpeta se llena con una corrida "
            f"real: python -m herramientas.diagnostico_ia --run <carpeta> --modelo anthropic --grabar. "
            f"No se inventa el contenido."
        )
    return json.loads(ruta.read_text(encoding="utf-8"))


def _pedir_a_anthropic(sistema: str, peticion: str, raiz: Path | None) -> str:
    clave = leer_clave("ANTHROPIC_API_KEY", raiz)
    modelo = os.environ.get("MODELO_ANTHROPIC") or _del_env("MODELO_ANTHROPIC", raiz) or MODELO_ANTHROPIC
    cuerpo = {
        "model": modelo,
        "max_tokens": MAXIMO_DE_SALIDA,
        "system": sistema,
        "messages": [{"role": "user", "content": peticion}],
    }
    datos = _post(URL_ANTHROPIC, cuerpo, {
        "x-api-key": clave,
        "anthropic-version": VERSION_ANTHROPIC,
    })
    bloques = [b.get("text", "") for b in datos.get("content", []) if b.get("type") == "text"]
    return "\n".join(bloques)


def _pedir_a_google(sistema: str, peticion: str, raiz: Path | None) -> str:
    clave = leer_clave("GOOGLE_API_KEY", raiz)
    modelo = os.environ.get("MODELO_GOOGLE") or _del_env("MODELO_GOOGLE", raiz) or MODELO_GOOGLE
    cuerpo = {
        "system_instruction": {"parts": [{"text": sistema}]},
        "contents": [{"role": "user", "parts": [{"text": peticion}]}],
        "generationConfig": {"maxOutputTokens": MAXIMO_DE_SALIDA},
    }
    # La clave va en una cabecera, no en la URL: una URL con la clave queda en
    # los logs del servidor y en el historial de la terminal.
    datos = _post(URL_GOOGLE.format(modelo=modelo), cuerpo, {"x-goog-api-key": clave})
    partes = datos.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    return "\n".join(parte.get("text", "") for parte in partes)


def _post(url: str, cuerpo: dict, cabeceras: dict) -> dict:
    datos = json.dumps(cuerpo).encode("utf-8")
    peticion = urllib.request.Request(url, data=datos, method="POST",
                                      headers={"content-type": "application/json", **cabeceras})
    try:
        with urllib.request.urlopen(peticion, timeout=ESPERA) as respuesta:
            return json.loads(respuesta.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detalle = error.read().decode("utf-8", errors="replace")[:300]
        raise RespuestaInvalida(f"{url} respondió {error.code}: {detalle}") from error
    except urllib.error.URLError as error:
        raise RespuestaInvalida(f"No se pudo llegar a {url}: {error.reason}") from error


def _del_env(nombre: str, raiz: Path | None) -> str | None:
    try:
        return leer_clave(nombre, raiz)
    except SinClave:
        return None


def _rutas_env(raiz: Path | None) -> list[Path]:
    carpetas = [Path(raiz)] if raiz else []
    carpetas.append(Path(__file__).resolve().parents[2])
    carpetas.append(Path.cwd())
    return [carpeta / ".env" for carpeta in carpetas]
