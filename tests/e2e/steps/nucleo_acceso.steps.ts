import { expect } from '@playwright/test';
import type { DataTable } from 'playwright-bdd';
import { Given, Then, USUARIOS, When } from '../fixtures';
import type { DatosRegistro } from '../pages/RegistroPage';

// Módulo común: registro, ingreso, salida, consulta y edición del perfil (HU-N-01 a HU-N-05).

// ---------- Registro ----------

When('se registra con estos datos:', async ({ registro }, tabla: DataTable) => {
  await registro.registrar(tabla.hashes()[0] as unknown as DatosRegistro);
});

Then('ve el error de registro {string}', async ({ registro }, texto: string) => registro.esperarError(texto));
Then('ve el error de registro en español sobre los nombres', async ({ registro }) => registro.esperarErrorEnEspanol(/nombre/i));
Then('el formulario de registro conserva los datos ingresados', async ({ registro }) => registro.esperarFormularioConservado());

When('escribe {string} en el campo {string} del registro', async ({ registro }, texto: string, campo: string) => {
  await registro.escribir(campo, texto);
});

Then('el campo {string} del registro queda con {string}', async ({ registro }, campo: string, valor: string) => {
  await registro.esperarValor(campo, valor);
});

Then('no puede ingresar con el celular {string} y el PIN {string}', async ({ datos }, celular: string, pin: string) => {
  expect(await datos.codigoDeIngreso(celular, pin)).toBe(401);
});

// ---------- Ingreso y salida ----------

Given('que {string} acumula {int} intentos fallidos', async ({ datos }, nombre: string, veces: number) => {
  await datos.fallarIngreso(nombre, veces);
});

Given('que el navegador recuerda el dispositivo {string} llamado {string}', async ({ login }, id: string, nombre: string) => {
  await login.recordarDispositivo(id, nombre);
});

When('abre la pantalla de ingreso', async ({ login }) => login.abrir());
When('ingresa con el celular {string} y el PIN {string}', async ({ login }, celular: string, pin: string) => login.ingresar(celular, pin));
When('intenta ingresar con el celular {string} y el PIN {string}', async ({ login }, celular: string, pin: string) => login.enviar(celular, pin));

When('intenta ingresar como {string} con el PIN {string}', async ({ login }, nombre: string, pin: string) => {
  await login.enviar(USUARIOS[nombre].celular, pin);
});

When('sigue el enlace de desbloqueo', async ({ login }) => login.irADesbloqueo());
When('abre el inicio sin sesión', async ({ inicio }) => inicio.abrirPorDireccion());
When('regresa a la página anterior', async ({ nav }) => nav.volverAtras());

Then('ve el error de ingreso {string}', async ({ login }, texto: string) => login.esperarError(texto));
Then('el PIN queda vacío y listo para escribir', async ({ login }) => login.esperarPinVacioYEnfocado());
Then('ve la pantalla de desbloqueo', async ({ login }) => login.esperarDesbloqueo());
Then('ve el dispositivo {string}', async ({ login }, texto: string) => login.esperarDispositivo(texto));
Then('el navegador guarda la sesión', async ({ login }) => login.esperarSesionGuardada(true));
Then('el navegador ya no guarda la sesión', async ({ login }) => login.esperarSesionGuardada(false));
Then('vuelve a la pantalla de ingreso sin ver su saldo', async ({ login }) => login.esperarIngresoSinDatos());

Then('el ingreso envió el dispositivo {string}', async ({ peticiones }, id: string) => {
  expect(peticiones.ultimoCuerpo('POST /api/auth/login')?.dispositivo_id).toBe(id);
});

Then('{string} recibió {int} SMS de nuevo dispositivo', async ({ datos }, nombre: string, cantidad: number) => {
  expect(await datos.cantidadDeSms(nombre, 'nuevo dispositivo')).toBe(cantidad);
});

// ---------- Inicio ----------

Then('está en el inicio con el saludo {string}', async ({ inicio }, saludo: string) => {
  await inicio.esperarCargado();
  await inicio.esperarSaludo(saludo);
});

// A diferencia de "su saldo en inicio es", no navega: comprueba la pantalla a la que llegó.
Then('ve en inicio el saldo {string}', async ({ inicio }, saldo: string) => {
  await inicio.esperarCargado();
  await inicio.esperarSaldo(saldo);
});

Then('no tiene movimientos recientes', async ({ inicio }) => inicio.esperarSinMovimientos());
Then('el menú muestra el nombre {string}', async ({ nav }, nombres: string) => nav.esperarUsuario(nombres));
Then('la fecha de actualización del saldo tiene el formato dd\\/mm\\/aaaa hh:mm', async ({ inicio }) => inicio.esperarFormatoActualizado());

When('oculta su saldo', async ({ inicio }) => inicio.alternarSaldo());
When('vuelve a mostrar su saldo', async ({ inicio }) => inicio.alternarSaldo());
Then('el saldo queda oculto como {string}', async ({ inicio }, texto: string) => inicio.esperarSaldoOculto(true, texto));
Then('el saldo vuelve a verse como {string}', async ({ inicio }, texto: string) => inicio.esperarSaldoOculto(false, texto));

// ---------- Perfil ----------

When('intenta abrir la pantalla de perfil', async ({ perfil }) => perfil.pulsarEnElMenu());

When('guarda sus datos con nombres {string} y correo {string}', async ({ perfil }, nombres: string, correo: string) => {
  await perfil.guardar(nombres, correo);
});

Then('ve el mensaje de perfil {string}', async ({ perfil }, texto: string) => perfil.esperarMensaje(texto));

Then('el perfil muestra nombres {string}, celular {string}, DNI {string} y correo {string}',
  async ({ perfil }, nombres: string, celular: string, dni: string, correo: string) => {
    await perfil.esperarDatos({ nombres, celular, dni, correo });
  });

Then('el perfil muestra nombres {string} y correo {string}', async ({ perfil }, nombres: string, correo: string) => {
  await perfil.esperarDatos({ nombres, correo });
});

Then('la página no muestra el DNI completo {string}', async ({ perfil }, dni: string) => perfil.esperarSinTexto(dni));
Then('solo puede editar los nombres y el correo', async ({ perfil }) => perfil.esperarSoloNombresYCorreoEditables());
