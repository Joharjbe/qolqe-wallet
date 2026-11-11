# language: es
Característica: API del núcleo: transferir a otro usuario Qolqe (HU-N-07)
  Reglas RN-05 (monto por operación), RN-06 (límite diario), RN-07 (destino), RN-08 (saldo) y RN-10 (código de operación).
  El oráculo de movimientos es GET /api/movimientos/recientes, que filtra por usuario e incluye los de hoy.
  Los escenarios que acumulan el límite diario fijan el reloj a mediodía para no cruzar la medianoche.

  @HU-N-07 @CA1 @CP-NA97
  Escenario: CP-NA97 Transferir por celular con una descripción
    Cuando Ana hace una transferencia Qolqe de 100.00 a Bruno con la descripción "Almuerzo"
    Entonces la operación termina con "201"
    Y el comprobante es de tipo "QOLQE" por "100.00"
    Y el último movimiento de Ana tiene la descripción "Almuerzo"
    Y el último movimiento de Bruno tiene la descripción "Almuerzo"

  @HU-N-07 @CA1 @CP-NA98
  Esquema del escenario: CP-NA98 Valores límite válidos de la descripción (hasta 60 caracteres)
    Cuando Ana hace una transferencia Qolqe de 1.00 a Bruno con una descripción de <largo> caracteres "<caracter>"
    Entonces la operación termina con "201"
    Y Ana y Bruno ven en su último movimiento la descripción enviada

    Ejemplos:
      | largo | caracter |
      | 1     | d        |
      | 59    | d        |
      | 60    | d        |
      | 60    | ñ        |

  @HU-N-07 @CA1 @CP-NA99
  Esquema del escenario: CP-NA99 Una descripción de 61 caracteres se rechaza sin mover dinero
    Cuando Ana hace una transferencia Qolqe de 1.00 a Bruno con una descripción de 61 caracteres "<caracter>"
    Entonces la operación termina con "422 SOLICITUD_INVALIDA"
    Y el error de validación está en "body.descripcion"
    Y el saldo de Ana es "1500.00"
    Y el saldo de Bruno es "800.00"

    Ejemplos:
      | caracter |
      | d        |
      | ñ        |

  @HU-N-07 @CA1 @CP-NA100
  Esquema del escenario: CP-NA100 Sin descripción se usa el texto por defecto
    Cuando llega un pedido POST a "/api/transferencias" con el token de Ana y el cuerpo <cuerpo>
    Entonces la operación termina con "201"
    Y el último movimiento de Ana tiene la descripción "Transferencia a Bruno D."
    Y el último movimiento de Bruno tiene la descripción "Transferencia de Ana T."

    Ejemplos:
      | caso    | cuerpo                                                                               |
      | ausente | {"tipo": "QOLQE", "celular_destino": "912345678", "monto": "1"}                      |
      | vacía   | {"tipo": "QOLQE", "celular_destino": "912345678", "monto": "1", "descripcion": ""}   |
      | nula    | {"tipo": "QOLQE", "celular_destino": "912345678", "monto": "1", "descripcion": null} |

  @HU-N-07 @CA1 @CP-NA101
  Esquema del escenario: CP-NA101 Valores límite y clases del celular de destino
    Cuando Ana hace una transferencia Qolqe de 10.00 a "<celular>"
    Entonces la operación termina con "<resultado>"
    Y el saldo de Ana es "1500.00"

    Ejemplos:
      | celular    | resultado             |
      |            | 422 DESTINO_REQUERIDO |
      | 91234567   | 422 CELULAR_INVALIDO  |
      | 9123456789 | 422 CELULAR_INVALIDO  |
      | 812345678  | 422 CELULAR_INVALIDO  |
      | 91234567a  | 422 CELULAR_INVALIDO  |

  @HU-N-07 @CA1 @CP-NA102 @tecnico
  Escenario: CP-NA102 El contacto de otro usuario responde como inexistente
    Cuando Bruno hace una transferencia Qolqe de 1.00 con el contacto "Bruno" de Ana
    Entonces la operación termina con "404 CONTACTO_NO_ENCONTRADO"
    Y el saldo de Bruno es "800.00"

  @HU-N-07 @CA1 @CP-NA103 @tecnico
  Esquema del escenario: CP-NA103 Identificador de contacto inexistente, ausente o fuera de rango
    Cuando llega un pedido POST a "/api/transferencias" con el token de Ana y el cuerpo {"tipo": "QOLQE", "contacto_id": <contacto>, "monto": "1"}
    Entonces la operación termina con "<resultado>"
    Y el saldo de Ana es "1500.00"

    Ejemplos:
      | contacto             | resultado                  |
      | 99999                | 404 CONTACTO_NO_ENCONTRADO |
      | 0                    | 404 CONTACTO_NO_ENCONTRADO |
      | -1                   | 404 CONTACTO_NO_ENCONTRADO |
      | null                 | 422 DESTINO_REQUERIDO      |
      | 99999999999999999999 | 422 SOLICITUD_INVALIDA     |

  @HU-N-07 @CA1 @CP-NA104 @tecnico @DEF-NEW-contacto-booleano
  Escenario: CP-NA104 Un contacto_id booleano se rechaza como tipo inválido
    Cuando llega un pedido POST a "/api/transferencias" con el token de Ana y el cuerpo {"tipo": "QOLQE", "contacto_id": true, "monto": "1"}
    Entonces la operación termina con "422 SOLICITUD_INVALIDA"
    Y el error de validación está en "body.contacto_id"
    Y el saldo de Ana es "1500.00"

  @HU-N-07 @CA1 @CP-NA105 @tecnico
  Esquema del escenario: CP-NA105 Formas válidas del cuerpo y valores por defecto
    Cuando llega un pedido POST a "/api/transferencias" con el token de Ana y el cuerpo <cuerpo>
    Entonces la operación termina con "201"
    Y el comprobante es de tipo "QOLQE" por "<monto>"
    Y el comprobante identifica al destinatario como "Bruno D." con celular "912345678"

    Ejemplos:
      | caso                | cuerpo                                                          | monto  |
      | monto entero        | {"celular_destino": "912345678", "monto": 100}                  | 100.00 |
      | monto texto         | {"celular_destino": "912345678", "monto": "100.50"}             | 100.50 |
      | monto decimal       | {"celular_destino": "912345678", "monto": 10.10}                | 10.10  |
      | notación científica | {"celular_destino": "912345678", "monto": "1e2"}                | 100.00 |
      | tipo explícito      | {"tipo": "QOLQE", "celular_destino": "912345678", "monto": "5"} | 5.00   |

  @HU-N-07 @CA1 @CP-NA106 @tecnico
  Esquema del escenario: CP-NA106 Cuerpo mal formado o con tipos inválidos
    Cuando llega un pedido POST a "/api/transferencias" con el token de Ana y el cuerpo <cuerpo>
    Entonces la operación termina con "422 SOLICITUD_INVALIDA"
    Y el error de validación está en "<campo>"
    Y el saldo de Ana es "1500.00"

    Ejemplos:
      | caso                 | cuerpo                                                           | campo                |
      | monto booleano       | {"celular_destino": "912345678", "monto": true}                  | body.monto           |
      | monto nulo           | {"celular_destino": "912345678", "monto": null}                  | body.monto           |
      | monto no numérico    | {"celular_destino": "912345678", "monto": "abc"}                 | body.monto           |
      | monto NaN            | {"celular_destino": "912345678", "monto": "NaN"}                 | body.monto           |
      | monto infinito       | {"celular_destino": "912345678", "monto": "Infinity"}            | body.monto           |
      | sin monto            | {"celular_destino": "912345678"}                                 | body.monto           |
      | tipo desconocido     | {"tipo": "OTRO", "celular_destino": "912345678", "monto": "1"}   | body.tipo            |
      | tipo en minúsculas   | {"tipo": "qolqe", "celular_destino": "912345678", "monto": "1"}  | body.tipo            |
      | celular numérico     | {"celular_destino": 912345678, "monto": "1"}                     | body.celular_destino |
      | descripción numérica | {"celular_destino": "912345678", "monto": "1", "descripcion": 5} | body.descripcion     |
      | contacto texto       | {"contacto_id": "abc", "monto": "1"}                             | body.contacto_id     |
      | contacto decimal     | {"contacto_id": 1.5, "monto": "1"}                               | body.contacto_id     |
      | cuerpo lista         | [1, 2]                                                           | body                 |
      | sin cuerpo           | (ninguno)                                                        | body                 |
      | JSON malformado      | (JSON malformado)                                                | body.1               |

  @HU-N-07 @CA1 @CP-NA107 @tecnico
  Escenario: CP-NA107 Si se indican contacto y celular, prima el contacto
    Cuando Ana hace una transferencia Qolqe de 1.00 a su contacto "Bruno" indicando también el celular "956781234"
    Entonces la operación termina con "201"
    Y el comprobante identifica al destinatario como "Bruno D." con celular "912345678"
    Y el saldo de Bruno es "801.00"
    Y el saldo de Carla es "50.00"

  @HU-N-07 @CA1 @CP-NA108 @tecnico
  Esquema del escenario: CP-NA108 Transferir exige un token vigente, y el 401 tiene prioridad sobre el 422
    Cuando llega un pedido POST a "/api/transferencias" con <credencial> y el cuerpo <cuerpo>
    Entonces la operación termina con "401 NO_AUTENTICADO"
    Y el detalle del error dice "<detalle>"
    Y la respuesta exige autenticación Bearer
    Y el saldo de Ana es "1500.00"
    Y el saldo de Bruno es "800.00"

    Ejemplos:
      | credencial                      | cuerpo                                                          | detalle                         |
      | ningún token                    | {"tipo": "QOLQE", "celular_destino": "912345678", "monto": "1"} | Falta el token de autenticación |
      | ningún token                    | {"monto": "abc"}                                                | Falta el token de autenticación |
      | el esquema Basic                | {"tipo": "QOLQE", "celular_destino": "912345678", "monto": "1"} | Falta el token de autenticación |
      | un token inválido               | {"tipo": "QOLQE", "celular_destino": "912345678", "monto": "1"} | Token inválido                  |
      | un token firmado con otra clave | {"tipo": "QOLQE", "celular_destino": "912345678", "monto": "1"} | Token inválido                  |
      | el token vencido de Ana         | {"tipo": "QOLQE", "celular_destino": "912345678", "monto": "1"} | El token expiró                 |

  @HU-N-07 @CA2 @CP-NA109
  Esquema del escenario: CP-NA109 RN-05 valores límite válidos del monto por operación
    Cuando Ana hace una transferencia Qolqe de <monto> a Carla
    Entonces la operación termina con "201"
    Y el comprobante es de tipo "QOLQE" por "<registrado>"
    Y el saldo de Ana es "<saldo>"

    Ejemplos:
      | monto  | registrado | saldo   |
      | 0.01   | 0.01       | 1499.99 |
      | 499.99 | 499.99     | 1000.01 |
      | 500.00 | 500.00     | 1000.00 |
      | 500    | 500.00     | 1000.00 |

  @HU-N-07 @CA2 @CP-NA110
  Esquema del escenario: CP-NA110 RN-05 montos no válidos por operación
    Cuando Ana hace una transferencia Qolqe de <monto> a Carla
    Entonces la operación termina con "422 MONTO_INVALIDO"
    Y el detalle del error dice "<detalle>"
    Y el saldo de Ana es "1500.00"

    Ejemplos:
      | monto   | detalle                                              |
      | 0       | El monto debe ser mayor a cero                       |
      | -0.01   | El monto debe ser mayor a cero                       |
      | -5      | El monto debe ser mayor a cero                       |
      | 0.001   | El monto admite como máximo 2 decimales              |
      | 1.005   | El monto admite como máximo 2 decimales              |
      | 100.000 | El monto admite como máximo 2 decimales              |
      | 500.01  | El monto supera el límite por operación de S/ 500.00 |
      | 1000    | El monto supera el límite por operación de S/ 500.00 |

  @HU-N-07 @CA2 @CP-NA111
  Esquema del escenario: CP-NA111 RN-07 no se transfiere a sí mismo ni a un celular no registrado
    Cuando Ana hace una transferencia Qolqe de 10.00 a <destino>
    Entonces la operación termina con "<resultado>"
    Y el saldo de Ana es "<saldo>"

    Ejemplos:
      | destino     | resultado                    | saldo   |
      | Ana         | 422 TRANSFERENCIA_A_SI_MISMO | 1500.00 |
      | "900000999" | 404 DESTINO_NO_REGISTRADO    | 1500.00 |
      | Bruno       | 201                          | 1490.00 |

  @HU-N-07 @CA2 @CP-NA112 @DEF-04
  Escenario: CP-NA112 RN-07 no se transfiere por celular a una cuenta cerrada
    Cuando Ana hace una transferencia Qolqe de 10.00 a Fabián
    Entonces la operación termina con "422 DESTINO_INACTIVO"
    Y el saldo de Ana es "1500.00"

  @HU-N-07 @CA2 @CP-NA113
  Esquema del escenario: CP-NA113 RN-08 valores límite del saldo disponible
    Cuando Carla hace una transferencia Qolqe de <monto> a Bruno
    Entonces la operación termina con "<resultado>"
    Y el saldo de Carla es "<saldo>"

    Ejemplos:
      | monto | resultado              | saldo |
      | 49.99 | 201                    | 0.01  |
      | 50.00 | 201                    | 0.00  |
      | 50.01 | 422 SALDO_INSUFICIENTE | 50.00 |

  @HU-N-07 @CA2 @CP-NA114
  Escenario: CP-NA114 RN-08 con el saldo en cero no se transfiere ni un céntimo
    Dado Carla ya hizo transferencias Qolqe a Bruno de 50.00
    Cuando Carla hace una transferencia Qolqe de 0.01 a Bruno
    Entonces la operación termina con "422 SALDO_INSUFICIENTE"
    Y el saldo de Carla es "0.00"

  @HU-N-07 @CA2 @CP-NA115
  Esquema del escenario: CP-NA115 RN-06 valores límite del límite diario por defecto y del usuario
    Dado que el reloj de Qolqe marca hoy a las "12:00:00"
    Y el saldo de <usuario> se ajusta a "3000.00"
    Y <usuario> ya hizo transferencias Qolqe a Bruno de <previas>
    Cuando <usuario> hace una transferencia Qolqe de <monto> a Bruno
    Entonces la operación termina con "<resultado>"
    Y <usuario> ve usado hoy "<usado>" y disponible "<disponible>"

    Ejemplos:
      | usuario | limite  | previas                        | monto | resultado                  | usado   | disponible |
      | Diego   | 1000.00 | 500.00, 499.99                 | 0.01  | 201                        | 1000.00 | 0.00       |
      | Diego   | 1000.00 | 500.00, 499.99                 | 0.02  | 422 LIMITE_DIARIO_EXCEDIDO | 999.99  | 0.01       |
      | Ana     | 2000.00 | 500.00, 500.00, 500.00, 499.99 | 0.01  | 201                        | 2000.00 | 0.00       |
      | Ana     | 2000.00 | 500.00, 500.00, 500.00, 499.99 | 0.02  | 422 LIMITE_DIARIO_EXCEDIDO | 1999.99 | 0.01       |

  @HU-N-07 @CA2 @CP-NA116
  Escenario: CP-NA116 RN-06 con el límite diario agotado se rechaza un céntimo más
    Dado que el reloj de Qolqe marca hoy a las "12:00:00"
    Y Diego ya hizo transferencias Qolqe a Bruno de 500.00, 499.99, 0.01
    Cuando Diego hace una transferencia Qolqe de 0.01 a Bruno
    Entonces la operación termina con "422 LIMITE_DIARIO_EXCEDIDO"
    Y el detalle del error dice "La operación supera tu límite diario de S/ 1000.00"
    Y el saldo de Diego es "1500.00"

  @HU-N-07 @CA2 @CP-NA117 @DEF-20
  Escenario: CP-NA117 RN-06 el límite diario suma también las transferencias interbancarias
    Dado que el reloj de Qolqe marca hoy a las "12:00:00"
    Y Diego ya hizo transferencias interbancarias de 500.00
    Y Diego ya hizo transferencias Qolqe a Bruno de 500.00
    Cuando Diego hace una transferencia Qolqe de 0.01 a Bruno
    Entonces la operación termina con "422 LIMITE_DIARIO_EXCEDIDO"
    Y Diego ve usado hoy "1000.00" y disponible "0.00"

  @HU-N-07 @CA2 @CP-NA118
  Escenario: CP-NA118 RN-06 una interbancaria se rechaza si las Qolqe ya agotaron el límite
    Dado que el reloj de Qolqe marca hoy a las "12:00:00"
    Y Diego ya hizo transferencias Qolqe a Bruno de 500.00, 500.00
    Cuando Diego hace una transferencia interbancaria de 0.01 al CCI "00219300123456789012"
    Entonces la operación termina con "422 LIMITE_DIARIO_EXCEDIDO"
    Y el saldo de Diego es "1500.00"

  @HU-N-07 @CA2 @CP-NA119
  Escenario: CP-NA119 RN-06 una reducción del límite diario rige de inmediato
    Dado que el reloj de Qolqe marca hoy a las "12:00:00"
    Y Diego redujo su límite diario a "100"
    Y Diego ya hizo transferencias Qolqe a Bruno de 100.00
    Cuando Diego hace una transferencia Qolqe de 0.01 a Bruno
    Entonces la operación termina con "422 LIMITE_DIARIO_EXCEDIDO"
    Y el detalle del error dice "La operación supera tu límite diario de S/ 100.00"

  @HU-N-07 @CA2 @CP-NA120
  Esquema del escenario: CP-NA120 RN-06 un aumento del límite diario rige recién a las 24 horas
    Dado que el reloj de Qolqe marca hoy a las "12:00:00"
    Y Diego pidió subir su límite diario a "1500"
    Y el reloj de Qolqe avanza <minutos> minutos
    Y Diego ya hizo transferencias Qolqe a Bruno de 500.00, 500.00
    Cuando Diego hace una transferencia Qolqe de 0.01 a Bruno
    Entonces la operación termina con "<resultado>"

    Ejemplos:
      | minutos | resultado                  |
      | 1439    | 422 LIMITE_DIARIO_EXCEDIDO |
      | 1440    | 201                        |

  @HU-N-07 @CA2 @CP-NA121
  Esquema del escenario: CP-NA121 RN-06 el límite diario se reinicia a las 00:00 de Lima
    Dado que el reloj de Qolqe marca hoy a las "23:59:00"
    Y Diego ya hizo transferencias Qolqe a Bruno de 500.00, 500.00
    Y el reloj de Qolqe marca <dia> a las "<hora>"
    Cuando Diego hace una transferencia Qolqe de 0.01 a Bruno
    Entonces la operación termina con "<resultado>"

    Ejemplos:
      | dia    | hora     | resultado                  |
      | hoy    | 23:59:59 | 422 LIMITE_DIARIO_EXCEDIDO |
      | mañana | 00:00:00 | 201                        |

  @HU-N-07 @CA2 @CP-NA122 @tecnico
  Esquema del escenario: CP-NA122 Tabla de decisión del orden de validación cuando fallan varias reglas
    Dado que el reloj de Qolqe marca hoy a las "12:00:00"
    Y Diego ya hizo transferencias Qolqe a Bruno de 500.00, 500.00
    Y el saldo de Diego se ajusta a "<saldo>"
    Cuando Diego hace una transferencia Qolqe de <monto> a <destino>
    Entonces la operación termina con "<resultado>"

    Ejemplos:
      | regla | monto  | destino     | saldo   | resultado                    |
      | R1    | 0      | Diego       | 0.00    | 422 MONTO_INVALIDO           |
      | R2    | 600.00 | "900000999" | 0.00    | 422 MONTO_INVALIDO           |
      | R3    | 0.01   | Diego       | 0.00    | 422 TRANSFERENCIA_A_SI_MISMO |
      | R4    | 0.01   | "900000999" | 0.00    | 404 DESTINO_NO_REGISTRADO    |
      | R5    | 0.01   | Bruno       | 0.00    | 422 SALDO_INSUFICIENTE       |
      | R6    | 0.01   | Bruno       | 1500.00 | 422 LIMITE_DIARIO_EXCEDIDO   |

  @HU-N-07 @CA3 @CP-NA123
  Escenario: CP-NA123 La transferencia debita al emisor y acredita al destinatario el mismo monto
    Cuando Ana hace una transferencia Qolqe de 100.00 a Bruno
    Entonces la operación termina con "201"
    Y el comprobante informa el saldo "1400.00"
    Y el saldo de Ana es "1400.00"
    Y el saldo de Bruno es "900.00"

  @HU-N-07 @CA3 @CP-NA124
  Escenario: CP-NA124 Emisor y destinatario ven su movimiento con el mismo código de operación
    Cuando Ana hace una transferencia Qolqe de 100.00 a Bruno
    Entonces el último movimiento de Ana es "TRANSFERENCIA_ENVIADA" por "-100.00" con contraparte "912345678"
    Y el último movimiento de Ana registra la comisión "0.00" y el importe "-100.00"
    Y el último movimiento de Bruno es "TRANSFERENCIA_RECIBIDA" por "100.00" con contraparte "987654321"
    Y el último movimiento de Ana y el de Bruno llevan el código y la fecha del comprobante

  @HU-N-07 @CA3 @CP-NA125
  Escenario: CP-NA125 El destinatario recibe un SMS con el monto y el código de operación
    Cuando Ana hace una transferencia Qolqe de 100.00 a Bruno
    Entonces la operación termina con "201"
    Y "912345678" recibió un SMS que contiene "Recibiste S/ 100.00 de Ana T."
    Y el SMS de "912345678" incluye el código de operación del comprobante

  @HU-N-07 @CA3 @CP-NA126 @DEF-22
  Escenario: CP-NA126 RN-10 dos transferencias del mismo usuario en el mismo segundo tienen códigos distintos
    Dado Ana ya hizo transferencias Qolqe a Bruno de 1.00
    Y el reloj de Qolqe vuelve al segundo de la última transferencia
    Cuando Ana hace una transferencia Qolqe de 1.00 a Carla
    Entonces la operación termina con "201"
    Y las dos últimas transferencias tienen la misma fecha y códigos de operación distintos

  @HU-N-07 @CA3 @CA5 @CP-NA127 @tecnico @DEF-22
  Escenario: CP-NA127 RN-10 transferencias simultáneas del mismo usuario reciben códigos distintos
    Cuando Ana lanza 5 transferencias Qolqe simultáneas de 1.00 a Bruno
    Entonces las 5 transferencias simultáneas terminan con "201"
    Y los códigos de operación de las transferencias simultáneas son todos distintos

  @HU-N-07 @CA3 @CP-NA128 @tecnico
  Escenario: CP-NA128 El emisor consulta por código el detalle de su transferencia
    Dado Ana ya hizo transferencias Qolqe a Bruno de 100.00
    Cuando Ana consulta el movimiento por el código de la última transferencia
    Entonces la operación termina con "200"
    Y el movimiento consultado es "TRANSFERENCIA_ENVIADA" por "-100.00"

  @HU-N-07 @CA3 @CP-NA129 @tecnico @DEF-24
  Escenario: CP-NA129 El destinatario consulta por código su propio movimiento recibido
    Dado Ana ya hizo transferencias Qolqe a Bruno de 100.00
    Cuando Bruno consulta el movimiento por el código de la última transferencia
    Entonces la operación termina con "200"
    Y el movimiento consultado es "TRANSFERENCIA_RECIBIDA" por "100.00"

  @HU-N-07 @CA3 @CP-NA130 @tecnico @DEF-24
  Escenario: CP-NA130 Un tercero no puede ver por código el movimiento de otros
    Dado Ana ya hizo transferencias Qolqe a Bruno de 100.00
    Cuando Carla consulta el movimiento por el código de la última transferencia
    Entonces la operación termina con "404 MOVIMIENTO_NO_ENCONTRADO"

  @HU-N-07 @CA3 @CA5 @CP-NA131 @tecnico
  Escenario: CP-NA131 Transferencias cruzadas simultáneas conservan el dinero total
    Cuando Ana y Bruno se envían 10 transferencias simultáneas de 10.00 cada uno
    Entonces las 20 transferencias simultáneas terminan con "201"
    Y el saldo de Ana es "1500.00"
    Y el saldo de Bruno es "800.00"

  @HU-N-07 @CA4 @CP-NA132
  Escenario: CP-NA132 El comprobante de una transferencia Qolqe trae todos sus datos
    Dado que el reloj de Qolqe marca hoy a las "10:00:00"
    Cuando Ana hace una transferencia Qolqe de 100.00 a Bruno
    Entonces la operación termina con "201"
    Y el comprobante tiene un código de operación "TRF" seguido de 17 dígitos
    Y el comprobante es de tipo "QOLQE" por "100.00"
    Y el comprobante muestra monto "100.00", comisión "0.00", total "100.00" y saldo "1400.00"
    Y el comprobante identifica al destinatario como "Bruno D." con celular "912345678"
    Y la fecha del comprobante es hoy a las "10:00"

  @HU-N-07 @CA4 @CP-NA133
  Esquema del escenario: CP-NA133 El comprobante enmascara el nombre del destinatario
    Dado se registró la cuenta "Pedro" con el celular "955000222"
    Cuando Ana hace una transferencia Qolqe de 1.00 a "<celular>"
    Entonces la operación termina con "201"
    Y el comprobante identifica al destinatario como "<nombre>" con celular "<celular>"

    Ejemplos:
      | celular   | nombre   |
      | 956781234 | Carla R. |
      | 912345678 | Bruno D. |
      | 955000222 | Pedro    |

  @HU-N-07 @CA5 @CP-NA134 @tecnico @DEF-21
  Escenario: CP-NA134 Transferencias simultáneas no dejan el saldo negativo
    Cuando Carla lanza 5 transferencias Qolqe simultáneas de 20.00 a Bruno
    Entonces como máximo 2 de las transferencias simultáneas terminan con "201"
    Y las demás transferencias simultáneas terminan con "422 SALDO_INSUFICIENTE"
    Y los saldos cuadran con las transferencias simultáneas aceptadas

  @HU-N-07 @CA5 @CP-NA135 @tecnico @DEF-21
  Escenario: CP-NA135 Transferencias simultáneas no superan el límite diario
    Dado que el reloj de Qolqe marca hoy a las "12:00:00"
    Cuando Diego lanza 5 transferencias Qolqe simultáneas de 300.00 a Bruno
    Entonces como máximo 3 de las transferencias simultáneas terminan con "201"
    Y las demás transferencias simultáneas terminan con "422 LIMITE_DIARIO_EXCEDIDO"
    Y lo usado hoy por Diego no supera su límite diario
