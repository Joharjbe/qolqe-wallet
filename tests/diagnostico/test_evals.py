"""CP-IA-01 y CP-IA-02: evals contra el conjunto de oro y comparación con la línea base.

Conceptos de la clase 15 que se verifican aquí:

- **Evals.** La forma de validar un componente con IA no es mirar si la salida
  «se ve bien»: es medirla contra un conjunto de casos etiquetados antes de
  verla. Eso es `tests/diagnostico/conjunto_oro/` y esto es la medición.
- **Falsa cobertura.** Un reporte que diagnostica 40 fallos parece mucho
  trabajo; si acierta lo mismo que cuatro reglas de código, la IA no aportó
  nada. La única manera de saberlo es medir las dos columnas con la misma
  entrada: eso es la línea base (`--modelo lineabase`, sin IA).

Cómo se lee el resultado: **por clase, nunca con un solo porcentaje**. El
conjunto está desbalanceado a propósito (40 de 52 casos son `defecto_real`,
el 77 %), así que un promedio único lo decidiría esa clase sola.
"""

from __future__ import annotations

import json
from pathlib import Path

from herramientas.diagnostico_ia import guardas

# Mínimos MEDIDOS hoy con `lineabase` (ver el archivo de resultados). No son una
# meta inventada: son el número que dio la corrida y que no debe empeorar. Si
# alguien cambia las reglas de la línea base y bajan, la comparación de CP-IA-02
# cambió y hay que volver a leerla, no subirle el techo a la prueba.
PISO_LINEABASE = {"defecto_real": 38, "prueba_inestable": 4, "error_entorno": 7}


def escribir_resultados(carpeta: Path, evaluaciones: dict, comando_pendiente: str) -> Path:
    """Escribe la matriz de confusión y la comparación en un archivo legible.

    Tiene que quedar en un archivo y no solo en la consola: es la evidencia que
    se muestra en la exposición y la que se compara con la próxima corrida.
    """
    base = evaluaciones["lineabase"]
    elegido = evaluaciones["elegido"]
    clases = tuple(guardas.CLASES)
    lineas = [
        f"# Evals de la capacidad de IA · backend `{elegido['backend']}`",
        "",
        "Medición del componente `herramientas/diagnostico_ia/` contra el conjunto de oro",
        "`tests/diagnostico/conjunto_oro/conjunto_oro.json`. Lo escribe `tests/diagnostico/test_evals.py`",
        "(CP-IA-01 y CP-IA-02) cada vez que corre el arnés.",
        "",
        f"- Casos del conjunto: **{elegido['casos_del_conjunto']}**",
        f"- Casos con una clasificación aceptada por las guardas: **{elegido['casos_medidos']}**",
        f"- Casos sin clasificación: {', '.join(elegido['sin_prediccion']) or 'ninguno'}",
        (f"- Grupos que arma la firma determinista con las {elegido['casos_del_conjunto']} entradas en un solo "
         f"pase: **{elegido['grupos_del_pase_unico']}**"),
        f"- Respuestas rechazadas por las guardas: **{len(elegido['rechazos_de_guardas'])}**",
        f"- Errores del backend (sin clave, sin red): **{len(elegido['errores_del_backend'])}**",
        "",
        "## Exactitud por clase",
        "",
        "| Clase (lo que dice el conjunto de oro) | Aciertos | Casos | Se lee |",
        "|---|---:|---:|---|",
    ]
    for clase in clases:
        cuenta = elegido["por_clase"][clase]
        lineas.append(f"| `{clase}` | {cuenta['aciertos']} | {cuenta['total']} | "
                      f"{cuenta['aciertos']} de {cuenta['total']} |")
    lineas += [
        "",
        "Sin promedio global: el conjunto está desbalanceado y un solo porcentaje lo decidiría `defecto_real`.",
        "",
        "## Matriz de confusión",
        "",
        "Filas: la clase del conjunto de oro. Columnas: la que propuso el componente.",
        "",
        "| oro ↓ / propuesto → | " + " | ".join(f"`{c}`" for c in clases) + " |",
        "|---|" + "---:|" * len(clases),
    ]
    for real in clases:
        fila = " | ".join(str(elegido["matriz"][real][pred]) for pred in clases)
        lineas.append(f"| `{real}` | {fila} |")
    lineas += [
        "",
        "## DEF-xx propuesto",
        "",
        f"- Casos de oro que tienen un `DEF-xx` correcto esperado: **{elegido['defecto']['total']}**",
        f"- Acertados: **{elegido['defecto']['aciertos']}**",
        f"- `DEF-xx` propuestos en total: **{elegido['defecto']['propuestos']}**",
        (f"- `DEF-xx` que no existen en `docs/defectos.md` y pasaron las guardas: "
         f"**{elegido['defecto']['inventados']}** (tiene que ser 0: lo impide la guarda 2)"),
        "",
        "## Confianza declarada",
        "",
        "| Confianza | Casos |",
        "|---|---:|",
    ]
    for nivel, cuenta in elegido["confianzas"].items():
        lineas.append(f"| {nivel} | {cuenta} |")
    hay_modelo = evaluaciones["hay_modelo"]
    titulo_modelo = f"`{elegido['backend']}`" if hay_modelo else "modelo (pendiente)"
    lineas += [
        "",
        "## CP-IA-02 · Qué aporta la IA frente a la línea base",
        "",
        f"| Medida | `lineabase` (reglas, sin IA) | {titulo_modelo} |",
        "|---|---:|---:|",
    ]

    def columna_del_modelo(cuenta: dict) -> str:
        """La celda del modelo: el número si se midió, «pendiente» si no. Nunca un número inventado."""
        return f"{cuenta['aciertos']} de {cuenta['total']}" if hay_modelo else "pendiente"

    for clase in clases:
        base_clase = base["por_clase"][clase]
        lineas.append(f"| `{clase}` | {base_clase['aciertos']} de {base_clase['total']} | "
                      f"{columna_del_modelo(elegido['por_clase'][clase])} |")
    lineas.append(f"| `DEF-xx` acertados | {base['defecto']['aciertos']} de {base['defecto']['total']} | "
                  f"{columna_del_modelo(elegido['defecto'])} |")
    if hay_modelo:
        del_modelo = {fila["oro"]: fila["clase_propuesta"] for fila in elegido["detalle"]}
        acuerdo = sum(1 for fila in base["detalle"] if del_modelo.get(fila["oro"]) == fila["clase_propuesta"])
        lineas += ["", (f"Acuerdo entre la línea base y el modelo: **{acuerdo} de {len(base['detalle'])}** "
                        f"casos clasificados igual.")]
    else:
        lineas += ["", ("La columna del modelo está **pendiente de corrida real**: hoy no hay clave de API en "
                        "la máquina y el arnés no inventa el número. Se produce con:"), "", "```bash",
                   comando_pendiente, "```"]
    lineas += ["", "## Casos en los que la clase propuesta no coincide", "",
               ("Es la lista que se mira para decidir si el componente sirve. Un error aquí no es un error del "
                "conjunto de oro: es el resultado de la medición."), "",
               "| Oro | Caso | Clase de oro | Clase propuesta | Confianza | Razón |", "|---|---|---|---|---|---|"]
    for fila in elegido["detalle"]:
        if not fila["acierto"]:
            lineas.append(f"| {fila['oro']} | {fila['caso']} | `{fila['clase_oro']}` | "
                          f"`{fila['clase_propuesta']}` | {fila['confianza']} | {fila['razon']} |")
    ruta = carpeta / f"evals-{elegido['backend']}.md"
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    (carpeta / f"evals-{elegido['backend']}.json").write_text(
        json.dumps(evaluaciones, ensure_ascii=False, indent=2), encoding="utf-8")
    return ruta


def test_cp_ia_01_evals_contra_el_conjunto_de_oro(evaluaciones, carpeta_resultados, defectos, backend,
                                                  comando_de_la_corrida_real):
    """CP-IA-01 · Evals: exactitud por clase y matriz de confusión, en un archivo.

    Concepto de la clase 15: **evals**. El componente se mide contra casos
    etiquetados de antemano, con la entrada que de verdad va a ver (la del
    conjunto de oro, ya sin las fugas del artefacto).

    Lo que se exige:
      1. Que TODOS los casos del conjunto reciban una clasificación aceptada.
         Un caso sin clasificar no es «no sé»: es un hueco en la medición.
      2. Que la matriz de confusión cuadre con el número de casos.
      3. Que ningún DEF-xx aceptado se haya inventado (lo impide la guarda 2).
      4. Con `lineabase`, que no baje del piso ya medido.
    """
    elegido = evaluaciones["elegido"]
    ruta = escribir_resultados(carpeta_resultados, evaluaciones, comando_de_la_corrida_real)

    assert elegido["sin_prediccion"] == [], (
        f"quedaron casos de oro sin clasificación aceptada: {elegido['sin_prediccion']}")
    assert elegido["casos_medidos"] == elegido["casos_del_conjunto"]
    total_matriz = sum(sum(fila.values()) for fila in elegido["matriz"].values())
    assert total_matriz == elegido["casos_del_conjunto"]
    assert elegido["defecto"]["inventados"] == 0, "pasó un DEF-xx que no existe en docs/defectos.md"
    for propuesta in elegido["detalle"]:
        assert propuesta["defecto_propuesto"] is None or propuesta["defecto_propuesto"] in defectos

    if backend == "lineabase":
        # La línea base es código determinista: un rechazo de guarda aquí sería
        # un error del componente o del arnés, no un dato sobre el modelo.
        assert elegido["rechazos_de_guardas"] == []
        assert elegido["errores_del_backend"] == []
        for clase, piso in PISO_LINEABASE.items():
            aciertos = elegido["por_clase"][clase]["aciertos"]
            assert aciertos >= piso, f"{clase}: {aciertos} aciertos, el piso medido es {piso}"
    # Con un modelo real el arnés MIDE y escribe; no hay piso porque todavía no
    # se ha corrido ninguna vez. El piso se fija con el resultado de esa corrida.

    assert ruta.is_file()
    texto = ruta.read_text(encoding="utf-8")
    assert "Matriz de confusión" in texto
    assert "Exactitud por clase" in texto


def test_cp_ia_02_linea_base_frente_a_la_ia(evaluaciones, carpeta_resultados, comando_de_la_corrida_real):
    """CP-IA-02 · La comparación que responde «qué aporta».

    Concepto de la clase 15: **falsa cobertura**. Un componente con IA puede
    producir mucho texto y no aportar nada que no haga una regla. El control es
    `lineabase`, el clasificador por reglas del propio componente.

    Lo que se exige hoy, medido:
      1. La columna de la línea base está medida completa (52 de 52).
      2. La línea base NO propone ningún DEF-xx. Es el hueco concreto que la IA
         tiene que llenar: la entrada del conjunto no trae el DEF (se le quitó
         como fuga), así que proponerlo obliga a leer el escenario de Gherkin y
         cruzarlo con el catálogo de defectos, y eso una regla no lo hace.
      3. La línea base declara confianza `baja` en la mayoría de los casos: ella
         misma dice que está suponiendo. Es un control honesto, no un rival de
         cartón.
      4. La columna del modelo queda escrita como pendiente mientras no haya
         corrida real, con el comando que la produce.
    """
    base = evaluaciones["lineabase"]
    ruta = carpeta_resultados / f"evals-{evaluaciones['elegido']['backend']}.md"
    if not ruta.is_file():
        escribir_resultados(carpeta_resultados, evaluaciones, comando_de_la_corrida_real)
    texto = ruta.read_text(encoding="utf-8")

    assert base["casos_medidos"] == base["casos_del_conjunto"]
    assert base["defecto"]["total"] > 0, "el conjunto de oro no trae ningún DEF esperado"
    assert base["defecto"]["propuestos"] == 0, (
        "la línea base propuso un DEF-xx; eso cambia la comparación de CP-IA-02 y hay que volver a leerla")
    assert base["defecto"]["aciertos"] == 0
    bajas = base["confianzas"]["baja"]
    assert bajas > base["confianzas"]["alta"], (
        "la línea base dejó de declarar confianza baja: ya no se puede decir que 'ella misma avisa que supone'")

    assert "Qué aporta la IA frente a la línea base" in texto
    if evaluaciones["hay_modelo"]:
        assert "Acuerdo entre la línea base y el modelo" in texto
    else:
        assert "pendiente de corrida real" in texto
        assert "DIAGNOSTICO_IA_BACKEND=anthropic" in texto
