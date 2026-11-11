#!/usr/bin/env bash
# Corre un escenario de k6 y deja su evidencia en resultados/<escenario>/<AAAAMMDD-HHMM>/ (diseño §7.1 y §7.3):
#   consola.txt       salida de k6 (avance, avisos como "Insufficient VUs" para V-07, umbrales ✓/✗)
#   resumen.json/.txt handleSummary: datos de k6 + veredicto por umbral + hora de inicio y fin (Lima)
#   reporte.html      dashboard web de k6 exportado (período de 10 s)
#   muestras.csv.gz   datos crudos de k6 (una fila por muestra, timestamp en ms)
# Devuelve el código de salida de k6: 0 = todos los umbrales pasan, 99 = alguno falló (paso 1 de S14).
#
# Uso: tests/performance/k6/correr_k6.sh <escenario> [opciones extra de "k6 run"]
#   escenarios: referencia calibracion carga pico estres resistencia demo capacidad
#   Variables opcionales: BASE_URL (http://127.0.0.1:8090)  SALIDA (carpeta de la corrida)  TOP (estrés, M-14)
#                         L_CAP (capacidad)  USUARIOS_CSV (por defecto datos/usuarios.csv)
#                         ESCALA (ensayo comprimido, p. ej. 0.1: todo el escenario en 1/10 del tiempo; no es evidencia)
#                         K6_WEB_DASHBOARD_PORT (5665: la demo se ve en http://localhost:5665)
set -uo pipefail

ESCENARIO="${1:?Uso: correr_k6.sh <escenario> [opciones de k6 run]}"
shift
DIR="$(cd "$(dirname "$0")" && pwd)"
RESULTADOS="$(dirname "$DIR")/resultados"

# Carpeta de la corrida: hora de Lima, para cruzarla con los CSV de recursos (D11).
if [ -z "${SALIDA:-}" ]; then
  SALIDA="$RESULTADOS/$ESCENARIO/$(TZ=America/Lima date +%Y%m%d-%H%M)"
  [ -e "$SALIDA" ] && SALIDA="$SALIDA$(TZ=America/Lima date +%S)"
fi
mkdir -p "$SALIDA"

PARAMETROS=(-e "ESCENARIO=$ESCENARIO" -e "SALIDA=$SALIDA" -e "BASE_URL=${BASE_URL:-http://127.0.0.1:8090}")
[ -n "${TOP:-}" ] && PARAMETROS+=(-e "TOP=$TOP")
[ -n "${L_CAP:-}" ] && PARAMETROS+=(-e "L_CAP=$L_CAP")
[ -n "${USUARIOS_CSV:-}" ] && PARAMETROS+=(-e "USUARIOS_CSV=$USUARIOS_CSV")
[ -n "${ESCALA:-}" ] && [ "$ESCALA" != 1 ] && PARAMETROS+=(-e "ESCALA=$ESCALA")   # ensayo comprimido (escenarios.js)

echo "k6 $ESCENARIO → $SALIDA"
K6_WEB_DASHBOARD=true \
K6_WEB_DASHBOARD_EXPORT="$SALIDA/reporte.html" \
K6_WEB_DASHBOARD_PERIOD="${K6_WEB_DASHBOARD_PERIOD:-10s}" \
K6_WEB_DASHBOARD_OPEN=false \
K6_CSV_TIME_FORMAT=unix_milli \
  k6 run --no-usage-report "${PARAMETROS[@]}" --out "csv=$SALIDA/muestras.csv.gz" "$@" "$DIR/qolqe.js" 2>&1 \
  | tee "$SALIDA/consola.txt"
CODIGO=${PIPESTATUS[0]} # el código de k6, no el de tee (si no, un umbral fallido parecería un éxito)

echo "$CODIGO" > "$SALIDA/codigo_salida_k6.txt"
echo "Resultados en $SALIDA (código de salida de k6: $CODIGO)"
exit "$CODIGO"
