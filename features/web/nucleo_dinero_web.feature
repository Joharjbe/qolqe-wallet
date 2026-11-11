# language: es
Característica: Cierre de cuenta y transferencias en la web (módulo común)
  Los recorridos críticos de dinero, lo que solo muestra la pantalla (confirmación,
  comprobante, movimientos de inicio) y cómo comunica los errores de la API.
  Las reglas RN-05 a RN-10 se prueban en la API.

  @HU-N-06 @CA1 @CP-NW16
  Escenario: CP-NW16 Con un PIN incorrecto el diálogo muestra el error y la cuenta sigue activa
    Dado que "Carla" tiene saldo "0.00"
    Y que "Carla" ingresó a Qolqe
    Y abre la pantalla de perfil
    Cuando intenta cerrar su cuenta con el PIN "0000"
    Entonces ve el error del diálogo "El PIN no es correcto"
    Cuando cancela el diálogo
    Entonces el perfil muestra nombres "Carla Ramos Huamán" y correo "carla.ramos@correo.pe"
    Y la cuenta de "Carla" sigue activa

  @HU-N-06 @CA4 @CP-NW17
  Escenario: CP-NW17 Cerrar la cuenta desde Mi perfil impide volver a ingresar
    Dado que "Carla" tiene saldo "0.00"
    Y que "Carla" ingresó a Qolqe
    Y abre la pantalla de perfil
    Cuando cierra su cuenta con el PIN "5917"
    Entonces vuelve al ingreso con el aviso "Tu cuenta fue cerrada. Gracias por usar Qolqe."
    Cuando intenta ingresar como "Carla" con el PIN "5917"
    Entonces ve el error de ingreso "La cuenta fue cerrada"

  @HU-N-06 @CA4 @CP-NW18
  Escenario: CP-NW18 Al cerrar la cuenta, la sesión abierta en otro navegador se cierra
    Dado que "Carla" tiene saldo "0.00"
    Y que "Carla" también ingresó en otro navegador
    Y que "Carla" ingresó a Qolqe
    Y abre la pantalla de perfil
    Cuando cierra su cuenta con el PIN "5917"
    Entonces vuelve al ingreso con el aviso "Tu cuenta fue cerrada. Gracias por usar Qolqe."
    Cuando en el otro navegador abre el inicio
    Entonces el otro navegador vuelve al ingreso con el aviso "Tu sesión expiró o fue cerrada. Vuelve a ingresar."

  @HU-N-07 @CA1 @CA4 @CP-NW19
  Escenario: CP-NW19 Transferir por celular, confirmar y ver el comprobante
    Dado que "Ana" ingresó a Qolqe
    Y abre la pantalla de transferencias
    Cuando prepara una transferencia de "100" al celular "912345678" con la descripción "Almuerzo"
    Entonces la confirmación muestra destino "912345678", monto "S/ 100.00", comisión "S/ 0.00" y total "S/ 100.00"
    Cuando confirma la transferencia
    Entonces ve el aviso "Transferencia realizada con éxito"
    Y el comprobante muestra destino "Bruno D. (912345678)", monto "S/ 100.00", comisión "S/ 0.00", total "S/ 100.00" y saldo "S/ 1,400.00"
    Y el comprobante tiene código de operación y fecha
    Cuando inicia una nueva transferencia
    Entonces el formulario de transferencia está vacío

  @HU-N-07 @CA2 @CP-NW20
  Escenario: CP-NW20 La pantalla comunica los errores de monto y de saldo
    Dado que "Carla" ingresó a Qolqe
    Y abre la pantalla de transferencias
    Cuando prepara una transferencia de "600" al celular "912345678"
    Entonces ve el error de transferencia "El monto supera el límite por operación de S/ 500.00"
    Y no se abre la confirmación
    Cuando prepara una transferencia de "60" al celular "912345678"
    Y confirma la transferencia
    Entonces ve el error de transferencia "Saldo insuficiente para realizar la operación"
    Y no se muestra el comprobante
    Y su saldo en inicio es "S/ 50.00"

  @HU-N-07 @CA3 @CP-NW21
  Escenario: CP-NW21 Emisor y destinatario ven el saldo y el movimiento en inicio
    Dado que "Ana" le transfirió "100.00" a "Bruno" con la descripción "Almuerzo"
    Y que "Ana" ingresó a Qolqe
    Entonces ve en inicio el saldo "S/ 1,400.00"
    Y su último movimiento es "Almuerzo" por "-S/ 100.00"
    Cuando cierra sesión e ingresa como "Bruno"
    Entonces ve en inicio el saldo "S/ 900.00"
    Y su último movimiento es "Almuerzo" por "S/ 100.00"

  @HU-N-08 @CA1 @CP-NW22
  Escenario: CP-NW22 Un CCI de 19 dígitos se rechaza y no se debita nada
    Dado que "Ana" ingresó a Qolqe
    Y abre la pantalla de transferencias
    Cuando prepara una transferencia de "100" al CCI "0021930012345678901"
    Y confirma la transferencia
    Entonces ve el error de transferencia "El CCI debe tener 20 dígitos"
    Y no se muestra el comprobante
    Y su saldo en inicio es "S/ 1,500.00"

  @HU-N-08 @CA2 @CA3 @CP-NW23
  Escenario: CP-NW23 Transferir a otro banco cobra la comisión y enmascara el CCI
    Dado que "Ana" ingresó a Qolqe
    Y abre la pantalla de transferencias
    Cuando prepara una transferencia de "100" al CCI "00219300123456789012"
    Entonces la confirmación muestra destino "CCI 00219300123456789012", monto "S/ 100.00", comisión "S/ 1.50" y total "S/ 101.50"
    Cuando confirma la transferencia
    Entonces el comprobante muestra destino "CCI ****************9012", monto "S/ 100.00", comisión "S/ 1.50", total "S/ 101.50" y saldo "S/ 1,398.50"
    Y su saldo en inicio es "S/ 1,398.50"
    Y su último movimiento es "Transferencia interbancaria a CCI ****************9012" por "-S/ 101.50"

  @HU-N-09 @CA1 @CP-NW24
  Escenario: CP-NW24 La confirmación muestra la simulación y cancelar no transfiere
    Dado que "Ana" ingresó a Qolqe
    Y abre la pantalla de transferencias
    Cuando prepara una transferencia de "100" al CCI "00219300123456789012"
    Entonces la confirmación muestra destino "CCI 00219300123456789012", monto "S/ 100.00", comisión "S/ 1.50" y total "S/ 101.50"
    Cuando cancela la transferencia
    Entonces no se abre la confirmación
    Y no se muestra el comprobante
    Y la pantalla envió 0 peticiones "POST /api/transferencias"
    Y su saldo en inicio es "S/ 1,500.00"
