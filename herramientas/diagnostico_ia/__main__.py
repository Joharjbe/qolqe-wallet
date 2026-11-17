"""Línea de comandos del diagnóstico.

  python -m herramientas.diagnostico_ia --run <carpeta> --modelo <backend> --salida <carpeta>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import diagnostico, modelo

AYUDA = """Lee los artefactos de un run del pipeline (el JUnit por caso y los logs), agrupa los fallos
parecidos con una firma determinista y, por cada grupo, propone si el fallo es un defecto real, una prueba
inestable o un error de entorno, con el DEF-xx que le corresponde. Escribe diagnostico.json y diagnostico.md.

LA IA NO DECIDE NADA. Este comando solo escribe un reporte: no cambia el veredicto del quality gate, no toca
ningún archivo del pipeline y no modifica ningún caso de prueba. La IA propone, el tester decide.

Backends (--modelo):
  lineabase  reglas deterministas, SIN IA. Es el control: si acierta lo mismo que el modelo, la IA no aporta.
  grabado    respuestas guardadas de una corrida real (reproducible, sin red). Se llenan con --grabar.
  anthropic  modelo de Anthropic por HTTPS. Necesita ANTHROPIC_API_KEY en el .env local.
  google     modelo de Google por HTTPS. Necesita GOOGLE_API_KEY en el .env local.

Si falta la clave, el comando falla con un mensaje claro: nunca inventa una respuesta."""


def main(argumentos: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(
        prog="python -m herramientas.diagnostico_ia",
        description=AYUDA,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    analizador.add_argument("--run", required=True, type=Path,
                            help="Carpeta con los artefactos del run (junit-cp.xml o los junit.xml de cada job)")
    analizador.add_argument("--modelo", default="lineabase", choices=modelo.BACKENDS,
                            help="Backend que clasifica (por defecto: lineabase, sin IA)")
    analizador.add_argument("--salida", type=Path,
                            help="Carpeta donde escribir diagnostico.json y diagnostico.md (si no, va a pantalla)")
    analizador.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2],
                            help="Raíz del repositorio, de donde salen docs/defectos.md y el .env")
    analizador.add_argument("--grabados", type=Path, default=Path(__file__).resolve().parent / "respuestas_grabadas",
                            help="Carpeta de respuestas grabadas que usa --modelo grabado")
    analizador.add_argument("--grabar", action="store_true",
                            help="Guarda en --grabados las respuestas REALES de anthropic o google")
    opciones = analizador.parse_args(argumentos)

    if not opciones.run.is_dir():
        print(f"error: no existe la carpeta del run: {opciones.run}", file=sys.stderr)
        return 2
    try:
        resultado = diagnostico.diagnosticar(
            opciones.run,
            backend=opciones.modelo,
            raiz_repo=opciones.repo,
            carpeta_grabados=opciones.grabados,
            grabar=opciones.grabar,
        )
    except (FileNotFoundError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if opciones.salida:
        ruta_json, ruta_md = diagnostico.escribir(resultado, opciones.salida)
        totales = resultado["totales"]
        print(f"{totales['fallos']} fallos ({totales['casos_distintos']} casos) · {totales['grupos']} grupos · "
              f"{totales['clasificados']} clasificados · {totales['rechazados_por_guardas']} rechazados por las "
              f"guardas · {totales['errores_del_backend']} errores del backend")
        print(f"escritos: {ruta_json}\n          {ruta_md}")
    else:
        print(diagnostico.a_markdown(resultado))
    # Un rechazo no es un fallo del comando: es un dato del reporte. El código de
    # salida solo distingue si el diagnóstico se pudo escribir.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
