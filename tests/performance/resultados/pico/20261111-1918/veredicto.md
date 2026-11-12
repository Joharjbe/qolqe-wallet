# Veredicto · pico · 20261111-1918

- Inicio: 2026-11-11 19:18:14 · fin: 2026-11-11 19:39:18 (hora de Lima) · primera petición: 2026-11-11 19:18:20
- Duración con muestras: 21.0 min · peticiones: 16,947 · sesiones: 1,449
- Código de salida de k6: 0 (0 = todos los umbrales de k6 pasan; 99 = alguno falla)
- **Corrida válida** según V-01 a V-07

## 1. Validez de la corrida (V-01 a V-07)

| ID | Criterio | Medido | Umbral | Resultado | Nota |
|---|---|---|---|---|---|
| V-01 | CPU del generador k6 (% del equipo, máximo de las ventanas) | 0.3 % | < 80 % | ✓ PASA | pico de 1 s: 1.9 % del equipo (18 % de un núcleo) |
| V-01 | CPU total del equipo (máximo de las ventanas) | 90.2 % | < 80 % | ✗ FALLA | informativo: lo mueven procesos de macOS; ventanas ≥ 80 % en el minuto 10.2, 10.8 |
| V-02 | errores de datos · campaña | 0 (0.00 %) | = 0 (repetir si > 0.1 %) | ✓ PASA |  |
| V-03 | mezcla lograda · campaña (peor operación) | 0.48 pp | ± 2 pp | ✓ PASA |  |
| V-04 | CPU ocioso del equipo antes de empezar (top, 3 s) | 81.4 % | ≥ 65 % | ✓ PASA | carga de 1 min: 5.05 (diseño < 1.5; solo se registra) |
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
| U-06 | Campaña: degradación razonable del servicio | 78 ms | < 1,600 ms | ✓ PASA | 34 criterios (ver detalle) |
| U-07 | Ninguna operación de dinero a medias ni aplicada dos veces | 0 | = 0 | ✓ PASA | 1 criterio (ver detalle) |
| U-08 | Hasta cuántos usuarios simultáneos podemos crecer | — | — | NO APLICA | se evalúa en estrés |
| U-09 | Opera de 6:00 a 24:00 sin reinicios | — | — | NO APLICA | se evalúa en resistencia |

## 3. Detalle por grupo, endpoint y ventana

Las filas *informativas* no cambian el veredicto del umbral (por ejemplo, los endpoints de `otras` con < 100 muestras).

| ID | Criterio | Medido | Umbral | Resultado | n | Nota |
|---|---|---|---|---|---|---|
| U-06 | p95 grupo consulta · campaña | 78 ms | < 1,600 ms | ✓ PASA | 12,419 | S-05: 2 × el umbral normal |
| U-06 | p95 grupo dinero · campaña | 123 ms | < 3,000 ms | ✓ PASA | 2,166 | S-05: 2 × el umbral normal |
| U-06 | p95 grupo otras · campaña | 8 ms | < 1,600 ms | ✓ PASA | 770 | S-05: 2 × el umbral normal |
| U-06 | p95 `alertas` (GET /api/limites/alertas) · campaña | 9 ms | < 1,600 ms | ✓ PASA | 166 | informativo: el veredicto es el grupo otras (§3.3) |
| U-06 | p95 `comision` (GET /api/transferencias/comision) · campaña | 8 ms | < 1,600 ms | ✓ PASA | 1,115 | S-05: 2 × el umbral normal |
| U-06 | p95 `contactos_buscar` (GET /api/contactos?buscar) · campaña | 8 ms | < 1,600 ms | ✓ PASA | 754 | S-05: 2 × el umbral normal |
| U-06 | p95 `contactos_listar` (GET /api/contactos) · campaña | 10 ms | < 1,600 ms | ✓ PASA | 754 | S-05: 2 × el umbral normal |
| U-06 | p95 `deudas` (GET /api/servicios/deudas) · campaña | 7 ms | < 1,600 ms | ✓ PASA | 728 | S-05: 2 × el umbral normal |
| U-06 | p95 `dispositivos` (GET /api/seguridad/dispositivos) · campaña | 8 ms | < 1,600 ms | ✓ PASA | 170 | informativo: el veredicto es el grupo otras (§3.3) |
| U-06 | p95 `empresas` (GET /api/servicios/empresas) · campaña | 7 ms | < 1,600 ms | ✓ PASA | 728 | S-05: 2 × el umbral normal |
| U-06 | p95 `limites` (GET /api/limites) · campaña | 8 ms | < 1,600 ms | ✓ PASA | 153 | informativo: el veredicto es el grupo otras (§3.3) |
| U-06 | p95 `login` (POST /api/auth/login) · campaña | 97 ms | < 1,600 ms | ✓ PASA | 1,250 | S-05: 2 × el umbral normal |
| U-06 | p95 `movimientos` (GET /api/movimientos) · campaña | 34 ms | < 1,600 ms | ✓ PASA | 1,145 | S-05: 2 × el umbral normal |
| U-06 | p95 `pagar` (POST /api/servicios/pagos) · campaña | 13 ms | < 3,000 ms | ✓ PASA | 292 | S-05: 2 × el umbral normal |
| U-06 | p95 `perfil` (GET /api/cuentas/me) · campaña | 6 ms | < 1,600 ms | ✓ PASA | 2,208 | S-05: 2 × el umbral normal |
| U-06 | p95 `recargar` (POST /api/recargas) · campaña | 14 ms | < 3,000 ms | ✓ PASA | 759 | S-05: 2 × el umbral normal |
| U-06 | p95 `recargas_config` (GET /api/recargas/configuracion) · campaña | 6 ms | < 1,600 ms | ✓ PASA | 759 | S-05: 2 × el umbral normal |
| U-06 | p95 `saldo` (GET /api/cuentas/me/saldo) · campaña | 8 ms | < 1,600 ms | ✓ PASA | 2,208 | S-05: 2 × el umbral normal |
| U-06 | p95 `sesiones` (GET /api/seguridad/sesiones) · campaña | 8 ms | < 1,600 ms | ✓ PASA | 135 | informativo: el veredicto es el grupo otras (§3.3) |
| U-06 | p95 `solicitudes` (GET /api/solicitudes) · campaña | 8 ms | < 1,600 ms | ✓ PASA | 146 | informativo: el veredicto es el grupo otras (§3.3) |
| U-06 | p95 `transferir` (POST /api/transferencias) · campaña | 126 ms | < 3,000 ms | ✓ PASA | 1,115 | S-05: 2 × el umbral normal |
| U-06 | error de rendimiento · campaña | 0.00 % | ≤ 1 % | ✓ PASA | 8,729 | operacion_fallida (una muestra por operación, S-06) |
| U-06 | sesiones descartadas · campaña | 0 | = 0 | ✓ PASA |  |  |
| U-06 | p95 grupo consulta · recuperación 12:10–12:15 | 80 ms | < 800 ms | ✓ PASA | 2,486 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 grupo dinero · recuperación 12:10–12:15 | 123 ms | < 1,500 ms | ✓ PASA | 418 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 grupo otras · recuperación 12:10–12:15 | 9 ms | < 800 ms | ✓ PASA | 149 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `alertas` (GET /api/limites/alertas) · recuperación 12:10–12:15 | 9 ms | < 800 ms | ✓ PASA | 32 | informativo: el veredicto es el grupo otras (§3.3) |
| U-06 | p95 `comision` (GET /api/transferencias/comision) · recuperación 12:10–12:15 | 8 ms | < 800 ms | ✓ PASA | 220 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `contactos_buscar` (GET /api/contactos?buscar) · recuperación 12:10–12:15 | 8 ms | < 800 ms | ✓ PASA | 159 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `contactos_listar` (GET /api/contactos) · recuperación 12:10–12:15 | 10 ms | < 800 ms | ✓ PASA | 159 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `deudas` (GET /api/servicios/deudas) · recuperación 12:10–12:15 | 7 ms | < 800 ms | ✓ PASA | 132 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `dispositivos` (GET /api/seguridad/dispositivos) · recuperación 12:10–12:15 | 7 ms | < 800 ms | ✓ PASA | 31 | informativo: el veredicto es el grupo otras (§3.3) |
| U-06 | p95 `empresas` (GET /api/servicios/empresas) · recuperación 12:10–12:15 | 8 ms | < 800 ms | ✓ PASA | 132 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `limites` (GET /api/limites) · recuperación 12:10–12:15 | 8 ms | < 800 ms | ✓ PASA | 31 | informativo: el veredicto es el grupo otras (§3.3) |
| U-06 | p95 `login` (POST /api/auth/login) · recuperación 12:10–12:15 | 97 ms | < 800 ms | ✓ PASA | 250 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `movimientos` (GET /api/movimientos) · recuperación 12:10–12:15 | 33 ms | < 800 ms | ✓ PASA | 233 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `pagar` (POST /api/servicios/pagos) · recuperación 12:10–12:15 | 16 ms | < 1,500 ms | ✓ PASA | 48 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `perfil` (GET /api/cuentas/me) · recuperación 12:10–12:15 | 7 ms | < 800 ms | ✓ PASA | 451 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `recargar` (POST /api/recargas) · recuperación 12:10–12:15 | 15 ms | < 1,500 ms | ✓ PASA | 150 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `recargas_config` (GET /api/recargas/configuracion) · recuperación 12:10–12:15 | 7 ms | < 800 ms | ✓ PASA | 150 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `saldo` (GET /api/cuentas/me/saldo) · recuperación 12:10–12:15 | 9 ms | < 800 ms | ✓ PASA | 451 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `sesiones` (GET /api/seguridad/sesiones) · recuperación 12:10–12:15 | 10 ms | < 800 ms | ✓ PASA | 25 | informativo: el veredicto es el grupo otras (§3.3) |
| U-06 | p95 `solicitudes` (GET /api/solicitudes) · recuperación 12:10–12:15 | 10 ms | < 800 ms | ✓ PASA | 30 | informativo: el veredicto es el grupo otras (§3.3) |
| U-06 | p95 `transferir` (POST /api/transferencias) · recuperación 12:10–12:15 | 125 ms | < 1,500 ms | ✓ PASA | 220 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-01 | p95 grupo consulta · campaña frente al umbral normal | 78 ms | < 800 ms | ✓ PASA | 12,419 | S-05: informativo |
| U-02 | p95 grupo dinero · campaña frente al umbral normal | 123 ms | < 1,500 ms | ✓ PASA | 2,166 | S-05: informativo |
| U-01 | p95 grupo otras · campaña frente al umbral normal | 8 ms | < 800 ms | ✓ PASA | 770 | S-05: informativo |
| U-01 | p95 `alertas` (GET /api/limites/alertas) · campaña frente al umbral normal | 9 ms | < 800 ms | ✓ PASA | 166 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `comision` (GET /api/transferencias/comision) · campaña frente al umbral normal | 8 ms | < 800 ms | ✓ PASA | 1,115 | S-05: informativo |
| U-01 | p95 `contactos_buscar` (GET /api/contactos?buscar) · campaña frente al umbral normal | 8 ms | < 800 ms | ✓ PASA | 754 | S-05: informativo |
| U-01 | p95 `contactos_listar` (GET /api/contactos) · campaña frente al umbral normal | 10 ms | < 800 ms | ✓ PASA | 754 | S-05: informativo |
| U-01 | p95 `deudas` (GET /api/servicios/deudas) · campaña frente al umbral normal | 7 ms | < 800 ms | ✓ PASA | 728 | S-05: informativo |
| U-01 | p95 `dispositivos` (GET /api/seguridad/dispositivos) · campaña frente al umbral normal | 8 ms | < 800 ms | ✓ PASA | 170 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `empresas` (GET /api/servicios/empresas) · campaña frente al umbral normal | 7 ms | < 800 ms | ✓ PASA | 728 | S-05: informativo |
| U-01 | p95 `limites` (GET /api/limites) · campaña frente al umbral normal | 8 ms | < 800 ms | ✓ PASA | 153 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `login` (POST /api/auth/login) · campaña frente al umbral normal | 97 ms | < 800 ms | ✓ PASA | 1,250 | S-05: informativo |
| U-01 | p95 `movimientos` (GET /api/movimientos) · campaña frente al umbral normal | 34 ms | < 800 ms | ✓ PASA | 1,145 | S-05: informativo |
| U-02 | p95 `pagar` (POST /api/servicios/pagos) · campaña frente al umbral normal | 13 ms | < 1,500 ms | ✓ PASA | 292 | S-05: informativo |
| U-01 | p95 `perfil` (GET /api/cuentas/me) · campaña frente al umbral normal | 6 ms | < 800 ms | ✓ PASA | 2,208 | S-05: informativo |
| U-02 | p95 `recargar` (POST /api/recargas) · campaña frente al umbral normal | 14 ms | < 1,500 ms | ✓ PASA | 759 | S-05: informativo |
| U-01 | p95 `recargas_config` (GET /api/recargas/configuracion) · campaña frente al umbral normal | 6 ms | < 800 ms | ✓ PASA | 759 | S-05: informativo |
| U-01 | p95 `saldo` (GET /api/cuentas/me/saldo) · campaña frente al umbral normal | 8 ms | < 800 ms | ✓ PASA | 2,208 | S-05: informativo |
| U-01 | p95 `sesiones` (GET /api/seguridad/sesiones) · campaña frente al umbral normal | 8 ms | < 800 ms | ✓ PASA | 135 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `solicitudes` (GET /api/solicitudes) · campaña frente al umbral normal | 8 ms | < 800 ms | ✓ PASA | 146 | informativo: el veredicto es el grupo otras (§3.3) |
| U-02 | p95 `transferir` (POST /api/transferencias) · campaña frente al umbral normal | 126 ms | < 1,500 ms | ✓ PASA | 1,115 | S-05: informativo |
| U-01 | p95 grupo consulta · base 11:58–12:00 | 80 ms | < 800 ms | ✓ PASA | 1,025 | informativo: hora punta antes del salto |
| U-02 | p95 grupo dinero · base 11:58–12:00 | 123 ms | < 1,500 ms | ✓ PASA | 166 | informativo: hora punta antes del salto |
| U-01 | p95 grupo otras · base 11:58–12:00 | 8 ms | < 800 ms | ✓ PASA | 68 | informativo: hora punta antes del salto |
| U-01 | p95 `alertas` (GET /api/limites/alertas) · base 11:58–12:00 | 14 ms | < 800 ms | ✓ PASA | 11 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `comision` (GET /api/transferencias/comision) · base 11:58–12:00 | 7 ms | < 800 ms | ✓ PASA | 91 | informativo: hora punta antes del salto |
| U-01 | p95 `contactos_buscar` (GET /api/contactos?buscar) · base 11:58–12:00 | 6 ms | < 800 ms | ✓ PASA | 55 | informativo: hora punta antes del salto |
| U-01 | p95 `contactos_listar` (GET /api/contactos) · base 11:58–12:00 | 8 ms | < 800 ms | ✓ PASA | 55 | informativo: hora punta antes del salto |
| U-01 | p95 `deudas` (GET /api/servicios/deudas) · base 11:58–12:00 | 5 ms | < 800 ms | ✓ PASA | 65 | informativo: hora punta antes del salto |
| U-01 | p95 `dispositivos` (GET /api/seguridad/dispositivos) · base 11:58–12:00 | 11 ms | < 800 ms | ✓ PASA | 15 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `empresas` (GET /api/servicios/empresas) · base 11:58–12:00 | 7 ms | < 800 ms | ✓ PASA | 65 | informativo: hora punta antes del salto |
| U-01 | p95 `limites` (GET /api/limites) · base 11:58–12:00 | 7 ms | < 800 ms | ✓ PASA | 15 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `login` (POST /api/auth/login) · base 11:58–12:00 | 91 ms | < 800 ms | ✓ PASA | 100 | informativo: hora punta antes del salto |
| U-01 | p95 `movimientos` (GET /api/movimientos) · base 11:58–12:00 | 26 ms | < 800 ms | ✓ PASA | 89 | informativo: hora punta antes del salto |
| U-02 | p95 `pagar` (POST /api/servicios/pagos) · base 11:58–12:00 | 9 ms | < 1,500 ms | ✓ PASA | 20 | informativo: hora punta antes del salto |
| U-01 | p95 `perfil` (GET /api/cuentas/me) · base 11:58–12:00 | 4 ms | < 800 ms | ✓ PASA | 191 | informativo: hora punta antes del salto |
| U-02 | p95 `recargar` (POST /api/recargas) · base 11:58–12:00 | 11 ms | < 1,500 ms | ✓ PASA | 55 | informativo: hora punta antes del salto |
| U-01 | p95 `recargas_config` (GET /api/recargas/configuracion) · base 11:58–12:00 | 5 ms | < 800 ms | ✓ PASA | 55 | informativo: hora punta antes del salto |
| U-01 | p95 `saldo` (GET /api/cuentas/me/saldo) · base 11:58–12:00 | 7 ms | < 800 ms | ✓ PASA | 191 | informativo: hora punta antes del salto |
| U-01 | p95 `sesiones` (GET /api/seguridad/sesiones) · base 11:58–12:00 | 8 ms | < 800 ms | ✓ PASA | 15 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `solicitudes` (GET /api/solicitudes) · base 11:58–12:00 | 7 ms | < 800 ms | ✓ PASA | 12 | informativo: el veredicto es el grupo otras (§3.3) |
| U-02 | p95 `transferir` (POST /api/transferencias) · base 11:58–12:00 | 132 ms | < 1,500 ms | ✓ PASA | 91 | informativo: hora punta antes del salto |
| U-07 | descuadres en C1–C6 (verificacion_dinero.txt) | 0 | = 0 | ✓ PASA |  | línea TOTAL |
| U-07 | operaciones de dinero sin respuesta (status 0) | 0 | se concilian en C6 | INFO |  |  |
| §2.1 | p95 de http_req_connecting | 0.6 ms | ≤ 10 ms (si no, se suma) | INFO |  | no se suma |
| §6.3 | throttling del cgroup en la corrida | 18 períodos, 0.8 s | diagnóstico (H1) | INFO |  |  |

## 4. Mezcla lograda (V-03, M-06)

| Operación | Pedida (%) | Lograda (%) | Diferencia (pp) |
|---|---|---|---|
| saldo_perfil | 30.0 | 29.5 | -0.48 |
| movimientos | 15.0 | 15.3 | 0.31 |
| transferir | 15.0 | 14.9 | -0.09 |
| contactos | 10.0 | 10.1 | 0.08 |
| recarga | 10.0 | 10.1 | 0.15 |
| deudas | 6.0 | 5.8 | -0.17 |
| pago | 4.0 | 3.9 | -0.10 |
| otras | 10.0 | 10.3 | 0.30 |

## 5. Errores de rendimiento y de datos, por separado (toda la corrida)

| Clase | Tipo o código | Cantidad |
|---|---|---|
| — | sin errores | 0 |

## 6. Umbrales evaluados por k6 (resumen.json; ✓ cumple, ✗ falla, ○ sin muestras)

| Umbral | Métrica | Condición | Medido por k6 | k6 |
|---|---|---|---|---|
| U-06 consultas e inicio de sesión (grupo) | `http_req_duration{campana:si,grupo:consulta}` | `p(95)<1600` | 78.2 ms | ✓ |
| U-06 login (S-03) | `http_req_duration{campana:si,ep:login}` | `p(95)<1600` | 97.2 ms | ✓ |
| U-06 saldo (S-03) | `http_req_duration{campana:si,ep:saldo}` | `p(95)<1600` | 8.1 ms | ✓ |
| U-06 perfil (S-03) | `http_req_duration{campana:si,ep:perfil}` | `p(95)<1600` | 6.3 ms | ✓ |
| U-06 movimientos (S-03) | `http_req_duration{campana:si,ep:movimientos}` | `p(95)<1600` | 34.0 ms | ✓ |
| U-06 comision (S-03) | `http_req_duration{campana:si,ep:comision}` | `p(95)<1600` | 8.0 ms | ✓ |
| U-06 contactos_listar (S-03) | `http_req_duration{campana:si,ep:contactos_listar}` | `p(95)<1600` | 9.9 ms | ✓ |
| U-06 contactos_buscar (S-03) | `http_req_duration{campana:si,ep:contactos_buscar}` | `p(95)<1600` | 8.3 ms | ✓ |
| U-06 recargas_config (S-03) | `http_req_duration{campana:si,ep:recargas_config}` | `p(95)<1600` | 5.6 ms | ✓ |
| U-06 empresas (S-03) | `http_req_duration{campana:si,ep:empresas}` | `p(95)<1600` | 7.3 ms | ✓ |
| U-06 deudas (S-03) | `http_req_duration{campana:si,ep:deudas}` | `p(95)<1600` | 7.3 ms | ✓ |
| U-06 otras: 5 GET al 2 % (§3.3) | `http_req_duration{campana:si,op:otras}` | `p(95)<1600` | 8.3 ms | ✓ |
| U-06 operaciones de dinero (grupo) | `http_req_duration{campana:si,grupo:dinero}` | `p(95)<3000` | 123.0 ms | ✓ |
| U-06 transferir (S-03) | `http_req_duration{campana:si,ep:transferir}` | `p(95)<3000` | 126.2 ms | ✓ |
| U-06 recargar (S-03) | `http_req_duration{campana:si,ep:recargar}` | `p(95)<3000` | 14.1 ms | ✓ |
| U-06 pagar (S-03) | `http_req_duration{campana:si,ep:pagar}` | `p(95)<3000` | 12.7 ms | ✓ |
| U-06 error en la campaña (S-05) | `operacion_fallida{campana:si}` | `rate<=0.01` | 0.00 % | ✓ |
| U-06 sesiones descartadas | `dropped_iterations` | `count==0` | 0 | ✓ |
| U-01 consultas e inicio de sesión (grupo) | `http_req_duration{fase:base,grupo:consulta}` | `p(95)<800` | 80.3 ms | ✓ |
| U-01 login (S-03) | `http_req_duration{fase:base,ep:login}` | `p(95)<800` | 90.7 ms | ✓ |
| U-01 saldo (S-03) | `http_req_duration{fase:base,ep:saldo}` | `p(95)<800` | 7.3 ms | ✓ |
| U-01 perfil (S-03) | `http_req_duration{fase:base,ep:perfil}` | `p(95)<800` | 4.3 ms | ✓ |
| U-01 movimientos (S-03) | `http_req_duration{fase:base,ep:movimientos}` | `p(95)<800` | 25.3 ms | ✓ |
| U-01 comision (S-03) | `http_req_duration{fase:base,ep:comision}` | `p(95)<800` | 7.4 ms | ✓ |
| U-01 contactos_listar (S-03) | `http_req_duration{fase:base,ep:contactos_listar}` | `p(95)<800` | 8.3 ms | ✓ |
| U-01 contactos_buscar (S-03) | `http_req_duration{fase:base,ep:contactos_buscar}` | `p(95)<800` | 5.0 ms | ✓ |
| U-01 recargas_config (S-03) | `http_req_duration{fase:base,ep:recargas_config}` | `p(95)<800` | 5.1 ms | ✓ |
| U-01 empresas (S-03) | `http_req_duration{fase:base,ep:empresas}` | `p(95)<800` | 6.8 ms | ✓ |
| U-01 deudas (S-03) | `http_req_duration{fase:base,ep:deudas}` | `p(95)<800` | 5.3 ms | ✓ |
| U-01 otras: 5 GET al 2 % (§3.3) | `http_req_duration{fase:base,op:otras}` | `p(95)<800` | 8.2 ms | ✓ |
| U-02 operaciones de dinero (grupo) | `http_req_duration{fase:base,grupo:dinero}` | `p(95)<1500` | 122.8 ms | ✓ |
| U-02 transferir (S-03) | `http_req_duration{fase:base,ep:transferir}` | `p(95)<1500` | 131.5 ms | ✓ |
| U-02 recargar (S-03) | `http_req_duration{fase:base,ep:recargar}` | `p(95)<1500` | 10.8 ms | ✓ |
| U-02 pagar (S-03) | `http_req_duration{fase:base,ep:pagar}` | `p(95)<1500` | 9.3 ms | ✓ |
| U-06 recuperación U-01 consultas e inicio de sesión (grupo) | `http_req_duration{fase:recuperacion,grupo:consulta}` | `p(95)<800` | 80.5 ms | ✓ |
| U-06 recuperación U-01 login (S-03) | `http_req_duration{fase:recuperacion,ep:login}` | `p(95)<800` | 97.2 ms | ✓ |
| U-06 recuperación U-01 saldo (S-03) | `http_req_duration{fase:recuperacion,ep:saldo}` | `p(95)<800` | 9.0 ms | ✓ |
| U-06 recuperación U-01 perfil (S-03) | `http_req_duration{fase:recuperacion,ep:perfil}` | `p(95)<800` | 6.5 ms | ✓ |
| U-06 recuperación U-01 movimientos (S-03) | `http_req_duration{fase:recuperacion,ep:movimientos}` | `p(95)<800` | 33.0 ms | ✓ |
| U-06 recuperación U-01 comision (S-03) | `http_req_duration{fase:recuperacion,ep:comision}` | `p(95)<800` | 8.5 ms | ✓ |
| U-06 recuperación U-01 contactos_listar (S-03) | `http_req_duration{fase:recuperacion,ep:contactos_listar}` | `p(95)<800` | 9.9 ms | ✓ |
| U-06 recuperación U-01 contactos_buscar (S-03) | `http_req_duration{fase:recuperacion,ep:contactos_buscar}` | `p(95)<800` | 8.1 ms | ✓ |
| U-06 recuperación U-01 recargas_config (S-03) | `http_req_duration{fase:recuperacion,ep:recargas_config}` | `p(95)<800` | 6.8 ms | ✓ |
| U-06 recuperación U-01 empresas (S-03) | `http_req_duration{fase:recuperacion,ep:empresas}` | `p(95)<800` | 8.4 ms | ✓ |
| U-06 recuperación U-01 deudas (S-03) | `http_req_duration{fase:recuperacion,ep:deudas}` | `p(95)<800` | 6.9 ms | ✓ |
| U-06 recuperación U-01 otras: 5 GET al 2 % (§3.3) | `http_req_duration{fase:recuperacion,op:otras}` | `p(95)<800` | 9.2 ms | ✓ |
| U-06 recuperación U-02 operaciones de dinero (grupo) | `http_req_duration{fase:recuperacion,grupo:dinero}` | `p(95)<1500` | 122.8 ms | ✓ |
| U-06 recuperación U-02 transferir (S-03) | `http_req_duration{fase:recuperacion,ep:transferir}` | `p(95)<1500` | 125.3 ms | ✓ |
| U-06 recuperación U-02 recargar (S-03) | `http_req_duration{fase:recuperacion,ep:recargar}` | `p(95)<1500` | 14.0 ms | ✓ |
| U-06 recuperación U-02 pagar (S-03) | `http_req_duration{fase:recuperacion,ep:pagar}` | `p(95)<1500` | 15.7 ms | ✓ |
