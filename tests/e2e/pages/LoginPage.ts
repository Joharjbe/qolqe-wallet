import { expect, type Page } from '@playwright/test';

export class LoginPage {
  constructor(private readonly page: Page) {}

  async ingresar(celular: string, pin: string) {
    await this.page.goto('/login');
    await this.page.getByTestId('input-celular').fill(celular);
    await this.page.getByTestId('input-pin').fill(pin);
    await this.page.getByTestId('boton-ingresar').click();
    await expect(this.page.getByTestId('nav-contactos')).toBeVisible();
  }

  async cerrarSesion() {
    await this.page.getByTestId('boton-cerrar-sesion').click();
    await expect(this.page.getByTestId('boton-ingresar')).toBeVisible();
  }
}
