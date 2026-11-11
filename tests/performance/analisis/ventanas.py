"""Tabla por ventana de tiempo (diseño §7.2): una fila por ventana con tiempos, throughput, errores,
sesiones simultáneas y recursos. Es la base de los gráficos en el tiempo y de U-05, U-08 y U-09(a)."""
import numpy as np
import pandas as pd
from config import EP_CRITICOS, EP_OTRAS, PERCENTIL
from corrida import Corrida, rejilla
from metricas import concurrencia, percentil
from perfiles import fase_en, peticiones_ofrecidas, simultaneos_esperados, tasa_llegada

# errores_rendimiento{tipo} de k6/operaciones.js → rótulo de los gráficos (S-06, §5.4)
TIPOS = {"http_5xx": "5xx (p. ej. database is locked)", "timeout": "timeout de 30 s", "conexion": "conexión rechazada o cortada",
         "cuerpo_invalido": "2xx con cuerpo inválido", "no_autenticado": "401 a mitad de sesión"}


def bordes(c: Corrida, ancho: float) -> np.ndarray:
    """Bordes alineados con el inicio de la fase medida (p. ej. 120 s), para que ninguna ventana mezcle fases."""
    desfase = c.perfil.inicio_medicion_s % ancho
    b = np.arange(desfase, c.duracion + ancho, ancho)
    return np.concatenate([[0.0], b]) if desfase > 0 else b


def _por_ventana(df: pd.DataFrame, b: np.ndarray, columna: str = "t") -> np.ndarray:
    return np.searchsorted(b, df[columna].to_numpy(), side="right") - 1


def _percentiles(pet: pd.DataFrame, filtro: pd.Series, nombre: str, salida: pd.DataFrame) -> None:
    grupo = pet[filtro].groupby("w")["dur"]
    salida[f"p95_{nombre}"] = grupo.agg(lambda v: percentil(v, PERCENTIL))
    salida[f"p50_{nombre}"] = grupo.agg(lambda v: percentil(v, 50))
    salida[f"n_{nombre}"] = grupo.size()


def _media_recurso(c: Corrida, monitor: str, columna: str, b: np.ndarray, salida: pd.DataFrame, nombre: str) -> None:
    df = c.recursos.get(monitor)
    if df is None or columna not in df or df[columna].isna().all():
        return
    w = _por_ventana(df, b)
    serie = df[columna].groupby(w)
    if nombre == "nr_throttled":   # contador acumulado del cgroup: interesa cuánto subió en la ventana
        salida[nombre] = serie.max() - serie.min()
        return
    salida[nombre] = serie.mean()
    salida[f"{nombre}_max"] = serie.max()


def tabla_ventanas(c: Corrida, ancho: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devuelve (ventanas, errores de datos por código y ventana en formato largo)."""
    b = bordes(c, ancho)
    v = pd.DataFrame({"ini": b[:-1], "fin": b[1:]})
    v["ancho"] = v["fin"] - v["ini"]
    v["minuto"] = (v["ini"] + v["ancho"] / 2) / 60
    v["fase"] = fase_en(c.perfil, (v["ini"] + v["ancho"] / 2).to_numpy())

    pet = c.pet.assign(w=_por_ventana(c.pet, b))
    pet = pet[(pet["w"] >= 0) & (pet["w"] < len(v))]
    v["req_n"] = pet.groupby("w").size()
    v["req_s"] = pet[~pet["error_rend"]].groupby("w").size() / v["ancho"]          # atendidas (U-04)
    _percentiles(pet, pet["dur"].notna(), "todas", v)
    for grupo in ("consulta", "dinero"):
        _percentiles(pet, pet["grupo"] == grupo, grupo, v)
    _percentiles(pet, pet["ep"].isin(EP_OTRAS), "otras", v)
    for ep in [e for lista in EP_CRITICOS.values() for e in lista]:
        _percentiles(pet, pet["ep"] == ep, ep, v)

    # Carga programada (modelo abierto) y Ley de Little, promediadas en cada ventana
    medias = {"req_s_ofrecidas": [], "llegada_min": [], "L_esperada": [], "L_medida": []}
    for ini, fin in zip(v["ini"], v["fin"], strict=True):
        t = rejilla(ini, fin)
        medias["req_s_ofrecidas"].append(np.mean(peticiones_ofrecidas(c.perfil, t)) if t.size else np.nan)
        medias["llegada_min"].append(np.mean(tasa_llegada(c.perfil, t)) * 60 if t.size else np.nan)
        medias["L_esperada"].append(np.mean(simultaneos_esperados(c.perfil, t)) if t.size else np.nan)
        medias["L_medida"].append(np.mean(concurrencia(c.inicios_sesion, c.sesiones["fin"], t))
                                  if t.size and len(c.inicios_sesion) else np.nan)
    for columna, valores in medias.items():
        v[columna] = valores
    # iniciadas = logins (todas las sesiones, también las que k6 cortó); completadas = iteration_duration
    inicios = pd.Series(c.inicios_sesion)
    v["sesiones_iniciadas_min"] = inicios.groupby(np.searchsorted(b, inicios.to_numpy(), side="right") - 1).size() / v["ancho"] * 60
    if len(c.sesiones):
        v["sesiones_completadas_min"] = c.sesiones.groupby(_por_ventana(c.sesiones, b, "fin")).size() / v["ancho"] * 60

    otras = c.otras.assign(w=_por_ventana(c.otras, b))
    vus = otras[otras["metrica"] == "vus"]
    v["vus_k6"] = vus.groupby("w")["valor"].mean()
    v["descartadas"] = otras[otras["metrica"] == "dropped_iterations"].groupby("w")["valor"].sum()

    # Errores de rendimiento (U-03): por operación si existe operacion_fallida; si no, por petición
    ops = otras[otras["metrica"] == "operacion_fallida"]
    if len(ops):
        v["ops_n"] = ops.groupby("w").size()
        v["error_ops"] = ops.groupby("w")["valor"].mean()
    else:
        v["ops_n"] = v["req_n"]
        v["error_ops"] = pet.groupby("w")["error_rend"].mean()
    # Tipo de cada error: errores_rendimiento{tipo} de k6 (incluye cuerpo inválido y 401); si no está, por status
    por_tipo = otras[otras["metrica"] == "errores_rendimiento"].assign(tipo_error=lambda d: d["tipo"].map(TIPOS).fillna(d["tipo"]))
    if por_tipo.empty:
        por_tipo = pet[pet["tipo_error"] != ""].assign(valor=1)
    for tipo, filas in por_tipo.groupby("tipo_error"):
        v[f"err_req::{tipo}"] = filas.groupby("w")["valor"].sum() / v["req_n"]

    # Errores de datos (V-02), por código de negocio
    datos = otras[otras["metrica"] == "errores_datos"]
    if datos.empty:   # respaldo: 4xx por status
        datos = pet[pet["error_datos"]].assign(codigo=lambda d: "HTTP " + d["status"].astype(str), valor=1)
    largo = datos.groupby(["w", "codigo"])["valor"].sum().rename("n").reset_index()

    q = c.recursos.get("qolqe")
    cpu_qolqe = "cpu_cgroup" if q is not None and "cpu_cgroup" in q and q["cpu_cgroup"].notna().any() else "cpu"
    throttling = "qolqe" if q is not None and "nr_throttled" in q else "docker"
    # CPU de Qolqe: el del cgroup (100 % = la cuota de 1 CPU) si el monitor lo da; si no, el de psutil sobre el proceso
    for monitor, columna, nombre in (("qolqe", cpu_qolqe, "cpu_qolqe"), ("qolqe", "cpu", "cpu_qolqe_proceso"),
                                     ("qolqe", "mem_mb", "rss_qolqe"),
                                     ("qolqe", "hilos", "hilos"), ("qolqe", "descriptores", "descriptores"),
                                     ("docker", "cpu", "cpu_docker"), ("docker", "mem_mb", "mem_docker"),
                                     (throttling, "nr_throttled", "nr_throttled"),
                                     ("k6", "cpu", "cpu_k6"), ("k6", "mem_mb", "mem_k6"),
                                     ("k6", "cpu_k6_equipo", "cpu_k6_equipo"), ("k6", "cpu_equipo", "cpu_equipo")):
        _media_recurso(c, monitor, columna, b, v, nombre)
    for columna in ("req_n", "descartadas", "ops_n", "req_s"):   # req_s: una ventana sin respuestas atendidas vale 0
        v[columna] = v[columna].fillna(0)
    return v, largo
