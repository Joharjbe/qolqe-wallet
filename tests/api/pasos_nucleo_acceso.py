"""Pasos de pytest-bdd del núcleo: registro, sesión, saldo y perfil (HU-N-01 a HU-N-05)."""
from pytest_bdd import given, parsers, then, when  # noqa: F401

import conftest  # noqa: F401  Helpers compartidos: URL, USUARIOS, Sesiones.
