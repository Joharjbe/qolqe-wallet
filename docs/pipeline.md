# Pipeline de pruebas (núcleo y G4)

Archivo: `.github/workflows/pruebas.yml`. Corre en cada push a `main`, en cada pull request a `main` y a pedido (*Run workflow*). Las etapas van de la más barata a la más cara: si falla una barata, no se gasta en la cara.

```
estatico ──► api ───────┐
         └─► contrato ──┴─► web (x3) ──► quality-gate        (veredicto único)
                api, contrato, web ──► reportes ──► gestion-casos   (solo main)
                                                └─► publicar        (solo main, en serie)
```

## Jobs

| Job | Propósito | needs / condición | Justificación | Artefactos |
|---|---|---|---|---|
| `estatico` | `ruff check`, `tsc --noEmit -p tests/e2e`, `bddgen`, `pytest --collect-only`, `trazabilidad.py --verificar` | — | *Shift left* y *fail fast* (ISTQB 2.1.5): en un minuto, sin servidor ni navegador, detecta lo que rompería todas las suites (Gherkin mal escrito, paso sin definir, error de tipos, etiqueta @CP faltante o repetida). Playwright no revisa tipos. | Log del job |
| `api` | pytest-bdd funcional y técnico del núcleo y de G4 | `estatico` | Primera prueba dinámica y la más barata: reglas de negocio, errores, autorización y defectos conocidos (xfail estricto con su DEF). Nombre del check obligatorio. | `reportes-api`: `junit.xml`, `reporte.html`, log de uvicorn |
| `contrato` | Schemathesis contra `/openapi.json` (núcleo y G4) | `estatico`, en paralelo con `api` | Casos generados desde el contrato, complementarios a los casos diseñados. Otro runner y otra base de datos: no comparte estado con `api`. Antes iba en el mismo job que la API y se perdía si fallaba pytest. | `reportes-contrato`: `junit.xml`, `html/`, `peticiones.har` (con imágenes) |
| `web` | Playwright + playwright-bdd, `--repeat-each=3` | `api` y `contrato` en verde | La etapa más cara (Chromium, 3 repeticiones) solo corre con la capa API en verde: con el backend roto la web solo repetiría el síntoma. x3 con `failOnFlakyTests` detecta pruebas inestables. Nombre del check obligatorio. | `reportes-web`: `junit.xml`, `html/` (capturas, videos y trazas según el modo) |
| `quality-gate` | Pasa solo si las cuatro etapas terminan en `success` | las 4 etapas, `always()` | Criterios de salida automatizados (ISTQB 5.1.3). Con `always()` siempre da veredicto. | Tabla en el resumen |
| `reportes` | Matriz HU → caso → resultado, `junit-cp.xml` (un caso por CP), `run.json`, evidencias por CP y vista previa del historial | `estatico` en verde; corre aunque fallen las pruebas | Trazabilidad (ISTQB 1.4.4). Corre también en PR, con la matriz en el resumen del run, porque el reporte es lo que explica un fallo. No es parte del gate. | `sitio` (7 o 14 días), `trazabilidad` (90 días) |
| `gestion-casos` | Registra el run en Kiwi TCMS | `reportes`; solo `main` | Preparado para un Kiwi accesible desde internet. Hoy Kiwi corre en la máquina del equipo y se sincroniza en modo pull (`docs/gestion-casos.md`), así que el job termina con un aviso mientras no existan los secretos. No bloquea merges. | Test Run en Kiwi |
| `publicar` | GitHub Pages con la portada, los reportes y el historial de los últimos 30 runs | `reportes`; solo `main` | Único job con `pages: write` e `id-token: write` (mínimo privilegio). `concurrency: github-pages` sin cancelar: los despliegues van en serie y ningún run pisa la fila de otro en el historial. | Sitio publicado |

Además: `permissions: contents: read` en todo el workflow, `timeout-minutes` en cada job, un run de PR cancela el anterior del mismo PR (en `main` ningún run se cancela) y los artefactos de prueba se guardan 14 días (7 si son con imágenes, por tamaño).

## Checks obligatorios

La protección de `main` exige `api` y `web`; sus nombres no cambian. GitHub cuenta un job **omitido** como aprobado, así que con `estatico` delante un fallo estático dejaría `api` y `web` omitidos y el PR se podría fusionar. Para evitarlo sin tocar la protección, `api` y `web` corren con `if: !cancelled()` y empiezan con una **guarda**: si la etapa anterior no terminó en `success`, el job falla en segundos y el check queda en rojo.

Recomendado (lo hace el dueño del repo en *Settings → Branches*): agregar `quality-gate` como check obligatorio, conservando `api` y `web`. No se usan filtros `paths` en este workflow: un check obligatorio que nunca corre deja el PR esperando.

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

La variable `EVIDENCIA` la leen `playwright.config.ts`, `tests/api/evidencia.py` (plugin de pytest-html; el token se enmascara) y `scripts/correr-contrato.sh`. En las peticiones de API no se anota la preparación del fixture (reinicio de datos y reloj), solo los pasos del escenario.

## Trazabilidad a lo largo de muchas ejecuciones

`.github/scripts/trazabilidad.py` (con el modelo en `casos.py`) une las etiquetas de los `.feature` con los JUnit:

- **Etiquetas:** `@HU-N-01`..`@HU-N-09` y `@HU-G4-01`..`@HU-G4-10` (títulos leídos de `docs/requisitos.md`), `@CA<n>`, `@CP-<id>` (`A`, `T`, `W`, `NA`, `NW`), `@DEF-xx` y `@tecnico`. En la web, un defecto conocido lleva `@fail @DEF-xx`.
- **Agrupación:** módulo (núcleo si el CP empieza con `CP-N`, si no G4), nivel (api, web, contrato) y tipo (técnico si tiene `@tecnico` o es `CP-T`). El contrato es el caso `CP-T04`, con el detalle por operación y su HU.
- **Estados por CP:** `passed`, `xfailed` (fallo esperado con su DEF), `flaky` (alternó en las repeticiones), `failed`, `skipped` y `sin ejecutar`. Un esquema cuenta cada ejemplo; la web, cada repetición (`passed (3/3)`).
- **Salidas de cada run:** `trazabilidad.md` y la portada, `junit-cp.xml` (un `<testcase>` por CP con propiedades `hu`, `ca`, `defecto`, `modulo`, `nivel`, `tipo`, `estado`, `ejecuciones` y `evidencia`), `run.json` (número, intento, commit, rama, evento, evidencia, fecha, conclusión, totales y estado de cada CP) y `evidencias/` (captura por CP y el reporte de API).
- **Historial:** `publicar` descarga el `historial.json` publicado en Pages y el de la caché de `main` (respaldo si Pages no responde), los une por id de run, suma el run actual (un reintento reemplaza a su intento anterior) y guarda los últimos 30. Publica `historial.html` (grilla CP × runs, conteos pasó/falló/xfail/flaky, estabilidad, primera y última vez) y `historial.json`. Estabilidad = porcentaje de runs ejecutados con el resultado esperado (passed o xfailed). El primer run parte vacío.
- **`--verificar`** (job `estatico`): error si un escenario no tiene @HU o @CP, si el CP del título no coincide con la etiqueta, si un CP se repite, si una HU no existe en `requisitos.md`, si falta @CA en un caso funcional, si un par @HU @CA no existe en `requisitos.md` (cada @CA va después de sus @HU) o si un `@fail` no tiene `@DEF`. Aviso si falta @CA en un caso técnico, si un DEF todavía no está en `docs/defectos.md`, si una HU no tiene casos o si un CP tiene sufijo de letra.
- `docs/trazabilidad.md` se sigue generando en local con `python .github/scripts/trazabilidad.py` y se versiona al cerrar cada entrega.

## Contrato: alcance, exclusiones y hallazgos

`scripts/correr-contrato.sh` prueba 19 operaciones: registro (`POST /api/usuarios`), ingreso y salida (`/api/auth/login`, `/api/auth/logout`), sesiones (`GET /api/seguridad/sesiones`), cuenta (`/api/cuentas/me`, `/saldo`, `/cierre`), transferencias y simulación de comisión, contactos y solicitudes. `scripts/contrato_hooks.py` pone el token: logout y cierre de cuenta usan un usuario desechable recién registrado, para no invalidar el token de Ana a mitad de la corrida.

| Hallazgo | Clasificación | Tratamiento |
|---|---|---|
| `POST /api/auth/login` responde 423 a un PIN mal formado cuando la cuenta está bloqueada | Falso positivo: 423 `CUENTA_BLOQUEADA` está en el contrato y es un rechazo (HU-N-02 CA4); la lista por defecto de Schemathesis no lo incluye | `schemathesis.toml`: 423 se acepta como rechazo solo en esa operación |
| `PUT /api/cuentas/me` acepta `correo: ""` | Falso positivo: la descripción del campo en el contrato dice "`null` o vacío lo quita" (lo prueba CP-NA67); `format: email` no puede expresarlo | `filter_failure` en `contrato_hooks.py`, solo ST201 con `correo == ""` |
| `POST /api/transferencias` acepta un `cci` inválido en QOLQE y un `celular_destino` inválido en INTERBANCARIA | **Defecto: DEF-29** | `filter_failure` en `contrato_hooks.py`, solo ST201 con esa combinación; el resto del check sigue activo |
| `DELETE /api/seguridad/sesiones` | Fuera de alcance: HU-G6-10 (módulo G6) | `enabled = false` en `schemathesis.toml` |

Las fallas descartadas siguen visibles: Schemathesis las cuenta como "dropped by `filter_failure`" en la consola y en el HTML. Con la semilla 42 y con las semillas 1, 7 y 2026 (50 ejemplos) la corrida queda en verde.

### DEF-29: la transferencia acepta un campo del otro tipo que no cumple su formato

Para pasar a `docs/defectos.md` con el número que toque.

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · contrato de `POST /api/transferencias` (HU-N-07, HU-N-08) |
| Severidad | Baja |
| Prioridad | Baja |
| Prueba que lo detecta | Schemathesis, check `negative_data_rejection` (ST201), caso `mAjOr5` con la semilla 42 |

**Pasos para reproducir** (token de Ana):

1. `POST /api/transferencias` con `{"tipo": "QOLQE", "celular_destino": "912345678", "monto": "10.00", "cci": "AAA"}`.
2. `POST /api/transferencias` con `{"tipo": "INTERBANCARIA", "cci": "00219300123456789012", "monto": "10.00", "celular_destino": "abc"}`.

**Resultado esperado:** 422, porque el contrato declara `cci` con patrón `^\d{20}$` y `celular_destino` con `^9\d{8}$`, sin condición por tipo.

**Resultado obtenido:** 201 en ambos casos; la transferencia se hace y el campo inválido se ignora sin validarlo. Controles: `{"tipo": "INTERBANCARIA", "cci": "AAA", ...}` responde 422 `CCI_INVALIDO` y `"cci": 12345` (número) responde 422 `SOLICITUD_INVALIDA`. Ignorar un campo **válido** del otro tipo es el comportamiento esperado (CP-NA139); el defecto es aceptar un valor que incumple el formato declarado. Clasificación: desajuste entre el código y el contrato, como DEF-08.

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

## Limitaciones conocidas

- `concurrency.queue: max` no es válido para actionlint, así que no se usa: con tres o más pushes seguidos a `main`, GitHub reemplaza el despliegue pendiente y ese run no queda en el historial de Pages (sí en su artefacto `trazabilidad` y en Kiwi).
- `web` también depende de `contrato`: un fallo de contrato deja la web sin correr en ese run. Es una decisión de *fail fast*.
- Con `con-imagenes` el reporte web crece (capturas, video y traza por prueba); por eso se retiene 7 días.
