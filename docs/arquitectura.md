# Arquitectura de la automatización, herramientas y patrón de diseño

Este documento atiende tres observaciones de la profesora para la entrega final: que la arquitectura del proyecto de automatización (API y web) sea clara, que las herramientas sean complementarias y estén justificadas, y que el patrón de diseño se compare con otros. El pipeline se detalla en [`pipeline.md`](pipeline.md) y la gestión de casos en [`gestion-casos.md`](gestion-casos.md).

**En pocas líneas:** los criterios de aceptación se escriben en Gherkin y los ejecutan dos suites: API, en Python, y web, en TypeScript. Una tercera suite, de contrato, genera casos desde el OpenAPI de Qolqe. Las tres corren contra Qolqe sin modificarlo y entregan JUnit XML, que alimenta la trazabilidad, GitHub Pages y Kiwi TCMS.

| Tamaño actual (rama `entrega-final`) | API | Contrato | Web |
|---|---|---|---|
| Escenarios Gherkin | 276 en 10 `.feature` | — (caso CP-T04) | 58 en 4 `.feature` |
| Pruebas que ejecuta el runner | 766 (los esquemas se expanden) | 19 operaciones de `/openapi.json` | 71, por 3 repeticiones = 213 |
| Definiciones de pasos | 266 | — | 139 |
| Última corrida local completa (11-nov-2026, después de la revisión final) | 707 passed y 59 xfailed estrictos, iguales en 3 corridas | 1414 casos generados en verde (el número varía por la fase *stateful*) | 210 passed y 3 fallos esperados (CP-NW03, `@fail @DEF-18`), 0 inestables |

En total hay 335 casos: 334 escenarios más CP-T04, que es la corrida de contrato. Los conteos se comprueban con `pytest tests/api --collect-only -q`, `npx playwright test --list` y `python .github/scripts/trazabilidad.py --verificar`.

---

## 1. Arquitectura del proyecto de automatización

### 1.1 Capas

| Capa | Qué responde | Dónde está |
|---|---|---|
| 1. Requisitos | ¿Qué debe hacer Qolqe? | [`requisitos.md`](requisitos.md): HU-N-01..09 (núcleo) y HU-G4-01..10, con sus CA y reglas |
| 2. Especificación | ¿Con qué ejemplos se comprueba cada CA? | `features/*.feature` (API) y `features/web/*.feature` (web), en español (`# language: es`). Cada escenario lleva `@HU-…`, `@CA…`, `@CP-…` y, si aplica, `@DEF-…` y `@tecnico`. En la web, un defecto conocido lleva además `@fail`. El ID del caso va también al inicio del título. |
| 3. Pasos | ¿Qué código ejecuta cada frase? | API: `tests/api/conftest.py` y `tests/api/pasos_*.py` (pytest-bdd). Web: `tests/e2e/steps/*.steps.ts` (playwright-bdd). |
| 4. Acceso a Qolqe | ¿Cómo se habla con el sistema? | API: fixture `s`, que entrega el cliente `Sesiones` (httpx con el token de cada usuario y la última respuesta). Web: fixtures que entregan Page Objects y componentes (`tests/e2e/pages/`), que usan los localizadores de Playwright. Los datos web se preparan con `DatosPrueba`, que usa el cliente HTTP de Playwright. |
| 5. Sistema bajo prueba | — | `qolqe/` sin cambios, levantado con `QOLQE_MODO_PRUEBA=1` y una base SQLite propia por suite |

El contrato no pasa por Gherkin: Schemathesis lee `/openapi.json` y genera los casos. Su alcance y sus exclusiones están en `scripts/correr-contrato.sh`, `schemathesis.toml` y `scripts/contrato_hooks.py`.

```mermaid
flowchart LR
  REQ["docs/requisitos.md<br/>HU y CA"] --> ESP

  subgraph ESP["Especificación en Gherkin"]
    FA["features/*.feature<br/>API: 276 escenarios"]
    FW["features/web/*.feature<br/>web: 58 escenarios"]
  end

  subgraph SAPI["API - Python"]
    PB["pytest-bdd<br/>pasos"] --> CL["fixture s<br/>cliente Sesiones con httpx"]
  end

  subgraph SCON["Contrato - Python CLI"]
    ST["Schemathesis"]
  end

  subgraph SWEB["Web - TypeScript"]
    FX["fixtures.ts"] -. inyecta .-> PW["playwright-bdd<br/>pasos"]
    PW --> PO["Page Objects<br/>y componentes"]
  end

  subgraph SUT["Qolqe en modo prueba"]
    SOP["API de soporte<br/>/api/pruebas/*"]
    RES["API REST<br/>/api/*"]
    OAS["Contrato<br/>/openapi.json"]
    UI["Interfaz web"]
  end

  FA --> PB
  FW --> PW
  CL --> RES
  CL -. reinicio .-> SOP
  FX -. reinicio y datos .-> SOP
  PO --> UI
  ST --> OAS
  ST --> RES
```

### 1.2 Datos independientes en cada escenario

Todas las suites comparten la semilla de Qolqe (`qolqe/semilla.py`) y la API de soporte. Esa API solo existe en modo prueba (`qolqe/api/soporte_pruebas.py`). La automatización usa estas operaciones:

| Operación | Para qué | Quién la usa |
|---|---|---|
| `POST /api/pruebas/reiniciar` | Restaurar los datos semilla | Antes de cada escenario: fixture `s` (API) y fixture automática `datos` (web). Una vez al inicio: `correr-contrato.sh`. |
| `GET`, `PUT` y `DELETE /api/pruebas/reloj` | Ver, fijar o adelantar la hora, y volver a la real | Vencimientos, bloqueos y límites diarios. Las fixtures vuelven a la hora real antes y después de cada escenario. |
| `PUT /api/pruebas/saldo` | Fijar el saldo de un usuario | Pasos `Dado` que fijan un saldo: consulta, transferencias y cierre de cuenta |
| `GET /api/pruebas/notificaciones` | Leer los SMS simulados | CA que exigen enviar un SMS, o que no se envíe |

Reglas que se derivan:

- **Independencia (FIRST).** Ningún escenario depende de otro. Cada escenario web ingresa por la pantalla de login. La sesión no se reutiliza con `storageState` porque Qolqe la guarda en `sessionStorage`, que Playwright no persiste ([Playwright, Authentication](https://playwright.dev/docs/auth)).
- **Preparar por API, verificar por pantalla.** Lo que un escenario web necesita de antemano (contactos, solicitudes, transferencias, saldo, intentos fallidos) lo crea `DatosPrueba` por HTTP en milisegundos, no recorriendo otras pantallas. Es el uso que propone Playwright para su cliente de API ([API testing](https://playwright.dev/docs/api-testing)) y la recomendación de la clase 11 contra el entorno inestable.
- **Un solo worker en la web.** Las pruebas comparten una base que se reinicia, así que `playwright.config.ts` fija `workers: 1` y `fullyParallel: false`.
- **Bases separadas en CI.** Los jobs `api` y `contrato` corren en runners distintos, cada uno con su propia base (`datos/api.db` y `datos/contrato.db`). La web usa `.demo-data/e2e.db`.

### 1.3 Cómo corre cada suite

| | API funcional y técnica | Contrato | Web E2E |
|---|---|---|---|
| Comando local | `npm run test:api` (pytest con JUnit y HTML) | `./scripts/correr-contrato.sh` | `npm run test:web` o `npm run test:web:3x` (`bddgen` y luego `playwright test`) |
| Job en CI | `api`, después de `estatico` | `contrato`, en paralelo con `api` | `web`, solo si `api` y `contrato` están en verde |
| Cómo se levanta Qolqe en CI | Un paso del job con uvicorn | Un paso del job con uvicorn | `webServer` de Playwright lo levanta si no está corriendo (`reuseExistingServer: true`) |
| Cómo se descubren los casos | Cada `test_*.py` llama a `scenarios("<archivo>.feature")` | `--include-path-regex` con las operaciones del núcleo y G4: 20 coinciden y se excluye `DELETE /api/seguridad/sesiones` (HU-G6-10) | `bddgen` genera los `.spec.js` en `.features-gen/` desde `features/web/*.feature` |
| Defectos conocidos | `@DEF-xx` se convierte en `xfail(strict=True, raises=AssertionError)` con el hook `pytest_bdd_apply_tag` de `conftest.py`. Si el defecto se corrige, la prueba falla y avisa; un error que no es una aserción (servidor caído, paso roto) es un fallo, no el defecto. | Checks u operaciones desactivados con su motivo en `schemathesis.toml`; dos fallos descartados por valor en `contrato_hooks.py` (DEF-29 y un falso positivo) | `@fail @DEF-xx`: playwright-bdd lo traduce a `test.fail()`, que falla si la prueba pasa. Lo que el paso necesita para comparar es una precondición (`tests/e2e/precondicion.ts`): si no se cumple, el caso falla de verdad |
| Repetibilidad | Datos reiniciados por escenario; en la corrida local del 11-nov-2026 se compararon 3 corridas caso por caso y salieron iguales | `--seed 42 --max-examples 30` | `--repeat-each=3`; en CI, `retries: 1` y `failOnFlakyTests: true` ponen el run en rojo si una prueba alterna |
| Evidencia (`EVIDENCIA`) | `tests/api/evidencia.py` adjunta peticiones y respuestas, con el token enmascarado: de cada caso, o solo de fallos y xfail | Con `con-imagenes`, además `peticiones.har` | Con `con-imagenes`: captura, video y traza de cada prueba. Sin imágenes: captura y traza de los fallos, video en el reintento. |

### 1.4 Dónde quedan los resultados

| Resultado | Lo produce | Dónde queda |
|---|---|---|
| JUnit XML de cada suite (formato común) | pytest, Schemathesis, Playwright | `reportes/api/junit.xml`, `reportes/contrato/junit.xml`, `reportes/web/junit.xml` |
| HTML con el detalle | pytest-html, Schemathesis, reporte HTML de Playwright | `reportes/api/reporte.html`, `reportes/contrato/html/`, `reportes/web/html/` |
| Resumen en la página del run | `.github/scripts/resumen.py` en cada job; tabla del job `quality-gate`; matriz del job `reportes` | Resumen del run en GitHub Actions |
| Artefactos del run | `actions/upload-artifact` | `reportes-api`, `reportes-contrato`, `reportes-web` y `sitio`: 14 días, o 7 si son con imágenes. `trazabilidad`: 90 días. |
| Matriz HU → CA → CP → resultado, JUnit con un caso por CP, `run.json` y evidencias por CP | `.github/scripts/trazabilidad.py` y `casos.py` (job `reportes`) | Artefactos `sitio` y `trazabilidad` |
| Portada, reportes e historial de los últimos 30 runs | Job `publicar` (solo `main`) | GitHub Pages: `index.html`, `historial.html`, `historial.json` |
| Historial por caso, requisito y defecto | `scripts/kiwi_sincronizar.py` con `kiwitcms-junit.xml-plugin` | Kiwi TCMS (`herramientas/kiwi/`): un TestRun por run de GitHub ([`gestion-casos.md`](gestion-casos.md)) |

```mermaid
flowchart LR
  PB["pytest-bdd"] --> JA["reportes/api<br/>junit.xml y reporte.html"]
  ST["Schemathesis"] --> JC["reportes/contrato<br/>junit.xml y html"]
  PW["Playwright"] --> JW["reportes/web<br/>junit.xml y html"]
  ET["Etiquetas de features"] -.-> TR
  JA --> TR["trazabilidad.py<br/>matriz, junit-cp.xml y run.json"]
  JC --> TR
  JW --> TR
  TR --> PG["GitHub Pages<br/>portada e historial de 30 runs"]
  TR -- kiwi_sincronizar.py --> KW["Kiwi TCMS<br/>un TestRun por run"]
```

### 1.5 Árbol del código de automatización

Solo se listan los archivos versionados. Se omiten `qolqe/` (el sistema bajo prueba), `docs/` y `labs/`.

```
qolqe-wallet/
├── features/                                   # Especificación en Gherkin
│   ├── nucleo_registro_api.feature             # HU-N-01
│   ├── nucleo_sesion_api.feature               # HU-N-02 y 03
│   ├── nucleo_cuenta_api.feature               # HU-N-04 y 05
│   ├── nucleo_dinero_cierre_api.feature        # HU-N-06
│   ├── nucleo_dinero_qolqe_api.feature         # HU-N-07
│   ├── nucleo_dinero_interbancaria_api.feature # HU-N-08
│   ├── nucleo_dinero_comision_api.feature      # HU-N-09
│   ├── contactos_api.feature                   # HU-G4-01..05
│   ├── solicitudes_api.feature                 # HU-G4-06..10
│   ├── g4_tecnico_api.feature                  # Casos técnicos CP-T de G4
│   └── web/
│       ├── nucleo_acceso_web.feature           # HU-N-01..05
│       ├── nucleo_dinero_web.feature           # HU-N-06..09
│       ├── contactos_web.feature               # HU-G4-01..05
│       └── solicitudes_web.feature             # HU-G4-06..10
├── tests/
│   ├── api/                                    # Python: pytest + pytest-bdd + httpx
│   │   ├── test_contactos_api.py, test_solicitudes_api.py, test_g4_tecnico_api.py,
│   │   │   test_nucleo_acceso_api.py, test_nucleo_dinero_api.py   # scenarios("…feature")
│   │   ├── conftest.py                         # Fixture s (Sesiones), @DEF → xfail estricto, pasos comunes y de G4
│   │   ├── pasos_nucleo_acceso.py              # Pasos HU-N-01..05
│   │   ├── pasos_nucleo_dinero.py              # Pasos HU-N-06..09
│   │   ├── pasos_g4_extra.py                   # Pasos extra de G4, incluida la validación contra OpenAPI
│   │   └── evidencia.py                        # Peticiones y respuestas en reporte.html
│   ├── e2e/                                    # TypeScript: Playwright Test + playwright-bdd
│   │   ├── fixtures.ts                         # datos (automática), DatosPrueba, Page Objects, componentes,
│   │   │                                       #   otroNavegador y peticiones
│   │   ├── pages/
│   │   │   ├── componentes.ts                  # Aviso, DialogoConfirmacion, DialogoFormulario, ListaVacia, Navegacion
│   │   │   ├── PaginaQolqe.ts                  # Base de un nivel para las pantallas con menú
│   │   │   ├── LoginPage.ts, RegistroPage.ts   # Sin menú: no heredan de PaginaQolqe
│   │   │   └── InicioPage.ts, PerfilPage.ts, TransferirPage.ts, ContactosPage.ts, SolicitudesPage.ts
│   │   ├── steps/                              # comunes, nucleo_acceso, nucleo_dinero, contactos, solicitudes
│   │   └── tsconfig.json                       # Para tsc --noEmit (job estatico)
│   └── test_humo.py                            # Humo de la app con TestClient (fuera del pipeline)
├── scripts/
│   ├── correr-contrato.sh, contrato_hooks.py   # Contrato: alcance, token y filtros por valor
│   ├── kiwi_sincronizar.py                     # Runs de GitHub → TestRuns de Kiwi
│   └── preparar-demo.sh                        # Demo en vivo
├── .github/
│   ├── workflows/pruebas.yml                   # estatico, api, contrato, web, quality-gate, reportes,
│   │                                           #   gestion-casos, publicar
│   └── scripts/casos.py, trazabilidad.py, resumen.py   # Modelo de casos, matriz e historial, resumen del job
├── herramientas/kiwi/                          # docker-compose de Kiwi TCMS y su certificado local
├── playwright.config.ts, package.json          # Runner web, reportes y evidencia según EVIDENCIA
├── pytest.ini, schemathesis.toml, ruff.toml    # Runner de API, exclusiones del contrato, lint
└── requirements*.txt, constraints.txt          # Dependencias fijadas (FastAPI 0.117.1, ver DEF-07)
```

---

## 2. Herramientas y por qué son complementarias

**Criterio.** Cada herramienta responde una pregunta que las demás no responden. Una herramienta nueva solo entra si cubre un hueco. Donde hay solapamiento, es a propósito y con otro oráculo. Por ejemplo, la API prueba la regla que produce un error, y la web prueba que ese error le llega al usuario.

| Capa | Herramienta (versión fijada) | Qué cubre que las otras no | Alternativas consideradas y por qué no |
|---|---|---|---|
| Especificación | Gherkin en español, leído por pytest-bdd y por playwright-bdd | Un solo formato y las mismas etiquetas para API y web: el CA y el caso se leen igual en los dos niveles, y `trazabilidad.py` los une con los JUnit | **Karate:** su Gherkin trae los pasos ya implementados, pero su propio README marca *Readable Specification: No* y lo describe como un mini lenguaje de programación ([README, Cucumber vs Karate](https://github.com/karatelabs/karate/blob/v1.5.2.RC2/README.md#cucumber-vs-karate)). Los `.feature` dejarían de leerse como criterios de aceptación. |
| API funcional y técnica | pytest 8.4.2, pytest-bdd 9.0.0, httpx (0.28.1 instalado), pytest-html 4.2.0 | Reglas de negocio por CA: valores límite, particiones, estados, permisos, formato de error, 401 y 404. Además: concurrencia con hilos sincronizados (`threading.Barrier`), validación de respuestas puntuales contra el esquema OpenAPI (`jsonschema-rs`, fijado en `requirements-dev.txt`), defectos como xfail estricto y fixtures de pytest ([fixtures](https://docs.pytest.org/en/stable/explanation/fixtures.html)) | **Postman + Newman:** Postman indica que Newman ya no recibirá actualizaciones ni correcciones y pide migrar a Postman CLI ([Postman](https://learning.postman.com/docs/collections/using-newman-cli/command-line-integration-with-newman/)). Sus pruebas son JavaScript dentro de la colección, sin Gherkin compartido. **Bruno:** colecciones en texto versionable, con JS o un DSL propio (clase 10); tampoco ejecuta Gherkin. **REST Assured:** DSL de Java ([rest-assured.io](https://rest-assured.io/)); sumaría un tercer lenguaje y la JVM. **Robot + RequestsLibrary:** palabras clave, no `.feature` (clase 10). **Cliente HTTP de Playwright:** su documentación lo propone para probar la API, preparar estado y validar postcondiciones, y no trae validación de esquema ([API testing](https://playwright.dev/docs/api-testing)). Lo usamos para preparar datos web. Para la suite de API no aporta nada que falte en pytest y obligaría a reescribir 266 pasos. |
| Contrato | Schemathesis 4.32.7 (CLI) | Casos que nadie escribió, generados desde `/openapi.json` (OpenAPI 3.1.0) en cuatro fases: ejemplos, cobertura, fuzzing y secuencias con estado. Comprueba propiedades como "ninguna respuesta es 500" o "toda respuesta cumple su esquema". Así aparecieron DEF-05, DEF-06, DEF-08 y DEF-29. Su artículo reporta de 1.4 a 4.5 veces más defectos únicos que el segundo mejor fuzzer ([Hatfield-Dodds y Dygalo](https://arxiv.org/abs/2112.10328)). No conoce reglas de negocio: complementa a pytest-bdd, no lo reemplaza. | **Dredd:** repositorio archivado el 8 de noviembre de 2024 y soporte de OpenAPI 3 experimental ([GitHub](https://github.com/apiaryio/dredd)). **Pact:** contratos guiados por el consumidor. Su documentación dice que no sirve para la prueba funcional del proveedor ni para APIs cuyos consumidores no se identifican uno por uno ([Pact](https://docs.pact.io/getting_started/what_is_pact_good_for)). Además, no se puede tocar `qolqe/`. |
| Web E2E | Playwright Test 1.64.1, playwright-bdd 9.2.1, TypeScript 5.9.3 (Chromium) | Lo que solo se ve en pantalla (mensajes, máscaras, pestañas, estados de botones), recorridos críticos y que el error de la API llegue al usuario. Espera automática antes de cada acción; aserciones que reintentan; traza, captura y video; `repeatEach`, `retries` y `failOnFlakyTests` ([TestConfig](https://playwright.dev/docs/api/class-testconfig)); `webServer`; varios contextos aislados en una prueba (CP-NW18 cierra la cuenta y comprueba la sesión en "otro navegador") | **Selenium WebDriver:** la espera implícita vale 0 por defecto y su guía advierte no mezclar esperas implícitas y explícitas ([Waits](https://www.selenium.dev/documentation/webdriver/waits/)). No trae runner ni reporte. **Cypress:** solo JavaScript, corre dentro del navegador y no controla más de un navegador a la vez ([Trade-offs](https://docs.cypress.io/app/references/trade-offs)); CP-NW18 necesita dos sesiones. **Robot Framework + Browser:** corre sobre Playwright y también espera sola ([robotframework-browser.org](https://robotframework-browser.org/)), pero no ejecuta `.feature`. Lo usamos en el laboratorio S11 (`labs/s11-robot/`). **WebdriverIO:** usa WebDriver BiDi por defecto ([Protocols](https://webdriver.io/docs/automationProtocols)); es válido, pero no aporta nada que falte aquí. |
| Calidad del código de prueba | ruff 0.17.1, `tsc --noEmit`, `bddgen`, `pytest --collect-only`, `trazabilidad.py --verificar` (job `estatico`) | Detecta en segundos, sin servidor, lo que rompería todas las suites: paso sin definir, error de tipos, etiqueta `@CP` repetida o par `@HU @CA` inexistente. Playwright no revisa tipos y recomienda correr `tsc` aparte ([TypeScript](https://playwright.dev/docs/test-typescript)). | Sin alternativa relevante: son verificaciones baratas que no compiten con nada |
| Orquestación y quality gate | GitHub Actions (`.github/workflows/pruebas.yml`) | Ejecuta todo en cada push y PR. `api` y `web` son checks obligatorios de `main`, y el sitio se publica en Pages sin servidor propio. | **Jenkins:** exige mantener un servidor y agentes. **GitLab CI:** exige migrar el repositorio (clase 12). El detalle de cada job está en [`pipeline.md`](pipeline.md). |
| Evidencia de un run | JUnit XML (formato común), HTML de cada herramienta, resumen del job | JUnit es lo único que las tres suites escriben igual: lo leen la matriz, el resumen y Kiwi. El HTML da el detalle propio de cada nivel: peticiones en API, HAR en contrato, trazas en web. | **Allure Report:** tiene adaptadores para pytest y Playwright ([Allure](https://allurereport.org/docs/playwright/)). Agregaría un cuarto formato que repite lo que ya dan JUnit, la portada y Kiwi. |
| Trazabilidad entre ejecuciones | `trazabilidad.py` + `casos.py` (propios), historial en GitHub Pages | Lee nuestras etiquetas (`@HU`, `@CA`, `@CP`, `@DEF`, `@tecnico`) y los JUnit de las tres suites. Marca `flaky` cuando un caso alterna en sus repeticiones y guarda la grilla de los últimos 30 runs. | La matriz versionada de la Entrega 2 (`docs/trazabilidad.md`) muestra un solo run (#10). Los artefactos y runs de GitHub vencen, por defecto a los 90 días. |
| Gestión de casos | Kiwi TCMS CE 17.0 en Docker; `tcms-api` 15.0 y `kiwitcms-junit.xml-plugin` 15.0 | Casos, planes, un TestRun por run, versión (commit), requisito (HU), defecto (DEF) y adjuntos, sin límite de usuarios ni de historial | **Qase Free, TestRail, Xray/Zephyr y TestLink:** la comparación está en [`gestion-casos.md`](gestion-casos.md). Kiwi es el TCMS open source que presenta la semana 12. |

### ¿Por qué Python y TypeScript?

La respuesta corta: cada capa usa el runner que mejor la resuelve, en el lenguaje en que el curso lo enseña. El precio es real y lo pagamos a sabiendas.

- **Python para API y contrato.**
  - Qolqe está escrito en Python (FastAPI) y la clase 10 enseña pytest + httpx + pytest-bdd + Schemathesis.
  - pytest aporta fixtures, parametrización (con los Esquemas del escenario, 276 escenarios se convierten en 766 pruebas) y hooks: con `pytest_bdd_apply_tag` cada `@DEF` queda como xfail estricto, y `evidencia.py` registra las peticiones en el HTML.
  - Schemathesis es Python y se usa por línea de comandos, así que no depende del lenguaje de las pruebas.
- **TypeScript para la web.**
  - La clase 11 enseña Playwright + playwright-bdd en TypeScript.
  - El runner Playwright Test es de Node. En Python, Playwright se usa con el plugin de pytest, que documenta trazas, capturas, video y paralelo con xdist, pero no reintentos ni repeticiones ([Playwright para Python](https://playwright.dev/python/docs/test-runners)). Para tenerlos habría que sumar pytest-rerunfailures y pytest-repeat.
  - Playwright Test trae integrado lo que usamos: fixtures inyectadas por nombre, `repeatEach`, `retries` con `failOnFlakyTests`, `webServer`, `test.fail()` y reporte HTML con trazas.
- **Lo que comparten las capas son artefactos, no código.** Comparten el Gherkin con sus etiquetas, la API de soporte, la semilla y el formato JUnit. La frontera del lenguaje coincide con la frontera de la capa: ningún archivo de una suite importa algo de la otra.
- **Lo que cuesta.**
  - Dos gestores de dependencias (pip con `constraints.txt` y npm con `package-lock.json`), y el job `web` instala ambos porque necesita Python para levantar Qolqe.
  - Usuarios de prueba repetidos en `tests/api/conftest.py` y `tests/e2e/fixtures.ts`.
  - Dos sintaxis de pasos: `parsers.parse`/`parsers.re` y Cucumber Expressions.
- **¿Se podía usar un solo lenguaje?** Sí.
  - Todo en Python: pytest-bdd + pytest-playwright + pytest-rerunfailures + pytest-repeat. Es razonable para un proyecto que empieza de cero. No migramos porque habría que reescribir 139 pasos y 9 archivos de páginas, y perderíamos el reporte HTML del runner de Node, que integra trazas, capturas y video.
  - Todo en TypeScript: habría que reescribir 266 pasos de API y los hooks de pytest (xfail por etiqueta, evidencia de peticiones). Además, el cliente HTTP de Playwright no valida esquemas y habría que sumar una librería.

---

## 3. Patrón de diseño

### 3.1 Lo que implementamos

El patrón es **Page Object con componentes, una base de un solo nivel y fixtures**. Usa tres de los cuatro patrones de la clase 11: Page Object, Fixture y la idea del Test Data Builder (valores válidos por defecto, sin interfaz fluida). El cuarto, Screenplay, se compara en 3.3.

| Pieza | Archivo | Responsabilidad | Regla que se cumple |
|---|---|---|---|
| Escenario | `features/web/*.feature` | **Qué** hace y ve el usuario | Sin selectores ni detalles del HTML |
| Paso | `tests/e2e/steps/*.steps.ts` (139) | Traducir una frase a una llamada | Ningún localizador: `grep -rnE "getBy\|locator\(\|page\." tests/e2e/steps` no devuelve nada |
| Fixtures | `tests/e2e/fixtures.ts` | Entregar por nombre los Page Objects y componentes que pide cada paso. Preparar y limpiar. | `datos` es automática: reinicia base y reloj antes de cada escenario y restaura el reloj después |
| Datos de prueba | `DatosPrueba` en `fixtures.ts` | Crear por HTTP contactos, solicitudes, transferencias, saldo e intentos fallidos | Rellena con valores por defecto (`Alias <nombre>`, `Zeta 01`…); el escenario solo dice lo que importa |
| Page Object | `LoginPage`, `RegistroPage`, `InicioPage`, `PerfilPage`, `TransferirPage`, `ContactosPage`, `SolicitudesPage` | **Cómo** se usa cada pantalla: acciones (verbos) y verificaciones (`esperar…`) | Es el único lugar, junto con los componentes, que conoce el HTML |
| Base | `PaginaQolqe.ts` | Dar `nav` a las pantallas con menú | Un solo nivel. `LoginPage` y `RegistroPage` no heredan porque no tienen menú. Ninguna pantalla hereda de otra. |
| Componentes | `componentes.ts`: `Aviso`, `DialogoConfirmacion`, `DialogoFormulario`, `ListaVacia`, `Navegacion` | Un objeto por cada widget que `qolqe/web/static/app.js` genera igual en todas las pantallas: `toast()`, `confirmar()`, `dialogoFormulario()`, `itemVacio()` y el menú `nav-<ruta>` | Las pantallas los **componen** como campos. El diálogo propio de `/transferir` no es compartido y vive en `TransferirPage`. |
| Localizadores | Dentro de Page Objects y componentes | `getByTestId` con `testIdAttribute: 'data-testid'` | Sin clases de estilo ni `nth-child`. La posición solo se usa cuando es la regla ("el primer contacto es…"). |

Fixtures adicionales: `otroNavegador` abre un contexto aislado con su propio `sessionStorage`, para la segunda sesión de CP-NW18 y CP-NW27. `peticiones` anota las peticiones que salen del navegador con su cuerpo, para las reglas que solo existen en la interfaz: el doble clic que debe enviar una sola petición (CP-W30) o el ingreso que debe enviar el dispositivo recordado (CP-NW08). `DatosPrueba` revisa cada respuesta de la API de soporte: si el reinicio falla, el escenario no corre con los datos del anterior.

**En la API no hay Page Objects.** El equivalente es el cliente `Sesiones` (fixture `s`), que oculta la URL base, el login, el token de cada usuario y la paginación. La ruta y el cuerpo HTTP sí aparecen en los pasos, a propósito: en una prueba de API la petición es lo que se prueba.

### 3.2 Del escenario al Page Object (código real, extractos)

Escenario (`features/web/solicitudes_web.feature`, CP-W10):

```gherkin
  @HU-G4-01 @HU-G4-06 @HU-G4-07 @CA1 @HU-G4-08 @CA3 @CP-W10
  Escenario: CP-W10 Recorrido completo de una solicitud entre dos usuarios
    # …
    Cuando cierra sesión e ingresa como "Bruno"
    Y abre la pantalla de solicitudes
    Y acepta la solicitud "Devolución demo G4"
    Entonces la solicitud "Devolución demo G4" está "Aceptada"
```

Pasos: cada uno es una línea y recibe sus objetos por fixture (`tests/e2e/steps/solicitudes.steps.ts` y `comunes.steps.ts`):

```ts
When('acepta la solicitud {string}', async ({ solicitudes }, motivo: string) => solicitudes.aceptar(motivo));
// …
Then('la solicitud {string} está {string}', async ({ solicitudes }, motivo: string, estado: string) => solicitudes.esperarEstado(motivo, estado));

When('cierra sesión e ingresa como {string}', async ({ nav, login }, nombre: string) => {
  await nav.cerrarSesion();
  await login.ingresar(USUARIOS[nombre].celular, USUARIOS[nombre].pin);
});
```

Page Object, que compone un componente (`tests/e2e/pages/SolicitudesPage.ts`):

```ts
export class SolicitudesPage extends PaginaQolqe {
  private readonly formulario = new DialogoFormulario(this.page);
  private readonly confirmacion = new DialogoConfirmacion(this.page);

  private filas = () => this.page.getByTestId('solicitud');
  private fila = (motivo: string) => this.filas().filter({ has: this.page.getByTestId('solicitud-motivo').getByText(motivo, { exact: true }) });
  // …
  async esperarEstado(motivo: string, estado: string) {
    await expect(this.fila(motivo).getByTestId('solicitud-estado')).toHaveText(estado);
  }
  // …
  async pulsarAceptar(motivo: string) {
    await this.fila(motivo).getByTestId('boton-aceptar-solicitud').click();
  }

  async aceptar(motivo: string) {
    await this.pulsarAceptar(motivo);
    await this.confirmacion.esperarMensaje(motivo);
    await this.confirmacion.confirmar();
  }
```

Componente compartido (`tests/e2e/pages/componentes.ts`) y su registro como fixture (`tests/e2e/fixtures.ts`):

```ts
/** Diálogo "¿Seguro?" con Confirmar y Cancelar. */
export class DialogoConfirmacion {
  constructor(private readonly page: Page) {}

  private raiz = () => this.page.getByTestId('dialogo-confirmar');

  async confirmar() {
    await this.raiz().getByTestId('boton-confirmar-accion').click();
  }
  // …
}

// fixtures.ts
  datos: [async ({ request }, use) => {
    const datos = new DatosPrueba(request);
    await datos.reiniciar();
    await use(datos);
    await request.delete('/api/pruebas/reloj');
  }, { auto: true }],
  // …
  solicitudes: async ({ page }, use) => use(new SolicitudesPage(page)),
```

Si cambia el diálogo de confirmación de Qolqe, se corrige `DialogoConfirmacion` y nada más. Lo usan `ContactosPage.eliminar`, `SolicitudesPage.aceptar` y `cancelar`, y los pasos "cancela la confirmación" y "la confirmación dice".

```mermaid
flowchart LR
  E["Escenario<br/>QUÉ hace el usuario"] --> P["Paso<br/>una línea"]
  P --> PO["Page Object<br/>CÓMO se usa la pantalla"]
  PO --> C["Componentes<br/>aviso, diálogos, menú"]
  PO --> L["Localizadores<br/>data-testid"]
  C --> L
  F["Fixtures<br/>datos, páginas"] -. inyecta .-> P
  F -. prepara por API .-> Q["Qolqe<br/>/api/pruebas/* y /api/*"]
```

### 3.3 Comparación con otros patrones

**Qué propone cada uno**

| Patrón | Idea | Fuente |
|---|---|---|
| Sin patrón | Los pasos usan los localizadores directamente | Línea base de la clase 11 |
| Page Object clásico | Una clase por pantalla con sus localizadores y acciones; la prueba nunca toca el HTML | [Fowler (2013)](https://martinfowler.com/bliki/PageObject.html), [Selenium](https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/), [Playwright](https://playwright.dev/docs/pom) |
| **Page Object + componentes + fixtures (elegido)** | Lo anterior, más objetos para los fragmentos que se repiten y fixtures del runner que preparan datos e inyectan objetos | Fowler pide objetos "for the significant elements on a page", no solo por página. Selenium describe *page component objects* que se incluyen en los Page Objects. Ver [fixtures de Playwright](https://playwright.dev/docs/test-fixtures). |
| Page Factory | Campos anotados con `@FindBy`; `PageFactory.initElements` los convierte en proxies perezosos | [Selenium Java API](https://www.selenium.dev/selenium/docs/api/java/org/openqa/selenium/support/PageFactory.html) |
| Page Object fluido (encadenado) | Cada acción devuelve el Page Object siguiente para encadenar llamadas | Fowler: navegar "should return another page object"; [Fluent Interface](https://martinfowler.com/bliki/FluentInterface.html) |
| Screenplay | Actores con habilidades realizan tareas e interacciones y responden preguntas | [Smart, Marcano, Molak y Palmer (InfoQ, 2016)](https://www.infoq.com/articles/Beyond-Page-Objects-Test-Automation-Serenity-Screenplay), [Serenity/JS](https://serenity-js.org/handbook/design/screenplay-pattern/) |
| App Actions | La prueba llama a la lógica interna de la app, expuesta por ejemplo en `window`, en vez de preparar estado por la UI | [Bahmutov, Cypress (2019)](https://www.cypress.io/blog/stop-using-page-objects-and-start-using-app-actions) |
| Por palabras clave | La prueba es una secuencia de palabras clave reutilizables en tablas; el BDD se hace con prefijos Given/When/Then | [Robot Framework User Guide](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html), clase 11 |

**Evaluación con los criterios de la clase 11 para Qolqe** (58 escenarios web, 7 pantallas, 1 persona)

| Patrón | Tamaño de la suite | Cambios de la UI | Encaje con Gherkin y playwright-bdd | Lo que ya trae Playwright | Costo de adopción | Veredicto |
|---|---|---|---|---|---|---|
| Sin patrón | Solo para muy pocos escenarios | Un cambio toca todos los pasos que usan ese selector | Pasos con HTML adentro | — | Ninguno | No |
| Page Object clásico | Adecuado | Se corrige en un Page Object, pero el aviso, los diálogos y el menú quedarían repetidos en varias pantallas (el menú, en 5) | Bueno | Fixtures que entregan los Page Objects | Bajo | Insuficiente solo |
| **PO + componentes + fixtures** | **Adecuado** | **Un solo lugar: la pantalla o el componente** | **Pasos de una línea; un paso puede usar dos objetos** | **Usa fixtures, espera automática y aserciones con reintento** | **Bajo** | **Sí** |
| Page Factory | No aporta | Igual que Page Object | Igual que Page Object | Los localizadores de Playwright ya se resuelven en cada uso ("Every time a locator is used… an up-to-date DOM element is located", [Locators](https://playwright.dev/docs/locators)). No existe en Playwright. | Una capa sin beneficio | No |
| Fluido (encadenado) | Indiferente | Igual que Page Object | Cada paso es una función aparte que recibe sus objetos por fixture, así que la cadena se corta entre pasos. Con `async/await` cada eslabón necesita su propio `await`. | — | Bajo | No |
| Screenplay | Pensado para suites grandes; la clase 11 lo orienta a cientos de pruebas | Muy bueno: bajo acoplamiento | Con Cucumber, Serenity/JS corre los `.feature` con cucumber-js, no con Playwright Test ([Serenity/JS + Cucumber](https://serenity-js.org/handbook/test-runners/cucumber/)). Su integración con Playwright Test no menciona playwright-bdd ([Serenity/JS + Playwright Test](https://serenity-js.org/handbook/test-runners/playwright-test/)). | La espera y el registro de cada acción ya los da Playwright (traza) | Alto: actores, habilidades, tareas, interacciones y preguntas para 58 escenarios | No por ahora |
| App Actions | Solo resuelve la preparación | No modela la UI | — | — | Qolqe es multipágina y su estado vive en el servidor: no hay un modelo en el navegador al que llamar, y exponer uno exigiría modificar `qolqe/` | No. Tomamos su idea (no preparar por pantalla) con la API de soporte. |
| Por palabras clave (Robot + Browser) | Adecuado | Un solo lugar: el recurso con las palabras clave | Robot no ejecuta `.feature`: habría que traducir los 58 escenarios y dejar de compartir formato con la API | Browser corre sobre Playwright, pero con otro runner y otro reporte | Medio | No. Probado en `labs/s11-robot/`, con `.resource` como Page Objects. |

### 3.4 Justificación

Se aplican los cuatro criterios de la clase 11, cuya regla práctica es "empezar simple (Page Object + fixtures) y escalar solo cuando duela":

1. **Tamaño.** Son decenas de escenarios, no cientos, y los mantiene una persona. Eso orienta a Page Object. Screenplay agregaría actores, tareas y preguntas sin un problema que lo pida.
2. **Cambios de la UI.** Qolqe genera el aviso, los diálogos, la lista vacía y el menú desde las mismas funciones de `app.js`. Un componente por cada uno hace que un cambio se corrija en un solo archivo. Es lo que Fowler y Selenium llaman objetos de componente.
3. **BDD.** El Gherkin dice qué hace el usuario, el paso solo traduce y el Page Object dice cómo. Por eso los pasos no tienen localizadores.
4. **Lo que trae el framework.** Playwright ya espera, reintenta las aserciones y registra cada acción en la traza. Sus fixtures preparan, inyectan y limpian. No hace falta construir esa infraestructura con otro patrón.

### 3.5 Decisiones explícitas (y su costo)

- **Verificaciones dentro del Page Object.**
  - Fowler y Selenium prefieren que el Page Object no verifique. Fowler admite verificar invariantes de la página, y Selenium acepta una sola verificación: que la página cargó. El ejemplo oficial de Playwright sí pone un `expect` en un método del Page Object.
  - Usamos métodos `esperar…` porque las aserciones de Playwright esperan y reintentan sobre el localizador, y así los localizadores no salen del Page Object.
  - Regla: las acciones son verbos y las verificaciones empiezan con `esperar`. Ningún paso `Dado` o `Cuando` llama a un `esperar…`.
  - Una acción sí puede esperar su propio efecto para sincronizarse. Por ejemplo, `abrir()` espera a que la pantalla termine de cargar y `aceptar()` comprueba que el diálogo es el de esa solicitud.
- **Composición, no jerarquía.** Los autores de Screenplay critican las jerarquías de Page Objects que crecen y violan los principios de responsabilidad única y abierto/cerrado (InfoQ, 2016). Aquí la herencia tiene un solo nivel y solo aporta el menú; los diálogos se agregan como campos.
- **Sin pasos con decoradores de playwright-bdd.** Los pasos con decorador viven dentro de una clase y solo reciben los parámetros del paso ([decorators](https://vitalets.github.io/playwright-bdd/#/writing-steps/decorators)). Pasos como "cierra sesión e ingresa como" (`nav` y `login`) o "transfiere … al contacto" (`contactos` y `transferir`) usan dos objetos.
- **`data-testid` como contrato.**
  - Qolqe expone `data-testid` en sus controles. Playwright recomienda priorizar el rol y también los "explicit contracts" ([Locators](https://playwright.dev/docs/locators)), y la clase 11 los presenta como alternativa a los localizadores frágiles (posición, clases de estilo).
  - El rol, el texto y los atributos de accesibilidad se usan donde el significado visible es lo que se verifica: `aria-pressed` del favorito, `aria-selected` de la pestaña, el `main` sin el DNI completo y el importe exacto del movimiento.
- **Costos conocidos.**
  - Los usuarios de prueba están repetidos entre Python y TypeScript.
  - La regla "pasos sin localizadores" se revisa con `grep`, pero el pipeline no la hace cumplir.
  - En la API, la lógica de peticiones simultáneas está repetida en tres módulos de pasos. No se unificó para no alterar carreras que ya se validaron 200 de 200 veces; las 10 llevan la etiqueta `@concurrencia`. Los pasos de G4 siguen en `conftest.py` junto a la infraestructura.

### 3.6 Cuándo cambiaríamos de patrón

Pasaríamos a Screenplay en cualquiera de estos casos:

- la suite web supera unos 100 escenarios o la mantienen varios equipos;
- muchos recorridos combinan varios actores y canales (web, API, SMS) en un mismo escenario;
- agregar pruebas obliga a modificar seguido Page Objects existentes.

Hoy solo cuatro escenarios web tienen dos usuarios o dos sesiones. CP-W10 y CP-NW21 se resuelven cerrando sesión e ingresando con el otro usuario (`nav` + `login`), y CP-NW18 y CP-NW27 con la fixture `otroNavegador`.

### 3.7 El patrón del lado de la API

En la API no hay pantallas: el objeto que oculta los detalles es un cliente.

| Opción | Idea | Para Qolqe | Veredicto |
|---|---|---|---|
| **Cliente `Sesiones` + fixture `s` (elegido)** | Un objeto por escenario guarda el token de cada usuario, la última respuesta y lo que el escenario recuerda (ids, saldos). Los pasos piden la ruta y el cuerpo exactos | La petición es lo que se prueba: con la ruta y el cuerpo a la vista, un caso técnico (tipo inválido, `Content-Type`, 405) se escribe sin crear métodos nuevos. La fixture reinicia datos y reloj (FIRST) | Sí |
| Cliente por recurso (*Gateway* o *Service Object*) | Una clase por recurso (`ContactosApi.agregar(...)`) que encapsula el acceso al sistema externo ([Fowler, Gateway](https://martinfowler.com/articles/gateway-pattern.html)) | Útil para preparar datos (lo hace `DatosPrueba` en la web). En las pruebas de API escondería justo lo que se verifica, y cada caso técnico pediría un método o un parámetro más | Solo para preparar datos |
| Karate | DSL propio sobre Gherkin, con los pasos HTTP ya implementados | Su README marca *Readable Specification: No*; los `.feature` dejarían de leerse como criterios (sección 2) | No |
| Tavern | Plugin de pytest con pruebas en YAML ([Tavern](https://tavern.readthedocs.io/en/latest/)) | Corre en pytest, pero no lee Gherkin: los casos dejarían de compartir formato y etiquetas con la web | No |

---

## Fuentes

**Material del curso CS5383:** clase 10 (pruebas de API, herramientas y Schemathesis), clase 11 (herramientas web, los cuatro patrones, cómo elegir y localizadores) y semana 12 (CI/CD, quality gate y gestión de casos).

**Patrones**
- Fowler, M. (2013). PageObject. https://martinfowler.com/bliki/PageObject.html
- Fowler, M. (2005). FluentInterface. https://martinfowler.com/bliki/FluentInterface.html
- Selenium. Page object models. https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/
- Selenium. PageFactory (Java API). https://www.selenium.dev/selenium/docs/api/java/org/openqa/selenium/support/PageFactory.html
- Playwright. Page object models. https://playwright.dev/docs/pom
- Playwright. Fixtures. https://playwright.dev/docs/test-fixtures
- Playwright. Locators. https://playwright.dev/docs/locators
- Playwright. Authentication. https://playwright.dev/docs/auth
- Smart, J. F., Marcano, A., Molak, J. y Palmer, A. (2016). Beyond Page Objects. InfoQ. https://www.infoq.com/articles/Beyond-Page-Objects-Test-Automation-Serenity-Screenplay
- Serenity/JS. Screenplay Pattern. https://serenity-js.org/handbook/design/screenplay-pattern/
- Serenity/JS. Playwright Test. https://serenity-js.org/handbook/test-runners/playwright-test/
- Serenity/JS. Cucumber. https://serenity-js.org/handbook/test-runners/cucumber/
- Bahmutov, G. (2019). Stop using Page Objects and start using App Actions. https://www.cypress.io/blog/stop-using-page-objects-and-start-using-app-actions
- Robot Framework User Guide. https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html
- playwright-bdd. Decorators. https://vitalets.github.io/playwright-bdd/#/writing-steps/decorators
- Fowler, M. Gateway. https://martinfowler.com/articles/gateway-pattern.html
- Tavern. https://tavern.readthedocs.io/en/latest/

**Herramientas**
- pytest. Fixtures. https://docs.pytest.org/en/stable/explanation/fixtures.html
- pytest-bdd. https://pytest-bdd.readthedocs.io
- HTTPX. https://www.python-httpx.org
- Postman. Newman. https://learning.postman.com/docs/collections/using-newman-cli/command-line-integration-with-newman/
- Karate. README v1.5.2.RC2, Cucumber vs Karate. https://github.com/karatelabs/karate/blob/v1.5.2.RC2/README.md#cucumber-vs-karate
- REST Assured. https://rest-assured.io/
- Playwright. API testing. https://playwright.dev/docs/api-testing
- Schemathesis. https://schemathesis.readthedocs.io/en/stable/
- Hatfield-Dodds, Z. y Dygalo, D. (2022). Deriving Semantics-Aware Fuzzers from Web API Schemas. https://arxiv.org/abs/2112.10328
- Dredd. https://github.com/apiaryio/dredd
- Pact. What is Pact good for? https://docs.pact.io/getting_started/what_is_pact_good_for
- Selenium. Waiting strategies. https://www.selenium.dev/documentation/webdriver/waits/
- Cypress. Trade-offs. https://docs.cypress.io/app/references/trade-offs
- Robot Framework Browser. https://robotframework-browser.org/
- WebdriverIO. Automation Protocols. https://webdriver.io/docs/automationProtocols
- Playwright. TestConfig. https://playwright.dev/docs/api/class-testconfig
- Playwright. TypeScript. https://playwright.dev/docs/test-typescript
- Playwright para Python. Pytest plugin. https://playwright.dev/python/docs/test-runners
- Allure Report. Playwright. https://allurereport.org/docs/playwright/
- Kiwi TCMS. kiwitcms-junit.xml-plugin. https://pypi.org/project/kiwitcms-junit.xml-plugin/
