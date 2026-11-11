import { expect } from '@playwright/test';
import { DialogoFormulario } from './componentes';
import { PaginaQolqe } from './PaginaQolqe';

export interface DatosPerfil {
  nombres: string;
  celular?: string;
  dni?: string;
  correo: string;
}

export class PerfilPage extends PaginaQolqe {
  private readonly formulario = new DialogoFormulario(this.page);

  async abrir() {
    await this.nav.ir('perfil');
    // Los datos y los campos del formulario se llenan juntos al terminar la carga.
    await expect(this.page.getByTestId('perfil-nombres')).not.toBeEmpty();
  }

  /** Solo pulsa el menú: con la sesión vencida la pantalla no llega a cargar. */
  async pulsarEnElMenu() {
    await this.nav.ir('perfil');
  }

  async guardar(nombres: string, correo: string) {
    await this.page.getByTestId('input-nombres').fill(nombres);
    await this.page.getByTestId('input-correo').fill(correo);
    await this.page.getByTestId('boton-guardar-perfil').click();
  }

  async cerrarCuenta(pin: string) {
    await this.page.getByTestId('boton-cerrar-cuenta').click();
    await this.formulario.llenar('pin-cierre', pin);
    await this.formulario.guardar();
  }

  async esperarMensaje(texto: string) {
    await expect(this.page.getByTestId('perfil-mensaje')).toHaveText(texto);
  }

  async esperarDatos({ nombres, celular, dni, correo }: DatosPerfil) {
    await expect(this.page).toHaveURL(/\/perfil$/);
    await expect(this.page.getByTestId('perfil-nombres')).toHaveText(nombres);
    if (celular) await expect(this.page.getByTestId('perfil-celular')).toHaveText(celular);
    if (dni) await expect(this.page.getByTestId('perfil-dni')).toHaveText(dni);
    await expect(this.page.getByTestId('perfil-correo')).toHaveText(correo);
  }

  async esperarSinTexto(texto: string) {
    await expect(this.page.getByRole('main')).not.toContainText(texto);
  }

  async esperarSoloNombresYCorreoEditables() {
    await expect(this.page.getByText('El DNI y el celular no se pueden modificar.')).toBeVisible();
    await expect(this.page.getByRole('textbox')).toHaveCount(2);
    await expect(this.page.getByTestId('input-nombres')).toBeEditable();
    await expect(this.page.getByTestId('input-correo')).toBeEditable();
    await expect(this.page.getByTestId('input-dni')).toHaveCount(0);
    await expect(this.page.getByTestId('input-celular')).toHaveCount(0);
  }
}
