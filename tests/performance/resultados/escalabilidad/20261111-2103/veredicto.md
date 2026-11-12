# Veredicto · estres · 20261111-2103

- Inicio: 2026-11-11 21:03:10 · fin: 2026-11-11 21:25:21 (hora de Lima) · primera petición: 2026-11-11 21:03:16
- Duración con muestras: 22.1 min · peticiones: 66,246 · sesiones: 9,312
- Código de salida de k6: 99 (0 = todos los umbrales de k6 pasan; 99 = alguno falla)
- **Corrida válida** según V-01 a V-07

## 1. Validez de la corrida (V-01 a V-07)

| ID | Criterio | Medido | Umbral | Resultado | Nota |
|---|---|---|---|---|---|
| V-01 | CPU del generador k6 (% del equipo, máximo de las ventanas) | 1.7 % | < 80 % | ✓ PASA | pico de 1 s: 12.2 % del equipo (122 % de un núcleo) |
| V-01 | CPU total del equipo (máximo de las ventanas) | 42.6 % | < 80 % | ✓ PASA | informativo: lo mueven procesos de macOS; ninguna ventana ≥ 80 % |
| V-02 | errores de datos · rampa y meseta | 0 (0.00 %) | = 0 (repetir si > 0.1 %) | ✓ PASA |  |
| V-03 | mezcla lograda · rampa y meseta (peor operación) | 0.31 pp | ± 2 pp | ✓ PASA |  |
| V-04 | CPU ocioso del equipo antes de empezar (top, 3 s) | 93.3 % | ≥ 65 % | ✓ PASA | carga de 1 min: 5.73 (diseño < 1.5; solo se registra) |
| V-05 | base restaurada idéntica y cpu.max del contenedor | base True, cpu.max 200000 100000 | base idéntica y 200000 100000 | ✓ PASA |  |
| V-07 | avisos de k6 'Insufficient VUs' | 0 | 0 | ✓ PASA | solo decide en carga y resistencia |

## 2. Umbrales (U-01 a U-09)

| ID | Criterio | Medido | Umbral | Resultado | Nota |
|---|---|---|---|---|---|
| U-01 | Consultas e inicio de sesión: el 95 % en menos de 800 ms | — | — | NO APLICA | se evalúa en carga y resistencia |
| U-02 | Operaciones de dinero: el 95 % en menos de 1.5 s | — | — | NO APLICA | se evalúa en carga y resistencia |
| U-03 | En hora punta, no más del 1 % de operaciones fallidas | — | — | NO APLICA | se evalúa en carga y resistencia |
| U-04 | Sostener el volumen de la hora punta | — | — | NO APLICA | se evalúa en carga y resistencia |
| U-05 | …sin acumular retrasos | — | — | NO APLICA | se evalúa en carga y resistencia |
| U-06 | Campaña: degradación razonable del servicio | — | — | NO APLICA | se evalúa en pico |
| U-07 | Ninguna operación de dinero a medias ni aplicada dos veces | 0 | = 0 | ✓ PASA | 1 criterio (ver detalle) |
| U-08 | Hasta cuántos usuarios simultáneos podemos crecer | 1,300 usuarios simultáneos | se mide | MEDIDO | última ventana que cumple: min 16.2 con 1,337 simultáneos; primera falla sostenida: min 16.8 con 1,417 (p95 consulta < 800 ms (U-01); p95 dinero < 1,500 ms (U-02); error ≤ 1 % (U-03); atendido ≥ 89% de lo ofrecido (U-04); p95 login < 800 ms; p95 saldo < 800 ms; p95 movimientos < 800 ms; p95 transferir < 1,500 ms; p95 recargar < 1,500 ms) |
| U-09 | Opera de 6:00 a 24:00 sin reinicios | — | — | NO APLICA | se evalúa en resistencia |

## 3. Detalle por grupo, endpoint y ventana

Las filas *informativas* no cambian el veredicto del umbral (por ejemplo, los endpoints de `otras` con < 100 muestras).

| ID | Criterio | Medido | Umbral | Resultado | n | Nota |
|---|---|---|---|---|---|---|
| U-08 | capacidad (S-10: ventanas de 30 s, 2 fallas seguidas, redondeo a 50) | 1,300 usuarios simultáneos | se mide | MEDIDO |  | última ventana que cumple: min 16.2 con 1,337 simultáneos; primera falla sostenida: min 16.8 con 1,417 (p95 consulta < 800 ms (U-01); p95 dinero < 1,500 ms (U-02); error ≤ 1 % (U-03); atendido ≥ 89% de lo ofrecido (U-04); p95 login < 800 ms; p95 saldo < 800 ms; p95 movimientos < 800 ms; p95 transferir < 1,500 ms; p95 recargar < 1,500 ms) |
| U-08 | tolerancia de throughput por ventana (S-04 en 30 s) | 10.6 % | máx(2 %, 3 σ de la fase base) | INFO |  |  |
| U-08 | hipótesis previa (§8) | 1,500 ± 300 | se valida o se refuta | INFO |  | H1: CPU por el PBKDF2 del login |
| U-03 | error de rendimiento · rampa y meseta | 20.37 % | ≤ 1 % | ✗ FALLA | 41,334 | operacion_fallida (una muestra por operación, S-06) |
| U-07 | descuadres en C1–C6 (verificacion_dinero.txt) | 0 | = 0 | ✓ PASA |  | línea TOTAL |
| U-07 | operaciones de dinero sin respuesta (status 0) | 75 | se concilian en C6 | INFO |  |  |
| §2.1 | p95 de http_req_connecting | 0.6 ms | ≤ 10 ms (si no, se suma) | INFO |  | no se suma |
| §6.3 | throttling del cgroup en la corrida | 217 períodos, 26.6 s | diagnóstico (H1) | INFO |  |  |

## 4. Mezcla lograda (V-03, M-06)

| Operación | Pedida (%) | Lograda (%) | Diferencia (pp) |
|---|---|---|---|
| saldo_perfil | 30.0 | 30.2 | 0.23 |
| movimientos | 15.0 | 14.7 | -0.27 |
| transferir | 15.0 | 15.3 | 0.31 |
| contactos | 10.0 | 9.7 | -0.29 |
| recarga | 10.0 | 9.8 | -0.21 |
| deudas | 6.0 | 6.1 | 0.11 |
| pago | 4.0 | 4.0 | -0.00 |
| otras | 10.0 | 10.1 | 0.11 |

## 5. Errores de rendimiento y de datos, por separado (toda la corrida)

| Clase | Tipo o código | Cantidad |
|---|---|---|
| rendimiento (U-03) | http_5xx | 120 |
| rendimiento (U-03) | timeout | 9,960 |

## 6. Umbrales evaluados por k6 (resumen.json; ✓ cumple, ✗ falla, ○ sin muestras)

| Umbral | Métrica | Condición | Medido por k6 | k6 |
|---|---|---|---|---|
| red de seguridad: corta si falla más del 20 % | `operacion_fallida` | `rate<0.2` | 20.02 % | ✗ |
