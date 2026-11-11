# Pruebas de rendimiento de Qolqe Wallet (P2, Parte 3)

Esta carpeta tiene todo lo necesario para repetir las pruebas: el entorno (Docker), los datos de prueba, los scripts de k6, la medición de recursos, la verificación del dinero y el análisis. El diseño completo (umbrales U, supuestos S, modelo M y criterios de validez V) está en el informe; cada valor de configuración lleva en un comentario el ID del que sale.

`qolqe/` es el sistema bajo prueba y **no se modifica**: la imagen se construye desde el repo tal cual.

## 1. Estructura

| Ruta | Qué tiene |
|---|---|
| `preparar.sh [N]` | Construye la imagen, genera los datos y la base `base_perf.db` (una vez, el mismo día de las corridas) |
| `correr.sh <escenario>` | Corre un escenario completo y deja la evidencia en `resultados/<escenario>/<AAAAMMDD-HHMM>/` |
| `docker/Dockerfile`, `Dockerfile.dockerignore`, `versiones.txt` | Imagen `qolqe-perf:p3`: Python 3.11, mismas versiones que el `.venv` y `constraints.txt` (FastAPI 0.117.1, DEF-07) |
| `docker/config.env` | Puerto 8090, contenedor, volumen, `CPUS=1`, `MEMORIA=1g`, usuarios (M-16), V-04. Todo se puede sobrescribir por entorno |
| `docker/comun.sh` | Funciones comunes: arrancar Qolqe con los límites, esperar `/api/salud`, restaurar la base, leer el cgroup |
| `datos/preparar_datos.py`, `datos/preparar_bd.sql` | Generador de datos (§5.2 del diseño) |
| `datos/usuarios.csv` | Generado: una fila por VU (`vu,celular,pin,usuario_id,suministro,contactos,buscar`) |
| `k6/` | Scripts de k6: sesión, mezcla, escenarios y umbrales (ver `k6/README.md`) |
| `monitor/monitor.py` | El script psutil del enunciado, adaptado (columnas extra al final y PID del host o de un contenedor) |
| `monitor/monitor_docker.py` | `docker stats` del contenedor de Qolqe a CSV |
| `monitor/corrida.py` | `corrida.json` (hora de inicio y fin, versiones, cgroup, V-04, V-05) y `entorno.json` |
| `integridad/` | Verificación del dinero antes y después (U-07): `verificar.py`, `verificar_dinero.sql`, `foto.sql`, `verificar_bd.py` |
| `analisis/` | Veredicto por umbral, tablas y gráficos de cada corrida |
| `resultados/` | Evidencia de cada corrida (§4, "Qué queda en…") |

## 2. Requisitos

- macOS con Docker Desktop (probado con el motor 29.8.2 y una VM de 10 CPU y 8 GB). La imagen base `python:3.11.15-slim-bookworm` se descarga sola la primera vez.
- k6 2.3.0: `brew install k6 && brew pin k6` (`k6 version` debe decir `v2.3.0`).
- El `.venv` del repo (Python 3.11). Los monitores usan `psutil`; el análisis usa `pandas`, `numpy` y `matplotlib`. Los scripts toman `.venv/bin/python` solos; para otro intérprete: `PYTHON=/ruta/python`.
- `curl` y `bash` (sirve el 3.2 de macOS).
- Puertos: Qolqe se publica en `127.0.0.1:8090` (el diseño decía 8141; se cambió a 8090 y así debe ir en el informe). **No se usan el 8000** (demo del alumno) **ni el 8443** (Kiwi TCMS).

## 3. Entorno elegido: Docker con 1 CPU y 1 GB

Qolqe corre en un contenedor con `--cpus=1 --memory=1g --memory-swap=1g` y k6 corre en macOS, en la misma Mac. La cuota separa el CPU de Qolqe del de k6 (9 núcleos libres), así que la herramienta no compite con la aplicación y el estrés sí llega al límite.

- Un solo proceso de uvicorn, como pide el README del repo (el reloj de pruebas vive en memoria), con `QOLQE_MODO_PRUEBA=1` para tener `/api/pruebas/reiniciar` y `/api/pruebas/saldo`.
- La base está en el volumen con nombre `qolqe-perf-datos` (`/data`): `qolqe.db`, la plantilla de la semilla, `base_perf.db` y su huella `base_perf.json`.
- `correr.sh` comprueba en cada corrida que `cpu.max = 100000 100000` y `memory.max = 1073741824` (V-05).
- Limitaciones (§6 del informe): el proxy de puertos de Docker Desktop suma latencia (por eso la referencia de 1 VU se mide en Docker); `--cpus` es una cuota y no un `cpuset` (dentro, `nproc` da 10 y hay *throttling*); la memoria del cgroup incluye la caché de páginas de la base (el RSS del proceso lo da `monitor.py`).
- Los resultados son una **línea base relativa** de Qolqe en un contenedor de 1 CPU y 1 GB dentro de una laptop. No son la capacidad de producción.

## 4. Cómo correr todo (orden del diseño, §10.2)

```bash
cd <raíz del repo>
# 0. Equipo libre (V-04): cerrar otras apps, enchufado, sin modo de bajo consumo. correr.sh espera a que la
#    carga de 1 min baje de 1.5 (hasta 15 min) y la registra.
# 1-2. Imagen + datos + base_perf.db (≈ 3 min con 3,000 usuarios; ver §7)
tests/performance/preparar.sh 3000
# 3. Referencia de 1 VU (≈ 1 min, V-06) y 4. calibración (≈ 2.5 min, M-14: imprime el TOP sugerido)
tests/performance/correr.sh referencia
tests/performance/correr.sh calibracion
# 5-8. Los cuatro tipos de prueba
tests/performance/correr.sh carga                 # 17 min + drenaje
tests/performance/correr.sh pico                  # 19 min + drenaje
TOP=<calibrado> tests/performance/correr.sh estres   # 28 min + drenaje, con perfiles de py-spy
tests/performance/correr.sh resistencia           # 62 min + drenaje
# 9. Gráficos de todas las corridas y comparativo
.venv/bin/python tests/performance/analisis/graficos.py --todo
# 10. Demo en clase (≈ 2.5 min; dashboard en vivo en http://localhost:5665)
tests/performance/correr.sh demo
```

Opcionales: escalabilidad `CPUS=2 TOP=<n> tests/performance/correr.sh estres` y confirmación de capacidad `L_CAP=<n> tests/performance/correr.sh capacidad`.

**Sobre el TOP del estrés.** En el ensayo del 11-nov (§5) la calibración de 1 VU midió D ≈ 147 ms de CPU por sesión (TOP sugerido 1,100), pero bajo carga el CPU de Qolqe llegó al 100 % con ≈ 610 sesiones/min, es decir D ≈ 100 ms y L_sat ≈ 1,200 simultáneos. Con 1 VU el CPU casi no se usa y macOS puede llevar la vCPU de Docker a los núcleos de eficiencia (§6.3 del diseño), así que D sale inflado y TOP queda corto. Si la calibración da un TOP menor que 1.33 × 1,200 ≈ 1,600, conviene correr el estrés con `TOP=1800` (o con la hipótesis de 2,400) para pasar con seguridad la rodilla, y dejar anotada la razón en el informe.

Variables de `correr.sh`:

| Variable | Efecto |
|---|---|
| `HUMO=<s>` | Validación corta: corta k6 a los `<s>` segundos (SIGINT; k6 cierra ordenado y escribe su resumen) y deja todo en `resultados/descartadas/<escenario>_<marca>_humo/` con su `motivo.txt`. No espera al equipo libre. k6 termina con código 105 |
| `ESCALA=<f>` | Ensayo comprimido (0 < f ≤ 1): todo el escenario, con sus fases, en f veces el tiempo y con la misma tasa de llegada (§5). Va a `resultados/descartadas/<escenario>_<marca>_ensayo/` con su `motivo.txt` y no espera al equipo libre |
| `RESULTADOS=<carpeta>` | Raíz de resultados distinta de `tests/performance/resultados` (ensayos fuera del repo). Ahí las corridas quedan en `<carpeta>/<escenario>/<marca>/`. También la usa `preparar.sh` para `entorno/` |
| `USUARIOS_CSV=<ruta>` | `usuarios.csv` distinto de `datos/usuarios.csv` (también en `preparar.sh`) |
| `TOP`, `L_CAP` | Parámetros de k6 para el estrés (M-14) y la capacidad |
| `CPUS`, `MEMORIA` | Límites del contenedor al medir (por defecto 1 y 1g) |
| `FORZAR=1` | Sigue aunque no se cumplan V-04 o V-05 (queda registrado en `corrida.json`) |
| `PYSPY=0` | Sin py-spy en el estrés. `PYSPY_BASE_S`, `PYSPY_SATURACION_S`, `PYSPY_MESETA_S` y `PYSPY_DURACION` cambian cuándo y cuánto se perfila |
| `ANALIZAR=0` | No ejecuta el análisis ni los gráficos al final |

Código de salida de `correr.sh`: el de k6 si no es 0 (**99** = algún umbral falló, 105 = cortado); si k6 dio 0, el de la verificación del dinero (**1** = descuadre). Un error de preparación da 2.

### Qué hace `correr.sh` en cada corrida

1. **V-04**: espera a que la carga del equipo baje de `CARGA_MAX`.
2. **Base y proceso nuevos**: borra el contenedor, copia `base_perf.db` sobre `qolqe.db` (nunca llama a `reiniciar`, que borraría a los usuarios creados por la API) y arranca un contenedor nuevo con `--cpus=$CPUS --memory=$MEMORIA --memory-swap=$MEMORIA`.
3. **V-05 y `corrida.json`**: huella de la base restaurada contra la de `base_perf.json`, `cpu.max`, `memory.max`, versiones, commit, carga del equipo y `cpu.stat` antes.
4. **Monitores** (una fila por segundo): `docker stats` → `recursos_docker.csv`; psutil sobre el PID 1 de Qolqe desde un contenedor auxiliar (`--pid=container:qolqe-perf --cgroupns=host`, así no gasta la cuota de Qolqe) → `recursos_qolqe.csv`; psutil sobre el proceso de k6 en el host → `recursos_k6.csv`.
5. **k6** con `k6/correr_k6.sh` (reporte HTML, crudos, resumen). En el estrés programa py-spy.
6. **Fin**: hora de fin y `cpu.stat` después (con la Δ; en la calibración calcula D_sesión, L_sat y TOP), detiene los monitores y guarda el log de Qolqe.
7. **U-07**: `integridad/verificar.py` compara la base después contra `base_perf.db` y concilia con los 201 de k6.
8. **Análisis y gráficos**: `analisis/graficos.py` sobre la carpeta (veredicto, tablas y G1–G10; es lo mismo que `analizar.py` más los PNG).

### Qué queda en `resultados/<escenario>/<AAAAMMDD-HHMM>/`

| Archivo | Contenido |
|---|---|
| `corrida.json` | Escenario, **hora de inicio y fin** (Lima, ISO y epoch), commit, versiones, `cpu.max`, `memory.max`, `cpu.stat` antes, después y Δ, V-04, V-05, códigos de salida |
| `consola.txt`, `resumen.json`, `resumen.txt`, `reporte.html`, `muestras.csv.gz` | Salida, resumen, reporte HTML y datos crudos de k6 |
| `recursos_docker.csv` | `hora,cpu_%,memoria_MB,ts,memoria_%,pids` (100 % = 1 CPU, la cuota) |
| `recursos_qolqe.csv` | `hora,cpu_%,memoria_MB,ts,hilos,descriptores,cpu_cgroup_%,nr_throttled,throttled_usec` (RSS del proceso; throttling acumulado) |
| `recursos_k6.csv` | `hora,cpu_%,memoria_MB,ts,hilos,descriptores,cpu_k6_equipo_%,cpu_total_equipo_%` (V-01: < 80 %) |
| `verificacion_dinero.txt/.json` | C1 a C6 y la línea `TOTAL descuadres: N` (U-07) |
| `qolqe.log.gz` | Log de acceso de uvicorn (`docker logs`) |
| `perfil_base.svg`, `perfil_saturacion.svg`, `hilos_meseta.txt` | Solo en el estrés: py-spy (flamegraph) y foto de los hilos |
| `peticiones.csv.gz`, `tabla_resumen.*`, `veredicto.*`, `ventanas.csv`, `graficos/` | Análisis |

`resultados/entorno/` guarda `entorno.json` (especificaciones de la Mac, Docker, k6 e imagen), `pip_freeze.txt`, `cgroup.txt` y `preparacion.json` (tiempos y conteos de la preparación). Una corrida inválida se mueve a `resultados/descartadas/<escenario>_<AAAAMMDD-HHMM>/` con un `motivo.txt`. Si `muestras.csv.gz` pasa de 50 MB, `correr.sh` lo deja fuera de git (queda la versión compacta `peticiones.csv.gz`).

## 5. Ensayo de la cadena completa (antes de las corridas reales)

Con `ESCALA` se corre cada escenario completo, con todas sus fases, en pocos minutos: la duración, las fases, las ventanas del análisis, el think time y la reserva de VUs se multiplican por `ESCALA`, y la tasa de llegada (sesiones/min) no cambia. Así req/s y sesiones/min son los del diseño y los simultáneos bajan a L·`ESCALA`. Sirve para comprobar que k6, los monitores, la verificación del dinero, el análisis y los gráficos funcionan juntos sin gastar 3 horas. **No es evidencia**: el veredicto y cada gráfico lo dicen, y con la carpeta por defecto la corrida va a `resultados/descartadas/`.

```bash
S=/tmp/ensayo-qolqe          # fuera del repo
RESULTADOS=$S USUARIOS_CSV=$S/usuarios.csv tests/performance/preparar.sh 300               # ≈ 15 s
FORZAR=1 RESULTADOS=$S USUARIOS_CSV=$S/usuarios.csv tests/performance/correr.sh referencia   # 1 min (tiempo real)
ESCALA=0.1  RESULTADOS=$S USUARIOS_CSV=$S/usuarios.csv tests/performance/correr.sh carga     # 2 min
ESCALA=0.09 RESULTADOS=$S USUARIOS_CSV=$S/usuarios.csv tests/performance/correr.sh pico      # 2 min
ESCALA=0.06 TOP=2400 RESULTADOS=$S USUARIOS_CSV=$S/usuarios.csv tests/performance/correr.sh estres   # 2 min, satura
ESCALA=0.5  RESULTADOS=$S USUARIOS_CSV=$S/usuarios.csv tests/performance/correr.sh demo      # 1.3 min
.venv/bin/python tests/performance/analisis/graficos.py --todo --resultados $S
```

Con N = 300 usuarios caben las reservas de VUs de esos ensayos (el estrés con `ESCALA=0.06` y `TOP=2400` usa hasta 180 VUs). Después hay que volver a correr `preparar.sh 3000` sin `RESULTADOS` ni `USUARIOS_CSV`, porque el ensayo deja en el volumen la base de 300 usuarios.

## 6. Medición de recursos sin `correr.sh`

```bash
# Script del enunciado, para cualquier PID del host (por ejemplo, k6). Ctrl+C para detener.
.venv/bin/python tests/performance/monitor/monitor.py <PID> --salida recursos.csv [--equipo]
# docker stats del contenedor de Qolqe
.venv/bin/python tests/performance/monitor/monitor_docker.py qolqe-perf recursos_docker.csv
# psutil sobre Qolqe dentro de Docker, sin gastar su cuota de CPU
docker run --rm --pid=container:qolqe-perf --cgroupns=host -v "$PWD/tests/performance/monitor:/monitor:ro" \
  -v "$PWD:/out" qolqe-perf:p3 python /monitor/monitor.py 1 --salida /out/recursos_qolqe.csv --cgroup
```

Las tres primeras columnas son las del script del enunciado (`hora,cpu_%,memoria_MB`). En `monitor.py`, `cpu_%` es respecto de 1 núcleo, como lo da psutil.

## 7. Datos de prueba

`preparar.sh N` arranca Qolqe con `--cpus=4` (la preparación no se mide) y ejecuta `datos/preparar_datos.py`:

1. `POST /api/pruebas/reiniciar`: la semilla deja 200 usuarios de carga (celulares 900000001–900000200, PIN 2580).
2. `POST /api/usuarios` para 201…N (DNI `7NNNNNNN`, nombre `Carga NNNN`, celular `9NNNNNNNN`, PIN 2580).
3. `PUT /api/pruebas/saldo`: S/ 10,000 para todos.
4. Login y 5 contactos por usuario por la API (anillo n → n+1…n+5, alias `Amigo NNNN`).
5. `datos/preparar_bd.sql` dentro del contenedor: historial de 1,000 movimientos clonado a los usuarios nuevos y 30 deudas AGUA pendientes por usuario en su suministro propio `5` + id con 9 dígitos.
6. Conteos (N usuarios, 5N contactos, 30N deudas, ≥ 1,000 movimientos por usuario, saldos de S/ 10,000) y `PRAGMA integrity_check`.
7. Respaldo `base_perf.db` (API de backup de SQLite) y su huella `base_perf.json`.
8. `datos/usuarios.csv`: el VU n usa la fila n (`exec.vu.idInTest`), así nunca hay dos sesiones sobre el mismo usuario.

Tiempos medidos con N = 3,000 (2,800 creados por la API; `--cpus=4`, 6 hilos, 11-nov-2026, con otro trabajo usando la Mac): registro 50.7 s (18.1 ms por usuario), saldo 6.2 s, login + 5 contactos 66.6 s (22.2 ms por usuario), SQL del historial (2.8 M filas) y las deudas 22.9 s, verificación 6.0 s y respaldo 0.8 s: **153.6 s de datos y 158 s con `preparar.sh` completo** (con la imagen ya construida), base de **539.5 MB** con 3,000,031 movimientos. Construir la imagen sin caché de capas tarda 12 s (con la imagen base ya descargada). Restaurar la base y arrancar el contenedor en cada corrida tarda ≈ 3 s.

Reglas: la base se genera **el mismo día** de las corridas (`correr.sh` avisa si no); **nunca** se llama a `reiniciar` entre corridas; ninguna corrida cruza la medianoche de Lima (los límites diarios se reinician).

## 8. Verificación del dinero (U-07)

"Antes" es `base_perf.db` (cada corrida la restaura) y "después" es `qolqe.db` sin tráfico. Las consultas corren dentro del contenedor en solo lectura.

| Chequeo | Correcto |
|---|---|
| C1 Conservación: Σ saldos antes − después = recargas + pagos + comisiones + interbancarias; y Δ saldos = Σ movimientos nuevos | descuadre 0 |
| C2 Libro mayor: por usuario, Δ saldo = Σ de sus movimientos nuevos | 0 filas |
| C3 Operación ↔ movimientos, agrupando por código (DEF-22 no se confunde con un duplicado) | 0 filas |
| C4 Ninguna deuda pagada dos veces; deudas PAGADA ↔ pagos | 0 filas |
| C5 Ningún saldo negativo ni transferencias Qolqe del día sobre el límite (síntomas de DEF-21) | 0 filas |
| C6 Filas nuevas contra los 201 de k6: 0 ≤ BD − confirmadas ≤ respuestas perdidas (status 0) + POST cortados en vuelo (`dinero_intentos` sin ninguna respuesta registrada, p. ej. al terminar la demo) | diferencia explicada |

```bash
.venv/bin/python tests/performance/integridad/verificar.py comparar --k6 <carpeta>/muestras.csv.gz --salida <carpeta>/verificacion_dinero.txt
.venv/bin/python tests/performance/integridad/verificar.py comparar --esperado transferencias=3,recargas=1,pagos=1   # pruebas a mano con curl
.venv/bin/python tests/performance/integridad/verificar.py foto       # huella de la base (V-05)
```

Código de salida: 0 = PASA, 1 = FALLA (el detalle de cada fila sale en el texto).

## 9. Problemas comunes

- **`V-04: el equipo no está libre`**: otra app usa el CPU. Esperar, cerrarla o, solo para probar, `FORZAR=1`.
- **`no existe base_perf.db`**: falta `preparar.sh`.
- **`base_perf.db es del …`**: la base es de otro día; volver a correr `preparar.sh 3000`.
- **Puerto 8090 ocupado**: `PUERTO=8091 tests/performance/correr.sh …` (nunca 8000 ni 8443).
- **Limpiar todo**: `docker rm -f qolqe-perf && docker volume rm qolqe-perf-datos` (luego hay que volver a preparar).
