# Diseño de las pruebas de rendimiento de Qolqe Wallet (P2, Parte 3)

> **Plan previo a las corridas** (11-nov-2026). Los cambios hechos al ejecutar (puerto 8090 en lugar de 8141, V-01, V-04, el TOP del estrés y el momento de py-spy) están en el informe, §5 y §6 ([`Informe_Rendimiento_Qolqe.docx`](Informe_Rendimiento_Qolqe.docx)). Los comentarios del código citan este documento como «diseño §N».

> Documento de diseño. Sirve para implementar `tests/performance/` y para llenar el *Template_Informe_Rendimiento.docx* (secciones 1 a 6). Cada valor lleva un ID (F, U, S, M o V) que lo enlaza con la frase del requerimiento de la que sale. Las cifras de costo por petición vienen de sondeos con un solo cliente en el puerto 8141, con el equipo ocupado: solo sirven como **hipótesis** y la calibración (§4.2) las reemplaza.

## 0. Decisiones base y convenciones

| Decisión | Elección | Razón principal (el detalle está en §6 y en la investigación de herramientas) |
|---|---|---|
| Herramienta | **k6 2.3.0** (`brew install k6 && brew pin k6`; 2.3.0 es la versión estable en Homebrew, verificado) | Tiene modelo abierto nativo (`constant-arrival-rate`, `ramping-arrival-rate`): la carga se expresa en **sesiones por hora**, igual que el requerimiento. También tiene umbrales como código con veredicto por código de salida (99), etiquetas por operación y reporte HTML (`K6_WEB_DASHBOARD_EXPORT`). |
| Entorno | **Docker**: Qolqe en un contenedor con `--cpus=1 --memory=1g`; k6 en macOS, en la misma Mac | Johar trabaja solo y tiene una sola Mac. La cuota separa el CPU de Qolqe del de k6, así se puede llegar al límite sin que la herramienta compita con la aplicación (§6). |
| Capa objetivo | **API** (☒ API) | Los umbrales hablan del tiempo en que "responde" la operación, que es el servidor. La web es una SPA estática que llama a los mismos endpoints. Se reproduce la secuencia exacta de peticiones de cada pantalla (`qolqe/web/static/app.js`), así que la carga en la API es la misma que genera la web. Simular 300 navegadores en una laptop mediría Chromium y no Qolqe. Los archivos estáticos quedan fuera (supuesto S-16: el navegador o una CDN los tiene en caché). |
| Modelo de carga | **Abierto** (por tasa de llegada) | Lo explica §3.1. |
| Puerto / BD | Qolqe en `127.0.0.1:8141` (nunca en el 8000). La BD va en un volumen Docker con nombre | |

IDs: **F** = flujo crítico · **U** = umbral · **S** = supuesto · **M** = valor del modelo · **V** = criterio de validez de una corrida.

---

## 1. Flujos críticos (mínimo tres) y criterio de selección

Se usan los criterios del enunciado: **frecuencia** (porcentaje de la tabla del requerimiento), **impacto en el dinero del usuario** y **riesgo** (técnico, con evidencia en el código, y de negocio).

| ID | Flujo | Endpoints (orden de `app.js`) | Frecuencia | Dinero | Riesgo (evidencia) | ¿Crítico? |
|---|---|---|---|---|---|---|
| F-01 | **Iniciar sesión** | `POST /api/auth/login` | Alta: 1 por sesión (0.83/s en hora punta, 2.5/s en campaña) | Indirecto: sin login no hay ninguna operación | **Alto.** PBKDF2-SHA256 con 200,000 iteraciones (`credenciales.py:13,24`) cuesta ≈ 45 ms de CPU, ≈ 65 % del CPU de una sesión. En la campaña "la mayoría inicia sesión en los primeros 5 minutos", así que la ráfaga cae sobre la operación más cara. RN-04: si falla 3 veces, bloqueo | **Sí** |
| F-02 | **Transferir a otro usuario Qolqe** | `GET /api/transferencias/comision` → `POST /api/transferencias` | 15 % | **Directo** | **Alto.** El antifraude duerme de 40 a 120 ms dentro de la operación (`operaciones.py:99-102`) y ocupa un hilo del pool. Hay una ventana de carrera entre validar y escribir (DEF-21). El requerimiento exige que ninguna quede "a medias ni aplicada dos veces" | **Sí** |
| F-03 | **Consultar saldo y perfil** | `GET /api/cuentas/me/saldo` + `GET /api/cuentas/me` | **30 %**, la más frecuente | Indirecto: el usuario verifica su dinero | Medio: 3 consultas con índice por petición autenticada (`dependencias.py`) | **Sí** |
| F-04 | **Recargar un celular** | `GET /api/recargas/configuracion` → `POST /api/recargas` | 10 % | **Directo** | Medio: `SCAN recargas` en cada recarga (sin índice). La tabla crece durante la resistencia. R-G1-03 aplica bajo carga | **Sí** |
| F-05 | **Pagar servicios** | `GET /api/servicios/empresas` → `GET /api/servicios/deudas` → `POST /api/servicios/pagos` | 4 % (+6 % que solo consulta) | **Directo** | Medio-alto: las deudas no tienen dueño (`servicios.py:105`), así que un pago duplicado da 409. Es la operación de dinero con menos muestras | **Sí** |
| F-06 | **Consultar movimientos** | `GET /api/movimientos` (30 días, página 1) | 15 % | No | **Alto técnico.** Consulta N+1: un `SUM` por cada fila del rango (`movimientos.py:113-123`), ≈ 243 consultas y 12 ms de CPU, con costo cuadrático respecto al historial | **Sí** (por riesgo técnico) |
| — | Ver y buscar contactos | `GET /api/contactos?pagina=1` + `GET /api/contactos?buscar=…` | 10 % | No | Bajo (`SCAN contactos` + B-tree temporal) | Carga de fondo |
| — | Otras (límites, alertas, solicitudes, dispositivos, sesiones) | 5 × GET, 2 % cada uno | 10 % | No | Bajo | Carga de fondo |

**Criterio aplicado.** Un flujo es crítico si cumple al menos dos de estas condiciones: frecuencia ≥ 15 %, mueve dinero, o tiene un riesgo alto con evidencia en el código. F-01 se incluye aunque no mueva dinero, porque todas las sesiones pasan por él.

Todos los flujos, críticos o no, forman parte de la mezcla: el perfil operacional tiene que estar completo. Los críticos tienen umbral propio por endpoint y se analizan primero.

---

## 2. Umbrales, supuestos y criterios de validez

### 2.1 Tabla de umbrales (métrica + percentil + valor límite + carga)

"Tiempo de respuesta" es `http_req_duration` de k6 (envío + espera + recepción). Coincide con la definición del curso: "desde que el cliente envía una petición hasta que recibe la respuesta completa". También se registra `http_req_connecting`: si su p95 pasa de 10 ms, en el análisis se suma al tiempo de respuesta. Los percentiles de las ventanas se calculan por **rango más cercano**, igual que en S14.

| ID | Frase del requerimiento | Métrica | Percentil / agregado | Límite | Carga | Escenario (fase) | Supuestos |
|---|---|---|---|---|---|---|---|
| U-01 | "Consultas e inicio de sesión: el 95 % debe responder en menos de 800 ms." | Tiempo de respuesta de **cada** endpoint de consulta y del login, y del grupo `consulta` | p95 | **< 800 ms** | 100 usuarios simultáneos (3,000 sesiones/h) | carga (`estable`), resistencia (`estable`) y criterio de capacidad en estrés | S-01, S-02, S-03 |
| U-02 | "Operaciones de dinero (transferencias, recargas y pagos): el 95 % debe responder en menos de 1.5 segundos." | Tiempo de respuesta de `POST /api/transferencias`, `POST /api/recargas` y `POST /api/servicios/pagos`, y del grupo `dinero` | p95 | **< 1,500 ms** | 100 simultáneos | ídem U-01 | S-01, S-03 |
| U-03 | "En hora punta, no más del 1 % de las operaciones puede fallar" | Tasa de error de rendimiento = operaciones fallidas ÷ operaciones totales (login incluido) | tasa | **≤ 1 %** | 100 simultáneos | carga, resistencia y criterio de capacidad | S-06 |
| U-04 | "…la plataforma debe sostener el volumen de la hora punta…" | Throughput atendido en el estado estable | promedio de la fase | **≥ 50 sesiones/min (3,000/h) y ≥ 9.6 req/s** (98 % de los 9.78 req/s ofrecidos, M-08) | 100 simultáneos | carga, resistencia | S-04 |
| U-05 | "…sin acumular retrasos." | (a) `dropped_iterations`; (b) p95 por ventana de 1 min; (c) sesiones simultáneas medidas | conteo; p95 por ventana; promedio por ventana | (a) **= 0**; (b) **ninguna ventana** sobre U-01/U-02; (c) **90–110** (100 ± 10 %) | 100 simultáneos | carga, resistencia | S-04 |
| U-06 | "Durante el pico de la campaña se acepta una degradación razonable del servicio" | Tiempo de respuesta por endpoint y grupo; tasa de error; sesiones descartadas; recuperación | p95; tasa; conteo | consultas **< 1,600 ms**, dinero **< 3,000 ms**; error **≤ 1 %**; descartadas **= 0**; recuperación: en 12:10–12:15 se vuelve a cumplir U-01/U-02 | Pico de 300 simultáneos (M-09) | pico (`campana:si`; `fase:recuperacion`) | S-05, S-07, S-08 |
| U-07 | "…ninguna operación de dinero puede quedar a medias ni aplicarse dos veces." | Descuadres en los 6 chequeos de integridad (§5.5) | conteo absoluto | **= 0** | Toda la corrida | **pico** (literal) y además todos los escenarios | S-09 |
| U-08 | "…hasta cuántos usuarios simultáneos podemos crecer antes de dejar de cumplir." | Capacidad = máximo de sesiones simultáneas con el que se cumplen U-01 a U-05 en ventanas de 30 s | máximo | Se **mide**: no es un límite que se pasa o se falla | Rampa de 100 a L_top | estrés | S-10 |
| U-09 | "Qolqe opera todos los días de 6:00 a 24:00 sin reinicios." | (a) U-01 a U-03 por ventana de 5 min; (b) RSS proyectado; (c) hilos y descriptores proyectados; (d) deriva del p95 | p95/tasa por ventana; regresión lineal | (a) todas las ventanas cumplen; (b) RSS a 54,000 sesiones **< 700 MB** (70 % de 1 GB, criterio de S13); (c) proyección ≤ 2× el valor inicial; (d) p95 de los últimos 10 min ≤ 1.2 × p95 de los primeros 10 | 100 simultáneos durante 60 min | resistencia | S-11, S-12 |

**Por qué U-07 es 0 y no < 1 %.** El curso advierte que un 0 % de error "casi nunca es alcanzable", pero eso se refiere a la **disponibilidad**. Una operación de dinero a medias o duplicada no es lentitud: es un defecto de integridad. El requerimiento la prohíbe sin tolerancia, así que el umbral correcto es 0.

### 2.2 Partes del requerimiento que no se pueden convertir tal cual, y supuesto tomado

| ID | Qué falta o es ambiguo | Supuesto tomado | Justificación |
|---|---|---|---|
| S-01 | Los umbrales de tiempo **no dicen con qué carga** se cumplen (S14: un umbral necesita métrica + percentil + valor + **carga**) | Se exigen en hora punta, con 100 simultáneos y 3,000 sesiones/h | Es la única carga "normal" que define el requerimiento. En campaña rige U-06 |
| S-02 | "Consultas" no dice qué peticiones incluye | Toda petición GET de la mezcla, incluidas las GET de apoyo dentro de una operación de dinero (comisión, configuración, empresas, deudas) | Responden datos sin mover dinero |
| S-03 | "El 95 %" puede leerse sobre todo el grupo o sobre cada operación | **Veredicto por endpoint** (más estricto) y también por grupo (lectura literal). Se reportan los dos | Un p95 de grupo puede pasar mientras todos los usuarios de un endpoint (por ejemplo, movimientos, ≈ 9 % del grupo) superan el límite |
| S-04 | "Sin acumular retrasos" no es un número | Modelo abierto. Retraso acumulado significa que la cola crece. Se mide con U-04 y U-05 (sesiones descartadas = 0, ninguna ventana sobre el umbral, sesiones simultáneas estables según la Ley de Little, throughput ≥ 98 % del ofrecido) | Con un modelo cerrado el generador frena cuando Qolqe se pone lento y el retraso queda oculto. La tolerancia del 98 % sale del cálculo: la mezcla aleatoria hace variar el total de peticiones en ±0.4 % (1 σ con 750 sesiones), así que 98 % deja unas 5 σ de margen |
| S-05 | "Degradación razonable" no es un número | p95 de hasta **2 ×** el umbral normal (consultas < 1,600 ms, dinero < 3,000 ms). La tasa de error sigue en ≤ 1 %, ninguna sesión se rechaza y se exige recuperación al volver la carga normal | La degradación que se acepta es de **velocidad**, no de fallos: una operación fallida en campaña significa pérdida de cliente o de dinero. Con 2 × los tiempos siguen debajo de 3 s, dentro de la franja de 1–10 s en la que el usuario nota la demora pero no abandona la tarea (aporte propio; Nielsen, 1993). Además se reporta el resultado frente a los umbrales normales, por si el negocio decide renegociar (paso 4 de S14). Cambiar el factor es una línea en `umbrales.js` |
| S-06 | "Operaciones que fallan" no está definido | Unidad = **operación de negocio** (si falla una de sus peticiones, falla la operación). Un **error de rendimiento** es un 5xx (incluido `database is locked`), un timeout del cliente (30 s), un error de conexión, una respuesta 2xx con cuerpo incorrecto o un 401 a mitad de sesión con token vigente. Los **4xx de regla de negocio** se cuentan aparte (V-02) | Así lo piden el enunciado (§5: "Sepárenlos en el análisis") y S14 (5xx, timeouts, "respuestas incorrectas") |
| S-07 | "El triple de usuarios simultáneos" no dice si es el máximo o el promedio de los 15 min | Es el **máximo**: 3 × 100 = **300 simultáneos** | Es la única lectura que cuadra con "la mayoría inicia sesión en los primeros 5 minutos" si las sesiones de campaña duran lo mismo que las normales (2 min). Mantener 300 durante los 15 min exigiría 150 sesiones/min constantes, y solo el 33 % entraría en los primeros 5 min, lo que contradice "la mayoría". Esa lectura igual queda cubierta por el estrés, que pasa por 300 de forma sostenida |
| S-08 | "La mayoría" no es un número | En 12:00–12:05 llegan 150 sesiones/min. En 12:05–12:15 se vuelve a la hora punta (50/min). Resultado: el **58 %** de las sesiones de campaña empieza en los primeros 5 min, y **todos** los usuarios adicionales de la campaña llegan en esos 5 min | Es la lectura que menos inventa: no hay una tasa nueva, solo la de hora punta y la que produce 300 simultáneos |
| S-09 | "A medias o dos veces" no dice cómo se verifica | Se comparan saldos y movimientos antes y después (§5.5) y se cruzan con los 201 que recibió k6. k6 **no reintenta** POST | Recomendación del enunciado (§5). Sin reintentos del cliente, un duplicado solo puede venir del servidor |
| S-10 | "Dejar de cumplir" no dice con qué criterio | Se usan los criterios de hora punta (U-01 a U-05). Capacidad = sesiones simultáneas de la última ventana que cumple antes de la primera falla sostenida (2 ventanas seguidas), redondeadas hacia abajo a 50 | Responde "hasta cuántos podemos crecer" con el mismo SLA que el día normal |
| S-11 | Solo se conoce el volumen de la hora punta; el resto del día no | Cota superior de un día: 18 h × 3,000 = **54,000 sesiones**. Las proyecciones se hacen **por sesión**, no por hora | Es conservador: ninguna hora del día tiene más carga que la hora punta |
| S-12 | No se pueden ejecutar 18 h antes de la entrega (12-nov, 23:59) | Resistencia de **60 min** en hora punta (la hora completa de mayor intensidad, 3,000 sesiones) y proyección a 54,000 sesiones | Se documenta en §6 de la plantilla, "Diferencias entre el plan y la ejecución real" |
| S-13 | La sesión dura 2 min, pero 6 pausas × 18 s = 108 s | Hay **12 s finales sin peticiones** (lectura del último resultado antes de cerrar la app) | No agrega carga: en el modelo abierto la carga la fija la tasa de llegada. Solo hace que "usuarios simultáneos" signifique lo mismo que en el requerimiento (L = 100) |
| S-14 | "Pausa de 10 a 25 s (18 s en promedio)": una uniforme entre 10 y 25 tiene media 17.5 s, no 18 | Se usa **triangular (10, 19, 25)**: rango de 10 a 25 y media exacta (10+19+25)/3 = 18 s | Cumple los dos datos del requerimiento con un solo supuesto (la moda) |
| S-15 | "Consultar deudas y pagar servicios (6 % consulta, 4 % pago)": para pagar hay que consultar antes | El 4 % de pagos **incluye** su consulta previa (empresas → deudas → pago). El 6 % se queda en la consulta | Así funciona la pantalla `/servicios` (`app.js:815, 860, 889`) |
| S-16 | La tabla no dice cuántas peticiones tiene cada operación, ni si hay logout | Las peticiones de cada pantalla según `app.js` (M-07). "Ver y buscar contactos" son 2 peticiones; "Otras" son 5 endpoints al 2 % cada uno; **sin logout** | El requerimiento describe la sesión como login + 6 operaciones y no menciona el cierre. El token vence a los 30 min |
| S-17 | La capacidad de producción es desconocida | Los resultados son una **línea base relativa** (§6) | Enunciado §5 y S13 ("no extrapolar") |

### 2.3 Criterios de validez de cada corrida (no son SLA)

| ID | Criterio | Fuente |
|---|---|---|
| V-01 | El CPU de k6 (psutil ÷ 10 núcleos) y el CPU total del equipo se mantienen **< 80 %** en todas las ventanas. Si no, la ventana o la corrida no vale | Enunciado §5 ("si supera ~80 %, el resultado no es válido") |
| V-02 | Errores de datos (4xx de negocio) **= 0**. Si superan el 0.1 % de las operaciones, se corrige el generador de datos y se repite la corrida | Enunciado §5 |
| V-03 | La mezcla lograda queda a ±2 puntos porcentuales de la pedida en cada operación | Rúbrica: "operaciones ponderadas" |
| V-04 | Antes de empezar, el equipo está libre (carga promedio de 1 min < 1.5, sin otras apps abiertas) y queda registrado | Enunciado §5 y S13 ("un servidor compartido introduce ruido") |
| V-05 | La base restaurada es idéntica a `base_perf.db` (Σ saldos, conteos e ids máximos), el proceso arranca de cero y `cpu.max = 100000 100000` | Que las corridas sean comparables |
| V-06 | Con 1 VU, el p95 de cada endpoint es ≤ 10 % de su umbral (el entorno no consume el margen) | Enunciado §5 (referencia de 1 VU) |
| V-07 | k6 no emite avisos de "insufficient VUs" en carga ni en resistencia | Que el generador sostenga la tasa |

Los niveles de S13 "CPU < 80 %, memoria < 70 %" **no** son SLA: el requerimiento no los pide. Se usan como alertas de diagnóstico, y el de memoria también en U-09(b).

---

## 3. Modelo de carga con todos los cálculos

### 3.1 Dos conceptos que el material no trae (aporte propio, en palabras simples)

- **Modelo abierto y modelo cerrado.** En el modelo **abierto**, los usuarios llegan a un ritmo fijo (50 por minuto) aunque Qolqe esté lento. Si Qolqe se atrasa, los usuarios se acumulan, y eso es justamente lo que el requerimiento pide detectar ("sin acumular retrasos"). En el modelo **cerrado** (el *Thread Group* de JMeter o `ramping-vus` de k6), hay un número fijo de usuarios que repiten la sesión. Si Qolqe se pone lento, esperan, llegan menos peticiones y el retraso se esconde. En k6 cada **iteración es una sesión**.
- **Ley de Little.** *Usuarios a la vez = usuarios que llegan por segundo × segundos que se queda cada uno* (L = λ·W). Ejemplo: si a un restaurante llegan 10 personas por hora y cada una se queda media hora, hay 5 mesas ocupadas. Con esta ley se traducen "sesiones por hora" a "usuarios simultáneos", y al revés.

### 3.2 Cálculos (M = valor del modelo)

| ID | Dato del requerimiento | Cálculo | Valor |
|---|---|---|---|
| M-01 | "se inician unas 3 000 sesiones por hora" | 3,000 ÷ 3,600 s | **λ = 0.833 sesiones/s = 50 sesiones/min** |
| M-02 | "Una sesión dura en promedio 2 minutos" | — | **W = 120 s** |
| M-03 | M-01 y M-02 | L = 0.833 × 120 | **L = 100 usuarios simultáneos** |
| M-04 | "pausa de 10 a 25 segundos (18 s en promedio) entre una y otra" | 6 pausas por sesión (después del login y entre cada par de operaciones, porque son 7 acciones). T ~ triangular(10, 19, 25), E[T] = 18 s | **6 × 18 = 108 s** |
| M-05 | M-02 − M-04 (S-13) | 120 − 108 | **12 s de cierre** sin peticiones |
| M-06 | Tabla de operaciones | Se sortean 6 operaciones por sesión, con reemplazo y con los pesos de la tabla | Ver M-07 |
| M-07 | Pantallas de `app.js` (S-15, S-16) | Peticiones por operación | Login 1 · Saldo y perfil 2 · Movimientos 1 · Transferir 2 · Contactos 2 · Recarga 2 · Consulta de deudas 2 · Pago 3 · Otras 1 |
| M-08 | M-06 y M-07 | Peticiones por operación: 0.30·2 + 0.15·1 + 0.15·2 + 0.10·2 + 0.10·2 + 0.06·2 + 0.04·3 + 0.10·1 = 1.79. Por sesión: 1 + 6 × 1.79 = **11.74**. Por segundo: 0.833 × 11.74 | **9.78 req/s** en hora punta (35,220 por hora); dinero: 0.833 × 6 × 0.29 = **1.45 POST/s**; logins **0.83/s**; operaciones de negocio: 0.833 × 7 = **5.83/s** |
| M-09 | "el triple de usuarios simultáneos… la mayoría inicie sesión en los primeros 5 minutos" (S-07, S-08) | L_pico = 3 × 100 = 300 → λ = 300 ÷ 2 min = 150/min en 12:00–12:05; 50/min en 12:05–12:15 | **150 → 50 sesiones/min**. Sesiones de campaña: 725 + 525 = 1,250, con un **58 %** en los primeros 5 min |
| M-10 | "la mayoría inicie sesión en los primeros 5 minutos" (salto) | La tasa se triplica en 30 s | Salto = **30 s** |
| M-11 | Hora punta antes del pico | 120 s de llenado + 120 s medidos | Base = **4 min** |
| M-12 | Hora punta 12:00–13:00 | Estado estable de 15 min: la tasa es la misma en toda la hora, 15 min son 750 sesiones (el 25 % de la hora) y el endpoint de dinero más escaso tiene ≥ 100 muestras (pagos: 0.2/s × 900 s = 180). La hora completa se ejecuta en la resistencia | **15 min estables** (17 min de llegadas) |
| M-13 | "6:00 a 24:00 sin reinicios" (S-11, S-12) | 60 min estables = 3,000 sesiones. Proyección a 18 × 3,000 | **60 min**, proyección a **54,000 sesiones** |
| M-14 | "hasta cuántos usuarios simultáneos" | L_sat = W ÷ D_sesión (1 CPU). Hipótesis: D ≈ 66–69 ms → L_sat ≈ 1,750–1,800. L_top = ⌈1.33 × L_sat⌉₁₀₀. Pendiente: +100 simultáneos por minuto | Hipótesis: **L_top = 2,400** (1,200 sesiones/min), rampa de 23 min. La calibración (§4.2) fija el valor final |
| M-15 | Técnico: techo del generador, no es carga | preAllocatedVUs ≈ 1.5 × L y maxVUs ≈ 2 × L (en estrés, 1.25 × L_top) | carga y resistencia 150/200 · pico 400/600 · estrés 2,500/3,000 · demo 200 + 50 |
| M-16 | "un usuario distinto por VU" | Usuarios = maxVUs del escenario más grande | **3,000 usuarios** (200 de la semilla + 2,800 creados por API) |
| M-24 | Calentamiento | = W (en 120 s se llena la concurrencia y se calienta la caché de SQLite) | **120 s**, que no entran en el veredicto |

**Lo que dice la Ley de Little sobre la rampa.** Con una tasa de llegada constante de 50/min, los usuarios simultáneos suben solos de 0 a 100 en exactamente 120 s, que es lo que dura una sesión. Por eso el ramp-up de carga y resistencia es **120 s**, y sale del dato M-02 (es la misma forma de "0 → 200 VUs en 2 min" que muestra S13).

**Duración de una sesión simulada.** Va de 72 s (mínimo: 6 × 10 + 12) a 162 s (máximo: 6 × 25 + 12), con media de 120 s más los tiempos de respuesta (≈ 0.3–0.6 s, que se miden en la referencia). La desviación estándar de las 6 pausas es √(6 × 9.5) ≈ 7.6 s, porque la varianza de una triangular(10, 19, 25) es 171/18 = 9.5 s².

### 3.3 Distribución de operaciones y volumen esperado

| Operación | % | ops/s (hora punta) | Peticiones por op | req/s hora punta | req/s pico (×3) | Peticiones en 15 min de carga |
|---|---|---|---|---|---|---|
| Login | 1 por sesión | 0.833 | 1 | 0.83 | 2.50 | 750 |
| Saldo y perfil | 30 | 1.50 | 2 | 3.00 | 9.00 | 2,700 |
| Movimientos | 15 | 0.75 | 1 | 0.75 | 2.25 | 675 |
| Transferir | 15 | 0.75 | 2 (comisión + **POST**) | 1.50 | 4.50 | 1,350 (675 POST) |
| Contactos | 10 | 0.50 | 2 | 1.00 | 3.00 | 900 |
| Recarga | 10 | 0.50 | 2 (configuración + **POST**) | 1.00 | 3.00 | 900 (450 POST) |
| Consulta de deudas | 6 | 0.30 | 2 | 0.60 | 1.80 | 540 |
| Pago | 4 | 0.20 | 3 (empresas + deudas + **POST**) | 0.60 | 1.80 | 540 (180 POST) |
| Otras (5 × 2 %) | 10 | 0.50 | 1 | 0.50 | 1.50 | 450 (90 por endpoint) |
| **Total** | 100 | **5.83** | 11.74 por sesión | **9.78** | **29.35** | **8,805** |

Con 90 muestras, el p95 de cada endpoint de "Otras" es poco estable. Para el veredicto se usa el grupo "otras" (450 muestras), y cada endpoint se reporta como información.

**CPU esperado de Qolqe (hipótesis: λ × 69 ms):** carga ≈ 6 % de 1 CPU · pico ≈ 17 % · estrés: 100 % con ≈ 1,750 simultáneos.

---

## 4. Escenarios

### 4.1 Resumen y tipos de prueba (Tabla 1 de la plantilla)

| Tipo | ¿Aplica? | Pregunta del requerimiento (el tipo lo define la pregunta, S13) | Patrón |
|---|---|---|---|
| **Carga** | ☒ Sí, **ejecutada** (obligatoria) | "si cumplimos en hora punta" y "sostener el volumen de la hora punta sin acumular retrasos". Es el caso A del ejercicio 1 de S13 | Llenado de 120 s → 15 min estables a 100 → drenaje |
| **Estrés** | ☒ Sí, **ejecutada** (obligatoria) | "hasta cuántos usuarios simultáneos podemos crecer antes de dejar de cumplir" y "qué tan lejos está de su límite". Caso D de S13: "¿se degrada con gracia o se cae?" | Rampa continua de 100 a L_top, más allá del límite estimado |
| **Pico (spike)** | ☒ Sí, **ejecutada** | Campaña "Quincena Qolqe": triple de usuarios y "la mayoría inicia sesión en los primeros 5 minutos". Caso B de S13: "salto abrupto" | 100 → salto ×3 en 30 s → 300 → vuelta a 100 |
| **Resistencia (soak)** | ☒ Sí, **ejecutada en versión de 60 min** | "opera todos los días de 6:00 a 24:00 sin reinicios". Caso C de S13: fugas de memoria, conexiones que no se liberan, logs que llenan el disco | 60 min constantes a 100, con proyección a 54,000 sesiones (S-12) |
| *(Referencia de 1 VU y calibración)* | Apoyo, no es un tipo | Línea base (enunciado §5) y D_sesión para fijar la cima del estrés | 1 VU |
| *(Escalabilidad)* | No está en la plantilla. **Opcional**, como evidencia del cuello de botella | "¿mejora al agregar CPU?" | Estrés con `--cpus=2` |

### 4.2 Configuración exacta en k6 (`k6/escenarios.js`)

En cada corrida se elige un solo escenario con `-e ESCENARIO=<nombre>`. No se usa la opción `--scenario`, así el script funciona en cualquier versión.

```js
// Todas las sesiones ejecutan exec:'sesion' (login + 6 operaciones + pausas), salvo donde se indica otra cosa.
export const ESCENARIOS = {
  referencia: { recorrido: { executor: 'per-vu-iterations', exec: 'recorrido', vus: 1, iterations: 5, maxDuration: '3m' } },
  calibracion: { calibracion: { executor: 'per-vu-iterations', exec: 'calibracion', vus: 1, iterations: 40, maxDuration: '5m' } },
  carga: { carga: { executor: 'constant-arrival-rate', exec: 'sesion', rate: 50, timeUnit: '1m',          // M-01
    duration: '17m', preAllocatedVUs: 150, maxVUs: 200, gracefulStop: '3m' } },                         // M-12, M-15
  pico: { pico: { executor: 'ramping-arrival-rate', exec: 'sesion', startRate: 50, timeUnit: '1m',
    preAllocatedVUs: 400, maxVUs: 600, gracefulStop: '3m',
    stages: [
      { duration: '4m',    target: 50  },   // 11:56–12:00 hora punta: llenado + base (M-11)
      { duration: '30s',   target: 150 },   // 12:00 salto ×3 (M-10)
      { duration: '4m30s', target: 150 },   // hasta 12:05: la mayoría inicia sesión; 300 simultáneos desde ~12:02:30 (M-09)
      { duration: '30s',   target: 50  },   // 12:05 vuelve la llegada normal
      { duration: '9m30s', target: 50  },   // hasta 12:15: resto de la campaña y recuperación
    ] } },
  estres: { estres: { executor: 'ramping-arrival-rate', exec: 'sesion', startRate: 50, timeUnit: '1m',
    preAllocatedVUs: 2500, maxVUs: 3000, gracefulStop: '2m',
    stages: [
      { duration: '3m',  target: 50 },          // base: 100 simultáneos
      { duration: '23m', target: TOP / 2 },     // TOP = L_top de la calibración (hipótesis 2400 → 1200/min); +100 simultáneos por min
      { duration: '2m',  target: TOP / 2 },     // meseta más allá del límite
    ] } },
  resistencia: { resistencia: { executor: 'constant-arrival-rate', exec: 'sesion', rate: 50, timeUnit: '1m',
    duration: '62m', preAllocatedVUs: 150, maxVUs: 200, gracefulStop: '3m' } },                         // M-13
  demo: {
    demo_hora_punta: { executor: 'constant-arrival-rate', exec: 'sesion', rate: 50, timeUnit: '1m',
      duration: '100s', preAllocatedVUs: 150, maxVUs: 200, gracefulStop: '0s' },
    demo_sin_pausa:  { executor: 'constant-vus', exec: 'sesionSinPausa', vus: 50, duration: '45s',
      startTime: '100s', gracefulStop: '0s' },
  },
};
```

**Fases** (etiqueta `fase`, calculada como `(Date.now() − exec.scenario.startTime)/1000` en cada petición). Los umbrales de k6 solo miran la fase que corresponde, así el código de salida ya es el veredicto sobre el estado estable.

| Escenario | Fases (segundos desde el inicio) |
|---|---|
| carga | `calentamiento` 0–120 · **`estable` 120–1020** · `drenaje` > 1020 |
| pico | `calentamiento` 0–120 · **`base`** 120–240 · **`salto`** 240–540 (12:00–12:05) · `resto` 540–840 · **`recuperacion`** 840–1140 (12:10–12:15) · `drenaje`. Además, `campana=si` en 240–1140 |
| estres | `base` 0–180 · **`rampa`** 180–1560 · **`meseta`** 1560–1680 · `drenaje` |
| resistencia | `calentamiento` 0–120 · **`estable` 120–3720** · `drenaje` |

**Qué se mide y qué es obligatorio**

| Escenario | Obligatorio | Duración (máquina) | Mide | Veredicto |
|---|---|---|---|---|
| referencia | Apoyo | ≈ 2 min | p50/p95 de cada endpoint con 1 VU (recorre las 12 operaciones y el login, 5 veces, con pausa de 1 s) | V-06 |
| calibracion | Apoyo | ≈ 3 min | D_sesión = Δ`usage_usec` de `cpu.stat` ÷ 40 sesiones con la mezcla y pausa de 0.5 s → L_sat = 120 ÷ D → TOP | Fija M-14 |
| carga | **Sí** | 17 + 3 min | U-01 a U-05, recursos, U-07 | Pasa o falla |
| pico | Justificado (ejecutado) | 19 + 3 min | U-06 y U-07, recursos, recuperación | Pasa o falla |
| estres | **Sí** | 28 + 2 min | Capacidad U-08, patrón de degradación, perfil py-spy, throttling | Capacidad N |
| resistencia | Justificado (60 min) | 62 + 3 min | U-09, U-01 a U-05 por ventana de 5 min, tendencias | Pasa o falla |

**Por qué se ejecutan pico y resistencia.** El requerimiento describe de forma explícita un evento de pico (la campaña) y una operación de 18 h sin reinicios. Por la regla de S13, el plan combina "carga para validar el día normal, pico para simular el día de vencimiento y resistencia para verificar la operación continua". Los dos caben en el tiempo de máquina disponible (§10).

**Por qué el estrés es una rampa continua y no una escalera.** Es el formato del ejercicio 3 de S14 (0 → 500 VUs en 20 min, leído en T1 a T4). Con el mismo tiempo da una resolución de ±50 usuarios. En el modelo abierto la concurrencia va unos 60 s detrás de la tasa, por eso el eje X usa las **sesiones simultáneas medidas** de cada ventana, no la tasa programada. Si la confirmación es opcional y sobra tiempo, se hace una corrida de 10 min a L_cap y otra a 1.15 × L_cap (§10).

### 4.3 Tabla 2 de la plantilla (modelo de carga), lista para copiar

| Parámetro | Carga | Pico | Estrés | Resistencia |
|---|---|---|---|---|
| VUs (usuarios simultáneos) | 100 (modelo abierto, 50 sesiones/min; k6 reserva 150 y como máximo 200) | 100 → **300** → 100 | 100 → L_top (hipótesis 2,400) | 100 |
| Ramp-up (s) | 120 (llenado natural = W) | 120 + salto de 30 | 1,380 (rampa) | 120 |
| Duración (s) | 1,020 de llegadas (900 medidos) + ≤ 180 de drenaje | 1,140 (campaña 900) + ≤ 180 | 1,680 + ≤ 120 | 3,720 (3,600 medidos) + ≤ 180 |
| Think time (ms) | 10,000–25,000, triangular con moda de 19,000 y **media de 18,000**; más 12,000 de cierre | ídem | ídem | ídem |
| Distribución de operaciones (%) | Login 1 por sesión; saldo y perfil 30; movimientos 15; transferir 15; contactos 10; recarga 10; consulta de deudas 6; pago 4; otras 10 (2 cada una) | ídem | ídem | ídem |

En "Origen de los valores" se copian M-01 a M-16 y S-07, S-08, S-13 y S-14.

### 4.4 Esqueleto del script (`k6/qolqe.js`)

```js
import http from 'k6/http'; import { sleep, check } from 'k6'; import exec from 'k6/execution';
import { SharedArray } from 'k6/data'; import { Rate, Counter } from 'k6/metrics';
import { ESCENARIOS, fasesDe } from './escenarios.js'; import { UMBRALES } from './umbrales.js';
import { OPERACIONES, login } from './operaciones.js';

const ESC = __ENV.ESCENARIO || 'carga';
export const USUARIOS = new SharedArray('usuarios', () => open('../datos/usuarios.csv').trim().split('\n').slice(1)
  .map(l => { const [vu, celular, pin, id, suministro, contactos] = l.split(',');
              return { celular, pin, id: +id, suministro, contactos: contactos.split('|').map(Number) }; }));
export const options = { scenarios: ESCENARIOS[ESC], thresholds: UMBRALES[ESC],
  summaryTrendStats: ['avg', 'min', 'med', 'p(90)', 'p(95)', 'p(99)', 'max'] };
http.setResponseCallback(http.expectedStatuses({ min: 200, max: 499 }));   // http_req_failed = solo 5xx y red

const MEZCLA = [['saldo_perfil', 30], ['movimientos', 15], ['transferir', 15], ['contactos', 10], ['recarga', 10],
  ['deudas', 6], ['pago', 4], ['limites', 2], ['alertas', 2], ['solicitudes', 2], ['dispositivos', 2], ['sesiones', 2]];
function elegir() { let r = Math.random() * 100; for (const [op, p] of MEZCLA) if ((r -= p) < 0) return op; return 'saldo_perfil'; }
// S-14: triangular(10, 19, 25) → rango 10–25 s, media 18 s
function pausa() { const u = Math.random();
  return u < 0.6 ? 10 + Math.sqrt(u * 135) : 25 - Math.sqrt((1 - u) * 90); }       // 135 = 15·9, 90 = 15·6

export function sesion() {
  const u = USUARIOS[exec.vu.idInTest - 1];          // C4: un usuario distinto y fijo por VU
  const token = login(u);                            // F-01
  if (token) for (let i = 0; i < 6; i++) { sleep(pausa()); OPERACIONES[elegir()](u, token); }
  sleep(12);                                         // S-13: cierre sin peticiones
}
export function sesionSinPausa() { const u = USUARIOS[exec.vu.idInTest - 1]; const t = login(u);
  if (t) for (let i = 0; i < 6; i++) OPERACIONES[elegir()](u, t); }       // "estrés disfrazado" (S13), solo para la demo
```

`operaciones.js` tiene una función por operación con las peticiones de M-07. Cada petición lleva las etiquetas `ep` (por ejemplo `login`, `saldo`, `perfil`, `movimientos`, `comision`, `transferir`, `contactos_listar`, `contactos_buscar`, `recargas_config`, `recargar`, `empresas`, `deudas`, `pagar`, `limites`, …), `op` (operación de la mezcla), `grupo` (`consulta` o `dinero`), `fase`/`campana` y `name` (por ejemplo `GET /api/movimientos`, para el reporte), y `timeout: '30s'`. Clasifica cada respuesta así (S-06):

```js
// status 0 (timeout/conexión) o ≥ 500 → error de rendimiento; 2xx con cuerpo inválido → error de rendimiento;
// 4xx con body.codigo de regla de negocio → errores_datos{codigo} (V-02), no cuenta en U-03;
// POST de dinero con status 0 → dinero_sin_respuesta (resultado desconocido, se concilia en §5.5).
const operacionFallida = new Rate('operacion_fallida');          // U-03: una muestra por operación
const erroresDatos = new Counter('errores_datos'), dineroConfirmado = new Counter('dinero_confirmado'),
      dineroSinRespuesta = new Counter('dinero_sin_respuesta');
```

`umbrales.js` genera los umbrales desde dos listas de `ep` (15 de consulta y 3 de dinero). Cada umbral lleva un comentario con su ID U y la frase del requerimiento. Ejemplo para carga:

```js
'http_req_duration{fase:estable,grupo:consulta}': ['p(95)<800'],     // U-01 (grupo, lectura literal)
'http_req_duration{fase:estable,ep:login}':       ['p(95)<800'],     // U-01 (por endpoint, S-03), uno por cada ep de consulta
'http_req_duration{fase:estable,grupo:dinero}':   ['p(95)<1500'],    // U-02, más uno por transferir/recargar/pagar
'operacion_fallida{fase:estable}':                ['rate<=0.01'],    // U-03
'dropped_iterations':                             ['count==0'],      // U-05(a)
```

En pico se aplican sobre `{campana:si}` los límites de 1,600/3,000 ms, error ≤ 1 % y descartadas = 0, y sobre `{fase:base}` y `{fase:recuperacion}` los normales. En estrés solo hay una red de seguridad: `operacion_fallida: [{ threshold: 'rate<0.2', abortOnFail: true, delayAbortEval: '2m' }]`; la capacidad la calcula el análisis. En la demo los umbrales se filtran por `{scenario:demo_hora_punta}` y `{scenario:demo_sin_pausa}`. U-04, U-05(b, c) y U-09 los calcula `analisis/analizar.py` por ventanas.

---

## 5. Datos de prueba

### 5.1 Qué necesita cada VU

| Operación | Dato | Cómo se garantiza | Regla que se evita romper |
|---|---|---|---|
| Login | Usuario propio y PIN correcto | VU n → fila n de `usuarios.csv` (celular `900000000 + n`, PIN 2580). Nunca se usan los ids 1 a 6: Elena, por ejemplo, está bloqueada en la semilla | RN-04 (bloqueo por 3 fallos) |
| Transferir | Destino que sea otro usuario Qolqe; monto | `contacto_id` al azar entre sus 5 contactos. Monto uniforme entre S/ 1.00 y S/ 20.00 con 2 decimales | RN-05 (≤ 500), RN-06 (peor caso por VU en 62 min: 52 sesiones × 0.9 × 10.5 ≈ S/ 491 < S/ 2,000), RN-07 |
| Recarga | Número y monto | Número aleatorio `95XXXXXXX`, distinto en cada recarga. Monto al azar de {5, 10, 20, 30, 50, 100} | R-G1-01, R-G1-03 (5 al día por número; nunca se llega) |
| Consulta de deudas y pago | Suministro con deudas pendientes que solo use ese VU | Suministro propio `printf('5%09d', id)` con **30 deudas** AGUA sin mora. Se paga la primera pendiente | 404 `SIN_DEUDA_PENDIENTE` y 409 `DEUDA_YA_PAGADA`. Peor caso: 52 sesiones × 0.24 = 12.5 pagos por VU, así que 30 da más de 5 σ de margen |
| Contactos | 5 contactos | Anillo: el usuario i agrega a i+1 … i+5, con alias `Amigo NNNN`. Búsqueda por el alias de uno de ellos | R-G4-03 (≤ 15) |
| Movimientos | El mismo historial para todos | 1,000 movimientos en 120 días, ≈ 243 en 30 días. Es el perfil de la semilla, clonado a los usuarios creados por API | Si los usuarios nuevos tuvieran historial vacío, el costo del N+1 bajaría justo cuando hay más carga y el estrés mediría de menos |
| Saldo | Suficiente | S/ 10,000 vía `PUT /api/pruebas/saldo`. Gasto esperado por VU en el peor caso (62 min): ≈ S/ 2,000 | RN-08 (`SALDO_INSUFICIENTE`) |

### 5.2 Generador (`datos/preparar_datos.py`) y cantidades

Se ejecuta **una sola vez**, con un contenedor de preparación con `--cpus=4`, porque la preparación no se mide.

1. `POST /api/pruebas/reiniciar` deja 200 usuarios de carga: 900000001 a 900000200, ids 7 a 206, S/ 10,000, 1,000 movimientos y 1 deuda cada uno. Es el endpoint de soporte que pide el enunciado, D2.
2. `POST /api/usuarios` para los usuarios 201 a 3,000, con 4 hilos: DNI sintético único, nombre `Carga NNNN`, celular `900000NNN` y PIN 2580 (≈ 1 min).
3. `PUT /api/pruebas/saldo` en S/ 10,000 para los 3,000 (el otro endpoint de soporte, D2).
4. `POST /api/contactos` × 5 por usuario, previo login. Se hace por API para que los datos respeten las reglas por construcción (≈ 1 min).
5. `sqlite3 < datos/preparar_bd.sql` para lo que la API **no** permite: clonar el historial y crear las 30 deudas por usuario. No toca `qolqe/`, solo el archivo de datos.
6. Exporta `datos/usuarios.csv` con las columnas `vu,celular,pin,usuario_id,suministro,contactos` (los ids de los contactos separados con `|`).
7. Verifica los conteos (3,000 usuarios, 15,000 contactos, 90,000 deudas pendientes, ≈ 3 M movimientos) y `PRAGMA integrity_check`. Luego hace `.backup /data/base_perf.db` (≈ 540 MB).

Reglas:

- **Nunca** se llama a `reiniciar` entre corridas, porque borra a los usuarios creados por la API.
- Antes de **cada** corrida se restaura `base_perf.db` y se reinicia el contenedor, así cada corrida arranca con un proceso nuevo, la misma base y el reloj en hora real.
- La base se genera **el mismo día** de las corridas (los vencimientos y la ventana de 30 días son relativos a la fecha).
- Ninguna corrida cruza la medianoche de Lima, porque los límites diarios se reinician.

### 5.3 Asignación usuario ↔ VU

Se usa `exec.vu.idInTest` (de 1 a maxVUs, único en la prueba). Un VU ejecuta una sola sesión a la vez y sus operaciones son secuenciales: **nunca hay dos sesiones simultáneas sobre el mismo usuario**, que es lo que pide el enunciado (D1) y evita provocar DEF-21. No se usa `iterationInTest` ni un CSV compartido con reciclaje.

Efecto colateral que se declara: en la resistencia cada usuario hace unas 30 sesiones por hora, más que un usuario real. Su historial de hoy crece y su `sesiones` acumula filas. Si aparece deriva en `movimientos`, se distingue con datos (filas por usuario antes y después) de una fuga de memoria.

### 5.4 Clasificación de errores

| Clase | Condición | Ejemplos | Dónde cuenta |
|---|---|---|---|
| Correcta | 2xx esperado y check del cuerpo correcto | 200, 201 | — |
| **Error de datos** | 4xx con `codigo` de regla de negocio | 422 `SALDO_INSUFICIENTE`, `LIMITE_DIARIO_EXCEDIDO`, `LIMITE_RECARGAS`, `MONTO_*`; 404 `SIN_DEUDA_PENDIENTE`; 409 `DEUDA_YA_PAGADA`; 423 `CUENTA_BLOQUEADA`; 401 `CREDENCIALES_INVALIDAS` | `errores_datos{codigo}` → V-02. Se reporta aparte y no entra en U-03 |
| **Error de rendimiento** | 5xx, status 0 (timeout de 30 s, conexión rechazada o reiniciada), 2xx con cuerpo inválido, 401 a mitad de sesión con token vigente | 500 `database is locked` (cuando vence `busy_timeout` de 10 s) | `operacion_fallida` → U-03 |
| Dinero sin respuesta | POST de dinero con status 0 | Timeout | `dinero_sin_respuesta` → conciliación C6 |

### 5.5 Verificación del dinero antes y después (U-07)

Como cada corrida restaura la base, **"antes" = `base_perf.db`** (V-05 lo comprueba con checksum). **"Después"** = `/data/qolqe.db` sin tráfico. `verificacion/verificar.py` se ejecuta dentro del contenedor (`docker exec -i qolqe-perf python - < verificar.py`), en modo solo lectura, y escribe `verificacion_dinero.txt`:

| Chequeo | Qué compara | Correcto |
|---|---|---|
| C1 Conservación | Σ saldos después − Σ saldos antes = −(recargas + pagos + comisiones interbancarias nuevas). Las transferencias Qolqe suman cero | descuadre 0 |
| C2 Libro mayor | Por usuario: Δsaldo = Σ importes de sus movimientos nuevos | 0 filas |
| C3 Operación ↔ movimientos | Por código: cada transferencia tiene 1 ENVIADA + 1 RECIBIDA; cada recarga y cada pago, 1 movimiento; no hay movimientos huérfanos. Se agrupa por código y tipo para no confundir DEF-22 con un duplicado | 0 filas |
| C4 Pagos | Ninguna `deuda_id` pagada dos veces; toda deuda `PAGADA` tiene su pago, y al revés | 0 filas |
| C5 Reglas | Ningún saldo negativo; ninguna suma diaria de transferencias por encima del límite (síntomas de DEF-21) | 0 filas |
| C6 Conteos | Filas nuevas por tipo en la BD comparadas con `dinero_confirmado{ep}` de k6. Exceso ≤ `dinero_sin_respuesta` significa "aplicada sin confirmación" y se explica. Si la BD tiene menos que los 201 de k6, hay operaciones confirmadas sin guardar (riesgo de DEF-07) | Diferencia explicada |

---

## 6. Entorno

### 6.1 Elección para este caso: **Docker**, `--cpus=1 --memory=1g --memory-swap=1g`

| Opción | Para Johar (trabaja solo, tiene una Mac M1 Pro) | Decisión |
|---|---|---|
| Local | Qolqe dispone de 10 núcleos: el PBKDF2 y SQLite liberan el GIL y escalan, así que saturarlo exigiría miles de VUs **en el mismo CPU**. La herramienta competiría con la aplicación (regla del 80 %). Además macOS tiene `somaxconn=128` y `maxfiles=256` (comprobado) | No |
| Dos equipos | No tiene una segunda laptop. En la red de la universidad, además, se necesitaría el punto de acceso del celular | No aplica |
| Codespaces | La latencia de internet se suma al tiempo de respuesta y no se puede aislar. El entorno es compartido y ruidoso, el puerto es público, y la demo dependería del Wi-Fi del aula | No |
| **Docker** | La cuota fija 1 CPU para Qolqe y le deja 9 núcleos libres a k6, así que no compiten. El límite es reproducible entre corridas y no depende de otras apps. `docker stats` y `cpu.stat` miden el contenedor de forma directa. El límite se alcanza con una cantidad de VUs manejable, de modo que el estrés **sí encuentra** el límite. Es el ejemplo del propio enunciado, se parece a una instancia pequeña de 1 vCPU y la misma imagen sirve para la demo en clase | **Sí** |

Detalles que se documentan:

- Imagen `python:3.11.15-slim-bookworm` (arm64, ya descargada), con un solo proceso de uvicorn como pide el README y `--host 0.0.0.0` dentro del contenedor.
- Se instala con `-c constraints.txt` (FastAPI 0.117.1, que evita DEF-07) y versiones fijadas iguales a las del `.venv`. Se guarda `pip freeze` en `resultados/entorno/`.
- La BD va en un volumen con nombre, no en un *bind mount*.
- El puerto se publica como `-p 127.0.0.1:8141:8141`.
- Se registra `cpu.max` y `memory.max` (deben dar `100000 100000` y `1073741824`).

### 6.2 Especificaciones (para §6 de la plantilla)

- Apple M1 Pro, 10 núcleos (8 de rendimiento y 2 de eficiencia), 16 GB.
- macOS 27.2.1.
- Docker Desktop: motor 29.8.2, VM de 10 CPU y 8 GB.
- Qolqe limitado a 1 CPU y 1 GB.
- k6 2.3.0 en el host.
- Antes de cada corrida: `ulimit -n 10240`, equipo enchufado, sin modo de bajo consumo y sin otras apps (V-04).

### 6.3 Limitaciones conocidas (para §6 de la plantilla)

- El proxy de puertos de Docker Desktop suma latencia en Qolqe y CPU en el host. Por eso se mide la referencia de 1 VU en Docker (V-06) y el CPU total del equipo.
- `--cpus=1` es una cuota, no un `cpuset`: dentro del contenedor `nproc` sigue dando 10. Los hilos que hacen PBKDF2 en paralelo gastan la cuota antes de tiempo y sufren *throttling*, que se ve en `nr_throttled` y `throttled_usec`.
- macOS puede programar la vCPU en núcleos de eficiencia.
- La memoria del cgroup incluye la caché de páginas de la base. La memoria del proceso se toma como RSS con psutil.
- La resistencia dura 60 min y no 18 h (S-12).
- Se usa SQLite con un solo proceso, igual que en el entorno entregado.

**Frase de línea base relativa (va textual en §6):** "Los resultados son una **línea base relativa** de Qolqe en un contenedor de 1 CPU y 1 GB dentro de una laptop. **No son la capacidad de producción.** Sirven para comparar versiones y configuraciones (por ejemplo, 1 contra 2 CPU) y para ubicar el primer cuello de botella. No deben extrapolarse ('soporta N usuarios en la laptop, entonces soporta N en producción')."

---

## 7. Mediciones, gráficos y estructura de resultados

### 7.1 Qué se recoge en cada corrida (todas, incluidas la referencia y la demo)

| Archivo | Contenido | Origen |
|---|---|---|
| `corrida.json` | Escenario, **hora de inicio y fin** (hora de Lima, ISO, con epoch), commit, versiones (k6, Docker, digest de la imagen), `cpu.max` y `memory.max`, `cpu.stat` antes y después, carga del equipo antes de empezar (V-04), checksum de la base (V-05), parámetros (λ, TOP), código de salida de k6 | `correr.sh` |
| `consola.txt` | Salida de k6 con los umbrales ✓/✗ | `k6 run … \| tee` |
| `resumen.json` | Resumen de k6 (`handleSummary`, que conserva también el resumen de consola) | k6 |
| `reporte.html` | **Reporte de la herramienta**: dashboard exportado (`K6_WEB_DASHBOARD=true K6_WEB_DASHBOARD_EXPORT=…`, período de 10 s) | k6 |
| `muestras.csv.gz` → `peticiones.csv.gz` | Datos crudos (`--out csv=…csv.gz`, timestamp en ms; verificar `K6_CSV_TIME_FORMAT=unix_milli` en 2.3) y la versión compacta: ts, ep, op, grupo, fase, status, duración, `error_code` | k6 y `analizar.py` |
| `recursos_qolqe.csv` | `hora,cpu_%,memoria_MB` (el formato del script del enunciado) más `ts,hilos,descriptores`, cada 1 s, sobre el **PID 1 de Qolqe** | `monitor.py` en un contenedor auxiliar con `--pid=container:qolqe-perf`, así su CPU no se descuenta de la cuota de Qolqe |
| `recursos_docker.csv` | `hora,ts,cpu_%,memoria_MB,memoria_%,pids` (100 % = 1 CPU) | `monitor_docker.py` (`docker stats`) |
| `recursos_k6.csv` | `hora,ts,cpu_%,memoria_MB,cpu_k6_equipo_%,cpu_total_equipo_%` (V-01) | `monitor.py` en el host, sobre el PID de k6 |
| `verificacion_dinero.txt` | C1 a C6 (§5.5) | `verificar.py` |
| `tabla_resumen.md/.csv` | Formato de S14: endpoint, peticiones, promedio, p50, p90, p95, p99, error, throughput (fase medida) | `analizar.py` |
| `veredicto.md` | Cada U y V con el valor medido, el umbral y si pasa o falla. Errores de datos y de rendimiento por separado. Mezcla lograda | `analizar.py` |
| `graficos/*.png` | §7.2 | `graficos.py` |
| (estrés) `perfil_base.svg`, `perfil_saturacion.svg`, `hilos_meseta.txt` | py-spy `record --nonblocking` de 60 s en la base y al llegar a 0.9 × L_sat; `dump` en la meseta | Contenedor auxiliar con `SYS_PTRACE` |
| `qolqe.log.gz` | `docker logs` (log de acceso; su crecimiento interesa en la resistencia) | `correr.sh` |

### 7.2 Gráficos (la plantilla pide "a lo largo de la prueba"; la rúbrica, "p95, tasa de error y throughput comparados, con gráficos")

Ventanas: 1 min en carga, 30 s en pico y estrés, 5 min en resistencia (y 1 min para U-05).

| Gráfico | Contenido | Escenarios |
|---|---|---|
| G1 Tiempo de respuesta | p50 y p95 por ventana de los grupos `consulta` y `dinero`, más login y transferir, con líneas de umbral (800/1,500; en pico también 1,600/3,000) y las fases sombreadas | todos |
| G2 Throughput | req/s atendidas contra ofrecidas (λ × 11.74), y sesiones iniciadas y completadas por minuto contra la tasa de llegada | todos |
| G3 Errores | % por ventana, apilado: rendimiento (por tipo) y datos (por código), con la línea del 1 % | todos |
| G4 Usuarios simultáneos | Medidos (calculados de `iteration_duration`: inicio = fin − duración, contrastado con `vus`) contra los esperados por Little | todos |
| G5 Recursos | CPU de Qolqe (% de 1 CPU) y throttling, RSS, CPU de k6 y del equipo con la línea del 80 %, en el mismo eje de tiempo | todos |
| G6 p95 contra usuarios simultáneos | Por endpoint crítico, con umbrales y la marca de capacidad | estrés |
| G7 Throughput contra usuarios | Rodilla de saturación (el patrón de S14: "los VUs suben pero el throughput baja") | estrés |
| G8 CPU contra usuarios | Lo compara con la recta de la Ley de utilización (U = X·D) | estrés |
| G9 RSS contra sesiones acumuladas | Regresión y proyección a 54,000 | resistencia |
| G10 Hilos y descriptores en el tiempo | | resistencia |
| G11 Comparativo | p95 por endpoint crítico en cada escenario contra su umbral | `comparativo/` |

En estrés también se arma la tabla del ejercicio 3 de S14 (una fila por momento T1…Tn, cada 100 usuarios): VUs, p50, p95, error, throughput, CPU, memoria, hilos y throttling.

### 7.3 Estructura

```
tests/performance/resultados/
├── entorno/            entorno.json (specs, versiones), pip_freeze.txt, cgroup.txt
├── referencia/  calibracion/  carga/  pico/  estres/  resistencia/  demo/
│     └── corrida.json consola.txt resumen.json reporte.html peticiones.csv.gz recursos_*.csv
│         verificacion_dinero.txt tabla_resumen.md veredicto.md graficos/
├── comparativo/        G11, tabla de veredictos de todos los escenarios
└── descartadas/<escenario>_<AAAAMMDD-HHMM>/motivo.txt   (corridas inválidas: se conservan y se explica el motivo)
```

`.gitignore` excluye `*.db` y los `muestras.csv.gz` de más de 50 MB. Se versiona `peticiones.csv.gz`, la versión compacta.

---

## 8. Método de análisis (S14: ¿pasó? → ¿dónde? → ¿por qué? → ¿qué hacer?)

1. **¿Pasó o falló?** Se da un veredicto binario por umbral (`veredicto.md` y el código de salida de k6) **antes** de mirar los gráficos. Primero se confirman V-01 a V-07: si una no se cumple, la corrida no se analiza y se repite. Los errores de datos y los de rendimiento se reportan por separado.
2. **¿Dónde falló?** Endpoint, métrica, momento (ventana) y cantidad de usuarios simultáneos (G1, G4, G6).
3. **¿Por qué?** Se cruza el momento de la falla con los recursos (G5, G8), se identifica el patrón (gradual, abrupto o periódico) y se contrastan las hipótesis:

| H | Cuello candidato (evidencia en el código) | Qué se vería si es el cuello | Qué lo descarta |
|---|---|---|---|
| H1 | **CPU por el PBKDF2 del login** (`credenciales.py:13,24`) | El login es el primero en superar 800 ms. CPU de Qolqe ≈ 100 % y `nr_throttled` en aumento. py-spy: la mayoría de las muestras en `verificar_pin`. Patrón **gradual**. La rodilla real cerca de L_sat = W/D. Con `--cpus=2` la capacidad se acerca a ×2 | El CPU está < 70 % cuando falla, o falla primero otro endpoint |
| H2 | **CPU por el N+1 del historial** (`movimientos.py:113-123`) | `movimientos` tiene la mayor razón p95/p95_ref. py-spy: `listar` en `movimientos.py:118` | Su razón es menor que la del login |
| H3 | **Pool de 40 hilos de AnyIO**. El antifraude duerme de 40 a 120 ms (`operaciones.py:101`) | Los hilos llegan a 40 o más (psutil). El p95 sube con CPU < 80 %. Patrón **abrupto** (como "el pool de conexiones se llenó" de S14). `py-spy dump`: hilos en `time.sleep` o en espera | Hilos < 40 en la meseta |
| H4 | **SQLite**: un escritor, `synchronous=FULL`, `busy_timeout` de 10 s (`bd.py:207-212`) | Aparecen 500 `database is locked`. Los POST se degradan antes que los GET. py-spy en `commit`/`execute`. Si hay picos **periódicos**, el checkpoint de WAL | No hay 500 y GET y POST se degradan juntos |
| H5 | **Memoria** | RSS crece sin parar y el p95 empeora con el tiempo en la resistencia | RSS plano (G9) |
| H6 | **Generador o entorno** | CPU de k6 o del equipo > 80 %, o errores de conexión con Qolqe ocioso | V-01 se cumple |

**Hipótesis previa** (se valida o se refuta): H1 primero. La capacidad estaría en unos **1,500 ± 300 simultáneos** (cerca de 15 veces la hora punta y 5 veces la campaña), y el pico y la carga pasarían con margen (≈ 6 % y 17 % de CPU).

**Ley de utilización** (aporte propio): si cada sesión gasta D segundos de CPU, 1 CPU alcanza para 1/D sesiones por segundo. La rodilla observada se compara con la predicha.

4. **¿Qué hacer?** Son recomendaciones, no cambios al código, que es de solo lectura:
   - escalar con más CPU o más procesos (la evidencia es el estrés con `--cpus=2`; para varios procesos habría que sacar el reloj de memoria);
   - no bajar las iteraciones de PBKDF2 (OWASP recomienda subirlas), sino reducir cuántas veces se hace login (renovación de token) o mover el *hashing* a un pool o proceso propio;
   - una sala de espera virtual para la ráfaga de la campaña;
   - corregir el N+1 con `SUM() OVER (…)` y paginar en SQL;
   - agregar índices en `recargas`, `alertas`, `contactos` y en las tablas por usuario;
   - usar una clave de idempotencia en las operaciones de dinero (riesgo de duplicado si el cliente reintenta tras un timeout);
   - o renegociar el SLA de la campaña.

**Redacción de resultados** (modelo de S13): "Con **100 usuarios simultáneos** (3,000 sesiones/h, perfil operacional de la hora punta), el **p95** de `POST /api/transferencias` fue **X ms**, dentro del umbral de **1,500 ms**; la tasa de error fue Y %, frente al umbral de 1 %."

Hallazgos funcionales que se registran como defectos, fuera del alcance de rendimiento:

- `GET /api/movimientos` no incluye los movimientos de hoy: `m.fecha BETWEEN 'AAAA-MM-DD' AND 'AAAA-MM-DD'` deja fuera las marcas de hora de hoy (`movimientos.py:85`), lo que contradice R-G3-01.
- El límite de recargas permite 6 en lugar de 5 (R-G1-03).

---

## 9. Demostración en vivo (exposición de 15 min; el arranque debe caber en la transición de 5–10 min)

**Antes de la clase:**

- Docker Desktop abierto, la imagen construida, la base restaurada y el contenedor arriba (`until curl -sf …/api/salud`).
- Tres paneles: k6, `docker stats qolqe-perf` y el navegador en `http://localhost:5665`.
- Respaldo: un video grabado del ensayo y los `reporte.html` de las corridas completas.

**En vivo: `tests/performance/correr.sh demo` (≈ 2 min 30 s, menos de 3 min):**

| Tiempo | Qué se ve | Mensaje |
|---|---|---|
| 0:00–1:40 | `demo_hora_punta`: 50 sesiones/min con las pausas reales. En el dashboard, los usuarios simultáneos suben solos (Little) y el p95 de consulta y dinero queda bajo las líneas. El CPU de Qolqe en `docker stats` ronda el 6 % | "Modelo abierto: así se ve la hora punta" |
| 1:40–2:25 | `demo_sin_pausa`: 50 VUs sin think time. El CPU se clava en 100 % y el p95 del login supera 800 ms | "Un modelo de carga sin think time es una prueba de estrés disfrazada" (S13) |
| 2:25–2:30 | Resumen de k6: los umbrales de `demo_hora_punta` en ✓ y los de `demo_sin_pausa` en ✗. Código de salida **99** | La herramienta decide si pasa o falla: es el paso 1 de S14 |
| 2:30–2:40 | `verificar.py` da **0 descuadres** | U-07 |

Después se muestran los gráficos ya generados de carga, pico, estrés (capacidad) y resistencia. Johar trabaja solo, así que tiene que poder explicar cada fila de §2 y §3.

---

## 10. Archivos a implementar y orden de ejecución

### 10.1 Archivos (`tests/performance/`; `qolqe/` no se toca)

```
tests/performance/
├── README.md                    cómo preparar, correr cada escenario y la demo; estructura de resultados; trazabilidad U/S/M
├── config.env                   PUERTO=8141, CONTENEDOR=qolqe-perf, IMAGEN=qolqe-perf:p3, VOLUMEN=qolqe-perf-datos, CPUS=1, MEMORIA=1g
├── requirements.txt             psutil, pandas, matplotlib (análisis y monitores)
├── preparar.sh                  build → contenedor de preparación (--cpus=4) → preparar_datos.py → base_perf.db → contenedor de medición (--cpus=1)
├── correr.sh <escenario>        V-04 (espera equipo libre) → restaura la base y reinicia el contenedor → V-05 → monitores → k6 → hora de inicio y fin
│                                → cpu.stat → (estrés: py-spy programado) → verificar → analizar → gráficos
├── docker/Dockerfile            python:3.11.15-slim-bookworm, -c constraints.txt, psutil y py-spy, CMD uvicorn --host 0.0.0.0 --port 8141
├── docker/Dockerfile.dockerignore  **, !requirements.txt, !constraints.txt, !qolqe/**
├── k6/qolqe.js                  sesión, mezcla ponderada, pausa triangular, recorrido, calibración, sesionSinPausa
├── k6/operaciones.js            una función por operación (peticiones de app.js), etiquetas y clasificación de errores
├── k6/escenarios.js             §4.2 y las fases por escenario; TOP se toma de -e TOP=…
├── k6/umbrales.js               §4.4; cada umbral con su ID U y la frase del requerimiento
├── datos/preparar_datos.py      §5.2 (reiniciar, registro, PUT saldo, contactos por API, SQL, CSV, verificación, backup)
├── datos/preparar_bd.sql        historial clonado y 30 deudas por usuario
├── datos/usuarios.csv           generado (3,000 filas)
├── monitor/monitor.py           script psutil del enunciado: hora,cpu_%,memoria_MB + ts,hilos,descriptores (+ CPU del equipo con --equipo)
├── monitor/monitor_docker.py    docker stats → CSV
├── verificacion/verificar.py    C1–C6 sobre base_perf.db y qolqe.db, más la conciliación con resumen.json
├── verificacion/verificar_dinero.sql
├── analisis/analizar.py         ventanas, percentil por rango más cercano, veredicto U/V, mezcla, capacidad U-08, proyecciones U-09
├── analisis/graficos.py         G1–G11 y la tabla T1…Tn del estrés
└── resultados/                  §7.3
(opcional) jmeter/carga.jmx      contraste: diseñado en la GUI y ejecutado con jmeter -n -t … -l … -e -o …
```

Fuera de `tests/performance/`:

- `docs/informe.md`: §4 y la fila "Herramienta de rendimiento" de §1.
- El informe hecho con la plantilla (`docs/Informe_Rendimiento_Parte3.docx`).
- La presentación de la Entrega 3.
- El tag `parte-3`.

### 10.2 Orden de ejecución y tiempo de máquina

| # | Paso | Comando | Tiempo | Por qué en este orden |
|---|---|---|---|---|
| 0 | Preparación del equipo: el otro trabajo terminó (carga < 1.5), apps cerradas, `ulimit -n 10240`, `brew install k6 && brew pin k6` | — | 5 min | V-04 |
| 1 | Construir la imagen y verificar las versiones (`pip freeze` igual al `.venv`, FastAPI 0.117.1) | `docker build -f tests/performance/docker/Dockerfile -t qolqe-perf:p3 .` | 3 min | |
| 2 | Preparar los datos y la base | `tests/performance/preparar.sh 3000` | 5–8 min | Una sola vez, el mismo día |
| 3 | Referencia de 1 VU | `correr.sh referencia` | 3 min | Valida el script y los datos (V-06) |
| 4 | Calibración | `correr.sh calibracion`, que da D y TOP | 4 min | Fija la cima del estrés (M-14) |
| 5 | **Carga** | `correr.sh carga` | 22 min | Responde la pregunta principal |
| 6 | **Pico** | `correr.sh pico` | 24 min | |
| 7 | **Estrés** (+ py-spy) | `TOP=<calibrado> correr.sh estres` | 33 min | Usa la calibración |
| 8 | **Resistencia** | `correr.sh resistencia` | 67 min | Va al final para correr sin supervisión mientras se redacta |
| 9 | Análisis y comparativo | `python analisis/graficos.py --todo` | 3 min | |
| 10 | Ensayo de la demo (×2) | `correr.sh demo` | 6 min | |
| | **Total obligatorio** | | **≈ 2 h 55 min** | |
| Opc. 1 | Escalabilidad (evidencia de H1) | `CPUS=2 TOP=… correr.sh estres` | 33 min | La evidencia más fuerte del cuello |
| Opc. 2 | Confirmar la capacidad: 10 min a L_cap y a 1.15 × L_cap | `correr.sh capacidad` | 26 min | |
| Opc. 3 | Contraste con JMeter (carga, 10 min estables) | `jmeter -n -t …` | 20 min | Refuerza la comparación de herramientas |

Hay que reservar ≈ 1 h para repetir corridas inválidas. Ninguna corrida debe empezar entre las 23:00 y las 00:30 de Lima. Todo debe estar terminado antes del 12-nov a las 23:59 (tag `parte-3` y envío en Canvas).

### 10.3 Riesgos del diseño y mitigación

| Riesgo | Mitigación |
|---|---|
| Otro trabajo ocupa el CPU | `correr.sh` espera a que la carga baje de 1.5 y lo registra (V-04) |
| La memoria de k6 con 3,000 VUs (≈ 1–3 MB por VU) | Se vigila en `recursos_k6.csv`. Si hace falta, se baja `preAllocatedVUs` a 1,500 y k6 inicializa el resto sobre la marcha |
| uvicorn cierra el keep-alive a los 5 s y las pausas son de 10 a 25 s | Se abre una conexión nueva después de cada pausa (se ve en `http_req_connecting`). Si aparecen errores EOF o de reinicio de conexión, se usa `noConnectionReuse: true` |
| El contenedor de preparación tiene `--cpus=4` | Se recrea con `--cpus=1` y se verifica `cpu.max` en cada corrida (V-05) |
| Archivos crudos demasiado grandes | Se comprimen con gz, se versiona la versión compacta y se aplica `.gitignore` |
| Se llama a `reiniciar` por error | Prohibido en `correr.sh`: solo se restaura `base_perf.db` |
| py-spy sin `--native` en ARM64 | Igual alcanza: el tiempo del PBKDF2 se atribuye a `verificar_pin (credenciales.py:24)` |