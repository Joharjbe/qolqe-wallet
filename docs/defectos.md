# Reporte de defectos · núcleo y G4

Entorno común: Qolqe (`qolqe/` sin modificar), Python 3.12 en el pipeline y 3.11 en local, SQLite, `QOLQE_MODO_PRUEBA=1`, Chromium; pipeline en `ubuntu-24.04`.
Cada defecto con prueba de pytest-bdd queda como **fallo esperado** (`xfail` estricto, `raises=AssertionError`): si se corrige, la prueba pasa a XPASS y el pipeline obliga a retirar la etiqueta; un error que no es una aserción (servidor caído, paso roto) queda como fallo y no como el defecto. En la web el fallo esperado es `@DEF-xx @fail` (`test.fail` de Playwright) y lo que el paso necesita para comparar (que el error aparezca) es una precondición: si no se cumple, el caso falla de verdad (`tests/e2e/precondicion.ts`).

**Regla para la concurrencia.** Un defecto de concurrencia se automatiza solo si su escenario lo reprodujo en **200 de 200** corridas locales con `--runxfail` (los 10 escenarios con `@concurrencia`, 11-nov-2026: los 9 con DEF fallaron 200 de 200 y CP-NA131 pasó 200 de 200). Con 20 corridas no alcanzaba: CP-T20, con una sola ráfaga, no reprodujo DEF-26 en 2 de 90 corridas de la revisión, porque el alta de contacto no tiene la pausa antifraude de las transferencias y la ventana es de milisegundos. Por eso CP-T20 repite la ráfaga hasta 5 veces. Si un escenario no cumple la regla, queda como evidencia manual (CP-NA69, CP-T19). La regla se vuelve a comprobar en el runner de GitHub cuando el workflow corra ahí (pendiente).

| ID | Título | Severidad | Prioridad | Estado |
|---|---|---|---|---|
| DEF-03 | Se puede aceptar una solicitud vencida y se transfiere el dinero | Crítica | Alta | Abierto |
| DEF-04 | Se puede transferir a una cuenta cerrada (contacto, celular o solicitud) | Crítica | Alta | Abierto |
| DEF-09 | Cerrar sesión no invalida el token | Crítica | Alta | Abierto |
| DEF-11 | Intentos fallidos simultáneos no bloquean la cuenta | Crítica | Alta | Abierto |
| DEF-19 | La interbancaria no considera la comisión y el saldo queda negativo | Crítica | Alta | Abierto |
| DEF-21 | Transferencias simultáneas superan el saldo o el límite diario | Crítica | Alta | Abierto |
| DEF-25 | Aceptaciones simultáneas de la misma solicitud debitan varias veces | Crítica | Alta | Abierto |
| DEF-07 | La respuesta puede llegar antes de que los datos queden guardados | Alta | Alta | Abierto (mitigado en el pipeline) |
| DEF-12 | Se acepta un PIN con secuencia descendente | Alta | Alta | Abierto |
| DEF-20 | El límite diario no suma las transferencias interbancarias | Alta | Alta | Abierto |
| DEF-22 | El código de operación se repite en el mismo segundo | Alta | Media | Abierto |
| DEF-24 | El detalle por código de operación no filtra por usuario (G3) | Alta | Media | Abierto |
| DEF-10 | Un ingreso exitoso no reinicia el conteo de intentos fallidos | Media | Alta | Abierto |
| DEF-02 | El alias duplicado no se detecta si tiene espacios alrededor | Media | Media | Abierto |
| DEF-01 | El alias rechaza la letra ñ | Media | Media | Abierto |
| DEF-13 | Nombres con espacios se guardan vacíos o con 1 carácter | Media | Media | Abierto |
| DEF-14 | Registros simultáneos del mismo celular responden 500 | Media | Media | Abierto |
| DEF-15 | Correo duplicado entre cuentas activas con registros o ediciones simultáneas | Media | Media | Abierto |
| DEF-23 | La comisión usa redondeo bancario en vez del comercial | Media | Media | Abierto |
| DEF-26 | Altas simultáneas del mismo celular crean contactos repetidos | Media | Media | Abierto |
| DEF-16 | El tiempo de respuesta revela si un celular está registrado | Media | Baja | Abierto (solo evidencia manual) |
| DEF-05 | El contrato OpenAPI no declara las reglas de los campos | Baja | Baja | Abierto |
| DEF-06 | `Allow` incompleto en la respuesta a `OPTIONS` | Baja | Baja | Abierto |
| DEF-08 | `favorito` acepta 0 y 1 aunque el contrato pide un booleano | Baja | Baja | Abierto |
| DEF-17 | Un token con `sub` no numérico responde 500 | Baja | Baja | Abierto |
| DEF-18 | El registro muestra el mensaje de validación en inglés (web) | Baja | Baja | Abierto |
| DEF-27 | Los alias que empiezan con tilde se ordenan al final | Baja | Baja | Abierto |
| DEF-28 | `contacto_id` acepta un booleano y transfiere al contacto 1 | Baja | Baja | Abierto |
| DEF-29 | La transferencia acepta un campo del otro tipo que no cumple su formato | Baja | Baja | Abierto |

## DEF-03: Se puede aceptar una solicitud vencida y se transfiere el dinero

| Campo | Valor |
|---|---|
| Módulo / regla | G4 · HU-G4-08 CA4, R-G4-05 |
| Severidad | Crítica |
| Prioridad | Alta |
| Prueba que lo detecta | `tests/api/test_solicitudes_api.py::test_cpa32_una_solicitud_vencida_no_se_puede_aceptar` y `tests/api/test_nucleo_dinero_api.py::test_cpna95_…` (la solicitud vencida de una cuenta cerrada, ver DEF-04) |

**Pasos para reproducir**
1. Reiniciar datos e iniciar sesión como Ana (987654321 / 4826).
2. Consultar `GET /api/solicitudes?estado=VENCIDA` y tomar la solicitud recibida de Carla (S/ 30.00).
3. Enviar `POST /api/solicitudes/{id}/aceptar`.

**Resultado esperado:** 409 `ESTADO_INVALIDO`; el saldo de Ana sigue en S/ 1,500.00.

**Resultado obtenido:** 200, estado `ACEPTADA`, saldo de Ana S/ 1,470.00.

**Evidencia:** `qolqe/api/solicitudes.py`: `aceptar` compara el estado guardado (`fila["estado"] != "PENDIENTE"`) en lugar de usar `_exigir_pendiente`, como hacen `rechazar` y `cancelar`. La interfaz oculta el botón (CP-W15), por lo que el defecto solo se detecta en la API.

## DEF-04: Se puede transferir a una cuenta cerrada (contacto, celular o solicitud)

| Campo | Valor |
|---|---|
| Módulo / regla | G4 · HU-G4-05 CA1; núcleo · RN-07, HU-N-07 CA2 y HU-N-06 CA4 |
| Severidad | Crítica |
| Prioridad | Alta |
| Prueba que lo detecta | `tests/api/test_contactos_api.py::test_cpa18_transferir_a_un_contacto_con_cuenta_cerrada`; en el núcleo, `tests/api/test_nucleo_dinero_api.py::test_cpna112_…` (por `celular_destino`), y `test_cpna94_…` (cuenta recién cerrada, por celular y por contacto) |

**Pasos para reproducir**
1. Reiniciar datos e iniciar sesión como Diego (998877665 / 3604), que tiene a Fabián (cuenta cerrada) como contacto.
2. Enviar `POST /api/transferencias` con `{"tipo": "QOLQE", "monto": "10", "contacto_id": <id de Fabián>}`.

**Resultado esperado:** 422 `DESTINO_INACTIVO`; el saldo de Diego no cambia.

**Resultado obtenido:** 201 con código de operación; el saldo de Diego baja a S/ 2,490.00. Lo mismo ocurre con `celular_destino: "934567812"` (CP-NA112) y con una cuenta que se acaba de cerrar (CP-NA94). Además, si Carla cierra su cuenta y Ana acepta la solicitud vencida de Carla, se transfieren S/ 30.00 a la cuenta cerrada. Ese efecto combinado está en CP-NA95, que lleva solo `@DEF-03`: la única solicitud de una cuenta cerrada es una vencida, porque HU-N-06 CA3 impide cerrar con pendientes, así que el caso falla por DEF-03. Si se corrige DEF-03 y no DEF-04, CP-NA95 pasa y DEF-04 sigue detectado por CP-A18, NA94 y NA112.

**Evidencia:** `qolqe/api/transferencias.py`: `_resolver_destino_qolqe` busca el destino sin comprobar su estado. El dinero queda en una cuenta que nadie puede usar.

## DEF-07: La respuesta puede llegar antes de que los datos queden guardados

| Campo | Valor |
|---|---|
| Módulo / regla | Toda la API · `qolqe/bd.py`, con `fastapi>=0.118` |
| Severidad | Alta |
| Prioridad | Alta |
| Prueba que lo detecta | El primer run del pipeline, con 6 fallos que no aparecían en local |

**Pasos para reproducir**
1. Instalar `requirements.txt` sin `constraints.txt` (se instala FastAPI 0.162).
2. En un ciclo, enviar `POST /api/auth/login` y, apenas responda, `GET /api/cuentas/me/saldo` con el token recibido.

**Resultado esperado:** la consulta responde 200 siempre: lo que la API confirmó ya está guardado.

**Resultado obtenido:** 2 de 300 ciclos en local responden 401 `La sesión fue cerrada`. En el pipeline, además, una segunda aceptación respondió 200 y un saldo salió sin actualizar.

**Evidencia:** [run del pipeline](https://github.com/Joharjbe/qolqe-wallet/actions/runs/41116477903). `obtener_bd` hace el `commit` después del `yield`, y desde FastAPI 0.118 ese código corre después de enviar la respuesta.

**Mitigación:** `constraints.txt` fija FastAPI 0.117.1, versión con la que no hubo fallos en 1,500 ciclos. No se modificó `qolqe/`.

## DEF-02: El alias duplicado no se detecta si tiene espacios alrededor

| Campo | Valor |
|---|---|
| Módulo / regla | G4 · HU-G4-01 CA1, R-G4-02 |
| Severidad | Media |
| Prioridad | Media |
| Prueba que lo detecta | `tests/api/test_contactos_api.py::test_cpa06_el_alias_duplicado_se_detecta_tras_quitar_los_espacios` |

**Pasos para reproducir**
1. Iniciar sesión como Ana, que tiene el contacto "Bruno".
2. Enviar `POST /api/contactos` con `{"celular": "998877665", "alias": " Bruno "}`.

**Resultado esperado:** 409 `ALIAS_DUPLICADO`.

**Resultado obtenido:** 201 con alias "Bruno": Ana queda con dos contactos con el mismo alias.

**Evidencia:** `qolqe/reglas/contactos.py`: `validar_alias` compara el alias antes de aplicar `strip()`. `validar_cambio_alias` tiene el mismo orden.

## DEF-01: El alias rechaza la letra ñ

| Campo | Valor |
|---|---|
| Módulo / regla | G4 · HU-G4-01 CA1, R-G4-02 |
| Severidad | Media |
| Prioridad | Media |
| Prueba que lo detecta | `tests/api/test_contactos_api.py::test_cpa04_el_alias_admite_la_letra_ñ` |

**Pasos para reproducir**
1. Iniciar sesión como Diego.
2. Enviar `POST /api/contactos` con `{"celular": "912345678", "alias": "Peña"}`.

**Resultado esperado:** 201. R-G4-02 admite "letras (incluidas tildes y ñ)".

**Resultado obtenido:** 422 `ALIAS_INVALIDO`.

**Evidencia:** `qolqe/reglas/contactos.py`: `PATRON_ALIAS` no incluye `ñ` ni `Ñ`.

## DEF-05: El contrato OpenAPI no declara las reglas de los campos

| Campo | Valor |
|---|---|
| Módulo / regla | G4 · contrato de `POST /api/contactos`, `PUT /api/contactos/{id}`, `POST /api/solicitudes` |
| Severidad | Baja |
| Prioridad | Baja |
| Prueba que lo detecta | Schemathesis, check `positive_data_acceptance` (ST202) |

**Pasos para reproducir:** ejecutar Schemathesis sin excluir el check; por ejemplo, `PUT /api/contactos/1` con un alias de caracteres arbitrarios.

**Resultado esperado:** el esquema declara `minLength`, `maxLength` y `pattern`, de modo que un dato válido según el contrato se acepta.

**Resultado obtenido:** 422 `ALIAS_INVALIDO` para datos que el esquema permite. Clasificación (paso 6 de la clase 10): defecto del **contrato**, no del código.

## DEF-06: `Allow` incompleto en la respuesta a `OPTIONS`

| Campo | Valor |
|---|---|
| Módulo / regla | G4 · contrato HTTP (RFC 9110) |
| Severidad | Baja |
| Prioridad | Baja |
| Prueba que lo detecta | Schemathesis, check `allow_header_conformance` (ST205) |

**Pasos para reproducir:** enviar `OPTIONS /api/contactos`.

**Resultado esperado:** `Allow: GET, POST`.

**Resultado obtenido:** 405 con `Allow: GET`. También en `/api/contactos/{id}` (`Allow: PUT`, falta DELETE) y `/api/solicitudes` (`Allow: GET`, falta POST).

## DEF-08: `favorito` acepta 0 y 1 aunque el contrato pide un booleano

| Campo | Valor |
|---|---|
| Módulo / regla | G4 · contrato de `PUT /api/contactos/{id}` |
| Severidad | Baja |
| Prioridad | Baja |
| Prueba que lo detecta | Schemathesis, check `negative_data_rejection` (ST201) |

**Pasos para reproducir:** enviar `PUT /api/contactos/1` con `{"alias": "Bruno oficina", "favorito": 0}`.

**Resultado esperado:** 422, porque el contrato declara `favorito` como booleano.

**Resultado obtenido:** 200 con `favorito: false`. Pydantic convierte el número en modo permisivo. Clasificación: desajuste entre el código y el contrato.

## DEF-09: Cerrar sesión no invalida el token

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · HU-N-03 CA1 |
| Severidad | Crítica |
| Prioridad | Alta |
| Prueba que lo detecta | `tests/api/test_nucleo_acceso_api.py::test_cpna44_después_del_logout_el_token_ya_no_debe_servir`, `test_cpna45_…`, `test_cpna46_…` y `tests/api/test_g4_tecnico_api.py::test_cpt07_después_de_cerrar_sesión_el_token_ya_no_sirve_en_g4` |

**Pasos para reproducir**
1. Reiniciar datos e iniciar sesión como Ana (987654321 / 4826).
2. Enviar `POST /api/auth/logout` con el token.
3. Con el mismo token, enviar `GET /api/cuentas/me/saldo`, `GET /api/seguridad/sesiones` y otra vez `POST /api/auth/logout`.

**Resultado esperado:** 204 en el paso 2 y luego 401 `NO_AUTENTICADO`; la sesión ya no figura como activa.

**Resultado obtenido:** 204; el saldo responde 200 (`1500.00`), la sesión sigue en la lista de activas y el segundo logout vuelve a responder 204. El token también sigue sirviendo en contactos y solicitudes (CP-T07, 10 operaciones).

**Evidencia:** `qolqe/api/autenticacion.py` (`cerrar_sesion`) guarda el `jti` en `tokens_revocados` pero no marca `sesiones.cerrada_en`, y `qolqe/dependencias.py` busca en `tokens_revocados` el JWT completo (`credenciales.credentials`) en lugar del `jti`. La web no lo muestra porque borra `sessionStorage` al salir (CP-NW09).

## DEF-10: Un ingreso exitoso no reinicia el conteo de intentos fallidos

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · HU-N-02 CA3, RN-04 |
| Severidad | Media |
| Prioridad | Alta |
| Prueba que lo detecta | `tests/api/test_nucleo_acceso_api.py::test_cpna30_un_ingreso_exitoso_reinicia_el_conteo_de_intentos_fallidos` |

**Pasos para reproducir**
1. Reiniciar datos.
2. Enviar `POST /api/auth/login` como Bruno (912345678) con PIN `0000`, otra vez con `0000`, luego con su PIN `7391` y por último con `0000`.

**Resultado esperado:** 401, 401, 200 y 401 `CREDENCIALES_INVALIDAS`: el ingreso exitoso deja el conteo en 0 (RN-04).

**Resultado obtenido:** 401, 401, 200 y **423** `CUENTA_BLOQUEADA`: el cuarto intento cuenta como el tercero consecutivo.

**Evidencia:** el ingreso exitoso de `qolqe/api/autenticacion.py` no pone `intentos_fallidos = 0`.

## DEF-11: Intentos fallidos simultáneos no bloquean la cuenta

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · HU-N-02 CA3, RN-04 |
| Severidad | Crítica |
| Prioridad | Alta |
| Prueba que lo detecta | `tests/api/test_nucleo_acceso_api.py::test_cpna33_los_intentos_fallidos_simultáneos_también_deben_bloquear` (200 de 200 corridas) |

**Pasos para reproducir**
1. Reiniciar datos.
2. Enviar a la vez 6 `POST /api/auth/login` como Carla (956781234) con PIN `0000` (un cliente por hilo, sincronizados con una barrera).
3. Enviar `POST /api/auth/login` con su PIN `5917`.

**Resultado esperado:** la cuenta queda bloqueada: el paso 3 responde 423 y Carla recibe el SMS de bloqueo.

**Resultado obtenido:** 6 × 401, el paso 3 responde 200 y no se envía ningún SMS. Un atacante puede probar PIN en paralelo sin bloquear la cuenta.

**Evidencia:** el conteo es lectura, verificación del PIN (PBKDF2, unos 45 ms) y escritura, sin bloqueo ni `UPDATE` atómico en `qolqe/api/autenticacion.py`.

## DEF-12: Se acepta un PIN con secuencia descendente

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · HU-N-01 CA4, RN-03 |
| Severidad | Alta |
| Prioridad | Alta |
| Prueba que lo detecta | `tests/api/test_nucleo_acceso_api.py::test_cpna15_se_acepta_un_pin_con_secuencia_descendente` (4321, 9876 y 3210) |

**Pasos para reproducir:** enviar `POST /api/usuarios` con `{"dni": "12345678", "nombres": "Nombre Valido", "celular": "987000330", "pin": "4321"}`.

**Resultado esperado:** 422 `PIN_INVALIDO`; RN-03 prohíbe las secuencias ascendentes y descendentes.

**Resultado obtenido:** 201; lo mismo con `9876` y `3210`. `1234` sí se rechaza (CP-NA14).

**Evidencia:** `qolqe/reglas/nucleo.py`: `validar_pin` solo busca el PIN dentro de `SECUENCIA_DIGITOS = "0123456789"`.

## DEF-13: Nombres con espacios se guardan vacíos o con 1 carácter

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · HU-N-01 CA1 |
| Severidad | Media |
| Prioridad | Media |
| Prueba que lo detecta | `tests/api/test_nucleo_acceso_api.py::test_cpna04_nombres_que_quedan_vacíos_o_de_1_carácter_tras_recortar` |

**Pasos para reproducir:** enviar `POST /api/usuarios` con `nombres` = `"   "` (tres espacios) y, en otro registro, `" a  "`.

**Resultado esperado:** 422 `SOLICITUD_INVALIDA`: los nombres deben tener de 2 a 80 caracteres.

**Resultado obtenido:** 201 con `nombres: ""` y 201 con `nombres: "a"`.

**Evidencia:** Pydantic valida la longitud antes del `strip()` que hace `qolqe/api/autenticacion.py` al guardar. La web recorta antes de enviar, por eso solo se ve en la API.

## DEF-14: Registros simultáneos del mismo celular responden 500

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · HU-N-01 CA3 |
| Severidad | Media |
| Prioridad | Media |
| Prueba que lo detecta | `tests/api/test_nucleo_acceso_api.py::test_cpna12_registros_simultáneos_con_el_mismo_celular` (200 de 200 corridas) |

**Pasos para reproducir:** enviar a la vez 5 `POST /api/usuarios` con el mismo celular `987123123` y datos válidos.

**Resultado esperado:** 1 × 201 y 4 × 409 `CELULAR_REGISTRADO`.

**Resultado obtenido:** 1 × 201 y 4 × **500**.

**Evidencia:** la unicidad la garantiza `celular TEXT NOT NULL UNIQUE` en `qolqe/bd.py`, pero el `IntegrityError` de la carrera no se traduce a 409.

## DEF-15: Correo duplicado entre cuentas activas con registros o ediciones simultáneas

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · HU-N-01 CA5 y HU-N-05 CA1 |
| Severidad | Media |
| Prioridad | Media |
| Prueba que lo detecta | `tests/api/test_nucleo_acceso_api.py::test_cpna20_registros_simultáneos_con_el_mismo_correo` (200 de 200 corridas). La edición simultánea (CP-NA69) queda como evidencia manual: en 1 de cada 25 corridas el servidor serializa las peticiones. |

**Pasos para reproducir:** enviar a la vez 5 `POST /api/usuarios` con celulares distintos y el mismo correo `mismo@correo.pe`.

**Resultado esperado:** 1 × 201 y 4 × 409 `CORREO_REGISTRADO`.

**Resultado obtenido:** 5 × 201: cinco cuentas activas con el mismo correo. Con 10 ediciones simultáneas de perfil al mismo correo pasa lo mismo.

**Evidencia:** la unicidad del correo es una consulta previa sin restricción `UNIQUE` en `qolqe/bd.py` ni bloqueo.

## DEF-16: El tiempo de respuesta revela si un celular está registrado

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · HU-N-02 CA2 |
| Severidad | Media |
| Prioridad | Baja |
| Prueba que lo detecta | Solo evidencia manual (CP-NA28): depende del equipo, no se automatiza con xfail estricto |

**Pasos para reproducir:** medir 40 `POST /api/auth/login` con PIN errado a celulares registrados (usuarios de carga 900000001 a 900000040) y 40 a celulares que no existen (911111001 a 911111040).

**Resultado esperado:** el mensaje es genérico y el tiempo no permite distinguir los dos casos.

**Resultado obtenido:** mediana de 45.9 ms con celular registrado frente a 1.6 ms con celular inexistente (medido en local el 11-nov-2026): se puede enumerar quién tiene cuenta.

**Evidencia:** `qolqe/api/autenticacion.py` solo calcula el PBKDF2 del PIN cuando el celular existe.

## DEF-17: Un token con `sub` no numérico responde 500

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · HU-N-04 CA3 |
| Severidad | Baja |
| Prioridad | Baja |
| Prueba que lo detecta | `tests/api/test_nucleo_acceso_api.py::test_cpna60_un_token_forjado_con_la_clave_por_defecto_y_sub_no_numérico` |

**Pasos para reproducir:** firmar con HS256 y la clave por defecto de `qolqe/config.py` un JWT con `{"sub": "abc", "jti": "y…", "exp": <ahora + 10 min>}` y enviar `GET /api/cuentas/me`.

**Resultado esperado:** 401 `NO_AUTENTICADO`.

**Resultado obtenido:** 500 `Internal Server Error`.

**Evidencia:** `qolqe/dependencias.py` hace `int(contenido["sub"])` sin capturar el `ValueError`. El caso muestra además que la clave por defecto es pública.

## DEF-18: El registro muestra el mensaje de validación en inglés

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · HU-N-01 CA1 (web) |
| Severidad | Baja |
| Prioridad | Baja |
| Prueba que lo detecta | `features/web/nucleo_acceso_web.feature`, CP-NW03 (`@DEF-18 @fail`, fallo esperado 3 de 3) |

**Tipo:** usabilidad (consistencia de mensajes). Ningún requisito fija el idioma: `requisitos.md` solo pide un `codigo` estable y un mensaje (`detail`). La base es la propia interfaz, que está en español, y la misma regla (nombres de 2 a 80 caracteres) en Mi perfil, que muestra "Los nombres deben tener entre 2 y 80 caracteres" (CP-NW14).

**Pasos para reproducir:** en `/registro.html`, registrar DNI 12345678, nombres "A", celular 987000113 y PIN 4826.

**Resultado esperado:** un mensaje en español sobre los nombres, con el texto que sea (por ejemplo, el de Mi perfil). El oráculo de CP-NW03 no exige una frase: pide que el error mencione "nombre" y no traiga el texto de Pydantic ("String should…", "characters").

**Resultado obtenido:** `registro-error` muestra "La solicitud tiene datos inválidos: String should have at least 2 characters": el `detail` en español seguido del texto de Pydantic que llega en `errores[0].mensaje` del 422.

## DEF-19: La interbancaria no considera la comisión y el saldo queda negativo

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · HU-N-08 CA2, RN-08 |
| Severidad | Crítica |
| Prioridad | Alta |
| Prueba que lo detecta | `tests/api/test_nucleo_dinero_api.py::test_cpna144_rn08_el_saldo_debe_cubrir_el_monto_más_la_comisión` (49.01 y 50.00) |

**Pasos para reproducir:** iniciar sesión como Carla (saldo S/ 50.00) y enviar `POST /api/transferencias` con `{"tipo": "INTERBANCARIA", "monto": "50.00", "cci": "00219300123456789012"}`.

**Resultado esperado:** 422 `SALDO_INSUFICIENTE` (el total con comisión es S/ 51.00); el saldo sigue en S/ 50.00.

**Resultado obtenido:** 201 con comisión 1.00 y total 51.00; el saldo de Carla queda en **S/ -1.00**.

**Evidencia:** `qolqe/transacciones.py` compara el saldo con `monto_cent` y no con monto más comisión.

## DEF-20: El límite diario no suma las transferencias interbancarias

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · RN-06, HU-N-07 CA2 y HU-N-08 CA2 |
| Severidad | Alta |
| Prioridad | Alta |
| Prueba que lo detecta | `tests/api/test_nucleo_dinero_api.py::test_cpna117_…` y `test_cpna146_rn06_las_transferencias_interbancarias_consumen_el_límite_diario` |

**Pasos para reproducir:** fijar el reloj a las 12:00 de hoy, iniciar sesión como Diego (límite diario S/ 1,000.00) y hacer 3 interbancarias de S/ 500.00.

**Resultado esperado:** la tercera responde 422 `LIMITE_DIARIO_EXCEDIDO`.

**Resultado obtenido:** las tres responden 201 y `GET /api/limites` informa `usado_hoy: "0.00"`. Con 500 interbancaria + 500 Qolqe se acepta otra Qolqe de S/ 0.01.

**Evidencia:** `qolqe/operaciones.py`: `transferido_hoy_centimos` filtra `tipo = 'QOLQE'`. También afecta el `usado_hoy` de HU-G5-01.

## DEF-21: Transferencias simultáneas superan el saldo o el límite diario

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · HU-N-07 CA5, RN-06 y RN-08; G4 · HU-G4-08 CA1 |
| Severidad | Crítica |
| Prioridad | Alta |
| Prueba que lo detecta | `tests/api/test_nucleo_dinero_api.py::test_cpna134_…`, `test_cpna135_…` y `tests/api/test_g4_tecnico_api.py::test_cpt18_…` (200 de 200 corridas cada una) |

**Pasos para reproducir**
1. Iniciar sesión como Carla (saldo S/ 50.00) y enviar a la vez 5 transferencias Qolqe de S/ 20.00 a Bruno.
2. Fijar el reloj a las 12:00, iniciar sesión como Diego (límite S/ 1,000.00) y enviar a la vez 5 transferencias de S/ 300.00.

**Resultado esperado:** en (1), como máximo 2 × 201 y el resto 422 `SALDO_INSUFICIENTE`; en (2), como máximo 3 × 201 y el resto 422 `LIMITE_DIARIO_EXCEDIDO`.

**Resultado obtenido:** (1) 5 × 201 y el saldo de Carla queda en **S/ -50.00**; (2) 5 × 201 y `usado_hoy` llega a S/ 1,500.00. Aceptar a la vez dos solicitudes de S/ 40.00 con saldo de S/ 50.00 también deja el saldo negativo (CP-T18).

**Evidencia:** leer, validar y escribir sin transacción exclusiva (`BEGIN IMMEDIATE`) ni `UPDATE` condicional en `qolqe/transacciones.py`; la pausa antifraude de 40 a 120 ms abre la ventana.

## DEF-22: El código de operación se repite en el mismo segundo

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · RN-10, HU-N-07 CA3 |
| Severidad | Alta |
| Prioridad | Media |
| Prueba que lo detecta | `tests/api/test_nucleo_dinero_api.py::test_cpna126_…` y `test_cpna127_rn10_transferencias_simultáneas_del_mismo_usuario_reciben_códigos_distintos` |

**Pasos para reproducir:** fijar el reloj a las 12:00:00 e iniciar sesión como Ana; transferir S/ 1.00 a Bruno y S/ 1.00 a Carla.

**Resultado esperado:** dos códigos de operación distintos (RN-10).

**Resultado obtenido:** ambas transferencias reciben `TRF26111112000000001`.

**Evidencia:** `qolqe/operaciones.py`: `generar_codigo_operacion` arma el código con prefijo, fecha y hora al segundo y el id del usuario, sin secuencia.

## DEF-23: La comisión usa redondeo bancario en vez del comercial

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · RN-09, HU-N-08 CA2 y HU-N-09 CA1 |
| Severidad | Media |
| Prioridad | Media |
| Prueba que lo detecta | `tests/api/test_nucleo_dinero_api.py::test_cpna142_…` (cobro real) y `test_cpna151_…` (simulación) |

**Pasos para reproducir:** enviar `GET /api/transferencias/comision?tipo=INTERBANCARIA&monto=67`, y luego con 71 y 299.

**Resultado esperado:** 1.5 % con redondeo comercial: 1.005 → 1.01, 1.065 → 1.07, 4.485 → 4.49.

**Resultado obtenido:** 1.00, 1.06 y 4.48. El cobro real de la interbancaria da los mismos valores.

**Evidencia:** `qolqe/reglas/nucleo.py`: `calcular_comision` usa `quantize(Decimal("0.01"))`, cuyo redondeo por defecto es `ROUND_HALF_EVEN`.

## DEF-24: El detalle por código de operación no filtra por usuario

| Campo | Valor |
|---|---|
| Módulo / regla | G3 · HU-G3-02 (hallado desde el núcleo, HU-N-07 CA3) |
| Severidad | Alta |
| Prioridad | Media |
| Prueba que lo detecta | `tests/api/test_nucleo_dinero_api.py::test_cpna129_…` y `test_cpna130_un_tercero_no_puede_ver_por_código_el_movimiento_de_otros` |

**Pasos para reproducir:** Ana transfiere S/ 100.00 a Bruno; Bruno y luego Carla envían `GET /api/movimientos/{codigo}` con ese código.

**Resultado esperado:** Bruno ve su `TRANSFERENCIA_RECIBIDA`; Carla recibe 404 `MOVIMIENTO_NO_ENCONTRADO`.

**Resultado obtenido:** los dos reciben 200 con el movimiento de Ana (`TRANSFERENCIA_ENVIADA`, contraparte 912345678): un tercero ve movimientos ajenos.

**Evidencia:** `qolqe/api/movimientos.py`: `detalle` busca solo por `codigo_operacion`, sin `usuario_id`.

## DEF-25: Aceptaciones simultáneas de la misma solicitud debitan varias veces

| Campo | Valor |
|---|---|
| Módulo / regla | G4 · HU-G4-08 CA1 y CA4 |
| Severidad | Crítica |
| Prioridad | Alta |
| Prueba que lo detecta | `tests/api/test_g4_tecnico_api.py::test_cpt17_tres_aceptaciones_simultáneas_de_la_misma_solicitud_debitan_una_sola_vez` (200 de 200 corridas) |

**Pasos para reproducir:** Diego le solicita S/ 25.00 a Bruno; Bruno envía a la vez 3 `POST /api/solicitudes/{id}/aceptar`.

**Resultado esperado:** 1 × 200 y 2 × 409 `ESTADO_INVALIDO`; Bruno queda con S/ 775.00 y Diego con S/ 2,525.00.

**Resultado obtenido:** 3 × 200; Bruno queda con S/ 725.00 y Diego con S/ 2,575.00: la misma solicitud se pagó tres veces.

**Evidencia:** `qolqe/api/solicitudes.py`: `aceptar` lee el estado, transfiere y recién después actualiza, sin `UPDATE … WHERE estado = 'PENDIENTE'` ni bloqueo.

## DEF-26: Altas simultáneas del mismo celular crean contactos repetidos

| Campo | Valor |
|---|---|
| Módulo / regla | G4 · HU-G4-01 CA1 (`CONTACTO_EXISTENTE`) |
| Severidad | Media |
| Prioridad | Media |
| Prueba que lo detecta | `tests/api/test_g4_tecnico_api.py::test_cpt20_cinco_altas_simultáneas_del_mismo_celular_crean_un_solo_contacto`: hasta 5 ráfagas de 5 altas; el defecto apareció en 200 de 200 corridas |

**Pasos para reproducir:** iniciar sesión como Diego y enviar a la vez 5 `POST /api/contactos` con el celular 912345678 y alias distintos. Si la ráfaga sale bien (1 × 201), borrar el contacto y repetir: a veces el servidor serializa las 5 peticiones.

**Resultado esperado:** 1 × 201 y 4 × 409 `CONTACTO_EXISTENTE`.

**Resultado obtenido:** en casi todas las ráfagas, más de un 201 (en la revisión, de 3 a 5); Bruno aparece repetido en la lista de Diego y ocupa varios de los 15 cupos.

**Evidencia:** la tabla `contactos` de `qolqe/bd.py` no tiene `UNIQUE (usuario_id, contacto_usuario_id)` y la verificación previa no está protegida.

## DEF-27: Los alias que empiezan con tilde se ordenan al final

| Campo | Valor |
|---|---|
| Módulo / regla | G4 · HU-G4-02 CA1 |
| Severidad | Baja |
| Prioridad | Baja |
| Prueba que lo detecta | `tests/api/test_contactos_api.py::test_cpa47_los_alias_que_empiezan_con_tilde_se_ordenan_con_su_letra` |

**Pasos para reproducir:** Diego agrega los contactos "Ángel" (956781234), "álvaro" (923456789) y "Beto" (987654321) y consulta `GET /api/contactos`.

**Resultado esperado:** orden alfabético por alias: álvaro, Ángel, Beto, Fabián.

**Resultado obtenido:** Beto, Fabián, Ángel, álvaro.

**Tipo:** usabilidad (interpretación del requisito). HU-G4-02 CA1 pide "ordenados por alias" sin fijar la intercalación. Lo tomamos como orden alfabético en español, que no separa las vocales con tilde: la misma HU ya ignora tildes al buscar (CA2) y la API ya ignora mayúsculas al ordenar (`COLLATE NOCASE`). El oráculo es el mismo en toda la suite: `orden_alfabetico` de `tests/api/conftest.py` (sin mayúsculas ni tildes, la ñ después de la n), que usan CP-A08 y CP-A47.

**Evidencia:** `qolqe/api/contactos.py` ordena con `COLLATE NOCASE`, que solo iguala mayúsculas ASCII; la búsqueda sí ignora tildes (HU-G4-02 CA2), así que la lista y la búsqueda no son coherentes.

## DEF-28: `contacto_id` acepta un booleano y transfiere al contacto 1

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · HU-N-07 CA1 (contrato de `POST /api/transferencias`) |
| Severidad | Baja |
| Prioridad | Baja |
| Prueba que lo detecta | `tests/api/test_nucleo_dinero_api.py::test_cpna104_un_contacto_id_booleano_se_rechaza_como_tipo_inválido` |

**Pasos para reproducir:** iniciar sesión como Ana y enviar `POST /api/transferencias` con `{"tipo": "QOLQE", "contacto_id": true, "monto": "1"}`.

**Resultado esperado:** 422 `SOLICITUD_INVALIDA` con el error en `body.contacto_id`; el saldo no cambia.

**Resultado obtenido:** 201: Pydantic convierte `true` en el id 1 (el contacto "Bruno" de Ana) y se transfiere S/ 1.00.

**Evidencia:** misma causa que DEF-08 (modo permisivo de Pydantic), pero aquí mueve dinero.

## DEF-29: La transferencia acepta un campo del otro tipo que no cumple su formato

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · contrato de `POST /api/transferencias` (HU-N-07 y HU-N-08) |
| Severidad | Baja |
| Prioridad | Baja |
| Prueba que lo detecta | Schemathesis, check `negative_data_rejection` (ST201), CP-T04; el fallo se descarta solo para este caso con `filter_failure` en `scripts/contrato_hooks.py` |

**Pasos para reproducir:** enviar `POST /api/transferencias` con `{"tipo": "QOLQE", "monto": "1.00", "celular_destino": "912345678", "cci": "no-es-un-cci"}`, o una INTERBANCARIA con `"celular_destino": "abc"`.

**Resultado esperado:** 422, porque el contrato declara `cci` con `pattern ^\d{20}$` y `celular_destino` con el formato de celular.

**Resultado obtenido:** 201 en los dos casos: la API ignora el campo del otro tipo sin validarlo. Clasificación: desajuste entre el código y el contrato.

## Observaciones (no son defectos según los requisitos)

### OBS-01: el cierre de cuenta sirve para adivinar el PIN

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · HU-N-06 CA1 y CA2 |
| Riesgo | Medio: quien tiene un token puede probar PIN sin límite |
| Prueba | `tests/api/test_nucleo_dinero_api.py::test_cpna84_…` (pasa: documenta el comportamiento actual) |

**Qué pasa:** `POST /api/cuentas/me/cierre` responde 422 `PIN_INCORRECTO` con un PIN errado y, si el PIN es correcto y hay saldo, 422 `SALDO_PENDIENTE`. Los intentos errados no bloquean nada: CP-NA84 envía 4 PIN errados y después el correcto, y el ingreso sigue habilitado.

**Por qué no es un DEF:** RN-04 (bloqueo al tercer intento fallido) está escrita para el ingreso (HU-N-02 CA3), y HU-N-06 solo pide confirmar con el PIN. Ningún requisito limita los intentos en el cierre. Se recomienda aplicar RN-04 también a las operaciones que piden el PIN.

### OBS-02: sin Content-Type, la API toma el cuerpo como JSON

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo y G4 · contrato (todas las operaciones con cuerpo) |
| Riesgo | Bajo |
| Prueba | `tests/api/test_nucleo_acceso_api.py::test_cpna160_…` (pasa: documenta el comportamiento actual) |

**Qué pasa:** `POST /api/usuarios` y `POST /api/transferencias` con un cuerpo JSON y sin cabecera `Content-Type` responden 201 y hacen la operación. Con `Content-Type: text/plain` responden 422 `SOLICITUD_INVALIDA` (CP-NA159). Es el comportamiento por defecto de FastAPI.

**Por qué no es un DEF:** el contrato declara `application/json` como cuerpo, pero ningún requisito pide rechazar una petición sin la cabecera. La clase 10 propone 400 o 415 para este caso; se deja como observación para que el equipo de desarrollo decida.

## Hallazgo descartado

Schemathesis, check `ensure_resource_availability` (ST302): reporta 404 al aceptar una solicitud recién creada con el mismo usuario que la creó. **Falso positivo:** HU-G4-08 CA4 exige ese 404 (solo el destinatario puede aceptar), y CP-A31 lo verifica.

En el contrato del núcleo hay dos falsos positivos más, documentados en `schemathesis.toml` y `scripts/contrato_hooks.py`: el 423 `CUENTA_BLOQUEADA` ante un PIN mal formado de una cuenta bloqueada (HU-N-02 CA4) y el correo `""` en `PUT /api/cuentas/me`, que el contrato describe como "null o vacío lo quita" (CP-NA67).

## Quality gate

Todas las pruebas pasan, salvo los fallos esperados de esta lista; no hay flaky (`failOnFlakyTests`); la suite web pasa 3 veces seguidas; no hay respuestas 500 ni incumplimientos de esquema en el contrato; los reportes quedan publicados. `schemathesis.toml` declara los checks excluidos: DEF-05, DEF-06, DEF-08 (solo en esa operación) y los falsos positivos anteriores; DEF-29 se descarta por valor con `filter_failure`, sin desactivar el check en toda la operación.
