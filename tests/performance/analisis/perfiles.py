"""Perfil de cada escenario: tasa de llegada programada, fases y subconjuntos que se miden.

Repite lo que hace k6/escenarios.js (diseño §4.2) para poder dibujar la carga *ofrecida* y sombrear las fases.
Los segundos se cuentan desde el inicio del escenario (la primera petición de la corrida).
"""
from dataclasses import dataclass, replace

import numpy as np
from config import (
    CONCURRENCIA_RANGO,
    DURACION_SESION_S,
    LLEGADA_POR_MIN,
    OPERACIONES_POR_SESION,
    PAUSA_MEDIA_S,
    REQ_POR_OPERACION_MEDIA,
    TOP_HIPOTESIS,
    VENTANA_S,
)


@dataclass(frozen=True)
class Perfil:
    escenario: str
    ventana_s: int
    tasa_inicial: float | None   # sesiones/min al empezar (None = no es modelo abierto)
    etapas: tuple                # ((duración_s, objetivo_sesiones_min), …) como las stages de k6
    fases: tuple                 # ((nombre, inicio_s, fin_s), …); fin None = hasta el final
    medidas: tuple               # ((título, etiqueta, valores), …): qué peticiones entran al veredicto
    inicio_medicion_s: float = 0  # las ventanas se alinean con el inicio de la fase medida
    escala: float = 1.0          # ensayo comprimido (-e ESCALA de k6/escenarios.js); 1 = el diseño tal cual

    @property
    def duracion_sesion_s(self) -> float:   # W (M-02), comprimido en un ensayo
        return DURACION_SESION_S * self.escala

    @property
    def pausa_media_s(self) -> float:       # M-04, comprimida en un ensayo
        return PAUSA_MEDIA_S * self.escala

    @property
    def simultaneos(self) -> float:         # Little: L = λ·W (M-03); 100 en hora punta, L_cap en capacidad
        return (self.tasa_inicial or LLEGADA_POR_MIN) / 60 * self.duracion_sesion_s


def perfil(escenario: str, top: float | None = None, l_cap: float | None = None, escala: float = 1.0) -> Perfil:
    """Perfil del diseño; con escala < 1 se comprimen duraciones, fases y ventanas como en k6/escenarios.js (ESCALA)."""
    p = _perfil(escenario, top, l_cap)
    if escala == 1:
        return p
    return replace(p, ventana_s=p.ventana_s * escala, etapas=tuple((d * escala, obj) for d, obj in p.etapas),
                   fases=tuple((n, i * escala, None if f is None else f * escala) for n, i, f in p.fases),
                   inicio_medicion_s=p.inicio_medicion_s * escala, escala=escala)


def _perfil(escenario: str, top: float | None, l_cap: float | None) -> Perfil:
    top = top or TOP_HIPOTESIS
    v = VENTANA_S.get(escenario, 60)
    estable = (("estable", "fase", ("estable",)),)
    if escenario == "carga":
        # M-01: 50 sesiones/min durante 17 min (M-12); M-24: 120 s de calentamiento fuera del veredicto
        return Perfil(escenario, v, LLEGADA_POR_MIN, ((1020, LLEGADA_POR_MIN),),
                      (("calentamiento", 0, 120), ("estable", 120, 1020), ("drenaje", 1020, None)), estable, 120)
    if escenario == "resistencia":
        # M-13: 60 min estables + 2 de calentamiento
        return Perfil(escenario, v, LLEGADA_POR_MIN, ((3720, LLEGADA_POR_MIN),),
                      (("calentamiento", 0, 120), ("estable", 120, 3720), ("drenaje", 3720, None)), estable, 120)
    if escenario == "capacidad" and l_cap:
        # §10.2 Opc. 2: 10 min estables a L_cap simultáneos; Little: λ = L_cap / W (M-02)
        tasa = round(l_cap / (DURACION_SESION_S / 60))
        return Perfil(escenario, v, tasa, ((720, tasa),),
                      (("calentamiento", 0, 120), ("estable", 120, 720), ("drenaje", 720, None)), estable, 120)
    if escenario == "pico":
        # M-09/M-10/M-11: base 4 min, salto ×3 en 30 s, 150/min hasta 12:05, vuelta a 50/min hasta 12:15
        etapas = ((240, 50), (30, 150), (270, 150), (30, 50), (570, 50))
        fases = (("calentamiento", 0, 120), ("base", 120, 240), ("salto", 240, 540), ("resto", 540, 840),
                 ("recuperacion", 840, 1140), ("drenaje", 1140, None))
        medidas = (("campaña", "campana", ("si",)), ("base", "fase", ("base",)), ("recuperación", "fase", ("recuperacion",)))
        return Perfil(escenario, v, LLEGADA_POR_MIN, etapas, fases, medidas, 0)
    if escenario == "estres":
        # M-14: base 3 min a 50/min, rampa de 23 min hasta TOP/2 por min (TOP simultáneos), meseta de 2 min
        etapas = ((180, 50), (1380, top / 2), (120, top / 2))
        fases = (("base", 0, 180), ("rampa", 180, 1560), ("meseta", 1560, 1680), ("drenaje", 1680, None))
        return Perfil(escenario, v, LLEGADA_POR_MIN, etapas, fases, (("rampa y meseta", "fase", ("rampa", "meseta")),), 0)
    if escenario == "demo":
        # §9: 100 s de hora punta (modelo abierto) y 45 s con 50 VUs sin pausa (modelo cerrado: no hay tasa ofrecida)
        fases = (("hora punta", 0, 100), ("sin pausa", 100, 145), ("fin", 145, None))
        medidas = (("demo_hora_punta", "scenario", ("demo_hora_punta",)), ("demo_sin_pausa", "scenario", ("demo_sin_pausa",)))
        return Perfil(escenario, v, LLEGADA_POR_MIN, ((100, LLEGADA_POR_MIN),), fases, medidas, 0)
    # referencia y calibración: 1 VU con iteraciones fijas (no hay tasa de llegada)
    return Perfil(escenario, v, None, (), (("1 VU", 0, None),), (("toda la corrida", None, None),), 0)


def rango_concurrencia(p: Perfil) -> tuple[float, float]:
    """U-05(c): 100 ± 10 % simultáneos; en capacidad, L_cap ± 10 %; en un ensayo comprimido, L·escala ± 10 %."""
    factor = p.simultaneos / 100
    return CONCURRENCIA_RANGO[0] * factor, CONCURRENCIA_RANGO[1] * factor


def tasa_llegada(p: Perfil, t: np.ndarray) -> np.ndarray:
    """Sesiones por segundo programadas en cada instante t (s). Fuera de las etapas vale 0."""
    t = np.asarray(t, dtype=float)
    if p.tasa_inicial is None or not p.etapas:
        return np.full_like(t, np.nan)
    xs, ys = [0.0], [p.tasa_inicial]
    for duracion, objetivo in p.etapas:
        xs.append(xs[-1] + duracion)
        ys.append(objetivo)
    tasa = np.interp(t, xs, ys) / 60
    tasa[(t < 0) | (t > xs[-1])] = 0
    return tasa


def peticiones_ofrecidas(p: Perfil, t: np.ndarray) -> np.ndarray:
    """req/s que la carga programada debería generar en t.

    Cada sesión hace el login al llegar (1 petición) y luego 6 operaciones separadas por la pausa media
    (M-04), con 1.79 peticiones por operación (M-08). Con una tasa constante da λ × 11.74 = 9.78 req/s.
    """
    t = np.asarray(t, dtype=float)
    q = tasa_llegada(p, t)
    for k in range(1, OPERACIONES_POR_SESION + 1):
        q = q + REQ_POR_OPERACION_MEDIA * tasa_llegada(p, t - k * p.pausa_media_s)
    return q


def simultaneos_esperados(p: Perfil, t: np.ndarray, paso: float = 1.0) -> np.ndarray:
    """Ley de Little en el tiempo: sesiones que llegaron en los últimos W = 120 s (M-02, M-03; × escala en un ensayo)."""
    t = np.asarray(t, dtype=float)
    if p.tasa_inicial is None:
        return np.full_like(t, np.nan)
    w = p.duracion_sesion_s
    paso = min(paso, w / 20)   # en un ensayo comprimido W puede ser de pocos segundos
    rejilla = np.arange(-w, max(t.max(initial=0), 0) + paso, paso)
    acumulado = np.cumsum(tasa_llegada(p, rejilla)) * paso
    return np.interp(t, rejilla, acumulado) - np.interp(t - w, rejilla, acumulado)


def fase_en(p: Perfil, t: np.ndarray) -> np.ndarray:
    """Nombre de la fase programada en cada t (para los datos que no traen la etiqueta fase)."""
    t = np.asarray(t, dtype=float)
    salida = np.full(t.shape, p.fases[-1][0], dtype=object)
    for nombre, ini, fin in p.fases:
        dentro = (t >= ini) if fin is None else (t >= ini) & (t < fin)
        salida[dentro] = nombre
    return salida


def intervalo_fase(p: Perfil, nombres: tuple) -> tuple[float, float] | None:
    """(inicio, fin) en segundos que cubren las fases dadas, o None si no hay ninguna."""
    tramos = [(ini, fin) for nombre, ini, fin in p.fases if nombre in nombres and fin is not None]
    if not tramos:
        return None
    return min(i for i, _ in tramos), max(f for _, f in tramos)


def intervalo_campana(p: Perfil) -> tuple[float, float] | None:
    """Pico: la campaña va de 12:00 a 12:15, es decir, de salto a recuperacion (diseño §4.2)."""
    return intervalo_fase(p, ("salto", "resto", "recuperacion")) if p.escenario == "pico" else None
