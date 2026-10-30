#!/usr/bin/env bash
# Deja lista la demo en vivo: dependencias, datos limpios, Qolqe levantado y pestañas abiertas.
# Uso, desde la raíz del repositorio: ./scripts/preparar-demo.sh
set -euo pipefail
cd "$(dirname "$0")/.."

PUERTO=8000
BD=.demo-data/qolqe.db

[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements-dev.txt
[ -d node_modules ] || npm ci
npx playwright install chromium > /dev/null
npx bddgen

if ! curl -sf "http://127.0.0.1:$PUERTO/api/salud" > /dev/null; then
  mkdir -p .demo-data reportes
  QOLQE_BD="$BD" QOLQE_MODO_PRUEBA=1 nohup python -m uvicorn qolqe.main:app --host 127.0.0.1 --port "$PUERTO" > reportes/uvicorn-demo.log 2>&1 &
  curl -sf --retry 60 --retry-delay 1 --retry-connrefused "http://127.0.0.1:$PUERTO/api/salud" > /dev/null
fi
curl -sf -X POST "http://127.0.0.1:$PUERTO/api/pruebas/reiniciar" > /dev/null

REPO=https://github.com/Joharjbe/qolqe-wallet
for url in \
  "$REPO/actions/workflows/pruebas.yml" \
  "https://joharjbe.github.io/qolqe-wallet/" \
  "https://joharjbe.github.io/qolqe-wallet/web/" \
  "$REPO/pull/3" \
  "http://127.0.0.1:$PUERTO/login"; do
  command -v open > /dev/null && open "$url" || echo "Abrir: $url"
done

echo
echo "Listo. Qolqe responde en http://127.0.0.1:$PUERTO con datos limpios."
echo "Para la demo, en esta terminal: source .venv/bin/activate"
echo "Para apagar Qolqe al terminar: lsof -ti:$PUERTO | xargs kill"
