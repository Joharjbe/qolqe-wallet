"""U-08 (estrés): capacidad = máximo de sesiones simultáneas con el que se cumplen U-01 a U-05 en ventanas de 30 s (S-10),
y la tabla T1…Tn del ejercicio 3 de S14 (una fila cada 100 usuarios)."""
import math

import numpy as np
import pandas as pd
from config import (
    DESCARTADAS_MAX,
    EP_CRITICOS,
    ERROR_MAX,
    FALLAS_SEGUIDAS,
    FRACCION_ATENDIDA,
    MUESTRAS_MIN_ENDPOINT,
    REDONDEO_CAPACIDAD,
    UMBRAL_CONSULTA_MS,
    UMBRAL_DINERO_MS,
    VENTANA_SIGMAS,
)

FASES_ESTRES = ("base", "rampa", "meseta")   # diseño §4.2; el drenaje no cuenta


def criterios_por_ventana(v: pd.DataFrame, escala: float = 1.0) -> tuple[pd.DataFrame, float]:
    """Marca en cada ventana qué criterio de hora punta se cumple. Devuelve (tabla, tolerancia de throughput)."""
    w = v[v["fase"].isin(FASES_ESTRES)].copy()
    w["razon_atendida"] = w["req_s"] / w["req_s_ofrecidas"]
    base = w[(w["fase"] == "base") & (w["ini"] >= 60 * escala)]["razon_atendida"]   # sin el primer minuto de llenado
    sigma = base.std() if len(base) >= 3 else math.nan
    tolerancia = max(1 - FRACCION_ATENDIDA, VENTANA_SIGMAS * sigma) if not math.isnan(sigma) else 1 - FRACCION_ATENDIDA

    criterios = {
        "p95 consulta < 800 ms (U-01)": w["p95_consulta"].isna() | (w["p95_consulta"] < UMBRAL_CONSULTA_MS),
        "p95 dinero < 1,500 ms (U-02)": w["p95_dinero"].isna() | (w["p95_dinero"] < UMBRAL_DINERO_MS),
        "error ≤ 1 % (U-03)": w["error_ops"].isna() | (w["error_ops"] <= ERROR_MAX),
        f"atendido ≥ {1 - tolerancia:.0%} de lo ofrecido (U-04)": w["razon_atendida"].isna() | (w["razon_atendida"] >= 1 - tolerancia),
        "sesiones descartadas = 0 (U-05a)": w["descartadas"] <= DESCARTADAS_MAX,
    }
    for grupo, eps in EP_CRITICOS.items():   # S-03: también por endpoint, si la ventana tiene muestras suficientes
        limite = UMBRAL_DINERO_MS if grupo == "dinero" else UMBRAL_CONSULTA_MS
        for ep in eps:
            if f"p95_{ep}" in w:
                pocas = w[f"n_{ep}"].fillna(0) < MUESTRAS_MIN_ENDPOINT
                criterios[f"p95 {ep} < {limite:,} ms"] = pocas | w[f"p95_{ep}"].isna() | (w[f"p95_{ep}"] < limite)
    tabla = pd.DataFrame(criterios)
    w["cumple"] = tabla.all(axis=1)
    w["motivo"] = tabla.apply(lambda fila: "; ".join(c for c, ok in fila.items() if not ok), axis=1)
    return w, tolerancia


def capacidad(v: pd.DataFrame, escala: float = 1.0) -> dict:
    """S-10: sesiones simultáneas de la última ventana que cumple antes de la primera falla sostenida, hacia abajo a 50."""
    w, tolerancia = criterios_por_ventana(v, escala)
    redondeo = max(1, round(REDONDEO_CAPACIDAD * escala))
    cumple = w["cumple"].to_numpy()
    falla = next((i for i in range(len(cumple) - FALLAS_SEGUIDAS + 1) if not cumple[i:i + FALLAS_SEGUIDAS].any()), None)
    previas = w.iloc[: falla if falla is not None else len(w)]
    previas = previas[previas["cumple"]]
    ultima = previas.iloc[-1] if len(previas) else None
    l_ok = float(ultima["L_medida"]) if ultima is not None else math.nan
    resultado = {
        "criterios": w, "tolerancia": tolerancia, "limite_alcanzado": falla is not None,
        "L_ultima_ok": l_ok, "minuto_ultima_ok": float(ultima["minuto"]) if ultima is not None else math.nan,
        # S-10: hacia abajo a 50 (en un ensayo comprimido los simultáneos se escalan, y el redondeo también)
        "capacidad": math.floor(l_ok / redondeo) * redondeo if not math.isnan(l_ok) else math.nan,
        "L_max": float(w["L_medida"].max()) if len(w) else math.nan,
    }
    if falla is not None:
        primera = w.iloc[falla]
        resultado |= {"minuto_falla": float(primera["minuto"]), "L_falla": float(primera["L_medida"]), "motivo_falla": primera["motivo"]}
    return resultado


def tabla_momentos(v: pd.DataFrame, paso: int = 100, escala: float = 1.0) -> pd.DataFrame:
    """Formato del ejercicio 3 de S14: el primer momento en que las sesiones simultáneas llegan a 100, 200, …
    (en un ensayo comprimido los simultáneos son L·escala, así que el paso también se escala)."""
    paso = max(1, round(paso * escala))
    w = v[v["fase"].isin(FASES_ESTRES)]
    filas, usadas = [], set()
    tope = int(np.nanmax(w["L_medida"])) if len(w) and w["L_medida"].notna().any() else 0
    for objetivo in range(paso, tope + 1, paso):
        llegan = w[w["L_medida"] >= objetivo]
        if llegan.empty:
            break
        if llegan.index[0] in usadas:   # la concurrencia saltó más de 100 en una ventana: no se repite la fila
            continue
        usadas.add(llegan.index[0])
        f = llegan.iloc[0]
        filas.append({
            "Momento": f"T{len(filas) + 1}", "Minuto": round(f["minuto"], 1), "Usuarios simultáneos": round(f["L_medida"]),
            "VUs de k6": f.get("vus_k6"), "p50 (ms)": f["p50_todas"], "p95 (ms)": f["p95_todas"],
            "p95 consulta (ms)": f["p95_consulta"], "p95 dinero (ms)": f["p95_dinero"], "Error (%)": f["error_ops"] * 100,
            "Throughput (req/s)": f["req_s"], "CPU Qolqe (%)": f.get("cpu_qolqe"), "Memoria (MB)": f.get("rss_qolqe"),
            "Hilos": f.get("hilos"), "Throttling (períodos)": f.get("nr_throttled"),
        })
    return pd.DataFrame(filas)
