# language: es
Característica: Pantalla de solicitudes de dinero (G4)

  @HU-G4-01 @HU-G4-06 @HU-G4-07 @CA1 @HU-G4-08 @CA3 @CP-W10
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

  @HU-G4-08 @CA1 @CA2 @CP-W20
  Escenario: CP-W20 Cancelar la confirmación de aceptar no transfiere
    Dado que "Ana" ingresó a Qolqe
    Y abre la pantalla de solicitudes
    Cuando pulsa aceptar en la solicitud "Almuerzo del viernes"
    Entonces la confirmación dice "Se transferirán S/ 45.00 a Bruno D. (912345678) por \"Almuerzo del viernes\"."
    Cuando cancela la confirmación
    Entonces la solicitud "Almuerzo del viernes" está "Pendiente"
    Y su saldo en inicio es "S/ 1,500.00"

  @HU-G4-08 @CA4 @HU-G4-10 @CA1 @CP-W21
  Escenario: CP-W21 Aceptar una solicitud que el solicitante ya canceló muestra el error y refresca la lista
    Dado que "Bruno" ingresó a Qolqe
    Y abre la pantalla de solicitudes
    Y la solicitud "Taxi al aeropuerto" está "Pendiente"
    Cuando "Ana" cancela por su lado la solicitud "Taxi al aeropuerto"
    Y acepta la solicitud "Taxi al aeropuerto"
    Entonces ve el aviso "La solicitud ya no está pendiente"
    Y la solicitud "Taxi al aeropuerto" está "Cancelada"
    Y su saldo en inicio es "S/ 800.00"

  @HU-G4-10 @CA1 @HU-G4-07 @CA2 @CP-W22
  Escenario: CP-W22 Una solicitud enviada vencida no ofrece cancelar
    Dado que "Carla" ingresó a Qolqe
    Y abre la pantalla de solicitudes
    Cuando va a la pestaña "enviadas"
    Y filtra por el estado "Vencidas"
    Entonces la solicitud "Entradas al cine" está "Vencida"
    Y la solicitud "Entradas al cine" muestra "Venció el"
    Y la solicitud "Entradas al cine" no ofrece cancelar

  @HU-G4-06 @CA1 @CP-W26
  Escenario: CP-W26 Sin elegir contacto la pantalla lo pide y no envía nada
    Dado que "Diego" ingresó a Qolqe
    Y abre la pantalla de solicitudes
    Cuando envía una solicitud de "10.00" por "Cuota del regalo" sin elegir contacto
    Entonces ve la confirmación "Elige un contacto"
    Y la pantalla envió 0 peticiones "POST /api/solicitudes"
    Cuando va a la pestaña "enviadas"
    Entonces ve el mensaje vacío "No tienes solicitudes enviadas"

  @HU-G4-07 @CA1 @CP-W27
  Escenario: CP-W27 Los contadores de pendientes se actualizan al rechazar una solicitud
    Dado que "Ana" ingresó a Qolqe
    Entonces el inicio indica "1" solicitud pendiente
    Cuando abre la pantalla de solicitudes
    Entonces la pestaña "recibidas" dice "Recibidas (1)"
    Y la pestaña "enviadas" dice "Enviadas (1)"
    Cuando rechaza la solicitud "Almuerzo del viernes" con el motivo "Ya lo pagué"
    Entonces la solicitud "Almuerzo del viernes" está "Rechazada"
    Y la pestaña "recibidas" dice "Recibidas"
    Y la pestaña "enviadas" dice "Enviadas (1)"
    Y el inicio no indica solicitudes pendientes

  @HU-N-04 @CA3 @CP-W28
  Escenario: CP-W28 Con la sesión vencida, la pantalla de solicitudes vuelve al ingreso
    Dado que "Ana" ingresó a Qolqe
    Y abre la pantalla de solicitudes
    Cuando pasan 30 minutos
    Y intenta ir a la pestaña "enviadas"
    Entonces vuelve al ingreso con el aviso "Tu sesión expiró o fue cerrada. Vuelve a ingresar."

  @HU-G4-01 @HU-G4-06 @CA1 @CP-W30
  Escenario: CP-W30 Un doble clic en Agregar o en Enviar solicitud crea un solo registro
    Dado que "Diego" ingresó a Qolqe
    Y abre la pantalla de contactos
    Cuando agrega con doble clic el contacto "912345678" con alias "Bruno Doble"
    Entonces ve el aviso "Contacto \"Bruno Doble\" agregado"
    Y el contacto "Bruno Doble" aparece en la lista
    Y la pantalla envió 1 petición "POST /api/contactos"
    Cuando abre la pantalla de solicitudes
    Y solicita con doble clic "12.00" a "Bruno Doble" por "Pago a medias"
    Entonces ve la confirmación "Solicitud enviada"
    Y ve 1 solicitud
    Y la pantalla envió 1 petición "POST /api/solicitudes"

  @HU-G4-09 @CA1 @CP-W31
  Escenario: CP-W31 Un motivo de rechazo de 61 caracteres muestra el error en el diálogo
    Dado que "Ana" ingresó a Qolqe
    Y abre la pantalla de solicitudes
    Cuando rechaza la solicitud "Almuerzo del viernes" con un motivo de 61 caracteres
    Entonces ve el error del diálogo "El motivo admite como máximo 60 caracteres"
    Cuando cancela el diálogo
    Entonces la solicitud "Almuerzo del viernes" está "Pendiente"
