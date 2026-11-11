# language: es
Característica: API de registro de usuarios (núcleo HU-N-01)
  Reglas RN-01 a RN-03 y correo opcional. Cada escenario lleva la historia (@HU-N-01), el criterio (@CA) y el caso (@CP).

  @HU-N-01 @CA1 @CP-NA01
  Escenario: CP-NA01 Registro válido crea la cuenta con saldo S/ 0.00 y límite S/ 2,000.00
    Cuando se registra la cuenta de ejemplo de Lucía
    Entonces la respuesta tiene estado 201
    Y el usuario registrado tiene nombres "Lucía Fernández Rojas", celular "987000111" y correo "lucia.f@correo.pe"
    Y el cuerpo del registro no incluye DNI ni PIN
    Cuando inicia sesión el celular "987000111" con PIN "4826"
    Entonces la respuesta tiene estado 200
    Y el saldo actual es "0.00"
    Y el límite diario actual es "2000.00"
    Y el perfil actual tiene estado "ACTIVA" y DNI "****5678"

  @HU-N-01 @CA1 @CP-NA02
  Esquema del escenario: CP-NA02 El correo es opcional: omitido, vacío, solo espacios o nulo
    Cuando se registra a <celular> con el correo <variante>
    Entonces la respuesta tiene estado 201
    Y el correo del nuevo usuario es nulo

    Ejemplos:
      | celular   | variante |
      | 987000121 | omitido  |
      | 987000122 | vacío    |
      | 987000123 | espacios |
      | 987000124 | nulo     |

  @HU-N-01 @CA1 @CP-NA03
  Esquema del escenario: CP-NA03 Longitud de nombres en el registro
    Cuando se registra a <celular> con nombres "<nombres>"
    Entonces la respuesta tiene estado <estado>

    Ejemplos:
      | celular   | nombres | estado |
      | 987000131 | 1xa     | 422    |
      | 987000132 | 2xa     | 201    |
      | 987000133 | 80xa    | 201    |
      | 987000134 | 81xa    | 422    |

  @HU-N-01 @CA1 @CP-NA04 @DEF-13
  Esquema del escenario: CP-NA04 Nombres que quedan vacíos o de 1 carácter tras recortar
    Cuando se registra a <celular> con nombres "<nombres>"
    Entonces la respuesta tiene estado 422
    Y el código de error es "SOLICITUD_INVALIDA"

    Ejemplos:
      | celular   | nombres       |
      | 987000135 | SOLO_ESPACIOS |
      | 987000136 | ESPACIO_A     |

  @HU-N-01 @CA1 @CP-NA05 @tecnico
  Esquema del escenario: CP-NA05 Cuerpo incompleto, tipos incorrectos o JSON inválido
    Cuando se envía al registro la variante "<variante>"
    Entonces la respuesta tiene estado 422
    Y el código de error es "SOLICITUD_INVALIDA"

    Ejemplos:
      | variante         |
      | cuerpo vacío     |
      | sin dni          |
      | sin nombres      |
      | sin celular      |
      | sin pin          |
      | dni numérico     |
      | pin numérico     |
      | nombres nulo     |
      | json mal formado |
      | formulario       |

  @HU-N-01 @CA1 @CP-NA06 @tecnico
  Escenario: CP-NA06 Los campos que no son del registro se ignoran
    Cuando se registra agregando campos ajenos con celular "987000142"
    Entonces la respuesta tiene estado 201
    Cuando inicia sesión el celular "987000142" con PIN "4826"
    Entonces el saldo actual es "0.00"
    Y el límite diario actual es "2000.00"
    Y el perfil actual tiene estado "ACTIVA" y DNI "****5678"

  @HU-N-01 @CA1 @CP-NA07
  Escenario: CP-NA07 Un DNI ya usado por otra cuenta se acepta (sin unicidad de DNI)
    Cuando se registra a 987000143 con DNI "45678912"
    Entonces la respuesta tiene estado 201

  @HU-N-01 @CA2 @CP-NA08
  Esquema del escenario: CP-NA08 Longitud del DNI
    Cuando se registra a <celular> con DNI "<dni>"
    Entonces la respuesta tiene estado <estado>

    Ejemplos:
      | celular   | dni       | estado |
      | 987000201 | 1234567   | 422    |
      | 987000202 | 12345678  | 201    |
      | 987000203 | 123456789 | 422    |
      | 987000204 | 00000000  | 201    |

  @HU-N-01 @CA2 @CP-NA09
  Esquema del escenario: CP-NA09 DNI con caracteres no numéricos
    Cuando se registra a 987000205 con DNI "<dni>"
    Entonces la respuesta tiene estado 422
    Y el código de error es "DNI_INVALIDO"

    Ejemplos:
      | dni      |
      | 1234567a |
      | 1234 567 |
      | ١٢٣٤٥٦٧٨  |

  @HU-N-01 @CA3 @CP-NA10
  Esquema del escenario: CP-NA10 Formato del celular
    Cuando se registra con el celular "<celular>"
    Entonces la respuesta tiene estado <estado>

    Ejemplos:
      | celular      | estado |
      | 98700011     | 422    |
      | 9870001112   | 422    |
      | 887000111    | 422    |
      | 98700011a    | 422    |
      | +51987000111 | 422    |
      | 900000000    | 201    |
      | 999999999    | 201    |

  @HU-N-01 @CA3 @CP-NA11
  Esquema del escenario: CP-NA11 Celular ya registrado, incluso con la cuenta cerrada
    Cuando se registra con el celular "<celular>"
    Entonces la respuesta tiene estado 409
    Y el código de error es "CELULAR_REGISTRADO"

    Ejemplos:
      | celular   |
      | 987654321 |
      | 934567812 |

  @HU-N-01 @CA3 @CP-NA12 @DEF-14 @tecnico @concurrencia
  Escenario: CP-NA12 Registros simultáneos con el mismo celular
    Cuando 5 usuarios se registran a la vez con el celular "987123123"
    Entonces el registro simultáneo deja 1 creado y 4 en conflicto sin errores 500

  @HU-N-01 @CA4 @CP-NA13
  Esquema del escenario: CP-NA13 Longitud del PIN
    Cuando se registra a <celular> con PIN "<pin>"
    Entonces la respuesta tiene estado <estado>

    Ejemplos:
      | celular   | pin   | estado |
      | 987000301 | 482   | 422    |
      | 987000302 | 4826  | 201    |
      | 987000303 | 48265 | 422    |

  @HU-N-01 @CA4 @CP-NA14
  Esquema del escenario: CP-NA14 Clases de PIN inválidas y válidas cercanas
    Cuando se registra a <celular> con PIN "<pin>"
    Entonces la respuesta tiene estado <estado>

    Ejemplos:
      | celular   | pin  | estado |
      | 987000310 | 12a4 | 422    |
      | 987000311 | 0000 | 422    |
      | 987000312 | 9999 | 422    |
      | 987000313 | 0123 | 422    |
      | 987000314 | 6789 | 422    |
      | 987000315 | 1235 | 201    |
      | 987000316 | 1212 | 201    |
      | 987000317 | 2580 | 201    |

  @HU-N-01 @CA4 @CP-NA15 @DEF-12
  Esquema del escenario: CP-NA15 Se acepta un PIN con secuencia descendente
    Cuando se registra a <celular> con PIN "<pin>"
    Entonces la respuesta tiene estado 422
    Y el código de error es "PIN_INVALIDO"

    Ejemplos:
      | celular   | pin  |
      | 987000330 | 4321 |
      | 987000331 | 9876 |
      | 987000332 | 3210 |

  @HU-N-01 @CA5 @CP-NA16
  Esquema del escenario: CP-NA16 Formato del correo
    Cuando se registra a <celular> con correo "<correo>"
    Entonces la respuesta tiene estado 422
    Y el código de error es "CORREO_INVALIDO"

    Ejemplos:
      | celular   | correo                |
      | 987000401 | mal                   |
      | 987000402 | a@b                   |
      | 987000403 | a@b.c                 |
      | 987000404 | ana@                  |
      | 987000405 | @correo.pe            |

  @HU-N-01 @CA5 @CP-NA17
  Esquema del escenario: CP-NA17 Longitud máxima del correo
    Cuando se registra a <celular> con un correo de <largo> caracteres
    Entonces la respuesta tiene estado <estado>

    Ejemplos:
      | celular   | largo | estado |
      | 987000411 | 100   | 201    |
      | 987000412 | 101   | 422    |

  @HU-N-01 @CA5 @CP-NA18
  Esquema del escenario: CP-NA18 Correo ya usado, sin distinguir mayúsculas
    Cuando se registra a <celular> con correo "<correo>"
    Entonces la respuesta tiene estado <estado>
    Y el código de error es "<codigo>"

    Ejemplos:
      | celular   | correo                | estado | codigo            |
      | 987000420 | ANA.TORRES@CORREO.PE  | 409    | CORREO_REGISTRADO |

  @HU-N-01 @CA5 @CP-NA75
  Escenario: CP-NA75 El correo de una cuenta cerrada queda libre
    Cuando se registra a 987000421 con correo "fabian.rojas@correo.pe"
    Entonces la respuesta tiene estado 201

  @HU-N-01 @CA5 @CP-NA19
  Esquema del escenario: CP-NA19 Orden de los errores cuando fallan varios datos
    Cuando se registra con dni "<dni>", celular "<celular>", pin "<pin>" y correo "<correo>"
    Entonces la respuesta tiene estado <estado>
    Y el código de error es "<codigo>"

    Ejemplos:
      | dni      | celular   | pin  | correo               | estado | codigo             |
      | 1        | 1         | 1    | -                    | 422    | DNI_INVALIDO       |
      | 12345678 | 987000501 | 1111 | mal                  | 422    | PIN_INVALIDO       |
      | 12345678 | 987654321 | 4826 | mal                  | 422    | CORREO_INVALIDO    |
      | 12345678 | 987654321 | 4826 | ana.torres@correo.pe | 409    | CELULAR_REGISTRADO |

  @HU-N-01 @CA5 @CP-NA20 @DEF-15 @tecnico @concurrencia
  Escenario: CP-NA20 Registros simultáneos con el mismo correo
    Cuando 5 usuarios se registran a la vez con el correo "mismo@correo.pe"
    Entonces el registro simultáneo deja 1 creado y 4 en conflicto sin errores 500

  @HU-N-01 @CA6 @CP-NA21
  Escenario: CP-NA21 El registro envía un SMS de bienvenida
    Cuando se registra con el celular "987000111"
    Entonces la respuesta tiene estado 201
    Y "987000111" tiene 1 mensajes SMS
    Y "987000111" recibió un SMS que contiene "Bienvenido a Qolqe"

  @HU-N-01 @CA6 @CP-NA22
  Escenario: CP-NA22 Un registro rechazado no envía SMS
    Cuando se registra a 987000141 con PIN "1111"
    Entonces la respuesta tiene estado 422
    Y "987000141" tiene 0 mensajes SMS
    Cuando se registra con el celular "987654321"
    Entonces la respuesta tiene estado 409
    Y "987654321" tiene 0 mensajes SMS
