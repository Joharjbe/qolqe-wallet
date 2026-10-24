# Qolqe Wallet

Billetera digital **ficticia** usada como sistema bajo prueba (SUT) en el Proyecto 2 del curso **CS5383 Pruebas y Verificación de Software**.

> ⚠️ **Antes de empezar:**
> - **No modifiquen el código de la carpeta `qolqe/`.** Su trabajo es probarlo, no repararlo.
> - Todos los datos son ficticios.

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

## 6. Estructura sugerida del repositorio del grupo

```
qolqe/                    # App (NO modificar)
features/                 # Casos del módulo en Gherkin
tests/
  api/                    # Parte 1
  e2e/pages/              # Parte 2 (Page Objects)
  performance/            # Parte 3
docs/                     # Herramienta, trazabilidad, rendimiento, defectos
.github/workflows/        # Pipeline (Parte 2)
IA.md                     # Declaración de uso de IA
```

En `docs/` encontrarán la especificación de requisitos, la plantilla del informe del proyecto y la plantilla del reporte de defectos; en la raíz, la plantilla de `IA.md`.

---

## 7. Demo E2E del grupo 4: Robot Framework

El caso de [`tests/e2e/g4_solicitud_happy_path.robot`](tests/e2e/g4_solicitud_happy_path.robot) automatiza por la **interfaz web** este recorrido: Diego agrega a Bruno como contacto, le solicita S/ 25.00, Bruno acepta y ambos ven la solicitud aceptada. La prueba verifica también el código de operación y los saldos finales. Se aplica **Page Object** mediante los archivos de [`tests/e2e/pages/`](tests/e2e/pages/): la prueba expresa acciones de negocio y los localizadores están en recursos de cada pantalla.

### Instalación (una vez)

Usa Python 3.11 o superior. Los comandos siguientes corresponden a macOS o Linux. Desde la raíz de este repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-robot.txt
rfbrowser install chromium
```

La descarga de Chromium requiere conexión a internet. Si ya tienes el entorno creado para Qolqe, instala solo `requirements-robot.txt`.

### Ejecutar la demo

**Terminal 1** — iniciar Qolqe en modo de pruebas y con base de datos aislada:

```bash
source .venv/bin/activate
QOLQE_BD=.demo-data/qolqe.db QOLQE_MODO_PRUEBA=1 python -m uvicorn qolqe.main:app --host 127.0.0.1 --port 8000
```

**Terminal 2** — ejecutar y ver el navegador:

```bash
source .venv/bin/activate
python -m robot --variable HEADLESS:False --outputdir reportes tests/e2e/g4_solicitud_happy_path.robot
```

Para ejecutar sin ventana, omite `--variable HEADLESS:False`. Al terminar, abre `reportes/report.html` para el resultado y `reportes/log.html` para el detalle de cada paso. `reportes/output.xml` es el resultado legible por herramientas. Si usas otro puerto, pasa `--variable BASE_URL:http://127.0.0.1:PUERTO`.

**Atención:** antes de cada ejecución, la prueba llama a `/api/pruebas/reiniciar` y restaura los datos semilla de la instancia local indicada. No la ejecutes contra una base de datos que quieras conservar. El preparador rechaza direcciones remotas y exige que Qolqe esté en modo de pruebas.

### Qué se comprueba

| Paso | Evidencia esperada |
|---|---|
| Alta de contacto | Aparece «Bruno Demo» en la lista de Diego. |
| Solicitud | Mensaje de envío y estado «Pendiente» para S/ 25.00. |
| Aceptación | Estado «Aceptada» y código de operación visible para Bruno. |
| Efecto financiero | Bruno: S/ 775.00; Diego: S/ 2,525.00. |
| Visibilidad de ambos usuarios | Diego ve la misma solicitud como «Aceptada». |

Los datos iniciales proceden de la semilla del repositorio: Diego tiene S/ 2,500.00 y Bruno S/ 800.00. Las transferencias entre cuentas Qolqe tienen comisión S/ 0.00 (RN-09). Este caso cubre el camino válido de HU-G4-01, HU-G4-06, HU-G4-07 y HU-G4-08; no pretende cubrir todos los errores, condiciones de carrera ni los demás módulos. Consulta [`docs/demo-robot-ia.md`](docs/demo-robot-ia.md) para la demostración de IA y el guion de presentación.

La presentación final de 10 minutos está en [`docs/Presentacion_Robot_Framework_G4_visual.pptx`](docs/Presentacion_Robot_Framework_G4_visual.pptx). Cubre la herramienta, su evolución y arquitectura; muestra el patrón Page Object aplicado al código; guía la ejecución y las validaciones en vivo; incluye la revisión con IA y cierra con dificultades y límites. Sus notas indican los tiempos (0:00–10:00), las acciones de cada demo y las fuentes. Las capturas reales están en [`docs/capturas/`](docs/capturas/).
