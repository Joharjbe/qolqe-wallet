# Evals de la capacidad de IA · backend `google`

Medición del componente `herramientas/diagnostico_ia/` contra el conjunto de oro
`tests/diagnostico/conjunto_oro/conjunto_oro.json`. Lo escribe `tests/diagnostico/test_evals.py`
(CP-IA-01 y CP-IA-02) cada vez que corre el arnés.

- Casos del conjunto: **52**
- Casos con una clasificación aceptada por las guardas: **48**
- Casos sin clasificación: ORO-04, ORO-09, ORO-11, ORO-18
- Grupos que arma la firma determinista con las 52 entradas en un solo pase: **20**
- Respuestas rechazadas por las guardas: **4**
- Errores del backend (sin clave, sin red, límite del plan): **0**

## Exactitud por clase

Esta tabla es la medida CRUDA de cada columna sobre los casos que ELLA clasificó, así que su denominador cambia con lo que se le cayó. **No se usa para comparar las dos columnas**: para eso está «Comparación comparable» más abajo.

| Clase (lo que dice el conjunto de oro) | Aciertos | Casos | Se lee |
|---|---:|---:|---|
| `defecto_real` | 28 | 36 | 28 de 36 |
| `prueba_inestable` | 4 | 4 | 4 de 4 |
| `error_entorno` | 8 | 8 | 8 de 8 |

Sin promedio global: el conjunto está desbalanceado y un solo porcentaje lo decidiría `defecto_real`.

## Matriz de confusión

Filas: la clase del conjunto de oro. Columnas: la que propuso el componente.

| oro ↓ / propuesto → | `defecto_real` | `prueba_inestable` | `error_entorno` |
|---|---:|---:|---:|
| `defecto_real` | 28 | 8 | 0 |
| `prueba_inestable` | 0 | 4 | 0 |
| `error_entorno` | 0 | 0 | 8 |

## Casos sin clasificación y su causa

Un caso sin clasificar no se tapa ni se saca del conjunto: se cuenta con su causa. La distinción es la que decide qué se puede afirmar. Un rechazo de guarda y una respuesta incompleta SON datos sobre el modelo (contestó algo que no se podía sostener, o dejó casos fuera de su respuesta). Un error del backend NO lo es: es infraestructura, y de ese caso simplemente no hay medición.

- Rechazados por una guarda (dato del modelo): **4** (ORO-04, ORO-09, ORO-11, ORO-18)
- Perdidos por un error del backend (infraestructura): **0** (ninguno)
- El modelo contestó por el grupo y dejó el caso fuera (dato del modelo): **0** (ninguno) · el componente no lleva hoy esta cuenta: se deduce cruzando los grupos con las predicciones, y debería registrarla `clasificar_fallos`

| Oro | Caso | Grupo | Tipo de causa | Motivo |
|---|---|---|---|---|
| ORO-04 | CP-A32 | G2 | guarda | clase inválida: None |
| ORO-09 | CP-NA04 | G3 | guarda | posible dato personal (celular o documento) en el texto: 987000135… |
| ORO-11 | CP-NA15 | G3 | guarda | posible dato personal (celular o documento) en el texto: 987000330… |
| ORO-18 | CP-NA60 | G5 | guarda | clase inválida: None |

## DEF-xx propuesto

- Casos de oro que tienen un `DEF-xx` correcto esperado: **38**
- Acertados: **0**
- `DEF-xx` propuestos en total: **0**
- `DEF-xx` que no existen en `docs/defectos.md` y pasaron las guardas: **0** (tiene que ser 0: lo impide la guarda 2)

## Confianza declarada

| Confianza | Casos |
|---|---:|
| alta | 35 |
| media | 13 |
| baja | 0 |

## CP-IA-02 · Qué aporta la IA frente a la línea base

### Comparación comparable

Las dos columnas se miden aquí sobre los MISMOS casos, siempre. La tabla cruda de arriba dice «38 de 40» para la línea base y «28 de 36» para el modelo en `defecto_real`, y poner esos dos números uno al lado del otro sería engañoso: no son los mismos casos. Los que el modelo no clasificó (4) salieron de SU denominador, así que lo haría ver mejor justo por lo que no entregó. Por eso se informan las dos lecturas honestas, que responden preguntas distintas y hay que leer juntas.

**(a) Sobre el mismo subconjunto · 48 casos que las dos columnas clasificaron.** Responde «cuando los dos contestan, ¿quién acierta más?». Aísla la calidad de la clasificación de la disponibilidad del backend.

| Clase | Casos | `lineabase` | `google` |
|---|---:|---:|---:|
| `defecto_real` | 36 | 34 de 36 | 28 de 36 |
| `prueba_inestable` | 4 | 4 de 4 | 4 de 4 |
| `error_entorno` | 8 | 7 de 8 | 8 de 8 |
| `DEF-xx` acertados | 38 | 0 de 38 | 0 de 38 |

**(b) Sobre el conjunto completo · 52 casos, y un caso sin respuesta cuenta como fallo.** Responde «¿qué componente sirve más para el trabajo?». Para quien recibe el reporte, un fallo sin diagnosticar no es «no sé»: es trabajo que no se hizo, sin importar si la culpa fue del modelo o del límite del plan.

| Clase | Casos | `lineabase` | `google` |
|---|---:|---:|---:|
| `defecto_real` | 40 | 38 de 40 | 28 de 40 |
| `prueba_inestable` | 4 | 4 de 4 | 4 de 4 |
| `error_entorno` | 8 | 7 de 8 | 8 de 8 |
| `DEF-xx` acertados | 42 | 0 de 42 | 0 de 42 |

De los casos que el modelo no clasificó, los que se perdieron por un error del backend (**0**) no dicen nada sobre su clasificación: en la lectura (b) le cuentan en contra de todas formas, porque el componente tampoco entregó un diagnóstico. Lo que la lectura (a) muestra es cuánto de la diferencia es clasificación y cuánto es disponibilidad.

Acuerdo entre la línea base y el modelo: **39 de 52** casos clasificados igual.

## Casos en los que la clase propuesta no coincide

Es la lista que se mira para decidir si el componente sirve. Un error aquí no es un error del conjunto de oro: es el resultado de la medición.

| Oro | Caso | Clase de oro | Clase propuesta | Confianza | Razón |
|---|---|---|---|---|---|
| ORO-10 | CP-NA12 | `defecto_real` | `prueba_inestable` | media | El fallo en registros simultáneos sugiere una posible condición de carrera o problemas de sincronización en el test. |
| ORO-12 | CP-NA20 | `defecto_real` | `prueba_inestable` | media | El fallo en registros simultáneos con el mismo correo es característico de pruebas de concurrencia inestables. |
| ORO-25 | CP-NA127 | `defecto_real` | `prueba_inestable` | media | Las pruebas de concurrencia suelen fallar debido a condiciones de carrera en el entorno de pruebas, no necesariamente por un fallo del código. |
| ORO-28 | CP-NA134 | `defecto_real` | `prueba_inestable` | media | La gestión de saldos bajo condiciones de carga simultánea es propensa a fallos de concurrencia en la ejecución de pruebas. |
| ORO-29 | CP-NA135 | `defecto_real` | `prueba_inestable` | media | La validación de límites diarios bajo concurrencia extrema es inestable en el entorno de pruebas. |
| ORO-36 | CP-T17 | `defecto_real` | `prueba_inestable` | media | La prueba de concurrencia falló en una única ejecución, sugiriendo problemas de sincronización. |
| ORO-37 | CP-T18 | `defecto_real` | `prueba_inestable` | media | Fallo en escenario de concurrencia que requiere condiciones exactas para validar el saldo. |
| ORO-38 | CP-T20 | `defecto_real` | `prueba_inestable` | media | Las pruebas de ráfagas simultáneas suelen ser inestables si la infraestructura no garantiza el orden de ejecución. |
