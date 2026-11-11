# Scripts de k6 (Parte 3, rendimiento)

Implementan §3 y §4 del diseño: la sesión de la hora punta, la mezcla ponderada, el think time, los escenarios y los umbrales del requerimiento. Cada valor lleva en un comentario su ID del diseño (M = modelo, U = umbral, S = supuesto, V = validez, F = flujo).

| Archivo | Qué tiene |
|---|---|
| `qolqe.js` | Script principal: carga `usuarios.csv`, mezcla (M-06), pausa triangular 10–25 s con media 18 s (M-04, S-14), cierre de 12 s (S-13), funciones `sesion`, `sesionSinPausa`, `recorrido` y `calibracion` |
| `operaciones.js` | Una función por operación, con las peticiones de cada pantalla de `app.js` (M-07), etiquetas y clasificación de errores (S-06, §5.4) |
| `escenarios.js` | Los escenarios de §4.2 y las fases de cada uno |
| `umbrales.js` | U-01 a U-06 como umbrales de k6, más V-02 y V-06 en la referencia |
| `resumen.js` | `handleSummary`: tabla de umbrales ✓/✗ con su ID, `resumen.json` y `resumen.txt` |
| `correr_k6.sh` | Corre un escenario y guarda toda la evidencia de k6 en `resultados/<escenario>/<AAAAMMDD-HHMM>/` |

## Cómo correr

Requisitos: k6 2.3.0, Qolqe levantado (por defecto en `http://127.0.0.1:8090`; el diseño decía 8141, se usa 8090) y `../datos/usuarios.csv` generado por `datos/preparar_datos.py`.

```bash
tests/performance/k6/correr_k6.sh referencia            # 1 VU, ≈ 1 min (V-06)
tests/performance/k6/correr_k6.sh calibracion           # 1 VU, 40 sesiones, ≈ 2.5 min (M-14)
tests/performance/k6/correr_k6.sh carga                 # 17 min + drenaje
tests/performance/k6/correr_k6.sh pico                  # 19 min + drenaje
TOP=1800 tests/performance/k6/correr_k6.sh estres       # TOP = L_top calibrado (por defecto 2400)
tests/performance/k6/correr_k6.sh resistencia           # 62 min + drenaje
tests/performance/k6/correr_k6.sh demo                  # 2 min 25 s; dashboard en vivo en http://localhost:5665
L_CAP=1500 tests/performance/k6/correr_k6.sh capacidad  # opcional: 10 min estables a L_CAP simultáneos
```

Variables: `BASE_URL`, `SALIDA` (carpeta de la corrida), `TOP`, `L_CAP`, `USUARIOS_CSV`, `ESCALA` y `K6_WEB_DASHBOARD_PORT`. Lo que se pase después del escenario va tal cual a `k6 run` (por ejemplo, `--no-connection-reuse` si aparecen errores de conexión por el keep-alive de 5 s de uvicorn, §10.3).

`ESCALA=<f>` (0 < f ≤ 1, por defecto 1) es un **ensayo comprimido**: multiplica por f las duraciones, `gracefulStop`, `startTime`, los bordes de las fases, el think time (10–25 s), el cierre de 12 s, la reserva de VUs (M-15) y la cantidad mínima de U-04; la tasa de llegada (sesiones/min) no cambia. Sirve para validar la cadena completa en pocos minutos (p. ej. `ESCALA=0.1` corre la carga entera, con sus fases, en 2 min). Con f = 1 las opciones son exactamente las del diseño (comprobado con `k6 inspect`). No es evidencia: `correr.sh` la guarda en `resultados/descartadas/`.

Sin el envoltorio: `k6 run -e ESCENARIO=carga -e BASE_URL=http://127.0.0.1:8090 tests/performance/k6/qolqe.js`.

El código de salida es el de k6: **0** si todos los umbrales se cumplen y **99** si alguno falla. En la demo se espera 99, porque `demo_sin_pausa` debe fallar.

## Qué deja cada corrida

| Archivo | Origen |
|---|---|
| `consola.txt` | Salida completa de k6, con avisos como "Insufficient VUs" (V-07) y la tabla de umbrales |
| `resumen.json` | Datos de `handleSummary` y el bloque `qolqe`: escenario, hora de inicio y fin (Lima y epoch en ms), veredicto por umbral |
| `resumen.txt` | La tabla de umbrales de la consola |
| `reporte.html` | Dashboard web de k6 exportado (`K6_WEB_DASHBOARD_EXPORT`, período de 10 s) |
| `muestras.csv.gz` | Datos crudos (`--out csv`, `K6_CSV_TIME_FORMAT=unix_milli`): una fila por muestra. Las etiquetas propias están en `extra_tags` (`ep=…&op=…&grupo=…&fase=…`) |
| `codigo_salida_k6.txt` | Código de salida de k6 |

`corrida.json`, los CSV de recursos, la verificación del dinero y los gráficos los agrega `correr.sh`.

## Datos: `datos/usuarios.csv`

Columnas: `vu,celular,pin,usuario_id,suministro,contactos,buscar`, con una fila por VU (la fila `vu = n` es la del VU `n`, `exec.vu.idInTest`). `contactos` son los `id` de la tabla `contactos` del usuario (los que acepta `contacto_id` en `POST /api/transferencias`), separados con `|`. La columna `buscar` (o `busqueda`) es opcional: el alias de uno de sus contactos, que se usa en la búsqueda. Si no está, se busca `amigo`, que coincide con los alias `Amigo NNNN` (§5.1). Si un VU no tiene fila, la prueba se corta con un mensaje (M-16).

## Etiquetas y métricas

- Cada petición lleva `ep` (endpoint), `op` (operación de la mezcla; las 5 "otras" llevan `op=otras`), `grupo` (`consulta` o `dinero`), `fase` y, en el pico, `campana=si|no`. `name` es `MÉTODO /ruta` sin la consulta. El login va en el grupo `consulta`, porque U-01 dice "Consultas e inicio de sesión".
- `operacion_fallida` (Rate): una muestra por operación de negocio, login incluido (U-03, S-06).
- `operacion_error_datos` (Rate) y `errores_datos{codigo}` (Counter): 4xx de regla de negocio (V-02). No cuentan en U-03.
- `errores_rendimiento{tipo}`: `http_5xx`, `timeout`, `conexion`, `cuerpo_invalido` (2xx con cuerpo incorrecto) y `no_autenticado` (401 a mitad de sesión).
- `dinero_confirmado{ep}` (201 recibidos), `dinero_sin_respuesta{ep}` (POST sin respuesta) y `dinero_intentos{ep}` (POST enviados, contado antes de enviar) para la conciliación C6. `dinero_intentos` hace falta porque, si k6 corta la sesión con el POST en vuelo (fin de `gracefulStop`, fin de la demo, humo), esa petición no deja ninguna otra muestra y la fila en la BD parecería un duplicado.
- `http_req_failed` solo cuenta 5xx y errores de red (`expectedStatuses` 200–499).

## Diferencias con el diseño (k6 2.3.0)

- El resumen de consola lo arma `resumen.js`. Si hay `handleSummary`, k6 no imprime su resumen y `textSummary` solo está en una librería remota (jslib.k6.io): se evita depender de internet en la demo.
- k6 da por cumplido un umbral sin muestras (por ejemplo, una fase que no llegó a correr). `resumen.js` lo marca con ○ y el veredicto queda "incompleto".
- U-04 se expresa como conteo: `http_reqs{fase:estable,expected_response:true}` ≥ 9.6 req/s × 900 s = 8,640 en carga (34,560 en resistencia). El `rate` de k6 divide por toda la corrida, no por la fase.
- k6 2.x quitó `k6 stop`/`k6 pause`. Para detener una corrida desde otra terminal: `k6 run --address localhost:6565 …` y `curl -X PATCH localhost:6565/v1/status -H 'Content-Type: application/json' -d '{"data":{"attributes":{"stopped":true}}}'` (código de salida 103).
