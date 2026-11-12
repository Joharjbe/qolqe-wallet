"""Cálculos básicos: percentil por rango más cercano (S14), estadísticas, clasificación de errores y concurrencia."""
import math

import numpy as np
import pandas as pd
from config import TIMEOUT_MS


def percentil(valores, p: float = 95) -> float:
    """Percentil por rango más cercano, como en S14: se ordena y se toma la posición ⌈p/100 · n⌉."""
    datos = np.sort(np.asarray(valores, dtype=float))
    datos = datos[~np.isnan(datos)]
    if datos.size == 0:
        return math.nan
    return float(datos[max(math.ceil(p / 100 * datos.size), 1) - 1])


def estadisticas(valores) -> dict:
    """Columnas de la tabla resumen de S14 (sin error ni throughput, que dependen del status y del tiempo)."""
    datos = np.asarray(valores, dtype=float)
    if datos.size == 0:
        return {"n": 0, "promedio": math.nan, "p50": math.nan, "p90": math.nan, "p95": math.nan, "p99": math.nan, "max": math.nan}
    return {"n": int(datos.size), "promedio": float(np.nanmean(datos)), "p50": percentil(datos, 50),
            "p90": percentil(datos, 90), "p95": percentil(datos, 95), "p99": percentil(datos, 99), "max": float(np.nanmax(datos))}


# S-06: error de rendimiento = status 0 (timeout o conexión) o 5xx. Un 4xx es regla de negocio (error de datos, V-02).
def es_error_rendimiento(status: pd.Series) -> pd.Series:
    return (status == 0) | (status >= 500)


def es_error_datos(status: pd.Series) -> pd.Series:
    return (status >= 400) & (status < 500)


def tipo_error(status: pd.Series, duracion_ms: pd.Series) -> pd.Series:
    """Tipo de error de rendimiento de cada petición, para el gráfico de errores (vacío si no es error)."""
    tipo = pd.Series("", index=status.index, dtype=object)
    tipo[status >= 500] = "5xx (p. ej. database is locked)"
    tipo[(status == 0) & (duracion_ms >= TIMEOUT_MS * 0.99)] = "timeout de 30 s"
    tipo[(status == 0) & (duracion_ms < TIMEOUT_MS * 0.99)] = "conexión rechazada o cortada"
    return tipo


def sesiones_desde_iteraciones(otras: pd.DataFrame) -> pd.DataFrame:
    """Inicio y fin de cada sesión: k6 emite iteration_duration al terminar, así que inicio = fin − duración (G4)."""
    it = otras[otras["metrica"] == "iteration_duration"]
    return pd.DataFrame({"inicio": it["ts"] - it["valor"] / 1000, "fin": it["ts"]}).sort_values("inicio").reset_index(drop=True)


def concurrencia(inicios: np.ndarray, fines: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Sesiones simultáneas medidas en cada instante t: las que empezaron antes de t y aún no terminan.

    inicios = inicio del login de TODAS las sesiones (cada sesión empieza con su login); fines = fin de las sesiones que
    terminaron (iteration_duration). Así cuentan también las que quedaron atascadas y k6 cortó al final (gracefulStop),
    que no emiten iteration_duration: si solo se usaran las terminadas, justo antes de un colapso la concurrencia
    medida bajaría en vez de subir."""
    inicios, fines = np.sort(np.asarray(inicios, dtype=float)), np.sort(np.asarray(fines, dtype=float))
    return np.searchsorted(inicios, t, side="right") - np.searchsorted(fines, t, side="right")


def regresion(x, y) -> tuple[float, float, float]:
    """Recta de mínimos cuadrados y = a·x + b. Devuelve (a, b, r²)."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    ok = ~(np.isnan(x) | np.isnan(y))
    x, y = x[ok], y[ok]
    if x.size < 3 or np.ptp(x) == 0:
        return math.nan, math.nan, math.nan
    a, b = np.polyfit(x, y, 1)
    residuo = y - (a * x + b)
    total = ((y - y.mean()) ** 2).sum()
    return float(a), float(b), float(1 - (residuo ** 2).sum() / total) if total > 0 else math.nan


def fmt(valor, decimales: int = 0, unidad: str = "") -> str:
    """Número con separador de miles y punto decimal, como el diseño (1,500 ms; 9.78 req/s)."""
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return "—"
    return f"{valor:,.{decimales}f}{(' ' + unidad) if unidad else ''}"
