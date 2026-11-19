# Gestión de casos: Kiwi TCMS

## Herramientas comparadas (revisión al 11-nov-2026; QMetry, al 18-nov-2026)

| Herramienta | Costo | Lo que importa para nosotros | Fuente |
|---|---|---|---|
| **Kiwi TCMS CE 17.0** | Gratis y open source (Docker propio) | Sin límite de usuarios, runs ni retención. Plugin oficial `kiwitcms-junit.xml-plugin` que importa JUnit. Requisito, defectos, adjuntos y API completa. La imagen pública es solo amd64 (en Apple Silicon corre con Rosetta). | https://github.com/kiwitcms/Kiwi/releases · https://kiwitcms.readthedocs.io/en/latest/installing_docker.html · https://pypi.org/project/kiwitcms-junit.xml-plugin/ |
| Qase (plan Free) | Gratis | Historial de 30 días, 2 runs activos, 5 000 resultados por API al mes, sin trazabilidad de requisitos ni integraciones. Cuenta e internet. | https://qase.io/pricing |
| TestRail | Prueba de 30 días, luego de pago | Vence a mitad del curso | https://www.testrail.com/pricing/ |
| Xray / Zephyr (Jira) | Prueba de 30 días, luego de pago | Hay que montar Jira y la app | https://marketplace.atlassian.com/ |
| QMetry Test Management (SmartBear) | Prueba de 14 días, luego de pago (la página no publica precios) | Integrada con Jira: habría que montar Jira, como con Xray y Zephyr. Trae IA: generación de casos desde historias de usuario y detección de defectos y de pruebas inestables. La clase 7 la nombra entre las herramientas de gestión | https://smartbear.com/product/qmetry-test-management/ (adonde redirige https://www.qmetry.com/pricing) |
| Testmo / Allure TestOps | De pago | — | https://www.testmo.com/pricing/ · https://qameta.io/pricing |
| TestLink | Gratis | Última versión de 2020, sin imagen oficial ni importador JUnit | https://github.com/TestLinkOpenSourceTRMS/testlink-code |
| Matriz en el repo (Pages) | Gratis | Ya existe; ahora con historial acumulado. GitHub borra artefactos y runs a los 90 días. | https://docs.github.com/en/actions/how-tos/manage-workflow-runs/remove-workflow-artifacts |

## Por qué Kiwi

- Cuesta cero, no vence y no pide cuenta externa: el alumno crea su propio usuario local.
- Es la herramienta de la semana 12 y su plugin oficial lee JUnit, el formato que ya generan pytest-bdd, Playwright y Schemathesis. Las herramientas se complementan: las de prueba ejecutan, Kiwi registra y traza.
- Cubre el modelo de trazabilidad (ISTQB CTFL v4.0.1, 1.4.4, https://www.istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/): caso, plan, ejecución, versión, requisito, defecto y evidencia.
- Resuelve que el pipeline corre muchas veces: cada run de GitHub es un TestRun propio y cada caso acumula todas sus ejecuciones (Telemetry → Testing → Matrix, Execution trends, Test case health).

La clase 7 lo dice así: «Ninguna herramienta arregla un proceso mal definido». Por eso el proceso se definió antes que la herramienta: cada escenario lleva `@HU`, `@CA` y `@CP`, y `trazabilidad.py --verificar` lo comprueba en cada run, en el job `estatico`. Kiwi recibe ese resultado; no lo define.

### Los siete criterios de la clase 7, aplicados

La clase 7 propone siete criterios para elegir una herramienta de gestión de pruebas (diap. 31). Esta tabla los aplica con los datos de la comparación de arriba.

| Criterio (clase 7) | Lo que necesita este proyecto | Kiwi TCMS 17.0 | Qué alternativa queda fuera por este criterio |
|---|---|---|---|
| 1. Integración con incidencias y requisitos | Importar el JUnit del pipeline y enlazar cada caso con su HU y su `DEF` | Plugin oficial `kiwitcms-junit.xml-plugin`; requisito y enlace de defecto por caso (tabla de abajo) | TestLink: sin importador JUnit. Qase Free: sin integraciones |
| 2. Trazabilidad y reportes | HU ↔ CP ↔ ejecución ↔ `DEF` | Requisito, defecto, adjuntos y *Telemetry* (Matrix, Execution trends, Test case health) | Qase Free: sin trazabilidad de requisitos |
| 3. Escala | Muchos runs, con un historial que no venza | Sin límite de usuarios, runs ni retención | Qase Free: historial de 30 días y 2 runs activos. Los artefactos de GitHub: 90 días |
| 4. Automatización y BDD | Casos que salen de escenarios Gherkin ya automatizados | Los pasos Gherkin quedan en el caso (*text* y *script*); importa el JUnit de pytest-bdd, Playwright y Schemathesis | — (ninguna quedó fuera solo por esto) |
| 5. Costo total: licencias, alojamiento, adopción | Gratis hasta el final del curso | Gratis y open source; se aloja en Docker propio | TestRail, Xray y Zephyr: prueba de 30 días; QMetry: prueba de 14 días; Testmo y Allure TestOps: de pago. Xray, Zephyr y QMetry suman montar Jira |
| 6. Gobierno y auditoría | Sin cuenta externa; los datos quedan con el alumno | Corre en la máquina del alumno; el usuario es local | Qase: cuenta e internet |
| 7. IA integrada | No se necesita: la capacidad de IA del proyecto va aparte ([`capacidad-ia.md`](capacidad-ia.md)) | No llama a ningún modelo: su entorno no tiene paquetes de IA (`pip list` en `qolqe_kiwi_web`, [`informe.md`](informe.md) §3) | No descarta a nadie. La tienen Zephyr («Zephyr Agent for Rovo», nombrado en la clase 7, diap. 32) y QMetry (casos generados desde historias de usuario y detección de pruebas inestables, según su página) |

## De un run de GitHub a un TestRun de Kiwi

Kiwi corre en la máquina del alumno y los runners de GitHub no llegan a ella. Por eso la integración es **pull**: `scripts/kiwi_sincronizar.py` descarga con `gh` el artefacto `trazabilidad` de cada run de `main` (la misma población que el historial de Pages; `--rama ""` incluye también los PR, con la etiqueta `evento:pull_request`) (JUnit por CP, `run.json` y evidencias) y lo importa con el plugin oficial. Los runs #1 a #15 solo tienen `reportes-api` y `reportes-web`: el script reconstruye el mismo JUnit por CP con las etiquetas de los `.feature` de ese commit (`git archive`).

| Proyecto | Kiwi TCMS |
|---|---|
| CP-xx (escenario Gherkin) | Caso "CP-xx título" (si cambia el título se renombra, no se duplica) |
| HU-xx | Campo *requirement* y etiqueta |
| CAn | Etiqueta `HU-xx:CAn` |
| módulo, nivel, tipo | Etiquetas `modulo:G4`, `nivel:api`, `tipo:técnico` (CP-T04: `modulo:núcleo y G4`) |
| Pasos Gherkin y archivo | *text*, *script* y *extra_link* (enlace a la línea del `.feature`) |
| passed / failed / flaky | PASSED / FAILED (flaky con comentario y etiqueta `inestable`) |
| xfailed con DEF-xx | WAIVED + enlace marcado como defecto a `docs/defectos.md` |
| sin ejecutar | IDLE |
| Run #N, intento k | TestRun "Qolqe · run #N.k · commit · evento rama · evidencia" con etiquetas `gh-run-<id>-<k>`, `commit:<sha7>`, `evento:…`, `rama:…`, `evidencia:…` y `conclusion:…` |
| Commit / run | Build `run-N` (`run-N.k` en un reintento) dentro de la versión del plan (`base`): Kiwi 17 solo acepta en un TestRun builds de la versión de su plan. El commit queda en el resumen, en las notas y en la etiqueta `commit:<sha7>` |
| Capturas | Adjuntos de la ejecución del CP (PNG). Un adjunto rechazado se avisa y no corta la importación |
| Reporte HTML de API | No se sube: Kiwi rechaza archivos con `<html>` o `<script>`. Las notas del TestRun enlazan el run, sus artefactos y los reportes de Pages |

Un run ya importado no se repite (se busca su etiqueta `gh-run-<id>-<k>`, que se agrega al final). Mientras se importa, el TestRun lleva `incompleto:gh-run-<id>-<k>`: si la importación se corta, la siguiente sincronización retoma ese mismo TestRun. Opciones: `--rama` (por defecto `main`), `--simular` (no se conecta a Kiwi), `--ultimos N`, `--run N ...`, `--crear-plan`, `--desde-carpeta DIR` (sin GitHub) e `--historial DIR` (escribe `historial.html` de los runs revisados).

## Pasos del alumno (una vez, unos 30 minutos)

1. Abrir Docker Desktop y comprobar que `docker info` responde. En *Settings → General* debe estar activa la emulación con Rosetta.
2. `cd herramientas/kiwi && ./generar-certificado.sh && docker compose up -d`. La primera vez descarga las imágenes; los contenedores son `qolqe_kiwi_web` y `qolqe_kiwi_db`, con volúmenes persistentes.
3. `docker exec -it qolqe_kiwi_web /Kiwi/manage.py initial_setup`: crea las tablas y **tu propio superusuario** (usuario, correo y clave los eliges tú). Como dominio, `localhost:8443`.
4. Abrir https://localhost:8443 e iniciar sesión. Para que el navegador confíe, importar `herramientas/kiwi/ssl/localhost.crt` en Llavero (o aceptar la advertencia).
5. Crear `~/.tcms.conf` y protegerlo con `chmod 600 ~/.tcms.conf`:
   ```ini
   [tcms]
   url = https://localhost:8443/xml-rpc/
   username = <tu usuario>
   password = <tu clave>
   ```
6. `.venv/bin/pip install -r requirements-gestion.txt`
7. `.venv/bin/python scripts/kiwi_sincronizar.py --crear-plan` y anotar el id que imprime (o crear en la web el producto `Qolqe Wallet`, la versión `base` y el plan).
8. Primera sincronización: `GH_TOKEN=$(gh auth token --user Joharjbe) KIWI_PLAN_ID=<id> .venv/bin/python scripts/kiwi_sincronizar.py --ultimos 20`. Con varias cuentas en `gh`, `--user Joharjbe` elige la del repositorio de entrega.
9. Revisar en Kiwi: *Test runs*, un caso → pestaña de ejecuciones y *Telemetry → Testing → Matrix*.

Después de cada run nuevo: `... kiwi_sincronizar.py --ultimos 1` (o `--ultimos 20`: lo ya importado se salta). Para ver antes qué se va a crear, el mismo comando con `--simular`.

## Demo en clase

Lo que se proyecta ya está cargado antes de clase. El orden del día, con sus minutos, está en `docs/exposicion/hoja-demo.md`. El pipeline completo tardó 9 min 44 s en el run #20 y 13 min 38 s en el intento 1 del run #24, con la web repetida 3 veces (`--repeat-each=3`): si la demo esperara un run en vivo, la gestión de casos quedaría colgada de que termine a tiempo. Por eso hay dos carriles, y solo el primero es obligatorio.

**Carril A: lo precargado. Es lo que se muestra.**

1. En casa, con red: `./scripts/preparar-demo.sh`. Instala dependencias (`pip install`, `npm ci`, `playwright install chromium`), levanta Qolqe en el puerto 8000, arranca Kiwi si Docker está abierto y abre las pestañas de Actions, Pages, `historial.html`, el reporte web, los PR, Kiwi y Qolqe. Kiwi ya debe tener importados los runs de `main` (pasos 8 y 9).
2. Diez minutos antes: abrir Docker, `docker compose up -d` en `herramientas/kiwi` y comprobar que https://localhost:8443 abre con la sesión iniciada.
3. Pages: la portada, la matriz y `historial.html` (grilla CP × runs, estabilidad e intento de cada run).
4. Kiwi, como en D3 de `docs/exposicion/guion.md`: *Test runs*; el TestRun del run #18 (`con-imagenes`), con sus capturas como adjuntos y el enlace DEF de cada caso WAIVED, y dentro un caso con su pestaña de ejecuciones. *Telemetry → Testing → Matrix* no entra en la demo: queda para las preguntas.

**Carril B: opcional y fuera del orden del día.**

1. Durante la demo no se lanza: un run lanzado desde el minuto 9:00 terminaría después del 15:00, cuando la demo ya acabó y Kiwi ya está detenido (se detiene en el minuto 12:10, antes de k6; `hoja-demo.md`). Solo va después de k6, si en las preguntas la profesora lo pide, o fuera de la exposición: `docker start qolqe_kiwi_db qolqe_kiwi_web` y `gh workflow run pruebas.yml -R Joharjbe/qolqe-wallet --ref main -f evidencia=con-imagenes`. Va con `con-imagenes` para que el sitio que lo reemplace siga teniendo captura, video y traza de cada prueba: Pages guarda una sola versión del sitio (`docs/pipeline.md`), la del último run de `main`, y los push a `main` van sin imágenes.
2. Al terminar el run: `kiwi_sincronizar.py --ultimos 1` y mostrar el TestRun nuevo junto a los anteriores.

Kiwi comparte el CPU de la VM de Docker: se detiene siempre antes de k6, con la línea «Antes de k6» de `docs/exposicion/hoja-demo.md`. Para verlo en las preguntas o después de clase: `docker start qolqe_kiwi_db qolqe_kiwi_web`.

## Plan B

- La matriz y el historial en Pages, más el artefacto `trazabilidad` de cada run, funcionan sin ninguna cuenta y ya cubren la trazabilidad a lo largo de muchas ejecuciones.
- `kiwi_sincronizar.py --simular --ultimos 20 --historial /tmp/historial` muestra lo que se crearía en Kiwi y arma el historial local de los runs de GitHub, para sustentar el diseño aunque falte el paso de la cuenta.
- Si algún día hay un Kiwi accesible por internet, el job `gestion-casos` ya está listo: basta con los secretos `KIWI_URL`, `KIWI_USUARIO`, `KIWI_CLAVE` y la variable `KIWI_PLAN_ID`.
- Alternativa en la nube: Qase Free con `qasectl testops result upload --format junit` sobre el mismo `junit-cp.xml` (historial de 30 días y cuota mensual).

## Por qué escala a muchas ejecuciones

- Un run produce unas 1000 ejecuciones (766 de API, 213 web y las operaciones del contrato), que se reducen a 335 filas: una por CP, con su estado y el conteo de sus ejecuciones (`junit-cp.xml`).
- `historial.json` guarda hasta los últimos 30 runs; `historial.html` dibuja como máximo 15 × 335 celdas (los últimos 15 runs) y cada intento es su propia columna.
- Kiwi no tiene límite: cada run es un TestRun y cada CP acumula todas sus ejecuciones, también después de que GitHub borre los artefactos a los 90 días.
- Los ID de caso nunca se reutilizan (los retirados están en `alcance-y-casos.md`), así que la historia de un CP no mezcla dos casos.

## Estado verificado

- **(11-nov-2026)** `docker compose up -d`: `qolqe_kiwi_db` y `qolqe_kiwi_web` en estado *healthy*; https://localhost:8443 responde 302 a `/init-db/` (falta el `initial_setup` del alumno) y el certificado de `localhost.crt` se verifica con curl y con Python. Imágenes fijadas por digest (Kiwi 17.0).
- **(11-nov-2026)** `kiwi_sincronizar.py --simular --ultimos 20` sobre `Joharjbe/qolqe-wallet`: 15 runs reconstruidos desde `reportes-api`/`reportes-web` con las etiquetas de su commit, 61 casos cada uno; detecta los runs fallidos (#1, #2, #8, #13) y el CP-W10 inestable del run #13. (Esa corrida es anterior a `--rama main`; con el valor por defecto, los runs de PR quedan fuera.)
- **(11-nov-2026) Importación de prueba contra Kiwi 17.0.** En contenedores desechables de la misma imagen (MariaDB y Kiwi, con `migrate` y un superusuario de prueba, borrados después): `--crear-plan` creó el plan; `--desde-carpeta` importó un run, con el build en la versión del plan; una segunda sincronización del mismo run se saltó, y una importación cortada a mitad se retomó en el mismo TestRun, sin duplicarlo. Sus conteos no se citan: ese run es anterior a CP-NA157 a NA160, no coincide con ningún run de GitHub (del #16 en adelante todos traen 335 casos) y sus datos se borraron con los contenedores.
- **(17-nov-2026) Simulación con el run #18**, el que tiene captura, video y traza de cada prueba web: `GH_TOKEN=$(gh auth token --user Joharjbe) .venv/bin/python scripts/kiwi_sincronizar.py --simular --run 18` (no se conecta a Kiwi). Crearía el TestRun "Qolqe · run #18.1 · 5fbe969 · workflow_dispatch main · evidencia: con-imagenes" con 335 ejecuciones (295 PASSED y 40 WAIVED), 40 enlaces de defecto (uno por cada caso WAIVED, hacia 25 DEF distintos) y 219 capturas PNG para adjuntar. Los 335/295/40 son los mismos totales del `run.json` de ese run.
- **(17-nov-2026)** `qolqe_kiwi_web` y `qolqe_kiwi_db` arriba y en estado *healthy*; https://localhost:8443 ya responde 302 a `/accounts/login/` en vez de `/init-db/`, porque la base está migrada. En ese momento faltaba el usuario del alumno; se creó ese mismo día (entrada siguiente).
- **(17-nov-2026) Primera importación real, en el Kiwi del alumno.** Usuario `johar` creado con `createsuperuser` (la clave queda solo en `~/.tcms.conf`), `--crear-plan` → plan 1 («Qolqe · Pruebas automatizadas (entrega final)») y `GH_TOKEN=$(gh auth token --user Joharjbe) KIWI_PLAN_ID=1 .venv/bin/python scripts/kiwi_sincronizar.py --ultimos 20`. Salida: 9 TestRuns. #5.1, #7.1, #10.1, #12.1 y #15.1 → TestRuns 1 a 5, con 61 casos cada uno (57 PASSED y 4 WAIVED, reconstruidos de `reportes-api` y `reportes-web`, sin adjuntos); #17.1, #18.1, #20.1 y #24.1 → TestRuns 6 a 9, con 335 casos cada uno (295 PASSED y 40 WAIVED, 40 enlaces de defecto hacia 25 DEF distintos). El TestRun 7 (run #18, `con-imagenes`) recibió 216 de las 219 capturas: Kiwi rechazó `CP-NW25_r3.png`, `_r8` y `_r13` con «File contains forbidden tag: <rt>», un falso positivo de su filtro de subida sobre los bytes del PNG. El plan tiene 338 casos: los 335 de hoy más CP-A38, CP-T01 y CP-T03, que solo existen en los runs viejos.
- **(17-nov-2026) Segunda sincronización, después del *re-run* del #24.** Los 9 runs ya importados se saltan (etiqueta `gh-run-<id>-<intento>`) y el intento 2 del #24 entra como TestRun 10 (335 casos). Así el mismo commit `1025a78` tiene dos TestRuns, uno por intento. Las descargas de los 10 runs quedan en `reportes/kiwi/runs/`, que git ignora. La copia para el plan sin red, `~/kiwi-runs` (fuera del repositorio), se hizo antes del *re-run*: tiene los 9 runs de la primera importación, sin el #24.2.

## Evidencia de la primera importación real

Capturas en `docs/img/`, tomadas el 17-nov-2026: la lista de TestRuns, el TestRun del run #18, un CP con sus ejecuciones, la matriz de ejecuciones (*Telemetry → Testing → Matrix*) y `historial.html` de Pages con 5 columnas (#17, #18 `con-imagenes`, #20, #24.1 y #24.2, el *re-run*).

| Captura | Qué muestra |
|---|---|
| [`kiwi-testruns.png`](img/kiwi-testruns.png) | Los TestRuns del plan 1, uno por run de `main`, con su commit, evento y modo de evidencia en el resumen y las etiquetas |
| [`kiwi-testrun-18.png`](img/kiwi-testrun-18.png) | El TestRun 7 (run #18, `con-imagenes`): 295 PASSED, 40 WAIVED, 335 en total, con el enlace al run de GitHub y a Pages en las notas |
| [`kiwi-caso-ejecuciones.png`](img/kiwi-caso-ejecuciones.png) | CP-W10 (TC-52) con sus pasos Gherkin y una ejecución por TestRun |
| [`kiwi-status-matrix.png`](img/kiwi-status-matrix.png) | La matriz caso × TestRun de los 10 TestRuns |
| [`pages-historial.png`](img/pages-historial.png) | `historial.html` de Pages con las 5 columnas, incluido el intento 2 del #24 |
