import { expect, type Page } from '@playwright/test';
import { precondicion } from '../precondicion';

export interface DatosRegistro {
  dni: string;
  nombres: string;
  celular: string;
  correo?: string;
  pin: string;
  confirmacion?: string;
}

export class RegistroPage {
  private enviados: Required<DatosRegistro> | null = null;

  constructor(private readonly page: Page) {}

  async registrar({ dni, nombres, celular, correo = '', pin, confirmacion = pin }: DatosRegistro) {
    this.enviados = { dni, nombres, celular, correo, pin, confirmacion };
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

  /**
   * DEF-18 (@fail): el error debe hablar del campo en español, con el texto que sea. Que el error aparezca es una
   * precondición: si no aparece, el caso falla de verdad y no cuenta como el defecto esperado.
   */
  async esperarErrorEnEspanol(campo: RegExp) {
    const error = this.page.getByTestId('registro-error');
    await precondicion(() => expect(error).toBeVisible());
    await expect(error).not.toContainText(/String should|characters|at least|at most/i);
    await expect(error).toContainText(campo);
  }

  /** Después de un error de la API el formulario conserva lo que se escribió. */
  async esperarFormularioConservado() {
    if (!this.enviados) throw new Error('No se envió ningún registro en este escenario');
    const { dni, nombres, celular, correo, pin, confirmacion } = this.enviados;
    const campos = { dni, nombres, celular, correo, pin, 'pin-confirmacion': confirmacion };
    for (const [campo, valor] of Object.entries(campos)) {
      await expect(this.page.getByTestId(`input-${campo}`)).toHaveValue(valor);
    }
  }

  /** Escribe tecla por tecla, como una persona: así se aplica el maxlength del campo. */
  async escribir(campo: string, texto: string) {
    if (!/\/registro$/.test(this.page.url())) await this.page.goto('/registro');
    await this.page.getByTestId(`input-${campo}`).pressSequentially(texto);
  }

  async esperarValor(campo: string, valor: string) {
    await expect(this.page.getByTestId(`input-${campo}`)).toHaveValue(valor);
  }
}
