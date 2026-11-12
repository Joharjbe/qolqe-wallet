# Tabla resumen · carga · 20261111-1833

Formato de S14. Tiempos en ms (percentil por rango más cercano). Error de rendimiento = 5xx y status 0; error de datos = 4xx de regla de negocio (se reportan por separado, enunciado §5).

## estable

| Endpoint | Peticiones | Promedio | p50 | p90 | p95 | p99 | Error rend. | Error datos | Throughput (req/s) |
|---|---|---|---|---|---|---|---|---|---|
| `login` POST /api/auth/login | 750 | 91 | 93 | 103 | 105 | 109 | 0.00 % | 0.00 % | 0.83 |
| `alertas` GET /api/limites/alertas | 89 | 6 | 6 | 11 | 12 | 14 | 0.00 % | 0.00 % | 0.10 |
| `comision` GET /api/transferencias/comision | 639 | 6 | 6 | 11 | 12 | 16 | 0.00 % | 0.00 % | 0.71 |
| `contactos_buscar` GET /api/contactos?buscar | 483 | 4 | 4 | 6 | 8 | 10 | 0.00 % | 0.00 % | 0.54 |
| `contactos_listar` GET /api/contactos | 483 | 8 | 7 | 13 | 14 | 19 | 0.00 % | 0.00 % | 0.54 |
| `deudas` GET /api/servicios/deudas | 449 | 4 | 4 | 7 | 7 | 11 | 0.00 % | 0.00 % | 0.50 |
| `dispositivos` GET /api/seguridad/dispositivos | 94 | 7 | 6 | 10 | 12 | 16 | 0.00 % | 0.00 % | 0.10 |
| `empresas` GET /api/servicios/empresas | 449 | 6 | 5 | 11 | 12 | 17 | 0.00 % | 0.00 % | 0.50 |
| `limites` GET /api/limites | 83 | 7 | 6 | 12 | 12 | 18 | 0.00 % | 0.00 % | 0.09 |
| `movimientos` GET /api/movimientos | 689 | 25 | 22 | 36 | 38 | 46 | 0.00 % | 0.00 % | 0.77 |
| `perfil` GET /api/cuentas/me | 1,339 | 3 | 3 | 5 | 6 | 8 | 0.00 % | 0.00 % | 1.49 |
| `recargas_config` GET /api/recargas/configuracion | 463 | 4 | 3 | 8 | 9 | 14 | 0.00 % | 0.00 % | 0.51 |
| `saldo` GET /api/cuentas/me/saldo | 1,339 | 7 | 6 | 11 | 13 | 16 | 0.00 % | 0.00 % | 1.49 |
| `sesiones` GET /api/seguridad/sesiones | 84 | 7 | 6 | 12 | 12 | 15 | 0.00 % | 0.00 % | 0.09 |
| `solicitudes` GET /api/solicitudes | 83 | 6 | 6 | 11 | 12 | 21 | 0.00 % | 0.00 % | 0.09 |
| `pagar` POST /api/servicios/pagos | 178 | 8 | 7 | 10 | 12 | 17 | 0.00 % | 0.00 % | 0.20 |
| `recargar` POST /api/recargas | 463 | 9 | 8 | 12 | 13 | 18 | 0.00 % | 0.00 % | 0.51 |
| `transferir` POST /api/transferencias | 639 | 96 | 95 | 128 | 134 | 144 | 0.00 % | 0.00 % | 0.71 |
| **grupo consulta** | 7,516 | 16 | 5 | 72 | 93 | 103 | 0.00 % | 0.00 % | 8.35 |
| **grupo dinero** | 1,280 | 52 | 25 | 120 | 128 | 140 | 0.00 % | 0.00 % | 1.42 |
| **total** | 8,796 | 21 | 6 | 85 | 101 | 126 | 0.00 % | 0.00 % | 9.77 |
