#!/usr/bin/env bash
# Pruebas de contrato de G4 contra Qolqe en el puerto 8000. Los checks excluidos están en schemathesis.toml.
set -euo pipefail
URL=${QOLQE_URL:-http://127.0.0.1:8000}
curl -sf -X POST "$URL/api/pruebas/reiniciar" > /dev/null
TOKEN=$(curl -sf -X POST "$URL/api/auth/login" -H "Content-Type: application/json" \
  -d '{"celular":"987654321","pin":"4826"}' | python -c "import json,sys;print(json.load(sys.stdin)['access_token'])")
schemathesis run "$URL/openapi.json" -H "Authorization: Bearer $TOKEN" \
  --include-path-regex '^/api/(contactos|solicitudes)' \
  --max-examples 30 --seed 42 \
  --report junit,html --report-junit-path reportes/contrato/junit.xml --report-html-path reportes/contrato/html
