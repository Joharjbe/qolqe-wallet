# Alcance y diseño de casos · Módulo G4

**Módulo:** G4 · Contactos y solicitudes de dinero (`docs/requisitos.md`, sección 7).

## Por qué G4

G4 mueve dinero sin que el pagador inicie la operación: una persona pide y otra acepta. Combina tres riesgos que justifican su prioridad:

| Riesgo | Dónde | Impacto |
|---|---|---|
| Dinero mal transferido | Aceptar una solicitud (HU-G4-08), transferir a un contacto (HU-G4-05) | Alto: 3 historias de prioridad Alta tocan saldo |
| Máquina de estados | PENDIENTE → ACEPTADA, RECHAZADA, CANCELADA o VENCIDA (R-G4-05) | Alto: una transición indebida mueve dinero o bloquea una deuda |
| Acceso entre usuarios | Solo el destinatario acepta y solo el solicitante cancela | Alto: un recurso ajeno debe responder 404 |

## Criterio de nivel

Regla de la clase 11: *cada regla se prueba en el nivel más bajo donde se pueda detectar; por la interfaz solo van los recorridos críticos y lo que solo se ve en la pantalla.*

Un criterio se define como **web** si cumple al menos una condición:

1. Lo que afirma solo se ve en la pantalla (lista, orden, pestañas, avisos, botones disponibles).
2. Es un paso de un recorrido crítico que pasa por dinero.
3. La interfaz debe comunicar al usuario un error de la API.

Las validaciones de reglas (límites, formatos, permisos) quedan en **API**; la web solo confirma que un error se muestra.

## Criterios por nivel

| HU | Prioridad | CA | Qué verifica | API | Web |
|---|---|---|---|---|---|
| HU-G4-01 | Alta | CA1 | Alta y reglas R-G4-01 a 03 | CP-A01 a A07 | CP-W01, W02, W10 |
| HU-G4-02 | Media | CA1 | Favoritos primero, orden, 10 por página, total | CP-A08 | CP-W03 |
| HU-G4-02 | Media | CA2 | Búsqueda sin mayúsculas ni tildes | CP-A09 | CP-W04 |
| HU-G4-02 | Media | CA3 | Alias, nombre enmascarado, celular, favorito | CP-A10 | CP-W05 |
| HU-G4-03 | Media | CA1 | Editar alias y favorito, límite de 5 | CP-A11 a A13 | CP-W06 |
| HU-G4-04 | Baja | CA1 | Eliminar conserva transferencias | CP-A14 | CP-W07 |
| HU-G4-04 | Baja | CA2 | Bloqueo con solicitudes pendientes | CP-A15, A16 | CP-W08 |
| HU-G4-05 | Alta | CA1 | Transferir eligiendo un contacto | CP-A17, A18 | CP-W09 |
| HU-G4-06 | Alta | CA1 | Contacto, monto y motivo | CP-A21 a A24 | CP-W10, W11, W12 |
| HU-G4-06 | Alta | CA2 | PENDIENTE, vence a las 48 h, SMS | CP-A20 | CP-W13 |
| HU-G4-07 | Media | CA1 | Enviadas y recibidas, filtro | CP-A25, A26 | CP-W14 |
| HU-G4-07 | Media | CA2 | Se muestra VENCIDA | CP-A27 | CP-W15 |
| HU-G4-08 | Alta | CA1, CA3 | Transferencia, ACEPTADA, código, SMS | CP-A28 | CP-W10, W16 |
| HU-G4-08 | Alta | CA2 | Si falla, sigue PENDIENTE | CP-A29, A30 | CP-W17 |
| HU-G4-08 | Alta | CA4 | Solo el destinatario, solo PENDIENTE y no vencida | CP-A31 a A33 | CP-W15 (sin botones) |
| HU-G4-09 | Media | CA1 | Rechazar con motivo opcional, SMS | CP-A34 a A36 | CP-W18 |
| HU-G4-10 | Media | CA1 | Cancelar, solo el solicitante | CP-A37 a A39 | CP-W19 |

## Casos técnicos

| Caso | Qué verifica | Herramienta |
|---|---|---|
| CP-T01, T03 | Sin token responde 401 `NO_AUTENTICADO` | pytest-bdd |
| CP-T02, A31, A38 | Recurso de otro usuario responde 404 (propiedad de los datos) | pytest-bdd |
| CP-T04 | Sin respuestas 500; estados, cabeceras y esquemas según el contrato OpenAPI | Schemathesis |
| Repetibilidad | Datos reiniciados en cada escenario; suite web 3 veces seguidas | Playwright `--repeat-each=3` |

## Técnicas de diseño

| Técnica (ISTQB 4.2) | Dónde se aplica |
|---|---|
| Valores límite | Alias 2/3/20/21 (CP-A03), monto 0/0.01/500/500.01 (CP-A21), motivo 2/3/60/61 (CP-A22), rechazo 60/61 (CP-A34), 15 contactos (CP-A07), 5 favoritos (CP-A12), 10 solicitudes (CP-A23), 48 horas exactas (CP-A27) |
| Partición de equivalencia | Celular inválido, propio, no registrado, cerrado, existente (CP-A02); caracteres del alias (CP-A03, A04) |
| Transición de estados | PENDIENTE a cada estado final (CP-A27, A28, A35, A37) y transiciones no válidas (CP-A32, A33, A36, A39) |
| Tabla de decisión | Quién actúa × estado de la solicitud (CP-A31, A38) |
| Casos de uso | Recorrido completo entre dos usuarios (CP-W10) |
