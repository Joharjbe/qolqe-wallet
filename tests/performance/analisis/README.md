# Análisis de resultados (Parte 3, rendimiento)

Implementa §7.2 y §8 del diseño: el **veredicto binario por umbral antes de mirar gráficos** (paso 1 de S14), las tablas en el formato de S14 y los gráficos G1 a G11. Cada valor sale de `config.py`, donde lleva en un comentario su ID del diseño (U = umbral, S = supuesto, M = modelo, V = validez).

## Cómo correr

```bash
.venv/bin/python -m pip install -r tests/performance/requirements.txt        # una vez (pandas, numpy, matplotlib, psutil)
.venv/bin/python tests/performance/analisis/analizar.py <carpeta_corrida>      # veredicto y tablas (lo llama correr.sh)
.venv/bin/python tests/performance/analisis/graficos.py <carpeta_corrida>      # lo anterior + gráficos de esa corrida
.venv/bin/python tests/performance/analisis/graficos.py --todo                 # todas las corridas + resultados/comparativo/
```

`<carpeta_corrida>` es `tests/performance/resultados/<escenario>/<AAAAMMDD-HHMM>/`. `--todo` recorre `resultados/<escenario>/*` (no entra a `entorno/`, `comparativo/`, `descartadas/` ni `humo/`) y arma el comparativo con la última corrida de cada escenario. Con `--resultados <otra carpeta>` se apunta a otra raíz.

Para probar sin Qolqe, `sintetico.py` genera corridas inventadas con el formato real de k6 2.3.0 y de los monitores. Nunca escribe en `resultados/`:

```bash
.venv/bin/python tests/performance/analisis/sintetico.py /tmp/qolqe-sintetico
.venv/bin/python tests/performance/analisis/graficos.py --todo --resultados /tmp/qolqe-sintetico
```

## Qué lee de cada corrida

| Archivo | Qué usa |
|---|---|
| `muestras.csv.gz` | `k6 run --out csv` con `K6_CSV_TIME_FORMAT=unix_milli` (la unidad se detecta sola). Métricas: `http_req_duration`, `http_req_connecting`, `iteration_duration`, `dropped_iterations`, `vus`, `operacion_fallida`, `operacion_error_datos`, `errores_datos{codigo}`, `errores_rendimiento{tipo}` y `dinero_*`. Etiquetas de `extra_tags`: `ep`, `op`, `grupo`, `fase`, `campana`. Se descarta el chequeo de salud de `setup()` |
| `peticiones.csv.gz`, `metricas_k6.csv.gz` | Versión compacta que escribe el análisis. Se usa si no están las muestras crudas (las de más de 50 MB no se versionan) |
| `recursos_qolqe.csv` | psutil sobre Qolqe: `cpu_%`, `memoria_MB` (RSS), `ts`, `hilos`, `descriptores` y, con `--cgroup`, `cpu_cgroup_%` y `nr_throttled` |
| `recursos_docker.csv`, `recursos_k6.csv` | `docker stats` del contenedor y psutil sobre k6 (`cpu_k6_equipo_%`, `cpu_total_equipo_%` para V-01) |
| `corrida.json` | `inicio`/`fin` (`{hora, epoch}`), `parametros.TOP`, `parametros.ESCALA`, `codigo_salida_k6`, `cpu_ocioso_antes` (V-04, decide) y `carga_equipo_antes` (V-04 del diseño, solo informa), `base_identica` y `cpu_max` (V-05), `cpu_stat_antes`/`despues` (throttling y M-14), `calibracion` |
| `resumen.json` | Umbrales que evaluó k6 (`qolqe.umbrales` de `k6/resumen.js`), solo para mostrarlos junto al veredicto propio |
| `verificacion_dinero.txt` | La línea `TOTAL descuadres: N` (U-07) |
| `consola.txt` | Avisos `Insufficient VUs` (V-07) |

Si falta la columna `ts` en un monitor, se reconstruye la hora con `hora` (se prueba hora de Lima y UTC y se elige la que cae dentro de la corrida). Si falta la etiqueta `fase`, se calcula con el perfil del escenario (`perfiles.py`, copia de `k6/escenarios.js`).

## Qué escribe

| Archivo | Contenido |
|---|---|
| `veredicto.md/.csv` | V-01 a V-07 (si una falla, la corrida no vale), U-01 a U-09 con lo medido, el umbral y PASA/FALLA, el detalle por grupo, endpoint y ventana, la mezcla lograda y los umbrales de k6 |
| `tabla_resumen.md/.csv` | Formato de S14 por endpoint: peticiones, promedio, p50, p90, p95, p99, error de rendimiento y de datos por separado, throughput |
| `ventanas.csv`, `errores_datos_ventanas.csv` | Todo lo anterior por ventana (1 min en carga, 30 s en pico y estrés, 5 min en resistencia) |
| `tabla_estres.md/.csv` | (estrés) Un momento cada 100 usuarios, formato del ejercicio 3 de S14 |
| `calibracion.json` | (calibración) D_sesión, L_sat y TOP (M-14) |
| `graficos/G1…G10.png` | G1 tiempo de respuesta con umbrales, G2 throughput contra lo ofrecido, G3 errores (rendimiento y datos por separado), G4 usuarios simultáneos contra Little, G5 recursos con la línea del 80 %, G6 a G8 (estrés) p95, throughput y CPU contra usuarios con la capacidad, G9 y G10 (resistencia) proyección de memoria e hilos |
| `resultados/comparativo/` | G11 y `veredictos.md/.csv` (cada umbral en cada escenario), `resumen_escenarios.csv` |

## Cómo se calcula

- **Percentil por rango más cercano** (S14): se ordena y se toma la posición ⌈p/100 · n⌉.
- **Tiempo** = `http_req_duration`. Si el p95 de `http_req_connecting` pasa de 10 ms, se le suma (§2.1).
- **U-01/U-02** por grupo (lectura literal) y por endpoint (S-03). Los 5 endpoints de "otras" deciden como grupo (§3.3).
- **U-03** = `operacion_fallida` (una muestra por operación, login incluido). Los 4xx de negocio van aparte (V-02).
- **Carga ofrecida** (G2, U-04, U-08): λ(t) programada más 1.79 peticiones por operación cada 18 s (M-04, M-08). Con λ constante da 9.78 req/s.
- **Usuarios simultáneos** medidos = sesiones iniciadas (un login por sesión) − sesiones terminadas (`iteration_duration`), contra L = λ·W (M-03). Así cuentan las sesiones que quedaron atascadas y k6 cortó al final (no emiten `iteration_duration`): si solo se usaran las terminadas, justo antes de un colapso la concurrencia medida bajaría.
- **U-08** (S-10): ventanas de 30 s; capacidad = sesiones simultáneas de la última ventana que cumple U-01 a U-05 antes de 2 ventanas seguidas que fallan, hacia abajo a 50. Una ventana con peticiones pero ninguna atendida tiene throughput 0 (falla U-04).
- **U-09**: regresión lineal de RSS, hilos y descriptores contra sesiones acumuladas, proyectada a 54,000 sesiones (S-11).

## Decisiones del análisis que el diseño no fijaba (revisar)

| Decisión | Por qué |
|---|---|
| U-04: sesiones completadas ≥ 98 % de 50/min (≥ 49), igual que el throughput | Con 750 sesiones el borde de la ventana mueve el conteo ± 0.4/min: exigir ≥ 50 exacto fallaría por azar |
| U-08: el throughput de cada ventana de 30 s se acepta si es ≥ (1 − máx(2 %, 3 σ)) de lo ofrecido, con σ medida en la fase base | En 30 s el conteo varía más que en 15 min; el 98 % de S-04 se pensó para 750 sesiones |
| U-08: el p95 de un endpoint en una ventana solo decide con ≥ 20 muestras | Con menos, el p95 es el máximo (S-03 se mantiene con el grupo) |
| V-03 en la demo es informativo | Con ~80 sesiones la mezcla varía más de ± 2 pp |
| V-01 decide con el CPU de k6 (% de los núcleos del equipo, por ventana); el CPU total del equipo es una fila informativa con los minutos en que pasó del 80 % (11-nov) | El enunciado (§5) pide que la **herramienta** no pase del ~80 %. En esta Mac el CPU total lo suben procesos de macOS (`mediaanalysisd`, `suggestd`, WindowServer) que no son ni k6 ni Qolqe; en el pico llegó a 90 % durante 1.5 min con k6 en 0.3 %. Esas ventanas se señalan y su efecto en los tiempos se comenta en el informe |
| Comparativo del estrés: peticiones hasta la ventana de capacidad | Más allá, Qolqe ya no cumple y el p95 solo dice que colapsó |

## Ensayo comprimido (`ESCALA`)

Si la corrida se hizo con `ESCALA=<f>` (ensayo de la cadena completa en menos tiempo, ver `../README.md`), `perfiles.py` comprime igual que `k6/escenarios.js` las etapas, las fases, las ventanas, W (120 s × f) y la pausa media (18 s × f); los simultáneos esperados pasan a L·f y el rango de U-05(c), el redondeo de la capacidad (50 × f) y el paso de la tabla del estrés (100 × f) también. La tasa de llegada no cambia, así que U-04 (9.6 req/s, 49 sesiones/min) se mide igual. El veredicto, las tablas y cada gráfico dicen "ensayo comprimido: no es evidencia". El factor se lee de `corrida.json` (`parametros.ESCALA`) o de `resumen.json` (`qolqe.escala`).
