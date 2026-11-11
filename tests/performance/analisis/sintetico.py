"""Genera corridas SINTÉTICAS con el formato real de k6 2.3.0 (--out csv, K6_CSV_TIME_FORMAT=unix_milli) y de los monitores,
para probar el análisis y los gráficos sin ejecutar Qolqe. Los números son inventados: nunca van al informe.

Uso:
  .venv/bin/python tests/performance/analisis/sintetico.py <carpeta_salida> [--escenarios carga pico …] [--semilla 7]
  .venv/bin/python tests/performance/analisis/graficos.py --todo --resultados <carpeta_salida>

Modelo simple: Qolqe con 1 CPU y D = 69 ms de CPU por sesión (hipótesis M-14). La utilización ρ = λ·D infla los tiempos
(1/(1−ρ)) y, si pasa de 1, se acumula una cola que termina en timeouts y 5xx (lo que se espera ver en el estrés).
"""
import argparse
import heapq
import json
import math
import random
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from config import EP_OTRAS, MEZCLA, REQ_POR_SESION
from metricas import concurrencia
from perfiles import fase_en, intervalo_campana, perfil, peticiones_ofrecidas, tasa_llegada

LIMA = ZoneInfo("America/Lima")
D_SESION = 0.069                     # M-14 (hipótesis): s de CPU por sesión
COSTO_MS = {"login": 55, "saldo": 9, "perfil": 8, "movimientos": 28, "comision": 7, "transferir": 110, "contactos_listar": 10,
            "contactos_buscar": 12, "recargas_config": 6, "recargar": 25, "empresas": 6, "deudas": 9, "pagar": 30,
            "limites": 7, "alertas": 8, "solicitudes": 9, "dispositivos": 7, "sesiones": 8}
OPERACIONES = {"saldo_perfil": ["saldo", "perfil"], "movimientos": ["movimientos"], "transferir": ["comision", "transferir"],
               "contactos": ["contactos_listar", "contactos_buscar"], "recarga": ["recargas_config", "recargar"],
               "deudas": ["empresas", "deudas"], "pago": ["empresas", "deudas", "pagar"], "limites": ["limites"],
               "alertas": ["alertas"], "solicitudes": ["solicitudes"], "dispositivos": ["dispositivos"], "sesiones": ["sesiones"]}
NOMBRES = {"login": "POST /api/auth/login", "saldo": "GET /api/cuentas/me/saldo", "perfil": "GET /api/cuentas/me",
           "movimientos": "GET /api/movimientos", "comision": "GET /api/transferencias/comision", "transferir": "POST /api/transferencias",
           "contactos_listar": "GET /api/contactos", "contactos_buscar": "GET /api/contactos?buscar", "recargas_config": "GET /api/recargas/configuracion",
           "recargar": "POST /api/recargas", "empresas": "GET /api/servicios/empresas", "deudas": "GET /api/servicios/deudas",
           "pagar": "POST /api/servicios/pagos", "limites": "GET /api/limites", "alertas": "GET /api/alertas",
           "solicitudes": "GET /api/solicitudes", "dispositivos": "GET /api/dispositivos", "sesiones": "GET /api/sesiones"}
DINERO = {"transferir", "recargar", "pagar"}
ERRORES_DATOS = {"transferir": (0.0004, 422, "SALDO_INSUFICIENTE"), "recargar": (0.0006, 422, "LIMITE_RECARGAS"),
                 "pagar": (0.002, 409, "DEUDA_YA_PAGADA")}
INICIOS = {"referencia": "16:30", "calibracion": "16:35", "carga": "17:00", "pico": "17:25", "estres": "17:55",
           "resistencia": "18:35", "demo": "19:45"}
SIN_FASES = ("referencia", "calibracion", "demo")    # k6/escenarios.js les pone fase=unica
MAX_VUS = {"carga": 200, "resistencia": 200, "pico": 600, "estres": 3000, "demo": 250}


class Simulador:
    def __init__(self, escenario: str, t0: float, rng: random.Random):
        self.esc, self.t0, self.rng = escenario, t0, rng
        self.k6 = escenario                            # nombre del escenario de k6 (en la demo hay dos)
        self.datos_en_op = False                       # la operación en curso tuvo un 4xx de negocio
        self.p = perfil(escenario)
        self.filas: list[list] = []
        fin = sum(d for d, _ in self.p.etapas) + 400 if self.p.etapas else 600
        self.rejilla = np.arange(0, fin)
        rho = peticiones_ofrecidas(self.p, self.rejilla) / REQ_POR_SESION * D_SESION if self.p.etapas else np.zeros(fin)
        self.rho = np.nan_to_num(rho)
        self.cola = np.zeros_like(self.rho)            # s de trabajo atrasado cuando ρ > 1
        for i in range(1, len(self.rho)):
            self.cola[i] = max(0.0, self.cola[i - 1] + self.rho[i] - 1)

    def _fila(self, metrica, t, valor, extra="", **k):
        self.filas.append([metrica, int((self.t0 + t) * 1000), f"{valor:.6f}", "", k.get("error", ""), k.get("error_code", ""),
                           k.get("expected", ""), k.get("group", ""), k.get("method", ""), k.get("name", ""), k.get("proto", ""),
                           k.get("scenario", self.k6),
                           "", k.get("status", ""), "", "", k.get("name", ""), extra, ""])

    def _tiempo(self, ep: str, t: float) -> float:
        i = min(int(t), len(self.rho) - 1)
        base = COSTO_MS[ep] * (1 + 0.04 * t / 3600 if ep == "movimientos" else 1)       # el historial crece (§5.3)
        if self.esc == "demo" and 100 <= t < 145:
            base *= 25                                                                     # 50 VUs sin pausa: CPU al 100 %
        return base * self.rng.lognormvariate(0, 0.35) / (1 - min(self.rho[i], 0.9)) + self.cola[i] * 1000 * self.rng.uniform(0.6, 1)

    def peticion(self, ep: str, op: str, t: float, etiquetas: str) -> tuple[float, bool]:
        """Simula una petición que empieza en t. Devuelve (t de fin, falló por rendimiento)."""
        dur = self._tiempo(ep, t)
        status, error, codigo = (201 if ep in DINERO else 200), "", ""
        i = min(int(t), len(self.cola) - 1)
        if dur >= 30_000:
            dur, status, error, codigo = 30_000.0, 0, "request timeout", "1050"
            self._fila("errores_rendimiento", t + dur / 1000, 1, f"ep={ep}&{etiquetas}&tipo=timeout")
        elif self.rng.random() < 0.0002 + min(0.08, self.cola[i] / 150) * (ep in DINERO):
            status = 500
            self._fila("errores_rendimiento", t + dur / 1000, 1, f"ep={ep}&{etiquetas}&tipo=http_5xx")
        elif ep in ERRORES_DATOS and self.rng.random() < ERRORES_DATOS[ep][0]:
            status = ERRORES_DATOS[ep][1]
            self._fila("errores_datos", t + dur / 1000, 1, f"{etiquetas}&codigo={ERRORES_DATOS[ep][2]}")
            self.datos_en_op = True
        fin = t + dur / 1000
        comun = {"method": NOMBRES[ep].split()[0], "name": NOMBRES[ep], "proto": "HTTP/1.1", "status": str(status),
                 "expected": "true" if 0 < status < 500 else "false", "error": error, "error_code": codigo}
        extra = f"ep={ep}&{etiquetas}&grupo={'dinero' if ep in DINERO else 'consulta'}"
        self._fila("http_reqs", fin, 1, extra, **comun)
        self._fila("http_req_duration", fin, dur, extra, **comun)
        self._fila("http_req_connecting", fin, self.rng.uniform(0.2, 0.9), extra, **comun)   # uvicorn cierra el keep-alive a los 5 s
        self._fila("http_req_failed", fin, float(not 0 < status < 500), extra, **comun)
        if ep in DINERO and status == 201:
            self._fila("dinero_confirmado", fin, 1, f"ep={ep}")
        return fin, status == 0 or status >= 500

    def etiquetas(self, op: str, t: float) -> str:
        """Como k6/escenarios.js: op (las 5 "otras" van con op=otras), fase ('unica' sin fases) y campana en el pico."""
        fase = "unica" if self.esc in SIN_FASES else fase_en(self.p, np.array([t]))[0]
        texto = f"op={'otras' if op in EP_OTRAS else op}&fase={fase}"
        campana = intervalo_campana(self.p)
        if campana:
            texto += f"&campana={'si' if campana[0] <= t < campana[1] else 'no'}"
        return texto

    def _fin_operacion(self, t: float, fallo: bool, etiquetas: str) -> None:
        """operacion_fallida (U-03) y operacion_error_datos (V-02): una muestra por operación."""
        self._fila("operacion_fallida", t, float(fallo), etiquetas)
        self._fila("operacion_error_datos", t, float(self.datos_en_op and not fallo), etiquetas)

    def sesion(self, t: float, pausas: bool = True, corte: float = math.inf) -> float:
        """login + 6 operaciones con pausa triangular(10, 19, 25) (S-14) + 12 s de cierre (S-13).
        corte: gracefulStop de 0 s (demo): la sesión se interrumpe ahí y no emite iteration_duration."""
        inicio = t
        self.datos_en_op = False
        t, fallo = self.peticion("login", "login", t, self.etiquetas("login", t))
        self._fin_operacion(t, fallo, self.etiquetas("login", t))
        ops, pesos = zip(*MEZCLA.items(), strict=True)
        for _ in range(6):
            if pausas:
                t += self.rng.triangular(10, 25, 19)
            if t >= corte:
                return t
            op = self.rng.choices(ops, pesos)[0]
            etiquetas, algun_fallo, self.datos_en_op = self.etiquetas(op, t), False, False
            for ep in OPERACIONES[op]:
                t, fallo = self.peticion(ep, op, t, etiquetas)
                algun_fallo |= fallo
            self._fin_operacion(t, algun_fallo, etiquetas)
        t += 12 if pausas else 0
        self._fila("iteration_duration", t, (t - inicio) * 1000)
        self._fila("iterations", t, 1)
        return t


def llegadas(p, fin: float) -> np.ndarray:
    """Inicios de sesión de un ejecutor de llegada de k6: equiespaciados según la tasa (no Poisson)."""
    rejilla = np.arange(0, fin, 0.01)
    acumulado = np.cumsum(tasa_llegada(p, rejilla)) * 0.01
    return np.interp(np.arange(0, math.floor(acumulado[-1])), acumulado, rejilla)


def simular(escenario: str, t0: float, rng: random.Random) -> tuple[Simulador, pd.DataFrame]:
    s = Simulador(escenario, t0, rng)
    activos: list[float] = []      # montículo con el fin de las sesiones en curso: tope de maxVUs (dropped_iterations)
    # setup() de k6: chequeo de salud antes del escenario (el análisis debe ignorarlo)
    s._fila("http_req_duration", -1.5, 1.4, "grupo=soporte&ep=salud", method="GET", name="http://127.0.0.1:8090/api/salud",
            status="200", group="::setup", scenario="")
    if escenario in ("referencia", "calibracion"):
        s.k6 = "recorrido" if escenario == "referencia" else "calibracion"
        t = 0.0
        for _ in range(5 if escenario == "referencia" else 40):
            if escenario == "referencia":
                inicio = t
                t, _ = s.peticion("login", "login", t, "op=login&fase=unica")
                for op in MEZCLA:
                    t += 1
                    for ep in OPERACIONES[op]:
                        t, _ = s.peticion(ep, op, t, s.etiquetas(op, t))
                s._fila("iteration_duration", t, (t - inicio) * 1000)
            else:
                t = s.sesion(t, pausas=False) + 0.5
    else:
        tope = sum(d for d, _ in s.p.etapas)
        s.k6 = "demo_hora_punta" if escenario == "demo" else escenario
        for inicio in llegadas(s.p, tope):
            while activos and activos[0] <= inicio:
                heapq.heappop(activos)
            if len(activos) >= MAX_VUS[escenario]:
                s._fila("dropped_iterations", inicio, 1)
                continue
            heapq.heappush(activos, s.sesion(float(inicio), corte=100 if escenario == "demo" else math.inf))
        if escenario == "demo":
            s.k6 = "demo_sin_pausa"
            for vu in range(50):
                t = 100 + vu * 0.02
                while t < 145:
                    t = s.sesion(t, pausas=False)
    df = pd.DataFrame(s.filas, columns=["metric_name", "timestamp", "metric_value", "check", "error", "error_code",
                                        "expected_response", "group", "method", "name", "proto", "scenario", "service",
                                        "status", "subproto", "tls_version", "url", "extra_tags", "metadata"])
    return s, df


def recursos(s: Simulador, df: pd.DataFrame, carpeta: Path, rng: np.random.Generator, fin: float) -> None:
    it = df[df["metric_name"] == "iteration_duration"]
    fin_s = it["timestamp"].to_numpy() / 1000 - s.t0
    ses = pd.DataFrame({"inicio": fin_s - it["metric_value"].astype(float).to_numpy() / 1000, "fin": fin_s})
    t = np.arange(-3, fin + 3, 1.0)
    L = concurrencia(ses, t)
    acumuladas = np.searchsorted(np.sort(ses["inicio"].to_numpy()), t)
    i = np.clip(t.astype(int), 0, len(s.rho) - 1)
    rho = np.where(t >= 0, s.rho[i], 0.0)
    if s.esc == "demo":
        rho = np.where((t >= 100) & (t < 145), 1.0, rho)
    if s.esc in ("referencia", "calibracion"):
        rho = np.where((t >= 0) & (t <= fin), 0.06, 0.0)
    cpu_q = np.clip(100 * rho + rng.normal(0, 1.2, t.size), 0.3, 100)
    rss = 92 + 0.0035 * acumuladas + 0.02 * L + rng.normal(0, 0.4, t.size)
    hilos = 7 + np.minimum(34, np.round(rho * 30 + rng.uniform(0, 4, t.size)))
    fds = 24 + np.round(L * 0.08 + 0.0004 * acumuladas)
    hora = [datetime.fromtimestamp(s.t0 + x, LIMA).strftime("%H:%M:%S") for x in t]
    ts = np.round(s.t0 + t, 3)
    throttled = np.cumsum(rho > 0.95) * 10    # períodos de 100 ms con la cuota agotada (acumulado del cgroup)
    qolqe = pd.DataFrame({"hora": hora, "cpu_%": (cpu_q * rng.uniform(0.95, 1.1, t.size)).round(1), "memoria_MB": rss.round(1),
                          "ts": ts, "hilos": hilos.astype(int), "descriptores": fds.astype(int), "cpu_cgroup_%": cpu_q.round(1),
                          "nr_throttled": throttled, "throttled_usec": throttled * 20_000})
    if s.esc == "demo":   # prueba del respaldo: monitor dentro del contenedor, solo con hora en UTC
        qolqe["hora"] = [datetime.fromtimestamp(x, ZoneInfo("UTC")).strftime("%H:%M:%S") for x in ts]
        qolqe = qolqe.drop(columns=["ts"])
    qolqe.to_csv(carpeta / "recursos_qolqe.csv", index=False)
    mem_docker = rss + 380 + rng.normal(0, 2, t.size)
    pd.DataFrame({"hora": hora, "ts": ts, "cpu_%": np.clip(cpu_q + 1 + rng.normal(0, 0.5, t.size), 0, 100).round(2),
                  "memoria_MB": mem_docker.round(1), "memoria_%": (mem_docker / 1024 * 100).round(2),
                  "pids": (hilos + 1).astype(int)}).to_csv(carpeta / "recursos_docker.csv", index=False)
    cpu_k6 = np.clip(2 + 0.035 * L + rng.normal(0, 0.8, t.size), 0.1, None)
    cpu_k6_equipo = cpu_k6 / 10
    cpu_equipo = np.clip(9 + cpu_k6_equipo + cpu_q / 10 + rng.normal(0, 1.5, t.size), 0, 100)
    pd.DataFrame({"hora": hora, "cpu_%": cpu_k6.round(1), "memoria_MB": (70 + 0.6 * MAX_VUS.get(s.esc, 1) + 0.5 * L).round(1),
                  "ts": ts, "hilos": 14, "descriptores": (10 + L * 0.2).astype(int), "cpu_k6_equipo_%": cpu_k6_equipo.round(2),
                  "cpu_total_equipo_%": cpu_equipo.round(1)}).to_csv(carpeta / "recursos_k6.csv", index=False)


def escribir(escenario: str, raiz: Path, semilla: int) -> Path:
    rng = random.Random(semilla)
    hoy = datetime.now(LIMA).date()
    hh, mm = map(int, INICIOS[escenario].split(":"))
    inicio = datetime(hoy.year, hoy.month, hoy.day, hh, mm, tzinfo=LIMA)
    carpeta = raiz / escenario / inicio.strftime("%Y%m%d-%H%M")
    carpeta.mkdir(parents=True, exist_ok=True)
    t0 = inicio.timestamp() + 2.4            # k6 tarda unos segundos en inicializar los VUs
    s, df = simular(escenario, t0, rng)
    fin = float(df["timestamp"].max() / 1000 - t0)
    vus = pd.DataFrame({c: "" for c in df.columns}, index=range(int(fin)))
    vus["metric_name"], vus["timestamp"] = "vus", ((t0 + vus.index.to_numpy()) * 1000).astype(int)
    vus["metric_value"] = f"{min(MAX_VUS.get(escenario, 1), 150):.6f}"
    df = pd.concat([df, vus], ignore_index=True).sort_values("timestamp", kind="stable")
    df.to_csv(carpeta / "muestras.csv.gz", index=False, compression="gzip")
    recursos(s, df, carpeta, np.random.default_rng(semilla), fin)
    usos = 40 * 0.0689e6
    fin_epoch = t0 + fin + 1
    meta = {"escenario": escenario, "inicio": {"hora": inicio.isoformat(), "epoch": inicio.timestamp()},
            "fin": {"hora": datetime.fromtimestamp(fin_epoch, LIMA).isoformat(), "epoch": fin_epoch},
            "parametros": {"TOP": "2400", "CPUS": "1"}, "codigo_salida_k6": 99 if escenario in ("estres", "demo") else 0, "nucleos": 10,
            "carga_equipo_antes": 0.92, "base_identica": True, "cpu_max": "100000 100000", "memory_max": "1073741824",
            "cpu_stat_antes": {"usage_usec": 1_000_000, "nr_throttled": 0, "throttled_usec": 0},
            "cpu_stat_despues": {"usage_usec": 1_000_000 + (usos if escenario == "calibracion" else 5e8), "nr_throttled": 120,
                                 "throttled_usec": 3_400_000}, "sintetico": True}
    if escenario == "calibracion":   # lo agrega monitor/corrida.py fin (M-14)
        meta["calibracion"] = {"sesiones": 40, "d_sesion_s": 0.0689, "l_sat": 1742, "top": 2400}
    (carpeta / "corrida.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (carpeta / "consola.txt").write_text("datos sintéticos: no hay salida real de k6\n", encoding="utf-8")
    (carpeta / "verificacion_dinero.txt").write_text(
        "Verificación del dinero (SINTÉTICA)\nC1 Conservación del dinero     PASA   descuadre 0 cént.\n"
        "C2 Libro mayor por usuario     PASA   0 usuarios con descuadre\nC6 Conteos y conciliación      PASA\n\n"
        "TOTAL descuadres: 0\nResultado U-07: PASA\n", encoding="utf-8")
    umbrales = [{"descripcion": "U-01 p95 grupo consulta", "metrica": "http_req_duration{fase:estable,grupo:consulta}",
                 "condicion": "p(95)<800", "ok": True, "muestras": 100, "sin_muestras": False, "valor": "—"}]
    (carpeta / "resumen.json").write_text(json.dumps({"qolqe": {"escenario": escenario, "umbrales": umbrales, "top": "2400"},
                                                      "metrics": {"dropped_iterations": {"type": "counter", "values": {"count": 0}}}}),
                                          encoding="utf-8")
    return carpeta


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Genera corridas sintéticas para probar el análisis")
    parser.add_argument("salida", type=Path)
    parser.add_argument("--escenarios", nargs="+", default=["referencia", "calibracion", "carga", "pico", "estres", "resistencia", "demo"])
    parser.add_argument("--semilla", type=int, default=7)
    args = parser.parse_args(argv)
    resultados = (Path(__file__).resolve().parent.parent / "resultados").resolve()
    if args.salida.resolve() == resultados or resultados in args.salida.resolve().parents:
        sys.exit("No se escriben datos sintéticos en tests/performance/resultados/: use otra carpeta")
    for i, escenario in enumerate(args.escenarios):
        print(escribir(escenario, args.salida, args.semilla + i))
    return 0


if __name__ == "__main__":
    sys.exit(main())
