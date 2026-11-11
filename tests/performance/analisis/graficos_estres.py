"""G6 a G8 (estrés): p95, throughput y CPU contra las sesiones simultáneas medidas, con la marca de capacidad (U-08)."""
import json
import math

import numpy as np
from config import EP_CRITICOS, UMBRAL_CONSULTA_MS, UMBRAL_DINERO_MS
from estilo import COLOR, CRITICO, MARCADOR, MILES, TINTA, TINTA_2, figura, guardar, linea_umbral
from veredicto import d_sesion

FASES = ("base", "rampa", "meseta")


def _marcar_capacidad(ax, cap: dict, rotulo: bool = True) -> None:
    """Línea vertical en la capacidad y zona roja desde la primera falla sostenida."""
    if not math.isnan(cap.get("capacidad", math.nan)):
        ax.axvline(cap["capacidad"], color=CRITICO, lw=2, zorder=4)
        if rotulo:
            ax.annotate(f"capacidad U-08\n≈ {cap['capacidad']:,.0f} usuarios", xy=(cap["capacidad"], 0.02), xycoords=("data", "axes fraction"),
                        xytext=(-8, 0), textcoords="offset points", ha="right", va="bottom", fontsize=13, color=CRITICO, fontweight="bold")
    if cap.get("limite_alcanzado"):
        ax.axvspan(cap["L_falla"], ax.get_xlim()[1] if ax.get_xlim()[1] > cap["L_falla"] else cap["L_max"] * 1.05,
                   color=CRITICO, alpha=0.06, lw=0, zorder=0)


def _ventanas(a):
    return a.ventanas[a.ventanas["fase"].isin(FASES)].sort_values("ini")


def g6_p95_vs_usuarios(a, ruta) -> None:
    v, cap = _ventanas(a), a.evaluacion["extra"]["capacidad"]
    fig, ejes = figura(1, f"Estrés · p95 por ventana de {a.corrida.perfil.ventana_s:g} s contra usuarios simultáneos", alto=7.5, columnas=2)
    for ax, grupo, umbral, uid in ((ejes[0], "consulta", UMBRAL_CONSULTA_MS, "U-01"), (ejes[1], "dinero", UMBRAL_DINERO_MS, "U-02")):
        for serie in [grupo, *EP_CRITICOS[grupo]]:
            if f"p95_{serie}" in v and v[f"p95_{serie}"].notna().any():
                ax.plot(v["L_medida"], v[f"p95_{serie}"], color=COLOR[serie], marker=MARCADOR[serie], lw=2.4 if serie == grupo else 1.4,
                        ms=6, label=f"grupo {serie}" if serie == grupo else serie)
        ax.set_yscale("log")
        ax.set_xlim(0, v["L_medida"].max() * 1.05)
        linea_umbral(ax, umbral, f"{uid}\n{umbral:,} ms")
        _marcar_capacidad(ax, cap, rotulo=ax is ejes[0])
        ax.set_xlabel("usuarios simultáneos (medidos)")
        ax.set_ylabel("p95 (ms, escala log)")
        ax.xaxis.set_major_formatter(MILES)
        ax.yaxis.set_major_formatter(MILES)
        ax.set_title("Consultas e inicio de sesión" if grupo == "consulta" else "Operaciones de dinero")
        ax.legend(loc="upper left")
    guardar(fig, ruta)


def g7_throughput_vs_usuarios(a, ruta) -> None:
    v, cap = _ventanas(a), a.evaluacion["extra"]["capacidad"]
    fig, ejes = figura(1, "Estrés · throughput contra usuarios simultáneos (rodilla de saturación)", alto=7)
    ax = ejes[0]
    # La carga ofrecida se dibuja contra los simultáneos que predice Little (L = λ·W): es la recta "si Qolqe diera abasto".
    # Contra los medidos haría un rulo, porque al colapsar los medidos dejan de crecer en orden.
    ax.plot(v["L_esperada"], v["req_s_ofrecidas"], color=TINTA, ls="--", lw=1.8, label="ofrecidas por el modelo (M-08), contra L = λ·W")
    ax.plot(v["L_medida"], v["req_s"], color=COLOR["qolqe"], marker="o", label="atendidas (sin errores de rendimiento)")
    ax.set_xlim(0, max(v["L_medida"].max(), v["L_esperada"].max()) * 1.05)
    ax.set_ylim(bottom=0)
    _marcar_capacidad(ax, cap)
    ax.set_xlabel("usuarios simultáneos (medidos)")
    ax.set_ylabel("peticiones/s")
    ax.xaxis.set_major_formatter(MILES)
    ax.legend(loc="upper left")
    guardar(fig, ruta)


def d_para_estres(a) -> tuple[float, str]:
    """D_sesión para la Ley de utilización: corrida.json → última calibración → estimado con las ventanas con CPU < 70 %."""
    d = d_sesion(a.corrida)
    if not math.isnan(d):
        return d, "corrida.json"
    for carpeta in sorted((a.corrida.carpeta.parent.parent / "calibracion").glob("*"), reverse=True):
        propio = json.loads((carpeta / "calibracion.json").read_text()) if (carpeta / "calibracion.json").exists() else {}
        de_correr = (json.loads((carpeta / "corrida.json").read_text()) if (carpeta / "corrida.json").exists() else {}).get("calibracion", {})
        d = propio.get("D_sesion_s") or de_correr.get("d_sesion_s")
        if d:
            return float(d), f"calibración {carpeta.name}"
    v = _ventanas(a)
    if "cpu_qolqe" not in v or "sesiones_completadas_min" not in v:
        return math.nan, ""
    w = v[(v["cpu_qolqe"] < 70) & v["sesiones_completadas_min"].notna()]
    x, y = w["sesiones_completadas_min"].to_numpy() / 60, w["cpu_qolqe"].to_numpy() / 100
    return (float((x * y).sum() / (x * x).sum()), "estimado con las ventanas de CPU < 70 %") if len(w) >= 3 else (math.nan, "")


def g8_cpu_vs_usuarios(a, ruta) -> None:
    v, cap = _ventanas(a), a.evaluacion["extra"]["capacidad"]
    if "cpu_qolqe" not in v:
        return
    fig, ejes = figura(1, "Estrés · CPU de Qolqe contra usuarios simultáneos y Ley de utilización (U = X·D)", alto=7)
    ax = ejes[0]
    ax.plot(v["L_medida"], v["cpu_qolqe"], color=COLOR["qolqe"], marker="o", ls="none", label="CPU medido (promedio de la ventana)")
    d, fuente = d_para_estres(a)
    if not math.isnan(d):
        usuarios = np.linspace(0, v["L_medida"].max() * 1.05, 200)
        w_s = a.corrida.perfil.duracion_sesion_s   # W = 120 s (M-02; comprimido en un ensayo)
        ax.plot(usuarios, np.minimum(100, 100 * d * usuarios / w_s), color=TINTA, ls="--", lw=1.8,
                label=f"U = X·D con X = L/W y D = {d * 1000:.0f} ms ({fuente})")
        l_sat = w_s / d
        ax.axvline(l_sat, color=TINTA_2, ls=":", lw=1.6)
        ax.annotate(f"L_sat = W/D ≈ {l_sat:,.0f}", xy=(l_sat, 0.04), xycoords=("data", "axes fraction"), xytext=(6, 0),
                    textcoords="offset points", fontsize=12, color=TINTA_2)
    ax.set_xlim(0, v["L_medida"].max() * 1.05)
    ax.set_ylim(0, 110)
    _marcar_capacidad(ax, cap)
    ax.set_xlabel("usuarios simultáneos (medidos)")
    ax.set_ylabel("CPU de Qolqe (% de 1 CPU)")
    ax.xaxis.set_major_formatter(MILES)
    ax.legend(loc="lower right")   # arriba a la izquierda taparía la recta U = X·D
    guardar(fig, ruta)
