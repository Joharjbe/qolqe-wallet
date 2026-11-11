import { test } from '@playwright/test';

/**
 * En un escenario @fail (test.fail()) cualquier error cuenta como el defecto esperado, también un timeout.
 * Una precondición que no se cumple vuelve a marcar el caso como "debe pasar": así falla de verdad en el reporte.
 */
export async function precondicion(comprobar: () => Promise<void>) {
  try {
    await comprobar();
  } catch (error) {
    test.info().expectedStatus = 'passed';
    throw error;
  }
}
