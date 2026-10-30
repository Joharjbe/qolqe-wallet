"""Preparación controlada de la instancia local de Qolqe para la demo E2E."""

from urllib.parse import urlparse
from urllib.request import Request, urlopen
import json

from robot.api.deco import keyword


@keyword("Reiniciar datos locales de Qolqe")
def reiniciar_datos_locales_de_qolqe(base_url: str) -> None:
    parsed = urlparse(base_url)
    if parsed.scheme != "http" or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("La demo solo permite reiniciar una instancia HTTP local de Qolqe.")
    if not parsed.port:
        raise ValueError("Indica el puerto explícitamente en BASE_URL.")
    with urlopen(f"{base_url.rstrip('/')}/api/salud", timeout=20) as response:
        health = json.load(response)
    if health.get("estado") != "ok" or health.get("modo_prueba") is not True:
        raise RuntimeError("Qolqe no está sano o no tiene habilitado QOLQE_MODO_PRUEBA=1.")
    request = Request(f"{base_url.rstrip('/')}/api/pruebas/reiniciar", data=b"", method="POST")
    with urlopen(request, timeout=90) as response:
        if response.status != 200:
            raise RuntimeError(f"No se pudieron reiniciar los datos: HTTP {response.status}.")
