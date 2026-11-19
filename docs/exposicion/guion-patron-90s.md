# Recorrido del patrón en 90 segundos

Es el paso D2 de la demo ([`guion.md`](guion.md)) y lo que [`respuesta-feedback.md`](../respuesta-feedback.md) promete para el punto 4: ir de un paso de Gherkin al Page Object y al componente `DialogoConfirmacion`, en el código y no de memoria. La lámina 13 (`patron`) ya dijo el porqué; aquí se ve. En la exposición de 15 minutos va la [versión de 40 s](#versión-de-40-s-la-de-la-exposición-de-15-minutos); la de 90 s es para las preguntas o para cuando vas adelantado.

`scripts/preparar-demo.sh` deja los cuatro archivos abiertos en VS Code, cada uno en la línea del salto. Para pasar de uno a otro: `Ctrl + Tab`. Si no están abiertos, desde la raíz del repositorio:

```bash
code features/web/solicitudes_web.feature tests/e2e/steps/solicitudes.steps.ts tests/e2e/pages/SolicitudesPage.ts tests/e2e/pages/componentes.ts
```

y en el `.feature`, `Cmd + F` con `acepta la solicitud "Devolución`.

## Los cuatro saltos y el remate

| Tiempo | Archivo y línea | Qué señalas | Di |
|---|---|---|---|
| 0:00–0:15 | `features/web/solicitudes_web.feature`, escenario CP-W10, paso `acepta la solicitud "Devolución demo G4"` | El paso, sin un solo localizador | «Este es CP-W10, el recorrido crítico de una solicitud entre dos usuarios. El paso dice qué hace el usuario, acepta la solicitud, y no sabe nada de la pantalla.» |
| 0:15–0:35 | `tests/e2e/steps/solicitudes.steps.ts:27` | Una línea: recibe la página `solicitudes` y llama a `solicitudes.aceptar(motivo)` | «La definición del paso es una sola línea: le pide la acción a la página. Si alguien pone aquí un localizador, el job estático del pipeline falla.» |
| 0:35–0:55 | `tests/e2e/pages/SolicitudesPage.ts:93-97` (`aceptar`), con `pulsarAceptar` justo arriba, en la 89-91 | `pulsarAceptar` es el único que pulsa `boton-aceptar-solicitud`; después vienen `confirmacion.esperarMensaje(motivo)` y `confirmacion.confirmar()` | «El Page Object es el único que conoce el botón de aceptar. El diálogo de confirmación no lo escribe él: lo usa.» |
| 0:55–1:15 | `tests/e2e/pages/componentes.ts:16-32` (`DialogoConfirmacion`) | `confirmar()` pulsa `boton-confirmar-accion` dentro de `dialogo-confirmar`. El editor abre en la línea 16: sube a la cabecera, `componentes.ts:3-4`, cuyo comentario dice que `app.js` genera ese diálogo igual en todas las pantallas (el de la línea 15 solo lo describe) | «Este es el diálogo de "¿Seguro?". La aplicación lo genera igual en todas las pantallas, así que se escribe una sola vez, como componente.» |
| 1:15–1:30 | `Cmd + P` → `ContactosPage.ts`, `Ctrl + G` → `87` (`eliminar`, líneas 87-90) | `eliminar` termina con el mismo `this.confirmacion.confirmar()` | «Eliminar un contacto usa el mismo componente, igual que cancelar una solicitud. Si mañana cambia el diálogo, se arregla en `componentes.ts` y no en cada página que confirma algo. Eso es lo que escala.» |

## Versión de 40 s (la de la exposición de 15 minutos)

Tres de los cinco saltos: el `.feature`, la página y otra página que usa el mismo componente. `DialogoConfirmacion` se ve dentro de `aceptar`, sin abrir `componentes.ts`. Con `Ctrl + Tab` se pasa del `.feature` a `SolicitudesPage.ts` sin detenerse en el archivo de pasos.

| Tiempo | Archivo y línea | Di |
|---|---|---|
| 0:00–0:10 | `features/web/solicitudes_web.feature`, CP-W10, paso `acepta la solicitud "Devolución demo G4"` | «El paso dice qué hace el usuario, acepta la solicitud, y no sabe nada de la pantalla.» |
| 0:10–0:25 | `tests/e2e/pages/SolicitudesPage.ts:89-97` (`pulsarAceptar` y `aceptar`) | «La página es la única que conoce el botón de aceptar. El diálogo de confirmación no lo escribe ella: lo usa, con `confirmacion.confirmar()`.» |
| 0:25–0:40 | `Cmd + P` → `ContactosPage.ts`, `Ctrl + G` → `87` (`eliminar`, líneas 87-90) | «Eliminar un contacto usa el mismo componente. Si mañana cambia el diálogo, se arregla en `componentes.ts` y no en cada página: eso es lo que escala.» |

## Si pregunta

| Pregunta | Dónde se ve |
|---|---|
| ¿Qué otros usan el mismo diálogo? | 9 de los 58 escenarios web (CP-W07, W08, W10, W16, W17, W19, W20, W21 y W23). En el código: `SolicitudesPage.cancelar` (`SolicitudesPage.ts:105-108`) y dos pasos comunes que reciben el componente directo: `cancela la confirmación` y `la confirmación dice {string}` (`tests/e2e/steps/comunes.steps.ts:37` y `:42`) |
| ¿Cómo sabes que ningún paso tiene localizadores? | `.github/workflows/pruebas.yml:84-89`: el job `estatico` hace `grep` de `getBy`, `locator(` y `page.` sobre `tests/e2e/steps` y falla si encuentra uno |
| ¿De dónde sale la página que recibe el paso? | `tests/e2e/fixtures.ts:174`: el fixture `solicitudes` crea un `SolicitudesPage` por prueba |
| ¿Y por qué no Screenplay? | Lámina 13, la columna «Screenplay» («solo si >100»), y su nota de orador: está pensado para suites grandes; con 58 escenarios sumaría actores, tareas y preguntas sin un problema que lo pida, y lo usaría con más de unos 100 escenarios, varios equipos o recorridos de varios actores (`docs/arquitectura.md` §3.3 y §3.7) |
