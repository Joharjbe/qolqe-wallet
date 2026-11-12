# Tabla resumen · pico · 20261111-1918

Formato de S14. Tiempos en ms (percentil por rango más cercano). Error de rendimiento = 5xx y status 0; error de datos = 4xx de regla de negocio (se reportan por separado, enunciado §5).

## campaña

| Endpoint | Peticiones | Promedio | p50 | p90 | p95 | p99 | Error rend. | Error datos | Throughput (req/s) |
|---|---|---|---|---|---|---|---|---|---|
| `login` POST /api/auth/login | 1,250 | 81 | 78 | 90 | 97 | 134 | 0.00 % | 0.00 % | 1.39 |
| `alertas` GET /api/limites/alertas | 166 | 4 | 3 | 7 | 9 | 12 | 0.00 % | 0.00 % | 0.18 |
| `comision` GET /api/transferencias/comision | 1,115 | 4 | 3 | 7 | 8 | 12 | 0.00 % | 0.00 % | 1.24 |
| `contactos_buscar` GET /api/contactos?buscar | 754 | 4 | 3 | 7 | 8 | 11 | 0.00 % | 0.00 % | 0.84 |
| `contactos_listar` GET /api/contactos | 754 | 5 | 4 | 8 | 10 | 13 | 0.00 % | 0.00 % | 0.84 |
| `deudas` GET /api/servicios/deudas | 728 | 3 | 3 | 6 | 7 | 10 | 0.00 % | 0.00 % | 0.81 |
| `dispositivos` GET /api/seguridad/dispositivos | 170 | 4 | 3 | 7 | 8 | 10 | 0.00 % | 0.00 % | 0.19 |
| `empresas` GET /api/servicios/empresas | 728 | 4 | 2 | 6 | 7 | 10 | 0.00 % | 0.00 % | 0.81 |
| `limites` GET /api/limites | 153 | 4 | 3 | 7 | 8 | 12 | 0.00 % | 0.00 % | 0.17 |
| `movimientos` GET /api/movimientos | 1,145 | 20 | 18 | 29 | 34 | 55 | 0.00 % | 0.00 % | 1.27 |
| `perfil` GET /api/cuentas/me | 2,208 | 3 | 2 | 5 | 6 | 10 | 0.00 % | 0.00 % | 2.45 |
| `recargas_config` GET /api/recargas/configuracion | 759 | 3 | 2 | 5 | 6 | 9 | 0.00 % | 0.00 % | 0.84 |
| `saldo` GET /api/cuentas/me/saldo | 2,208 | 4 | 3 | 7 | 8 | 12 | 0.00 % | 0.00 % | 2.45 |
| `sesiones` GET /api/seguridad/sesiones | 135 | 5 | 3 | 7 | 8 | 10 | 0.00 % | 0.00 % | 0.15 |
| `solicitudes` GET /api/solicitudes | 146 | 4 | 3 | 7 | 8 | 10 | 0.00 % | 0.00 % | 0.16 |
| `pagar` POST /api/servicios/pagos | 292 | 7 | 5 | 11 | 13 | 19 | 0.00 % | 0.00 % | 0.32 |
| `recargar` POST /api/recargas | 759 | 7 | 6 | 11 | 14 | 21 | 0.00 % | 0.00 % | 0.84 |
| `transferir` POST /api/transferencias | 1,115 | 91 | 91 | 123 | 126 | 134 | 0.00 % | 0.00 % | 1.24 |
| **grupo consulta** | 12,419 | 13 | 3 | 73 | 78 | 91 | 0.00 % | 0.00 % | 13.80 |
| **grupo dinero** | 2,166 | 50 | 51 | 116 | 123 | 131 | 0.00 % | 0.00 % | 2.41 |
| **total** | 14,585 | 18 | 4 | 77 | 89 | 121 | 0.00 % | 0.00 % | 16.21 |

## base

| Endpoint | Peticiones | Promedio | p50 | p90 | p95 | p99 | Error rend. | Error datos | Throughput (req/s) |
|---|---|---|---|---|---|---|---|---|---|
| `login` POST /api/auth/login | 100 | 82 | 80 | 88 | 91 | 100 | 0.00 % | 0.00 % | 0.83 |
| `alertas` GET /api/limites/alertas | 11 | 6 | 6 | 8 | 14 | 14 | 0.00 % | 0.00 % | 0.09 |
| `comision` GET /api/transferencias/comision | 91 | 5 | 6 | 7 | 7 | 8 | 0.00 % | 0.00 % | 0.76 |
| `contactos_buscar` GET /api/contactos?buscar | 55 | 3 | 3 | 4 | 6 | 7 | 0.00 % | 0.00 % | 0.46 |
| `contactos_listar` GET /api/contactos | 55 | 6 | 7 | 8 | 8 | 13 | 0.00 % | 0.00 % | 0.46 |
| `deudas` GET /api/servicios/deudas | 65 | 3 | 3 | 4 | 5 | 7 | 0.00 % | 0.00 % | 0.54 |
| `dispositivos` GET /api/seguridad/dispositivos | 15 | 5 | 5 | 7 | 11 | 11 | 0.00 % | 0.00 % | 0.12 |
| `empresas` GET /api/servicios/empresas | 65 | 4 | 5 | 6 | 7 | 7 | 0.00 % | 0.00 % | 0.54 |
| `limites` GET /api/limites | 15 | 5 | 5 | 7 | 7 | 7 | 0.00 % | 0.00 % | 0.12 |
| `movimientos` GET /api/movimientos | 89 | 18 | 18 | 24 | 26 | 35 | 0.00 % | 0.00 % | 0.74 |
| `perfil` GET /api/cuentas/me | 191 | 2 | 2 | 3 | 4 | 6 | 0.00 % | 0.00 % | 1.59 |
| `recargas_config` GET /api/recargas/configuracion | 55 | 3 | 3 | 5 | 5 | 6 | 0.00 % | 0.00 % | 0.46 |
| `saldo` GET /api/cuentas/me/saldo | 191 | 5 | 5 | 7 | 7 | 9 | 0.00 % | 0.00 % | 1.59 |
| `sesiones` GET /api/seguridad/sesiones | 15 | 6 | 7 | 8 | 8 | 8 | 0.00 % | 0.00 % | 0.12 |
| `solicitudes` GET /api/solicitudes | 12 | 4 | 3 | 6 | 7 | 7 | 0.00 % | 0.00 % | 0.10 |
| `pagar` POST /api/servicios/pagos | 20 | 6 | 5 | 8 | 9 | 13 | 0.00 % | 0.00 % | 0.17 |
| `recargar` POST /api/recargas | 55 | 7 | 6 | 10 | 11 | 13 | 0.00 % | 0.00 % | 0.46 |
| `transferir` POST /api/transferencias | 91 | 94 | 97 | 123 | 132 | 138 | 0.00 % | 0.00 % | 0.76 |
| **grupo consulta** | 1,025 | 13 | 4 | 26 | 80 | 88 | 0.00 % | 0.00 % | 8.54 |
| **grupo dinero** | 166 | 54 | 57 | 118 | 123 | 138 | 0.00 % | 0.00 % | 1.38 |
| **total** | 1,191 | 19 | 5 | 80 | 91 | 121 | 0.00 % | 0.00 % | 9.93 |

## recuperación

| Endpoint | Peticiones | Promedio | p50 | p90 | p95 | p99 | Error rend. | Error datos | Throughput (req/s) |
|---|---|---|---|---|---|---|---|---|---|
| `login` POST /api/auth/login | 250 | 83 | 80 | 92 | 97 | 129 | 0.00 % | 0.00 % | 0.83 |
| `alertas` GET /api/limites/alertas | 32 | 5 | 5 | 7 | 9 | 11 | 0.00 % | 0.00 % | 0.11 |
| `comision` GET /api/transferencias/comision | 220 | 5 | 6 | 8 | 8 | 11 | 0.00 % | 0.00 % | 0.73 |
| `contactos_buscar` GET /api/contactos?buscar | 159 | 4 | 3 | 6 | 8 | 11 | 0.00 % | 0.00 % | 0.53 |
| `contactos_listar` GET /api/contactos | 159 | 6 | 7 | 9 | 10 | 13 | 0.00 % | 0.00 % | 0.53 |
| `deudas` GET /api/servicios/deudas | 132 | 3 | 3 | 4 | 7 | 10 | 0.00 % | 0.00 % | 0.44 |
| `dispositivos` GET /api/seguridad/dispositivos | 31 | 5 | 5 | 7 | 7 | 7 | 0.00 % | 0.00 % | 0.10 |
| `empresas` GET /api/servicios/empresas | 132 | 5 | 5 | 8 | 8 | 11 | 0.00 % | 0.00 % | 0.44 |
| `limites` GET /api/limites | 31 | 5 | 6 | 8 | 8 | 12 | 0.00 % | 0.00 % | 0.10 |
| `movimientos` GET /api/movimientos | 233 | 21 | 19 | 27 | 33 | 52 | 0.00 % | 0.00 % | 0.78 |
| `perfil` GET /api/cuentas/me | 451 | 3 | 2 | 4 | 7 | 9 | 0.00 % | 0.00 % | 1.50 |
| `recargas_config` GET /api/recargas/configuracion | 150 | 4 | 4 | 6 | 7 | 13 | 0.00 % | 0.00 % | 0.50 |
| `saldo` GET /api/cuentas/me/saldo | 451 | 5 | 6 | 8 | 9 | 14 | 0.00 % | 0.00 % | 1.50 |
| `sesiones` GET /api/seguridad/sesiones | 25 | 6 | 6 | 9 | 10 | 14 | 0.00 % | 0.00 % | 0.08 |
| `solicitudes` GET /api/solicitudes | 30 | 5 | 5 | 9 | 10 | 10 | 0.00 % | 0.00 % | 0.10 |
| `pagar` POST /api/servicios/pagos | 48 | 7 | 6 | 14 | 16 | 38 | 0.00 % | 0.00 % | 0.16 |
| `recargar` POST /api/recargas | 150 | 8 | 6 | 11 | 15 | 22 | 0.00 % | 0.00 % | 0.50 |
| `transferir` POST /api/transferencias | 220 | 91 | 90 | 122 | 125 | 130 | 0.00 % | 0.00 % | 0.73 |
| **grupo consulta** | 2,486 | 14 | 5 | 73 | 80 | 93 | 0.00 % | 0.00 % | 8.29 |
| **grupo dinero** | 418 | 51 | 54 | 117 | 123 | 128 | 0.00 % | 0.00 % | 1.39 |
| **total** | 2,904 | 19 | 6 | 80 | 88 | 121 | 0.00 % | 0.00 % | 9.68 |
