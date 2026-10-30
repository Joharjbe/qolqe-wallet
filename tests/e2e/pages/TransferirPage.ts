import { expect, type Page } from '@playwright/test';

export class TransferirPage {
  constructor(private readonly page: Page) {}

  async transferirAlContactoElegido(monto: string) {
    await expect(this.page.getByTestId('input-celular-destino')).toBeDisabled();
    await this.page.getByTestId('input-monto').fill(monto);
    await this.page.getByTestId('boton-continuar').click();
    await expect(this.page.getByTestId('dialogo-confirmacion')).toBeVisible();
    await this.page.getByTestId('boton-confirmar').click();
  }

  async esperarComprobante(destino: string, total: string, saldo: string) {
    await expect(this.page.getByTestId('comprobante-destino')).toHaveText(destino);
    await expect(this.page.getByTestId('comprobante-total')).toHaveText(total);
    await expect(this.page.getByTestId('comprobante-saldo')).toHaveText(saldo);
    await expect(this.page.getByTestId('comprobante-codigo')).not.toBeEmpty();
  }
}
