# language: es
Característica: API de inicio y cierre de sesión (núcleo HU-N-02 y HU-N-03)
  RN-04 (bloqueo por intentos), vigencia del token de 30 minutos y revocación al cerrar sesión.

  @HU-N-02 @CA1 @CP-NA23
  Escenario: CP-NA23 El ingreso correcto entrega un token de 30 minutos y crea la sesión
    Cuando Ana inicia sesión
    Entonces la respuesta tiene estado 200
    Y el token expira en 1800 segundos
    Y el token identifica al usuario 1 con celular "987654321"
    Y la sesión creada figura como actual y vence a los 30 minutos

  @HU-N-02 @CA1 @CP-NA24
  Escenario: CP-NA24 Vigencia del token en el borde de los 30 minutos
    Dado que Bruno inició sesión
    Cuando el reloj se adelanta 29 minutos
    Y Bruno consulta su saldo
    Entonces la respuesta tiene estado 200
    Y el saldo consultado es "800.00"
    Cuando el reloj se adelanta 1 minutos
    Y Bruno consulta su saldo
    Entonces la respuesta tiene estado 401
    Y el código de error es "NO_AUTENTICADO"
    Y el mensaje de error es "El token expiró"

  @HU-N-02 @CA1 @CP-NA25
  Escenario: CP-NA25 Cada ingreso crea una sesión independiente
    Cuando Ana abre dos sesiones
    Entonces las dos sesiones son independientes

  @HU-N-02 @CA1 @CP-NA26 @tecnico
  Esquema del escenario: CP-NA26 Solicitudes de ingreso mal formadas
    Cuando se envía al login la variante "<variante>"
    Entonces la respuesta tiene estado <estado>
    Y el código de error es "<codigo>"

    Ejemplos:
      | variante             | estado | codigo             |
      | cuerpo vacío         | 422    | SOLICITUD_INVALIDA |
      | sin pin              | 422    | SOLICITUD_INVALIDA |
      | pin numérico         | 422    | SOLICITUD_INVALIDA |
      | dispositivo numérico | 422    | SOLICITUD_INVALIDA |
      | formulario           | 422    | SOLICITUD_INVALIDA |
      | método GET           | 405    | ERROR_HTTP         |

  @HU-N-02 @CA2 @CP-NA27
  Esquema del escenario: CP-NA27 Mensaje genérico ante credenciales inválidas
    Cuando ingresa con el celular "<celular>" y PIN "<pin>"
    Entonces la respuesta tiene estado 401
    Y el código de error es "CREDENCIALES_INVALIDAS"
    Y el mensaje de error es "Celular o PIN incorrectos"

    Ejemplos:
      | celular   | pin  |
      | 900999999 | 4826 |
      | 987654321 | 0000 |
      | 123       | 4826 |

  @HU-N-02 @CA3 @CP-NA29
  Escenario: CP-NA29 El tercer fallo consecutivo bloquea la cuenta y avisa por SMS
    Cuando Carla falla el ingreso
    Entonces la respuesta tiene estado 401
    Cuando Carla falla el ingreso
    Entonces la respuesta tiene estado 401
    Cuando Carla falla el ingreso
    Entonces la respuesta tiene estado 423
    Y el código de error es "CUENTA_BLOQUEADA"
    Y "956781234" tiene 1 mensajes SMS
    Y "956781234" recibió un SMS que contiene "fue bloqueada por intentos fallidos hasta las"

  @HU-N-02 @CA3 @CP-NA30 @DEF-10
  Escenario: CP-NA30 Un ingreso exitoso reinicia el conteo de intentos fallidos
    Cuando Bruno falla el ingreso
    Y Bruno falla el ingreso
    Y Bruno ingresa correctamente
    Y Bruno falla el ingreso
    Entonces la respuesta tiene estado 401
    Y el código de error es "CREDENCIALES_INVALIDAS"

  @HU-N-02 @CA3 @CP-NA31
  Escenario: CP-NA31 Los intentos durante el bloqueo no envían más SMS
    Dado que Carla está bloqueada por intentos fallidos
    Cuando ingresa con el celular "956781234" y PIN "0000"
    Entonces la respuesta tiene estado 423
    Cuando ingresa con el celular "956781234" y PIN "5917"
    Entonces la respuesta tiene estado 423
    Y "956781234" tiene 1 mensajes SMS

  @HU-N-02 @CA3 @CP-NA32
  Escenario: CP-NA32 Los fallos de un usuario no cuentan para otro
    Cuando Ana falla el ingreso
    Y Bruno falla el ingreso
    Y Ana falla el ingreso
    Y Bruno falla el ingreso
    Y Ana ingresa correctamente
    Y Bruno ingresa correctamente
    Entonces la respuesta tiene estado 200

  @HU-N-02 @CA3 @CP-NA33 @DEF-11 @tecnico @concurrencia
  Escenario: CP-NA33 Los intentos fallidos simultáneos también deben bloquear
    Cuando Carla recibe 6 intentos fallidos simultáneos
    Y Carla intenta ingresar con su PIN correcto
    Entonces la respuesta tiene estado 423

  @HU-N-02 @CA4 @CP-NA34
  Escenario: CP-NA34 Durante el bloqueo ningún PIN permite ingresar
    Dado que Carla está bloqueada por intentos fallidos
    Cuando ingresa con el celular "956781234" y PIN "5917"
    Entonces la respuesta tiene estado 423
    Y el código de error es "CUENTA_BLOQUEADA"
    Cuando ingresa con el celular "956781234" y PIN "0000"
    Entonces la respuesta tiene estado 423

  @HU-N-02 @CA4 @CP-NA35
  Escenario: CP-NA35 El bloqueo dura exactamente 15 minutos
    Dado que Carla está bloqueada por intentos fallidos
    Cuando el reloj se adelanta 14 minutos
    Y ingresa con el celular "956781234" y PIN "5917"
    Entonces la respuesta tiene estado 423
    Cuando el reloj se adelanta 1 minutos
    Y ingresa con el celular "956781234" y PIN "5917"
    Entonces la respuesta tiene estado 200

  @HU-N-02 @CA4 @CP-NA36
  Escenario: CP-NA36 Elena, bloqueada en la semilla, ingresa al vencer el bloqueo
    Cuando ingresa con el celular "923456789" y PIN "8152"
    Entonces la respuesta tiene estado 423
    Cuando el reloj se adelanta 15 minutos
    Y ingresa con el celular "923456789" y PIN "8152"
    Entonces la respuesta tiene estado 200

  @HU-N-02 @CA4 @CP-NA37
  Escenario: CP-NA37 Tras vencer el bloqueo, el conteo empieza de nuevo
    Dado que Carla está bloqueada por intentos fallidos
    Cuando el reloj se adelanta 15 minutos
    Y Carla falla el ingreso
    Entonces la respuesta tiene estado 401
    Cuando Carla falla el ingreso
    Entonces la respuesta tiene estado 401
    Cuando Carla falla el ingreso
    Entonces la respuesta tiene estado 423
    Y "956781234" tiene 2 mensajes SMS

  @HU-N-02 @CA5 @CP-NA38
  Esquema del escenario: CP-NA38 La cuenta cerrada solo revela su estado si el PIN es correcto
    Cuando ingresa con el celular "934567812" y PIN "<pin>"
    Entonces la respuesta tiene estado 401
    Y el código de error es "<codigo>"

    Ejemplos:
      | pin  | codigo                 |
      | 6029 | CUENTA_CERRADA         |
      | 0000 | CREDENCIALES_INVALIDAS |

  @HU-N-02 @CA5 @CP-NA39
  Escenario: CP-NA39 Una cuenta que se cierra deja de poder ingresar
    Cuando se registra con el celular "987000151"
    Entonces la respuesta tiene estado 201
    Cuando inicia sesión el celular "987000151" con PIN "4826"
    Y se cierra la cuenta actual con PIN "4826"
    Entonces la respuesta tiene estado 204
    Cuando ingresa con el celular "987000151" y PIN "4826"
    Entonces la respuesta tiene estado 401
    Y el código de error es "CUENTA_CERRADA"
    Cuando se registra con el celular "987000151"
    Entonces la respuesta tiene estado 409
    Y el código de error es "CELULAR_REGISTRADO"

  @HU-N-02 @CA6 @CP-NA40
  Escenario: CP-NA40 El ingreso desde un dispositivo de confianza no envía alerta
    Cuando Ana inicia sesión desde el dispositivo "a1b2c3d4e5f60718"
    Entonces la respuesta tiene estado 200
    Y "987654321" tiene 0 mensajes SMS
    Y la sesión actual registra el dispositivo "a1b2c3d4e5f60718" con nombre "Celular de Ana"

  @HU-N-02 @CA6 @CP-NA41
  Escenario: CP-NA41 El ingreso desde un dispositivo nuevo envía alerta
    Cuando Ana inicia sesión desde el dispositivo "ffffffffffffffff"
    Entonces la respuesta tiene estado 200
    Y "987654321" tiene 1 mensajes SMS
    Y "987654321" recibió un SMS que contiene "se inició sesión en tu cuenta desde un nuevo dispositivo"
    Y la sesión actual registra el dispositivo "ffffffffffffffff" con nombre "null"

  @HU-N-02 @CA6 @CP-NA42 @tecnico
  Escenario: CP-NA42 El dispositivo de confianza de otro usuario cuenta como nuevo
    Cuando Bruno inicia sesión desde el dispositivo "a1b2c3d4e5f60718"
    Entonces la respuesta tiene estado 200
    Y "912345678" tiene 1 mensajes SMS
    Y el dispositivo "a1b2c3d4e5f60718" de Ana no cambió su último ingreso

  @HU-N-02 @CA6 @CP-NA43 @tecnico
  Esquema del escenario: CP-NA43 Casos borde del identificador de dispositivo
    Cuando Ana intenta ingresar con el dispositivo de prueba "<variante>"
    Entonces la respuesta tiene estado <estado>
    Y "987654321" tiene <sms> mensajes SMS

    Ejemplos:
      | variante      | estado | sms |
      | sin id        | 200    | 0   |
      | id vacío      | 200    | 0   |
      | mayúsculas    | 200    | 1   |
      | pin incorrecto | 401   | 0   |
      | id numérico   | 422    | 0   |

  @HU-N-03 @CA1 @CP-NA44 @DEF-09
  Escenario: CP-NA44 Después del logout el token ya no debe servir
    Cuando Ana cierra su sesión
    Entonces la respuesta tiene estado 204
    Cuando con el token cerrado se consulta el saldo
    Entonces la respuesta tiene estado 401
    Y el código de error es "NO_AUTENTICADO"

  # NA45 y NA48 usan reglas de Seguridad (HU-G6-09 CA2 y HU-G6-10 CA1, módulo G6, fuera del alcance) como evidencia
  # adicional del cierre de sesión. Son técnicos y no cuentan como cobertura de un CA de HU-N-03.
  @HU-N-03 @CP-NA45 @DEF-09 @tecnico
  Escenario: CP-NA45 La sesión cerrada debe desaparecer de mis sesiones activas
    Cuando Ana abre dos sesiones
    Y Ana cierra la primera sesión
    Entonces la respuesta tiene estado 204
    Y Ana conserva 1 sesiones activas

  @HU-N-03 @CA1 @CP-NA46 @DEF-09 @tecnico
  Escenario: CP-NA46 Un segundo logout con el mismo token debe ser rechazado
    Cuando Ana cierra su sesión
    Entonces la respuesta tiene estado 204
    Y el segundo cierre de sesión es rechazado

  @HU-N-03 @CA1 @CP-NA47 @tecnico
  Esquema del escenario: CP-NA47 Logout sin token, con token inválido o vencido
    Cuando se cierra sesión con la variante "<variante>"
    Entonces la respuesta tiene estado <estado>
    Y el mensaje de error es "<mensaje>"

    Ejemplos:
      | variante       | estado | mensaje                          |
      | sin token      | 401    | Falta el token de autenticación  |
      | token inválido | 401    | Token inválido                   |
      | token vencido  | 401    | El token expiró                  |

  @HU-N-03 @CP-NA48 @tecnico
  Escenario: CP-NA48 Cerrar la sesión desde Seguridad sí invalida el token
    Cuando Ana abre dos sesiones
    Y Ana cierra la primera sesión desde seguridad
    Entonces la respuesta tiene estado 204
    Cuando con la primera sesión se consulta el saldo
    Entonces la respuesta tiene estado 401
    Y el código de error es "NO_AUTENTICADO"
    Y el mensaje de error es "La sesión fue cerrada"

  @HU-N-03 @CA2 @CP-NA49
  Escenario: CP-NA49 La otra sesión del mismo usuario sigue activa
    Cuando Ana abre dos sesiones
    Y Ana cierra la primera sesión
    Y con la segunda sesión se consulta el perfil
    Entonces la respuesta tiene estado 200
    Cuando con la segunda sesión se edita el nombre a "Ana Torres"
    Entonces la respuesta tiene estado 200
    Y la segunda sesión de Ana sigue activa como la actual

  @HU-N-03 @CA2 @CP-NA50 @tecnico
  Escenario: CP-NA50 El logout de un usuario no afecta a otro
    Dado que Bruno inició sesión
    Cuando Ana cierra su sesión
    Y Bruno consulta su saldo
    Entonces la respuesta tiene estado 200
    Y el saldo consultado es "800.00"

  @HU-N-03 @CA2 @CP-NA51
  Escenario: CP-NA51 Después del logout puedo volver a ingresar
    Cuando Ana abre dos sesiones
    Y Ana cierra la primera sesión
    Y Ana vuelve a iniciar sesión
    Entonces la respuesta tiene estado 200
    Y el nuevo inicio de sesión tiene un identificador distinto

  @HU-N-02 @CA2 @CP-NA157 @tecnico
  Escenario: CP-NA157 Celular inexistente y PIN incorrecto responden igual en estado, cuerpo y cabeceras
    Cuando se intenta ingresar con el celular "900999999" y el PIN "4826" y luego con el celular "912345678" y el PIN "0000"
    Entonces los dos intentos de ingreso responden igual en estado, cuerpo y cabeceras salvo la fecha
