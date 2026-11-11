"""Gráficos G1 a G11 del diseño (§7.2). Antes de dibujar, analiza la corrida (veredicto y tablas, ver analizar.py).

Uso:
  .venv/bin/python tests/performance/analisis/graficos.py <carpeta_corrida> [<carpeta_corrida> …]
  .venv/bin/python tests/performance/analisis/graficos.py --todo [--resultados tests/performance/resultados]

--todo analiza y dibuja todas las corridas de resultados/<escenario>/<marca>/ (salvo entorno/, comparativo/ y descartadas/)
y escribe resultados/comparativo/ con G11, veredictos.md/.csv y resumen_escenarios.csv usando la última corrida de cada escenario.
Cada corrida deja sus PNG en <carpeta_corrida>/graficos/.
"""
import argparse
import sys
import traceback
from pathlib import Path

import comparativo
import estilo
from analizar import Analisis, analizar, linea_resumen
from graficos_estres import g6_p95_vs_usuarios, g7_throughput_vs_usuarios, g8_cpu_vs_usuarios
from graficos_resistencia import g9_memoria_vs_sesiones, g10_hilos_descriptores
from graficos_tiempo import g1_tiempo_respuesta, g2_throughput, g3_errores, g4_usuarios, g5_recursos
from lectura import epoca, leer_json

RESULTADOS = Path(__file__).resolve().parent.parent / "resultados"
COMUNES = {"G1_tiempo_respuesta": g1_tiempo_respuesta, "G2_throughput": g2_throughput, "G3_errores": g3_errores,
           "G4_usuarios_simultaneos": g4_usuarios, "G5_recursos": g5_recursos}
POR_ESCENARIO = {
    "estres": {"G6_p95_vs_usuarios": g6_p95_vs_usuarios, "G7_throughput_vs_usuarios": g7_throughput_vs_usuarios,
               "G8_cpu_vs_usuarios": g8_cpu_vs_usuarios},
    "resistencia": {"G9_memoria_vs_sesiones": g9_memoria_vs_sesiones, "G10_hilos_descriptores": g10_hilos_descriptores},
}


def dibujar(a: Analisis) -> list[Path]:
    carpeta = a.corrida.carpeta / "graficos"
    carpeta.mkdir(exist_ok=True)
    escala = a.corrida.perfil.escala
    estilo.AVISO["texto"] = f"ensayo comprimido ×{escala:g}: no es evidencia" if escala != 1 else ""
    hechos = []
    for nombre, funcion in (COMUNES | POR_ESCENARIO.get(a.corrida.escenario, {})).items():
        ruta = carpeta / f"{nombre}.png"
        funcion(a, ruta)
        if ruta.exists():
            hechos.append(ruta)
    return hechos


def corridas(raiz: Path) -> dict[str, list[Path]]:
    """Carpetas resultados/<escenario>/<marca>/ con datos de k6, ordenadas por hora de inicio (la última al final)."""
    salida = {}
    for escenario in comparativo.ORDEN:
        base = raiz / escenario
        if not base.is_dir():
            continue
        lista = [d for d in base.iterdir() if d.is_dir() and (any(d.glob("muestras*.csv*")) or (d / "peticiones.csv.gz").exists())]
        lista.sort(key=lambda d: (epoca(leer_json(d / "corrida.json"), "inicio") or 0, d.name))
        if lista:
            salida[escenario] = lista
    return salida


def procesar(carpeta: Path) -> Analisis | None:
    try:
        a = analizar(carpeta)
        graficos = dibujar(a)
        print(f"{linea_resumen(a)}\n    {len(graficos)} gráficos en {a.corrida.carpeta / 'graficos'}")
        return a
    except Exception:   # noqa: BLE001 — una corrida rota no detiene a las demás (el error se muestra completo)
        print(f"ERROR en {carpeta}:\n{traceback.format_exc()}", file=sys.stderr)
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("carpetas", nargs="*", type=Path, help="carpetas resultados/<escenario>/<marca>/")
    parser.add_argument("--todo", action="store_true", help="todas las corridas y el comparativo")
    parser.add_argument("--resultados", type=Path, default=RESULTADOS, help="raíz de resultados (por defecto tests/performance/resultados)")
    args = parser.parse_args(argv)
    if not args.todo and not args.carpetas:
        parser.error("indique una o más carpetas de corrida, o --todo")
    errores = 0
    for carpeta in args.carpetas:
        errores += procesar(carpeta) is None
    if args.todo:
        ultimas = {}
        for escenario, lista in corridas(args.resultados).items():
            for carpeta in lista:
                a = procesar(carpeta)
                errores += a is None
                if a is not None:
                    ultimas[escenario] = a   # la lista va en orden: queda la última que se pudo analizar
        if ultimas:
            ensayos = sorted({f"×{a.corrida.perfil.escala:g}" for a in ultimas.values() if a.corrida.perfil.escala != 1})
            estilo.AVISO["texto"] = f"incluye ensayos comprimidos ({', '.join(ensayos)}): no es evidencia" if ensayos else ""
            comparativo.escribir(ultimas, args.resultados / "comparativo")
            print(f"Comparativo en {args.resultados / 'comparativo'}")
        else:
            print(f"No hay corridas en {args.resultados}")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
