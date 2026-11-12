# Tabla resumen · referencia · 20261111-1828

Formato de S14. Tiempos en ms (percentil por rango más cercano). Error de rendimiento = 5xx y status 0; error de datos = 4xx de regla de negocio (se reportan por separado, enunciado §5).

## toda la corrida

| Endpoint | Peticiones | Promedio | p50 | p90 | p95 | p99 | Error rend. | Error datos | Throughput (req/s) |
|---|---|---|---|---|---|---|---|---|---|
| `login` POST /api/auth/login | 5 | 83 | 87 | 92 | 92 | 92 | 0.00 % | 0.00 % | 0.08 |
| `alertas` GET /api/limites/alertas | 5 | 12 | 11 | 15 | 15 | 15 | 0.00 % | 0.00 % | 0.08 |
| `comision` GET /api/transferencias/comision | 5 | 10 | 11 | 12 | 12 | 12 | 0.00 % | 0.00 % | 0.08 |
| `contactos_buscar` GET /api/contactos?buscar | 5 | 6 | 6 | 6 | 6 | 6 | 0.00 % | 0.00 % | 0.08 |
| `contactos_listar` GET /api/contactos | 5 | 13 | 13 | 17 | 17 | 17 | 0.00 % | 0.00 % | 0.08 |
| `deudas` GET /api/servicios/deudas | 10 | 6 | 6 | 6 | 7 | 7 | 0.00 % | 0.00 % | 0.16 |
| `dispositivos` GET /api/seguridad/dispositivos | 5 | 12 | 10 | 19 | 19 | 19 | 0.00 % | 0.00 % | 0.08 |
| `empresas` GET /api/servicios/empresas | 10 | 11 | 10 | 14 | 15 | 15 | 0.00 % | 0.00 % | 0.16 |
| `limites` GET /api/limites | 5 | 12 | 12 | 15 | 15 | 15 | 0.00 % | 0.00 % | 0.08 |
| `movimientos` GET /api/movimientos | 5 | 33 | 33 | 35 | 35 | 35 | 0.00 % | 0.00 % | 0.08 |
| `perfil` GET /api/cuentas/me | 5 | 4 | 4 | 5 | 5 | 5 | 0.00 % | 0.00 % | 0.08 |
| `recargas_config` GET /api/recargas/configuracion | 5 | 8 | 9 | 11 | 11 | 11 | 0.00 % | 0.00 % | 0.08 |
| `saldo` GET /api/cuentas/me/saldo | 5 | 12 | 10 | 17 | 17 | 17 | 0.00 % | 0.00 % | 0.08 |
| `sesiones` GET /api/seguridad/sesiones | 5 | 11 | 11 | 13 | 13 | 13 | 0.00 % | 0.00 % | 0.08 |
| `solicitudes` GET /api/solicitudes | 5 | 11 | 11 | 12 | 12 | 12 | 0.00 % | 0.00 % | 0.08 |
| `pagar` POST /api/servicios/pagos | 5 | 10 | 10 | 11 | 11 | 11 | 0.00 % | 0.00 % | 0.08 |
| `recargar` POST /api/recargas | 5 | 12 | 12 | 13 | 13 | 13 | 0.00 % | 0.00 % | 0.08 |
| `transferir` POST /api/transferencias | 5 | 119 | 124 | 136 | 136 | 136 | 0.00 % | 0.00 % | 0.08 |
| **grupo consulta** | 85 | 15 | 10 | 32 | 70 | 92 | 0.00 % | 0.00 % | 1.37 |
| **grupo dinero** | 15 | 47 | 12 | 134 | 136 | 136 | 0.00 % | 0.00 % | 0.24 |
| **total** | 100 | 20 | 11 | 35 | 90 | 134 | 0.00 % | 0.00 % | 1.61 |
