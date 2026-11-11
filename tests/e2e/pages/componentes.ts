import { expect, type Page } from '@playwright/test';

// Un objeto por cada componente que app.js genera igual en todas las pantallas
// (toast, confirmar, dialogoFormulario, itemVacio y el menú). Las pantallas los componen.

/** Aviso flotante: dura 4 s y uno nuevo reemplaza al anterior. */
export class Aviso {
  constructor(private readonly page: Page) {}

  async esperar(texto: string) {
    await expect(this.page.getByTestId('toast').filter({ hasText: texto })).toBeVisible();
  }
}

/** Diálogo "¿Seguro?" con Confirmar y Cancelar. */
export class DialogoConfirmacion {
  constructor(private readonly page: Page) {}

  private raiz = () => this.page.getByTestId('dialogo-confirmar');

  async confirmar() {
    await this.raiz().getByTestId('boton-confirmar-accion').click();
  }

  async cancelar() {
    await this.raiz().getByTestId('boton-cancelar-accion').click();
  }

  async esperarMensaje(texto: string) {
    await expect(this.raiz().getByTestId('confirmar-mensaje')).toContainText(texto);
  }
}

/** Diálogo con formulario: cada campo es input-<id> y el error de la API queda dentro del diálogo abierto. */
export class DialogoFormulario {
  constructor(private readonly page: Page) {}

  private raiz = () => this.page.getByTestId('dialogo-formulario');

  async llenar(campo: string, valor: string) {
    await this.raiz().getByTestId(`input-${campo}`).fill(valor);
  }

  async marcar(campo: string, valor: boolean) {
    await this.raiz().getByTestId(`input-${campo}`).setChecked(valor);
  }

  async guardar() {
    await this.raiz().getByTestId('boton-guardar-dialogo').click();
  }

  async cancelar() {
    await this.raiz().getByTestId('boton-cancelar-dialogo').click();
    await expect(this.raiz()).toHaveCount(0);
  }

  async esperarError(texto: string) {
    await expect(this.raiz().getByTestId('dialogo-error')).toBeVisible();
    await expect(this.raiz().getByTestId('dialogo-error')).toContainText(texto);
  }
}

/** Mensaje que reemplaza a una lista sin elementos. */
export class ListaVacia {
  constructor(private readonly page: Page) {}

  async esperar(texto: string) {
    await expect(this.page.getByTestId('lista-vacia')).toHaveText(texto);
  }
}

/** Menú lateral de las pantallas con sesión. */
export class Navegacion {
  constructor(private readonly page: Page) {}

  /** Espera el documento nuevo: si ya estaba en esa pantalla, la anterior no responde por la nueva. */
  async ir(ruta: string) {
    await Promise.all([this.page.waitForEvent('framenavigated'), this.page.getByTestId(`nav-${ruta}`).click()]);
  }

  async cerrarSesion() {
    await this.page.getByTestId('boton-cerrar-sesion').click();
    await expect(this.page).toHaveURL(/\/login\?motivo=salida$/);
  }

  async volverAtras() {
    await this.page.goBack();
  }

  async esperarUsuario(nombres: string) {
    await expect(this.page.getByTestId('usuario-nombre')).toHaveText(nombres);
  }
}
