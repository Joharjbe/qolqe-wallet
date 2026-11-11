# language: es
Característica: API del núcleo: simular la comisión (HU-N-09)
  GET /api/transferencias/comision calcula monto, comisión y total con la regla RN-09 sin realizar ninguna operación.

  @HU-N-09 @CA1 @CP-NA149
  Esquema del escenario: CP-NA149 Simular una transferencia Qolqe no tiene comisión
    Cuando Ana simula una transferencia de "<monto>" de tipo "<tipo>"
    Entonces la operación termina con "200"
    Y la simulación muestra monto "<registrado>", comisión "0.00" y total "<registrado>"

    Ejemplos:
      | monto | tipo          | registrado |
      | 100   | QOLQE         | 100.00     |
      | 100   | (por defecto) | 100.00     |
      | 0.01  | QOLQE         | 0.01       |
      | 500   | QOLQE         | 500.00     |

  @HU-N-09 @CA1 @CP-NA150
  Esquema del escenario: CP-NA150 Simular una interbancaria en el mínimo, la zona proporcional y el tope
    Cuando Ana simula una transferencia de "<monto>" de tipo "INTERBANCARIA"
    Entonces la operación termina con "200"
    Y la simulación muestra monto "<registrado>", comisión "<comision>" y total "<total>"

    Ejemplos:
      | clase        | monto  | registrado | comision | total  |
      | mínimo       | 0.01   | 0.01       | 1.00     | 1.01   |
      | mínimo       | 66.99  | 66.99      | 1.00     | 67.99  |
      | proporcional | 67.01  | 67.01      | 1.01     | 68.02  |
      | proporcional | 70     | 70.00      | 1.05     | 71.05  |
      | proporcional | 100    | 100.00     | 1.50     | 101.50 |
      | proporcional | 100.5  | 100.50     | 1.51     | 102.01 |
      | proporcional | 332.99 | 332.99     | 4.99     | 337.98 |
      | tope         | 333.33 | 333.33     | 5.00     | 338.33 |
      | tope         | 333.34 | 333.34     | 5.00     | 338.34 |
      | tope         | 500    | 500.00     | 5.00     | 505.00 |
      | científica   | 1e2    | 100.00     | 1.50     | 101.50 |

  @HU-N-09 @CA1 @CP-NA151 @DEF-23
  Esquema del escenario: CP-NA151 La simulación usa redondeo comercial cuando el tercer decimal es 5
    Cuando Ana simula una transferencia de "<monto>" de tipo "INTERBANCARIA"
    Entonces la operación termina con "200"
    Y la simulación muestra monto "<registrado>", comisión "<comision>" y total "<total>"

    Ejemplos:
      | monto | registrado | comision | total  |
      | 67    | 67.00      | 1.01     | 68.01  |
      | 71    | 71.00      | 1.07     | 72.07  |
      | 299   | 299.00     | 4.49     | 303.49 |

  @HU-N-09 @CA1 @CP-NA152
  Esquema del escenario: CP-NA152 La simulación aplica RN-05 al monto
    Cuando Ana simula una transferencia de "<monto>" de tipo "<tipo>"
    Entonces la operación termina con "422 MONTO_INVALIDO"
    Y el detalle del error dice "<detalle>"

    Ejemplos:
      | monto   | tipo          | detalle                                              |
      | 0       | INTERBANCARIA | El monto debe ser mayor a cero                       |
      | -1      | QOLQE         | El monto debe ser mayor a cero                       |
      | 0.001   | INTERBANCARIA | El monto admite como máximo 2 decimales              |
      | 100.000 | (por defecto) | El monto admite como máximo 2 decimales              |
      | 500.01  | INTERBANCARIA | El monto supera el límite por operación de S/ 500.00 |

  @HU-N-09 @CA1 @CP-NA153 @tecnico
  Esquema del escenario: CP-NA153 Parámetros ausentes o de tipo inválido en la simulación
    Cuando Ana simula una transferencia de "<monto>" de tipo "<tipo>"
    Entonces la operación termina con "422 SOLICITUD_INVALIDA"
    Y el error de validación está en "<campo>"

    Ejemplos:
      | monto       | tipo          | campo       |
      | abc         | INTERBANCARIA | query.monto |
      |             | INTERBANCARIA | query.monto |
      | NaN         | INTERBANCARIA | query.monto |
      | Infinity    | (por defecto) | query.monto |
      | (sin monto) | INTERBANCARIA | query.monto |
      | 100         | OTRO          | query.tipo  |
      | 100         | qolqe         | query.tipo  |

  @HU-N-09 @CA1 @CP-NA154 @tecnico
  Escenario: CP-NA154 Simular la comisión no mueve dinero ni registra operaciones
    Dado que se anotan el saldo, los movimientos, el límite usado y los SMS de Ana
    Cuando Ana simula una transferencia de "100" de tipo "INTERBANCARIA" 3 veces
    Entonces las 3 simulaciones responden lo mismo
    Y el saldo, los movimientos, el límite usado y los SMS de Ana no cambiaron

  @HU-N-09 @CA1 @CP-NA155 @tecnico
  Esquema del escenario: CP-NA155 La simulación coincide con lo que cobra la transferencia
    Cuando Ana simula una transferencia de "<monto>" de tipo "INTERBANCARIA"
    Y Ana hace una transferencia interbancaria de <monto> al CCI "00219300123456789012"
    Entonces la operación termina con "201"
    Y la comisión y el total del comprobante coinciden con la simulación

    Ejemplos:
      | monto  |
      | 0.01   |
      | 67.00  |
      | 100.00 |
      | 299.00 |
      | 500.00 |

  @HU-N-09 @CA1 @CP-NA156 @tecnico
  Esquema del escenario: CP-NA156 La simulación exige un token vigente y solo acepta GET
    Cuando llega un pedido <metodo> a "<ruta>" con <credencial>
    Entonces la operación termina con "<resultado>"

    Ejemplos:
      | metodo | ruta                                                      | credencial                      | resultado          |
      | GET    | /api/transferencias/comision?monto=100&tipo=INTERBANCARIA | ningún token                    | 401 NO_AUTENTICADO |
      | GET    | /api/transferencias/comision                              | ningún token                    | 401 NO_AUTENTICADO |
      | GET    | /api/transferencias/comision?monto=100                    | un token inválido               | 401 NO_AUTENTICADO |
      | GET    | /api/transferencias/comision?monto=100                    | un token firmado con otra clave | 401 NO_AUTENTICADO |
      | GET    | /api/transferencias/comision?monto=100                    | el token vencido de Ana         | 401 NO_AUTENTICADO |
      | POST   | /api/transferencias/comision?monto=100                    | el token de Ana                 | 405 ERROR_HTTP     |
