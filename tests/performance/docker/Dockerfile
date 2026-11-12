# Qolqe Wallet para las pruebas de rendimiento (P2, Parte 3). Entorno elegido: Docker (diseño §6.1).
# Se construye desde la raíz del repo, sin modificar qolqe/:
#   docker build -f tests/performance/docker/Dockerfile -t qolqe-perf:p3 .
# El contexto lo filtra Dockerfile.dockerignore: solo entran requirements, constraints, versiones y qolqe/.
# Los límites (--cpus=1 --memory=1g --memory-swap=1g) se ponen al ejecutar (docker/comun.sh), no aquí.

# Python 3.11 como el .venv del repo (3.11.6 en local; 3.11.15 es la imagen oficial ya descargada, arm64).
FROM python:3.11.15-slim-bookworm

# QOLQE_MODO_PRUEBA=1 habilita /api/pruebas/* (reiniciar y saldo): endpoints de soporte que pide el
# enunciado para preparar los datos (D2). La BD y la plantilla van en /data, que es un volumen con nombre
# (diseño §6.1: no un bind mount de macOS, que es más lento y afecta al WAL de SQLite).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    QOLQE_BD=/data/qolqe.db \
    QOLQE_BD_PLANTILLA=/data/plantilla_carga.db \
    QOLQE_MODO_PRUEBA=1

WORKDIR /app
COPY requirements.txt constraints.txt tests/performance/docker/versiones.txt ./

# Dependencias del repo con sus restricciones (constraints.txt fija FastAPI 0.117.1 por DEF-07) y las
# versiones transitivas del .venv (versiones.txt). psutil y py-spy son para medir (monitor y perfil).
# pip_freeze.txt queda en la imagen como evidencia (preparar.sh lo copia a resultados/entorno/).
RUN pip install --no-cache-dir -r requirements.txt -c constraints.txt -c versiones.txt \
 && pip install --no-cache-dir -c versiones.txt psutil py-spy \
 && pip freeze > /app/pip_freeze.txt

COPY qolqe/ ./qolqe/

# Un solo proceso de uvicorn, como pide el README (el reloj de pruebas vive en memoria). Escucha en 0.0.0.0
# porque la publicación del puerto entra por la interfaz del contenedor; en el host se publica en
# 127.0.0.1:8090 (config.env), lejos del 8000 (demo) y del 8443 (Kiwi).
EXPOSE 8090
CMD ["python", "-m", "uvicorn", "qolqe.main:app", "--host", "0.0.0.0", "--port", "8090"]
