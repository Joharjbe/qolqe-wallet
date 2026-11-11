# language: es
Característica: API de saldo, perfil y edición (núcleo HU-N-04 y HU-N-05)
  Lectura del saldo y el perfil (DNI enmascarado, moneda PEN), autenticación y edición de nombres y correo.

  @HU-N-04 @CA1 @CP-NA52
  Escenario: CP-NA52 Consultar mi saldo
    Dado que Ana inició sesión
    Cuando Ana consulta su saldo
    Entonces la respuesta tiene estado 200
    Y el saldo consultado es "1500.00"
    Y la moneda consultada es "PEN"
    Y el saldo consultado cumple el formato de centavos

  @HU-N-04 @CA1 @CP-NA53
  Escenario: CP-NA53 El saldo y su fecha cambian con cada operación
    Dado que Bruno inició sesión
    Y que Ana inició sesión
    Cuando el reloj se adelanta 10 minutos
    Y Bruno transfiere 10.50 soles a Ana
    Entonces la respuesta tiene estado 201
    Y el saldo de Bruno es "789.50"
    Y el saldo de Ana es "1510.50"

  @HU-N-04 @CA1 @CP-NA54
  Esquema del escenario: CP-NA54 Formato del saldo en los bordes
    Dado que se fija el saldo de Bruno en "<saldo>"
    Y que Bruno inició sesión
    Cuando Bruno consulta su saldo
    Entonces el saldo consultado es "<esperado>"

    Ejemplos:
      | saldo     | esperado  |
      | 0         | 0.00      |
      | 0.05      | 0.05      |
      | 0.10      | 0.10      |
      | 123456.78 | 123456.78 |

  @HU-N-04 @CA1 @CP-NA55 @tecnico
  Escenario: CP-NA55 Cada token ve solo su propio saldo
    Dado que Ana inició sesión
    Y que Bruno inició sesión
    Entonces el saldo de Ana es "1500.00"
    Y el saldo de Bruno es "800.00"
    Cuando con el token de Bruno se consulta la cuenta 1
    Entonces la respuesta tiene estado 404

  @HU-N-04 @CA2 @CP-NA56
  Escenario: CP-NA56 Consultar mi perfil con el DNI enmascarado
    Dado que Ana inició sesión
    Cuando Ana consulta su perfil
    Entonces la respuesta tiene estado 200
    Y el perfil consultado muestra nombres "Ana Torres Quispe", celular "987654321", correo "ana.torres@correo.pe", DNI "****8912" y estado "ACTIVA"
    Y el DNI del perfil cumple el enmascarado y no revela "45678912"

  @HU-N-04 @CA2 @CP-NA57
  Esquema del escenario: CP-NA57 Perfil de un usuario sin correo
    Cuando se consulta el perfil del caso "<caso>"
    Entonces la respuesta tiene estado 200
    Y el correo del perfil actual es nulo
    Y el DNI del perfil actual es "<dni>"

    Ejemplos:
      | caso              | dni      |
      | usuario de carga  | ****0001 |
      | recién registrado | ****0000 |

  @HU-N-04 @CA3 @CP-NA58 @tecnico
  Esquema del escenario: CP-NA58 Credenciales ausentes o inválidas
    Cuando se consulta /api/cuentas/me con la credencial "<variante>"
    Entonces la respuesta tiene estado 401
    Y el código de error es "NO_AUTENTICADO"
    Y el mensaje de error es "<mensaje>"

    Ejemplos:
      | variante         | mensaje                         |
      | sin token        | Falta el token de autenticación |
      | token básico     | Falta el token de autenticación |
      | bearer sin valor | Falta el token de autenticación |
      | bearer basura    | Token inválido                  |
      | firma alterada   | Token inválido                  |
      | otra clave       | Token inválido                  |
      | algoritmo none   | Token inválido                  |

  @HU-N-04 @CA3 @CP-NA59 @tecnico
  Esquema del escenario: CP-NA59 Token vencido o de una sesión cerrada
    Cuando se consulta el saldo tras "<variante>"
    Entonces la respuesta tiene estado 401
    Y el mensaje de error es "<mensaje>"

    Ejemplos:
      | variante       | mensaje              |
      | token vencido  | El token expiró      |
      | sesión cerrada | La sesión fue cerrada |

  @HU-N-04 @CA3 @CP-NA60 @DEF-17 @tecnico
  Escenario: CP-NA60 Un token forjado con la clave por defecto y sub no numérico
    Cuando se consulta el perfil con un token forjado con sub "1"
    Entonces la respuesta tiene estado 401
    Cuando se consulta el perfil con un token forjado con sub "abc"
    Entonces la respuesta tiene estado 401

  @HU-N-04 @CA3 @CP-NA61 @tecnico
  Escenario: CP-NA61 Editar el perfil sin token no cambia nada
    Cuando se edita el perfil sin token
    Entonces la respuesta tiene estado 401
    Y el código de error es "NO_AUTENTICADO"
    Y el nombre guardado de Ana sigue siendo "Ana Torres Quispe"

  @HU-N-05 @CA1 @CP-NA62
  Esquema del escenario: CP-NA62 Longitud de nombres al editar
    Dado que Ana inició sesión
    Cuando Ana edita sus nombres a "<nombres>"
    Entonces la respuesta tiene estado <estado>
    Y el perfil de Ana guardó nombres "<guardado>"

    Ejemplos:
      | nombres           | estado | guardado         |
      | A                 | 422    | SIN_CAMBIO       |
      | Ab                | 200    | Ab               |
      | 80xa              | 200    | 80xa             |
      | 81xa              | 422    | SIN_CAMBIO       |
      | 80xa_CON_ESPACIOS | 200    | 80xa             |
      | ANA_CON_ESPACIOS  | 200    | Ana Lucía Torres |

  @HU-N-05 @CA1 @CP-NA63
  Esquema del escenario: CP-NA63 Nombres vacíos o nulos al editar
    Dado que Ana inició sesión
    Cuando Ana edita sus nombres a "<nombres>"
    Entonces la respuesta tiene estado 422
    Y el código de error es "PERFIL_INVALIDO"

    Ejemplos:
      | nombres       |
      | SOLO_ESPACIOS |
      | ESPACIO_A     |
      | NULO          |

  @HU-N-05 @CA1 @CP-NA64 @tecnico
  Esquema del escenario: CP-NA64 Tipos incorrectos al editar
    Dado que Ana inició sesión
    Cuando Ana edita el perfil con la variante "<variante>"
    Entonces la respuesta tiene estado 422
    Y el código de error es "SOLICITUD_INVALIDA"

    Ejemplos:
      | variante         |
      | nombres numérico |
      | correo numérico  |
      | cuerpo lista     |
      | json mal formado |

  @HU-N-05 @CA1 @CP-NA65
  Esquema del escenario: CP-NA65 Formato inválido del correo al editar
    Dado que Ana inició sesión
    Cuando Ana edita su correo a "<correo>"
    Entonces la respuesta tiene estado 422
    Y el código de error es "CORREO_INVALIDO"

    Ejemplos:
      | correo     |
      | ana@       |
      | a@b.c      |
      | @correo.pe |

  @HU-N-05 @CA1 @CP-NA66
  Escenario: CP-NA66 Unicidad del correo entre cuentas activas al editar
    Dado que Ana inició sesión
    Cuando Ana edita su correo a "BRUNO.DIAZ@correo.pe"
    Entonces la respuesta tiene estado 409
    Y el código de error es "CORREO_REGISTRADO"
    Y el correo guardado de Ana es "ana.torres@correo.pe"
    Cuando Ana edita su correo a "fabian.rojas@correo.pe"
    Entonces la respuesta tiene estado 200
    Cuando Ana edita su correo a "ANA.TORRES@correo.pe"
    Entonces la respuesta tiene estado 200
    Y el correo guardado de Ana es "ana.torres@correo.pe"

  @HU-N-05 @CA1 @CP-NA67
  Escenario: CP-NA67 Quitar el correo lo libera para otra cuenta
    Dado que Ana inició sesión
    Y que Bruno inició sesión
    Cuando Ana vacía su correo
    Entonces la respuesta tiene estado 200
    Y el correo guardado de Ana es "null"
    Cuando Bruno edita su correo a "ana.torres@correo.pe"
    Entonces la respuesta tiene estado 200
    Cuando Ana edita su correo a "ana.torres@correo.pe"
    Entonces la respuesta tiene estado 409
    Y el código de error es "CORREO_REGISTRADO"

  @HU-N-05 @CA1 @CP-NA68
  Esquema del escenario: CP-NA68 Un error al editar no deja cambios a medias
    Dado que Ana inició sesión
    Cuando Ana edita el perfil con nombres "<nombres>" y correo "<correo>"
    Entonces la respuesta tiene estado 422
    Y el código de error es "<codigo>"
    Y el perfil de Ana no cambió respecto de nombres "Ana Torres Quispe" y correo "ana.torres@correo.pe"

    Ejemplos:
      | nombres        | correo         | codigo          |
      | Cambio Parcial | mal            | CORREO_INVALIDO |
      | A              | otro@correo.pe | PERFIL_INVALIDO |

  # CP-NA69 (DEF-15 en edición simultánea) NO se automatiza: la carrera de 10 ediciones no es
  # 100 % reproducible (en ~1 de 25 corridas el proceso se serializa y da el resultado correcto,
  # lo que rompería el xfail estricto). Se documenta como evidencia manual en el informe. El mismo
  # DEF-15 queda automatizado de forma estable en el registro simultáneo (CP-NA20).

  @HU-N-05 @CA2 @CP-NA70
  Escenario: CP-NA70 El DNI y el celular enviados junto con nombres se ignoran
    Dado que Ana inició sesión
    Cuando Ana edita el perfil enviando DNI "11111111", celular "999999999" y nombres "Ana T"
    Entonces la respuesta tiene estado 200
    Y el perfil de Ana conserva DNI "****8912" y celular "987654321"
    Y el correo guardado de Ana es "ana.torres@correo.pe"
    Cuando ingresa con el celular "987654321" y PIN "4826"
    Entonces la respuesta tiene estado 200
    Cuando ingresa con el celular "999999999" y PIN "4826"
    Entonces la respuesta tiene estado 401
    Y el código de error es "CREDENCIALES_INVALIDAS"

  @HU-N-05 @CA2 @CP-NA71 @tecnico
  Escenario: CP-NA71 Enviar solo DNI y celular no cambia nada ni avisa
    Dado que Ana inició sesión
    Cuando Ana edita el perfil enviando solo DNI "11111111" y celular "999999999"
    Entonces la respuesta tiene estado 200
    Y el perfil de Ana conserva DNI "****8912" y celular "987654321"
    Y "987654321" tiene 0 mensajes SMS

  @HU-N-05 @CA3 @CP-NA72
  Escenario: CP-NA72 Cambiar el correo envía un SMS con el correo nuevo
    Dado que Ana inició sesión
    Cuando Ana edita su correo a "ANA.NUEVA@Correo.PE"
    Entonces la respuesta tiene estado 200
    Y el correo guardado de Ana es "ana.nueva@correo.pe"
    Y "987654321" tiene 1 mensajes SMS
    Y "987654321" recibió un SMS que contiene "se cambió a ana.nueva@correo.pe"

  @HU-N-05 @CA3 @CP-NA73
  Esquema del escenario: CP-NA73 Sin cambio del correo guardado no hay SMS
    Dado que Ana inició sesión
    Cuando Ana envía el cambio de perfil "<variante>"
    Entonces "987654321" tiene 0 mensajes SMS

    Ejemplos:
      | variante               |
      | solo nombres           |
      | mismo correo otra caja |
      | correo de otro         |
      | correo inválido        |

  @HU-N-05 @CA3 @CP-NA74
  Esquema del escenario: CP-NA74 Quitar o agregar correo también avisa
    Cuando se cambia el correo del caso "<caso>"
    Entonces la respuesta tiene estado 200
    Y "<celular>" tiene 1 mensajes SMS
    Y "<celular>" recibió un SMS que contiene "<texto>"

    Ejemplos:
      | caso                          | celular   | texto                 |
      | Ana quita el correo           | 987654321 | se cambió a (sin correo) |
      | usuario de carga agrega correo | 900000001 | se cambió a carga1@correo.pe |
