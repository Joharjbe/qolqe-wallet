// Resumen de fin de prueba (handleSummary): la consola muestra cada umbral con ✓/✗, su ID y el valor medido,
// y se guardan resumen.json (datos completos de k6 + veredicto) y resumen.txt en la carpeta de la corrida (§7.1).
import { DESCRIPCIONES } from './umbrales.js';

const LIMA_MS = -5 * 3600 * 1000; // hora de Lima (UTC−5, sin horario de verano), para cruzar con los recursos (D11)
const horaLima = (ms) => new Date(ms + LIMA_MS).toISOString().replace('Z', '-05:00');

// "p(95)<800" → valor de la estadística p(95) de la métrica, con su unidad.
function valorMedido(metrica, condicion) {
  const estadistica = condicion.split(/<=|>=|==|!=|<|>/)[0].trim();
  const v = metrica.values[estadistica];
  if (v === undefined) return '—';
  if (estadistica === 'rate') return `${(100 * v).toFixed(2)} %`;
  if (estadistica === 'count') return String(v);
  return metrica.type === 'trend' ? `${v.toFixed(1)} ms` : String(v);
}

// Muestras de la sub-métrica. k6 da por cumplido un umbral sin muestras (p. ej., una fase que no llegó a correr):
// aquí se marca aparte para no confundir "no se midió" con "pasó".
function muestras(metrica) {
  if (metrica.type === 'trend') return metrica.values.count;
  if (metrica.type === 'rate') return metrica.values.passes + metrica.values.fails;
  return null; // contador: 0 es un valor medido (p. ej., 0 sesiones descartadas)
}

function evaluarUmbrales(data) {
  const filas = [];
  for (const [clave, descripcion] of Object.entries(DESCRIPCIONES)) {
    const metrica = data.metrics[clave];
    for (const [condicion, estado] of Object.entries((metrica && metrica.thresholds) || {})) {
      const n = muestras(metrica);
      filas.push({ descripcion, metrica: clave, condicion, ok: estado.ok, muestras: n, sin_muestras: n === 0,
        valor: n === 0 ? 'sin muestras' : valorMedido(metrica, condicion) });
    }
  }
  return filas;
}

function veredicto(filas) {
  if (filas.some((f) => !f.ok)) return 'falla';
  return filas.some((f) => f.sin_muestras) ? 'incompleto (hay umbrales sin muestras)' : 'pasa';
}

const valor = (data, nombre, estadistica) => ((data.metrics[nombre] || {}).values || {})[estadistica] || 0;

function texto(meta, filas, data) {
  const ancho = Math.max(...filas.map((f) => f.descripcion.length), 10);
  const lineas = [
    '', `Qolqe · escenario ${meta.escenario} · ${meta.inicio_lima} → ${meta.fin_lima} · ${meta.base_url}`,
    'Umbrales (k6 termina con código 99 si alguno falla):',
    ...filas.map((f) => `  ${f.sin_muestras ? '○' : f.ok ? '✓' : '✗'} ${f.descripcion.padEnd(ancho)}  ${f.condicion.padEnd(14)} ` +
      `medido ${f.valor.padStart(12)}${f.muestras ? ` (n=${f.muestras})` : ''}   ${f.metrica}`),
    `Veredicto: ${filas.filter((f) => f.ok && !f.sin_muestras).length} de ${filas.length} umbrales cumplidos con muestras → ` +
      `${meta.veredicto.toUpperCase()}   (✓ cumple · ✗ falla · ○ sin muestras)`,
    `Peticiones ${valor(data, 'http_reqs', 'count')} (${valor(data, 'http_reqs', 'rate').toFixed(2)} req/s en toda la corrida) · ` +
      `sesiones ${valor(data, 'iterations', 'count')} · descartadas ${valor(data, 'dropped_iterations', 'count')} · ` +
      `VUs máx. ${valor(data, 'vus_max', 'max')}`,
    `Operaciones fallidas (rendimiento) ${(100 * valor(data, 'operacion_fallida', 'rate')).toFixed(2)} % · ` +
      `errores de rendimiento ${valor(data, 'errores_rendimiento', 'count')} · errores de datos ${valor(data, 'errores_datos', 'count')} · ` +
      `dinero confirmado ${valor(data, 'dinero_confirmado', 'count')} · dinero sin respuesta ${valor(data, 'dinero_sin_respuesta', 'count')}`,
    `http_req_duration total: p50 ${valor(data, 'http_req_duration', 'med').toFixed(1)} ms · p95 ${valor(data, 'http_req_duration', 'p(95)').toFixed(1)} ms · ` +
      `http_req_connecting p95 ${valor(data, 'http_req_connecting', 'p(95)').toFixed(2)} ms`,
    '',
  ];
  return lineas.join('\n');
}

export function resumen(data, { escenario, baseUrl, salida, usuarios }) {
  const fin = Date.now();
  const inicio = fin - Math.round(data.state.testRunDurationMs);
  const filas = evaluarUmbrales(data);
  const meta = {
    escenario, base_url: baseUrl, usuarios_csv: usuarios, top: __ENV.TOP || null, l_cap: __ENV.L_CAP || null,
    escala: Number(__ENV.ESCALA || 1), // ensayo comprimido (escenarios.js): 1 = el diseño tal cual
    inicio_epoch_ms: inicio, fin_epoch_ms: fin, inicio_lima: horaLima(inicio), fin_lima: horaLima(fin),
    veredicto: veredicto(filas), umbrales: filas,
  };
  const consola = texto(meta, filas, data);
  const archivos = { stdout: consola };
  if (salida) {
    archivos[`${salida}/resumen.json`] = JSON.stringify({ qolqe: meta, ...data }, null, 2);
    archivos[`${salida}/resumen.txt`] = consola;
  }
  return archivos;
}
