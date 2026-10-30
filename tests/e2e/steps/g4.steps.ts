import { Given, Then, USUARIOS, When } from '../fixtures';

// ---------- Preparación ----------

Given('que {string} ingresó a Qolqe', async ({ login }, nombre: string) => {
  await login.ingresar(USUARIOS[nombre].celular, USUARIOS[nombre].pin);
});

Given('que {string} tiene el contacto {string} con alias {string}', async ({ datos }, nombre: string, celular: string, alias: string) => {
  await datos.crearContacto(nombre, celular, alias);
});

Given('que {string} tiene {int} contactos y {string} es favorito', async ({ datos }, nombre: string, total: number, favorito: string) => {
  await datos.completarContactos(nombre, total, favorito);
});

Given('que {string} le solicitó {string} a {string} por {string}', async ({ datos }, de: string, monto: string, a: string, motivo: string) => {
  await datos.crearSolicitud(de, a, monto, motivo);
});

// ---------- Navegación ----------

When('abre la pantalla de contactos', async ({ contactos }) => contactos.abrir());
When('abre la pantalla de solicitudes', async ({ solicitudes }) => solicitudes.abrir());

When('cierra sesión e ingresa como {string}', async ({ login }, nombre: string) => {
  await login.cerrarSesion();
  await login.ingresar(USUARIOS[nombre].celular, USUARIOS[nombre].pin);
});

// ---------- Contactos ----------

When('agrega el contacto {string} con alias {string}', async ({ contactos }, celular: string, alias: string) => {
  await contactos.agregar(celular, alias);
});

When('pasa a la página siguiente', async ({ contactos }) => contactos.paginaSiguiente());
When('busca {string}', async ({ contactos }, texto: string) => contactos.buscar(texto));

When('edita {string} con el alias {string} y la marca como favorito', async ({ contactos }, alias: string, nuevo: string) => {
  await contactos.editar(alias, nuevo, true);
});

When('elimina el contacto {string} y confirma', async ({ contactos, comun }, alias: string) => {
  await contactos.pulsarEliminar(alias);
  await comun.confirmar();
});

When('transfiere {string} al contacto {string}', async ({ contactos, transferir }, monto: string, alias: string) => {
  await contactos.irATransferir(alias);
  await transferir.transferirAlContactoElegido(monto);
});

When('solicita {string} al contacto {string} por {string}', async ({ contactos }, monto: string, alias: string, motivo: string) => {
  await contactos.solicitar(alias, monto, motivo);
});

Then('ve el error de contactos {string}', async ({ contactos }, texto: string) => contactos.esperarError(texto));
Then('el contacto {string} aparece en la lista', async ({ contactos }, alias: string) => contactos.esperarPresente(alias));
Then('el contacto {string} no aparece en la lista', async ({ contactos }, alias: string) => contactos.esperarAusente(alias));
Then('el primer contacto de la lista es {string}', async ({ contactos }, alias: string) => contactos.esperarPrimero(alias));
Then('la lista solo muestra el contacto {string}', async ({ contactos }, alias: string) => contactos.esperarUnico(alias));

Then('la página muestra {int} contactos con el texto {string} y {string}', async ({ contactos }, n: number, contador: string, pagina: string) => {
  await contactos.esperarPagina(n, contador, pagina);
});

Then('el contacto {string} muestra {string} y está marcado como favorito', async ({ contactos }, alias: string, detalle: string) => {
  await contactos.esperarDetalle(alias, detalle, true);
});

Then('el contacto {string} muestra {string} y no está marcado como favorito', async ({ contactos }, alias: string, detalle: string) => {
  await contactos.esperarDetalle(alias, detalle, false);
});

Then('el comprobante muestra destino {string}, total {string} y saldo {string}', async ({ transferir }, destino: string, total: string, saldo: string) => {
  await transferir.esperarComprobante(destino, total, saldo);
});

// ---------- Solicitudes ----------

When('solicita {string} a {string} por {string}', async ({ solicitudes }, monto: string, alias: string, motivo: string) => {
  await solicitudes.solicitar(alias, monto, motivo);
});

When('acepta la solicitud {string}', async ({ solicitudes }, motivo: string) => solicitudes.aceptar(motivo));
When('rechaza la solicitud {string} con el motivo {string}', async ({ solicitudes }, motivo: string, razon: string) => solicitudes.rechazar(motivo, razon));
When('cancela la solicitud {string}', async ({ solicitudes }, motivo: string) => solicitudes.cancelar(motivo));
When('va a la pestaña {string}', async ({ solicitudes }, vista: string) => solicitudes.irAPestana(vista));
When('filtra por el estado {string}', async ({ solicitudes }, estado: string) => solicitudes.filtrar(estado));

Then('ve la confirmación {string}', async ({ solicitudes }, texto: string) => solicitudes.esperarMensaje(texto));
Then('la solicitud {string} está {string}', async ({ solicitudes }, motivo: string, estado: string) => solicitudes.esperarEstado(motivo, estado));
Then('la solicitud {string} muestra {string}', async ({ solicitudes }, motivo: string, texto: string) => solicitudes.esperarDetalle(motivo, texto));
Then('la solicitud {string} no aparece', async ({ solicitudes }, motivo: string) => solicitudes.esperarAusente(motivo));
Then('ve {int} solicitudes', async ({ solicitudes }, n: number) => solicitudes.esperarCantidad(n));

Then('la primera solicitud está {string} y no ofrece aceptar ni rechazar', async ({ solicitudes }, estado: string) => {
  await solicitudes.esperarPrimeraSinAcciones(estado);
});

// ---------- Comunes ----------

Then('ve el aviso {string}', async ({ comun }, texto: string) => comun.esperarAviso(texto));
Then('ve el mensaje vacío {string}', async ({ comun }, texto: string) => comun.esperarMensajeVacio(texto));
Then('su saldo en inicio es {string}', async ({ comun }, saldo: string) => comun.esperarSaldo(saldo));
