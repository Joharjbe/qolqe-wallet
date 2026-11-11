# Gestión de casos: Kiwi TCMS

## Herramientas comparadas (revisión al 11-nov-2026)

| Herramienta | Costo | Lo que importa para nosotros | Fuente |
|---|---|---|---|
| **Kiwi TCMS CE 17.0** | Gratis y open source (Docker propio) | Sin límite de usuarios, runs ni retención. Plugin oficial `kiwitcms-junit.xml-plugin` que importa JUnit. Requisito, defectos, adjuntos y API completa. La imagen pública es solo amd64 (en Apple Silicon corre con Rosetta). | github.com/kiwitcms/Kiwi/releases · kiwitcms.readthedocs.io/en/latest/installing_docker.html · pypi.org/project/kiwitcms-junit.xml-plugin |
| Qase (plan Free) | Gratis | Historial de 30 días, 2 runs activos, 5 000 resultados por API al mes, sin trazabilidad de requisitos ni integraciones. Cuenta e internet. | qase.io/pricing |
| TestRail | Prueba de 30 días, luego de pago | Vence a mitad del curso | testrail.com/pricing |
| Xray / Zephyr (Jira) | Prueba de 30 días, luego de pago | Hay que montar Jira y la app | marketplace.atlassian.com |
| Testmo / Allure TestOps | De pago | — | testmo.com/pricing · qameta.io/pricing |
| TestLink | Gratis | Última versión de 2020, sin imagen oficial ni importador JUnit | github.com/TestLinkOpenSourceTRMS/testlink-code |
| Matriz en el repo (Pages) | Gratis | Ya existe; ahora con historial acumulado. GitHub borra artefactos y runs a los 90 días. | docs.github.com (retención de artefactos) |

## Por qué Kiwi

- Cuesta cero, no vence y no pide cuenta externa: el alumno crea su propio usuario local.
- Es la herramienta de la semana 12 y su plugin oficial lee JUnit, el formato que ya generan pytest-bdd, Playwright y Schemathesis. Las herramientas se complementan: las de prueba ejecutan, Kiwi registra y traza.
- Cubre el modelo de trazabilidad (ISTQB 1.4.4): caso, plan, ejecución, versión, requisito, defecto y evidencia.
- Resuelve que el pipeline corre muchas veces: cada run de GitHub es un TestRun propio y cada caso acumula todas sus ejecuciones (Telemetry → Status matrix, Execution trends, Test case health).

## De un run de GitHub a un TestRun de Kiwi

Kiwi corre en la máquina del equipo y los runners de GitHub no llegan a ella. Por eso la integración es **pull**: `scripts/kiwi_sincronizar.py` descarga con `gh` el artefacto `trazabilidad` de cada run (JUnit por CP, `run.json` y evidencias) y lo importa con el plugin oficial. Los runs #1 a #15 solo tienen `reportes-api` y `reportes-web`: el script reconstruye el mismo JUnit por CP con las etiquetas de los `.feature` de ese commit (`git archive`).

| Proyecto | Kiwi TCMS |
|---|---|
| CP-xx (escenario Gherkin) | Caso "CP-xx título" (si cambia el título se renombra, no se duplica) |
| HU-xx | Campo *requirement* y etiqueta |
| CAn | Etiqueta `HU-xx:CAn` |
| módulo, nivel, tipo | Etiquetas `modulo:G4`, `nivel:api`, `tipo:técnico` |
| Pasos Gherkin y archivo | *text*, *script* y *extra_link* (enlace a la línea del `.feature`) |
| passed / failed / flaky | PASSED / FAILED (flaky con comentario y etiqueta `inestable`) |
| xfailed con DEF-xx | WAIVED + enlace marcado como defecto a `docs/defectos.md` |
| sin ejecutar | IDLE |
| Run #N, intento k | TestRun "Qolqe · run #N.k · commit · evento rama · evidencia" con etiqueta `gh-run-<id>-<k>` |
| Commit / run | Version (commit corto) / Build `run-N` (`run-N.k` en un reintento) |
| Capturas y reporte de API | Adjuntos de la ejecución del CP y del TestRun |

Un run ya importado no se repite (se busca su etiqueta `gh-run-<id>-<k>`). Opciones: `--simular` (no se conecta a Kiwi), `--ultimos N`, `--run N ...`, `--crear-plan`, `--desde-carpeta DIR` (sin GitHub) e `--historial DIR` (escribe `historial.html` de los runs revisados).

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
8. Primera sincronización: `GH_TOKEN=$(gh auth token --user Joharjbe) KIWI_PLAN_ID=<id> .venv/bin/python scripts/kiwi_sincronizar.py --ultimos 20`.
9. Revisar en Kiwi: *Test runs*, un caso → pestaña de ejecuciones y *Telemetry → Status matrix*.

Después de cada run nuevo: `... kiwi_sincronizar.py --ultimos 1` (o `--ultimos 20`: lo ya importado se salta). Para ver antes qué se va a crear, el mismo comando con `--simular`.

## Demo en clase

1. Diez minutos antes: abrir Docker y `docker compose up -d` en `herramientas/kiwi`.
2. Lanzar el pipeline con `evidencia=con-imagenes` (`docs/pipeline.md`).
3. Mostrar en Pages la portada, la matriz y `historial.html`.
4. Al terminar el run: `kiwi_sincronizar.py --ultimos 1` y mostrar el TestRun con sus capturas, el historial de un CP y el Status matrix.

## Plan B

- La matriz y el historial en Pages, más el artefacto `trazabilidad` de cada run, funcionan sin ninguna cuenta y ya cubren la trazabilidad a lo largo de muchas ejecuciones.
- `kiwi_sincronizar.py --simular --ultimos 20 --historial /tmp/historial` muestra lo que se crearía en Kiwi y arma el historial local de los runs de GitHub, para sustentar el diseño aunque falte el paso de la cuenta.
- Si algún día hay un Kiwi accesible por internet, el job `gestion-casos` ya está listo: basta con los secretos `KIWI_URL`, `KIWI_USUARIO`, `KIWI_CLAVE` y la variable `KIWI_PLAN_ID`.
- Alternativa en la nube: Qase Free con `qasectl testops result upload --format junit` sobre el mismo `junit-cp.xml` (historial de 30 días y cuota mensual).

## Estado verificado (11-nov-2026)

- `docker compose up -d`: `qolqe_kiwi_db` y `qolqe_kiwi_web` en estado *healthy*; https://localhost:8443 responde 302 a `/init-db/` (falta el `initial_setup` del alumno) y el certificado de `localhost.crt` se verifica con curl y con Python. Imágenes fijadas por digest (Kiwi 17.0).
- `kiwi_sincronizar.py --simular --ultimos 20` sobre `Joharjbe/qolqe-wallet`: 15 runs reconstruidos desde `reportes-api`/`reportes-web` con las etiquetas de su commit, 61 casos cada uno; detecta los runs fallidos (#1, #2, #8, #13) y el CP-W10 inestable del run #13.
- La importación real no se probó contra Kiwi porque necesita el usuario del alumno; la parte de Kiwi se ejercitó con un RPC simulado que valida los métodos de la API de Kiwi 17.
