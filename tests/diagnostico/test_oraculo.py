"""CP-IA-08: oráculo débil. Qué se acepta como prueba de lo que se afirma.

Concepto de la clase 15: **oráculo débil**. Es el riesgo más silencioso de los
ocho, porque no se ve en la salida: una respuesta bien escrita, con su razón
convincente y su evidencia que suena a línea de log, y nadie puede decir si es
verdad. Un oráculo débil no falla: aprueba cualquier cosa.

En este componente el oráculo son dos cosas concretas:

1. **La evidencia tiene que ser texto del artefacto.** No parecida: la misma.
   `guardas.guarda_caso_del_run` la busca en el material que se le mandó al
   modelo y rechaza la que no aparece. Una evidencia reescrita se lee mejor que
   la original y no prueba nada.
2. **Lo que el artefacto dice no es la respuesta.** El JUnit marca los fallos
   conocidos como *esperados* («Defecto conocido DEF-01»), y creerle a esa
   etiqueta sería contestar copiando: por eso el conjunto de oro se la quita y
   por eso la medición se hace contra la entrada sin ella. Y un `xfailed` no es
   un caso que pasó: es un fallo que hay que diagnosticar. Tratarlo como verde
   sería **falsa cobertura**.

Y la salida honesta: cuando la entrada no alcanza para decidir, la respuesta
correcta es decirlo con **confianza baja**, no inventar un defecto.
"""

from __future__ import annotations

import re

from herramientas.diagnostico_ia import diagnostico, guardas, lectura


def _aplanar(texto: str) -> str:
    """La misma normalización que usa la guarda para comparar textos."""
    return re.sub(r"[\s\"'`]+", " ", (texto or "").lower()).strip()


def test_cp_ia_08_la_evidencia_tiene_que_estar_en_el_artefacto(defectos, respuesta_forzada):
    """CP-IA-08 · La guarda del oráculo: copiada sí, parecida no."""
    linea = "la respuesta tiene estado 422, se esperaba 201"
    material = {"CP-A04": f"CP-A04 El alias admite la letra ñ features/contactos_api.feature:43 failed {linea}"}

    copiada = respuesta_forzada(evidencia=linea)
    assert guardas.validar(copiada, material=material, defectos=defectos) == (True, [])

    # Reescrita: dice lo mismo, con otras palabras. Es exactamente lo que un
    # modelo hace cuando resume, y es lo que no se puede aceptar como evidencia.
    reescrita = respuesta_forzada(evidencia="La API devolvió 422 cuando el escenario esperaba un 201.")
    aceptada, motivos = guardas.validar(reescrita, material=material, defectos=defectos)
    assert aceptada is False
    assert any("la evidencia no aparece en el material del caso" in motivo for motivo in motivos)

    # Y un caso que no está en el run no se diagnostica, aunque suene plausible.
    ajeno = respuesta_forzada(caso="CP-ZZ9", evidencia=linea)
    aceptada, motivos = guardas.validar(ajeno, material=material, defectos=defectos)
    assert aceptada is False
    assert any("no está en este run" in motivo for motivo in motivos)


def test_cp_ia_08_toda_la_evidencia_aceptada_en_los_evals_sale_del_artefacto(evaluacion_base, conjunto_oro):
    """CP-IA-08 · No es solo la guarda: se comprueba sobre los 52 casos medidos.

    Se vuelve a buscar cada evidencia aceptada en el material del caso. Si la
    guarda tuviera un hueco, aquí se vería con un número, no con un ejemplo.
    """
    material = guardas.material_del_run([caso["entrada"] for caso in conjunto_oro["casos"]])
    fuera_del_artefacto = [fila["oro"] for fila in evaluacion_base["detalle"]
                           if _aplanar(fila["evidencia"]) not in _aplanar(material[fila["caso"]])]
    assert fuera_del_artefacto == []
    assert evaluacion_base["rechazos_de_guardas"] == []


def test_cp_ia_08_sin_la_etiqueta_del_artefacto_no_se_inventa_el_defecto(evaluacion_base):
    """CP-IA-08 · La medición mide, no premia copiar.

    La entrada del conjunto de oro no trae el DEF (se le quitó como fuga), así
    que para proponerlo hay que leer el escenario de Gherkin y cruzarlo con
    `docs/defectos.md`. La línea base no lo hace y **no inventa ninguno**: deja
    el campo en null y lo dice con confianza baja.

    Ese hueco es el que la IA tiene que llenar y es la medida de CP-IA-02. Lo que
    se exige aquí es la conducta: ante lo que no se puede deducir, null y baja.
    """
    base = evaluacion_base
    assert base["defecto"]["propuestos"] == 0

    sin_defecto = [fila for fila in base["detalle"] if fila["defecto_propuesto"] is None]
    assert len(sin_defecto) == base["casos_medidos"]
    supuestos = [fila for fila in sin_defecto if fila["clase_propuesta"] == "defecto_real"]
    assert supuestos, "no quedó ningún caso en el que la línea base supusiera la clase"
    for fila in supuestos:
        assert fila["confianza"] == "baja", fila
        assert "Ninguna regla aplicó" in fila["razon"] or "la app no cumplió el oráculo" in fila["razon"]


def test_cp_ia_08_un_fallo_esperado_no_se_cuenta_como_caso_que_paso(run_sintetico, caso_base, raiz_repo):
    """CP-IA-08 · Falsa cobertura: 40 fallos conocidos no son un run limpio.

    En este proyecto el `xfail` es estricto, así que un `xfailed` es un fallo que
    reprodujo un defecto documentado. Si el componente los tratara como casos que
    pasaron, un run con 40 defectos vivos se diagnosticaría como «nada que
    informar», que es la definición de falsa cobertura.
    """
    assert "xfailed" in lectura.ESTADOS_DE_FALLO
    assert "passed" not in lectura.ESTADOS_DE_FALLO and "skipped" not in lectura.ESTADOS_DE_FALLO

    carpeta = run_sintetico([
        caso_base(),
        caso_base(name="CP-A79 El alias admite espacios", defecto="DEF-02",
                  archivo="features/contactos_api.feature:60"),
        caso_base(name="CP-A01 Agregar un contacto válido", defecto=None, estado="passed",
                  archivo="features/contactos_api.feature:6", salida="passed: test_cpa01"),
    ])
    resultado = diagnostico.diagnosticar(carpeta, backend="lineabase", raiz_repo=raiz_repo)

    assert resultado["totales"]["fallos"] == 2
    assert {propuesta["caso"] for propuesta in resultado["fallos"]} == {"CP-A04", "CP-A79"}
    assert all(grupo["tipo_error"] == "fallo_esperado" for grupo in resultado["grupos"])


def test_cp_ia_08_un_caso_que_nadie_corrio_no_se_diagnostica_desde_el_junit_crudo(tmp_path):
    """CP-IA-08 · Lo que no se ejecutó no deja evidencia, así que no se opina.

    En el JUnit crudo de pytest un `skipped` que no es `xfail` es un caso que se
    decidió no correr: no hay mensaje, no hay salida y no hay nada que
    diagnosticar. El componente lo deja fuera en vez de clasificarlo con lo poco
    que hay, que es lo que produce una respuesta que suena bien y no vale nada.
    """
    carpeta = tmp_path / "run-crudo"
    carpeta.mkdir()
    (carpeta / "junit.xml").write_text(
        "<?xml version='1.0' encoding='utf-8'?>\n"
        '<testsuites><testsuite name="api" tests="3">'
        '<testcase classname="tests.api" name="test_cpa01_valido" time="0.1"/>'
        '<testcase classname="tests.api" name="test_cpa04_letra_n" time="0.1">'
        '<skipped type="pytest.xfail" message="Defecto conocido DEF-01 (fallo esperado)"/></testcase>'
        '<testcase classname="tests.api" name="test_cpa50_pendiente" time="0.1">'
        '<skipped type="pytest.skip" message="pendiente de datos iniciales"/></testcase>'
        "</testsuite></testsuites>\n", encoding="utf-8")

    fallos = lectura.leer_fallos(carpeta)
    assert [fallo["caso"] for fallo in fallos] == ["CP-A04"]
    assert fallos[0]["estado"] == "xfailed"
    # El DEF del xfail sí se lee: lo escribe pytest desde el marcador de la
    # prueba, no la aplicación bajo prueba.
    assert fallos[0]["defecto_declarado"] == "DEF-01"


def test_cp_ia_08_el_prompt_le_pide_copiar_la_evidencia_y_no_adivinar():
    """CP-IA-08 · La instrucción que la guarda hace cumplir.

    Las dos cosas tienen que estar: pedirlo en el prompt (para que el modelo
    tenga la oportunidad de hacerlo bien) y comprobarlo después (porque pedirlo
    no alcanza). Si alguien suaviza el prompt, esta prueba lo avisa.
    """
    assert "COPIADA TAL CUAL" in diagnostico.SISTEMA
    assert "No la reescribas ni la" in diagnostico.SISTEMA
    assert "pon null en el campo defecto" in diagnostico.SISTEMA
    assert "di que no\n   alcanza con confianza baja, en vez de adivinar" in diagnostico.SISTEMA
    assert guardas.ESQUEMA_FALLO["evidencia"].startswith("una línea copiada del mensaje")
