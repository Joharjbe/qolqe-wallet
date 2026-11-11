import { expect, type Page } from '@playwright/test';

export interface DatosRegistro {
  dni: string;
  nombres: string;
  celular: string;
  correo?: string;
  pin: string;
  confirmacion?: string;
}

export class RegistroPage {
  constructor(private readonly page: Page) {}

  async registrar({ dni, nombres, celular, correo = '', pin, confirmacion = pin }: DatosRegistro) {
    await this.page.goto('/registro');
    await this.page.getByTestId('input-dni').fill(dni);
    await this.page.getByTestId('input-nombres').fill(nombres);
    await this.page.getByTestId('input-celular').fill(celular);
    await this.page.getByTestId('input-correo').fill(correo);
    await this.page.getByTestId('input-pin').fill(pin);
    await this.page.getByTestId('input-pin-confirmacion').fill(confirmacion);
    await this.page.getByTestId('boton-registrar').click();
  }

  /** El error se muestra en la misma pantalla y el formulario queda listo para corregirlo. */
  async esperarError(texto: string) {
    await expect(this.page.getByTestId('registro-error')).toContainText(texto);
    await expect(this.page).toHaveURL(/\/registro$/);
    await expect(this.page.getByTestId('boton-registrar')).toHaveText('Crear cuenta');
    await expect(this.page.getByTestId('boton-registrar')).toBeEnabled();
  }
}
