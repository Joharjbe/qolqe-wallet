# Hoja de la demo · sábado 21-nov

Lo que se dice y por qué este orden: [`guion.md`](guion.md). Carpeta: la raíz del clon `qolqe-wallet`, la que tiene `.venv` y `node_modules` (el clon `qolqe-wallet-p3` no se usa).

**Antes de k6, en una línea:** `docker stop qolqe_kiwi_web qolqe_kiwi_db; lsof -ti tcp:8000 -sTCP:LISTEN | xargs kill` y cerrar el editor y todas las pestañas menos la del deck.

## 1. En casa, el sábado por la mañana (con red y Docker Desktop abierto)

| # | Qué | Comando |
|---|---|---|
| 1 | Repo al tag | `git switch main && git pull --ff-only entrega main && git fetch -q entrega --tags && git describe --tags` → `entrega-final-v1`. Si sale `entrega-final-v1-N-g…`, hay commits después del tag; si da error, el tag todavía no existe (al 18-nov, `git ls-remote --tags entrega` solo daba `parte-2` y `parte-3`) |
| 1b | Checks de main | `gh api repos/Joharjbe/qolqe-wallet/branches/main -q .protection.required_status_checks.contexts` → `["api","web","quality-gate"]` (salida del 18-nov), lo mismo que dicen la lámina 13, `docs/pipeline.md:32` y `docs/informe.md:164`. Si da otra cosa, en la lámina 13 di lo que dio (`guion.md`, fila `gate`) |
| 2 | Base de k6 (≈ 2,5 min) | `export RESULTADOS="$HOME/demo-qolqe" USUARIOS_CSV="$HOME/demo-qolqe/usuarios.csv"` y `SIN_BUILD=1 tests/performance/preparar.sh 3000` |
| 3 | Ensayo de k6 (≈ 2:40) | «Antes de k6» y el principal: primera línea `…/demo-qolqe/demo/<marca>`, última `k6 = 99 … integridad = 0` |
| 4 | Parte 3 al respaldo | `.venv/bin/python .github/scripts/sitio_rendimiento.py --sitio ~/Desktop/respaldo-sitio-con-imagenes` |
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
- **Si k6 falla dos veces:** `open tests/performance/resultados/demo/20261111-2125/reporte.html` o el video.
- **Sin internet:** `cd ~/Desktop/respaldo-sitio-con-imagenes && python3 -m http.server 8100` → http://localhost:8100/
