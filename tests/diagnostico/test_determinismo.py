"""CP-IA-06: no determinismo. La misma entrada, varias veces.

Concepto de la clase 15: **no determinismo**. Una prueba que compara con la
salida de un modelo puede pasar y fallar con la misma entrada, porque el modelo
no contesta siempre lo mismo. Eso rompe lo que una suite de pruebas promete: que
el resultado de hoy se pueda comparar con el de ayer.

Cómo lo encara el componente, y qué se mide aquí:

1. **Todo lo que decide el reporte está en código determinista**: qué cuenta
   como fallo, la firma del fallo, los grupos, el orden y las guardas. Con el
   backend `lineabase` el diagnóstico completo es byte a byte el mismo en cada
   corrida, y eso se mide: la varianza tiene que ser CERO. Esa es la gracia de
   tener un control.
2. **Lo que el modelo aporta es texto y clase, encima de esa base.** Su varianza
   no se puede suponer: se mide con el modelo puesto, y hoy esa prueba queda
   omitida con su motivo.
3. **El reporte se puede repetir sin volver a pagar**: el backend `grabado`
   devuelve las respuestas de una corrida real y, si no hay ninguna grabada,
   falla con un mensaje claro en vez de improvisar.
"""

from __future__ import annotations

import json

from herramientas.diagnostico_ia import diagnostico, modelo


def _sin_la_fecha(resultado: dict) -> str:
    """El diagnóstico en JSON, sin la marca de tiempo, que cambia a propósito."""
    copia = json.loads(json.dumps(resultado, ensure_ascii=False))
    copia["run"]["fecha_del_diagnostico"] = "«fecha»"
    return json.dumps(copia, ensure_ascii=False, sort_keys=True)


def _casos_de_prueba(caso_base) -> list[dict]:
    """Cuatro fallos distintos: un fallo esperado, dos aserciones y uno sin ejecutar."""
    return [
        caso_base(),
        caso_base(name="CP-A79 El alias admite espacios", defecto="DEF-02",
                  archivo="features/contactos_api.feature:60"),
        caso_base(name="CP-T20 Cinco altas simultáneas del mismo celular", defecto="DEF-26", estado="failed",
                  archivo="features/g4_tecnico_api.feature:419",
                  fallo="AssertionError: se crearon 5 contactos, se esperaba 1"),
        caso_base(name="CP-NA03 Longitud de nombres en el registro", defecto=None, estado="sin ejecutar",
                  ejecuciones="0/0", archivo="features/nucleo_registro_api.feature:31"),
    ]


def test_cp_ia_06_la_linea_base_no_varia_ni_un_byte(run_sintetico, caso_base, raiz_repo, repeticiones,
                                                    carpeta_resultados):
    """CP-IA-06 · La misma entrada N veces con `lineabase`: varianza cero.

    Se repite el diagnóstico completo (leer, agrupar, clasificar, resumir) sobre
    la misma carpeta y se comparan los JSON sin la fecha. Tienen que ser
    idénticos, incluidas las firmas y los IDs de grupo: si los grupos cambiaran
    de nombre entre corridas, dos reportes del mismo run no se podrían comparar.
    """
    carpeta = run_sintetico(_casos_de_prueba(caso_base))
    corridas = [diagnostico.diagnosticar(carpeta, backend="lineabase", raiz_repo=raiz_repo)
                for _ in range(repeticiones)]

    textos = {_sin_la_fecha(resultado) for resultado in corridas}
    assert len(textos) == 1, f"{len(textos)} resultados distintos en {repeticiones} corridas con lineabase"

    # Varianza por caso: cuántos casos cambiaron de clase entre corridas.
    clases_por_caso: dict[str, set[str]] = {}
    for resultado in corridas:
        for propuesta in resultado["fallos"]:
            clases_por_caso.setdefault(propuesta["caso"], set()).add(propuesta["clase"])
    cambiaron = [caso for caso, clases in clases_por_caso.items() if len(clases) > 1]
    assert cambiaron == []

    medida = {
        "backend": "lineabase",
        "corridas": repeticiones,
        "casos": len(clases_por_caso),
        "casos_que_cambiaron_de_clase": len(cambiaron),
        "diagnosticos_distintos": len(textos),
    }
    (carpeta_resultados / "no-determinismo-lineabase.json").write_text(
        json.dumps(medida, ensure_ascii=False, indent=2), encoding="utf-8")


def test_cp_ia_06_los_grupos_no_dependen_del_orden_del_diccionario(run_sintetico, caso_base, raiz_repo):
    """CP-IA-06 · Los IDs de grupo salen del orden del artefacto, no del azar.

    `agrupar` numera G1..Gn según en qué orden aparece el primer fallo de cada
    grupo. Es lo que permite decir «el G3 del run de ayer» y que signifique algo.
    """
    carpeta = run_sintetico(_casos_de_prueba(caso_base))
    primera = diagnostico.diagnosticar(carpeta, backend="lineabase", raiz_repo=raiz_repo)
    segunda = diagnostico.diagnosticar(carpeta, backend="lineabase", raiz_repo=raiz_repo)

    def identidad(resultado):
        return [(grupo["id"], grupo["firma"], tuple(grupo["casos"])) for grupo in resultado["grupos"]]

    assert identidad(primera) == identidad(segunda)
    assert [grupo["id"] for grupo in primera["grupos"]] == [f"G{n}" for n in range(1, len(primera["grupos"]) + 1)]


def test_cp_ia_06_sin_respuestas_grabadas_el_backend_falla_en_vez_de_improvisar(run_sintetico, caso_base, raiz_repo,
                                                                               tmp_path):
    """CP-IA-06 · La reproducibilidad no se finge.

    `--modelo grabado` sirve para repetir un reporte sin volver a llamar al
    modelo. Con la carpeta vacía NO devuelve algo parecido: cuenta un error de
    backend por grupo, deja el reporte sin clasificaciones y dice cómo llenarla.
    Un reporte vacío y honesto es mejor que uno completo e inventado.
    """
    carpeta = run_sintetico(_casos_de_prueba(caso_base))
    vacia = tmp_path / "sin-grabados"
    vacia.mkdir()

    resultado = diagnostico.diagnosticar(carpeta, backend="grabado", raiz_repo=raiz_repo, carpeta_grabados=vacia)

    assert resultado["totales"]["clasificados"] == 0
    assert resultado["totales"]["rechazados_por_guardas"] == 0  # no es un rechazo: es que no hubo respuesta

    # Un error de backend por grupo, más el del resumen del run: el resumen también
    # le pregunta al modelo. El total se calcula después de pedirlo, así que la tabla
    # de medidas y la de rechazos dan el mismo número; si no cuadraran, el reporte
    # estaría diciendo que midió menos fallos de los que enseña.
    por_grupo = len(resultado["grupos"])
    assert resultado["totales"]["errores_del_backend"] == por_grupo + 1
    assert resultado["totales"]["errores_del_backend"] == len(resultado["rechazos"])
    assert [rechazo["grupo"] for rechazo in resultado["rechazos"]][-1] == "resumen"
    assert len(resultado["rechazos"]) == por_grupo + 1

    motivos = " ".join(motivo for rechazo in resultado["rechazos"] for motivo in rechazo["motivos"])
    assert "No hay respuesta grabada" in motivos
    assert "No se inventa el contenido" in motivos
    assert resultado["resumen"] == {"resumen": "", "riesgo": ""}


def test_cp_ia_06_un_backend_que_no_existe_se_rechaza_de_entrada():
    """CP-IA-06 · Solo los cuatro backends declarados. Nada de adivinar."""
    assert modelo.BACKENDS == ("anthropic", "google", "grabado", "lineabase")
    try:
        modelo.responder("sistema", "prompt", {}, backend="el-que-sea")
    except ValueError as error:
        assert "Backend desconocido" in str(error)
    else:
        raise AssertionError("aceptó un backend que no existe")


def test_cp_ia_06_no_determinismo_de_un_modelo_real(exige_modelo, exigir_que_el_backend_contestara, run_sintetico,
                                                    caso_base, raiz_repo, repeticiones, carpeta_resultados):
    """CP-IA-06 · La varianza del modelo. OMITIDA sin clave de API.

    Lo que mide: el mismo run N veces con el modelo puesto, y cuántos casos
    cambian de clase entre corridas. El número que salga es el que hay que decir
    en la exposición, y no se puede escribir antes de medirlo. Lo que sí se
    exige, pase lo que pase: la parte determinista (grupos y firmas) no cambia,
    porque no la decide el modelo.
    """
    carpeta = run_sintetico(_casos_de_prueba(caso_base))
    corridas = [diagnostico.diagnosticar(carpeta, backend=exige_modelo, raiz_repo=raiz_repo)
                for _ in range(repeticiones)]
    exigir_que_el_backend_contestara(*corridas)

    firmas = {tuple((grupo["id"], grupo["firma"]) for grupo in resultado["grupos"]) for resultado in corridas}
    assert len(firmas) == 1, "los grupos cambiaron entre corridas: eso no lo decide el modelo"

    clases_por_caso: dict[str, set[str]] = {}
    for resultado in corridas:
        for propuesta in resultado["fallos"]:
            clases_por_caso.setdefault(propuesta["caso"], set()).add(propuesta["clase"])
    cambiaron = {caso: sorted(clases) for caso, clases in clases_por_caso.items() if len(clases) > 1}

    (carpeta_resultados / f"no-determinismo-{exige_modelo}.json").write_text(json.dumps({
        "backend": exige_modelo,
        "corridas": repeticiones,
        "casos": len(clases_por_caso),
        "casos_que_cambiaron_de_clase": len(cambiaron),
        "detalle": cambiaron,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    assert len(clases_por_caso) == len({caso["name"].split()[0] for caso in _casos_de_prueba(caso_base)})
