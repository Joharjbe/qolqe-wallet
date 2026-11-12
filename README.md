# Qolqe Wallet

Billetera digital **ficticia** usada como sistema bajo prueba (SUT) en el Proyecto 2 del curso **CS5383 Pruebas y Verificación de Software**.

> ⚠️ **Antes de empezar:**
> - **No modifiquen el código de la carpeta `qolqe/`.** Su trabajo es probarlo, no repararlo.
> - Todos los datos son ficticios.

---

## Entrega del Proyecto 2 · Núcleo común y G4

[![Pruebas](https://github.com/Joharjbe/qolqe-wallet/actions/workflows/pruebas.yml/badge.svg?branch=main)](https://github.com/Joharjbe/qolqe-wallet/actions/workflows/pruebas.yml)

| | |
|---|---|
| **Módulos** | Núcleo común (HU-N-01 a HU-N-09) y G4 · Contactos y solicitudes de dinero (HU-G4-01 a HU-G4-10): 51 criterios, 335 casos |
| **API** | pytest + httpx + pytest-bdd: 276 escenarios, funcionales y técnicos (766 ejecuciones) · Schemathesis: contrato de 19 operaciones |
| **Web** | Playwright (TypeScript) + playwright-bdd · Page Object con componentes y fixtures: 58 escenarios (71 pruebas), 3 repeticiones |
| **Pipeline** | [`.github/workflows/pruebas.yml`](.github/workflows/pruebas.yml): `estatico` → `api` y `contrato` → `web` → `quality-gate`, más `reportes`, `gestion-casos` y `publicar` · evidencia `sin-imagenes` o `con-imagenes` · [ejecuciones](https://github.com/Joharjbe/qolqe-wallet/actions/workflows/pruebas.yml) · [detalle](docs/pipeline.md) |
| **Reportes publicados** | https://joharjbe.github.io/qolqe-wallet/ (con el workflow nuevo en `main`: portada, reportes, matriz del run e historial de los últimos 30 runs) |
| **Trazabilidad y gestión de casos** | Matriz HU → CA → CP → resultado por run, `junit-cp.xml` e historial · Kiwi TCMS 17.0 en Docker: [`docs/gestion-casos.md`](docs/gestion-casos.md) |
| **Rendimiento (Parte 3)** | k6 2.3.0 + Docker (1 CPU, 1 GB): carga, pico, estrés y resistencia; capacidad de 850 usuarios simultáneos · [`tests/performance/`](tests/performance/README.md) · [informe de rendimiento](docs/Informe_Rendimiento_Qolqe.docx) ([PDF](docs/Informe_Rendimiento_Qolqe.pdf)) |
| **Informe** | [`docs/informe.md`](docs/informe.md) · [respuesta a la retroalimentación](docs/respuesta-feedback.md) · [arquitectura](docs/arquitectura.md) · [alcance y casos](docs/alcance-y-casos.md) · [defectos](docs/defectos.md) · [matriz](docs/trazabilidad.md) · presentaciones: [Entrega 1](docs/Entrega1_G4_API.pptx), [Entrega 2](docs/Entrega2_G4_E2E_CICD.pptx) |

Comandos en la [sección 6](#6-ejecutar-las-pruebas).

---

## 1. Requisitos

- Python **3.11 o superior** (recomendado 3.12)
- Git

## 2. Instalación y ejecución

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn qolqe.main:app --reload
```

| Recurso | URL |
|---|---|
| Interfaz web | http://localhost:8000 |
| Documentación de la API (Swagger / OpenAPI) | http://localhost:8000/docs |
| Contrato OpenAPI en JSON | http://localhost:8000/openapi.json |
| Estado del servicio | http://localhost:8000/api/salud |

La primera vez la app crea la base de datos en `datos/` (tarda unos segundos porque genera los usuarios de carga). Para empezar desde cero, borren la carpeta `datos/` o usen `POST /api/pruebas/reiniciar`.

> Ejecuten **un solo proceso** de uvicorn (sin `--workers`). El reloj de pruebas vive en memoria.

### Variables de entorno (opcionales)

| Variable | Por defecto | Uso |
|---|---|---|
| `QOLQE_BD` | `datos/qolqe.db` | Ruta de la base de datos |
| `QOLQE_MODO_PRUEBA` | `1` | `1` habilita la API de soporte para pruebas (`/api/pruebas/*`) |
| `QOLQE_MINUTOS_TOKEN` | `30` | Vigencia del token JWT |
| `QOLQE_CLAVE_SECRETA` | clave de desarrollo | Firma de los tokens |

---

## 3. Funcionalidades

| Módulo | Pantalla | Endpoints principales |
|---|---|---|
| **Núcleo:** registro, sesión, perfil, saldo y transferencias | `/registro`, `/login`, `/inicio`, `/perfil`, `/transferir` | `POST /api/usuarios` · `POST /api/auth/login` · `POST /api/auth/logout` · `GET/PUT /api/cuentas/me` · `POST /api/cuentas/me/cierre` · `GET /api/cuentas/me/saldo` · `POST /api/transferencias` · `GET /api/transferencias/comision` |
| **G1** Recargas y recargas programadas | `/recargas` | `GET /api/recargas/configuracion` · `GET/POST /api/recargas` · `GET/POST /api/recargas/programadas` · `PUT/DELETE /api/recargas/programadas/{id}` · `POST /api/recargas/programadas/{id}/pausar` · `POST .../reanudar` |
| **G2** Pago de servicios y afiliaciones | `/servicios` | `GET /api/servicios/empresas` · `GET /api/servicios/deudas` · `GET/POST /api/servicios/pagos` · `GET /api/servicios/pagos/{codigo}` · `GET/POST /api/servicios/afiliaciones` · `PUT/DELETE /api/servicios/afiliaciones/{id}` |
| **G3** Historial y categorías | `/historial` | `GET /api/movimientos` · `GET /api/movimientos/recientes` · `GET /api/movimientos/{codigo}` · `PUT /api/movimientos/{codigo}/clasificacion` · `GET /api/movimientos/exportar` · `GET/POST /api/categorias` · `PUT/DELETE /api/categorias/{id}` |
| **G4** Contactos y solicitudes de dinero | `/contactos`, `/solicitudes` | `GET/POST /api/contactos` · `PUT/DELETE /api/contactos/{id}` · `GET/POST /api/solicitudes` · `POST /api/solicitudes/{id}/aceptar` · `.../rechazar` · `.../cancelar` |
| **G5** Límites y alertas de consumo | `/limites` | `GET/PUT /api/limites` · `GET/POST /api/limites/alertas` · `PUT/DELETE /api/limites/alertas/{id}` |
| **G6** Seguridad, dispositivos y sesiones | `/seguridad`, `/desbloqueo` | `PUT /api/seguridad/pin` · `POST /api/seguridad/desbloqueo/solicitar` · `.../confirmar` · `GET/POST /api/seguridad/dispositivos` · `PUT/DELETE /api/seguridad/dispositivos/{id}` · `GET/DELETE /api/seguridad/sesiones` · `DELETE /api/seguridad/sesiones/{id}` |

Las **historias de usuario, criterios de aceptación y reglas de negocio** están en `docs/requisitos.md`. Las funciones que las implementan, sin base de datos ni red, están en `qolqe/reglas/`:

```
qolqe/reglas/nucleo.py      qolqe/reglas/servicios.py   qolqe/reglas/contactos.py
qolqe/reglas/recargas.py    qolqe/reglas/historial.py   qolqe/reglas/limites.py
qolqe/reglas/seguridad.py
```

### Autenticación

```http
POST /api/auth/login
Content-Type: application/json

{"celular": "987654321", "pin": "4826"}
```

Opcionalmente se envía `"dispositivo_id"` (identificador de un dispositivo de confianza, ver G6). La respuesta incluye `access_token` y `sesion_id`. Envíen el token en cada solicitud protegida:

```http
Authorization: Bearer <access_token>
```

- Cada inicio de sesión crea una **sesión**; el token vence a los **30 minutos**.
- `POST /api/auth/logout` cierra la sesión. Las sesiones activas se consultan y cierran en `/api/seguridad/sesiones`.
- Tras **3 intentos fallidos** consecutivos, la cuenta se bloquea 15 minutos (`423`).

### Convenciones de la API

- **Montos:** se envían como número o texto decimal (`100`, `"100.50"`) y se devuelven como texto con 2 decimales (`"100.50"`).
- **Fechas:** hora de Lima, formato `AAAA-MM-DDTHH:MM:SS`.
- **Errores:** todos responden con un código estable y un mensaje:

```json
{"codigo": "SALDO_INSUFICIENTE", "detail": "Saldo insuficiente para realizar la operación"}
```

| HTTP | Significado | Ejemplos de `codigo` |
|---|---|---|
| 204 | Eliminación o cierre correcto, sin contenido | |
| 401 | Sin token, token inválido, vencido o de una sesión cerrada, o credenciales incorrectas | `NO_AUTENTICADO`, `CREDENCIALES_INVALIDAS`, `CUENTA_CERRADA` |
| 404 | Recurso inexistente **o de otro usuario** | `DESTINO_NO_REGISTRADO`, `CONTACTO_NO_ENCONTRADO`, `SIN_DEUDA_PENDIENTE` |
| 409 | Conflicto con el estado actual | `CELULAR_REGISTRADO`, `ALIAS_DUPLICADO`, `DEUDA_YA_PAGADA`, `ESTADO_INVALIDO` |
| 422 | Regla de negocio o datos inválidos | `MONTO_INVALIDO`, `SALDO_INSUFICIENTE`, `LIMITE_DIARIO_EXCEDIDO`, `FILTRO_INVALIDO`, `SOLICITUD_INVALIDA` |
| 423 | Cuenta bloqueada | `CUENTA_BLOQUEADA` |

El contrato completo está en `/docs` (Swagger) y en `/openapi.json`. Cada operación indica su historia de usuario, los esquemas de entrada y salida con sus restricciones, y todos los códigos de error que puede devolver, con un ejemplo por código.

---

## 4. Datos de prueba

Se restauran con `POST /api/pruebas/reiniciar`. Las fechas de las deudas y algunos movimientos se calculan **respecto del día actual** del reloj de la app.

### Usuarios

| Usuario | Celular | PIN | Correo | Saldo | Notas |
|---|---|---|---|---|---|
| Ana Torres Quispe | 987654321 | 4826 | ana.torres@correo.pe | S/ 1,500.00 | Usuario principal de ejemplo (ver abajo). Ha usado otros PIN antes |
| Bruno Díaz Mendoza | 912345678 | 7391 | bruno.diaz@correo.pe | S/ 800.00 | Tiene a Ana como contacto |
| Carla Ramos Huamán | 956781234 | 5917 | carla.ramos@correo.pe | S/ 50.00 | Saldo bajo. Tiene a Ana como contacto |
| Diego Salas Paredes | 998877665 | 3604 | diego.salas@correo.pe | S/ 2,500.00 | Límite diario configurado en S/ 1,000. Tiene a Fabián como contacto |
| Elena Vargas Ccori | 923456789 | 8152 | elena.vargas@correo.pe | S/ 300.00 | **Cuenta bloqueada** al reiniciar (para probar el desbloqueo) |
| Fabián Rojas Núñez | 934567812 | 6029 | fabian.rojas@correo.pe | S/ 0.00 | **Cuenta cerrada** |

### Datos de Ana por módulo

| Módulo | Datos |
|---|---|
| G1 | Programada "Mamá" (987111222, S/ 20, día 15, ACTIVA) y "Trabajo" (999000111, S/ 10, día 5, PAUSADA). Una recarga de hoy al 999000111 |
| G2 | Afiliaciones "Luz casa" (ELECTRO 10000001), "Agua depa" (AGUA 2000000008, **débito automático activo**) e "Internet casa" (INTERNET 300000000007) |
| G3 | Historial de unos 60 días. Categorías Comida, Familia y Servicios, con movimientos asignados y una nota |
| G4 | Contactos "Bruno" (favorito) y "Prima Carla". Solicitudes: Bruno le pide S/ 45.00 (pendiente), Carla le pidió S/ 30.00 hace más de 48 horas, y Ana le pide S/ 20.00 a Bruno (pendiente) |
| G5 | Alerta de TRANSFERENCIAS con umbral S/ 300 |
| G6 | Dispositivo de confianza "Celular de Ana" con identificador `a1b2c3d4e5f60718` |

### Usuarios de carga (pruebas de rendimiento)

- Celulares **900000001** a **900000200**, todos con PIN **2580**.
- Saldo S/ 10,000.00 y unos 1,000 movimientos de los últimos 120 días cada uno.

### Deudas de servicios

| Empresa | Suministro | Vencimiento (respecto de hoy) |
|---|---|---|
| ELECTRO | 10000001 | Vence en 10 días |
| ELECTRO | 10000002 | Vence hoy |
| ELECTRO | 10000003 | Venció ayer |
| ELECTRO | 100000009 | Dos periodos: uno venció hace 5 días y otro vence en 25 |
| AGUA | 20000004 | Venció hace 10 días |
| AGUA | 20000005 | Venció hace 30 días |
| AGUA | 2000000008 | Vence en 3 días |
| INTERNET | 300000000006 | Venció hace 60 días |
| INTERNET | 300000000007 | Venció hace 61 días |
| AGUA | 4000000001 a 4000000200 | Venció hace 5 días (para pruebas de carga) |

### Transferencias interbancarias

Usen cualquier CCI de 20 dígitos, por ejemplo `00219300123456789012`.

---

## 5. API de soporte para pruebas

Disponible solo con `QOLQE_MODO_PRUEBA=1`. **No forma parte del producto**: existe para que las pruebas automatizadas sean repetibles.

| Endpoint | Para qué |
|---|---|
| `POST /api/pruebas/reiniciar` | Restaura todos los datos semilla |
| `GET /api/pruebas/reloj` | Ver la fecha y hora de la app |
| `PUT /api/pruebas/reloj` | Fijar (`{"ahora": "2026-11-15T10:00:00"}`) o adelantar (`{"avanzar_minutos": 60}`) el reloj |
| `DELETE /api/pruebas/reloj` | Volver a la hora real |
| `GET /api/pruebas/notificaciones?celular=...` | Ver los SMS simulados enviados a un celular (por ejemplo, el código de desbloqueo) |
| `PUT /api/pruebas/saldo` | Fijar el saldo de un usuario: `{"celular": "...", "saldo": "100.00"}` |
| `POST /api/pruebas/procesar-diario` | Ejecutar el proceso diario (recargas programadas y débitos automáticos) con la fecha del reloj de la app |

> 💡 Para probar el proceso diario: fijen o adelanten el reloj al día que necesiten y luego llamen a `POST /api/pruebas/procesar-diario`.
>
> 💡 Si sus pruebas modifican datos (transferencias, bloqueos, límites), reinicien los datos antes de cada prueba o diseñen datos independientes. Así cumplen la propiedad *Independent* de FIRST.

---

## 6. Ejecutar las pruebas

Requisitos: Python 3.11 o superior y Node 22 o superior. Instalación, una sola vez:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
npm ci
npx playwright install chromium
```

**Terminal 1**: levantar Qolqe con una base de datos aislada.

```bash
source .venv/bin/activate
QOLQE_BD=.demo-data/qolqe.db QOLQE_MODO_PRUEBA=1 python -m uvicorn qolqe.main:app --port 8000
```

**Terminal 2**: ejecutar las suites con el entorno virtual activo (`source .venv/bin/activate`). Reinician los datos de esa instancia: no las ejecuten contra una base que quieran conservar. Para otro puerto, `QOLQE_URL=http://127.0.0.1:<puerto>` delante de cada comando.

| Qué | Sin imágenes (por defecto) | Con imágenes | Reporte |
|---|---|---|---|
| Etiquetas y trazabilidad (como el job `estatico`) | `npm run trazabilidad:verificar` | — | Consola: `334 casos, 0 errores` |
| API funcional y técnica, núcleo y G4 | `npm run test:api` | `npm run test:api:con-imagenes` | `reportes/api/reporte.html` y `junit.xml` |
| Contrato (Schemathesis, 19 operaciones) | `npm run test:contrato` | `EVIDENCIA=con-imagenes npm run test:contrato` | `reportes/contrato/html/`, `junit.xml` y, con imágenes, `peticiones.har` |
| Web, una vez | `npm run test:web` | `npm run test:web:con-imagenes` | `npx playwright show-report reportes/web/html` |
| Web, 3 veces seguidas (como el pipeline) | `npm run test:web:3x` | `EVIDENCIA=con-imagenes npm run test:web:3x` | Igual que la anterior |
| Matriz HU → CA → CP → resultado | `npm run trazabilidad` (lee `reportes/` y escribe `docs/trazabilidad.md` con "Run #local"; la versión que se entrega sale del artefacto `trazabilidad` de un run de `main`, ver `docs/pipeline.md`) | — | `docs/trazabilidad.md` |

Sin imágenes, la evidencia es solo de los fallos y de los defectos conocidos. Con imágenes, se guarda la evidencia de cada caso:
- en la web, captura, video y traza;
- en la API, peticiones y respuestas, con el token enmascarado.

Un subconjunto se corre así: `npm run test:web -- --grep CP-NW19` o `python -m pytest tests/api -k cpna97`.

`SLOWMO=700 npx playwright test --headed --grep "CP-W10"` muestra un recorrido en el navegador, a una velocidad que se puede seguir. `./scripts/preparar-demo.sh` deja lista la demo en vivo. Si Qolqe no está levantado, Playwright lo inicia solo con `.demo-data/e2e.db`.

### Ejecutar el workflow a pedido, con imágenes

- **Desde GitHub:** *Actions → Pruebas núcleo y G4 → Run workflow*, rama `main`, *evidencia*: `con-imagenes`, *Run workflow*.
- **Desde la terminal:** `gh workflow run pruebas.yml -R Joharjbe/qolqe-wallet --ref main -f evidencia=con-imagenes`

Los push y los PR usan `sin-imagenes`. Los artefactos con imágenes se guardan 7 días y los demás, 14. Qué hace cada job y por qué: [`docs/pipeline.md`](docs/pipeline.md).

### Kiwi TCMS (gestión de casos)

Guía completa, con la creación del usuario y la demo, en [`docs/gestion-casos.md`](docs/gestion-casos.md). En resumen:

```bash
cd herramientas/kiwi && ./generar-certificado.sh && docker compose up -d && cd ../..
docker exec -it qolqe_kiwi_web /Kiwi/manage.py initial_setup     # crea tu propio superusuario
.venv/bin/pip install -r requirements-gestion.txt
# Crear ~/.tcms.conf con la URL https://localhost:8443/xml-rpc/, tu usuario y tu clave (chmod 600)
.venv/bin/python scripts/kiwi_sincronizar.py --crear-plan
GH_TOKEN=$(gh auth token --user Joharjbe) KIWI_PLAN_ID=<id> .venv/bin/python scripts/kiwi_sincronizar.py --ultimos 20
```

Para ver qué se crearía sin conectarse a Kiwi: `GH_TOKEN=$(gh auth token --user Joharjbe) .venv/bin/python scripts/kiwi_sincronizar.py --simular --ultimos 20`. Cada run de `main` queda como un TestRun, y cada caso acumula todas sus ejecuciones.

### Pruebas de rendimiento (Parte 3)

k6 2.3.0 contra Qolqe en Docker con 1 CPU y 1 GB (puerto `127.0.0.1:8090`; no usa el 8000 ni el 8443). Requisitos: Docker Desktop, `brew install k6` (v2.3.0) y el `.venv` del repo. Guía completa, variables y qué deja cada corrida en [`tests/performance/README.md`](tests/performance/README.md).

```bash
tests/performance/preparar.sh 3000             # imagen, 3,000 usuarios de prueba y base_perf.db (el mismo día de las corridas)
tests/performance/correr.sh referencia         # 1 VU (≈ 1 min); luego: calibracion, carga, pico, estres, resistencia
TOP=2400 tests/performance/correr.sh estres    # rampa hasta 2,400 simultáneos, con perfiles de py-spy
tests/performance/correr.sh demo               # demo de clase (≈ 2.5 min, dashboard en http://localhost:5665)
```

Cada corrida queda en `tests/performance/resultados/<escenario>/<AAAAMMDD-HHMM>/` con el reporte HTML de k6, los CSV de recursos, la verificación del dinero, el veredicto por umbral y los gráficos. Resultados y análisis: [`docs/informe.md`](docs/informe.md) §4 y el informe con la plantilla del curso, [`docs/Informe_Rendimiento_Qolqe.docx`](docs/Informe_Rendimiento_Qolqe.docx) ([PDF](docs/Informe_Rendimiento_Qolqe.pdf)).

### Estructura

```
qolqe/                         # App bajo prueba (sin modificar)
features/                      # Casos en Gherkin con @HU, @CA, @CP, @DEF y @tecnico
  nucleo_*_api.feature         # Núcleo: registro, sesión, cuenta, transferencias, interbancaria, comisión, cierre
  contactos_api.feature  solicitudes_api.feature  g4_tecnico_api.feature
  web/nucleo_acceso_web.feature  web/nucleo_dinero_web.feature
  web/contactos_web.feature  web/solicitudes_web.feature
tests/
  api/conftest.py              # Cliente, sesiones, reinicio por escenario y pasos comunes
  api/pasos_*.py               # Pasos de pytest-bdd por área (núcleo acceso, núcleo dinero, G4)
  api/evidencia.py             # Peticiones y respuestas en el reporte HTML (sin o con imágenes)
  e2e/pages/                   # Page Objects y componentes compartidos (componentes.ts, PaginaQolqe.ts)
  e2e/steps/                   # Pasos de Playwright por área, sin localizadores
  e2e/fixtures.ts              # Páginas y datos de prueba preparados por la API
  performance/                 # Parte 3: k6, Docker, datos, monitores, verificación del dinero, análisis y resultados
scripts/
  correr-contrato.sh  contrato_hooks.py   # Contrato (Schemathesis)
  kiwi_sincronizar.py                     # Runs de GitHub → Kiwi TCMS
  preparar-demo.sh
schemathesis.toml              # Checks y operaciones excluidos, con su motivo
herramientas/kiwi/             # Kiwi TCMS con Docker (HTTPS en 8443)
.github/
  workflows/pruebas.yml        # Pipeline
  scripts/                     # casos.py, trazabilidad.py (matriz, JUnit por CP, historial) y resumen.py
docs/                          # Informe, arquitectura, alcance, pipeline, gestión de casos, defectos, trazabilidad y presentaciones
labs/s11-robot/                # Laboratorio S11 (Robot Framework), fuera del pipeline
IA.md                          # Declaración de uso de IA
```
