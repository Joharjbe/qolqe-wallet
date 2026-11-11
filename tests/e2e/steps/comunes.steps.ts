import { expect } from '@playwright/test';
import { Given, Then, USUARIOS, When } from '../fixtures';

// Pasos que comparten el módulo común y G4. Ningún paso usa localizadores: eso vive en los Page Objects.

// ---------- Preparación ----------

Given('que {string} ingresó a Qolqe', async ({ login }, nombre: string) => {
  await login.ingresar(USUARIOS[nombre].celular, USUARIOS[nombre].pin);
});

Given('que el reloj de Qolqe marca las {string}', async ({ datos }, hora: string) => datos.fijarHora(hora));
Given('que {string} tiene saldo {string}', async ({ datos }, nombre: string, saldo: string) => datos.fijarSaldo(nombre, saldo));

When('pasan {int} minutos', async ({ datos }, minutos: number) => datos.avanzarReloj(minutos));

// ---------- Navegación ----------

When('abre la pantalla de contactos', async ({ contactos }) => contactos.abrir());
When('abre la pantalla de solicitudes', async ({ solicitudes }) => solicitudes.abrir());
When('abre la pantalla de perfil', async ({ perfil }) => perfil.abrir());
When('abre la pantalla de transferencias', async ({ transferir }) => transferir.abrir());

When('ingresa como {string}', async ({ login }, nombre: string) => {
  await login.ingresar(USUARIOS[nombre].celular, USUARIOS[nombre].pin);
});

When('cierra sesión', async ({ nav }) => nav.cerrarSesion());

When('cierra sesión e ingresa como {string}', async ({ nav, login }, nombre: string) => {
  await nav.cerrarSesion();
  await login.ingresar(USUARIOS[nombre].celular, USUARIOS[nombre].pin);
});

// ---------- Componentes compartidos ----------

When('cancela la confirmación', async ({ confirmacion }) => confirmacion.cancelar());
When('cancela el diálogo', async ({ formulario }) => formulario.cancelar());

Then('ve el aviso {string}', async ({ aviso }, texto: string) => aviso.esperar(texto));
Then('ve el mensaje vacío {string}', async ({ listaVacia }, texto: string) => listaVacia.esperar(texto));
Then('la confirmación dice {string}', async ({ confirmacion }, texto: string) => confirmacion.esperarMensaje(texto));
Then('ve el error del diálogo {string}', async ({ formulario }, texto: string) => formulario.esperarError(texto));
Then('vuelve al ingreso con el aviso {string}', async ({ login }, texto: string) => login.esperarAviso(texto));

Then('su saldo en inicio es {string}', async ({ inicio }, saldo: string) => {
  await inicio.abrir();
  await inicio.esperarSaldo(saldo);
});

// Reglas que solo existen en la interfaz: se comprueba qué peticiones salieron del navegador.
Then('la pantalla envió {int} petición/peticiones {string}', async ({ peticiones }, cantidad: number, peticion: string) => {
  expect(peticiones.cantidad(peticion)).toBe(cantidad);
});
