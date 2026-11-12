# Veredicto · referencia · 20261111-1826

- Inicio: 2026-11-11 18:27:02 · fin: 2026-11-11 18:28:08 (hora de Lima) · primera petición: 2026-11-11 18:27:06
- Duración con muestras: 1.0 min · peticiones: 100 · sesiones: 5
- Código de salida de k6: 99 (0 = todos los umbrales de k6 pasan; 99 = alguno falla)
- **Corrida NO válida: se repite y no se analiza (paso 1 de S14)** según V-01 a V-07

## 1. Validez de la corrida (V-01 a V-07)

| ID | Criterio | Medido | Umbral | Resultado | Nota |
|---|---|---|---|---|---|
| V-01 | CPU de k6 y del equipo (máximo de las ventanas) | 56.7 % | < 80 % | ✓ PASA | pico de 1 s: 98.1 % |
| V-02 | errores de datos · toda la corrida | 0 (0.00 %) | = 0 (repetir si > 0.1 %) | ✓ PASA |  |
| V-04 | CPU ocioso del equipo antes de empezar (top, 3 s) | 78.4 % | ≥ 65 % | ✓ PASA | carga de 1 min: 5.54 (diseño < 1.5; solo se registra) |
| V-05 | base restaurada idéntica y cpu.max del contenedor | base True, cpu.max 100000 100000 | base idéntica y 100000 100000 | ✓ PASA |  |
| V-06 | p95 `alertas` con 1 VU | 12 ms | ≤ 80 ms | ✓ PASA |  |
| V-06 | p95 `comision` con 1 VU | 12 ms | ≤ 80 ms | ✓ PASA |  |
| V-06 | p95 `contactos_buscar` con 1 VU | 5 ms | ≤ 80 ms | ✓ PASA |  |
| V-06 | p95 `contactos_listar` con 1 VU | 13 ms | ≤ 80 ms | ✓ PASA |  |
| V-06 | p95 `deudas` con 1 VU | 7 ms | ≤ 80 ms | ✓ PASA |  |
| V-06 | p95 `dispositivos` con 1 VU | 11 ms | ≤ 80 ms | ✓ PASA |  |
| V-06 | p95 `empresas` con 1 VU | 14 ms | ≤ 80 ms | ✓ PASA |  |
| V-06 | p95 `limites` con 1 VU | 15 ms | ≤ 80 ms | ✓ PASA |  |
| V-06 | p95 `login` con 1 VU | 94 ms | ≤ 80 ms | ✗ FALLA |  |
| V-06 | p95 `movimientos` con 1 VU | 91 ms | ≤ 80 ms | ✗ FALLA |  |
| V-06 | p95 `pagar` con 1 VU | 10 ms | ≤ 150 ms | ✓ PASA |  |
| V-06 | p95 `perfil` con 1 VU | 4 ms | ≤ 80 ms | ✓ PASA |  |
| V-06 | p95 `recargar` con 1 VU | 13 ms | ≤ 150 ms | ✓ PASA |  |
| V-06 | p95 `recargas_config` con 1 VU | 9 ms | ≤ 80 ms | ✓ PASA |  |
| V-06 | p95 `saldo` con 1 VU | 11 ms | ≤ 80 ms | ✓ PASA |  |
| V-06 | p95 `sesiones` con 1 VU | 15 ms | ≤ 80 ms | ✓ PASA |  |
| V-06 | p95 `solicitudes` con 1 VU | 12 ms | ≤ 80 ms | ✓ PASA |  |
| V-06 | p95 `transferir` con 1 VU | 127 ms | ≤ 150 ms | ✓ PASA |  |
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
| U-08 | Hasta cuántos usuarios simultáneos podemos crecer | — | — | NO APLICA | se evalúa en estrés |
| U-09 | Opera de 6:00 a 24:00 sin reinicios | — | — | NO APLICA | se evalúa en resistencia |

## 3. Detalle por grupo, endpoint y ventana

Las filas *informativas* no cambian el veredicto del umbral (por ejemplo, los endpoints de `otras` con < 100 muestras).

| ID | Criterio | Medido | Umbral | Resultado | n | Nota |
|---|---|---|---|---|---|---|
| U-01 | p95 grupo consulta · 1 VU | 72 ms | < 800 ms | ✓ PASA | 85 | referencia (no decide) |
| U-02 | p95 grupo dinero · 1 VU | 127 ms | < 1,500 ms | ✓ PASA | 15 | referencia (no decide) |
| U-01 | p95 grupo otras · 1 VU | 15 ms | < 800 ms | ✓ PASA | 25 | referencia (no decide) |
| U-01 | p95 `alertas` (GET /api/limites/alertas) · 1 VU | 12 ms | < 800 ms | ✓ PASA | 5 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `comision` (GET /api/transferencias/comision) · 1 VU | 12 ms | < 800 ms | ✓ PASA | 5 | referencia (no decide) |
| U-01 | p95 `contactos_buscar` (GET /api/contactos?buscar) · 1 VU | 5 ms | < 800 ms | ✓ PASA | 5 | referencia (no decide) |
| U-01 | p95 `contactos_listar` (GET /api/contactos) · 1 VU | 13 ms | < 800 ms | ✓ PASA | 5 | referencia (no decide) |
| U-01 | p95 `deudas` (GET /api/servicios/deudas) · 1 VU | 7 ms | < 800 ms | ✓ PASA | 10 | referencia (no decide) |
| U-01 | p95 `dispositivos` (GET /api/seguridad/dispositivos) · 1 VU | 11 ms | < 800 ms | ✓ PASA | 5 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `empresas` (GET /api/servicios/empresas) · 1 VU | 14 ms | < 800 ms | ✓ PASA | 10 | referencia (no decide) |
| U-01 | p95 `limites` (GET /api/limites) · 1 VU | 15 ms | < 800 ms | ✓ PASA | 5 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `login` (POST /api/auth/login) · 1 VU | 94 ms | < 800 ms | ✓ PASA | 5 | referencia (no decide) |
| U-01 | p95 `movimientos` (GET /api/movimientos) · 1 VU | 91 ms | < 800 ms | ✓ PASA | 5 | referencia (no decide) |
| U-02 | p95 `pagar` (POST /api/servicios/pagos) · 1 VU | 10 ms | < 1,500 ms | ✓ PASA | 5 | referencia (no decide) |
| U-01 | p95 `perfil` (GET /api/cuentas/me) · 1 VU | 4 ms | < 800 ms | ✓ PASA | 5 | referencia (no decide) |
| U-02 | p95 `recargar` (POST /api/recargas) · 1 VU | 13 ms | < 1,500 ms | ✓ PASA | 5 | referencia (no decide) |
| U-01 | p95 `recargas_config` (GET /api/recargas/configuracion) · 1 VU | 9 ms | < 800 ms | ✓ PASA | 5 | referencia (no decide) |
| U-01 | p95 `saldo` (GET /api/cuentas/me/saldo) · 1 VU | 11 ms | < 800 ms | ✓ PASA | 5 | referencia (no decide) |
| U-01 | p95 `sesiones` (GET /api/seguridad/sesiones) · 1 VU | 15 ms | < 800 ms | ✓ PASA | 5 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `solicitudes` (GET /api/solicitudes) · 1 VU | 12 ms | < 800 ms | ✓ PASA | 5 | informativo: el veredicto es el grupo otras (§3.3) |
| U-02 | p95 `transferir` (POST /api/transferencias) · 1 VU | 127 ms | < 1,500 ms | ✓ PASA | 5 | referencia (no decide) |
| U-07 | descuadres en C1–C6 (verificacion_dinero.txt) | 0 | = 0 | ✓ PASA |  | línea TOTAL |
| U-07 | operaciones de dinero sin respuesta (status 0) | 0 | se concilian en C6 | INFO |  |  |
| §2.1 | p95 de http_req_connecting | 0.0 ms | ≤ 10 ms (si no, se suma) | INFO |  | no se suma |
| §6.3 | throttling del cgroup en la corrida | 0 períodos, 0.0 s | diagnóstico (H1) | INFO |  |  |

## 5. Errores de rendimiento y de datos, por separado (toda la corrida)

| Clase | Tipo o código | Cantidad |
|---|---|---|
| — | sin errores | 0 |

## 6. Umbrales evaluados por k6 (resumen.json; ✓ cumple, ✗ falla, ○ sin muestras)

| Umbral | Métrica | Condición | Medido por k6 | k6 |
|---|---|---|---|---|
| validez: sin errores de rendimiento | `operacion_fallida` | `rate==0` | 0.00 % | ✓ |
| V-02 sin errores de datos | `errores_datos` | `count==0` | 0 | ✓ |
| V-06 login ≤ 10 % de U-01 | `http_req_duration{ep:login}` | `p(95)<=80` | 91.4 ms | ✗ |
| V-06 saldo ≤ 10 % de U-01 | `http_req_duration{ep:saldo}` | `p(95)<=80` | 10.9 ms | ✓ |
| V-06 perfil ≤ 10 % de U-01 | `http_req_duration{ep:perfil}` | `p(95)<=80` | 4.2 ms | ✓ |
| V-06 movimientos ≤ 10 % de U-01 | `http_req_duration{ep:movimientos}` | `p(95)<=80` | 79.1 ms | ✓ |
| V-06 comision ≤ 10 % de U-01 | `http_req_duration{ep:comision}` | `p(95)<=80` | 11.4 ms | ✓ |
| V-06 contactos_listar ≤ 10 % de U-01 | `http_req_duration{ep:contactos_listar}` | `p(95)<=80` | 12.6 ms | ✓ |
| V-06 contactos_buscar ≤ 10 % de U-01 | `http_req_duration{ep:contactos_buscar}` | `p(95)<=80` | 5.5 ms | ✓ |
| V-06 recargas_config ≤ 10 % de U-01 | `http_req_duration{ep:recargas_config}` | `p(95)<=80` | 8.7 ms | ✓ |
| V-06 empresas ≤ 10 % de U-01 | `http_req_duration{ep:empresas}` | `p(95)<=80` | 12.0 ms | ✓ |
| V-06 deudas ≤ 10 % de U-01 | `http_req_duration{ep:deudas}` | `p(95)<=80` | 6.8 ms | ✓ |
| V-06 limites ≤ 10 % de U-01 | `http_req_duration{ep:limites}` | `p(95)<=80` | 14.2 ms | ✓ |
| V-06 alertas ≤ 10 % de U-01 | `http_req_duration{ep:alertas}` | `p(95)<=80` | 11.1 ms | ✓ |
| V-06 solicitudes ≤ 10 % de U-01 | `http_req_duration{ep:solicitudes}` | `p(95)<=80` | 11.8 ms | ✓ |
| V-06 dispositivos ≤ 10 % de U-01 | `http_req_duration{ep:dispositivos}` | `p(95)<=80` | 10.0 ms | ✓ |
| V-06 sesiones ≤ 10 % de U-01 | `http_req_duration{ep:sesiones}` | `p(95)<=80` | 13.6 ms | ✓ |
| V-06 transferir ≤ 10 % de U-02 | `http_req_duration{ep:transferir}` | `p(95)<=150` | 124.2 ms | ✓ |
| V-06 recargar ≤ 10 % de U-02 | `http_req_duration{ep:recargar}` | `p(95)<=150` | 13.0 ms | ✓ |
| V-06 pagar ≤ 10 % de U-02 | `http_req_duration{ep:pagar}` | `p(95)<=150` | 9.6 ms | ✓ |
