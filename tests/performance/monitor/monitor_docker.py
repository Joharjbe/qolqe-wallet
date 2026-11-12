"""Monitor de recursos del contenedor de Qolqe con `docker stats` (enunciado §5: "Docker: docker stats").

Uso:  python monitor_docker.py <contenedor> <salida.csv>
      Se detiene con Ctrl+C o SIGTERM, o solo cuando el contenedor se detiene.

Columnas: hora, cpu_%, memoria_MB (como el script psutil del enunciado) + ts (epoch en s), memoria_% y pids.
Aquí cpu_% es del contenedor completo y 100 % = 1 CPU, que es la cuota de Qolqe (--cpus=1, diseño §6.1).
memoria_MB es la que reporta Docker para el cgroup (incluye la caché de páginas de la base; el RSS del
proceso lo da monitor.py). docker stats emite una muestra por segundo aprox.; se guarda una por segundo.
"""
import csv
import json
import re
import signal
import subprocess
import sys
import time

ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
UNIDADES = {"B": 1e-6, "kB": 1e-3, "KB": 1e-3, "KiB": 1024 / 1e6, "MB": 1.0, "MiB": 1024**2 / 1e6,
            "GB": 1e3, "GiB": 1024**3 / 1e6}


def a_mb(texto: str) -> float:
    numero, unidad = re.match(r"([\d.]+)\s*([A-Za-z]+)", texto).groups()
    return round(float(numero) * UNIDADES[unidad], 1)


def detener(_senal, _marco):
    raise KeyboardInterrupt


def main() -> None:
    contenedor, salida = sys.argv[1], sys.argv[2]
    signal.signal(signal.SIGTERM, detener)
    proceso = subprocess.Popen(["docker", "stats", contenedor, "--format", "{{json .}}"],
                               stdout=subprocess.PIPE, text=True)
    with open(salida, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["hora", "cpu_%", "memoria_MB", "ts", "memoria_%", "pids"])
        f.flush()
        ultima = None
        try:
            for linea in proceso.stdout:
                linea = ANSI.sub("", linea).strip()
                if not linea.startswith("{"):
                    continue
                d = json.loads(linea)
                ahora = time.time()
                hora = time.strftime("%H:%M:%S", time.localtime(ahora))
                if hora == ultima or d.get("CPUPerc", "--") == "--":  # repetida en el mismo segundo o sin dato
                    continue
                ultima = hora
                w.writerow([hora, d["CPUPerc"].rstrip("%"), a_mb(d["MemUsage"].split(" / ")[0]),
                            round(ahora, 3), d["MemPerc"].rstrip("%"), d["PIDs"]])
                f.flush()
        except KeyboardInterrupt:
            pass
        finally:
            proceso.terminate()


if __name__ == "__main__":
    main()
