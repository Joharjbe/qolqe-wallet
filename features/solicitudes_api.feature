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

  # Los límites inválidos del monto (0, -1, 500.01, 1.234 y otros) están en CP-A61, y los del motivo (2 y 61) en
  # CP-A90, los dos con el código de error y la comprobación de que no se creó nada.
  @HU-G4-06 @CA1 @CP-A21
  Esquema del escenario: CP-A21 Valores límite válidos del monto
    Dado que Diego inició sesión
    Y Diego tiene el contacto "912345678" con alias "Bruno"
    Cuando solicita <monto> a "Bruno" por "Motivo valido"
    Entonces la respuesta tiene estado 201
    Y la solicitud está en estado "PENDIENTE"

    Ejemplos:
      | monto |
      | 0.01  |
      | 500   |

  @HU-G4-06 @CA1 @CP-A22
  Esquema del escenario: CP-A22 Valores límite válidos del motivo
    Dado que Diego inició sesión
    Y Diego tiene el contacto "912345678" con alias "Bruno"
    Cuando solicita 10.00 a "Bruno" con un motivo de <largo> caracteres
    Entonces la respuesta tiene estado 201
    Y la solicitud está en estado "PENDIENTE"

    Ejemplos:
      | largo |
      | 3     |
      | 60    |

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
    Y el saldo de Bruno es "770.00"
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
    Dado que el reloj de Qolqe marca hoy a las "12:00:00"
    Y que Ana le solicitó 500.00 a Diego
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

  # El motivo de 61 caracteres está en CP-A97 con el código de error.
  @HU-G4-09 @CA1 @CP-A34
  Esquema del escenario: CP-A34 Rechazar con motivo opcional de hasta 60 caracteres
    Dado que Diego le solicitó 25.00 a Bruno
    Cuando Bruno rechaza la solicitud con un motivo de <largo> caracteres
    Entonces la respuesta tiene estado 200
    Y la solicitud está en estado "RECHAZADA"

    Ejemplos:
      | largo |
      | 0     |
      | 60    |

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

  @HU-G4-10 @CA1 @CP-A39
  Escenario: CP-A39 Una solicitud ya aceptada no se puede cancelar
    Dado que Diego le solicitó 25.00 a Bruno
    Y Bruno aceptó la solicitud
    Cuando Diego cancela la solicitud
    Entonces la respuesta tiene estado 409
    Y el código de error es "ESTADO_INVALIDO"

  @HU-G4-06 @CA1 @CP-A61
  Esquema del escenario: CP-A61 Un monto o motivo inválido informa SOLICITUD_INVALIDA y no crea la solicitud
    Dado que Diego inició sesión
    Y Diego tiene el contacto "912345678" con alias "Bruno"
    Cuando Diego envía a su contacto "Bruno" una solicitud con monto <monto> y motivo <motivo>
    Entonces la respuesta tiene estado 422
    Y el código de error es "SOLICITUD_INVALIDA"
    Y Diego no tiene solicitudes enviadas
    Y "912345678" no recibió un SMS que contenga "te solicita"

    Ejemplos:
      | monto    | motivo          |
      | 0        | "Motivo valido" |
      | "0.00"   | "Motivo valido" |
      | -1       | "Motivo valido" |
      | "500.01" | "Motivo valido" |
      | "1.234"  | "Motivo valido" |
      | "10.000" | "Motivo valido" |
      | "10.00"  | "  ab  "        |
      | "10.00"  | "      "        |

  @HU-G4-06 @CA1 @CP-A89
  Esquema del escenario: CP-A89 El monto se acepta como número o texto y el motivo se guarda sin espacios en los extremos
    Dado que Diego inició sesión
    Y Diego tiene el contacto "912345678" con alias "Bruno"
    Cuando Diego envía a su contacto "Bruno" una solicitud con monto <monto> y motivo <motivo>
    Entonces la respuesta tiene estado 201
    Y la solicitud está en estado "PENDIENTE"
    Y la solicitud creada tiene monto "<guardado>" y motivo "<motivo_guardado>"

    Ejemplos:
      | monto   | motivo                                                             | guardado | motivo_guardado                                              |
      | 45.5    | "Numero decimal"                                                   | 45.50    | Numero decimal                                               |
      | 10      | "Monto entero"                                                     | 10.00    | Monto entero                                                 |
      | "1e2"   | "Exponente"                                                        | 100.00   | Exponente                                                    |
      | "0.01"  | "Minimo"                                                           | 0.01     | Minimo                                                       |
      | "10.00" | "  Cena  "                                                         | 10.00    | Cena                                                         |
      | "10.00" | "  mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm  " | 10.00    | mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm |

  @HU-G4-06 @CA1 @CP-A90
  Esquema del escenario: CP-A90 Un motivo fuera de rango informa SOLICITUD_INVALIDA
    Dado que Diego inició sesión
    Y Diego tiene el contacto "912345678" con alias "Bruno"
    Cuando solicita 10.00 a "Bruno" con un motivo de <largo> caracteres
    Entonces la respuesta tiene estado 422
    Y el código de error es "SOLICITUD_INVALIDA"
    Y Diego no tiene solicitudes enviadas

    Ejemplos:
      | largo |
      | 2     |
      | 61    |

  @HU-G4-06 @CA1 @CP-A62
  Esquema del escenario: CP-A62 Una solicitud que deja de estar pendiente libera el cupo de 10
    Dado que Diego inició sesión
    Y Diego tiene el contacto "912345678" con alias "Bruno"
    Y Diego envió 10 solicitudes a "Bruno"
    Y <liberacion>
    Cuando Diego solicita 10.00 a su contacto "Bruno" por "Una mas"
    Entonces la respuesta tiene estado 201

    Ejemplos:
      | liberacion                                          |
      | pasaron 48 horas desde la última solicitud de Diego |
      | Diego canceló la solicitud                          |
      | Bruno rechazó la solicitud                          |
      | Bruno aceptó la solicitud                           |

  @HU-G4-06 @CA1 @CP-A91
  Escenario: CP-A91 Las solicitudes recibidas no cuentan para el límite de 10 enviadas
    Dado que Diego inició sesión
    Y Diego tiene el contacto "912345678" con alias "Bruno"
    Y Diego envió 9 solicitudes a "Bruno"
    Y que Bruno le solicitó 5.00 a Diego
    Cuando Diego solicita 10.00 a su contacto "Bruno" por "La decima"
    Entonces la respuesta tiene estado 201

  @HU-G4-06 @CA1 @CP-A92
  Escenario: CP-A92 El límite de 10 suma las pendientes enviadas a distintos contactos
    Dado que Ana inició sesión
    Y Ana envió 9 solicitudes a su contacto "Prima Carla"
    Cuando Ana solicita 10.00 a su contacto "Bruno" por "Una de mas"
    Entonces la respuesta tiene estado 422
    Y el código de error es "LIMITE_SOLICITUDES"

  @HU-G4-06 @CA2 @CP-A63
  Escenario: CP-A63 La solicitud creada informa a los participantes y el SMS trae monto, motivo y vencimiento
    Dado que Diego inició sesión
    Y Diego tiene el contacto "912345678" con alias "Bruno"
    Cuando Diego solicita 45.50 a su contacto "Bruno" por "Almuerzo del viernes"
    Entonces la respuesta tiene estado 201
    Y la solicitud creada tiene solicitante "Diego S." (998877665), destinatario "Bruno D." (912345678) y aún no tiene resolución
    Y el SMS a "912345678" indica el monto, el motivo y la fecha de vencimiento de la solicitud

  @HU-G4-07 @CA1 @CP-A64
  Esquema del escenario: CP-A64 Cada filtro de estado devuelve solo sus solicitudes, enviadas y recibidas
    Dado que Ana inició sesión
    Y Ana tiene una solicitud enviada a su contacto "Bruno" en cada estado final
    Cuando <usuario> filtra sus solicitudes por el estado "<estado>"
    Entonces la respuesta tiene estado 200
    Y las enviadas son "<enviadas>" y las recibidas son "<recibidas>"

    Ejemplos:
      | usuario | estado    | enviadas                         | recibidas                        |
      | Ana     | PENDIENTE | Taxi al aeropuerto (PENDIENTE)   | Almuerzo del viernes (PENDIENTE) |
      | Ana     | ACEPTADA  | Para aceptar (ACEPTADA)          |                                  |
      | Ana     | RECHAZADA | Para rechazar (RECHAZADA)        |                                  |
      | Ana     | CANCELADA | Para cancelar (CANCELADA)        |                                  |
      | Ana     | VENCIDA   |                                  | Entradas al cine (VENCIDA)       |
      | Bruno   | PENDIENTE | Almuerzo del viernes (PENDIENTE) | Taxi al aeropuerto (PENDIENTE)   |
      | Bruno   | ACEPTADA  |                                  | Para aceptar (ACEPTADA)          |
      | Bruno   | RECHAZADA |                                  | Para rechazar (RECHAZADA)        |
      | Bruno   | CANCELADA |                                  | Para cancelar (CANCELADA)        |
      | Bruno   | VENCIDA   |                                  |                                  |

  @HU-G4-07 @CA1 @CP-A93
  Escenario: CP-A93 Sin filtro aparecen todas, de la más reciente a la más antigua
    Dado que Ana inició sesión
    Y Ana tiene una solicitud enviada a su contacto "Bruno" en cada estado final
    Cuando Ana consulta todas sus solicitudes
    Entonces la respuesta tiene estado 200
    Y las enviadas son "Para cancelar (CANCELADA), Para rechazar (RECHAZADA), Para aceptar (ACEPTADA), Taxi al aeropuerto (PENDIENTE)" y las recibidas son "Almuerzo del viernes (PENDIENTE), Entradas al cine (VENCIDA)"

  @HU-G4-07 @CA2 @CP-A65
  Escenario: CP-A65 Una solicitud resuelta no pasa a VENCIDA con el tiempo
    Dado que Ana inició sesión
    Y Ana tiene una solicitud enviada a su contacto "Bruno" en cada estado final
    Y pasaron 49 horas en el reloj de Qolqe
    Cuando Ana consulta todas sus solicitudes
    Entonces la respuesta tiene estado 200
    Y las enviadas son "Para cancelar (CANCELADA), Para rechazar (RECHAZADA), Para aceptar (ACEPTADA), Taxi al aeropuerto (VENCIDA)" y las recibidas son "Almuerzo del viernes (VENCIDA), Entradas al cine (VENCIDA)"

  @HU-G4-07 @CA1 @CP-A66
  Escenario: CP-A66 Cada usuario ve solo sus solicitudes y la misma solicitud se ve igual desde ambos lados
    Dado que Ana le solicitó 15.00 a Bruno
    Cuando Carla consulta todas sus solicitudes
    Entonces la respuesta tiene estado 200
    Y las enviadas son "Entradas al cine (VENCIDA)" y las recibidas son ""
    Y la solicitud aparece igual en las enviadas de Ana y en las recibidas de Bruno

  @HU-G4-07 @CA1 @CP-A67
  Esquema del escenario: CP-A67 El filtro distingue mayúsculas y no admite un valor vacío
    Dado que Ana inició sesión
    Cuando Ana filtra sus solicitudes por el estado <estado>
    Entonces la respuesta tiene estado 422
    Y el código de error es "FILTRO_INVALIDO"

    Ejemplos:
      | estado       |
      | "pendiente"  |
      | "Pendiente"  |
      | " PENDIENTE" |
      | ""           |

  @HU-G4-08 @CA1 @CA3 @CP-A68
  Escenario: CP-A68 Aceptar deja el mismo código en la solicitud, en ambos movimientos y en el SMS
    Dado que Diego le solicitó 25.00 a Bruno
    Cuando Bruno acepta la solicitud
    Entonces la respuesta tiene estado 200
    Y Bruno tiene el movimiento reciente "TRANSFERENCIA_ENVIADA" por "-25.00" con el código de la operación y la descripción "Solicitud: Motivo de prueba"
    Y Diego tiene el movimiento reciente "TRANSFERENCIA_RECIBIDA" por "25.00" con el código de la operación y la descripción "Solicitud: Motivo de prueba"
    Y el SMS de aceptación a "998877665" incluye el código de la operación
    Y la solicitud resuelta tiene fecha de resolución

  @HU-G4-08 @CA1 @CP-A69
  Escenario: CP-A69 Se puede aceptar con un saldo exactamente igual al monto
    Dado que Ana le solicitó 50.00 a Carla
    Cuando Carla acepta la solicitud
    Entonces la respuesta tiene estado 200
    Y el saldo de Carla es "0.00"
    Y el saldo de Ana es "1550.00"

  @HU-G4-08 @CA1 @CP-A94
  Escenario: CP-A94 Se puede aceptar si se alcanza exactamente el límite diario
    Dado que el reloj de Qolqe marca hoy a las "12:00:00"
    Y que Ana le solicitó 400.00 a Diego
    Y Diego ya transfirió 600.00 hoy
    Cuando Diego acepta la solicitud
    Entonces la respuesta tiene estado 200
    Y Diego usó hoy "1000.00" de su límite diario

  @HU-G4-08 @CA1 @CP-A70
  Escenario: CP-A70 Lo aceptado cuenta para el límite diario de quien paga
    Dado que Diego le solicitó 25.00 a Bruno
    Cuando Bruno acepta la solicitud
    Entonces la respuesta tiene estado 200
    Y Bruno usó hoy "25.00" de su límite diario

  @HU-G4-08 @CA2 @CP-A95
  Escenario: CP-A95 Sin saldo no hay SMS de aceptación ni movimientos
    Dado que Ana le solicitó 100.00 a Carla
    Cuando Carla acepta la solicitud
    Entonces la respuesta tiene estado 422
    Y el código de error es "SALDO_INSUFICIENTE"
    Y "987654321" no recibió un SMS que contenga "aceptó tu solicitud"
    Y ningún movimiento reciente de Carla ni de Ana dice "Solicitud: Motivo de prueba"

  @HU-G4-08 @CA2 @CP-A96
  Escenario: CP-A96 Sobre el límite diario no hay SMS de aceptación ni movimientos
    Dado que el reloj de Qolqe marca hoy a las "12:00:00"
    Y que Ana le solicitó 500.00 a Diego
    Y Diego ya transfirió 600.00 hoy
    Cuando Diego acepta la solicitud
    Entonces la respuesta tiene estado 422
    Y el código de error es "LIMITE_DIARIO_EXCEDIDO"
    Y "987654321" no recibió un SMS que contenga "aceptó tu solicitud"
    Y ningún movimiento reciente de Diego ni de Ana dice "Solicitud: Motivo de prueba"

  @HU-G4-08 @CA4 @CP-A71
  Esquema del escenario: CP-A71 Una solicitud rechazada o cancelada no se puede aceptar
    Dado que Diego le solicitó 25.00 a Bruno
    Y <resolucion> la solicitud
    Cuando Bruno acepta la solicitud
    Entonces la respuesta tiene estado 409
    Y el código de error es "ESTADO_INVALIDO"
    Y el saldo de Bruno es "800.00"

    Ejemplos:
      | resolucion    |
      | Bruno rechazó |
      | Diego canceló |

  @HU-G4-09 @CA1 @CP-A72
  Esquema del escenario: CP-A72 Solo el destinatario puede rechazar
    Dado que Diego le solicitó 25.00 a Bruno
    Cuando <otro> rechaza la solicitud con un motivo de 0 caracteres
    Entonces la respuesta tiene estado 404
    Y el código de error es "SOLICITUD_NO_ENCONTRADA"
    Y Bruno ve la solicitud en estado "PENDIENTE"

    Ejemplos:
      | otro  |
      | Diego |
      | Carla |

  @HU-G4-09 @CA1 @CP-A73
  Esquema del escenario: CP-A73 Una solicitud aceptada, rechazada o cancelada no se puede rechazar
    Dado que Diego le solicitó 25.00 a Bruno
    Y <resolucion> la solicitud
    Cuando Bruno rechaza la solicitud con un motivo de 10 caracteres
    Entonces la respuesta tiene estado 409
    Y el código de error es "ESTADO_INVALIDO"
    Y Bruno ve la solicitud en estado "<estado>"

    Ejemplos:
      | resolucion    | estado    |
      | Bruno aceptó  | ACEPTADA  |
      | Bruno rechazó | RECHAZADA |
      | Diego canceló | CANCELADA |

  @HU-G4-09 @CA1 @CP-A74
  Esquema del escenario: CP-A74 El motivo del rechazo es opcional, se recorta y llega en el SMS
    Dado que Diego le solicitó 25.00 a Bruno
    Cuando Bruno rechaza la solicitud con el cuerpo <cuerpo>
    Entonces la respuesta tiene estado 200
    Y la solicitud está en estado "RECHAZADA"
    Y la solicitud queda con motivo_rechazo <motivo>
    Y "998877665" recibió un SMS que contiene "<sms>"

    Ejemplos:
      | cuerpo                                                                         | motivo                                                         | sms                                                                                             |
      | (sin cuerpo)                                                                   | null                                                           | rechazó tu solicitud de S/ 25.00.                                                               |
      | {}                                                                             | null                                                           | rechazó tu solicitud de S/ 25.00.                                                               |
      | {"motivo": null}                                                               | null                                                           | rechazó tu solicitud de S/ 25.00.                                                               |
      | {"motivo": "    "}                                                             | null                                                           | rechazó tu solicitud de S/ 25.00.                                                               |
      | {"motivo": "Ya te pagué"}                                                      | "Ya te pagué"                                                  | rechazó tu solicitud de S/ 25.00: Ya te pagué.                                                  |
      | {"motivo": "  Ya te pagué  "}                                                  | "Ya te pagué"                                                  | rechazó tu solicitud de S/ 25.00: Ya te pagué.                                                  |
      | {"motivo": "  mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm  "} | "mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm" | rechazó tu solicitud de S/ 25.00: mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm. |

  @HU-G4-09 @CA1 @CP-A97
  Escenario: CP-A97 Un motivo de rechazo de 61 caracteres informa SOLICITUD_INVALIDA y no rechaza
    Dado que Diego le solicitó 25.00 a Bruno
    Cuando Bruno rechaza la solicitud con un motivo de 61 caracteres
    Entonces la respuesta tiene estado 422
    Y el código de error es "SOLICITUD_INVALIDA"
    Y Bruno ve la solicitud en estado "PENDIENTE"
    Y "998877665" no recibió un SMS que contenga "rechazó"

  @HU-G4-10 @CA1 @CP-A75
  Esquema del escenario: CP-A75 Una solicitud rechazada o ya cancelada no se puede cancelar
    Dado que Diego le solicitó 25.00 a Bruno
    Y <resolucion> la solicitud
    Cuando Diego cancela la solicitud
    Entonces la respuesta tiene estado 409
    Y el código de error es "ESTADO_INVALIDO"
    Y Bruno ve la solicitud en estado "<estado>"

    Ejemplos:
      | resolucion    | estado    |
      | Bruno rechazó | RECHAZADA |
      | Diego canceló | CANCELADA |

  @HU-G4-10 @CA1 @CP-A98
  Escenario: CP-A98 Una solicitud vencida no se puede cancelar
    Dado la solicitud vencida de Carla a Ana
    Cuando Carla cancela la solicitud
    Entonces la respuesta tiene estado 409
    Y el código de error es "ESTADO_INVALIDO"
    Y Ana ve la solicitud en estado "VENCIDA"

  @HU-G4-10 @CA1 @CP-A76
  Escenario: CP-A76 Al cancelar, el destinatario la ve CANCELADA y no se mueve dinero
    Dado que Diego le solicitó 25.00 a Bruno
    Cuando Diego cancela la solicitud
    Entonces la respuesta tiene estado 200
    Y la solicitud resuelta tiene fecha de resolución
    Y Bruno ve la solicitud en estado "CANCELADA"
    Y el saldo de Bruno es "800.00"
    Y el saldo de Diego es "2500.00"

  @HU-G4-10 @CA1 @CP-A99
  Esquema del escenario: CP-A99 Cancelar una solicitud ajena informa SOLICITUD_NO_ENCONTRADA y no la cambia
    Dado que Diego le solicitó 25.00 a Bruno
    Cuando <otro> cancela la solicitud
    Entonces la respuesta tiene estado 404
    Y el código de error es "SOLICITUD_NO_ENCONTRADA"
    Y Bruno ve la solicitud en estado "PENDIENTE"

    Ejemplos:
      | otro  |
      | Bruno |
      | Carla |
