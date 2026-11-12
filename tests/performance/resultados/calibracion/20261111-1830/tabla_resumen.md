# Tabla resumen · calibracion · 20261111-1830

Formato de S14. Tiempos en ms (percentil por rango más cercano). Error de rendimiento = 5xx y status 0; error de datos = 4xx de regla de negocio (se reportan por separado, enunciado §5).

## toda la corrida

| Endpoint | Peticiones | Promedio | p50 | p90 | p95 | p99 | Error rend. | Error datos | Throughput (req/s) |
|---|---|---|---|---|---|---|---|---|---|
| `login` POST /api/auth/login | 40 | 81 | 81 | 93 | 93 | 95 | 0.00 % | 0.00 % | 0.31 |
| `alertas` GET /api/limites/alertas | 5 | 9 | 8 | 12 | 12 | 12 | 0.00 % | 0.00 % | 0.04 |
| `comision` GET /api/transferencias/comision | 35 | 9 | 9 | 13 | 15 | 17 | 0.00 % | 0.00 % | 0.27 |
| `contactos_buscar` GET /api/contactos?buscar | 20 | 4 | 4 | 7 | 7 | 7 | 0.00 % | 0.00 % | 0.15 |
| `contactos_listar` GET /api/contactos | 20 | 10 | 9 | 15 | 15 | 16 | 0.00 % | 0.00 % | 0.15 |
| `deudas` GET /api/servicios/deudas | 27 | 4 | 3 | 6 | 7 | 8 | 0.00 % | 0.00 % | 0.21 |
| `dispositivos` GET /api/seguridad/dispositivos | 5 | 12 | 12 | 16 | 16 | 16 | 0.00 % | 0.00 % | 0.04 |
| `empresas` GET /api/servicios/empresas | 27 | 8 | 7 | 11 | 12 | 19 | 0.00 % | 0.00 % | 0.21 |
| `limites` GET /api/limites | 2 | 9 | 7 | 11 | 11 | 11 | 0.00 % | 0.00 % | 0.02 |
| `movimientos` GET /api/movimientos | 38 | 27 | 23 | 37 | 39 | 39 | 0.00 % | 0.00 % | 0.29 |
| `perfil` GET /api/cuentas/me | 73 | 3 | 2 | 5 | 5 | 8 | 0.00 % | 0.00 % | 0.56 |
| `recargas_config` GET /api/recargas/configuracion | 24 | 7 | 7 | 10 | 14 | 14 | 0.00 % | 0.00 % | 0.18 |
| `saldo` GET /api/cuentas/me/saldo | 73 | 8 | 7 | 12 | 12 | 15 | 0.00 % | 0.00 % | 0.56 |
| `sesiones` GET /api/seguridad/sesiones | 7 | 10 | 9 | 13 | 13 | 13 | 0.00 % | 0.00 % | 0.05 |
| `solicitudes` GET /api/solicitudes | 4 | 11 | 10 | 13 | 13 | 13 | 0.00 % | 0.00 % | 0.03 |
| `pagar` POST /api/servicios/pagos | 11 | 8 | 8 | 10 | 11 | 11 | 0.00 % | 0.00 % | 0.08 |
| `recargar` POST /api/recargas | 24 | 10 | 11 | 13 | 14 | 16 | 0.00 % | 0.00 % | 0.18 |
| `transferir` POST /api/transferencias | 35 | 100 | 94 | 137 | 141 | 143 | 0.00 % | 0.00 % | 0.27 |
| **grupo consulta** | 400 | 16 | 7 | 39 | 81 | 93 | 0.00 % | 0.00 % | 3.05 |
| **grupo dinero** | 70 | 55 | 16 | 134 | 137 | 143 | 0.00 % | 0.00 % | 0.53 |
| **total** | 470 | 22 | 8 | 79 | 93 | 136 | 0.00 % | 0.00 % | 3.59 |
