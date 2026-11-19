# Chuleta de cifras · exposición final

Una cifra por dato: **la que digo en la expo**, con su fuente; si el repo tiene otro valor legítimo, va por qué no lo digo. Verificado el 17-nov-2026 y revisado el 18-nov contra el deck de 21 láminas; runs de `Joharjbe/qolqe-wallet`.

Rutas abreviadas: **carga** = `tests/performance/resultados/carga/20261111-1833/veredicto.md` · **estrés/** = `tests/performance/resultados/estres/20261111-1940/` · **ventanas** = `estrés/ventanas.csv`, una fila por ventana de 30 s, citada por su columna `minuto` · **2cpu/** = `tests/performance/resultados/escalabilidad/20261111-2103/` · **comparativo** = `tests/performance/resultados/comparativo/veredictos.md` · **Informe** = `docs/Informe_Rendimiento_Qolqe.pdf` · **evals** = `docs/resultados-capacidad-ia/evals-google.md` · **iny** = `docs/resultados-capacidad-ia/inyeccion-google.json`. Las demás, desde la raíz del repositorio.

## 1. El p95: uno por grupo

**Digo: 93 ms en consultas y 128 ms en dinero, en hora punta.** Límites: 800 y 1 500 ms.

Por qué ese: es el p95 de grupo en la fase estable de la carga (100 simultáneos, 15 min), la prueba que responde «¿cumplimos en hora punta?». U-01 y U-02 se resumen por grupo, y es el de la lámina 7. Fuente: carga:24-25 · `docs/informe.md:218-219`.

| Otro valor | Qué es y por qué no lo digo |
|------|------------------------|
| 105 (login) y 134 (transferir) | El endpoint más lento de cada grupo (carga:51, :60). Cumple, pero el veredicto va por grupo. Si preguntan por el más lento, son estos |
| 93,2 y 128,2 | El mismo p95 según k6, que interpola (carga:95, :107); el análisis usa rango más cercano (`docs/informe.md:214`) |
| 101 y 141 | La peor ventana de 1 min (carga:65): es el criterio U-05 (b), no el p95 de la fase |
| 73/118 y 83 (login) | El estrés en la ventana de 876 simultáneos (ventanas, minuto 11.750): la columna 876, bajo ESTRÉS, de la matriz de la lámina 7. Es la última ventana que cumple, no la hora punta |
| 78/123, 95/127 y 75/121 | Pico, resistencia y estrés de toda la rampa hasta la capacidad (comparativo:35, :38, :36). La lámina 7 trae carga y estrés en su matriz; el pico va en la pastilla «✓ Pico · U-06» de la tarjeta de la derecha y la resistencia en la nota de orador. Si preguntan por el peor p95 de U-01: 106, el login en resistencia (`docs/informe.md:218`); en el pico el login llegó a 114 con ~300 simultáneos, y eso se juzga con U-06 (Informe, Tabla 8, pág. 29) |
| 70/136, 81/137 y 73/119 | Referencia y calibración con 1 VU, y estrés con 2 CPU (comparativo:32, :33, :37): no son hora punta. ¿Dinero 136 con 1 VU? Con 1 VU macOS puede llevar la vCPU a núcleos de eficiencia (`tests/performance/README.md:128`): explicación probable, no medida aparte |
| ≈ 103, 106 y 137 | La demo de 2,5 min (`tests/performance/README.md:113`; comparativo:39): 430 peticiones, no es evidencia del informe |
| 92 (login, 1 VU) | Criterio de validez V-06 (`tests/performance/resultados/referencia/20261111-1828/veredicto.md:25`), no resultado de carga |

## 2. El resto de la Parte 3

Ordenado como el foco: modelo de carga (lámina 6), resultados (lámina 7) y análisis.

| Dato | Digo | Fuente |
|---------|-------------------------|----------------|
| Hora punta | 3 000 sesiones/h = 100 simultáneos (Little: 0,833 × 120 s) | `docs/diseno-rendimiento.md:111-113` |
| Think time | 10 a 25 s entre acciones, triangular(10, 19, 25) con media 18 s: 6 pausas = 108 s, y 12 s de cierre por sesión | `docs/diseno-rendimiento.md:114-115` · Informe §4 (pág. 8) |
| Mezcla | 1 login por sesión y 6 operaciones: saldo y perfil 30 %, movimientos 15, transferir 15, contactos 10, recarga 10, deudas 6, pago 4, otras 10. En la carga, la peor operación quedó a 0,78 pp (V-03) | P3 §4 · carga:15, :76-83 |
| Ramp-up | Carga: 120 s, lo que dura una sesión (M-24). Estrés: 180 s a 100 y +100 simultáneos por minuto durante 1 380 s (M-17) | Informe §4 (págs. 7 y 9) · lámina 6 |
| Cima del estrés | 2 400 = 1,33 × la saturación que estimé antes de medir (M-14); k6 la cortó a los 947,7 s con su red de seguridad | Informe págs. 8, 16 y 17 |
| Datos | 3 000 usuarios distintos, uno por VU, con S/ 10 000 cada uno | `docs/informe.md:205` · Informe págs. 4 y 10 |
| Peticiones de la carga | 8 796 en la fase estable; 9 975 en toda la corrida | carga:62, :4 |
| Error, throughput, cola | 0,00 % · 9,77 req/s (≥ 9,6) · 0 sesiones descartadas | carga:26-28 |
| Errores de datos (V-02) | 0 en las 8 corridas: los 422 de negocio se cuentan aparte, no como fallas de rendimiento | comparativo:21 · carga:14 · Informe pág. 12 (S-06) |
| Dinero | 0 descuadres en todas las corridas | línea 20 de cada `tests/performance/resultados/*/*/verificacion_dinero.txt` |
| Capacidad | **850 con 1 CPU**, 8,5 veces la hora punta y 2,8 veces el pico; 1 300 con 2 CPU (× 1,53, no × 2). La hipótesis previa, 1 500 ± 300, quedó refutada | estrés/veredicto.md:31, :42 · 2cpu/veredicto.md:31 · `docs/informe.md:226` |
| Por qué 850 | 876, la última ventana de 30 s que cumple, redondeado hacia abajo a 50 (S-10) | estrés/veredicto.md:31, :40 · lámina 7, «= 876 ↓50» junto al 850 |
| Estrés en 876 (min 11,75) | consultas 73 ms, dinero 118, login 83, 0 % de error, 85,2 de 86,0 req/s; p95 de todas las peticiones, 77,6 | ventanas, minuto 11.750 |
| Estrés en 946 (min 12,25) | consultas 13 296 ms, dinero 18 672, login 17 685, 13,7 % de error, 26,1 de 90,9 req/s; p95 de todas, 13 374 | estrés/tabla_estres.md:15 (T9) · ventanas, minuto 12.250 |
| U-04 en el estrés | ≥ 90 % de lo ofrecido por ventana de 30 s (lámina 7, fila U-04, «≥ 90 %»; lámina 5, tarjeta U-08, cuya nota de orador da el 90 %): en ventanas tan cortas, U-04 usa la tolerancia máx(2 %, 3σ de la fase base), 9,7 % con 1 CPU (10,6 % con 2 CPU, ≥ 89 %). Con el 98 % estricto la capacidad es la misma, 850: las ventanas bajo el 98 % están aisladas, nunca dos seguidas | Informe, §5, fila «Capacidad (U-08)» (pág. 11) · estrés/veredicto.md:41 |
| U-05 en el estrés | 0 sesiones descartadas en las 32 ventanas, también en la de 946: k6 siguió ofreciendo toda la carga, así que la caída es de Qolqe | ventanas, columna `descartadas` · lámina 7, fila U-05 |
| Colapso | entre 876 y 946 simultáneos. **Digo el de la matriz de la lámina 7: consultas de 73 ms a más de 13 s** (13 296) y el error de 0 a 13,7 %. El p95 de todas las peticiones, 78 ms → 13,4 s, es el de la nota «informe:» bajo el gráfico de la lámina y el del informe: lo digo si cruza con el Informe pág. 41 | estrés/veredicto.md:31 · ventanas, minutos 11.750 (77,6) y 12.250 (13 374) · estrés/tabla_estres.md:15 · `docs/informe.md:226` · Informe pág. 41 |
| CPU de Qolqe en el colapso | 75,5 % en la ventana de 876 y 60,0 % en la de 946: baja cuando cae, no se satura | Informe, Tabla 5 (pág. 22) · ventanas, columna `cpu_qolqe` |
| Máximo del estrés | 1 144 simultáneos; k6 cortó a los 947,7 s, cuando quedaban 889 VUs | `docs/informe.md:211` · Informe págs. 16-17 |
| Dinero en el colapso | 0 descuadres; 98 operaciones de dinero sin respuesta, que concilian en C6; 2 transferencias aplicadas cuyo cliente recibió un timeout (sin clave de idempotencia) | estrés/veredicto.md:44-45 · Informe págs. 22 y 41 |
| Si preguntan por el 99 o el 20,81 % | k6 salió con 99 y U-03 da 20,81 % en toda la rampa, colapso incluido. El estrés no se juzga con U-03 de toda la corrida: se juzga por ventanas, con U-08 | estrés/veredicto.md:5, :43 |
| Pico sostenido | ~300 simultáneos durante ≈ 3 min (12:02-12:05, S-07). Si el triple durara los 15 min, la evidencia más cercana es el estrés: 6 min seguidos sobre 300, con p95 de consultas ≤ 76 ms y 0 % de error | Informe págs. 13 y 38 · `docs/informe.md:224` |
| U-06 | 2 × el umbral normal, 1 600 / 3 000 ms: supuesto propio S-05, no lo dice el requerimiento | Informe pág. 12 |
| Cuello de botella | 733 de 829 excepciones son `database is locked` en `autenticacion.py:136`; py-spy da a `verificar_pin` el 53-63 % de las muestras con 1 CPU. El ≈ 65 % del CPU de una sesión es la estimación del diseño, antes de medir | `docs/informe.md:239`, `:242` · `docs/diseno-rendimiento.md:27`; recontado en estrés/qolqe.log.gz |
| Memoria (resistencia) | 92 MB a 54 000 sesiones (límite 700) | `tests/performance/resultados/resistencia/20261111-1958/veredicto.md:68` |
| Línea base relativa | Qolqe en 1 CPU y 1 GB dentro de una laptop: sirve para comparar versiones, no se extrapola a producción | Informe §6 (pág. 17) |
| Qué hacer | commit justo después del INSERT de la sesión y fallar rápido con 503; escalar CPU ayuda, pero da × 1,53; el SLA no necesita renegociarse | Informe §8, «Acciones recomendadas» (pág. 41) · `docs/informe.md:245` |

## 3. Casos, ejecuciones y defectos

| Dato | Digo | Fuente |
|---------|-------------------------|----------------|
| Requisitos | 19 historias, 51 criterios: 33 del núcleo y 18 de G4 | `docs/alcance-y-casos.md:3` |
| Casos | **335**: 198 API funcionales, 78 API técnicos, 58 web y el contrato CP-T04 | `docs/informe.md:32`, `:41-46` |
| Resultado por caso | 295 pasan y 40 en fallo esperado, por 25 defectos; 0 fallan, 0 inestables, 0 sin ejecutar | `docs/trazabilidad.md:5-17` (run #24, intento 1; el `run.json` del intento 2 da lo mismo) · `docs/informe.md:305` |
| API por caso (lámina 11) | 276 casos: **237 pasan y 39 en fallo esperado estricto**; 0 fallan, 0 omitidos, 0 sin ejecutar | `docs/trazabilidad.md:11-16` (88 + 41 + 89 + 19 y 13 + 12 + 8 + 6) |
| Web (lámina 12) | 58: 27 del núcleo y 31 de G4. En la Entrega 2 eran 19 (9 de contactos y 10 de solicitudes) | `docs/trazabilidad.md:13`, `:16` · `git show refs/tags/parte-2:features/web/` (los dos `.feature`) |
| Ejecuciones | **766 de API y 213 web**. Si digo 707 (las de API que pasan), parece que faltan 59. 213 son 71 pruebas × 3 | `docs/informe.md:98` · `docs/alcance-y-casos.md:33-34` |
| Contrato | 19 operaciones; los casos generados cambian entre corridas (1 291 a 1 414): no los digo | `docs/informe.md:99`, `:104` |
| Concurrencia | 10 escenarios, automatizados solo con 200 de 200 corridas locales. **Por escenario es lo que más defectos encontró: 7 DEF distintos en 10 escenarios** (DEF-11, 14, 15, 21, 22, 25 y 26), 3 de ellos críticos (11, 21 y 25). En número absoluto no: los escenarios funcionales de API llevan 13 DEF distintos y los técnicos sin concurrencia, 6. Por eso digo «por escenario» (el recuadro ámbar de la lámina 11, «Concurrencia · 10 escenarios → 7 DEF», hay que leerlo así) | `docs/defectos.md:6` · etiquetas `@concurrencia` y `@DEF-xx` de `features/*.feature`, contadas el 18-nov |
| Sin automatizar | 3: CP-NA28, CP-NA69 y CP-T19. CP-T19 falla en 118 y 136 de 200 rondas (cancelar y rechazar): es DEF-30 | `docs/informe.md:346` |
| Deuda del código de prueba de la API | Dos de los tres costos declarados se pagaron el 18-nov: los 45 pasos de G4 pasaron de `conftest.py` a `pasos_g4.py` y los usuarios de la semilla quedaron en un solo lugar de la suite. Sin cambiar ninguna prueba: antes y después, las mismas 766 con los mismos IDs, 707 passed y 59 xfailed. Lo que queda es una decisión, no una deuda: la ayuda de concurrencia sigue en tres módulos, porque unificarla obliga a volver a medir los 10 escenarios con 200 de 200 | `docs/informe.md:347-350` · `tests/api/conftest.py:9-17` y `:112-115` |
| Defectos | **30**: 8 críticos, 5 altos, 9 medios, 8 bajos. Detectados: 24 por API, 1 web, 2 solo por contrato, 1 en el pipeline, 2 manuales (DEF-16 y DEF-30) | `docs/informe.md:251`, `:258-263` |
| Críticos de concurrencia | **4 de 8**: DEF-11, DEF-21 y DEF-25, automatizados con `@concurrencia`, y DEF-30, evidencia manual (CP-T19) | `@concurrencia` en `features/` · `docs/defectos.md:10-17` · `docs/resultados-manuales/cp-t19.md` |

## 4. Pipeline, reportería y trazabilidad

| Dato | Digo | Fuente |
|---------|-------------------------|----------------|
| Jobs | **8**: estatico → contrato → api → web, quality-gate, y reportes → gestion-casos → publicar | `.github/workflows/pruebas.yml:39` a `:396` · `docs/pipeline.md:17-26` |
| Checks obligatorios de `main` | **`api`, `web` y `quality-gate`** (el último se sumó el 18-nov): los tres de la app de GitHub Actions y aplicados a todos (`enforcement_level: everyone`; `enforce_admins` activo). Lo dicen igual los candados de la lámina 15 (en api, web y quality-gate, y «3 obligatorios · también el dueño» bajo main), `docs/pipeline.md:32` y `docs/informe.md:164`; en la lámina 14, quality-gate lleva debajo «veredicto único». Si el sábado el comando da otra cosa, digo lo que dio | `gh api repos/Joharjbe/qolqe-wallet/branches/main -q .protection.required_status_checks` → `contexts: ["api","web","quality-gate"]`, `enforcement_level: everyone` (18-nov) · `hoja-demo.md`, fila 1b |
| PR #10 | Run #25: `estatico` y `contrato` en verde; `api`, `web` y `quality-gate`, los tres obligatorios, en rojo; la fusión queda bloqueada | `gh pr view 10 -R Joharjbe/qolqe-wallet` (18-nov: `BLOCKED`) · `docs/pipeline.md:34` · `docs/img/demo-gate-rojo.png` |
| Tiempos de la lámina 14 | estatico 53 s, contrato 35 s, api 6 min 53 s y web 4 min 7 s; el run completo, 13 min 38 s (este va en la nota de orador). Son del run #24, intento 1: contrato de 02:43:38 a 02:44:13 UTC y el run de 02:42:40 a 02:56:18 UTC | `gh api repos/Joharjbe/qolqe-wallet/actions/runs/44225240314/attempts/1/jobs` |
| Costo de poner el contrato delante | 41 s en el run #20, cuando iba en paralelo (07:52:32 a 07:53:13 UTC), de un run de 9 min 44 s | `docs/pipeline.md:11` · API de GitHub, job `contrato` del run 43178430994 |
| Con el pipeline actual | El contrato, 35 a 54 s; el run, 10 min 7 s a 15 min 58 s (#21 a #24, los dos intentos; #21 a #23 son de PR, sin gestion-casos ni publicar) | API de GitHub: inicio y fin de cada job y `timing` del run |
| Variación del runner | Misma suite de API, mismo commit `1025a78`: 386 s en el intento 1 del #24 y 245 s en el intento 2. La duración del run no sirve para esto: el pipeline cambió | log del job `api`: «707 passed, 59 xfailed in …» |
| Runs en verde | Al 18-nov, del #16 al #24, 9 de 9. Las cifras son del #24, intento 1 (id 44225240314, commit `1025a78`, 8 jobs en verde); el intento 2 (17-nov, 22:41 de Lima) también salió en verde. El #25 es el PR #10, en rojo a propósito | `gh run list -R Joharjbe/qolqe-wallet --workflow pruebas.yml` · `docs/trazabilidad.md:5` |
| Historial en Pages | `historial.json` guarda hasta 30 runs (`--historial-max 30`) y `historial.html` dibuja los últimos 15 (`columnas=15`). Al 18-nov, con el run #28, había 7 entradas: #17, #18, #20, #24.1, #24.2, #27 y #28. Volver a contarlas el sábado: cada run nuevo de `main`, como el del commit final, suma una | https://joharjbe.github.io/qolqe-wallet/historial.json (`maximo` 30, 7 runs, leído el 18-nov después del run #28) · `.github/scripts/trazabilidad.py:471`, `:474`, `:524` · `docs/pipeline.md:81` |
| Evidencia completa | Run #18 (`con-imagenes`): el artefacto `sitio` pesa casi 200 MB; el run deja ~416 MB entre todos. `sitio` vencía el 18-nov a las 17:28 de Lima (7 días de retención): el sábado ya no está y queda la copia offline, y las capturas por caso siguen en el artefacto `trazabilidad` hasta el 09-feb-2027 | `gh api repos/Joharjbe/qolqe-wallet/actions/runs/43109117336/artifacts` (`expires_at` de `sitio`: 2026-11-18T22:28:26Z; de `trazabilidad`: 2027-02-09) · `.github/workflows/pruebas.yml:35` · `~/Desktop/respaldo-sitio-con-imagenes` |
| Kiwi, en simulación | run #18: 335 ejecuciones (295 PASSED, 40 WAIVED), 40 enlaces de defecto, 219 capturas | `docs/informe.md:340`; se reproduce con `scripts/kiwi_sincronizar.py --simular --run 18` |
| Kiwi, real | 10 TestRuns (17-nov). El del run #18 (TR-7): 335 casos, 295 PASSED, 40 WAIVED, 40 enlaces de defecto hacia 25 DEF y **216** capturas (Kiwi rechazó 3 por un falso positivo de su filtro) | `docs/gestion-casos.md` («Primera importación real») · `docs/img/kiwi-testrun-18.png` |

Entrega: **pendiente.** El tag y la Release `entrega-final-v1` se crean el viernes 20 sobre el commit final de `main`; al 18-nov, `git ls-remote --tags entrega` solo daba `parte-2` y `parte-3`. Se verifica con ese mismo comando. Sitio: https://joharjbe.github.io/qolqe-wallet/.

## 5. Capacidad de IA

Fuente de verdad: `docs/capacidad-ia.md` y `docs/resultados-capacidad-ia/`. Modelo `gemini-3.1-flash-lite`, corrida del 17-nov-2026 (`docs/capacidad-ia.md:14`). En palabras de la clase 15, el conjunto de oro es un *eval* y las guardas son *guardrails*. Las reglas sin IA son el «control sin IA» (en los archivos, `evals-lineabase.md`): no digo «línea base», que en el curso es la de rendimiento. Si digo «matriz», es la tabla del eval: lo esperado contra lo propuesto.

| Dato | Digo | Fuente |
|---------|-------------------------|----------------|
| Conjunto de oro (el eval) | 52: 40 defecto real, 4 prueba inestable (3 documentadas, 1 sembrada), 8 error de entorno (sembrados) | `docs/capacidad-ia.md:329-334` |
| Clasificados | 48 de 52 (a 4 los paró una guarda); confianza alta 35, media 13, baja 0 | evals:8, :11, :62-64 |
| Por clase, mismos 48 | Defecto real: modelo 28 de 36, reglas 34 de 36. Inestable: 4 de 4 los dos. Entorno: modelo 8 de 8, reglas 7 de 8. No comparo 38 de 40 con 28 de 36: no son los mismos casos | evals:76-78, :70 |
| `DEF-xx` | 0 de 38: no propuso ninguno | evals:53-55 |
| Lo que ahorra | 40 fallos en 32 grupos, 20 % menos de lectura; con los artefactos crudos del run #20, 62 en 29. No medí minutos | `docs/capacidad-ia.md:73-74` |
| Privacidad | 2 respuestas paradas por copiar un celular (ORO-09 y ORO-11) | evals:47-48 |
| Inyección (LIM-IA-01) | limpio 0 de 5, inyectado 5 de 5 (4 pasaron las guardas), agresivo 0 de 5. `DEF-99` dictado: 1 de 5, rechazado siempre por las guardas | iny:73, :144, :146, :215, :145 · `docs/capacidad-ia.md:626-632` |
| No determinismo | **0 de 4 casos** cambiaron de clase en 5 corridas; CP-NA03 contestado 1 de 5. Si pregunta: son los 4 casos del run medido, no los 52 del eval (la nota de orador de la lámina 19 ya lo dice con el 4: «ninguno de sus 4 casos») | `docs/resultados-capacidad-ia/no-determinismo-google.json:3-4`, `:6`, `:11` |

No digo un porcentaje global: el conjunto está desbalanceado y lo decidiría la clase mayoritaria (`docs/capacidad-ia.md:368-371`).

## 6. Decisiones discutibles, en una línea

- **Qolqe en Docker con 1 CPU y 1 GB.** Sin cuota, k6 compite con la app y los números no se comparan entre corridas (banco, pregunta 7).
- **El rendimiento fuera del pipeline.** Va en la etapa no funcional, por release, y un runner compartido daría rojos falsos con umbrales de latencia (pregunta 13).
- **El contrato delante de api, con guardas.** Sin guarda, un contrato en rojo dejaría api «omitido», y GitHub lo cuenta como verde (preguntas 21 y 22).
- **Fallo esperado estricto y la regla de 200 de 200.** El pipeline queda verde sin esconder defectos; una carrera que no se reproduce siempre no se automatiza (preguntas 17 y 24).
- **La web tres veces seguidas.** Una prueba que pasa dos de tres es una prueba frágil (*flaky*, clase 11), no aprobada (pregunta 18).
- **La IA fuera del gate y la agrupación en código.** Lo que decide tiene que dar lo mismo en cada corrida (preguntas 27 y 33).
