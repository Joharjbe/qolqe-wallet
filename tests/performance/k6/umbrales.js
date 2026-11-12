// Umbrales como código (diseño §2.1 y §4.4). Cada umbral lleva su ID (U o V) y la frase del requerimiento.
// Si alguno falla, k6 termina con código 99: es el paso 1 de S14, "¿pasó o falló?".
// Lo que k6 no puede expresar (U-05 b y c, U-07, U-08, U-09, V-01, V-03…) lo calcula analisis/analizar.py.
import { EP_CONSULTA, EP_DINERO, EP_OTRAS } from './operaciones.js';
import { ESCALA, L_CAP, dur } from './escenarios.js';

// U-01 "Consultas e inicio de sesión: el 95 % debe responder en menos de 800 ms."
const LIMITE_CONSULTA_MS = 800;
// U-02 "Operaciones de dinero (transferencias, recargas y pagos): el 95 % debe responder en menos de 1.5 segundos."
const LIMITE_DINERO_MS = 1500;
// U-06 / S-05 "se acepta una degradación razonable del servicio" → hasta 2 × el umbral normal (1,600 / 3,000 ms).
const FACTOR_CAMPANA = 2;
// U-03 "En hora punta, no más del 1 % de las operaciones puede fallar"
const ERROR_MAXIMO = 0.01;
// U-04 "…sostener el volumen de la hora punta…": ≥ 9.6 req/s atendidas (98 % de los 9.78 ofrecidos, M-08, S-04).
const REQ_POR_S_MINIMAS = 9.6;
// V-06 "referencia de 1 VU": el p95 de cada endpoint es ≤ 10 % de su umbral.
const FRACCION_REFERENCIA = 0.1;

export const DESCRIPCIONES = {}; // "métrica{filtro}" → "ID texto", para el resumen de consola (resumen.js)

function agregar(umbrales, clave, condicion, descripcion) {
  (umbrales[clave] = umbrales[clave] || []).push(condicion);
  DESCRIPCIONES[clave] = descripcion;
}

// p95 por grupo (lectura literal) y por endpoint (S-03) para un filtro de etiquetas como "fase:estable".
function tiempos(u, filtro, factor, idConsulta, idDinero) {
  const consulta = Math.round(LIMITE_CONSULTA_MS * factor), dinero = Math.round(LIMITE_DINERO_MS * factor);
  agregar(u, `http_req_duration{${filtro},grupo:consulta}`, `p(95)<${consulta}`, `${idConsulta} consultas e inicio de sesión (grupo)`);
  for (const ep of EP_CONSULTA) agregar(u, `http_req_duration{${filtro},ep:${ep}}`, `p(95)<${consulta}`, `${idConsulta} ${ep} (S-03)`);
  agregar(u, `http_req_duration{${filtro},op:otras}`, `p(95)<${consulta}`, `${idConsulta} otras: 5 GET al 2 % (§3.3)`);
  agregar(u, `http_req_duration{${filtro},grupo:dinero}`, `p(95)<${dinero}`, `${idDinero} operaciones de dinero (grupo)`);
  for (const ep of EP_DINERO) agregar(u, `http_req_duration{${filtro},ep:${ep}}`, `p(95)<${dinero}`, `${idDinero} ${ep} (S-03)`);
}

// Hora punta en el estado estable (carga, resistencia y capacidad): U-01 a U-05 (a).
function horaPunta(segundosEstables, simultaneos = 100) {
  const u = {};
  tiempos(u, 'fase:estable', 1, 'U-01', 'U-02');
  agregar(u, 'operacion_fallida{fase:estable}', `rate<=${ERROR_MAXIMO}`, 'U-03 operaciones fallidas (S-06)');
  // U-04: peticiones atendidas (status 200–499) en la fase estable ≥ 9.6 req/s × segundos de la fase.
  // En un ensayo comprimido la fase estable dura segundosEstables × ESCALA (la tasa no cambia).
  const minimas = Math.ceil(REQ_POR_S_MINIMAS * (simultaneos / 100) * segundosEstables * ESCALA);
  agregar(u, 'http_reqs{fase:estable,expected_response:true}', `count>=${minimas}`, `U-04 throughput ≥ ${(REQ_POR_S_MINIMAS * simultaneos / 100).toFixed(1)} req/s`);
  // U-05 (a) "…sin acumular retrasos": ninguna sesión descartada por falta de VUs (modelo abierto, S-04).
  agregar(u, 'dropped_iterations', 'count==0', 'U-05a sesiones descartadas');
  return u;
}

// Pico de la campaña: U-06 en 12:00–12:15 y los umbrales normales antes (base) y en la recuperación (12:10–12:15).
function pico() {
  const u = {};
  tiempos(u, 'campana:si', FACTOR_CAMPANA, 'U-06', 'U-06');
  agregar(u, 'operacion_fallida{campana:si}', `rate<=${ERROR_MAXIMO}`, 'U-06 error en la campaña (S-05)');
  agregar(u, 'dropped_iterations', 'count==0', 'U-06 sesiones descartadas');
  tiempos(u, 'fase:base', 1, 'U-01', 'U-02');
  tiempos(u, 'fase:recuperacion', 1, 'U-06 recuperación U-01', 'U-06 recuperación U-02');
  return u;
}

// Referencia de 1 VU (V-06) y validez de los datos (V-02): sin errores de ningún tipo.
function referencia() {
  const u = validez();
  for (const ep of [...EP_CONSULTA, ...EP_OTRAS]) {
    agregar(u, `http_req_duration{ep:${ep}}`, `p(95)<=${LIMITE_CONSULTA_MS * FRACCION_REFERENCIA}`, `V-06 ${ep} ≤ 10 % de U-01`);
  }
  for (const ep of EP_DINERO) {
    agregar(u, `http_req_duration{ep:${ep}}`, `p(95)<=${LIMITE_DINERO_MS * FRACCION_REFERENCIA}`, `V-06 ${ep} ≤ 10 % de U-02`);
  }
  return u;
}

function validez() {
  const u = {};
  agregar(u, 'operacion_fallida', 'rate==0', 'validez: sin errores de rendimiento');
  agregar(u, 'errores_datos', 'count==0', 'V-02 sin errores de datos');
  return u;
}

// Demo (§9): los mismos SLA, filtrados por cada sub-escenario. Se espera ✓ en hora punta y ✗ sin pausa (código 99).
function demo() {
  const u = {};
  for (const s of ['demo_hora_punta', 'demo_sin_pausa']) {
    agregar(u, `http_req_duration{scenario:${s},grupo:consulta}`, `p(95)<${LIMITE_CONSULTA_MS}`, `U-01 ${s}: consultas`);
    agregar(u, `http_req_duration{scenario:${s},ep:login}`, `p(95)<${LIMITE_CONSULTA_MS}`, `U-01 ${s}: login`);
    agregar(u, `http_req_duration{scenario:${s},grupo:dinero}`, `p(95)<${LIMITE_DINERO_MS}`, `U-02 ${s}: dinero`);
    agregar(u, `operacion_fallida{scenario:${s}}`, `rate<=${ERROR_MAXIMO}`, `U-03 ${s}: operaciones fallidas`);
  }
  agregar(u, 'dropped_iterations{scenario:demo_hora_punta}', 'count==0', 'U-05a demo_hora_punta: sesiones descartadas');
  return u;
}

// Estrés: solo una red de seguridad; la capacidad (U-08) la calcula el análisis por ventanas de 30 s.
function estres() {
  const u = { operacion_fallida: [{ threshold: 'rate<0.2', abortOnFail: true, delayAbortEval: dur('2m') }] };
  DESCRIPCIONES.operacion_fallida = 'red de seguridad: corta si falla más del 20 %';
  return u;
}

const CONSTRUCTORES = {
  referencia,
  calibracion: validez,
  carga: () => horaPunta(900),        // M-12: 15 min estables
  resistencia: () => horaPunta(3600), // M-13: 60 min estables
  capacidad: () => horaPunta(600, L_CAP), // 10 min estables a L_cap simultáneos
  pico,
  estres,
  demo,
};

// Solo se construyen los umbrales del escenario elegido (así DESCRIPCIONES no mezcla escenarios).
export function umbralesDe(escenario) {
  return CONSTRUCTORES[escenario] ? CONSTRUCTORES[escenario]() : {};
}
