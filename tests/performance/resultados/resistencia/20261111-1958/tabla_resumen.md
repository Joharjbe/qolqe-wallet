# Tabla resumen · resistencia · 20261111-1958

Formato de S14. Tiempos en ms (percentil por rango más cercano). Error de rendimiento = 5xx y status 0; error de datos = 4xx de regla de negocio (se reportan por separado, enunciado §5).

## estable

| Endpoint | Peticiones | Promedio | p50 | p90 | p95 | p99 | Error rend. | Error datos | Throughput (req/s) |
|---|---|---|---|---|---|---|---|---|---|
| `login` POST /api/auth/login | 3,000 | 94 | 95 | 103 | 106 | 123 | 0.00 % | 0.00 % | 0.83 |
| `alertas` GET /api/limites/alertas | 342 | 6 | 6 | 9 | 10 | 14 | 0.00 % | 0.00 % | 0.10 |
| `comision` GET /api/transferencias/comision | 2,695 | 6 | 6 | 10 | 11 | 15 | 0.00 % | 0.00 % | 0.75 |
| `contactos_buscar` GET /api/contactos?buscar | 1,791 | 4 | 4 | 6 | 6 | 8 | 0.00 % | 0.00 % | 0.50 |
| `contactos_listar` GET /api/contactos | 1,791 | 7 | 7 | 12 | 13 | 16 | 0.00 % | 0.00 % | 0.50 |
| `deudas` GET /api/servicios/deudas | 1,782 | 4 | 4 | 6 | 6 | 9 | 0.00 % | 0.00 % | 0.49 |
| `dispositivos` GET /api/seguridad/dispositivos | 375 | 6 | 5 | 10 | 11 | 14 | 0.00 % | 0.00 % | 0.10 |
| `empresas` GET /api/servicios/empresas | 1,782 | 5 | 5 | 9 | 10 | 14 | 0.00 % | 0.00 % | 0.49 |
| `limites` GET /api/limites | 380 | 6 | 6 | 10 | 11 | 14 | 0.00 % | 0.00 % | 0.11 |
| `movimientos` GET /api/movimientos | 2,703 | 27 | 26 | 37 | 39 | 45 | 0.00 % | 0.00 % | 0.75 |
| `perfil` GET /api/cuentas/me | 5,403 | 3 | 3 | 4 | 5 | 7 | 0.00 % | 0.00 % | 1.50 |
| `recargas_config` GET /api/recargas/configuracion | 1,804 | 4 | 3 | 7 | 8 | 12 | 0.00 % | 0.00 % | 0.50 |
| `saldo` GET /api/cuentas/me/saldo | 5,403 | 6 | 5 | 10 | 11 | 15 | 0.00 % | 0.00 % | 1.50 |
| `sesiones` GET /api/seguridad/sesiones | 363 | 6 | 6 | 10 | 11 | 18 | 0.00 % | 0.00 % | 0.10 |
| `solicitudes` GET /api/solicitudes | 359 | 6 | 6 | 10 | 11 | 16 | 0.00 % | 0.00 % | 0.10 |
| `pagar` POST /api/servicios/pagos | 710 | 7 | 7 | 10 | 11 | 13 | 0.00 % | 0.00 % | 0.20 |
| `recargar` POST /api/recargas | 1,804 | 8 | 8 | 12 | 12 | 15 | 0.00 % | 0.00 % | 0.50 |
| `transferir` POST /api/transferencias | 2,695 | 94 | 94 | 126 | 130 | 137 | 0.00 % | 0.00 % | 0.75 |
| **grupo consulta** | 29,973 | 16 | 5 | 72 | 95 | 103 | 0.00 % | 0.00 % | 8.33 |
| **grupo dinero** | 5,209 | 53 | 55 | 119 | 127 | 134 | 0.00 % | 0.00 % | 1.45 |
| **total** | 35,182 | 21 | 6 | 90 | 101 | 125 | 0.00 % | 0.00 % | 9.77 |
