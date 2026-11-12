# Informe del proyecto – Johar Barzola

## 1. Datos generales y alcance

| Campo | Valor |
|---|---|
| Integrantes | Johar Jared Barzola Estrella |
| Módulos | Núcleo común (HU-N-01 a HU-N-09) y G4 · Contactos y solicitudes de dinero (HU-G4-01 a HU-G4-10) |
| Herramienta de API | pytest 8.4.2 + httpx + pytest-bdd 9.0.0; Schemathesis 4.32.7 para el contrato |
| Herramienta web | Playwright 1.64.1 (TypeScript) + playwright-bdd 9.2.1, con Page Object, componentes y fixtures |
| CI/CD | GitHub Actions (`.github/workflows/pruebas.yml`), 8 jobs y quality gate |
| Gestión de casos | Kiwi TCMS 17.0 (Docker local) más matriz e historial de ejecuciones en GitHub Pages |
| Herramienta de rendimiento | Pendiente (Parte 3) |

**Alcance y nivel de prueba.** Son 19 historias y sus 51 criterios: 33 del núcleo y 18 de G4. Hay 335 casos: 334 escenarios Gherkin y el caso de contrato CP-T04.

Cada regla se prueba en el nivel más bajo donde se pueda detectar (clase 11). Por la interfaz van solo tres cosas:
- los recorridos críticos;
- lo que solo se ve en la pantalla;
- que un error de la API llegue al usuario.

Por eso la API tiene casi 5 veces más escenarios que la web.

| Módulo | API funcional | API técnico | Web | Contrato | Total |
|---|---:|---:|---:|---:|---:|
| Núcleo | 101 | 53 | 27 | — | 181 |
| G4 | 97 | 25 | 31 | — | 153 |
| Núcleo y G4 | — | — | — | 1 (CP-T04, 19 operaciones) | 1 |
| **Total** | **198** | **78** | **58** | **1** | **335** |

Todos los criterios tienen al menos un caso de API. Los 18 criterios de G4 y 30 de los 33 del núcleo tienen además un caso web. Los otros 3 no se ven en la pantalla: dos SMS y la concurrencia.

El detalle criterio por criterio, la técnica de cada grupo de casos y los casos técnicos están en [`alcance-y-casos.md`](alcance-y-casos.md). La respuesta punto por punto a la retroalimentación está en [`respuesta-feedback.md`](respuesta-feedback.md).

## 2. Pruebas de API

**Herramienta.** pytest-bdd ejecuta escenarios Gherkin con solicitudes HTTP reales (httpx) contra Qolqe levantado. Schemathesis genera casos desde `/openapi.json`. Las dos se complementan: una prueba las reglas de negocio que dice el criterio y la otra, lo que el contrato promete ante entradas que nadie escribió. La comparación con Postman/Newman, Bruno, REST Assured, Karate, Robot Framework, el cliente HTTP de Playwright, Dredd y Pact está en [`arquitectura.md`](arquitectura.md), sección 2.

| Enfoque | Ventajas | Limitaciones | Capacidades de IA |
|---|---|---|---|
| pytest-bdd: casos escritos a partir de los criterios | Gherkin legible y compartido con la web, etiquetas para la trazabilidad, `xfail` estricto ligado a cada `@DEF`, esquemas con ejemplos, JUnit XML | Requiere programar los pasos; pytest-bdd 9 no es compatible con pytest 9 (se fijó pytest 8.4.2) | No las trae; con un asistente externo se generan pasos, que hay que revisar contra los requisitos |
| Schemathesis: casos generados desde el contrato | Cientos de solicitudes sin escribirlas, en 4 fases (ejemplos, cobertura, fuzzing y secuencias con estado); encontró DEF-05, DEF-06, DEF-08 y DEF-29 | No conoce las reglas de negocio; genera falsos positivos que hay que clasificar; el número de casos cambia entre corridas por la fase con estado | Generación basada en propiedades, sin IA |

**Arquitectura de la capa API.** Detalle y diagrama en [`arquitectura.md`](arquitectura.md), sección 1.

- **Escenarios.** `features/*.feature`: 7 archivos del núcleo y 3 de G4.
- **Enlace.** `tests/api/test_*.py`, que solo llaman a `scenarios()`.
- **Pasos por área.**
  - `conftest.py`: cliente, sesiones por usuario y pasos comunes.
  - `pasos_nucleo_acceso.py`, `pasos_nucleo_dinero.py` y `pasos_g4_extra.py`.
- **Fixture `s`.** Reinicia los datos semilla y el reloj antes de cada escenario (FIRST, *Independent*).
- **Defectos conocidos.** El hook `pytest_bdd_apply_tag` convierte cada `@DEF-xx` en `xfail(strict=True, raises=AssertionError)`: si el defecto se corrige, la prueba da XPASS y el pipeline obliga a retirar la etiqueta; si falla por otra causa (servidor caído, paso roto), queda como fallo y no como el defecto.
- **Evidencia.** El plugin `tests/api/evidencia.py` agrega al reporte HTML las peticiones y respuestas de cada caso, con el token enmascarado.

**Casos funcionales y técnicos.**
- **Funcionales.** Cubren cada criterio con valores límite, particiones, transiciones de estado y tablas de decisión. Revisan el código de error y que un rechazo no deje efectos: saldo, SMS y movimientos.
- **Técnicos.** Son 78, más CP-T04. Verifican:
  - autenticación y revocación del token;
  - aislamiento entre usuarios (404 para un recurso ajeno);
  - datos que no deben salir: CCI y DNI completos, y si un celular existe (mismo estado, cuerpo y cabeceras en el ingreso);
  - tipos y forma del cuerpo, y las cabeceras `Content-Type` y `Accept`;
  - asignación masiva;
  - identificadores en el borde;
  - semántica HTTP (405 y `Allow`);
  - esquema de cada respuesta;
  - concurrencia: 10 escenarios con `threading.Barrier` y la etiqueta `@concurrencia`.

**Contrato ampliado.** `scripts/correr-contrato.sh` pasó de 9 operaciones de G4 a 19.
- **Operaciones.** Se sumaron registro, ingreso y salida, sesiones, cuenta, saldo, cierre, transferencias y simulación de comisión.
- **Token por operación.** `scripts/contrato_hooks.py` lo pone y usa un usuario desechable para el logout y el cierre.
- **Exclusiones.** Las exclusiones, los falsos positivos y su motivo están en `schemathesis.toml` y en [`pipeline.md`](pipeline.md).

**Cómo ejecutar.** README, sección 6.

**Resultados y evidencia** (corrida local del 11-nov-2026, rama `entrega-final`):

| Suite | Escenarios | Ejecuciones | Pasan | Fallo esperado (DEF) | Tiempo |
|---|---:|---:|---:|---:|---:|
| API núcleo | 154 | 404 | 370 | 34 | — |
| API G4 | 122 | 362 | 337 | 25 | — |
| **API total** | **276** | **766** | **707** | **59** | 194 s |
| Contrato (CP-T04) | 19 operaciones | 1373 casos generados | 1373 | 0 | 14 s |

- **API.** 4 corridas (3 de la revisión final y la de verificación) dieron 707 passed y 59 xfailed, idénticas test por test, sin XPASS ni fallos. Los 59 xfail fallan por una aserción (`raises=AssertionError`).
- **Concurrencia.** Los 10 escenarios con hilos dieron el mismo resultado en 200 de 200 corridas con `--runxfail`: los 9 con DEF reprodujeron su defecto siempre y CP-NA131 pasó siempre. CP-T20 repite su ráfaga hasta 5 veces porque, con una sola, el servidor a veces serializa las altas (regla en [`defectos.md`](defectos.md)).
- **Contrato.** Las 4 fases pasaron en verde. Hubo 26 casos omitidos y 5 descartados por `filter_failure`. Ese filtro solo descarta dos hallazgos ya clasificados: DEF-29 y el falso positivo de `correo: ""`.
  - En otras corridas se generaron 1291, 1376 y 1414 casos con el mismo veredicto: la fase con estado depende de las respuestas.
- **Evidencia anterior en GitHub.** La de las entregas 1 y 2 sigue publicada en https://joharjbe.github.io/qolqe-wallet/.

## 3. Pruebas web y CI/CD

**Herramienta y patrón.** Playwright Test con playwright-bdd ejecuta los `.feature` de `features/web/`: 2 del núcleo y 2 de G4. El patrón es **Page Object con componentes y fixtures**:

- **Pasos** (`tests/e2e/steps/`, uno por área). Solo traducen el Gherkin: no tienen localizadores (`grep -E "getBy|locator\(" tests/e2e/steps/*.ts` no encuentra ninguno).
- **Page Objects** (`tests/e2e/pages/`). Login, Registro, Inicio, Perfil, Transferir, Contactos y Solicitudes. Las cinco pantallas con menú heredan de `PaginaQolqe`, una base de un solo nivel. Las pantallas no heredan entre sí.
- **Componentes** (`componentes.ts`). `Aviso`, `DialogoConfirmacion`, `DialogoFormulario`, `ListaVacia` y `Navegacion`, uno por cada componente que `app.js` genera igual en todas las pantallas. Cada pantalla los compone. Así un cambio en un diálogo se corrige en un solo lugar.
- **Fixtures** (`tests/e2e/fixtures.ts`). Entregan las páginas. `DatosPrueba` reinicia datos y reloj y prepara el estado por la API de soporte, no por la pantalla; si el reinicio falla, el escenario no corre.
- **Localizadores.**
  - Se localiza por `data-testid`, el contrato estable que expone Qolqe.
  - El rol, el texto y los atributos de accesibilidad (`aria-pressed`, `aria-selected`) se usan cuando lo que se verifica es lo que se ve.
  - La posición se usa solo cuando lo que se verifica es el orden. No hay clases de estilo.
  - Hay un solo worker porque todas las pruebas comparten una base.

La comparación con Page Factory, Page Object encadenado, Screenplay, App Actions y Robot Framework está en [`arquitectura.md`](arquitectura.md), sección 3, con los criterios de la clase 11 (tamaño, cambios de interfaz, BDD y lo que trae el framework). Frente a Robot Framework, la diferencia no es la espera automática: la librería Browser también corre sobre Playwright. Las diferencias son tres:
- los mismos `.feature`, con las mismas etiquetas que la API;
- el runner de Playwright, con `repeatEach`, reintentos que marcan una prueba como inestable, `failOnFlakyTests`, `webServer` y el reporte con trazas;
- la evidencia de que esa combinación sirve: en el run #13 detectó un escenario inestable real y puso el pipeline en rojo.

**Etapas del pipeline** (`.github/workflows/pruebas.yml`). Corre en cada push a `main`, en cada PR a `main` y a pedido. El detalle y la justificación de cada job están en [`pipeline.md`](pipeline.md).

| Job | Depende de | Qué hace | Por qué |
|---|---|---|---|
| `estatico` | — | ruff, `tsc --noEmit`, `bddgen`, `pytest --collect-only`, `trazabilidad.py --verificar` | *Fail fast*: en un minuto y sin servidor detecta un paso sin definir, un error de tipos o una etiqueta `@CP` faltante |
| `api` | `estatico` | pytest-bdd del núcleo y de G4, funcional y técnico | Primera prueba dinámica y la más barata. Check obligatorio |
| `contrato` | `estatico`, en paralelo con `api` | Schemathesis, 19 operaciones | Otro runner y otra base. Antes iba dentro de `api` y se perdía si fallaba pytest |
| `web` | `api` y `contrato` | Playwright, 3 repeticiones | La etapa más cara solo corre con la API en verde. Check obligatorio |
| `quality-gate` | las 4 anteriores, `always()` | Pasa solo si las 4 terminan en `success` | Un solo veredicto; un job omitido no cuenta como aprobado |
| `reportes` | `estatico` en verde | Matriz, `junit-cp.xml`, `run.json`, evidencias por CP | Corre aunque fallen las pruebas: el reporte explica el fallo |
| `gestion-casos` | `reportes`, solo `main` | Registra el run en Kiwi TCMS | Preparado para un Kiwi accesible desde internet. Hoy termina con un aviso y la sincronización es local (pull) |
| `publicar` | `reportes`, solo `main` | GitHub Pages con portada, reportes e historial de 30 runs | Único job con `pages: write` (mínimo privilegio). Despliegues en serie |

**Evidencia con o sin imágenes.** *Run workflow* tiene la entrada `evidencia`. Push y PR usan `sin-imagenes`.

| | `sin-imagenes` | `con-imagenes` |
|---|---|---|
| Web | Captura y traza de los fallos, video en el reintento | Captura, video y traza de cada prueba |
| API | Peticiones y respuestas de los fallos y de los xfail | Peticiones y respuestas de cada caso |
| Contrato | JUnit y HTML | Además `peticiones.har` |
| Retención | 14 días | 7 días |

La variable `EVIDENCIA` la leen `playwright.config.ts`, `tests/api/evidencia.py` y `scripts/correr-contrato.sh`. Las mismas opciones existen en local con `npm run test:web:con-imagenes` y `npm run test:api:con-imagenes`.

**Quality gate.** El criterio de salida es que todas las pruebas pasen. Los fallos conocidos deben ser xfail estrictos con su DEF en [`defectos.md`](defectos.md) y no puede haber pruebas inestables (`failOnFlakyTests`). El job `quality-gate` lo evalúa en cada run.

En la protección de `main`, `api` y `web` son status checks obligatorios (consultado con la API de GitHub el 11-nov-2026). Como `estatico` va delante, los dos empiezan con una guarda: si la etapa anterior no terminó en `success`, fallan en segundos y no quedan como omitidos. Se recomienda agregar también `quality-gate` como check obligatorio.

**Trazabilidad HU → casos → ejecución, a lo largo de muchas ejecuciones.**

- **Modelo.** `.github/scripts/trazabilidad.py`, con el modelo en `casos.py`, une las etiquetas `@HU`, `@CA`, `@CP`, `@DEF` y `@tecnico` con los JUnit de las tres herramientas.
- **Salidas de cada run:**
  - la matriz agrupada por módulo, nivel y tipo;
  - `junit-cp.xml`, un caso por CP con sus propiedades;
  - `run.json`, con el commit, el evento, la evidencia y el estado de cada CP;
  - las evidencias por CP.
- **Historial.** `publicar` suma cada run a `historial.json` y publica `historial.html` en Pages. Es una grilla CP × runs de los últimos 30, con conteos, estabilidad y primera y última vez.
- **Kiwi TCMS 17.0.** Es la herramienta de gestión de casos elegida: gratis, sin límite de runs y con importador JUnit oficial. Corre en Docker local.
  - `scripts/kiwi_sincronizar.py` importa cada run de GitHub como un TestRun, también los runs anteriores reconstruidos desde sus artefactos.
  - Cada CP acumula ahí todas sus ejecuciones.
- **Investigación y estado.** La comparación con Qase, TestRail, Xray, Zephyr, Testmo y TestLink, la integración y el estado verificado están en [`gestion-casos.md`](gestion-casos.md).
- **Verificación.** `trazabilidad.py --verificar` corre en `estatico` y falla si a un escenario le falta `@HU` o `@CP`, si un CP se repite o si un par `@HU` `@CA` no existe en `requisitos.md`.

**Resultados** (corrida local del 11-nov-2026):
- **Web.** 58 escenarios, que son 71 pruebas; con 3 repeticiones, 213 ejecuciones en 2.5 minutos. Pasan 210, hay 3 fallos esperados (CP-NW03, DEF-18) y 0 inestables con `CI=1` (reintento y `failOnFlakyTests`).
- **Trazabilidad.** Con los JUnit de esa corrida: 335 casos, 295 passed y 40 xfailed, sin casos sin ejecutar. Hay 25 defectos enlazados a sus casos.
- **Etapa estática.** `ruff`, `tsc`, `bddgen`, `--verificar` y `actionlint`, este último sobre el workflow, terminan sin errores.

El workflow nuevo todavía no corrió en GitHub: la rama `entrega-final` no está publicada. `gestion-casos` y `publicar` solo corren en `main`.

**Evidencia anterior en GitHub (Entrega 2).**
- El [run #10](https://github.com/Joharjbe/qolqe-wallet/actions/runs/41123298780) pasó 57 de 57 ejecuciones web.
- En el run #13, `failOnFlakyTests` puso el pipeline en rojo por CP-W10 inestable. Era un error de la prueba, que no esperaba el alta del contacto, y se corrigió.
- El [PR #3](https://github.com/Joharjbe/qolqe-wallet/pull/3) muestra el quality gate bloqueando un cambio.

**Defectos vistos desde la interfaz.**
- Por la interfaz apareció un defecto propio: DEF-18, el mensaje de validación en inglés.
- DEF-03 no se alcanza por pantalla: la interfaz oculta el botón de aceptar en una solicitud vencida (CP-W15). Sí se alcanza por la API.

## 4. Pruebas de rendimiento

Pendiente (Parte 3).

## 5. Defectos encontrados

Hay 29 defectos abiertos: 7 críticos, 5 altos, 9 medios y 8 bajos. Por módulo:
- 16 son del núcleo;
- 9 son de G4;
- 2 afectan a ambos (DEF-04 y DEF-21);
- 1 afecta a toda la API (DEF-07);
- 1 es de G3 y se halló desde el núcleo (DEF-24).

Por cómo se detectaron:
- 24 con pruebas de API;
- 1 con la web (DEF-18);
- 2 solo con el contrato (DEF-05 y DEF-29);
- 1 en el pipeline (DEF-07);
- 1 con evidencia manual (DEF-16).

| ID | Título | Módulo | Severidad | Lo detecta | Estado |
|---|---|---|---|---|---|
| DEF-01 | El alias rechaza la letra ñ | G4 | Media | CP-A04, A79, A80 | Abierto |
| DEF-02 | El alias duplicado no se detecta si tiene espacios alrededor | G4 | Media | CP-A06, A54 | Abierto |
| DEF-03 | Se puede aceptar una solicitud vencida y se transfiere el dinero | G4 | Crítica | CP-A32, NA95 | Abierto |
| DEF-04 | Se puede transferir a una cuenta cerrada (contacto, celular o solicitud) | Núcleo y G4 | Crítica | CP-A18, NA94, NA112 (NA95, junto con DEF-03) | Abierto |
| DEF-05 | El contrato OpenAPI no declara las reglas de los campos | G4 (contrato) | Baja | CP-T04 (check excluido) | Abierto |
| DEF-06 | `Allow` incompleto en la respuesta a `OPTIONS` | G4 | Baja | CP-T29 | Abierto |
| DEF-07 | La respuesta puede llegar antes de que los datos queden guardados | Toda la API | Alta | Primer run del pipeline | Abierto (mitigado en el pipeline) |
| DEF-08 | `favorito` acepta 0 y 1 aunque el contrato pide un booleano | G4 | Baja | CP-T26 | Abierto |
| DEF-09 | Cerrar sesión no invalida el token | Núcleo | Crítica | CP-NA44 a NA46, T07 | Abierto |
| DEF-10 | Un ingreso exitoso no reinicia el conteo de intentos fallidos | Núcleo | Media | CP-NA30 | Abierto |
| DEF-11 | Intentos fallidos simultáneos no bloquean la cuenta | Núcleo | Crítica | CP-NA33 | Abierto |
| DEF-12 | Se acepta un PIN con secuencia descendente | Núcleo | Alta | CP-NA15 | Abierto |
| DEF-13 | Nombres con espacios se guardan vacíos o con 1 carácter | Núcleo | Media | CP-NA04 | Abierto |
| DEF-14 | Registros simultáneos del mismo celular responden 500 | Núcleo | Media | CP-NA12 | Abierto |
| DEF-15 | Correo duplicado entre cuentas activas con registros o ediciones simultáneas | Núcleo | Media | CP-NA20 (la edición, CP-NA69, es evidencia manual) | Abierto |
| DEF-16 | El tiempo de respuesta revela si un celular está registrado | Núcleo | Media | Evidencia manual (CP-NA28) | Abierto (solo evidencia manual) |
| DEF-17 | Un token con `sub` no numérico responde 500 | Núcleo | Baja | CP-NA60 | Abierto |
| DEF-18 | El registro muestra el mensaje de validación en inglés | Núcleo (web) | Baja | CP-NW03 (`@fail`) | Abierto |
| DEF-19 | La interbancaria no considera la comisión y el saldo queda negativo | Núcleo | Crítica | CP-NA144 | Abierto |
| DEF-20 | El límite diario no suma las transferencias interbancarias | Núcleo | Alta | CP-NA117, NA146 | Abierto |
| DEF-21 | Transferencias simultáneas superan el saldo o el límite diario | Núcleo y G4 | Crítica | CP-NA134, NA135, T18 | Abierto |
| DEF-22 | El código de operación se repite en el mismo segundo | Núcleo | Alta | CP-NA126, NA127 | Abierto |
| DEF-23 | La comisión usa redondeo bancario en vez del comercial | Núcleo | Media | CP-NA142, NA151 | Abierto |
| DEF-24 | El detalle por código de operación no filtra por usuario | G3 (hallado desde el núcleo) | Alta | CP-NA129, NA130 | Abierto |
| DEF-25 | Aceptaciones simultáneas de la misma solicitud debitan varias veces | G4 | Crítica | CP-T17 | Abierto |
| DEF-26 | Altas simultáneas del mismo celular crean contactos repetidos | G4 | Media | CP-T20 | Abierto |
| DEF-27 | Los alias que empiezan con tilde se ordenan al final | G4 | Baja | CP-A47 | Abierto |
| DEF-28 | `contacto_id` acepta un booleano y transfiere al contacto 1 | Núcleo | Baja | CP-NA104 | Abierto |
| DEF-29 | La transferencia acepta un campo del otro tipo que no cumple su formato | Núcleo (contrato) | Baja | CP-T04 (`filter_failure`) | Abierto |

Pasos para reproducir, resultado esperado y obtenido, prioridad y evidencia de cada uno en [`defectos.md`](defectos.md). Del DEF-09 al DEF-29 se volvieron a reproducir contra la app el 11-nov-2026 antes de documentarlos. DEF-18 y DEF-27 son de usabilidad: `defectos.md` dice en qué se basa cada uno, porque ningún requisito fija el idioma ni la intercalación.

Además hay dos observaciones que no son defectos según los requisitos: OBS-01, el cierre de cuenta permite probar PIN sin límite (CP-NA84), y OBS-02, sin `Content-Type` la API toma el cuerpo como JSON (CP-NA160).

## 6. Conclusiones y recomendaciones

**Estado de calidad.** El núcleo y G4 no están listos para producción.
- De los 335 casos, 295 pasan y 40 fallan por 25 defectos conocidos.
- Los 7 defectos críticos tocan lo más sensible de una billetera.
  - Cinco mueven dinero de forma indebida: DEF-03, DEF-04, DEF-19, DEF-21 y DEF-25.
  - Dos debilitan el acceso: DEF-09 (el token sigue sirviendo tras el logout) y DEF-11 (el bloqueo se evita con intentos simultáneos).
- Lo que sí funciona según los criterios:
  - las validaciones de formato y límites;
  - los permisos entre usuarios en G4;
  - la máquina de estados de las solicitudes, salvo aceptar una vencida (DEF-03) y las aceptaciones simultáneas (DEF-25);
  - lo que muestra la interfaz.

**Causas que se repiten** (de la evidencia de [`defectos.md`](defectos.md)):

| Causa | Defectos |
|---|---|
| Leer, validar y escribir sin transacción atómica ni `UPDATE` condicional | DEF-11, DEF-21, DEF-25 |
| Unicidad comprobada con una consulta previa, sin restricción `UNIQUE` | DEF-14, DEF-15, DEF-26 |
| Validación de estado incompleta: aceptar no usa `_exigir_pendiente`; el destino no se revisa | DEF-03, DEF-04 |
| Reglas de dinero mal implementadas: comisión fuera del saldo, límite sin interbancarias, redondeo, código sin secuencia | DEF-19, DEF-20, DEF-22, DEF-23 |
| Revocación del token por el JWT completo en vez del `jti`; conteo de fallos que no se reinicia | DEF-09, DEF-10 |
| Código y contrato desalineados: Pydantic permisivo y esquema sin restricciones | DEF-05, DEF-06, DEF-08, DEF-28, DEF-29 |

**Recomendaciones para el equipo de desarrollo, en orden.**
1. **Operaciones de dinero atómicas.** Usar `BEGIN IMMEDIATE` o `UPDATE … WHERE saldo >= total` y `WHERE estado = 'PENDIENTE'`. Comparar el saldo con monto más comisión y exigir que el destino esté activo. Corrige DEF-03, 04, 19, 21 y 25.
2. **Sesión.** Revocar por `jti`, marcar `sesiones.cerrada_en` y actualizar el conteo de fallos de forma atómica. Reiniciar el conteo tras un ingreso exitoso. Corrige DEF-09, 10 y 11.
3. **Unicidad.** Agregar `UNIQUE` en correo activo y en (usuario, contacto). Traducir el `IntegrityError` a 409. Corrige DEF-14, 15 y 26.
4. **Contrato.** Activar el modo estricto de Pydantic en booleanos y enteros. Declarar `minLength`, `maxLength` y `pattern` en OpenAPI y validar cada campo según el tipo de transferencia. Corrige DEF-05, 08, 28 y 29.
5. **Resto de defectos.** Redondeo comercial (DEF-23), secuencia en el código de operación (DEF-22), límite que incluya las interbancarias (DEF-20) y filtro por usuario en `/api/movimientos/{codigo}` (DEF-24). También el commit antes de responder (DEF-07), los mensajes en español (DEF-18) y un tiempo de respuesta constante en el login (DEF-16).

Cada corrección se comprueba sola. La prueba del defecto pasa a XPASS y el pipeline obliga a quitar la etiqueta `@DEF`, de modo que el caso queda como prueba de regresión.

**Riesgos abiertos.**
- **Rendimiento.** No se ha medido (Parte 3). Los defectos de concurrencia anticipan problemas bajo carga.
- **Workflow nuevo.** Todavía no corrió en GitHub. `gestion-casos` y `publicar` solo se prueban en `main`.
- **Kiwi TCMS.** La sincronización se probó con `--simular` sobre los 15 runs anteriores y con una importación real en un Kiwi 17 desechable (plan, TestRun, 331 casos, enlaces de defecto y capturas; fue antes de agregar CP-NA157 a NA160). Falta la primera sincronización en el Kiwi del alumno, con runs reales de `main`.
- **Concurrencia en GitHub.** Los 10 escenarios `@concurrencia` cumplen la regla de 200 de 200 en local. Falta repetir el job `api` en el runner de GitHub y revisar que ninguno dé XPASS.
- **Sin automatizar.** Tres casos quedan como evidencia manual: CP-NA28, CP-NA69 y CP-T19. Los números retirados (CP-A19, A38, T01, T03 y T27) y su motivo están en [`alcance-y-casos.md`](alcance-y-casos.md).
- **Deuda del código de prueba.**
  - La ayuda de concurrencia está repetida en tres módulos de pasos.
  - Los usuarios de prueba están en `conftest.py` y en `fixtures.ts`.

**Lecciones aprendidas.**
- **La regla del nivel más bajo abarata.** La API ejecuta 766 casos en unos 3.2 minutos y la web, 213 ejecuciones en 2.5 minutos. Cada ejecución web cuesta casi 3 veces más (0.71 s frente a 0.25 s).
- **El xfail estricto ligado a un DEF** deja el pipeline en verde con defectos conocidos, sin ocultarlos: avisa en cuanto se corrigen.
- **Concurrencia.** Una prueba de concurrencia solo sirve si es determinista: un cliente por hilo, `Barrier` y 200 de 200 corridas iguales. Con 20 no alcanzaba: CP-T20 pasaba 20 de 20 y aun así fallaba cerca de 2 de cada 100. Cuando la ventana es corta, se repite la ráfaga; las que no cumplen se documentan a mano en lugar de volverse inestables.
- **El contrato generado** encuentra lo que los casos escritos no prueban (DEF-29), pero cada hallazgo exige clasificarlo: en esta entrega hubo dos falsos positivos.
- **IDs estables** en el título y en la etiqueta, más un JUnit por CP, son lo que permite seguir un caso a lo largo de muchas ejecuciones.

**Recomendaciones para el equipo de pruebas.**
- Agregar `quality-gate` como check obligatorio.
- Sincronizar Kiwi después de cada run de `main`.
- Unificar la ayuda de concurrencia y los usuarios de prueba en un solo lugar.
- Ejecutar la Parte 3 con los flujos de dinero y sesión como prioridad.
