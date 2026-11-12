# Tabla resumen · referencia · 20261111-1826

Formato de S14. Tiempos en ms (percentil por rango más cercano). Error de rendimiento = 5xx y status 0; error de datos = 4xx de regla de negocio (se reportan por separado, enunciado §5).

## toda la corrida

| Endpoint | Peticiones | Promedio | p50 | p90 | p95 | p99 | Error rend. | Error datos | Throughput (req/s) |
|---|---|---|---|---|---|---|---|---|---|
| `login` POST /api/auth/login | 5 | 78 | 73 | 94 | 94 | 94 | 0.00 % | 0.00 % | 0.08 |
| `alertas` GET /api/limites/alertas | 5 | 8 | 8 | 12 | 12 | 12 | 0.00 % | 0.00 % | 0.08 |
| `comision` GET /api/transferencias/comision | 5 | 9 | 9 | 12 | 12 | 12 | 0.00 % | 0.00 % | 0.08 |
| `contactos_buscar` GET /api/contactos?buscar | 5 | 4 | 4 | 5 | 5 | 5 | 0.00 % | 0.00 % | 0.08 |
| `contactos_listar` GET /api/contactos | 5 | 10 | 10 | 13 | 13 | 13 | 0.00 % | 0.00 % | 0.08 |
| `deudas` GET /api/servicios/deudas | 10 | 4 | 5 | 6 | 7 | 7 | 0.00 % | 0.00 % | 0.16 |
| `dispositivos` GET /api/seguridad/dispositivos | 5 | 7 | 6 | 11 | 11 | 11 | 0.00 % | 0.00 % | 0.08 |
| `empresas` GET /api/servicios/empresas | 10 | 8 | 6 | 9 | 14 | 14 | 0.00 % | 0.00 % | 0.16 |
| `limites` GET /api/limites | 5 | 10 | 9 | 15 | 15 | 15 | 0.00 % | 0.00 % | 0.08 |
| `movimientos` GET /api/movimientos | 5 | 39 | 31 | 91 | 91 | 91 | 0.00 % | 0.00 % | 0.08 |
| `perfil` GET /api/cuentas/me | 5 | 3 | 3 | 4 | 4 | 4 | 0.00 % | 0.00 % | 0.08 |
| `recargas_config` GET /api/recargas/configuracion | 5 | 6 | 8 | 9 | 9 | 9 | 0.00 % | 0.00 % | 0.08 |
| `saldo` GET /api/cuentas/me/saldo | 5 | 9 | 9 | 11 | 11 | 11 | 0.00 % | 0.00 % | 0.08 |
| `sesiones` GET /api/seguridad/sesiones | 5 | 8 | 7 | 15 | 15 | 15 | 0.00 % | 0.00 % | 0.08 |
| `solicitudes` GET /api/solicitudes | 5 | 9 | 7 | 12 | 12 | 12 | 0.00 % | 0.00 % | 0.08 |
| `pagar` POST /api/servicios/pagos | 5 | 8 | 7 | 10 | 10 | 10 | 0.00 % | 0.00 % | 0.08 |
| `recargar` POST /api/recargas | 5 | 9 | 7 | 13 | 13 | 13 | 0.00 % | 0.00 % | 0.08 |
| `transferir` POST /api/transferencias | 5 | 97 | 101 | 127 | 127 | 127 | 0.00 % | 0.00 % | 0.08 |
| **grupo consulta** | 85 | 13 | 7 | 21 | 72 | 94 | 0.00 % | 0.00 % | 1.37 |
| **grupo dinero** | 15 | 38 | 10 | 112 | 127 | 127 | 0.00 % | 0.00 % | 0.24 |
| **total** | 100 | 17 | 7 | 60 | 85 | 112 | 0.00 % | 0.00 % | 1.62 |
