"""Monitor de CPU y memoria de un proceso con psutil: el script del enunciado (P2 Parte 3, §5), adaptado.

Uso:  python monitor.py <PID> [--salida recursos.csv] [--equipo] [--cgroup]
      Se detiene con Ctrl+C o SIGTERM, o solo cuando el proceso termina.

Igual que el del enunciado: una fila por segundo con hora, cpu_% (p.cpu_percent(interval=1)) y memoria_MB
(RSS / 1e6), con flush en cada fila. Se agregan columnas al final, sin cambiar las tres primeras:
  siempre    ts (epoch en s, para cruzar con k6), hilos y descriptores (fugas en la resistencia, U-09 c)
  --equipo   cpu_k6_equipo_% (= cpu_% / núcleos) y cpu_total_equipo_%: criterio V-01 (< 80 %) para k6 en el host
  --cgroup   cpu_cgroup_% (100 % = 1 CPU), nr_throttled y throttled_usec (acumulados) del cgroup del
             proceso: Qolqe en Docker, medido desde un contenedor auxiliar con
             --pid=container:qolqe-perf --cgroupns=host (así el monitor no gasta la cuota de Qolqe)
cpu_% es respecto de 1 núcleo, como lo da psutil: con varios hilos puede pasar de 100 %.
"""
import argparse
import csv
import signal
import sys
import time
from pathlib import Path

import psutil


def leer_cpu_stat(ruta: Path) -> dict[str, int]:
    return {clave: int(valor) for clave, valor in (linea.split() for linea in ruta.read_text().splitlines())}


def ruta_cgroup(pid: int) -> Path | None:
    """cpu.stat del cgroup v2 del proceso (línea '0::/ruta' de /proc/<pid>/cgroup)."""
    try:
        ruta = Path(f"/proc/{pid}/cgroup").read_text().strip().split("::", 1)[1]
    except (OSError, IndexError):
        return None
    cpu_stat = Path("/sys/fs/cgroup") / ruta.lstrip("/") / "cpu.stat"
    return cpu_stat if cpu_stat.exists() else None


def detener(_senal, _marco):
    raise KeyboardInterrupt  # SIGTERM (docker stop, kill) termina igual que Ctrl+C


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pid", type=int)
    parser.add_argument("--salida", default="recursos.csv")
    parser.add_argument("--equipo", action="store_true", help="agrega el CPU del equipo (V-01)")
    parser.add_argument("--cgroup", action="store_true", help="agrega CPU y throttling del cgroup (Docker)")
    args = parser.parse_args()
    signal.signal(signal.SIGTERM, detener)

    p = psutil.Process(args.pid)
    nucleos = psutil.cpu_count()
    cpu_stat = ruta_cgroup(args.pid) if args.cgroup else None
    if args.cgroup and cpu_stat is None:
        print("monitor: no se encontró el cpu.stat del cgroup; se omiten esas columnas", file=sys.stderr)

    columnas = ["hora", "cpu_%", "memoria_MB", "ts", "hilos", "descriptores"]
    if args.equipo:
        columnas += ["cpu_k6_equipo_%", "cpu_total_equipo_%"]  # nombres del diseño §7.1
    if cpu_stat:
        columnas += ["cpu_cgroup_%", "nr_throttled", "throttled_usec"]

    with open(args.salida, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(columnas)
        f.flush()
        psutil.cpu_percent(None)
        previo = (time.time(), leer_cpu_stat(cpu_stat)) if cpu_stat else None
        try:
            while True:
                cpu = p.cpu_percent(interval=1)  # como el enunciado: mide durante 1 s
                ahora = time.time()
                fila = [time.strftime("%H:%M:%S"), cpu, round(p.memory_info().rss / 1e6, 1),
                        round(ahora, 3), p.num_threads(), p.num_fds()]
                if args.equipo:
                    fila += [round(cpu / nucleos, 1), psutil.cpu_percent(None)]
                if cpu_stat:
                    stat = leer_cpu_stat(cpu_stat)
                    t0, stat0 = previo
                    uso = (stat["usage_usec"] - stat0["usage_usec"]) / ((ahora - t0) * 1e6) * 100
                    fila += [round(uso, 1), stat["nr_throttled"], stat["throttled_usec"]]
                    previo = (ahora, stat)
                w.writerow(fila)
                f.flush()
        except (KeyboardInterrupt, psutil.NoSuchProcess, psutil.ZombieProcess, FileNotFoundError):
            pass  # Ctrl+C, SIGTERM o el proceso terminó: el CSV queda completo hasta la última fila


if __name__ == "__main__":
    main()
