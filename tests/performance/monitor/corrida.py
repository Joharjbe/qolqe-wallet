"""Registro de cada corrida (corrida.json) y del entorno (entorno.json). Lo llaman correr.sh y preparar.sh.

Enunciado §5: "Registren la hora de inicio y fin de cada prueba para cruzar los recursos con los resultados".
  python corrida.py esperar-equipo [carpeta]           V-04: espera CPU ocioso ≥ OCIOSO_MIN % (máx. ESPERA_MAX s);
                                                       con carpeta deja la medición en v04.json para corrida.json
  python corrida.py inicio <carpeta> <escenario>       hora de inicio, versiones, cgroup, cpu.stat, V-04 y V-05
  python corrida.py fin <carpeta> <codigo_k6>          al terminar k6: hora de fin, cpu.stat y Δ (y M-14)
  python corrida.py cerrar <carpeta> <codigo_integridad>   resultado de U-07 y lista de archivos
  python corrida.py entorno <archivo.json>             especificaciones del equipo, Docker, k6 e imagen (§6.2)
Lee CONTENEDOR, IMAGEN, CPUS, MEMORIA, OCIOSO_MIN, CARGA_MAX y ESPERA_MAX del entorno (docker/config.env).

V-04 (cambio del 11-nov, documentado en el README §4): en esta Mac la carga promedio de 1 min no baja de ~3-4 aunque
el equipo esté ocioso (la sostienen los procesos del sistema), así que "carga < 1.5" del diseño no se puede cumplir.
El criterio que decide es el CPU ocioso medido con `top -l 2 -n 0 -s 3` (segunda muestra, 3 s) ≥ OCIOSO_MIN (65 %);
la carga de 1 min se sigue registrando en corrida.json junto al CPU ocioso.
"""
import json
import math
import os
import re
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


def cpu_ocioso() -> float | None:
    """% de CPU ocioso del equipo según top: segunda muestra de 3 s (la primera es el promedio desde el arranque)."""
    valores = re.findall(r"([\d.]+)% idle", sh("top", "-l", "2", "-n", "0", "-s", "3"))
    return float(valores[-1]) if valores else None


def medir_equipo() -> dict:
    """V-04: CPU ocioso (decide) y carga promedio de 1, 5 y 15 min (se registra)."""
    ocioso, minimo = cpu_ocioso(), float(ENV("OCIOSO_MIN", "65"))
    return {"criterio": f"CPU ocioso (top, 3 s) >= {minimo:g} %", "cpu_ocioso_%": ocioso, "ocioso_min_%": minimo,
            "carga_1_5_15": [round(x, 2) for x in os.getloadavg()],
            "carga_max_diseno": float(ENV("CARGA_MAX", "1.5")),
            "ok": ocioso is not None and ocioso >= minimo}


def esperar_equipo(carpeta: Path | None = None) -> int:
    """V-04: el equipo libre antes de empezar (CPU ocioso ≥ OCIOSO_MIN; la carga solo se registra).
    Con carpeta, guarda la medición con la que se decidió en carpeta/v04.json: inicio() la pasa a corrida.json."""
    espera = int(ENV("ESPERA_MAX", "900"))
    fin = time.time() + espera
    while not (m := medir_equipo())["ok"]:
        if carpeta:
            (carpeta / "v04.json").write_text(json.dumps(m | {"hora": ahora()["hora"]}, ensure_ascii=False))
        if time.time() > fin:
            print(f"V-04: CPU ocioso {m['cpu_ocioso_%']} % (< {m['ocioso_min_%']:g} %) después de {espera} s; "
                  f"carga {m['carga_1_5_15'][0]}", file=sys.stderr)
            return 1
        print(f"V-04: CPU ocioso {m['cpu_ocioso_%']} % < {m['ocioso_min_%']:g} % (carga {m['carga_1_5_15'][0]}); "
              "esperando…", file=sys.stderr)
        time.sleep(12)
    if carpeta:
        (carpeta / "v04.json").write_text(json.dumps(m | {"hora": ahora()["hora"]}, ensure_ascii=False))
    print(f"V-04: CPU ocioso {m['cpu_ocioso_%']} % ≥ {m['ocioso_min_%']:g} % (carga de 1 min {m['carga_1_5_15'][0]}, "
          "solo se registra)")
    return 0


def _v04_espera(carpeta: Path) -> dict | None:
    archivo = carpeta / "v04.json"
    if not archivo.exists():
        return None
    datos = json.loads(archivo.read_text())
    archivo.unlink()   # queda dentro de corrida.json
    return datos


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
        "parametros": {k: ENV(k) for k in ("TOP", "L_CAP", "ESCALA", "HUMO", "BASE_URL", "CPUS", "MEMORIA", "USUARIOS_CSV",
                                           "OCIOSO_MIN", "PYSPY", "PYSPY_BASE_S", "PYSPY_SATURACION_S", "PYSPY_MESETA_S",
                                           "PYSPY_DURACION") if ENV(k)},
        "commit": sh("git", "-C", str(PERF), "rev-parse", "HEAD"),
        "cambios_sin_commit": bool(sh("git", "-C", str(PERF), "status", "--porcelain", "--", ".", ":(exclude)resultados")),
        "versiones": {"k6": sh("k6", "version").splitlines()[0] if sh("k6", "version") else "",
                      "docker": sh("docker", "version", "--format", "{{.Server.Version}}"),
                      "imagen": ENV("IMAGEN", "qolqe-perf:p3"),
                      "imagen_id": sh("docker", "inspect", "-f", "{{.Image}}", ENV("CONTENEDOR", "qolqe-perf"))},
        # V-04: la medición con la que esperar-equipo decidió empezar (v04.json); sin ella (humo, ensayo), una nueva.
        # Se agrega una segunda medición al arrancar Qolqe, solo informativa (el CPU ocioso varía de un segundo a otro).
        "v04": (v04 := _v04_espera(carpeta) or medir_equipo()),
        "v04_al_iniciar": medir_equipo(),
        "carga_equipo_antes": v04["carga_1_5_15"][0],        # V-04 del diseño: carga promedio de 1 min (solo se registra)
        "cpu_ocioso_antes": v04["cpu_ocioso_%"],             # V-04 que decide
        "v04_ok": v04["ok"],
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
        sys.exit(esperar_equipo(Path(resto[0]) if resto else None))
    elif orden == "inicio":
        sys.exit(inicio(Path(resto[0]), resto[1]))
    elif orden == "fin":
        sys.exit(fin(Path(resto[0]), resto[1]))
    elif orden == "cerrar":
        sys.exit(cerrar(Path(resto[0]), resto[1]))
    elif orden == "entorno":
        sys.exit(entorno(Path(resto[0])))
    sys.exit(__doc__)
