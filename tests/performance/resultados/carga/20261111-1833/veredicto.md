# Veredicto · carga · 20261111-1833

- Inicio: 2026-11-11 18:33:22 · fin: 2026-11-11 18:52:32 (hora de Lima) · primera petición: 2026-11-11 18:33:26
- Duración con muestras: 19.1 min · peticiones: 9,975 · sesiones: 850
- Código de salida de k6: 0 (0 = todos los umbrales de k6 pasan; 99 = alguno falla)
- **Corrida válida** según V-01 a V-07

## 1. Validez de la corrida (V-01 a V-07)

| ID | Criterio | Medido | Umbral | Resultado | Nota |
|---|---|---|---|---|---|
| V-01 | CPU del generador k6 (% del equipo, máximo de las ventanas) | 0.3 % | < 80 % | ✓ PASA | pico de 1 s: 1.4 % del equipo (14 % de un núcleo) |
| V-01 | CPU total del equipo (máximo de las ventanas) | 60.9 % | < 80 % | ✓ PASA | informativo: lo mueven procesos de macOS; ninguna ventana ≥ 80 % |
| V-02 | errores de datos · estable | 0 (0.00 %) | = 0 (repetir si > 0.1 %) | ✓ PASA |  |
| V-03 | mezcla lograda · estable (peor operación) | 0.78 pp | ± 2 pp | ✓ PASA |  |
| V-04 | CPU ocioso del equipo antes de empezar (top, 3 s) | 81.5 % | ≥ 65 % | ✓ PASA | carga de 1 min: 4.23 (diseño < 1.5; solo se registra) |
| V-05 | base restaurada idéntica y cpu.max del contenedor | base True, cpu.max 100000 100000 | base idéntica y 100000 100000 | ✓ PASA |  |
| V-07 | avisos de k6 'Insufficient VUs' | 0 | 0 | ✓ PASA |  |

## 2. Umbrales (U-01 a U-09)

| ID | Criterio | Medido | Umbral | Resultado | Nota |
|---|---|---|---|---|---|
| U-01 | Consultas e inicio de sesión: el 95 % en menos de 800 ms | 93 ms | < 800 ms | ✓ PASA | 12 criterios (ver detalle) |
| U-02 | Operaciones de dinero: el 95 % en menos de 1.5 s | 128 ms | < 1,500 ms | ✓ PASA | 4 criterios (ver detalle) |
| U-03 | En hora punta, no más del 1 % de operaciones fallidas | 0.00 % | ≤ 1 % | ✓ PASA | 1 criterio (ver detalle) |
| U-04 | Sostener el volumen de la hora punta | 9.77 req/s | ≥ 9.60 req/s | ✓ PASA | 2 criterios (ver detalle) |
| U-05 | …sin acumular retrasos | 0 | = 0 | ✓ PASA | 3 criterios (ver detalle) |
| U-06 | Campaña: degradación razonable del servicio | — | — | NO APLICA | se evalúa en pico |
| U-07 | Ninguna operación de dinero a medias ni aplicada dos veces | 0 | = 0 | ✓ PASA | 1 criterio (ver detalle) |
| U-08 | Hasta cuántos usuarios simultáneos podemos crecer | — | — | NO APLICA | se evalúa en estrés |
| U-09 | Opera de 6:00 a 24:00 sin reinicios | — | — | NO APLICA | se evalúa en resistencia |

## 3. Detalle por grupo, endpoint y ventana

Las filas *informativas* no cambian el veredicto del umbral (por ejemplo, los endpoints de `otras` con < 100 muestras).

| ID | Criterio | Medido | Umbral | Resultado | n | Nota |
|---|---|---|---|---|---|---|
| U-01 | p95 grupo consulta · fase estable | 93 ms | < 800 ms | ✓ PASA | 7,516 | lectura literal (S-03) |
| U-02 | p95 grupo dinero · fase estable | 128 ms | < 1,500 ms | ✓ PASA | 1,280 | lectura literal (S-03) |
| U-01 | p95 grupo otras · fase estable | 12 ms | < 800 ms | ✓ PASA | 433 | lectura literal (S-03) |
| U-01 | p95 `alertas` (GET /api/limites/alertas) · fase estable | 12 ms | < 800 ms | ✓ PASA | 89 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `comision` (GET /api/transferencias/comision) · fase estable | 12 ms | < 800 ms | ✓ PASA | 639 | por endpoint (S-03) |
| U-01 | p95 `contactos_buscar` (GET /api/contactos?buscar) · fase estable | 8 ms | < 800 ms | ✓ PASA | 483 | por endpoint (S-03) |
| U-01 | p95 `contactos_listar` (GET /api/contactos) · fase estable | 14 ms | < 800 ms | ✓ PASA | 483 | por endpoint (S-03) |
| U-01 | p95 `deudas` (GET /api/servicios/deudas) · fase estable | 7 ms | < 800 ms | ✓ PASA | 449 | por endpoint (S-03) |
| U-01 | p95 `dispositivos` (GET /api/seguridad/dispositivos) · fase estable | 12 ms | < 800 ms | ✓ PASA | 94 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `empresas` (GET /api/servicios/empresas) · fase estable | 12 ms | < 800 ms | ✓ PASA | 449 | por endpoint (S-03) |
| U-01 | p95 `limites` (GET /api/limites) · fase estable | 12 ms | < 800 ms | ✓ PASA | 83 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `login` (POST /api/auth/login) · fase estable | 105 ms | < 800 ms | ✓ PASA | 750 | por endpoint (S-03) |
| U-01 | p95 `movimientos` (GET /api/movimientos) · fase estable | 38 ms | < 800 ms | ✓ PASA | 689 | por endpoint (S-03) |
| U-02 | p95 `pagar` (POST /api/servicios/pagos) · fase estable | 12 ms | < 1,500 ms | ✓ PASA | 178 | por endpoint (S-03) |
| U-01 | p95 `perfil` (GET /api/cuentas/me) · fase estable | 6 ms | < 800 ms | ✓ PASA | 1,339 | por endpoint (S-03) |
| U-02 | p95 `recargar` (POST /api/recargas) · fase estable | 13 ms | < 1,500 ms | ✓ PASA | 463 | por endpoint (S-03) |
| U-01 | p95 `recargas_config` (GET /api/recargas/configuracion) · fase estable | 9 ms | < 800 ms | ✓ PASA | 463 | por endpoint (S-03) |
| U-01 | p95 `saldo` (GET /api/cuentas/me/saldo) · fase estable | 13 ms | < 800 ms | ✓ PASA | 1,339 | por endpoint (S-03) |
| U-01 | p95 `sesiones` (GET /api/seguridad/sesiones) · fase estable | 12 ms | < 800 ms | ✓ PASA | 84 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `solicitudes` (GET /api/solicitudes) · fase estable | 12 ms | < 800 ms | ✓ PASA | 83 | informativo: el veredicto es el grupo otras (§3.3) |
| U-02 | p95 `transferir` (POST /api/transferencias) · fase estable | 134 ms | < 1,500 ms | ✓ PASA | 639 | por endpoint (S-03) |
| U-03 | error de rendimiento · fase estable | 0.00 % | ≤ 1 % | ✓ PASA | 5,245 | operacion_fallida (una muestra por operación, S-06) |
| U-04 | throughput atendido · fase estable | 9.77 req/s | ≥ 9.60 req/s | ✓ PASA | 8,796 | ofrecido por el modelo: 9.78 req/s (M-08) |
| U-04 | sesiones completadas por minuto · fase estable | 49.6 /min | ≥ 50/min (98 %: ≥ 49) | ✓ PASA | 744 | S-04: misma tolerancia del 98 % que el throughput |
| U-05 | (a) sesiones descartadas (dropped_iterations), toda la corrida | 0 | = 0 | ✓ PASA |  |  |
| U-05 | (b) ventanas de 1 min con p95 sobre U-01/U-02 · fase estable | 0 de 15 | 0 | ✓ PASA |  | peor ventana: consulta 101 ms, dinero 141 ms |
| U-05 | (c) sesiones simultáneas por ventana de 1 min · fase estable | 98.8 a 101.0 | 90–110 | ✓ PASA |  | Ley de Little: L = λ·W = 100 (M-03) |
| U-07 | descuadres en C1–C6 (verificacion_dinero.txt) | 0 | = 0 | ✓ PASA |  | línea TOTAL |
| U-07 | operaciones de dinero sin respuesta (status 0) | 0 | se concilian en C6 | INFO |  |  |
| §2.1 | p95 de http_req_connecting | 1.3 ms | ≤ 10 ms (si no, se suma) | INFO |  | no se suma |
| §6.3 | throttling del cgroup en la corrida | 2 períodos, 0.0 s | diagnóstico (H1) | INFO |  |  |

## 4. Mezcla lograda (V-03, M-06)

| Operación | Pedida (%) | Lograda (%) | Diferencia (pp) |
|---|---|---|---|
| saldo_perfil | 30.0 | 29.8 | -0.21 |
| movimientos | 15.0 | 15.3 | 0.33 |
| transferir | 15.0 | 14.2 | -0.78 |
| contactos | 10.0 | 10.7 | 0.75 |
| recarga | 10.0 | 10.3 | 0.30 |
| deudas | 6.0 | 6.0 | 0.03 |
| pago | 4.0 | 4.0 | -0.04 |
| otras | 10.0 | 9.6 | -0.37 |

## 5. Errores de rendimiento y de datos, por separado (toda la corrida)

| Clase | Tipo o código | Cantidad |
|---|---|---|
| — | sin errores | 0 |

## 6. Umbrales evaluados por k6 (resumen.json; ✓ cumple, ✗ falla, ○ sin muestras)

| Umbral | Métrica | Condición | Medido por k6 | k6 |
|---|---|---|---|---|
| U-01 consultas e inicio de sesión (grupo) | `http_req_duration{fase:estable,grupo:consulta}` | `p(95)<800` | 93.2 ms | ✓ |
| U-01 login (S-03) | `http_req_duration{fase:estable,ep:login}` | `p(95)<800` | 104.8 ms | ✓ |
| U-01 saldo (S-03) | `http_req_duration{fase:estable,ep:saldo}` | `p(95)<800` | 12.7 ms | ✓ |
| U-01 perfil (S-03) | `http_req_duration{fase:estable,ep:perfil}` | `p(95)<800` | 5.8 ms | ✓ |
| U-01 movimientos (S-03) | `http_req_duration{fase:estable,ep:movimientos}` | `p(95)<800` | 37.9 ms | ✓ |
| U-01 comision (S-03) | `http_req_duration{fase:estable,ep:comision}` | `p(95)<800` | 12.4 ms | ✓ |
| U-01 contactos_listar (S-03) | `http_req_duration{fase:estable,ep:contactos_listar}` | `p(95)<800` | 14.4 ms | ✓ |
| U-01 contactos_buscar (S-03) | `http_req_duration{fase:estable,ep:contactos_buscar}` | `p(95)<800` | 7.5 ms | ✓ |
| U-01 recargas_config (S-03) | `http_req_duration{fase:estable,ep:recargas_config}` | `p(95)<800` | 9.3 ms | ✓ |
| U-01 empresas (S-03) | `http_req_duration{fase:estable,ep:empresas}` | `p(95)<800` | 12.4 ms | ✓ |
| U-01 deudas (S-03) | `http_req_duration{fase:estable,ep:deudas}` | `p(95)<800` | 7.4 ms | ✓ |
| U-01 otras: 5 GET al 2 % (§3.3) | `http_req_duration{fase:estable,op:otras}` | `p(95)<800` | 12.2 ms | ✓ |
| U-02 operaciones de dinero (grupo) | `http_req_duration{fase:estable,grupo:dinero}` | `p(95)<1500` | 128.2 ms | ✓ |
| U-02 transferir (S-03) | `http_req_duration{fase:estable,ep:transferir}` | `p(95)<1500` | 134.2 ms | ✓ |
| U-02 recargar (S-03) | `http_req_duration{fase:estable,ep:recargar}` | `p(95)<1500` | 13.3 ms | ✓ |
| U-02 pagar (S-03) | `http_req_duration{fase:estable,ep:pagar}` | `p(95)<1500` | 11.5 ms | ✓ |
| U-03 operaciones fallidas (S-06) | `operacion_fallida{fase:estable}` | `rate<=0.01` | 0.00 % | ✓ |
| U-04 throughput ≥ 9.6 req/s | `http_reqs{fase:estable,expected_response:true}` | `count>=8640` | 8796 | ✓ |
| U-05a sesiones descartadas | `dropped_iterations` | `count==0` | 0 | ✓ |
