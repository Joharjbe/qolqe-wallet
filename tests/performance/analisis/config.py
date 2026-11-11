"""Valores del análisis. Cada uno lleva el ID del diseño del que sale.

IDs: U = umbral, S = supuesto, M = valor del modelo de carga, V = criterio de validez de una corrida.
Si cambia el requerimiento, se cambia aquí y nada más.
"""

# --- Umbrales (diseño §2.1) ---
PERCENTIL = 95                    # U-01/U-02: "el 95 % debe responder en menos de…"
UMBRAL_CONSULTA_MS = 800          # U-01: "Consultas e inicio de sesión: … menos de 800 ms"
UMBRAL_DINERO_MS = 1500           # U-02: "Operaciones de dinero …: … menos de 1.5 segundos"
ERROR_MAX = 0.01                  # U-03: "no más del 1 % de las operaciones puede fallar"
SESIONES_MIN_POR_MIN = 50         # U-04: ≥ 50 sesiones/min (3,000/h, M-01)
FRACCION_ATENDIDA = 0.98          # U-04 y S-04: se atiende ≥ 98 % de lo ofrecido
REQ_S_MIN = 9.6                   # U-04: 98 % de los 9.78 req/s ofrecidos (M-08)
DESCARTADAS_MAX = 0               # U-05(a): dropped_iterations = 0
CONCURRENCIA_RANGO = (90, 110)    # U-05(c): 100 ± 10 % sesiones simultáneas por ventana de 1 min
VENTANA_U05_S = 60                # U-05(b, c): "p95 por ventana de 1 min"
FACTOR_CAMPANA = 2                # S-05 / U-06: "degradación razonable" = hasta 2 × el umbral normal
UMBRAL_CONSULTA_CAMPANA_MS = UMBRAL_CONSULTA_MS * FACTOR_CAMPANA   # U-06: 1,600 ms
UMBRAL_DINERO_CAMPANA_MS = UMBRAL_DINERO_MS * FACTOR_CAMPANA       # U-06: 3,000 ms
REDONDEO_CAPACIDAD = 50           # S-10: la capacidad se redondea hacia abajo a 50
FALLAS_SEGUIDAS = 2               # S-10: "primera falla sostenida (2 ventanas seguidas)"
VENTANA_SIGMAS = 3                # S-04 en ventanas de 30 s (estrés): tolerancia = máx(2 %, 3 σ de atendido/ofrecido en la fase base)
MUESTRAS_MIN_ENDPOINT = 20        # S-03 en ventanas cortas: con < 20 muestras el p95 de un endpoint no decide (solo el del grupo)
SESIONES_DIA = 54_000             # S-11 / M-13: 18 h × 3,000 sesiones
RSS_MAX_MB = 700                  # U-09(b): 70 % de 1 GB (criterio de memoria de S13)
FACTOR_HILOS = 2                  # U-09(c): proyección ≤ 2 × el valor inicial
FACTOR_DERIVA = 1.2               # U-09(d): p95 últimos 10 min ≤ 1.2 × p95 primeros 10 min
MINUTOS_DERIVA = 10               # U-09(d)
CONEXION_P95_MAX_MS = 10          # §2.1: si el p95 de http_req_connecting pasa de 10 ms, se suma al tiempo de respuesta
TIMEOUT_MS = 30_000               # S-06: timeout del cliente (30 s) = error de rendimiento

# --- Criterios de validez (diseño §2.3) ---
CPU_GENERADOR_MAX = 80            # V-01: CPU de k6 y del equipo < 80 % (enunciado §5)
ERRORES_DATOS_MAX = 0.001         # V-02: errores de datos > 0.1 % de las operaciones → repetir la corrida
MEZCLA_TOLERANCIA_PP = 2          # V-03: mezcla lograda a ± 2 puntos porcentuales
CARGA_EQUIPO_MAX = 1.5            # V-04 del diseño: carga de 1 min < 1.5 (en esta Mac no se alcanza: solo se informa)
OCIOSO_EQUIPO_MIN = 65            # V-04 que decide: CPU ocioso del equipo (top, 3 s) ≥ 65 % antes de empezar
CPU_MAX_ESPERADO = "100000 100000"  # V-05: cpu.max del contenedor = 1 CPU
REFERENCIA_FRACCION = 0.10        # V-06: con 1 VU, p95 de cada endpoint ≤ 10 % de su umbral

# --- Modelo de carga (diseño §3.2) ---
LLEGADA_POR_MIN = 50              # M-01: 3,000 sesiones/h = 50 sesiones/min
DURACION_SESION_S = 120           # M-02: W = 120 s
SIMULTANEOS = 100                 # M-03: L = λ·W = 100
PAUSA_MEDIA_S = 18                # M-04: pausa triangular(10, 19, 25), media 18 s
OPERACIONES_POR_SESION = 6        # M-06: login + 6 operaciones
REQ_POR_OPERACION_MEDIA = 1.79    # M-08: peticiones promedio por operación de la mezcla
REQ_POR_SESION = 1 + OPERACIONES_POR_SESION * REQ_POR_OPERACION_MEDIA   # M-08: 11.74
SESIONES_CALIBRACION = 40         # §4.2: la calibración mide 40 sesiones
FACTOR_TOP = 1.33                 # M-14: L_top = ⌈1.33 × L_sat⌉ a la centena
TOP_HIPOTESIS = 2400              # M-14: hipótesis de L_top mientras no haya calibración

# M-06: mezcla de operaciones (porcentaje de las 6 operaciones de cada sesión)
MEZCLA = {
    "saldo_perfil": 30, "movimientos": 15, "transferir": 15, "contactos": 10, "recarga": 10,
    "deudas": 6, "pago": 4, "limites": 2, "alertas": 2, "solicitudes": 2, "dispositivos": 2, "sesiones": 2,
}
OP_LOGIN = "login"                # F-01: una por sesión, fuera de la mezcla
# M-07: peticiones por operación (para estimar la mezcla si falta la métrica operacion_fallida)
REQ_POR_OPERACION = {
    "login": 1, "saldo_perfil": 2, "movimientos": 1, "transferir": 2, "contactos": 2, "recarga": 2,
    "deudas": 2, "pago": 3, "limites": 1, "alertas": 1, "solicitudes": 1, "dispositivos": 1, "sesiones": 1,
}

# --- Endpoints (etiqueta ep de k6, diseño §4.4) ---
EP_DINERO = ["transferir", "recargar", "pagar"]                         # U-02 (S-02: solo los POST de dinero)
EP_OTRAS = ["limites", "alertas", "solicitudes", "dispositivos", "sesiones"]   # §3.3: veredicto por el grupo "otras"
EP_CONSULTA = ["login", "saldo", "perfil", "movimientos", "comision", "contactos_listar", "contactos_buscar",
               "recargas_config", "empresas", "deudas", *EP_OTRAS]      # U-01 (S-02: toda GET + login)
# Endpoints críticos que se dibujan (F-01 a F-06)
EP_CRITICOS = {"consulta": ["login", "saldo", "movimientos"], "dinero": ["transferir", "recargar", "pagar"]}

# --- Ventanas de análisis (diseño §7.2) ---
VENTANA_S = {"carga": 60, "pico": 30, "estres": 30, "resistencia": 300, "capacidad": 60,
             "demo": 10, "referencia": 30, "calibracion": 30}
