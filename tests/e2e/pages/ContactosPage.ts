import { expect, type Page } from '@playwright/test';

export class ContactosPage {
  constructor(private readonly page: Page) {}

  private filas = () => this.page.getByTestId('contacto');
  private fila = (alias: string) => this.filas().filter({ has: this.page.getByTestId('contacto-alias').getByText(alias, { exact: true }) });

  async abrir() {
    await this.page.getByTestId('nav-contactos').click();
    await expect(this.page.getByTestId('boton-agregar-contacto')).toBeVisible();
  }

  async agregar(celular: string, alias: string) {
    await this.page.getByTestId('input-celular').fill(celular);
    await this.page.getByTestId('input-alias').fill(alias);
    await this.page.getByTestId('boton-agregar-contacto').click();
  }

  async esperarError(texto: string) {
    await expect(this.page.getByTestId('contactos-error')).toContainText(texto);
  }

  async esperarPresente(alias: string) {
    await expect(this.fila(alias)).toBeVisible();
  }

  async esperarAusente(alias: string) {
    await expect(this.page.getByTestId('contador-contactos')).not.toBeEmpty();
    await expect(this.fila(alias)).toHaveCount(0);
  }

  async esperarPrimero(alias: string) {
    await expect(this.filas().first().getByTestId('contacto-alias')).toHaveText(alias);
  }

  async esperarPagina(cantidad: number, contador: string, indicador: string) {
    await expect(this.filas()).toHaveCount(cantidad);
    await expect(this.page.getByTestId('contador-contactos')).toHaveText(contador);
    await expect(this.page.getByTestId('indicador-pagina')).toHaveText(indicador);
  }

  async paginaSiguiente() {
    await this.page.getByTestId('boton-siguiente').click();
  }

  async buscar(texto: string) {
    await this.page.getByTestId('input-buscar-contacto').fill(texto);
  }

  async esperarUnico(alias: string) {
    await expect(this.filas()).toHaveCount(1);
    await this.esperarPresente(alias);
  }

  async esperarDetalle(alias: string, detalle: string, favorito: boolean) {
    const fila = this.fila(alias);
    await expect(fila.getByTestId('contacto-detalle')).toHaveText(detalle);
    await expect(fila.getByTestId('boton-favorito')).toHaveAttribute('aria-pressed', String(favorito));
  }

  async editar(alias: string, nuevoAlias: string, favorito: boolean) {
    await this.fila(alias).getByTestId('boton-editar-contacto').click();
    await this.page.getByTestId('input-nuevo-alias').fill(nuevoAlias);
    await this.page.getByTestId('input-favorito').setChecked(favorito);
    await this.page.getByTestId('boton-guardar-dialogo').click();
  }

  async pulsarEliminar(alias: string) {
    await this.fila(alias).getByTestId('boton-eliminar-contacto').click();
  }

  async irATransferir(alias: string) {
    await this.fila(alias).getByTestId('boton-transferir-contacto').click();
  }

  async solicitar(alias: string, monto: string, motivo: string) {
    await this.fila(alias).getByTestId('boton-solicitar-contacto').click();
    await this.page.getByTestId('input-solicitud-monto').last().fill(monto);
    await this.page.getByTestId('input-solicitud-motivo').last().fill(motivo);
    await this.page.getByTestId('boton-guardar-dialogo').click();
  }
}
