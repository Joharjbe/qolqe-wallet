# Respuesta a la retroalimentación · Entrega final

La profesora dejó **6 observaciones** en la Entrega 2 y **3 comentarios** en el laboratorio S11; la Entrega 1 y la Entrega 3 no tienen comentarios. Este documento responde las 6 observaciones, una por sección, y los 3 comentarios del laboratorio, y al final resume la Parte 3, porque la entrega final es el consolidado de las tres partes.

Cada punto tiene tres partes: qué cambió, dónde está y cómo comprobarlo.

Los números salen del [run #24](https://github.com/Joharjbe/qolqe-wallet/actions/runs/44225240314) de GitHub Actions, intento 1: push a `main`, commit `1025a78` (merge del PR #9), los 8 jobs en verde. Los comandos se ejecutan desde la raíz del repositorio, con el entorno virtual activo y Qolqe levantado en modo de pruebas (README, sección 6).

**Dónde mirarlo en GitHub**
- Repositorio: https://github.com/Joharjbe/qolqe-wallet. Versión entregada: tag y Release [`entrega-final-v1`](https://github.com/Joharjbe/qolqe-wallet/releases/tag/entrega-final-v1).
- Sitio en Pages, que cada run de `main` vuelve a publicar: [portada](https://joharjbe.github.io/qolqe-wallet/) · [matriz de trazabilidad](https://joharjbe.github.io/qolqe-wallet/trazabilidad.md) · [historial de runs](https://joharjbe.github.io/qolqe-wallet/historial.html) · [evidencias por caso](https://joharjbe.github.io/qolqe-wallet/evidencias/) · [rendimiento (Parte 3)](https://joharjbe.github.io/qolqe-wallet/rendimiento/).

**Texto literal** (Canvas, Entrega 2, nota 14, comentario del 31-oct-2026, 21:47 en Lima). Se copia tal cual, sin tildes agregadas:

| # | Lo que escribió la profesora | Se responde en |
|---|---|---|
| 1a | «Para la entrega final, se deberán considerar los demás escenarios que, a su criterio, también requieran automatización, y agregar las pruebas del módulo común» | §1 |
| 1b | «Ademas se va considerar la cobertura completa de los casos de prueba funcionales y tecnicos en las APIs» | §1 |
| 1c | «Debe quedar claro la arquitectura planteada del proyecto de automatizacion (API y Web), que las herramientas seleccionadas sean complementarias y que su justificación esté debidamente sustentada» | §1 y §5 |
| 2a | «Mejorar la estructura del workflow propuesta para el pipeline. Y cada job planteado debidamente justificado.» | §2 |
| 2b | «Para la entrega final incluir la opcion de permitir seleccionar si la reporteria se desea con evidencia (imagenes) o sin evidencia» | §2 |
| 3 | «Optimizar el tema de trazabilidad tomando en cuenta las multiples veces que se pueden ejecutar. Para la entrega final considerar trabajar con una herramienta de gestion de casos de prueba (se valorara la investigacion)» | §3 |
| 4 | «La justificacion del uso del patron de diseño no esta claro, deben fundamentar mejor en comparativa con otros patrones» | §4 |
| 5 | «Revisar que las herramientas de automatización seleccionadas sean complementarias y que su justificación esté debidamente sustentada» | §5 |
| 6 | «Durante algunas partes de la exposición se percibió cierta inseguridad en lo presentado» | Fila 6 de la tabla de abajo (se responde en la exposición) |

En corto, con lo que cambió:

| Comentario | Qué cambió | Dónde verlo | Cómo se muestra en la exposición |
|---|---|---|---|
| 1. Automatizar lo que falta, módulo común, cobertura de API y arquitectura clara | 181 casos del núcleo (101 API funcionales, 53 técnicos, 27 web) y 96 de G4; 48 de los 51 criterios con caso web; arquitectura API y web documentada | [`alcance-y-casos.md`](alcance-y-casos.md), [`arquitectura.md`](arquitectura.md) §1, [matriz del run #24](trazabilidad.md) | La lámina `arquitectura` y, en la demo (D1), la portada de Pages con los reportes de API y web del último run de `main` |
| 2. Pipeline con jobs justificados y reportes con o sin imágenes | 8 jobs de lo barato a lo caro, con el contrato al inicio, quality gate y entrada `evidencia` | [`pipeline.md`](pipeline.md), [`pruebas.yml`](../.github/workflows/pruebas.yml), [run #18](https://github.com/Joharjbe/qolqe-wallet/actions/runs/43109117336) (con imágenes; su sitio con videos y trazas se retuvo 7 días, hasta el 18-nov-2026; sus capturas por caso siguen en el artefacto `trazabilidad` hasta el 09-feb-2027 y hay una copia local del sitio completo) y [run #24](https://github.com/Joharjbe/qolqe-wallet/actions/runs/44225240314) (sin imágenes) | El desplegable `evidencia` de *Run workflow* (D1, paso 7), la lámina `gate` con los cuatro criterios y, si se pregunta, el [PR #10](https://github.com/Joharjbe/qolqe-wallet/pull/10) bloqueado (`gh pr view 10` → `BLOCKED`; run #25 en rojo, [captura](img/demo-gate-rojo.png)) |
| 3. Trazabilidad con muchas ejecuciones y gestión de casos | `junit-cp.xml` y `run.json` por run; `historial.json` guarda hasta los últimos 30 runs de `main` y `historial.html` dibuja los últimos 15 (al 17-nov, 5 columnas: #17, #18, #20 y los dos intentos del #24); Kiwi TCMS, elegido frente a 8 alternativas, con la importación probada en simulación y hecha de verdad el 17-nov-2026 en el Kiwi del alumno: 10 TestRuns, uno por cada run de `main` importable, incluidos los dos intentos del #24 | [`pipeline.md`](pipeline.md) §Trazabilidad, [`gestion-casos.md`](gestion-casos.md), [`historial.html`](https://joharjbe.github.io/qolqe-wallet/historial.html) | `historial.html` en Pages y, en Kiwi, el TestRun del run #18 (TR-7) y el historial de CP-W10, con una ejecución por TestRun |
| 4. Justificación del patrón frente a otros | 8 patrones web (§3.3) y 4 opciones de API (§3.8), con los criterios de la clase 11; la lámina `patron` resume 5: el elegido, Page Object clásico, palabras clave (Robot), Screenplay y sin patrón; Page Factory (§3.3) y los decoradores de playwright-bdd (§3.6) quedan para las preguntas. Escalabilidad en §3.5. El job `estatico` hace cumplir la regla del patrón | [`arquitectura.md`](arquitectura.md) §3 | De un paso Gherkin al Page Object y al componente (`DialogoConfirmacion`) |
| 5. Herramientas complementarias y justificadas | Una pregunta por herramienta, alternativas con fuente; k6 para el rendimiento | [`arquitectura.md`](arquitectura.md) §2 | La lámina `herramientas` y el JUnit común que las une |
| 6. Inseguridad en partes de la exposición | Cada lámina del deck lleva sus notas de orador con el porqué de lo que muestra; la demo tiene un orden escrito y arranca con datos limpios y Qolqe levantado por un script | [Deck de la exposición](exposicion/deck.pdf) (las notas de orador están en el `<aside>` de cada lámina, en [`deck/project/slides/`](exposicion/deck/project/slides/)), [hoja de la demo](exposicion/hoja-demo.md), [`preparar-demo.sh`](../scripts/preparar-demo.sh) | La exposición misma. Si falla la red, se abre una copia descargada del sitio del run #18 |

La observación 6 no pide un cambio en el repositorio: se responde en la exposición. La fila dice cómo se preparó.

## 1. Automatizar lo que falta, módulo común, cobertura de API y arquitectura clara

> «Para la entrega final, se deberán considerar los demás escenarios que, a su criterio, también requieran automatización, y agregar las pruebas del módulo común»
>
> «Ademas se va considerar la cobertura completa de los casos de prueba funcionales y tecnicos en las APIs»
>
> «Debe quedar claro la arquitectura planteada del proyecto de automatizacion (API y Web), que las herramientas seleccionadas sean complementarias y que su justificación esté debidamente sustentada»

**Qué cambió**
- **Módulo común.** Se agregaron 181 casos para HU-N-01 a HU-N-09: 101 de API funcionales, 53 de API técnicos y 27 web.
- **G4.** Se agregaron 96 casos.
  - 60 de API funcionales: bordes, transiciones no válidas, efectos y códigos de error.
  - 24 técnicos: credenciales, recurso ajeno, tipos, ids en el borde, 405, esquema y concurrencia.
  - 12 web.
- **Total.** 335 casos, 277 de ellos nuevos. Tres casos anteriores (CP-A38, T01 y T03) se retiraron porque repetían a otros más estrictos.
- **Cobertura de los 51 criterios.**
  - Todos tienen caso de API.
  - 48 tienen además caso web: los errores de la API en el registro (CP-NW25), el tope de dígitos de la pantalla (NW26), dos sesiones (NW27) y los rechazos del cierre de cuenta (NW16) cubren los criterios del núcleo que faltaban.
  - Los 3 que no lo tienen no se ven en la pantalla: dos SMS y la concurrencia. Quedan en la API por la regla de la clase 11.
- **Casos técnicos de cabecera (clase 10).** `Content-Type: text/plain`, sin `Content-Type` y `Accept: application/xml` en el registro y la transferencia (CP-NA159, NA160), más no enumeración en el ingreso (NA157) y DNI fuera de las respuestas (NA158).
- **Lo que no se automatizó.** CP-NA28, CP-NA69 y CP-T19 quedan como evidencia manual, porque no dan el mismo resultado en todas las corridas. CP-T19 se midió el 17-nov con un script: la falla aparece en 118 de 200 rondas al cancelar y en 136 de 200 al rechazar, y quedó registrada como DEF-30 ([`resultados-manuales/cp-t19.md`](resultados-manuales/cp-t19.md)).
- **Contrato.** Pasó de 9 operaciones de G4 a 19 del núcleo y de G4.
- **Arquitectura.** Hay un documento propio con las capas, el diagrama y cómo se conectan.
  - En la API, los pasos están separados por área en cuatro módulos (`pasos_g4.py`, `pasos_g4_extra.py`, `pasos_nucleo_acceso.py` y `pasos_nucleo_dinero.py`), y `conftest.py` queda con la infraestructura y los usuarios de la semilla, que la suite escribe solo ahí. Los 45 pasos de G4 de la Parte 2 estuvieron en `conftest.py` hasta el 18-nov-2026, cuando pasaron a `pasos_g4.py` sin cambiar ninguna prueba: las mismas 766 con los mismos IDs, 707 passed y 59 xfailed ([`informe.md`](informe.md) §6).
  - En la web, se crearon componentes compartidos y pasos por área, sin localizadores.

**Dónde**
- [`alcance-y-casos.md`](alcance-y-casos.md): criterio por criterio con sus casos de API funcional, API técnico y web, más la técnica por grupo y los casos técnicos.
- [`arquitectura.md`](arquitectura.md), sección 1: capas, diagrama, datos independientes y árbol del código de API y web.
- [`informe.md`](informe.md), secciones 1 a 3.
- La matriz del run #24, versionada en [`trazabilidad.md`](trazabilidad.md). Pages publica la del último run de `main` ([`trazabilidad.md`](https://joharjbe.github.io/qolqe-wallet/trazabilidad.md)).
- Código:
  - escenarios en `features/nucleo_*_api.feature`, `features/g4_tecnico_api.feature` y `features/web/nucleo_*_web.feature`;
  - pasos en `tests/api/pasos_*.py`;
  - Page Objects en `tests/e2e/pages/`.

**Cómo verificarlo**

| Comando | Resultado esperado |
|---|---|
| `npm run trazabilidad:verificar` | `Trazabilidad: 334 casos, 0 errores, 3 avisos.` (CP-NA45, NA48 y T28 son técnicos sin `@CA`) |
| `python -m pytest tests/api --collect-only -q` | `766 tests collected` |
| `npm run test:api` | `707 passed, 59 xfailed` |
| `npm run test:contrato` | 19 operaciones en verde |
| `npx bddgen && npx playwright test --list` | `Total: 71 tests in 4 files` |
| `npm run test:web:3x` | `213 passed`: 210 pasan y 3 son el fallo esperado de CP-NW03 (DEF-18), que Playwright cuenta como pasado |

**Por qué 334 y no 335.** `--verificar` cuenta los escenarios Gherkin y sus etiquetas: son 334. La matriz suma un caso más, CP-T04, que es la corrida de Schemathesis contra el contrato y no tiene escenario Gherkin ([`casos.py:22-23`](../.github/scripts/casos.py)). Por eso la matriz del run #24 dice 335 casos: 295 passed y 40 xfailed ([`trazabilidad.md`](trazabilidad.md)). Los dos números son correctos y miden cosas distintas. El 334 se volvió a comprobar el 17-nov-2026 sobre el commit `1025a78`.

Los mismos resultados salen en GitHub: en el run #24, el JUnit de `api` tiene 766 casos (59 xfail), el de `web` 213 y el de `contrato` las 19 operaciones más la fase *stateful*, todos sin fallos.

## 2. Estructura del pipeline, cada job justificado y reportes con o sin imágenes

> «Mejorar la estructura del workflow propuesta para el pipeline. Y cada job planteado debidamente justificado.»
>
> «Para la entrega final incluir la opcion de permitir seleccionar si la reporteria se desea con evidencia (imagenes) o sin evidencia»

**Qué cambió**

Antes había 3 jobs: `api`, `web` y `reportes`. Ahora hay 8. Las etapas de prueba van de la más barata a la más cara (`estatico` → `contrato` → `api` → `web`), y las de evidencia corren aparte.

| Job | Qué aporta |
|---|---|
| `estatico` | *Fail fast* sin servidor: ruff, tsc, bddgen, `--collect-only`, etiquetas de trazabilidad, actionlint y la regla del patrón |
| `contrato` | Va al inicio, justo después de `estatico`: si la API no cumple su propio contrato, los casos funcionales y el navegador todavía no significan nada |
| `api` | Solo con `estatico` y `contrato` en verde |
| `web` | Solo con `api` y `contrato` en verde. 3 repeticiones y `failOnFlakyTests` |
| `quality-gate` | Un solo veredicto: las 4 etapas en `success`. Escribe sus 4 criterios de salida en el resumen del run |
| `reportes` | Corre aunque fallen las pruebas (basta `estatico` en verde): el reporte explica el fallo |
| `gestion-casos` | Solo en `main`. Registra el run en Kiwi TCMS si existen los secretos; sin ellos deja un aviso, y la sincronización se hace desde la máquina del alumno con `scripts/kiwi_sincronizar.py` |
| `publicar` | Solo en `main`, y es el último job del run: GitHub Pages. Es el único job con permisos de escritura en Pages |

- **Checks obligatorios.** `main` exige `api` y `web`, y desde el 18-nov-2026 también `quality-gate`, incluso al dueño (`enforce_admins`). `api` y `web` empiezan con una guarda: si la etapa anterior falla, quedan en rojo y no como omitidos. `quality-gate` da el veredicto único en el resumen y cuenta como no aprobada una etapa omitida.
- **Evidencia a elección.** *Run workflow* tiene la entrada `evidencia`. Push y PR usan `sin-imagenes`.

| Modo | Web | API | Contrato | Retención |
|---|---|---|---|---|
| `sin-imagenes` | Captura y traza de los fallos, video en el reintento | Peticiones y respuestas de los fallos y de los xfail | JUnit y HTML | 14 días |
| `con-imagenes` | Captura, video y traza de cada prueba | Peticiones y respuestas de cada caso | Además `peticiones.har` | 7 días |

**Dónde**
- [`pipeline.md`](pipeline.md): un job por fila con su propósito, dependencias, justificación y artefactos.
- [`.github/workflows/pruebas.yml`](../.github/workflows/pruebas.yml).
- `playwright.config.ts`, `tests/api/evidencia.py` y `scripts/correr-contrato.sh`: los tres leen `EVIDENCIA`.
- [`informe.md`](informe.md), sección 3.

**Cómo verificarlo**
- **En GitHub.** El [run #18](https://github.com/Joharjbe/qolqe-wallet/actions/runs/43109117336) se lanzó a pedido con `evidencia=con-imagenes`; el [run #24](https://github.com/Joharjbe/qolqe-wallet/actions/runs/44225240314) es un push con `sin-imagenes`. El resumen de cada run muestra la tabla del quality gate y la matriz. Un run nuevo: *Actions → Pruebas núcleo y G4 → Run workflow*, o `gh workflow run pruebas.yml -R Joharjbe/qolqe-wallet --ref main -f evidencia=con-imagenes`.
- **En local.**
  - Ejecutar `npm run test:web:sin-imagenes` y después `npm run test:web:con-imagenes`.
  - En el reporte de Playwright, solo el segundo tiene captura, video y traza en cada prueba.
  - Lo mismo con `npm run test:api:con-imagenes`: cada caso de `reportes/api/reporte.html` muestra sus peticiones.
- **Validación del workflow.** `actionlint .github/workflows/pruebas.yml` termina sin errores. El job `estatico` lo corre en cada run.

El workflow ya corrió en GitHub: en los PR #7, #8 y #9 y en cada merge a `main`, todos en verde (lista al final). En los PR, `gestion-casos` y `publicar` se omiten porque solo corren en `main`.

## 3. Trazabilidad con muchas ejecuciones y herramienta de gestión de casos

> «Optimizar el tema de trazabilidad tomando en cuenta las multiples veces que se pueden ejecutar. Para la entrega final considerar trabajar con una herramienta de gestion de casos de prueba (se valorara la investigacion)»

**Qué cambió**
- **Antes.** La matriz mostraba un solo run.
- **Ahora, en cada run,** `trazabilidad.py` genera:
  - `junit-cp.xml`, un caso por CP con HU, CA, defecto, módulo, nivel, tipo, estado y evidencia;
  - `run.json`, con commit, evento, modo de evidencia y estado de cada CP;
  - las evidencias por CP.
- **Historial.** `publicar` guarda hasta los últimos 30 runs de `main` en `historial.json` y `historial.html` dibuja los últimos 15, una grilla CP × runs; la estabilidad y la primera y última vez se calculan sobre todos los guardados (hasta 30). Al 17-nov-2026 tiene 5 columnas: #17, #18, #20, #24.1 y #24.2, porque el *re-run* del #24 es su propia columna. Cada merge a `main` suma una.
- **Herramienta de gestión de casos: Kiwi TCMS 17.0**, en Docker local.
  - Se eligió tras comparar ocho alternativas: Qase, TestRail, Xray, Zephyr, QMetry, Testmo, Allure TestOps y TestLink. Kiwi es gratis, sin límite de runs, sin cuenta externa y con importador JUnit oficial.
  - `scripts/kiwi_sincronizar.py` importa cada run de `main` como un TestRun, también los anteriores, que reconstruye desde sus artefactos.
  - Cada CP acumula todas sus ejecuciones, y un xfail con DEF queda como WAIVED con enlace al defecto.
- **Etiquetas.** `--verificar` exige `@HU`, `@CA` y `@CP` válidos en cada escenario, y que cada par `@HU` `@CA` exista en `requisitos.md`.

**Dónde**
- [`gestion-casos.md`](gestion-casos.md): investigación con fuentes, mapeo proyecto → Kiwi, pasos y estado verificado.
- [`pipeline.md`](pipeline.md), sección de trazabilidad.
- En Pages: [`historial.html`](https://joharjbe.github.io/qolqe-wallet/historial.html), y el [`junit-cp.xml`](https://joharjbe.github.io/qolqe-wallet/junit-cp.xml) y el [`run.json`](https://joharjbe.github.io/qolqe-wallet/run.json) del último run de `main`.
- Código: `.github/scripts/casos.py` y `trazabilidad.py`, `herramientas/kiwi/` y `requirements-gestion.txt`.

**Cómo verificarlo**
- **Matriz del pipeline.** El job `reportes` la arma en cada run. La del run #24 da *335 casos, 295 passed, 40 xfailed* y 0 inestables, y es la que está versionada en [`trazabilidad.md`](trazabilidad.md).
- **Matriz local.** `python .github/scripts/trazabilidad.py --sitio /tmp/sitio --matriz /tmp/sitio/trazabilidad.md --junit-cp /tmp/sitio/junit-cp.xml --run-json /tmp/sitio/run.json` después de correr las suites (sin `--matriz` reescribe `docs/trazabilidad.md`).
- **Kiwi sin conectarse.** `GH_TOKEN=$(gh auth token --user Joharjbe) python scripts/kiwi_sincronizar.py --simular --ultimos 20` muestra lo que se crearía en Kiwi. Corrido el 17-nov-2026, revisó 9 runs de `main`. El #17, el #18, el #20 y el #24 dan 335 ejecuciones cada uno (295 PASSED, 40 WAIVED y 40 enlaces de defecto), y el #18 trae además 219 capturas como adjuntos. Los #5, #7, #10, #12 y #15, anteriores al núcleo común, se reconstruyen de `reportes-api` y `reportes-web` con 61 ejecuciones cada uno (57 PASSED y 4 WAIVED). Es una simulación: no crea nada en Kiwi.
- **Kiwi real.** Kiwi corre en la máquina del alumno (`docker compose up -d` en `herramientas/kiwi`). La primera sincronización real (17-nov-2026, `kiwi_sincronizar.py --ultimos 20` con `KIWI_PLAN_ID=1`, repetida después del *re-run*) dejó 10 TestRuns en el plan TP-1: los runs #5, #7, #10, #12 y #15 con 61 ejecuciones cada uno (57 PASSED y 4 WAIVED), y los #17, #18, #20, #24 y el intento 2 del #24 con 335 cada uno (295 PASSED, 40 WAIVED y 40 enlaces de defecto hacia 25 DEF distintos). El TestRun del #18 (TR-7) recibió 216 de las 219 capturas: Kiwi rechazó 3 (CP-NW25, repeticiones 3, 8 y 13) con «File contains forbidden tag: <rt>», un falso positivo de su filtro de subida sobre los bytes del PNG. Capturas: [`kiwi-testruns.png`](img/kiwi-testruns.png), [`kiwi-testrun-18.png`](img/kiwi-testrun-18.png), [`kiwi-caso-ejecuciones.png`](img/kiwi-caso-ejecuciones.png), [`kiwi-status-matrix.png`](img/kiwi-status-matrix.png) y [`pages-historial.png`](img/pages-historial.png).

## 4. Justificación del patrón de diseño frente a otros

> «La justificacion del uso del patron de diseño no esta claro, deben fundamentar mejor en comparativa con otros patrones»

Es una crítica repetida: el laboratorio S11 la hizo antes con otras palabras (ver «Laboratorio S11», abajo).

**Qué cambió**
- **Comparación.** Se compararon 8 opciones con los criterios de la clase 11 (tamaño de la suite, cuánto cambia la interfaz, uso de BDD y lo que trae el framework):
  - sin patrón;
  - Page Object;
  - Page Object con componentes y fixtures;
  - Page Factory;
  - Page Object encadenado;
  - Screenplay;
  - App Actions;
  - palabras clave (Robot Framework).
- **Elegido: Page Object con componentes y fixtures.** El documento explica cuándo convendría Screenplay.
- **El código ahora sigue esa decisión.**
  - `componentes.ts` tiene un objeto por cada componente que `app.js` repite: aviso, diálogo de confirmación, diálogo de formulario, lista vacía y menú.
  - `PaginaQolqe` es una base de un solo nivel. Las pantallas componen, no heredan entre sí: usan el diálogo de formulario, el de confirmación y el menú. El aviso y la lista vacía no los usa ninguna pantalla: `fixtures.ts` los inyecta directo a los pasos.
  - Se eliminó `ComunPage`, que mezclaba responsabilidades, y el localizador por posición `.last()`.
  - Los pasos están separados por área y no tienen localizadores.
- **Escalabilidad.** Qué cuesta sumar un módulo, una pantalla o un integrante, y qué no escala igual de bien: [`arquitectura.md`](arquitectura.md) §3.5.
- **Decisión explícita.** Las verificaciones `esperar…` van dentro del Page Object y solo las llaman los pasos `Entonces`. Fowler prefiere no verificar en el Page Object; Playwright sí lo hace en su ejemplo oficial.
- **La regla ya no vive solo en el documento.** Desde el PR #9, el job `estatico` falla si un paso usa `getBy`, `locator(` o `page.` (paso *Regla del patrón*).

**Dónde**
- [`arquitectura.md`](arquitectura.md), sección 3: comparación, justificación, escalabilidad, decisiones explícitas y cuándo cambiaríamos de patrón.
- `tests/e2e/pages/componentes.ts`, `PaginaQolqe.ts` y `tests/e2e/fixtures.ts`.
- [`informe.md`](informe.md), sección 3.
- Fuentes:
  - https://martinfowler.com/bliki/PageObject.html
  - https://playwright.dev/docs/pom
  - https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/
  - https://serenity-js.org/handbook/design/screenplay-pattern/

**Cómo verificarlo**
- `grep -cE "getBy|locator\(" tests/e2e/steps/*.ts` da 0 en los 5 archivos: ningún paso conoce el HTML.
- `npx tsc --noEmit -p tests/e2e` termina sin errores. El job `estatico` lo ejecuta.

## 5. Herramientas complementarias y bien justificadas

> «Revisar que las herramientas de automatización seleccionadas sean complementarias y que su justificación esté debidamente sustentada»

Repite la parte final de la observación 1c: es la otra crítica repetida.

**Qué cambió.** Cada herramienta responde una pregunta distinta. Donde dos se solapan, es a propósito y con un oráculo distinto: la web confirma que el usuario ve el error y la API prueba la regla que lo produce.

| Herramienta | Pregunta que responde | Lo que no cubre y cubre otra |
|---|---|---|
| pytest-bdd + httpx | ¿Se cumple cada regla y cada criterio? Funcional y técnico | Entradas que nadie escribió (Schemathesis) y lo que se ve en pantalla (Playwright) |
| Schemathesis | ¿La API cumple su contrato OpenAPI, también con entradas generadas? | Reglas de negocio (pytest-bdd) |
| Playwright + playwright-bdd | ¿El usuario ve y logra lo que dice el criterio? | Reglas y concurrencia (pytest-bdd) |
| GitHub Actions | ¿Se prueba todo en cada cambio y se bloquea si falla? | Historial de muchas ejecuciones (Pages y Kiwi) |
| `trazabilidad.py` + Pages | ¿Qué pasó en este run y en los anteriores (hasta 30 guardados, 15 en la grilla)? | Gestión de casos con planes, versiones y builds (Kiwi) |
| Kiwi TCMS | ¿Cómo evoluciona cada caso a lo largo de todas las ejecuciones? | No ejecuta pruebas: importa el JUnit de las otras |
| k6 2.3.0, con Qolqe en Docker (1 CPU y 1 GB); psutil, `docker stats` y py-spy | ¿Cumple el SLA con la carga del requerimiento y hasta cuántos usuarios aguanta? k6 modela la carga como tasa de llegada (modelo abierto) | Si cada regla se cumple (pytest-bdd). k6 mide tiempos, errores y capacidad; el dinero íntegro se verifica aparte, antes y después de cada corrida (`tests/performance/integridad/`) |

Las tres herramientas de prueba funcional escriben JUnit XML, el formato común que leen la matriz, el resumen del run y Kiwi. k6 deja su propia evidencia por corrida en `tests/performance/resultados/`.

- **Alternativas descartadas, con un dato verificable y su fuente para cada una** ([`arquitectura.md`](arquitectura.md), sección 2):
  - Karate, Postman/Newman, Bruno, REST Assured, Robot + RequestsLibrary y el cliente HTTP de Playwright en la API;
  - Dredd y Pact en el contrato;
  - Selenium, Cypress, Robot Framework + Browser y WebdriverIO en la web;
  - Jenkins y GitLab CI en la orquestación;
  - Allure Report en los reportes;
  - Qase, TestRail, Xray, Zephyr, QMetry, Testmo, Allure TestOps y TestLink en la gestión de casos ([`gestion-casos.md`](gestion-casos.md));
  - JMeter, Gatling, Locust, Artillery y Taurus en el rendimiento ([informe de rendimiento](Informe_Rendimiento_Qolqe.pdf), §2).
- **Robot Framework.** Se corrigió la justificación anterior, que se apoyaba en la espera automática. Robot Browser también corre sobre Playwright. Las diferencias reales son tres:
  - los mismos `.feature` que la API;
  - el runner de Playwright, con repeticiones, `failOnFlakyTests` y trazas;
  - la evidencia del run #13, donde esa combinación detectó un escenario inestable real.

**Dónde**
- [`arquitectura.md`](arquitectura.md), sección 2, incluida la elección de Python y TypeScript.
- [`informe.md`](informe.md), secciones 2, 3 y 4.
- [`gestion-casos.md`](gestion-casos.md), para la elección de Kiwi.
- Fuentes:
  - https://schemathesis.readthedocs.io/en/stable/
  - https://playwright.dev/docs/api/class-testconfig
  - https://robotframework-browser.org/
  - https://pypi.org/project/kiwitcms-junit.xml-plugin/
  - https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/open-vs-closed/
  - https://psutil.readthedocs.io/en/stable/
  - https://docs.docker.com/reference/cli/docker/container/stats/
  - https://github.com/benfred/py-spy

**Cómo verificarlo.** Los JUnit de las tres herramientas funcionales quedan en `reportes/api/junit.xml`, `reportes/contrato/junit.xml` y `reportes/web/junit.xml`. Con `trazabilidad.py` se unen en una sola matriz por CP.

## Laboratorio S11 (nota 15, comentario del 25-oct-2026)

Tres comentarios, copiados tal cual. Dos vuelven en el anuncio final: el del patrón (crítica repetida) y el de la reportería.

| Lo que escribió la profesora | Cómo se responde en la entrega final |
|---|---|
| «Mayor sustento en el uso del patron de diseño» | Es la misma crítica que la observación 4 de la Entrega 2. Se responde en §4: [`arquitectura.md`](arquitectura.md) §3.3 a §3.5 compara 8 patrones con los criterios de la clase 11 y suma la escalabilidad |
| «Falto profundizar la reporteria de la herramienta y las opciones que ofrece» | En el laboratorio la herramienta era Robot Framework (`labs/s11-robot/`). En la entrega final, [`pipeline.md`](pipeline.md#opciones-de-reportería-de-cada-herramienta), «Opciones de reportería de cada herramienta», lista lo que ofrece cada una y qué se usa: los reporters `list`, `html` y `junit` (con `includeRetries`) de Playwright, y `screenshot`, `video` y `trace` en sus dos modos (`playwright.config.ts:26-37`); `--junitxml` y `--html --self-contained-html` de pytest (`package.json:9`); JUnit, HTML y HAR de Schemathesis (`scripts/correr-contrato.sh:15-19`), y el resumen del job en `$GITHUB_STEP_SUMMARY` (`.github/scripts/resumen.py:35`) |
| «Los materiales no se subieron a tiempo» | Para la entrega final el plazo es el viernes 20-nov (anuncio del 15-nov), y la versión entregada queda congelada en el tag `entrega-final-v1` (README, «Congelación») |

## La Parte 3: rendimiento con k6

La Entrega 3 no recibió observaciones escritas. Esta sección está porque la entrega final consolida las tres partes.

**Qué se hizo**
- **Herramienta y entorno.** k6 2.3.0 con Qolqe en Docker, limitado a 1 CPU y 1 GB. CPU y memoria de Qolqe con psutil y `docker stats`, perfiles con py-spy.
- **Escenarios.** Carga (100 simultáneos, 15 min estables), pico (100 → 300 → 100), estrés (rampa de 100 a 2,400, que k6 cortó tras un máximo de 1,144 simultáneos) y resistencia (100 simultáneos, 60 min). Se ejecutaron los cuatro; las dos más importantes son carga y estrés, porque responden «si cumplimos en hora punta» y «hasta cuántos usuarios simultáneos podemos crecer», y son las que pide la rúbrica de la Parte 3 («Carga y estrés ejecutadas»).
- **Veredicto frente al SLA.** Carga, pico y resistencia cumplen todos sus umbrales, con 0.00 % de operaciones fallidas y 0 descuadres de dinero. La capacidad medida es de 850 usuarios simultáneos con 1 CPU.
- **Limitaciones declaradas.** La resistencia duró 60 min en lugar de 18 h. El login con 1 usuario dio 92 ms frente al límite de 80 ms de la referencia (V-06). V-04 y V-01 se ajustaron durante la ejecución. El estrés lo cortó la red de seguridad de k6 antes de la meseta. La laptop estaba compartida con procesos de macOS. Por eso los resultados son una línea base relativa, no la capacidad de producción.
- **Lo que cambió en la entrega final.** Pages publica la Parte 3 en [`rendimiento/`](https://joharjbe.github.io/qolqe-wallet/rendimiento/), con el veredicto por umbral de cada escenario (PR #9). El rendimiento no corre en el pipeline ni entra al quality gate, y es una decisión: [`pipeline.md`](pipeline.md), sección *Por qué el rendimiento no corre en el pipeline*.

**Dónde**
- [`informe.md`](informe.md), sección 4, y el informe con la plantilla del curso: [`Informe_Rendimiento_Qolqe.docx`](Informe_Rendimiento_Qolqe.docx) ([PDF](Informe_Rendimiento_Qolqe.pdf)).
- [`arquitectura.md`](arquitectura.md) §1.6 (las capas del rendimiento) y §3.9 (el patrón del lado del rendimiento).
- [`tests/performance/README.md`](../tests/performance/README.md): cómo repetir cada corrida.
- [`tests/performance/resultados/`](../tests/performance/resultados/): la evidencia de cada corrida, con su `veredicto.md`.

**Cómo verificarlo.** Abrir [`rendimiento/`](https://joharjbe.github.io/qolqe-wallet/rendimiento/) en Pages, o el `veredicto.md` de cada corrida en `tests/performance/resultados/`. Para repetir una corrida, `tests/performance/correr.sh <escenario>` (README de rendimiento).

## Lo que ya se ejecutó en GitHub

| Run | Evento | Commit | Qué demuestra |
|---|---|---|---|
| [#16](https://github.com/Joharjbe/qolqe-wallet/actions/runs/43104812888) | PR #7 | `51ccfa9` | El workflow nuevo en verde antes de fusionar |
| [#17](https://github.com/Joharjbe/qolqe-wallet/actions/runs/43109102424) | Push a `main`, merge del PR #7 | `5fbe969` | Los 8 jobs en verde en `main`, con `publicar` y Pages |
| [#18](https://github.com/Joharjbe/qolqe-wallet/actions/runs/43109117336) | A pedido, `evidencia=con-imagenes` | `5fbe969` | Captura, video y traza de cada prueba web |
| [#19](https://github.com/Joharjbe/qolqe-wallet/actions/runs/43175341232) | PR #8, Parte 3 | `34584ed` | La Parte 3 no rompe el pipeline |
| [#20](https://github.com/Joharjbe/qolqe-wallet/actions/runs/43178430994) | Push a `main`, merge del PR #8 | `60e80d3` | La Parte 3 en `main` (tag `parte-3`) |
| [#21](https://github.com/Joharjbe/qolqe-wallet/actions/runs/44103875074) a [#23](https://github.com/Joharjbe/qolqe-wallet/actions/runs/44162762505) | PR #9 | `2bbf44f` a `f87c7c1` | El contrato al inicio, la Parte 3 en el sitio y la capacidad de IA, en verde antes de fusionar |
| [#24](https://github.com/Joharjbe/qolqe-wallet/actions/runs/44225240314) | Push a `main`, merge del PR #9 | `1025a78` | Los 8 jobs en verde. Es el run del que salen los números de este documento |
| [#24, intento 2](https://github.com/Joharjbe/qolqe-wallet/actions/runs/44225240314/attempts/2) | *Re-run* de todos los jobs | `1025a78` | Los 8 jobs otra vez en verde con el mismo commit. En `historial.html` es una columna aparte (#24.2) |
| [#25](https://github.com/Joharjbe/qolqe-wallet/actions/runs/44240958431) | PR #10, no se fusiona | `100674c` | El gate corta con el pipeline actual: `api` en rojo (1 failed, 706 passed y 59 xfailed; CP-A28 espera 770.00 y el saldo es 775.00), `web` en rojo por su guarda y `quality-gate` en rojo ([captura del run](img/demo-gate-rojo.png)). La fusión queda bloqueada (`gh pr view 10` → `BLOCKED`, 18-nov-2026) |

- **Concurrencia en el runner.** La misma suite corrió en los 9 runs seguidos del #16 al #24, todos en verde, y otra vez en el intento 2 del #24 (*Re-run*: 707 passed y 59 xfailed en 244.79 s). Como el xfail es estricto (`tests/api/conftest.py:26`), un escenario `@concurrencia` que diera XPASS habría puesto `api` en rojo.
- **Matriz versionada.** [`trazabilidad.md`](trazabilidad.md) es la matriz del artefacto `trazabilidad` del run #24, no una corrida local.
- **Checks obligatorios.** `main` exige `api` y `web`, y desde el 18-nov-2026 también `quality-gate`, con `enforce_admins` activo. El PR #10 sigue `BLOCKED` con los tres en rojo (`gh pr view 10`, 18-nov-2026).

- **Kiwi TCMS.** Primera sincronización real el 17-nov-2026: 10 TestRuns, con las capturas en `docs/img/` (§3).

**Límites de la evidencia**
1. **Evidencia con imágenes.** El sitio completo del run #18 (artefactos `sitio` y `reportes-web`, con los videos y las trazas) se retuvo en GitHub 7 días, hasta el 18-nov-2026, porque es lo que retiene el modo `con-imagenes`. Sus capturas por caso siguen en el artefacto `trazabilidad` hasta el 09-feb-2027, y para la exposición hay una copia descargada del sitio completo. Al 18-nov-2026, Pages servía el intento 2 del run #24, que es `sin-imagenes` (`run.json` publicado, leído ese día); cada run nuevo de `main` lo reemplaza.
