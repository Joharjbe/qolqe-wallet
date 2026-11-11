# Gestión de casos: Kiwi TCMS

## Herramientas comparadas (revisión al 11-nov-2026)

| Herramienta | Costo | Lo que importa para nosotros | Fuente |
|---|---|---|---|
| **Kiwi TCMS CE 17.0** | Gratis y open source (Docker propio) | Sin límite de usuarios, runs ni retención. Plugin oficial `kiwitcms-junit.xml-plugin` que importa JUnit. Requisito, defectos, adjuntos y API completa. La imagen pública es solo amd64 (en Apple Silicon corre con Rosetta). | https://github.com/kiwitcms/Kiwi/releases · https://kiwitcms.readthedocs.io/en/latest/installing_docker.html · https://pypi.org/project/kiwitcms-junit.xml-plugin/ |
| Qase (plan Free) | Gratis | Historial de 30 días, 2 runs activos, 5 000 resultados por API al mes, sin trazabilidad de requisitos ni integraciones. Cuenta e internet. | https://qase.io/pricing |
| TestRail | Prueba de 30 días, luego de pago | Vence a mitad del curso | https://www.testrail.com/pricing/ |
| Xray / Zephyr (Jira) | Prueba de 30 días, luego de pago | Hay que montar Jira y la app | https://marketplace.atlassian.com/ |
| Testmo / Allure TestOps | De pago | — | https://www.testmo.com/pricing/ · https://qameta.io/pricing |
| TestLink | Gratis | Última versión de 2020, sin imagen oficial ni importador JUnit | https://github.com/TestLinkOpenSourceTRMS/testlink-code |
| Matriz en el repo (Pages) | Gratis | Ya existe; ahora con historial acumulado. GitHub borra artefactos y runs a los 90 días. | https://docs.github.com/en/actions/how-tos/manage-workflow-runs/remove-workflow-artifacts |

## Por qué Kiwi

- Cuesta cero, no vence y no pide cuenta externa: el alumno crea su propio usuario local.
- Es la herramienta de la semana 12 y su plugin oficial lee JUnit, el formato que ya generan pytest-bdd, Playwright y Schemathesis. Las herramientas se complementan: las de prueba ejecutan, Kiwi registra y traza.
- Cubre el modelo de trazabilidad (ISTQB CTFL v4.0.1, 1.4.4, https://www.istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/): caso, plan, ejecución, versión, requisito, defecto y evidencia.
- Resuelve que el pipeline corre muchas veces: cada run de GitHub es un TestRun propio y cada caso acumula todas sus ejecuciones (Telemetry → Status matrix, Execution trends, Test case health).

## De un run de GitHub a un TestRun de Kiwi

Kiwi corre en la máquina del equipo y los runners de GitHub no llegan a ella. Por eso la integración es **pull**: `scripts/kiwi_sincronizar.py` descarga con `gh` el artefacto `trazabilidad` de cada run de `main` (la misma población que el historial de Pages; `--rama ""` incluye también los PR, con la etiqueta `evento:pull_request`) (JUnit por CP, `run.json` y evidencias) y lo importa con el plugin oficial. Los runs #1 a #15 solo tienen `reportes-api` y `reportes-web`: el script reconstruye el mismo JUnit por CP con las etiquetas de los `.feature` de ese commit (`git archive`).

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

## Por qué escala a muchas ejecuciones

- Un run produce unas 1000 ejecuciones (766 de API, 213 web y las operaciones del contrato), que se reducen a 335 filas: una por CP, con su estado y el conteo de sus ejecuciones (`junit-cp.xml`).
- Pages guarda los últimos 30 runs (30 × 335 celdas en `historial.html`) y cada intento es su propia columna.
- Kiwi no tiene límite: cada run es un TestRun y cada CP acumula todas sus ejecuciones, también después de que GitHub borre los artefactos a los 90 días.
- Los ID de caso nunca se reutilizan (los retirados están en `alcance-y-casos.md`), así que la historia de un CP no mezcla dos casos.

## Estado verificado (11-nov-2026)

- `docker compose up -d`: `qolqe_kiwi_db` y `qolqe_kiwi_web` en estado *healthy*; https://localhost:8443 responde 302 a `/init-db/` (falta el `initial_setup` del alumno) y el certificado de `localhost.crt` se verifica con curl y con Python. Imágenes fijadas por digest (Kiwi 17.0).
- `kiwi_sincronizar.py --simular --ultimos 20` sobre `Joharjbe/qolqe-wallet`: 15 runs reconstruidos desde `reportes-api`/`reportes-web` con las etiquetas de su commit, 61 casos cada uno; detecta los runs fallidos (#1, #2, #8, #13) y el CP-W10 inestable del run #13. (Esa corrida es anterior a `--rama main`; con el valor por defecto, los runs de PR quedan fuera.)
- **Importación real contra Kiwi 17.0.** En contenedores desechables de la misma imagen (MariaDB y Kiwi, con `migrate` y un superusuario de prueba, borrados después): `--crear-plan` creó el plan 1; `--desde-carpeta` importó un run con 331 casos (291 PASSED y 40 WAIVED), 41 enlaces de defecto y 180 capturas como adjuntos, con el build en la versión del plan; una segunda sincronización del mismo run se saltó; una importación cortada a mitad se retomó en el mismo TestRun, sin duplicarlo. Falta repetirla en el Kiwi del alumno, con runs reales de GitHub.

## Evidencia pendiente (después del primer run en `main`)

Capturas para `docs/img/`: la lista de TestRuns, un CP con sus ejecuciones, *Telemetry → Status matrix* y `historial.html` de Pages con al menos 3 runs (uno `sin-imagenes`, uno `con-imagenes` y un re-run, para mostrar el intento 2).
