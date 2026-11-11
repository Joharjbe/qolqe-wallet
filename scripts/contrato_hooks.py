"""Hooks de Schemathesis para el contrato (se cargan con SCHEMATHESIS_HOOKS).

1. Token: cerrar sesión y cerrar la cuenta invalidan el token con el que se llaman. Esas dos operaciones
   reciben un token recién emitido de un usuario desechable; el resto usa el token de Ana, que así no se
   invalida a mitad de la corrida.
2. Fallos descartados por valor: schemathesis.toml solo desactiva un check entero por operación. Para no
   perder el check en toda la operación, los dos casos clasificados se descartan aquí con filter_failure
   (el reporte HTML los cuenta como "dropped by filter_failure").
"""
import os
import random
import re

import httpx
import schemathesis

URL = os.environ.get("QOLQE_URL", "http://127.0.0.1:8000")
ANA = {"celular": "987654321", "pin": "4826"}
INVALIDAN_EL_TOKEN = {"/api/auth/logout", "/api/cuentas/me/cierre"}
# PIN distinto al de los ejemplos del contrato (4826): un ejemplo no debe cerrar la cuenta desechable.
PIN_DESECHABLE = "2580"


def _token(credenciales: dict) -> str | None:
    r = httpx.post(f"{URL}/api/auth/login", json=credenciales, timeout=30)
    return r.json()["access_token"] if r.status_code == 200 else None


def _registrar_desechable() -> dict:
    while True:
        celular = f"9{random.randint(10_000_000, 99_999_999)}"
        r = httpx.post(f"{URL}/api/usuarios", timeout=30, json={
            "dni": f"{random.randint(10_000_000, 99_999_999)}", "nombres": "Usuario Contrato",
            "celular": celular, "pin": PIN_DESECHABLE,
        })
        if r.status_code == 201:
            return {"celular": celular, "pin": PIN_DESECHABLE}


@schemathesis.auth(refresh_interval=None)
class TokenQolqe:
    ana: str | None = None
    desechable: dict | None = None

    def get(self, case, context):
        if context.operation.path in INVALIDAN_EL_TOKEN:
            token = _token(self.desechable) if self.desechable else None
            if token is None:  # Primera vez, o la cuenta desechable quedó cerrada.
                self.desechable = _registrar_desechable()
                token = _token(self.desechable)
            return token
        if self.ana is None:
            self.ana = _token(ANA)
        return self.ana

    def set(self, case, data, context):
        case.headers = {**(case.headers or {}), "Authorization": f"Bearer {data}"}


def _dato_invalido_aceptado(failure) -> bool:
    return getattr(failure, "code", None) == "ST201"  # Schema-violating request accepted (negative_data_rejection)


@schemathesis.hook("filter_failure").apply_to(name="POST /api/transferencias")
def defecto_campo_de_otro_tipo(context, failure, case, response):
    """DEF-NEW-transferencia-campos-ignorados: la API ignora el campo del otro tipo aunque no cumpla su formato
    (cci en QOLQE, celular_destino en INTERBANCARIA). Solo se descarta ese fallo; cualquier otro dato inválido
    aceptado en esta operación sigue fallando."""
    body = case.body if isinstance(case.body, dict) else {}
    campo, formato = ("celular_destino", r"9\d{8}") if body.get("tipo") == "INTERBANCARIA" else ("cci", r"\d{20}")
    valor = body.get(campo)
    return not (_dato_invalido_aceptado(failure) and isinstance(valor, str) and not re.fullmatch(formato, valor))


@schemathesis.hook("filter_failure").apply_to(name="PUT /api/cuentas/me")
def correo_vacio_documentado(context, failure, case, response):
    """Falso positivo: la descripción de `correo` en el contrato dice "null o vacío lo quita" (lo prueba CP-NA67).
    El esquema `format: email` no lo expresa, así que Schemathesis toma "" como dato inválido."""
    body = case.body if isinstance(case.body, dict) else {}
    return not (_dato_invalido_aceptado(failure) and body.get("correo") == "")
