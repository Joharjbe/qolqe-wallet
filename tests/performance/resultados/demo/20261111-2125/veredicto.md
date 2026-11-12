# Veredicto · demo · 20261111-2125

- Inicio: 2026-11-11 21:26:03 · fin: 2026-11-11 21:28:32 (hora de Lima) · primera petición: 2026-11-11 21:26:07
- Duración con muestras: 2.4 min · peticiones: 1,189 · sesiones: 208
- Código de salida de k6: 99 (0 = todos los umbrales de k6 pasan; 99 = alguno falla)
- **Corrida válida** según V-01 a V-07

## 1. Validez de la corrida (V-01 a V-07)

| ID | Criterio | Medido | Umbral | Resultado | Nota |
|---|---|---|---|---|---|
| V-01 | CPU del generador k6 (% del equipo, máximo de las ventanas) | 0.5 % | < 80 % | ✓ PASA | pico de 1 s: 1.2 % del equipo (12 % de un núcleo) |
| V-01 | CPU total del equipo (máximo de las ventanas) | 28.1 % | < 80 % | ✓ PASA | informativo: lo mueven procesos de macOS; ninguna ventana ≥ 80 % |
| V-02 | errores de datos · demo_hora_punta | 0 (0.00 %) | = 0 (repetir si > 0.1 %) | ✓ PASA |  |
| V-03 | mezcla lograda · demo_hora_punta (peor operación) | 9.27 pp | ± 2 pp | ✗ FALLA | informativo: la demo es demasiado corta |
| V-04 | CPU ocioso del equipo antes de empezar (top, 3 s) | 90.4 % | ≥ 65 % | ✓ PASA | carga de 1 min: 6.80 (diseño < 1.5; solo se registra) |
| V-05 | base restaurada idéntica y cpu.max del contenedor | base True, cpu.max 100000 100000 | base idéntica y 100000 100000 | ✓ PASA |  |
| V-07 | avisos de k6 'Insufficient VUs' | 0 | 0 | ✓ PASA | solo decide en carga y resistencia |

## 2. Umbrales (U-01 a U-09)

| ID | Criterio | Medido | Umbral | Resultado | Nota |
|---|---|---|---|---|---|
| U-01 | Consultas e inicio de sesión: el 95 % en menos de 800 ms | 103 ms | < 800 ms | ✓ PASA | 12 criterios (ver detalle) |
| U-02 | Operaciones de dinero: el 95 % en menos de 1.5 s | 138 ms | < 1,500 ms | ✓ PASA | 4 criterios (ver detalle) |
| U-03 | En hora punta, no más del 1 % de operaciones fallidas | 0.00 % | ≤ 1 % | ✓ PASA | 1 criterio (ver detalle) |
| U-04 | Sostener el volumen de la hora punta | — | — | NO APLICA | se evalúa en carga y resistencia |
| U-05 | …sin acumular retrasos | — | — | NO APLICA | se evalúa en carga y resistencia |
| U-06 | Campaña: degradación razonable del servicio | — | — | NO APLICA | se evalúa en pico |
| U-07 | Ninguna operación de dinero a medias ni aplicada dos veces | 0 | = 0 | ✓ PASA | 1 criterio (ver detalle) |
| U-08 | Hasta cuántos usuarios simultáneos podemos crecer | — | — | NO APLICA | se evalúa en estrés |
| U-09 | Opera de 6:00 a 24:00 sin reinicios | — | — | NO APLICA | se evalúa en resistencia |

## 3. Detalle por grupo, endpoint y ventana

Las filas *informativas* no cambian el veredicto del umbral (por ejemplo, los endpoints de `otras` con < 100 muestras).

| ID | Criterio | Medido | Umbral | Resultado | n | Nota |
|---|---|---|---|---|---|---|
| U-01 | p95 grupo consulta · demo_hora_punta | 103 ms | < 800 ms | ✓ PASA | 387 | lectura literal (S-03) |
| U-02 | p95 grupo dinero · demo_hora_punta | 138 ms | < 1,500 ms | ✓ PASA | 43 | lectura literal (S-03) |
| U-01 | p95 grupo otras · demo_hora_punta | 11 ms | < 800 ms | ✓ PASA | 16 | lectura literal (S-03) |
| U-01 | p95 `alertas` (GET /api/limites/alertas) · demo_hora_punta | 9 ms | < 800 ms | ✓ PASA | 4 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `comision` (GET /api/transferencias/comision) · demo_hora_punta | 10 ms | < 800 ms | ✓ PASA | 21 | por endpoint (S-03) |
| U-01 | p95 `contactos_buscar` (GET /api/contactos?buscar) · demo_hora_punta | 6 ms | < 800 ms | ✓ PASA | 37 | por endpoint (S-03) |
| U-01 | p95 `contactos_listar` (GET /api/contactos) · demo_hora_punta | 12 ms | < 800 ms | ✓ PASA | 37 | por endpoint (S-03) |
| U-01 | p95 `deudas` (GET /api/servicios/deudas) · demo_hora_punta | 6 ms | < 800 ms | ✓ PASA | 18 | por endpoint (S-03) |
| U-01 | p95 `dispositivos` (GET /api/seguridad/dispositivos) · demo_hora_punta | 11 ms | < 800 ms | ✓ PASA | 5 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `empresas` (GET /api/servicios/empresas) · demo_hora_punta | 10 ms | < 800 ms | ✓ PASA | 18 | por endpoint (S-03) |
| U-01 | p95 `limites` (GET /api/limites) · demo_hora_punta | 10 ms | < 800 ms | ✓ PASA | 1 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `login` (POST /api/auth/login) · demo_hora_punta | 106 ms | < 800 ms | ✓ PASA | 84 | por endpoint (S-03) |
| U-01 | p95 `movimientos` (GET /api/movimientos) · demo_hora_punta | 37 ms | < 800 ms | ✓ PASA | 31 | por endpoint (S-03) |
| U-02 | p95 `pagar` (POST /api/servicios/pagos) · demo_hora_punta | 11 ms | < 1,500 ms | ✓ PASA | 9 | por endpoint (S-03) |
| U-01 | p95 `perfil` (GET /api/cuentas/me) · demo_hora_punta | 4 ms | < 800 ms | ✓ PASA | 56 | por endpoint (S-03) |
| U-02 | p95 `recargar` (POST /api/recargas) · demo_hora_punta | 13 ms | < 1,500 ms | ✓ PASA | 13 | por endpoint (S-03) |
| U-01 | p95 `recargas_config` (GET /api/recargas/configuracion) · demo_hora_punta | 8 ms | < 800 ms | ✓ PASA | 13 | por endpoint (S-03) |
| U-01 | p95 `saldo` (GET /api/cuentas/me/saldo) · demo_hora_punta | 13 ms | < 800 ms | ✓ PASA | 56 | por endpoint (S-03) |
| U-01 | p95 `sesiones` (GET /api/seguridad/sesiones) · demo_hora_punta | 9 ms | < 800 ms | ✓ PASA | 5 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `solicitudes` (GET /api/solicitudes) · demo_hora_punta | 10 ms | < 800 ms | ✓ PASA | 1 | informativo: el veredicto es el grupo otras (§3.3) |
| U-02 | p95 `transferir` (POST /api/transferencias) · demo_hora_punta | 138 ms | < 1,500 ms | ✓ PASA | 21 | por endpoint (S-03) |
| U-03 | error de rendimiento · demo_hora_punta | 0.00 % | ≤ 1 % | ✓ PASA | 276 | operacion_fallida (una muestra por operación, S-06) |
| U-01 | p95 grupo consulta · demo_sin_pausa | 15,689 ms | < 800 ms | ✗ FALLA | 689 | estrés disfrazado (S13): se espera que falle |
| U-02 | p95 grupo dinero · demo_sin_pausa | 11,713 ms | < 1,500 ms | ✗ FALLA | 70 | estrés disfrazado (S13): se espera que falle |
| U-01 | p95 grupo otras · demo_sin_pausa | 1,004 ms | < 800 ms | ✗ FALLA | 41 | estrés disfrazado (S13): se espera que falle |
| U-01 | p95 `alertas` (GET /api/limites/alertas) · demo_sin_pausa | 785 ms | < 800 ms | ✓ PASA | 9 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `comision` (GET /api/transferencias/comision) · demo_sin_pausa | 1,852 ms | < 800 ms | ✗ FALLA | 45 | estrés disfrazado (S13): se espera que falle |
| U-01 | p95 `contactos_buscar` (GET /api/contactos?buscar) · demo_sin_pausa | 2,852 ms | < 800 ms | ✗ FALLA | 26 | estrés disfrazado (S13): se espera que falle |
| U-01 | p95 `contactos_listar` (GET /api/contactos) · demo_sin_pausa | 1,999 ms | < 800 ms | ✗ FALLA | 27 | estrés disfrazado (S13): se espera que falle |
| U-01 | p95 `deudas` (GET /api/servicios/deudas) · demo_sin_pausa | 2,416 ms | < 800 ms | ✗ FALLA | 23 | estrés disfrazado (S13): se espera que falle |
| U-01 | p95 `dispositivos` (GET /api/seguridad/dispositivos) · demo_sin_pausa | 2,710 ms | < 800 ms | ✗ FALLA | 13 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `empresas` (GET /api/servicios/empresas) · demo_sin_pausa | 7,149 ms | < 800 ms | ✗ FALLA | 23 | estrés disfrazado (S13): se espera que falle |
| U-01 | p95 `limites` (GET /api/limites) · demo_sin_pausa | 881 ms | < 800 ms | ✗ FALLA | 7 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `login` (POST /api/auth/login) · demo_sin_pausa | 17,886 ms | < 800 ms | ✗ FALLA | 234 | estrés disfrazado (S13): se espera que falle |
| U-01 | p95 `movimientos` (GET /api/movimientos) · demo_sin_pausa | 3,396 ms | < 800 ms | ✗ FALLA | 33 | estrés disfrazado (S13): se espera que falle |
| U-02 | p95 `pagar` (POST /api/servicios/pagos) · demo_sin_pausa | 12,489 ms | < 1,500 ms | ✗ FALLA | 10 | estrés disfrazado (S13): se espera que falle |
| U-01 | p95 `perfil` (GET /api/cuentas/me) · demo_sin_pausa | 1,294 ms | < 800 ms | ✗ FALLA | 102 | estrés disfrazado (S13): se espera que falle |
| U-02 | p95 `recargar` (POST /api/recargas) · demo_sin_pausa | 12,125 ms | < 1,500 ms | ✗ FALLA | 25 | estrés disfrazado (S13): se espera que falle |
| U-01 | p95 `recargas_config` (GET /api/recargas/configuracion) · demo_sin_pausa | 1,407 ms | < 800 ms | ✗ FALLA | 32 | estrés disfrazado (S13): se espera que falle |
| U-01 | p95 `saldo` (GET /api/cuentas/me/saldo) · demo_sin_pausa | 1,618 ms | < 800 ms | ✗ FALLA | 103 | estrés disfrazado (S13): se espera que falle |
| U-01 | p95 `sesiones` (GET /api/seguridad/sesiones) · demo_sin_pausa | 1,735 ms | < 800 ms | ✗ FALLA | 6 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `solicitudes` (GET /api/solicitudes) · demo_sin_pausa | 1,004 ms | < 800 ms | ✗ FALLA | 6 | informativo: el veredicto es el grupo otras (§3.3) |
| U-02 | p95 `transferir` (POST /api/transferencias) · demo_sin_pausa | 11,098 ms | < 1,500 ms | ✗ FALLA | 35 | estrés disfrazado (S13): se espera que falle |
| U-03 | error de rendimiento · demo_sin_pausa | 35.07 % | ≤ 1 % | ✗ FALLA | 519 | operacion_fallida (una muestra por operación, S-06) |
| U-07 | descuadres en C1–C6 (verificacion_dinero.txt) | 0 | = 0 | ✓ PASA |  | línea TOTAL |
| U-07 | operaciones de dinero sin respuesta (status 0) | 0 | se concilian en C6 | INFO |  |  |
| §2.1 | p95 de http_req_connecting | 1.0 ms | ≤ 10 ms (si no, se suma) | INFO |  | no se suma |
| §6.3 | throttling del cgroup en la corrida | 225 períodos, 134.4 s | diagnóstico (H1) | INFO |  |  |

## 4. Mezcla lograda (V-03, M-06)

| Operación | Pedida (%) | Lograda (%) | Diferencia (pp) |
|---|---|---|---|
| saldo_perfil | 30.0 | 29.2 | -0.83 |
| movimientos | 15.0 | 16.1 | 1.15 |
| transferir | 15.0 | 10.9 | -4.06 |
| contactos | 10.0 | 19.3 | 9.27 |
| recarga | 10.0 | 6.8 | -3.23 |
| deudas | 6.0 | 4.7 | -1.31 |
| pago | 4.0 | 4.7 | 0.69 |
| otras | 10.0 | 8.3 | -1.67 |

## 5. Errores de rendimiento y de datos, por separado (toda la corrida)

| Clase | Tipo o código | Cantidad |
|---|---|---|
| rendimiento (U-03) | conexion | 81 |
| rendimiento (U-03) | http_5xx | 101 |

## 6. Umbrales evaluados por k6 (resumen.json; ✓ cumple, ✗ falla, ○ sin muestras)

| Umbral | Métrica | Condición | Medido por k6 | k6 |
|---|---|---|---|---|
| U-01 demo_hora_punta: consultas | `http_req_duration{scenario:demo_hora_punta,grupo:consulta}` | `p(95)<800` | 103.0 ms | ✓ |
| U-01 demo_hora_punta: login | `http_req_duration{scenario:demo_hora_punta,ep:login}` | `p(95)<800` | 105.7 ms | ✓ |
| U-02 demo_hora_punta: dinero | `http_req_duration{scenario:demo_hora_punta,grupo:dinero}` | `p(95)<1500` | 136.7 ms | ✓ |
| U-03 demo_hora_punta: operaciones fallidas | `operacion_fallida{scenario:demo_hora_punta}` | `rate<=0.01` | 0.00 % | ✓ |
| U-01 demo_sin_pausa: consultas | `http_req_duration{scenario:demo_sin_pausa,grupo:consulta}` | `p(95)<800` | 15647.8 ms | ✗ |
| U-01 demo_sin_pausa: login | `http_req_duration{scenario:demo_sin_pausa,ep:login}` | `p(95)<800` | 17857.7 ms | ✗ |
| U-02 demo_sin_pausa: dinero | `http_req_duration{scenario:demo_sin_pausa,grupo:dinero}` | `p(95)<1500` | 11522.3 ms | ✗ |
| U-03 demo_sin_pausa: operaciones fallidas | `operacion_fallida{scenario:demo_sin_pausa}` | `rate<=0.01` | 35.07 % | ✗ |
| U-05a demo_hora_punta: sesiones descartadas | `dropped_iterations{scenario:demo_hora_punta}` | `count==0` | 0 | ✓ |
