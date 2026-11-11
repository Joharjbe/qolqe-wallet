#!/usr/bin/env bash
# Certificado propio para Kiwi en https://localhost:8443. El de la imagen oficial está emitido para "buildkitsandbox",
# así que tcms-api (que verifica el certificado) no aceptaría localhost. Se genera una sola vez; ssl/ no se versiona.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p ssl
if [ -f ssl/localhost.crt ] && [ -f ssl/localhost.key ]; then
  echo "Ya existe ssl/localhost.crt"
  exit 0
fi
openssl req -x509 -newkey rsa:2048 -nodes -days 825 -subj "/O=Qolqe G4/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" -addext "basicConstraints=critical,CA:TRUE" \
  -keyout ssl/localhost.key -out ssl/localhost.crt 2> /dev/null
# El contenedor corre con otro usuario: necesita leer la clave montada.
chmod 644 ssl/localhost.key ssl/localhost.crt
echo "Listo: ssl/localhost.crt (úsalo como certificado de confianza en kiwi_sincronizar.py y en el navegador)."
