// Escenarios de k6 (diseño §4.2) y fases de cada uno.
// En cada corrida se elige UNO con -e ESCENARIO=<nombre>; no se usa --scenario.
// Cada iteración de k6 es una SESIÓN (login + 6 operaciones + pausas); la carga se expresa en sesiones por minuto.
import exec from 'k6/execution';

// ---------------------------------------------------------------- valores del modelo de carga (§3.2)
export const SESIONES_POR_MIN = 50;  // M-01: "unas 3 000 sesiones por hora" → 3,000 / 60 = 50 por minuto (λ = 0.833/s)
export const DURACION_SESION_S = 120; // M-02: "una sesión dura en promedio 2 minutos" (W = 120 s)
// M-03: L = λ·W = 0.833 × 120 = 100 usuarios simultáneos. Con llegada constante, 0 → 100 se llena solo en W = 120 s (M-24).

// M-14: cima del estrés. Hipótesis L_top = 2,400 simultáneos; la calibración (§4.2) fija el valor final con -e TOP=<n>.
export const TOP = Number(__ENV.TOP || 2400);
// Opcional 2 (§10.2): confirmar la capacidad 10 min a L_cap y a 1.15 × L_cap, con -e L_CAP=<n> (lo da el análisis del estrés).
export const L_CAP = Number(__ENV.L_CAP || 0);

const porMinuto = (simultaneos) => Math.round(simultaneos / (DURACION_SESION_S / 60)); // Little: λ = L / W

// ---------------------------------------------------------------- ensayo comprimido (no es evidencia)
// -e ESCALA=0.1 comprime el tiempo de un escenario para validar la cadena completa en pocos minutos: duraciones, fases,
// think time y cierre se multiplican por ESCALA; la tasa de llegada (sesiones/min) NO cambia, así que req/s y sesiones/min
// son las del diseño y los simultáneos bajan a L·ESCALA (Little: L = λ·W, con W = 120 s × ESCALA). Las reservas de VUs
// (M-15) se escalan igual. Con ESCALA = 1 (por defecto) todo es exactamente el diseño. correr.sh guarda estas corridas
// fuera de la evidencia (resultados/descartadas/).
export const ESCALA = Number(__ENV.ESCALA || 1);
if (!(ESCALA > 0 && ESCALA <= 1)) throw new Error(`ESCALA=${__ENV.ESCALA} no es válida: debe estar en (0, 1]`);
// '4m30s' → 270 (segundos)
const segundos = (texto) => [...texto.matchAll(/(\d+(?:\.\d+)?)(ms|h|m|s)/g)]
  .reduce((total, [, n, u]) => total + Number(n) * { h: 3600, m: 60, s: 1, ms: 0.001 }[u], 0);
export const dur = (texto) => (ESCALA === 1 ? texto : `${Math.round(segundos(texto) * ESCALA * 1000)}ms`);
const vus = (n) => (ESCALA === 1 ? n : Math.max(2, Math.ceil(n * ESCALA)));

// ---------------------------------------------------------------- escenarios (§4.2, tal cual el diseño)
export const ESCENARIOS = {
  // Apoyo: 1 VU recorre las 12 operaciones y el login, 5 veces, con pausa de 1 s → p50/p95 de referencia (V-06).
  referencia: { recorrido: { executor: 'per-vu-iterations', exec: 'recorrido', vus: 1, iterations: 5, maxDuration: '3m' } },

  // Apoyo: 40 sesiones con la mezcla y pausa de 0.5 s; correr.sh mide Δusage_usec de cpu.stat → D_sesión → TOP (M-14).
  calibracion: { calibracion: { executor: 'per-vu-iterations', exec: 'calibracion', vus: 1, iterations: 40, maxDuration: '5m' } },

  // Carga (obligatoria): 50 sesiones/min durante 17 min = 120 s de llenado + 15 min estables (M-12) → drenaje.
  carga: { carga: { executor: 'constant-arrival-rate', exec: 'sesion',
    rate: SESIONES_POR_MIN, timeUnit: '1m',             // M-01
    duration: dur('17m'),                                // M-12: 2 min de llenado (M-24) + 15 min estables
    preAllocatedVUs: vus(150), maxVUs: vus(200),         // M-15: 1.5 × L y 2 × L con L = 100
    gracefulStop: dur('3m') } },                         // deja terminar las sesiones en curso (≤ 162 s, §3.2)

  // Pico (campaña "Quincena Qolqe"): 100 → salto ×3 en 30 s → 300 simultáneos → vuelta a 100.
  pico: { pico: { executor: 'ramping-arrival-rate', exec: 'sesion',
    startRate: SESIONES_POR_MIN, timeUnit: '1m',         // M-01: arranca en hora punta
    preAllocatedVUs: vus(400), maxVUs: vus(600),         // M-15: 1.33 × 300 y 2 × 300
    gracefulStop: dur('3m'),
    stages: [
      { duration: dur('4m'), target: 50 },               // 11:56–12:00 hora punta: llenado + base (M-11)
      { duration: dur('30s'), target: 150 },             // 12:00 salto ×3 en 30 s (M-10)
      { duration: dur('4m30s'), target: 150 },           // hasta 12:05: "la mayoría inicia sesión"; 300 simultáneos (M-09, S-07, S-08)
      { duration: dur('30s'), target: 50 },              // 12:05 vuelve la llegada normal (S-08)
      { duration: dur('9m30s'), target: 50 },            // hasta 12:15: resto de la campaña y recuperación (U-06)
    ] } },

  // Estrés (obligatoria): rampa continua de 100 simultáneos a TOP, más allá del límite estimado (U-08, S-10).
  estres: { estres: { executor: 'ramping-arrival-rate', exec: 'sesion',
    startRate: SESIONES_POR_MIN, timeUnit: '1m',
    preAllocatedVUs: vus(TOP + 100),                     // M-15: 2,500 con TOP = 2,400
    maxVUs: vus(Math.ceil(1.25 * TOP)),                  // M-15: 1.25 × L_top = 3,000 (= usuarios de M-16)
    gracefulStop: dur('2m'),
    stages: [
      { duration: dur('3m'), target: 50 },               // base: 100 simultáneos
      { duration: dur('23m'), target: porMinuto(TOP) },  // M-14: +100 simultáneos por minuto hasta TOP (1,200/min con 2,400)
      { duration: dur('2m'), target: porMinuto(TOP) },   // meseta más allá del límite
    ] } },

  // Resistencia: 60 min estables a 50 sesiones/min (M-13, S-12) + 2 min de llenado.
  resistencia: { resistencia: { executor: 'constant-arrival-rate', exec: 'sesion',
    rate: SESIONES_POR_MIN, timeUnit: '1m',              // M-01
    duration: dur('62m'),                                // M-13: 2 min de llenado + 60 min = 3,000 sesiones medidas
    preAllocatedVUs: vus(150), maxVUs: vus(200),         // M-15
    gracefulStop: dur('3m') } },

  // Demo en clase (§9): 100 s de hora punta real y luego 45 s sin think time ("estrés disfrazado", S13).
  demo: {
    demo_hora_punta: { executor: 'constant-arrival-rate', exec: 'sesion',
      rate: SESIONES_POR_MIN, timeUnit: '1m', duration: dur('100s'), // M-01
      preAllocatedVUs: vus(150), maxVUs: vus(200), gracefulStop: dur('0s') }, // M-15
    demo_sin_pausa: { executor: 'constant-vus', exec: 'sesionSinPausa', vus: vus(50), duration: dur('45s'),
      startTime: dur('100s'), gracefulStop: dur('0s') }, // M-15: demo 200 + 50
  },

  // Opcional 2 (§10.2): confirmación de la capacidad. Se corre dos veces: L_CAP = L_cap y L_CAP = 1.15 × L_cap.
  capacidad: { capacidad: { executor: 'constant-arrival-rate', exec: 'sesion',
    rate: porMinuto(L_CAP), timeUnit: '1m',              // Little: λ = L_cap / W
    duration: dur('12m'),                                // 2 min de llenado (M-24) + 10 min estables (§4.2)
    preAllocatedVUs: vus(Math.ceil(1.5 * L_CAP)), maxVUs: vus(2 * L_CAP), // M-15: 1.5 × L y 2 × L
    gracefulStop: dur('3m') } },
};
// Opcional 1 (escalabilidad, evidencia de H1): es el mismo escenario "estres" con Qolqe en --cpus=2 (lo fija correr.sh).

// ---------------------------------------------------------------- fases (segundos desde el inicio del escenario, §4.2)
// Cada petición lleva la etiqueta "fase"; los umbrales solo miran la fase medida, así el código de salida es el veredicto.
const FASES = {
  carga:       [[120, 'calentamiento'], [1020, 'estable'], [Infinity, 'drenaje']],   // M-24 + M-12
  resistencia: [[120, 'calentamiento'], [3720, 'estable'], [Infinity, 'drenaje']],   // M-24 + M-13
  capacidad:   [[120, 'calentamiento'], [720, 'estable'], [Infinity, 'drenaje']],    // M-24 + 10 min
  pico: [[120, 'calentamiento'], [240, 'base'], [540, 'salto'], [840, 'resto'],      // 12:00 = 240 s; 12:05 = 540 s
         [1140, 'recuperacion'], [Infinity, 'drenaje']],                             // 12:10–12:15 = 840–1140 s (U-06)
  estres: [[180, 'base'], [1560, 'rampa'], [1680, 'meseta'], [Infinity, 'drenaje']],
};
const CAMPANA = { pico: [240, 1140] };  // 12:00–12:15: la campaña (U-06, S-08)
// Con ESCALA < 1 los bordes se comprimen igual que las duraciones (ensayo comprimido).
for (const fases of Object.values(FASES)) for (const borde of fases) borde[0] *= ESCALA;
for (const tramo of Object.values(CAMPANA)) tramo.forEach((t, i) => { tramo[i] = t * ESCALA; });

export const ESCENARIO = __ENV.ESCENARIO || 'carga';

// Escenarios de k6 del escenario elegido; falla en el arranque si el nombre no existe o falta un parámetro.
export function escenariosElegidos() {
  const elegidos = ESCENARIOS[ESCENARIO];
  if (!elegidos) throw new Error(`ESCENARIO="${ESCENARIO}" no existe. Opciones: ${Object.keys(ESCENARIOS).join(', ')}`);
  if (ESCENARIO === 'capacidad' && !(L_CAP > 0)) throw new Error('El escenario "capacidad" necesita -e L_CAP=<simultáneos>');
  return elegidos;
}

// Etiquetas de tiempo a los "segundos" del escenario: {fase} y, en el pico, {campana: si|no}.
export function faseEn(escenario, segundos) {
  const fases = FASES[escenario];
  const etiquetas = { fase: fases ? fases.find(([fin]) => segundos < fin)[1] : 'unica' };
  const campana = CAMPANA[escenario];
  if (campana) etiquetas.campana = segundos >= campana[0] && segundos < campana[1] ? 'si' : 'no';
  return etiquetas;
}

// Etiquetas de tiempo de la petición actual (se calculan en cada petición).
export function etiquetasDeTiempo() {
  return faseEn(ESCENARIO, (Date.now() - exec.scenario.startTime) / 1000);
}

// VUs que puede llegar a usar el escenario elegido: hace falta una fila de usuarios.csv por cada uno (M-16).
// Se toma el máximo, no la suma: los dos sub-escenarios de la demo no se solapan y k6 reutiliza los VUs.
export function vusNecesarios() {
  return Math.max(...Object.values(escenariosElegidos()).map((e) => e.maxVUs || e.vus || 1));
}
