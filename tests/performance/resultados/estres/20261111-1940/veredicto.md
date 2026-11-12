# Veredicto · estres · 20261111-1940

- Inicio: 2026-11-11 19:40:31 · fin: 2026-11-11 19:56:23 (hora de Lima) · primera petición: 2026-11-11 19:40:36
- Duración con muestras: 15.8 min · peticiones: 31,424 · sesiones: 3,993
- Código de salida de k6: 99 (0 = todos los umbrales de k6 pasan; 99 = alguno falla)
- **Corrida válida** según V-01 a V-07

## 1. Validez de la corrida (V-01 a V-07)

| ID | Criterio | Medido | Umbral | Resultado | Nota |
|---|---|---|---|---|---|
| V-01 | CPU del generador k6 (% del equipo, máximo de las ventanas) | 1.2 % | < 80 % | ✓ PASA | pico de 1 s: 7.9 % del equipo (79 % de un núcleo) |
| V-01 | CPU total del equipo (máximo de las ventanas) | 82.3 % | < 80 % | ✗ FALLA | informativo: lo mueven procesos de macOS; ventanas ≥ 80 % en el minuto 2.2 |
| V-02 | errores de datos · rampa y meseta | 0 (0.00 %) | = 0 (repetir si > 0.1 %) | ✓ PASA |  |
| V-03 | mezcla lograda · rampa y meseta (peor operación) | 0.94 pp | ± 2 pp | ✓ PASA |  |
| V-04 | CPU ocioso del equipo antes de empezar (top, 3 s) | 80.3 % | ≥ 65 % | ✓ PASA | carga de 1 min: 5.05 (diseño < 1.5; solo se registra) |
| V-05 | base restaurada idéntica y cpu.max del contenedor | base True, cpu.max 100000 100000 | base idéntica y 100000 100000 | ✓ PASA |  |
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
| U-08 | Hasta cuántos usuarios simultáneos podemos crecer | 850 usuarios simultáneos | se mide | MEDIDO | última ventana que cumple: min 11.8 con 876 simultáneos; primera falla sostenida: min 12.2 con 946 (p95 consulta < 800 ms (U-01); p95 dinero < 1,500 ms (U-02); error ≤ 1 % (U-03); atendido ≥ 90% de lo ofrecido (U-04); p95 login < 800 ms; p95 saldo < 800 ms; p95 movimientos < 800 ms; p95 transferir < 1,500 ms; p95 recargar < 1,500 ms) |
| U-09 | Opera de 6:00 a 24:00 sin reinicios | — | — | NO APLICA | se evalúa en resistencia |

## 3. Detalle por grupo, endpoint y ventana

Las filas *informativas* no cambian el veredicto del umbral (por ejemplo, los endpoints de `otras` con < 100 muestras).

| ID | Criterio | Medido | Umbral | Resultado | n | Nota |
|---|---|---|---|---|---|---|
| U-08 | capacidad (S-10: ventanas de 30 s, 2 fallas seguidas, redondeo a 50) | 850 usuarios simultáneos | se mide | MEDIDO |  | última ventana que cumple: min 11.8 con 876 simultáneos; primera falla sostenida: min 12.2 con 946 (p95 consulta < 800 ms (U-01); p95 dinero < 1,500 ms (U-02); error ≤ 1 % (U-03); atendido ≥ 90% de lo ofrecido (U-04); p95 login < 800 ms; p95 saldo < 800 ms; p95 movimientos < 800 ms; p95 transferir < 1,500 ms; p95 recargar < 1,500 ms) |
| U-08 | tolerancia de throughput por ventana (S-04 en 30 s) | 9.7 % | máx(2 %, 3 σ de la fase base) | INFO |  |  |
| U-08 | hipótesis previa (§8) | 1,500 ± 300 | se valida o se refuta | INFO |  | H1: CPU por el PBKDF2 del login |
| U-03 | error de rendimiento · rampa y meseta | 20.81 % | ≤ 1 % | ✗ FALLA | 19,206 | operacion_fallida (una muestra por operación, S-06) |
| U-07 | descuadres en C1–C6 (verificacion_dinero.txt) | 0 | = 0 | ✓ PASA |  | línea TOTAL |
| U-07 | operaciones de dinero sin respuesta (status 0) | 98 | se concilian en C6 | INFO |  |  |
| §2.1 | p95 de http_req_connecting | 0.6 ms | ≤ 10 ms (si no, se suma) | INFO |  | no se suma |
| §6.3 | throttling del cgroup en la corrida | 525 períodos, 63.5 s | diagnóstico (H1) | INFO |  |  |

## 4. Mezcla lograda (V-03, M-06)

| Operación | Pedida (%) | Lograda (%) | Diferencia (pp) |
|---|---|---|---|
| saldo_perfil | 30.0 | 29.1 | -0.94 |
| movimientos | 15.0 | 15.4 | 0.39 |
| transferir | 15.0 | 15.2 | 0.17 |
| contactos | 10.0 | 10.1 | 0.14 |
| recarga | 10.0 | 10.2 | 0.18 |
| deudas | 6.0 | 6.0 | 0.04 |
| pago | 4.0 | 4.0 | 0.00 |
| otras | 10.0 | 10.0 | 0.02 |

## 5. Errores de rendimiento y de datos, por separado (toda la corrida)

| Clase | Tipo o código | Cantidad |
|---|---|---|
| rendimiento (U-03) | http_5xx | 116 |
| rendimiento (U-03) | timeout | 4,762 |

## 6. Umbrales evaluados por k6 (resumen.json; ✓ cumple, ✗ falla, ○ sin muestras)

| Umbral | Métrica | Condición | Medido por k6 | k6 |
|---|---|---|---|---|
| red de seguridad: corta si falla más del 20 % | `operacion_fallida` | `rate<0.2` | 20.05 % | ✗ |
