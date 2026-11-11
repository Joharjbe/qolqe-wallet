import { expect } from '@playwright/test';
import { DialogoConfirmacion, DialogoFormulario } from './componentes';
import { PaginaQolqe } from './PaginaQolqe';

export class ContactosPage extends PaginaQolqe {
  private readonly formulario = new DialogoFormulario(this.page);
  private readonly confirmacion = new DialogoConfirmacion(this.page);

  private filas = () => this.page.getByTestId('contacto');
  private fila = (alias: string) => this.filas().filter({ has: this.page.getByTestId('contacto-alias').getByText(alias, { exact: true }) });

  async abrir() {
    await this.nav.ir('contactos');
    // El contador se escribe al terminar la primera carga de la lista.
    await expect(this.page.getByTestId('contador-contactos')).not.toBeEmpty();
  }

  async agregar(celular: string, alias: string, dobleClic = false) {
    await this.page.getByTestId('input-celular').fill(celular);
    await this.page.getByTestId('input-alias').fill(alias);
    const boton = this.page.getByTestId('boton-agregar-contacto');
    await (dobleClic ? boton.dblclick() : boton.click());
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

  /** boton: "Anterior" o "Siguiente", como dice la pantalla. */
  async esperarBotonPagina(boton: string, habilitado: boolean) {
    await expect(this.page.getByTestId(`boton-${boton.toLowerCase()}`)).toBeEnabled({ enabled: habilitado });
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
    await this.esperarFavorito(alias, favorito);
  }

  async esperarFavorito(alias: string, favorito: boolean) {
    await expect(this.fila(alias).getByTestId('boton-favorito')).toHaveAttribute('aria-pressed', String(favorito));
  }

  async editar(alias: string, nuevoAlias: string, favorito?: boolean) {
    await this.fila(alias).getByTestId('boton-editar-contacto').click();
    await this.formulario.llenar('nuevo-alias', nuevoAlias);
    if (favorito !== undefined) await this.formulario.marcar('favorito', favorito);
    await this.formulario.guardar();
  }

  async alternarFavorito(alias: string) {
    await this.fila(alias).getByTestId('boton-favorito').click();
  }

  async eliminar(alias: string) {
    await this.fila(alias).getByTestId('boton-eliminar-contacto').click();
    await this.confirmacion.confirmar();
  }

  async irATransferir(alias: string) {
    await this.fila(alias).getByTestId('boton-transferir-contacto').click();
  }

  async solicitar(alias: string, monto: string, motivo: string) {
    await this.fila(alias).getByTestId('boton-solicitar-contacto').click();
    await this.formulario.llenar('solicitud-monto', monto);
    await this.formulario.llenar('solicitud-motivo', motivo);
    await this.formulario.guardar();
  }
}
