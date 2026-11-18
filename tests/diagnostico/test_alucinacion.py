"""CP-IA-03: alucinación. Un DEF-xx que no existe no entra al reporte.

Concepto de la clase 15: **alucinación**. Un modelo contesta con la misma
seguridad cuando sabe y cuando no. En este componente la alucinación tiene una
forma concreta y peligrosa: proponer `DEF-31` para un fallo cuando el catálogo
`docs/defectos.md` llega hasta `DEF-29`. Un número inventado dentro de un
reporte de defectos es peor que no decir nada, porque alguien lo va a buscar.

La defensa no es pedirle al modelo que no invente (ya se le pide, en el prompt
del sistema): es **comprobarlo después**. `guardas.guarda_defecto_conocido`
cruza el DEF propuesto contra los encabezados de `docs/defectos.md` y descarta
la respuesta que no cuadra. Esa guarda es la que se prueba aquí, y se prueba con
una respuesta forzada: si solo se esperara a que un modelo alucine de verdad, la
guarda nunca demostraría que rechaza nada.

La misma regla corre en el otro sentido (defensa en profundidad): un DEF-xx que
el artefacto declara pero que no existe en el catálogo tampoco se le pasa al
modelo, para no sugerirle que lo repita.
"""

from __future__ import annotations

from herramientas.diagnostico_ia import diagnostico, guardas, lectura


def test_cp_ia_03_la_guarda_rechaza_un_defecto_que_no_existe(defectos, respuesta_forzada):
    """CP-IA-03 · El DEF propuesto tiene que existir en docs/defectos.md."""
    material = {"CP-A04": "Fallaron 1 de 1 ejecuciones"}

    inventado = respuesta_forzada(defecto="DEF-99")
    aceptada, motivos = guardas.validar(inventado, material=material, defectos=defectos)
    assert aceptada is False
    assert any("DEF-99 no existe en docs/defectos.md" in motivo for motivo in motivos)

    # Control: la misma respuesta con un DEF del catálogo sí se acepta. Sin este
    # contraste, una guarda que rechazara todo también «pasaría» la prueba.
    verdadero = respuesta_forzada(defecto="DEF-01")
    assert verdadero["defecto"] in defectos
    aceptada, motivos = guardas.validar(verdadero, material=material, defectos=defectos)
    assert (aceptada, motivos) == (True, [])

    # Y la salida honesta también se acepta: null es una respuesta válida.
    sin_defecto = respuesta_forzada(defecto=None, confianza="baja")
    aceptada, motivos = guardas.validar(sin_defecto, material=material, defectos=defectos)
    assert (aceptada, motivos) == (True, [])


def test_cp_ia_03_un_defecto_mal_formado_no_pasa_por_la_puerta_del_esquema(defectos, respuesta_forzada):
    """CP-IA-03 · La otra forma de inventar: un identificador que no tiene la forma de un DEF.

    La guarda del esquema corre primero, así que «el defecto 1 del reporte» o una
    lista de defectos se rechazan antes de llegar al cruce con el catálogo.
    """
    material = {"CP-A04": "Fallaron 1 de 1 ejecuciones"}
    for valor in ("DEF-1A", "el defecto del alias", ["DEF-01"], 1):
        aceptada, motivos = guardas.validar(respuesta_forzada(defecto=valor), material=material, defectos=defectos)
        assert aceptada is False, f"se aceptó un defecto mal formado: {valor!r}"
        assert any("defecto mal formado" in motivo for motivo in motivos)


def test_cp_ia_03_un_def_desconocido_del_artefacto_no_llega_al_reporte(run_sintetico, caso_base, raiz_repo):
    """CP-IA-03 · De punta a punta: el artefacto declara DEF-99 y el reporte no lo repite.

    Es el caso realista: `trazabilidad.py` copia la etiqueta `@DEF-xx` del
    escenario, así que una etiqueta mal escrita en un `.feature` mete un DEF que
    no existe. El componente lo borra del fallo antes de armar el prompt, lo
    cuenta aparte y nunca lo propone como defecto.
    """
    carpeta = run_sintetico([caso_base(defecto="DEF-99", mensaje_xfail="Defecto conocido DEF-99 (fallo esperado)")])

    fallos = lectura.leer_fallos(carpeta)
    assert len(fallos) == 1
    assert fallos[0]["defecto_declarado"] == "DEF-99"  # el artefacto lo trae

    resultado = diagnostico.diagnosticar(carpeta, backend="lineabase", raiz_repo=raiz_repo)
    assert resultado["totales"]["defectos_declarados_desconocidos"] == 1
    assert [propuesta["defecto"] for propuesta in resultado["fallos"]] == [None]
    assert all(grupo["defectos_declarados"] == [] for grupo in resultado["grupos"])

    reporte = diagnostico.a_markdown(resultado)
    # El reporte cuenta el hallazgo y NO escribe el identificador: quien lo lea no
    # se va a llevar un DEF-99 que no puede buscar en ninguna parte.
    assert "| DEF declarados que no existen en docs/defectos.md | 1 |" in reporte
    assert "DEF-99" not in reporte


def test_cp_ia_03_el_prompt_no_le_sugiere_el_def_desconocido_al_modelo(run_sintetico, caso_base, raiz_repo):
    """CP-IA-03 · Defensa en profundidad: lo que no existe no se le ofrece al modelo.

    Pasarle «el run declara DEF-99» sería invitarlo a repetirlo, y la guarda lo
    rechazaría después. Mejor no ensuciar el prompt: el fallo llega sin defecto
    declarado y el grupo, sin defectos.
    """
    carpeta = run_sintetico([caso_base(defecto="DEF-99", mensaje_xfail="Defecto conocido DEF-99 (fallo esperado)")])
    resultado = diagnostico.diagnosticar(carpeta, backend="lineabase", raiz_repo=raiz_repo)

    grupo = resultado["grupos"][0]
    fallos = lectura.leer_fallos(carpeta)
    fallos[0]["defecto_declarado"] = ""  # el estado con el que el componente arma el prompt
    prompt = diagnostico.prompt_del_grupo(grupo, fallos)

    assert "defecto declarado por el run: ninguno" in prompt
    assert "Defectos que el run ya declara para este grupo: ninguno" in prompt
