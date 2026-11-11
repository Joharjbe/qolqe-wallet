import { expect } from '@playwright/test';
import { Given, Then, USUARIOS, When } from '../fixtures';

// Módulo común: cierre de cuenta, transferencias y simulación de la comisión (HU-N-06 a HU-N-09).

// ---------- Cierre de cuenta ----------

Given('que {string} también ingresó en otro navegador', async ({ otroNavegador }, nombre: string) => {
  await otroNavegador.login.ingresar(USUARIOS[nombre].celular, USUARIOS[nombre].pin);
});

When('cierra su cuenta con el PIN {string}', async ({ perfil }, pin: string) => perfil.cerrarCuenta(pin));
When('intenta cerrar su cuenta con el PIN {string}', async ({ perfil }, pin: string) => perfil.cerrarCuenta(pin));
When('en el otro navegador abre el inicio', async ({ otroNavegador }) => otroNavegador.nav.ir('inicio'));

Then('el otro navegador vuelve al ingreso con el aviso {string}', async ({ otroNavegador }, texto: string) => {
  await otroNavegador.login.esperarAviso(texto);
});

Then('el otro navegador ve en inicio el saldo {string}', async ({ otroNavegador }, saldo: string) => {
  await otroNavegador.inicio.esperarCargado();
  await otroNavegador.inicio.esperarSaldo(saldo);
});

Given('que {string} tiene {int} solicitud(es) recibida(s) pendiente(s)', async ({ datos }, nombre: string, cantidad: number) => {
  for (let i = 1; i <= cantidad; i++) await datos.crearSolicitud(nombre === 'Ana' ? 'Bruno' : 'Ana', nombre, '1.00', `Pendiente ${i}`);
});

Then('la cuenta de {string} sigue activa', async ({ datos }, nombre: string) => {
  expect(await datos.codigoDeIngreso(USUARIOS[nombre].celular, USUARIOS[nombre].pin)).toBe(200);
});

// ---------- Transferencias ----------

Given('que {string} le transfirió {string} a {string} con la descripción {string}',
  async ({ datos }, origen: string, monto: string, destino: string, descripcion: string) => {
    await datos.transferir(origen, destino, monto, descripcion);
  });

When('prepara una transferencia de {string} al celular {string}', async ({ transferir }, monto: string, celular: string) => {
  await transferir.continuarAlCelular(celular, monto);
});

When('prepara una transferencia de {string} al celular {string} con la descripción {string}',
  async ({ transferir }, monto: string, celular: string, descripcion: string) => {
    await transferir.continuarAlCelular(celular, monto, descripcion);
  });

When('prepara una transferencia de {string} al CCI {string}', async ({ transferir }, monto: string, cci: string) => {
  await transferir.continuarAlCci(cci, monto);
});

When('elige el contacto {string}', async ({ transferir }, opcion: string) => transferir.elegirContacto(opcion));
When('prepara una transferencia de {string} al contacto elegido', async ({ transferir }, monto: string) => transferir.continuar(monto));
When('confirma la transferencia', async ({ transferir }) => transferir.confirmar());
When('cancela la transferencia', async ({ transferir }) => transferir.cancelar());
When('inicia una nueva transferencia', async ({ transferir }) => transferir.nuevaTransferencia());

Then('el selector de contactos ofrece {string}', async ({ transferir }, opcion: string) => transferir.esperarOpcionContacto(opcion));
Then('el celular de destino queda bloqueado', async ({ transferir }) => transferir.esperarCelularBloqueado());

Then('la confirmación muestra destino {string}, monto {string}, comisión {string} y total {string}',
  async ({ transferir }, destino: string, monto: string, comision: string, total: string) => {
    await transferir.esperarConfirmacion(destino, monto, comision, total);
  });

Then('el comprobante muestra destino {string}, monto {string}, comisión {string}, total {string} y saldo {string}',
  async ({ transferir }, destino: string, monto: string, comision: string, total: string, saldo: string) => {
    await transferir.esperarComprobante({ destino, monto, comision, total, saldo });
  });

Then('el comprobante tiene código de operación y fecha', async ({ transferir }) => transferir.esperarCodigoYFecha());
Then('el formulario de transferencia está vacío', async ({ transferir }) => transferir.esperarFormularioVacio());
Then('ve el error de transferencia {string}', async ({ transferir }, texto: string) => transferir.esperarError(texto));
Then('no se abre la confirmación', async ({ transferir }) => transferir.esperarSinConfirmacion());
Then('no se muestra el comprobante', async ({ transferir }) => transferir.esperarSinComprobante());

Then('su último movimiento es {string} por {string}', async ({ inicio }, descripcion: string, importe: string) => {
  await inicio.esperarUltimoMovimiento(descripcion, importe);
});
