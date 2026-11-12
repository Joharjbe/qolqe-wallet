# Veredicto · pico · 20261111-1852

- Inicio: 2026-11-11 18:53:32 · fin: 2026-11-11 19:14:40 (hora de Lima) · primera petición: 2026-11-11 18:53:37
- Duración con muestras: 21.0 min · peticiones: 16,896 · sesiones: 1,449
- Código de salida de k6: 0 (0 = todos los umbrales de k6 pasan; 99 = alguno falla)
- **Corrida NO válida: se repite y no se analiza (paso 1 de S14)** según V-01 a V-07

## 1. Validez de la corrida (V-01 a V-07)

| ID | Criterio | Medido | Umbral | Resultado | Nota |
|---|---|---|---|---|---|
| V-01 | CPU de k6 y del equipo (máximo de las ventanas) | 35.1 % | < 80 % | ✓ PASA | pico de 1 s: 73.4 % |
| V-02 | errores de datos · campaña | 0 (0.00 %) | = 0 (repetir si > 0.1 %) | ✓ PASA |  |
| V-03 | mezcla lograda · campaña (peor operación) | 0.42 pp | ± 2 pp | ✓ PASA |  |
| V-04 | CPU ocioso del equipo antes de empezar (top, 3 s) | 64.2 % | ≥ 65 % | ✗ FALLA | carga de 1 min: 7.97 (diseño < 1.5; solo se registra) |
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
| U-06 | Campaña: degradación razonable del servicio | 90 ms | < 1,600 ms | ✓ PASA | 34 criterios (ver detalle) |
| U-07 | Ninguna operación de dinero a medias ni aplicada dos veces | — | = 0 | SIN DATO | falta medir 1 de 1: descuadres en C1–C6 (verificacion_dinero.txt) |
| U-08 | Hasta cuántos usuarios simultáneos podemos crecer | — | — | NO APLICA | se evalúa en estrés |
| U-09 | Opera de 6:00 a 24:00 sin reinicios | — | — | NO APLICA | se evalúa en resistencia |

## 3. Detalle por grupo, endpoint y ventana

Las filas *informativas* no cambian el veredicto del umbral (por ejemplo, los endpoints de `otras` con < 100 muestras).

| ID | Criterio | Medido | Umbral | Resultado | n | Nota |
|---|---|---|---|---|---|---|
| U-06 | p95 grupo consulta · campaña | 90 ms | < 1,600 ms | ✓ PASA | 12,444 | S-05: 2 × el umbral normal |
| U-06 | p95 grupo dinero · campaña | 126 ms | < 3,000 ms | ✓ PASA | 2,196 | S-05: 2 × el umbral normal |
| U-06 | p95 grupo otras · campaña | 11 ms | < 1,600 ms | ✓ PASA | 771 | S-05: 2 × el umbral normal |
| U-06 | p95 `alertas` (GET /api/limites/alertas) · campaña | 9 ms | < 1,600 ms | ✓ PASA | 145 | informativo: el veredicto es el grupo otras (§3.3) |
| U-06 | p95 `comision` (GET /api/transferencias/comision) · campaña | 11 ms | < 1,600 ms | ✓ PASA | 1,131 | S-05: 2 × el umbral normal |
| U-06 | p95 `contactos_buscar` (GET /api/contactos?buscar) · campaña | 6 ms | < 1,600 ms | ✓ PASA | 742 | S-05: 2 × el umbral normal |
| U-06 | p95 `contactos_listar` (GET /api/contactos) · campaña | 13 ms | < 1,600 ms | ✓ PASA | 742 | S-05: 2 × el umbral normal |
| U-06 | p95 `deudas` (GET /api/servicios/deudas) · campaña | 6 ms | < 1,600 ms | ✓ PASA | 736 | S-05: 2 × el umbral normal |
| U-06 | p95 `dispositivos` (GET /api/seguridad/dispositivos) · campaña | 10 ms | < 1,600 ms | ✓ PASA | 156 | informativo: el veredicto es el grupo otras (§3.3) |
| U-06 | p95 `empresas` (GET /api/servicios/empresas) · campaña | 10 ms | < 1,600 ms | ✓ PASA | 736 | S-05: 2 × el umbral normal |
| U-06 | p95 `limites` (GET /api/limites) · campaña | 11 ms | < 1,600 ms | ✓ PASA | 142 | informativo: el veredicto es el grupo otras (§3.3) |
| U-06 | p95 `login` (POST /api/auth/login) · campaña | 104 ms | < 1,600 ms | ✓ PASA | 1,250 | S-05: 2 × el umbral normal |
| U-06 | p95 `movimientos` (GET /api/movimientos) · campaña | 36 ms | < 1,600 ms | ✓ PASA | 1,124 | S-05: 2 × el umbral normal |
| U-06 | p95 `pagar` (POST /api/servicios/pagos) · campaña | 10 ms | < 3,000 ms | ✓ PASA | 289 | S-05: 2 × el umbral normal |
| U-06 | p95 `perfil` (GET /api/cuentas/me) · campaña | 5 ms | < 1,600 ms | ✓ PASA | 2,218 | S-05: 2 × el umbral normal |
| U-06 | p95 `recargar` (POST /api/recargas) · campaña | 11 ms | < 3,000 ms | ✓ PASA | 776 | S-05: 2 × el umbral normal |
| U-06 | p95 `recargas_config` (GET /api/recargas/configuracion) · campaña | 8 ms | < 1,600 ms | ✓ PASA | 776 | S-05: 2 × el umbral normal |
| U-06 | p95 `saldo` (GET /api/cuentas/me/saldo) · campaña | 11 ms | < 1,600 ms | ✓ PASA | 2,218 | S-05: 2 × el umbral normal |
| U-06 | p95 `sesiones` (GET /api/seguridad/sesiones) · campaña | 11 ms | < 1,600 ms | ✓ PASA | 168 | informativo: el veredicto es el grupo otras (§3.3) |
| U-06 | p95 `solicitudes` (GET /api/solicitudes) · campaña | 12 ms | < 1,600 ms | ✓ PASA | 160 | informativo: el veredicto es el grupo otras (§3.3) |
| U-06 | p95 `transferir` (POST /api/transferencias) · campaña | 131 ms | < 3,000 ms | ✓ PASA | 1,131 | S-05: 2 × el umbral normal |
| U-06 | error de rendimiento · campaña | 0.00 % | ≤ 1 % | ✓ PASA | 8,748 | operacion_fallida (una muestra por operación, S-06) |
| U-06 | sesiones descartadas · campaña | 0 | = 0 | ✓ PASA |  |  |
| U-06 | p95 grupo consulta · recuperación 12:10–12:15 | 93 ms | < 800 ms | ✓ PASA | 2,460 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 grupo dinero · recuperación 12:10–12:15 | 127 ms | < 1,500 ms | ✓ PASA | 460 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 grupo otras · recuperación 12:10–12:15 | 13 ms | < 800 ms | ✓ PASA | 159 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `alertas` (GET /api/limites/alertas) · recuperación 12:10–12:15 | 12 ms | < 800 ms | ✓ PASA | 25 | informativo: el veredicto es el grupo otras (§3.3) |
| U-06 | p95 `comision` (GET /api/transferencias/comision) · recuperación 12:10–12:15 | 12 ms | < 800 ms | ✓ PASA | 235 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `contactos_buscar` (GET /api/contactos?buscar) · recuperación 12:10–12:15 | 6 ms | < 800 ms | ✓ PASA | 148 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `contactos_listar` (GET /api/contactos) · recuperación 12:10–12:15 | 14 ms | < 800 ms | ✓ PASA | 148 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `deudas` (GET /api/servicios/deudas) · recuperación 12:10–12:15 | 7 ms | < 800 ms | ✓ PASA | 134 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `dispositivos` (GET /api/seguridad/dispositivos) · recuperación 12:10–12:15 | 15 ms | < 800 ms | ✓ PASA | 28 | informativo: el veredicto es el grupo otras (§3.3) |
| U-06 | p95 `empresas` (GET /api/servicios/empresas) · recuperación 12:10–12:15 | 11 ms | < 800 ms | ✓ PASA | 134 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `limites` (GET /api/limites) · recuperación 12:10–12:15 | 13 ms | < 800 ms | ✓ PASA | 37 | informativo: el veredicto es el grupo otras (§3.3) |
| U-06 | p95 `login` (POST /api/auth/login) · recuperación 12:10–12:15 | 104 ms | < 800 ms | ✓ PASA | 250 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `movimientos` (GET /api/movimientos) · recuperación 12:10–12:15 | 36 ms | < 800 ms | ✓ PASA | 225 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `pagar` (POST /api/servicios/pagos) · recuperación 12:10–12:15 | 11 ms | < 1,500 ms | ✓ PASA | 54 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `perfil` (GET /api/cuentas/me) · recuperación 12:10–12:15 | 5 ms | < 800 ms | ✓ PASA | 428 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `recargar` (POST /api/recargas) · recuperación 12:10–12:15 | 12 ms | < 1,500 ms | ✓ PASA | 171 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `recargas_config` (GET /api/recargas/configuracion) · recuperación 12:10–12:15 | 11 ms | < 800 ms | ✓ PASA | 171 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `saldo` (GET /api/cuentas/me/saldo) · recuperación 12:10–12:15 | 12 ms | < 800 ms | ✓ PASA | 428 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-06 | p95 `sesiones` (GET /api/seguridad/sesiones) · recuperación 12:10–12:15 | 12 ms | < 800 ms | ✓ PASA | 23 | informativo: el veredicto es el grupo otras (§3.3) |
| U-06 | p95 `solicitudes` (GET /api/solicitudes) · recuperación 12:10–12:15 | 12 ms | < 800 ms | ✓ PASA | 46 | informativo: el veredicto es el grupo otras (§3.3) |
| U-06 | p95 `transferir` (POST /api/transferencias) · recuperación 12:10–12:15 | 131 ms | < 1,500 ms | ✓ PASA | 235 | recuperación: se vuelve a cumplir U-01/U-02 |
| U-01 | p95 grupo consulta · campaña frente al umbral normal | 90 ms | < 800 ms | ✓ PASA | 12,444 | S-05: informativo |
| U-02 | p95 grupo dinero · campaña frente al umbral normal | 126 ms | < 1,500 ms | ✓ PASA | 2,196 | S-05: informativo |
| U-01 | p95 grupo otras · campaña frente al umbral normal | 11 ms | < 800 ms | ✓ PASA | 771 | S-05: informativo |
| U-01 | p95 `alertas` (GET /api/limites/alertas) · campaña frente al umbral normal | 9 ms | < 800 ms | ✓ PASA | 145 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `comision` (GET /api/transferencias/comision) · campaña frente al umbral normal | 11 ms | < 800 ms | ✓ PASA | 1,131 | S-05: informativo |
| U-01 | p95 `contactos_buscar` (GET /api/contactos?buscar) · campaña frente al umbral normal | 6 ms | < 800 ms | ✓ PASA | 742 | S-05: informativo |
| U-01 | p95 `contactos_listar` (GET /api/contactos) · campaña frente al umbral normal | 13 ms | < 800 ms | ✓ PASA | 742 | S-05: informativo |
| U-01 | p95 `deudas` (GET /api/servicios/deudas) · campaña frente al umbral normal | 6 ms | < 800 ms | ✓ PASA | 736 | S-05: informativo |
| U-01 | p95 `dispositivos` (GET /api/seguridad/dispositivos) · campaña frente al umbral normal | 10 ms | < 800 ms | ✓ PASA | 156 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `empresas` (GET /api/servicios/empresas) · campaña frente al umbral normal | 10 ms | < 800 ms | ✓ PASA | 736 | S-05: informativo |
| U-01 | p95 `limites` (GET /api/limites) · campaña frente al umbral normal | 11 ms | < 800 ms | ✓ PASA | 142 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `login` (POST /api/auth/login) · campaña frente al umbral normal | 104 ms | < 800 ms | ✓ PASA | 1,250 | S-05: informativo |
| U-01 | p95 `movimientos` (GET /api/movimientos) · campaña frente al umbral normal | 36 ms | < 800 ms | ✓ PASA | 1,124 | S-05: informativo |
| U-02 | p95 `pagar` (POST /api/servicios/pagos) · campaña frente al umbral normal | 10 ms | < 1,500 ms | ✓ PASA | 289 | S-05: informativo |
| U-01 | p95 `perfil` (GET /api/cuentas/me) · campaña frente al umbral normal | 5 ms | < 800 ms | ✓ PASA | 2,218 | S-05: informativo |
| U-02 | p95 `recargar` (POST /api/recargas) · campaña frente al umbral normal | 11 ms | < 1,500 ms | ✓ PASA | 776 | S-05: informativo |
| U-01 | p95 `recargas_config` (GET /api/recargas/configuracion) · campaña frente al umbral normal | 8 ms | < 800 ms | ✓ PASA | 776 | S-05: informativo |
| U-01 | p95 `saldo` (GET /api/cuentas/me/saldo) · campaña frente al umbral normal | 11 ms | < 800 ms | ✓ PASA | 2,218 | S-05: informativo |
| U-01 | p95 `sesiones` (GET /api/seguridad/sesiones) · campaña frente al umbral normal | 11 ms | < 800 ms | ✓ PASA | 168 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `solicitudes` (GET /api/solicitudes) · campaña frente al umbral normal | 12 ms | < 800 ms | ✓ PASA | 160 | informativo: el veredicto es el grupo otras (§3.3) |
| U-02 | p95 `transferir` (POST /api/transferencias) · campaña frente al umbral normal | 131 ms | < 1,500 ms | ✓ PASA | 1,131 | S-05: informativo |
| U-01 | p95 grupo consulta · base 11:58–12:00 | 98 ms | < 800 ms | ✓ PASA | 994 | informativo: hora punta antes del salto |
| U-02 | p95 grupo dinero · base 11:58–12:00 | 132 ms | < 1,500 ms | ✓ PASA | 173 | informativo: hora punta antes del salto |
| U-01 | p95 grupo otras · base 11:58–12:00 | 13 ms | < 800 ms | ✓ PASA | 71 | informativo: hora punta antes del salto |
| U-01 | p95 `alertas` (GET /api/limites/alertas) · base 11:58–12:00 | 17 ms | < 800 ms | ✓ PASA | 14 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `comision` (GET /api/transferencias/comision) · base 11:58–12:00 | 13 ms | < 800 ms | ✓ PASA | 94 | informativo: hora punta antes del salto |
| U-01 | p95 `contactos_buscar` (GET /api/contactos?buscar) · base 11:58–12:00 | 7 ms | < 800 ms | ✓ PASA | 55 | informativo: hora punta antes del salto |
| U-01 | p95 `contactos_listar` (GET /api/contactos) · base 11:58–12:00 | 15 ms | < 800 ms | ✓ PASA | 55 | informativo: hora punta antes del salto |
| U-01 | p95 `deudas` (GET /api/servicios/deudas) · base 11:58–12:00 | 6 ms | < 800 ms | ✓ PASA | 55 | informativo: hora punta antes del salto |
| U-01 | p95 `dispositivos` (GET /api/seguridad/dispositivos) · base 11:58–12:00 | 12 ms | < 800 ms | ✓ PASA | 11 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `empresas` (GET /api/servicios/empresas) · base 11:58–12:00 | 13 ms | < 800 ms | ✓ PASA | 55 | informativo: hora punta antes del salto |
| U-01 | p95 `limites` (GET /api/limites) · base 11:58–12:00 | 13 ms | < 800 ms | ✓ PASA | 20 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `login` (POST /api/auth/login) · base 11:58–12:00 | 105 ms | < 800 ms | ✓ PASA | 100 | informativo: hora punta antes del salto |
| U-01 | p95 `movimientos` (GET /api/movimientos) · base 11:58–12:00 | 39 ms | < 800 ms | ✓ PASA | 90 | informativo: hora punta antes del salto |
| U-02 | p95 `pagar` (POST /api/servicios/pagos) · base 11:58–12:00 | 11 ms | < 1,500 ms | ✓ PASA | 25 | informativo: hora punta antes del salto |
| U-01 | p95 `perfil` (GET /api/cuentas/me) · base 11:58–12:00 | 6 ms | < 800 ms | ✓ PASA | 183 | informativo: hora punta antes del salto |
| U-02 | p95 `recargar` (POST /api/recargas) · base 11:58–12:00 | 14 ms | < 1,500 ms | ✓ PASA | 54 | informativo: hora punta antes del salto |
| U-01 | p95 `recargas_config` (GET /api/recargas/configuracion) · base 11:58–12:00 | 9 ms | < 800 ms | ✓ PASA | 54 | informativo: hora punta antes del salto |
| U-01 | p95 `saldo` (GET /api/cuentas/me/saldo) · base 11:58–12:00 | 13 ms | < 800 ms | ✓ PASA | 182 | informativo: hora punta antes del salto |
| U-01 | p95 `sesiones` (GET /api/seguridad/sesiones) · base 11:58–12:00 | 11 ms | < 800 ms | ✓ PASA | 11 | informativo: el veredicto es el grupo otras (§3.3) |
| U-01 | p95 `solicitudes` (GET /api/solicitudes) · base 11:58–12:00 | 15 ms | < 800 ms | ✓ PASA | 15 | informativo: el veredicto es el grupo otras (§3.3) |
| U-02 | p95 `transferir` (POST /api/transferencias) · base 11:58–12:00 | 135 ms | < 1,500 ms | ✓ PASA | 94 | informativo: hora punta antes del salto |
| U-07 | descuadres en C1–C6 (verificacion_dinero.txt) | — | = 0 | SIN DATO |  | no existe verificacion_dinero.txt |
| U-07 | operaciones de dinero sin respuesta (status 0) | 0 | se concilian en C6 | INFO |  |  |
| §2.1 | p95 de http_req_connecting | 1.2 ms | ≤ 10 ms (si no, se suma) | INFO |  | no se suma |

## 4. Mezcla lograda (V-03, M-06)

| Operación | Pedida (%) | Lograda (%) | Diferencia (pp) |
|---|---|---|---|
| saldo_perfil | 30.0 | 29.6 | -0.42 |
| movimientos | 15.0 | 15.0 | -0.01 |
| transferir | 15.0 | 15.1 | 0.08 |
| contactos | 10.0 | 9.9 | -0.10 |
| recarga | 10.0 | 10.3 | 0.35 |
| deudas | 6.0 | 6.0 | -0.04 |
| pago | 4.0 | 3.9 | -0.15 |
| otras | 10.0 | 10.3 | 0.28 |

## 5. Errores de rendimiento y de datos, por separado (toda la corrida)

| Clase | Tipo o código | Cantidad |
|---|---|---|
| rendimiento (U-03) | conexion | 315 |

## 6. Umbrales evaluados por k6 (resumen.json; ✓ cumple, ✗ falla, ○ sin muestras)

| Umbral | Métrica | Condición | Medido por k6 | k6 |
|---|---|---|---|---|
| U-06 consultas e inicio de sesión (grupo) | `http_req_duration{campana:si,grupo:consulta}` | `p(95)<1600` | 89.7 ms | ✓ |
| U-06 login (S-03) | `http_req_duration{campana:si,ep:login}` | `p(95)<1600` | 103.7 ms | ✓ |
| U-06 saldo (S-03) | `http_req_duration{campana:si,ep:saldo}` | `p(95)<1600` | 10.6 ms | ✓ |
| U-06 perfil (S-03) | `http_req_duration{campana:si,ep:perfil}` | `p(95)<1600` | 4.5 ms | ✓ |
| U-06 movimientos (S-03) | `http_req_duration{campana:si,ep:movimientos}` | `p(95)<1600` | 36.2 ms | ✓ |
| U-06 comision (S-03) | `http_req_duration{campana:si,ep:comision}` | `p(95)<1600` | 10.7 ms | ✓ |
| U-06 contactos_listar (S-03) | `http_req_duration{campana:si,ep:contactos_listar}` | `p(95)<1600` | 12.7 ms | ✓ |
| U-06 contactos_buscar (S-03) | `http_req_duration{campana:si,ep:contactos_buscar}` | `p(95)<1600` | 5.8 ms | ✓ |
| U-06 recargas_config (S-03) | `http_req_duration{campana:si,ep:recargas_config}` | `p(95)<1600` | 8.0 ms | ✓ |
| U-06 empresas (S-03) | `http_req_duration{campana:si,ep:empresas}` | `p(95)<1600` | 9.9 ms | ✓ |
| U-06 deudas (S-03) | `http_req_duration{campana:si,ep:deudas}` | `p(95)<1600` | 6.0 ms | ✓ |
| U-06 otras: 5 GET al 2 % (§3.3) | `http_req_duration{campana:si,op:otras}` | `p(95)<1600` | 11.1 ms | ✓ |
| U-06 operaciones de dinero (grupo) | `http_req_duration{campana:si,grupo:dinero}` | `p(95)<3000` | 125.8 ms | ✓ |
| U-06 transferir (S-03) | `http_req_duration{campana:si,ep:transferir}` | `p(95)<3000` | 130.6 ms | ✓ |
| U-06 recargar (S-03) | `http_req_duration{campana:si,ep:recargar}` | `p(95)<3000` | 11.5 ms | ✓ |
| U-06 pagar (S-03) | `http_req_duration{campana:si,ep:pagar}` | `p(95)<3000` | 10.1 ms | ✓ |
| U-06 error en la campaña (S-05) | `operacion_fallida{campana:si}` | `rate<=0.01` | 0.00 % | ✓ |
| U-06 sesiones descartadas | `dropped_iterations` | `count==0` | 0 | ✓ |
| U-01 consultas e inicio de sesión (grupo) | `http_req_duration{fase:base,grupo:consulta}` | `p(95)<800` | 98.0 ms | ✓ |
| U-01 login (S-03) | `http_req_duration{fase:base,ep:login}` | `p(95)<800` | 105.0 ms | ✓ |
| U-01 saldo (S-03) | `http_req_duration{fase:base,ep:saldo}` | `p(95)<800` | 13.3 ms | ✓ |
| U-01 perfil (S-03) | `http_req_duration{fase:base,ep:perfil}` | `p(95)<800` | 5.5 ms | ✓ |
| U-01 movimientos (S-03) | `http_req_duration{fase:base,ep:movimientos}` | `p(95)<800` | 38.2 ms | ✓ |
| U-01 comision (S-03) | `http_req_duration{fase:base,ep:comision}` | `p(95)<800` | 13.1 ms | ✓ |
| U-01 contactos_listar (S-03) | `http_req_duration{fase:base,ep:contactos_listar}` | `p(95)<800` | 14.3 ms | ✓ |
| U-01 contactos_buscar (S-03) | `http_req_duration{fase:base,ep:contactos_buscar}` | `p(95)<800` | 6.6 ms | ✓ |
| U-01 recargas_config (S-03) | `http_req_duration{fase:base,ep:recargas_config}` | `p(95)<800` | 8.4 ms | ✓ |
| U-01 empresas (S-03) | `http_req_duration{fase:base,ep:empresas}` | `p(95)<800` | 12.6 ms | ✓ |
| U-01 deudas (S-03) | `http_req_duration{fase:base,ep:deudas}` | `p(95)<800` | 6.3 ms | ✓ |
| U-01 otras: 5 GET al 2 % (§3.3) | `http_req_duration{fase:base,op:otras}` | `p(95)<800` | 12.4 ms | ✓ |
| U-02 operaciones de dinero (grupo) | `http_req_duration{fase:base,grupo:dinero}` | `p(95)<1500` | 131.4 ms | ✓ |
| U-02 transferir (S-03) | `http_req_duration{fase:base,ep:transferir}` | `p(95)<1500` | 134.2 ms | ✓ |
| U-02 recargar (S-03) | `http_req_duration{fase:base,ep:recargar}` | `p(95)<1500` | 13.6 ms | ✓ |
| U-02 pagar (S-03) | `http_req_duration{fase:base,ep:pagar}` | `p(95)<1500` | 11.4 ms | ✓ |
| U-06 recuperación U-01 consultas e inicio de sesión (grupo) | `http_req_duration{fase:recuperacion,grupo:consulta}` | `p(95)<800` | 92.6 ms | ✓ |
| U-06 recuperación U-01 login (S-03) | `http_req_duration{fase:recuperacion,ep:login}` | `p(95)<800` | 103.6 ms | ✓ |
| U-06 recuperación U-01 saldo (S-03) | `http_req_duration{fase:recuperacion,ep:saldo}` | `p(95)<800` | 11.6 ms | ✓ |
| U-06 recuperación U-01 perfil (S-03) | `http_req_duration{fase:recuperacion,ep:perfil}` | `p(95)<800` | 4.6 ms | ✓ |
| U-06 recuperación U-01 movimientos (S-03) | `http_req_duration{fase:recuperacion,ep:movimientos}` | `p(95)<800` | 36.1 ms | ✓ |
| U-06 recuperación U-01 comision (S-03) | `http_req_duration{fase:recuperacion,ep:comision}` | `p(95)<800` | 11.5 ms | ✓ |
| U-06 recuperación U-01 contactos_listar (S-03) | `http_req_duration{fase:recuperacion,ep:contactos_listar}` | `p(95)<800` | 13.4 ms | ✓ |
| U-06 recuperación U-01 contactos_buscar (S-03) | `http_req_duration{fase:recuperacion,ep:contactos_buscar}` | `p(95)<800` | 5.9 ms | ✓ |
| U-06 recuperación U-01 recargas_config (S-03) | `http_req_duration{fase:recuperacion,ep:recargas_config}` | `p(95)<800` | 10.3 ms | ✓ |
| U-06 recuperación U-01 empresas (S-03) | `http_req_duration{fase:recuperacion,ep:empresas}` | `p(95)<800` | 11.3 ms | ✓ |
| U-06 recuperación U-01 deudas (S-03) | `http_req_duration{fase:recuperacion,ep:deudas}` | `p(95)<800` | 6.7 ms | ✓ |
| U-06 recuperación U-01 otras: 5 GET al 2 % (§3.3) | `http_req_duration{fase:recuperacion,op:otras}` | `p(95)<800` | 12.1 ms | ✓ |
| U-06 recuperación U-02 operaciones de dinero (grupo) | `http_req_duration{fase:recuperacion,grupo:dinero}` | `p(95)<1500` | 126.6 ms | ✓ |
| U-06 recuperación U-02 transferir (S-03) | `http_req_duration{fase:recuperacion,ep:transferir}` | `p(95)<1500` | 131.1 ms | ✓ |
| U-06 recuperación U-02 recargar (S-03) | `http_req_duration{fase:recuperacion,ep:recargar}` | `p(95)<1500` | 11.7 ms | ✓ |
| U-06 recuperación U-02 pagar (S-03) | `http_req_duration{fase:recuperacion,ep:pagar}` | `p(95)<1500` | 10.8 ms | ✓ |
