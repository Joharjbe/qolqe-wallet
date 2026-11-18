"""Infraestructura de la suite de API contra Qolqe en QOLQE_URL: usuarios de la semilla, sesiones y reinicio por escenario."""
import os
import unicodedata

import httpx
import pytest

URL = os.environ.get("QOLQE_URL", "http://127.0.0.1:8000")
USUARIOS = {  # Credenciales de la semilla (qolqe/semilla.py): la suite de API las escribe solo aquí.
    "Ana": ("987654321", "4826"),
    "Bruno": ("912345678", "7391"),
    "Carla": ("956781234", "5917"),
    "Diego": ("998877665", "3604"),
}
CERRADAS = {"Fabián": ("934567812", "6029")}  # Cuenta CERRADA de la semilla.
CARGA_BASE = 900000000  # Usuarios de carga de la semilla, disponibles como contactos: celulares 900000001 a 900000200.
PIN_CARGA = "2580"  # El mismo PIN para todos los usuarios de carga.


def pytest_bdd_apply_tag(tag, function):
    """Un escenario con @DEF-xx es un fallo esperado enlazado a su defecto en docs/defectos.md.

    Solo una aserción cuenta como el defecto: un error de conexión, un KeyError o un paso roto quedan como fallo.
    """
    if tag.startswith("DEF-"):
        pytest.mark.xfail(strict=True, raises=AssertionError, reason=f"{tag} reportado en docs/defectos.md")(function)
        return True
    return None


class Sesiones:
    """Cliente HTTP con los tokens de cada usuario y lo que el escenario va recordando."""

    def __init__(self, cliente):
        self.cliente = cliente
        self.tokens = {}
        self.actual = None
        self.respuesta = None
        self.solicitud_id = None

    def ingresar(self, nombre):
        celular, pin = USUARIOS[nombre]
        r = self.cliente.post("/api/auth/login", json={"celular": celular, "pin": pin})
        assert r.status_code == 200, r.text
        self.tokens[nombre] = {"Authorization": f"Bearer {r.json()['access_token']}"}
        self.actual = nombre

    def como(self, nombre=None):
        nombre = nombre or self.actual
        if nombre not in self.tokens:
            self.ingresar(nombre)
        return self.tokens[nombre]

    def pedir(self, metodo, ruta, nombre=None, **opciones):
        self.respuesta = self.cliente.request(metodo, ruta, headers=self.como(nombre), **opciones)
        return self.respuesta

    def contactos(self, nombre=None):
        filas, pagina = [], 1
        while True:
            datos = self.cliente.get("/api/contactos", headers=self.como(nombre), params={"pagina": pagina}).json()
            filas += datos["contactos"]
            if pagina >= datos["total_paginas"]:
                return filas
            pagina += 1

    def contacto_id(self, alias, nombre=None):
        return next(c["id"] for c in self.contactos(nombre) if c["alias"] == alias)

    def agregar(self, nombre, celular, alias):
        r = self.cliente.post("/api/contactos", headers=self.como(nombre), json={"celular": celular, "alias": alias})
        assert r.status_code == 201, r.text
        return r.json()

    def completar_contactos(self, nombre, total):
        existentes = len(self.contactos(nombre))
        for i in range(existentes + 1, total + 1):
            self.agregar(nombre, str(CARGA_BASE + i), f"Zeta {i:02d}")

    def saldo(self, nombre):
        return self.cliente.get("/api/cuentas/me/saldo", headers=self.como(nombre)).json()["saldo"]

    def solicitar_entre(self, solicitante, destinatario, monto, motivo="Motivo de prueba"):
        celular = USUARIOS[destinatario][0]
        contacto = next((c for c in self.contactos(solicitante) if c["celular"] == celular), None)
        contacto_id = contacto["id"] if contacto else self.agregar(solicitante, celular, f"Alias {destinatario}")["id"]
        r = self.cliente.post("/api/solicitudes", headers=self.como(solicitante),
                              json={"contacto_id": contacto_id, "monto": monto, "motivo": motivo})
        assert r.status_code == 201, r.text
        self.solicitud_id = r.json()["id"]


@pytest.fixture
def s():
    """FIRST-Independent: cada escenario empieza con datos semilla y el reloj real."""
    with httpx.Client(base_url=URL, timeout=30) as cliente:
        assert cliente.delete("/api/pruebas/reloj").status_code == 200
        assert cliente.post("/api/pruebas/reiniciar").status_code == 200
        yield Sesiones(cliente)
        cliente.delete("/api/pruebas/reloj")


def orden_alfabetico(texto):
    """Orden alfabético en español: sin distinguir mayúsculas ni tildes (el mismo criterio que CP-A47)."""
    texto = texto.replace("ñ", "n\uffff").replace("Ñ", "N\uffff")  # La ñ es una letra propia, después de la n.
    sin_tildes = "".join(c for c in unicodedata.normalize("NFD", texto) if not unicodedata.combining(c))
    return sin_tildes.casefold()


# Pasos de cada área y hooks de evidencia en su propio módulo. Se importan al final porque usan los helpers de arriba.
from evidencia import *
from pasos_g4 import *
from pasos_g4_extra import *
from pasos_nucleo_acceso import *
from pasos_nucleo_dinero import *
