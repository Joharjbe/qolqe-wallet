# Matriz de trazabilidad · G4

Generada por `.github/scripts/trazabilidad.py` a partir de las etiquetas de `features/` y los JUnit XML del pipeline.

Run **#10** · commit `c7d3d14` · 2026-10-30 15:29 (hora de Lima) · [ver run](https://github.com/Joharjbe/qolqe-wallet/actions/runs/41123298780)

## Cobertura por historia

| HU | Historia | Casos API | Casos web |
|---|---|---|---|
| HU-G4-01 | Agregar un contacto | 7 | 3 |
| HU-G4-02 | Ver y buscar mis contactos | 4 | 3 |
| HU-G4-03 | Editar un contacto | 4 | 1 |
| HU-G4-04 | Eliminar un contacto | 4 | 2 |
| HU-G4-05 | Transferir a un contacto | 2 | 1 |
| HU-G4-06 | Solicitar dinero a un contacto | 5 | 4 |
| HU-G4-07 | Ver mis solicitudes | 4 | 3 |
| HU-G4-08 | Aceptar una solicitud recibida | 6 | 4 |
| HU-G4-09 | Rechazar una solicitud recibida | 3 | 1 |
| HU-G4-10 | Cancelar una solicitud enviada | 3 | 1 |

## HU → caso → resultado

| HU | CA | Caso | Título | Nivel | Resultado (run #10) |
|---|---|---|---|---|---|
| HU-G4-01 | CA1 | CP-A01 | Agregar un contacto válido normaliza el alias | api | passed (1/1) |
| HU-G4-01 | CA1 | CP-A02 | Rechazar un celular que no puede ser contacto | api | passed (6/6) |
| HU-G4-01 | CA1 | CP-A03 | Valores límite y clases del alias | api | passed (6/6) |
| HU-G4-01 | CA1 | CP-A04 | El alias admite la letra ñ | api | xfailed → DEF-01 |
| HU-G4-01 | CA1 | CP-A05 | El alias es único sin distinguir mayúsculas | api | passed (1/1) |
| HU-G4-01 | CA1 | CP-A06 | El alias duplicado se detecta tras quitar los espacios | api | xfailed → DEF-02 |
| HU-G4-01 | CA1 | CP-A07 | Límite de 15 contactos | api | passed (1/1) |
| HU-G4-01 | CA1 | CP-W01 | Agregar un contacto desde la pantalla | web | passed (3/3) |
| HU-G4-01 | CA1 | CP-W02 | El error de la API se muestra al usuario | web | passed (3/3) |
| HU-G4-01, HU-G4-06, HU-G4-07, HU-G4-08 | CA1, CA3 | CP-W10 | Recorrido completo de una solicitud entre dos usuarios | web | passed (3/3) |
| HU-G4-02 | CA1 | CP-A08 | Favoritos primero, por alias y 10 por página | api | passed (1/1) |
| HU-G4-02 | CA2 | CP-A09 | Buscar sin distinguir mayúsculas ni tildes | api | passed (4/4) |
| HU-G4-02 | CA3 | CP-A10 | Cada contacto informa alias, nombre enmascarado, celular y favorito | api | passed (1/1) |
| HU-G4-02 | técnico | CP-T01 | Sin token no se accede a los contactos | api | passed (1/1) |
| HU-G4-02 | CA1 | CP-W03 | Favoritos primero, 10 por página y total visible | web | passed (3/3) |
| HU-G4-02 | CA2 | CP-W04 | Buscar sin tildes ni mayúsculas | web | passed (3/3) |
| HU-G4-02 | CA3 | CP-W05 | Cada contacto muestra alias, nombre enmascarado, celular y favorito | web | passed (3/3) |
| HU-G4-03 | CA1 | CP-A11 | Editar alias y favorito, sin compararlo consigo mismo | api | passed (1/1) |
| HU-G4-03 | CA1 | CP-A12 | Límite de 5 favoritos | api | passed (1/1) |
| HU-G4-03 | CA1 | CP-A13 | Editar con el alias de otro contacto | api | passed (1/1) |
| HU-G4-03, HU-G4-04 | técnico | CP-T02 | El contacto de otro usuario responde como inexistente | api | passed (2/2) |
| HU-G4-03 | CA1 | CP-W06 | Editar el alias y marcar como favorito | web | passed (3/3) |
| HU-G4-04 | CA1 | CP-A14 | Eliminar un contacto conserva las transferencias | api | passed (1/1) |
| HU-G4-04 | CA2 | CP-A15 | No se elimina un contacto con solicitudes pendientes | api | passed (1/1) |
| HU-G4-04 | CA2 | CP-A16 | Una solicitud vencida no impide eliminar el contacto | api | passed (1/1) |
| HU-G4-04 | CA1 | CP-W07 | Eliminar un contacto pide confirmación | web | passed (3/3) |
| HU-G4-04 | CA2 | CP-W08 | No se elimina un contacto con solicitudes pendientes | web | passed (3/3) |
| HU-G4-05 | CA1 | CP-A17 | Transferir eligiendo un contacto | api | passed (1/1) |
| HU-G4-05 | CA1 | CP-A18 | Transferir a un contacto con cuenta cerrada | api | xfailed → DEF-04 |
| HU-G4-05 | CA1 | CP-W09 | Transferir eligiendo un contacto | web | passed (3/3) |
| HU-G4-06 | CA2 | CP-A20 | Crear una solicitud pendiente que vence a las 48 horas y avisa por SMS | api | passed (1/1) |
| HU-G4-06 | CA1 | CP-A21 | Valores límite del monto | api | passed (6/6) |
| HU-G4-06 | CA1 | CP-A22 | Valores límite del motivo | api | passed (4/4) |
| HU-G4-06 | CA1 | CP-A23 | Máximo 10 solicitudes pendientes enviadas | api | passed (1/1) |
| HU-G4-06 | CA1 | CP-A24 | No se solicita a un contacto con cuenta cerrada | api | passed (1/1) |
| HU-G4-06 | CA1 | CP-W11 | Solicitar desde la lista de contactos | web | passed (3/3) |
| HU-G4-06 | CA1 | CP-W12 | Una solicitud inválida muestra el error y no se crea | web | passed (3/3) |
| HU-G4-06 | CA2 | CP-W13 | La solicitud creada queda pendiente con su vencimiento | web | passed (3/3) |
| HU-G4-07 | CA1 | CP-A25 | Enviadas y recibidas por separado, con filtro por estado | api | passed (1/1) |
| HU-G4-07 | CA1 | CP-A26 | Un filtro de estado desconocido se rechaza | api | passed (1/1) |
| HU-G4-07 | CA2 | CP-A27 | Vencimiento a las 48 horas exactas | api | passed (2/2) |
| HU-G4-07 | técnico | CP-T03 | Sin token no se accede a las solicitudes | api | passed (1/1) |
| HU-G4-07 | CA1 | CP-W14 | Enviadas y recibidas por separado, con filtro por estado | web | passed (3/3) |
| HU-G4-07, HU-G4-08 | CA2, CA4 | CP-W15 | Una solicitud vencida se muestra como Vencida y sin acciones | web | passed (3/3) |
| HU-G4-08 | CA1, CA3 | CP-A28 | Aceptar transfiere el dinero y deja el código de operación | api | passed (1/1) |
| HU-G4-08 | CA2 | CP-A29 | Sin saldo la solicitud sigue pendiente | api | passed (1/1) |
| HU-G4-08 | CA2 | CP-A30 | Sobre el límite diario la solicitud sigue pendiente | api | passed (1/1) |
| HU-G4-08 | CA4 | CP-A31 | Solo el destinatario puede aceptar | api | passed (2/2) |
| HU-G4-08 | CA4 | CP-A32 | Una solicitud vencida no se puede aceptar | api | xfailed → DEF-03 |
| HU-G4-08 | CA4 | CP-A33 | Una solicitud ya aceptada no se acepta dos veces | api | passed (1/1) |
| HU-G4-08 | CA1, CA3 | CP-W16 | Aceptar pide confirmación e informa la transferencia | web | passed (3/3) |
| HU-G4-08 | CA2 | CP-W17 | Sin saldo se muestra el error y la solicitud sigue pendiente | web | passed (3/3) |
| HU-G4-09 | CA1 | CP-A34 | Rechazar con motivo opcional de hasta 60 caracteres | api | passed (3/3) |
| HU-G4-09 | CA1 | CP-A35 | Rechazar cambia el estado y avisa al solicitante sin mover dinero | api | passed (1/1) |
| HU-G4-09 | CA1 | CP-A36 | Una solicitud vencida no se puede rechazar | api | passed (1/1) |
| HU-G4-09 | CA1 | CP-W18 | Rechazar con motivo | web | passed (3/3) |
| HU-G4-10 | CA1 | CP-A37 | El solicitante cancela una solicitud pendiente | api | passed (1/1) |
| HU-G4-10 | CA1 | CP-A38 | Solo el solicitante puede cancelar | api | passed (2/2) |
| HU-G4-10 | CA1 | CP-A39 | Una solicitud ya aceptada no se puede cancelar | api | passed (1/1) |
| HU-G4-10 | CA1 | CP-W19 | Cancelar una solicitud enviada pide confirmación | web | passed (3/3) |
| HU-G4-01 a HU-G4-10 | técnico | CP-T04 | Contrato OpenAPI generado con Schemathesis | api | passed (10/10) |

Los casos web se ejecutan 3 veces seguidas: `passed (3/3)` indica las tres pasadas. `xfailed → DEF-xx` es un fallo esperado enlazado a `docs/defectos.md`.
