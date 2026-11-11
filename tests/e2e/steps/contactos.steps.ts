import { Given, Then, When } from '../fixtures';

// Pantalla de contactos (HU-G4-01 a HU-G4-05).

Given('que {string} tiene el contacto {string} con alias {string}', async ({ datos }, nombre: string, celular: string, alias: string) => {
  await datos.crearContacto(nombre, celular, alias);
});

Given('que {string} tiene {int} contactos', async ({ datos }, nombre: string, total: number) => {
  await datos.completarContactos(nombre, total, []);
});

Given('que {string} tiene {int} contactos y {string} es favorito', async ({ datos }, nombre: string, total: number, favorito: string) => {
  await datos.completarContactos(nombre, total, [favorito]);
});

Given('que {string} tiene {int} contactos y sus favoritos son {string}', async ({ datos }, nombre: string, total: number, favoritos: string) => {
  await datos.completarContactos(nombre, total, favoritos.split(', '));
});

When('agrega el contacto {string} con alias {string}', async ({ contactos }, celular: string, alias: string) => {
  await contactos.agregar(celular, alias);
});

When('agrega con doble clic el contacto {string} con alias {string}', async ({ contactos }, celular: string, alias: string) => {
  await contactos.agregar(celular, alias, true);
});

When('pasa a la página siguiente', async ({ contactos }) => contactos.paginaSiguiente());
When('busca {string}', async ({ contactos }, texto: string) => contactos.buscar(texto));

When('edita {string} con el alias {string} y la marca como favorito', async ({ contactos }, alias: string, nuevo: string) => {
  await contactos.editar(alias, nuevo, true);
});

When('edita {string} con el alias {string}', async ({ contactos }, alias: string, nuevo: string) => {
  await contactos.editar(alias, nuevo);
});

When('pulsa la estrella de {string}', async ({ contactos }, alias: string) => contactos.alternarFavorito(alias));
When('elimina el contacto {string} y confirma', async ({ contactos }, alias: string) => contactos.eliminar(alias));

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

Then('la página muestra {int} contacto(s) con el texto {string} y {string}', async ({ contactos }, n: number, contador: string, pagina: string) => {
  await contactos.esperarPagina(n, contador, pagina);
});

Then('el botón {string} está habilitado', async ({ contactos }, boton: string) => contactos.esperarBotonPagina(boton, true));
Then('el botón {string} está deshabilitado', async ({ contactos }, boton: string) => contactos.esperarBotonPagina(boton, false));

Then('el contacto {string} muestra {string} y está marcado como favorito', async ({ contactos }, alias: string, detalle: string) => {
  await contactos.esperarDetalle(alias, detalle, true);
});

Then('el contacto {string} muestra {string} y no está marcado como favorito', async ({ contactos }, alias: string, detalle: string) => {
  await contactos.esperarDetalle(alias, detalle, false);
});

Then('el contacto {string} está marcado como favorito', async ({ contactos }, alias: string) => contactos.esperarFavorito(alias, true));
Then('el contacto {string} sigue sin ser favorito', async ({ contactos }, alias: string) => contactos.esperarFavorito(alias, false));

Then('el comprobante muestra destino {string}, total {string} y saldo {string}', async ({ transferir }, destino: string, total: string, saldo: string) => {
  await transferir.esperarComprobante({ destino, total, saldo });
});
