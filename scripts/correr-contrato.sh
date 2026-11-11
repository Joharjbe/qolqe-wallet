#!/usr/bin/env bash
# Pruebas de contrato (Schemathesis) del núcleo y de G4 contra Qolqe en QOLQE_URL (por defecto el puerto 8000).
# Los checks y operaciones excluidos, con su motivo, están en schemathesis.toml.
# El token y los filtros por valor están en scripts/contrato_hooks.py.
# EVIDENCIA=con-imagenes guarda además todas las peticiones y respuestas en reportes/contrato/peticiones.har.
set -euo pipefail
cd "$(dirname "$0")/.."
export QOLQE_URL=${QOLQE_URL:-http://127.0.0.1:8000}
export SCHEMATHESIS_HOOKS=scripts/contrato_hooks.py
curl -sf -X POST "$QOLQE_URL/api/pruebas/reiniciar" > /dev/null

# Núcleo: registro, ingreso y salida, sesiones, saldo, perfil, cierre, transferencias y simulación. G4: contactos y solicitudes.
OPERACIONES='^/api/((contactos|solicitudes)(/.*)?|usuarios|auth/(login|logout)|seguridad/sesiones|cuentas/me(/saldo|/cierre)?|transferencias(/comision)?)$'

FORMATOS=junit,html
HAR=()
if [ "${EVIDENCIA:-sin-imagenes}" = con-imagenes ]; then
  FORMATOS=junit,html,har
  HAR=(--report-har-path reportes/contrato/peticiones.har)
fi
mkdir -p reportes/contrato
# ${HAR[@]+...} evita el error de set -u con un arreglo vacío en el bash 3.2 de macOS.
schemathesis run "$QOLQE_URL/openapi.json" \
  --include-path-regex "$OPERACIONES" \
  --max-examples 30 --seed 42 \
  --report "$FORMATOS" --report-junit-path reportes/contrato/junit.xml --report-html-path reportes/contrato/html \
  ${HAR[@]+"${HAR[@]}"}
