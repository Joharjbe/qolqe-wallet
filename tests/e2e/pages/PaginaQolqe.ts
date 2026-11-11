import type { Page } from '@playwright/test';
import { Navegacion } from './componentes';

/**
 * Base de un solo nivel para las pantallas con menú. Las pantallas no heredan entre sí:
 * cada una crea como campo los diálogos que usa (después de super(), así `this.page` ya existe).
 */
export abstract class PaginaQolqe {
  protected readonly nav: Navegacion;

  constructor(protected readonly page: Page) {
    this.nav = new Navegacion(page);
  }
}
