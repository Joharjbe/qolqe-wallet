import { defineConfig, devices } from '@playwright/test';
import { defineBddConfig } from 'playwright-bdd';

const BASE_URL = process.env.QOLQE_URL ?? 'http://127.0.0.1:8000';
const PUERTO = new URL(BASE_URL).port || '8000';
const CI = Boolean(process.env.CI);
// EVIDENCIA=con-imagenes: captura, video y traza de cada prueba. Sin la variable o con sin-imagenes: solo de los fallos.
const CON_IMAGENES = process.env.EVIDENCIA === 'con-imagenes';

const testDir = defineBddConfig({
  features: 'features/web/*.feature',
  steps: ['tests/e2e/steps/*.ts', 'tests/e2e/fixtures.ts'],
  outputDir: '.features-gen',
});

export default defineConfig({
  testDir,
  outputDir: 'reportes/web/resultados',
  // Las pruebas comparten una sola base de datos que se reinicia en cada escenario.
  fullyParallel: false,
  workers: 1,
  forbidOnly: CI,
  // Un reintento solo sirve para diagnosticar: failOnFlakyTests hace que un flaky ponga el pipeline en rojo.
  retries: CI ? 1 : 0,
  failOnFlakyTests: CI,
  reporter: [
    ['list'],
    ['html', { outputFolder: 'reportes/web/html', open: 'never' }],
    // includeRetries deja el intento fallido de un flaky como <flakyFailure>: la trazabilidad lo marca inestable.
    ['junit', { outputFile: 'reportes/web/junit.xml', includeRetries: true }],
  ],
  use: {
    baseURL: BASE_URL,
    testIdAttribute: 'data-testid',
    screenshot: CON_IMAGENES ? 'on' : 'only-on-failure',
    video: CON_IMAGENES ? 'on' : 'on-first-retry',
    trace: CON_IMAGENES ? 'on' : 'retain-on-failure',
    // Solo para la demo: SLOWMO=700 hace visibles los pasos en el navegador.
    launchOptions: { slowMo: Number(process.env.SLOWMO ?? 0) },
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    command: `python -m uvicorn qolqe.main:app --host 127.0.0.1 --port ${PUERTO}`,
    url: `${BASE_URL}/api/salud`,
    reuseExistingServer: true,
    timeout: 60_000,
    env: { QOLQE_BD: '.demo-data/e2e.db', QOLQE_MODO_PRUEBA: '1' },
  },
});
