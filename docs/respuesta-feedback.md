# Respuesta a la retroalimentación · Entrega final

Cada punto tiene tres partes: qué cambió, dónde está y cómo comprobarlo.

Los comandos se ejecutan desde la raíz del repositorio, con el entorno virtual activo y Qolqe levantado en modo de pruebas (README, sección 6). Los números son de la corrida local del 11-nov-2026 sobre la rama `entrega-final`, después de la revisión final.

| Comentario | Qué cambió | Dónde verlo | Cómo se muestra en la exposición |
|---|---|---|---|
| 1. Automatizar lo que falta, módulo común, cobertura de API y arquitectura clara | 181 casos del núcleo (101 API funcionales, 53 técnicos, 27 web) y 96 de G4; 48 de los 51 criterios con caso web; arquitectura API y web documentada | [`alcance-y-casos.md`](alcance-y-casos.md), [`arquitectura.md`](arquitectura.md) §1 | Diagrama de capas y una corrida de `npm run test:api` y `npm run test:web:3x` |
| 2. Pipeline con jobs justificados y reportes con o sin imágenes | 8 jobs de lo barato a lo caro, quality gate y entrada `evidencia` | [`pipeline.md`](pipeline.md), `.github/workflows/pruebas.yml` | Run a pedido con `evidencia=con-imagenes` y el resumen del quality gate |
| 3. Trazabilidad con muchas ejecuciones y gestión de casos | `junit-cp.xml` y `run.json` por run, `historial.html` de 30 runs en Pages y Kiwi TCMS con un TestRun por run | [`pipeline.md`](pipeline.md) §Trazabilidad, [`gestion-casos.md`](gestion-casos.md) | `historial.html` y el TestRun del run en Kiwi, con un CP y su historia |
| 4. Justificación del patrón frente a otros | Comparación con 8 opciones (web) y 4 (API) con los criterios de la clase 11 | [`arquitectura.md`](arquitectura.md) §3 | De un paso Gherkin al Page Object y al componente (`DialogoConfirmacion`) |
| 5. Herramientas complementarias y justificadas | Una pregunta por herramienta, alternativas con fuente | [`arquitectura.md`](arquitectura.md) §2 | La tabla de herramientas y el JUnit común que las une |

## 1. Automatizar lo que falta, módulo común, cobertura de API y arquitectura clara

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
- **Lo que no se automatizó.** CP-NA28, CP-NA69 y CP-T19 quedan como evidencia manual, porque no dan el mismo resultado en todas las corridas.
- **Contrato.** Pasó de 9 operaciones de G4 a 19 del núcleo y de G4.
- **Arquitectura.** Hay un documento propio con las capas, el diagrama y cómo se conectan.
  - En la API, los pasos se separaron por área.
  - En la web, se crearon componentes compartidos y pasos por área, sin localizadores.

**Dónde**
- [`alcance-y-casos.md`](alcance-y-casos.md): criterio por criterio con sus casos de API funcional, API técnico y web, más la técnica por grupo y los casos técnicos.
- [`arquitectura.md`](arquitectura.md), sección 1: capas, diagrama, datos independientes y árbol del código de API y web.
- [`informe.md`](informe.md), secciones 1 a 3.
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

## 2. Estructura del pipeline, cada job justificado y reportes con o sin imágenes

**Qué cambió**

Antes había 3 jobs: `api`, `web` y `reportes`. Ahora hay 8. Las etapas de prueba van de la más barata a la más cara, y las de evidencia corren aparte.

| Job | Qué aporta |
|---|---|
| `estatico` | *Fail fast* sin servidor: ruff, tsc, bddgen, `--collect-only` y etiquetas de trazabilidad |
| `api` y `contrato` | Corren en paralelo. El contrato ya no depende de que pytest pase |
| `web` | Solo con `api` y `contrato` en verde. 3 repeticiones y `failOnFlakyTests` |
| `quality-gate` | Un solo veredicto: las 4 etapas en `success` |
| `reportes` | Corre aunque fallen las pruebas: el reporte explica el fallo |
| `gestion-casos` | Registra el run en Kiwi TCMS |
| `publicar` | GitHub Pages. Es el único job con permisos de escritura en Pages |

- **Checks obligatorios.** `api` y `web` siguen siéndolo en `main` y empiezan con una guarda: si la etapa anterior falla, no quedan como omitidos.
- **Evidencia a elección.** *Run workflow* tiene la entrada `evidencia`. Push y PR usan `sin-imagenes`.

| Modo | Web | API | Contrato | Retención |
|---|---|---|---|---|
| `sin-imagenes` | Captura y traza de los fallos, video en el reintento | Peticiones y respuestas de los fallos y de los xfail | JUnit y HTML | 14 días |
| `con-imagenes` | Captura, video y traza de cada prueba | Peticiones y respuestas de cada caso | Además `peticiones.har` | 7 días |

**Dónde**
- [`pipeline.md`](pipeline.md): un job por fila con su propósito, dependencias, justificación y artefactos.
- `.github/workflows/pruebas.yml`.
- `playwright.config.ts`, `tests/api/evidencia.py` y `scripts/correr-contrato.sh`: los tres leen `EVIDENCIA`.
- [`informe.md`](informe.md), sección 3.

**Cómo verificarlo**
- **En GitHub.** *Actions → Pruebas núcleo y G4 → Run workflow* con *evidencia* `con-imagenes`, o `gh workflow run pruebas.yml -R Joharjbe/qolqe-wallet --ref main -f evidencia=con-imagenes`. El resumen del run muestra la tabla del quality gate y la matriz.
- **En local.**
  - Ejecutar `npm run test:web:sin-imagenes` y después `npm run test:web:con-imagenes`.
  - En el reporte de Playwright, solo el segundo tiene captura, video y traza en cada prueba.
  - Lo mismo con `npm run test:api:con-imagenes`: cada caso de `reportes/api/reporte.html` muestra sus peticiones.
- **Validación del workflow.** `actionlint .github/workflows/pruebas.yml` termina sin errores.

El workflow nuevo todavía no corrió en GitHub: la rama no está publicada. `gestion-casos` y `publicar` solo corren en `main`.

## 3. Trazabilidad con muchas ejecuciones y herramienta de gestión de casos

**Qué cambió**
- **Antes.** La matriz mostraba un solo run.
- **Ahora, en cada run,** `trazabilidad.py` genera:
  - `junit-cp.xml`, un caso por CP con HU, CA, defecto, módulo, nivel, tipo, estado y evidencia;
  - `run.json`, con commit, evento, modo de evidencia y estado de cada CP;
  - las evidencias por CP.
- **Historial.** `publicar` acumula los últimos 30 runs en `historial.html`, una grilla CP × runs con estabilidad y primera y última vez.
- **Herramienta de gestión de casos: Kiwi TCMS 17.0**, en Docker local.
  - Se eligió tras comparar Qase, TestRail, Xray, Zephyr, Testmo, Allure TestOps y TestLink: es gratis, sin límite de runs, sin cuenta externa y con importador JUnit oficial.
  - `scripts/kiwi_sincronizar.py` importa cada run de `main` como un TestRun, también los anteriores, que reconstruye desde sus artefactos.
  - Cada CP acumula todas sus ejecuciones, y un xfail con DEF queda como WAIVED con enlace al defecto.
- **Etiquetas.** `--verificar` exige `@HU`, `@CA` y `@CP` válidos en cada escenario, y que cada par `@HU` `@CA` exista en `requisitos.md`.

**Dónde**
- [`gestion-casos.md`](gestion-casos.md): investigación con fuentes, mapeo proyecto → Kiwi, pasos y estado verificado.
- [`pipeline.md`](pipeline.md), sección de trazabilidad.
- Código: `.github/scripts/casos.py` y `trazabilidad.py`, `herramientas/kiwi/` y `requirements-gestion.txt`.

**Cómo verificarlo**
- **Matriz local.** `python .github/scripts/trazabilidad.py --sitio /tmp/sitio --matriz /tmp/sitio/trazabilidad.md --junit-cp /tmp/sitio/junit-cp.xml --run-json /tmp/sitio/run.json` después de correr las suites (sin `--matriz` reescribe `docs/trazabilidad.md`). Con los JUnit del 11-nov da *335 casos, 295 passed, 40 xfailed*.
- **Kiwi sin conectarse.** `GH_TOKEN=$(gh auth token --user Joharjbe) python scripts/kiwi_sincronizar.py --simular --ultimos 20 --historial /tmp/historial` muestra lo que se crearía en Kiwi y arma el historial de los runs de GitHub.
- **Kiwi real.** `docker compose up -d` en `herramientas/kiwi` y abrir https://localhost:8443. La importación se probó en un Kiwi 17 desechable de la misma imagen; en el Kiwi del alumno falta crear su usuario (`initial_setup`) y sincronizar los runs de `main`.

## 4. Justificación del patrón de diseño frente a otros

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
  - `PaginaQolqe` es una base de un solo nivel. Las pantallas componen, no heredan entre sí.
  - Se eliminó `ComunPage`, que mezclaba responsabilidades, y el localizador por posición `.last()`.
  - Los pasos están separados por área y no tienen localizadores.
- **Decisión explícita.** Las verificaciones `esperar…` van dentro del Page Object y solo las llaman los pasos `Entonces`. Fowler prefiere no verificar en el Page Object; Playwright sí lo hace en su ejemplo oficial.

**Dónde**
- [`arquitectura.md`](arquitectura.md), sección 3: comparación, justificación, decisiones explícitas y cuándo cambiaríamos de patrón.
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

**Qué cambió.** Cada herramienta responde una pregunta distinta. Donde dos se solapan, es a propósito y con un oráculo distinto: la web confirma que el usuario ve el error y la API prueba la regla que lo produce.

| Herramienta | Pregunta que responde | Lo que no cubre y cubre otra |
|---|---|---|
| pytest-bdd + httpx | ¿Se cumple cada regla y cada criterio? Funcional y técnico | Entradas que nadie escribió (Schemathesis) y lo que se ve en pantalla (Playwright) |
| Schemathesis | ¿La API cumple su contrato OpenAPI, también con entradas generadas? | Reglas de negocio (pytest-bdd) |
| Playwright + playwright-bdd | ¿El usuario ve y logra lo que dice el criterio? | Reglas y concurrencia (pytest-bdd) |
| GitHub Actions | ¿Se prueba todo en cada cambio y se bloquea si falla? | Historial de muchas ejecuciones (Pages y Kiwi) |
| `trazabilidad.py` + Pages | ¿Qué pasó en este run y en los últimos 30? | Gestión de casos con planes, versiones y builds (Kiwi) |
| Kiwi TCMS | ¿Cómo evoluciona cada caso a lo largo de todas las ejecuciones? | No ejecuta pruebas: importa el JUnit de las otras |

Las tres herramientas de prueba escriben JUnit XML, el formato común que leen la matriz, el resumen del run y Kiwi.

- **Alternativas descartadas, con un dato verificable y su fuente para cada una** ([`arquitectura.md`](arquitectura.md), sección 2):
  - Karate, Postman/Newman, Bruno, REST Assured, Robot + RequestsLibrary y el cliente HTTP de Playwright en la API;
  - Dredd y Pact en el contrato;
  - Selenium, Cypress, Robot Framework + Browser y WebdriverIO en la web;
  - Jenkins y GitLab CI en la orquestación;
  - Allure Report en los reportes;
  - Qase, TestRail, Xray, Zephyr y TestLink en la gestión de casos.
- **Robot Framework.** Se corrigió la justificación anterior, que se apoyaba en la espera automática. Robot Browser también corre sobre Playwright. Las diferencias reales son tres:
  - los mismos `.feature` que la API;
  - el runner de Playwright, con repeticiones, `failOnFlakyTests` y trazas;
  - la evidencia del run #13, donde esa combinación detectó un escenario inestable real.

**Dónde**
- [`arquitectura.md`](arquitectura.md), sección 2, incluida la elección de Python y TypeScript.
- [`informe.md`](informe.md), secciones 2 y 3.
- [`gestion-casos.md`](gestion-casos.md), para la elección de Kiwi.
- Fuentes:
  - https://schemathesis.readthedocs.io/en/stable/
  - https://playwright.dev/docs/api/class-testconfig
  - https://robotframework-browser.org/
  - https://pypi.org/project/kiwitcms-junit.xml-plugin/

**Cómo verificarlo.** Los JUnit de las tres herramientas quedan en `reportes/api/junit.xml`, `reportes/contrato/junit.xml` y `reportes/web/junit.xml`. Con `trazabilidad.py` se unen en una sola matriz por CP.

## Pendiente de ejecutar en GitHub

Lo que solo se puede ver después de publicar la rama (lo hace el alumno; la rama `entrega-final` no está publicada):

1. `git push entrega entrega-final` (el remoto de entrega, no `origin`) y abrir el PR a `main` en `Joharjbe/qolqe-wallet`.
2. Confirmar en el PR `estatico`, `api`, `contrato`, `web`, `quality-gate` y `reportes` en verde, con la matriz en el resumen del run. Repetir el job `api` 3 veces y revisar que ningún escenario `@concurrencia` dé XPASS en el runner.
3. Fusionar y confirmar `publicar` y Pages (portada con veredicto e `historial.html`).
4. `gh workflow run pruebas.yml -R Joharjbe/qolqe-wallet --ref main -f evidencia=con-imagenes` y un re-run, para que el historial muestre varios runs y un intento 2.
5. Agregar `quality-gate` como check obligatorio en *Settings → Branches*.
6. Sincronizar Kiwi (`docs/gestion-casos.md`), guardar las capturas en `docs/img/` y versionar `docs/trazabilidad.md` desde el artefacto `trazabilidad` del run verde.
