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
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

BACKENDS = ("anthropic", "google", "grabado", "lineabase")

URL_ANTHROPIC = "https://api.anthropic.com/v1/messages"
VERSION_ANTHROPIC = "2023-06-01"
MODELO_ANTHROPIC = "claude-opus-5-5"
# Google movió su API: `:generateContent` ya no acepta claves nuevas («no longer available to
# new users») y el camino actual es la Interactions API, con el modelo dentro del cuerpo.
URL_GOOGLE = "https://generativelanguage.googleapis.com/v1beta/interactions"
MODELO_GOOGLE = "gemini-3.1-flash-lite"
MAXIMO_DE_SALIDA = 2000
ESPERA = 120

# --- Reintentos ante un error TEMPORAL del backend -------------------------
#
# Por qué están: un 503 («high demand») o un 429 (límite de peticiones del plan)
# no dicen NADA sobre el modelo. Sin reintentos, el grupo entero se cae de la
# medición y los casos de ese grupo aparecen «sin clasificación», mezclando un
# problema de infraestructura con un resultado del modelo. En la primera corrida
# real eso se llevó 9 de los 52 casos del conjunto de oro.
#
# Está puesto a propósito simple y con techo: pocos intentos, espera creciente y
# un presupuesto total de espera para toda la corrida. Un reintento sin límite
# convertiría una caída del backend en un arnés que no termina nunca.
CODIGOS_TEMPORALES = (429, 500, 502, 503, 504)
INTENTOS = int(os.environ.get("DIAGNOSTICO_IA_INTENTOS") or "3")
ESPERA_ENTRE_INTENTOS = float(os.environ.get("DIAGNOSTICO_IA_ESPERA") or "5")
ESPERA_MAXIMA = 60.0
# Techo de espera acumulada por proceso. Al agotarse ya no se reintenta: el
# error se reporta tal cual y queda contado como error del backend.
PRESUPUESTO_DE_ESPERA = float(os.environ.get("DIAGNOSTICO_IA_PRESUPUESTO") or "180")
# El propio 429 dice cuánto esperar («Please retry in 55s»): se le hace caso en
# vez de adivinar, con el techo de ESPERA_MAXIMA.
PISTA_DE_ESPERA = re.compile(r"retry in (\d+)\s*s", re.IGNORECASE)

# Pausa mínima entre dos llamadas HTTP al modelo. El plan gratuito de Google
# admite 15 peticiones por minuto y el arnés manda una por grupo (20 grupos) de
# corrido: sin la pausa, el 429 es seguro a partir de la petición 16. Esperar
# ~4 s antes de cada llamada cuesta menos tiempo total que reintentar un 429
# que pide 55 s. Se puede desactivar con DIAGNOSTICO_IA_PAUSA=0.
PAUSA_ENTRE_LLAMADAS = float(os.environ.get("DIAGNOSTICO_IA_PAUSA") or "4.2")

_ultima_llamada = 0.0
_espera_gastada = 0.0

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


class ErrorTemporal(RespuestaInvalida):
    """Error del backend que vale la pena reintentar (429, 503, 5xx).

    Hereda de RespuestaInvalida a propósito: quien ya atrapaba RespuestaInvalida
    (el arnés, el CLI) sigue funcionando igual, y el mensaje final dice cuántos
    intentos se hicieron para que en el reporte se vea que no fue un solo tiro.
    """

    def __init__(self, mensaje: str, segundos_sugeridos: float | None = None) -> None:
        super().__init__(mensaje)
        self.segundos_sugeridos = segundos_sugeridos


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
        "model": modelo,
        "system_instruction": sistema,
        "input": peticion,
        "generation_config": {"max_output_tokens": MAXIMO_DE_SALIDA},
    }
    # La clave va en una cabecera, no en la URL: una URL con la clave queda en
    # los logs del servidor y en el historial de la terminal.
    datos = _post(URL_GOOGLE, cuerpo, {"x-goog-api-key": clave})
    # La respuesta viene como una lista de pasos. Solo interesa el de la salida del
    # modelo: los pasos de tipo "thought" son su razonamiento y se descartan, porque
    # lo que el componente promete entregar es la clasificación, no cómo la pensó.
    textos = []
    for paso in datos.get("steps", []):
        if paso.get("type") != "model_output":
            continue
        textos += [parte.get("text", "") for parte in paso.get("content", []) if parte.get("type") == "text"]
    return "\n".join(textos)


def _post(url: str, cuerpo: dict, cabeceras: dict) -> dict:
    """Una petición POST, con reintentos solo ante errores temporales.

    Lo que NO se reintenta: un 400, un 401 o un 404. Esos no se arreglan
    esperando (clave mal puesta, modelo que no existe, camino de la API que
    cambió) y reintentarlos solo haría más lenta la corrida.
    """
    ultimo: ErrorTemporal | None = None
    for intento in range(1, max(INTENTOS, 1) + 1):
        _esperar_turno()
        try:
            return _post_una_vez(url, cuerpo, cabeceras)
        except ErrorTemporal as error:
            ultimo = error
            if intento == max(INTENTOS, 1) or not _dormir(_cuanto_esperar(error, intento)):
                break
    raise RespuestaInvalida(f"{ultimo} (tras {intento} intento(s))")


def _post_una_vez(url: str, cuerpo: dict, cabeceras: dict) -> dict:
    datos = json.dumps(cuerpo).encode("utf-8")
    peticion = urllib.request.Request(url, data=datos, method="POST",
                                      headers={"content-type": "application/json", **cabeceras})
    try:
        with urllib.request.urlopen(peticion, timeout=ESPERA) as respuesta:
            return json.loads(respuesta.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detalle = error.read().decode("utf-8", errors="replace")[:300]
        mensaje = f"{url} respondió {error.code}: {detalle}"
        if error.code in CODIGOS_TEMPORALES:
            pista = PISTA_DE_ESPERA.search(detalle)
            raise ErrorTemporal(mensaje, float(pista.group(1)) if pista else None) from error
        raise RespuestaInvalida(mensaje) from error
    except urllib.error.URLError as error:
        # Sin red o DNS caído: también es temporal, y si no se arregla el último
        # intento lo reporta igual.
        raise ErrorTemporal(f"No se pudo llegar a {url}: {error.reason}") from error


def _cuanto_esperar(error: ErrorTemporal, intento: int) -> float:
    """Espera creciente, y si el backend dijo cuánto esperar, se le hace caso."""
    sugerida = error.segundos_sugeridos or 0.0
    return min(max(ESPERA_ENTRE_INTENTOS * intento, sugerida), ESPERA_MAXIMA)


def _dormir(segundos: float) -> bool:
    """Espera antes del siguiente intento. Devuelve False si ya no queda
    presupuesto de espera, y entonces no se reintenta más."""
    global _espera_gastada
    if _espera_gastada + segundos > PRESUPUESTO_DE_ESPERA:
        return False
    _espera_gastada += segundos
    time.sleep(segundos)
    return True


def _esperar_turno() -> None:
    """Deja pasar PAUSA_ENTRE_LLAMADAS entre dos llamadas al modelo.

    No es un reintento: es no provocar el 429. Vale para todo el proceso, así
    que una corrida de 20 grupos agrega ~84 s y a cambio no pierde grupos.
    """
    global _ultima_llamada
    if PAUSA_ENTRE_LLAMADAS > 0:
        falta = PAUSA_ENTRE_LLAMADAS - (time.monotonic() - _ultima_llamada)
        if falta > 0:
            time.sleep(falta)
    _ultima_llamada = time.monotonic()


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
