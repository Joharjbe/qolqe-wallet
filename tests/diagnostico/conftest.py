"""Arnés de verificación de la capacidad de IA (punto 8 de la entrega final).

Lo que se verifica está en `herramientas/diagnostico_ia/`: un componente que lee
los artefactos del run, agrupa los fallos parecidos con código determinista y,
por cada grupo, propone la clase del fallo (defecto real / prueba inestable /
error de entorno) y el DEF-xx que le corresponde.

Aquí no se prueba la billetera Qolqe: se prueba la herramienta de pruebas. El
vocabulario de los IDs viene de la clase 15 (IA en las pruebas) y cada archivo
cubre un riesgo de esa clase:

  tests/diagnostico/test_evals.py         CP-IA-01 evals   · CP-IA-02 línea base
  tests/diagnostico/test_alucinacion.py   CP-IA-03 alucinación
  tests/diagnostico/test_inyeccion.py     CP-IA-04 inyección de prompts
  tests/diagnostico/test_privacidad.py    CP-IA-05 privacidad
  tests/diagnostico/test_determinismo.py  CP-IA-06 no determinismo
  tests/diagnostico/test_no_decide.py     CP-IA-07 guardrail y human-in-the-loop
  tests/diagnostico/test_oraculo.py       CP-IA-08 oráculo débil

Reglas del arnés, que son las que lo hacen defendible:

1. **Corre sin clave de API y sin red.** El backend por omisión es `lineabase`,
   el clasificador por reglas del propio componente, que no llama a nadie. Es el
   CONTROL del experimento: lo que mide el arnés con `lineabase` es un número de
   verdad, medido hoy.
2. **Lo que necesita un modelo real se OMITE con su motivo.** Nunca se inventa
   el resultado de una corrida que no ocurrió. Para medir con modelo:

       DIAGNOSTICO_IA_BACKEND=anthropic .venv/bin/python -m pytest tests/diagnostico -v

   (hace falta ANTHROPIC_API_KEY en el .env local; ver ejemplo.env).
3. **No se toca lo que se mide.** El arnés no modifica el componente ni el
   conjunto de oro: solo los lee. Los archivos temporales van a `tmp_path`.
4. **La entrada se toma del conjunto de oro tal cual.** No se vuelve a leer el
   run con `lectura.py`, porque el conjunto guarda la entrada ya normalizada y
   sin fugas: volver a leerla reintroduciría el estado `xfailed` y la propiedad
   `defecto`, que son la respuesta.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from herramientas.diagnostico_ia import agrupar, diagnostico, guardas, modelo

RAIZ = Path(__file__).resolve().parents[2]
RUTA_CONJUNTO_ORO = Path(__file__).resolve().parent / "conjunto_oro" / "conjunto_oro.json"
RUTA_DEFECTOS = RAIZ / "docs" / "defectos.md"
CARPETA_GRABADOS = RAIZ / "herramientas" / "diagnostico_ia" / "respuestas_grabadas"

# Backend con el que corre el arnés. Por omisión, el control sin IA.
BACKEND = (os.environ.get("DIAGNOSTICO_IA_BACKEND") or "lineabase").strip()

# Cuántas veces se repite la misma entrada en la prueba de no determinismo.
REPETICIONES = int(os.environ.get("DIAGNOSTICO_IA_REPETICIONES") or "5")

MOTIVO_SIN_MODELO = (
    "Pendiente de corrida real: esta medida necesita un modelo de verdad y el arnés corre con "
    "--modelo lineabase (sin clave, sin red). Para medirla: "
    "DIAGNOSTICO_IA_BACKEND=anthropic .venv/bin/python -m pytest tests/diagnostico -v "
    "(con ANTHROPIC_API_KEY en el .env local). No se inventa el número."
)

COMANDO_DE_LA_CORRIDA_REAL = (
    "cp ejemplo.env .env  # y poner ANTHROPIC_API_KEY\n"
    "DIAGNOSTICO_IA_BACKEND=anthropic .venv/bin/python -m pytest tests/diagnostico -v"
)


# ---------------------------------------------------------------------------
# Datos del arnés
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def raiz_repo() -> Path:
    return RAIZ


@pytest.fixture(scope="session")
def backend() -> str:
    return BACKEND


@pytest.fixture(scope="session")
def defectos() -> set[str]:
    """Los DEF-xx que existen de verdad, leídos de docs/defectos.md."""
    return guardas.cargar_defectos(RUTA_DEFECTOS)


@pytest.fixture(scope="session")
def conjunto_oro() -> dict:
    """El conjunto de oro versionado: 52 fallos etiquetados con su procedencia."""
    return json.loads(RUTA_CONJUNTO_ORO.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def carpeta_resultados() -> Path:
    """Dónde se escriben los resultados de los evals.

    `reportes/` está en .gitignore: el resultado de una medición no se versiona,
    se vuelve a medir. Se puede mover con DIAGNOSTICO_IA_RESULTADOS.
    """
    carpeta = Path(os.environ.get("DIAGNOSTICO_IA_RESULTADOS") or (RAIZ / "reportes" / "diagnostico_ia"))
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta


@pytest.fixture
def exige_modelo(backend: str) -> str:
    """Omite la prueba cuando no hay un modelo que pueda contestar, con el motivo escrito."""
    if backend == "lineabase":
        pytest.skip(MOTIVO_SIN_MODELO)
    if backend == "grabado" and not list(CARPETA_GRABADOS.glob("*.json")):
        pytest.skip("Pendiente de corrida real: no hay ninguna respuesta grabada en "
                    f"{CARPETA_GRABADOS.relative_to(RAIZ)}. Se llenan con --grabar en una corrida con clave.")
    nombre_de_la_clave = {"anthropic": "ANTHROPIC_API_KEY", "google": "GOOGLE_API_KEY"}.get(backend)
    if nombre_de_la_clave:
        try:
            modelo.leer_clave(nombre_de_la_clave, RAIZ)
        except modelo.SinClave as error:
            # Falta la clave: la prueba se OMITE con el motivo. No falla, porque
            # no hay nada roto, y no se inventa el resultado de la corrida.
            pytest.skip(f"Pendiente de corrida real. {error}")
    return backend


@pytest.fixture
def exigir_que_el_backend_contestara():
    """Omite la prueba si el backend no contestó, con el error que dio.

    La diferencia importa: que el modelo no conteste no es un hallazgo sobre el
    componente, es que la medición no se pudo hacer. Decirlo como fallo mezcla
    las dos cosas; decirlo como omisión con el error a la vista, no.
    """
    def revisar(*resultados: dict) -> None:
        for resultado in resultados:
            if resultado["totales"]["errores_del_backend"]:
                motivos = "; ".join(motivo for rechazo in resultado["rechazos"]
                                    if rechazo["tipo"] == "backend" for motivo in rechazo["motivos"])
                pytest.skip(f"El backend no contestó, así que no hay medida: {motivos[:300]}")
    return revisar


# ---------------------------------------------------------------------------
# El camino real del componente, sobre una lista de fallos ya leídos
# ---------------------------------------------------------------------------

def clasificar_fallos(entradas: list[dict], *, backend: str, defectos: set[str],
                      raiz_repo: Path = RAIZ, carpeta_grabados: Path = CARPETA_GRABADOS) -> dict:
    """Agrupa, pregunta por grupo y valida con las guardas: el mismo camino que
    `diagnostico.diagnosticar`, pero partiendo de fallos ya leídos (los del
    conjunto de oro) en vez de volver a leer el run.

    Devuelve las predicciones por caso, los grupos y los rechazos.
    """
    grupos = agrupar.agrupar(entradas)
    material = guardas.material_del_run(entradas)
    predicciones: dict[str, dict] = {}
    rechazos: list[dict] = []
    for grupo in grupos:
        del_grupo = agrupar.fallos_del_grupo(grupo, entradas)
        contexto = {"tarea": "grupo", "grupo": grupo, "fallos": del_grupo}
        esquema = {"grupo": grupo["id"], "nombre": "nombre corto del grupo", "fallos": [guardas.ESQUEMA_FALLO]}
        prompt = diagnostico.prompt_del_grupo(grupo, del_grupo)
        try:
            respuesta = modelo.responder(diagnostico.SISTEMA, prompt, esquema, backend=backend,
                                         contexto=contexto, raiz=raiz_repo, carpeta_grabados=carpeta_grabados)
        except (modelo.SinClave, modelo.RespuestaInvalida) as error:
            rechazos.append({"grupo": grupo["id"], "caso": "", "tipo": "backend",
                             "motivos": [f"{type(error).__name__}: {error}"]})
            continue
        propuestas = respuesta.get("fallos", []) if isinstance(respuesta, dict) else []
        for propuesta in propuestas:
            aceptada, motivos = guardas.validar(propuesta, material=material, defectos=defectos)
            caso = propuesta.get("caso", "") if isinstance(propuesta, dict) else ""
            if aceptada:
                predicciones[caso] = propuesta
            else:
                rechazos.append({"grupo": grupo["id"], "caso": caso, "tipo": "guarda", "motivos": motivos})
    return {"predicciones": predicciones, "grupos": grupos, "rechazos": rechazos}


def repartir_en_lotes(casos_oro: list[dict]) -> list[list[dict]]:
    """Reparte los casos de oro en lotes que no repiten el ID del caso.

    Por qué hace falta: CP-T20 está dos veces a propósito en el conjunto (como
    `defecto_real` cuando reprodujo DEF-26 y como `prueba_inestable` en la
    corrida en que no lo reprodujo), y las dos entradas tienen la misma firma.
    `agrupar.fallos_del_grupo` devuelve UN fallo por caso, así que en un solo
    lote la segunda entrada no llegaría al clasificador y quedaría sin medir.
    Con dos lotes se mide la respuesta del componente a las dos entradas.

    El reparto no cambia la clasificación de nadie más: la firma y el
    `tipo_error` de un fallo no dependen de con quién le toque compartir lote.
    """
    lotes: list[list[dict]] = []
    for caso in casos_oro:
        for lote in lotes:
            if all(otro["entrada"]["caso"] != caso["entrada"]["caso"] for otro in lote):
                lote.append(caso)
                break
        else:
            lotes.append([caso])
    return lotes


def evaluar(conjunto_oro: dict, *, backend: str, defectos: set[str], raiz_repo: Path = RAIZ) -> dict:
    """Mide el componente contra el conjunto de oro: exactitud por clase, matriz
    de confusión, acierto del DEF propuesto y reparto de confianzas.

    El resultado se lee POR CLASE y nunca como un porcentaje global: el conjunto
    está desbalanceado (defecto_real es el 77 %), así que un promedio único lo
    decidiría esa clase. Lo dice el README del conjunto de oro y se respeta aquí.
    """
    casos_oro = conjunto_oro["casos"]
    clases = tuple(guardas.CLASES)
    por_clase = {clase: {"aciertos": 0, "total": 0} for clase in clases}
    matriz = {real: dict.fromkeys(clases, 0) for real in clases}
    confianzas = dict.fromkeys(guardas.CONFIANZAS, 0)
    defecto = {"aciertos": 0, "total": 0, "propuestos": 0, "inventados": 0}
    detalle: list[dict] = []
    sin_prediccion: list[str] = []
    rechazos: list[dict] = []
    grupos_del_pase_unico = agrupar.agrupar([caso["entrada"] for caso in casos_oro])

    for lote in repartir_en_lotes(casos_oro):
        resultado = clasificar_fallos([caso["entrada"] for caso in lote], backend=backend,
                                      defectos=defectos, raiz_repo=raiz_repo)
        rechazos.extend(resultado["rechazos"])
        for caso in lote:
            propuesta = resultado["predicciones"].get(caso["entrada"]["caso"])
            if propuesta is None:
                sin_prediccion.append(caso["id"])
                continue
            real, predicha = caso["etiqueta"]["clase"], propuesta["clase"]
            por_clase[real]["total"] += 1
            matriz[real][predicha] += 1
            confianzas[propuesta["confianza"]] += 1
            if real == predicha:
                por_clase[real]["aciertos"] += 1
            if propuesta["defecto"]:
                defecto["propuestos"] += 1
                if propuesta["defecto"] not in defectos:
                    defecto["inventados"] += 1
            if caso["etiqueta"]["defecto"]:
                defecto["total"] += 1
                if propuesta["defecto"] == caso["etiqueta"]["defecto"]:
                    defecto["aciertos"] += 1
            detalle.append({
                "oro": caso["id"],
                "caso": caso["entrada"]["caso"],
                "clase_oro": real,
                "clase_propuesta": predicha,
                "acierto": real == predicha,
                "defecto_oro": caso["etiqueta"]["defecto"],
                "defecto_propuesto": propuesta["defecto"],
                "confianza": propuesta["confianza"],
                "razon": propuesta["razon"],
                "evidencia": propuesta["evidencia"],
            })

    return {
        "backend": backend,
        "casos_del_conjunto": len(casos_oro),
        "casos_medidos": sum(c["total"] for c in por_clase.values()),
        "sin_prediccion": sin_prediccion,
        "por_clase": por_clase,
        "matriz": matriz,
        "confianzas": confianzas,
        "defecto": defecto,
        "grupos_del_pase_unico": len(grupos_del_pase_unico),
        "rechazos_de_guardas": [r for r in rechazos if r["tipo"] == "guarda"],
        "errores_del_backend": [r for r in rechazos if r["tipo"] == "backend"],
        "detalle": detalle,
    }


@pytest.fixture(scope="session")
def evaluacion_base(conjunto_oro: dict, defectos: set[str], raiz_repo: Path) -> dict:
    """La evaluación del control (`lineabase`). Corre siempre, sin clave y sin red.

    Las pruebas que miran la CONDUCTA del componente (que la evidencia salga del
    artefacto, que no se invente un DEF) usan esta, así que no quedan colgadas de
    que haya o no un modelo disponible. La conducta del modelo pasa por las
    mismas guardas y sus rechazos los cuenta CP-IA-01.
    """
    return evaluar(conjunto_oro, backend="lineabase", defectos=defectos, raiz_repo=raiz_repo)


@pytest.fixture(scope="session")
def evaluaciones(evaluacion_base: dict, conjunto_oro: dict, defectos: set[str], backend: str,
                 raiz_repo: Path) -> dict:
    """Las evaluaciones que comparten CP-IA-01 y CP-IA-02.

    Siempre se mide `lineabase` (el control, que corre hoy). Si el arnés corre
    con un modelo, se mide además ese backend, para poder comparar las dos
    columnas con la misma entrada y el mismo conjunto de oro.
    """
    base = evaluacion_base
    if backend == "lineabase":
        return {"lineabase": base, "elegido": base, "hay_modelo": False}
    del_modelo = evaluar(conjunto_oro, backend=backend, defectos=defectos, raiz_repo=raiz_repo)
    if del_modelo["casos_medidos"] == 0:
        # El backend pedido no contestó ni una vez (falta la clave, no hay red o
        # no hay respuestas grabadas). No se degrada a la línea base por lo bajo
        # ni se escribe un número: se omite diciendo qué pasó.
        primero = del_modelo["errores_del_backend"][0]["motivos"][0] if del_modelo["errores_del_backend"] else "—"
        pytest.skip(f"El backend '{backend}' no clasificó ningún caso, así que no hay nada que medir. "
                    f"Primer error: {primero}")
    return {"lineabase": base, "elegido": del_modelo, "hay_modelo": True}


# ---------------------------------------------------------------------------
# Runs sintéticos: un junit-cp.xml escrito a mano para probar un riesgo
# ---------------------------------------------------------------------------

PROPIEDADES = ("hu", "ca", "defecto", "modulo", "nivel", "tipo", "estado", "ejecuciones", "archivo")


def escribir_junit_por_caso(carpeta: Path, casos: list[dict], *, nombre_run: str = "Qolqe · run de prueba") -> Path:
    """Escribe un `junit-cp.xml` con el mismo formato que `.github/scripts/trazabilidad.py`.

    Sirve para armar la entrada exacta que necesita un riesgo (una inyección en
    el log, un DEF que no existe, un caso sin ejecutar) sin tocar el repositorio
    ni correr las suites de Qolqe.
    """
    carpeta.mkdir(parents=True, exist_ok=True)
    suites = ET.Element("testsuites", {"name": nombre_run})
    suite = ET.SubElement(suites, "testsuite", {"name": "prueba", "tests": str(len(casos))})
    for caso in casos:
        elemento = ET.SubElement(suite, "testcase", {"classname": caso.get("classname", "prueba"),
                                                     "name": caso["name"], "time": "0.1"})
        propiedades = ET.SubElement(elemento, "properties")
        for nombre in PROPIEDADES:
            if caso.get(nombre):
                ET.SubElement(propiedades, "property", {"name": nombre, "value": caso[nombre]})
        if caso.get("estado") == "xfailed":
            ET.SubElement(elemento, "skipped", {"type": "xfail", "message": caso.get("mensaje_xfail", "fallo esperado")})
        if caso.get("fallo"):
            fallo = ET.SubElement(elemento, "failure", {"message": caso.get("mensaje_fallo", "falló el caso")})
            fallo.text = caso["fallo"]
        if caso.get("salida"):
            ET.SubElement(elemento, "system-out").text = caso["salida"]
    ruta = carpeta / "junit-cp.xml"
    ET.ElementTree(suites).write(ruta, encoding="utf-8", xml_declaration=True)
    return ruta


@pytest.fixture
def run_sintetico(tmp_path: Path):
    """Factory de carpetas de run: `run_sintetico(casos, logs={...})` devuelve la carpeta."""
    contador = {"n": 0}

    def armar(casos: list[dict], logs: dict[str, str] | None = None) -> Path:
        contador["n"] += 1
        carpeta = tmp_path / f"run{contador['n']}"
        escribir_junit_por_caso(carpeta, casos)
        for nombre, contenido in (logs or {}).items():
            (carpeta / nombre).write_text(contenido, encoding="utf-8")
        return carpeta

    return armar


def _caso_base(**cambios) -> dict:
    """Un caso de fallo esperado como los 40 del run real, para construir variantes."""
    caso = {
        "name": "CP-A04 El alias admite la letra ñ",
        "classname": "G4.api",
        "hu": "HU-G4-01",
        "ca": "HU-G4-01:CA1",
        "defecto": "DEF-01",
        "modulo": "G4",
        "nivel": "api",
        "tipo": "funcional",
        "estado": "xfailed",
        "ejecuciones": "1/1",
        "archivo": "features/contactos_api.feature:43",
        "mensaje_xfail": "Defecto conocido DEF-01 (fallo esperado)",
        "salida": "xfailed: test_cpa04_el_alias_admite_la_letra_ñ",
    }
    caso.update(cambios)
    return caso


def _respuesta_forzada(**cambios) -> dict:
    """Una respuesta con la forma exacta del esquema.

    Se usa para forzar lo que un modelo real haría de vez en cuando (proponer un
    DEF que no existe, reescribir la evidencia, soltar una ruta de la máquina) sin
    quedarse esperando a que ocurra. Es la manera de probar una guarda: si nunca
    se le da una respuesta mala, la guarda nunca demuestra que rechaza algo.
    """
    propuesta = {
        "caso": "CP-A04",
        "grupo": "G1",
        "clase": "defecto_real",
        "defecto": "DEF-01",
        "confianza": "alta",
        "razon": "El escenario espera 201 y el run lo marca como fallo del producto.",
        "evidencia": "Fallaron 1 de 1 ejecuciones",
    }
    propuesta.update(cambios)
    return propuesta


@pytest.fixture(scope="session")
def caso_base():
    """Factory del caso del JUnit: `caso_base(estado="failed", defecto=None)`."""
    return _caso_base


@pytest.fixture(scope="session")
def respuesta_forzada():
    """Factory de una respuesta del modelo con la forma del esquema."""
    return _respuesta_forzada


@pytest.fixture(scope="session")
def repeticiones() -> int:
    """Cuántas veces se repite la misma entrada en CP-IA-06."""
    return REPETICIONES


@pytest.fixture(scope="session")
def comando_de_la_corrida_real() -> str:
    """El comando exacto que produce los números que hoy quedan pendientes."""
    return COMANDO_DE_LA_CORRIDA_REAL
