# Reporte de defectos · G4

Entorno común: Qolqe (`qolqe/` sin modificar), Python 3.12, SQLite, `QOLQE_MODO_PRUEBA=1`, Chromium; pipeline en `ubuntu-24.04`.
Cada defecto con prueba automatizada queda como **fallo esperado** (`xfail` estricto): si se corrige, la prueba pasa a XPASS y el pipeline obliga a retirar la etiqueta.

| ID | Título | Severidad | Prioridad | Estado |
|---|---|---|---|---|
| DEF-03 | Se puede aceptar una solicitud vencida y se transfiere el dinero | Crítica | Alta | Abierto |
| DEF-04 | Se puede transferir a un contacto con la cuenta cerrada | Crítica | Alta | Abierto |
| DEF-07 | La respuesta puede llegar antes de que los datos queden guardados | Alta | Alta | Abierto (mitigado en el pipeline) |
| DEF-02 | El alias duplicado no se detecta si tiene espacios alrededor | Media | Media | Abierto |
| DEF-01 | El alias rechaza la letra ñ | Media | Media | Abierto |
| DEF-05 | El contrato OpenAPI no declara las reglas de los campos | Baja | Baja | Abierto |
| DEF-06 | `Allow` incompleto en la respuesta a `OPTIONS` | Baja | Baja | Abierto |

## DEF-03: Se puede aceptar una solicitud vencida y se transfiere el dinero

| Campo | Valor |
|---|---|
| Módulo / regla | G4 · HU-G4-08 CA4, R-G4-05 |
| Severidad | Crítica |
| Prioridad | Alta |
| Prueba que lo detecta | `tests/api/test_solicitudes_api.py::test_cpa32_una_solicitud_vencida_no_se_puede_aceptar` |

**Pasos para reproducir**
1. Reiniciar datos e iniciar sesión como Ana (987654321 / 4826).
2. Consultar `GET /api/solicitudes?estado=VENCIDA` y tomar la solicitud recibida de Carla (S/ 30.00).
3. Enviar `POST /api/solicitudes/{id}/aceptar`.

**Resultado esperado:** 409 `ESTADO_INVALIDO`; el saldo de Ana sigue en S/ 1,500.00.

**Resultado obtenido:** 200, estado `ACEPTADA`, saldo de Ana S/ 1,470.00.

**Evidencia:** `qolqe/api/solicitudes.py`: `aceptar` compara el estado guardado (`fila["estado"] != "PENDIENTE"`) en lugar de usar `_exigir_pendiente`, como hacen `rechazar` y `cancelar`. La interfaz oculta el botón (CP-W15), por lo que el defecto solo se detecta en la API.

## DEF-04: Se puede transferir a un contacto con la cuenta cerrada

| Campo | Valor |
|---|---|
| Módulo / regla | G4 · HU-G4-05 CA1; núcleo · RN-07, HU-N-07 CA2 |
| Severidad | Crítica |
| Prioridad | Alta |
| Prueba que lo detecta | `tests/api/test_contactos_api.py::test_cpa18_transferir_a_un_contacto_con_cuenta_cerrada` |

**Pasos para reproducir**
1. Reiniciar datos e iniciar sesión como Diego (998877665 / 3604), que tiene a Fabián (cuenta cerrada) como contacto.
2. Enviar `POST /api/transferencias` con `{"tipo": "QOLQE", "monto": "10", "contacto_id": <id de Fabián>}`.

**Resultado esperado:** 422 `DESTINO_INACTIVO`; el saldo de Diego no cambia.

**Resultado obtenido:** 201 con código de operación; el saldo de Diego baja a S/ 2,490.00. Lo mismo ocurre con `celular_destino: "934567812"`.

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

## Hallazgo descartado

Schemathesis, check `ensure_resource_availability` (ST302): reporta 404 al aceptar una solicitud recién creada con el mismo usuario que la creó. **Falso positivo:** HU-G4-08 CA4 exige ese 404 (solo el destinatario puede aceptar), y CP-A31 lo verifica.

## Quality gate

Todas las pruebas pasan, salvo los fallos esperados de esta lista; no hay flaky (`failOnFlakyTests`); la suite web pasa 3 veces seguidas; no hay respuestas 500 ni incumplimientos de esquema en el contrato; los reportes quedan publicados. Los tres checks de Schemathesis excluidos corresponden a DEF-05, DEF-06 y al falso positivo anterior.
