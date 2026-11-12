"""U-09 (resistencia): proyección a un día completo de 54,000 sesiones (S-11, S-12) y deriva del p95."""
import math

import numpy as np
from config import MINUTOS_DERIVA, PERCENTIL, SESIONES_DIA
from corrida import Corrida
from metricas import percentil, regresion
from perfiles import intervalo_fase


def sesiones_acumuladas(c: Corrida, t: np.ndarray) -> np.ndarray:
    """Sesiones iniciadas desde el arranque hasta t (las proyecciones son por sesión, no por hora: S-11)."""
    return np.searchsorted(c.inicios_sesion, t, side="right")   # una sesión = un login (también las cortadas)


def proyecciones(c: Corrida) -> dict:
    """RSS, hilos y descriptores contra sesiones acumuladas en el estado estable (regresión lineal)."""
    tramo = intervalo_fase(c.perfil, ("estable",)) or (0.0, c.duracion)
    salida = {"tramo": tramo}
    rec = c.recursos.get("qolqe")
    fuente_memoria = "RSS del proceso (psutil)"
    if rec is None or "mem_mb" not in rec:   # respaldo: memoria del contenedor (incluye la caché de páginas, §6.3)
        rec, fuente_memoria = c.recursos.get("docker"), "memoria del contenedor (docker stats)"
    if rec is not None:
        rec = rec[(rec["t"] >= tramo[0]) & (rec["t"] <= tramo[1])]
        x = sesiones_acumuladas(c, rec["t"].to_numpy())
        for columna, nombre in (("mem_mb", "memoria"), ("hilos", "hilos"), ("descriptores", "descriptores")):
            if columna not in rec or rec[columna].isna().all():
                continue
            a, b, r2 = regresion(x, rec[columna])
            inicial = float(rec.loc[rec["t"] < tramo[0] + 300 * c.perfil.escala, columna].mean())   # primeros 5 min del estado estable
            salida[nombre] = {"pendiente": a, "intercepto": b, "r2": r2, "inicial": inicial,
                              "final": float(rec[columna].tail(60).mean()), "proyeccion": a * SESIONES_DIA + b,
                              "x": x, "y": rec[columna].to_numpy(), "sesiones_medidas": int(x.max(initial=0))}
        salida["fuente_memoria"] = fuente_memoria

    # U-09(d): p95 de los últimos 10 min ≤ 1.2 × p95 de los primeros 10 min del estado estable
    pet = c.pet[c.pet["fase"] == "estable"] if (c.pet["fase"] == "estable").any() else c.pet
    inicio_pet = pet["t"] - pet["duracion_ms"] / 1000
    minutos = MINUTOS_DERIVA * 60 * c.perfil.escala   # 10 min (comprimidos en un ensayo)
    primeros = pet[inicio_pet < tramo[0] + minutos]
    ultimos = pet[inicio_pet >= tramo[1] - minutos]
    salida["deriva"] = {}
    for grupo in ("consulta", "dinero"):
        p_ini = percentil(primeros.loc[primeros["grupo"] == grupo, "dur"], PERCENTIL)
        p_fin = percentil(ultimos.loc[ultimos["grupo"] == grupo, "dur"], PERCENTIL)
        salida["deriva"][grupo] = (p_ini, p_fin, p_fin / p_ini if p_ini and not math.isnan(p_ini) else math.nan)
    return salida
