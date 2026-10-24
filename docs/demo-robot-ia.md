# Demo en vivo: IA aplicada a Robot Framework

Robot Framework no necesita IA para ejecutar pruebas. Aquí la IA actúa como **asistente para revisar resultados y proponer mejoras**; el oráculo y la decisión final siguen en el test y en los requisitos de Qolqe.

## Antes de presentar

1. Inicia Qolqe y ejecuta la prueba con los comandos de la sección 7 del README. Comprueba que `reportes/report.html` muestre `1 test, 1 passed`.
2. Abre en Codex este repositorio y ten visibles `docs/requisitos.md`, `tests/e2e/g4_solicitud_happy_path.robot` y `reportes/output.xml`.

## Prompt para mostrar en vivo en Codex

> Revisa el resultado real de `reportes/output.xml` y la prueba `tests/e2e/g4_solicitud_happy_path.robot` contra HU-G4-06 y HU-G4-08 de `docs/requisitos.md`. Dime qué validación importante falta en este único happy path. Propón un cambio mínimo a Robot Framework, con el criterio de aceptación exacto que cubre. No modifiques el código de `qolqe/` ni afirmes que la prueba cubre escenarios negativos. Distingue claramente lo que el reporte ya comprobó de lo que solo estás proponiendo.

La respuesta útil debe detectar que el caso comprueba estado, operación y saldos, pero **no valida el SMS simulado** que HU-G4-06 CA2 envía al destinatario ni el que HU-G4-08 CA3 envía al solicitante. Una propuesta aceptable es consultar `/api/pruebas/notificaciones` en un keyword de soporte y buscar el motivo y el código de operación. Revisar el cambio antes de incorporarlo; un texto generado por IA no equivale a una prueba ejecutada.
