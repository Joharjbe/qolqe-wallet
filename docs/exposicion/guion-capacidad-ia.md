# Capacidad de IA en 4 minutos

Son las láminas 18 a 21 (`ia-que`, `ia-validacion`, `ia-resultado`, `ia-inyeccion`), con una demo sin red entre la 19 y la 20. En la exposición de 15 minutos esas láminas van de 8:05 a 9:30 y sin demo ([`guion.md`](guion.md)); si D1 termina con ventaja, la línea de totales entra antes de D2 (`guion.md`, «Si vas adelantado»). Esta es la versión larga: para cuando la profesora pida el punto 8 en detalle, por ejemplo en las preguntas. La demo no usa Qolqe ni Kiwi, así que funciona también después de k6, con los dos apagados.

Cada cifra lleva al lado su archivo y su línea. La fuente de verdad es [`capacidad-ia.md`](../capacidad-ia.md) y [`resultados-capacidad-ia/`](../resultados-capacidad-ia/README.md).

Por qué hace falta este guion: en el laboratorio S11 ya mostré una IA que revisa resultados. Si no digo en los primeros 45 segundos qué cambió, la profesora ve lo mismo otra vez.

## Qué es distinto del laboratorio S11

En S11 le pasé a Codex el `output.xml` de una sola prueba de Robot y los criterios de HU-G4-06 y HU-G4-08, y le pedí qué validación faltaba. La respuesta esperada era el SMS que el caso no comprueba, y yo la revisaba contra los requisitos ([`labs/s11-robot/demo-robot-ia.md`](../../labs/s11-robot/demo-robot-ia.md), líneas 27 y 29).

| | Laboratorio S11 | Capacidad de la entrega final |
|---|---|---|
| Qué lee la IA | Una prueba de Robot y su `output.xml` | Los 40 fallos de un run entero: `junit-cp.xml`, 335 casos (`run.json:15-17` del respaldo) |
| Cómo se le pide | Un prompt pegado a mano en el chat de Codex | Un comando del repo, `python -m herramientas.diagnostico_ia`, con una llamada por grupo de fallos |
| Qué devuelve | Texto libre | Un JSON de 7 campos. `guarda_esquema` rechaza un campo de más o una clase fuera de la lista (`capacidad-ia.md:269-279`) |
| Quién revisa la respuesta | Yo, a ojo | Cuatro guardas en código antes del reporte: el esquema, el `DEF-xx` contra los de `defectos.md` (29 en la corrida del 17-nov; DEF-30 se agregó después), la evidencia contra el material del caso y los datos personales (`capacidad-ia.md:277-282`; los 29, `:778`) |
| Cómo sé si acierta | No lo sé: es una respuesta, sin medida | Un eval de la clase 15: el conjunto de oro de 52 casos, la tabla del eval por clase (lo esperado contra lo propuesto) y un control sin IA, unas reglas, sobre los mismos casos (`capacidad-ia.md:325-334`, `evals-google.md:30-34`, `:74-79`) |
| ¿Se repite? | No se midió: era una conversación suelta | Los grupos los arma una firma de código; `--modelo grabado` repite el reporte sin red; la varianza del modelo se midió en 5 corridas (`no-determinismo-google.json:3`) |
| Riesgos | Una advertencia escrita: un texto de IA no es una prueba ejecutada | Medidos: la inyección mueve la clase (LIM-IA-01, `capacidad-ia.md:647-654`) y el modelo copió un celular en 2 respuestas que la guarda paró (`evals-google.md:47-48`) |

Lo que no cambió es la regla: la IA propone y el tester decide. En S11 era una advertencia. Ahora está medida.

## Antes de clase

1. Tiene que existir `~/Desktop/respaldo-sitio-con-imagenes`. Es el sitio del run #18 (id 43109117336, `workflow_dispatch`, commit `5fbe969`), y esta demo lo usa porque las respuestas grabadas se buscan por la petición exacta, que sale de ese run. El plan B de la reportería es otro: `~/Desktop/respaldo-sitio-entrega-final` (run #28). Su `run.json` dice 335 casos, 295 `passed`, 40 `xfailed`, 0 `failed` y conclusión `success` (`run.json:10-19`).
2. Ensayo en casa: corre una vez el comando de la demo con `--salida ~/Desktop/diagnostico-ensayo`, para que la corrida en vivo no lo pise. La primera línea tiene que ser la de abajo. Si no lo es, no lo muestres en vivo: usa `evals-google.md`. Ese reporte es el respaldo.
3. Los archivos se abren en el momento de usarlos, no antes de clase. En las preguntas ya pasó k6, y la línea «Antes de k6» de [`hoja-demo.md`](hoja-demo.md) cierra el editor. Desde la terminal de la demo, que está en la raíz del repositorio:

   ```bash
   code docs/resultados-capacidad-ia/evals-google.md
   code -g docs/resultados-capacidad-ia/inyeccion-google.json:144
   ```

   `evals-google.md` se ve en vista previa con `Cmd + Shift + V`.

No hace falta red, ni clave, ni Qolqe levantado. `--modelo grabado` no llama a ningún modelo: lee las respuestas que `gemini-3.1-flash-lite` dio el 17-nov, guardadas en `herramientas/diagnostico_ia/respuestas_grabadas/` (31 respuestas, `capacidad-ia.md:216`). Si falta una, la cuenta como error del backend y no inventa nada ([`modelo.py:297-307`](../../herramientas/diagnostico_ia/modelo.py)).

## El comando de la demo

Desde la raíz del repositorio:

```bash
.venv/bin/python -m herramientas.diagnostico_ia --run ~/Desktop/respaldo-sitio-con-imagenes --modelo grabado --salida ~/Desktop/diagnostico-expo
code ~/Desktop/diagnostico-expo/diagnostico.md
```

Salida real, corrida el 17-nov-2026 sobre ese respaldo, con código de salida 0. Esta es la primera línea; debajo imprime las rutas de `diagnostico.json` y `diagnostico.md`:

```text
40 fallos (40 casos) · 32 grupos · 36 clasificados · 1 rechazados por las guardas · 2 errores del backend
```

Qué hay en `diagnostico.md` y se muestra:

| Dónde | Qué dice | Por qué importa |
|---|---|---|
| Arriba de todo | «La IA propone, el tester decide. Este reporte no cambia el veredicto del quality gate.» | Lo escribe el código, no el modelo (`diagnostico.py:145`) |
| «Rechazos de las guardas», fila G7 | CP-T17: «la evidencia no aparece en el material del caso». El modelo citó «Mensaje normalizado: defecto conocido def-25 (fallo esperado)», que es una línea del encabezado del grupo en el prompt (`diagnostico.py:155`), no del artefacto del caso (`guardas.py:60-68`) | Es la guarda del oráculo débil funcionando en vivo |
| «Rechazos de las guardas», filas G2 y G23 | «No hay respuesta grabada para esta petición». Son CP-A06, CP-A54 y CP-NA15. El run pide 33 respuestas (32 grupos y el resumen, `capacidad-ia.md:840`) y hay 31 grabadas. **Ojo:** el mensaje sugiere `--modelo anthropic` porque es un texto fijo del código (`modelo.py:304`). Las 31 grabadas son de `google` con `gemini-3.1-flash-lite` (`capacidad-ia.md:741-744`), y `anthropic` no se midió (`:217`) | El reporte cuenta lo que falta y no lo rellena |
| «Fallos», columna «DEF propuesto» | CP-A04 propone DEF-01, y el JUnit ya dice `<property name="defecto" value="DEF-01" />` (`junit-cp.xml:54` del respaldo). Los 36 DEF propuestos son el mismo que declara el run, y los 36 vienen con confianza alta | En un run real la respuesta viaja en la entrada: el prompt le pasa el DEF que el run declara (`diagnostico.py:156`, `:166`). Es la fuga de la lámina 19, y por eso se mide con el conjunto de oro |
| «Resumen del run» (si sobra tiempo) | Habla de «una degradación generalizada en la estabilidad». El run #18 terminó en `success`, con los 40 fallos esperados y 0 `failed` (`run.json:10-19`) | Bien escrito y sin sustento: lo que la clase 15 llama equivocarse con seguridad y con buen formato |

## Guion

| Tiempo | Pantalla | Qué señalas | Di |
|---|---|---|---|
| 0:00–0:45 | Lámina 18 · `ia-que` | El flujo, de izquierda a derecha: los 40 fallos, el recuadro SIN IA, el recuadro CON IA y el del Tester. La agrupación es de código: 40 fallos en 32 grupos (`capacidad-ia.md:73`) | «En el laboratorio S11 ya les mostré una IA que revisa resultados: le pasé a Codex el reporte de una prueba de Robot y le pedí que propusiera la validación que faltaba. Era una respuesta suelta, en texto libre, que yo revisaba a ojo. Esto es otra cosa. Es un componente del repositorio que lee los fallos de un run entero, los agrupa con código y le pide al modelo una clasificación por grupo, en un JSON fijo que el código valida antes de escribirla. En la clase 15 es el enfoque A, IA para probar, en la fase de Reporte.» |
| 0:45–1:40 | Lámina 19 · `ia-validacion` | 52 casos: 40, 4 y 8 (`capacidad-ia.md:329-334`). La tercera guarda, `guarda_caso_del_run` (`guardas.py:13`; `capacidad-ia.md:281`), es la que se ve en la demo. El checklist de 6 preguntas, aplicado a esta capacidad: `capacidad-ia.md:800-811` (la pregunta 5, en la 810) | «Lo que el S11 no tenía es cómo saber si la IA acierta. Es lo que la clase 15 llama un eval: 52 fallos con la respuesta correcta y de dónde sale cada una, una tabla por clase con lo esperado contra lo propuesto, y un control sin IA, unas reglas, medido sobre los mismos casos. Antes del reporte hay cuatro guardas en código, mis guardrails: el esquema, el DEF contra los 30 del catálogo de defectos, la evidencia contra el material del caso y los datos personales. Y lo que pasa las guardas lo reviso yo con el checklist de 6 preguntas de la clase 15. La que más pesa es la 5, si algún caso contradice el requisito: los 8 casos de concurrencia que llamó inestables contradicen la regla de 200 de 200.» |
| 1:40–2:40 | Terminal y `diagnostico.md` | La línea de totales; después, en el reporte, el rechazo de CP-T17, las filas G2 y G23 y la columna DEF (tabla de arriba) | «Lo corro sin red: `grabado` repite las respuestas que el modelo dio el 17 de noviembre, así que no llamo a nadie. Cuarenta fallos, treinta y dos grupos, treinta y seis clasificados, uno rechazado y dos errores del backend. El rechazo es CP-T17: citó como evidencia una línea que no está en el artefacto del caso, la sacó del encabezado del grupo. La guarda la paró. Los dos errores son grupos sin respuesta grabada: el reporte los cuenta y no inventa. Y miren la columna DEF: los treinta y seis son el mismo que el JUnit ya trae. El modelo copió la etiqueta. Por eso medí con el conjunto de oro, donde esa fuga está quitada.» |
| 2:40–3:20 | Lámina 20 · `ia-resultado`; después `evals-google.md` | Las barras de la lámina, reglas contra modelo (`evals-google.md:74-79`). En el archivo, la tabla de las líneas 98-107: los 8 errores, todos de concurrencia y todos con confianza `media` | «Con la fuga quitada, este es el resultado, y es incómodo. Sobre los mismos 48 casos, en defecto real el modelo acierta 28 de 36 y las reglas 34 de 36. El DEF correcto sale 0 de 38 en los dos. Los 8 errores son casos de concurrencia que el modelo leyó como inestables, con confianza media. Tal como está, no sustituye al tester ni a las reglas.» |
| 3:20–4:00 | Lámina 21 · `ia-inyeccion` | 0 de 5, 5 de 5 y 0 de 5 (`inyeccion-google.json:73`, `:144`, `:215`). El `DEF-99` dictado salió 1 de 5 en ese archivo (`:145`) y lo rechazó la guarda; en las tres corridas del día, 1, 2 y 4 de 5 (`capacidad-ia.md:626-631`) | «Y la prueba que encontró algo, el red teaming de la clase 15: una orden escrita dentro de la salida de un caso le cambió la clase 5 de 5 veces, contra 0 de 5 sin la orden. Las guardas pararon el DEF inventado, pero no la clase. Es la limitación LIM-IA-01. La regla es la misma del S11, la IA propone y el tester decide, pero ahora está medida: una propuesta no se usa sin mirar el artefacto.» |

**Si va tarde:** en la demo, solo la línea de totales y el rechazo de CP-T17. Te quedas en 20 segundos. La lámina 21, en una frase: «Una orden escrita en el log le cambió la clase 5 de 5 veces. Por eso la IA propone y yo decido».

**Si el comando falla en vivo:** `error: no existe la carpeta del run` quiere decir que falta el respaldo del escritorio. Si la línea de totales no es la de arriba, cambió el prompt o la carpeta de respuestas: una respuesta grabada se busca por el hash del prompt ([`modelo.py:133-135`](../../herramientas/diagnostico_ia/modelo.py)). En los dos casos, abre el del ensayo (`code ~/Desktop/diagnostico-ensayo/diagnostico.md`) y dilo así.

**Si preguntan por qué no llamo al modelo en vivo:** necesita red y la clave en un `.env` local. El comando es el mismo con `--modelo google` (`capacidad-ia.md:757-762`). En el aula no dependo de la red.
