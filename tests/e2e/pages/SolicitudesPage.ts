import { expect } from '@playwright/test';
import { DialogoConfirmacion, DialogoFormulario } from './componentes';
import { PaginaQolqe } from './PaginaQolqe';

export class SolicitudesPage extends PaginaQolqe {
  private readonly formulario = new DialogoFormulario(this.page);
  private readonly confirmacion = new DialogoConfirmacion(this.page);

  private filas = () => this.page.getByTestId('solicitud');
  private fila = (motivo: string) => this.filas().filter({ has: this.page.getByTestId('solicitud-motivo').getByText(motivo, { exact: true }) });

  async abrir() {
    await this.nav.ir('solicitudes');
    // La pantalla engancha pestañas y formulario después de cargar los contactos; la lista se pinta al final.
    await expect(this.page.getByTestId('lista-solicitudes').getByRole('listitem').first()).toBeVisible();
  }

  async solicitar(alias: string, monto: string, motivo: string, dobleClic = false) {
    const selector = this.page.getByTestId('select-solicitud-contacto');
    await expect(selector.locator('option', { hasText: alias })).toHaveCount(1);
    await selector.selectOption({ label: await selector.locator('option', { hasText: alias }).innerText() });
    await this.enviar(monto, motivo, dobleClic);
  }

  async enviar(monto: string, motivo: string, dobleClic = false) {
    await this.page.getByTestId('input-solicitud-monto').fill(monto);
    await this.page.getByTestId('input-solicitud-motivo').fill(motivo);
    const boton = this.page.getByTestId('boton-solicitar');
    await (dobleClic ? boton.dblclick() : boton.click());
  }

  async esperarMensaje(texto: string) {
    await expect(this.page.getByTestId('solicitud-mensaje')).toContainText(texto);
  }

  /**
   * La pestaña se marca al instante, pero la lista se vuelve a pintar cuando responde la API. Se espera un contenido
   * propio de la vista nueva (una fila "Para …" en enviadas, "De …" en recibidas, o su mensaje vacío).
   */
  async irAPestana(vista: string) {
    await this.pulsarPestana(vista);
    await expect(this.page.getByTestId(`pestana-${vista}`)).toHaveAttribute('aria-selected', 'true');
    const fila = this.page.getByTestId('solicitud-persona').filter({ hasText: vista === 'enviadas' ? /^Para / : /^De / });
    const vacia = this.page.getByTestId('lista-vacia').filter({ hasText: `No tienes solicitudes ${vista}` });
    await expect(fila.or(vacia).first()).toBeVisible();
  }

  async pulsarPestana(vista: string) {
    await this.page.getByTestId(`pestana-${vista}`).click();
  }

  async esperarPestana(vista: string, texto: string) {
    await expect(this.page.getByTestId(`pestana-${vista}`)).toHaveText(texto);
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

  async esperarSinCancelar(motivo: string) {
    await expect(this.fila(motivo)).toBeVisible();
    await expect(this.fila(motivo).getByTestId('boton-cancelar-solicitud')).toHaveCount(0);
  }

  async pulsarAceptar(motivo: string) {
    await this.fila(motivo).getByTestId('boton-aceptar-solicitud').click();
  }

  async aceptar(motivo: string) {
    await this.pulsarAceptar(motivo);
    await this.confirmacion.esperarMensaje(motivo);
    await this.confirmacion.confirmar();
  }

  async rechazar(motivo: string, razon: string) {
    await this.fila(motivo).getByTestId('boton-rechazar-solicitud').click();
    await this.formulario.llenar('motivo-rechazo', razon);
    await this.formulario.guardar();
  }

  async cancelar(motivo: string) {
    await this.fila(motivo).getByTestId('boton-cancelar-solicitud').click();
    await this.confirmacion.confirmar();
  }
}
