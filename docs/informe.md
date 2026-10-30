# Informe del proyecto – Johar Barzola

## 1. Datos generales y alcance

| Campo | Valor |
|---|---|
| Integrantes | Johar Jared Barzola Estrella |
| Módulo | G4 · Contactos y solicitudes de dinero |
| Herramienta de API | pytest + httpx + pytest-bdd; Schemathesis para el contrato |
| Herramienta web | Playwright (TypeScript) + playwright-bdd |
| Herramienta de rendimiento | Pendiente (Parte 3) |

**Alcance y nivel de prueba:** HU-G4-01 a HU-G4-10, con todos sus criterios. Cada regla se prueba en el nivel más bajo donde se pueda detectar; por la interfaz van los recorridos críticos y lo que solo se ve en la pantalla. Detalle criterio por criterio en [`alcance-y-casos.md`](alcance-y-casos.md).

## 2. Pruebas de API

**Herramienta.** pytest-bdd ejecuta escenarios en Gherkin con solicitudes HTTP reales (httpx) contra Qolqe levantado. Schemathesis genera casos desde `/openapi.json`.

| Enfoque | Ventajas | Limitaciones | Capacidades de IA |
|---|---|---|---|
| pytest-bdd: casos escritos a partir de los criterios | Gherkin legible, etiquetas para la trazabilidad, `xfail` estricto, JUnit XML | Requiere programar los pasos; pytest-bdd 9 no es compatible con pytest 9 | No las trae; con un asistente externo se generan pasos, que hay que revisar contra los requisitos |
| Schemathesis: casos generados desde el contrato | Cientos de solicitudes sin escribirlas; encontró DEF-05, DEF-06 y DEF-08 | No conoce las reglas de negocio; genera falsos positivos que hay que clasificar | Generación basada en propiedades, sin IA |

**Cómo ejecutar.** README, sección 6.

**Resultados y evidencia.** 41 escenarios, 68 ejecuciones: 64 passed y 4 xfailed (DEF-01 a DEF-04). Contrato: 9 operaciones, unos 700 casos generados, sin respuestas 500 ni incumplimientos de esquema. Reportes en https://joharjbe.github.io/qolqe-wallet/.

## 3. Pruebas web y CI/CD

**Herramienta y patrón.** Playwright con playwright-bdd y Page Object (`tests/e2e/pages/`). Se eligió sobre Robot Framework, usado en el laboratorio S11, porque trae de fábrica espera automática, `--repeat-each`, `test.fail`, `failOnFlakyTests` y reportes HTML y JUnit. Sin esperas fijas. Cada escenario empieza con datos reiniciados.

**Etapas del pipeline** (`.github/workflows/pruebas.yml`, en cada push a main y cada PR):

| Job | Depende de | Qué hace | Evidencia |
|---|---|---|---|
| `api` | — | pytest-bdd y Schemathesis | JUnit, HTML, resumen del job |
| `web` | `api` | Playwright, 3 veces seguidas | JUnit, HTML con trazas, resumen del job |
| `reportes` | `api`, `web` | Solo en main: matriz, portada y GitHub Pages | Sitio publicado |

Es **integración continua**: se integra y se prueba en cada cambio, pero no se publica la app. API y web van en un solo workflow porque la suite es pequeña.

**Quality gate.** Definido en [`defectos.md`](defectos.md). `api` y `web` son status checks obligatorios en la protección de `main`.

**Trazabilidad HU → casos → ejecución.** [`trazabilidad.md`](trazabilidad.md), generada por `.github/scripts/trazabilidad.py` desde las etiquetas de `features/` y el JUnit XML de cada run.

**Resultados.** [Run #7](https://github.com/Joharjbe/qolqe-wallet/actions/runs/41119242555): 19 escenarios web, 57 de 57 ejecuciones en verde; API 64 passed y 4 xfailed; contrato 10 de 10. El [PR #3](https://github.com/Joharjbe/qolqe-wallet/pull/3) muestra el quality gate bloqueando un cambio. No aparecieron defectos propios de la interfaz. DEF-03 no se alcanza por pantalla, porque la interfaz oculta el botón de aceptar en una solicitud vencida (CP-W15), pero sí por la API.

## 4. Pruebas de rendimiento

Pendiente (Parte 3).

## 5. Defectos encontrados

| ID | Título | Severidad | Estado |
|---|---|---|---|
| DEF-03 | Se puede aceptar una solicitud vencida y se transfiere el dinero | Crítica | Abierto |
| DEF-04 | Se puede transferir a un contacto con la cuenta cerrada | Crítica | Abierto |
| DEF-07 | La respuesta puede llegar antes de que los datos queden guardados | Alta | Abierto, mitigado en el pipeline |
| DEF-01 | El alias rechaza la letra ñ | Media | Abierto |
| DEF-02 | El alias duplicado no se detecta si tiene espacios alrededor | Media | Abierto |
| DEF-05 | El contrato OpenAPI no declara las reglas de los campos | Baja | Abierto |
| DEF-06 | `Allow` incompleto en la respuesta a `OPTIONS` | Baja | Abierto |
| DEF-08 | `favorito` acepta 0 y 1 aunque el contrato pide un booleano | Baja | Abierto |

Pasos y evidencia en [`defectos.md`](defectos.md).

## 6. Conclusiones y recomendaciones

Pendiente para la entrega final. Avance: corregir primero DEF-03 y DEF-04, porque mueven dinero, y DEF-07, porque invalida lo que la API confirma.
