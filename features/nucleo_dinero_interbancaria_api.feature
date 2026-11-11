# language: es
Característica: API del núcleo: transferir a otro banco (HU-N-08)
  Reglas RN-05, RN-06, RN-08 y RN-09 (comisión de 1.5 %, mínimo S/ 1.00 y máximo S/ 5.00, redondeo comercial).
  El CCI de prueba es 00219300123456789012; el comprobante y el movimiento solo muestran sus últimos 4 dígitos.

  @HU-N-08 @CA1 @CP-NA136
  Esquema del escenario: CP-NA136 Valores límite y clases del CCI
    Cuando Ana hace una transferencia interbancaria de 100.00 al CCI "<cci>"
    Entonces la operación termina con "<resultado>"
    Y el saldo de Ana es "<saldo>"

    Ejemplos:
      | caso           | cci                    | resultado             | saldo   |
      | 19 dígitos     | 0021930012345678901    | 422 CCI_INVALIDO      | 1500.00 |
      | 20 dígitos     | 00219300123456789012   | 201                   | 1398.50 |
      | 21 dígitos     | 002193001234567890123  | 422 CCI_INVALIDO      | 1500.00 |
      | con una letra  | 0021930012345678901A   | 422 CCI_INVALIDO      | 1500.00 |
      | con guiones    | 0021-9300-1234-5678-90 | 422 CCI_INVALIDO      | 1500.00 |
      | ancho completo | ００２１９３００１２３４５６７８９０１２   | 422 CCI_INVALIDO      | 1500.00 |
      | vacío          |                        | 422 DESTINO_REQUERIDO | 1500.00 |

  @HU-N-08 @CA1 @CP-NA137 @tecnico
  Esquema del escenario: CP-NA137 CCI ausente, con espacios o de tipo inválido
    Cuando llega un pedido POST a "/api/transferencias" con el token de Ana y el cuerpo <cuerpo>
    Entonces la operación termina con "<resultado>"
    Y el saldo de Ana es "1500.00"

    Ejemplos:
      | caso                | cuerpo                                                                    | resultado              |
      | sin CCI             | {"tipo": "INTERBANCARIA", "monto": "100"}                                 | 422 DESTINO_REQUERIDO  |
      | CCI nulo            | {"tipo": "INTERBANCARIA", "monto": "100", "cci": null}                    | 422 DESTINO_REQUERIDO  |
      | espacio al inicio   | {"tipo": "INTERBANCARIA", "monto": "100", "cci": " 0021930012345678901"}  | 422 CCI_INVALIDO       |
      | espacio al final    | {"tipo": "INTERBANCARIA", "monto": "100", "cci": "00219300123456789012 "} | 422 CCI_INVALIDO       |
      | CCI numérico        | {"tipo": "INTERBANCARIA", "monto": "100", "cci": 219300123456789012}      | 422 SOLICITUD_INVALIDA |
      | sin monto           | {"tipo": "INTERBANCARIA", "cci": "00219300123456789012"}                  | 422 SOLICITUD_INVALIDA |
      | monto antes que CCI | {"tipo": "INTERBANCARIA", "monto": "0", "cci": "123"}                     | 422 MONTO_INVALIDO     |

  @HU-N-08 @CA1 @CP-NA138
  Escenario: CP-NA138 Transferencia interbancaria válida y su comprobante
    Cuando Ana hace una transferencia interbancaria de 100.00 al CCI "00219300123456789012"
    Entonces la operación termina con "201"
    Y el comprobante tiene un código de operación "TRF" seguido de 17 dígitos
    Y el comprobante es de tipo "INTERBANCARIA" por "100.00"
    Y el comprobante muestra monto "100.00", comisión "1.50", total "101.50" y saldo "1398.50"
    Y el comprobante identifica el destino solo por el CCI "****************9012"

  @HU-N-08 @CA1 @CP-NA139 @tecnico
  Esquema del escenario: CP-NA139 Los campos que no corresponden al tipo de transferencia se ignoran
    Cuando llega un pedido POST a "/api/transferencias" con el token de Ana y el cuerpo <cuerpo>
    Entonces la operación termina con "201"
    Y el comprobante es de tipo "<tipo>" por "1.00"
    Y el comprobante cobra una comisión de "<comision>" y un total de "<total>"
    Y el saldo de Bruno es "<saldo_bruno>"

    Ejemplos:
      | caso                      | cuerpo                                                                                                 | tipo          | comision | total | saldo_bruno |
      | interbancaria con celular | {"tipo": "INTERBANCARIA", "cci": "00219300123456789012", "celular_destino": "912345678", "monto": "1"} | INTERBANCARIA | 1.00     | 2.00  | 800.00      |
      | Qolqe con CCI             | {"tipo": "QOLQE", "celular_destino": "912345678", "cci": "00219300123456789012", "monto": "1"}         | QOLQE         | 0.00     | 1.00  | 801.00      |

  @HU-N-08 @CA1 @CP-NA140 @tecnico
  Esquema del escenario: CP-NA140 La transferencia interbancaria exige un token vigente
    Cuando llega un pedido POST a "/api/transferencias" con <credencial> y el cuerpo {"tipo": "INTERBANCARIA", "cci": "00219300123456789012", "monto": "100"}
    Entonces la operación termina con "401 NO_AUTENTICADO"
    Y el detalle del error dice "<detalle>"
    Y la respuesta exige autenticación Bearer
    Y el saldo de Ana es "1500.00"

    Ejemplos:
      | credencial                      | detalle                         |
      | ningún token                    | Falta el token de autenticación |
      | un token inválido               | Token inválido                  |
      | un token firmado con otra clave | Token inválido                  |
      | el token vencido de Ana         | El token expiró                 |

  @HU-N-08 @CA2 @CP-NA141
  Esquema del escenario: CP-NA141 RN-09 comisión cobrada en el mínimo, la zona proporcional y el tope
    Cuando Ana hace una transferencia interbancaria de <monto> al CCI "00219300123456789012"
    Entonces la operación termina con "201"
    Y el comprobante cobra una comisión de "<comision>" y un total de "<total>"
    Y el comprobante informa el saldo "<saldo>"
    Y el último movimiento de Ana registra la comisión "<comision>" y el importe "-<total>"

    Ejemplos:
      | clase        | monto  | comision | total  | saldo   |
      | mínimo       | 0.01   | 1.00     | 1.01   | 1498.99 |
      | mínimo       | 66.99  | 1.00     | 67.99  | 1432.01 |
      | proporcional | 67.01  | 1.01     | 68.02  | 1431.98 |
      | proporcional | 70.00  | 1.05     | 71.05  | 1428.95 |
      | proporcional | 100.00 | 1.50     | 101.50 | 1398.50 |
      | proporcional | 100.50 | 1.51     | 102.01 | 1397.99 |
      | proporcional | 332.99 | 4.99     | 337.98 | 1162.02 |
      | tope         | 333.34 | 5.00     | 338.34 | 1161.66 |
      | tope         | 500.00 | 5.00     | 505.00 | 995.00  |

  @HU-N-08 @CA2 @CP-NA142 @DEF-23
  Esquema del escenario: CP-NA142 RN-09 la comisión usa redondeo comercial cuando el tercer decimal es 5
    Cuando Ana hace una transferencia interbancaria de <monto> al CCI "00219300123456789012"
    Entonces la operación termina con "201"
    Y el comprobante cobra una comisión de "<comision>" y un total de "<total>"

    Ejemplos:
      | monto  | exacta | comision | total  |
      | 67.00  | 1.005  | 1.01     | 68.01  |
      | 71.00  | 1.065  | 1.07     | 72.07  |
      | 299.00 | 4.485  | 4.49     | 303.49 |

  @HU-N-08 @CA2 @CP-NA143
  Escenario: CP-NA143 RN-08 una interbancaria puede usar todo el saldo incluida la comisión
    Cuando Carla hace una transferencia interbancaria de 49.00 al CCI "00219300123456789012"
    Entonces la operación termina con "201"
    Y el comprobante cobra una comisión de "1.00" y un total de "50.00"
    Y el saldo de Carla es "0.00"

  @HU-N-08 @CA2 @CP-NA144 @DEF-19
  Esquema del escenario: CP-NA144 RN-08 el saldo debe cubrir el monto más la comisión
    Cuando Carla hace una transferencia interbancaria de <monto> al CCI "00219300123456789012"
    Entonces la operación termina con "422 SALDO_INSUFICIENTE"
    Y el saldo de Carla es "50.00"

    Ejemplos:
      | monto | total |
      | 49.01 | 50.01 |
      | 50.00 | 51.00 |

  @HU-N-08 @CA2 @CP-NA145
  Esquema del escenario: CP-NA145 RN-05 valores límite del monto en una interbancaria
    Cuando Ana hace una transferencia interbancaria de <monto> al CCI "00219300123456789012"
    Entonces la operación termina con "<resultado>"
    Y el saldo de Ana es "<saldo>"

    Ejemplos:
      | monto  | resultado          | saldo   |
      | 0      | 422 MONTO_INVALIDO | 1500.00 |
      | 0.001  | 422 MONTO_INVALIDO | 1500.00 |
      | 0.01   | 201                | 1498.99 |
      | 500.00 | 201                | 995.00  |
      | 500.01 | 422 MONTO_INVALIDO | 1500.00 |

  @HU-N-08 @CA2 @CP-NA146 @DEF-20
  Escenario: CP-NA146 RN-06 las transferencias interbancarias consumen el límite diario
    Dado que el reloj de Qolqe marca hoy a las "12:00:00"
    Y Diego ya hizo transferencias interbancarias de 500.00, 500.00
    Cuando Diego hace una transferencia interbancaria de 500.00 al CCI "00219300123456789012"
    Entonces la operación termina con "422 LIMITE_DIARIO_EXCEDIDO"
    Y Diego ve usado hoy "1000.00" y disponible "0.00"

  @HU-N-08 @CA3 @CP-NA147
  Escenario: CP-NA147 El movimiento interbancario muestra el CCI enmascarado
    Cuando Ana hace una transferencia interbancaria de 100.00 al CCI "00219300123456789012"
    Entonces la operación termina con "201"
    Y el último movimiento de Ana es "TRANSFERENCIA_ENVIADA" por "-101.50" con contraparte "****************9012"
    Y el último movimiento de Ana tiene la descripción "Transferencia interbancaria a CCI ****************9012"
    Y el último movimiento de Ana registra la comisión "1.50" y el importe "-101.50"

  @HU-N-08 @CA3 @CP-NA148 @tecnico
  Esquema del escenario: CP-NA148 El CCI completo no aparece en ninguna respuesta
    Cuando Ana hace una transferencia interbancaria de 100.00 al CCI "00219300123456789012" con la descripción "<descripcion>"
    Entonces la operación termina con "201"
    Y ninguna respuesta sobre la última transferencia muestra el CCI completo

    Ejemplos:
      | descripcion   |
      |               |
      | Pago alquiler |
