# Alcance y diseño de casos · Núcleo común y G4

**Módulos:** Núcleo común, HU-N-01 a HU-N-09 (`docs/requisitos.md`, sección 3), y G4 · Contactos y solicitudes de dinero, HU-G4-01 a HU-G4-10 (sección 7). Son 19 historias y 51 criterios de aceptación (33 del núcleo y 18 de G4).

## Por qué estos módulos

G4 mueve dinero sin que el pagador inicie la operación: una persona pide y otra acepta. El núcleo es la base de G4. Transferir a un contacto (HU-G4-05) y aceptar una solicitud (HU-G4-08) aplican todas las reglas de HU-N-07. Además, una solicitud pendiente impide cerrar la cuenta (HU-N-06 CA3).

| Riesgo | Dónde | Impacto |
|---|---|---|
| Dinero mal transferido | Transferir (HU-N-07, HU-N-08), transferir a un contacto (HU-G4-05), aceptar una solicitud (HU-G4-08) | Alto: RN-05 a RN-10 deciden si se debita, cuánto y a quién |
| Acceso y sesiones | Registro, ingreso, bloqueo y cierre de sesión (HU-N-01 a HU-N-03, RN-04) | Alto: un token que sigue sirviendo o un bloqueo que no se aplica exponen la cuenta |
| Máquina de estados | PENDIENTE → ACEPTADA, RECHAZADA, CANCELADA o VENCIDA (R-G4-05); cuenta ACTIVA → CERRADA (HU-N-06) | Alto: una transición indebida mueve dinero o bloquea una deuda |
| Acceso entre usuarios | Solo el destinatario acepta, solo el solicitante cancela, cada usuario ve sus datos | Alto: un recurso ajeno debe responder 404 |
| Concurrencia | HU-N-07 CA5 exige que las reglas se cumplan con operaciones simultáneas | Alto: el saldo o el límite se pueden superar |

## Totales

Fuente: etiquetas de `features/` (`npm run trazabilidad:verificar` → *334 casos, 0 errores, 3 avisos*: CP-NA45, NA48 y T28 son técnicos sin `@CA`, a propósito) más el caso de contrato CP-T04. Resultado de la corrida local del 11-nov-2026, después de la revisión final.

| Módulo | Nivel | Tipo | Casos | Pasan | Fallo esperado (con su DEF) |
|---|---|---|---:|---:|---:|
| Núcleo | API | Funcional | 101 | 88 | 13 |
| Núcleo | API | Técnico | 53 | 41 | 12 |
| Núcleo | Web | Funcional | 27 | 26 | 1 |
| G4 | API | Funcional | 97 | 89 | 8 |
| G4 | API | Técnico | 25 | 19 | 6 |
| G4 | Web | Funcional | 31 | 31 | 0 |
| Núcleo y G4 | Contrato | Técnico | 1 (CP-T04) | 1 | 0 |
| **Total** | | | **335** | **295** | **40** |

- **Ejecuciones.** Un esquema cuenta cada ejemplo y la web cada repetición.
  - API: 276 escenarios generan 766 ejecuciones (707 pasan y 59 son xfail estricto).
  - Web: 58 escenarios generan 71 pruebas, porque 8 esquemas tienen entre 2 y 5 ejemplos. Con 3 repeticiones son 213 ejecuciones (210 pasan y 3 son el fallo esperado de CP-NW03).
  - Contrato: 19 operaciones.
- **Nuevos en la entrega final:** 277 casos.
  - Núcleo: 181.
  - G4: 96 (CP-A40 a A99, 24 técnicos entre CP-T05 y T30, y CP-W20 a W31).
  - De los 60 escenarios anteriores quedan 57 (CP-A01 a A39 sin A19 ni A38, CP-W01 a W19 y CP-T02), con su ID. CP-A38, CP-T01 y CP-T03 se retiraron porque repetían a CP-A99 y a dos filas de CP-T05 con un oráculo más débil (ver "Lo que no se automatizó"). CP-A03, A21, A22 y A34 conservan solo sus filas válidas: las inválidas ya estaban, con el código de error, en CP-A78, A61, A90 y A97.
- **Módulo por ID.** El módulo se toma del prefijo del ID. Por eso CP-W28 (pantalla de solicitudes con la sesión vencida) cuenta en G4 aunque cubre HU-N-04 CA3, y CP-T07 y CP-T18 cuentan en G4 aunque también cubren HU-N-03 y HU-N-07. CP-T04, el contrato, cubre los dos módulos y cuenta como "núcleo y G4".

**Convención de ID.**

| Prefijo | Módulo | Nivel |
|---|---|---|
| `CP-NA` | Núcleo | API. Los técnicos llevan además `@tecnico` |
| `CP-NW` | Núcleo | Web |
| `CP-A` | G4 | API funcional |
| `CP-T` | G4 | API técnico y contrato (CP-T04) |
| `CP-W` | G4 | Web |

## Criterio de nivel

Regla de la clase 11: *cada regla se prueba en el nivel más bajo donde se pueda detectar; por la interfaz solo van los recorridos críticos y lo que solo se ve en la pantalla.*

Un criterio se define como **web** si cumple al menos una condición:

1. Lo que afirma solo se ve en la pantalla (lista, orden, pestañas, avisos, botones disponibles, saldo oculto, DNI enmascarado).
2. Es un paso de un recorrido crítico que pasa por dinero o por el acceso (registro, ingreso, transferencia, aceptar).
3. La interfaz debe comunicar al usuario un error de la API.

Las validaciones de reglas (límites, formatos, permisos, estados) quedan en **API**; la web solo confirma que un error se muestra. Los efectos que no aparecen en la pantalla también quedan en API: el SMS simulado se lee en `/api/pruebas/notificaciones`. Lo mismo pasa con la concurrencia, que no se puede provocar de forma determinista desde la interfaz.

Un caso es **técnico** si verifica una propiedad de la API que no está escrita como regla de negocio en el criterio: autenticación, propiedad de los datos, tipos y forma del cuerpo, semántica HTTP, conformidad con el contrato, concurrencia. Se etiqueta `@tecnico` (o tiene ID `CP-T`) y va enlazado al criterio que protege.

## Criterios por nivel · Núcleo

| HU | Prioridad | CA | Qué verifica | API funcional | API técnico | Web |
|---|---|---|---|---|---|---|
| HU-N-01 | Alta | CA1 | Alta válida: saldo S/ 0.00, límite S/ 2,000.00, nombres 2 a 80 | CP-NA01 a NA04, NA07 | NA05, NA06, NA159, NA160 | CP-NW01, NW02, NW03 |
| HU-N-01 | Alta | CA2 | DNI (RN-01) | NA08, NA09 | — | NW25, NW26 |
| HU-N-01 | Alta | CA3 | Celular (RN-02) y ya registrado | NA10, NA11 | NA12 | NW04, NW26 |
| HU-N-01 | Alta | CA4 | PIN (RN-03) | NA13 a NA15 | — | NW25, NW26 |
| HU-N-01 | Alta | CA5 | Correo: formato y único entre cuentas activas | NA16 a NA19, NA75 | NA20 | NW25 |
| HU-N-01 | Alta | CA6 | SMS de bienvenida | NA21, NA22 | — (no aplica: efecto fuera de la pantalla) | — (SMS) |
| HU-N-02 | Alta | CA1 | Token de 30 minutos y sesión activa | NA23 a NA25 | NA26 | NW05 |
| HU-N-02 | Alta | CA2 | Mensaje genérico ante credenciales inválidas | NA27 | NA157 | NW06 |
| HU-N-02 | Alta | CA3 | RN-04: el tercer fallo bloquea y avisa | NA29 a NA32 | NA33 | NW07 |
| HU-N-02 | Alta | CA4 | Durante el bloqueo 423; a los 15 minutos se ingresa | NA34 a NA37 | — | NW07 |
| HU-N-02 | Alta | CA5 | Una cuenta cerrada no ingresa | NA38, NA39 | — | NW17 |
| HU-N-02 | Alta | CA6 | Dispositivo nuevo: ingresa y recibe alerta | NA40, NA41 | NA42, NA43 | NW08 |
| HU-N-03 | Alta | CA1 | Tras cerrar sesión el token no sirve | NA44 | NA46, NA47, CP-T07 (y NA45, NA48 sin `@CA`: usan reglas de G6) | NW09 |
| HU-N-03 | Alta | CA2 | No afecta las otras sesiones | NA49, NA51 | NA50 | NW27 |
| HU-N-04 | Alta | CA1 | Saldo, moneda y fecha | NA52 a NA54 | NA55 | NW10 |
| HU-N-04 | Alta | CA2 | Perfil con DNI enmascarado | NA56, NA57 | NA158 | NW11 |
| HU-N-04 | Alta | CA3 | Sin token o con token vencido o inválido: 401 | — | NA58 a NA61 | NW12, CP-W28 |
| HU-N-05 | Media | CA1 | Editar nombres y correo | NA62, NA63, NA65 a NA68 | NA64 | NW13, NW14 |
| HU-N-05 | Media | CA2 | DNI y celular no se modifican | NA70 | NA71 | NW15 |
| HU-N-05 | Media | CA3 | SMS al cambiar el correo | NA72 a NA74 | — (no aplica: efecto fuera de la pantalla) | — (SMS) |
| HU-N-06 | Media | CA1 | Confirmar con el PIN | NA80 | NA81 a NA84, NA86 | NW16 |
| HU-N-06 | Media | CA2 | Solo con saldo S/ 0.00 exactos | NA85 | NA86 | NW16 |
| HU-N-06 | Media | CA3 | Sin solicitudes pendientes | NA87 a NA90 | NA86 | NW16 |
| HU-N-06 | Media | CA4 | Cierra las sesiones, no ingresa, nadie le transfiere | NA91 a NA95 | NA96 | NW17, NW18 |
| HU-N-07 | Alta | CA1 | Celular o contacto, monto y descripción | NA97 a NA101 | NA102 a NA108, NA159, NA160 | NW19 |
| HU-N-07 | Alta | CA2 | RN-05 a RN-08 | NA109 a NA121 | NA122 | NW20 |
| HU-N-07 | Alta | CA3 | Débito, crédito, mismo código (RN-10), SMS | NA123 a NA126 | NA127 a NA131 | NW21 |
| HU-N-07 | Alta | CA4 | Comprobante | NA132, NA133 | — | NW19 |
| HU-N-07 | Alta | CA5 | Reglas bajo concurrencia | — | NA127, NA131, NA134, NA135, CP-T18 | — (concurrencia) |
| HU-N-08 | Alta | CA1 | CCI de 20 dígitos | NA136, NA138 | NA137, NA139, NA140 | NW22 |
| HU-N-08 | Alta | CA2 | Comisión RN-09 y RN-05, RN-06, RN-08 | NA141 a NA146 | — | NW23 |
| HU-N-08 | Alta | CA3 | CCI enmascarado | NA147 | NA148 | NW23 |
| HU-N-09 | Media | CA1 | Simular sin operar | NA149 a NA152 | NA153 a NA156 | NW24, CP-W29 |

Los 33 criterios del núcleo tienen al menos un caso de API. 30 tienen además un caso web. Los otros 3 no se ven en la pantalla: dos SMS (HU-N-01 CA6, HU-N-05 CA3) y la concurrencia (HU-N-07 CA5). Para las reglas de validación, la web confirma que el error de la API llega al usuario (NW03, NW04, NW14, NW16, NW20, NW22, NW25) y que la pantalla aplica su propio tope de dígitos (NW26).

En la columna de API técnico, un "—" sin nota es una regla de negocio pura: lo que podría probar un caso técnico (autenticación, tipos, contrato) ya lo cubren los casos técnicos de la misma operación en otra fila o CP-T04.

## Criterios por nivel · G4

| HU | Prioridad | CA | Qué verifica | API funcional | API técnico | Web |
|---|---|---|---|---|---|---|
| HU-G4-01 | Alta | CA1 | Alta y reglas R-G4-01 a 03 | CP-A01 a A07, A40 a A43, A77 a A79, A81, A86 | CP-T05, T07, T11, T16, T20, T21, T25, T29, T30 | CP-W01, W02, W10, W30 |
| HU-G4-02 | Media | CA1 | Favoritos primero, orden, 10 por página, total | A08, A44 a A47, A82, A83 | T05 a T07, T15, T16, T21, T22 | W03, W23, W24 |
| HU-G4-02 | Media | CA2 | Búsqueda sin mayúsculas ni tildes | A09, A48, A83 | — | W04 |
| HU-G4-02 | Media | CA3 | Alias, nombre enmascarado, celular, favorito | A10, A49 | — | W05 |
| HU-G4-03 | Media | CA1 | Editar alias y favorito, límite de 5 | A11 a A13, A50 a A54, A80, A84, A85 | T02, T05, T07, T08, T10, T12, T16, T21, T23 a T26, T29, T30 | W06, W24, W25 |
| HU-G4-04 | Baja | CA1 | Eliminar conserva las transferencias | A14, A43, A58, A86, A87 | T02, T05, T07, T08, T10, T16, T21, T23, T24 | W07 |
| HU-G4-04 | Baja | CA2 | Bloqueo con solicitudes pendientes | A15, A16, A55 a A57 | — | W08 |
| HU-G4-05 | Alta | CA1 | Transferir eligiendo un contacto (reglas de HU-N-07) | A17, A18, A59, A60, A88 | T09 | W09, W29 |
| HU-G4-06 | Alta | CA1 | Contacto, monto y motivo; máximo 10 pendientes | A21 a A24, A61, A62, A89 a A92 | T05, T07, T09, T13, T21, T25, T29, T30 | W10, W11, W12, W26, W30 |
| HU-G4-06 | Alta | CA2 | PENDIENTE, vence a las 48 h, SMS | A20, A63 | — | W13 |
| HU-G4-07 | Media | CA1 | Enviadas y recibidas, filtro por estado | A25, A26, A64, A66, A67, A93 | T05 a T07, T16, T21, T22 (y T28 sin `@CA`: ruta inexistente) | W10, W14, W27 |
| HU-G4-07 | Media | CA2 | Se muestra VENCIDA | A27, A65 | — | W15, W22 |
| HU-G4-08 | Alta | CA1 | Transferencia con las reglas de HU-N-07 | A28, A68 a A70, A94 | T05 a T07, T10, T16 a T18, T21 a T24 | W16, W20 |
| HU-G4-08 | Alta | CA2 | Si falla, sigue PENDIENTE | A29, A30, A95, A96 | — | W17, W20 |
| HU-G4-08 | Alta | CA3 | ACEPTADA, código de operación, SMS | A28, A68 | — | W10, W16 |
| HU-G4-08 | Alta | CA4 | Solo el destinatario, solo PENDIENTE y no vencida | A31 a A33, A71 | T08, T17 | W15 (sin botones), W21 |
| HU-G4-09 | Media | CA1 | Rechazar con motivo opcional, SMS | A34 a A36, A72 a A74, A97 | T05, T07, T08, T10, T14, T21, T23, T24, T30 | W18, W31 |
| HU-G4-10 | Media | CA1 | Cancelar, solo el solicitante | A37, A39, A75, A76, A98, A99 | T05, T07, T08, T10, T21, T23, T24 | W19, W21, W22 |

**Qué se agregó en G4.**
- **60 funcionales (CP-A40 a A99).** Cubren:
  - los bordes que faltaban: 15 contactos y liberar el cupo, 10 por página, 5 favoritos, 10 pendientes entre varios contactos, 48 horas exactas al eliminar;
  - las transiciones no válidas restantes: aceptar, rechazar o cancelar una solicitud ya resuelta;
  - los efectos de cada operación: SMS, mismo código en la solicitud y en ambos movimientos, sin movimientos si falla;
  - el código de error de cada rechazo: A61, A78, A90, A97, A99;
  - las ampliaciones de DEF-01 (Ñ mayúscula y al editar) y DEF-02 (al editar), y el defecto nuevo DEF-27.
- **24 técnicos (CP-T05 a T30).** Credenciales en cada endpoint, vencimiento del token con el reloj, token tras el logout, recurso ajeno o inexistente, ids no enteros o fuera de rango, tipos inválidos, asignación masiva, 405 y `Allow`, esquema del contrato y concurrencia.
- **12 web (CP-W20 a W31).** Cancelar la confirmación, aceptar una solicitud ya cancelada, enviada vencida sin cancelar, extremos de la paginación, estrella de favorito con el máximo de 5, error al editar, validación solo de pantalla, contadores, sesión vencida, transferir desde la pantalla de transferencias, doble clic y motivo de 61 caracteres.

## Casos técnicos

| Grupo | Qué verifica | Núcleo | G4 | Defectos | Herramienta |
|---|---|---|---|---|---|
| Autenticación | Sin token, token inválido, vencido, de una sesión cerrada o de una cuenta cerrada: 401 `NO_AUTENTICADO`, sin cambiar datos | CP-NA47, NA58, NA59, NA61, NA83, NA96, NA140, NA156 | CP-T05, T06, T22 | — | pytest-bdd |
| Revocación del token | Después del logout el token no debe servir; cerrar una sesión desde Seguridad sí la invalida | NA45, NA46, NA48 (y el funcional NA44) | T07 | DEF-09 | pytest-bdd |
| Token forjado | `sub` no numérico firmado con la clave por defecto | NA60 | — | DEF-17 | pytest-bdd |
| Aislamiento entre usuarios | Un recurso de otro usuario responde como inexistente (404) y lo que hace un usuario no afecta a otro. La cuenta solo se lee por `/api/cuentas/me` (NA55 revisa que el contrato no tenga otra ruta) | NA42, NA50, NA102, NA128 a NA130 | T02, T08, T09 | DEF-24 | pytest-bdd |
| Tipos y forma del cuerpo | Campo faltante, tipo incorrecto o JSON mal formado: 422 `SOLICITUD_INVALIDA` que nombra el campo y no cambia nada | NA05, NA26, NA64, NA82, NA104, NA106, NA137, NA153 | T10 a T15, T26, T30 | DEF-08, DEF-28 | pytest-bdd |
| Cabeceras (clase 10) | `Content-Type: text/plain` se rechaza sin cambiar nada; sin `Content-Type` el cuerpo se toma como JSON; con `Accept: application/xml` la respuesta es JSON según el contrato | NA159, NA160 | T11 | OBS-02 | pytest-bdd + `jsonschema_rs` |
| Campos ignorados | Asignación masiva, campos no editables y campos del otro tipo de transferencia | NA06, NA71, NA105, NA107, NA139 | T25 | — | pytest-bdd |
| Identificadores en el borde | ids 0, negativos, ausentes y fuera de 64 bits; identificador de dispositivo; PIN que no tiene 4 dígitos | NA43, NA81, NA103 | T23, T24 | — | pytest-bdd |
| Semántica HTTP | 405 con `Allow`, ruta inexistente con el formato de error, la simulación solo acepta GET | NA156 | T16, T28, T29 | DEF-06 | pytest-bdd |
| Orden de validación | Qué error gana cuando fallan varias reglas; el 401 va antes que el 422 | NA86, NA108, NA122 | — | — | pytest-bdd |
| Fuga de datos | El CCI y el DNI completos no aparecen en ninguna respuesta; el ingreso no revela si el celular existe (mismo estado, cuerpo y cabeceras); el cierre de cuenta como oráculo del PIN (OBS-01 en `defectos.md`) | NA84, NA148, NA157, NA158 | — | — | pytest-bdd |
| Consistencia sin efectos | Simular no mueve dinero y coincide con lo que se cobra | NA154, NA155 | — | — | pytest-bdd |
| Esquema del contrato | Las respuestas cumplen el esquema y el tipo de contenido de `/openapi.json` (el contrato no declara cabeceras de respuesta) | — | T21 | — | pytest-bdd + `jsonschema_rs` |
| Contrato generado | Sin 500 y con estados, cabeceras y esquemas según OpenAPI, también con entradas generadas, en 19 operaciones del núcleo y de G4 | CP-T04 | CP-T04 | DEF-05, DEF-29 | Schemathesis |
| Concurrencia (`@concurrencia`) | Peticiones simultáneas, un cliente por hilo, sincronizadas con `threading.Barrier`; CP-T20 repite la ráfaga hasta 5 veces | NA12, NA20, NA33, NA127, NA131, NA134, NA135 | T17, T18, T20 | DEF-11, 14, 15, 21, 22, 25, 26 | pytest-bdd |
| Repetibilidad | Datos y reloj reiniciados en cada escenario (en la web, si el reinicio falla el escenario no corre); API 4 corridas idénticas; web 3 repeticiones con `failOnFlakyTests` | todos | todos | — | fixtures de pytest y Playwright |

Un caso de concurrencia se automatiza solo si da el mismo resultado en todas las corridas. Los 10 escenarios con hilos lo dieron en 200 de 200 corridas con `--runxfail`: los 9 con DEF fallaron siempre por su defecto y CP-NA131 pasó siempre. CP-T20 necesitó repetir su ráfaga: con una sola, la revisión vio 2 corridas de 90 en que el servidor serializó las altas (ver la regla en `defectos.md`). Los que no cumplen la regla quedan como evidencia manual (ver abajo).

## Técnicas de diseño

Un caso puede combinar dos técnicas; por eso los conteos suman más que el total. Las técnicas de caja negra son las de ISTQB CTFL v4.0, sección 4.2, y la adivinación de errores es la 4.4.1. Casos de uso viene del syllabus v3.1.

| Técnica | Núcleo | G4 | Dónde se aplica, ejemplos |
|---|---:|---:|---|
| Partición de equivalencia | 86 | 69 | Clases de celular, DNI, PIN y correo (NA09 a NA18); token ausente, inválido o vencido (NA58, NA59); recurso propio o ajeno (NA102, T02); celular inválido, propio, no registrado, cerrado, existente (CP-A02); error de la API en la pantalla (NW04, NW16, NW25, CP-W02); dispositivo de confianza o nuevo (NW08); `Content-Type` y `Accept` (NA159, NA160) |
| Valores límite | 36 | 38 | Nombres 1/2/80/81 (NA03), DNI 7/8/9 (NA08), PIN 3/4/5 (NA13), token a los 29 y 30 minutos (NA24, T06, T22), bloqueo de 15 minutos (NA35), saldo 0.00/0.01 para cerrar (NA85), 48 horas (NA89, A27, A57), descripción 60/61 (NA98, NA99), monto RN-05 (NA109, A21 y A61), saldo exacto (NA113, A69), límite diario y 00:00 de Lima (NA115, NA116, NA121, A94), CCI 19/20/21 (NA136), comisión mínima, proporcional y tope (NA141, NA150), alias 2/3/20/21 (A03 y A78), tope de dígitos en la pantalla (NW26), 15 contactos, 5 favoritos, 10 pendientes (A07, A12, A23), ids fuera de 64 bits (T24) |
| Transición de estados | 18 | 29 | Bloqueo por intentos (NA29 a NA37), sesión cerrada (NA44 a NA48), cuenta ACTIVA → CERRADA (NA39, NA91), aumento del límite a las 24 horas (NA120), solicitud PENDIENTE a cada estado final y transiciones no válidas (A28, A32, A33, A35 a A37, A39, A71, A73, A75, A98) |
| Tabla de decisión | 7 | 5 | Orden de los errores del registro (NA19), cuenta cerrada × PIN (NA38), cierre: PIN × saldo × pendientes, 7 reglas (NA86), 401 frente a 422 (NA108), orden de validación de la transferencia (NA122), quién actúa × estado (A31, A72, A99), alias × favorito enviados u omitidos (A52) |
| Casos de uso | 33 | 22 | Recorridos de alta, ingreso, transferencia Qolqe e interbancaria (NW01, NW05, NW19, NW23), recorrido de una solicitud entre dos usuarios (CP-W10), dos sesiones de la misma persona (NW27), efectos de SMS y código de operación (NA21, NA125, A60, A68) |
| Concurrencia (carreras) | 7 | 3 | Registros, ingresos fallidos, transferencias y aceptaciones simultáneas (ver casos técnicos) |
| Adivinación de errores | 6 | 1 | Token forjado (NA60), PIN errado al cerrar (NA84), mismo segundo con el reloj fijo (NA126), CCI en las respuestas (NA148), enumeración de celulares (NA157), DNI en las respuestas (NA158), doble clic (CP-W30) |
| Basada en el contrato | 1 | 2 | CP-T04 (Schemathesis), CP-T21 (esquema de cada respuesta de G4) y NA160 (respuesta JSON del registro y de la transferencia) |

## Lo que no se automatizó

| Caso | Por qué | Dónde está la evidencia |
|---|---|---|
| CP-NA28: el tiempo de respuesta revela si el celular existe (DEF-16) | Depende del equipo; mediana 45.9 ms frente a 1.6 ms en local | `docs/defectos.md`, DEF-16 |
| CP-NA69: ediciones simultáneas con el mismo correo (DEF-15) | Cerca de 1 de 25 corridas se serializa y daría XPASS | `docs/defectos.md`, DEF-15 (el registro simultáneo sí está automatizado en CP-NA20) |
| CP-T19: aceptar frente a cancelar o rechazar a la vez | No se reprodujo en todas las corridas | Sin DEF |

Además hay números sin caso:

| Número | Motivo |
|---|---|
| CP-A19 | Retirado en la Entrega 1; no quedó registrado el motivo |
| CP-T27 | Reservado sin uso durante el diseño de la entrega final |
| CP-A38 | Retirado en la revisión final: repetía a CP-A99 (mismos ejemplos), que además revisa el código de error y que la solicitud siga pendiente |
| CP-T01 y CP-T03 | Retirados en la revisión final: eran las filas `GET /api/contactos` y `GET /api/solicitudes` sin token de CP-T05, que además revisa el desafío Bearer y que nada cambie |

Esos números no se reutilizan, para que la trazabilidad acumulada entre ejecuciones no mezcle casos distintos.
