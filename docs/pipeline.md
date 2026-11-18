# Pipeline de pruebas (núcleo y G4)

Archivo: `.github/workflows/pruebas.yml`. Corre en cada push a `main`, en cada pull request a `main` y a pedido (*Run workflow*). Las etapas van de la más barata a la más cara: si falla una barata, no se gasta en la cara. En las etapas de la clase 12 (etapa de commit, aceptación automatizada y no funcional), `estatico` es la etapa de commit (análisis estático) y `contrato`, `api` y `web` son la de aceptación automatizada. La Parte 3 es la etapa no funcional, que la clase pone «programado / release» y no en cada push: se corrió a mano para la entrega de la Parte 3 (tag `parte-3`, corridas del 11-nov-2026), y el job `reportes` publica su evidencia en cada run (sección *Por qué el rendimiento no corre en el pipeline*).

```
estatico ──► contrato ──► api ──► web (x3)                                 (en serie; contrato, api y web con su guarda)
estatico, contrato, api, web ──► quality-gate                              (veredicto único, siempre corre)
estatico, contrato, api, web ──► reportes ──► gestion-casos ──► publicar   (gestion-casos y publicar: solo main)
```

La validación de contrato va **al inicio**, antes de las pruebas funcionales: el contrato es el acuerdo que la API promete cumplir, así que si no se cumple, los casos funcionales y los del navegador todavía no significan nada y no vale la pena gastar dos runners en ellos. El costo de serializarlo es lo que dura el job `contrato`, que antes se solapaba con `api`: 41 segundos en el run #20 (horas de inicio y fin del job en la API de GitHub), de los 9 min 44 s que duró ese run. En la lámina de la clase 12 el contrato iba en la segunda etapa, junto a la API funcional. El anuncio final lo pide «al inicio», y por eso va primero dentro de esa etapa: si falla lo barato, no se gasta en lo caro (*fail fast*).

`quality-gate` y `reportes` esperan a las cuatro etapas: el gate, para juzgarlas juntas; `reportes`, para unir sus JUnit en la matriz. `reportes` solo exige `estatico` en verde, porque ese job valida las etiquetas con las que se arma la matriz (`trazabilidad.py --verificar`), y corre aunque fallen las pruebas.

## Jobs

| Job | Propósito | needs / condición | Justificación | Artefactos |
|---|---|---|---|---|
| `estatico` | `ruff check`, `tsc --noEmit -p tests/e2e`, `bddgen`, `pytest --collect-only`, `trazabilidad.py --verificar`, `actionlint` y la regla del patrón | — | *Shift left* y *fail fast* (ISTQB CTFL v4.0.1, 2.1.5; el *commit build* rápido de Fowler): en un minuto, sin servidor ni navegador, detecta lo que rompería todas las suites (Gherkin mal escrito, paso sin definir, error de tipos, etiqueta @CP faltante o repetida). Playwright no revisa tipos. Revisa también sus propias herramientas: `actionlint` (con shellcheck) valida el workflow, que es el único artefacto que el job no revisaba, y un `grep` sobre `tests/e2e/steps` falla si un paso de Gherkin usa localizadores o `page` directamente, que es la regla del patrón Page Object. | Log del job |
| `contrato` | Schemathesis contra `/openapi.json` (núcleo y G4) | `estatico` | **Primera prueba dinámica, al inicio:** los casos se generan desde el contrato que la API promete cumplir, así que si el contrato falla, los casos diseñados prueban sobre una base que ya no se sostiene. Su propio runner y su propia base de datos: no comparte estado con `api`. En la Entrega 2 iba en el mismo job que la API y se perdía si fallaba pytest; en la primera versión del pipeline final (PR #7) corría en paralelo con `api`, y desde el PR #9 va antes. | `reportes-contrato`: `junit.xml`, `html/`, `peticiones.har` (con imágenes) |
| `api` | pytest-bdd funcional y técnico del núcleo y de G4 | `estatico` y `contrato` en verde | Con el contrato cumplido, los casos diseñados: reglas de negocio, errores, autorización y defectos conocidos (xfail estricto con su DEF, solo ante una `AssertionError`). Nombre del check obligatorio. | `reportes-api`: `junit.xml`, `reporte.html`, log de uvicorn |
| `web` | Playwright + playwright-bdd, `--repeat-each=3` | `api` y `contrato` en verde | La etapa más cara (Chromium, 3 repeticiones) solo corre con la capa API en verde: con el backend roto la web solo repetiría el síntoma. x3 con `failOnFlakyTests` detecta pruebas inestables. Nombre del check obligatorio. | `reportes-web`: `junit.xml`, `html/` (capturas, videos y trazas según el modo) |
| `quality-gate` | Pasa solo si las cuatro etapas terminan en `success` | las 4 etapas, `always()` | Criterios de salida automatizados (ISTQB CTFL v4.0.1, 5.1.3). Con `always()` siempre da veredicto. Escribe en el resumen del run los **cuatro criterios de salida con el job que hace cumplir cada uno** y su alcance (no evalúa el rendimiento ni el job `reportes`), para que el veredicto se lea sin abrir el YAML. | Criterios, tabla y veredicto en el resumen |
| `reportes` | Página de la Parte 3, matriz HU → caso → resultado, `junit-cp.xml` (un caso por CP), `run.json`, evidencias por CP y vista previa del historial | `estatico` en verde; corre aunque fallen las pruebas | Trazabilidad (ISTQB CTFL v4.0.1, 1.4.4). Corre también en PR, con la matriz en el resumen del run, porque el reporte es lo que explica un fallo. No es parte del gate. La evidencia de rendimiento está versionada en `tests/performance/resultados/`, así que `sitio_rendimiento.py` solo la copia y arma su página; va antes de la portada porque el nav enlaza `rendimiento/` solo si existe. | `sitio` (7 o 14 días), `trazabilidad` (90 días) |
| `gestion-casos` | Registra el run de `main` en Kiwi TCMS | `reportes`; solo `main` | Preparado para un Kiwi accesible desde internet. Hoy Kiwi corre en la máquina del alumno y se sincroniza en modo pull (`docs/gestion-casos.md`), así que el job deja ese aviso en el resumen del run y se salta sus pasos mientras no existan los secretos. No bloquea merges. | Test Run en Kiwi; aviso en el resumen |
| `publicar` | GitHub Pages con la portada, los reportes, la Parte 3, las evidencias por caso y el historial: `historial.json` guarda hasta los últimos 30 runs y `historial.html` dibuja la grilla de los últimos 15 | `reportes` y `gestion-casos`; solo `main` | **Último job del run**, para que el reporte quede visible al terminar: su paso final deja en el resumen la URL del sitio, la de la Parte 3, la de las evidencias y el modo de evidencia. Depende de `gestion-casos` solo para ir al final; no exige que esté en verde, así que el sitio se publica igual si Kiwi no está configurado. Único job con `pages: write` e `id-token: write` (mínimo privilegio). `concurrency: github-pages` sin cancelar: los despliegues van en serie y ningún run pisa la entrada de otro en el historial. | Sitio publicado; enlaces en el resumen |

Además: `permissions: contents: read` en todo el workflow, `timeout-minutes` en cada job, un run de PR cancela el anterior del mismo PR (en `main` ningún run se cancela) y los artefactos de prueba se guardan 14 días (7 si son con imágenes, por tamaño).

## Checks obligatorios

La protección de `main` exige dos checks: `api` y `web` (al 18-nov-2026, según `gh api repos/Joharjbe/qolqe-wallet/branches/main/protection/required_status_checks`). GitHub cuenta un job **omitido** por una condición como aprobado ([GitHub Docs](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks)), así que con `estatico` delante un fallo estático dejaría `api` y `web` omitidos, y esos dos checks no lo detendrían. La clase 12 lo resume así: «Skipped no es verde». Por eso los tres jobs de prueba (`contrato`, `api` y `web`) corren con `if: !cancelled()` y empiezan con una **guarda**: si la etapa anterior no terminó en `success`, el job falla en segundos y el check queda en rojo.

Esto es lo que hace que serializar el contrato sea seguro: si `contrato` falla, `api` no se omite —falla en su guarda—, así que el check obligatorio `api` queda en rojo y el PR no se puede fusionar. Sin la guarda, serializar habría *debilitado* la protección en vez de reforzarla. Se ve en el [PR #10](https://github.com/Joharjbe/qolqe-wallet/pull/10), que rompe a propósito el saldo esperado de CP-A28 y no se fusiona. En su [run #25](https://github.com/Joharjbe/qolqe-wallet/actions/runs/44240958431), `api` quedó en rojo y `web` no se omitió: falló en su guarda con «api terminó en 'failure' y contrato en 'success': no se ejecuta la web». `quality-gate` dio «no pasa» ([captura del run](img/demo-gate-rojo.png)) y la fusión quedó bloqueada (`gh pr view 10` → `BLOCKED`, 18-nov-2026).

`quality-gate` es el único check que mira las cuatro etapas a la vez, incluidas `estatico` y `contrato`, que no son obligatorias por sí solas. Corre con `always()`, trata `skipped` como no aprobado y deja el veredicto único en el resumen. No está marcado como obligatorio, así que no bloquea el merge por sí solo: lo bloquean `api` y `web`, que con las guardas quedan en rojo si falla cualquier etapa anterior. Si se marcara como obligatorio, sería una segunda defensa: aunque una etapa se omitiera, el gate la contaría en rojo. `api` y `web` se conservan porque sus nombres ya están en la protección y en el historial de los PR. La regla tiene `enforce_admins` activo: tampoco el dueño del repositorio fusiona sin `api` y `web` en verde. No se usan filtros `paths` en este workflow: un check obligatorio que nunca corre deja el PR esperando.

Los cuatro criterios de salida que `quality-gate` escribe en el resumen de cada run, con el job que hace cumplir cada uno:

1. **Análisis estático** (`estatico`): ruff, tipos de TypeScript, Gherkin con todos sus pasos definidos, etiquetas de trazabilidad, actionlint y la regla del patrón (ningún localizador en los pasos).
2. **Contrato de la API** (`contrato`): Schemathesis genera los casos desde el OpenAPI y corre antes que las pruebas funcionales.
3. **API funcional y técnica** (`api`): todas pasan y los fallos conocidos van declarados como xfail estricto con su DEF.
4. **Web de punta a punta** (`web`): pasa las 3 corridas seguidas, sin pruebas inestables.

El gate no evalúa el rendimiento (sección siguiente) ni el job `reportes`, que publica la evidencia incluso cuando las pruebas fallan.

## Por qué el rendimiento no corre en el pipeline

Las pruebas de rendimiento de la Parte 3 (k6) **no son un job de este workflow**, y es una decisión, no un olvido:

- **Un umbral de rendimiento solo significa algo con un entorno fijo.** Los umbrales U-01 a U-09 se midieron con Qolqe en un contenedor limitado a 1 CPU y 1 GB, con k6 generando carga desde los otros núcleos del mismo equipo (`tests/performance/resultados/entorno/entorno.json`). Un runner de GitHub es otra máquina, virtual y compartida (4 vCPU y 16 GB en un repositorio público, según [GitHub Docs](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)): el mismo escenario daría números distintos en cada run y el veredicto dejaría de ser comparable.
- **Ya está medido de cerca cuánto margen hay.** La comprobación de validez V-06 exige que con **1 solo usuario** el p95 no pase del 10 % del umbral, y `login` dio 92 ms frente a los 80 ms de ese margen (`tests/performance/resultados/referencia/*/veredicto.md`), por el costo de PBKDF2 al verificar el PIN. Con tan poco margen, un runner compartido produciría rojos falsos que bloquearían merges sin que nada se haya roto.
- **Las corridas duran más que el pipeline.** Las corridas de carga, pico, estrés, resistencia y escalabilidad duran entre 15.8 minutos (estrés, que k6 cortó a los 947.7 s; su diseño es de 28 + 2 minutos en `docs/diseno-rendimiento.md`) y 64.1 minutos (resistencia), según el `resumen.json` de cada una en `tests/performance/resultados/`. Solo la de carga (19.1 minutos) más que duplicaría el pipeline completo, que tardó 9 min 44 s en el run #20 y 13 min 38 s en el intento 1 del run #24.
- **La evidencia sí viaja con el repositorio.** Las corridas quedan versionadas en `tests/performance/resultados/` y el job `reportes` las publica en `rendimiento/` del sitio, así que el resultado es auditable aunque la medición no se repita en CI. El diseño, los supuestos y la validez están en `docs/diseno-rendimiento.md`.

Lo que sí hace el pipeline con la Parte 3 es publicarla: el veredicto por umbral, el comparativo entre escenarios y el reporte de cada corrida quedan a un clic desde la portada del sitio.

## Evidencia con o sin imágenes

| | `sin-imagenes` (push, PR y por defecto) | `con-imagenes` (solo a pedido) |
|---|---|---|
| Web | captura de los fallos, video en el reintento, traza de los fallos | captura, video y traza de **cada** prueba |
| API | peticiones y respuestas de los fallos y de los xfail (DEF) en `reporte.html` | peticiones y respuestas de **cada** caso |
| Contrato | JUnit y HTML | además `peticiones.har` con todo el tráfico |
| Retención | 14 días | 7 días |

- **Desde GitHub:** *Actions → Pruebas núcleo y G4 → Run workflow* → rama `main` → *evidencia*: `con-imagenes` → *Run workflow*.
- **Desde la terminal:** `gh workflow run pruebas.yml -R Joharjbe/qolqe-wallet --ref main -f evidencia=con-imagenes`.
- **En local:** `npm run test:web:con-imagenes`, `npm run test:api:con-imagenes` y `EVIDENCIA=con-imagenes ./scripts/correr-contrato.sh` (o las variantes `sin-imagenes`).

La variable `EVIDENCIA` la leen `playwright.config.ts`, `tests/api/evidencia.py` (plugin de pytest-html) y `scripts/correr-contrato.sh`. El token no llega a la evidencia publicada: `evidencia.py` enmascara la cabecera `Authorization`, el `access_token` y cualquier JWT en las peticiones, en las respuestas y en el mensaje de un fallo; Schemathesis filtra la cabecera del HAR y `correr-contrato.sh` enmascara los JWT de los cuerpos al terminar. En las peticiones de API no se anota la preparación del fixture (reinicio de datos y reloj), solo los pasos del escenario. Las opciones de reportería que ofrece cada herramienta, y cuáles se usan, están en [Opciones de reportería de cada herramienta](#opciones-de-reportería-de-cada-herramienta).

## Trazabilidad a lo largo de muchas ejecuciones

`.github/scripts/trazabilidad.py` (con el modelo en `casos.py`) une las etiquetas de los `.feature` con los JUnit:

- **Etiquetas:** `@HU-N-01`..`@HU-N-09` y `@HU-G4-01`..`@HU-G4-10` (títulos leídos de `docs/requisitos.md`), `@CA<n>`, `@CP-<id>` (`A`, `T`, `W`, `NA`, `NW`), `@DEF-xx` y `@tecnico`. En la web, un defecto conocido lleva `@fail @DEF-xx`.
- **Agrupación:** módulo (núcleo si el CP empieza con `CP-N`, si no G4: sale del prefijo del CP, no de la HU), nivel (api, web, contrato) y tipo (técnico si tiene `@tecnico` o es `CP-T`). El contrato es el caso `CP-T04`, con el detalle por operación y su HU; cubre los dos módulos y cuenta como "núcleo y G4" (grupo `NUCLEO_G4.contrato` en el JUnit por CP).
- **Estados por CP:** `passed`, `xfailed` (fallo esperado con su DEF), `flaky` (alternó en las repeticiones), `failed`, `skipped` y `sin ejecutar`. Un esquema cuenta cada ejemplo; la web, cada repetición (`passed (3/3)`).
- **Salidas de cada run:** `trazabilidad.md` y la portada (con el veredicto del run: `success` o `failure`), `junit-cp.xml` (un `<testcase>` por CP con propiedades `hu`, `ca`, `defecto`, `modulo`, `nivel`, `tipo`, `estado`, `ejecuciones` y `evidencia`), `run.json` (número, intento, commit, rama, evento, evidencia, fecha, conclusión, totales y estado de cada CP) y `evidencias/` (captura por CP y el reporte de API).
- **Historial:** `publicar` descarga el `historial.json` publicado en Pages y el de la caché de `main` (respaldo si Pages no responde), los une por id de run (`<run_id>-<intento>`), suma el run actual y guarda hasta los últimos 30 en `historial.json`. `historial.html` dibuja una columna por cada uno de los últimos 15 (`escribir_historial`, `columnas=15`), y los conteos, la estabilidad y la primera y última vez se calculan sobre todos los guardados (hasta 30). **Cada intento es su propia columna de `historial.html` (una entrada de `historial.json`):** un *re-run* (#N.2) no reemplaza al #N.1, porque que el mismo commit falle y luego pase es justo la inestabilidad que se quiere ver. Publica `historial.html` (grilla CP × runs, conteos pasó/falló/xfail/flaky, estabilidad, primera y última vez) y `historial.json`. Estabilidad = porcentaje de ejecuciones con el resultado esperado (passed o xfailed); un intento fallido y su re-run exitoso dejan un 50 %. El primer run parte vacío.
- **Por qué `publicar` es solo de `main`:** Pages guarda una sola versión del sitio. Cada despliegue sube la carpeta `sitio` entera y reemplaza la anterior; por eso `publicar` baja antes el `historial.json` publicado. Si un PR publicara, la portada mostraría el resultado de un código que todavía no está en `main` y su columna quedaría en el historial del código entregado. En un PR, el reporte queda en el artefacto `sitio` y la matriz en el resumen del run (job `reportes`). Además, el entorno `github-pages` del repositorio solo acepta despliegues desde `main`.
- **Por qué el historial arranca en el run #17 y no en el #5:** los runs verdes de `main` del 30-oct-2026 (#5, #7, #10, #12 y #15) ya publicaban en Pages desde el job `reportes` la portada, la matriz y los reportes web, API y de contrato de ese run, pero no escribían `run.json` y cada despliegue reemplazaba al anterior, así que de ellos no quedó nada que sumar. `run.json`, el job `publicar` y el historial acumulado llegaron con el commit `87bec4e` (11-nov-2026), y el run #17 (commit `5fbe969`) es el primero de `main` que los trae. De esos runs viejos solo quedan los artefactos `reportes-api` y `reportes-web`; quien los recupera es Kiwi, que rearma su JUnit por CP desde ellos (`docs/gestion-casos.md`). Al terminar el intento 1 del run #24 (17-nov-2026), el historial tenía los runs #17, #18, #20 y #24, los cuatro en intento 1. El *re-run* del #24 sumó la columna #24.2: 5 columnas.
- **Inestable o cambio:** un caso es *inestable* si fue `flaky` en algún run, si el mismo commit dio un resultado esperado y uno fallido (por ejemplo, en un re-run) o si alternó dos o más veces. Un solo cambio entre esperado y fallido se marca *cambió en #N*: es lo típico de una regresión o de una corrección, no de una prueba inestable.
- **Corridas locales:** fuera de Actions cada corrida tiene su propio id (`local-<fecha>`), el commit y la rama de git, y el encabezado de la matriz dice que es una corrida local, así que varias corridas locales se pueden sumar sin pisarse: `python .github/scripts/trazabilidad.py --solo-historial --run-json <run.json nuevo> --historial-previo <sitio>/historial.json --sitio <sitio>` después de cada corrida.
- **`--verificar`** (job `estatico`): error si un escenario no tiene @HU o @CP, si el CP del título no coincide con la etiqueta, si un CP se repite, si una HU no existe en `requisitos.md`, si falta @CA en un caso funcional, si un par @HU @CA no existe en `requisitos.md` (cada @CA va después de sus @HU) o si un `@fail` no tiene `@DEF`. Aviso si falta @CA en un caso técnico, si un DEF todavía no está en `docs/defectos.md`, si una HU no tiene casos o si un CP tiene sufijo de letra.
- `docs/trazabilidad.md` es la matriz versionada al cerrar una entrega. Se toma del artefacto `trazabilidad` de un run verde de `main` (`gh run download <id> -R Joharjbe/qolqe-wallet -n trazabilidad`), para que el encabezado lleve el número de run y su enlace; generada en local diría "Run #local" y lo aclara en el encabezado. La versión actual es la del **run #24**, intento 1 (push a `main`, commit `1025a78`, el último de `main` antes del PR de documentación de la entrega; 17-nov-2026, veredicto `success`): es idéntica al artefacto `trazabilidad` de ese intento y a la `trazabilidad.md` que Pages publicó al terminarlo. Pages muestra siempre la matriz del último run de `main`, así que después de ese intento su encabezado cambia. Se toma de `main` y no de una corrida local porque es el resultado de un commit tal como lo vio el pipeline, y cualquiera puede abrir ese run en Actions.

## Contrato: alcance, exclusiones y hallazgos

`scripts/correr-contrato.sh` prueba 19 operaciones: registro (`POST /api/usuarios`), ingreso y salida (`/api/auth/login`, `/api/auth/logout`), sesiones (`GET /api/seguridad/sesiones`), cuenta (`/api/cuentas/me`, `/saldo`, `/cierre`), transferencias y simulación de comisión, contactos y solicitudes. `scripts/contrato_hooks.py` pone el token: logout y cierre de cuenta usan un usuario desechable recién registrado, para no invalidar el token de Ana a mitad de la corrida.

| Hallazgo | Clasificación | Tratamiento |
|---|---|---|
| `POST /api/auth/login` responde 423 a un PIN mal formado cuando la cuenta está bloqueada | Falso positivo: 423 `CUENTA_BLOQUEADA` está en el contrato y es un rechazo (HU-N-02 CA4); la lista por defecto de Schemathesis no lo incluye | `schemathesis.toml`: 423 se acepta como rechazo solo en esa operación |
| `PUT /api/cuentas/me` acepta `correo: ""` | Falso positivo: la descripción del campo en el contrato dice "`null` o vacío lo quita" (lo prueba CP-NA67); `format: email` no puede expresarlo | `filter_failure` en `contrato_hooks.py`, solo ST201 con `correo == ""` |
| `POST /api/transferencias` acepta un `cci` inválido en QOLQE y un `celular_destino` inválido en INTERBANCARIA | **Defecto: DEF-29** | `filter_failure` en `contrato_hooks.py`, solo ST201 con esa combinación; el resto del check sigue activo |
| `DELETE /api/seguridad/sesiones` | Fuera de alcance: HU-G6-10 (módulo G6) | `enabled = false` en `schemathesis.toml` |

Las fallas descartadas siguen visibles: Schemathesis las cuenta como "dropped by `filter_failure`" en la consola y en el HTML. Con la semilla 42 y con las semillas 1, 7 y 2026 (50 ejemplos) la corrida queda en verde. El número de casos generados no es fijo: la fase con estado depende de las respuestas (en las corridas del 11-nov-2026 fueron 1291, 1376, 1414 y 1373). Para que la semilla repita lo más posible, `contrato_hooks.py` usa un generador propio (`random.Random()`) en vez del módulo global que controla Hypothesis, y `constraints.txt` fija `hypothesis==6.170.14`.

El reporte completo de DEF-29 está en [`defectos.md`](defectos.md#def-29-la-transferencia-acepta-un-campo-del-otro-tipo-que-no-cumple-su-formato).

## Ejecutar en local

```bash
source .venv/bin/activate
QOLQE_BD=/tmp/qolqe.db QOLQE_MODO_PRUEBA=1 python -m uvicorn qolqe.main:app --port 8000 &
npm run trazabilidad:verificar
npm run test:api                    # o test:api:con-imagenes
./scripts/correr-contrato.sh        # QOLQE_URL=http://127.0.0.1:<puerto> para otro puerto
npm run test:web -- --grep CP-W01   # o test:web:con-imagenes
python .github/scripts/trazabilidad.py --sitio /tmp/sitio --junit-cp /tmp/sitio/junit-cp.xml --run-json /tmp/sitio/run.json
```

## Pruebas de concurrencia en el pipeline

Los 10 escenarios con hilos llevan `@concurrencia`. Los 9 que tienen DEF son xfail **estrictos** como los demás: si un defecto de concurrencia se corrige, el pipeline obliga a quitar su `@DEF`. El riesgo es que una carrera no se manifieste en una corrida y dé XPASS, que pondría `api` en rojo sin que nadie haya corregido nada. Por eso:

- un escenario de concurrencia se automatiza solo si dio el mismo resultado en 200 de 200 corridas locales (`pytest -m concurrencia --runxfail`): los 9 con DEF fallaron siempre por su defecto y CP-NA131, el único sin defecto, pasó siempre (`docs/defectos.md`);
- donde la ventana de la carrera es corta, el escenario repite la ráfaga: CP-T20 envía hasta 5 ráfagas de 5 altas y termina en la primera que crea duplicados, así que un XPASS espurio exige que las 5 se serialicen;
- `raises=AssertionError`: si el servidor no responde o un paso se rompe, la prueba falla en vez de contar como el defecto;
- en el runner de GitHub, los 10 dieron el resultado esperado en los 9 runs del #16 al #24 (cinco de PR y cuatro de `main`) y en el intento 2 del #24. El job `api` terminó en verde en todos, y con xfail estricto un XPASS lo habría puesto en rojo. El historial de Pages lo muestra caso por caso en #17, #18, #20, #24.1 y #24.2: los 9 con DEF en `xfailed` y CP-NA131 en `passed`. Diez corridas no son 200: si alguno llegara a dar XPASS en el runner, pasa a evidencia manual como CP-NA69.

## Limitaciones conocidas

- `concurrency.queue: max` no es válido para actionlint, así que no se usa: con tres o más pushes seguidos a `main`, GitHub reemplaza el despliegue pendiente y ese run no queda en el historial de Pages (sí en su artefacto `trazabilidad` y en Kiwi).
- Con el contrato al inicio, un fallo de contrato deja ese run sin resultados funcionales: `api` y `web` fallan en su guarda sin correr sus pruebas, y la matriz muestra sus casos como *sin ejecutar*. Es el costo del *fail fast*: hasta que el contrato vuelva a verde, el run no dice nada de los casos diseñados.
- Con `con-imagenes` el reporte web crece (capturas, video y traza por prueba); por eso se retiene 7 días.
- Kiwi solo recibe los runs de `main` (`kiwi_sincronizar.py --rama main` por defecto), la misma población que el historial de Pages. `gh run list` devuelve el último intento de cada run: un intento anterior queda en Kiwi solo si se sincronizó antes del re-run (en Pages queda siempre).

## Opciones de reportería de cada herramienta

La clase 12 pide tres formatos: JUnit XML para las herramientas, HTML para las personas y el resumen en la página del run (`$GITHUB_STEP_SUMMARY`). Cada herramienta ofrece más de una opción. Esta tabla dice cuáles se usan y dónde se configuran.

| Herramienta | Opciones que se usan | Dónde se configura | Para quién |
|---|---|---|---|
| Playwright | Reporters `list` (consola), `html` (reporte con trazas) y `junit` con `includeRetries`, que deja el intento fallido de un flaky como `<flakyFailure>`. Evidencia según `EVIDENCIA`: `screenshot` en `'only-on-failure'` o `'on'`, `video` en `'on-first-retry'` o `'on'` y `trace` en `'retain-on-failure'` o `'on'` | `playwright.config.ts:26-37` | JUnit: matriz y Kiwi. HTML: personas |
| pytest (pytest-bdd) | `--junitxml` y `--html --self-contained-html` (pytest-html, un solo archivo), más el plugin `tests/api/evidencia.py`, que agrega las peticiones y respuestas de cada caso o solo de los fallos | `package.json:9` (`test:api`) | JUnit: matriz y Kiwi. HTML: personas |
| Schemathesis | `--report junit,html`, y además `har` (`peticiones.har`) con `con-imagenes` | `scripts/correr-contrato.sh:15-19` y `:27` | JUnit: matriz. HTML y HAR: personas |
| GitHub Actions | El resumen de cada job: `.github/scripts/resumen.py` lee el JUnit y escribe la tabla en `$GITHUB_STEP_SUMMARY`. `quality-gate` escribe ahí sus criterios de salida y `reportes`, la matriz | `.github/scripts/resumen.py:35` | Quien abre el run |

En palabras de la clase 12: JUnit XML para las herramientas (aquí, la matriz y Kiwi), HTML para las personas y el resumen en la página del run. El JUnit es el formato común de las tres suites funcionales.

## Fuentes

- ISTQB. Certified Tester Foundation Level v4.0 (syllabus v4.0.1): 1.4.4 trazabilidad, 2.1.5 *shift left*, 5.1.3 criterios de entrada y salida. https://www.istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/
- GitHub Docs. Troubleshooting required status checks (un job omitido por una condición reporta *Success*). https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks
- GitHub Docs. Control the concurrency of workflows and jobs (grupos, `cancel-in-progress` y el reemplazo del run pendiente). https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/control-the-concurrency-of-workflows-and-jobs
- GitHub Docs. Removing workflow artifacts (retención de 90 días por defecto). https://docs.github.com/en/actions/how-tos/manage-workflow-runs/remove-workflow-artifacts
- GitHub Docs. GitHub-hosted runners reference (4 vCPU y 16 GB para Linux en repositorios públicos). https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- Playwright. TestConfig, `failOnFlakyTests`. https://playwright.dev/docs/api/class-testconfig#test-config-fail-on-flaky-tests
- Fowler, M. Continuous Integration, "Keep the Build Fast" (*commit build* y etapas). https://martinfowler.com/articles/continuousIntegration.html
