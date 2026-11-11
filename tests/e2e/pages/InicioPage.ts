import { expect } from '@playwright/test';
import { PaginaQolqe } from './PaginaQolqe';

export class InicioPage extends PaginaQolqe {
  private saldo = () => this.page.getByTestId('saldo-valor');
  private botonSaldo = () => this.page.getByTestId('boton-ocultar-saldo');

  async abrir() {
    await this.nav.ir('inicio');
    await this.esperarCargado();
  }

  /** Entra por la dirección, como alguien que escribe /inicio sin haber ingresado. */
  async abrirPorDireccion() {
    await this.page.goto('/inicio');
  }

  async alternarSaldo() {
    await this.botonSaldo().click();
  }

  async esperarCargado() {
    await expect(this.page).toHaveURL(/\/inicio$/);
    await expect(this.saldo()).toHaveText(/^S\/ /);
  }

  async esperarSaldo(saldo: string) {
    await expect(this.saldo()).toHaveText(saldo);
  }

  async esperarSaludo(saludo: string) {
    await expect(this.page.getByTestId('saludo')).toHaveText(saludo);
  }

  async esperarFormatoActualizado() {
    await expect(this.page.getByText(/^Actualizado: /)).toHaveText(/^Actualizado: \d{2}\/\d{2}\/\d{4} \d{2}:\d{2}$/);
  }

  async esperarSaldoOculto(oculto: boolean, texto: string) {
    await expect(this.saldo()).toHaveText(texto);
    await expect(this.botonSaldo()).toHaveText(oculto ? 'Mostrar saldo' : 'Ocultar saldo');
    await expect(this.botonSaldo()).toHaveAttribute('aria-pressed', String(oculto));
  }

  async esperarSinMovimientos() {
    await expect(this.page.getByTestId('lista-recientes')).toHaveText('Aún no tienes movimientos');
  }

  async esperarUltimoMovimiento(descripcion: string, importe: string) {
    const primero = this.page.getByTestId('movimiento-reciente').first();
    await expect(primero).toContainText(descripcion);
    // Texto exacto: "S/ 100.00" no debe coincidir con "-S/ 100.00".
    await expect(primero.getByText(importe, { exact: true })).toBeVisible();
  }

  async esperarSolicitudesPendientes(cantidad: string | null) {
    const insignia = this.page.getByTestId('solicitudes-pendientes');
    if (cantidad === null) await expect(insignia).toBeHidden();
    else await expect(insignia).toHaveText(cantidad);
  }
}
