import { test as base, createBdd } from 'playwright-bdd';
import type { APIRequestContext, APIResponse, Page } from '@playwright/test';
import { Aviso, DialogoConfirmacion, DialogoFormulario, ListaVacia, Navegacion } from './pages/componentes';
import { ContactosPage } from './pages/ContactosPage';
import { InicioPage } from './pages/InicioPage';
import { LoginPage } from './pages/LoginPage';
import { PerfilPage } from './pages/PerfilPage';
import { RegistroPage } from './pages/RegistroPage';
import { SolicitudesPage } from './pages/SolicitudesPage';
import { TransferirPage } from './pages/TransferirPage';

// Elena queda bloqueada 15 min en cada reinicio y Fabián tiene la cuenta cerrada (semilla.py).
export const USUARIOS: Record<string, { celular: string; pin: string }> = {
  Ana: { celular: '987654321', pin: '4826' },
  Bruno: { celular: '912345678', pin: '7391' },
  Carla: { celular: '956781234', pin: '5917' },
  Diego: { celular: '998877665', pin: '3604' },
  Elena: { celular: '923456789', pin: '8152' },
  Fabián: { celular: '934567812', pin: '6029' },
  'Carga 001': { celular: '900000001', pin: '2580' },
};

/** Prepara datos por la API de soporte: rápido y sin depender de otras pantallas. */
export class DatosPrueba {
  constructor(private readonly api: APIRequestContext) {}

  /** FIRST-Independent: si el reinicio falla (servidor sin QOLQE_MODO_PRUEBA, base bloqueada), el escenario no corre. */
  async reiniciar() {
    await this.exigir(this.api.delete('/api/pruebas/reloj'), 'volver al reloj real');
    await this.exigir(this.api.post('/api/pruebas/reiniciar'), 'reiniciar los datos');
  }

  /** Fija la hora de hoy y vuelve a sembrar, para que los datos relativos (como el bloqueo de Elena) partan de ella. */
  async fijarHora(hora: string) {
    const { ahora } = await (await this.exigir(this.api.get('/api/pruebas/reloj'), 'leer el reloj')).json();
    await this.exigir(this.api.put('/api/pruebas/reloj', { data: { ahora: `${ahora.slice(0, 10)}T${hora}:00` } }), 'fijar la hora');
    await this.exigir(this.api.post('/api/pruebas/reiniciar'), 'reiniciar los datos');
  }

  async avanzarReloj(minutos: number) {
    await this.exigir(this.api.put('/api/pruebas/reloj', { data: { avanzar_minutos: minutos } }), 'adelantar el reloj');
  }

  async fijarSaldo(nombre: string, saldo: string) {
    await this.exigir(this.api.put('/api/pruebas/saldo', { data: { celular: USUARIOS[nombre].celular, saldo } }), 'fijar el saldo');
  }

  async fallarIngreso(nombre: string, veces: number) {
    for (let i = 0; i < veces; i++) {
      const r = await this.api.post('/api/auth/login', { data: { celular: USUARIOS[nombre].celular, pin: '0000' } });
      if (r.status() !== 401) throw new Error(`Se esperaba 401 al fallar el PIN: ${r.status()} ${await r.text()}`);
    }
  }

  async codigoDeIngreso(celular: string, pin: string) {
    return (await this.api.post('/api/auth/login', { data: { celular, pin } })).status();
  }

  async sms(nombre: string) {
    const r = await this.exigir(this.api.get('/api/pruebas/notificaciones', { params: { celular: USUARIOS[nombre].celular } }), 'leer los SMS');
    return ((await r.json()) as { mensaje: string }[]).map((m) => m.mensaje);
  }

  async cantidadDeSms(nombre: string, texto = '') {
    return (await this.sms(nombre)).filter((m) => m.includes(texto)).length;
  }

  private async exigir(peticion: Promise<APIResponse>, accion: string) {
    const r = await peticion;
    if (!r.ok()) throw new Error(`No se pudo ${accion}: ${await r.text()}`);
    return r;
  }

  private async token(nombre: string) {
    const { celular, pin } = USUARIOS[nombre];
    const r = await this.exigir(this.api.post('/api/auth/login', { data: { celular, pin } }), `ingresar como ${nombre}`);
    return { Authorization: `Bearer ${(await r.json()).access_token}` };
  }

  async crearContacto(nombre: string, celular: string, alias: string) {
    const r = await this.exigir(this.api.post('/api/contactos', { headers: await this.token(nombre), data: { celular, alias } }), 'crear el contacto');
    return (await r.json()).id as number;
  }

  async completarContactos(nombre: string, total: number, favoritos: string[]) {
    const headers = await this.token(nombre);
    const actual = (await (await this.api.get('/api/contactos', { headers })).json()).total as number;
    for (let i = actual + 1; i <= total; i++) {
      const alias = `Zeta ${String(i).padStart(2, '0')}`;
      const id = await this.crearContacto(nombre, String(900000000 + i), alias);
      if (favoritos.includes(alias)) await this.exigir(this.api.put(`/api/contactos/${id}`, { headers, data: { favorito: true } }), 'marcar el favorito');
    }
  }

  async crearSolicitud(solicitante: string, destinatario: string, monto: string, motivo: string) {
    const headers = await this.token(solicitante);
    const { contactos } = await (await this.api.get('/api/contactos', { headers })).json();
    const celular = USUARIOS[destinatario].celular;
    const id = contactos.find((c: { celular: string }) => c.celular === celular)?.id
      ?? await this.crearContacto(solicitante, celular, `Alias ${destinatario}`);
    await this.exigir(this.api.post('/api/solicitudes', { headers, data: { contacto_id: id, monto, motivo } }), 'crear la solicitud');
  }

  /** Motivos de las solicitudes enviadas, leídos por la API: confirman lo que la pantalla no creó. */
  async motivosEnviados(nombre: string) {
    const r = await this.exigir(this.api.get('/api/solicitudes', { headers: await this.token(nombre) }), 'leer las solicitudes');
    return ((await r.json()).enviadas as { motivo: string }[]).map((s) => s.motivo);
  }

  async cancelarSolicitud(solicitante: string, motivo: string) {
    const headers = await this.token(solicitante);
    const { enviadas } = await (await this.api.get('/api/solicitudes', { headers })).json();
    const id = enviadas.find((s: { motivo: string }) => s.motivo === motivo)?.id;
    await this.exigir(this.api.post(`/api/solicitudes/${id}/cancelar`, { headers }), 'cancelar la solicitud');
  }

  async transferir(origen: string, destino: string, monto: string, descripcion: string) {
    const data = { tipo: 'QOLQE', monto, celular_destino: USUARIOS[destino].celular, descripcion };
    await this.exigir(this.api.post('/api/transferencias', { headers: await this.token(origen), data }), 'transferir');
  }
}

/** Anota las peticiones que la pantalla envía a la API, con su cuerpo: algunas reglas solo existen en la interfaz. */
export class Peticiones {
  private readonly enviadas: { peticion: string; cuerpo: string | null }[] = [];

  constructor(page: Page) {
    page.on('request', (r) => this.enviadas.push({ peticion: `${r.method()} ${new URL(r.url()).pathname}`, cuerpo: r.postData() }));
  }

  cantidad(peticion: string) {
    return this.enviadas.filter((p) => p.peticion === peticion).length;
  }

  /** Cuerpo JSON de la última petición de ese tipo (null si no salió ninguna). */
  ultimoCuerpo(peticion: string): Record<string, unknown> | null {
    const ultima = this.enviadas.filter((p) => p.peticion === peticion).at(-1);
    return ultima?.cuerpo ? JSON.parse(ultima.cuerpo) : null;
  }
}

/** Una segunda sesión en otro navegador (contexto aislado, con su propio sessionStorage). */
export interface OtroNavegador {
  login: LoginPage;
  inicio: InicioPage;
  nav: Navegacion;
}

export const test = base.extend<{
  datos: DatosPrueba; peticiones: Peticiones; otroNavegador: OtroNavegador;
  login: LoginPage; registro: RegistroPage; inicio: InicioPage; perfil: PerfilPage;
  contactos: ContactosPage; solicitudes: SolicitudesPage; transferir: TransferirPage;
  aviso: Aviso; confirmacion: DialogoConfirmacion; formulario: DialogoFormulario; listaVacia: ListaVacia; nav: Navegacion;
}>({
  // FIRST-Independent: el fixture corre antes de cada escenario.
  datos: [async ({ request }, use) => {
    const datos = new DatosPrueba(request);
    await datos.reiniciar();
    await use(datos);
    await request.delete('/api/pruebas/reloj');
  }, { auto: true }],
  peticiones: async ({ page }, use) => use(new Peticiones(page)),
  otroNavegador: async ({ browser }, use) => {
    const contexto = await browser.newContext();
    const pagina = await contexto.newPage();
    await use({ login: new LoginPage(pagina), inicio: new InicioPage(pagina), nav: new Navegacion(pagina) });
    await contexto.close();
  },
  login: async ({ page }, use) => use(new LoginPage(page)),
  registro: async ({ page }, use) => use(new RegistroPage(page)),
  inicio: async ({ page }, use) => use(new InicioPage(page)),
  perfil: async ({ page }, use) => use(new PerfilPage(page)),
  contactos: async ({ page }, use) => use(new ContactosPage(page)),
  solicitudes: async ({ page }, use) => use(new SolicitudesPage(page)),
  transferir: async ({ page }, use) => use(new TransferirPage(page)),
  aviso: async ({ page }, use) => use(new Aviso(page)),
  confirmacion: async ({ page }, use) => use(new DialogoConfirmacion(page)),
  formulario: async ({ page }, use) => use(new DialogoFormulario(page)),
  listaVacia: async ({ page }, use) => use(new ListaVacia(page)),
  nav: async ({ page }, use) => use(new Navegacion(page)),
});

export const { Given, When, Then } = createBdd(test);
