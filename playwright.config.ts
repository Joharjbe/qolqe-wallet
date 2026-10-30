import { defineConfig, devices } from '@playwright/test';
import { defineBddConfig } from 'playwright-bdd';

const BASE_URL = process.env.QOLQE_URL ?? 'http://127.0.0.1:8000';
const CI = Boolean(process.env.CI);

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
    ['junit', { outputFile: 'reportes/web/junit.xml' }],
  ],
  use: {
    baseURL: BASE_URL,
    testIdAttribute: 'data-testid',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    command: 'python -m uvicorn qolqe.main:app --host 127.0.0.1 --port 8000',
    url: `${BASE_URL}/api/salud`,
    reuseExistingServer: true,
    timeout: 60_000,
    env: { QOLQE_BD: '.demo-data/e2e.db', QOLQE_MODO_PRUEBA: '1' },
  },
});
