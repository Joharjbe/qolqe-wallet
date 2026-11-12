"""Estilo común de los gráficos: letra grande para diapositivas, colores fijos por entidad y ayudas de dibujo.

Colores: paleta categórica validada para daltonismo (orden fijo, nunca se recicla). Cada entidad tiene siempre el mismo
color en todos los gráficos (consulta = azul, dinero = naranja, Qolqe = azul, k6 = naranja, …).
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

TINTA, TINTA_2, TINTA_3 = "#0b0b0b", "#52514e", "#8a8984"
FONDO, SOMBRA, REJILLA = "#ffffff", "#f0efec", "#e4e3df"
CRITICO = "#d03b3b"
COLOR = {
    # grupos y endpoints críticos
    "consulta": "#2a78d6", "dinero": "#eb6834", "login": "#1baf7a", "transferir": "#6250d6",
    "movimientos": "#e87ba4", "recargar": "#008300", "pagar": "#eda100", "saldo": "#e34948", "todas": TINTA_2,
    # recursos
    "qolqe": "#2a78d6", "docker": "#86b6ef", "k6": "#eb6834", "equipo": TINTA_2,
    # escenarios (comparativo)
    "carga": "#2a78d6", "pico": "#eb6834", "resistencia": "#1baf7a", "estres": "#eda100", "demo": "#e87ba4",
    "capacidad": "#6250d6",
    # tipos de error de rendimiento
    "5xx (p. ej. database is locked)": "#e34948", "timeout de 30 s": "#6250d6", "conexión rechazada o cortada": "#e87ba4",
    "2xx con cuerpo inválido": "#eda100", "401 a mitad de sesión": "#008300",
    "operación fallida": TINTA,
}
SERIE_DATOS = ["#eda100", "#1baf7a", "#2a78d6", "#008300", "#e87ba4", "#6250d6", "#eb6834", "#e34948"]
MARCADOR = {"consulta": "o", "dinero": "s", "login": "^", "transferir": "D", "movimientos": "v", "recargar": "P",
            "pagar": "X", "saldo": "<"}
NOMBRE_ESCENARIO = {"carga": "Carga", "pico": "Pico", "estres": "Estrés", "resistencia": "Resistencia",
                    "demo": "Demo", "referencia": "Referencia (1 VU)", "calibracion": "Calibración",
                    "capacidad": "Capacidad (confirmación)"}

plt.rcParams.update({
    "figure.figsize": (13.33, 7.5), "figure.dpi": 100, "savefig.dpi": 150, "figure.facecolor": FONDO,
    "axes.facecolor": FONDO, "axes.edgecolor": TINTA_3, "axes.linewidth": 0.8, "axes.grid": True,
    "grid.color": REJILLA, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False,
    "font.size": 15, "axes.titlesize": 17, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "axes.labelsize": 15, "axes.labelcolor": TINTA_2, "xtick.labelsize": 13, "ytick.labelsize": 13,
    "xtick.color": TINTA_2, "ytick.color": TINTA_2, "legend.fontsize": 13, "legend.frameon": False,
    "lines.linewidth": 2.2, "lines.markersize": 7, "figure.titlesize": 20, "figure.titleweight": "bold",
    "text.color": TINTA, "axes.formatter.use_locale": False,
})
MILES = FuncFormatter(lambda x, _: f"{x:,.0f}")


AVISO = {"texto": ""}   # graficos.py lo llena en un ensayo comprimido (ESCALA < 1): se agrega a cada título


def figura(filas: int = 1, titulo: str = "", alto: float | None = None, columnas: int = 1):
    """Figura de 16:9 (13.33 × 7.5 in, 2000 px a 150 dpi) con ejes que comparten el tiempo si van apilados."""
    fig, ejes = plt.subplots(filas, columnas, figsize=(13.33, alto or (7.5 if filas < 3 else 9.5)), sharex=columnas == 1,
                             squeeze=False)
    if titulo:
        fig.suptitle(titulo, x=0.01, y=0.985, ha="left")
    if AVISO["texto"]:   # debajo del título, a la derecha: no lo alarga ni lo corta
        fig.text(0.99, 0.935, AVISO["texto"], ha="right", va="top", fontsize=13, color=CRITICO, fontweight="bold")
    return fig, list(ejes.flat)


def sombrear_fases(ax, fases, duracion_min: float, rotulos: bool = True) -> None:
    """Fases del escenario sombreadas una sí y otra no, con su nombre arriba."""
    for i, (nombre, ini, fin) in enumerate(fases):
        fin = duracion_min * 60 if fin is None else fin
        if ini / 60 >= duracion_min:
            continue
        if i % 2 == 1:
            ax.axvspan(ini / 60, min(fin / 60, duracion_min), color=SOMBRA, zorder=0, lw=0)
        if rotulos:
            ax.text((ini + min(fin, duracion_min * 60)) / 120, 1.0, nombre, transform=ax.get_xaxis_transform(),
                    ha="center", va="bottom", fontsize=12, color=TINTA_3)


def linea_umbral(ax, valor: float, texto: str, estilo: str = "--", color: str = TINTA) -> None:
    """Umbral horizontal con su rótulo a la derecha (texto en tinta, no en el color de la serie)."""
    ax.axhline(valor, color=color, ls=estilo, lw=1.6, zorder=3)
    ax.annotate(texto, xy=(1, valor), xycoords=("axes fraction", "data"), xytext=(4, 0), textcoords="offset points",
                va="center", ha="left", fontsize=12, color=color)


def leyenda(ax, ncol: int = 1, ticks_hasta: float | None = None) -> None:
    """Leyenda arriba a la izquierda sin tapar datos ni umbrales: sube el tope del eje lo que ocupa la leyenda."""
    n = len(ax.get_legend_handles_labels()[0])
    if n == 0:
        return
    filas = -(-n // ncol)
    abajo, arriba = ax.get_ylim()
    if ax.get_yscale() == "log":
        ax.set_ylim(abajo, arriba * (arriba / abajo) ** (0.13 * filas))
    else:
        ax.set_ylim(abajo, arriba + (arriba - abajo) * 0.18 * filas)
    if ticks_hasta is not None:   # que el eje no muestre marcas imposibles (p. ej. CPU de 120 %)
        ax.set_yticks([t for t in ax.get_yticks() if abajo <= t <= ticks_hasta])
    ax.legend(loc="upper left", ncol=ncol)


def guardar(fig, ruta, rect: tuple | None = None) -> None:
    """Deja margen a la derecha para los rótulos de umbral y arriba para el título."""
    fig.tight_layout(rect=rect or (0, 0, 0.93, 0.96 if fig._suptitle else 1))
    fig.savefig(ruta, facecolor=FONDO)
    plt.close(fig)
