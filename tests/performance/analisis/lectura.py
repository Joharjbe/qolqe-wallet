"""Lectura de los archivos de cada corrida (diseño §7.1).

- muestras.csv.gz: salida cruda de `k6 run --out csv=…` (k6 2.3.0: columnas metric_name, timestamp, metric_value, …,
  extra_tags con "ep=…&op=…&grupo=…&fase=…"). La marca de tiempo puede venir en s, ms (K6_CSV_TIME_FORMAT=unix_milli),
  µs, ns o RFC 3339: se detecta sola.
- peticiones.csv.gz y metricas_k6.csv.gz: versión compacta que escribe este análisis (sirve si se borran las muestras).
- recursos_qolqe.csv, recursos_docker.csv, recursos_k6.csv: monitores (psutil y docker stats), una fila por segundo.
- corrida.json (hora de inicio y fin), resumen.json (handleSummary de k6), verificacion_dinero.txt, consola.txt.
"""
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qsl
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from config import EP_CONSULTA, EP_DINERO

LIMA = ZoneInfo("America/Lima")
ETIQUETAS = ("ep", "op", "grupo", "fase", "campana", "codigo", "tipo")
METRICAS_OTRAS = ("http_req_connecting", "iteration_duration", "dropped_iterations", "operacion_fallida",
                  "operacion_error_datos", "errores_datos", "errores_rendimiento", "dinero_confirmado",
                  "dinero_sin_respuesta", "vus", "vus_max")   # nombres de k6/operaciones.js
COLUMNAS_K6 = ("metric_name", "timestamp", "metric_value", "error_code", "group", "method", "name", "scenario", "status",
               "extra_tags")
COLUMNAS_PETICIONES = ["ts", "ep", "op", "grupo", "fase", "campana", "status", "duracion_ms", "conexion_ms",
                       "error_code", "name", "method", "scenario"]
COLUMNAS_OTRAS = ["metrica", "ts", "valor", "op", "ep", "fase", "campana", "codigo", "tipo", "scenario"]


# ---------- tiempos ----------
def a_segundos(valores: pd.Series) -> pd.Series:
    """Convierte marcas de tiempo de k6 o de los monitores a segundos epoch (float)."""
    numeros = pd.to_numeric(valores, errors="coerce")
    if numeros.notna().mean() < 0.5:   # RFC 3339
        return pd.to_datetime(valores, utc=True, errors="coerce").astype("int64") / 1e9
    mediana = float(numeros.median())
    escala = 1e9 if mediana > 1e17 else 1e6 if mediana > 1e14 else 1e3 if mediana > 1e11 else 1
    return numeros / escala


def epoca(meta: dict, clave: str) -> float | None:
    """Hora de inicio o fin de corrida.json en epoch, aceptando `<clave>_epoch`, un número, un ISO o {epoch|iso}."""
    candidatos = [meta.get(f"{clave}_epoch"), meta.get(clave), meta.get(f"{clave}_iso")]
    for valor in candidatos:
        if isinstance(valor, dict):
            valor = valor.get("epoch", valor.get("ts", valor.get("iso")))
        if isinstance(valor, int | float):
            return float(valor) / (1000 if valor > 1e11 else 1)
        if isinstance(valor, str) and valor.strip():
            try:
                fecha = datetime.fromisoformat(valor.strip())   # Python 3.11 ya acepta la Z final
                return (fecha if fecha.tzinfo else fecha.replace(tzinfo=LIMA)).timestamp()
            except ValueError:
                continue
    return None


# ---------- k6 ----------
def _expandir_etiquetas(extra: pd.Series) -> pd.DataFrame:
    """'ep=login&fase=estable' → columnas ep, fase… (se parsea cada combinación distinta una sola vez)."""
    unicos = {texto: dict(parse_qsl(texto, keep_blank_values=True)) for texto in extra.unique()}
    filas = extra.map(unicos)
    return pd.DataFrame({e: filas.map(lambda d, e=e: d.get(e, "")) for e in ETIQUETAS}, index=extra.index)


def leer_muestras_k6(ruta: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lee el CSV crudo de k6 por trozos y deja solo las métricas que usa el análisis."""
    trozos = []
    for trozo in pd.read_csv(ruta, usecols=lambda c: c in COLUMNAS_K6, dtype=str, keep_default_na=False, chunksize=500_000):
        trozos.append(trozo[trozo["metric_name"].isin(("http_req_duration", *METRICAS_OTRAS))])
    crudo = pd.concat(trozos, ignore_index=True)
    for columna in COLUMNAS_K6:
        if columna not in crudo:
            crudo[columna] = ""
    crudo = pd.concat([crudo, _expandir_etiquetas(crudo["extra_tags"])], axis=1)
    # fuera: el chequeo de salud de setup() (grupo "soporte"), que corre antes del escenario y no es carga
    crudo = crudo[~crudo["group"].str.startswith(("::setup", "::teardown")) & (crudo["grupo"] != "soporte")]
    crudo["ts"] = a_segundos(crudo["timestamp"])
    crudo["valor"] = pd.to_numeric(crudo["metric_value"], errors="coerce")

    es_peticion = crudo["metric_name"] == "http_req_duration"
    pet = crudo[es_peticion].rename(columns={"valor": "duracion_ms"}).reset_index(drop=True)
    pet["status"] = pd.to_numeric(pet["status"], errors="coerce").fillna(-1).astype(int)
    conexion = crudo[crudo["metric_name"] == "http_req_connecting"]
    # k6 escribe las métricas de una petición juntas y en el mismo orden: si los conteos coinciden, se emparejan por orden
    pet["conexion_ms"] = conexion["valor"].to_numpy() if len(conexion) == len(pet) else np.nan
    otras = crudo[~es_peticion].rename(columns={"metric_name": "metrica"})
    if len(conexion) == len(pet):
        otras = otras[otras["metrica"] != "http_req_connecting"]
    return completar_grupo(pet[COLUMNAS_PETICIONES]), otras[COLUMNAS_OTRAS].reset_index(drop=True)


def completar_grupo(pet: pd.DataFrame) -> pd.DataFrame:
    """Si una petición no trae la etiqueta grupo, se deduce del ep (S-02)."""
    pet = pet.copy()
    falta = pet["grupo"].fillna("").astype(str) == ""
    pet.loc[falta & pet["ep"].isin(EP_DINERO), "grupo"] = "dinero"
    pet.loc[falta & pet["ep"].isin(EP_CONSULTA), "grupo"] = "consulta"
    return pet


def leer_k6(carpeta: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Las muestras crudas mandan si están (y se reescribe la versión compacta); si no, se usa la compacta."""
    compacta_pet, compacta_otras = carpeta / "peticiones.csv.gz", carpeta / "metricas_k6.csv.gz"
    crudas = sorted(carpeta.glob("muestras*.csv*"))
    if crudas:
        pet, otras = leer_muestras_k6(crudas[0])
        pet.to_csv(compacta_pet, index=False, float_format="%.3f", compression="gzip")
        otras.to_csv(compacta_otras, index=False, float_format="%.3f", compression="gzip")
        return pet, otras
    if compacta_pet.exists():
        pet = pd.read_csv(compacta_pet, dtype={e: str for e in ETIQUETAS} | {"name": str, "scenario": str}, keep_default_na=False)
        for columna in ("ts", "duracion_ms", "conexion_ms"):
            pet[columna] = pd.to_numeric(pet[columna], errors="coerce")
        otras = (pd.read_csv(compacta_otras, dtype={e: str for e in ETIQUETAS} | {"scenario": str}, keep_default_na=False)
                 if compacta_otras.exists() else pd.DataFrame(columns=COLUMNAS_OTRAS))
        otras["valor"] = pd.to_numeric(otras["valor"], errors="coerce")
        otras["ts"] = pd.to_numeric(otras["ts"], errors="coerce")
        return completar_grupo(pet), otras
    raise FileNotFoundError(f"{carpeta}: no hay muestras*.csv(.gz) de k6 ni peticiones.csv.gz")


# ---------- recursos ----------
NOMBRES_RECURSOS = {"cpu_%": "cpu", "memoria_mb": "mem_mb", "memoria_%": "mem_pct", "hilos": "hilos",
                    "descriptores": "descriptores", "pids": "pids", "cpu_k6_equipo_%": "cpu_k6_equipo", "cpu_cgroup_%": "cpu_cgroup",
                    "cpu_total_equipo_%": "cpu_equipo", "cpu_herramienta_%": "cpu_herramienta",
                    "nr_throttled": "nr_throttled", "throttled_usec": "throttled_usec"}


def _desde_hora(horas: pd.Series, referencia: float | None) -> pd.Series:
    """'HH:MM:SS' → epoch. Se prueba hora de Lima y UTC (un monitor dentro del contenedor escribe en UTC)
    y se queda con la que cae más cerca del inicio de la corrida; si la hora retrocede, pasó la medianoche."""
    referencia = referencia or datetime.now(LIMA).timestamp()
    segundos = pd.to_timedelta(horas.astype(str).str.strip()).dt.total_seconds().to_numpy()
    segundos = segundos + 86400 * np.concatenate([[0], np.cumsum(np.diff(segundos) < -43200)])
    mejor = None
    for zona in (LIMA, ZoneInfo("UTC")):
        dia = datetime.fromtimestamp(referencia, zona).replace(hour=0, minute=0, second=0, microsecond=0)
        for desplazamiento in (-86400, 0, 86400):
            ts = dia.timestamp() + desplazamiento + segundos
            distancia = abs(ts[0] - referencia)
            if mejor is None or distancia < mejor[0]:
                mejor = (distancia, ts)
    return pd.Series(mejor[1], index=horas.index)


def leer_recursos(ruta: Path, referencia: float | None) -> pd.DataFrame | None:
    """CSV de un monitor → columnas normalizadas (cpu, mem_mb, hilos, …) y ts epoch. None si no existe."""
    if not ruta.exists() or ruta.stat().st_size == 0:
        return None
    df = pd.read_csv(ruta)
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.rename(columns={c: NOMBRES_RECURSOS[c] for c in df.columns if c in NOMBRES_RECURSOS})
    if "ts" in df and df["ts"].notna().any():
        df["ts"] = a_segundos(df["ts"])
    elif "hora" in df:
        df["ts"] = _desde_hora(df["hora"], referencia)
    else:
        return None
    for columna in df.columns:
        if columna != "hora":
            df[columna] = pd.to_numeric(df[columna], errors="coerce")
    return df.dropna(subset=["ts"]).sort_values("ts").reset_index(drop=True)


# ---------- metadatos y resultados de otras partes ----------
def leer_json(ruta: Path) -> dict:
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def umbrales_k6(resumen: dict) -> list[dict]:
    """Umbrales que evaluó k6: del bloque qolqe.umbrales de k6/resumen.js (con ID y valor medido) o, si no está,
    de data.metrics[…].thresholds del handleSummary. estado: ✓ cumple, ✗ falla, ○ sin muestras."""
    propios = (resumen.get("qolqe") or {}).get("umbrales")
    if propios:
        return [{"descripcion": u.get("descripcion", ""), "metrica": u.get("metrica", ""), "condicion": u.get("condicion", ""),
                 "valor": u.get("valor", ""), "estado": "○" if u.get("sin_muestras") else "✓" if u.get("ok") else "✗"}
                for u in propios]
    metricas = resumen.get("metrics") or {}
    return [{"descripcion": "", "metrica": nombre, "condicion": expresion, "valor": "", "estado": "✓" if estado.get("ok") else "✗"}
            for nombre, datos in metricas.items() for expresion, estado in (datos.get("thresholds") or {}).items()]


def leer_verificacion(ruta: Path) -> tuple[int | None, str]:
    """Descuadres de verificacion_dinero.txt (U-07). Se espera una línea 'TOTAL descuadres: N';
    si no está, se suman los 'descuadre(s): N' de C1…C6. Devuelve (None, motivo) si no se puede leer."""
    if not ruta.exists():
        return None, "no existe verificacion_dinero.txt"
    texto = ruta.read_text(encoding="utf-8", errors="replace")
    total = re.findall(r"(?im)^\s*total\b[^\n\d]*?(\d+)", texto)
    if total:
        return int(total[-1]), "línea TOTAL"
    partes = re.findall(r"(?i)descuadres?\s*[:=]\s*(-?\d+)", texto)
    if partes:
        return sum(abs(int(p)) for p in partes), f"suma de {len(partes)} chequeos"
    return None, "formato no reconocido"


def avisos_vus_insuficientes(ruta: Path) -> int | None:
    """V-07: cuántas veces k6 avisó 'Insufficient VUs' en consola.txt (None si no existe)."""
    if not ruta.exists():
        return None
    return len(re.findall(r"(?i)insufficient vus", ruta.read_text(encoding="utf-8", errors="replace")))
