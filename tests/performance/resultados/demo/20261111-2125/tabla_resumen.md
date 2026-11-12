# Tabla resumen · demo · 20261111-2125

Formato de S14. Tiempos en ms (percentil por rango más cercano). Error de rendimiento = 5xx y status 0; error de datos = 4xx de regla de negocio (se reportan por separado, enunciado §5).

## demo_hora_punta

| Endpoint | Peticiones | Promedio | p50 | p90 | p95 | p99 | Error rend. | Error datos | Throughput (req/s) |
|---|---|---|---|---|---|---|---|---|---|
| `login` POST /api/auth/login | 84 | 100 | 101 | 104 | 106 | 120 | 0.00 % | 0.00 % | 0.84 |
| `alertas` GET /api/limites/alertas | 4 | 5 | 4 | 9 | 9 | 9 | 0.00 % | 0.00 % | 0.04 |
| `comision` GET /api/transferencias/comision | 21 | 6 | 7 | 9 | 10 | 13 | 0.00 % | 0.00 % | 0.21 |
| `contactos_buscar` GET /api/contactos?buscar | 37 | 4 | 5 | 6 | 6 | 7 | 0.00 % | 0.00 % | 0.37 |
| `contactos_listar` GET /api/contactos | 37 | 7 | 8 | 11 | 12 | 13 | 0.00 % | 0.00 % | 0.37 |
| `deudas` GET /api/servicios/deudas | 18 | 4 | 5 | 5 | 6 | 6 | 0.00 % | 0.00 % | 0.18 |
| `dispositivos` GET /api/seguridad/dispositivos | 5 | 8 | 9 | 11 | 11 | 11 | 0.00 % | 0.00 % | 0.05 |
| `empresas` GET /api/servicios/empresas | 18 | 6 | 7 | 10 | 10 | 10 | 0.00 % | 0.00 % | 0.18 |
| `limites` GET /api/limites | 1 | 10 | 10 | 10 | 10 | 10 | 0.00 % | 0.00 % | 0.01 |
| `movimientos` GET /api/movimientos | 31 | 27 | 30 | 35 | 37 | 38 | 0.00 % | 0.00 % | 0.31 |
| `perfil` GET /api/cuentas/me | 56 | 3 | 3 | 4 | 4 | 5 | 0.00 % | 0.00 % | 0.56 |
| `recargas_config` GET /api/recargas/configuracion | 13 | 5 | 5 | 7 | 8 | 8 | 0.00 % | 0.00 % | 0.13 |
| `saldo` GET /api/cuentas/me/saldo | 56 | 7 | 8 | 11 | 13 | 14 | 0.00 % | 0.00 % | 0.56 |
| `sesiones` GET /api/seguridad/sesiones | 5 | 8 | 9 | 9 | 9 | 9 | 0.00 % | 0.00 % | 0.05 |
| `solicitudes` GET /api/solicitudes | 1 | 10 | 10 | 10 | 10 | 10 | 0.00 % | 0.00 % | 0.01 |
| `pagar` POST /api/servicios/pagos | 9 | 7 | 6 | 11 | 11 | 11 | 0.00 % | 0.00 % | 0.09 |
| `recargar` POST /api/recargas | 13 | 10 | 11 | 12 | 13 | 13 | 0.00 % | 0.00 % | 0.13 |
| `transferir` POST /api/transferencias | 21 | 97 | 102 | 138 | 138 | 143 | 0.00 % | 0.00 % | 0.21 |
| **grupo consulta** | 387 | 28 | 7 | 102 | 103 | 106 | 0.00 % | 0.00 % | 3.87 |
| **grupo dinero** | 43 | 52 | 13 | 114 | 138 | 143 | 0.00 % | 0.00 % | 0.43 |
| **total** | 430 | 30 | 8 | 102 | 104 | 120 | 0.00 % | 0.00 % | 4.30 |

## demo_sin_pausa

| Endpoint | Peticiones | Promedio | p50 | p90 | p95 | p99 | Error rend. | Error datos | Throughput (req/s) |
|---|---|---|---|---|---|---|---|---|---|
| `login` POST /api/auth/login | 234 | 7,114 | 3,188 | 16,692 | 17,886 | 25,916 | 73.08 % | 0.00 % | 5.20 |
| `alertas` GET /api/limites/alertas | 9 | 289 | 94 | 785 | 785 | 785 | 0.00 % | 0.00 % | 0.20 |
| `comision` GET /api/transferencias/comision | 45 | 629 | 200 | 1,713 | 1,852 | 8,584 | 0.00 % | 0.00 % | 1.00 |
| `contactos_buscar` GET /api/contactos?buscar | 26 | 507 | 122 | 1,809 | 2,852 | 2,860 | 0.00 % | 0.00 % | 0.58 |
| `contactos_listar` GET /api/contactos | 27 | 697 | 182 | 1,846 | 1,999 | 8,238 | 0.00 % | 0.00 % | 0.60 |
| `deudas` GET /api/servicios/deudas | 23 | 853 | 186 | 2,297 | 2,416 | 8,394 | 0.00 % | 0.00 % | 0.51 |
| `dispositivos` GET /api/seguridad/dispositivos | 13 | 510 | 214 | 1,000 | 2,710 | 2,710 | 0.00 % | 0.00 % | 0.29 |
| `empresas` GET /api/servicios/empresas | 23 | 1,066 | 109 | 1,397 | 7,149 | 10,985 | 0.00 % | 0.00 % | 0.51 |
| `limites` GET /api/limites | 7 | 194 | 101 | 881 | 881 | 881 | 0.00 % | 0.00 % | 0.16 |
| `movimientos` GET /api/movimientos | 33 | 1,045 | 298 | 2,858 | 3,396 | 9,942 | 0.00 % | 0.00 % | 0.73 |
| `perfil` GET /api/cuentas/me | 102 | 299 | 115 | 818 | 1,294 | 1,801 | 0.00 % | 0.00 % | 2.27 |
| `recargas_config` GET /api/recargas/configuracion | 32 | 489 | 92 | 1,265 | 1,407 | 7,044 | 0.00 % | 0.00 % | 0.71 |
| `saldo` GET /api/cuentas/me/saldo | 103 | 327 | 115 | 908 | 1,618 | 1,928 | 0.00 % | 0.00 % | 2.29 |
| `sesiones` GET /api/seguridad/sesiones | 6 | 555 | 292 | 1,735 | 1,735 | 1,735 | 0.00 % | 0.00 % | 0.13 |
| `solicitudes` GET /api/solicitudes | 6 | 274 | 98 | 1,004 | 1,004 | 1,004 | 0.00 % | 0.00 % | 0.13 |
| `pagar` POST /api/servicios/pagos | 10 | 4,984 | 3,198 | 11,289 | 12,489 | 12,489 | 30.00 % | 0.00 % | 0.22 |
| `recargar` POST /api/recargas | 25 | 2,809 | 394 | 11,713 | 12,125 | 12,586 | 16.00 % | 0.00 % | 0.56 |
| `transferir` POST /api/transferencias | 35 | 2,131 | 493 | 10,669 | 11,098 | 11,287 | 11.43 % | 0.00 % | 0.78 |
| **grupo consulta** | 689 | 2,756 | 197 | 13,101 | 15,689 | 18,133 | 24.82 % | 0.00 % | 15.32 |
| **grupo dinero** | 70 | 2,781 | 500 | 10,798 | 11,713 | 12,586 | 15.71 % | 0.00 % | 1.56 |
| **total** | 759 | 2,758 | 206 | 13,007 | 15,488 | 18,089 | 23.98 % | 0.00 % | 16.87 |
