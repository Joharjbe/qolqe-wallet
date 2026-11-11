// Script principal de las pruebas de rendimiento de Qolqe Wallet (k6 2.3.0).
// Uso: k6 run -e ESCENARIO=<referencia|calibracion|carga|pico|estres|resistencia|demo|capacidad> tests/performance/k6/qolqe.js
// (correr_k6.sh agrega el reporte HTML, los datos crudos y la carpeta de resultados).
import http from 'k6/http';
import { sleep } from 'k6';
import exec from 'k6/execution';
import { SharedArray } from 'k6/data';
import { ESCALA, ESCENARIO, escenariosElegidos, vusNecesarios } from './escenarios.js';
import { umbralesDe } from './umbrales.js';
import { BASE_URL, OPERACIONES, login } from './operaciones.js';
import { resumen } from './resumen.js';

// ---------------------------------------------------------------- datos de prueba (§5.1, §5.3)
// C4 "un usuario distinto por VU": la fila n de usuarios.csv es del VU n (exec.vu.idInTest). Lo genera datos/preparar_datos.py.
// Columnas: vu,celular,pin,usuario_id,suministro,contactos (ids de la tabla contactos separados con "|") y, opcional,
// buscar (o busqueda): el alias que se busca en "Ver y buscar contactos".
const ARCHIVO_USUARIOS = __ENV.USUARIOS_CSV || '../datos/usuarios.csv';
function leerArchivo(ruta) {
  try {
    return open(ruta);
  } catch (e) {
    throw new Error(`No se pudo leer ${ruta}: genérelo con datos/preparar_datos.py o indique otro con -e USUARIOS_CSV=<ruta>`);
  }
}

const USUARIOS = new SharedArray('usuarios', () => {
  const [cabecera, ...filas] = leerArchivo(ARCHIVO_USUARIOS).split(/\r?\n/).filter((l) => l.trim());
  const columnas = cabecera.split(',').map((c) => c.trim());
  const usuarios = [];
  for (const linea of filas) {
    const f = Object.fromEntries(linea.split(',').map((v, i) => [columnas[i], v.trim()]));
    usuarios[Number(f.vu) - 1] = {
      celular: f.celular, pin: f.pin, id: Number(f.usuario_id), suministro: f.suministro,
      contactos: f.contactos.split('|').map(Number),
      buscar: f.buscar || f.busqueda || 'amigo', // alias de uno de sus contactos ("Amigo NNNN", §5.1)
    };
  }
  return usuarios;
});

export const options = {
  scenarios: escenariosElegidos(),
  thresholds: umbralesDe(ESCENARIO),
  summaryTrendStats: ['count', 'avg', 'min', 'med', 'p(90)', 'p(95)', 'p(99)', 'max'], // la tabla de S14 (p50, p90, p95, p99)
  summaryTimeUnit: 'ms',
};

// http_req_failed = solo 5xx y errores de red; los 4xx de negocio se separan en errores_datos (S-06, §5.4).
http.setResponseCallback(http.expectedStatuses({ min: 200, max: 499 }));

// ---------------------------------------------------------------- mezcla y think time (§3.2)
// M-06: 6 operaciones por sesión, sorteadas con reemplazo con los pesos de la tabla del requerimiento (%).
const MEZCLA = [['saldo_perfil', 30], ['movimientos', 15], ['transferir', 15], ['contactos', 10], ['recarga', 10],
  ['deudas', 6], ['pago', 4], ['limites', 2], ['alertas', 2], ['solicitudes', 2], ['dispositivos', 2], ['sesiones', 2]];
const OPERACIONES_POR_SESION = 6; // "login + 6 operaciones"
const CIERRE_S = 12 * ESCALA;     // S-13 / M-05: 120 s − 6 × 18 s = 12 s finales sin peticiones (× ESCALA en un ensayo comprimido)

function elegir() {
  let r = Math.random() * 100;
  for (const [op, peso] of MEZCLA) if ((r -= peso) < 0) return op;
  return MEZCLA[0][0];
}

// M-04 / S-14: pausa triangular(10, 19, 25) → rango 10–25 s y media exacta (10 + 19 + 25) / 3 = 18 s.
// Inversa de la distribución: F(19) = (19 − 10) / 15 = 0.6; 135 = 15 × 9 y 90 = 15 × 6.
// En un ensayo comprimido (-e ESCALA < 1) la pausa se multiplica por ESCALA, igual que las duraciones (escenarios.js).
function pausa() {
  const u = Math.random();
  return ESCALA * (u < 0.6 ? 10 + Math.sqrt(u * 135) : 25 - Math.sqrt((1 - u) * 90));
}

function usuarioDelVu() {
  const u = USUARIOS[exec.vu.idInTest - 1];
  if (!u) exec.test.abort(`El VU ${exec.vu.idInTest} no tiene usuario: ${ARCHIVO_USUARIOS} tiene ${USUARIOS.length} filas (M-16)`);
  return u;
}

// ---------------------------------------------------------------- funciones de los escenarios
export function setup() {
  const salud = http.get(`${BASE_URL}/api/salud`, { tags: { ep: 'salud', grupo: 'soporte' } });
  if (salud.status !== 200) exec.test.abort(`Qolqe no responde en ${BASE_URL}/api/salud (status ${salud.status})`);
  if (USUARIOS.length < vusNecesarios()) {
    console.warn(`${ARCHIVO_USUARIOS} tiene ${USUARIOS.length} usuarios y el escenario puede usar hasta ${vusNecesarios()} VUs`);
  }
}

// Sesión de la hora punta: login, 6 pausas + 6 operaciones ponderadas y el cierre (carga, pico, estrés, resistencia, demo).
export function sesion() {
  const u = usuarioDelVu();
  const token = login(u); // F-01
  if (token) {
    for (let i = 0; i < OPERACIONES_POR_SESION; i++) {
      sleep(pausa());
      OPERACIONES[elegir()](u, token);
    }
  }
  sleep(CIERRE_S);
}

// Demo: la misma sesión sin think time. "Un modelo de carga sin think time es una prueba de estrés disfrazada" (S13).
export function sesionSinPausa() {
  const u = usuarioDelVu();
  const token = login(u);
  if (token) for (let i = 0; i < OPERACIONES_POR_SESION; i++) OPERACIONES[elegir()](u, token);
}

// Referencia (V-06): el login y las 12 operaciones en orden fijo, con 1 s de pausa entre una y otra.
export function recorrido() {
  const u = usuarioDelVu();
  const token = login(u);
  if (!token) return;
  for (const [op] of MEZCLA) {
    sleep(1);
    OPERACIONES[op](u, token);
  }
}

// Calibración (M-14): sesiones con la mezcla y 0.5 s de pausa; correr.sh mide el CPU de Qolqe que consumen.
export function calibracion() {
  const u = usuarioDelVu();
  const token = login(u);
  if (!token) return;
  for (let i = 0; i < OPERACIONES_POR_SESION; i++) {
    sleep(0.5);
    OPERACIONES[elegir()](u, token);
  }
}

// Resumen: consola con los umbrales ✓/✗ y, si se pasa -e SALIDA=<carpeta>, resumen.json y resumen.txt (§7.1).
export function handleSummary(data) {
  return resumen(data, { escenario: ESCENARIO, baseUrl: BASE_URL, salida: __ENV.SALIDA, usuarios: ARCHIVO_USUARIOS });
}
