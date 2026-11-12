# Tabla resumen · pico · 20261111-1852

Formato de S14. Tiempos en ms (percentil por rango más cercano). Error de rendimiento = 5xx y status 0; error de datos = 4xx de regla de negocio (se reportan por separado, enunciado §5).

## campaña

| Endpoint | Peticiones | Promedio | p50 | p90 | p95 | p99 | Error rend. | Error datos | Throughput (req/s) |
|---|---|---|---|---|---|---|---|---|---|
| `login` POST /api/auth/login | 1,250 | 90 | 90 | 102 | 104 | 113 | 0.00 % | 0.00 % | 1.39 |
| `alertas` GET /api/limites/alertas | 145 | 4 | 3 | 7 | 9 | 12 | 0.00 % | 0.00 % | 0.16 |
| `comision` GET /api/transferencias/comision | 1,131 | 5 | 3 | 9 | 11 | 14 | 0.00 % | 0.00 % | 1.26 |
| `contactos_buscar` GET /api/contactos?buscar | 742 | 4 | 3 | 5 | 6 | 8 | 0.00 % | 0.00 % | 0.82 |
| `contactos_listar` GET /api/contactos | 742 | 6 | 5 | 10 | 13 | 16 | 0.00 % | 0.00 % | 0.82 |
| `deudas` GET /api/servicios/deudas | 736 | 4 | 3 | 5 | 6 | 9 | 0.00 % | 0.00 % | 0.82 |
| `dispositivos` GET /api/seguridad/dispositivos | 156 | 5 | 3 | 9 | 10 | 15 | 0.00 % | 0.00 % | 0.17 |
| `empresas` GET /api/servicios/empresas | 736 | 4 | 3 | 8 | 10 | 12 | 0.00 % | 0.00 % | 0.82 |
| `limites` GET /api/limites | 142 | 5 | 4 | 10 | 11 | 13 | 0.00 % | 0.00 % | 0.16 |
| `movimientos` GET /api/movimientos | 1,124 | 23 | 21 | 32 | 36 | 42 | 0.00 % | 0.00 % | 1.25 |
| `perfil` GET /api/cuentas/me | 2,218 | 3 | 2 | 4 | 5 | 7 | 0.00 % | 0.00 % | 2.46 |
| `recargas_config` GET /api/recargas/configuracion | 776 | 3 | 2 | 6 | 8 | 13 | 0.00 % | 0.00 % | 0.86 |
| `saldo` GET /api/cuentas/me/saldo | 2,218 | 4 | 3 | 9 | 11 | 14 | 0.00 % | 0.00 % | 2.46 |
| `sesiones` GET /api/seguridad/sesiones | 168 | 5 | 3 | 9 | 11 | 13 | 0.00 % | 0.00 % | 0.19 |
| `solicitudes` GET /api/solicitudes | 160 | 5 | 4 | 11 | 12 | 17 | 0.00 % | 0.00 % | 0.18 |
| `pagar` POST /api/servicios/pagos | 289 | 7 | 6 | 9 | 10 | 17 | 0.00 % | 0.00 % | 0.32 |
| `recargar` POST /api/recargas | 776 | 7 | 7 | 11 | 11 | 15 | 0.00 % | 0.00 % | 0.86 |
| `transferir` POST /api/transferencias | 1,131 | 93 | 92 | 125 | 131 | 139 | 0.00 % | 0.00 % | 1.26 |
| **grupo consulta** | 12,444 | 14 | 4 | 72 | 90 | 102 | 0.00 % | 0.00 % | 13.83 |
| **grupo dinero** | 2,196 | 51 | 53 | 117 | 126 | 138 | 0.00 % | 0.00 % | 2.44 |
| **total** | 14,640 | 20 | 4 | 86 | 98 | 124 | 0.00 % | 0.00 % | 16.27 |

## base

| Endpoint | Peticiones | Promedio | p50 | p90 | p95 | p99 | Error rend. | Error datos | Throughput (req/s) |
|---|---|---|---|---|---|---|---|---|---|
| `login` POST /api/auth/login | 100 | 96 | 98 | 104 | 105 | 108 | 0.00 % | 0.00 % | 0.83 |
| `alertas` GET /api/limites/alertas | 14 | 7 | 7 | 11 | 17 | 17 | 0.00 % | 0.00 % | 0.12 |
| `comision` GET /api/transferencias/comision | 94 | 7 | 6 | 12 | 13 | 20 | 0.00 % | 0.00 % | 0.78 |
| `contactos_buscar` GET /api/contactos?buscar | 55 | 5 | 5 | 6 | 7 | 9 | 0.00 % | 0.00 % | 0.46 |
| `contactos_listar` GET /api/contactos | 55 | 9 | 8 | 14 | 15 | 16 | 0.00 % | 0.00 % | 0.46 |
| `deudas` GET /api/servicios/deudas | 55 | 5 | 5 | 6 | 6 | 8 | 0.00 % | 0.00 % | 0.46 |
| `dispositivos` GET /api/seguridad/dispositivos | 11 | 6 | 4 | 11 | 12 | 12 | 0.00 % | 0.00 % | 0.09 |
| `empresas` GET /api/servicios/empresas | 55 | 7 | 6 | 12 | 13 | 16 | 0.00 % | 0.00 % | 0.46 |
| `limites` GET /api/limites | 20 | 7 | 5 | 12 | 13 | 13 | 0.00 % | 0.00 % | 0.17 |
| `movimientos` GET /api/movimientos | 90 | 28 | 28 | 37 | 39 | 48 | 0.00 % | 0.00 % | 0.75 |
| `perfil` GET /api/cuentas/me | 183 | 3 | 3 | 5 | 6 | 8 | 0.00 % | 0.00 % | 1.52 |
| `recargas_config` GET /api/recargas/configuracion | 54 | 4 | 3 | 8 | 9 | 14 | 0.00 % | 0.00 % | 0.45 |
| `saldo` GET /api/cuentas/me/saldo | 182 | 7 | 6 | 12 | 13 | 17 | 0.00 % | 0.00 % | 1.52 |
| `sesiones` GET /api/seguridad/sesiones | 11 | 7 | 7 | 10 | 11 | 11 | 0.00 % | 0.00 % | 0.09 |
| `solicitudes` GET /api/solicitudes | 15 | 6 | 5 | 12 | 15 | 15 | 0.00 % | 0.00 % | 0.12 |
| `pagar` POST /api/servicios/pagos | 25 | 9 | 8 | 11 | 11 | 20 | 0.00 % | 0.00 % | 0.21 |
| `recargar` POST /api/recargas | 54 | 9 | 8 | 13 | 14 | 22 | 0.00 % | 0.00 % | 0.45 |
| `transferir` POST /api/transferencias | 94 | 102 | 105 | 131 | 135 | 143 | 0.00 % | 0.00 % | 0.78 |
| **grupo consulta** | 994 | 17 | 6 | 71 | 98 | 105 | 0.00 % | 0.00 % | 8.28 |
| **grupo dinero** | 173 | 59 | 68 | 128 | 132 | 142 | 0.00 % | 0.00 % | 1.44 |
| **total** | 1,167 | 23 | 6 | 95 | 104 | 130 | 0.00 % | 0.00 % | 9.72 |

## recuperación

| Endpoint | Peticiones | Promedio | p50 | p90 | p95 | p99 | Error rend. | Error datos | Throughput (req/s) |
|---|---|---|---|---|---|---|---|---|---|
| `login` POST /api/auth/login | 250 | 93 | 92 | 100 | 104 | 114 | 0.00 % | 0.00 % | 0.83 |
| `alertas` GET /api/limites/alertas | 25 | 6 | 5 | 11 | 12 | 12 | 0.00 % | 0.00 % | 0.08 |
| `comision` GET /api/transferencias/comision | 235 | 6 | 5 | 10 | 12 | 15 | 0.00 % | 0.00 % | 0.78 |
| `contactos_buscar` GET /api/contactos?buscar | 148 | 4 | 4 | 5 | 6 | 9 | 0.00 % | 0.00 % | 0.49 |
| `contactos_listar` GET /api/contactos | 148 | 7 | 6 | 12 | 14 | 17 | 0.00 % | 0.00 % | 0.49 |
| `deudas` GET /api/servicios/deudas | 134 | 4 | 4 | 6 | 7 | 10 | 0.00 % | 0.00 % | 0.45 |
| `dispositivos` GET /api/seguridad/dispositivos | 28 | 7 | 6 | 14 | 15 | 16 | 0.00 % | 0.00 % | 0.09 |
| `empresas` GET /api/servicios/empresas | 134 | 6 | 6 | 10 | 11 | 14 | 0.00 % | 0.00 % | 0.45 |
| `limites` GET /api/limites | 37 | 6 | 6 | 10 | 13 | 16 | 0.00 % | 0.00 % | 0.12 |
| `movimientos` GET /api/movimientos | 225 | 25 | 24 | 33 | 36 | 41 | 0.00 % | 0.00 % | 0.75 |
| `perfil` GET /api/cuentas/me | 428 | 3 | 3 | 4 | 5 | 7 | 0.00 % | 0.00 % | 1.43 |
| `recargas_config` GET /api/recargas/configuracion | 171 | 5 | 3 | 8 | 11 | 20 | 0.00 % | 0.00 % | 0.57 |
| `saldo` GET /api/cuentas/me/saldo | 428 | 6 | 6 | 10 | 12 | 19 | 0.00 % | 0.00 % | 1.43 |
| `sesiones` GET /api/seguridad/sesiones | 23 | 6 | 5 | 11 | 12 | 13 | 0.00 % | 0.00 % | 0.08 |
| `solicitudes` GET /api/solicitudes | 46 | 7 | 6 | 11 | 12 | 17 | 0.00 % | 0.00 % | 0.15 |
| `pagar` POST /api/servicios/pagos | 54 | 8 | 7 | 10 | 11 | 17 | 0.00 % | 0.00 % | 0.18 |
| `recargar` POST /api/recargas | 171 | 8 | 8 | 11 | 12 | 13 | 0.00 % | 0.00 % | 0.57 |
| `transferir` POST /api/transferencias | 235 | 93 | 93 | 127 | 131 | 138 | 0.00 % | 0.00 % | 0.78 |
| **grupo consulta** | 2,460 | 16 | 5 | 78 | 93 | 101 | 0.00 % | 0.00 % | 8.20 |
| **grupo dinero** | 460 | 51 | 51 | 119 | 127 | 137 | 0.00 % | 0.00 % | 1.53 |
| **total** | 2,920 | 21 | 6 | 90 | 98 | 125 | 0.00 % | 0.00 % | 9.73 |
