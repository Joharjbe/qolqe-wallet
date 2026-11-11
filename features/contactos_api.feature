# language: es
Característica: API de contactos (G4)
  Reglas R-G4-01 a R-G4-03. Cada escenario lleva la historia (@HU), el criterio (@CA) y el caso (@CP).

  @HU-G4-01 @CA1 @CP-A01
  Escenario: CP-A01 Agregar un contacto válido normaliza el alias
    Dado que Diego inició sesión
    Cuando agrega el contacto "912345678" con alias "  Bruno Trabajo  "
    Entonces la respuesta tiene estado 201
    Y el contacto creado tiene alias "Bruno Trabajo" y nombre enmascarado "Bruno D."

  @HU-G4-01 @CA1 @CP-A02
  Esquema del escenario: CP-A02 Rechazar un celular que no puede ser contacto
    Dado que <usuario> inició sesión
    Cuando agrega el contacto "<celular>" con alias "Alias Valido"
    Entonces la respuesta tiene estado <estado>
    Y el código de error es "<codigo>"

    Ejemplos:
      | usuario | celular    | estado | codigo                |
      | Diego   | 12345678   | 422    | CELULAR_INVALIDO      |
      | Diego   | 812345678  | 422    | CELULAR_INVALIDO      |
      | Diego   | 998877665  | 422    | CONTACTO_PROPIO       |
      | Diego   | 900000999  | 404    | CELULAR_NO_REGISTRADO |
      | Diego   | 934567812  | 404    | CELULAR_NO_REGISTRADO |
      | Ana     | 912345678  | 409    | CONTACTO_EXISTENTE    |

  @HU-G4-01 @CA1 @CP-A03
  Esquema del escenario: CP-A03 Valores límite y clases del alias
    Dado que Diego inició sesión
    Cuando agrega el contacto "912345678" con alias "<alias>"
    Entonces la respuesta tiene estado <estado>

    Ejemplos:
      | alias                 | estado |
      | Ab                    | 422    |
      | Abc                   | 201    |
      | Abcdefghijklmnopqrst  | 201    |
      | Abcdefghijklmnopqrstu | 422    |
      | José 2                | 201    |
      | Bruno_01              | 422    |

  @HU-G4-01 @CA1 @CP-A04 @DEF-01
  Escenario: CP-A04 El alias admite la letra ñ
    Dado que Diego inició sesión
    Cuando agrega el contacto "912345678" con alias "Peña"
    Entonces la respuesta tiene estado 201

  @HU-G4-01 @CA1 @CP-A05
  Escenario: CP-A05 El alias es único sin distinguir mayúsculas
    Dado que Ana inició sesión
    Cuando agrega el contacto "998877665" con alias "BRUNO"
    Entonces la respuesta tiene estado 409
    Y el código de error es "ALIAS_DUPLICADO"

  @HU-G4-01 @CA1 @CP-A06 @DEF-02
  Escenario: CP-A06 El alias duplicado se detecta tras quitar los espacios
    Dado que Ana inició sesión
    Cuando agrega el contacto "998877665" con alias " Bruno "
    Entonces la respuesta tiene estado 409
    Y el código de error es "ALIAS_DUPLICADO"

  @HU-G4-01 @CA1 @CP-A07
  Escenario: CP-A07 Límite de 15 contactos
    Dado que Diego inició sesión
    Y Diego tiene 15 contactos en total
    Cuando agrega el contacto "900000100" con alias "Uno de mas"
    Entonces la respuesta tiene estado 422
    Y el código de error es "LIMITE_CONTACTOS"

  @HU-G4-02 @CA1 @CP-A08
  Escenario: CP-A08 Favoritos primero, por alias y 10 por página
    Dado que Diego inició sesión
    Y Diego tiene 12 contactos en total
    Y el contacto "Zeta 05" es favorito
    Cuando consulta sus contactos
    Entonces la respuesta tiene estado 200
    Y la página tiene 10 contactos de un total de 12
    Y el primer contacto es "Zeta 05"
    Y los demás contactos están ordenados por alias

  @HU-G4-02 @CA2 @CP-A09
  Esquema del escenario: CP-A09 Buscar sin distinguir mayúsculas ni tildes
    Dado que Diego inició sesión
    Y Diego tiene el contacto "912345678" con alias "José Pérez"
    Cuando busca contactos con "<busqueda>"
    Entonces la búsqueda encuentra <total> contactos

    Ejemplos:
      | busqueda | total |
      | jose     | 1     |
      | JOSÉ     | 1     |
      | perez    | 1     |
      | xyz      | 0     |

  @HU-G4-02 @CA3 @CP-A10
  Escenario: CP-A10 Cada contacto informa alias, nombre enmascarado, celular y favorito
    Dado que Ana inició sesión
    Cuando consulta sus contactos
    Entonces el primer contacto tiene alias "Bruno", nombre "Bruno D.", celular "912345678" y favorito

  @HU-G4-03 @CA1 @CP-A11
  Escenario: CP-A11 Editar alias y favorito, sin compararlo consigo mismo
    Dado que Ana inició sesión
    Cuando edita el contacto "Prima Carla" con alias "PRIMA carla" y favorito
    Entonces la respuesta tiene estado 200
    Y el contacto creado tiene alias "PRIMA carla" y nombre enmascarado "Carla R."

  @HU-G4-03 @CA1 @CP-A12
  Escenario: CP-A12 Límite de 5 favoritos
    Dado que Diego inició sesión
    Y Diego tiene 6 contactos en total
    Y Diego marcó 5 contactos como favoritos
    Cuando marca como favorito el último contacto
    Entonces la respuesta tiene estado 422
    Y el código de error es "LIMITE_FAVORITOS"

  @HU-G4-03 @CA1 @CP-A13
  Escenario: CP-A13 Editar con el alias de otro contacto
    Dado que Ana inició sesión
    Cuando edita el contacto "Prima Carla" con alias "bruno"
    Entonces la respuesta tiene estado 409
    Y el código de error es "ALIAS_DUPLICADO"

  @HU-G4-04 @CA1 @CP-A14
  Escenario: CP-A14 Eliminar un contacto conserva las transferencias
    Dado que Diego inició sesión
    Y Diego tiene el contacto "912345678" con alias "Bruno"
    Y Diego transfirió 10.00 al contacto "Bruno"
    Cuando elimina el contacto "Bruno"
    Entonces la respuesta tiene estado 204
    Y el contacto "Bruno" ya no aparece
    Y la transferencia sigue en sus movimientos

  @HU-G4-04 @CA2 @CP-A15
  Escenario: CP-A15 No se elimina un contacto con solicitudes pendientes
    Dado que Ana inició sesión
    Cuando elimina el contacto "Bruno"
    Entonces la respuesta tiene estado 409
    Y el código de error es "SOLICITUDES_PENDIENTES"

  @HU-G4-04 @CA2 @CP-A16
  Escenario: CP-A16 Una solicitud vencida no impide eliminar el contacto
    Dado que Ana inició sesión
    Cuando elimina el contacto "Prima Carla"
    Entonces la respuesta tiene estado 204

  @HU-G4-05 @CA1 @CP-A17
  Escenario: CP-A17 Transferir eligiendo un contacto
    Dado que Ana inició sesión
    Cuando transfiere 100.00 al contacto "Bruno"
    Entonces la respuesta tiene estado 201
    Y el saldo de Ana es "1400.00"
    Y el saldo de Bruno es "900.00"

  @HU-G4-05 @CA1 @CP-A18 @DEF-04
  Escenario: CP-A18 Transferir a un contacto con cuenta cerrada
    Dado que Diego inició sesión
    Cuando transfiere 10.00 al contacto "Fabián"
    Entonces la respuesta tiene estado 422
    Y el código de error es "DESTINO_INACTIVO"

  @HU-G4-02 @CA1 @CP-T01
  Escenario: CP-T01 Sin token no se accede a los contactos
    Cuando se consultan los contactos sin token
    Entonces la respuesta tiene estado 401
    Y el código de error es "NO_AUTENTICADO"

  @HU-G4-03 @HU-G4-04 @CA1 @CP-T02
  Esquema del escenario: CP-T02 El contacto de otro usuario responde como inexistente
    Dado que Carla inició sesión
    Cuando intenta <accion> el contacto "Bruno" de Ana
    Entonces la respuesta tiene estado 404
    Y el código de error es "CONTACTO_NO_ENCONTRADO"

    Ejemplos:
      | accion   |
      | editar   |
      | eliminar |

  @HU-G4-01 @CA1 @CP-A40
  Escenario: CP-A40 El contacto agregado queda en la lista con celular, nombre enmascarado y sin favorito
    Dado que Diego inició sesión
    Cuando agrega el contacto "912345678" con alias "Bruno Nuevo"
    Entonces la respuesta tiene estado 201
    Y el contacto devuelto tiene nombre "Bruno D.", celular "912345678" y no es favorito
    Y la lista de contactos de Diego queda "Bruno Nuevo, Fabián"

  @HU-G4-01 @CA1 @CP-A77
  Esquema del escenario: CP-A77 Un alta rechazada no agrega ningún contacto
    Dado que Diego inició sesión
    Cuando agrega el contacto "<celular>" con alias "<alias>"
    Entonces la respuesta tiene estado <estado>
    Y el código de error es "<codigo>"
    Y la lista de contactos de Diego queda "Fabián"

    Ejemplos:
      | celular   | alias      | estado | codigo                |
      | 900000999 | Nadie Aqui | 404    | CELULAR_NO_REGISTRADO |
      | 12345678  | Corto      | 422    | CELULAR_INVALIDO      |
      | 998877665 | Yo Mismo   | 422    | CONTACTO_PROPIO       |
      | 912345678 | Br         | 422    | ALIAS_INVALIDO        |
      | 912345678 | FABIÁN     | 409    | ALIAS_DUPLICADO       |

  @HU-G4-01 @CA1 @CP-A41
  Esquema del escenario: CP-A41 Clases válidas del alias después de quitar los espacios
    Dado que Diego inició sesión
    Cuando Diego envía el alta de contacto con celular "912345678" y alias <alias>
    Entonces la respuesta tiene estado 201
    Y el contacto creado tiene alias "<guardado>" y nombre enmascarado "Bruno D."

    Ejemplos:
      | alias                      | guardado             |
      | "  Abcdefghijklmnopqrst  " | Abcdefghijklmnopqrst |
      | " Abc "                    | Abc                  |
      | "123"                      | 123                  |
      | "ÁNGEL Ü"                  | ÁNGEL Ü              |

  @HU-G4-01 @CA1 @CP-A78
  Esquema del escenario: CP-A78 Clases inválidas del alias informan ALIAS_INVALIDO y no agregan nada
    Dado que Diego inició sesión
    Cuando Diego envía el alta de contacto con celular "912345678" y alias <alias>
    Entonces la respuesta tiene estado 422
    Y el código de error es "ALIAS_INVALIDO"
    Y la lista de contactos de Diego queda "Fabián"

    Ejemplos:
      | alias                   |
      | "Ab"                    |
      | "Abcdefghijklmnopqrstu" |
      | "  Ab  "                |
      | "     "                 |
      | ""                      |
      | "Bruno_01"              |
      | "Bru\tno"               |
      | "José-Luis"             |

  @HU-G4-01 @CA1 @CP-A79 @DEF-01
  Escenario: CP-A79 El alias admite la letra Ñ mayúscula
    Dado que Diego inició sesión
    Cuando Diego envía el alta de contacto con celular "912345678" y alias "ÑANDÚ"
    Entonces la respuesta tiene estado 201

  @HU-G4-01 @CA1 @CP-A42
  Esquema del escenario: CP-A42 Particiones inválidas del celular
    Dado que Diego inició sesión
    Cuando Diego envía el alta de contacto con celular <celular> y alias "Alias Valido"
    Entonces la respuesta tiene estado 422
    Y el código de error es "CELULAR_INVALIDO"
    Y la lista de contactos de Diego queda "Fabián"

    Ejemplos:
      | celular        |
      | "9123456789"   |
      | "91234567a"    |
      | " 912345678"   |
      | "912345678 "   |
      | ""             |
      | "+51912345678" |

  @HU-G4-01 @CA1 @CP-A81
  Escenario: CP-A81 Una cuenta bloqueada pero activa sí puede ser contacto
    Dado que Diego inició sesión
    Cuando agrega el contacto "923456789" con alias "Elena"
    Entonces la respuesta tiene estado 201
    Y el contacto devuelto tiene nombre "Elena V.", celular "923456789" y no es favorito

  @HU-G4-01 @HU-G4-04 @CA1 @CP-A43
  Escenario: CP-A43 Eliminar un contacto libera el cupo de 15
    Dado que Diego inició sesión
    Y Diego tiene 15 contactos en total
    Y Diego eliminó su contacto "Zeta 05"
    Cuando agrega el contacto "912345678" con alias "Bruno"
    Entonces la respuesta tiene estado 201
    Y Diego queda con 15 contactos

  @HU-G4-02 @CA1 @CP-A44
  Esquema del escenario: CP-A44 Valores límite de la paginación de 10 contactos
    Dado que Diego inició sesión
    Y Diego tiene <total> contactos en total
    Cuando Diego consulta la página <pagina> de sus contactos
    Entonces la respuesta tiene estado 200
    Y la página <pagina> trae <cantidad> contactos con total <total> y total_paginas <paginas>

    Ejemplos:
      | total | pagina | cantidad | paginas |
      | 10    | 1      | 10       | 1       |
      | 11    | 1      | 10       | 2       |
      | 11    | 2      | 1        | 2       |
      | 12    | 2      | 2        | 2       |
      | 15    | 2      | 5        | 2       |

  @HU-G4-02 @CA1 @CP-A45
  Escenario: CP-A45 Una página fuera de rango responde vacía (comportamiento no especificado)
    Dado que Diego inició sesión
    Y Diego tiene 12 contactos en total
    Cuando Diego consulta la página 3 de sus contactos
    Entonces la respuesta tiene estado 200
    Y la página 3 trae 0 contactos con total 12 y total_paginas 2

  @HU-G4-02 @CA1 @CP-A82
  Escenario: CP-A82 Un usuario sin contactos recibe una página vacía
    Dado que el usuario de carga "900000001" ingresó a Qolqe
    Cuando consulta sus contactos
    Entonces la respuesta tiene estado 200
    Y la página 1 trae 0 contactos con total 0 y total_paginas 1

  @HU-G4-02 @CA1 @CP-A46
  Escenario: CP-A46 Varios favoritos van primero y todos se ordenan por alias sin distinguir mayúsculas
    Dado que Diego inició sesión
    Y Diego tiene el contacto "912345678" con alias "zoila"
    Y Diego tiene el contacto "987654321" con alias "Beto"
    Y Diego tiene el contacto "956781234" con alias "carla"
    Y el contacto "zoila" es favorito
    Y el contacto "Beto" es favorito
    Cuando consulta sus contactos
    Entonces los contactos de la página están en el orden "Beto, zoila, carla, Fabián"

  @HU-G4-02 @CA1 @CP-A47 @DEF-27
  Escenario: CP-A47 Los alias que empiezan con tilde se ordenan con su letra
    Dado que Diego inició sesión
    Y Diego tiene el contacto "956781234" con alias "Ángel"
    Y Diego tiene el contacto "923456789" con alias "álvaro"
    Y Diego tiene el contacto "987654321" con alias "Beto"
    Cuando consulta sus contactos
    Entonces los contactos de la página están en el orden "álvaro, Ángel, Beto, Fabián"

  @HU-G4-02 @CA2 @CP-A48
  Esquema del escenario: CP-A48 La búsqueda recorta el texto y solo mira el alias
    Dado que Diego inició sesión
    Y Diego tiene el contacto "912345678" con alias "José Pérez"
    Y Diego tiene el contacto "956781234" con alias "Ángel"
    Cuando Diego busca entre sus contactos el texto <texto>
    Entonces la respuesta tiene estado 200
    Y la búsqueda encuentra <total> contactos

    Ejemplos:
      | texto      | total |
      | "  jose  " | 1     |
      | "   "      | 3     |
      | "ÁNGEL"    | 1     |
      | "angel"    | 1     |
      | "Bruno D." | 0     |
      | "912"      | 0     |

  @HU-G4-02 @CA1 @CA2 @CP-A83
  Escenario: CP-A83 La búsqueda también se pagina de 10 en 10
    Dado que Diego inició sesión
    Y Diego tiene 13 contactos en total
    Cuando Diego busca entre sus contactos el texto "zeta" en la página 2
    Entonces la respuesta tiene estado 200
    Y la página 2 trae 2 contactos con total 12 y total_paginas 2

  @HU-G4-02 @CA3 @CP-A49
  Escenario: CP-A49 Un contacto que no es favorito lo informa
    Dado que Ana inició sesión
    Cuando consulta sus contactos
    Entonces el contacto "Prima Carla" de la respuesta tiene nombre "Carla R.", celular "956781234" y no es favorito

  @HU-G4-03 @CA1 @CP-A50
  Escenario: CP-A50 Desmarcar un favorito lo devuelve al orden por alias
    Dado que Ana inició sesión
    Y Ana agregó el contacto "998877665" con alias "Abel"
    Cuando Ana desmarca como favorito su contacto "Bruno"
    Entonces la respuesta tiene estado 200
    Y el contacto devuelto tiene nombre "Bruno D.", celular "912345678" y no es favorito
    Y la lista de contactos de Ana queda "Abel, Bruno, Prima Carla"

  @HU-G4-03 @CA1 @CP-A51
  Escenario: CP-A51 Volver a marcar un favorito con 5 favoritos no cuenta como uno nuevo
    Dado que Diego inició sesión
    Y Diego tiene 7 contactos en total
    Y Diego marcó 5 contactos como favoritos
    Cuando Diego marca como favorito su contacto "Zeta 02"
    Entonces la respuesta tiene estado 200
    Y Diego queda con 5 favoritos

  @HU-G4-03 @CA1 @CP-A84
  Escenario: CP-A84 Desmarcar un favorito libera el cupo para marcar otro
    Dado que Diego inició sesión
    Y Diego tiene 7 contactos en total
    Y Diego marcó 5 contactos como favoritos
    Y Diego desmarcó como favorito su contacto "Zeta 02"
    Cuando Diego marca como favorito su contacto "Zeta 06"
    Entonces la respuesta tiene estado 200
    Y Diego queda con 5 favoritos

  @HU-G4-03 @CA1 @CP-A52
  Esquema del escenario: CP-A52 Solo se actualizan los campos enviados
    Dado que Ana inició sesión
    Cuando Ana modifica su contacto "Bruno" con el cuerpo <cuerpo>
    Entonces la respuesta tiene estado 200
    Y el contacto queda con alias "<alias>" y <favorito>

    Ejemplos:
      | cuerpo                             | alias         | favorito       |
      | {"favorito": false}                | Bruno         | no es favorito |
      | {"alias": "Bruno Oficina"}         | Bruno Oficina | es favorito    |
      | {}                                 | Bruno         | es favorito    |
      | {"alias": null}                    | Bruno         | es favorito    |
      | {"favorito": null}                 | Bruno         | es favorito    |
      | {"alias": null, "favorito": false} | Bruno         | no es favorito |

  @HU-G4-03 @CA1 @CP-A53
  Esquema del escenario: CP-A53 Un alias inválido al editar informa ALIAS_INVALIDO y no cambia el contacto
    Dado que Ana inició sesión
    Cuando Ana modifica su contacto "Prima Carla" con el cuerpo <cuerpo>
    Entonces la respuesta tiene estado 422
    Y el código de error es "ALIAS_INVALIDO"
    Y la lista de contactos de Ana queda "Bruno, Prima Carla"

    Ejemplos:
      | cuerpo                             |
      | {"alias": "Ca"}                    |
      | {"alias": "Abcdefghijklmnopqrstu"} |
      | {"alias": "  Ca  "}                |
      | {"alias": "   "}                   |
      | {"alias": ""}                      |
      | {"alias": "Bruno_01"}              |

  @HU-G4-03 @CA1 @CP-A85
  Esquema del escenario: CP-A85 Un alias válido al editar se guarda sin los espacios de los extremos
    Dado que Ana inició sesión
    Cuando Ana modifica su contacto "Prima Carla" con el cuerpo <cuerpo>
    Entonces la respuesta tiene estado 200
    Y el contacto queda con alias "<guardado>" y no es favorito

    Ejemplos:
      | cuerpo                              | guardado             |
      | {"alias": "  Carlita  "}            | Carlita              |
      | {"alias": "Car"}                    | Car                  |
      | {"alias": " Abcdefghijklmnopqrst "} | Abcdefghijklmnopqrst |

  @HU-G4-03 @CA1 @CP-A80 @DEF-01
  Escenario: CP-A80 Editar el alias con la letra ñ
    Dado que Ana inició sesión
    Cuando Ana modifica su contacto "Prima Carla" con el cuerpo {"alias": "Prima Peña"}
    Entonces la respuesta tiene estado 200

  @HU-G4-03 @CA1 @CP-A54 @DEF-02
  Escenario: CP-A54 Al editar, el alias duplicado se detecta tras quitar los espacios
    Dado que Ana inició sesión
    Cuando Ana modifica su contacto "Prima Carla" con el cuerpo {"alias": " bruno "}
    Entonces la respuesta tiene estado 409
    Y el código de error es "ALIAS_DUPLICADO"

  @HU-G4-04 @CA2 @CP-A55
  Esquema del escenario: CP-A55 Una sola solicitud pendiente, enviada o recibida, impide eliminar
    Dado que Diego inició sesión
    Y Diego tiene el contacto "912345678" con alias "Bruno"
    Y que <solicitante> le solicitó 10.00 a <destinatario>
    Cuando Diego elimina su contacto "Bruno"
    Entonces la respuesta tiene estado 409
    Y el código de error es "SOLICITUDES_PENDIENTES"
    Y la lista de contactos de Diego queda "Bruno, Fabián"

    Ejemplos:
      | solicitante | destinatario |
      | Diego       | Bruno        |
      | Bruno       | Diego        |

  @HU-G4-04 @CA2 @CP-A56
  Esquema del escenario: CP-A56 Una solicitud ya resuelta no impide eliminar el contacto
    Dado que Diego le solicitó 10.00 a Bruno
    Y <resolucion> la solicitud
    Cuando Diego elimina su contacto "Alias Bruno"
    Entonces la respuesta tiene estado 204

    Ejemplos:
      | resolucion    |
      | Diego canceló |
      | Bruno rechazó |
      | Bruno aceptó  |

  @HU-G4-04 @CA2 @CP-A57
  Esquema del escenario: CP-A57 La pendiente deja de bloquear a las 48 horas exactas
    Dado que Diego inició sesión
    Y Diego tiene el contacto "912345678" con alias "Bruno"
    Y Diego envió 1 solicitudes a "Bruno"
    Cuando el reloj avanza <minutos> minutos y Diego vuelve a ingresar
    Y Diego elimina su contacto "Bruno"
    Entonces la respuesta tiene estado <estado>

    Ejemplos:
      | minutos | estado |
      | 2879    | 409    |
      | 2880    | 204    |

  @HU-G4-04 @CA1 @CP-A58
  Escenario: CP-A58 Eliminar un contacto no borra sus solicitudes ni el contacto inverso
    Dado que Ana inició sesión
    Cuando Ana elimina su contacto "Prima Carla"
    Entonces la respuesta tiene estado 204
    Y la lista de contactos de Ana queda "Bruno"
    Y Ana todavía ve la solicitud "Entradas al cine" en estado "VENCIDA"
    Y la lista de contactos de Carla queda "Prima Ana"

  @HU-G4-01 @HU-G4-04 @CA1 @CP-A86
  Escenario: CP-A86 Un contacto eliminado se puede volver a agregar
    Dado que Ana inició sesión
    Y Ana eliminó su contacto "Prima Carla"
    Cuando agrega el contacto "956781234" con alias "Prima Carla"
    Entonces la respuesta tiene estado 201
    Y la lista de contactos de Ana queda "Bruno, Prima Carla"

  @HU-G4-04 @CA1 @CP-A87
  Escenario: CP-A87 La transferencia a un contacto eliminado sigue en los movimientos de ambos
    Dado que Diego inició sesión
    Y Diego tiene el contacto "912345678" con alias "Bruno"
    Y Diego transfirió 10.00 al contacto "Bruno"
    Cuando Diego elimina su contacto "Bruno"
    Entonces la respuesta tiene estado 204
    Y Diego tiene el movimiento reciente "TRANSFERENCIA_ENVIADA" por "-10.00" con el código de la operación
    Y Bruno tiene el movimiento reciente "TRANSFERENCIA_RECIBIDA" por "10.00" con el código de la operación

  @HU-G4-05 @CA1 @CP-A59
  Esquema del escenario: CP-A59 Transferir a un contacto aplica el saldo y el monto de HU-N-07
    Dado que <usuario> inició sesión
    Cuando transfiere <monto> al contacto "<alias>"
    Entonces la respuesta tiene estado 422
    Y el código de error es "<codigo>"
    Y el saldo de <usuario> es "<saldo>"

    Ejemplos:
      | usuario | alias     | monto  | codigo             | saldo   |
      | Carla   | Prima Ana | 100.00 | SALDO_INSUFICIENTE | 50.00   |
      | Carla   | Prima Ana | 50.01  | SALDO_INSUFICIENTE | 50.00   |
      | Ana     | Bruno     | 0      | MONTO_INVALIDO     | 1500.00 |
      | Ana     | Bruno     | 500.01 | MONTO_INVALIDO     | 1500.00 |
      | Ana     | Bruno     | 1.234  | MONTO_INVALIDO     | 1500.00 |

  @HU-G4-05 @CA1 @CP-A88
  Escenario: CP-A88 Transferir a un contacto respeta el límite diario
    Dado que Diego inició sesión
    Y Diego tiene el contacto "912345678" con alias "Bruno"
    Y Diego ya transfirió 600.00 hoy
    Cuando transfiere 400.01 al contacto "Bruno"
    Entonces la respuesta tiene estado 422
    Y el código de error es "LIMITE_DIARIO_EXCEDIDO"
    Y el saldo de Diego es "1900.00"

  @HU-G4-05 @CA1 @CP-A60
  Escenario: CP-A60 Transferir a un contacto avisa por SMS y deja el mismo código en ambos movimientos
    Dado que Ana inició sesión
    Cuando transfiere 100.00 al contacto "Bruno"
    Entonces la respuesta tiene estado 201
    Y "912345678" recibió un SMS que contiene "Recibiste S/ 100.00 de Ana T."
    Y Ana tiene el movimiento reciente "TRANSFERENCIA_ENVIADA" por "-100.00" con el código de la operación
    Y Bruno tiene el movimiento reciente "TRANSFERENCIA_RECIBIDA" por "100.00" con el código de la operación
