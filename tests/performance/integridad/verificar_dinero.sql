-- Chequeos de integridad del dinero antes y después de una corrida (U-07, diseño §5.5).
-- U-07: "ninguna operación de dinero puede quedar a medias ni aplicarse dos veces" → descuadres = 0.
-- main = base DESPUÉS de la corrida (/data/qolqe.db, sin tráfico); a = base ANTES (/data/base_perf.db, la que
-- correr.sh restaura antes de cada corrida, S-09). Lo nuevo de la corrida es todo id > MAX(id) de "antes".
-- Cada bloque empieza con "-- @nombre" y lo ejecuta verificar_bd.py; el correcto de cada uno va en su comentario.

-- @ultimos  Ids máximos de "antes": frontera entre los datos de la base y los de la corrida.
SELECT (SELECT COALESCE(MAX(id), 0) FROM a.movimientos)    AS movimientos,
       (SELECT COALESCE(MAX(id), 0) FROM a.transferencias) AS transferencias,
       (SELECT COALESCE(MAX(id), 0) FROM a.recargas)       AS recargas,
       (SELECT COALESCE(MAX(id), 0) FROM a.pagos_servicio) AS pagos,
       (SELECT COALESCE(MAX(id), 0) FROM a.sesiones)       AS sesiones;

-- @C1_conservacion  Conservación: lo que salió del sistema = recargas + pagos + comisiones + interbancarias
-- (las transferencias entre cuentas Qolqe suman cero, RN-09). Además, la variación total de saldos debe ser
-- igual a la suma de los importes de los movimientos nuevos. Correcto: descuadre_cent = 0 y descuadre_libro_cent = 0.
WITH u AS (SELECT (SELECT COALESCE(MAX(id), 0) FROM a.movimientos) m, (SELECT COALESCE(MAX(id), 0) FROM a.transferencias) t,
                  (SELECT COALESCE(MAX(id), 0) FROM a.recargas) r, (SELECT COALESCE(MAX(id), 0) FROM a.pagos_servicio) p),
     v AS (SELECT (SELECT SUM(saldo_cent) FROM a.cuentas) AS antes,
                  (SELECT SUM(saldo_cent) FROM main.cuentas) AS despues,
                  (SELECT COALESCE(SUM(monto_cent), 0) FROM main.recargas, u WHERE id > u.r) AS recargas,
                  (SELECT COALESCE(SUM(total_cent), 0) FROM main.pagos_servicio, u WHERE id > u.p) AS pagos,
                  (SELECT COALESCE(SUM(comision_cent), 0) FROM main.transferencias, u WHERE id > u.t) AS comisiones,
                  (SELECT COALESCE(SUM(monto_cent), 0) FROM main.transferencias, u
                    WHERE id > u.t AND tipo = 'INTERBANCARIA') AS interbancarias,
                  (SELECT COALESCE(SUM(importe_cent), 0) FROM main.movimientos, u WHERE id > u.m) AS movimientos_neto)
SELECT antes AS antes_cent, despues AS despues_cent, recargas AS recargas_cent, pagos AS pagos_cent,
       comisiones AS comisiones_cent, interbancarias AS interbancarias_cent,
       (antes - despues) - (recargas + pagos + comisiones + interbancarias) AS descuadre_cent,
       movimientos_neto AS movimientos_neto_cent, (despues - antes) - movimientos_neto AS descuadre_libro_cent
FROM v;

-- @C2_libro_mayor  Por usuario: variación de su saldo = suma de sus movimientos nuevos. Detecta operaciones a
-- medias (saldo movido sin movimiento, o al revés). Una cuenta creada en la corrida parte de 0. Correcto: 0 filas.
SELECT c.usuario_id, COALESCE(ca.saldo_cent, 0) AS antes_cent, c.saldo_cent AS despues_cent,
       COALESCE(m.suma, 0) AS movimientos_cent,
       c.saldo_cent - COALESCE(ca.saldo_cent, 0) - COALESCE(m.suma, 0) AS descuadre_cent
FROM main.cuentas c
LEFT JOIN a.cuentas ca USING (usuario_id)
LEFT JOIN (SELECT usuario_id, SUM(importe_cent) AS suma FROM main.movimientos
           WHERE id > (SELECT COALESCE(MAX(id), 0) FROM a.movimientos) GROUP BY usuario_id) m USING (usuario_id)
WHERE c.saldo_cent - COALESCE(ca.saldo_cent, 0) - COALESCE(m.suma, 0) <> 0;

-- @C3_operacion_movimientos  Cada operación nueva tiene exactamente sus movimientos: transferencia = 1 ENVIADA
-- (monto + comisión) + 1 RECIBIDA (monto, solo Qolqe); recarga = 1 RECARGA; pago = 1 PAGO_SERVICIO (total).
-- Se agrupa por código y tipo, así dos operaciones del mismo usuario en el mismo segundo (DEF-22, comparten
-- código) no se confunden con un duplicado. Correcto: 0 filas.
WITH u AS (SELECT (SELECT COALESCE(MAX(id), 0) FROM a.transferencias) t, (SELECT COALESCE(MAX(id), 0) FROM a.recargas) r,
                  (SELECT COALESCE(MAX(id), 0) FROM a.pagos_servicio) p, (SELECT COALESCE(MAX(id), 0) FROM a.movimientos) m),
ops AS (
  SELECT codigo_operacion AS c, 'TRANSFERENCIA_ENVIADA' AS tipo, COUNT(*) AS n, SUM(monto_cent + comision_cent) AS s
    FROM main.transferencias, u WHERE id > u.t GROUP BY 1
  UNION ALL SELECT codigo_operacion, 'TRANSFERENCIA_RECIBIDA', COUNT(*), SUM(monto_cent)
    FROM main.transferencias, u WHERE id > u.t AND tipo = 'QOLQE' GROUP BY 1
  UNION ALL SELECT codigo_operacion, 'RECARGA', COUNT(*), SUM(monto_cent) FROM main.recargas, u WHERE id > u.r GROUP BY 1
  UNION ALL SELECT codigo_operacion, 'PAGO_SERVICIO', COUNT(*), SUM(total_cent) FROM main.pagos_servicio, u WHERE id > u.p GROUP BY 1),
movs AS (SELECT codigo_operacion AS c, tipo, COUNT(*) AS n, SUM(ABS(importe_cent)) AS s
         FROM main.movimientos, u WHERE id > u.m GROUP BY 1, 2)
SELECT 'operacion_sin_sus_movimientos' AS problema, o.c AS codigo, o.tipo, o.n AS operaciones, m.n AS movimientos
FROM ops o LEFT JOIN movs m ON m.c = o.c AND m.tipo = o.tipo
WHERE m.n IS NOT o.n OR m.s IS NOT o.s
UNION ALL
SELECT 'movimiento_sin_operacion', m.c, m.tipo, NULL, m.n
FROM movs m LEFT JOIN ops o ON o.c = m.c AND o.tipo = m.tipo
WHERE o.c IS NULL;

-- @C4_pagos  Ninguna deuda pagada dos veces; toda deuda PAGADA tiene su pago y todo pago apunta a una deuda
-- PAGADA. Correcto: 0 filas.
SELECT 'pago_duplicado' AS problema, deuda_id, COUNT(*) AS n FROM main.pagos_servicio GROUP BY deuda_id HAVING COUNT(*) > 1
UNION ALL
SELECT 'deuda_pagada_sin_pago', d.id, 0 FROM main.deudas d
WHERE d.estado = 'PAGADA' AND NOT EXISTS (SELECT 1 FROM main.pagos_servicio p WHERE p.deuda_id = d.id)
UNION ALL
SELECT 'pago_de_deuda_no_pagada', p.deuda_id, 1 FROM main.pagos_servicio p JOIN main.deudas d ON d.id = p.deuda_id
WHERE d.estado <> 'PAGADA';

-- @C5_reglas  Síntomas de la carrera entre validar y escribir (DEF-21): saldos negativos (RN-08) y
-- transferencias Qolqe de hoy (hora de Lima) por encima del límite diario (RN-06). Correcto: 0 filas.
SELECT 'saldo_negativo' AS problema, usuario_id, saldo_cent AS valor_cent FROM main.cuentas WHERE saldo_cent < 0
UNION ALL
SELECT 'limite_diario_superado', t.origen_id, SUM(t.monto_cent)
FROM main.transferencias t JOIN main.limites l ON l.usuario_id = t.origen_id
WHERE t.tipo = 'QOLQE' AND t.fecha >= date('now', '-5 hours')
GROUP BY t.origen_id, l.limite_diario_cent HAVING SUM(t.monto_cent) > l.limite_diario_cent;

-- @C6_conteos  Filas nuevas por tipo. verificar.py las concilia con los 201 que recibió k6 (o con --esperado).
SELECT (SELECT COUNT(*) FROM main.transferencias WHERE id > (SELECT COALESCE(MAX(id), 0) FROM a.transferencias)) AS transferencias,
       (SELECT COUNT(*) FROM main.recargas WHERE id > (SELECT COALESCE(MAX(id), 0) FROM a.recargas)) AS recargas,
       (SELECT COUNT(*) FROM main.pagos_servicio WHERE id > (SELECT COALESCE(MAX(id), 0) FROM a.pagos_servicio)) AS pagos,
       (SELECT COUNT(*) FROM main.sesiones WHERE id > (SELECT COALESCE(MAX(id), 0) FROM a.sesiones)) AS logins,
       (SELECT COUNT(*) FROM main.movimientos WHERE id > (SELECT COALESCE(MAX(id), 0) FROM a.movimientos)) AS movimientos;
