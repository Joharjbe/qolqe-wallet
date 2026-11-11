# Declaración de uso de IA

| Fecha | Herramienta | Tarea | Qué aceptamos | Qué corregimos o descartamos y por qué |
|---|---|---|---|---|
| 2026-10-24 | Codex | Ayuda en el diseño de la prueba G4 con Robot Framework, los Page Objects, el README y la presentación del laboratorio S11 | Estructura de la suite y propuesta de validaciones contrastadas con `docs/requisitos.md`, la interfaz real y la ejecución en Chromium | La primera ejecución leía «Pendiente» antes de que terminara la actualización; se reemplazó esa lectura inmediata por una espera del estado visible. La prueba se volvió a ejecutar y pasó. No se cambió `qolqe/`. |
| 2026-10-30 | Claude Code | Generación de las suites de API (pytest-bdd, Schemathesis) y web (Playwright, playwright-bdd), el pipeline, los scripts de reportes, la documentación y las presentaciones de las entregas 1 y 2 | Casos derivados de `docs/requisitos.md` y de las clases 10, 11 y 12; cada defecto se reprodujo contra la app antes de reportarlo | Se descartó ST302 de Schemathesis como falso positivo (HU-G4-08 CA4 exige ese 404). Se reemplazó pytest 9 por 8.4 por incompatibilidad con pytest-bdd. Se cambió Robot Framework por Playwright para la Parte 2. Se corrigieron dos errores detectados al revisar el pipeline: la ruta de los artefactos y la versión de FastAPI (DEF-07). No se cambió `qolqe/`. |
| 2026-11-11 | Claude Code (varios agentes en paralelo) | Entrega final: análisis de la retroalimentación y de las clases 10 a 12, diseño e implementación de los casos del núcleo (HU-N-01 a 09) y de los que faltaban en G4 (API funcional y técnica, y web), mejora del Page Object, nuevo pipeline con evidencia a elección, trazabilidad acumulada, integración con Kiwi TCMS, integración de ramas y documentación | 335 casos derivados de `docs/requisitos.md` con su técnica. Del DEF-09 al DEF-29, cada defecto se reprodujo contra la app con un script aparte antes de documentarlo. Después de una revisión adversarial con tres revisores, los resultados se verificaron con 3 corridas de API idénticas (707 passed, 59 xfailed), la web 3 veces seguidas sin pruebas inestables y los 10 casos de concurrencia en 200 de 200 corridas | Detalle en la sección siguiente. No se cambió `qolqe/`: `git diff 1b3b60e..HEAD -- qolqe/` sale vacío. |

## Entrega final: qué hizo la IA y qué se corrigió

**Qué hizo.** Claude Code trabajó con agentes en paralelo, cada uno con su propia instancia de Qolqe y su propia base de datos.

| Etapa | Resultado |
|---|---|
| Análisis | Comparación de patrones de diseño, herramientas complementarias, estructura del pipeline e investigación de herramientas de gestión de casos (Kiwi TCMS, Qase, TestRail, Xray, Zephyr, Testmo, TestLink), con fuentes |
| Diseño de casos | Casos del núcleo por criterio y casos faltantes de G4, con técnica ISTQB y nivel (API o web) según la regla de la clase 11 |
| Implementación | Pasos de pytest-bdd por área, escenarios web del núcleo y de G4, componentes de Page Object, plugin de evidencia de la API |
| Pipeline | 8 jobs, entrada `evidencia`, quality gate, matriz por run, `junit-cp.xml`, historial en Pages y sincronización con Kiwi |
| Integración | Unión de las ramas, renumeración de IDs y de defectos, verificación estática y 3 corridas completas |
| Documentación | Informe, alcance y casos, arquitectura, pipeline, gestión de casos, defectos, README y respuesta a la retroalimentación |

**Qué se corrigió o descartó.**
- **Casos que no se automatizaron**, porque no dan el mismo resultado en todas las corridas. Quedaron como evidencia manual:
  - CP-NA28 (DEF-16, tiempo de respuesta): depende del equipo.
  - CP-NA69 (DEF-15 en la edición simultánea): 1 de cada 25 corridas se serializa.
  - CP-T19 (aceptar frente a cancelar a la vez).
- **IDs corregidos por el integrador.**
  - CP-NA18b pasó a CP-NA75 (sin sufijo de letra).
  - Los defectos provisionales `DEF-NEW-…` se numeraron DEF-25 a DEF-29.
  - Se corrigieron los pares `@HU` `@CA` de CP-T08, CP-T18 y CP-W10.
  - Se agregó `@CA1` a CP-T01, CP-T02 y CP-T03. Después, en la revisión final, CP-T01 y T03 se retiraron por duplicar filas de CP-T05.
- **Schemathesis.** Dos hallazgos se clasificaron como falsos positivos: 423 en el ingreso de una cuenta bloqueada y `correo: ""`, que el contrato permite. Otro se confirmó como defecto (DEF-29). Cada exclusión quedó con su motivo en `schemathesis.toml` y `scripts/contrato_hooks.py`.
- **Prueba web corregida.** CP-NW18 falló la primera vez por un error de la prueba: cambiaba de navegador antes de que terminara el cierre de la cuenta. Se agregó la espera del aviso y pasó 5 de 5.
- **Patrón web.**
  - Se eliminó `ComunPage`, que mezclaba responsabilidades.
  - Se quitó un localizador por posición (`.last()`).
  - No se usó Screenplay: agrega más clases que escenarios en esta suite.
  - Tampoco Page Factory: Playwright ya resuelve los localizadores en cada uso.
  - Ni los decoradores de playwright-bdd: atan el texto del Gherkin a una clase.
- **Justificación de Playwright.** El informe anterior decía que se eligió sobre Robot Framework por la espera automática. Es incorrecto: la librería Browser de Robot también corre sobre Playwright. Se reemplazó por las diferencias reales (`docs/informe.md`, sección 3).
- **Kiwi TCMS.** El RPC simulado no validaba los formularios de Kiwi y ocultó dos fallas que la revisión encontró en un Kiwi 17 real: el build se creaba en una versión distinta a la del plan (Kiwi rechaza el TestRun) y el reporte HTML de API como adjunto (Kiwi rechaza archivos con `<html>`). Se corrigieron y la importación real se probó en contenedores desechables; falta la del alumno.
- **Revisión final (tres revisores adversariales, 11-nov-2026).** Lo que se corrigió:
  - CP-T20 daba XPASS cerca de 2 de cada 100 corridas: ahora repite la ráfaga hasta 5 veces, y la regla de concurrencia pasó de 20 a 200 corridas.
  - El xfail aceptaba cualquier excepción como el defecto: ahora solo una `AssertionError`; en la web, una precondición que no se cumple es un fallo real.
  - Oráculos que no probaban lo que decía el título: CP-NA55 (404 de una ruta inexistente), NA53 (fecha del saldo), NW08 (dispositivo enviado), CP-W12 (pestaña sin recargar), NW04, A11, NA86 y NA115 (columnas sin usar).
  - Códigos de error en los esquemas del registro, casos duplicados retirados (CP-A38, T01, T03) y etiquetas HU/CA que no correspondían (NA45, NA48, T28).
  - Pipeline y trazabilidad: reintentos en el historial, inestable frente a regresión, módulo del contrato, corridas locales con id propio, veredicto en la portada, token enmascarado en la evidencia y semilla del contrato.
  - DEF-18 y DEF-27 pasaron a defectos de usabilidad con su base explícita; el oráculo de DEF-18 ya no exige una frase exacta. Se agregaron OBS-01 y OBS-02.

## Lo que el alumno debe revisar antes de entregar

1. Leer `docs/informe.md`, `docs/arquitectura.md` y `docs/respuesta-feedback.md`, y confirmar que puede sustentar cada decisión: niveles, patrón, herramientas y jobs.
2. Revisar una muestra de escenarios contra `docs/requisitos.md`.
   - En especial las técnicas que asignó el integrador leyendo el título y los pasos, porque los informes de los escritores llegaron incompletos.
   - Son CP-NA26 en adelante (salvo NA80 a NA103), parte de CP-A55 a A99 y de CP-T05 a T30, y CP-W20 a W31.
3. Reproducir a mano los defectos críticos (DEF-03, 04, 09, 11, 19, 21 y 25) con los pasos de `docs/defectos.md`.
4. Publicar la rama `entrega-final` y abrir el PR. Verificar en GitHub:
   - que el workflow nuevo pasa;
   - un run con `evidencia=con-imagenes`;
   - la portada y `historial.html` en Pages.
5. Crear su usuario en Kiwi (`initial_setup`) y hacer la primera sincronización real (`docs/gestion-casos.md`).
6. Versionar `docs/trazabilidad.md` desde el artefacto `trazabilidad` de un run verde de `main` (`gh run download <id> -R Joharjbe/qolqe-wallet -n trazabilidad`), no con `npm run trazabilidad`, que deja "Run #local".
