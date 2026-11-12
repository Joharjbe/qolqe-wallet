#!/usr/bin/env bash
# Corre un escenario y deja toda su evidencia en resultados/<escenario>/<AAAAMMDD-HHMM>/ (diseño §7.1 y §7.3).
#
# Uso:  tests/performance/correr.sh <escenario>
#         escenarios: referencia calibracion carga pico estres resistencia demo capacidad (k6/escenarios.js)
#       TOP=<n> tests/performance/correr.sh estres       cima del estrés que da la calibración (M-14)
#       CPUS=2 TOP=<n> tests/performance/correr.sh estres   escalabilidad opcional (§10.2, Opc. 1)
#       HUMO=60 tests/performance/correr.sh carga        validación corta: corta k6 a los 60 s (SIGINT, k6 cierra
#                                                        ordenado) y guarda en resultados/descartadas/<esc>_<marca>_humo/
#       ESCALA=0.1 tests/performance/correr.sh carga     ensayo comprimido: todo el escenario (fases incluidas) en 1/10
#                                                        del tiempo y con la misma tasa de llegada (k6/escenarios.js);
#                                                        guarda en resultados/descartadas/<esc>_<marca>_ensayo/
#       RESULTADOS=<carpeta> …   raíz de resultados distinta de tests/performance/resultados (ensayos fuera del repo)
#       USUARIOS_CSV=<ruta> …    usuarios.csv distinto de datos/usuarios.csv (el que dejó preparar.sh)
#       FORZAR=1 …   sigue aunque V-04 (equipo libre) o V-05 (base y cgroup) no se cumplan; queda en corrida.json
#       PYSPY=0 …    sin perfil de py-spy en el estrés     ANALIZAR=0 …   sin análisis ni gráficos al final
#
# Orden (§10.1): V-04 → restaura base_perf.db y arranca un contenedor nuevo (--cpus=$CPUS) → V-05 y corrida.json →
# monitores (docker stats, psutil de Qolqe y de k6) → k6 (k6/correr_k6.sh) → hora de fin y cpu.stat → detiene
# los monitores → log de Qolqe → verificación del dinero U-07 (integridad/verificar.py) → análisis y gráficos.
# Código de salida: el de k6 si no es 0 (99 = algún umbral falló); si no, el de la verificación (1 = descuadre).
set -uo pipefail

PERF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(cd "$PERF/../.." && pwd)"
source "$PERF/docker/config.env"
source "$PERF/docker/comun.sh"

ESCENARIO="${1:?Uso: correr.sh <referencia|calibracion|carga|pico|estres|resistencia|demo|capacidad>}"
PY="$(python_host)"
MONITOR_QOLQE="${CONTENEDOR}-monitor"

# ---------------------------------------------------------------- carpeta de la corrida (hora de Lima, D11)
MARCA="$(TZ=America/Lima date +%Y%m%d-%H%M)"
RESULTADOS="${RESULTADOS:-$PERF/resultados}"
USUARIOS_CSV="${USUARIOS_CSV:-$PERF/datos/usuarios.csv}"
ESCALA="${ESCALA:-1}"
# Humo (k6 cortado) y ensayo comprimido (ESCALA < 1) no son evidencia (§7.3): en la carpeta del repo van a
# descartadas/ con su motivo.txt, fuera del análisis --todo; con RESULTADOS=<otra carpeta> quedan como cualquier corrida.
MOTIVO=""
[ "$ESCALA" != 1 ] && MOTIVO="Ensayo comprimido (ESCALA=${ESCALA}): duraciones, fases y think time × ${ESCALA}, con la misma tasa de llegada; valida la cadena completa, no es evidencia." && TIPO=ensayo
[ -n "${HUMO:-}" ] && MOTIVO="Corrida de humo (HUMO=${HUMO} s): k6 se cortó para validar la cadena completa; no es evidencia." && TIPO=humo
# Escalabilidad (§10.2, Opc. 1): el estrés con CPUS≠1 va a resultados/escalabilidad/ para que --todo no lo tome
# como "la última corrida del estrés" en el comparativo.
CARPETA_ESC="$ESCENARIO"
[ "$ESCENARIO" = estres ] && [ "${CPUS:-1}" != 1 ] && CARPETA_ESC=escalabilidad
if [ -n "$MOTIVO" ] && [ "$RESULTADOS" = "$PERF/resultados" ]; then DIR="$RESULTADOS/descartadas/${CARPETA_ESC}_${MARCA}_${TIPO}"
else DIR="$RESULTADOS/$CARPETA_ESC/$MARCA"; fi
[ -e "$DIR" ] && DIR="$DIR$(TZ=America/Lima date +%S)"
mkdir -p "$DIR"
[ -n "$MOTIVO" ] && echo "$MOTIVO" > "$DIR/motivo.txt"
export ESCALA USUARIOS_CSV

command -v k6 >/dev/null || fallo "falta k6 (brew install k6)"
[ -f "$USUARIOS_CSV" ] || fallo "falta $USUARIOS_CSV: ejecuta primero tests/performance/preparar.sh"
[ -f "$PERF/k6/correr_k6.sh" ] || fallo "falta k6/correr_k6.sh"
info "Escenario $ESCENARIO → $DIR"

# ---------------------------------------------------------------- limpieza (también con Ctrl+C o error)
TRABAJOS=()
INTERRUMPIDA=0
limpiar() {
  for p in ${TRABAJOS[@]+"${TRABAJOS[@]}"}; do pkill -P "$p" 2>/dev/null; kill "$p" 2>/dev/null; done  # y sus hijos (sleep)
  docker rm -f "$MONITOR_QOLQE" >/dev/null 2>&1
  docker ps -aq --filter "name=${CONTENEDOR}-pyspy" | xargs docker rm -f >/dev/null 2>&1
}
trap limpiar EXIT
trap 'INTERRUMPIDA=1; aviso "interrumpida: k6 se detiene ordenado y se completa la evidencia"' INT TERM

# ---------------------------------------------------------------- V-04: equipo libre (no aplica al humo ni al ensayo)
if [ -z "$MOTIVO" ]; then
  "$PY" "$PERF/monitor/corrida.py" esperar-equipo "$DIR" \
    || { [ "${FORZAR:-0}" = 1 ] && aviso "V-04 no se cumple (FORZAR=1)" || fallo "V-04: el equipo no está libre"; }
fi

# ---------------------------------------------------------------- base restaurada y proceso nuevo (§5.2, V-05)
info "Restaurando base_perf.db y arrancando $CONTENEDOR con --cpus=$CPUS --memory=$MEMORIA"
qolqe_restaurar_base
qolqe_arrancar "$CPUS"
"$PY" "$PERF/monitor/corrida.py" inicio "$DIR" "$ESCENARIO" \
  || { [ "${FORZAR:-0}" = 1 ] && aviso "V-05 no se cumple (FORZAR=1)" || fallo "V-05 no se cumple (ver $DIR/corrida.json)"; }

# ---------------------------------------------------------------- monitores de recursos (C6 del enunciado)
# Docker: CPU (100 % = 1 CPU) y memoria del contenedor, como pide el enunciado ("docker stats").
"$PY" "$PERF/monitor/monitor_docker.py" "$CONTENEDOR" "$DIR/recursos_docker.csv" &
PID_DOCKER=$!
TRABAJOS+=("$PID_DOCKER")
# psutil sobre el PID 1 de Qolqe desde un contenedor auxiliar: RSS, hilos, descriptores y throttling del cgroup,
# sin gastar la cuota de --cpus de Qolqe (§7.1).
docker rm -f "$MONITOR_QOLQE" >/dev/null 2>&1
docker run -d --name "$MONITOR_QOLQE" --pid="container:$CONTENEDOR" --cgroupns=host -e TZ=America/Lima \
  -v "$PERF/monitor:/monitor:ro" -v "$DIR:/out" "$IMAGEN" \
  python /monitor/monitor.py 1 --salida /out/recursos_qolqe.csv --cgroup >/dev/null \
  || aviso "no arrancó el monitor psutil de Qolqe"

# py-spy en el estrés (§7.1): perfil en la base, al acercarse a la saturación y foto de hilos en la meseta.
programar_pyspy() {  # $1 = segundos desde el inicio, $2 = archivo de salida en $DIR, $3… = orden de py-spy
  local espera="$1" salida="$2"; shift 2
  ( sleep "$espera"
    docker run --rm --name "${CONTENEDOR}-pyspy-${salida%%.*}" --pid="container:$CONTENEDOR" --cap-add SYS_PTRACE \
      -v "$DIR:/out" "$IMAGEN" py-spy "$@" > "$DIR/$salida.log" 2>&1
    [ -s "$DIR/$salida.log" ] && [[ "$salida" == *.txt ]] && mv "$DIR/$salida.log" "$DIR/$salida" ) &
  TRABAJOS+=($!)
}
if [ "$ESCENARIO" = estres ] && [ "${PYSPY:-1}" = 1 ]; then
  # 0.9 × L_sat con L_sat = TOP / 1.33 (M-14). La tasa sube de 50/min (t = 180 s) a TOP/2 por min (t = 1560 s)
  # y la concurrencia va ~60 s detrás (Little, §4.2); el registro de 60 s se centra en ese momento.
  # En un ensayo comprimido todos los tiempos se multiplican por ESCALA (mínimo 3 s de registro).
  T_SAT=$("$PY" -c "t=${TOP:-2400}; r=0.9*t/1.33/2; print(int((180+1380*(r-50)/(t/2-50)+60-30)*${ESCALA}))")
  T_BASE=$("$PY" -c "print(int(60*${ESCALA}))"); T_MESETA=$("$PY" -c "print(int(1600*${ESCALA}))")
  T_REG=$("$PY" -c "print(max(3, int(60*${ESCALA})))")
  programar_pyspy "${PYSPY_BASE_S:-$T_BASE}" perfil_base.svg record --pid 1 --duration "${PYSPY_DURACION:-$T_REG}" --rate 100 --nonblocking -o /out/perfil_base.svg
  programar_pyspy "${PYSPY_SATURACION_S:-$T_SAT}" perfil_saturacion.svg record --pid 1 --duration "${PYSPY_DURACION:-$T_REG}" --rate 100 --nonblocking -o /out/perfil_saturacion.svg
  programar_pyspy "${PYSPY_MESETA_S:-$T_MESETA}" hilos_meseta.txt dump --pid 1
  info "py-spy programado: base ${PYSPY_BASE_S:-$T_BASE} s, saturación ${PYSPY_SATURACION_S:-$T_SAT} s, meseta ${PYSPY_MESETA_S:-$T_MESETA} s"
fi

# ---------------------------------------------------------------- k6
ulimit -n 10240 2>/dev/null || aviso "no se pudo subir ulimit -n a 10240 (§6.2)"
SALIDA="$DIR" BASE_URL="$BASE_URL" bash "$PERF/k6/correr_k6.sh" "$ESCENARIO" &
PID_K6SH=$!
K6_PID=""
for _ in $(seq 1 100); do
  K6_PID="$(pgrep -P "$PID_K6SH" -x k6 | head -1)" && [ -n "$K6_PID" ] && break
  sleep 0.1
done
if [ -n "$K6_PID" ]; then
  # psutil sobre k6 en el host: CPU por núcleo, del equipo y total (V-01: < 80 %).
  "$PY" "$PERF/monitor/monitor.py" "$K6_PID" --salida "$DIR/recursos_k6.csv" --equipo &
  TRABAJOS+=($!)
  if [ -n "${HUMO:-}" ]; then
    ( sleep "$HUMO"; info "HUMO: cortando k6 a los $HUMO s"; kill -INT "$K6_PID" 2>/dev/null ) &
    TRABAJOS+=($!)
  fi
else
  aviso "no se encontró el proceso de k6: no habrá recursos_k6.csv"
fi
CODIGO_K6=0
wait "$PID_K6SH"; CODIGO_K6=$?
while kill -0 "$PID_K6SH" 2>/dev/null; do wait "$PID_K6SH"; CODIGO_K6=$?; done  # si wait volvió por una señal

# ---------------------------------------------------------------- fin, recursos y log
"$PY" "$PERF/monitor/corrida.py" fin "$DIR" "$CODIGO_K6" || aviso "no se pudo registrar el fin en corrida.json"
sleep 2                                      # una última muestra de recursos ya sin tráfico
limpiar
TRABAJOS=()
wait 2>/dev/null
docker logs "$CONTENEDOR" 2>&1 | gzip > "$DIR/qolqe.log.gz"
if [ -f "$DIR/muestras.csv.gz" ] && [ "$(wc -c < "$DIR/muestras.csv.gz")" -gt 50000000 ]; then
  echo "muestras.csv.gz" > "$DIR/.gitignore"  # §7.3: no se versionan crudos de más de 50 MB (queda peticiones.csv.gz)
  aviso "muestras.csv.gz pasa de 50 MB: queda fuera de git (se versiona la versión compacta)"
fi

# ---------------------------------------------------------------- U-07: dinero antes y después (§5.5)
info "Verificando el dinero (U-07)"
CONCILIAR=()
[ -f "$DIR/muestras.csv.gz" ] && CONCILIAR=(--k6 "$DIR/muestras.csv.gz") || aviso "sin muestras de k6: C6 solo cuenta"
"$PY" "$PERF/integridad/verificar.py" comparar --antes /data/base_perf.db --despues /data/qolqe.db \
  ${CONCILIAR[@]+"${CONCILIAR[@]}"} --salida "$DIR/verificacion_dinero.txt" | grep -E "^C[0-9]|^TOTAL|^Resultado"
CODIGO_INTEGRIDAD=${PIPESTATUS[0]}

# ---------------------------------------------------------------- análisis y gráficos (§8: veredicto, tablas, G1–G10)
# graficos.py analiza la corrida (lo mismo que analizar.py) y además dibuja sus gráficos en graficos/.
if [ "${ANALIZAR:-1}" = 1 ]; then
  info "Analizando la corrida (veredicto, tablas y gráficos)"
  "${PYTHON_ANALISIS:-$PY}" "$PERF/analisis/graficos.py" "$DIR" \
    || aviso "el análisis falló (se repite con: .venv/bin/python tests/performance/analisis/graficos.py $DIR)"
fi
"$PY" "$PERF/monitor/corrida.py" cerrar "$DIR" "$CODIGO_INTEGRIDAD"

[ "$INTERRUMPIDA" = 1 ] && aviso "corrida interrumpida: si no vale, muévela a resultados/descartadas/ con un motivo.txt"
info "Fin: k6 = $CODIGO_K6 (0 = umbrales OK, 99 = algún umbral falló), integridad = $CODIGO_INTEGRIDAD (0 = PASA). $DIR"
[ "$CODIGO_K6" -ne 0 ] && exit "$CODIGO_K6"
exit "$CODIGO_INTEGRIDAD"
