"""G9 y G10 (resistencia): memoria contra sesiones acumuladas con proyección a 54,000 (U-09b), e hilos y descriptores (U-09c)."""
import numpy as np
from config import FACTOR_HILOS, RSS_MAX_MB, SESIONES_DIA
from estilo import COLOR, CRITICO, MILES, TINTA, TINTA_2, figura, guardar, leyenda, linea_umbral, sombrear_fases


def g9_memoria_vs_sesiones(a, ruta) -> None:
    pr = a.evaluacion["extra"].get("proyecciones", {})
    m = pr.get("memoria")
    if not m:
        return
    fig, ejes = figura(1, f"Resistencia · memoria contra sesiones acumuladas y proyección a {SESIONES_DIA:,} (U-09b)", alto=7)
    ax = ejes[0]
    paso = max(1, len(m["x"]) // 600)   # ~600 puntos bastan para ver la tendencia
    ax.plot(m["x"][::paso], m["y"][::paso], color=COLOR["qolqe"], marker="o", ls="none", ms=4, alpha=0.6,
            label=f"medido: {pr.get('fuente_memoria', '')}")
    x = np.array([0, SESIONES_DIA])
    ax.plot(x, m["pendiente"] * x + m["intercepto"], color=TINTA, ls="--", lw=1.8,
            label=f"regresión: {m['pendiente'] * 1000:.2f} MB por 1,000 sesiones (r² {m['r2']:.2f})")
    ax.axvspan(0, m["sesiones_medidas"], color=COLOR["qolqe"], alpha=0.08, lw=0)
    ax.annotate(f"medido: {m['sesiones_medidas']:,} sesiones", xy=(m["sesiones_medidas"], 0.03), xycoords=("data", "axes fraction"),
                xytext=(6, 0), textcoords="offset points", color=TINTA_2, fontsize=12)
    color = CRITICO if m["proyeccion"] >= RSS_MAX_MB else TINTA
    ax.plot([SESIONES_DIA], [m["proyeccion"]], marker="D", ms=10, color=color, ls="none")
    ax.annotate(f"proyección a {SESIONES_DIA:,}:\n{m['proyeccion']:,.0f} MB", xy=(SESIONES_DIA, m["proyeccion"]), xytext=(-12, 14),
                textcoords="offset points", ha="right", fontsize=13, color=color, fontweight="bold")
    linea_umbral(ax, RSS_MAX_MB, "U-09(b)\n700 MB")
    ax.set_xlim(0, SESIONES_DIA * 1.03)
    ax.set_ylim(0, max(RSS_MAX_MB, m["proyeccion"], np.nanmax(m["y"])) * 1.15)
    ax.set_xlabel("sesiones acumuladas (un día de 6:00 a 24:00 = 18 × 3,000, S-11)")
    ax.set_ylabel("MB")
    ax.xaxis.set_major_formatter(MILES)
    ax.legend(loc="upper left")
    guardar(fig, ruta)


def g10_hilos_descriptores(a, ruta) -> None:
    c, pr = a.corrida, a.evaluacion["extra"].get("proyecciones", {})
    q = c.recursos.get("qolqe")
    columnas = [(col, nombre) for col, nombre in (("hilos", "hilos"), ("descriptores", "descriptores")) if q is not None and col in q]
    if not columnas:
        return
    fig, ejes = figura(len(columnas), "Resistencia · hilos y descriptores de archivo de Qolqe (U-09c)")
    for ax, (columna, nombre) in zip(ejes, columnas, strict=True):
        sombrear_fases(ax, c.perfil.fases, c.duracion / 60, rotulos=ax is ejes[0])
        ax.plot(q["t"] / 60, q[columna], color=COLOR["qolqe"], lw=1.2, alpha=0.5, label="cada 1 s")
        ax.plot(q["t"] / 60, q[columna].rolling(60, min_periods=1, center=True).mean(), color=COLOR["qolqe"], lw=2.4, label="promedio de 1 min")
        if nombre in pr:
            limite = FACTOR_HILOS * pr[nombre]["inicial"]
            linea_umbral(ax, limite, f"2 × inicial\n{limite:,.0f}", estilo=":")
            ax.set_ylim(0, max(limite, q[columna].max()) * 1.15)
        ax.set_ylabel(nombre)
        ax.set_title("Hilos del proceso (el pool de AnyIO tiene 40, H3)" if columna == "hilos" else "Descriptores de archivo abiertos",
                     pad=22 if ax is ejes[0] else 6)
        leyenda(ax, ncol=2)
    ejes[-1].set_xlabel("Minuto de la prueba")
    ejes[-1].set_xlim(0, c.duracion / 60)
    guardar(fig, ruta)
