# language: es
Característica: API del núcleo: cerrar mi cuenta (HU-N-06)
  Regla RN-07. El cierre exige el PIN, saldo S/ 0.00 y ninguna solicitud de dinero pendiente.
  Los celulares 9000000NN son usuarios de carga de la semilla (PIN 2580, saldo S/ 10,000.00, sin contactos).

  @HU-N-06 @CA1 @CP-NA80
  Escenario: CP-NA80 Un PIN incorrecto no cierra la cuenta
    Dado que el saldo de Carla se ajusta a "0.00"
    Cuando Carla pide cerrar su cuenta con el PIN "5918"
    Entonces la operación termina con "422 PIN_INCORRECTO"
    Y la cuenta de Carla figura como "ACTIVA"

  @HU-N-06 @CA1 @CP-NA81 @tecnico
  Esquema del escenario: CP-NA81 Un PIN que no tiene 4 dígitos se responde como incorrecto
    Dado que el saldo de Carla se ajusta a "0.00"
    Cuando Carla pide cerrar su cuenta con el PIN "<pin>"
    Entonces la operación termina con "422 PIN_INCORRECTO"
    Y la cuenta de Carla figura como "ACTIVA"

    Ejemplos:
      | pin   |
      |       |
      | 591   |
      | 59170 |

  @HU-N-06 @CA1 @CP-NA82 @tecnico
  Esquema del escenario: CP-NA82 Cuerpo del cierre ausente, mal formado o con tipos inválidos
    Dado que el saldo de Carla se ajusta a "0.00"
    Cuando llega un pedido POST a "/api/cuentas/me/cierre" con el token de Carla y el cuerpo <cuerpo>
    Entonces la operación termina con "422 SOLICITUD_INVALIDA"
    Y el error de validación está en "<campo>"
    Y la cuenta de Carla figura como "ACTIVA"

    Ejemplos:
      | cuerpo            | campo    |
      | {"pin": 5917}     | body.pin |
      | {"pin": null}     | body.pin |
      | {}                | body.pin |
      | (ninguno)         | body     |
      | (JSON malformado) | body.1   |

  @HU-N-06 @CA1 @CP-NA83 @tecnico
  Esquema del escenario: CP-NA83 Cerrar la cuenta exige un token vigente
    Dado que el saldo de Carla se ajusta a "0.00"
    Cuando llega un pedido POST a "/api/cuentas/me/cierre" con <credencial> y el cuerpo {"pin": "5917"}
    Entonces la operación termina con "401 NO_AUTENTICADO"
    Y el detalle del error dice "<detalle>"
    Y la respuesta exige autenticación Bearer
    Y la cuenta de Carla figura como "ACTIVA"

    Ejemplos:
      | credencial                      | detalle                         |
      | ningún token                    | Falta el token de autenticación |
      | el esquema Basic                | Falta el token de autenticación |
      | un token inválido               | Token inválido                  |
      | un token firmado con otra clave | Token inválido                  |
      | el token vencido de Carla       | El token expiró                 |

  @HU-N-06 @CA1 @CP-NA84 @tecnico
  Escenario: CP-NA84 Los PIN errados al cerrar la cuenta no bloquean el ingreso (riesgo: el cierre revela el PIN)
    Cuando Bruno pide cerrar su cuenta con el PIN "0000" 4 veces
    Entonces todos los intentos de cierre responden "PIN_INCORRECTO"
    Cuando Bruno pide cerrar su cuenta con el PIN "7391"
    Entonces la operación termina con "422 SALDO_PENDIENTE"
    Y la cuenta de Bruno figura como "ACTIVA"

  @HU-N-06 @CA2 @CP-NA85
  Esquema del escenario: CP-NA85 Valores límite del saldo: solo se cierra con S/ 0.00 exactos
    Dado que el saldo de Carla se ajusta a "<saldo>"
    Cuando Carla pide cerrar su cuenta con el PIN "5917"
    Entonces la operación termina con "<resultado>"
    Y la cuenta de Carla figura como "<estado>"

    Ejemplos:
      | saldo | resultado           | estado  |
      | 0.01  | 422 SALDO_PENDIENTE | ACTIVA  |
      | 50.00 | 422 SALDO_PENDIENTE | ACTIVA  |
      | 0.00  | 204                 | CERRADA |

  @HU-N-06 @CA1 @CA2 @CA3 @CP-NA86 @tecnico
  Esquema del escenario: CP-NA86 Tabla de decisión del cierre: PIN, saldo y solicitudes pendientes
    Dado que el saldo de <usuario> se ajusta a "<saldo>"
    Y <usuario> <pendientes> solicitudes pendientes
    Cuando <usuario> pide cerrar su cuenta con el PIN "<pin>"
    Entonces la operación termina con "<resultado>"
    Y la cuenta de <usuario> figura como "<estado>"

    Ejemplos:
      | regla | usuario | saldo  | pin  | pendientes | resultado                  | estado  |
      | R1    | Bruno   | 800.00 | 0000 | tiene      | 422 PIN_INCORRECTO         | ACTIVA  |
      | R2    | Carla   | 0.00   | 0000 | no tiene   | 422 PIN_INCORRECTO         | ACTIVA  |
      | R3    | Bruno   | 800.00 | 7391 | tiene      | 422 SALDO_PENDIENTE        | ACTIVA  |
      | R4    | Bruno   | 0.00   | 7391 | tiene      | 409 SOLICITUDES_PENDIENTES | ACTIVA  |
      | R5    | Carla   | 0.00   | 5917 | no tiene   | 204                        | CERRADA |
      | R6    | Carla   | 0.00   | 5917 | tiene      | 409 SOLICITUDES_PENDIENTES | ACTIVA  |
      | R7    | Bruno   | 0.00   | 7391 | no tiene   | 204                        | CERRADA |

  @HU-N-06 @CA3 @CP-NA87
  Esquema del escenario: CP-NA87 Una solicitud pendiente, enviada o recibida, impide cerrar la cuenta
    Dado que <solicitante> registró una solicitud pendiente de 10.00 para <destinatario>
    Y el saldo de <titular> se ajusta a "0.00"
    Cuando <titular> pide cerrar su cuenta con el PIN "2580"
    Entonces la operación termina con "409 SOLICITUDES_PENDIENTES"
    Y la cuenta de <titular> figura como "ACTIVA"

    Ejemplos:
      | rol      | solicitante | destinatario | titular   |
      | recibida | Diego       | 900000001    | 900000001 |
      | enviada  | 900000003   | Bruno        | 900000003 |

  @HU-N-06 @CA3 @CP-NA88
  Esquema del escenario: CP-NA88 Una solicitud ya resuelta no impide cerrar la cuenta
    Dado que <solicitante> registró una solicitud pendiente de 10.00 para <destinatario>
    Y <titular> resuelve la solicitud como "<estado>"
    Y el saldo de <titular> se ajusta a "0.00"
    Cuando <titular> pide cerrar su cuenta con el PIN "2580"
    Entonces la operación termina con "204"
    Y la cuenta de <titular> figura como "CERRADA"

    Ejemplos:
      | estado    | solicitante | destinatario | titular   |
      | RECHAZADA | Diego       | 900000002    | 900000002 |
      | ACEPTADA  | Diego       | 900000001    | 900000001 |
      | CANCELADA | 900000003   | Bruno        | 900000003 |

  @HU-N-06 @CA3 @CP-NA89
  Esquema del escenario: CP-NA89 Frontera de las 48 horas: al vencer, la solicitud deja de impedir el cierre
    Dado que Diego registró una solicitud pendiente de 10.00 para 900000001
    Y el saldo de 900000001 se ajusta a "0.00"
    Y el reloj se ubica <transcurrido> después de creada la solicitud
    Cuando 900000001 pide cerrar su cuenta con el PIN "2580"
    Entonces la operación termina con "<resultado>"

    Ejemplos:
      | transcurrido | resultado                  |
      | 47:59:59     | 409 SOLICITUDES_PENDIENTES |
      | 48:00:00     | 204                        |

  @HU-N-06 @CA3 @CP-NA90
  Escenario: CP-NA90 Una solicitud vencida de la semilla no impide cerrar la cuenta
    Dado que el saldo de Carla se ajusta a "0.00"
    Y la única solicitud de Carla figura como "VENCIDA"
    Cuando Carla pide cerrar su cuenta con el PIN "5917"
    Entonces la operación termina con "204"

  @HU-N-06 @CA4 @CP-NA91
  Escenario: CP-NA91 Cerrar la cuenta cierra todas sus sesiones y avisa por SMS
    Dado que el saldo de Carla se ajusta a "0.00"
    Y Carla abrió una segunda sesión
    Cuando Carla pide cerrar su cuenta con el PIN "5917"
    Entonces la operación termina con "204"
    Y ninguna de las dos sesiones de Carla sigue vigente
    Y "956781234" recibió un SMS que contiene "Tu cuenta Qolqe fue cerrada. Gracias por usar Qolqe."

  @HU-N-06 @CA4 @CP-NA92
  Esquema del escenario: CP-NA92 Una cuenta cerrada no puede volver a ingresar
    Dado que el saldo de Carla se ajusta a "0.00"
    Y Carla ya cerró su cuenta con su PIN
    Cuando se intenta ingresar como Carla con el PIN "<pin>"
    Entonces la operación termina con "<resultado>"

    Ejemplos:
      | pin  | resultado                  |
      | 5917 | 401 CUENTA_CERRADA         |
      | 1357 | 401 CREDENCIALES_INVALIDAS |

  @HU-N-06 @CA4 @CP-NA93
  Escenario: CP-NA93 El celular de una cuenta cerrada no se puede registrar otra vez
    Dado que el saldo de Carla se ajusta a "0.00"
    Y Carla ya cerró su cuenta con su PIN
    Cuando se registra una cuenta nueva con el celular "956781234"
    Entonces la operación termina con "409 CELULAR_REGISTRADO"

  @HU-N-06 @CA4 @CP-NA94 @DEF-04
  Esquema del escenario: CP-NA94 Nadie puede transferir a una cuenta recién cerrada
    Dado que el saldo de Carla se ajusta a "0.00"
    Y Carla ya cerró su cuenta con su PIN
    Cuando <emisor> hace una transferencia Qolqe de <monto> a <destino>
    Entonces la operación termina con "422 DESTINO_INACTIVO"
    Y el saldo de <emisor> es "<saldo>"

    Ejemplos:
      | via      | emisor | monto | destino                   | saldo   |
      | celular  | Bruno  | 10.00 | Carla                     | 800.00  |
      | contacto | Ana    | 1.00  | su contacto "Prima Carla" | 1500.00 |

  # La única solicitud de una cuenta cerrada es la vencida (CA3 impide cerrar con pendientes): el caso detecta DEF-03.
  # Si se corrige DEF-03 pero no DEF-04, este caso pasa; DEF-04 sigue detectado por CP-NA94 y CP-NA112.
  @HU-N-06 @CA4 @CP-NA95 @DEF-03
  Escenario: CP-NA95 Aceptar la solicitud de una cuenta cerrada no le transfiere dinero
    Dado que el saldo de Carla se ajusta a "0.00"
    Y Carla ya cerró su cuenta con su PIN
    Y la solicitud vencida de Carla a Ana
    Cuando Ana acepta la solicitud
    Entonces la operación termina con "409 ESTADO_INVALIDO"
    Y el saldo de Ana es "1500.00"

  @HU-N-06 @CA4 @CP-NA96 @tecnico
  Esquema del escenario: CP-NA96 El token de una cuenta cerrada ya no sirve en ningún endpoint
    Dado que el saldo de Carla se ajusta a "0.00"
    Y Carla ya cerró su cuenta con su PIN
    Cuando llega un pedido <metodo> a "<ruta>" con el token de Carla y el cuerpo <cuerpo>
    Entonces la operación termina con "401 NO_AUTENTICADO"
    Y el detalle del error dice "La sesión fue cerrada"
    Y el saldo de Bruno es "800.00"

    Ejemplos:
      | metodo | ruta                                  | cuerpo                                                          |
      | POST   | /api/transferencias                   | {"tipo": "QOLQE", "celular_destino": "912345678", "monto": "1"} |
      | POST   | /api/cuentas/me/cierre                | {"pin": "5917"}                                                 |
      | POST   | /api/auth/logout                      | (ninguno)                                                       |
      | GET    | /api/cuentas/me/saldo                 | (ninguno)                                                       |
      | GET    | /api/transferencias/comision?monto=10 | (ninguno)                                                       |
