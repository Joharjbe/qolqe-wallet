"""Paso 1 de S14: veredicto binario de cada umbral (U-01 a U-09) y de la validez de la corrida (V-01 a V-07).

Cada fila dice qué se midió, contra qué umbral y si pasa. Las filas con decide=False son informativas
(no cambian el veredicto del umbral; por ejemplo, los endpoints de "otras" con < 100 muestras, §3.3).
"""
import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from capacidad import capacidad
from config import (
    CARGA_EQUIPO_MAX,
    CPU_GENERADOR_MAX,
    DESCARTADAS_MAX,
    DURACION_SESION_S,
    EP_OTRAS,
    ERROR_MAX,
    ERRORES_DATOS_MAX,
    FACTOR_DERIVA,
    FACTOR_HILOS,
    FACTOR_TOP,
    FRACCION_ATENDIDA,
    MEZCLA,
    MEZCLA_TOLERANCIA_PP,
    OCIOSO_EQUIPO_MIN,
    OP_LOGIN,
    REFERENCIA_FRACCION,
    REQ_POR_OPERACION,
    REQ_S_MIN,
    RSS_MAX_MB,
    SESIONES_CALIBRACION,
    SESIONES_DIA,
    SESIONES_MIN_POR_MIN,
    UMBRAL_CONSULTA_CAMPANA_MS,
    UMBRAL_CONSULTA_MS,
    UMBRAL_DINERO_CAMPANA_MS,
    UMBRAL_DINERO_MS,
    VENTANA_U05_S,
)
from corrida import Corrida, rejilla
from lectura import leer_verificacion
from metricas import fmt, percentil
from perfiles import intervalo_campana, peticiones_ofrecidas, rango_concurrencia
from proyeccion import proyecciones
from ventanas import tabla_ventanas

PASA, FALLA, SIN_DATO, NO_APLICA, INFO, MEDIDO = "PASA", "FALLA", "SIN DATO", "NO APLICA", "INFO", "MEDIDO"

REQUISITO = {   # frase del requerimiento de cada umbral (diseño §2.1)
    "U-01": "Consultas e inicio de sesión: el 95 % en menos de 800 ms",
    "U-02": "Operaciones de dinero: el 95 % en menos de 1.5 s",
    "U-03": "En hora punta, no más del 1 % de operaciones fallidas",
    "U-04": "Sostener el volumen de la hora punta",
    "U-05": "…sin acumular retrasos",
    "U-06": "Campaña: degradación razonable del servicio",
    "U-07": "Ninguna operación de dinero a medias ni aplicada dos veces",
    "U-08": "Hasta cuántos usuarios simultáneos podemos crecer",
    "U-09": "Opera de 6:00 a 24:00 sin reinicios",
}
APLICA = {   # qué umbrales decide cada escenario (diseño §2.1, columna "Escenario")
    "carga": {"U-01", "U-02", "U-03", "U-04", "U-05", "U-07"},
    "resistencia": {"U-01", "U-02", "U-03", "U-04", "U-05", "U-07", "U-09"},
    "pico": {"U-06", "U-07"},
    "estres": {"U-07", "U-08"},
    "demo": {"U-01", "U-02", "U-03", "U-07"},
    "capacidad": {"U-01", "U-02", "U-03", "U-04", "U-05", "U-07"},   # §10.2 Opc. 2: hora punta a L_cap
    "referencia": {"U-07"},    # U-07 aplica a todos los escenarios que mueven dinero (§2.1)
    "calibracion": {"U-07"},
}
VALIDEZ = {   # criterios de validez de una corrida (diseño §2.3)
    "V-01": "CPU de k6 y del equipo < 80 %", "V-02": "errores de datos (4xx de negocio) = 0",
    "V-03": "mezcla lograda a ± 2 pp", "V-04": "equipo libre antes de empezar (CPU ocioso ≥ 65 %)",
    "V-05": "base restaurada idéntica y 1 CPU", "V-06": "con 1 VU, p95 ≤ 10 % del umbral",
    "V-07": "sin avisos 'Insufficient VUs'",
}
DONDE = {"U-01": "carga y resistencia", "U-02": "carga y resistencia", "U-03": "carga y resistencia",
         "U-04": "carga y resistencia", "U-05": "carga y resistencia", "U-06": "pico", "U-07": "todos",
         "U-08": "estrés", "U-09": "resistencia"}


@dataclass
class Fila:
    id: str
    criterio: str
    medido: str
    umbral: str
    resultado: str
    n: str = ""
    nota: str = ""
    decide: bool = True


def _res(ok) -> str:
    return SIN_DATO if ok is None or (isinstance(ok, float) and math.isnan(ok)) else (PASA if ok else FALLA)


# ---------- tiempos de respuesta (U-01, U-02, U-06) ----------
def filas_tiempos(c: Corrida, mascara: pd.Series, contexto: str, lim_c: float, lim_d: float,
                  id_c: str = "U-01", id_d: str = "U-02", decide: bool = True, nota: str = "") -> list[Fila]:
    pet = c.pet[mascara & c.pet["dur"].notna()]
    filas = []
    for nombre, filtro, limite, uid in (("consulta", pet["grupo"] == "consulta", lim_c, id_c),
                                         ("dinero", pet["grupo"] == "dinero", lim_d, id_d),
                                         ("otras", pet["ep"].isin(EP_OTRAS), lim_c, id_c)):
        d = pet.loc[filtro, "dur"]
        if d.empty and nombre == "otras":
            continue
        p = percentil(d)
        filas.append(Fila(uid, f"p95 grupo {nombre} · {contexto}", fmt(p, 0, "ms"), f"< {fmt(limite)} ms",
                          _res(None if d.empty else p < limite), fmt(len(d)), nota or "lectura literal (S-03)", decide))
    for ep, d in pet.groupby("ep"):
        dinero = (d["grupo"] == "dinero").any()
        limite, uid = (lim_d, id_d) if dinero else (lim_c, id_c)
        p = percentil(d["dur"])
        nombre = d["name"].iloc[0] if "name" in d and d["name"].iloc[0] else ep
        informativo = ep in EP_OTRAS
        filas.append(Fila(uid, f"p95 `{ep}` ({nombre}) · {contexto}", fmt(p, 0, "ms"), f"< {fmt(limite)} ms",
                          _res(p < limite), fmt(len(d)),
                          "informativo: el veredicto es el grupo otras (§3.3)" if informativo else nota or "por endpoint (S-03)",
                          decide and not informativo))
    return filas


def fila_error(c: Corrida, etiqueta, valores, contexto: str, uid: str = "U-03", decide: bool = True) -> Fila:
    """U-03 / S-06: operaciones fallidas ÷ operaciones totales (login incluido)."""
    ops = c.otras[(c.otras["metrica"] == "operacion_fallida") & c.mascara(c.otras, etiqueta, valores)]
    nota = "operacion_fallida (una muestra por operación, S-06)"
    if ops.empty:
        ops = c.pet[c.mascara(c.pet, etiqueta, valores)].assign(valor=lambda d: d["error_rend"].astype(float))
        nota = "falta operacion_fallida: se cuenta por petición (5xx y status 0)"
    tasa = float(ops["valor"].mean()) if len(ops) else math.nan
    return Fila(uid, f"error de rendimiento · {contexto}", fmt(tasa * 100, 2, "%"), f"≤ {fmt(ERROR_MAX * 100)} %",
                _res(None if ops.empty else tasa <= ERROR_MAX), fmt(len(ops)), nota, decide)


# ---------- volumen y retrasos (U-04, U-05) ----------
def filas_volumen(c: Corrida, etiqueta, valores, contexto: str) -> list[Fila]:
    ini, fin = c.intervalo(etiqueta, valores)
    duracion = max(fin - ini, 1e-9)
    pet = c.pet[c.mascara(c.pet, etiqueta, valores)]
    if pet.empty:   # la corrida no llegó a esa fase (p. ej., una de humo)
        return [Fila("U-04", f"throughput atendido · {contexto}", "—", f"≥ {REQ_S_MIN} req/s", SIN_DATO, nota="sin peticiones en la fase")]
    atendidas = float((~pet["error_rend"]).sum() / duracion)
    ofrecidas = float(np.nanmean(peticiones_ofrecidas(c.perfil, rejilla(ini, fin))))
    completas = c.sesiones[(c.sesiones["fin"] >= ini) & (c.sesiones["fin"] < fin)]
    por_min = len(completas) / duracion * 60 if len(c.sesiones) else math.nan
    # hora punta: los valores del diseño (U-04); capacidad (Opc. 2): 98 % de lo que ofrece su propia tasa
    hora_punta = c.perfil.tasa_inicial == SESIONES_MIN_POR_MIN
    minimo_req = REQ_S_MIN if hora_punta else FRACCION_ATENDIDA * ofrecidas
    llegada = c.perfil.tasa_inicial or SESIONES_MIN_POR_MIN
    minimo_sesiones = llegada * FRACCION_ATENDIDA
    return [
        Fila("U-04", f"throughput atendido · {contexto}", fmt(atendidas, 2, "req/s"), f"≥ {fmt(minimo_req, 2)} req/s",
             _res(atendidas >= minimo_req), fmt(len(pet)), f"ofrecido por el modelo: {fmt(ofrecidas, 2)} req/s (M-08)"),
        Fila("U-04", f"sesiones completadas por minuto · {contexto}", fmt(por_min, 1, "/min"),
             f"≥ {fmt(llegada)}/min (98 %: ≥ {minimo_sesiones:.0f})", _res(None if math.isnan(por_min) else por_min >= minimo_sesiones),
             fmt(len(completas)), "S-04: misma tolerancia del 98 % que el throughput"),
    ]


def filas_retrasos(c: Corrida, contexto: str) -> list[Fila]:
    descartadas = c.otras.loc[c.otras["metrica"] == "dropped_iterations", "valor"].sum()
    v, _ = tabla_ventanas(c, VENTANA_U05_S * c.perfil.escala)   # 1 min (comprimida en un ensayo)
    v = v[v["fase"] == "estable"]
    fuera = v[(v["p95_consulta"] >= UMBRAL_CONSULTA_MS) | (v["p95_dinero"] >= UMBRAL_DINERO_MS)]
    l_min, l_max = v["L_medida"].min(), v["L_medida"].max()
    rango = rango_concurrencia(c.perfil)
    rango_ok = None if v["L_medida"].isna().all() else bool(l_min >= rango[0] and l_max <= rango[1])
    peor = (f"peor ventana: consulta {fmt(v['p95_consulta'].max(), 0, 'ms')}, dinero {fmt(v['p95_dinero'].max(), 0, 'ms')}")
    return [
        Fila("U-05", "(a) sesiones descartadas (dropped_iterations), toda la corrida", fmt(descartadas),
             f"= {DESCARTADAS_MAX}", _res(descartadas <= DESCARTADAS_MAX)),
        Fila("U-05", f"(b) ventanas de 1 min con p95 sobre U-01/U-02 · {contexto}", f"{len(fuera)} de {len(v)}", "0",
             _res(None if v.empty else fuera.empty), nota=peor),
        Fila("U-05", f"(c) sesiones simultáneas por ventana de 1 min · {contexto}", f"{fmt(l_min, 1)} a {fmt(l_max, 1)}",
             f"{fmt(rango[0])}–{fmt(rango[1])}", _res(rango_ok), nota=f"Ley de Little: L = λ·W = {fmt(c.perfil.simultaneos)} (M-03)"),
    ]


# ---------- integridad del dinero (U-07) ----------
def fila_dinero(c: Corrida) -> list[Fila]:
    descuadres, como = leer_verificacion(c.carpeta / "verificacion_dinero.txt")
    sin_respuesta = c.otras.loc[c.otras["metrica"] == "dinero_sin_respuesta", "valor"].sum()
    return [Fila("U-07", "descuadres en C1–C6 (verificacion_dinero.txt)", fmt(descuadres), "= 0",
                 _res(None if descuadres is None else descuadres == 0), nota=como),
            Fila("U-07", "operaciones de dinero sin respuesta (status 0)", fmt(sin_respuesta), "se concilian en C6",
                 INFO, decide=False)]


# ---------- por escenario ----------
def filas_hora_punta(c: Corrida) -> list[Fila]:
    """Carga y resistencia: U-01 a U-05 en la fase estable (diseño §4.4)."""
    estable = c.mascara(c.pet, "fase", ("estable",))
    filas = filas_tiempos(c, estable, "fase estable", UMBRAL_CONSULTA_MS, UMBRAL_DINERO_MS)
    filas.append(fila_error(c, "fase", ("estable",), "fase estable"))
    return filas + filas_volumen(c, "fase", ("estable",), "fase estable") + filas_retrasos(c, "fase estable")


def filas_pico(c: Corrida) -> list[Fila]:
    """U-06: campaña con límites 2× (S-05), error ≤ 1 %, descartadas = 0 y recuperación a U-01/U-02."""
    campana = c.mascara(c.pet, "campana", ("si",))
    filas = filas_tiempos(c, campana, "campaña", UMBRAL_CONSULTA_CAMPANA_MS, UMBRAL_DINERO_CAMPANA_MS, "U-06", "U-06",
                          nota="S-05: 2 × el umbral normal")
    filas.append(fila_error(c, "campana", ("si",), "campaña", "U-06"))
    tramo = intervalo_campana(c.perfil) or (0, c.duracion)
    drop = c.otras[(c.otras["metrica"] == "dropped_iterations") & (c.otras["t"] >= tramo[0]) & (c.otras["t"] < tramo[1])]
    filas.append(Fila("U-06", "sesiones descartadas · campaña", fmt(drop["valor"].sum()), "= 0", _res(drop["valor"].sum() == 0)))
    recuperacion = c.mascara(c.pet, "fase", ("recuperacion",))
    filas += [f for f in filas_tiempos(c, recuperacion, "recuperación 12:10–12:15", UMBRAL_CONSULTA_MS, UMBRAL_DINERO_MS,
                                       "U-06", "U-06", nota="recuperación: se vuelve a cumplir U-01/U-02")]
    # S-05: el resultado de la campaña frente a los umbrales normales, por si el negocio renegocia (no decide)
    filas += filas_tiempos(c, campana, "campaña frente al umbral normal", UMBRAL_CONSULTA_MS, UMBRAL_DINERO_MS,
                           decide=False, nota="S-05: informativo")
    filas += filas_tiempos(c, c.mascara(c.pet, "fase", ("base",)), "base 11:58–12:00", UMBRAL_CONSULTA_MS,
                           UMBRAL_DINERO_MS, decide=False, nota="informativo: hora punta antes del salto")
    return filas


def filas_estres(c: Corrida, v: pd.DataFrame) -> tuple[list[Fila], dict]:
    cap = capacidad(v, c.perfil.escala)
    if cap["limite_alcanzado"]:
        detalle = (f"última ventana que cumple: min {fmt(cap['minuto_ultima_ok'], 1)} con {fmt(cap['L_ultima_ok'])} simultáneos; "
                   f"primera falla sostenida: min {fmt(cap['minuto_falla'], 1)} con {fmt(cap['L_falla'])} ({cap['motivo_falla']})")
        medido = f"{fmt(cap['capacidad'])} usuarios simultáneos"
    else:
        detalle = f"no hubo falla sostenida hasta {fmt(cap['L_max'])} simultáneos: el límite está más arriba"
        medido = f"≥ {fmt(cap['capacidad'])} usuarios simultáneos"
    filas = [Fila("U-08", "capacidad (S-10: ventanas de 30 s, 2 fallas seguidas, redondeo a 50)", medido, "se mide", MEDIDO,
                  nota=detalle),
             Fila("U-08", "tolerancia de throughput por ventana (S-04 en 30 s)", fmt(cap["tolerancia"] * 100, 1, "%"),
                  "máx(2 %, 3 σ de la fase base)", INFO, decide=False),
             Fila("U-08", "hipótesis previa (§8)", "1,500 ± 300", "se valida o se refuta", INFO, decide=False,
                  nota="H1: CPU por el PBKDF2 del login")]
    return filas + [fila_error(c, "fase", ("rampa", "meseta"), "rampa y meseta", decide=False)], cap


def filas_resistencia(c: Corrida, v: pd.DataFrame) -> tuple[list[Fila], dict]:
    """U-09 (a) a (d)."""
    ventanas = v[v["fase"] == "estable"]
    malas = ventanas[(ventanas["p95_consulta"] >= UMBRAL_CONSULTA_MS) | (ventanas["p95_dinero"] >= UMBRAL_DINERO_MS)
                     | (ventanas["error_ops"] > ERROR_MAX)]
    filas = [Fila("U-09", "(a) ventanas de 5 min que no cumplen U-01 a U-03", f"{len(malas)} de {len(ventanas)}", "0",
                  _res(None if ventanas.empty else malas.empty))]
    pr = proyecciones(c)
    if "memoria" in pr:
        m = pr["memoria"]
        filas.append(Fila("U-09", f"(b) memoria proyectada a {SESIONES_DIA:,} sesiones", fmt(m["proyeccion"], 0, "MB"),
                          f"< {RSS_MAX_MB} MB", _res(m["proyeccion"] < RSS_MAX_MB), fmt(m["sesiones_medidas"]),
                          f"{pr['fuente_memoria']}; pendiente {m['pendiente'] * 1000:.2f} MB por 1,000 sesiones, r² {m['r2']:.2f}"))
    else:
        filas.append(Fila("U-09", "(b) memoria proyectada", "—", f"< {RSS_MAX_MB} MB", SIN_DATO, nota="falta recursos_qolqe.csv"))
    for clave in ("hilos", "descriptores"):
        if clave in pr:
            h = pr[clave]
            limite = FACTOR_HILOS * h["inicial"]
            filas.append(Fila("U-09", f"(c) {clave} proyectados a {SESIONES_DIA:,} sesiones", fmt(h["proyeccion"], 1),
                              f"≤ {FACTOR_HILOS} × inicial ({fmt(limite, 1)})", _res(h["proyeccion"] <= limite),
                              nota=f"inicial {fmt(h['inicial'], 1)}, final {fmt(h['final'], 1)}"))
        else:
            filas.append(Fila("U-09", f"(c) {clave} proyectados", "—", f"≤ {FACTOR_HILOS} × inicial", SIN_DATO))
    for grupo, (p_ini, p_fin, razon) in pr["deriva"].items():
        filas.append(Fila("U-09", f"(d) deriva del p95 {grupo}: últimos 10 min ÷ primeros 10 min", fmt(razon, 2, "×"),
                          f"≤ {FACTOR_DERIVA} ×", _res(None if math.isnan(razon) else razon <= FACTOR_DERIVA),
                          nota=f"{fmt(p_ini, 0, 'ms')} → {fmt(p_fin, 0, 'ms')}"))
    return filas, pr


def filas_demo(c: Corrida) -> list[Fila]:
    filas = []
    for escenario_k6, esperado in (("demo_hora_punta", True), ("demo_sin_pausa", False)):
        m = c.mascara(c.pet, "scenario", (escenario_k6,))
        nota = "" if esperado else "estrés disfrazado (S13): se espera que falle"
        filas += filas_tiempos(c, m, escenario_k6, UMBRAL_CONSULTA_MS, UMBRAL_DINERO_MS, decide=esperado, nota=nota)
        filas.append(fila_error(c, "scenario", (escenario_k6,), escenario_k6, decide=esperado))
    return filas


def calibrar(c: Corrida) -> dict | None:
    """M-14: D_sesión = Δusage_usec ÷ sesiones → L_sat = W ÷ D → TOP = ⌈1.33 × L_sat⌉ a la centena."""
    antes, despues = c.meta.get("cpu_stat_antes") or {}, c.meta.get("cpu_stat_despues") or {}
    if "usage_usec" not in antes or "usage_usec" not in despues:
        return None
    sesiones = (c.meta.get("calibracion") or {}).get("sesiones") or len(c.sesiones) or SESIONES_CALIBRACION
    d = (float(despues["usage_usec"]) - float(antes["usage_usec"])) / 1e6 / sesiones
    l_sat = DURACION_SESION_S / d
    return {"sesiones": sesiones, "D_sesion_s": d, "L_sat": l_sat, "TOP": math.ceil(FACTOR_TOP * l_sat / 100) * 100}


def filas_calibracion(cal: dict | None) -> list[Fila]:
    if cal is None:
        return [Fila("M-14", "D_sesión (CPU por sesión)", "—", "se mide", SIN_DATO, nota="faltan cpu_stat_antes/despues en corrida.json")]
    return [Fila("M-14", "D_sesión (s de CPU por sesión)", f"{cal['D_sesion_s'] * 1000:.1f} ms", "se mide", MEDIDO, fmt(cal["sesiones"])),
            Fila("M-14", "L_sat = W ÷ D", fmt(cal["L_sat"]), "se calcula", MEDIDO),
            Fila("M-14", "TOP para el estrés", fmt(cal["TOP"]), "⌈1.33 × L_sat⌉ a la centena", MEDIDO,
                 nota=f"TOP={cal['TOP']} correr.sh estres")]


def d_sesion(c: Corrida) -> float:
    """D_sesión en s (de la propia corrida o de corrida.json); NaN si no hay datos."""
    for fuente in (c.meta.get("parametros") or {}, c.meta.get("calibracion") or {}, c.meta):
        for clave in ("D_sesion_s", "d_sesion_s"):
            if fuente.get(clave):
                return float(fuente[clave])
    return math.nan


# ---------- validez (V-01 a V-07) ----------
def mezcla_lograda(c: Corrida, etiqueta, valores) -> pd.DataFrame:
    """V-03: % de cada operación de la mezcla (sin login) frente al pedido (M-06)."""
    ops = c.otras[(c.otras["metrica"] == "operacion_fallida") & c.mascara(c.otras, etiqueta, valores)]
    if len(ops) and (ops["op"] != "").any():
        conteo = ops[ops["op"] != OP_LOGIN].groupby("op").size()
    else:   # respaldo: peticiones de la operación ÷ peticiones por operación (M-07)
        pet = c.pet[c.mascara(c.pet, etiqueta, valores)]
        conteo = pet.groupby("op").size() / pet.groupby("op").size().index.map(lambda o: REQ_POR_OPERACION.get(o, 1)).to_numpy()
        conteo = conteo.drop(OP_LOGIN, errors="ignore")
    total = conteo.sum()
    pedida = dict(MEZCLA)
    if "otras" in conteo.index:   # k6/operaciones.js etiqueta las 5 "otras" con op=otras: se comparan juntas (5 × 2 %)
        pedida = {op: p for op, p in MEZCLA.items() if op not in EP_OTRAS} | {"otras": sum(MEZCLA[op] for op in EP_OTRAS)}
    filas = [{"operacion": op, "pedida_%": p, "lograda_%": 100 * conteo.get(op, 0) / total if total else math.nan}
             for op, p in pedida.items()]
    tabla = pd.DataFrame(filas)
    tabla["diferencia_pp"] = tabla["lograda_%"] - tabla["pedida_%"]
    return tabla


def filas_validez(c: Corrida, v: pd.DataFrame) -> list[Fila]:
    titulo, etiqueta, valores = c.perfil.medidas[0]
    filas = []
    # V-01: CPU de k6 (÷ núcleos) y del equipo < 80 % en todas las ventanas
    cols = [col for col in ("cpu_k6_equipo", "cpu_equipo") if col in v]
    if cols:
        peor = float(np.nanmax(v[cols].to_numpy()))
        pico = max(float(np.nanmax(v[f"{col}_max"])) for col in cols if f"{col}_max" in v)
        filas.append(Fila("V-01", "CPU de k6 y del equipo (máximo de las ventanas)", fmt(peor, 1, "%"), f"< {CPU_GENERADOR_MAX} %",
                          _res(peor < CPU_GENERADOR_MAX), nota=f"pico de 1 s: {fmt(pico, 1)} %"))
    else:
        filas.append(Fila("V-01", "CPU de k6 y del equipo", "—", f"< {CPU_GENERADOR_MAX} %", SIN_DATO, nota="falta recursos_k6.csv"))
    # V-02: errores de datos (4xx de negocio) separados de los de rendimiento
    en = c.mascara(c.otras, etiqueta, valores)
    por_op = c.otras[(c.otras["metrica"] == "operacion_error_datos") & en]
    if len(por_op):   # k6: operacion_error_datos, una muestra por operación (como U-03)
        n_datos, tasa = int(por_op["valor"].sum()), float(por_op["valor"].mean())
    else:
        ops = c.otras[(c.otras["metrica"] == "operacion_fallida") & en]
        datos = c.otras[(c.otras["metrica"] == "errores_datos") & en]
        n_datos = datos["valor"].sum() if len(datos) else int(c.pet[c.mascara(c.pet, etiqueta, valores)]["error_datos"].sum())
        base = len(ops) or int(c.mascara(c.pet, etiqueta, valores).sum())
        tasa = n_datos / base if base else math.nan
    filas.append(Fila("V-02", f"errores de datos · {titulo}", f"{fmt(n_datos)} ({fmt(tasa * 100, 2)} %)",
                      f"= 0 (repetir si > {fmt(ERRORES_DATOS_MAX * 100, 1)} %)", _res(None if math.isnan(tasa) else tasa <= ERRORES_DATOS_MAX),
                      nota="" if n_datos == 0 else "revisar el generador de datos"))
    # V-03: mezcla
    if c.escenario not in ("referencia", "calibracion"):
        mezcla = mezcla_lograda(c, etiqueta, valores)
        peor = float(mezcla["diferencia_pp"].abs().max())
        corta = c.escenario == "demo"   # con ~80 sesiones el azar de la mezcla supera ± 2 pp: solo informa
        filas.append(Fila("V-03", f"mezcla lograda · {titulo} (peor operación)", fmt(peor, 2, "pp"), f"± {MEZCLA_TOLERANCIA_PP} pp",
                          _res(None if math.isnan(peor) else peor <= MEZCLA_TOLERANCIA_PP), decide=not corta,
                          nota="informativo: la demo es demasiado corta" if corta else ""))
    # V-04 y V-05: los registra correr.sh en corrida.json
    carga = c.meta.get("carga_equipo_antes", c.meta.get("carga_inicial"))
    ocioso = c.meta.get("cpu_ocioso_antes")
    if ocioso is not None:   # README §4: la carga de 1 min no baja de ~3-4 en esta Mac; decide el CPU ocioso
        filas.append(Fila("V-04", "CPU ocioso del equipo antes de empezar (top, 3 s)", fmt(ocioso, 1, "%"),
                          f"≥ {OCIOSO_EQUIPO_MIN} %", _res(float(ocioso) >= OCIOSO_EQUIPO_MIN),
                          nota=f"carga de 1 min: {fmt(carga, 2)} (diseño < {CARGA_EQUIPO_MAX}; solo se registra)"))
    else:
        filas.append(Fila("V-04", "carga promedio de 1 min antes de empezar", fmt(carga, 2), f"< {CARGA_EQUIPO_MAX}",
                          _res(None if carga is None else float(carga) < CARGA_EQUIPO_MAX)))
    identica, cpu_max = c.meta.get("base_identica"), c.meta.get("cpu_max")
    cpus = (c.meta.get("parametros") or {}).get("CPUS", "1")
    esperado = f"{round(float(cpus) * 100000)} 100000"   # escalabilidad (CPUS=2): 200000 100000
    ok5 = None if identica is None and cpu_max is None else bool(identica in (True, None) and cpu_max in (esperado, None))
    filas.append(Fila("V-05", "base restaurada idéntica y cpu.max del contenedor", f"base {identica}, cpu.max {cpu_max}",
                      f"base idéntica y {esperado}", _res(ok5)))
    # V-06: solo en la referencia de 1 VU
    if c.escenario == "referencia":
        for ep, d in c.pet.groupby("ep"):
            limite = UMBRAL_DINERO_MS if (d["grupo"] == "dinero").any() else UMBRAL_CONSULTA_MS
            p = percentil(d["dur"])
            filas.append(Fila("V-06", f"p95 `{ep}` con 1 VU", fmt(p, 0, "ms"), f"≤ {fmt(REFERENCIA_FRACCION * limite)} ms",
                              _res(p <= REFERENCIA_FRACCION * limite), fmt(len(d))))
    # V-07
    decide = c.escenario in ("carga", "resistencia", "capacidad")
    filas.append(Fila("V-07", "avisos de k6 'Insufficient VUs'", fmt(c.avisos_vus), "0",
                      _res(None if c.avisos_vus is None else c.avisos_vus == 0), decide=decide,
                      nota="" if decide else "solo decide en carga y resistencia"))
    return filas


def filas_entorno(c: Corrida) -> list[Fila]:
    """Informativo: conexión (§2.1) y throttling del cgroup (§6.3)."""
    filas = [Fila("§2.1", "p95 de http_req_connecting", fmt(c.conexion_p95, 1, "ms"), "≤ 10 ms (si no, se suma)", INFO,
                  nota="se sumó al tiempo de respuesta" if c.conexion_sumada else "no se suma", decide=False)]
    antes, despues = c.meta.get("cpu_stat_antes") or {}, c.meta.get("cpu_stat_despues") or {}
    if "nr_throttled" in antes and "nr_throttled" in despues:
        delta = float(despues["nr_throttled"]) - float(antes["nr_throttled"])
        usec = float(despues.get("throttled_usec", 0)) - float(antes.get("throttled_usec", 0))
        filas.append(Fila("§6.3", "throttling del cgroup en la corrida", f"{fmt(delta)} períodos, {fmt(usec / 1e6, 1)} s",
                          "diagnóstico (H1)", INFO, decide=False))
    return filas


def resumen_por_umbral(c: Corrida, detalle: list[Fila]) -> list[Fila]:
    """Una fila por umbral U-01 a U-09: FALLA si alguna fila que decide falla."""
    salida = []
    aplica = APLICA.get(c.escenario, set())
    for uid, requisito in REQUISITO.items():
        filas = [f for f in detalle if f.id == uid and f.decide]
        if uid not in aplica:
            salida.append(Fila(uid, requisito, "—", "—", NO_APLICA, nota=f"se evalúa en {DONDE[uid]}"))
            continue
        if not filas:
            salida.append(Fila(uid, requisito, "—", "—", SIN_DATO))
            continue
        resultados = {f.resultado for f in filas}
        # FALLA si algo falla; SIN DATO si falta medir algún criterio (no se da por cumplido lo que no se midió)
        resultado = (MEDIDO if MEDIDO in resultados else FALLA if FALLA in resultados
                     else SIN_DATO if SIN_DATO in resultados else PASA)
        clave = next((f for f in filas if f.resultado == FALLA), None) or next((f for f in filas if f.resultado == SIN_DATO), filas[0])
        fallan = sum(f.resultado == FALLA for f in filas)
        plural = "criterio" if len(filas) == 1 else "criterios"
        faltan = sum(f.resultado == SIN_DATO for f in filas)
        nota = (clave.nota if resultado == MEDIDO else
                f"{fallan} de {len(filas)} {plural} fallan; el primero: {clave.criterio}" if fallan
                else f"falta medir {faltan} de {len(filas)}: {clave.criterio}" if faltan
                else f"{len(filas)} {plural} (ver detalle)")
        salida.append(Fila(uid, requisito, clave.medido, clave.umbral, resultado, nota=nota))
    return salida


def evaluar(c: Corrida, v: pd.DataFrame) -> dict:
    """Devuelve {'validez', 'umbrales', 'detalle', 'mezcla', 'extra'} para escribir el veredicto y los gráficos."""
    detalle, extra = [], {}
    if c.escenario in ("carga", "resistencia", "capacidad"):
        detalle += filas_hora_punta(c)
    if c.escenario == "resistencia":
        filas, extra["proyecciones"] = filas_resistencia(c, v)
        detalle += filas
    if c.escenario == "pico":
        detalle += filas_pico(c)
    if c.escenario == "estres":
        filas, extra["capacidad"] = filas_estres(c, v)
        detalle += filas
    if c.escenario == "demo":
        detalle += filas_demo(c)
    if c.escenario == "calibracion":
        extra["calibracion"] = calibrar(c)
        detalle += filas_calibracion(extra["calibracion"])
    if c.escenario == "referencia":
        detalle += filas_tiempos(c, c.mascara(c.pet, None, None), "1 VU", UMBRAL_CONSULTA_MS, UMBRAL_DINERO_MS, decide=False,
                                 nota="referencia (no decide)")
    if c.escenario in APLICA:
        detalle += fila_dinero(c)
    detalle += filas_entorno(c)
    _, etiqueta, valores = c.perfil.medidas[0]
    mezcla = mezcla_lograda(c, etiqueta, valores) if c.escenario not in ("referencia", "calibracion") else None
    return {"validez": filas_validez(c, v), "umbrales": resumen_por_umbral(c, detalle), "detalle": detalle,
            "mezcla": mezcla, "extra": extra}
