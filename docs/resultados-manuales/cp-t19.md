# CP-T19 · Aceptar frente a cancelar o rechazar la misma solicitud a la vez

Evidencia manual del caso CP-T19, que en [`alcance-y-casos.md`](../alcance-y-casos.md) («Lo que no se automatizó») figuraba sin cifra y sin defecto. Ahora lleva estas cifras y DEF-30. Se midió el 17-nov-2026 con [`herramientas/mediciones/cp_t19.py`](../../herramientas/mediciones/cp_t19.py).

**Resultado.** El comportamiento no es correcto. En 118 de 200 rondas del modo cancelar y en 136 de 200 del modo rechazar, las dos operaciones respondieron 200 y la solicitud terminó ACEPTADA, con el dinero movido. En las demás rondas ganó cancelar o rechazar, como debe ser. Se registró un defecto nuevo, [DEF-30](../defectos.md#def-30-cancelar-o-rechazar-a-la-vez-que-se-acepta-responde-200-y-el-dinero-igual-se-mueve).

## Qué se probó

**La regla.** Aceptar, rechazar y cancelar exigen que la solicitud esté PENDIENTE; si no lo está, responden 409 `ESTADO_INVALIDO` ([`requisitos.md`](../requisitos.md): HU-G4-08 CA4, HU-G4-09 CA1 y HU-G4-10 CA1). Si dos de esas operaciones llegan a la vez sobre la misma solicitud, solo una puede encontrarla PENDIENTE. La otra tiene que recibir 409.

**Los datos.** Diego le solicita S/ 25.00 a Bruno, la misma solicitud de CP-T17. Con la semilla, Bruno tiene S/ 800.00 y Diego S/ 2,500.00.

**Los dos modos.**
- **cancelar:** Bruno acepta y Diego, el solicitante, cancela. Son dos personas que actúan a la vez.
- **rechazar:** Bruno acepta y Bruno rechaza, por ejemplo desde dos dispositivos.

**El oráculo.** Una ronda es correcta solo en uno de estos dos casos:

| Gana | Respuestas | Estado final | Saldos (Bruno · Diego) |
|---|---|---|---|
| aceptar | aceptar 200 · la otra 409 `ESTADO_INVALIDO` | ACEPTADA | S/ 775.00 · S/ 2,525.00 |
| cancelar o rechazar | la otra 200 · aceptar 409 `ESTADO_INVALIDO` | CANCELADA o RECHAZADA | S/ 800.00 · S/ 2,500.00 |

Cualquier otra combinación es incorrecta.

**Qué se mira, y por qué.**
- El código de cada respuesta y el estado que trae cada 200: es lo que la aplicación le dijo a cada usuario.
- El estado final y los dos saldos: es lo que pasó de verdad con el dinero.
- Los SMS que recibe Diego: es lo que ve el solicitante.

**Cómo se asegura que sea a la vez.** Igual que en los escenarios `@concurrencia` (`_a_la_vez` en `tests/api/pasos_g4_extra.py`, el ayudante de CP-T17): un hilo y una conexión por petición, la conexión calentada con `GET /api/salud` antes de la barrera y las dos peticiones liberadas con `threading.Barrier`. Así el saludo TCP no separa las peticiones. La salida informa el desfase de salida entre las dos: como máximo 0.19 ms en las 5 corridas.

**Por qué rondas independientes.** Cada ronda empieza con el reloj real y `POST /api/pruebas/reiniciar`, como el fixture `s` de `tests/api/conftest.py`. Así una ronda no hereda saldos ni solicitudes de la anterior.

**Por qué 5 corridas de 40 rondas.** Dan 200 rondas por modo. Es el número que la regla de concurrencia de [`defectos.md`](../defectos.md) pide para automatizar un caso, así que el resultado se puede comparar directamente con esa regla.

## Cómo se reproduce

El script usa solo la biblioteca estándar: `urllib.request` para preparar cada ronda, y `http.client` y `threading` para la ráfaga. La ráfaga no usa `urllib.request` porque abre y cierra una conexión por petición, y así no se puede calentar la conexión antes de la barrera. Desde la raíz del repositorio:

```bash
# 1. Qolqe en el puerto 8765, con una base nueva fuera del repositorio.
D=$(mktemp -d)
QOLQE_BD=$D/qolqe.db QOLQE_BD_PLANTILLA=$D/plantilla_carga.db QOLQE_MODO_PRUEBA=1 \
  .venv/bin/python -m uvicorn qolqe.main:app --host 127.0.0.1 --port 8765 > "$D/uvicorn.log" 2>&1 &
curl -sf --retry 60 --retry-delay 1 --retry-connrefused http://127.0.0.1:8765/api/salud

# 2. Cinco corridas de 40 rondas por modo (sale con 1 si alguna ronda es incorrecta).
for i in 1 2 3 4 5; do python3 herramientas/mediciones/cp_t19.py --rondas 40; done
python3 herramientas/mediciones/cp_t19.py --rondas 5 --detalle   # una línea por ronda

# 3. Apagar Qolqe y borrar la base temporal.
lsof -ti:8765 | xargs kill
rm -r "$D"
```

**Por qué así.**
- **Puerto 8765 y base propia.** El script reinicia los datos en cada ronda. En el 8000 corren la demo (`scripts/preparar-demo.sh`) y las suites locales (`tests/api/conftest.py`, `playwright.config.ts`), y sus datos no se deben pisar.
- **`QOLQE_BD_PLANTILLA` también.** Sin esa variable, Qolqe usa la plantilla de `datos/` o la reconstruye ahí si tiene 7 días o más (`qolqe/config.py`, `qolqe/semilla.py`). Con las dos rutas en la carpeta temporal, la base sale nueva de la semilla del proyecto y el repositorio no cambia.
- **FastAPI 0.117.1.** Es la versión que fija `constraints.txt` y la que tiene `.venv`. Con 0.118 o más, el `commit` llega después de la respuesta (DEF-07), y el estado y los saldos que el script lee justo después de la ráfaga podrían estar desactualizados.

**Entorno de la medición.** Commit `1025a78`, sin cambios en `qolqe/`. Python 3.11.6, FastAPI 0.117.1, uvicorn 0.54.0, SQLite en modo WAL (`qolqe/semilla.py`). macOS 27.2.1, Apple M1 Pro con 10 núcleos. Base nueva en una carpeta temporal, creada desde la semilla al levantar el servidor.

## Salida real

**Resumen de las 5 corridas** (las cifras salen de la salida de abajo):

| Corrida | cancelar: incorrectas | rechazar: incorrectas |
|---|---:|---:|
| 1 | 21 de 40 | 27 de 40 |
| 2 | 26 de 40 | 27 de 40 |
| 3 | 29 de 40 | 27 de 40 |
| 4 | 20 de 40 | 30 de 40 |
| 5 | 22 de 40 | 25 de 40 |
| **Total** | **118 de 200** | **136 de 200** |

En las 400 rondas ganó aceptar 0 veces. Todas las rondas incorrectas dieron la misma combinación: las dos peticiones con 200 y la solicitud ACEPTADA.

**Las 5 corridas**, tal como las imprimió la versión publicada del script:

```text
CP-T19 · 2026-11-17 22:56:31 · http://127.0.0.1:8765 · Qolqe 1.0.0 · Python 3.11.6 · Darwin arm64

Modo cancelar: Bruno acepta y Diego cancela la misma solicitud, 40 rondas
  correctas: 19 de 40 (gana aceptar 0, gana cancelar 19) · incorrectas: 21
  combinaciones observadas:
     21 × aceptar 200 ACEPTADA · cancelar 200 CANCELADA · estado ACEPTADA · Bruno 775.00 · Diego 2525.00 · SMS a Diego: 1 «aceptó», 0 «rechazó»
     19 × aceptar 409 ESTADO_INVALIDO · cancelar 200 CANCELADA · estado CANCELADA · Bruno 800.00 · Diego 2500.00 · SMS a Diego: 0 «aceptó», 0 «rechazó»
  duración mediana: aceptar 54.6 ms · cancelar 2.6 ms · desfase de salida máximo 0.08 ms

Modo rechazar: Bruno acepta y Bruno rechaza la misma solicitud, 40 rondas
  correctas: 13 de 40 (gana aceptar 0, gana rechazar 13) · incorrectas: 27
  combinaciones observadas:
     27 × aceptar 200 ACEPTADA · rechazar 200 RECHAZADA · estado ACEPTADA · Bruno 775.00 · Diego 2525.00 · SMS a Diego: 1 «aceptó», 1 «rechazó»
     13 × aceptar 409 ESTADO_INVALIDO · rechazar 200 RECHAZADA · estado RECHAZADA · Bruno 800.00 · Diego 2500.00 · SMS a Diego: 0 «aceptó», 1 «rechazó»
  duración mediana: aceptar 83.0 ms · rechazar 3.3 ms · desfase de salida máximo 0.06 ms

Total: 48 rondas incorrectas de 80 · 24.4 s

CP-T19 · 2026-11-17 22:56:55 · http://127.0.0.1:8765 · Qolqe 1.0.0 · Python 3.11.6 · Darwin arm64

Modo cancelar: Bruno acepta y Diego cancela la misma solicitud, 40 rondas
  correctas: 14 de 40 (gana aceptar 0, gana cancelar 14) · incorrectas: 26
  combinaciones observadas:
     26 × aceptar 200 ACEPTADA · cancelar 200 CANCELADA · estado ACEPTADA · Bruno 775.00 · Diego 2525.00 · SMS a Diego: 1 «aceptó», 0 «rechazó»
     14 × aceptar 409 ESTADO_INVALIDO · cancelar 200 CANCELADA · estado CANCELADA · Bruno 800.00 · Diego 2500.00 · SMS a Diego: 0 «aceptó», 0 «rechazó»
  duración mediana: aceptar 64.7 ms · cancelar 3.3 ms · desfase de salida máximo 0.04 ms

Modo rechazar: Bruno acepta y Bruno rechaza la misma solicitud, 40 rondas
  correctas: 13 de 40 (gana aceptar 0, gana rechazar 13) · incorrectas: 27
  combinaciones observadas:
     27 × aceptar 200 ACEPTADA · rechazar 200 RECHAZADA · estado ACEPTADA · Bruno 775.00 · Diego 2525.00 · SMS a Diego: 1 «aceptó», 1 «rechazó»
     13 × aceptar 409 ESTADO_INVALIDO · rechazar 200 RECHAZADA · estado RECHAZADA · Bruno 800.00 · Diego 2500.00 · SMS a Diego: 0 «aceptó», 1 «rechazó»
  duración mediana: aceptar 70.8 ms · rechazar 3.5 ms · desfase de salida máximo 0.19 ms

Total: 53 rondas incorrectas de 80 · 26.8 s

CP-T19 · 2026-11-17 22:57:22 · http://127.0.0.1:8765 · Qolqe 1.0.0 · Python 3.11.6 · Darwin arm64

Modo cancelar: Bruno acepta y Diego cancela la misma solicitud, 40 rondas
  correctas: 11 de 40 (gana aceptar 0, gana cancelar 11) · incorrectas: 29
  combinaciones observadas:
     29 × aceptar 200 ACEPTADA · cancelar 200 CANCELADA · estado ACEPTADA · Bruno 775.00 · Diego 2525.00 · SMS a Diego: 1 «aceptó», 0 «rechazó»
     11 × aceptar 409 ESTADO_INVALIDO · cancelar 200 CANCELADA · estado CANCELADA · Bruno 800.00 · Diego 2500.00 · SMS a Diego: 0 «aceptó», 0 «rechazó»
  duración mediana: aceptar 77.0 ms · cancelar 3.5 ms · desfase de salida máximo 0.12 ms

Modo rechazar: Bruno acepta y Bruno rechaza la misma solicitud, 40 rondas
  correctas: 13 de 40 (gana aceptar 0, gana rechazar 13) · incorrectas: 27
  combinaciones observadas:
     27 × aceptar 200 ACEPTADA · rechazar 200 RECHAZADA · estado ACEPTADA · Bruno 775.00 · Diego 2525.00 · SMS a Diego: 1 «aceptó», 1 «rechazó»
     13 × aceptar 409 ESTADO_INVALIDO · rechazar 200 RECHAZADA · estado RECHAZADA · Bruno 800.00 · Diego 2500.00 · SMS a Diego: 0 «aceptó», 1 «rechazó»
  duración mediana: aceptar 65.9 ms · rechazar 3.5 ms · desfase de salida máximo 0.06 ms

Total: 56 rondas incorrectas de 80 · 26.4 s

CP-T19 · 2026-11-17 22:57:48 · http://127.0.0.1:8765 · Qolqe 1.0.0 · Python 3.11.6 · Darwin arm64

Modo cancelar: Bruno acepta y Diego cancela la misma solicitud, 40 rondas
  correctas: 20 de 40 (gana aceptar 0, gana cancelar 20) · incorrectas: 20
  combinaciones observadas:
     20 × aceptar 409 ESTADO_INVALIDO · cancelar 200 CANCELADA · estado CANCELADA · Bruno 800.00 · Diego 2500.00 · SMS a Diego: 0 «aceptó», 0 «rechazó»
     20 × aceptar 200 ACEPTADA · cancelar 200 CANCELADA · estado ACEPTADA · Bruno 775.00 · Diego 2525.00 · SMS a Diego: 1 «aceptó», 0 «rechazó»
  duración mediana: aceptar 29.0 ms · cancelar 3.0 ms · desfase de salida máximo 0.05 ms

Modo rechazar: Bruno acepta y Bruno rechaza la misma solicitud, 40 rondas
  correctas: 10 de 40 (gana aceptar 0, gana rechazar 10) · incorrectas: 30
  combinaciones observadas:
     30 × aceptar 200 ACEPTADA · rechazar 200 RECHAZADA · estado ACEPTADA · Bruno 775.00 · Diego 2525.00 · SMS a Diego: 1 «aceptó», 1 «rechazó»
     10 × aceptar 409 ESTADO_INVALIDO · rechazar 200 RECHAZADA · estado RECHAZADA · Bruno 800.00 · Diego 2500.00 · SMS a Diego: 0 «aceptó», 1 «rechazó»
  duración mediana: aceptar 84.5 ms · rechazar 3.4 ms · desfase de salida máximo 0.05 ms

Total: 50 rondas incorrectas de 80 · 24.6 s

CP-T19 · 2026-11-17 22:58:13 · http://127.0.0.1:8765 · Qolqe 1.0.0 · Python 3.11.6 · Darwin arm64

Modo cancelar: Bruno acepta y Diego cancela la misma solicitud, 40 rondas
  correctas: 18 de 40 (gana aceptar 0, gana cancelar 18) · incorrectas: 22
  combinaciones observadas:
     22 × aceptar 200 ACEPTADA · cancelar 200 CANCELADA · estado ACEPTADA · Bruno 775.00 · Diego 2525.00 · SMS a Diego: 1 «aceptó», 0 «rechazó»
     18 × aceptar 409 ESTADO_INVALIDO · cancelar 200 CANCELADA · estado CANCELADA · Bruno 800.00 · Diego 2500.00 · SMS a Diego: 0 «aceptó», 0 «rechazó»
  duración mediana: aceptar 52.7 ms · cancelar 2.9 ms · desfase de salida máximo 0.04 ms

Modo rechazar: Bruno acepta y Bruno rechaza la misma solicitud, 40 rondas
  correctas: 15 de 40 (gana aceptar 0, gana rechazar 15) · incorrectas: 25
  combinaciones observadas:
     25 × aceptar 200 ACEPTADA · rechazar 200 RECHAZADA · estado ACEPTADA · Bruno 775.00 · Diego 2525.00 · SMS a Diego: 1 «aceptó», 1 «rechazó»
     15 × aceptar 409 ESTADO_INVALIDO · rechazar 200 RECHAZADA · estado RECHAZADA · Bruno 800.00 · Diego 2500.00 · SMS a Diego: 0 «aceptó», 1 «rechazó»
  duración mediana: aceptar 64.7 ms · rechazar 2.9 ms · desfase de salida máximo 0.03 ms

Total: 47 rondas incorrectas de 80 · 23.1 s
```

**Una corrida con `--detalle`** (5 rondas por modo), para ver las duraciones de cada petición:

```text
CP-T19 · 2026-11-17 22:58:36 · http://127.0.0.1:8765 · Qolqe 1.0.0 · Python 3.11.6 · Darwin arm64

Modo cancelar: Bruno acepta y Diego cancela la misma solicitud, 5 rondas
  ronda 01 · aceptar 200 ACEPTADA · cancelar 200 CANCELADA · estado ACEPTADA · Bruno 775.00 · Diego 2525.00 · SMS a Diego: 1 «aceptó», 0 «rechazó» · 67.4 ms / 3.3 ms · desfase 0.03 ms → INCORRECTA
  ronda 02 · aceptar 200 ACEPTADA · cancelar 200 CANCELADA · estado ACEPTADA · Bruno 775.00 · Diego 2525.00 · SMS a Diego: 1 «aceptó», 0 «rechazó» · 55.7 ms / 2.3 ms · desfase 0.02 ms → INCORRECTA
  ronda 03 · aceptar 200 ACEPTADA · cancelar 200 CANCELADA · estado ACEPTADA · Bruno 775.00 · Diego 2525.00 · SMS a Diego: 1 «aceptó», 0 «rechazó» · 70.6 ms / 2.9 ms · desfase 0.02 ms → INCORRECTA
  ronda 04 · aceptar 200 ACEPTADA · cancelar 200 CANCELADA · estado ACEPTADA · Bruno 775.00 · Diego 2525.00 · SMS a Diego: 1 «aceptó», 0 «rechazó» · 126.0 ms / 3.0 ms · desfase 0.02 ms → INCORRECTA
  ronda 05 · aceptar 409 ESTADO_INVALIDO · cancelar 200 CANCELADA · estado CANCELADA · Bruno 800.00 · Diego 2500.00 · SMS a Diego: 0 «aceptó», 0 «rechazó» · 3.3 ms / 2.3 ms · desfase 0.04 ms → correcta, gana cancelar
  correctas: 1 de 5 (gana aceptar 0, gana cancelar 1) · incorrectas: 4
  combinaciones observadas:
      4 × aceptar 200 ACEPTADA · cancelar 200 CANCELADA · estado ACEPTADA · Bruno 775.00 · Diego 2525.00 · SMS a Diego: 1 «aceptó», 0 «rechazó»
      1 × aceptar 409 ESTADO_INVALIDO · cancelar 200 CANCELADA · estado CANCELADA · Bruno 800.00 · Diego 2500.00 · SMS a Diego: 0 «aceptó», 0 «rechazó»
  duración mediana: aceptar 67.4 ms · cancelar 2.9 ms · desfase de salida máximo 0.04 ms

Modo rechazar: Bruno acepta y Bruno rechaza la misma solicitud, 5 rondas
  ronda 01 · aceptar 200 ACEPTADA · rechazar 200 RECHAZADA · estado ACEPTADA · Bruno 775.00 · Diego 2525.00 · SMS a Diego: 1 «aceptó», 1 «rechazó» · 83.6 ms / 2.9 ms · desfase 0.02 ms → INCORRECTA
  ronda 02 · aceptar 200 ACEPTADA · rechazar 200 RECHAZADA · estado ACEPTADA · Bruno 775.00 · Diego 2525.00 · SMS a Diego: 1 «aceptó», 1 «rechazó» · 51.3 ms / 3.2 ms · desfase 0.03 ms → INCORRECTA
  ronda 03 · aceptar 200 ACEPTADA · rechazar 200 RECHAZADA · estado ACEPTADA · Bruno 775.00 · Diego 2525.00 · SMS a Diego: 1 «aceptó», 1 «rechazó» · 109.3 ms / 3.3 ms · desfase 0.02 ms → INCORRECTA
  ronda 04 · aceptar 409 ESTADO_INVALIDO · rechazar 200 RECHAZADA · estado RECHAZADA · Bruno 800.00 · Diego 2500.00 · SMS a Diego: 0 «aceptó», 1 «rechazó» · 3.1 ms / 2.1 ms · desfase 0.03 ms → correcta, gana rechazar
  ronda 05 · aceptar 409 ESTADO_INVALIDO · rechazar 200 RECHAZADA · estado RECHAZADA · Bruno 800.00 · Diego 2500.00 · SMS a Diego: 0 «aceptó», 1 «rechazó» · 3.8 ms / 2.5 ms · desfase 0.02 ms → correcta, gana rechazar
  correctas: 2 de 5 (gana aceptar 0, gana rechazar 2) · incorrectas: 3
  combinaciones observadas:
      3 × aceptar 200 ACEPTADA · rechazar 200 RECHAZADA · estado ACEPTADA · Bruno 775.00 · Diego 2525.00 · SMS a Diego: 1 «aceptó», 1 «rechazó»
      2 × aceptar 409 ESTADO_INVALIDO · rechazar 200 RECHAZADA · estado RECHAZADA · Bruno 800.00 · Diego 2500.00 · SMS a Diego: 0 «aceptó», 1 «rechazó»
  duración mediana: aceptar 51.3 ms · rechazar 2.9 ms · desfase de salida máximo 0.03 ms

Total: 7 rondas incorrectas de 10 · 2.9 s
```

## Decisión

**El comportamiento observado no es correcto, y se registró un DEF nuevo: DEF-30.** Que no se reproduzca en todas las rondas no lo vuelve correcto. Cuando aparece, viola la regla de estado de las tres historias.

**Qué ve cada usuario en una ronda incorrecta.**
- **Modo cancelar.** Diego recibe 200 con la solicitud CANCELADA. Luego le llega el SMS «aceptó tu solicitud» y los S/ 25.00. La solicitud termina ACEPTADA.
- **Modo rechazar.** Bruno recibe 200 con la solicitud RECHAZADA y aun así paga S/ 25.00. Diego recibe los dos SMS: «rechazó» y «aceptó».

La aplicación confirma con 200 una decisión del usuario que después no se cumple.

**Por qué pasa** ([`qolqe/api/solicitudes.py`](../../qolqe/api/solicitudes.py)):
1. `aceptar` lee la solicitud y comprueba que esté PENDIENTE (línea 156).
2. Luego transfiere (línea 160). La transferencia incluye la consulta antifraude simulada, que espera entre 40 y 120 ms (`qolqe/operaciones.py:99-101`).
3. Recién después escribe ACEPTADA con `_resolver` (línea 163). `_resolver` actualiza con `WHERE id = ?`, sin `AND estado = 'PENDIENTE'` (líneas 92-95).
4. `cancelar` y `rechazar` comprueban y escriben en pocos milisegundos (líneas 191-192 y 175-179).

Hay dos órdenes posibles:
- Si cancelar o rechazar confirma antes de que `aceptar` lea la fila, `aceptar` responde 409. Esa ronda es correcta.
- Si `aceptar` lee antes de que la otra confirme, las dos pasan la comprobación. Cancelar o rechazar termina enseguida. Entre 40 y 120 ms después, `aceptar` mueve el dinero y pisa el estado con ACEPTADA.

Por eso aceptar nunca ganó de forma correcta (0 de 400): escribe recién después de la pausa, y para entonces la otra operación ya terminó. La corrida con `--detalle` lo muestra:
- `aceptar` con 200 tardó de 51.3 a 126.0 ms;
- `aceptar` con 409 tardó de 3.1 a 3.8 ms;
- cancelar y rechazar tardaron de 2.1 a 3.3 ms.

**Por qué un DEF nuevo y no DEF-25.** Los dos nacen en `aceptar`, pero la falla observable es distinta:
- DEF-25 son varias aceptaciones que cobran varias veces (CP-T17).
- Aquí el dinero se mueve una sola vez, pero contra una cancelación o un rechazo que la aplicación ya confirmó con 200. La regla que se viola es otra: HU-G4-09 CA1 y HU-G4-10 CA1.

Además, `cancelar` y `rechazar` también escriben con `WHERE id = ?`. Según el código, corregir solo `aceptar` no cierra este caso: una cancelación que leyó PENDIENTE todavía podría pisar una ACEPTADA. Esto es una lectura del código, no algo que se haya observado. Por eso que CP-T17 pase no prueba que este defecto esté corregido, y conviene tenerlo aparte.

**Severidad y prioridad: Crítica y Alta.** Es la misma clase de falla que DEF-03, aceptar una solicitud vencida, y que DEF-25: el dinero se mueve en una solicitud que ya no se debía pagar. Y lo hace después de que la aplicación confirmó lo contrario.

**Por qué no se automatiza.** Se reprodujo en 118 y 136 de 200 rondas, no en 200 de 200. No cumple la regla de concurrencia de [`defectos.md`](../defectos.md). Como `xfail` estricto, daría XPASS en las rondas en que gana cancelar o rechazar. Repetir la ráfaga hasta 5 veces, como CP-T20, es posible, pero exige un escenario nuevo en `features/` (CP-T19 no tiene ninguno) y su propia verificación de 200 de 200 corridas; queda fuera de esta entrega. CP-T19 sigue como evidencia manual, ahora con script, salida y defecto. La frase «No se reprodujo en todas las corridas» de `alcance-y-casos.md` queda confirmada con números, y «Sin DEF» se cambió por DEF-30.

### Ficha en `defectos.md`

La ficha de DEF-30, con los pasos, el resultado esperado y obtenido y la evidencia, está en [`defectos.md`](../defectos.md#def-30-cancelar-o-rechazar-a-la-vez-que-se-acepta-responde-200-y-el-dinero-igual-se-mueve), con el mismo formato que las demás.
