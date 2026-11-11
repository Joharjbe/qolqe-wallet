// Operaciones de la sesión: una función por operación de la mezcla, con las MISMAS peticiones que hace cada
// pantalla de la web (qolqe/web/static/app.js), sus etiquetas y la clasificación de errores (diseño §4.4 y §5.4).
import http from 'k6/http';
import { check } from 'k6';
import exec from 'k6/execution';
import { Counter, Rate } from 'k6/metrics';
import { etiquetasDeTiempo } from './escenarios.js';

export const BASE_URL = (__ENV.BASE_URL || 'http://127.0.0.1:8090').replace(/\/$/, ''); // Qolqe en Docker (§6.1)
const TIMEOUT = '30s'; // S-06: un timeout del cliente de 30 s es un error de rendimiento

// Endpoints (etiqueta "ep") por grupo de umbral. S-02: toda GET es "consulta", incluidas las de apoyo de una
// operación de dinero. El login va en "consulta" porque U-01 dice "Consultas e inicio de sesión".
export const EP_CONSULTA = ['login', 'saldo', 'perfil', 'movimientos', 'comision', 'contactos_listar',
  'contactos_buscar', 'recargas_config', 'empresas', 'deudas'];                      // veredicto por endpoint (S-03)
export const EP_OTRAS = ['limites', 'alertas', 'solicitudes', 'dispositivos', 'sesiones']; // 2 % c/u: veredicto por grupo (§3.3)
export const EP_DINERO = ['transferir', 'recargar', 'pagar'];                        // U-02

// ---------------------------------------------------------------- métricas propias (§4.4 y §5.4)
const operacionFallida = new Rate('operacion_fallida');        // U-03: una muestra por operación de negocio (login incluido)
const operacionErrorDatos = new Rate('operacion_error_datos'); // V-02: operaciones con un 4xx de regla de negocio
const erroresDatos = new Counter('errores_datos');             // V-02: por {codigo} (LIMITE_DIARIO_EXCEDIDO, SALDO_INSUFICIENTE…)
const erroresRendimiento = new Counter('errores_rendimiento'); // U-03 por {tipo}: http_5xx, timeout, conexion, cuerpo_invalido, no_autenticado
const dineroConfirmado = new Counter('dinero_confirmado');     // C6: 201 recibidos por {ep}, se cruzan con la BD
const dineroSinRespuesta = new Counter('dinero_sin_respuesta'); // C6: POST de dinero sin respuesta (resultado desconocido)
// C6: POST de dinero enviados. Se cuenta ANTES de enviar: si k6 corta la sesión con la petición en vuelo (gracefulStop,
// fin de la demo, humo), la respuesta no deja ninguna muestra y sin este conteo la fila en la BD parecería un duplicado.
const dineroIntentos = new Counter('dinero_intentos');

const RESULTADO = { ok: 0, datos: 1, rendimiento: 2 }; // el peor resultado de sus peticiones define el de la operación
let erroresMostrados = 0;                              // por VU: solo se muestran los primeros errores en la consola

// Clasifica una respuesta según S-06 / §5.4.
function clasificar(res, esperado, valido, ep) {
  if (res.status === 0) return { resultado: 'rendimiento', tipo: res.error_code === 1050 ? 'timeout' : 'conexion' };
  if (res.status >= 500) return { resultado: 'rendimiento', tipo: 'http_5xx' };
  if (res.status === 401 && ep !== 'login') return { resultado: 'rendimiento', tipo: 'no_autenticado' }; // token vigente (30 min)
  if (res.status >= 400) {
    let codigo = `HTTP_${res.status}`;
    try { codigo = res.json('codigo') || codigo; } catch (e) { /* cuerpo sin JSON */ }
    return { resultado: 'datos', codigo };
  }
  let correcto = false;
  try { correcto = res.status === esperado && valido(res.json()); } catch (e) { /* JSON inválido */ }
  return correcto ? { resultado: 'ok' } : { resultado: 'rendimiento', tipo: 'cuerpo_invalido' };
}

// Ejecuta una petición con sus etiquetas, la clasifica y la anota en la operación en curso.
function pedir(operacion, metodo, ruta, { ep, grupo = 'consulta', nombre, cuerpo, esperado = 200, valido = () => true }) {
  const etiquetas = { ...etiquetasDeTiempo(), ep, op: operacion.op, grupo, name: `${metodo} ${nombre || ruta}` };
  const cabeceras = { 'Content-Type': 'application/json' };
  if (operacion.token) cabeceras.Authorization = `Bearer ${operacion.token}`;
  if (grupo === 'dinero') dineroIntentos.add(1, etiquetas);
  const res = http.request(metodo, BASE_URL + ruta, cuerpo === undefined ? null : JSON.stringify(cuerpo),
    { headers: cabeceras, tags: etiquetas, timeout: TIMEOUT });

  const c = clasificar(res, esperado, valido, ep);
  check(res, { [`${ep}: respuesta correcta`]: () => c.resultado === 'ok' }, etiquetas);
  if (c.resultado === 'datos') erroresDatos.add(1, { ...etiquetas, codigo: c.codigo });
  if (c.resultado === 'rendimiento') erroresRendimiento.add(1, { ...etiquetas, tipo: c.tipo });
  if (grupo === 'dinero' && res.status === 201) dineroConfirmado.add(1, etiquetas);
  if (grupo === 'dinero' && res.status === 0) dineroSinRespuesta.add(1, etiquetas);
  // Al cortar un escenario (gracefulStop o fin de la prueba) las peticiones en vuelo terminan con "context canceled";
  // k6 ya descarta sus muestras, así que tampoco se muestran.
  const interrumpida = res.status === 0 && /context canceled/.test(res.error || '');
  if (c.resultado !== 'ok' && !interrumpida && erroresMostrados++ < 5) {
    console.warn(`VU ${exec.vu.idInTest} ${etiquetas.name}: ${res.status} ${c.codigo || c.tipo} ${String(res.body || res.error).slice(0, 160)}`);
  }
  if (RESULTADO[c.resultado] > RESULTADO[operacion.resultado]) operacion.resultado = c.resultado;
  return c.resultado === 'ok' ? res : null;
}

// Una operación de negocio: si falla una de sus peticiones, falla la operación (S-06).
function operacion(op, token, cuerpo) {
  const estado = { op, token, resultado: 'ok' };
  const etiquetas = { ...etiquetasDeTiempo(), op };
  const valor = cuerpo(estado);
  operacionFallida.add(estado.resultado === 'rendimiento', etiquetas);
  operacionErrorDatos.add(estado.resultado === 'datos', etiquetas);
  return valor;
}

// ---------------------------------------------------------------- utilidades de datos (§5.1)
const azar = (lista) => lista[Math.floor(Math.random() * lista.length)];
const entero = (min, max) => min + Math.floor(Math.random() * (max - min + 1));
const esLista = (x) => Array.isArray(x);
const MONTOS_RECARGA = [5, 10, 20, 30, 50, 100]; // R-G1-01: montos permitidos (GET /api/recargas/configuracion)

// ---------------------------------------------------------------- login (F-01)
// POST /api/auth/login con el usuario propio del VU (C4). Devuelve el token o null.
export function login(u) {
  return operacion('login', null, (o) => {
    const res = pedir(o, 'POST', '/api/auth/login', { ep: 'login', cuerpo: { celular: u.celular, pin: u.pin },
      valido: (b) => typeof b.access_token === 'string' && b.usuario.id === u.id });
    return res ? res.json('access_token') : null;
  });
}

// ---------------------------------------------------------------- operaciones de la mezcla (M-07)
export const OPERACIONES = {
  // F-03 Saldo y perfil (30 %): 2 peticiones.
  saldo_perfil: (u, token) => operacion('saldo_perfil', token, (o) => {
    pedir(o, 'GET', '/api/cuentas/me/saldo', { ep: 'saldo', valido: (b) => /^-?\d+\.\d{2}$/.test(b.saldo) });
    pedir(o, 'GET', '/api/cuentas/me', { ep: 'perfil', valido: (b) => b.id === u.id });
  }),

  // F-06 Movimientos (15 %): 30 días por defecto, página 1 (la consulta N+1 del historial).
  movimientos: (u, token) => operacion('movimientos', token, (o) => {
    pedir(o, 'GET', '/api/movimientos?pagina=1', { ep: 'movimientos', nombre: '/api/movimientos',
      valido: (b) => esLista(b.movimientos) && typeof b.total === 'number' });
  }),

  // F-02 Transferir (15 %): comisión → POST, a uno de sus 5 contactos, S/ 1.00–20.00 (RN-05, RN-06).
  transferir: (u, token) => operacion('transferir', token, (o) => {
    const monto = (entero(100, 2000) / 100).toFixed(2);
    if (!pedir(o, 'GET', `/api/transferencias/comision?monto=${monto}&tipo=QOLQE`, { ep: 'comision',
      nombre: '/api/transferencias/comision', valido: (b) => typeof b.total === 'string' })) return;
    pedir(o, 'POST', '/api/transferencias', { ep: 'transferir', grupo: 'dinero', esperado: 201,
      cuerpo: { tipo: 'QOLQE', contacto_id: azar(u.contactos), monto },
      valido: (b) => typeof b.codigo_operacion === 'string' });
  }),

  // Contactos (10 %): lista (página 1) + búsqueda por alias, como la pantalla /contactos.
  contactos: (u, token) => operacion('contactos', token, (o) => {
    pedir(o, 'GET', '/api/contactos?pagina=1', { ep: 'contactos_listar', nombre: '/api/contactos',
      valido: (b) => esLista(b.contactos) });
    pedir(o, 'GET', `/api/contactos?pagina=1&buscar=${encodeURIComponent(u.buscar)}`, { ep: 'contactos_buscar',
      nombre: '/api/contactos?buscar', valido: (b) => esLista(b.contactos) });
  }),

  // F-04 Recarga (10 %): configuración → POST a un número 95XXXXXXX al azar (nunca llega a R-G1-03).
  recarga: (u, token) => operacion('recarga', token, (o) => {
    if (!pedir(o, 'GET', '/api/recargas/configuracion', { ep: 'recargas_config', valido: (b) => esLista(b.montos) })) return;
    pedir(o, 'POST', '/api/recargas', { ep: 'recargar', grupo: 'dinero', esperado: 201,
      cuerpo: { celular: `95${String(entero(0, 9999999)).padStart(7, '0')}`, monto: String(azar(MONTOS_RECARGA)) },
      valido: (b) => typeof b.codigo_operacion === 'string' });
  }),

  // Consulta de deudas (6 %): empresas → deudas del suministro propio (S-15).
  deudas: (u, token) => operacion('deudas', token, (o) => consultarDeudas(o, u)),

  // F-05 Pago (4 %): empresas → deudas → POST de la primera pendiente (S-15).
  pago: (u, token) => operacion('pago', token, (o) => {
    const deudas = consultarDeudas(o, u);
    if (!deudas) return;
    pedir(o, 'POST', '/api/servicios/pagos', { ep: 'pagar', grupo: 'dinero', esperado: 201,
      cuerpo: { deuda_id: deudas[0].id }, valido: (b) => typeof b.codigo_operacion === 'string' });
  }),

  // Otras (10 %, 2 % cada una): una GET por pantalla (S-16).
  limites: (u, token) => otra(token, 'limites', '/api/limites', (b) => typeof b.limite_diario === 'string'),
  alertas: (u, token) => otra(token, 'alertas', '/api/limites/alertas', esLista),
  solicitudes: (u, token) => otra(token, 'solicitudes', '/api/solicitudes', (b) => esLista(b.enviadas)),
  dispositivos: (u, token) => otra(token, 'dispositivos', '/api/seguridad/dispositivos', esLista),
  sesiones: (u, token) => otra(token, 'sesiones', '/api/seguridad/sesiones', esLista),
};

function consultarDeudas(o, u) {
  if (!pedir(o, 'GET', '/api/servicios/empresas', { ep: 'empresas', valido: (b) => esLista(b) && b.length > 0 })) return null;
  const res = pedir(o, 'GET', `/api/servicios/deudas?empresa=AGUA&suministro=${u.suministro}`, { ep: 'deudas',
    nombre: '/api/servicios/deudas', valido: (b) => esLista(b) && b.length > 0 && b[0].id > 0 });
  return res ? res.json() : null;
}

function otra(token, ep, ruta, valido) {
  return operacion('otras', token, (o) => { pedir(o, 'GET', ruta, { ep, valido }); });
}
