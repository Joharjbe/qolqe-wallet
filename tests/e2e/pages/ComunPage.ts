import { expect, type Page } from '@playwright/test';

/** Elementos compartidos por todas las pantallas: avisos, confirmación y saldo en inicio. */
export class ComunPage {
  constructor(private readonly page: Page) {}

  async esperarAviso(texto: string) {
    await expect(this.page.getByTestId('toast').filter({ hasText: texto })).toBeVisible();
  }

  async esperarMensajeVacio(texto: string) {
    await expect(this.page.getByRole('listitem').filter({ hasText: texto })).toBeVisible();
  }

  async confirmar() {
    await this.page.getByTestId('boton-confirmar-accion').click();
  }

  async esperarSaldo(saldo: string) {
    await this.page.getByTestId('nav-inicio').click();
    await expect(this.page.getByTestId('saldo-valor')).toHaveText(saldo);
  }
}
