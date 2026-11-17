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

Dos decisiones de diseño de estas pruebas, que son las que las hacen evals y no
un sello de aprobación:

1. **No se le exige al modelo una exactitud mínima.** Una prueba que dice
   «falla si acierta menos del 80 %» no mide: aprueba. El umbral sería un
   número inventado y, el día que el modelo empeore, lo que se discutiría es el
   umbral y no el modelo. Aquí la prueba MIDE, escribe el resultado en
   `reportes/diagnostico_ia/` y falla solo por lo que de verdad es un defecto
   del componente (que no se pueda medir nada, que la matriz no cuadre, que una
   guarda deje pasar un `DEF-xx` inventado, que un caso se quede sin medir sin
   causa registrada, o que el conjunto de oro haya cambiado de tamaño sin que
   nadie lo note). Si el modelo pierde contra las reglas, eso se lee en el
   archivo de resultados; no es un fallo de la prueba.
2. **La línea base sí tiene piso.** Es código determinista: si baja, alguien
   cambió las reglas y la comparación hay que volver a leerla.

Y la parte que de verdad decide si la comparación sirve: `vistas_comparables`.
Los dos lados tienen que medirse sobre los mismos casos. Ver su docstring.
"""

from __future__ import annotations

import json
from pathlib import Path

from conftest import repartir_en_lotes

from herramientas.diagnostico_ia import agrupar, guardas

# Mínimos MEDIDOS hoy con `lineabase` (ver el archivo de resultados). No son una
# meta inventada: son el número que dio la corrida y que no debe empeorar. Si
# alguien cambia las reglas de la línea base y bajan, la comparación de CP-IA-02
# cambió y hay que volver a leerla, no subirle el techo a la prueba.
PISO_LINEABASE = {"defecto_real": 38, "prueba_inestable": 4, "error_entorno": 7}

# Las tres razones por las que un caso del conjunto puede quedarse sin
# clasificación. Ver `causa_de_cada_hueco`: la primera y la tercera son datos
# sobre el modelo, la segunda es infraestructura.
TIPOS_DE_CAUSA = ("guarda", "backend", "respuesta_incompleta")


# ---------------------------------------------------------------------------
# Por qué un caso se quedó sin clasificación
# ---------------------------------------------------------------------------

def grupo_por_caso_de_oro(conjunto_oro: dict) -> dict[str, str]:
    """A qué grupo (`G1`, `G2`, …) le tocó cada caso de oro.

    Hace falta para saber POR QUÉ un caso quedó sin clasificar: el modelo no se
    pregunta caso por caso sino grupo por grupo, así que cuando el backend falla
    se caen de la medición todos los casos de ese grupo a la vez. El reparto en
    lotes y la agrupación son los mismos que usa `conftest.evaluar`, que es lo
    que se está midiendo; se reutilizan en vez de copiarse para que no se
    desincronicen.
    """
    del_caso: dict[str, str] = {}
    for lote in repartir_en_lotes(conjunto_oro["casos"]):
        grupos = agrupar.agrupar([caso["entrada"] for caso in lote])
        de_este_lote = {cp: grupo["id"] for grupo in grupos for cp in grupo["casos"]}
        for caso in lote:
            del_caso[caso["id"]] = de_este_lote.get(caso["entrada"]["caso"], "")
    return del_caso


def causa_de_cada_hueco(evaluacion: dict, conjunto_oro: dict) -> dict[str, dict]:
    """Por cada caso sin clasificación, la causa y de qué tipo es.

    La separación importa para leer el resultado, y es la diferencia entre un
    hallazgo sobre el modelo y un problema de infraestructura:

    - `guarda`: el modelo contestó y la guarda rechazó la respuesta. ES un dato
      sobre el modelo, y además es la guarda haciendo su trabajo.
    - `backend`: el backend no contestó (429 del límite del plan, 503, red). NO
      es un dato sobre el modelo: es que la medición no se pudo hacer.
    - `respuesta_incompleta`: el backend sí contestó por el grupo y ninguna
      guarda rechazó nada, pero la respuesta no trajo una clasificación para
      este caso. Se deduce por descarte, y es seguro: si no hubo error de
      backend, hubo respuesta; si no hubo rechazo, nada se descartó; entonces la
      respuesta venía incompleta. SÍ es un dato sobre el modelo (dejó casos
      fuera de su propia respuesta) y además deja a la vista un hueco del
      componente: hoy no lo registra en ninguna parte, se descubre cruzando los
      grupos con las predicciones como se hace aquí. Esa cuenta debería llevarla
      el componente (`clasificar_fallos`), no esta prueba.

    Nota de precisión: el resultado solo guarda el ID del grupo que falló, no el
    lote, y los IDs se reinician en cada lote. Un caso se atribuye al backend si
    su grupo, en su propio lote, tiene el mismo ID que uno de los grupos que
    fallaron. Con el reparto actual (un solo caso repetido en el segundo lote)
    no hay ambigüedad; si algún día hubiera muchos lotes, esto habría que
    afinarlo.
    """
    por_caso_de_oro = grupo_por_caso_de_oro(conjunto_oro)
    cp_de_oro = {caso["id"]: caso["entrada"]["caso"] for caso in conjunto_oro["casos"]}
    de_guarda = {rechazo["caso"]: rechazo["motivos"] for rechazo in evaluacion["rechazos_de_guardas"] if rechazo["caso"]}
    de_backend = {rechazo["grupo"]: rechazo["motivos"] for rechazo in evaluacion["errores_del_backend"]}

    causas: dict[str, dict] = {}
    for oro in evaluacion["sin_prediccion"]:
        cp, grupo = cp_de_oro.get(oro, ""), por_caso_de_oro.get(oro, "")
        if cp in de_guarda:
            causas[oro] = {"caso": cp, "grupo": grupo, "tipo": "guarda",
                           "motivo": "; ".join(de_guarda[cp])}
        elif grupo in de_backend:
            causas[oro] = {"caso": cp, "grupo": grupo, "tipo": "backend",
                           "motivo": "; ".join(de_backend[grupo])}
        else:
            causas[oro] = {"caso": cp, "grupo": grupo, "tipo": "respuesta_incompleta",
                           "motivo": ("el backend contestó por el grupo y ninguna guarda rechazó nada, así que la "
                                      "respuesta del modelo no incluyó este caso")}
    return causas


# ---------------------------------------------------------------------------
# La comparación honesta entre la línea base y el modelo
# ---------------------------------------------------------------------------

def vistas_comparables(base: dict, elegido: dict, conjunto_oro: dict) -> dict:
    """Las dos lecturas con las que la comparación sí es honesta.

    El problema concreto: la línea base clasifica los 52 casos (es código, no se
    cae) y el modelo clasificó 39, porque 13 se le cayeron. Si cada columna se
    divide por su propio denominador sale «38 de 40 contra 20 de 29», y eso NO
    está comparando lo mismo: son dos conjuntos de casos distintos. Presentarlo
    así haría ver mejor al modelo justo por los casos que perdió.

    Las dos lecturas que sí se pueden defender, y las dos se informan porque
    responden preguntas distintas:

    - `mismo_subconjunto` — **¿quién clasifica mejor cuando los dos contestan?**
      Las dos columnas se miden sobre los MISMOS casos: los que el modelo
      alcanzó a clasificar. Mismo denominador en las dos columnas. Es la calidad
      de la clasificación, aislada de la disponibilidad.
    - `conjunto_completo` — **¿qué componente sirve más para el trabajo?** Las
      dos columnas se miden sobre los 52 casos y un caso sin respuesta cuenta
      como fallo, porque para quien recibe el reporte un fallo sin diagnosticar
      no es «no sé»: es trabajo que no se hizo. Mismo denominador y además el
      del problema real.

    Ninguna de las dos es la buena y la otra la mala: la primera sin la segunda
    esconde los 13 huecos, y la segunda sin la primera castiga al modelo por
    caídas del backend que no dicen nada de su clasificación. Por eso van las
    dos, una al lado de la otra, en el archivo de resultados.
    """
    clases = tuple(guardas.CLASES)
    clase_de_oro = {caso["id"]: caso["etiqueta"]["clase"] for caso in conjunto_oro["casos"]}
    defecto_de_oro = {caso["id"]: caso["etiqueta"]["defecto"] for caso in conjunto_oro["casos"]}
    filas_base = {fila["oro"]: fila for fila in base["detalle"]}
    filas_modelo = {fila["oro"]: fila for fila in elegido["detalle"]}
    todos = [caso["id"] for caso in conjunto_oro["casos"]]
    subconjunto = [oro for oro in todos if oro in filas_base and oro in filas_modelo]

    def contar(ids: list[str]) -> dict:
        """Aciertos de cada columna sobre la MISMA lista de casos de oro.

        Un caso que una columna no clasificó cuenta como fallo suyo, nunca se
        saca del denominador: sacarlo es justo lo que rompía la comparación.
        """
        por_clase = {clase: {"total": 0, "base": 0, "modelo": 0} for clase in clases}
        defecto = {"total": 0, "base": 0, "modelo": 0}
        for oro in ids:
            clase = clase_de_oro[oro]
            por_clase[clase]["total"] += 1
            if filas_base.get(oro, {}).get("clase_propuesta") == clase:
                por_clase[clase]["base"] += 1
            if filas_modelo.get(oro, {}).get("clase_propuesta") == clase:
                por_clase[clase]["modelo"] += 1
            esperado = defecto_de_oro.get(oro)
            if esperado:
                defecto["total"] += 1
                if filas_base.get(oro, {}).get("defecto_propuesto") == esperado:
                    defecto["base"] += 1
                if filas_modelo.get(oro, {}).get("defecto_propuesto") == esperado:
                    defecto["modelo"] += 1
        return {"casos": len(ids), "por_clase": por_clase, "defecto": defecto}

    return {
        "ids_del_subconjunto": subconjunto,
        "mismo_subconjunto": contar(subconjunto),
        "conjunto_completo": contar(todos),
    }


# ---------------------------------------------------------------------------
# El archivo de resultados
# ---------------------------------------------------------------------------

def escribir_resultados(carpeta: Path, evaluaciones: dict, conjunto_oro: dict, comando_pendiente: str) -> Path:
    """Escribe la matriz de confusión y la comparación en un archivo legible.

    Tiene que quedar en un archivo y no solo en la consola: es la evidencia que
    se muestra en la exposición y la que se compara con la próxima corrida.
    """
    base = evaluaciones["lineabase"]
    elegido = evaluaciones["elegido"]
    hay_modelo = evaluaciones["hay_modelo"]
    clases = tuple(guardas.CLASES)
    causas = causa_de_cada_hueco(elegido, conjunto_oro)
    por_tipo_de_causa = {tipo: [oro for oro, c in causas.items() if c["tipo"] == tipo]
                         for tipo in TIPOS_DE_CAUSA}
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
        f"- Errores del backend (sin clave, sin red, límite del plan): **{len(elegido['errores_del_backend'])}**",
        "",
        "## Exactitud por clase",
        "",
        ("Esta tabla es la medida CRUDA de cada columna sobre los casos que ELLA clasificó, así que su "
         "denominador cambia con lo que se le cayó. **No se usa para comparar las dos columnas**: para eso está "
         "«Comparación comparable» más abajo."),
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
        "## Casos sin clasificación y su causa",
        "",
        ("Un caso sin clasificar no se tapa ni se saca del conjunto: se cuenta con su causa. La distinción es "
         "la que decide qué se puede afirmar. Un rechazo de guarda y una respuesta incompleta SON datos sobre el "
         "modelo (contestó algo que no se podía sostener, o dejó casos fuera de su respuesta). Un error del "
         "backend NO lo es: es infraestructura, y de ese caso simplemente no hay medición."),
        "",
        (f"- Rechazados por una guarda (dato del modelo): **{len(por_tipo_de_causa['guarda'])}** "
        f"({', '.join(por_tipo_de_causa['guarda']) or 'ninguno'})"),
        (f"- Perdidos por un error del backend (infraestructura): **{len(por_tipo_de_causa['backend'])}** "
        f"({', '.join(por_tipo_de_causa['backend']) or 'ninguno'})"),
        (f"- El modelo contestó por el grupo y dejó el caso fuera (dato del modelo): "
        f"**{len(por_tipo_de_causa['respuesta_incompleta'])}** "
        f"({', '.join(por_tipo_de_causa['respuesta_incompleta']) or 'ninguno'}) · lo registra el propio "
        "componente como un rechazo de tipo `sin_respuesta`, no se deduce por descarte"),
        "",
        "| Oro | Caso | Grupo | Tipo de causa | Motivo |",
        "|---|---|---|---|---|",
    ]
    for oro, causa in causas.items():
        lineas.append(f"| {oro} | {causa['caso']} | {causa['grupo']} | {causa['tipo']} | {causa['motivo']} |")
    if not causas:
        lineas.append("| — | — | — | — | todos los casos recibieron clasificación |")
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
    titulo_modelo = f"`{elegido['backend']}`" if hay_modelo else "modelo (pendiente)"
    lineas += [
        "",
        "## CP-IA-02 · Qué aporta la IA frente a la línea base",
        "",
    ]
    if not hay_modelo:
        lineas += [
            ("Esta corrida se hizo con `lineabase` (reglas, sin IA, sin red), así que la columna del modelo queda "
             "**pendiente de corrida real**: el arnés no inventa un número que no midió. Se produce con:"),
            "", "```bash", comando_pendiente, "```",
            "",
            "| Medida | `lineabase` (reglas, sin IA) | modelo (pendiente) |",
            "|---|---:|---:|",
        ]
        for clase in clases:
            cuenta = base["por_clase"][clase]
            lineas.append(f"| `{clase}` | {cuenta['aciertos']} de {cuenta['total']} | pendiente |")
        lineas.append(f"| `DEF-xx` acertados | {base['defecto']['aciertos']} de {base['defecto']['total']} | pendiente |")
    else:
        vistas = vistas_comparables(base, elegido, conjunto_oro)
        lineas += [
            "### Comparación comparable",
            "",
            # El ejemplo de la comparación tramposa se arma con los números CRUDOS
            # de esta corrida, no con unos escritos a mano: así sigue siendo cierto
            # la próxima vez que cambien.
            (f"Las dos columnas se miden aquí sobre los MISMOS casos, siempre. La tabla cruda de arriba dice "
             f"«{base['por_clase']['defecto_real']['aciertos']} de {base['por_clase']['defecto_real']['total']}» "
             f"para la línea base y «{elegido['por_clase']['defecto_real']['aciertos']} de "
             f"{elegido['por_clase']['defecto_real']['total']}» para el modelo en `defecto_real`, y poner esos "
             "dos números uno al lado del otro sería engañoso: no son los mismos casos. Los que el modelo no "
             f"clasificó ({len(elegido['sin_prediccion'])}) salieron de SU denominador, así que lo haría ver "
             "mejor justo por lo que no entregó. Por eso se informan las dos lecturas honestas, que responden "
             "preguntas distintas y hay que leer juntas."),
            "",
            (f"**(a) Sobre el mismo subconjunto · {vistas['mismo_subconjunto']['casos']} casos que las dos columnas "
            "clasificaron.** Responde «cuando los dos contestan, ¿quién acierta más?». Aísla la calidad de la "
            "clasificación de la disponibilidad del backend."),
            "",
            f"| Clase | Casos | `lineabase` | {titulo_modelo} |",
            "|---|---:|---:|---:|",
        ]
        for clase in clases:
            cuenta = vistas["mismo_subconjunto"]["por_clase"][clase]
            lineas.append(f"| `{clase}` | {cuenta['total']} | {cuenta['base']} de {cuenta['total']} | "
                          f"{cuenta['modelo']} de {cuenta['total']} |")
        cuenta = vistas["mismo_subconjunto"]["defecto"]
        lineas += [
            (f"| `DEF-xx` acertados | {cuenta['total']} | {cuenta['base']} de {cuenta['total']} | "
            f"{cuenta['modelo']} de {cuenta['total']} |"),
            "",
            (f"**(b) Sobre el conjunto completo · {vistas['conjunto_completo']['casos']} casos, y un caso sin "
            "respuesta cuenta como fallo.** Responde «¿qué componente sirve más para el trabajo?». Para quien "
            "recibe el reporte, un fallo sin diagnosticar no es «no sé»: es trabajo que no se hizo, sin importar "
            "si la culpa fue del modelo o del límite del plan."),
            "",
            f"| Clase | Casos | `lineabase` | {titulo_modelo} |",
            "|---|---:|---:|---:|",
        ]
        for clase in clases:
            cuenta = vistas["conjunto_completo"]["por_clase"][clase]
            lineas.append(f"| `{clase}` | {cuenta['total']} | {cuenta['base']} de {cuenta['total']} | "
                          f"{cuenta['modelo']} de {cuenta['total']} |")
        cuenta = vistas["conjunto_completo"]["defecto"]
        lineas += [
            (f"| `DEF-xx` acertados | {cuenta['total']} | {cuenta['base']} de {cuenta['total']} | "
            f"{cuenta['modelo']} de {cuenta['total']} |"),
            "",
            ("De los casos que el modelo no clasificó, los que se perdieron por un error del backend "
             f"(**{len(por_tipo_de_causa['backend'])}**) no dicen nada sobre su clasificación: en la lectura (b) "
             "le cuentan en contra de todas formas, porque el componente tampoco entregó un diagnóstico. Lo que "
             "la lectura (a) muestra es cuánto de la diferencia es clasificación y cuánto es disponibilidad."),
        ]
        del_modelo = {fila["oro"]: fila["clase_propuesta"] for fila in elegido["detalle"]}
        acuerdo = sum(1 for fila in base["detalle"] if del_modelo.get(fila["oro"]) == fila["clase_propuesta"])
        lineas += ["", (f"Acuerdo entre la línea base y el modelo: **{acuerdo} de {len(base['detalle'])}** "
                        f"casos clasificados igual.")]
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
    # El JSON lleva además las causas de cada hueco y las dos vistas comparables,
    # para que el número del documento no haya que recalcularlo a mano.
    volcado = dict(evaluaciones)
    volcado["causas_sin_prediccion"] = causas
    if hay_modelo:
        volcado["comparacion"] = vistas_comparables(base, elegido, conjunto_oro)
    (carpeta / f"evals-{elegido['backend']}.json").write_text(
        json.dumps(volcado, ensure_ascii=False, indent=2), encoding="utf-8")
    return ruta


# ---------------------------------------------------------------------------
# Las pruebas
# ---------------------------------------------------------------------------

def test_cp_ia_01_evals_contra_el_conjunto_de_oro(evaluaciones, carpeta_resultados, defectos, backend,
                                                  conjunto_oro, comando_de_la_corrida_real):
    """CP-IA-01 · Evals: exactitud por clase y matriz de confusión, en un archivo.

    Concepto de la clase 15: **evals**. El componente se mide contra casos
    etiquetados de antemano, con la entrada que de verdad va a ver (la del
    conjunto de oro, ya sin las fugas del artefacto).

    Lo que se exige, y lo que a propósito NO se exige:

      1. Que se haya podido medir algo. Cero casos medidos no es un resultado
         malo, es que no hay resultado.
      2. Que el conjunto de oro siga teniendo los casos que dice tener.
      3. Que la matriz de confusión cuadre con los casos medidos.
      4. Que ningún `DEF-xx` aceptado se haya inventado (lo impide la guarda 2).
      5. Que TODOS los casos del conjunto estén contados: los que recibieron
         clasificación más los que no, cada uno con su causa de las tres
         posibles. Que se pierda un caso de la cuenta sí es un defecto.
      6. Con `lineabase`, que estén los 52 y que no baje del piso ya medido: es
         código determinista, ahí un hueco o una bajada es un defecto.

      NO se exige una exactitud mínima al modelo. Ese umbral sería inventado y
      convertiría la prueba en un sello: la prueba mide y escribe el número, y
      si el modelo acierta menos que las reglas eso se lee en el archivo de
      resultados y se explica, no se esconde haciendo fallar la prueba.

      Tampoco se exige que el modelo clasifique los 52. Que deje casos fuera es
      un resultado de la medición, no un defecto del arnés: se cuenta, se
      explica por causa y pesa en la comparación del conjunto completo de
      CP-IA-02, donde un caso sin respuesta cuenta como fallo.
    """
    elegido = evaluaciones["elegido"]
    ruta = escribir_resultados(carpeta_resultados, evaluaciones, conjunto_oro, comando_de_la_corrida_real)

    assert elegido["casos_medidos"] > 0, "no se clasificó ningún caso: no hay medición que leer"
    assert elegido["casos_del_conjunto"] == len(conjunto_oro["casos"]) == conjunto_oro["conteo"]["casos"], (
        "el conjunto de oro no tiene los casos que declara su propio conteo")
    total_matriz = sum(sum(fila.values()) for fila in elegido["matriz"].values())
    assert total_matriz == elegido["casos_medidos"], (
        f"la matriz suma {total_matriz} y se midieron {elegido['casos_medidos']} casos")
    assert elegido["defecto"]["inventados"] == 0, "pasó un DEF-xx que no existe en docs/defectos.md"
    for propuesta in elegido["detalle"]:
        assert propuesta["defecto_propuesto"] is None or propuesta["defecto_propuesto"] in defectos

    # Ningún caso se pierde de la cuenta: cada uno está medido o está en la
    # lista de huecos con una de las tres causas. Lo que haría fallar esto es que
    # el arnés perdiera un caso por el camino, no que el modelo deje huecos.
    causas = causa_de_cada_hueco(elegido, conjunto_oro)
    assert sorted(causas) == sorted(elegido["sin_prediccion"]), "se perdió un caso al explicar los huecos"
    assert all(causa["tipo"] in TIPOS_DE_CAUSA for causa in causas.values())
    assert elegido["casos_medidos"] + len(causas) == elegido["casos_del_conjunto"], (
        f"{elegido['casos_medidos']} medidos + {len(causas)} sin clasificar no son los "
        f"{elegido['casos_del_conjunto']} casos del conjunto")

    if backend == "lineabase":
        # La línea base es código determinista: un rechazo de guarda, un error de
        # backend o un hueco aquí serían un error del componente o del arnés, no
        # un dato sobre el modelo.
        assert elegido["rechazos_de_guardas"] == []
        assert elegido["errores_del_backend"] == []
        assert elegido["sin_prediccion"] == [], (
            f"la línea base dejó casos sin clasificar: {elegido['sin_prediccion']}")
        assert elegido["casos_medidos"] == elegido["casos_del_conjunto"]
        for clase, piso in PISO_LINEABASE.items():
            aciertos = elegido["por_clase"][clase]["aciertos"]
            assert aciertos >= piso, f"{clase}: {aciertos} aciertos, el piso medido es {piso}"

    assert ruta.is_file()
    texto = ruta.read_text(encoding="utf-8")
    assert "Matriz de confusión" in texto
    assert "Exactitud por clase" in texto
    assert "Casos sin clasificación y su causa" in texto


def test_cp_ia_02_linea_base_frente_a_la_ia(evaluaciones, carpeta_resultados, conjunto_oro,
                                            comando_de_la_corrida_real):
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
      4. Cuando hay modelo, que la comparación esté hecha sobre los MISMOS casos
         en las dos columnas, en las dos lecturas (mismo subconjunto y conjunto
         completo). Esto es lo que la prueba de verdad protege: un denominador
         distinto en cada columna no es una comparación, es un número bonito.
      5. Cuando no hay modelo, que su columna quede escrita como pendiente, con
         el comando que la produce.
    """
    base = evaluaciones["lineabase"]
    ruta = carpeta_resultados / f"evals-{evaluaciones['elegido']['backend']}.md"
    if not ruta.is_file():
        escribir_resultados(carpeta_resultados, evaluaciones, conjunto_oro, comando_de_la_corrida_real)
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
        vistas = vistas_comparables(base, evaluaciones["elegido"], conjunto_oro)
        # Mismos casos en las dos columnas: por construcción `contar` usa una
        # sola lista de IDs para las dos, y lo que se verifica aquí es que esa
        # lista sea la que corresponde y que nadie haya quedado fuera del
        # denominador por no haber contestado.
        completo = vistas["conjunto_completo"]
        assert completo["casos"] == len(conjunto_oro["casos"])
        for clase, esperado in conjunto_oro["conteo"]["por_clase"].items():
            assert completo["por_clase"][clase]["total"] == esperado, (
                f"{clase}: la vista del conjunto completo mide {completo['por_clase'][clase]['total']} casos y "
                f"el conjunto de oro declara {esperado}")
        subconjunto = vistas["mismo_subconjunto"]
        assert subconjunto["casos"] == len(vistas["ids_del_subconjunto"])
        assert subconjunto["casos"] == evaluaciones["elegido"]["casos_medidos"], (
            "el subconjunto comparable no son exactamente los casos que el modelo clasificó")
        assert sum(c["total"] for c in subconjunto["por_clase"].values()) == subconjunto["casos"]
        assert "Comparación comparable" in texto
        assert "Sobre el mismo subconjunto" in texto
        assert "Sobre el conjunto completo" in texto
        assert "Acuerdo entre la línea base y el modelo" in texto
    else:
        assert "pendiente de corrida real" in texto
        assert "DIAGNOSTICO_IA_BACKEND=anthropic" in texto
