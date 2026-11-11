"""Registro de cada corrida (corrida.json) y del entorno (entorno.json). Lo llaman correr.sh y preparar.sh.

Enunciado §5: "Registren la hora de inicio y fin de cada prueba para cruzar los recursos con los resultados".
  python corrida.py esperar-equipo                     V-04: espera carga de 1 min < CARGA_MAX (máx. ESPERA_MAX s)
  python corrida.py inicio <carpeta> <escenario>       hora de inicio, versiones, cgroup, cpu.stat, V-04 y V-05
  python corrida.py fin <carpeta> <codigo_k6>          al terminar k6: hora de fin, cpu.stat y Δ (y M-14)
  python corrida.py cerrar <carpeta> <codigo_integridad>   resultado de U-07 y lista de archivos
  python corrida.py entorno <archivo.json>             especificaciones del equipo, Docker, k6 e imagen (§6.2)
Lee CONTENEDOR, IMAGEN, CPUS, MEMORIA, CARGA_MAX y ESPERA_MAX del entorno (docker/config.env).
"""
import json
import math
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

PERF = Path(__file__).resolve().parent.parent
LIMA = ZoneInfo("America/Lima")
ENV = os.environ.get


def sh(*orden: str) -> str:
    salida = subprocess.run(orden, capture_output=True, text=True, check=False)
    return salida.stdout.strip() if salida.returncode == 0 else ""


def ahora() -> dict:
    t = time.time()
    return {"hora": datetime.fromtimestamp(t, LIMA).isoformat(timespec="seconds"), "epoch": round(t, 3)}


def en_qolqe(*orden: str) -> str:
    return sh("docker", "exec", ENV("CONTENEDOR", "qolqe-perf"), *orden)


def cpu_stat() -> dict:
    return {k: int(v) for k, v in (linea.split() for linea in en_qolqe("cat", "/sys/fs/cgroup/cpu.stat").splitlines())}


def a_bytes(memoria: str) -> int:
    unidades = {"k": 1024, "m": 1024**2, "g": 1024**3}
    return int(float(memoria[:-1]) * unidades[memoria[-1].lower()]) if memoria[-1].isalpha() else int(memoria)


def carga() -> float:
    return round(os.getloadavg()[0], 2)


def esperar_equipo() -> int:
    """V-04: el equipo libre antes de empezar (carga de 1 min < CARGA_MAX)."""
    limite, espera = float(ENV("CARGA_MAX", "1.5")), int(ENV("ESPERA_MAX", "900"))
    fin = time.time() + espera
    while carga() >= limite:
        if time.time() > fin:
            print(f"V-04: la carga sigue en {carga()} (≥ {limite}) después de {espera} s", file=sys.stderr)
            return 1
        print(f"V-04: carga {carga()} ≥ {limite}; esperando…", file=sys.stderr)
        time.sleep(15)
    print(f"V-04: carga {carga()} < {limite}")
    return 0


def inicio(carpeta: Path, escenario: str) -> int:
    cpus, memoria = ENV("CPUS", "1"), ENV("MEMORIA", "1g")
    cpu_max, memory_max = en_qolqe("cat", "/sys/fs/cgroup/cpu.max"), en_qolqe("cat", "/sys/fs/cgroup/memory.max")
    huella = json.loads(sh(sys.executable, str(PERF / "integridad" / "verificar.py"), "foto") or "{}")
    base = json.loads(en_qolqe("cat", "/data/base_perf.json") or "{}")
    v05 = {
        "base_igual_a_base_perf": bool(huella) and huella == base.get("huella"),
        "cpu_max": cpu_max, "cpu_max_ok": cpu_max == f"{round(float(cpus) * 100000)} 100000",
        "memory_max": memory_max, "memory_max_ok": memory_max == str(a_bytes(memoria)),
        "contenedor_iniciado": sh("docker", "inspect", "-f", "{{.State.StartedAt}}", ENV("CONTENEDOR", "qolqe-perf")),
    }
    v05["ok"] = v05["base_igual_a_base_perf"] and v05["cpu_max_ok"] and v05["memory_max_ok"]
    hoy = datetime.now(LIMA).date().isoformat()
    datos = {
        "escenario": escenario,
        "humo": ENV("HUMO") or None,
        "inicio": ahora(),
        "parametros": {k: ENV(k) for k in ("TOP", "L_CAP", "ESCALA", "HUMO", "BASE_URL", "CPUS", "MEMORIA", "USUARIOS_CSV")
                       if ENV(k)},
        "commit": sh("git", "-C", str(PERF), "rev-parse", "HEAD"),
        "cambios_sin_commit": bool(sh("git", "-C", str(PERF), "status", "--porcelain", "--", ".", ":(exclude)resultados")),
        "versiones": {"k6": sh("k6", "version").splitlines()[0] if sh("k6", "version") else "",
                      "docker": sh("docker", "version", "--format", "{{.Server.Version}}"),
                      "imagen": ENV("IMAGEN", "qolqe-perf:p3"),
                      "imagen_id": sh("docker", "inspect", "-f", "{{.Image}}", ENV("CONTENEDOR", "qolqe-perf"))},
        "carga_equipo_antes": carga(),                       # V-04 (carga promedio de 1 min)
        "v04_ok": carga() < float(ENV("CARGA_MAX", "1.5")),
        "base_identica": v05["base_igual_a_base_perf"],      # V-05 (las claves planas las lee analisis/)
        "cpu_max": cpu_max,
        "memory_max": memory_max,
        "nucleos": os.cpu_count(),
        "v05": v05,
        "base_perf": {"fecha": base.get("fecha"), "n": base.get("n"), "es_de_hoy": base.get("fecha") == hoy,
                      "huella": base.get("huella")},
        "huella_restaurada": huella,
        "cpu_stat_antes": cpu_stat(),
    }
    (carpeta / "corrida.json").write_text(json.dumps(datos, indent=1, ensure_ascii=False))
    if not v05["ok"]:
        print(f"V-05 no se cumple: {json.dumps(v05, ensure_ascii=False)}", file=sys.stderr)
    if not datos["base_perf"]["es_de_hoy"]:
        print(f"AVISO: base_perf.db es del {base.get('fecha')}; el diseño pide generarla el mismo día (§5.2)",
              file=sys.stderr)
    return 0 if v05["ok"] else 3


def fin(carpeta: Path, codigo_k6: str) -> int:
    """Justo al terminar k6: hora de fin, cpu.stat después (y su Δ) y código de salida de k6."""
    archivo = carpeta / "corrida.json"
    datos = json.loads(archivo.read_text())
    antes, despues = datos["cpu_stat_antes"], cpu_stat()
    delta = {k: despues[k] - antes.get(k, 0) for k in despues}
    datos |= {
        "fin": ahora(),
        "duracion_s": round(time.time() - datos["inicio"]["epoch"], 1),
        "cpu_stat_despues": despues,
        "cpu_stat_delta": delta,
        "codigo_salida_k6": int(codigo_k6),  # 0 = umbrales OK; 99 = algún umbral falló; otro = k6 cortado o con error
    }
    resumen = carpeta / "resumen.json"
    if datos["escenario"] == "calibracion" and resumen.exists():
        # M-14: D_sesión = Δusage_usec ÷ sesiones; L_sat = W ÷ D (W = 120 s, M-02); TOP = ⌈1.33 × L_sat⌉₁₀₀
        sesiones = json.loads(resumen.read_text())["metrics"]["iterations"]["values"]["count"]
        d = delta["usage_usec"] / 1e6 / sesiones
        datos["calibracion"] = {"sesiones": sesiones, "d_sesion_s": round(d, 4), "l_sat": round(120 / d),
                                "top": math.ceil(1.33 * 120 / d / 100) * 100}
        print(f"Calibración (M-14): D = {d * 1000:.1f} ms de CPU por sesión → L_sat ≈ {120 / d:.0f}; "
              f"TOP sugerido = {datos['calibracion']['top']}")
    archivo.write_text(json.dumps(datos, indent=1, ensure_ascii=False))
    return 0


def cerrar(carpeta: Path, codigo_integridad: str) -> int:
    """Al final de correr.sh: resultado de la verificación del dinero (U-07) y lista de archivos de la corrida."""
    archivo = carpeta / "corrida.json"
    datos = json.loads(archivo.read_text())
    datos["codigo_integridad"] = int(codigo_integridad)  # 0 = U-07 PASA; 1 = descuadre; 2 = no se pudo verificar
    datos["archivos"] = sorted(str(p.relative_to(carpeta)) for p in carpeta.rglob("*") if p.is_file())
    archivo.write_text(json.dumps(datos, indent=1, ensure_ascii=False))
    return 0


def entorno(archivo: Path) -> int:
    def sysctl(clave: str) -> str:
        return sh("sysctl", "-n", clave)
    datos = {
        "fecha": ahora(),
        "equipo": {"modelo": sysctl("hw.model"), "cpu": sysctl("machdep.cpu.brand_string"),
                   "nucleos": sysctl("hw.ncpu"), "nucleos_rendimiento": sysctl("hw.perflevel0.physicalcpu"),
                   "nucleos_eficiencia": sysctl("hw.perflevel1.physicalcpu"),
                   "memoria_GB": round(int(sysctl("hw.memsize") or 0) / 1024**3, 1),
                   "macos": sh("sw_vers", "-productVersion"), "maxfiles": sh("launchctl", "limit", "maxfiles"),
                   "somaxconn": sysctl("kern.ipc.somaxconn")},
        "docker": {"motor": sh("docker", "version", "--format", "{{.Server.Version}}"),
                   "vm": sh("docker", "info", "--format",
                            "cpus={{.NCPU}} memoria={{.MemTotal}} kernel={{.KernelVersion}} cgroup=v{{.CgroupVersion}}")},
        "k6": sh("k6", "version"),
        "imagen": {"nombre": ENV("IMAGEN", "qolqe-perf:p3"),
                   "id": sh("docker", "image", "inspect", "-f", "{{.Id}}", ENV("IMAGEN", "qolqe-perf:p3")),
                   "python": sh("docker", "run", "--rm", ENV("IMAGEN", "qolqe-perf:p3"), "python", "--version")},
        "python_host": sh(sys.executable, "--version"),
        "limites_qolqe": {"cpus": ENV("CPUS", "1"), "memoria": ENV("MEMORIA", "1g")},
        "commit": sh("git", "-C", str(PERF), "rev-parse", "HEAD"),
    }
    archivo.write_text(json.dumps(datos, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    orden, *resto = sys.argv[1:] or ["-h"]
    if orden == "esperar-equipo":
        sys.exit(esperar_equipo())
    elif orden == "inicio":
        sys.exit(inicio(Path(resto[0]), resto[1]))
    elif orden == "fin":
        sys.exit(fin(Path(resto[0]), resto[1]))
    elif orden == "cerrar":
        sys.exit(cerrar(Path(resto[0]), resto[1]))
    elif orden == "entorno":
        sys.exit(entorno(Path(resto[0])))
    sys.exit(__doc__)
