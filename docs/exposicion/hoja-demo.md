# Hoja de la demo · sábado 21-nov

Lo que se dice y por qué este orden: [`guion.md`](guion.md). Carpeta: la raíz del clon `qolqe-wallet`, la que tiene `.venv` y `node_modules` (el clon `qolqe-wallet-p3` no se usa).

**Antes de k6, en una línea:** `docker stop qolqe_kiwi_web qolqe_kiwi_db; lsof -ti tcp:8000 -sTCP:LISTEN | xargs kill` y cerrar el editor y todas las pestañas menos la del deck.

## 1. En casa, el sábado por la mañana (con red y Docker Desktop abierto)

| # | Qué | Comando |
|---|---|---|
| 1 | Repo al tag | `git switch main && git pull --ff-only entrega main && git fetch -q entrega --tags && git describe --tags` → `entrega-final-v2`. Si sale `entrega-final-v2-N-g…`, hay N commits en `main` después del tag: no debería pasar; revísalos con `git log --oneline entrega-final-v2..main` antes de exponer. Si da error, faltan los tags: repite el `git fetch` (v2 existe en `entrega` desde el 19-nov, sobre el commit final de `main`; v1, del 18-nov, queda como versión anterior) |
| 1b | Checks de main | `gh api repos/Joharjbe/qolqe-wallet/branches/main -q .protection.required_status_checks.contexts` → `["api","web","quality-gate"]` (salida del 18-nov), lo mismo que dicen la lámina 15, `docs/pipeline.md:32` y `docs/informe.md:164`. Si da otra cosa, en la lámina 15 di lo que dio (`guion.md`, fila `gate`) |
| 2 | Base de k6 (≈ 2,5 min) | `export RESULTADOS="$HOME/demo-qolqe" USUARIOS_CSV="$HOME/demo-qolqe/usuarios.csv"` y `SIN_BUILD=1 tests/performance/preparar.sh 3000` |
| 3 | Ensayo de k6 (≈ 2:40) | «Antes de k6» y el principal: primera línea `…/demo-qolqe/demo/<marca>`, última `k6 = 99 … integridad = 0` |
| 4 | Respaldo sin red | `ls ~/Desktop/respaldo-sitio-entrega-final/rendimiento/index.html`: es el sitio del run #28 (`con-imagenes`, commit del tag v1, mismo código que `main`) y ya trae la Parte 3 |
| 5 | Al final | `./scripts/preparar-demo.sh` → `Listo. Qolqe responde en …` |

## 2. En el salón, 10 minutos antes (sin red; checklist en [`guion.md`](guion.md#checklist-del-día))

1. Si Kiwi no responde: `(cd herramientas/kiwi && docker compose up -d)`; sesión en localhost:8443.
2. k6: `docker image inspect qolqe-perf:p3 --format '{{.Id}}'`, `k6 version` y `k6 inspect` (`tests/performance/README.md`).
3. Dos terminales: la de la demo, con `source .venv/bin/activate`, y `docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"`.
4. CPU ocioso: `top -l 2 -n 0 -s 3 | grep "CPU usage" | tail -1`. 75 % o más: ☐ principal; menos: ☐ respaldo (con todo abierto es más estricta que la de ese README).

## 3. En vivo

| Minuto | Paso |
|---|---|
| 9:55 | D1 Reportería: pestañas 2 (con la matriz), 3, 4 y 2; cierra en la 1 con el *Summary* del run #24, intento 1 (https://github.com/Joharjbe/qolqe-wallet/actions/runs/44225240314/attempts/1), y *Run workflow* abierto, sin lanzarlo |
| 11:10 | D2 Patrón: la versión de 40 s de [`guion-patron-90s.md`](guion-patron-90s.md), en el editor |
| 11:50 | D3 Kiwi: pestaña 6 |
| 12:10 | D4: la línea «Antes de k6» |
| 12:20 | D5: el comando marcado; con `web dashboard`, abrir http://localhost:5665. Fin ≈ 15:00 |

- **Principal:** `RESULTADOS="$HOME/demo-qolqe" USUARIOS_CSV="$HOME/demo-qolqe/usuarios.csv" ESPERA_MAX=20 tests/performance/correr.sh demo`
- **Respaldo,** si lo marcaste o si sale `V-04: el equipo no está libre`: `RESULTADOS="$HOME/demo-qolqe" USUARIOS_CSV="$HOME/demo-qolqe/usuarios.csv" FORZAR=1 ESPERA_MAX=0 tests/performance/correr.sh demo`
- **Opcional en D2, si vas adelantado o si pregunta cómo corre el Page Object:** `SLOWMO=700 npx playwright test --headed --grep "CP-W10"` → 28 s (23 s la prueba), el mismo recorrido de solicitudes del editor, en un Chromium visible. Después, `curl -sf -X POST http://127.0.0.1:8000/api/pruebas/reiniciar` deja los datos limpios.
- **Si k6 falla dos veces:** `open tests/performance/resultados/demo/20261111-2125/reporte.html` o el video.
- **Sin internet:** `cd ~/Desktop/respaldo-sitio-entrega-final && python3 -m http.server 8100` → http://localhost:8100/

## 4. Ensayo técnico del 18-nov (en esta Mac)

Cada comando de esta hoja tal como estaba el 18-nov, corrido en el orden de arriba, con el repo en la rama del PR #12 (mismo código que el tag). Ese día el paso 1 daba `entrega-final-v1` (v2 todavía no existía), y el paso 4 y el 8100 se probaron sobre el respaldo del run #18. El respaldo de ahora, `respaldo-sitio-entrega-final` (run #28), ya trae `rendimiento/`: vuelve a servirlo en el 8100 antes del sábado.

| Paso | Resultado | Tiempo |
|---|---|---|
| 1 y 1b. Tag y checks | `entrega-final-v1` · `["api","web","quality-gate"]` | — |
| 2. Base de k6 | `Listo. Evidencia del entorno en …/demo-qolqe/entorno` | 154 s |
| 3. Ensayo de k6, principal | V-04: 75,47 % ocioso · `5 de 9 umbrales … → FALLA` · `TOTAL descuadres: 0` · `U-07: PASA` · `k6 = 99 … integridad = 0` | 161 s |
| 4. Parte 3 al respaldo | 92 archivos de 8 escenarios en `rendimiento/` (8,4 MB) | segundos |
| 5. `preparar-demo.sh` | `Listo. Qolqe responde en …`, Kiwi arriba, 7 pestañas y los 4 archivos del patrón en sus líneas | 20 s con dependencias ya instaladas |
| API en vivo, CP-A28 | `1 passed, 765 deselected in 0.52s` | 2 s |
| Web en vivo, CP-W10 con `--headed` | `1 passed` | 28 s |
| Capacidad de IA sin red | `40 fallos (40 casos) · 32 grupos · 36 clasificados · 1 rechazados por las guardas`; CP-T17 rechazado | < 1 s |
| Respaldo sin red en el 8100 | portada, `historial.html`, `web/`, `api/`, `evidencias/` y `rendimiento/` responden 200 | — |

El CPU ocioso quedó justo en el límite de la principal (77 % antes de lanzar, 75,47 % en V-04). Lo que más consumía era `suggestd`, un proceso del sistema (≈ 80 % de un núcleo), y CodexBar (18 %). El sábado, antes del paso 4 del salón, mira `ps -Ao pcpu,comm -r | head -4` y cierra lo que se pueda; si no llega a 75 %, usa el respaldo.
