# language: es
Característica: Registro, ingreso, salida y perfil en la web (módulo común)
  Solo los recorridos críticos, las reglas que existen únicamente en la pantalla
  y la forma en que la pantalla comunica los errores de la API.
  Las reglas de negocio se prueban en la API, el nivel más bajo donde se detectan.

  @HU-N-01 @CA1 @CP-NW01
  Escenario: CP-NW01 Alta de cuenta desde la web y primer ingreso
    Cuando se registra con estos datos:
      | dni      | nombres         | celular   | correo          | pin  |
      | 12345678 | Lucía Fernández | 987000111 | lucia@correo.pe | 4826 |
    Entonces vuelve al ingreso con el aviso "Tu cuenta fue creada. Ya puedes ingresar."
    Cuando ingresa con el celular "987000111" y el PIN "4826"
    Entonces está en el inicio con el saludo "Hola, Lucía"
    Y ve en inicio el saldo "S/ 0.00"
    Y no tiene movimientos recientes

  @HU-N-01 @CA1 @CP-NW02
  Escenario: CP-NW02 Si el PIN y su confirmación no coinciden no se envía el registro
    Cuando se registra con estos datos:
      | dni      | nombres         | celular   | pin  | confirmacion |
      | 12345678 | Lucía Fernández | 987000112 | 4826 | 4827         |
    Entonces ve el error de registro "Los PIN no coinciden"
    Y la pantalla envió 0 peticiones "POST /api/usuarios"
    Y no puede ingresar con el celular "987000112" y el PIN "4826"

  @HU-N-01 @CA1 @CP-NW03 @DEF-18 @fail
  Escenario: CP-NW03 Con nombres de 1 letra el error se muestra en español
    Cuando se registra con estos datos:
      | dni      | nombres | celular   | pin  |
      | 12345678 | A       | 987000113 | 4826 |
    Entonces ve el error de registro "Los nombres deben tener entre 2 y 80 caracteres"

  @HU-N-01 @CA3 @CP-NW04
  Escenario: CP-NW04 Con un celular ya registrado se muestra el error y se conserva el formulario
    Cuando se registra con estos datos:
      | dni      | nombres         | celular   | pin  |
      | 12345678 | Lucía Fernández | 987654321 | 4826 |
    Entonces ve el error de registro "El celular ya está registrado"

  @HU-N-02 @CA1 @CP-NW05
  Escenario: CP-NW05 El ingreso correcto lleva al inicio
    Cuando ingresa con el celular "987654321" y el PIN "4826"
    Entonces está en el inicio con el saludo "Hola, Ana"
    Y el menú muestra el nombre "Ana Torres Quispe"
    Y ve en inicio el saldo "S/ 1,500.00"
    Y el navegador guarda la sesión

  @HU-N-02 @CA2 @CP-NW06
  Esquema del escenario: CP-NW06 El error de ingreso es genérico y limpia el PIN
    Cuando intenta ingresar con el celular "<celular>" y el PIN "<pin>"
    Entonces ve el error de ingreso "Celular o PIN incorrectos"
    Y el PIN queda vacío y listo para escribir

    Ejemplos:
      | caso                | celular   | pin  |
      | PIN incorrecto      | 987654321 | 0000 |
      | celular inexistente | 900999999 | 4826 |

  @HU-N-02 @CA3 @CA4 @CP-NW07
  Esquema del escenario: CP-NW07 La web informa el bloqueo con su hora y ofrece el desbloqueo
    Dado que el reloj de Qolqe marca las "10:00"
    Y que "<usuario>" acumula <fallos> intentos fallidos
    Cuando intenta ingresar como "<usuario>" con el PIN "<pin>"
    Entonces ve el error de ingreso "<mensaje>"
    Cuando sigue el enlace de desbloqueo
    Entonces ve la pantalla de desbloqueo

    Ejemplos:
      | caso                   | usuario | fallos | pin  | mensaje                                                                             |
      | tercer intento fallido | Carla   | 2      | 0000 | Superaste los intentos permitidos. Tu cuenta está bloqueada hasta las 10:15.        |
      | cuenta ya bloqueada    | Elena   | 0      | 8152 | Tu cuenta está bloqueada hasta las 10:15. Puedes solicitar un código de desbloqueo. |

  @HU-N-02 @CA6 @CP-NW08
  Escenario: CP-NW08 La pantalla de ingreso muestra el dispositivo recordado y no alerta
    Dado que el navegador recuerda el dispositivo "a1b2c3d4e5f60718" llamado "Celular de Ana"
    Cuando abre la pantalla de ingreso
    Entonces ve el dispositivo "Ingresando desde: Celular de Ana"
    Cuando ingresa como "Ana"
    Entonces está en el inicio con el saludo "Hola, Ana"
    Y "Ana" no recibió ningún SMS

  @HU-N-03 @CA1 @CP-NW09
  Escenario: CP-NW09 Cerrar sesión desde el menú borra la sesión del navegador
    Dado que "Ana" ingresó a Qolqe
    Cuando cierra sesión
    Entonces vuelve al ingreso con el aviso "Cerraste sesión correctamente."
    Y el navegador ya no guarda la sesión
    Cuando abre el inicio sin sesión
    Entonces vuelve a la pantalla de ingreso sin ver su saldo
    Cuando regresa a la página anterior
    Entonces vuelve a la pantalla de ingreso sin ver su saldo

  @HU-N-04 @CA1 @CP-NW10
  Escenario: CP-NW10 El inicio muestra el saldo con formato y permite ocultarlo
    Dado que "Ana" ingresó a Qolqe
    Entonces ve en inicio el saldo "S/ 1,500.00"
    Y la fecha de actualización del saldo tiene el formato dd/mm/aaaa hh:mm
    Cuando oculta su saldo
    Entonces el saldo queda oculto como "S/ ••••••"
    Cuando vuelve a mostrar su saldo
    Entonces el saldo vuelve a verse como "S/ 1,500.00"

  @HU-N-04 @CA2 @CP-NW11
  Esquema del escenario: CP-NW11 El perfil muestra los datos con el DNI enmascarado
    Dado que "<usuario>" ingresó a Qolqe
    Cuando abre la pantalla de perfil
    Entonces el perfil muestra nombres "<nombres>", celular "<celular>", DNI "<dni>" y correo "<correo>"
    Y la página no muestra el DNI completo "<dni_completo>"

    Ejemplos:
      | usuario   | nombres           | celular   | dni      | correo               | dni_completo |
      | Ana       | Ana Torres Quispe | 987654321 | ****8912 | ana.torres@correo.pe | 45678912     |
      | Carga 001 | Usuario Carga 001 | 900000001 | ****0001 | Sin correo           | 70000001     |

  @HU-N-04 @CA3 @CP-NW12
  Escenario: CP-NW12 Sin sesión o con la sesión vencida la web vuelve al ingreso
    Cuando abre el inicio sin sesión
    Entonces vuelve a la pantalla de ingreso sin ver su saldo
    Cuando ingresa como "Ana"
    Y pasan 30 minutos
    Y intenta abrir la pantalla de perfil
    Entonces vuelve al ingreso con el aviso "Tu sesión expiró o fue cerrada. Vuelve a ingresar."
    Y el navegador ya no guarda la sesión

  @HU-N-05 @CA1 @CP-NW13
  Escenario: CP-NW13 Editar nombres y correo desde la web
    Dado que "Ana" ingresó a Qolqe
    Y abre la pantalla de perfil
    Cuando guarda sus datos con nombres "Ana Lucía Torres" y correo "ANA.NUEVA@correo.pe"
    Entonces ve el mensaje de perfil "Tus datos fueron actualizados"
    Y el perfil muestra nombres "Ana Lucía Torres" y correo "ana.nueva@correo.pe"
    Y el menú muestra el nombre "Ana Lucía Torres"
    Cuando guarda sus datos con nombres "Ana Lucía Torres" y correo ""
    Entonces el perfil muestra nombres "Ana Lucía Torres" y correo "Sin correo"

  @HU-N-05 @CA1 @CP-NW14
  Esquema del escenario: CP-NW14 Los errores al editar el perfil se muestran y no cambian los datos
    Dado que "Ana" ingresó a Qolqe
    Y abre la pantalla de perfil
    Cuando guarda sus datos con nombres "<nombres>" y correo "<correo>"
    Entonces ve el mensaje de perfil "<mensaje>"
    Cuando abre la pantalla de perfil
    Entonces el perfil muestra nombres "Ana Torres Quispe" y correo "ana.torres@correo.pe"

    Ejemplos:
      | caso                  | nombres           | correo               | mensaje                                         |
      | correo de otra cuenta | Ana Torres Quispe | bruno.diaz@correo.pe | El correo ya está registrado en otra cuenta     |
      | nombres de 1 letra    | A                 | ana.torres@correo.pe | Los nombres deben tener entre 2 y 80 caracteres |

  @HU-N-05 @CA2 @CP-NW15
  Escenario: CP-NW15 El formulario de perfil no permite editar el DNI ni el celular
    Dado que "Ana" ingresó a Qolqe
    Cuando abre la pantalla de perfil
    Entonces solo puede editar los nombres y el correo
