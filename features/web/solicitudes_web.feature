# language: es
Característica: Pantalla de solicitudes de dinero (G4)

  @HU-G4-01 @HU-G4-06 @HU-G4-07 @HU-G4-08 @CA1 @CA3 @CP-W10
  Escenario: CP-W10 Recorrido completo de una solicitud entre dos usuarios
    Dado que "Diego" ingresó a Qolqe
    Y abre la pantalla de contactos
    Y agrega el contacto "912345678" con alias "Bruno Demo"
    Y el contacto "Bruno Demo" aparece en la lista
    Y abre la pantalla de solicitudes
    Cuando solicita "25.00" a "Bruno Demo" por "Devolución demo G4"
    Entonces ve la confirmación "Solicitud enviada"
    Y la solicitud "Devolución demo G4" está "Pendiente"
    Cuando cierra sesión e ingresa como "Bruno"
    Y abre la pantalla de solicitudes
    Y acepta la solicitud "Devolución demo G4"
    Entonces la solicitud "Devolución demo G4" está "Aceptada"
    Y la solicitud "Devolución demo G4" muestra "Operación"
    Y su saldo en inicio es "S/ 775.00"
    Cuando cierra sesión e ingresa como "Diego"
    Y abre la pantalla de solicitudes
    Y va a la pestaña "enviadas"
    Entonces la solicitud "Devolución demo G4" está "Aceptada"
    Y su saldo en inicio es "S/ 2,525.00"

  @HU-G4-06 @CA1 @CP-W11
  Escenario: CP-W11 Solicitar desde la lista de contactos
    Dado que "Ana" ingresó a Qolqe
    Y abre la pantalla de contactos
    Cuando solicita "15.00" al contacto "Prima Carla" por "Taxi compartido"
    Entonces ve el aviso "Solicitud enviada"

  @HU-G4-06 @CA1 @CP-W12
  Escenario: CP-W12 Una solicitud inválida muestra el error y no se crea
    Dado que "Ana" ingresó a Qolqe
    Y abre la pantalla de solicitudes
    Cuando solicita "10.00" a "Prima Carla" por "ab"
    Entonces ve la confirmación "entre 3 y 60 caracteres"
    Y va a la pestaña "enviadas"
    Y la solicitud "ab" no aparece

  @HU-G4-06 @CA2 @CP-W13
  Escenario: CP-W13 La solicitud creada queda pendiente con su vencimiento
    Dado que "Ana" ingresó a Qolqe
    Y abre la pantalla de solicitudes
    Cuando solicita "10.00" a "Prima Carla" por "Entradas al cine"
    Entonces la solicitud "Entradas al cine" está "Pendiente"
    Y la solicitud "Entradas al cine" muestra "Vence el"

  @HU-G4-07 @CA1 @CP-W14
  Escenario: CP-W14 Enviadas y recibidas por separado, con filtro por estado
    Dado que "Ana" ingresó a Qolqe
    Cuando abre la pantalla de solicitudes
    Entonces ve 2 solicitudes
    Y la solicitud "Almuerzo del viernes" está "Pendiente"
    Cuando filtra por el estado "Vencidas"
    Entonces ve 1 solicitudes
    Cuando va a la pestaña "enviadas"
    Entonces ve el mensaje vacío "No tienes solicitudes enviadas"
    Cuando filtra por el estado "Todos"
    Entonces ve 1 solicitudes

  @HU-G4-07 @CA2 @HU-G4-08 @CA4 @CP-W15
  Escenario: CP-W15 Una solicitud vencida se muestra como Vencida y sin acciones
    Dado que "Ana" ingresó a Qolqe
    Cuando abre la pantalla de solicitudes
    Y filtra por el estado "Vencidas"
    Entonces la primera solicitud está "Vencida" y no ofrece aceptar ni rechazar

  @HU-G4-08 @CA1 @CA3 @CP-W16
  Escenario: CP-W16 Aceptar pide confirmación e informa la transferencia
    Dado que "Diego" le solicitó "25.00" a "Bruno" por "Pago de la cena"
    Y que "Bruno" ingresó a Qolqe
    Y abre la pantalla de solicitudes
    Cuando acepta la solicitud "Pago de la cena"
    Entonces ve el aviso "Transferencia realizada. Operación"
    Y la solicitud "Pago de la cena" está "Aceptada"
    Y su saldo en inicio es "S/ 775.00"

  @HU-G4-08 @CA2 @CP-W17
  Escenario: CP-W17 Sin saldo se muestra el error y la solicitud sigue pendiente
    Dado que "Ana" le solicitó "100.00" a "Carla" por "Regalo de Ana"
    Y que "Carla" ingresó a Qolqe
    Y abre la pantalla de solicitudes
    Cuando acepta la solicitud "Regalo de Ana"
    Entonces ve el aviso "Saldo insuficiente"
    Y la solicitud "Regalo de Ana" está "Pendiente"
    Y su saldo en inicio es "S/ 50.00"

  @HU-G4-09 @CA1 @CP-W18
  Escenario: CP-W18 Rechazar con motivo
    Dado que "Diego" le solicitó "25.00" a "Bruno" por "Pago de la cena"
    Y que "Bruno" ingresó a Qolqe
    Y abre la pantalla de solicitudes
    Cuando rechaza la solicitud "Pago de la cena" con el motivo "Ya te pagué"
    Entonces ve el aviso "Solicitud rechazada"
    Y la solicitud "Pago de la cena" está "Rechazada"
    Y la solicitud "Pago de la cena" muestra "Motivo: Ya te pagué"

  @HU-G4-10 @CA1 @CP-W19
  Escenario: CP-W19 Cancelar una solicitud enviada pide confirmación
    Dado que "Diego" le solicitó "25.00" a "Bruno" por "Pago de la cena"
    Y que "Diego" ingresó a Qolqe
    Y abre la pantalla de solicitudes
    Y va a la pestaña "enviadas"
    Cuando cancela la solicitud "Pago de la cena"
    Entonces ve el aviso "Solicitud cancelada"
    Y la solicitud "Pago de la cena" está "Cancelada"
