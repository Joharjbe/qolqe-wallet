# Demo en vivo: IA aplicada a Robot Framework

Robot Framework no necesita IA para ejecutar pruebas. Aquí la IA actúa como **asistente para revisar resultados y proponer mejoras**; el oráculo y la decisión final siguen en el test y en los requisitos de Qolqe.

La guía PDF de esta carpeta (`Guion_exposicion_Robot_Qolqe_10_min.pdf`) usa las rutas de antes de que el laboratorio pasara a `labs/s11-robot/` (commit `a4b1034`): `tests/e2e/g4_solicitud_happy_path.robot` y `docs/demo-robot-ia.md`. Las vigentes son las de esta hoja.

## Antes de presentar

1. Desde la raíz del repositorio, inicia Qolqe en modo de pruebas (terminal 1) y ejecuta la prueba (terminal 2). La prueba reinicia los datos de esa instancia local con `/api/pruebas/reiniciar`. Comprueba que `reportes/report.html` muestre `1 test, 1 passed`. La carpeta `reportes/` la crea la ejecución y está en `.gitignore`.

   ```bash
   QOLQE_BD=.demo-data/qolqe.db QOLQE_MODO_PRUEBA=1 .venv/bin/python -m uvicorn qolqe.main:app --host 127.0.0.1 --port 8000
   .venv/bin/python -m robot --variable HEADLESS:False --variable SLOWMO:0.5s --outputdir reportes labs/s11-robot/g4_solicitud_happy_path.robot
   ```

   `.venv` ya tiene robotframework 7.5 y robotframework-browser 20.6.0, las versiones de `labs/s11-robot/requirements-robot.txt`. En un entorno nuevo no uses `pip install -r` con ese archivo: su línea `-r requirements.txt` se busca dentro de `labs/s11-robot/` y pip falla. Instala así (necesita red):

   ```bash
   .venv/bin/python -m pip install -r requirements.txt robotframework==7.5 "robotframework-browser[bb]==20.6.0"
   .venv/bin/rfbrowser install chromium
   ```

2. Abre en Codex este repositorio y ten visibles `docs/requisitos.md`, `labs/s11-robot/g4_solicitud_happy_path.robot` y `reportes/output.xml`.

## Prompt para mostrar en vivo en Codex

> Revisa el resultado real de `reportes/output.xml` y la prueba `labs/s11-robot/g4_solicitud_happy_path.robot` contra HU-G4-06 y HU-G4-08 de `docs/requisitos.md`. Dime qué validación importante falta en este único happy path. Propón un cambio mínimo a Robot Framework, con el criterio de aceptación exacto que cubre. No modifiques el código de `qolqe/` ni afirmes que la prueba cubre escenarios negativos. Distingue claramente lo que el reporte ya comprobó de lo que solo estás proponiendo.

La respuesta útil debe detectar que el caso comprueba estado, operación y saldos, pero **no valida el SMS simulado** que HU-G4-06 CA2 envía al destinatario ni el que HU-G4-08 CA3 envía al solicitante. Una propuesta aceptable es consultar `/api/pruebas/notificaciones` en un keyword de soporte y buscar el motivo y el código de operación. Revisar el cambio antes de incorporarlo; un texto generado por IA no equivale a una prueba ejecutada.
