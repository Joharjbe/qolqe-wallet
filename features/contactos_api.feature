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

  @HU-G4-02 @CP-T01
  Escenario: CP-T01 Sin token no se accede a los contactos
    Cuando se consultan los contactos sin token
    Entonces la respuesta tiene estado 401
    Y el código de error es "NO_AUTENTICADO"

  @HU-G4-03 @HU-G4-04 @CP-T02
  Esquema del escenario: CP-T02 El contacto de otro usuario responde como inexistente
    Dado que Carla inició sesión
    Cuando intenta <accion> el contacto "Bruno" de Ana
    Entonces la respuesta tiene estado 404
    Y el código de error es "CONTACTO_NO_ENCONTRADO"

    Ejemplos:
      | accion   |
      | editar   |
      | eliminar |
