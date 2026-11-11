"""G1 a G5 (diseño §7.2): tiempo de respuesta, throughput, errores, usuarios simultáneos y recursos a lo largo de la prueba."""
import numpy as np
import pandas as pd
from config import (
    CPU_GENERADOR_MAX,
    ERROR_MAX,
    ERRORES_DATOS_MAX,
    RSS_MAX_MB,
    UMBRAL_CONSULTA_CAMPANA_MS,
    UMBRAL_CONSULTA_MS,
    UMBRAL_DINERO_CAMPANA_MS,
    UMBRAL_DINERO_MS,
)
from estilo import COLOR, MARCADOR, MILES, NOMBRE_ESCENARIO, SERIE_DATOS, TINTA, TINTA_2, TINTA_3, figura, guardar, leyenda, linea_umbral, sombrear_fases
from matplotlib.ticker import FuncFormatter
from perfiles import intervalo_fase, rango_concurrencia


def _titulo(a, texto: str) -> str:
    c = a.corrida
    return f"{NOMBRE_ESCENARIO.get(c.escenario, c.escenario)} · {texto}"


def _eje_tiempo(ax, a) -> None:
    ax.set_xlabel("Minuto de la prueba")
    ax.set_xlim(0, a.corrida.duracion / 60)


def _ventana(a) -> str:
    ancho = a.ventanas["ancho"].median()
    return f"{ancho / 60:.0f} min" if ancho >= 60 else f"{ancho:.0f} s"


def g1_tiempo_respuesta(a, ruta) -> None:
    v, c = a.ventanas, a.corrida
    fig, ejes = figura(2, _titulo(a, f"Tiempo de respuesta por ventana de {_ventana(a)} (p95 y p50)"))
    pico = c.escenario == "pico"
    for ax, grupo, critico, umbral, campana, uid in ((ejes[0], "consulta", "login", UMBRAL_CONSULTA_MS, UMBRAL_CONSULTA_CAMPANA_MS, "U-01"),
                                                     (ejes[1], "dinero", "transferir", UMBRAL_DINERO_MS, UMBRAL_DINERO_CAMPANA_MS, "U-02")):
        sombrear_fases(ax, c.perfil.fases, c.duracion / 60, rotulos=ax is ejes[0])
        if f"p95_{grupo}" in v and v[f"p95_{grupo}"].notna().any():
            ax.plot(v["minuto"], v[f"p95_{grupo}"], color=COLOR[grupo], marker=MARCADOR[grupo], label=f"p95 grupo {grupo}")
            ax.plot(v["minuto"], v[f"p50_{grupo}"], color=COLOR[grupo], ls=":", lw=1.6, label=f"p50 grupo {grupo}")
        if f"p95_{critico}" in v and v[f"p95_{critico}"].notna().any():
            ax.plot(v["minuto"], v[f"p95_{critico}"], color=COLOR[critico], marker=MARCADOR[critico], lw=1.6, ms=6, label=f"p95 {critico}")
        linea_umbral(ax, umbral, f"{uid}\n{umbral:,} ms")
        if pico:
            linea_umbral(ax, campana, f"U-06\n{campana:,} ms", estilo=":")
        maximo = np.nanmax(v[[col for col in (f"p95_{grupo}", f"p95_{critico}") if col in v]].to_numpy(dtype=float), initial=0)
        if maximo > 5 * umbral:   # estrés: la escala lineal aplastaría la zona del umbral
            ax.set_yscale("log")
            ax.set_ylabel("ms (escala log)")
        else:
            ax.set_ylim(0, max(maximo, (campana if pico else umbral)) * 1.08)
            ax.set_ylabel("ms")
        ax.yaxis.set_major_formatter(MILES)
        ax.set_title(f"{'Consultas e inicio de sesión' if grupo == 'consulta' else 'Operaciones de dinero'}", pad=22 if ax is ejes[0] else 6)
        leyenda(ax, ncol=3)
    _eje_tiempo(ejes[1], a)
    guardar(fig, ruta)


def g2_throughput(a, ruta) -> None:
    v, c = a.ventanas, a.corrida
    fig, ejes = figura(2, _titulo(a, "Throughput atendido frente a la carga ofrecida"))
    ax = ejes[0]
    sombrear_fases(ax, c.perfil.fases, c.duracion / 60)
    ax.plot(v["minuto"], v["req_s"], color=COLOR["qolqe"], marker="o", label="atendidas (sin errores de rendimiento)")
    if v["req_s_ofrecidas"].notna().any():
        ax.plot(v["minuto"], v["req_s_ofrecidas"], color=TINTA, ls="--", lw=1.8, label="ofrecidas por el modelo (λ × 11.74, M-08)")
    ax.set_ylabel("peticiones/s")
    ax.set_title("Peticiones por segundo", pad=22)
    ax = ejes[1]
    sombrear_fases(ax, c.perfil.fases, c.duracion / 60, rotulos=False)
    if v["llegada_min"].notna().any():
        ax.plot(v["minuto"], v["llegada_min"], color=TINTA, ls="--", lw=1.8, label="llegada programada (M-01)")
    ax.plot(v["minuto"], v["sesiones_iniciadas_min"], color=COLOR["consulta"], marker="o", label="sesiones iniciadas")
    if "sesiones_completadas_min" in v:
        ax.plot(v["minuto"], v["sesiones_completadas_min"], color=COLOR["dinero"], marker="s", lw=1.6, label="sesiones completadas")
    ax.set_ylabel("sesiones/min")
    ax.set_title("Sesiones por minuto")
    for eje in ejes:
        eje.set_ylim(bottom=0)
        leyenda(eje, ncol=2 if eje is ejes[0] else 3)
    _eje_tiempo(ejes[1], a)
    guardar(fig, ruta)


def g3_errores(a, ruta) -> None:
    """Errores de rendimiento (por tipo) y de datos (por código), separados como pide el enunciado §5."""
    v, c = a.ventanas, a.corrida
    fig, ejes = figura(2, _titulo(a, f"Errores por ventana de {_ventana(a)}: rendimiento y datos por separado"))
    ancho = v["ancho"].median() / 60 * 0.85
    ax = ejes[0]
    sombrear_fases(ax, c.perfil.fases, c.duracion / 60)
    base = np.zeros(len(v))
    for columna in [col for col in v.columns if col.startswith("err_req::")]:
        tipo = columna.split("::", 1)[1]
        valores = v[columna].fillna(0).to_numpy() * 100
        ax.bar(v["minuto"], valores, width=ancho, bottom=base, color=COLOR.get(tipo, TINTA_3), label=f"{tipo} (% de peticiones)",
               edgecolor="white", linewidth=1)
        base += valores
    ax.plot(v["minuto"], v["error_ops"] * 100, color=TINTA, marker="o", lw=1.8, label="operaciones fallidas (% de operaciones)")
    linea_umbral(ax, ERROR_MAX * 100, "U-03\n1 %")
    maximo = max(1.5, np.nanmax(np.r_[base, v["error_ops"].to_numpy(dtype=float) * 100]) * 1.1)
    if maximo > 10:   # con muchos errores (estrés), escala lineal hasta 1 % y logarítmica arriba: la línea de U-03 se sigue viendo
        ax.set_yscale("symlog", linthresh=1, linscale=0.6)
        ax.set_ylim(0, max(100, maximo))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:g}"))
        ax.set_ylabel("% (log sobre 1 %)")
    else:
        ax.set_ylim(0, maximo)
        ax.set_ylabel("%")
    ax.set_title("Errores de rendimiento (5xx, timeouts, conexión, cuerpo inválido): cuentan en U-03", pad=22)
    leyenda(ax, ticks_hasta=100)
    ax = ejes[1]
    sombrear_fases(ax, c.perfil.fases, c.duracion / 60, rotulos=False)
    largo = a.errores_datos
    base = np.zeros(len(v))
    if len(largo):
        ops = v["ops_n"].replace(0, np.nan)
        for i, (codigo, filas) in enumerate(largo.groupby("codigo")):
            serie = filas.set_index("w")["n"].reindex(v.index).fillna(0) / ops * 100
            valores = serie.fillna(0).to_numpy()
            ax.bar(v["minuto"], valores, width=ancho, bottom=base, color=SERIE_DATOS[i % len(SERIE_DATOS)], label=codigo,
                   edgecolor="white", linewidth=1)
            base += valores
    else:
        ax.text(0.5, 0.5, "Sin errores de datos en la corrida", transform=ax.transAxes, ha="center", va="center", color=TINTA_2)
    linea_umbral(ax, ERRORES_DATOS_MAX * 100, "V-02\n0.1 %", estilo=":")
    ax.set_ylim(0, max(0.3, base.max(initial=0) * 1.1))
    leyenda(ax, ncol=3)
    ax.set_ylabel("% de operaciones")
    ax.set_title("Errores de datos (4xx de regla de negocio): no cuentan en U-03 (V-02)")
    _eje_tiempo(ejes[1], a)
    guardar(fig, ruta)


def g4_usuarios(a, ruta) -> None:
    v, c = a.ventanas, a.corrida
    fig, ejes = figura(1, _titulo(a, "Usuarios simultáneos medidos frente a la Ley de Little"), alto=6.5)
    ax = ejes[0]
    sombrear_fases(ax, c.perfil.fases, c.duracion / 60)
    tramo = intervalo_fase(c.perfil, ("estable",))
    if tramo:
        rango = rango_concurrencia(c.perfil)
        ax.fill_between([tramo[0] / 60, tramo[1] / 60], *rango, color=COLOR["consulta"], alpha=0.12, lw=0,
                        label=f"U-05(c): {rango[0]:,.0f}–{rango[1]:,.0f}")
    if v["L_esperada"].notna().any():
        ax.plot(v["minuto"], v["L_esperada"], color=TINTA, ls="--", lw=1.8, label="esperados: L = λ·W (M-03)")
    ax.plot(v["minuto"], v["L_medida"], color=COLOR["qolqe"], marker="o", label="medidos (logins − sesiones terminadas)")
    if "vus_k6" in v and v["vus_k6"].notna().any():
        ax.plot(v["minuto"], v["vus_k6"], color=TINTA_3, lw=1.2, ls="-.", label="VUs activos según k6")
    ax.set_ylabel("sesiones simultáneas")
    ax.set_ylim(bottom=0)
    ax.yaxis.set_major_formatter(MILES)
    leyenda(ax, ncol=2)
    _eje_tiempo(ax, a)
    guardar(fig, ruta)


def _suave(df: pd.DataFrame, columna: str, segundos: int = 10) -> pd.Series:
    return df[columna].rolling(segundos, min_periods=1, center=True).mean()


def g5_recursos(a, ruta) -> None:
    """CPU y memoria de Qolqe y del generador en el mismo eje de tiempo, con la línea del 80 % (V-01)."""
    c = a.corrida
    q, d, k = (c.recursos.get(n) for n in ("qolqe", "docker", "k6"))
    throttling = "nr_throttled" in a.ventanas and a.ventanas["nr_throttled"].notna().any()   # monitor psutil --cgroup
    fig, ejes = figura(4 if throttling else 3, _titulo(a, "Recursos de Qolqe y del generador (promedio móvil de 10 s)"), alto=11 if throttling else 9.5)
    ax = ejes[0]
    sombrear_fases(ax, c.perfil.fases, c.duracion / 60)
    for df, columna, color, texto, estilo in ((q, "cpu_cgroup", COLOR["qolqe"], "Qolqe, cgroup (100 % = su 1 CPU)", "-"),
                                              (q, "cpu", COLOR["qolqe"], "Qolqe, proceso (psutil)", ":"),
                                              (d, "cpu", COLOR["docker"], "Qolqe, contenedor (docker stats)", "--"),
                                              (k, "cpu_k6_equipo", COLOR["k6"], "k6 (% de los núcleos del equipo)", "-"),
                                              (k, "cpu_equipo", COLOR["equipo"], "equipo completo (%)", "-")):
        if df is not None and columna in df and df[columna].notna().any():
            ax.plot(df["t"] / 60, _suave(df, columna), color=color, ls=estilo, lw=1.8, label=texto)
    linea_umbral(ax, CPU_GENERADOR_MAX, "V-01\n80 %", color="#d03b3b")
    ax.set_ylim(0, 105)
    ax.set_ylabel("CPU (%)")
    ax.set_title("CPU", pad=22)
    leyenda(ax, ncol=3, ticks_hasta=100)
    ax = ejes[1]
    sombrear_fases(ax, c.perfil.fases, c.duracion / 60, rotulos=False)
    for df, color, texto, estilo in ((q, COLOR["qolqe"], "Qolqe, RSS del proceso (psutil)", "-"),
                                     (d, COLOR["docker"], "Qolqe, contenedor (incluye caché de la BD)", "--")):
        if df is not None and "mem_mb" in df and df["mem_mb"].notna().any():
            ax.plot(df["t"] / 60, _suave(df, "mem_mb"), color=color, ls=estilo, lw=1.8, label=texto)
    linea_umbral(ax, RSS_MAX_MB, "70 %\n700 MB", estilo=":")
    linea_umbral(ax, 1024, "límite\n1 GB", color=TINTA_3)
    ax.set_ylim(0, 1100)
    ax.set_ylabel("MB")
    ax.set_title("Memoria de Qolqe (contenedor de 1 GB)")
    leyenda(ax, ncol=2, ticks_hasta=1000)
    ax = ejes[2]
    sombrear_fases(ax, c.perfil.fases, c.duracion / 60, rotulos=False)
    if k is not None and "mem_mb" in k:
        ax.plot(k["t"] / 60, _suave(k, "mem_mb"), color=COLOR["k6"], lw=1.8, label="k6, RSS")
        ax.set_ylim(0, k["mem_mb"].max() * 1.2)
    ax.set_ylabel("MB")
    ax.yaxis.set_major_formatter(MILES)
    ax.set_title("Memoria del generador (k6)")
    if throttling:
        ax = ejes[3]
        sombrear_fases(ax, c.perfil.fases, c.duracion / 60, rotulos=False)
        v = a.ventanas
        ax.bar(v["minuto"], v["nr_throttled"].fillna(0), width=v["ancho"].median() / 60 * 0.85, color=COLOR["qolqe"], edgecolor="white")
        ax.set_ylim(0, max(1.0, float(v["nr_throttled"].max()) * 1.1))   # sin throttling, el eje no muestra negativos
        ax.set_ylabel("períodos")
        ax.set_title("Throttling del cgroup (nr_throttled por ventana): la cuota de 1 CPU se agotó")
    _eje_tiempo(ejes[-1], a)
    guardar(fig, ruta)
