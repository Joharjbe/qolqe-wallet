# Tabla resumen · estres · 20261111-1940

Formato de S14. Tiempos en ms (percentil por rango más cercano). Error de rendimiento = 5xx y status 0; error de datos = 4xx de regla de negocio (se reportan por separado, enunciado §5).

## rampa y meseta

| Endpoint | Peticiones | Promedio | p50 | p90 | p95 | p99 | Error rend. | Error datos | Throughput (req/s) |
|---|---|---|---|---|---|---|---|---|---|
| `login` POST /api/auth/login | 4,393 | 12,456 | 78 | 30,002 | 30,002 | 30,002 | 42.07 % | 0.00 % | 2.93 |
| `alertas` GET /api/limites/alertas | 273 | 4,551 | 2 | 30,000 | 30,001 | 30,002 | 15.02 % | 0.00 % | 0.18 |
| `comision` GET /api/transferencias/comision | 2,247 | 4,208 | 2 | 30,000 | 30,001 | 30,002 | 13.35 % | 0.00 % | 1.50 |
| `contactos_buscar` GET /api/contactos?buscar | 1,502 | 4,509 | 2 | 30,001 | 30,001 | 30,002 | 14.91 % | 0.00 % | 1.00 |
| `contactos_listar` GET /api/contactos | 1,529 | 4,879 | 3 | 30,001 | 30,001 | 30,002 | 15.70 % | 0.00 % | 1.02 |
| `deudas` GET /api/servicios/deudas | 1,307 | 1,281 | 2 | 5 | 720 | 30,002 | 3.98 % | 0.00 % | 0.87 |
| `dispositivos` GET /api/seguridad/dispositivos | 290 | 4,755 | 2 | 30,001 | 30,002 | 30,002 | 14.83 % | 0.00 % | 0.19 |
| `empresas` GET /api/servicios/empresas | 1,487 | 4,347 | 2 | 30,000 | 30,001 | 30,002 | 12.10 % | 0.00 % | 0.99 |
| `limites` GET /api/limites | 332 | 3,629 | 2 | 30,000 | 30,001 | 30,003 | 11.75 % | 0.00 % | 0.22 |
| `movimientos` GET /api/movimientos | 2,280 | 4,276 | 17 | 30,000 | 30,001 | 30,002 | 13.16 % | 0.00 % | 1.52 |
| `perfil` GET /api/cuentas/me | 4,305 | 4,271 | 2 | 30,000 | 30,001 | 30,002 | 14.05 % | 0.00 % | 2.87 |
| `recargas_config` GET /api/recargas/configuracion | 1,508 | 3,906 | 1 | 30,000 | 30,001 | 30,002 | 10.28 % | 0.00 % | 1.01 |
| `saldo` GET /api/cuentas/me/saldo | 4,394 | 4,622 | 2 | 30,000 | 30,001 | 30,002 | 14.59 % | 0.00 % | 2.93 |
| `sesiones` GET /api/seguridad/sesiones | 310 | 4,590 | 2 | 30,001 | 30,002 | 30,002 | 14.52 % | 0.00 % | 0.21 |
| `solicitudes` GET /api/solicitudes | 279 | 5,058 | 2 | 30,000 | 30,001 | 30,002 | 15.41 % | 0.00 % | 0.19 |
| `pagar` POST /api/servicios/pagos | 501 | 127 | 5 | 7 | 8 | 27 | 0.60 % | 0.00 % | 0.33 |
| `recargar` POST /api/recargas | 1,353 | 1,674 | 5 | 9 | 30,000 | 30,002 | 6.13 % | 0.00 % | 0.90 |
| `transferir` POST /api/transferencias | 1,947 | 579 | 89 | 122 | 126 | 30,001 | 1.85 % | 0.00 % | 1.30 |
| **grupo consulta** | 26,436 | 5,581 | 3 | 30,001 | 30,002 | 30,002 | 17.99 % | 0.00 % | 17.62 |
| **grupo dinero** | 3,801 | 909 | 53 | 117 | 126 | 30,001 | 3.21 % | 0.00 % | 2.53 |
| **total** | 30,237 | 4,994 | 3 | 30,001 | 30,002 | 30,002 | 16.13 % | 0.00 % | 20.16 |
