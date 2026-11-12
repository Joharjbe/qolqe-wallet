#!/usr/bin/env bash
# Prepara el entorno y los datos de las pruebas de rendimiento (diseño §5.2 y §10.2, pasos 1 y 2).
# Se ejecuta UNA vez, el mismo día de las corridas (los vencimientos y la ventana de 30 días son relativos).
#
# Uso:  tests/performance/preparar.sh [N]        N = usuarios de carga (por defecto 3000, M-16)
#       SIN_BUILD=1 tests/performance/preparar.sh 220   reutiliza la imagen ya construida
#
# 1 imagen (docker/Dockerfile) y comparación de versiones con el .venv → 2 contenedor de preparación con
# --cpus=$CPUS_PREPARACION → 3 datos/preparar_datos.py (usuarios, saldos, contactos, historial, deudas,
# base_perf.db, usuarios.csv) → 4 contenedor de medición con --cpus=$CPUS --memory=$MEMORIA → 5 evidencia del
# entorno en resultados/entorno/ (entorno.json, pip_freeze.txt, cgroup.txt, preparacion.json).
set -euo pipefail

PERF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(cd "$PERF/../.." && pwd)"
source "$PERF/docker/config.env"
source "$PERF/docker/comun.sh"

N="${1:-$N_USUARIOS}"
PY="$(python_host)"
# RESULTADOS y USUARIOS_CSV permiten preparar un ensayo fuera del repo (por defecto: resultados/ y datos/usuarios.csv).
ENTORNO="${RESULTADOS:-$PERF/resultados}/entorno"
USUARIOS_CSV="${USUARIOS_CSV:-$PERF/datos/usuarios.csv}"
mkdir -p "$ENTORNO"

# 1) Imagen y versiones (diseño §10.2, paso 1: pip freeze igual al .venv, FastAPI 0.117.1)
if [ "${SIN_BUILD:-0}" != 1 ]; then
  info "Construyendo $IMAGEN desde $RAIZ"
  docker build -f "$PERF/docker/Dockerfile" -t "$IMAGEN" "$RAIZ"
fi
docker run --rm "$IMAGEN" cat /app/pip_freeze.txt > "$ENTORNO/pip_freeze.txt"
distintas=""
while read -r linea; do
  grep -qixF "$linea" "$ENTORNO/pip_freeze.txt" || distintas="$distintas $linea"
done < <(grep -E '^[A-Za-z]' "$PERF/docker/versiones.txt")
[ -z "$distintas" ] && info "Versiones de la imagen = versiones.txt (.venv)" || aviso "versiones distintas al .venv:$distintas"

# 2) Contenedor de preparación: más CPU porque la preparación no se mide (§5.2)
info "Contenedor de preparación: --cpus=$CPUS_PREPARACION --memory=$MEMORIA, puerto $PUERTO"
docker volume create "$VOLUMEN" >/dev/null
qolqe_arrancar "$CPUS_PREPARACION"

# 3) Datos y base_perf.db (§5.2). Es el único lugar donde se llama a /api/pruebas/reiniciar.
"$PY" "$PERF/datos/preparar_datos.py" --n "$N" --url "$BASE_URL" --hilos "$HILOS_PREPARACION" \
  --csv "$USUARIOS_CSV" --informe "$ENTORNO/preparacion.json"

# 4) Contenedor de medición, con la cuota del entorno elegido (§6.1). La base ya es igual a base_perf.db.
info "Contenedor de medición: --cpus=$CPUS --memory=$MEMORIA --memory-swap=$MEMORIA"
qolqe_arrancar "$CPUS"
qolqe_cgroup | tee "$ENTORNO/cgroup.txt"

# 5) Especificaciones del equipo y versiones (§6.2 de la plantilla)
"$PY" "$PERF/monitor/corrida.py" entorno "$ENTORNO/entorno.json"
info "Listo. Evidencia del entorno en $ENTORNO. Siguiente paso: tests/performance/correr.sh referencia"
