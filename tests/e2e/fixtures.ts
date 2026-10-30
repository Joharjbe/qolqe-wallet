import { test as base, createBdd } from 'playwright-bdd';
import type { APIRequestContext } from '@playwright/test';
import { ComunPage } from './pages/ComunPage';
import { ContactosPage } from './pages/ContactosPage';
import { LoginPage } from './pages/LoginPage';
import { SolicitudesPage } from './pages/SolicitudesPage';
import { TransferirPage } from './pages/TransferirPage';

export const USUARIOS: Record<string, { celular: string; pin: string }> = {
  Ana: { celular: '987654321', pin: '4826' },
  Bruno: { celular: '912345678', pin: '7391' },
  Carla: { celular: '956781234', pin: '5917' },
  Diego: { celular: '998877665', pin: '3604' },
};

/** Prepara datos por la API de soporte: rápido y sin depender de otras pantallas. */
export class DatosPrueba {
  constructor(private readonly api: APIRequestContext) {}

  async reiniciar() {
    await this.api.delete('/api/pruebas/reloj');
    await this.api.post('/api/pruebas/reiniciar');
  }

  private async token(nombre: string) {
    const { celular, pin } = USUARIOS[nombre];
    const r = await this.api.post('/api/auth/login', { data: { celular, pin } });
    return { Authorization: `Bearer ${(await r.json()).access_token}` };
  }

  async crearContacto(nombre: string, celular: string, alias: string) {
    const r = await this.api.post('/api/contactos', { headers: await this.token(nombre), data: { celular, alias } });
    if (!r.ok()) throw new Error(`No se pudo crear el contacto: ${await r.text()}`);
    return (await r.json()).id as number;
  }

  async completarContactos(nombre: string, total: number, favorito: string) {
    const headers = await this.token(nombre);
    const actual = (await (await this.api.get('/api/contactos', { headers })).json()).total as number;
    for (let i = actual + 1; i <= total; i++) {
      const alias = `Zeta ${String(i).padStart(2, '0')}`;
      const id = await this.crearContacto(nombre, String(900000000 + i), alias);
      if (alias === favorito) await this.api.put(`/api/contactos/${id}`, { headers, data: { favorito: true } });
    }
  }

  async crearSolicitud(solicitante: string, destinatario: string, monto: string, motivo: string) {
    const headers = await this.token(solicitante);
    const { contactos } = await (await this.api.get('/api/contactos', { headers })).json();
    const celular = USUARIOS[destinatario].celular;
    const id = contactos.find((c: { celular: string }) => c.celular === celular)?.id
      ?? await this.crearContacto(solicitante, celular, `Alias ${destinatario}`);
    const r = await this.api.post('/api/solicitudes', { headers, data: { contacto_id: id, monto, motivo } });
    if (!r.ok()) throw new Error(`No se pudo crear la solicitud: ${await r.text()}`);
  }
}

export const test = base.extend<{
  datos: DatosPrueba; login: LoginPage; comun: ComunPage;
  contactos: ContactosPage; solicitudes: SolicitudesPage; transferir: TransferirPage;
}>({
  // FIRST-Independent: el fixture corre antes de cada escenario.
  datos: [async ({ request }, use) => {
    const datos = new DatosPrueba(request);
    await datos.reiniciar();
    await use(datos);
    await request.delete('/api/pruebas/reloj');
  }, { auto: true }],
  login: async ({ page }, use) => use(new LoginPage(page)),
  comun: async ({ page }, use) => use(new ComunPage(page)),
  contactos: async ({ page }, use) => use(new ContactosPage(page)),
  solicitudes: async ({ page }, use) => use(new SolicitudesPage(page)),
  transferir: async ({ page }, use) => use(new TransferirPage(page)),
});

export const { Given, When, Then } = createBdd(test);
