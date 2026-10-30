import { expect, type Page } from '@playwright/test';

export class SolicitudesPage {
  constructor(private readonly page: Page) {}

  private filas = () => this.page.getByTestId('solicitud');
  private fila = (motivo: string) => this.filas().filter({ has: this.page.getByTestId('solicitud-motivo').getByText(motivo, { exact: true }) });

  async abrir() {
    await this.page.getByTestId('nav-solicitudes').click();
    await expect(this.page.getByTestId('boton-solicitar')).toBeVisible();
  }

  async solicitar(alias: string, monto: string, motivo: string) {
    const selector = this.page.getByTestId('select-solicitud-contacto');
    await expect(selector.locator('option', { hasText: alias })).toHaveCount(1);
    await selector.selectOption({ label: await selector.locator('option', { hasText: alias }).innerText() });
    await this.page.getByTestId('input-solicitud-monto').fill(monto);
    await this.page.getByTestId('input-solicitud-motivo').fill(motivo);
    await this.page.getByTestId('boton-solicitar').click();
  }

  async esperarMensaje(texto: string) {
    await expect(this.page.getByTestId('solicitud-mensaje')).toContainText(texto);
  }

  async irAPestana(vista: string) {
    await this.page.getByTestId(`pestana-${vista}`).click();
    await expect(this.page.getByTestId(`pestana-${vista}`)).toHaveAttribute('aria-selected', 'true');
  }

  async filtrar(estado: string) {
    await this.page.getByTestId('select-filtro-estado').selectOption({ label: estado });
  }

  async esperarCantidad(cantidad: number) {
    await expect(this.filas()).toHaveCount(cantidad);
  }

  async esperarEstado(motivo: string, estado: string) {
    await expect(this.fila(motivo).getByTestId('solicitud-estado')).toHaveText(estado);
  }

  async esperarDetalle(motivo: string, texto: string) {
    await expect(this.fila(motivo).getByTestId('solicitud-detalle')).toContainText(texto);
  }

  async esperarAusente(motivo: string) {
    await expect(this.page.getByTestId('lista-solicitudes')).toBeVisible();
    await expect(this.fila(motivo)).toHaveCount(0);
  }

  async esperarPrimeraSinAcciones(estado: string) {
    const primera = this.filas().first();
    await expect(primera.getByTestId('solicitud-estado')).toHaveText(estado);
    await expect(primera.getByTestId('boton-aceptar-solicitud')).toHaveCount(0);
    await expect(primera.getByTestId('boton-rechazar-solicitud')).toHaveCount(0);
  }

  async aceptar(motivo: string) {
    await this.fila(motivo).getByTestId('boton-aceptar-solicitud').click();
    await expect(this.page.getByTestId('confirmar-mensaje')).toContainText(motivo);
    await this.page.getByTestId('boton-confirmar-accion').click();
  }

  async rechazar(motivo: string, razon: string) {
    await this.fila(motivo).getByTestId('boton-rechazar-solicitud').click();
    await this.page.getByTestId('input-motivo-rechazo').fill(razon);
    await this.page.getByTestId('boton-guardar-dialogo').click();
  }

  async cancelar(motivo: string) {
    await this.fila(motivo).getByTestId('boton-cancelar-solicitud').click();
    await this.page.getByTestId('boton-confirmar-accion').click();
  }
}
