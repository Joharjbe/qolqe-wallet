# Conjunto de oro de la capacidad de IA

Los casos etiquetados contra los que se mide el componente de diagnóstico (`herramientas/diagnostico_ia/`).
Es la pieza que contesta "¿cómo validaron su resultado?": sin una verdad de referencia con procedencia,
cualquier número de acierto es una opinión.

Por cada fallo hay dos cosas: la **entrada** que verá el componente (el fallo tal como sale del JUnit por
caso y de los logs) y la **etiqueta** correcta (clase y, si corresponde, el `DEF-xx`) con su **fuente**:
archivo y línea del repositorio donde está escrita esa verdad.

## Archivos

| Archivo | Qué es |
|---|---|
| `conjunto_oro.json` | El conjunto ya armado y versionado. Es lo que usa el arnés; no hace falta volver a armarlo. |
| `armar.py` | Lo construye leyendo el repositorio y el JUnit por caso, y se revisa a sí mismo (fugas, clases, citas). |
| `casos_escritos.json` | Los casos que no salen tal cual de un artefacto (reconstruidos o sembrados), con su motivo, y los que quedaron fuera. |

## Cuántos casos hay

52 casos. **El conjunto está desbalanceado a propósito**, porque los artefactos del proyecto lo están:
hay 40 casos de fallo esperado con su defecto y un solo caso inestable documentado dentro de un run.

| Clase | Casos | De artefacto | Reconstruido | Sembrado |
|---|---:|---:|---:|---:|
| `defecto_real` | 40 | 40 | 0 | 0 |
| `prueba_inestable` | 4 | 0 | 3 | 1 |
| `error_entorno` | 8 | 0 | 0 | 8 |
| **Total** | **52** | **40** | **3** | **9** |

Por eso el resultado **se lee por clase, nunca con un solo porcentaje global**: "acertó 38 de 40 en
`defecto_real`, 3 de 4 en `prueba_inestable`, 7 de 8 en `error_entorno`". Un promedio único lo decidiría
`defecto_real`, que es el 77 % del conjunto. Con 4 casos, `prueba_inestable` se informa como "N de 4" y
no como un porcentaje.

Cobertura: 25 de los 29 defectos del catálogo (`docs/defectos.md`), 47 casos de API y 5 de web,
29 del núcleo y 23 de G4.

## La regla de las tres clases

La clase va por **la causa del fallo**, que es la que decide la acción del equipo:

- `defecto_real`: lo causa el producto (Qolqe). Acción: enlazar o abrir el `DEF-xx`.
- `prueba_inestable`: lo causa la prueba (una espera que falta, una carrera que no siempre se reproduce).
  Volver a correrla sin tocar nada puede dar otro resultado. Acción: estabilizarla o retirarla.
- `error_entorno`: lo causa el entorno (servidor, puerto, base, dependencias, navegador) y no dice nada
  del producto. Acción: arreglar el entorno y volver a correr.

Un caso aparece dos veces a propósito: **CP-T20** está como `defecto_real` (cuando reproduce DEF-26) y como
`prueba_inestable` (la corrida en que no lo reprodujo y el `xfail` estricto lo dejó en rojo con XPASS). Es el
par que impide contestar por el nombre del caso.

## De dónde sale cada etiqueta

**`defecto_real` (40 casos, de artefacto).** Los 40 `xfailed` del JUnit por caso, cada uno con su propiedad
`defecto`. La etiqueta se comprueba dos veces: el `DEF-xx` tiene que existir como encabezado en
`docs/defectos.md` (y la cita queda guardada con su línea) y tiene que venir del `@DEF-xx` del `.feature`.
Uno de ellos, CP-NW03, lleva además el texto real del fallo que Playwright guardó en el `error-context.md`
de la corrida.

**`prueba_inestable` (4 casos).** Los tres reconstruidos salen de hechos documentados:

| Caso | Fuente | Por qué es de la prueba |
|---|---|---|
| CP-W10 (run #13) | `docs/informe.md:161`, `docs/gestion-casos.md:87` | `failOnFlakyTests` puso el pipeline en rojo; "era un error de la prueba, que no esperaba el alta del contacto". Pasó 2 de 3 repeticiones del mismo run. |
| CP-T20 (ráfaga única) | `docs/defectos.md:6`, `docs/pipeline.md:107`, `docs/informe.md:317` | La regla de las **200 de 200** corridas: con una sola ráfaga no reprodujo DEF-26 en 2 de 90 corridas, así que se cambió la prueba (hasta 5 ráfagas), no el producto. |
| CP-NA69 | `features/nucleo_cuenta_api.feature:208`, `docs/alcance-y-casos.md:184`, `docs/defectos.md:300` | "En ~1 de 25 corridas el proceso se serializa y da el resultado correcto, lo que rompería el xfail estricto": por eso quedó como evidencia manual. |

El cuarto es sembrado (CP-W05), porque con un solo caso real dentro de un run esta clase no se podría medir.

**`error_entorno` (8 casos, todos sembrados y marcados).** No hay ningún run con el entorno roto entre los
artefactos: todos corrieron con uvicorn arriba y con el navegador instalado. Se construyeron a partir de
errores de entorno verosímiles **de este proyecto**, con los textos medidos (ver abajo) y con las rutas y
los puertos reales (`127.0.0.1:8000`, `datos/api.db`, `/api/salud`, los 60 s de `playwright.config.ts`):

| Causa | Casos | Pista que lo separa |
|---|---|---|
| Servidor caído | CP-A01, CP-A05, CP-NA01 | `httpx.ConnectError` y el log de uvicorn vacío. Comparten `grupo_oro`: el agrupamiento tiene que dejarlos juntos. |
| Puerto ocupado | CP-A10 | Mismo fallo que el servidor caído; lo único que cambia es `ERROR: [Errno 48] Address already in use`. |
| Base bloqueada | CP-A09 | Un 500, que es lo más parecido a un defecto; el log dice `sqlite3.OperationalError: database is locked`. |
| Dependencia que ya no llega | CP-NA03 | `ModuleNotFoundError: No module named 'jsonschema_rs'`: el caso queda `sin ejecutar`, sin aserciones. |
| Navegador sin instalar | CP-W12 | `browserType.launch: Executable doesn't exist`. |
| `webServer` sin arrancar | CP-W01 | `Timed out waiting 60000ms from config.webServer` y un arranque de uvicorn a medias. |

El precedente real de esta clase sí existe y está citado en `casos_escritos.json`: DEF-07, cuando instalar
sin `constraints.txt` trajo FastAPI 0.162 y el primer run del pipeline tuvo 6 fallos que no aparecían en
local. No se usa como caso porque allí la causa está repartida entre el entorno y el producto, y una
etiqueta discutible no sirve de verdad de referencia.

## Fugas: qué se quitó de la entrada y por qué

Si la entrada trae la respuesta, el conjunto no mide nada: mide copiar. El JUnit por caso marca los fallos
conocidos como fallos **esperados**, así que había que quitarle cuatro rastros. `armar.py` los quita y
`revisar_fugas` falla si alguno vuelve a entrar.

| Lo que traía el artefacto | Qué se hizo | Por qué |
|---|---|---|
| `<property name="defecto" value="DEF-01">` | `defecto_declarado` queda en `null` | Es el `DEF-xx` de la etiqueta: dejarlo sería regalar la respuesta. |
| `<skipped type="xfail" message="Defecto conocido DEF-01 (fallo esperado)">` | Se reemplaza por el mensaje de un caso que falla (`Fallaron 1 de 1 ejecuciones`), con las mismas palabras que escribe `trazabilidad.py` | "Defecto conocido" ya dice que es un defecto real. |
| `estado = xfailed` | `estado = failed` | `xfailed` significa "defecto conocido": es la clase. |
| La línea de etiquetas del `.feature`, encima del escenario (`@HU-G4-01 @CA1 @CP-A04 @DEF-01`), y los comentarios | El bloque de Gherkin empieza en la línea `Escenario:`; las etiquetas y los comentarios quedan fuera | La etiqueta lleva el `@DEF-xx` y algún comentario nombra el defecto (por ejemplo el de CP-NA69). |

Además, ninguna entrada puede nombrar una clase (`defecto_real`, `prueba_inestable`, `error_entorno`),
decir que el caso es sembrado, ni traer una ruta local (`/Users/...`): lo último es privacidad, y es la
misma regla que `guardas.py` aplica a las respuestas del modelo. La única ruta de máquina que se admite es
`/home/runner`, la del runner de GitHub, que no es de nadie.

**Lo que sí se dejó, y no es fuga.** Las repeticiones de la web (`ejecuciones: 2/3`) y el mensaje
`Inestable: falló 1 de 3 ejecuciones`. Que un caso alterne dentro de un run es la evidencia que el proyecto
usa de verdad para decidir (`failOnFlakyTests`, la regla de las 200 corridas), no una etiqueta filtrada.
Conviene decirlo con precisión, porque es la primera pregunta que cabe hacerle al conjunto:

- En estos 52 casos, los 2 que alternan son los 2 inestables de la web. Así que "alternó → inestable"
  acierta siempre: es una **regla determinista válida**, y por eso el backend `lineabase` (sin IA) la
  resuelve sola. Eso no es una fuga, es el motivo de tener una línea base contra la que comparar.
- Lo que no vale es la vuelta: de los 4 inestables, 2 **no** alternan (CP-T20 con XPASS y CP-NA69), y
  fallar en todas las ejecuciones no dice nada, porque los 8 de entorno también fallan en todas. Así que
  mirando solo ese campo no se contesta el conjunto.

El título del caso también se deja: dice qué se esperaba, que es el oráculo, no la causa.

## Cómo se midieron los textos de los casos sembrados

Los mensajes de error de los casos sembrados no se escribieron de memoria. Cuatro de ellos se reprodujeron
en esta máquina (Python 3.11, macOS), sin levantar uvicorn ni correr las suites:

| Texto | Cómo se reprodujo |
|---|---|
| `httpx.ConnectError: [Errno 61] Connection refused` | `httpx` contra un puerto que se abre y se cierra antes de pedirlo |
| `OSError: [Errno 48] Address already in use` | dos `bind` al mismo puerto |
| `sqlite3.OperationalError: database is locked` | dos conexiones al mismo archivo SQLite, una con `begin exclusive` |
| `ModuleNotFoundError: No module named '...'` | `import` de un módulo que no existe |

Los `Errno` son los de macOS porque en local se corre ahí; en el runner `ubuntu-24.04` los mismos errores
son `[Errno 111]` y `[Errno 98]`, y cada caso lo dice en sus notas. Los dos textos de Playwright
(`Executable doesn't exist` y el timeout de `webServer`) **no** se midieron: son los mensajes conocidos de
la herramienta y así queda anotado, por eso el número de build del navegador va como `<build>` en lugar de
inventarse uno. La traza intermedia del `sqlite3` también va recortada: no se midió, no se escribe.

## Lo que quedó fuera, y por qué

En `casos_escritos.json`, campo `casos_fuera`. El motivo de fondo es el mismo en los cuatro: **no se le pide
al componente lo que la entrada no permite responder**, porque eso es entrenar la alucinación.

- **CP-T19** (no se reprodujo en todas las corridas, sin DEF): dentro de un solo run su fallo no se
  distingue de un defecto real. No hay XPASS ni repeticiones que alternen.
- **CP-NA28** (DEF-16): evidencia manual medida a mano (45.9 ms frente a 1.6 ms). No deja un fallo en el JUnit.
- **DEF-05, DEF-16 y DEF-29**: no tienen un caso que falle en este run (los dos de contrato los encuentran
  checks que `schemathesis.toml` excluye). Por eso la cobertura es 25 de 29 y no 29 de 29.
- **DEF-07**: su etiqueta sería discutible (entorno o producto), y se cita como precedente.

## Cómo se vuelve a armar

```bash
# El JUnit por caso no está versionado: se genera con .github/scripts/trazabilidad.py
# o se baja del artefacto 'trazabilidad' de un run:
#   gh run download <id> -R Joharjbe/qolqe-wallet -n trazabilidad
python tests/diagnostico/conjunto_oro/armar.py --junit reportes/junit-cp.xml

# Comprueba que el JSON versionado es el que arma el script (no escribe nada):
python tests/diagnostico/conjunto_oro/armar.py --junit reportes/junit-cp.xml --verificar
```

El script no escribe nada si alguna revisión falla: una clase desconocida, un `DEF-xx` que no está en
`docs/defectos.md`, una entrada con una fuga o **una cita que no aparece en el archivo y la línea que dice**.
Esa última revisión es la que mantiene honesto al conjunto: si alguien mueve un párrafo de la documentación,
el conjunto deja de armarse hasta que la cita vuelva a ser cierta.

El JUnit del que salió esta versión queda identificado en `conjunto_oro.json`, campo `run_fuente`
(nombre del run, 335 casos, 295 `passed`, 40 `xfailed`, y el sha256 del archivo).
