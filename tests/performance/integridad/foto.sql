-- Huella de una base (V-05: "la base restaurada es idéntica a base_perf.db": Σ saldos, conteos e ids máximos).
-- correr.sh compara la huella de /data/qolqe.db recién restaurada con la guardada al preparar los datos.

-- @foto
SELECT (SELECT COUNT(*) FROM usuarios)                                   AS usuarios,
       (SELECT COUNT(*) FROM usuarios WHERE celular BETWEEN '900000001' AND '900099999') AS usuarios_carga,
       (SELECT SUM(saldo_cent) FROM cuentas)                             AS saldo_total_cent,
       (SELECT COUNT(*) FROM contactos)                                  AS contactos,
       (SELECT COUNT(*) FROM deudas WHERE estado = 'PENDIENTE')          AS deudas_pendientes,
       (SELECT COALESCE(MAX(id), 0) FROM movimientos)                    AS max_id_movimientos,
       (SELECT COALESCE(MAX(id), 0) FROM transferencias)                 AS max_id_transferencias,
       (SELECT COALESCE(MAX(id), 0) FROM recargas)                       AS max_id_recargas,
       (SELECT COALESCE(MAX(id), 0) FROM pagos_servicio)                 AS max_id_pagos,
       (SELECT COALESCE(MAX(id), 0) FROM sesiones)                       AS max_id_sesiones,
       (SELECT COALESCE(MAX(id), 0) FROM notificaciones)                 AS max_id_notificaciones;
