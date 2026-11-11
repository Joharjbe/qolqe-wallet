import { expect } from '@playwright/test';
import { Given, Then, When } from '../fixtures';

// Pantalla de solicitudes de dinero (HU-G4-06 a HU-G4-10).

Given('que {string} le solicitó {string} a {string} por {string}', async ({ datos }, de: string, monto: string, a: string, motivo: string) => {
  await datos.crearSolicitud(de, a, monto, motivo);
});

When('{string} cancela por su lado la solicitud {string}', async ({ datos }, solicitante: string, motivo: string) => {
  await datos.cancelarSolicitud(solicitante, motivo);
});

When('solicita {string} a {string} por {string}', async ({ solicitudes }, monto: string, alias: string, motivo: string) => {
  await solicitudes.solicitar(alias, monto, motivo);
});

When('solicita con doble clic {string} a {string} por {string}', async ({ solicitudes }, monto: string, alias: string, motivo: string) => {
  await solicitudes.solicitar(alias, monto, motivo, true);
});

When('envía una solicitud de {string} por {string} sin elegir contacto', async ({ solicitudes }, monto: string, motivo: string) => {
  await solicitudes.enviar(monto, motivo);
});

When('pulsa aceptar en la solicitud {string}', async ({ solicitudes }, motivo: string) => solicitudes.pulsarAceptar(motivo));
When('acepta la solicitud {string}', async ({ solicitudes }, motivo: string) => solicitudes.aceptar(motivo));
When('rechaza la solicitud {string} con el motivo {string}', async ({ solicitudes }, motivo: string, razon: string) => solicitudes.rechazar(motivo, razon));

When('rechaza la solicitud {string} con un motivo de {int} caracteres', async ({ solicitudes }, motivo: string, largo: number) => {
  await solicitudes.rechazar(motivo, 'x'.repeat(largo));
});

When('cancela la solicitud {string}', async ({ solicitudes }, motivo: string) => solicitudes.cancelar(motivo));
When('va a la pestaña {string}', async ({ solicitudes }, vista: string) => solicitudes.irAPestana(vista));
When('intenta ir a la pestaña {string}', async ({ solicitudes }, vista: string) => solicitudes.pulsarPestana(vista));
When('filtra por el estado {string}', async ({ solicitudes }, estado: string) => solicitudes.filtrar(estado));

Then('ve la confirmación {string}', async ({ solicitudes }, texto: string) => solicitudes.esperarMensaje(texto));
Then('la solicitud {string} está {string}', async ({ solicitudes }, motivo: string, estado: string) => solicitudes.esperarEstado(motivo, estado));
Then('la solicitud {string} muestra {string}', async ({ solicitudes }, motivo: string, texto: string) => solicitudes.esperarDetalle(motivo, texto));
Then('la solicitud {string} no aparece', async ({ solicitudes }, motivo: string) => solicitudes.esperarAusente(motivo));

Then('{string} no tiene solicitudes enviadas con el motivo {string}', async ({ datos }, nombre: string, motivo: string) => {
  expect(await datos.motivosEnviados(nombre)).not.toContain(motivo);
});
Then('la solicitud {string} no ofrece cancelar', async ({ solicitudes }, motivo: string) => solicitudes.esperarSinCancelar(motivo));
Then('ve {int} solicitud(es)', async ({ solicitudes }, n: number) => solicitudes.esperarCantidad(n));
Then('la pestaña {string} dice {string}', async ({ solicitudes }, vista: string, texto: string) => solicitudes.esperarPestana(vista, texto));

Then('la primera solicitud está {string} y no ofrece aceptar ni rechazar', async ({ solicitudes }, estado: string) => {
  await solicitudes.esperarPrimeraSinAcciones(estado);
});

Then('el inicio indica {string} solicitud(es) pendiente(s)', async ({ inicio }, cantidad: string) => {
  await inicio.abrir();
  await inicio.esperarSolicitudesPendientes(cantidad);
});

Then('el inicio no indica solicitudes pendientes', async ({ inicio }) => {
  await inicio.abrir();
  await inicio.esperarSolicitudesPendientes(null);
});
