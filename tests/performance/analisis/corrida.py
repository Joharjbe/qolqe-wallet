"""Carga una carpeta de resultados (resultados/<escenario>/<marca>/) y deja todo en el mismo eje de tiempo.

El tiempo t (s) se cuenta desde el inicio del escenario = inicio de la primera petición, que es el mismo
origen que usa k6 para la etiqueta fase (diseño §4.2: (Date.now() − exec.scenario.startTime)/1000).
"""
import os
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from config import CONEXION_P95_MAX_MS
from lectura import avisos_vus_insuficientes, epoca, leer_json, leer_k6, leer_recursos
from metricas import es_error_datos, es_error_rendimiento, percentil, sesiones_desde_iteraciones, tipo_error
from perfiles import Perfil, fase_en, intervalo_campana, intervalo_fase, perfil

MONITORES = {"qolqe": "recursos_qolqe.csv", "docker": "recursos_docker.csv", "k6": "recursos_k6.csv"}


@dataclass
class Corrida:
    carpeta: Path
    escenario: str
    meta: dict
    perfil: Perfil
    t0: float                       # epoch del inicio del escenario
    duracion: float                 # s desde t0 hasta la última muestra
    pet: pd.DataFrame               # una fila por petición (t = fin de la respuesta, en s desde t0)
    otras: pd.DataFrame             # demás métricas de k6 (iteration_duration, operacion_fallida, …)
    sesiones: pd.DataFrame          # inicio y fin de cada sesión terminada (s desde t0, de iteration_duration)
    inicios_sesion: np.ndarray      # inicio del login de todas las sesiones, terminadas o cortadas (s desde t0)
    recursos: dict = field(default_factory=dict)   # 'qolqe' | 'docker' | 'k6' → DataFrame con columna t
    resumen: dict = field(default_factory=dict)    # handleSummary de k6
    conexion_sumada: bool = False   # §2.1: se sumó http_req_connecting al tiempo de respuesta
    conexion_p95: float = float("nan")
    avisos_vus: int | None = None   # V-07

    @property
    def marca(self) -> str:
        return self.carpeta.name

    @property
    def nombre(self) -> str:
        return f"{self.escenario} · {self.marca}"

    # --- subconjuntos que se miden (perfil.medidas) ---
    def mascara(self, df: pd.DataFrame, etiqueta: str | None, valores: tuple | None) -> pd.Series:
        if etiqueta is None:
            return pd.Series(True, index=df.index)
        return df[etiqueta].isin(valores)

    def intervalo(self, etiqueta: str | None, valores: tuple | None) -> tuple[float, float]:
        """Segundos (inicio, fin) que ocupa un subconjunto, para pasar conteos a tasas."""
        if etiqueta == "fase" and (tramo := intervalo_fase(self.perfil, valores)):
            return tramo
        if etiqueta == "campana" and (tramo := intervalo_campana(self.perfil)):
            return tramo
        filas = self.pet[self.mascara(self.pet, etiqueta, valores)]
        if filas.empty:
            return 0.0, self.duracion
        return float((filas["t"] - filas["duracion_ms"] / 1000).min()), float(filas["t"].max())


def _completar_fases(df: pd.DataFrame, p: Perfil, t_inicio: pd.Series) -> None:
    """Si faltan las etiquetas fase/campana (o se perdieron), se calculan con el perfil programado."""
    falta = df["fase"].fillna("").astype(str) == ""
    if falta.any():
        df.loc[falta, "fase"] = fase_en(p, t_inicio[falta].to_numpy())
    campana = intervalo_campana(p)
    if campana:
        falta = df["campana"].fillna("").astype(str) == ""
        dentro = (t_inicio >= campana[0]) & (t_inicio < campana[1])
        df.loc[falta & dentro, "campana"] = "si"
        df.loc[falta & ~dentro, "campana"] = "no"


def cargar(carpeta: Path) -> Corrida:
    carpeta = Path(carpeta)
    meta = leer_json(carpeta / "corrida.json")
    escenario = str(meta.get("escenario") or carpeta.parent.name)
    parametros = meta.get("parametros") or {}
    resumen = leer_json(carpeta / "resumen.json")
    qolqe = resumen.get("qolqe") or {}
    top = parametros.get("TOP") or qolqe.get("top")
    l_cap = parametros.get("L_CAP") or qolqe.get("l_cap")
    escala = float(parametros.get("ESCALA") or qolqe.get("escala") or 1)   # ensayo comprimido (k6/escenarios.js)
    p = perfil(escenario, float(top) if top else None, float(l_cap) if l_cap else None, escala)

    pet, otras = leer_k6(carpeta)
    if pet.empty:
        raise ValueError(f"{carpeta}: no hay peticiones en las muestras de k6")
    inicio_peticion = pet["ts"] - pet["duracion_ms"] / 1000
    t0 = float(meta.get("inicio_escenario_epoch") or inicio_peticion.min())
    pet["t"] = pet["ts"] - t0
    otras["t"] = otras["ts"] - t0
    _completar_fases(pet, p, inicio_peticion - t0)
    _completar_fases(otras, p, otras["t"])

    sesiones = sesiones_desde_iteraciones(otras)
    sesiones[["inicio", "fin"]] -= t0
    logins = pet[pet["ep"] == "login"]
    inicios_sesion = np.sort((logins["t"] - logins["duracion_ms"] / 1000).to_numpy())

    c = Corrida(carpeta, escenario, meta, p, t0, float(max(pet["t"].max(), otras["t"].max() if len(otras) else 0)),
                pet, otras, sesiones, inicios_sesion, resumen=resumen,
                avisos_vus=avisos_vus_insuficientes(carpeta / "consola.txt"))

    # §2.1: si el p95 de conexión del subconjunto medido pasa de 10 ms, se suma al tiempo de respuesta
    etiqueta, valores = p.medidas[0][1], p.medidas[0][2]
    conexion = pet.loc[c.mascara(pet, etiqueta, valores), "conexion_ms"]
    c.conexion_p95 = percentil(conexion.dropna(), 95) if conexion.notna().any() else float("nan")
    c.conexion_sumada = bool(c.conexion_p95 > CONEXION_P95_MAX_MS)
    pet["dur"] = pet["duracion_ms"] + (pet["conexion_ms"].fillna(0) if c.conexion_sumada else 0)
    pet["error_rend"] = es_error_rendimiento(pet["status"])
    pet["error_datos"] = es_error_datos(pet["status"])
    pet["tipo_error"] = tipo_error(pet["status"], pet["duracion_ms"])

    referencia = epoca(meta, "inicio") or t0
    fin = epoca(meta, "fin")
    for nombre, archivo in MONITORES.items():
        df = leer_recursos(carpeta / archivo, referencia)
        if df is None:
            continue
        df["t"] = df["ts"] - t0
        limite = max(c.duracion, (fin - t0) if fin else 0) + 30
        c.recursos[nombre] = df[(df["t"] >= -30) & (df["t"] <= limite)].reset_index(drop=True)
    _completar_k6(c)
    return c


def _completar_k6(c: Corrida) -> None:
    """V-01 usa el CPU de k6 respecto de todo el equipo. psutil lo da por núcleo: se divide entre los núcleos.
    Si el monitor de Qolqe trae la columna cpu_herramienta (script del scratchpad), se usa como monitor de k6."""
    k6 = c.recursos.get("k6")
    qolqe = c.recursos.get("qolqe")
    if k6 is None and qolqe is not None and "cpu_herramienta" in qolqe:
        k6 = qolqe[["ts", "t", "cpu_herramienta"] + (["cpu_equipo"] if "cpu_equipo" in qolqe else [])]
        k6 = k6.rename(columns={"cpu_herramienta": "cpu"})
    if k6 is None:
        return
    nucleos = int(c.meta.get("nucleos") or os.cpu_count() or 1)
    if "cpu_k6_equipo" not in k6 and "cpu" in k6:
        k6 = k6.assign(cpu_k6_equipo=k6["cpu"] / nucleos)
    c.recursos["k6"] = k6


def rejilla(desde: float, hasta: float, paso: float = 1.0) -> np.ndarray:
    return np.arange(desde + paso / 2, hasta, paso)
