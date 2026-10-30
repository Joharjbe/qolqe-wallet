# Guion de la demo en vivo

Dejar abiertas antes de exponer: la pestaña **Actions** del repositorio, la **portada de reportes**, el **PR #1** y el **PR de quality gate**, y dos terminales en la raíz del repositorio con `.venv` activado.

## Parte 2 (lo que pide la rúbrica)

| Paso | Qué abrir o ejecutar | Qué decir |
|---|---|---|
| 1. Run real | Actions → último run de *Pruebas G4* | Cada push o PR lo dispara. Tres jobs: `api`, luego `web` (con `needs`) y `reportes` solo en main |
| 2. Resumen | Dentro del run, la tabla del resumen | Sin descargar nada se ve qué pasó |
| 3. Reporte abierto | Portada → *Reporte web* | 57 ejecuciones: 19 escenarios × 3. Abrir CP-W10 y mostrar sus pasos Gherkin |
| 4. Trazabilidad | Portada → matriz, o `docs/trazabilidad.md` | Cada fila une historia, caso y resultado de un run concreto. Señalar `xfailed → DEF-03` |
| 5. Quality gate | PR de quality gate, en rojo y bloqueado | Una prueba rota impide fusionar: `web` queda *skipped* y skipped no es verde |
| 6. Automatización | Terminal, comando de abajo | Navegador visible: agrega contacto, solicita, Bruno acepta, ambos saldos cambian |
| 7. Código | `tests/e2e/pages/SolicitudesPage.ts` | El Page Object concentra los localizadores; no hay esperas fijas |

```bash
npx bddgen && npx playwright test --headed --grep "CP-W10"
```

## Parte 1 (API)

```bash
python -m pytest tests/api -v --no-header
```

Terminar en el resumen: `64 passed, 4 xfailed`. Los 4 fallos esperados son DEF-01 a DEF-04.

Para Schemathesis, usar el comando de la sección 6 del README y abrir `reportes/contrato/html/index.html`.

## Si algo falla en vivo

No improvisar: abrir el último run verde de Actions y su reporte publicado. Ese es el resultado oficial, y además es el argumento de la clase: *el pipeline es la referencia, no la máquina de nadie*.
