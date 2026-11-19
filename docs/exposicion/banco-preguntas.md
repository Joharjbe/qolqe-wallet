# Banco de preguntas · exposición final

Treinta y seis preguntas probables, en el orden del deck. La 14b, la 16b y la 28b se agregaron el 18-nov sin renumerar, porque el guion y la chuleta citan las demás por su número. Cada una tiene la respuesta en dos o tres líneas y la ruta exacta de la evidencia, desde la raíz del repositorio. Las cifras son las de [`chuleta-cifras.md`](chuleta-cifras.md); las limitaciones de la Parte 3 se defienden en [`defensa-limitaciones-p3.md`](defensa-limitaciones-p3.md).

## Parte 3: rendimiento (láminas 4 a 7)

**1. ¿Por qué esos seis flujos y no otros?**
Con los tres criterios del enunciado, y la regla es la del informe: un flujo es crítico si cumple al menos uno de los tres, frecuencia ≥ 15 %, mueve dinero o riesgo alto con evidencia. Toda operación de dinero entra (F-02, F-04 y F-05); por frecuencia, saldo y perfil (30 %), transferir y movimientos (15 %); por riesgo alto, el login, por el que pasan todas las sesiones (en el diseño estimé que su PBKDF2 se lleva ≈ 65 % del CPU de una sesión; medido después con py-spy, 53-63 % de las muestras), y movimientos, por su consulta N+1. Contactos y Otras no cumplen ninguno: son carga de fondo. Solo si pregunta por el diseño: `diseno-rendimiento.md` escribió «al menos dos», más estricta de lo que apliqué; al pie de la letra solo la cumplen F-02 y F-06, y está declarado ahí mismo.
Evidencia: `docs/Informe_Rendimiento_Qolqe.pdf`, §1 (pág. 1) · `docs/diseno-rendimiento.md:25-36` (la regla, en la 36) · `docs/informe.md:242` · lámina 4.

**2. ¿Por qué carga y estrés, y qué pasó con pico y resistencia?**
Cada tipo sale de una frase del requerimiento, con la regla de la clase 13: el tipo lo define la pregunta. Los cuatro aplican, los cuatro se ejecutaron y están en el informe con su justificación. Defiendo carga y estrés porque son las que pide el enunciado («Ejecutar al menos una prueba de carga y una de estrés») y responden «¿cumplimos en hora punta?» y «¿hasta dónde crecemos?». El pico cumple U-06, y el estrés lo refuerza: estuvo 6 min seguidos por encima de 300 simultáneos con p95 de consultas ≤ 76 ms y 0 % de error.
Evidencia: `docs/Informe_Rendimiento_Qolqe.pdf`, §3 (pág. 6) y §8 (pág. 38) · `P2_Parte3_Enunciado.pdf`, §3, paso 5 · `docs/informe.md:205` · lámina 4.

**3. ¿Qué no se podía convertir en umbral, y qué supuesto tomaste?**
Dos frases no traen número. «Sin acumular retrasos»: con modelo abierto, retraso es que la cola crezca, y lo mido con throughput ≥ 98 % de lo ofrecido y 0 sesiones descartadas (S-04, U-04 y U-05). «Una degradación razonable»: tomé hasta 2 × el umbral normal, 1 600 y 3 000 ms, con error ≤ 1 % y 0 descartadas; es un supuesto mío (S-05). Además, a los tiempos les faltaba la carga: la hora punta, 100 simultáneos (S-01). En clase, el tester no inventa el dato que falta, lo pregunta al negocio; aquí no había a quién, así que cada supuesto quedó escrito.
Evidencia: `docs/Informe_Rendimiento_Qolqe.pdf`, §5, tabla S-01 a S-06 (pág. 12) · `docs/informe.md:205` · lámina 5.

**4. ¿De dónde salen los 100 usuarios simultáneos?**
Del requerimiento: 3 000 sesiones por hora son 0,833 por segundo, y con sesiones de 120 s la ley de Little da L = λ·W = 100. En la carga se midieron entre 98,8 y 101,0 simultáneos por minuto.
Evidencia: `docs/diseno-rendimiento.md:111-113` · `tests/performance/resultados/carga/20261111-1833/veredicto.md:66` · lámina 6.

**5. ¿Varios VUs comparten usuario?**
No: 3 000 usuarios distintos, uno por VU, con S/ 10 000 cada uno; k6 los asigna con `SharedArray` y `exec.vu.idInTest`. Así una regla como el límite diario no se confunde con una falla de rendimiento.
Evidencia: `docs/informe.md:205` · `docs/Informe_Rendimiento_Qolqe.pdf`, págs. 4 y 10 · lámina 6.

**6. ¿Por qué k6 y no JMeter?**
Porque el requerimiento da la carga como tasa de llegada y pide «sin acumular retrasos»: k6 tiene modelo abierto, cuenta las sesiones que no pudo iniciar y termina con código 99 si falla un umbral. Frente a JMeter, Gatling, Locust, Artillery y Taurus, k6 es el único que cumple los cuatro criterios eliminatorios; JMeter cumple uno.
Evidencia: `docs/Informe_Rendimiento_Qolqe.pdf`, §2 (pág. 3) · `docs/informe.md:201`.

**7. ¿Por qué Qolqe en Docker con 1 CPU y 1 GB?**
Para que el umbral signifique algo: la cuota deja a Qolqe en 1 CPU y a k6 en los otros 9 núcleos, así no compiten, y el límite se repite igual en cada corrida (V-05 comprueba `cpu.max` cada vez). En local Qolqe tendría los 10 núcleos y saturarlo pediría miles de VUs en el mismo CPU que k6.
Evidencia: `docs/diseno-rendimiento.md:364-371` · `tests/performance/README.md:34-42` · fila V-05 de cada `veredicto.md`.

**8. ¿Pasó o no pasó?**
Carga, en hora punta: PASA U-01 a U-05 y U-07: 93 y 128 ms frente a 800 y 1 500, 0,00 % de error, 9,77 req/s frente a 9,6, 0 sesiones descartadas y 0 descuadres. Estrés: ahí U-01 a U-04 son el criterio de capacidad (por eso el comparativo los marca «no aplica» en esa columna): se cumplen hasta 876 simultáneos y con 946 fallan los cuatro a la vez (13,7 % de error); la capacidad, U-08, es 850, y U-07 PASA con 0 descuadres. Pico (U-06) y resistencia (U-09): PASAN. Si pregunta por el código 99 de k6 o por el 20,81 % de U-03 del estrés: es la rampa completa, colapso incluido; el estrés se juzga por ventanas de 30 s, con U-08.
Si pregunta por qué U-04 dice «≥ 90 %» en el estrés y no 98 %: en ventanas de 30 s, U-04 usa la tolerancia de 3σ de la fase base, 9,7 % con 1 CPU, o sea atendido ≥ 90 %; con el 98 % estricto la capacidad sigue en 850, porque las ventanas bajo el 98 % están aisladas, nunca dos seguidas. Y U-05 en el estrés: 0 sesiones descartadas en las 32 ventanas, también en la de 946, así que k6 siguió ofreciendo toda la carga y la caída es de Qolqe.
Evidencia: `tests/performance/resultados/carga/20261111-1833/veredicto.md:24-30` · `tests/performance/resultados/estres/20261111-1940/veredicto.md:5`, `:24-31`, `:41` (tolerancia), `:43` · `tests/performance/resultados/estres/20261111-1940/ventanas.csv`, columna `descartadas` · `docs/Informe_Rendimiento_Qolqe.pdf`, §5, fila «Capacidad (U-08)» (pág. 11) · `tests/performance/resultados/comparativo/veredictos.md:10-18` · `docs/informe.md:218-222` · `docs/Informe_Rendimiento_Qolqe.pdf`, §8 (pág. 38) · lámina 7.

**9. ¿Cómo separas los 422 de las fallas de rendimiento?**
Un 422 por regla de negocio es un error de datos, no de rendimiento: se cuenta aparte, con V-02, que exige 0 (S-06). En la carga hubo 0 errores de rendimiento y 0 de datos, y V-02 dio 0 en las 8 corridas.
Evidencia: `docs/Informe_Rendimiento_Qolqe.pdf`, §5, S-06 (pág. 12) · `tests/performance/resultados/carga/20261111-1833/veredicto.md:14`, `:85-89` · `tests/performance/resultados/comparativo/veredictos.md:21`.

**10. ¿Cuál es el cuello de botella y cómo lo demuestras?**
La escritura de la sesión en SQLite durante el login (`autenticacion.py:136`), con tres evidencias: 733 de las 829 excepciones del estrés son `database is locked` en ese INSERT, la foto de hilos con 2 CPU tiene las 40 plazas del pool en esa línea, y py-spy da a `verificar_pin` el 53-63 % de las muestras. No es solo CPU: el colapso llega con Qolqe al 75,5 % y 2 CPU dan × 1,53, no × 2. Y, como dice la clase 14, al resolver un cuello de botella puede aparecer el siguiente: el candidato es el N+1 de movimientos, que pesa el 32 % del CPU cuando sobra CPU (H2). Por eso la recomendación es volver a medir con `correr.sh estres` después de cada corrección.
Evidencia: `docs/informe.md:238-243`, `:362` · `docs/Informe_Rendimiento_Qolqe.pdf`, §8, «Acciones recomendadas» (pág. 41) · `tests/performance/resultados/estres/20261111-1940/qolqe.log.gz` · `tests/performance/resultados/escalabilidad/20261111-2103/hilos_meseta.txt` · `docs/Informe_Rendimiento_Qolqe.pdf`, Tabla 14 (pág. 38).

**11. ¿Quedó alguna operación de dinero a medias o duplicada?**
Cero descuadres en las 8 corridas, con seis chequeos (C1 a C6) de saldos y movimientos antes y después. En el colapso del estrés, 98 operaciones de dinero quedaron sin respuesta y concilian en C6, y 2 transferencias se aplicaron aunque el cliente recibió un timeout: el dinero cuadra, pero una app que reintente podría cobrar dos veces, porque no hay clave de idempotencia. Por eso la recomiendo.
Evidencia: `tests/performance/resultados/estres/20261111-1940/veredicto.md:44-45` · `docs/Informe_Rendimiento_Qolqe.pdf`, págs. 16 (C1 a C6), 22 y 41 · `docs/informe.md:245`.

**12. ¿Por qué la resistencia duró 60 minutos y no 18 horas?**
Porque lo que busca es deriva, y en 60 min no la hubo: el p95 final entre el inicial da 0,98 × en consultas y 1,01 × en dinero, y el RSS proyectado a 54 000 sesiones es 92 MB frente a 700. Las 18 h se proyectan, y lo digo así; el resto de limitaciones está en la hoja de defensa.
Evidencia: `tests/performance/resultados/resistencia/20261111-1958/veredicto.md:67-72` · `docs/exposicion/defensa-limitaciones-p3.md`.

**13. Tienes CI/CD: ¿por qué el rendimiento no está en el pipeline?**
Como enseña la clase 12, el rendimiento va en la etapa no funcional, programado o por release, no en cada push. Además, la carga sola dura 19,1 min, más que el pipeline entero (13 min 38 s en el run #24). Y un umbral de latencia solo significa algo en un entorno fijo: la misma suite de API (766 pruebas), en el mismo commit, tardó 386 s en el intento 1 del run #24 y 245 s en el intento 2. Con tan poco margen en mi criterio de validez V-06, que no es el umbral del cliente (con 1 usuario el login ya da 92 ms frente a 80), daría rojos falsos; la evidencia sí viaja: está versionada y el job `reportes` la publica en el sitio.
Evidencia: `docs/pipeline.md:3`, `:47-56` · `docs/arquitectura.md:254-260` · `tests/performance/resultados/referencia/20261111-1828/veredicto.md:25` · log del job `api` de los dos intentos del run #24 (commit `1025a78`): «707 passed, 59 xfailed in 386.20s» y «in 244.79s» · `.github/workflows/pruebas.yml:302-303` · https://joharjbe.github.io/qolqe-wallet/rendimiento/.

## Consolidado (láminas 8 a 17)

**14. ¿Por qué esas herramientas y no otras? ¿Por qué dos lenguajes?**
Cada una responde una pregunta que las otras no; donde se solapan es a propósito y con otro oráculo: la API prueba la regla que produce el error y la web, que el error le llega al usuario. Alternativas descartadas: Postman y Newman (Newman ya no recibe actualizaciones y no ejecuta Gherkin), Karate (su README dice *Readable Specification: No*), Cypress (no controla dos navegadores a la vez, y CP-NW18 necesita dos sesiones), Selenium (no trae runner ni reporte) y Robot (no ejecuta `.feature`). Python para la API porque Qolqe es Python y la clase 10 enseña pytest y Schemathesis; TypeScript para la web porque la clase 11 enseña playwright-bdd y el runner de Playwright, con `repeatEach` y `failOnFlakyTests`, es de Node. Comparten artefactos, no código: el Gherkin, las etiquetas y el JUnit.
Evidencia: `docs/arquitectura.md:264-303` (§2 y «¿Por qué Python y TypeScript?») · lámina 10.

**14b. ¿Qué riesgos de automatizar tuviste en cuenta?**
Los de la clase 11 (ISTQB 6.2), cada uno con lo que hice. Depender de un proyecto que se abandone: descarté Newman, que ya no recibe actualizaciones, y Dredd, archivado en noviembre de 2024. Automatizar donde la prueba manual es más adecuada: CP-NA28, CP-NA69 y CP-T19 quedaron como evidencia manual, porque no dan el mismo resultado en todas las corridas. Subestimar el costo de mantener los scripts: Page Object con componentes, para que un cambio de pantalla se corrija en un solo lugar. Confiar demasiado en la herramienta: cada hallazgo de Schemathesis se clasificó (dos fueron falsos positivos), y la capacidad de IA solo propone.
Evidencia: `docs/arquitectura.md:271-272` · `docs/alcance-y-casos.md:69` y «Lo que no se automatizó» · `docs/informe.md:356` · láminas 10, 13 y 18.

**15. ¿Cómo decides si un caso va por API o por web?**
Con la regla de la clase 11: cada regla se prueba en el nivel más bajo donde se pueda detectar. Por la web va solo lo que se ve en la pantalla, los recorridos críticos y que un error de la API llegue al usuario; por eso 3 criterios (dos SMS y la concurrencia) no tienen caso web. Y la clase 10 da tres ventajas de probar por API: es más rápida y estable que la UI, llega a reglas que la UI esconde y se automatiza temprano. La segunda pasó aquí: DEF-03, aceptar una solicitud vencida, no se alcanza por la pantalla, porque la interfaz oculta el botón (CP-W15); por la API, sí (CP-A32).
Evidencia: `docs/alcance-y-casos.md:52-60` · `docs/informe.md:34-39`, `:48`, `:195` · láminas 10 y 12.

**16. ¿Qué tan madura está la API? ¿Tiene deuda técnica?**
La Entrega 1 era esta parte. Cobertura: los 51 criterios tienen caso de API, 198 funcionales y 78 técnicos, más el contrato de 19 operaciones. En el run #24, por caso, 237 pasan y 39 en fallo esperado estricto con su DEF; en ejecuciones, 766: 707 pasan y 59 en fallo esperado, 0 fallan. Sin automatizar quedan tres casos de evidencia manual, con su motivo (CP-NA28, CP-NA69 y CP-T19). Deuda técnica: los dos costos que había declarado en el código de prueba, no en la cobertura, los pagué el 18-nov. Los 45 pasos de G4 pasaron de `conftest.py` a su propio módulo, `pasos_g4.py`, y los usuarios de la semilla, que estaban copiados en varios archivos de pasos, quedaron en un solo lugar, `conftest.py`. No cambió ninguna prueba: antes y después, las mismas 766 con los mismos IDs, 707 pasan y 59 en fallo esperado. Lo que queda es una decisión con su motivo, no una deuda: la ayuda de concurrencia sigue en tres módulos, con tres contratos distintos, porque unificarla obliga a volver a medir los 10 escenarios con 200 de 200.
Evidencia: `docs/trazabilidad.md:11-16` · `docs/informe.md:98`, `:346-350` · `tests/api/conftest.py:9-17`, `:112-115` · lámina 11.

**16b. ¿Puedes correr la API en vivo?**
Un caso sí; la suite entera no cabe en la exposición: son 766 ejecuciones, unos 3,2 min en la laptop y entre 245 y 386 s en el runner (los dos intentos del run #24). El caso es CP-A28, el que el PR #10 rompe a propósito: con Qolqe en el 8000, `python -m pytest tests/api -k cpa28 -v` recolecta 1 de 766 (en el ensayo del 18-nov: `1 passed, 765 deselected in 0.52s`, 2 s en total). Después de k6 el 8000 está apagado: primero se levanta en otra terminal con el `.venv`, `QOLQE_BD=.demo-data/qolqe.db QOLQE_MODO_PRUEBA=1 python -m uvicorn qolqe.main:app --port 8000`. La suite completa es `npm run test:api`, y su referencia es el reporte del run: 766, 707 pasan, 59 en fallo esperado y 0 fallan.
Evidencia: `docs/informe.md:353` («Lecciones aprendidas») y `:98` · `README.md:225-230` y `:247` · log del job `api` de los dos intentos del run #24: «707 passed, 59 xfailed in 386.20s» y «in 244.79s» · https://joharjbe.github.io/qolqe-wallet/api/ · lámina 11, nota de orador.

**17. ¿Cómo registras un defecto conocido sin romper el pipeline?**
Como fallo esperado estricto ligado a su DEF: el hook convierte cada `@DEF-xx` en `xfail(strict=True, raises=AssertionError)`. Si alguien corrige el defecto, la prueba da XPASS y el job se pone rojo hasta retirar la etiqueta; si falla por otra causa, cuenta como fallo y no como el defecto.
Evidencia: `tests/api/conftest.py:20-26` · `docs/informe.md:69` · `docs/defectos.md:4`.

**18. ¿Por qué la web corre tres veces?**
Porque una prueba que pasa dos de tres veces es una prueba frágil, *flaky*, como la llama la clase 11, no una aprobada: con `--repeat-each=3` y `failOnFlakyTests`, una sola frágil pone el job `web` en rojo. En las láminas y en Playwright se dice «inestable»; es lo mismo. Ya pasó: en el run #13, CP-W10 salió inestable, el pipeline quedó en rojo y el error era de la prueba.
Evidencia: `.github/workflows/pruebas.yml:218` · `playwright.config.ts:23-25` · `docs/informe.md:190` · lámina 12.

**19. ¿Por qué Page Object con componentes, y cómo escala?**
Porque el paso de Gherkin no sabe nada de la pantalla: pide una acción, y el menú, los diálogos y el aviso son componentes escritos una vez; Screenplay está pensado para suites grandes, y lo usaría con más de unos 100 escenarios o varios equipos: con 58 sumaría actores, tareas y preguntas sin un problema que lo pida; y Page Factory no aporta porque Playwright resuelve el localizador en cada uso. Escala porque un G5 es un `.feature`, un archivo de pasos y sus Page Objects, registrados en `fixtures.ts`, sin tocar los componentes, y el job `estatico` falla si un paso usa un localizador. Lo que sí cambia está fuera del patrón: la trazabilidad, que hoy conoce dos módulos, y la infraestructura, que corre con un solo worker porque todas las pruebas comparten una base.
Evidencia: `docs/arquitectura.md:309-336` (§3.1), `:430-456` (§3.3), `:469-484` (§3.5, escalabilidad), `:503-511` (§3.7, cuándo pasaría a Screenplay) · `.github/workflows/pruebas.yml:84-89` · lámina 13.

**20. ¿Para qué sirve cada uno de los 8 jobs?**
Lo que los ordena es la clase 12: el CI hace que las suites corran solas, en una máquina limpia, y dejen evidencia; lo rápido va primero, y lo que no hace falta en cada push se programa o va en el PR; por eso el rendimiento va aparte (pregunta 13). Tener API y web en un solo workflow es lo que la misma clase llama una simplificación válida para el proyecto, no la regla general. Job por job: `estatico`: *fail fast* sin servidor, en un minuto detecta lo que rompería todas las suites. `contrato`: la primera prueba dinámica, al inicio. `api`: las reglas de negocio, con los defectos como fallo esperado estricto. `web`: la etapa más cara, × 3 contra las inestables, solo con la API en verde. `quality-gate`: los criterios de salida; corre con `always()`, da veredicto siempre y es check obligatorio de `main`. `reportes`: la matriz y el sitio, y corre aunque fallen las pruebas, porque el reporte explica el fallo. `gestion-casos`: preparado para un Kiwi accesible desde internet; hoy Kiwi está en mi máquina, así que deja el aviso y la sincronización es *pull*. `publicar`: el último, sube Pages y deja el enlace en el resumen, solo en `main`.
Evidencia: `docs/pipeline.md:17-26` · lámina 14.

**21. ¿Por qué el contrato ahora va al inicio, y qué decías antes?**
Antes corría en paralelo con `api`, porque son independientes (otro runner, otra base); así lo dice `docs/pipeline.md:18` en el tag `parte-3`. La indicación pide validarlo al inicio, y el razonamiento es que si la API no cumple el contrato que ella misma publica, los casos funcionales prueban sobre una base que no se sostiene. Cuesta lo que dura el job: 41 s en el run #20, cuando iba en paralelo, y entre 35 y 54 s desde que va delante (#21 a #24).
Evidencia: `git show parte-3:docs/pipeline.md` (línea 18) · anuncio de Canvas del 15-nov, punto «Pipeline» · commit `2bbf44f` · `docs/pipeline.md:11`, `:20` · `.github/workflows/pruebas.yml:1-3`, `:95` · API de GitHub, inicio y fin del job `contrato` en cada run.

**22. Si el contrato falla, ¿se puede fusionar el PR igual?**
No: GitHub cuenta un job omitido como aprobado, así que `contrato`, `api` y `web` empiezan con una guarda que falla en segundos si la etapa anterior no terminó en `success`, y el check queda en rojo de verdad. `api`, `web` y `quality-gate` son checks obligatorios de `main`, también para el dueño, y `quality-gate` es la segunda defensa: corre con `always()` y cuenta como no aprobada una etapa omitida.
`main` exige los tres (`quality-gate`, desde el 18-nov): la fila 1b de `hoja-demo.md` da `["api","web","quality-gate"]`, y es lo que dicen la lámina 15, `docs/pipeline.md:32` y `docs/informe.md:164`.
Evidencia: `.github/workflows/pruebas.yml:100-105`, `:148-153`, `:192-197`, `:237-240` · `docs/pipeline.md:32-36` · [PR #10](https://github.com/Joharjbe/qolqe-wallet/pull/10), run #25: `web` en rojo por su guarda, no omitido (`docs/img/demo-gate-rojo.png`) · `gh api repos/Joharjbe/qolqe-wallet/branches/main -q .protection.required_status_checks.contexts`.

**23. ¿Qué evalúa el quality gate y qué deja fuera?**
Cuatro criterios de salida: `estatico`, `contrato`, `api` y `web` en `success`, con los defectos conocidos como fallo esperado estricto y la web sin inestables en las tres corridas; el propio job los escribe en el resumen del run. No evalúa el rendimiento ni el job `reportes`, y lo dice en el mismo resumen para que nadie crea que cubre más.
Evidencia: `.github/workflows/pruebas.yml:244-280` (alcance en `:261`) · `docs/pipeline.md:23`, `:38-45` · lámina 15.

**24. ¿Qué haces si el gate se pone rojo en vivo porque un `@concurrencia` da XPASS?**
Digo que es el diseño funcionando: esos casos son fallo esperado estricto, y si en ese run la carrera no se reprodujo, la prueba da XPASS y pone `api` en rojo sin que nadie haya corregido el defecto. Lo muestro en el JUnit del job y lo reviso con `pytest -m concurrencia --runxfail`: si no cumple 200 de 200, pasa a evidencia manual como CP-NA69. Al 18-nov, los 9 runs del #16 al #24 salieron en verde, el #24 en sus dos intentos; el #25 es el PR #10, en rojo a propósito. Si hay runs nuevos, se cuentan con el mismo comando. La clase 12 lo dice así: el pipeline es la referencia, no la máquina de nadie. Por eso cito el veredicto del run, y la regla de 200 de 200, que solo se midió en local, la declaro como límite.
Evidencia: `docs/pipeline.md:116-123` · `docs/defectos.md:6` · `docs/informe.md:345` · `gh run list -R Joharjbe/qolqe-wallet --workflow pruebas.yml`.

**25. ¿Dónde está el reporte con evidencia, y cómo se elige?**
Al lanzar el workflow a mano se elige `con-imagenes` o `sin-imagenes`; push y PR van sin imágenes porque el artefacto `sitio` de un run con evidencia completa pesa casi 200 MB (~416 MB entre todos sus artefactos) y se guarda 7 días. `publicar` es el último job y deja en el resumen el enlace al sitio; la copia con imágenes del run #18 está offline en el escritorio, porque su `sitio` vencía el 18-nov (7 días de retención) y el sábado ya no está. Las capturas por caso siguen en su artefacto `trazabilidad`, hasta el 09-feb-2027.
Evidencia: `.github/workflows/pruebas.yml:12-20`, `:35`, `:396-398` · `docs/pipeline.md:58-69` · https://joharjbe.github.io/qolqe-wallet/ · `gh api repos/Joharjbe/qolqe-wallet/actions/runs/43109117336/artifacts` · `~/Desktop/respaldo-sitio-con-imagenes` (las trazas, con `cd ~/Desktop/respaldo-sitio-con-imagenes && python3 -m http.server 8100` y http://localhost:8100/web/; el 8000 es del Qolqe de la demo: `docs/exposicion/hoja-demo.md:37`, `scripts/preparar-demo.sh:8`).

**26. Las pruebas corren muchas veces: ¿cómo sigues un caso? ¿Por qué Kiwi?**
En `historial.html`, donde cada run y cada reintento es su propia columna (la página dibuja los últimos 15 runs y `historial.json` guarda 30; al 18-nov, con el run #28, eran 7), y en Kiwi TCMS, donde cada run de `main` es un TestRun y cada caso acumula sus ejecuciones; al 18-nov mi Kiwi tenía 10 TestRuns, y el del run #18 tiene 335 ejecuciones, 40 enlaces de defecto y 216 capturas. Comparé ocho alternativas. Kiwi es gratis, sin límite de runs y su plugin oficial lee el JUnit que ya genero. Qase guarda 30 días y dos runs activos; TestRail, Xray y Zephyr dan 30 días de prueba y vencían a mitad del curso; QMetry, que nombra la clase 7, da 14 días y pide montar Jira; TestLink no importa JUnit; Testmo y Allure TestOps son de pago; y la matriz en el repo, que ya tenía, depende de artefactos que GitHub borra a los 90 días.
Evidencia: `docs/pipeline.md:81-84` · `docs/gestion-casos.md:5-21` (comparación, con QMetry, y «Por qué Kiwi») · lámina 17 · https://joharjbe.github.io/qolqe-wallet/historial.html · `.github/scripts/trazabilidad.py:471-474` · `docs/informe.md:340` (se reproduce con `scripts/kiwi_sincronizar.py --simular --run 18`) · `docs/img/kiwi-testrun-18.png` y `docs/img/kiwi-caso-ejecuciones.png`.

## Capacidad de IA (láminas 18 a 21)

**27. ¿Qué es la capacidad de IA?**
Un diagnóstico de los fallos de un run: enfoque A de la clase 15, IA para probar, en la fase de Reporte. Lee el JUnit por caso y los logs que el pipeline ya publica, agrupa los fallos con código determinista y, por grupo, el modelo propone si es defecto real, prueba inestable o error de entorno, con su DEF y su evidencia. No decide nada: no es un job del workflow, se corre a mano sobre los artefactos de un run, y CP-IA-07 comprueba que el quality gate no lo nombra en su `needs` y que correrlo no cambia ningún archivo del pipeline. La IA propone y el tester decide: es el *human-in-the-loop*.
Evidencia: `docs/capacidad-ia.md:46-94` (§1), `:709`, `:788-794` · `herramientas/diagnostico_ia/__main__.py:18-19` · `tests/diagnostico/test_no_decide.py:58` (CP-IA-07) · `.github/workflows/pruebas.yml:239`.

**28. ¿Qué aporta frente a unas reglas sin IA, y cómo lo validaste?**
Con un eval de 52 fallos etiquetados con su procedencia (40 defectos reales, 4 pruebas inestables y 8 errores de entorno sembrados), sin las cuatro fugas que traían la respuesta, contra un control sin IA, unas reglas de veinte líneas, sobre los mismos casos. En defecto real el modelo acierta 28 de 36 y las reglas 34 de 36, el DEF sale 0 de 38 (las reglas ni lo intentan) y solo en error de entorno gana el modelo (8 de 8 contra 7 de 8, sobre casos sembrados): tal como está, no sustituye al tester ni a las reglas. En los archivos, ese control se llama «línea base» (`evals-lineabase.md`); en la expo digo «control sin IA», porque en el curso la línea base es la de rendimiento.
Evidencia: `docs/capacidad-ia.md:323-364` (§5.1), `:471-479`, `:859-909` (§9) · `docs/resultados-capacidad-ia/evals-google.md:74-79` · `docs/resultados-capacidad-ia/evals-lineabase.md:18-22`.

**28b. ¿Por qué unas reglas sin IA son el control contra la falsa cobertura?**
En la clase 15, falsa cobertura es que lo generado parezca cubrir sin cubrir. Aquí sería un número alto de aciertos de la IA que haga creer que el diagnóstico está cubierto. Si unas reglas sin IA aciertan igual sobre los mismos casos, ese número no prueba que la IA aporte; y aciertan más: 34 de 36 contra 28 en defecto real. Por eso las dos columnas van sobre los mismos 48 casos.
Evidencia: `docs/resultados-capacidad-ia/evals-google.md:74-79` · `docs/resultados-capacidad-ia/evals-lineabase.md:18-22` · lámina 19, tarjeta «Un control sin IA, contra la falsa cobertura».

**29. ¿Por qué no usaste LLM-as-judge?**
Porque el juez también se equivoca con seguridad, y entonces no habría nada firme contra qué medir. Cada respuesta correcta del eval cita un archivo y una línea, y `armar.py` falla si una cita deja de ser cierta: eso se audita, el juicio de un modelo no.
Evidencia: `docs/capacidad-ia.md:784`, `:849` · lámina 19.

**30. ¿Le mandaste datos sensibles a la IA? ¿No es Shadow AI?**
Es el riesgo de privacidad y la pregunta 6 del checklist de la clase 15. Al modelo va el JUnit por caso y hasta 10 líneas de log de 240 caracteres; eso incluye celulares y PIN de usuarios de prueba que están en los `.feature`, ficticios, no de clientes. La clave va en un `.env` que está en `.gitignore`. No es Shadow AI: el punto 8 autoriza usar IA y no van datos reales. Y la guarda de privacidad mira también la salida: paró 2 respuestas que copiaban un celular (ORO-09 y ORO-11).
Evidencia: `docs/capacidad-ia.md:178-179`, `:282`, `:781`, `:811` · `docs/resultados-capacidad-ia/evals-google.md:47-48`.

**31. ¿Cómo aplicaste el checklist de la clase?**
Con las 6 preguntas adaptadas a una propuesta de diagnóstico: la IA no genera casos, así que cada pregunta se lee sobre lo que propone (tabla de `capacidad-ia.md` §7). La que más pesa es la 5, «¿algún caso contradice el requisito?»: sí, los 8 casos de concurrencia que llamó inestables contradicen la regla de 200 de 200. Después va una lista propia de 9 puntos antes de usar una propuesta.
Evidencia: `docs/capacidad-ia.md:796-828` · `docs/resultados-capacidad-ia/evals-google.md:100-107` · `docs/defectos.md:6`.

**32. Si pierde contra las reglas, ¿para qué sirve? ¿Por qué la presentas?**
Porque el punto 8 pide qué aporta y cómo se validó, y la validé: sin el eval habría presentado un reporte prolijo con confianza alta en 35 de 48 casos. Sirve como primer pase que ahorra la primera lectura: agrupa 40 fallos en 32 grupos, 20 % menos (62 en 29 con los artefactos crudos del run #20), y acierta los 8 errores de entorno, que son sembrados; en lo inestable acierta los 4, pero llamó inestables a 8 defectos reales. No medí minutos: lo medido son lecturas. No sirve para abrir un DEF ni para cerrar un caso sin mirar el artefacto.
Evidencia: `docs/capacidad-ia.md:73-74`, `:829`, `:854`, `:887-892` · `docs/resultados-capacidad-ia/evals-google.md:32`, `:62`, `:78` · lámina 20.

**33. ¿Y si la IA se equivoca, o un log le da órdenes?**
Se equivoca y no rompe nada, porque el gate es determinista. Lo que sí medí, con red teaming e inyección de prompts como en la clase 15, es que una orden escrita en la salida de un caso le cambió la clase 5 de 5 veces, contra 0 de 5 sin la orden, y 4 de esas 5 respuestas pasaron las guardas. Los guardrails (las guardas del código) frenaron el `DEF-99` inventado todas las veces, pero no la clase: es la limitación LIM-IA-01, y por eso una propuesta no se usa sin mirar el artefacto.
Evidencia: `docs/capacidad-ia.md:602-654` (§5.3f), `:788-831` (§7) · `docs/resultados-capacidad-ia/inyeccion-google.json:73`, `:144`, `:146`, `:215` · `tests/diagnostico/test_inyeccion.py:312` (fallo esperado estricto).
