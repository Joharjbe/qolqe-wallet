import { expect } from '@playwright/test';
import { PaginaQolqe } from './PaginaQolqe';

export interface Comprobante {
  destino: string;
  monto?: string;
  comision?: string;
  total: string;
  saldo: string;
}

/** Pantalla /transferir: tiene su propio diálogo de confirmación (no el compartido de app.js). */
export class TransferirPage extends PaginaQolqe {
  private dialogo = () => this.page.getByTestId('dialogo-confirmacion');
  private selectorContacto = () => this.page.getByTestId('select-contacto');

  async abrir() {
    await this.nav.ir('transferir');
    // El formulario se engancha después de cargar los contactos en el selector.
    // Todos los usuarios de estos escenarios tienen al menos un contacto.
    await expect(this.selectorContacto().locator('option').nth(1)).toBeAttached();
  }

  async elegirPestana(tipo: 'qolqe' | 'interbancaria') {
    await this.page.getByTestId(`pestana-${tipo}`).click();
    await expect(this.page.getByTestId(`pestana-${tipo}`)).toHaveAttribute('aria-selected', 'true');
  }

  async elegirContacto(opcion: string) {
    await this.selectorContacto().selectOption({ label: opcion });
  }

  async continuarAlCelular(celular: string, monto: string, descripcion = '') {
    await this.page.getByTestId('input-celular-destino').fill(celular);
    await this.continuar(monto, descripcion);
  }

  async continuarAlCci(cci: string, monto: string) {
    await this.elegirPestana('interbancaria');
    await this.page.getByTestId('input-cci').fill(cci);
    await this.continuar(monto);
  }

  async continuar(monto: string, descripcion = '') {
    await this.page.getByTestId('input-monto').fill(monto);
    await this.page.getByTestId('input-descripcion').fill(descripcion);
    await this.page.getByTestId('boton-continuar').click();
  }

  async confirmar() {
    await this.dialogo().getByTestId('boton-confirmar').click();
  }

  async cancelar() {
    await this.dialogo().getByTestId('boton-cancelar').click();
  }

  async nuevaTransferencia() {
    await this.page.getByTestId('boton-nueva-transferencia').click();
  }

  async transferirAlContactoElegido(monto: string) {
    await expect(this.page.getByTestId('input-celular-destino')).toBeDisabled();
    await this.continuar(monto);
    await expect(this.dialogo()).toBeVisible();
    await this.confirmar();
  }

  async esperarOpcionContacto(opcion: string) {
    await expect(this.selectorContacto().locator('option', { hasText: opcion })).toHaveCount(1);
  }

  async esperarCelularBloqueado() {
    await expect(this.page.getByTestId('input-celular-destino')).toBeDisabled();
  }

  async esperarConfirmacion(destino: string, monto: string, comision: string, total: string) {
    await expect(this.dialogo()).toBeVisible();
    await expect(this.dialogo().getByTestId('confirmar-destino')).toHaveText(destino);
    await expect(this.dialogo().getByTestId('confirmar-monto')).toHaveText(monto);
    await expect(this.dialogo().getByTestId('confirmar-comision')).toHaveText(comision);
    await expect(this.dialogo().getByTestId('confirmar-total')).toHaveText(total);
  }

  async esperarSinConfirmacion() {
    await expect(this.dialogo()).toBeHidden();
  }

  async esperarError(texto: string) {
    await expect(this.page.getByTestId('transferencia-error')).toHaveText(texto);
    await expect(this.dialogo()).toBeHidden();
  }

  async esperarComprobante({ destino, monto, comision, total, saldo }: Comprobante) {
    const comprobante = this.page.getByTestId('comprobante');
    await expect(comprobante).toBeVisible();
    await expect(comprobante.getByTestId('comprobante-destino')).toHaveText(destino);
    if (monto) await expect(comprobante.getByTestId('comprobante-monto')).toHaveText(monto);
    if (comision) await expect(comprobante.getByTestId('comprobante-comision')).toHaveText(comision);
    await expect(comprobante.getByTestId('comprobante-total')).toHaveText(total);
    await expect(comprobante.getByTestId('comprobante-saldo')).toHaveText(saldo);
    await expect(comprobante.getByTestId('comprobante-codigo')).not.toBeEmpty();
  }

  async esperarCodigoYFecha() {
    await expect(this.page.getByTestId('comprobante-codigo')).toHaveText(/^TRF\d{17}$/);
    await expect(this.page.getByTestId('comprobante-fecha')).toHaveText(/^\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}$/);
  }

  async esperarSinComprobante() {
    await expect(this.page.getByTestId('comprobante')).toBeHidden();
  }

  async esperarFormularioVacio() {
    await expect(this.page.getByTestId('comprobante')).toBeHidden();
    await expect(this.page.getByTestId('input-celular-destino')).toBeEditable();
    await expect(this.page.getByTestId('input-celular-destino')).toHaveValue('');
    await expect(this.page.getByTestId('input-monto')).toHaveValue('');
    await expect(this.page.getByTestId('input-descripcion')).toHaveValue('');
  }
}
