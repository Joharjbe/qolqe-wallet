-- Datos que la API de Qolqe no permite crear (diseño §5.2, paso 5). Lo ejecuta preparar_datos.py dentro del
-- contenedor, DESPUÉS de reiniciar, registrar a los usuarios, fijar saldos y crear contactos por la API.
-- Solo toca el archivo de datos (/data/qolqe.db); qolqe/ no se modifica.
-- Usuarios de carga: celulares 900000001..9000NNNNN (los 200 de la semilla + los creados por la API).
CREATE TEMP VIEW vu AS
  SELECT id, nombres FROM usuarios
  WHERE estado = 'ACTIVA' AND celular BETWEEN '900000001' AND '900099999';

-- 1) Historial (§5.1, "Movimientos"): los usuarios creados por la API no tienen movimientos. Se les copia el de
--    "Usuario Carga 001" (id 7: 1,000 movimientos en 120 días, ≈ 243 en los últimos 30) para que consultar
--    movimientos cueste lo mismo para todos. Si su historial quedara vacío, el costo del N+1 de
--    movimientos.py bajaría justo con más usuarios y el estrés mediría de menos.
INSERT INTO movimientos (usuario_id, codigo_operacion, tipo, descripcion, contraparte,
                         monto_cent, comision_cent, importe_cent, fecha)
SELECT u.id, substr(m.codigo_operacion, 1, 15) || printf('%05d', u.id), m.tipo, m.descripcion, m.contraparte,
       m.monto_cent, m.comision_cent, m.importe_cent, m.fecha
FROM vu u JOIN movimientos m ON m.usuario_id = 7 AND m.descripcion LIKE 'Movimiento %'
WHERE NOT EXISTS (SELECT 1 FROM movimientos x WHERE x.usuario_id = u.id);

-- 2) Deudas (§5.1, "Consulta de deudas y pago"): la semilla trae 1 por usuario y el primer pago la consume
--    (luego 404 SIN_DEUDA_PENDIENTE y 409 DEUDA_YA_PAGADA, que serían errores de datos). Se crean 30
--    pendientes por usuario en un suministro propio, '5' + id con 9 dígitos, que solo usa su VU.
--    Vencen de mañana en adelante, así que no tienen mora ni pasan a cobranza (RN de servicios).
--    30 = peor caso de 52 sesiones × 6 operaciones × 4 % ≈ 12.5 pagos por VU en la resistencia, con margen.
WITH RECURSIVE k(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM k WHERE n < 30)
INSERT INTO deudas (empresa, suministro, titular, periodo, monto_cent, vencimiento)
SELECT 'AGUA', printf('5%09d', u.id), u.nombres, strftime('%Y-%m', 'now', '-5 hours'),
       3000 + (u.id % 50) * 10, date('now', '-5 hours', '+' || k.n || ' days')
FROM vu u, k;
