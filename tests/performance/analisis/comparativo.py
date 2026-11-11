"""G11 y tablas comparativas entre escenarios (diseño §7.3: resultados/comparativo/)."""
import math
from pathlib import Path

import numpy as np
import pandas as pd
from config import EP_CRITICOS, ERROR_MAX, PERCENTIL, UMBRAL_CONSULTA_CAMPANA_MS, UMBRAL_CONSULTA_MS, UMBRAL_DINERO_CAMPANA_MS, UMBRAL_DINERO_MS
from estilo import COLOR, MILES, NOMBRE_ESCENARIO, figura, guardar, linea_umbral
from informe import MARCA, _md
from metricas import fmt, percentil
from veredicto import REQUISITO, VALIDEZ

ENCABEZADOS = {"escenario": "Escenario", "marca": "Corrida", "subconjunto": "Medido en", "peticiones": "Peticiones",
               "p95_consulta_ms": "p95 consulta (ms)", "p95_dinero_ms": "p95 dinero (ms)", "error_rendimiento_%": "Error rend. (%)",
               "error_datos_%": "Error datos (%)", "throughput_max_req_s": "Throughput máx. (req/s)",
               "usuarios_simultaneos_max": "Simultáneos máx.", "cpu_qolqe_max_%": "CPU Qolqe máx. (%)",
               "rss_qolqe_max_MB": "RSS máx. (MB)", "cpu_equipo_max_%": "CPU equipo máx. (%)", "capacidad_U08": "Capacidad U-08"}
ORDEN = ["referencia", "calibracion", "carga", "pico", "estres", "resistencia", "capacidad", "demo"]
EN_G11 = ["carga", "pico", "resistencia", "estres", "capacidad", "demo"]


def peticiones_medidas(a) -> tuple[pd.DataFrame, str, tuple[float, float]]:
    """Peticiones que representan al escenario en el comparativo, su rótulo y los umbrales que le aplican."""
    c = a.corrida
    normal = (UMBRAL_CONSULTA_MS, UMBRAL_DINERO_MS)
    if c.escenario == "pico":
        return c.pet[c.pet["campana"] == "si"], "pico (campaña)", (UMBRAL_CONSULTA_CAMPANA_MS, UMBRAL_DINERO_CAMPANA_MS)
    if c.escenario == "estres":
        cap = a.evaluacion["extra"]["capacidad"]
        # hasta el final de la última ventana que cumple ("minuto" es su centro: + media ventana)
        hasta = cap["minuto_ultima_ok"] * 60 + c.perfil.ventana_s / 2 if not math.isnan(cap["minuto_ultima_ok"]) else 0
        return c.pet[c.pet["fase"].isin(("base", "rampa")) & (c.pet["t"] <= hasta)], "estrés (hasta la capacidad)", normal
    if c.escenario == "demo":
        return c.pet[c.pet["scenario"] == "demo_hora_punta"], "demo (hora punta)", normal
    return c.pet[c.pet["fase"] == "estable"], NOMBRE_ESCENARIO[c.escenario].lower() + " (estable)", normal


def g11(analisis: dict, ruta: Path) -> None:
    escenarios = [e for e in EN_G11 if e in analisis]
    if not escenarios:
        return
    fig, ejes = figura(1, "Comparativo · p95 por endpoint crítico en cada escenario contra su umbral", alto=7.5, columnas=2)
    ancho = 0.8 / len(escenarios)
    for ax, grupo in zip(ejes, ("consulta", "dinero"), strict=True):
        entidades = [grupo, *EP_CRITICOS[grupo]]
        x = np.arange(len(entidades))
        for i, esc in enumerate(escenarios):
            pet, rotulo, _ = peticiones_medidas(analisis[esc])
            valores = [percentil(pet.loc[(pet["grupo"] == e) if e == grupo else (pet["ep"] == e), "dur"], PERCENTIL) for e in entidades]
            pos = x - 0.4 + ancho * (i + 0.5)
            ax.bar(pos, valores, width=ancho * 0.92, color=COLOR[esc], label=rotulo, edgecolor="white", linewidth=1)
        normal, campana = (UMBRAL_CONSULTA_MS, UMBRAL_CONSULTA_CAMPANA_MS) if grupo == "consulta" else (UMBRAL_DINERO_MS, UMBRAL_DINERO_CAMPANA_MS)
        linea_umbral(ax, normal, f"{'U-01' if grupo == 'consulta' else 'U-02'}\n{normal:,} ms")
        if "pico" in escenarios:
            linea_umbral(ax, campana, f"U-06 (solo\npico) {campana:,}", estilo=":")
        ax.set_xticks(x, [f"grupo\n{grupo}" if e == grupo else e for e in entidades])
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(MILES)
        ax.set_ylabel("p95 (ms, escala log)")
        ax.set_title("Consultas e inicio de sesión" if grupo == "consulta" else "Operaciones de dinero")
        ax.grid(axis="x", visible=False)
    handles, labels = ejes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, bbox_to_anchor=(0.47, 0.0))
    guardar(fig, ruta, rect=(0, 0.12, 0.95, 0.95))


def tabla_veredictos(analisis: dict) -> pd.DataFrame:
    filas = {}
    for esc in ORDEN:
        if esc not in analisis:
            continue
        ev = analisis[esc].evaluacion
        for f in ev["validez"] + ev["umbrales"]:
            if f.decide or f.id.startswith("U"):
                fila = filas.setdefault(f.id, {"ID": f.id, "Criterio": REQUISITO.get(f.id) or VALIDEZ.get(f.id, f.criterio)})
                actual = fila.get(esc)
                # V con varias filas (p. ej. V-06 por endpoint): basta una falla
                fila[esc] = "FALLA" if "FALLA" in (actual, f.resultado) else f.resultado if actual in (None, "PASA") else actual
    tabla = pd.DataFrame(sorted(filas.values(), key=lambda d: (d["ID"][0] != "U", d["ID"])))
    return tabla


def tabla_escenarios(analisis: dict) -> pd.DataFrame:
    filas = []
    for esc in ORDEN:
        if esc not in analisis:
            continue
        a = analisis[esc]
        pet, rotulo, _ = peticiones_medidas(a) if esc in EN_G11 else (a.corrida.pet, "toda la corrida", None)
        v = a.ventanas
        cap = a.evaluacion["extra"].get("capacidad", {})
        filas.append({"escenario": esc, "marca": a.corrida.marca, "subconjunto": rotulo, "peticiones": len(pet),
                      "p95_consulta_ms": percentil(pet.loc[pet["grupo"] == "consulta", "dur"]),
                      "p95_dinero_ms": percentil(pet.loc[pet["grupo"] == "dinero", "dur"]),
                      "error_rendimiento_%": 100 * pet["error_rend"].mean() if len(pet) else math.nan,
                      "error_datos_%": 100 * pet["error_datos"].mean() if len(pet) else math.nan,
                      "throughput_max_req_s": v["req_s"].max(), "usuarios_simultaneos_max": v["L_medida"].max(),
                      "cpu_qolqe_max_%": v["cpu_qolqe"].max() if "cpu_qolqe" in v else math.nan,
                      "rss_qolqe_max_MB": v["rss_qolqe_max"].max() if "rss_qolqe_max" in v else math.nan,
                      "cpu_equipo_max_%": v["cpu_equipo"].max() if "cpu_equipo" in v else math.nan,
                      "capacidad_U08": cap.get("capacidad", math.nan)})
    return pd.DataFrame(filas)


def escribir(analisis: dict, carpeta: Path) -> None:
    carpeta.mkdir(parents=True, exist_ok=True)
    g11(analisis, carpeta / "G11_comparativo.png")
    veredictos = tabla_veredictos(analisis)
    veredictos.to_csv(carpeta / "veredictos.csv", index=False)
    escenarios = tabla_escenarios(analisis)
    escenarios.to_csv(carpeta / "resumen_escenarios.csv", index=False, float_format="%.2f")
    vista = veredictos.fillna("—").map(lambda x: MARCA.get(x, x))
    resumen = escenarios.copy()
    for columna in resumen.columns[4:]:
        decimales = 2 if "%" in columna else 0
        resumen[columna] = resumen[columna].map(lambda x, d=decimales: fmt(x, d))
    resumen["peticiones"] = resumen["peticiones"].map(fmt)
    resumen = resumen.rename(columns=ENCABEZADOS)
    corridas = ", ".join(f"{e} `{a.corrida.marca}`" for e, a in analisis.items())
    texto = ["# Comparativo de escenarios", "", f"Última corrida de cada escenario: {corridas}.", "",
             f"Umbral de error de rendimiento: ≤ {fmt(ERROR_MAX * 100)} % (U-03). Capacidad U-08 en usuarios simultáneos.", "",
             "## Veredicto por umbral y escenario", "", _md(vista), "", "## Resumen por escenario", "", _md(resumen), "",
             "![G11](G11_comparativo.png)", ""]
    (carpeta / "veredictos.md").write_text("\n".join(texto), encoding="utf-8")
