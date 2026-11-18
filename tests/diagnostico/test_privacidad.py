"""CP-IA-05: privacidad. Los dos lados del tubo.

Concepto de la clase 15: **privacidad**. Hay dos preguntas distintas y las dos
hay que contestar:

- **Lo que sale.** El reporte del diagnóstico se publica como artefacto del
  pipeline y se proyecta en una exposición. No puede llevar rutas de la máquina
  de nadie, claves, correos ni números que parezcan un celular o un documento.
  Eso lo hace cumplir `guardas.guarda_sin_datos_sensibles`, que corre sobre cada
  respuesta antes de escribirla.
- **Lo que entra.** Mandar texto a un modelo es sacarlo de la máquina. Así que
  importa igual qué se le manda: el prompt se arma SOLO con los campos del fallo
  que vienen del JUnit, no con el contenido de los logs del run ni con nada del
  `.env`.

Un hallazgo que esta prueba deja escrito y medido: el encabezado del reporte
imprime la carpeta del run (`- Run: /private/var/...`), que es una ruta de la
máquina. La escribe el código, no el modelo, y es un dato que el operador ya
conoce; pero si el reporte se publica tal cual, esa línea viaja. Queda anotada
como pendiente y aquí se comprueba que es la ÚNICA del reporte.
"""

from __future__ import annotations

import re

from herramientas.diagnostico_ia import agrupar, diagnostico, guardas, lectura

CLAVE_DE_MENTIRA = "sk-ant-ESTA-NO-ES-UNA-CLAVE-REAL-0000"
SECRETO_EN_EL_LOG = "contrasena-de-la-base-no-real-9f3a"


def _lineas_sensibles(texto: str) -> list[str]:
    """Los pedazos de texto que la guarda de privacidad marcaría."""
    encontrados = []
    for patron, motivo in guardas.PATRONES_SENSIBLES:
        for coincidencia in patron.findall(texto):
            encontrados.append(f"{motivo}: {coincidencia}")
    return encontrados


def test_cp_ia_05_la_guarda_rechaza_cada_tipo_de_dato_sensible(defectos, respuesta_forzada):
    """CP-IA-05 · Salida: los cuatro patrones, uno por uno.

    Se prueba con respuestas forzadas porque es la única manera de saber que la
    guarda rechaza: esperar a que un modelo copie un celular en la evidencia no
    es una prueba, es una apuesta.
    """
    material = {"CP-A04": "Fallaron 1 de 1 ejecuciones el contacto 912345678 de ana@ejemplo.pe"}
    casos = [
        ("ruta de la máquina", {"razon": "Falla en /Users/alumno/proyecto/qolqe/contactos.py al normalizar el alias."}),
        ("posible clave o token", {"razon": f"La prueba usó la clave {CLAVE_DE_MENTIRA} para autenticarse."}),
        ("correo electrónico", {"evidencia": "Fallaron 1 de 1 ejecuciones el contacto 912345678 de ana@ejemplo.pe"}),
        ("posible dato personal", {"razon": "El contacto 912345678 no se pudo agregar."}),
    ]
    for motivo_esperado, cambio in casos:
        aceptada, motivos = guardas.validar(respuesta_forzada(**cambio), material=material, defectos=defectos)
        assert aceptada is False, f"se aceptó una respuesta con {motivo_esperado}"
        assert any(motivo_esperado in motivo for motivo in motivos), motivos

    # Control: la respuesta limpia pasa. Una guarda que rechaza todo no sirve.
    aceptada, motivos = guardas.validar(respuesta_forzada(), material=material, defectos=defectos)
    assert (aceptada, motivos) == (True, [])


def test_cp_ia_05_el_resumen_del_run_tambien_pasa_por_la_guarda():
    """CP-IA-05 · Salida: el resumen no se escapa de la revisión.

    El resumen es texto libre del modelo y es lo primero que se lee en el
    reporte: si la guarda solo mirara las clasificaciones, el resumen sería la
    puerta de atrás.
    """
    aceptada, motivos = guardas.validar_resumen({
        "resumen": "40 fallos en 32 grupos, casi todos esperados.",
        "riesgo": "Conviene mirar primero los de contactos.",
    })
    assert (aceptada, motivos) == (True, [])

    aceptada, motivos = guardas.validar_resumen({
        "resumen": "40 fallos, todos en /Users/alumno/proyecto/qolqe-wallet.",
        "riesgo": "Escribir a soporte@ejemplo.pe.",
    })
    assert aceptada is False
    assert any("ruta de la máquina" in motivo for motivo in motivos)
    assert any("correo electrónico" in motivo for motivo in motivos)


def test_cp_ia_05_el_reporte_escrito_no_lleva_datos_sensibles(evaluacion_base, run_sintetico, caso_base,
                                                             raiz_repo):
    """CP-IA-05 · Salida: el reporte de verdad, no un ejemplo.

    Se revisan dos salidas reales: los textos que el componente propuso para los
    52 casos del conjunto de oro, y el reporte completo de un run.

    Del reporte se excluye una sola línea, la del encabezado con la carpeta del
    run, y se comprueba que no haya ninguna otra: ese es el hallazgo que queda
    anotado como pendiente, acotado y medido en vez de contado de palabra.
    """
    for fila in evaluacion_base["detalle"]:
        assert _lineas_sensibles(fila["razon"]) == [], fila
        assert _lineas_sensibles(str(fila["defecto_propuesto"])) == []

    carpeta = run_sintetico([caso_base(), caso_base(name="CP-A79 El alias admite espacios", defecto="DEF-02",
                                                    archivo="features/contactos_api.feature:60")])
    resultado = diagnostico.diagnosticar(carpeta, backend="lineabase", raiz_repo=raiz_repo)
    reporte = diagnostico.a_markdown(resultado)

    encabezado = [linea for linea in reporte.splitlines() if linea.startswith("- Run: ")]
    assert len(encabezado) == 1
    assert _lineas_sensibles(encabezado[0]) != [], (
        "si esta línea ya no trae la ruta del run, el pendiente de privacidad está resuelto "
        "y hay que quitar esta excepción")

    resto = "\n".join(linea for linea in reporte.splitlines() if not linea.startswith("- Run: "))
    assert _lineas_sensibles(resto) == []
    # Y en el JSON, la ruta está en un solo campo, no repartida por el documento.
    assert _lineas_sensibles(str(resultado["fallos"])) == []
    assert _lineas_sensibles(str(resultado["grupos"])) == []
    assert _lineas_sensibles(str(resultado["resumen"])) == []


def test_cp_ia_05_el_prompt_no_lleva_los_logs_del_run_ni_la_clave(run_sintetico, caso_base, monkeypatch):
    """CP-IA-05 · Entrada: qué se le manda al modelo.

    El prompt se arma con los campos del fallo que trae el JUnit y nada más. Dos
    cosas que están en la misma carpeta y NO viajan:

    - el contenido de los `*.log` del run (el log de uvicorn trae cadenas de
      conexión, consultas y rutas del runner);
    - la clave de API, que vive en el `.env` y solo la lee `modelo.py` para la
      cabecera de la petición.

    `lectura.leer_lineas_de_log()` existe para el resumen, pero el orquestador no
    la usa: por eso el cuerpo del log no entra al prompt. Esta prueba fija ese
    contrato, para que agregarlo sea una decisión y no un descuido.
    """
    monkeypatch.setenv("ANTHROPIC_API_KEY", CLAVE_DE_MENTIRA)
    log = (f"INFO: Uvicorn running on http://127.0.0.1:8000\n"
           f"ERROR: fallo al abrir sqlite:///datos/api.db?clave={SECRETO_EN_EL_LOG}\n"
           f"ERROR: traceback en /Users/alumno/proyecto/qolqe-wallet/datos/api.db\n")
    carpeta = run_sintetico([caso_base(estado="failed", defecto=None,
                                       fallo="AssertionError: la respuesta tiene estado 422, se esperaba 201")],
                            logs={"uvicorn-api.log": log})

    fallos = lectura.leer_fallos(carpeta)
    grupos = agrupar.agrupar(fallos)
    prompts = [diagnostico.prompt_del_grupo(grupo, agrupar.fallos_del_grupo(grupo, fallos)) for grupo in grupos]
    prompts.append(diagnostico.prompt_del_resumen(
        {"fallos": len(fallos), "casos_distintos": len(fallos), "grupos": len(grupos)}, {}, grupos))

    # El log está en la carpeta y tiene lo que no debe viajar.
    assert SECRETO_EN_EL_LOG in log
    assert lectura.leer_lineas_de_log(carpeta), "el log no quedó donde la prueba cree"

    for prompt in prompts:
        assert SECRETO_EN_EL_LOG not in prompt
        assert CLAVE_DE_MENTIRA not in prompt
        assert "sqlite:///" not in prompt
        assert _lineas_sensibles(prompt) == [], "el prompt lleva un dato que la guarda marcaría en la salida"

    # El prompt tampoco se arma con el nombre de la carpeta del run.
    for prompt in prompts:
        assert str(carpeta) not in prompt


def test_cp_ia_05_el_prompt_solo_lleva_los_campos_del_fallo(run_sintetico, caso_base):
    """CP-IA-05 · Entrada: la lista de lo que viaja es corta y se puede leer.

    Si alguien agrega un campo al prompt, esta prueba lo obliga a decirlo. Es la
    diferencia entre «creemos que no mandamos nada raro» y una lista revisable.
    """
    carpeta = run_sintetico([caso_base()])
    fallos = lectura.leer_fallos(carpeta)
    grupo = agrupar.agrupar(fallos)[0]
    prompt = diagnostico.prompt_del_grupo(grupo, fallos)

    etiquetas = set(re.findall(r"^\s*(?:- )?([a-z_]+)=", prompt, flags=re.MULTILINE))
    assert etiquetas <= {"estado", "ejecuciones", "nivel", "tipo", "hu", "ca", "archivo"}, etiquetas
    for esperado in ("Grupo G1", "Tipo de error (calculado por código)", "Archivo:", "Mensaje normalizado:",
                     "defecto declarado por el run:", "mensaje:"):
        assert esperado in prompt
