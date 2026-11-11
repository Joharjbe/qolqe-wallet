# language: es
Característica: API de contactos y solicitudes (G4): casos técnicos
  Autenticación, propiedad de los datos, validación de entrada, métodos HTTP, contrato OpenAPI y concurrencia.
  Los ids de las rutas son los de la semilla: contactos 1 "Bruno" y 2 "Prima Carla" de Ana, 5 "Fabián" de Diego;
  solicitudes 1 de Bruno a Ana (pendiente), 2 de Carla a Ana (vencida) y 3 de Ana a Bruno (pendiente).

  @HU-G4-01 @HU-G4-02 @HU-G4-03 @HU-G4-04 @HU-G4-06 @HU-G4-07 @HU-G4-08 @HU-G4-09 @HU-G4-10 @CA1 @CP-T05 @tecnico
  Esquema del escenario: CP-T05 Sin un token Bearer válido ningún endpoint de G4 responde ni cambia datos
    Dado que Ana inició sesión
    Y se registran los saldos, contactos y solicitudes de los cuatro usuarios
    Cuando se envía <metodo> <ruta> con la credencial "<credencial>"
    Entonces la respuesta tiene estado 401
    Y el código de error es "NO_AUTENTICADO"
    Y la respuesta pide autenticarse con Bearer
    Y ningún saldo, contacto ni solicitud cambió

    Ejemplos:
      | metodo | ruta                        | credencial                         |
      | GET    | /api/contactos              | ninguna                            |
      | POST   | /api/contactos              | ninguna                            |
      | PUT    | /api/contactos/1            | ninguna                            |
      | DELETE | /api/contactos/2            | ninguna                            |
      | GET    | /api/solicitudes            | ninguna                            |
      | POST   | /api/solicitudes            | ninguna                            |
      | POST   | /api/solicitudes/1/aceptar  | ninguna                            |
      | POST   | /api/solicitudes/1/rechazar | ninguna                            |
      | POST   | /api/solicitudes/3/cancelar | ninguna                            |
      | GET    | /api/contactos              | token basura                       |
      | POST   | /api/contactos              | token basura                       |
      | PUT    | /api/contactos/1            | token basura                       |
      | DELETE | /api/contactos/2            | token basura                       |
      | GET    | /api/solicitudes            | token basura                       |
      | POST   | /api/solicitudes            | token basura                       |
      | POST   | /api/solicitudes/1/aceptar  | token basura                       |
      | POST   | /api/solicitudes/1/rechazar | token basura                       |
      | POST   | /api/solicitudes/3/cancelar | token basura                       |
      | GET    | /api/contactos              | token de Ana sin el prefijo Bearer |
      | POST   | /api/contactos              | token de Ana sin el prefijo Bearer |
      | PUT    | /api/contactos/1            | token de Ana sin el prefijo Bearer |
      | DELETE | /api/contactos/2            | token de Ana sin el prefijo Bearer |
      | GET    | /api/solicitudes            | token de Ana sin el prefijo Bearer |
      | POST   | /api/solicitudes            | token de Ana sin el prefijo Bearer |
      | POST   | /api/solicitudes/1/aceptar  | token de Ana sin el prefijo Bearer |
      | POST   | /api/solicitudes/1/rechazar | token de Ana sin el prefijo Bearer |
      | POST   | /api/solicitudes/3/cancelar | token de Ana sin el prefijo Bearer |
      | GET    | /api/contactos              | token de Ana con el esquema Basic  |
      | POST   | /api/contactos              | token de Ana con el esquema Basic  |
      | PUT    | /api/contactos/1            | token de Ana con el esquema Basic  |
      | DELETE | /api/contactos/2            | token de Ana con el esquema Basic  |
      | GET    | /api/solicitudes            | token de Ana con el esquema Basic  |
      | POST   | /api/solicitudes            | token de Ana con el esquema Basic  |
      | POST   | /api/solicitudes/1/aceptar  | token de Ana con el esquema Basic  |
      | POST   | /api/solicitudes/1/rechazar | token de Ana con el esquema Basic  |
      | POST   | /api/solicitudes/3/cancelar | token de Ana con el esquema Basic  |

  @HU-G4-02 @HU-G4-07 @HU-G4-08 @CA1 @CP-T06 @tecnico
  Esquema del escenario: CP-T06 El token vence a los 30 minutos del reloj de la aplicación
    Dado que Ana inició sesión
    Y se registran los saldos, contactos y solicitudes de los cuatro usuarios
    Y pasaron 30 minutos en el reloj de Qolqe desde el ingreso
    Cuando se envía <metodo> <ruta> con la credencial "token de Ana"
    Entonces la respuesta tiene estado 401
    Y el código de error es "NO_AUTENTICADO"
    Y el detalle del error es "El token expiró"
    Y ningún saldo, contacto ni solicitud cambió

    Ejemplos:
      | metodo | ruta                       |
      | GET    | /api/contactos             |
      | GET    | /api/solicitudes           |
      | POST   | /api/solicitudes/1/aceptar |

  @HU-G4-02 @HU-G4-07 @HU-G4-08 @CA1 @CP-T22 @tecnico
  Esquema del escenario: CP-T22 Un minuto antes de vencer, el token todavía sirve
    Dado que Ana inició sesión
    Y pasaron 29 minutos en el reloj de Qolqe desde el ingreso
    Cuando se envía <metodo> <ruta> con la credencial "token de Ana"
    Entonces la respuesta tiene estado 200

    Ejemplos:
      | metodo | ruta                       |
      | GET    | /api/contactos             |
      | GET    | /api/solicitudes           |
      | POST   | /api/solicitudes/1/aceptar |

  @HU-N-03 @HU-G4-01 @HU-G4-02 @HU-G4-03 @HU-G4-04 @HU-G4-06 @HU-G4-07 @HU-G4-08 @HU-G4-09 @HU-G4-10 @CA1 @CP-T07 @DEF-09 @tecnico
  Esquema del escenario: CP-T07 Después de cerrar sesión el token ya no sirve en G4
    Dado que Ana inició sesión
    Y Ana cerró sesión
    Cuando se envía <metodo> <ruta> con la credencial "token de Ana"
    Entonces la respuesta tiene estado 401
    Y el código de error es "NO_AUTENTICADO"

    Ejemplos:
      | metodo | ruta                        |
      | GET    | /api/contactos              |
      | POST   | /api/contactos              |
      | PUT    | /api/contactos/1            |
      | DELETE | /api/contactos/2            |
      | GET    | /api/solicitudes            |
      | POST   | /api/solicitudes            |
      | POST   | /api/solicitudes/1/aceptar  |
      | POST   | /api/solicitudes/1/rechazar |
      | POST   | /api/solicitudes/3/cancelar |

  @HU-G4-03 @HU-G4-04 @HU-G4-09 @HU-G4-10 @CA1 @HU-G4-08 @CA4 @CP-T08 @tecnico
  Esquema del escenario: CP-T08 Un id inexistente o una solicitud ajena responde 404 sin cambiar datos
    Dado que <usuario> inició sesión
    Y se registran los saldos, contactos y solicitudes de los cuatro usuarios
    Cuando se envía <metodo> <ruta> con la credencial "token de <usuario>"
    Entonces la respuesta tiene estado 404
    Y el código de error es "<codigo>"
    Y ningún saldo, contacto ni solicitud cambió

    Ejemplos:
      | usuario | metodo | ruta                             | codigo                  |
      | Ana     | PUT    | /api/contactos/999999            | CONTACTO_NO_ENCONTRADO  |
      | Ana     | DELETE | /api/contactos/999999            | CONTACTO_NO_ENCONTRADO  |
      | Ana     | POST   | /api/solicitudes/999999/aceptar  | SOLICITUD_NO_ENCONTRADA |
      | Ana     | POST   | /api/solicitudes/999999/rechazar | SOLICITUD_NO_ENCONTRADA |
      | Ana     | POST   | /api/solicitudes/999999/cancelar | SOLICITUD_NO_ENCONTRADA |
      | Ana     | POST   | /api/solicitudes/3/rechazar      | SOLICITUD_NO_ENCONTRADA |
      | Carla   | POST   | /api/solicitudes/3/rechazar      | SOLICITUD_NO_ENCONTRADA |

  @HU-G4-05 @HU-G4-06 @CA1 @CP-T09 @tecnico
  Esquema del escenario: CP-T09 Un contacto de otro usuario o inexistente no sirve para solicitar ni transferir
    Dado que Ana inició sesión
    Y se registran los saldos, contactos y solicitudes de los cuatro usuarios
    Cuando Ana envía POST <ruta> con el cuerpo <cuerpo>
    Entonces la respuesta tiene estado 404
    Y el código de error es "CONTACTO_NO_ENCONTRADO"
    Y ningún saldo, contacto ni solicitud cambió

    Ejemplos:
      | ruta                | cuerpo                                                           |
      | /api/solicitudes    | {"contacto_id": 5, "monto": "10.00", "motivo": "Contacto ajeno"} |
      | /api/solicitudes    | {"contacto_id": 999999, "monto": "10.00", "motivo": "No existe"} |
      | /api/transferencias | {"tipo": "QOLQE", "monto": "10.00", "contacto_id": 5}            |
      | /api/transferencias | {"tipo": "QOLQE", "monto": "10.00", "contacto_id": 999999}       |

  @HU-G4-03 @HU-G4-04 @HU-G4-08 @HU-G4-09 @HU-G4-10 @CA1 @CP-T10 @tecnico
  Esquema del escenario: CP-T10 Un id de ruta que no es entero informa el campo con error
    Dado que Ana inició sesión
    Y se registran los saldos, contactos y solicitudes de los cuatro usuarios
    Cuando se envía <metodo> <ruta> con la credencial "token de Ana"
    Entonces la respuesta tiene estado 422
    Y el error de validación nombra el campo "<campo>"
    Y ningún saldo, contacto ni solicitud cambió

    Ejemplos:
      | metodo | ruta                          | campo             |
      | PUT    | /api/contactos/abc            | path.contacto_id  |
      | DELETE | /api/contactos/abc            | path.contacto_id  |
      | POST   | /api/solicitudes/abc/aceptar  | path.solicitud_id |
      | POST   | /api/solicitudes/abc/rechazar | path.solicitud_id |
      | POST   | /api/solicitudes/abc/cancelar | path.solicitud_id |
      | PUT    | /api/contactos/1.5            | path.contacto_id  |
      | DELETE | /api/contactos/1.5            | path.contacto_id  |
      | POST   | /api/solicitudes/1.5/aceptar  | path.solicitud_id |
      | POST   | /api/solicitudes/1.5/rechazar | path.solicitud_id |
      | POST   | /api/solicitudes/1.5/cancelar | path.solicitud_id |

  @HU-G4-03 @HU-G4-04 @HU-G4-08 @HU-G4-09 @HU-G4-10 @CA1 @CP-T23 @tecnico
  Esquema del escenario: CP-T23 Los ids 0 y negativos se tratan como inexistentes
    Dado que Ana inició sesión
    Y se registran los saldos, contactos y solicitudes de los cuatro usuarios
    Cuando se envía <metodo> <ruta> con la credencial "token de Ana"
    Entonces la respuesta tiene estado 404
    Y el código de error es "<codigo>"
    Y ningún saldo, contacto ni solicitud cambió

    Ejemplos:
      | metodo | ruta                         | codigo                  |
      | PUT    | /api/contactos/0             | CONTACTO_NO_ENCONTRADO  |
      | DELETE | /api/contactos/0             | CONTACTO_NO_ENCONTRADO  |
      | POST   | /api/solicitudes/0/aceptar   | SOLICITUD_NO_ENCONTRADA |
      | POST   | /api/solicitudes/0/rechazar  | SOLICITUD_NO_ENCONTRADA |
      | POST   | /api/solicitudes/0/cancelar  | SOLICITUD_NO_ENCONTRADA |
      | PUT    | /api/contactos/-1            | CONTACTO_NO_ENCONTRADO  |
      | DELETE | /api/contactos/-1            | CONTACTO_NO_ENCONTRADO  |
      | POST   | /api/solicitudes/-1/aceptar  | SOLICITUD_NO_ENCONTRADA |
      | POST   | /api/solicitudes/-1/rechazar | SOLICITUD_NO_ENCONTRADA |
      | POST   | /api/solicitudes/-1/cancelar | SOLICITUD_NO_ENCONTRADA |

  @HU-G4-03 @HU-G4-04 @HU-G4-08 @HU-G4-09 @HU-G4-10 @CA1 @CP-T24 @tecnico
  Esquema del escenario: CP-T24 Un id fuera del rango de 64 bits no provoca un error del servidor
    Dado que Ana inició sesión
    Y se registran los saldos, contactos y solicitudes de los cuatro usuarios
    Cuando se envía <metodo> <ruta> con la credencial "token de Ana"
    Entonces la respuesta es un error del cliente con código y detalle
    Y ningún saldo, contacto ni solicitud cambió

    Ejemplos:
      | metodo | ruta                                           |
      | PUT    | /api/contactos/99999999999999999999            |
      | DELETE | /api/contactos/99999999999999999999            |
      | POST   | /api/solicitudes/99999999999999999999/aceptar  |
      | POST   | /api/solicitudes/99999999999999999999/rechazar |
      | POST   | /api/solicitudes/99999999999999999999/cancelar |

  @HU-G4-01 @CA1 @CP-T11 @tecnico
  Esquema del escenario: CP-T11 El alta de contacto con campos faltantes o de otro tipo nombra el campo
    Dado que Diego inició sesión
    Y se registran los saldos, contactos y solicitudes de los cuatro usuarios
    Cuando Diego envía POST /api/contactos con el cuerpo <cuerpo> y el tipo "<tipo>"
    Entonces la respuesta tiene estado 422
    Y el error de validación nombra el campo "<campo>"
    Y ningún saldo, contacto ni solicitud cambió

    Ejemplos:
      | cuerpo                                     | tipo             | campo        |
      | {}                                         | application/json | body.celular |
      | {}                                         | application/json | body.alias   |
      | {"alias": "Bruno"}                         | application/json | body.celular |
      | {"celular": "912345678"}                   | application/json | body.alias   |
      | {"celular": 912345678, "alias": "Bruno"}   | application/json | body.celular |
      | {"celular": "912345678", "alias": null}    | application/json | body.alias   |
      | {"celular": "912345678", "alias": 123}     | application/json | body.alias   |
      | []                                         | application/json | body         |
      | {"celular": "912345678", "alias": "Bruno"} | text/plain       | body         |

  @HU-G4-03 @CA1 @CP-T12 @tecnico
  Esquema del escenario: CP-T12 Editar un contacto con tipos inválidos nombra el campo
    Dado que Ana inició sesión
    Y se registran los saldos, contactos y solicitudes de los cuatro usuarios
    Cuando Ana envía PUT /api/contactos/1 con el cuerpo <cuerpo>
    Entonces la respuesta tiene estado 422
    Y el error de validación nombra el campo "<campo>"
    Y ningún saldo, contacto ni solicitud cambió

    Ejemplos:
      | cuerpo               | campo         |
      | {"favorito": "si"}   | body.favorito |
      | {"favorito": 2}      | body.favorito |
      | {"favorito": [true]} | body.favorito |
      | {"alias": 123}       | body.alias    |
      | []                   | body          |

  @HU-G4-03 @CA1 @CP-T26 @DEF-08 @tecnico
  Esquema del escenario: CP-T26 favorito no acepta números aunque Pydantic los convierta
    Dado que Ana inició sesión
    Cuando Ana envía PUT /api/contactos/1 con el cuerpo <cuerpo>
    Entonces la respuesta tiene estado 422
    Y el error de validación nombra el campo "body.favorito"

    Ejemplos:
      | cuerpo          |
      | {"favorito": 0} |
      | {"favorito": 1} |

  @HU-G4-06 @CA1 @CP-T13 @tecnico
  Esquema del escenario: CP-T13 Crear una solicitud con campos faltantes o de otro tipo nombra el campo
    Dado que Ana inició sesión
    Y se registran los saldos, contactos y solicitudes de los cuatro usuarios
    Cuando Ana envía POST /api/solicitudes con el cuerpo <cuerpo>
    Entonces la respuesta tiene estado 422
    Y el error de validación nombra el campo "<campo>"
    Y ningún saldo, contacto ni solicitud cambió

    Ejemplos:
      | cuerpo                                                              | campo            |
      | {}                                                                  | body.contacto_id |
      | {}                                                                  | body.monto       |
      | {}                                                                  | body.motivo      |
      | {"monto": "10.00", "motivo": "Motivo valido"}                       | body.contacto_id |
      | {"contacto_id": 1, "motivo": "Motivo valido"}                       | body.monto       |
      | {"contacto_id": 1, "monto": "10.00"}                                | body.motivo      |
      | {"contacto_id": 1, "monto": "abc", "motivo": "Motivo valido"}       | body.monto       |
      | {"contacto_id": 1, "monto": null, "motivo": "Motivo valido"}        | body.monto       |
      | {"contacto_id": 1, "monto": true, "motivo": "Motivo valido"}        | body.monto       |
      | {"contacto_id": 1, "monto": "NaN", "motivo": "Motivo valido"}       | body.monto       |
      | {"contacto_id": "uno", "monto": "10.00", "motivo": "Motivo valido"} | body.contacto_id |
      | {"contacto_id": 1.5, "monto": "10.00", "motivo": "Motivo valido"}   | body.contacto_id |
      | {"contacto_id": 1, "monto": "10.00", "motivo": 12345}               | body.motivo      |

  @HU-G4-09 @CA1 @CP-T14 @tecnico
  Esquema del escenario: CP-T14 Rechazar con un motivo que no es texto no cambia la solicitud
    Dado que Ana inició sesión
    Y se registran los saldos, contactos y solicitudes de los cuatro usuarios
    Cuando Ana envía POST /api/solicitudes/1/rechazar con el cuerpo <cuerpo>
    Entonces la respuesta tiene estado 422
    Y el error de validación nombra el campo "body.motivo"
    Y ningún saldo, contacto ni solicitud cambió

    Ejemplos:
      | cuerpo             |
      | {"motivo": 123}    |
      | {"motivo": ["no"]} |
      | {"motivo": false}  |

  @HU-G4-01 @HU-G4-03 @HU-G4-06 @HU-G4-09 @CA1 @CP-T30 @tecnico
  Esquema del escenario: CP-T30 Un JSON mal formado responde 422 SOLICITUD_INVALIDA sin cambiar datos
    Dado que Ana inició sesión
    Y se registran los saldos, contactos y solicitudes de los cuatro usuarios
    Cuando Ana envía <metodo> <ruta> con el cuerpo {"alias": "Bruno"
    Entonces la respuesta tiene estado 422
    Y el error indica que el JSON está mal formado
    Y ningún saldo, contacto ni solicitud cambió

    Ejemplos:
      | metodo | ruta                        |
      | POST   | /api/contactos              |
      | PUT    | /api/contactos/1            |
      | POST   | /api/solicitudes            |
      | POST   | /api/solicitudes/1/rechazar |

  @HU-G4-01 @HU-G4-03 @HU-G4-06 @CA1 @CP-T25 @tecnico
  Esquema del escenario: CP-T25 Los campos que no son del contrato se ignoran (asignación masiva)
    Dado que <usuario> inició sesión
    Cuando <usuario> envía <metodo> <ruta> con el cuerpo <cuerpo>
    Entonces la respuesta tiene estado <estado>
    Y la respuesta trae "<campo>" con el valor <valor>

    Ejemplos:
      | usuario | metodo | ruta             | cuerpo                                                                                         | estado | campo            | valor       |
      | Diego   | POST   | /api/contactos   | {"celular": "912345678", "alias": "Bruno", "favorito": true}                                   | 201    | favorito         | false       |
      | Ana     | PUT    | /api/contactos/1 | {"celular": "956781234"}                                                                       | 200    | celular          | "912345678" |
      | Ana     | POST   | /api/solicitudes | {"contacto_id": 1, "monto": "10.00", "motivo": "Motivo valido", "estado": "ACEPTADA"}          | 201    | estado           | "PENDIENTE" |
      | Ana     | POST   | /api/solicitudes | {"contacto_id": 1, "monto": "10.00", "motivo": "Motivo valido", "codigo_operacion": "TRF0001"} | 201    | codigo_operacion | null        |

  @HU-G4-02 @CA1 @CP-T15 @tecnico
  Esquema del escenario: CP-T15 Una página que no es un entero positivo informa query.pagina
    Dado que Ana inició sesión
    Cuando Ana envía GET /api/contactos?pagina=<pagina>
    Entonces la respuesta tiene estado 422
    Y el error de validación nombra el campo "query.pagina"

    Ejemplos:
      | pagina |
      | 0      |
      | -1     |
      | abc    |
      | 1.5    |

  @HU-G4-01 @HU-G4-02 @HU-G4-03 @HU-G4-04 @HU-G4-07 @HU-G4-08 @CA1 @CP-T16 @tecnico
  Esquema del escenario: CP-T16 Un método no permitido responde 405 con la cabecera Allow
    Dado que Ana inició sesión
    Cuando Ana envía <metodo> <ruta>
    Entonces la respuesta tiene estado 405
    Y el código de error es "ERROR_HTTP"
    Y la respuesta incluye la cabecera "Allow"

    Ejemplos:
      | metodo  | ruta                       |
      | PATCH   | /api/contactos/1           |
      | GET     | /api/contactos/1           |
      | DELETE  | /api/contactos             |
      | PUT     | /api/contactos             |
      | PUT     | /api/solicitudes           |
      | GET     | /api/solicitudes/1/aceptar |
      | OPTIONS | /api/contactos             |

  # Una ruta inexistente no prueba un CA: se etiqueta con la HU del recurso (solicitudes) y sin @CA.
  @HU-G4-07 @CP-T28 @tecnico
  Esquema del escenario: CP-T28 Una ruta inexistente responde 404 con el formato de error
    Dado que Ana inició sesión
    Cuando Ana envía <metodo> <ruta>
    Entonces la respuesta tiene estado 404
    Y el código de error es "ERROR_HTTP"

    Ejemplos:
      | metodo | ruta               |
      | GET    | /api/solicitudes/1 |
      | DELETE | /api/solicitudes/1 |

  @HU-G4-01 @HU-G4-03 @HU-G4-06 @CA1 @CP-T29 @DEF-06 @tecnico
  Esquema del escenario: CP-T29 La cabecera Allow lista todos los métodos de la ruta
    Dado que Ana inició sesión
    Cuando Ana envía <metodo> <ruta>
    Entonces la respuesta tiene estado 405
    Y la cabecera Allow lista los métodos "<metodos>"

    Ejemplos:
      | metodo  | ruta             | metodos     |
      | PATCH   | /api/contactos/1 | PUT, DELETE |
      | OPTIONS | /api/contactos   | GET, POST   |
      | PUT     | /api/solicitudes | GET, POST   |

  @HU-G4-01 @HU-G4-02 @HU-G4-03 @HU-G4-04 @HU-G4-06 @HU-G4-07 @HU-G4-08 @HU-G4-09 @HU-G4-10 @CA1 @CP-T21 @tecnico
  Esquema del escenario: CP-T21 Las respuestas cumplen el esquema y el tipo de contenido del contrato OpenAPI
    Dado que <usuario> inició sesión
    Cuando <usuario> envía <metodo> <ruta> con el cuerpo <cuerpo>
    Entonces la respuesta tiene estado <estado>
    Y la respuesta cumple el contrato OpenAPI de "<operacion>"

    Ejemplos:
      | usuario | metodo | ruta                        | cuerpo                                                     | estado | operacion                                     |
      | Ana     | GET    | /api/contactos              | (sin cuerpo)                                               | 200    | GET /api/contactos                            |
      | Diego   | POST   | /api/contactos              | {"celular": "912345678", "alias": "Bruno"}                 | 201    | POST /api/contactos                           |
      | Diego   | POST   | /api/contactos              | {"celular": "12", "alias": "Bruno"}                        | 422    | POST /api/contactos                           |
      | Diego   | POST   | /api/contactos              | {}                                                         | 422    | POST /api/contactos                           |
      | Ana     | PUT    | /api/contactos/1            | {"favorito": false}                                        | 200    | PUT /api/contactos/{contacto_id}              |
      | Ana     | DELETE | /api/contactos/2            | (sin cuerpo)                                               | 204    | DELETE /api/contactos/{contacto_id}           |
      | Ana     | DELETE | /api/contactos/1            | (sin cuerpo)                                               | 409    | DELETE /api/contactos/{contacto_id}           |
      | Ana     | GET    | /api/solicitudes            | (sin cuerpo)                                               | 200    | GET /api/solicitudes                          |
      | Ana     | GET    | /api/solicitudes?estado=X   | (sin cuerpo)                                               | 422    | GET /api/solicitudes                          |
      | Ana     | POST   | /api/solicitudes            | {"contacto_id": 1, "monto": "10.00", "motivo": "Contrato"} | 201    | POST /api/solicitudes                         |
      | Ana     | POST   | /api/solicitudes/1/aceptar  | (sin cuerpo)                                               | 200    | POST /api/solicitudes/{solicitud_id}/aceptar  |
      | Ana     | POST   | /api/solicitudes/3/aceptar  | (sin cuerpo)                                               | 404    | POST /api/solicitudes/{solicitud_id}/aceptar  |
      | Ana     | POST   | /api/solicitudes/1/rechazar | {}                                                         | 200    | POST /api/solicitudes/{solicitud_id}/rechazar |
      | Ana     | POST   | /api/solicitudes/3/cancelar | (sin cuerpo)                                               | 200    | POST /api/solicitudes/{solicitud_id}/cancelar |

  @HU-G4-08 @CA1 @CA4 @CP-T17 @DEF-25 @tecnico @concurrencia
  Escenario: CP-T17 Tres aceptaciones simultáneas de la misma solicitud debitan una sola vez
    Dado que Diego le solicitó 25.00 a Bruno
    Cuando Bruno acepta la misma solicitud 3 veces a la vez
    Entonces solo una de las peticiones simultáneas responde 200 y las demás 409 "ESTADO_INVALIDO"
    Y el saldo de Bruno es "775.00"
    Y el saldo de Diego es "2525.00"

  @HU-G4-08 @CA1 @HU-N-07 @CA5 @CP-T18 @DEF-21 @tecnico @concurrencia
  Escenario: CP-T18 Aceptar a la vez dos solicitudes que juntas superan el saldo no lo deja negativo
    Dado que Carla recibió solicitudes de 40.00 de Ana y de Bruno
    Cuando Carla acepta a la vez las solicitudes que recibió
    Entonces solo una de las peticiones simultáneas responde 200 y las demás 422 "SALDO_INSUFICIENTE"
    Y el saldo de Carla es "10.00"

  @HU-G4-01 @CA1 @CP-T20 @DEF-26 @tecnico @concurrencia
  Escenario: CP-T20 Cinco altas simultáneas del mismo celular crean un solo contacto
    Dado que Diego inició sesión
    Cuando Diego agrega 5 veces a la vez el celular "912345678" en 5 ráfagas
    Entonces solo una de las peticiones simultáneas responde 201 y las demás 409 "CONTACTO_EXISTENTE"
    Y Diego tiene el celular "912345678" una sola vez entre sus contactos
