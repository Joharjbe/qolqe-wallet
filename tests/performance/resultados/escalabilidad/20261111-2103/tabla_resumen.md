# Tabla resumen · estres · 20261111-2103

Formato de S14. Tiempos en ms (percentil por rango más cercano). Error de rendimiento = 5xx y status 0; error de datos = 4xx de regla de negocio (se reportan por separado, enunciado §5).

## rampa y meseta

| Endpoint | Peticiones | Promedio | p50 | p90 | p95 | p99 | Error rend. | Error datos | Throughput (req/s) |
|---|---|---|---|---|---|---|---|---|---|
| `login` POST /api/auth/login | 9,572 | 13,402 | 81 | 30,002 | 30,002 | 30,003 | 44.87 % | 0.00 % | 6.38 |
| `alertas` GET /api/limites/alertas | 668 | 3,776 | 2 | 30,000 | 30,001 | 30,002 | 12.57 % | 0.00 % | 0.45 |
| `comision` GET /api/transferencias/comision | 4,863 | 3,875 | 2 | 30,000 | 30,001 | 30,002 | 12.85 % | 0.00 % | 3.24 |
| `contactos_buscar` GET /api/contactos?buscar | 3,085 | 3,924 | 2 | 30,000 | 30,001 | 30,002 | 13.03 % | 0.00 % | 2.06 |
| `contactos_listar` GET /api/contactos | 3,099 | 4,003 | 3 | 30,000 | 30,001 | 30,002 | 13.29 % | 0.00 % | 2.07 |
| `deudas` GET /api/servicios/deudas | 2,850 | 615 | 2 | 4 | 5 | 30,001 | 2.00 % | 0.00 % | 1.90 |
| `dispositivos` GET /api/seguridad/dispositivos | 626 | 4,343 | 2 | 30,000 | 30,001 | 30,002 | 14.38 % | 0.00 % | 0.42 |
| `empresas` GET /api/servicios/empresas | 3,212 | 3,832 | 2 | 30,000 | 30,001 | 30,002 | 11.27 % | 0.00 % | 2.14 |
| `limites` GET /api/limites | 653 | 3,382 | 2 | 30,000 | 30,001 | 30,002 | 11.18 % | 0.00 % | 0.44 |
| `movimientos` GET /api/movimientos | 4,679 | 3,876 | 17 | 30,000 | 30,001 | 30,002 | 12.70 % | 0.00 % | 3.12 |
| `perfil` GET /api/cuentas/me | 9,602 | 3,868 | 2 | 30,000 | 30,001 | 30,002 | 12.86 % | 0.00 % | 6.40 |
| `recargas_config` GET /api/recargas/configuracion | 3,109 | 3,614 | 1 | 30,000 | 30,001 | 30,002 | 10.65 % | 0.00 % | 2.07 |
| `saldo` GET /api/cuentas/me/saldo | 9,640 | 3,916 | 2 | 30,000 | 30,001 | 30,002 | 12.96 % | 0.00 % | 6.43 |
| `sesiones` GET /api/seguridad/sesiones | 631 | 4,179 | 2 | 30,000 | 30,001 | 30,002 | 13.79 % | 0.00 % | 0.42 |
| `solicitudes` GET /api/solicitudes | 634 | 3,961 | 2 | 30,000 | 30,001 | 30,002 | 13.09 % | 0.00 % | 0.42 |
| `pagar` POST /api/servicios/pagos | 1,100 | 5 | 4 | 6 | 8 | 12 | 0.00 % | 0.00 % | 0.73 |
| `recargar` POST /api/recargas | 2,778 | 749 | 4 | 7 | 10 | 30,001 | 2.70 % | 0.00 % | 1.85 |
| `transferir` POST /api/transferencias | 4,238 | 212 | 88 | 119 | 124 | 168 | 0.61 % | 0.00 % | 2.83 |
| **grupo consulta** | 56,923 | 5,315 | 2 | 30,001 | 30,002 | 30,002 | 17.53 % | 0.00 % | 37.95 |
| **grupo dinero** | 8,116 | 368 | 51 | 114 | 121 | 18,274 | 1.24 % | 0.00 % | 5.41 |
| **total** | 65,039 | 4,698 | 3 | 30,000 | 30,001 | 30,002 | 15.50 % | 0.00 % | 43.36 |
