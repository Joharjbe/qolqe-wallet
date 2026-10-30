# language: es
Característica: API de solicitudes de dinero (G4)
  Reglas R-G4-04 y R-G4-05. Máquina de estados: PENDIENTE → ACEPTADA, RECHAZADA, CANCELADA o VENCIDA.

  @HU-G4-06 @CA2 @CP-A20
  Escenario: CP-A20 Crear una solicitud pendiente que vence a las 48 horas y avisa por SMS
    Dado que Diego inició sesión
    Y Diego tiene el contacto "912345678" con alias "Bruno"
    Cuando solicita 45.50 a "Bruno" por "Almuerzo del viernes"
    Entonces la respuesta tiene estado 201
    Y la solicitud está en estado "PENDIENTE"
    Y la solicitud vence 48 horas después de creada
    Y "912345678" recibió un SMS que contiene "te solicita S/ 45.50"

  @HU-G4-06 @CA1 @CP-A21
  Esquema del escenario: CP-A21 Valores límite del monto
    Dado que Diego inició sesión
    Y Diego tiene el contacto "912345678" con alias "Bruno"
    Cuando solicita <monto> a "Bruno" por "Motivo valido"
    Entonces la respuesta tiene estado <estado>

    Ejemplos:
      | monto  | estado |
      | 0      | 422    |
      | 0.01   | 201    |
      | 500    | 201    |
      | 500.01 | 422    |
      | 1.234  | 422    |
      | -1     | 422    |

  @HU-G4-06 @CA1 @CP-A22
  Esquema del escenario: CP-A22 Valores límite del motivo
    Dado que Diego inició sesión
    Y Diego tiene el contacto "912345678" con alias "Bruno"
    Cuando solicita 10.00 a "Bruno" con un motivo de <largo> caracteres
    Entonces la respuesta tiene estado <estado>

    Ejemplos:
      | largo | estado |
      | 2     | 422    |
      | 3     | 201    |
      | 60    | 201    |
      | 61    | 422    |

  @HU-G4-06 @CA1 @CP-A23
  Escenario: CP-A23 Máximo 10 solicitudes pendientes enviadas
    Dado que Diego inició sesión
    Y Diego tiene el contacto "912345678" con alias "Bruno"
    Y Diego envió 10 solicitudes a "Bruno"
    Cuando solicita 10.00 a "Bruno" por "Una de mas"
    Entonces la respuesta tiene estado 422
    Y el código de error es "LIMITE_SOLICITUDES"

  @HU-G4-06 @CA1 @CP-A24
  Escenario: CP-A24 No se solicita a un contacto con cuenta cerrada
    Dado que Diego inició sesión
    Cuando solicita 10.00 a "Fabián" por "Motivo valido"
    Entonces la respuesta tiene estado 422
    Y el código de error es "DESTINO_INACTIVO"

  @HU-G4-07 @CA1 @CP-A25
  Escenario: CP-A25 Enviadas y recibidas por separado, con filtro por estado
    Dado que Ana inició sesión
    Cuando consulta sus solicitudes con estado "PENDIENTE"
    Entonces la respuesta tiene estado 200
    Y tiene 1 enviadas y 1 recibidas

  @HU-G4-07 @CA1 @CP-A26
  Escenario: CP-A26 Un filtro de estado desconocido se rechaza
    Dado que Ana inició sesión
    Cuando consulta sus solicitudes con estado "X"
    Entonces la respuesta tiene estado 422
    Y el código de error es "FILTRO_INVALIDO"

  @HU-G4-07 @CA2 @CP-A27
  Esquema del escenario: CP-A27 Vencimiento a las 48 horas exactas
    Dado que Diego inició sesión
    Y Diego tiene el contacto "912345678" con alias "Bruno"
    Y Diego envió 1 solicitudes a "Bruno"
    Cuando el reloj avanza <minutos> minutos y Diego vuelve a ingresar
    Entonces su solicitud enviada figura como "<estado>"

    Ejemplos:
      | minutos | estado    |
      | 2879    | PENDIENTE |
      | 2880    | VENCIDA   |

  @HU-G4-08 @CA1 @CA3 @CP-A28
  Escenario: CP-A28 Aceptar transfiere el dinero y deja el código de operación
    Dado que Diego le solicitó 25.00 a Bruno
    Cuando Bruno acepta la solicitud
    Entonces la respuesta tiene estado 200
    Y la solicitud está en estado "ACEPTADA"
    Y la solicitud tiene código de operación
    Y el saldo de Bruno es "775.00"
    Y el saldo de Diego es "2525.00"
    Y "998877665" recibió un SMS que contiene "aceptó tu solicitud"

  @HU-G4-08 @CA2 @CP-A29
  Escenario: CP-A29 Sin saldo la solicitud sigue pendiente
    Dado que Ana le solicitó 100.00 a Carla
    Cuando Carla acepta la solicitud
    Entonces la respuesta tiene estado 422
    Y el código de error es "SALDO_INSUFICIENTE"
    Y Carla ve la solicitud en estado "PENDIENTE"
    Y el saldo de Carla es "50.00"

  @HU-G4-08 @CA2 @CP-A30
  Escenario: CP-A30 Sobre el límite diario la solicitud sigue pendiente
    Dado que Ana le solicitó 500.00 a Diego
    Y Diego ya transfirió 600.00 hoy
    Cuando Diego acepta la solicitud
    Entonces la respuesta tiene estado 422
    Y el código de error es "LIMITE_DIARIO_EXCEDIDO"
    Y Diego ve la solicitud en estado "PENDIENTE"

  @HU-G4-08 @CA4 @CP-A31
  Esquema del escenario: CP-A31 Solo el destinatario puede aceptar
    Dado que Diego le solicitó 25.00 a Bruno
    Cuando <otro> acepta la solicitud
    Entonces la respuesta tiene estado 404
    Y el código de error es "SOLICITUD_NO_ENCONTRADA"

    Ejemplos:
      | otro  |
      | Diego |
      | Carla |

  @HU-G4-08 @CA4 @CP-A32 @DEF-03
  Escenario: CP-A32 Una solicitud vencida no se puede aceptar
    Dado la solicitud vencida de Carla a Ana
    Cuando Ana acepta la solicitud
    Entonces la respuesta tiene estado 409
    Y el código de error es "ESTADO_INVALIDO"
    Y el saldo de Ana es "1500.00"

  @HU-G4-08 @CA4 @CP-A33
  Escenario: CP-A33 Una solicitud ya aceptada no se acepta dos veces
    Dado que Diego le solicitó 25.00 a Bruno
    Y Bruno aceptó la solicitud
    Cuando Bruno acepta la solicitud
    Entonces la respuesta tiene estado 409
    Y el código de error es "ESTADO_INVALIDO"
    Y el saldo de Bruno es "775.00"

  @HU-G4-09 @CA1 @CP-A34
  Esquema del escenario: CP-A34 Rechazar con motivo opcional de hasta 60 caracteres
    Dado que Diego le solicitó 25.00 a Bruno
    Cuando Bruno rechaza la solicitud con un motivo de <largo> caracteres
    Entonces la respuesta tiene estado <estado>

    Ejemplos:
      | largo | estado |
      | 0     | 200    |
      | 60    | 200    |
      | 61    | 422    |

  @HU-G4-09 @CA1 @CP-A35
  Escenario: CP-A35 Rechazar cambia el estado y avisa al solicitante sin mover dinero
    Dado que Diego le solicitó 25.00 a Bruno
    Cuando Bruno rechaza la solicitud con un motivo de 10 caracteres
    Entonces la solicitud está en estado "RECHAZADA"
    Y "998877665" recibió un SMS que contiene "rechazó tu solicitud"
    Y el saldo de Bruno es "800.00"

  @HU-G4-09 @CA1 @CP-A36
  Escenario: CP-A36 Una solicitud vencida no se puede rechazar
    Dado la solicitud vencida de Carla a Ana
    Cuando Ana rechaza la solicitud con un motivo de 10 caracteres
    Entonces la respuesta tiene estado 409
    Y el código de error es "ESTADO_INVALIDO"

  @HU-G4-10 @CA1 @CP-A37
  Escenario: CP-A37 El solicitante cancela una solicitud pendiente
    Dado que Diego le solicitó 25.00 a Bruno
    Cuando Diego cancela la solicitud
    Entonces la respuesta tiene estado 200
    Y la solicitud está en estado "CANCELADA"

  @HU-G4-10 @CA1 @CP-A38
  Esquema del escenario: CP-A38 Solo el solicitante puede cancelar
    Dado que Diego le solicitó 25.00 a Bruno
    Cuando <otro> cancela la solicitud
    Entonces la respuesta tiene estado 404

    Ejemplos:
      | otro  |
      | Bruno |
      | Carla |

  @HU-G4-10 @CA1 @CP-A39
  Escenario: CP-A39 Una solicitud ya aceptada no se puede cancelar
    Dado que Diego le solicitó 25.00 a Bruno
    Y Bruno aceptó la solicitud
    Cuando Diego cancela la solicitud
    Entonces la respuesta tiene estado 409
    Y el código de error es "ESTADO_INVALIDO"

  @HU-G4-07 @CP-T03
  Escenario: CP-T03 Sin token no se accede a las solicitudes
    Cuando se consultan las solicitudes sin token
    Entonces la respuesta tiene estado 401
    Y el código de error es "NO_AUTENTICADO"
