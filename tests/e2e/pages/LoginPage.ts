import { expect, type Page } from '@playwright/test';

export class LoginPage {
  constructor(private readonly page: Page) {}

  async abrir() {
    await this.page.goto('/login');
  }

  /** Solo envía el formulario: sirve tanto para el ingreso correcto como para los errores. */
  async enviar(celular: string, pin: string) {
    await this.abrir();
    await this.page.getByTestId('input-celular').fill(celular);
    await this.page.getByTestId('input-pin').fill(pin);
    await this.page.getByTestId('boton-ingresar').click();
  }

  async ingresar(celular: string, pin: string) {
    await this.enviar(celular, pin);
    await expect(this.page.getByTestId('nav-contactos')).toBeVisible();
  }

  /** Simula un navegador que ya guardó su dispositivo (app.js lo lee de localStorage al abrir /login). */
  async recordarDispositivo(id: string, nombre: string) {
    await this.page.addInitScript(([clave, valor]) => localStorage.setItem(clave, valor),
      ['qolqe.dispositivo', JSON.stringify({ id, nombre })]);
  }

  async irADesbloqueo() {
    await this.page.getByTestId('enlace-desbloqueo').click();
  }

  async esperarAviso(texto: string) {
    await expect(this.page).toHaveURL(/\/login\?motivo=\w+$/);
    await expect(this.page.getByTestId('login-aviso')).toHaveText(texto);
  }

  async esperarError(texto: string) {
    await expect(this.page.getByTestId('login-error')).toHaveText(texto);
    await expect(this.page).toHaveURL(/\/login$/);
  }

  async esperarPinVacioYEnfocado() {
    await expect(this.page.getByTestId('input-pin')).toHaveValue('');
    await expect(this.page.getByTestId('input-pin')).toBeFocused();
  }

  async esperarDispositivo(texto: string) {
    await expect(this.page.getByTestId('login-dispositivo')).toHaveText(texto);
  }

  /** Sin sesión, cualquier pantalla privada termina en el ingreso sin mostrar datos de la cuenta. */
  async esperarIngresoSinDatos() {
    await expect(this.page).toHaveURL(/\/login(\?motivo=\w+)?$/);
    await expect(this.page.getByTestId('boton-ingresar')).toBeVisible();
    await expect(this.page.getByTestId('saldo-valor')).toHaveCount(0);
  }

  async esperarSesionGuardada(guardada: boolean) {
    const token = () => this.page.evaluate(() => JSON.parse(sessionStorage.getItem('qolqe.sesion') ?? 'null')?.access_token ?? null);
    if (guardada) await expect.poll(token).toEqual(expect.any(String));
    else await expect.poll(token).toBeNull();
  }

  async esperarDesbloqueo() {
    await expect(this.page).toHaveURL(/\/desbloqueo$/);
    await expect(this.page.getByTestId('input-celular')).toBeVisible();
    await expect(this.page.getByTestId('boton-solicitar-codigo')).toBeVisible();
  }
}
