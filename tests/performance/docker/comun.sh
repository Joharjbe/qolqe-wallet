# Funciones comunes de preparar.sh y correr.sh (se cargan con `source`; requieren config.env).

info()  { printf '\033[1;34m[perf]\033[0m %s\n' "$*"; }
aviso() { printf '\033[1;33m[perf] AVISO:\033[0m %s\n' "$*" >&2; }
fallo() { printf '\033[1;31m[perf] ERROR:\033[0m %s\n' "$*" >&2; exit 2; }

# Arranca un contenedor nuevo de Qolqe (proceso nuevo en cada corrida, diseño §5.2) con la cuota indicada.
# $1 = CPUs (1 al medir, CPUS_PREPARACION al preparar). Memoria y swap iguales: límite estricto (§6.1).
qolqe_arrancar() {
  local cpus="$1"
  docker rm -f "$CONTENEDOR" >/dev/null 2>&1 || true
  docker run -d --name "$CONTENEDOR" \
    --cpus="$cpus" --memory="$MEMORIA" --memory-swap="$MEMORIA" \
    -p "127.0.0.1:${PUERTO}:${PUERTO_INTERNO}" \
    -v "${VOLUMEN}:/data" \
    "$IMAGEN" >/dev/null || fallo "no se pudo arrancar $CONTENEDOR"
  qolqe_esperar_salud
}

# Espera a que /api/salud responda (máximo 90 s; la primera vez Qolqe crea la plantilla de la semilla).
qolqe_esperar_salud() {
  local i
  for i in $(seq 1 90); do
    curl -sf "${BASE_URL}/api/salud" >/dev/null 2>&1 && return 0
    sleep 1
  done
  docker logs --tail 30 "$CONTENEDOR" >&2 || true
  fallo "Qolqe no respondió en ${BASE_URL}/api/salud"
}

# Restaura la base de las corridas (diseño §5.2: antes de cada corrida se restaura base_perf.db; nunca se
# llama a /api/pruebas/reiniciar entre corridas). Se hace con Qolqe detenido, desde un contenedor auxiliar.
qolqe_restaurar_base() {
  docker rm -f "$CONTENEDOR" >/dev/null 2>&1 || true
  docker run --rm -v "${VOLUMEN}:/data" "$IMAGEN" sh -c \
    'test -f /data/base_perf.db && cp /data/base_perf.db /data/qolqe.db && rm -f /data/qolqe.db-wal /data/qolqe.db-shm' \
    || fallo "no existe base_perf.db en el volumen ${VOLUMEN}: ejecuta primero ./preparar.sh"
}

# Límites efectivos del cgroup (evidencia de V-05: con --cpus=1 deben dar "100000 100000" y 1073741824).
qolqe_cgroup() {
  docker exec "$CONTENEDOR" sh -c 'echo "cpu.max $(cat /sys/fs/cgroup/cpu.max)"; echo "memory.max $(cat /sys/fs/cgroup/memory.max)"; echo "memory.swap.max $(cat /sys/fs/cgroup/memory.swap.max 2>/dev/null)"; echo "nproc $(nproc)"'
}

# cpu.stat del contenedor (usage_usec, nr_throttled, throttled_usec): antes y después de cada corrida.
qolqe_cpu_stat() {
  docker exec "$CONTENEDOR" cat /sys/fs/cgroup/cpu.stat
}

# Intérprete de Python del host: el .venv del repo (tiene psutil) o, si no existe, python3.
python_host() {
  if [ -n "${PYTHON:-}" ]; then echo "$PYTHON"
  elif [ -x "$RAIZ/.venv/bin/python" ]; then echo "$RAIZ/.venv/bin/python"
  else command -v python3
  fi
}
