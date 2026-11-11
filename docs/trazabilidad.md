# Matriz de trazabilidad · núcleo y G4

Generada por `.github/scripts/trazabilidad.py` a partir de las etiquetas de `features/` y los JUnit XML del pipeline.

Run **#local** (intento 1) · commit `11b3537` · local · entrega-final · evidencia: sin-imagenes · veredicto: **success** · 2026-11-11 16:34 (hora de Lima) · **corrida local, fuera de GitHub Actions**: el job `reportes` del pipeline genera esta matriz en cada run (artefacto `trazabilidad`)

## Resumen por módulo, nivel y tipo

| Módulo | Nivel | Tipo | Casos | passed | xfailed | flaky | failed | skipped | sin ejecutar |
|---|---|---|---|---|---|---|---|---|---|
| núcleo | api | funcional | 101 | 88 | 13 | 0 | 0 | 0 | 0 |
| núcleo | api | técnico | 53 | 41 | 12 | 0 | 0 | 0 | 0 |
| núcleo | web | funcional | 27 | 26 | 1 | 0 | 0 | 0 | 0 |
| G4 | api | funcional | 97 | 89 | 8 | 0 | 0 | 0 | 0 |
| G4 | api | técnico | 25 | 19 | 6 | 0 | 0 | 0 | 0 |
| G4 | web | funcional | 31 | 31 | 0 | 0 | 0 | 0 | 0 |
| núcleo y G4 | contrato | técnico | 1 | 1 | 0 | 0 | 0 | 0 | 0 |

## Cobertura por historia

| HU | Historia | API | Web | Contrato | Técnicos | Resultados |
|---|---|---|---|---|---|---|
| HU-N-01 | Registrarme | 25 | 6 | 1 | 7 | 27 passed, 5 xfailed |
| HU-N-02 | Iniciar sesión | 21 | 5 | 1 | 6 | 25 passed, 2 xfailed |
| HU-N-03 | Cerrar sesión | 9 | 2 | 1 | 7 | 8 passed, 4 xfailed |
| HU-N-04 | Consultar mi saldo y perfil | 11 | 4 | 1 | 7 | 15 passed, 1 xfailed |
| HU-N-05 | Editar mi perfil | 12 | 3 | 1 | 3 | 16 passed |
| HU-N-06 | Cerrar mi cuenta | 17 | 3 | 1 | 7 | 19 passed, 2 xfailed |
| HU-N-07 | Transferir a otro usuario Qolqe | 42 | 3 | 1 | 19 | 36 passed, 10 xfailed |
| HU-N-08 | Transferir a otro banco | 13 | 2 | 1 | 5 | 13 passed, 3 xfailed |
| HU-N-09 | Simular la comisión | 8 | 2 | 1 | 5 | 10 passed, 1 xfailed |
| HU-G4-01 | Agregar un contacto | 25 | 4 | 1 | 10 | 24 passed, 6 xfailed |
| HU-G4-02 | Ver y buscar mis contactos | 18 | 5 | 1 | 8 | 22 passed, 2 xfailed |
| HU-G4-03 | Editar un contacto | 25 | 3 | 1 | 15 | 24 passed, 5 xfailed |
| HU-G4-04 | Eliminar un contacto | 19 | 2 | 1 | 10 | 21 passed, 1 xfailed |
| HU-G4-05 | Transferir a un contacto | 6 | 2 | 1 | 2 | 8 passed, 1 xfailed |
| HU-G4-06 | Solicitar dinero a un contacto | 20 | 6 | 1 | 9 | 25 passed, 2 xfailed |
| HU-G4-07 | Ver mis solicitudes | 15 | 5 | 1 | 8 | 20 passed, 1 xfailed |
| HU-G4-08 | Aceptar una solicitud recibida | 25 | 6 | 1 | 13 | 28 passed, 4 xfailed |
| HU-G4-09 | Rechazar una solicitud recibida | 16 | 2 | 1 | 10 | 18 passed, 1 xfailed |
| HU-G4-10 | Cancelar una solicitud enviada | 13 | 3 | 1 | 8 | 16 passed, 1 xfailed |

## Núcleo: HU → caso → resultado

| HU | CA | Caso | Título | Nivel | Tipo | Resultado |
|---|---|---|---|---|---|---|
| HU-N-01 | CA1 | CP-NA01 | Registro válido crea la cuenta con saldo S/ 0.00 y límite S/ 2,000.00 | api | funcional | passed (1/1) |
| HU-N-01 | CA1 | CP-NA02 | El correo es opcional: omitido, vacío, solo espacios o nulo | api | funcional | passed (4/4) |
| HU-N-01 | CA1 | CP-NA03 | Longitud de nombres en el registro | api | funcional | passed (4/4) |
| HU-N-01 | CA1 | CP-NA04 | Nombres que quedan vacíos o de 1 carácter tras recortar | api | funcional | xfailed → DEF-13 |
| HU-N-01 | CA1 | CP-NA05 | Cuerpo incompleto, tipos incorrectos o JSON inválido | api | técnico | passed (10/10) |
| HU-N-01 | CA1 | CP-NA06 | Los campos que no son del registro se ignoran | api | técnico | passed (1/1) |
| HU-N-01 | CA1 | CP-NA07 | Un DNI ya usado por otra cuenta se acepta (sin unicidad de DNI) | api | funcional | passed (1/1) |
| HU-N-01 | CA2 | CP-NA08 | Longitud del DNI | api | funcional | passed (4/4) |
| HU-N-01 | CA2 | CP-NA09 | DNI con caracteres no numéricos | api | funcional | passed (3/3) |
| HU-N-01 | CA3 | CP-NA10 | Formato del celular | api | funcional | passed (7/7) |
| HU-N-01 | CA3 | CP-NA11 | Celular ya registrado, incluso con la cuenta cerrada | api | funcional | passed (2/2) |
| HU-N-01 | CA3 | CP-NA12 | Registros simultáneos con el mismo celular | api | técnico | xfailed → DEF-14 |
| HU-N-01 | CA4 | CP-NA13 | Longitud del PIN | api | funcional | passed (3/3) |
| HU-N-01 | CA4 | CP-NA14 | Clases de PIN inválidas y válidas cercanas | api | funcional | passed (8/8) |
| HU-N-01 | CA4 | CP-NA15 | Se acepta un PIN con secuencia descendente | api | funcional | xfailed → DEF-12 |
| HU-N-01, HU-N-07 | CA1 | CP-NA159 | Un cuerpo con Content-Type text/plain no registra ni transfiere | api | técnico | passed (2/2) |
| HU-N-01 | CA5 | CP-NA16 | Formato del correo | api | funcional | passed (5/5) |
| HU-N-01, HU-N-07 | CA1 | CP-NA160 | Sin Content-Type o con Accept XML la API responde en JSON según el contrato | api | técnico | passed (4/4) |
| HU-N-01 | CA5 | CP-NA17 | Longitud máxima del correo | api | funcional | passed (2/2) |
| HU-N-01 | CA5 | CP-NA18 | Correo ya usado, sin distinguir mayúsculas | api | funcional | passed (1/1) |
| HU-N-01 | CA5 | CP-NA19 | Orden de los errores cuando fallan varios datos | api | funcional | passed (4/4) |
| HU-N-01 | CA5 | CP-NA20 | Registros simultáneos con el mismo correo | api | técnico | xfailed → DEF-15 |
| HU-N-01 | CA6 | CP-NA21 | El registro envía un SMS de bienvenida | api | funcional | passed (1/1) |
| HU-N-01 | CA6 | CP-NA22 | Un registro rechazado no envía SMS | api | funcional | passed (1/1) |
| HU-N-01 | CA5 | CP-NA75 | El correo de una cuenta cerrada queda libre | api | funcional | passed (1/1) |
| HU-N-01 | CA1 | CP-NW01 | Alta de cuenta desde la web y primer ingreso | web | funcional | passed (3/3) |
| HU-N-01 | CA1 | CP-NW02 | Si el PIN y su confirmación no coinciden no se envía el registro | web | funcional | passed (3/3) |
| HU-N-01 | CA1 | CP-NW03 | Con nombres de 1 letra el error se muestra en español | web | funcional | xfailed → DEF-18 |
| HU-N-01 | CA3 | CP-NW04 | Con un celular ya registrado se muestra el error y se conserva el formulario | web | funcional | passed (3/3) |
| HU-N-01 | CA2, CA4, CA5 | CP-NW25 | El registro muestra el error de la API y no crea la cuenta | web | funcional | passed (15/15) |
| HU-N-01 | CA2, CA3, CA4 | CP-NW26 | Los campos numéricos del registro no admiten más dígitos que los permitidos | web | funcional | passed (9/9) |
| HU-N-02 | CA2 | CP-NA157 | Celular inexistente y PIN incorrecto responden igual en estado, cuerpo y cabeceras | api | técnico | passed (1/1) |
| HU-N-02 | CA1 | CP-NA23 | El ingreso correcto entrega un token de 30 minutos y crea la sesión | api | funcional | passed (1/1) |
| HU-N-02 | CA1 | CP-NA24 | Vigencia del token en el borde de los 30 minutos | api | funcional | passed (1/1) |
| HU-N-02 | CA1 | CP-NA25 | Cada ingreso crea una sesión independiente | api | funcional | passed (1/1) |
| HU-N-02 | CA1 | CP-NA26 | Solicitudes de ingreso mal formadas | api | técnico | passed (6/6) |
| HU-N-02 | CA2 | CP-NA27 | Mensaje genérico ante credenciales inválidas | api | funcional | passed (3/3) |
| HU-N-02 | CA3 | CP-NA29 | El tercer fallo consecutivo bloquea la cuenta y avisa por SMS | api | funcional | passed (1/1) |
| HU-N-02 | CA3 | CP-NA30 | Un ingreso exitoso reinicia el conteo de intentos fallidos | api | funcional | xfailed → DEF-10 |
| HU-N-02 | CA3 | CP-NA31 | Los intentos durante el bloqueo no envían más SMS | api | funcional | passed (1/1) |
| HU-N-02 | CA3 | CP-NA32 | Los fallos de un usuario no cuentan para otro | api | funcional | passed (1/1) |
| HU-N-02 | CA3 | CP-NA33 | Los intentos fallidos simultáneos también deben bloquear | api | técnico | xfailed → DEF-11 |
| HU-N-02 | CA4 | CP-NA34 | Durante el bloqueo ningún PIN permite ingresar | api | funcional | passed (1/1) |
| HU-N-02 | CA4 | CP-NA35 | El bloqueo dura exactamente 15 minutos | api | funcional | passed (1/1) |
| HU-N-02 | CA4 | CP-NA36 | Elena, bloqueada en la semilla, ingresa al vencer el bloqueo | api | funcional | passed (1/1) |
| HU-N-02 | CA4 | CP-NA37 | Tras vencer el bloqueo, el conteo empieza de nuevo | api | funcional | passed (1/1) |
| HU-N-02 | CA5 | CP-NA38 | La cuenta cerrada solo revela su estado si el PIN es correcto | api | funcional | passed (2/2) |
| HU-N-02 | CA5 | CP-NA39 | Una cuenta que se cierra deja de poder ingresar | api | funcional | passed (1/1) |
| HU-N-02 | CA6 | CP-NA40 | El ingreso desde un dispositivo de confianza no envía alerta | api | funcional | passed (1/1) |
| HU-N-02 | CA6 | CP-NA41 | El ingreso desde un dispositivo nuevo envía alerta | api | funcional | passed (1/1) |
| HU-N-02 | CA6 | CP-NA42 | El dispositivo de confianza de otro usuario cuenta como nuevo | api | técnico | passed (1/1) |
| HU-N-02 | CA6 | CP-NA43 | Casos borde del identificador de dispositivo | api | técnico | passed (5/5) |
| HU-N-02 | CA1 | CP-NW05 | El ingreso correcto lleva al inicio | web | funcional | passed (3/3) |
| HU-N-02 | CA2 | CP-NW06 | El error de ingreso es genérico y limpia el PIN | web | funcional | passed (6/6) |
| HU-N-02 | CA3, CA4 | CP-NW07 | La web informa el bloqueo con su hora y ofrece el desbloqueo | web | funcional | passed (6/6) |
| HU-N-02 | CA6 | CP-NW08 | El ingreso envía el dispositivo recordado y solo alerta si no es de confianza | web | funcional | passed (6/6) |
| HU-N-06, HU-N-02 | CA4, CA5 | CP-NW17 | Cerrar la cuenta desde Mi perfil impide volver a ingresar | web | funcional | passed (3/3) |
| HU-N-03 | CA1 | CP-NA44 | Después del logout el token ya no debe servir | api | funcional | xfailed → DEF-09 |
| HU-N-03 | — | CP-NA45 | La sesión cerrada debe desaparecer de mis sesiones activas | api | técnico | xfailed → DEF-09 |
| HU-N-03 | CA1 | CP-NA46 | Un segundo logout con el mismo token debe ser rechazado | api | técnico | xfailed → DEF-09 |
| HU-N-03 | CA1 | CP-NA47 | Logout sin token, con token inválido o vencido | api | técnico | passed (3/3) |
| HU-N-03 | — | CP-NA48 | Cerrar la sesión desde Seguridad sí invalida el token | api | técnico | passed (1/1) |
| HU-N-03 | CA2 | CP-NA49 | La otra sesión del mismo usuario sigue activa | api | funcional | passed (1/1) |
| HU-N-03 | CA2 | CP-NA50 | El logout de un usuario no afecta a otro | api | técnico | passed (1/1) |
| HU-N-03 | CA2 | CP-NA51 | Después del logout puedo volver a ingresar | api | funcional | passed (1/1) |
| HU-N-03 | CA1 | CP-NW09 | Cerrar sesión desde el menú borra la sesión del navegador | web | funcional | passed (3/3) |
| HU-N-03 | CA2 | CP-NW27 | Cerrar sesión en un navegador no cierra la sesión del otro | web | funcional | passed (3/3) |
| HU-N-04 | CA2 | CP-NA158 | El DNI completo no aparece en ninguna respuesta de la cuenta | api | técnico | passed (1/1) |
| HU-N-04 | CA1 | CP-NA52 | Consultar mi saldo | api | funcional | passed (1/1) |
| HU-N-04 | CA1 | CP-NA53 | El saldo y su fecha cambian con cada operación | api | funcional | passed (1/1) |
| HU-N-04 | CA1 | CP-NA54 | Formato del saldo en los bordes | api | funcional | passed (4/4) |
| HU-N-04 | CA1 | CP-NA55 | Cada token ve solo su propio saldo y no hay ruta para la cuenta de otro | api | técnico | passed (1/1) |
| HU-N-04 | CA2 | CP-NA56 | Consultar mi perfil con el DNI enmascarado | api | funcional | passed (1/1) |
| HU-N-04 | CA2 | CP-NA57 | Perfil de un usuario sin correo | api | funcional | passed (2/2) |
| HU-N-04 | CA3 | CP-NA58 | Credenciales ausentes o inválidas | api | técnico | passed (7/7) |
| HU-N-04 | CA3 | CP-NA59 | Token vencido o de una sesión cerrada | api | técnico | passed (2/2) |
| HU-N-04 | CA3 | CP-NA60 | Un token forjado con la clave por defecto y sub no numérico | api | técnico | xfailed → DEF-17 |
| HU-N-04 | CA3 | CP-NA61 | Editar el perfil sin token no cambia nada | api | técnico | passed (1/1) |
| HU-N-04 | CA1 | CP-NW10 | El inicio muestra el saldo con formato y permite ocultarlo | web | funcional | passed (3/3) |
| HU-N-04 | CA2 | CP-NW11 | El perfil muestra los datos con el DNI enmascarado | web | funcional | passed (6/6) |
| HU-N-04 | CA3 | CP-NW12 | Sin sesión o con la sesión vencida la web vuelve al ingreso | web | funcional | passed (3/3) |
| HU-N-05 | CA1 | CP-NA62 | Longitud de nombres al editar | api | funcional | passed (6/6) |
| HU-N-05 | CA1 | CP-NA63 | Nombres vacíos o nulos al editar | api | funcional | passed (3/3) |
| HU-N-05 | CA1 | CP-NA64 | Tipos incorrectos al editar | api | técnico | passed (4/4) |
| HU-N-05 | CA1 | CP-NA65 | Formato inválido del correo al editar | api | funcional | passed (3/3) |
| HU-N-05 | CA1 | CP-NA66 | Unicidad del correo entre cuentas activas al editar | api | funcional | passed (1/1) |
| HU-N-05 | CA1 | CP-NA67 | Quitar el correo lo libera para otra cuenta | api | funcional | passed (1/1) |
| HU-N-05 | CA1 | CP-NA68 | Un error al editar no deja cambios a medias | api | funcional | passed (2/2) |
| HU-N-05 | CA2 | CP-NA70 | El DNI y el celular enviados junto con nombres se ignoran | api | funcional | passed (1/1) |
| HU-N-05 | CA2 | CP-NA71 | Enviar solo DNI y celular no cambia nada ni avisa | api | técnico | passed (1/1) |
| HU-N-05 | CA3 | CP-NA72 | Cambiar el correo envía un SMS con el correo nuevo | api | funcional | passed (1/1) |
| HU-N-05 | CA3 | CP-NA73 | Sin cambio del correo guardado no hay SMS | api | funcional | passed (4/4) |
| HU-N-05 | CA3 | CP-NA74 | Quitar o agregar correo también avisa | api | funcional | passed (2/2) |
| HU-N-05 | CA1 | CP-NW13 | Editar nombres y correo desde la web | web | funcional | passed (3/3) |
| HU-N-05 | CA1 | CP-NW14 | Los errores al editar el perfil se muestran y no cambian los datos | web | funcional | passed (6/6) |
| HU-N-05 | CA2 | CP-NW15 | El formulario de perfil no permite editar el DNI ni el celular | web | funcional | passed (3/3) |
| HU-N-06 | CA1 | CP-NA80 | Un PIN incorrecto no cierra la cuenta | api | funcional | passed (1/1) |
| HU-N-06 | CA1 | CP-NA81 | Un PIN que no tiene 4 dígitos se responde como incorrecto | api | técnico | passed (3/3) |
| HU-N-06 | CA1 | CP-NA82 | Cuerpo del cierre ausente, mal formado o con tipos inválidos | api | técnico | passed (5/5) |
| HU-N-06 | CA1 | CP-NA83 | Cerrar la cuenta exige un token vigente | api | técnico | passed (5/5) |
| HU-N-06 | CA1 | CP-NA84 | Los PIN errados al cerrar la cuenta no bloquean el ingreso (riesgo: el cierre revela el PIN) | api | técnico | passed (1/1) |
| HU-N-06 | CA2 | CP-NA85 | Valores límite del saldo: solo se cierra con S/ 0.00 exactos | api | funcional | passed (3/3) |
| HU-N-06 | CA1, CA2, CA3 | CP-NA86 | Tabla de decisión del cierre: PIN, saldo y solicitudes pendientes | api | técnico | passed (7/7) |
| HU-N-06 | CA3 | CP-NA87 | Una solicitud pendiente, enviada o recibida, impide cerrar la cuenta | api | funcional | passed (2/2) |
| HU-N-06 | CA3 | CP-NA88 | Una solicitud ya resuelta no impide cerrar la cuenta | api | funcional | passed (3/3) |
| HU-N-06 | CA3 | CP-NA89 | Frontera de las 48 horas: al vencer, la solicitud deja de impedir el cierre | api | funcional | passed (2/2) |
| HU-N-06 | CA3 | CP-NA90 | Una solicitud vencida de la semilla no impide cerrar la cuenta | api | funcional | passed (1/1) |
| HU-N-06 | CA4 | CP-NA91 | Cerrar la cuenta cierra todas sus sesiones y avisa por SMS | api | funcional | passed (1/1) |
| HU-N-06 | CA4 | CP-NA92 | Una cuenta cerrada no puede volver a ingresar | api | funcional | passed (2/2) |
| HU-N-06 | CA4 | CP-NA93 | El celular de una cuenta cerrada no se puede registrar otra vez | api | funcional | passed (1/1) |
| HU-N-06 | CA4 | CP-NA94 | Nadie puede transferir a una cuenta recién cerrada | api | funcional | xfailed → DEF-04 |
| HU-N-06 | CA4 | CP-NA95 | Aceptar la solicitud de una cuenta cerrada no le transfiere dinero | api | funcional | xfailed → DEF-03 |
| HU-N-06 | CA4 | CP-NA96 | El token de una cuenta cerrada ya no sirve en ningún endpoint | api | técnico | passed (5/5) |
| HU-N-06 | CA1, CA2, CA3 | CP-NW16 | Si el cierre no procede, el diálogo muestra el error y la cuenta sigue activa | web | funcional | passed (9/9) |
| HU-N-06 | CA4 | CP-NW18 | Al cerrar la cuenta, la sesión abierta en otro navegador se cierra | web | funcional | passed (3/3) |
| HU-N-07 | CA1 | CP-NA100 | Sin descripción se usa el texto por defecto | api | funcional | passed (3/3) |
| HU-N-07 | CA1 | CP-NA101 | Valores límite y clases del celular de destino | api | funcional | passed (5/5) |
| HU-N-07 | CA1 | CP-NA102 | El contacto de otro usuario responde como inexistente | api | técnico | passed (1/1) |
| HU-N-07 | CA1 | CP-NA103 | Identificador de contacto inexistente, ausente o fuera de rango | api | técnico | passed (5/5) |
| HU-N-07 | CA1 | CP-NA104 | Un contacto_id booleano se rechaza como tipo inválido | api | técnico | xfailed → DEF-28 |
| HU-N-07 | CA1 | CP-NA105 | Formas válidas del cuerpo y valores por defecto | api | técnico | passed (5/5) |
| HU-N-07 | CA1 | CP-NA106 | Cuerpo mal formado o con tipos inválidos | api | técnico | passed (15/15) |
| HU-N-07 | CA1 | CP-NA107 | Si se indican contacto y celular, prima el contacto | api | técnico | passed (1/1) |
| HU-N-07 | CA1 | CP-NA108 | Transferir exige un token vigente, y el 401 tiene prioridad sobre el 422 | api | técnico | passed (6/6) |
| HU-N-07 | CA2 | CP-NA109 | RN-05 valores límite válidos del monto por operación | api | funcional | passed (4/4) |
| HU-N-07 | CA2 | CP-NA110 | RN-05 montos no válidos por operación | api | funcional | passed (8/8) |
| HU-N-07 | CA2 | CP-NA111 | RN-07 no se transfiere a sí mismo ni a un celular no registrado | api | funcional | passed (3/3) |
| HU-N-07 | CA2 | CP-NA112 | RN-07 no se transfiere por celular a una cuenta cerrada | api | funcional | xfailed → DEF-04 |
| HU-N-07 | CA2 | CP-NA113 | RN-08 valores límite del saldo disponible | api | funcional | passed (3/3) |
| HU-N-07 | CA2 | CP-NA114 | RN-08 con el saldo en cero no se transfiere ni un céntimo | api | funcional | passed (1/1) |
| HU-N-07 | CA2 | CP-NA115 | RN-06 valores límite del límite diario por defecto y del usuario | api | funcional | passed (4/4) |
| HU-N-07 | CA2 | CP-NA116 | RN-06 con el límite diario agotado se rechaza un céntimo más | api | funcional | passed (1/1) |
| HU-N-07 | CA2 | CP-NA117 | RN-06 el límite diario suma también las transferencias interbancarias | api | funcional | xfailed → DEF-20 |
| HU-N-07 | CA2 | CP-NA118 | RN-06 una interbancaria se rechaza si las Qolqe ya agotaron el límite | api | funcional | passed (1/1) |
| HU-N-07 | CA2 | CP-NA119 | RN-06 una reducción del límite diario rige de inmediato | api | funcional | passed (1/1) |
| HU-N-07 | CA2 | CP-NA120 | RN-06 un aumento del límite diario rige recién a las 24 horas | api | funcional | passed (2/2) |
| HU-N-07 | CA2 | CP-NA121 | RN-06 el límite diario se reinicia a las 00:00 de Lima | api | funcional | passed (2/2) |
| HU-N-07 | CA2 | CP-NA122 | Tabla de decisión del orden de validación cuando fallan varias reglas | api | técnico | passed (6/6) |
| HU-N-07 | CA3 | CP-NA123 | La transferencia debita al emisor y acredita al destinatario el mismo monto | api | funcional | passed (1/1) |
| HU-N-07 | CA3 | CP-NA124 | Emisor y destinatario ven su movimiento con el mismo código de operación | api | funcional | passed (1/1) |
| HU-N-07 | CA3 | CP-NA125 | El destinatario recibe un SMS con el monto y el código de operación | api | funcional | passed (1/1) |
| HU-N-07 | CA3 | CP-NA126 | RN-10 dos transferencias del mismo usuario en el mismo segundo tienen códigos distintos | api | funcional | xfailed → DEF-22 |
| HU-N-07 | CA3, CA5 | CP-NA127 | RN-10 transferencias simultáneas del mismo usuario reciben códigos distintos | api | técnico | xfailed → DEF-22 |
| HU-N-07 | CA3 | CP-NA128 | El emisor consulta por código el detalle de su transferencia | api | técnico | passed (1/1) |
| HU-N-07 | CA3 | CP-NA129 | El destinatario consulta por código su propio movimiento recibido | api | técnico | xfailed → DEF-24 |
| HU-N-07 | CA3 | CP-NA130 | Un tercero no puede ver por código el movimiento de otros | api | técnico | xfailed → DEF-24 |
| HU-N-07 | CA3, CA5 | CP-NA131 | Transferencias cruzadas simultáneas conservan el dinero total | api | técnico | passed (1/1) |
| HU-N-07 | CA4 | CP-NA132 | El comprobante de una transferencia Qolqe trae todos sus datos | api | funcional | passed (1/1) |
| HU-N-07 | CA4 | CP-NA133 | El comprobante enmascara el nombre del destinatario | api | funcional | passed (3/3) |
| HU-N-07 | CA5 | CP-NA134 | Transferencias simultáneas no dejan el saldo negativo | api | técnico | xfailed → DEF-21 |
| HU-N-07 | CA5 | CP-NA135 | Transferencias simultáneas no superan el límite diario | api | técnico | xfailed → DEF-21 |
| HU-N-07 | CA1 | CP-NA97 | Transferir por celular con una descripción | api | funcional | passed (1/1) |
| HU-N-07 | CA1 | CP-NA98 | Valores límite válidos de la descripción (hasta 60 caracteres) | api | funcional | passed (4/4) |
| HU-N-07 | CA1 | CP-NA99 | Una descripción de 61 caracteres se rechaza sin mover dinero | api | funcional | passed (2/2) |
| HU-N-07 | CA1, CA4 | CP-NW19 | Transferir por celular, confirmar y ver el comprobante | web | funcional | passed (3/3) |
| HU-N-07 | CA2 | CP-NW20 | La pantalla comunica los errores de monto y de saldo | web | funcional | passed (3/3) |
| HU-N-07 | CA3 | CP-NW21 | Emisor y destinatario ven el saldo y el movimiento en inicio | web | funcional | passed (3/3) |
| HU-N-08 | CA1 | CP-NA136 | Valores límite y clases del CCI | api | funcional | passed (7/7) |
| HU-N-08 | CA1 | CP-NA137 | CCI ausente, con espacios o de tipo inválido | api | técnico | passed (7/7) |
| HU-N-08 | CA1 | CP-NA138 | Transferencia interbancaria válida y su comprobante | api | funcional | passed (1/1) |
| HU-N-08 | CA1 | CP-NA139 | Los campos que no corresponden al tipo de transferencia se ignoran | api | técnico | passed (2/2) |
| HU-N-08 | CA1 | CP-NA140 | La transferencia interbancaria exige un token vigente | api | técnico | passed (4/4) |
| HU-N-08 | CA2 | CP-NA141 | RN-09 comisión cobrada en el mínimo, la zona proporcional y el tope | api | funcional | passed (9/9) |
| HU-N-08 | CA2 | CP-NA142 | RN-09 la comisión usa redondeo comercial cuando el tercer decimal es 5 | api | funcional | xfailed → DEF-23 |
| HU-N-08 | CA2 | CP-NA143 | RN-08 una interbancaria puede usar todo el saldo incluida la comisión | api | funcional | passed (1/1) |
| HU-N-08 | CA2 | CP-NA144 | RN-08 el saldo debe cubrir el monto más la comisión | api | funcional | xfailed → DEF-19 |
| HU-N-08 | CA2 | CP-NA145 | RN-05 valores límite del monto en una interbancaria | api | funcional | passed (5/5) |
| HU-N-08 | CA2 | CP-NA146 | RN-06 las transferencias interbancarias consumen el límite diario | api | funcional | xfailed → DEF-20 |
| HU-N-08 | CA3 | CP-NA147 | El movimiento interbancario muestra el CCI enmascarado | api | funcional | passed (1/1) |
| HU-N-08 | CA3 | CP-NA148 | El CCI completo no aparece en ninguna respuesta | api | técnico | passed (2/2) |
| HU-N-08 | CA1 | CP-NW22 | Un CCI de 19 dígitos se rechaza y no se debita nada | web | funcional | passed (3/3) |
| HU-N-08 | CA2, CA3 | CP-NW23 | Transferir a otro banco cobra la comisión y enmascara el CCI | web | funcional | passed (3/3) |
| HU-N-09 | CA1 | CP-NA149 | Simular una transferencia Qolqe no tiene comisión | api | funcional | passed (4/4) |
| HU-N-09 | CA1 | CP-NA150 | Simular una interbancaria en el mínimo, la zona proporcional y el tope | api | funcional | passed (11/11) |
| HU-N-09 | CA1 | CP-NA151 | La simulación usa redondeo comercial cuando el tercer decimal es 5 | api | funcional | xfailed → DEF-23 |
| HU-N-09 | CA1 | CP-NA152 | La simulación aplica RN-05 al monto | api | funcional | passed (5/5) |
| HU-N-09 | CA1 | CP-NA153 | Parámetros ausentes o de tipo inválido en la simulación | api | técnico | passed (7/7) |
| HU-N-09 | CA1 | CP-NA154 | Simular la comisión no mueve dinero ni registra operaciones | api | técnico | passed (1/1) |
| HU-N-09 | CA1 | CP-NA155 | La simulación coincide con lo que cobra la transferencia | api | técnico | passed (5/5) |
| HU-N-09 | CA1 | CP-NA156 | La simulación exige un token vigente y solo acepta GET | api | técnico | passed (6/6) |
| HU-N-09 | CA1 | CP-NW24 | La confirmación muestra la simulación y cancelar no transfiere | web | funcional | passed (3/3) |

## G4: HU → caso → resultado

| HU | CA | Caso | Título | Nivel | Tipo | Resultado |
|---|---|---|---|---|---|---|
| HU-G4-01 | CA1 | CP-A01 | Agregar un contacto válido normaliza el alias | api | funcional | passed (1/1) |
| HU-G4-01 | CA1 | CP-A02 | Rechazar un celular que no puede ser contacto | api | funcional | passed (6/6) |
| HU-G4-01 | CA1 | CP-A03 | Valores límite y clases válidas del alias | api | funcional | passed (3/3) |
| HU-G4-01 | CA1 | CP-A04 | El alias admite la letra ñ | api | funcional | xfailed → DEF-01 |
| HU-G4-01 | CA1 | CP-A05 | El alias es único sin distinguir mayúsculas | api | funcional | passed (1/1) |
| HU-G4-01 | CA1 | CP-A06 | El alias duplicado se detecta tras quitar los espacios | api | funcional | xfailed → DEF-02 |
| HU-G4-01 | CA1 | CP-A07 | Límite de 15 contactos | api | funcional | passed (1/1) |
| HU-G4-01 | CA1 | CP-A40 | El contacto agregado queda en la lista con celular, nombre enmascarado y sin favorito | api | funcional | passed (1/1) |
| HU-G4-01 | CA1 | CP-A41 | Clases válidas del alias después de quitar los espacios | api | funcional | passed (4/4) |
| HU-G4-01 | CA1 | CP-A42 | Particiones inválidas del celular | api | funcional | passed (6/6) |
| HU-G4-01, HU-G4-04 | CA1 | CP-A43 | Eliminar un contacto libera el cupo de 15 | api | funcional | passed (1/1) |
| HU-G4-01 | CA1 | CP-A77 | Un alta rechazada no agrega ningún contacto | api | funcional | passed (5/5) |
| HU-G4-01 | CA1 | CP-A78 | Clases inválidas del alias informan ALIAS_INVALIDO y no agregan nada | api | funcional | passed (8/8) |
| HU-G4-01 | CA1 | CP-A79 | El alias admite la letra Ñ mayúscula | api | funcional | xfailed → DEF-01 |
| HU-G4-01 | CA1 | CP-A81 | Una cuenta bloqueada pero activa sí puede ser contacto | api | funcional | passed (1/1) |
| HU-G4-01, HU-G4-04 | CA1 | CP-A86 | Un contacto eliminado se puede volver a agregar | api | funcional | passed (1/1) |
| HU-G4-01, HU-G4-02, HU-G4-03, HU-G4-04, HU-G4-06, HU-G4-07, HU-G4-08, HU-G4-09, HU-G4-10 | CA1 | CP-T05 | Sin un token Bearer válido ningún endpoint de G4 responde ni cambia datos | api | técnico | passed (36/36) |
| HU-N-03, HU-G4-01, HU-G4-02, HU-G4-03, HU-G4-04, HU-G4-06, HU-G4-07, HU-G4-08, HU-G4-09, HU-G4-10 | CA1 | CP-T07 | Después de cerrar sesión el token ya no sirve en G4 | api | técnico | xfailed → DEF-09 |
| HU-G4-01 | CA1 | CP-T11 | El alta de contacto con campos faltantes o de otro tipo nombra el campo | api | técnico | passed (9/9) |
| HU-G4-01, HU-G4-02, HU-G4-03, HU-G4-04, HU-G4-07, HU-G4-08 | CA1 | CP-T16 | Un método no permitido responde 405 con la cabecera Allow | api | técnico | passed (7/7) |
| HU-G4-01 | CA1 | CP-T20 | Cinco altas simultáneas del mismo celular crean un solo contacto | api | técnico | xfailed → DEF-26 |
| HU-G4-01, HU-G4-02, HU-G4-03, HU-G4-04, HU-G4-06, HU-G4-07, HU-G4-08, HU-G4-09, HU-G4-10 | CA1 | CP-T21 | Las respuestas cumplen el esquema y el tipo de contenido del contrato OpenAPI | api | técnico | passed (14/14) |
| HU-G4-01, HU-G4-03, HU-G4-06 | CA1 | CP-T25 | Los campos que no son del contrato se ignoran (asignación masiva) | api | técnico | passed (4/4) |
| HU-G4-01, HU-G4-03, HU-G4-06 | CA1 | CP-T29 | La cabecera Allow lista todos los métodos de la ruta | api | técnico | xfailed → DEF-06 |
| HU-G4-01, HU-G4-03, HU-G4-06, HU-G4-09 | CA1 | CP-T30 | Un JSON mal formado responde 422 SOLICITUD_INVALIDA sin cambiar datos | api | técnico | passed (4/4) |
| HU-G4-01 | CA1 | CP-W01 | Agregar un contacto desde la pantalla | web | funcional | passed (3/3) |
| HU-G4-01 | CA1 | CP-W02 | El error de la API se muestra al usuario | web | funcional | passed (3/3) |
| HU-G4-01, HU-G4-06, HU-G4-07, HU-G4-08 | CA1, CA3 | CP-W10 | Recorrido completo de una solicitud entre dos usuarios | web | funcional | passed (3/3) |
| HU-G4-01, HU-G4-06 | CA1 | CP-W30 | Un doble clic en Agregar o en Enviar solicitud crea un solo registro | web | funcional | passed (3/3) |
| HU-G4-02 | CA1 | CP-A08 | Favoritos primero, por alias y 10 por página | api | funcional | passed (1/1) |
| HU-G4-02 | CA2 | CP-A09 | Buscar sin distinguir mayúsculas ni tildes | api | funcional | passed (4/4) |
| HU-G4-02 | CA3 | CP-A10 | Cada contacto informa alias, nombre enmascarado, celular y favorito | api | funcional | passed (1/1) |
| HU-G4-02 | CA1 | CP-A44 | Valores límite de la paginación de 10 contactos | api | funcional | passed (5/5) |
| HU-G4-02 | CA1 | CP-A45 | Una página fuera de rango responde vacía (comportamiento no especificado) | api | funcional | passed (1/1) |
| HU-G4-02 | CA1 | CP-A46 | Varios favoritos van primero y todos se ordenan por alias sin distinguir mayúsculas | api | funcional | passed (1/1) |
| HU-G4-02 | CA1 | CP-A47 | Los alias que empiezan con tilde se ordenan con su letra | api | funcional | xfailed → DEF-27 |
| HU-G4-02 | CA2 | CP-A48 | La búsqueda recorta el texto y solo mira el alias | api | funcional | passed (6/6) |
| HU-G4-02 | CA3 | CP-A49 | Un contacto que no es favorito lo informa | api | funcional | passed (1/1) |
| HU-G4-02 | CA1 | CP-A82 | Un usuario sin contactos recibe una página vacía | api | funcional | passed (1/1) |
| HU-G4-02 | CA1, CA2 | CP-A83 | La búsqueda también se pagina de 10 en 10 | api | funcional | passed (1/1) |
| HU-G4-02, HU-G4-07, HU-G4-08 | CA1 | CP-T06 | El token vence a los 30 minutos del reloj de la aplicación | api | técnico | passed (3/3) |
| HU-G4-02 | CA1 | CP-T15 | Una página que no es un entero positivo informa query.pagina | api | técnico | passed (4/4) |
| HU-G4-02, HU-G4-07, HU-G4-08 | CA1 | CP-T22 | Un minuto antes de vencer, el token todavía sirve | api | técnico | passed (3/3) |
| HU-G4-02 | CA1 | CP-W03 | Favoritos primero, 10 por página y total visible | web | funcional | passed (3/3) |
| HU-G4-02 | CA2 | CP-W04 | Buscar sin tildes ni mayúsculas | web | funcional | passed (3/3) |
| HU-G4-02 | CA3 | CP-W05 | Cada contacto muestra alias, nombre enmascarado, celular y favorito | web | funcional | passed (3/3) |
| HU-G4-02 | CA1 | CP-W23 | La paginación deshabilita los extremos y se reajusta al vaciar la última página | web | funcional | passed (3/3) |
| HU-G4-03, HU-G4-02 | CA1 | CP-W24 | La estrella marca un favorito, lo sube al inicio y respeta el máximo de 5 | web | funcional | passed (3/3) |
| HU-G4-03 | CA1 | CP-A11 | Editar alias y favorito, sin compararlo consigo mismo | api | funcional | passed (1/1) |
| HU-G4-03 | CA1 | CP-A12 | Límite de 5 favoritos | api | funcional | passed (1/1) |
| HU-G4-03 | CA1 | CP-A13 | Editar con el alias de otro contacto | api | funcional | passed (1/1) |
| HU-G4-03 | CA1 | CP-A50 | Desmarcar un favorito lo devuelve al orden por alias | api | funcional | passed (1/1) |
| HU-G4-03 | CA1 | CP-A51 | Volver a marcar un favorito con 5 favoritos no cuenta como uno nuevo | api | funcional | passed (1/1) |
| HU-G4-03 | CA1 | CP-A52 | Solo se actualizan los campos enviados | api | funcional | passed (6/6) |
| HU-G4-03 | CA1 | CP-A53 | Un alias inválido al editar informa ALIAS_INVALIDO y no cambia el contacto | api | funcional | passed (6/6) |
| HU-G4-03 | CA1 | CP-A54 | Al editar, el alias duplicado se detecta tras quitar los espacios | api | funcional | xfailed → DEF-02 |
| HU-G4-03 | CA1 | CP-A80 | Editar el alias con la letra ñ | api | funcional | xfailed → DEF-01 |
| HU-G4-03 | CA1 | CP-A84 | Desmarcar un favorito libera el cupo para marcar otro | api | funcional | passed (1/1) |
| HU-G4-03 | CA1 | CP-A85 | Un alias válido al editar se guarda sin los espacios de los extremos | api | funcional | passed (3/3) |
| HU-G4-03, HU-G4-04 | CA1 | CP-T02 | El contacto de otro usuario responde como inexistente | api | técnico | passed (2/2) |
| HU-G4-03, HU-G4-04, HU-G4-09, HU-G4-10, HU-G4-08 | CA1, CA4 | CP-T08 | Un id inexistente o una solicitud ajena responde 404 sin cambiar datos | api | técnico | passed (7/7) |
| HU-G4-03, HU-G4-04, HU-G4-08, HU-G4-09, HU-G4-10 | CA1 | CP-T10 | Un id de ruta que no es entero informa el campo con error | api | técnico | passed (10/10) |
| HU-G4-03 | CA1 | CP-T12 | Editar un contacto con tipos inválidos nombra el campo | api | técnico | passed (5/5) |
| HU-G4-03, HU-G4-04, HU-G4-08, HU-G4-09, HU-G4-10 | CA1 | CP-T23 | Los ids 0 y negativos se tratan como inexistentes | api | técnico | passed (10/10) |
| HU-G4-03, HU-G4-04, HU-G4-08, HU-G4-09, HU-G4-10 | CA1 | CP-T24 | Un id fuera del rango de 64 bits no provoca un error del servidor | api | técnico | passed (5/5) |
| HU-G4-03 | CA1 | CP-T26 | favorito no acepta números aunque Pydantic los convierta | api | técnico | xfailed → DEF-08 |
| HU-G4-03 | CA1 | CP-W06 | Editar el alias y marcar como favorito | web | funcional | passed (3/3) |
| HU-G4-03 | CA1 | CP-W25 | Un error al editar se muestra en el diálogo y cancelar no guarda nada | web | funcional | passed (3/3) |
| HU-G4-04 | CA1 | CP-A14 | Eliminar un contacto conserva las transferencias | api | funcional | passed (1/1) |
| HU-G4-04 | CA2 | CP-A15 | No se elimina un contacto con solicitudes pendientes | api | funcional | passed (1/1) |
| HU-G4-04 | CA2 | CP-A16 | Una solicitud vencida no impide eliminar el contacto | api | funcional | passed (1/1) |
| HU-G4-04 | CA2 | CP-A55 | Una sola solicitud pendiente, enviada o recibida, impide eliminar | api | funcional | passed (2/2) |
| HU-G4-04 | CA2 | CP-A56 | Una solicitud ya resuelta no impide eliminar el contacto | api | funcional | passed (3/3) |
| HU-G4-04 | CA2 | CP-A57 | La pendiente deja de bloquear a las 48 horas exactas | api | funcional | passed (2/2) |
| HU-G4-04 | CA1 | CP-A58 | Eliminar un contacto no borra sus solicitudes ni el contacto inverso | api | funcional | passed (1/1) |
| HU-G4-04 | CA1 | CP-A87 | La transferencia a un contacto eliminado sigue en los movimientos de ambos | api | funcional | passed (1/1) |
| HU-G4-04 | CA1 | CP-W07 | Eliminar un contacto pide confirmación | web | funcional | passed (3/3) |
| HU-G4-04 | CA2 | CP-W08 | No se elimina un contacto con solicitudes pendientes | web | funcional | passed (3/3) |
| HU-G4-05 | CA1 | CP-A17 | Transferir eligiendo un contacto | api | funcional | passed (1/1) |
| HU-G4-05 | CA1 | CP-A18 | Transferir a un contacto con cuenta cerrada | api | funcional | xfailed → DEF-04 |
| HU-G4-05 | CA1 | CP-A59 | Transferir a un contacto aplica el saldo y el monto de HU-N-07 | api | funcional | passed (5/5) |
| HU-G4-05 | CA1 | CP-A60 | Transferir a un contacto avisa por SMS y deja el mismo código en ambos movimientos | api | funcional | passed (1/1) |
| HU-G4-05 | CA1 | CP-A88 | Transferir a un contacto respeta el límite diario | api | funcional | passed (1/1) |
| HU-G4-05, HU-G4-06 | CA1 | CP-T09 | Un contacto de otro usuario o inexistente no sirve para solicitar ni transferir | api | técnico | passed (4/4) |
| HU-G4-05 | CA1 | CP-W09 | Transferir eligiendo un contacto | web | funcional | passed (3/3) |
| HU-G4-05, HU-N-09 | CA1 | CP-W29 | Transferir eligiendo el contacto en la pantalla de transferencias | web | funcional | passed (3/3) |
| HU-G4-06 | CA2 | CP-A20 | Crear una solicitud pendiente que vence a las 48 horas y avisa por SMS | api | funcional | passed (1/1) |
| HU-G4-06 | CA1 | CP-A21 | Valores límite válidos del monto | api | funcional | passed (2/2) |
| HU-G4-06 | CA1 | CP-A22 | Valores límite válidos del motivo | api | funcional | passed (2/2) |
| HU-G4-06 | CA1 | CP-A23 | Máximo 10 solicitudes pendientes enviadas | api | funcional | passed (1/1) |
| HU-G4-06 | CA1 | CP-A24 | No se solicita a un contacto con cuenta cerrada | api | funcional | passed (1/1) |
| HU-G4-06 | CA1 | CP-A61 | Un monto o motivo inválido informa SOLICITUD_INVALIDA y no crea la solicitud | api | funcional | passed (8/8) |
| HU-G4-06 | CA1 | CP-A62 | Una solicitud que deja de estar pendiente libera el cupo de 10 | api | funcional | passed (4/4) |
| HU-G4-06 | CA2 | CP-A63 | La solicitud creada informa a los participantes y el SMS trae monto, motivo y vencimiento | api | funcional | passed (1/1) |
| HU-G4-06 | CA1 | CP-A89 | El monto se acepta como número o texto y el motivo se guarda sin espacios en los extremos | api | funcional | passed (6/6) |
| HU-G4-06 | CA1 | CP-A90 | Un motivo fuera de rango informa SOLICITUD_INVALIDA | api | funcional | passed (2/2) |
| HU-G4-06 | CA1 | CP-A91 | Las solicitudes recibidas no cuentan para el límite de 10 enviadas | api | funcional | passed (1/1) |
| HU-G4-06 | CA1 | CP-A92 | El límite de 10 suma las pendientes enviadas a distintos contactos | api | funcional | passed (1/1) |
| HU-G4-06 | CA1 | CP-T13 | Crear una solicitud con campos faltantes o de otro tipo nombra el campo | api | técnico | passed (13/13) |
| HU-G4-06 | CA1 | CP-W11 | Solicitar desde la lista de contactos | web | funcional | passed (3/3) |
| HU-G4-06 | CA1 | CP-W12 | Una solicitud inválida muestra el error y no se crea | web | funcional | passed (3/3) |
| HU-G4-06 | CA2 | CP-W13 | La solicitud creada queda pendiente con su vencimiento | web | funcional | passed (3/3) |
| HU-G4-06 | CA1 | CP-W26 | Sin elegir contacto la pantalla lo pide y no envía nada | web | funcional | passed (3/3) |
| HU-G4-07 | CA1 | CP-A25 | Enviadas y recibidas por separado, con filtro por estado | api | funcional | passed (1/1) |
| HU-G4-07 | CA1 | CP-A26 | Un filtro de estado desconocido se rechaza | api | funcional | passed (1/1) |
| HU-G4-07 | CA2 | CP-A27 | Vencimiento a las 48 horas exactas | api | funcional | passed (2/2) |
| HU-G4-07 | CA1 | CP-A64 | Cada filtro de estado devuelve solo sus solicitudes, enviadas y recibidas | api | funcional | passed (10/10) |
| HU-G4-07 | CA2 | CP-A65 | Una solicitud resuelta no pasa a VENCIDA con el tiempo | api | funcional | passed (1/1) |
| HU-G4-07 | CA1 | CP-A66 | Cada usuario ve solo sus solicitudes y la misma solicitud se ve igual desde ambos lados | api | funcional | passed (1/1) |
| HU-G4-07 | CA1 | CP-A67 | El filtro distingue mayúsculas y no admite un valor vacío | api | funcional | passed (4/4) |
| HU-G4-07 | CA1 | CP-A93 | Sin filtro aparecen todas, de la más reciente a la más antigua | api | funcional | passed (1/1) |
| HU-G4-07 | — | CP-T28 | Una ruta inexistente responde 404 con el formato de error | api | técnico | passed (2/2) |
| HU-G4-07 | CA1 | CP-W14 | Enviadas y recibidas por separado, con filtro por estado | web | funcional | passed (3/3) |
| HU-G4-07, HU-G4-08 | CA2, CA4 | CP-W15 | Una solicitud vencida se muestra como Vencida y sin acciones | web | funcional | passed (3/3) |
| HU-G4-10, HU-G4-07 | CA1, CA2 | CP-W22 | Una solicitud enviada vencida no ofrece cancelar | web | funcional | passed (3/3) |
| HU-G4-07 | CA1 | CP-W27 | Los contadores de pendientes se actualizan al rechazar una solicitud | web | funcional | passed (3/3) |
| HU-G4-08 | CA1, CA3 | CP-A28 | Aceptar transfiere el dinero y deja el código de operación | api | funcional | passed (1/1) |
| HU-G4-08 | CA2 | CP-A29 | Sin saldo la solicitud sigue pendiente | api | funcional | passed (1/1) |
| HU-G4-08 | CA2 | CP-A30 | Sobre el límite diario la solicitud sigue pendiente | api | funcional | passed (1/1) |
| HU-G4-08 | CA4 | CP-A31 | Solo el destinatario puede aceptar | api | funcional | passed (2/2) |
| HU-G4-08 | CA4 | CP-A32 | Una solicitud vencida no se puede aceptar | api | funcional | xfailed → DEF-03 |
| HU-G4-08 | CA4 | CP-A33 | Una solicitud ya aceptada no se acepta dos veces | api | funcional | passed (1/1) |
| HU-G4-08 | CA1, CA3 | CP-A68 | Aceptar deja el mismo código en la solicitud, en ambos movimientos y en el SMS | api | funcional | passed (1/1) |
| HU-G4-08 | CA1 | CP-A69 | Se puede aceptar con un saldo exactamente igual al monto | api | funcional | passed (1/1) |
| HU-G4-08 | CA1 | CP-A70 | Lo aceptado cuenta para el límite diario de quien paga | api | funcional | passed (1/1) |
| HU-G4-08 | CA4 | CP-A71 | Una solicitud rechazada o cancelada no se puede aceptar | api | funcional | passed (2/2) |
| HU-G4-08 | CA1 | CP-A94 | Se puede aceptar si se alcanza exactamente el límite diario | api | funcional | passed (1/1) |
| HU-G4-08 | CA2 | CP-A95 | Sin saldo no hay SMS de aceptación ni movimientos | api | funcional | passed (1/1) |
| HU-G4-08 | CA2 | CP-A96 | Sobre el límite diario no hay SMS de aceptación ni movimientos | api | funcional | passed (1/1) |
| HU-G4-08 | CA1, CA4 | CP-T17 | Tres aceptaciones simultáneas de la misma solicitud debitan una sola vez | api | técnico | xfailed → DEF-25 |
| HU-G4-08, HU-N-07 | CA1, CA5 | CP-T18 | Aceptar a la vez dos solicitudes que juntas superan el saldo no lo deja negativo | api | técnico | xfailed → DEF-21 |
| HU-G4-08 | CA1, CA3 | CP-W16 | Aceptar pide confirmación e informa la transferencia | web | funcional | passed (3/3) |
| HU-G4-08 | CA2 | CP-W17 | Sin saldo se muestra el error y la solicitud sigue pendiente | web | funcional | passed (3/3) |
| HU-G4-08 | CA1, CA2 | CP-W20 | Cancelar la confirmación de aceptar no transfiere | web | funcional | passed (3/3) |
| HU-G4-08, HU-G4-10 | CA4, CA1 | CP-W21 | Aceptar una solicitud que el solicitante ya canceló muestra el error y refresca la lista | web | funcional | passed (3/3) |
| HU-G4-09 | CA1 | CP-A34 | Rechazar con motivo opcional de hasta 60 caracteres | api | funcional | passed (2/2) |
| HU-G4-09 | CA1 | CP-A35 | Rechazar cambia el estado y avisa al solicitante sin mover dinero | api | funcional | passed (1/1) |
| HU-G4-09 | CA1 | CP-A36 | Una solicitud vencida no se puede rechazar | api | funcional | passed (1/1) |
| HU-G4-09 | CA1 | CP-A72 | Solo el destinatario puede rechazar | api | funcional | passed (2/2) |
| HU-G4-09 | CA1 | CP-A73 | Una solicitud aceptada, rechazada o cancelada no se puede rechazar | api | funcional | passed (3/3) |
| HU-G4-09 | CA1 | CP-A74 | El motivo del rechazo es opcional, se recorta y llega en el SMS | api | funcional | passed (7/7) |
| HU-G4-09 | CA1 | CP-A97 | Un motivo de rechazo de 61 caracteres informa SOLICITUD_INVALIDA y no rechaza | api | funcional | passed (1/1) |
| HU-G4-09 | CA1 | CP-T14 | Rechazar con un motivo que no es texto no cambia la solicitud | api | técnico | passed (3/3) |
| HU-G4-09 | CA1 | CP-W18 | Rechazar con motivo | web | funcional | passed (3/3) |
| HU-G4-09 | CA1 | CP-W31 | Un motivo de rechazo de 61 caracteres muestra el error en el diálogo | web | funcional | passed (3/3) |
| HU-G4-10 | CA1 | CP-A37 | El solicitante cancela una solicitud pendiente | api | funcional | passed (1/1) |
| HU-G4-10 | CA1 | CP-A39 | Una solicitud ya aceptada no se puede cancelar | api | funcional | passed (1/1) |
| HU-G4-10 | CA1 | CP-A75 | Una solicitud rechazada o ya cancelada no se puede cancelar | api | funcional | passed (2/2) |
| HU-G4-10 | CA1 | CP-A76 | Al cancelar, el destinatario la ve CANCELADA y no se mueve dinero | api | funcional | passed (1/1) |
| HU-G4-10 | CA1 | CP-A98 | Una solicitud vencida no se puede cancelar | api | funcional | passed (1/1) |
| HU-G4-10 | CA1 | CP-A99 | Cancelar una solicitud ajena informa SOLICITUD_NO_ENCONTRADA y no la cambia | api | funcional | passed (2/2) |
| HU-G4-10 | CA1 | CP-W19 | Cancelar una solicitud enviada pide confirmación | web | funcional | passed (3/3) |
| HU-N-04 | CA3 | CP-W28 | Con la sesión vencida, la pantalla de solicitudes vuelve al ingreso | web | funcional | passed (3/3) |

## Contrato (CP-T04): operación → resultado

| Operación | HU | Resultado |
|---|---|---|
| POST /api/auth/login | HU-N-02 | passed |
| POST /api/auth/logout | HU-N-03 | passed |
| POST /api/contactos | HU-G4-01 | passed |
| POST /api/cuentas/me/cierre | HU-N-06 | passed |
| POST /api/usuarios | HU-N-01 | passed |
| PUT /api/cuentas/me | HU-N-05 | passed |
| GET /api/contactos | HU-G4-02 | passed |
| GET /api/cuentas/me | HU-N-04 | passed |
| GET /api/cuentas/me/saldo | HU-N-04 | passed |
| GET /api/seguridad/sesiones | HU-N-02, HU-N-03 | passed |
| GET /api/solicitudes | HU-G4-07 | passed |
| GET /api/transferencias/comision | HU-N-09 | passed |
| PUT /api/contactos/{contacto_id} | HU-G4-03 | passed |
| POST /api/solicitudes | HU-G4-06 | passed |
| POST /api/transferencias | HU-G4-05, HU-N-07, HU-N-08 | passed |
| DELETE /api/contactos/{contacto_id} | HU-G4-04 | passed |
| POST /api/solicitudes/{solicitud_id}/aceptar | HU-G4-08 | passed |
| POST /api/solicitudes/{solicitud_id}/cancelar | HU-G4-10 | passed |
| POST /api/solicitudes/{solicitud_id}/rechazar | HU-G4-09 | passed |
| Stateful tests | — | passed |

## Defectos → casos

| Defecto | Casos (estado en este run) |
|---|---|
| DEF-01 | CP-A04 (xfailed), CP-A79 (xfailed), CP-A80 (xfailed) |
| DEF-02 | CP-A06 (xfailed), CP-A54 (xfailed) |
| DEF-03 | CP-A32 (xfailed), CP-NA95 (xfailed) |
| DEF-04 | CP-A18 (xfailed), CP-NA112 (xfailed), CP-NA94 (xfailed) |
| DEF-06 | CP-T29 (xfailed) |
| DEF-08 | CP-T26 (xfailed) |
| DEF-09 | CP-NA44 (xfailed), CP-NA45 (xfailed), CP-NA46 (xfailed), CP-T07 (xfailed) |
| DEF-10 | CP-NA30 (xfailed) |
| DEF-11 | CP-NA33 (xfailed) |
| DEF-12 | CP-NA15 (xfailed) |
| DEF-13 | CP-NA04 (xfailed) |
| DEF-14 | CP-NA12 (xfailed) |
| DEF-15 | CP-NA20 (xfailed) |
| DEF-17 | CP-NA60 (xfailed) |
| DEF-18 | CP-NW03 (xfailed) |
| DEF-19 | CP-NA144 (xfailed) |
| DEF-20 | CP-NA117 (xfailed), CP-NA146 (xfailed) |
| DEF-21 | CP-NA134 (xfailed), CP-NA135 (xfailed), CP-T18 (xfailed) |
| DEF-22 | CP-NA126 (xfailed), CP-NA127 (xfailed) |
| DEF-23 | CP-NA142 (xfailed), CP-NA151 (xfailed) |
| DEF-24 | CP-NA129 (xfailed), CP-NA130 (xfailed) |
| DEF-25 | CP-T17 (xfailed) |
| DEF-26 | CP-T20 (xfailed) |
| DEF-27 | CP-A47 (xfailed) |
| DEF-28 | CP-NA104 (xfailed) |

Los casos web se ejecutan 3 veces seguidas: `passed (3/3)` indica las tres pasadas. Un esquema de escenario cuenta cada ejemplo. `xfailed → DEF-xx` es un fallo esperado enlazado a `docs/defectos.md`. `flaky` alternó entre pasar y fallar. `sin ejecutar` es un caso diseñado que no corrió en este run.
