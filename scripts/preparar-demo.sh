#!/usr/bin/env bash
# Deja lista la demo en vivo: dependencias, datos limpios, Qolqe levantado, Kiwi, pestañas y archivos del patrón abiertos.
# Uso, desde la raíz del repositorio: ./scripts/preparar-demo.sh
# Necesita red (pip, npm y Chromium): se corre en casa, no en el aula. Orden del día: docs/exposicion/hoja-demo.md
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

# Kiwi TCMS (docs/gestion-casos.md): solo si Docker está abierto; la demo sigue sin él.
# El certificado va antes del compose, que monta ssl/localhost.crt y .key; generar-certificado.sh no hace nada si ya existen.
KIWI=https://localhost:8443
if docker info > /dev/null 2>&1; then
  (cd herramientas/kiwi && ./generar-certificado.sh > /dev/null && docker compose up -d > /dev/null)
else
  echo "Docker no responde: se omite Kiwi TCMS ($KIWI)."
fi

REPO=https://github.com/Joharjbe/qolqe-wallet
PAGES=https://joharjbe.github.io/qolqe-wallet
for url in \
  "$REPO/actions/workflows/pruebas.yml" \
  "$PAGES/" \
  "$PAGES/historial.html" \
  "$PAGES/web/" \
  "$REPO/pulls?q=is%3Apr" \
  "$KIWI/" \
  "http://127.0.0.1:$PUERTO/login"; do
  command -v open > /dev/null && open "$url" || echo "Abrir: $url"
done

# Recorrido del patrón (docs/exposicion/guion-patron-90s.md): los cuatro archivos, cada uno en la línea del salto.
# La línea se busca por su texto, porque el .feature puede cambiar de largo.
linea() { grep -n -m1 -F -- "$2" "$1" | cut -d: -f1 || echo 1; }
PATRON=(
  "features/web/solicitudes_web.feature:$(linea features/web/solicitudes_web.feature 'acepta la solicitud "Devolución demo G4"')"
  "tests/e2e/steps/solicitudes.steps.ts:$(linea tests/e2e/steps/solicitudes.steps.ts "When('acepta la solicitud")"
  "tests/e2e/pages/SolicitudesPage.ts:$(linea tests/e2e/pages/SolicitudesPage.ts 'async aceptar(')"
  "tests/e2e/pages/componentes.ts:$(linea tests/e2e/pages/componentes.ts 'export class DialogoConfirmacion')"
)
if command -v code > /dev/null; then
  code -g "${PATRON[@]}" || echo "Abrir en el editor: ${PATRON[*]}"
else
  for archivo in "${PATRON[@]}"; do
    command -v open > /dev/null && open -t "${archivo%%:*}" || echo "Abrir: $archivo"
  done
fi

echo
echo "Listo. Qolqe responde en http://127.0.0.1:$PUERTO con datos limpios."
echo "Para la demo, en esta terminal: source .venv/bin/activate"
echo "Para apagar Qolqe al terminar: lsof -ti tcp:$PUERTO -sTCP:LISTEN | xargs kill"
