# Evals de la capacidad de IA · backend `lineabase`

Medición del componente `herramientas/diagnostico_ia/` contra el conjunto de oro
`tests/diagnostico/conjunto_oro/conjunto_oro.json`. Lo escribe `tests/diagnostico/test_evals.py`
(CP-IA-01 y CP-IA-02) cada vez que corre el arnés.

- Casos del conjunto: **52**
- Casos con una clasificación aceptada por las guardas: **52**
- Casos sin clasificación: ninguno
- Grupos que arma la firma determinista con las 52 entradas en un solo pase: **20**
- Respuestas rechazadas por las guardas: **0**
- Errores del backend (sin clave, sin red, límite del plan): **0**

## Exactitud por clase

Esta tabla es la medida CRUDA de cada columna sobre los casos que ELLA clasificó, así que su denominador cambia con lo que se le cayó. **No se usa para comparar las dos columnas**: para eso está «Comparación comparable» más abajo.

| Clase (lo que dice el conjunto de oro) | Aciertos | Casos | Se lee |
|---|---:|---:|---|
| `defecto_real` | 38 | 40 | 38 de 40 |
| `prueba_inestable` | 4 | 4 | 4 de 4 |
| `error_entorno` | 7 | 8 | 7 de 8 |

Sin promedio global: el conjunto está desbalanceado y un solo porcentaje lo decidiría `defecto_real`.

## Matriz de confusión

Filas: la clase del conjunto de oro. Columnas: la que propuso el componente.

| oro ↓ / propuesto → | `defecto_real` | `prueba_inestable` | `error_entorno` |
|---|---:|---:|---:|
| `defecto_real` | 38 | 1 | 1 |
| `prueba_inestable` | 0 | 4 | 0 |
| `error_entorno` | 1 | 0 | 7 |

## Casos sin clasificación y su causa

Un caso sin clasificar no se tapa ni se saca del conjunto: se cuenta con su causa. La distinción es la que decide qué se puede afirmar. Un rechazo de guarda y una respuesta incompleta SON datos sobre el modelo (contestó algo que no se podía sostener, o dejó casos fuera de su respuesta). Un error del backend NO lo es: es infraestructura, y de ese caso simplemente no hay medición.

- Rechazados por una guarda (dato del modelo): **0** (ninguno)
- Perdidos por un error del backend (infraestructura): **0** (ninguno)
- El modelo contestó por el grupo y dejó el caso fuera (dato del modelo): **0** (ninguno) · lo registra el propio componente como un rechazo de tipo `sin_respuesta`, no se deduce por descarte

| Oro | Caso | Grupo | Tipo de causa | Motivo |
|---|---|---|---|---|
| — | — | — | — | todos los casos recibieron clasificación |

## DEF-xx propuesto

- Casos de oro que tienen un `DEF-xx` correcto esperado: **42**
- Acertados: **0**
- `DEF-xx` propuestos en total: **0**
- `DEF-xx` que no existen en `docs/defectos.md` y pasaron las guardas: **0** (tiene que ser 0: lo impide la guarda 2)

## Confianza declarada

| Confianza | Casos |
|---|---:|
| alta | 2 |
| media | 11 |
| baja | 39 |

## CP-IA-02 · Qué aporta la IA frente a la línea base

Esta corrida se hizo con `lineabase` (reglas, sin IA, sin red), así que la columna del modelo queda **pendiente de corrida real**: el arnés no inventa un número que no midió. Se produce con:

```bash
cp ejemplo.env .env  # y poner ANTHROPIC_API_KEY
DIAGNOSTICO_IA_BACKEND=anthropic .venv/bin/python -m pytest tests/diagnostico -v
```

| Medida | `lineabase` (reglas, sin IA) | modelo (pendiente) |
|---|---:|---:|
| `defecto_real` | 38 de 40 | pendiente |
| `prueba_inestable` | 4 de 4 | pendiente |
| `error_entorno` | 7 de 8 | pendiente |
| `DEF-xx` acertados | 0 de 42 | pendiente |

## Casos en los que la clase propuesta no coincide

Es la lista que se mira para decidir si el componente sirve. Un error aquí no es un error del conjunto de oro: es el resultado de la medición.

| Oro | Caso | Clase de oro | Clase propuesta | Confianza | Razón |
|---|---|---|---|---|---|
| ORO-34 | CP-NW03 | `defecto_real` | `error_entorno` | media | El tipo de error del grupo es tiempo_de_espera: apunta al entorno, no a la app. |
| ORO-38 | CP-T20 | `defecto_real` | `prueba_inestable` | media | La documentación del proyecto declara este caso inestable: no da el mismo resultado en todas las corridas. |
| ORO-51 | CP-W12 | `error_entorno` | `defecto_real` | baja | Ninguna regla aplicó; la línea base supone defecto real porque es la clase más frecuente. |
