"""Lleva la evidencia de la Parte 3 (rendimiento) al sitio de GitHub Pages.

Las corridas de rendimiento no se ejecutan en el pipeline (necesitan el equipo libre y Docker con 1 CPU), así que
su evidencia está versionada en tests/performance/resultados/. Este script la copia a sitio/rendimiento/ y escribe
sitio/rendimiento/index.html con el veredicto por umbral, el resumen por escenario y los enlaces a cada reporte.

Solo biblioteca estándar: el job `reportes` del pipeline no instala dependencias.
"""
import argparse
import csv
import html
import json
import re
import shutil
import sys
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
from trazabilidad import pagina, tabla_html

ESCENARIOS = ["referencia", "calibracion", "carga", "pico", "estres", "escalabilidad", "resistencia", "demo"]
# Del comparativo se publica el gráfico y las tablas en crudo, para que el profesor pueda abrir los datos.
ARCHIVOS_COMPARATIVO = ["G11_comparativo.png", "resumen_escenarios.csv", "veredictos.csv", "veredictos.md"]
# De cada corrida, solo lo que se ve en un navegador. Los .gz (muestras, peticiones, métricas, log) son megas de datos crudos.
ARCHIVOS_CORRIDA = ["reporte.html", "veredicto.csv", "veredicto.md", "tabla_resumen.csv", "resumen.json"]
# Los gráficos del informe (G1 a G5, más los propios de cada escenario). reporte.html es el panel de k6, en inglés.
EMBEBIDOS = ["G1_tiempo_respuesta.png", "G2_throughput.png"]
MARCA = re.compile(r"^\d{8}-\d{4}$")
# Rutas absolutas del equipo de medición dentro de los .json: no se pueden publicar (exponen el usuario del sistema
# y la copia de trabajo). Se dejan con el nombre del archivo. No toca URLs (http://127.0.0.1:8090 no coincide).
RUTA_LOCAL = re.compile(r"/(?:Users|home|root|private|var|tmp|opt|Volumes|mnt|srv)/[^\s\"']*")
# veredictos.csv guarda el veredicto en seco; el comparativo en Markdown lo muestra con símbolo y la celda vacía como raya.
SIMBOLOS = {"PASA": "✓ PASA", "FALLA": "✗ FALLA", "": "—"}
# Clases de ESTILO (trazabilidad.py) para colorear el veredicto: .passed verde, .failed rojo, .xfailed ámbar, .sin gris.
CLASES = {"✓ PASA": "passed", "✗ FALLA": "failed", "MEDIDO": "xfailed", "NO APLICA": "skipped", "—": "sin"}
# El nav lleva solo páginas: la portada y la matriz (las escribe trazabilidad.py en el mismo job, después de este script).
NAV = ('<nav><a href="../index.html">Volver a la portada</a>'
       '<a href="../trazabilidad.md">Matriz en Markdown</a></nav>')
CRUDOS = ["veredictos.md", "veredictos.csv", "resumen_escenarios.csv"]
COLUMNAS_RESUMEN = ["Escenario", "Corrida", "Medido en", "Peticiones", "p95 consulta (ms)", "p95 dinero (ms)",
                    "Error rend. (%) ≤ 1 % (U-03)", "Error datos (%)", "Throughput máx. (req/s)", "Simultáneos máx.",
                    "CPU Qolqe máx. (%)", "RSS máx. (MB)", "CPU equipo máx. (%)", "Capacidad U-08"]
NOTA_VEREDICTO = ("«NO APLICA» significa que ese umbral no se evalúa en ese escenario (cada escenario cubre los suyos, "
                  "ver docs/diseno-rendimiento.md §2.1 «Tabla de umbrales»). «MEDIDO» es U-08: la capacidad no pasa ni "
                  "falla, se mide. V-06 falla solo en referencia y solo en el login (92 ms con 1 VU frente al límite de "
                  "80 ms); está declarado como limitación en docs/informe.md. La columna «referencia» va como contexto y "
                  "no como escenario analizado: su propio veredicto.md la declara «Corrida NO válida: se repite y no se "
                  "analiza (paso 1 de S14)». La capacidad U-08 de 850 usuarios lleva la salvedad del informe: «el estrés "
                  "lo cortó la red de seguridad técnica de k6 (20 % de operaciones fallidas acumulado desde el inicio, no "
                  "es un umbral del SLA) antes de la meseta».")


def ultima_corrida(carpeta: Path) -> Path | None:
    """La subcarpeta con la marca de tiempo más alta (AAAAMMDD-HHMM). 'descartadas' queda fuera por no estar en ESCENARIOS."""
    marcas = sorted(p for p in carpeta.iterdir() if p.is_dir() and MARCA.match(p.name))
    return marcas[-1] if marcas else None


def sin_rutas(valor: object) -> object:
    """Deja cualquier ruta absoluta del equipo con solo el nombre del archivo, en todo el JSON (no solo en un campo)."""
    if isinstance(valor, str):
        return RUTA_LOCAL.sub(lambda m: PurePosixPath(m.group()).name, valor)
    if isinstance(valor, dict):
        return {sin_rutas(k): sin_rutas(v) for k, v in valor.items()}
    if isinstance(valor, list):
        return [sin_rutas(v) for v in valor]
    return valor


def copiar(origen: Path, destino: Path) -> bool:
    """Copia un archivo de evidencia. Los .json se sanean antes: el sitio es público y traen rutas del equipo."""
    if not origen.is_file():
        return False
    destino.parent.mkdir(parents=True, exist_ok=True)
    if origen.suffix == ".json":
        crudo = origen.read_text(encoding="utf-8")
        try:
            texto = json.dumps(sin_rutas(json.loads(crudo)), ensure_ascii=False)
        except ValueError:  # JSON ilegible: igual se publica sin las rutas, pero no se reescribe
            texto = RUTA_LOCAL.sub(lambda m: PurePosixPath(m.group()).name, crudo)
        destino.write_text(texto, encoding="utf-8")
    else:
        shutil.copy(origen, destino)
    return True


def numero(valor: str, decimales: int = 0) -> str:
    """Igual que el comparativo en Markdown: separador de miles y sin decimales de más. Vacío es una raya."""
    try:
        return f"{float(valor):,.{decimales}f}"
    except (TypeError, ValueError):
        return "—"


def colorear(tabla: str) -> str:
    """Pone la clase de color en las celdas de veredicto, sin quitarles el texto («✓ PASA» sigue leyéndose).

    Se hace sobre la tabla ya armada porque clase() de trazabilidad.py solo reconoce los estados de pytest
    (passed, failed, …), no los veredictos de rendimiento; así se reutiliza tabla_html y ESTILO sin tocarlos.
    """
    for texto, clase in CLASES.items():
        tabla = tabla.replace(f"<td>{texto}</td>", f'<td class="{clase}">{texto}</td>')
    return tabla


def leer_veredictos(ruta: Path) -> tuple[list[str], list[list[str]], list[list[str]]]:
    """Separa las filas U-xx (umbrales del requerimiento) de las V-xx (validez de la medición)."""
    with ruta.open(encoding="utf-8") as f:
        filas = list(csv.reader(f))
    if not filas:
        return [], [], []
    cabecera = ["ID", "Criterio", *filas[0][2:]]

    def convertir(fila: list[str]) -> list[str]:
        return [fila[0], fila[1], *[SIMBOLOS.get(v, v) for v in fila[2:]]]
    umbrales = [convertir(f) for f in filas[1:] if f and f[0].startswith("U-")]
    validez = [convertir(f) for f in filas[1:] if f and f[0].startswith("V-")]
    return cabecera, umbrales, validez


def leer_resumen(ruta: Path) -> list[list[str]]:
    """Las mismas columnas que comparativo/veredictos.md. Con r.get: renombrar una columna no debe tumbar el job."""
    with ruta.open(encoding="utf-8") as f:
        filas = list(csv.DictReader(f, restval=""))
    return [[r.get("escenario", ""), r.get("marca", ""), r.get("subconjunto", ""),
             numero(r.get("peticiones", "")), numero(r.get("p95_consulta_ms", "")), numero(r.get("p95_dinero_ms", "")),
             numero(r.get("error_rendimiento_%", ""), 2), numero(r.get("error_datos_%", ""), 2),
             numero(r.get("throughput_max_req_s", "")), numero(r.get("usuarios_simultaneos_max", "")),
             numero(r.get("cpu_qolqe_max_%", ""), 2), numero(r.get("rss_qolqe_max_MB", "")),
             numero(r.get("cpu_equipo_max_%", ""), 2), numero(r.get("capacidad_U08", ""))] for r in filas]


def linea_entorno(ruta: Path, marcas: list[str]) -> str:
    """Qué se midió y cuándo, leído de entorno/entorno.json (lo escribe correr.sh en cada corrida)."""
    fechas = sorted({m[:8] for m in marcas})
    dia = f"{fechas[0][6:8]}-{fechas[0][4:6]}-{fechas[0][:4]}" if fechas else "sin corridas"
    rango = f" ({marcas[0]} … {marcas[-1]})" if marcas else ""
    try:
        e = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return f"Qolqe en Docker con 1 CPU y 1 GB; k6 como generador de carga. Corridas del {dia}{rango}."
    limites, equipo = e.get("limites_qolqe", {}), e.get("equipo", {})
    memoria = limites.get("memoria", "1g").replace("g", " GB").replace("m", " MB")
    return (f"Qolqe en Docker con {limites.get('cpus', '1')} CPU y {memoria} de memoria "
            f"(imagen {e.get('imagen', {}).get('nombre', 'qolqe-perf')}), sobre {equipo.get('modelo', 'el equipo de medición')} "
            f"/ {equipo.get('cpu', '')} con {equipo.get('nucleos', '?')} núcleos; generador de carga {e.get('k6', 'k6')}. "
            f"Corridas del {dia}{rango}.")


def linea_crudos(destino: Path) -> str:
    """Los archivos de datos del comparativo, en una línea y solo los que se copiaron (no son páginas del nav)."""
    enlaces = [f'<a href="{n}">{html.escape(n)}</a>' for n in CRUDOS if (destino / n).is_file()]
    return f"<p><small>Datos en crudo: {' · '.join(enlaces)}</small></p>" if enlaces else ""


def titulo_grafico(nombre: str) -> str:
    """'G4_usuarios_simultaneos.png' → 'G4 usuarios simultaneos', para el alt y el texto del enlace."""
    return Path(nombre).stem.replace("_", " ")


def bloques_escenario(corridas: dict[str, list[str]], graficos: dict[str, list[str]]) -> str:
    """Un bloque por escenario: sus archivos, G1 y G2 embebidos y el resto de gráficos como enlaces."""
    partes = []
    for escenario, archivos in corridas.items():
        enlaces = " · ".join(f'<a href="{a}">{html.escape(Path(a).name)}</a>' for a in archivos)
        partes.append(f"<h3>{html.escape(escenario)}</h3><p>{enlaces}</p>")
        propios = graficos.get(escenario, [])
        embebidos = [g for g in propios if Path(g).name in EMBEBIDOS]
        if embebidos:
            partes.append("<p>" + "".join(
                f'<img src="{g}" alt="{html.escape(titulo_grafico(g))} de {html.escape(escenario)}"'
                ' style="max-width:min(100%,520px);height:auto;margin:4px 8px 4px 0">' for g in embebidos) + "</p>")
        resto = [g for g in propios if Path(g).name not in EMBEBIDOS]
        if resto:
            mas = " · ".join(f'<a href="{g}">{html.escape(titulo_grafico(g))}</a>' for g in resto)
            partes.append(f"<p><small>Más gráficos: {mas}</small></p>")
    return "".join(partes)


def escribir_index(destino: Path, resultados: Path, corridas: dict[str, list[str]], graficos: dict[str, list[str]],
                   marcas: list[str]) -> None:
    cuerpo = [f"<h1>Qolqe · Parte 3 · Pruebas de rendimiento</h1><p>{html.escape(linea_entorno(resultados / 'entorno' / 'entorno.json', marcas))}</p>",
              NAV, linea_crudos(destino)]

    veredictos = destino / "veredictos.csv"
    if veredictos.exists():
        # Sin veredictos.csv el sitio se publica sin estas dos tablas: morir aquí tumbaría todo el job de reportes.
        cabecera, umbrales, validez = leer_veredictos(veredictos)
        if umbrales:
            cuerpo.append('<h2>Veredicto por umbral y escenario (U-01 a U-09)</h2>'
                          f'<div class="tabla">{colorear(tabla_html(cabecera, umbrales))}</div>')
            cuerpo.append(f"<p><small>{html.escape(NOTA_VEREDICTO)}</small></p>")
        if validez:
            cuerpo.append('<h2>Comprobaciones de validez de la medición (V-01 a V-07)</h2>'
                          f'<div class="tabla">{colorear(tabla_html(cabecera, validez))}</div>')

    resumen = destino / "resumen_escenarios.csv"
    if resumen.exists():
        cuerpo.append(f'<h2>Resumen por escenario</h2><div class="tabla">{tabla_html(COLUMNAS_RESUMEN, leer_resumen(resumen))}</div>')

    if (destino / "G11_comparativo.png").exists():
        cuerpo.append('<h2>Comparativo de los ocho escenarios (G11)</h2>'
                      '<p><img src="G11_comparativo.png" alt="G11: comparativo de p95, throughput y usuarios simultáneos por escenario"'
                      ' style="max-width:100%;height:auto"></p>')

    if corridas:
        cuerpo.append(f"<h2>Evidencia por escenario</h2>{bloques_escenario(corridas, graficos)}"
                      "<p><small>G1 a G5 (y los propios de cada escenario) son los gráficos del informe; cada "
                      "<code>reporte.html</code> es el panel de k6 de la última corrida del escenario. "
                      "Las muestras en crudo (<code>muestras.csv.gz</code>, <code>peticiones.csv.gz</code>) no se publican por tamaño: "
                      "están en <code>tests/performance/resultados/</code> del repositorio.</small></p>")

    (destino / "index.html").write_text(pagina("Qolqe · Parte 3 · Rendimiento", "".join(cuerpo)), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sitio", required=True, type=Path, help="Carpeta del sitio de GitHub Pages")
    parser.add_argument("--resultados", default=Path("tests/performance/resultados"), type=Path,
                        help="Carpeta con la evidencia de rendimiento versionada en el repo")
    args = parser.parse_args()

    if not args.resultados.is_dir():
        # Un clon sin la evidencia (o un run que no la descargó) no debe romper la publicación del sitio.
        print(f"Rendimiento: no existe {args.resultados}; el sitio se publica sin la Parte 3.")
        return

    destino = args.sitio / "rendimiento"
    destino.mkdir(parents=True, exist_ok=True)
    copiados = 0
    for nombre in ARCHIVOS_COMPARATIVO:
        if copiar(args.resultados / "comparativo" / nombre, destino / nombre):
            copiados += 1

    corridas: dict[str, list[str]] = {}
    graficos: dict[str, list[str]] = {}
    marcas: list[str] = []
    for escenario in ESCENARIOS:
        carpeta = args.resultados / escenario
        corrida = ultima_corrida(carpeta) if carpeta.is_dir() else None
        if corrida is None:
            print(f"::warning::Rendimiento: {escenario} no tiene corridas en {carpeta}")
            continue
        marcas.append(corrida.name)
        for nombre in ARCHIVOS_CORRIDA:
            if copiar(corrida / nombre, destino / escenario / nombre):
                corridas.setdefault(escenario, []).append(f"{escenario}/{nombre}")
                copiados += 1
        # Los gráficos del informe. Una corrida sin carpeta graficos/ simplemente no aporta ninguno.
        for png in sorted((corrida / "graficos").glob("*.png")) if (corrida / "graficos").is_dir() else []:
            if copiar(png, destino / escenario / "graficos" / png.name):
                graficos.setdefault(escenario, []).append(f"{escenario}/graficos/{png.name}")
                copiados += 1

    if not copiados and not corridas:
        # Sin nada que publicar, la carpeta se borra: la portada enlaza rendimiento/ solo si existe, y así no deja un 404.
        shutil.rmtree(destino)
        print("::warning::Rendimiento: no se copió ningún archivo; el sitio se publica sin la Parte 3.")
        return

    escribir_index(destino, args.resultados, corridas, graficos, sorted(marcas))
    peso = sum(p.stat().st_size for p in destino.rglob("*") if p.is_file())
    print(f"Rendimiento: {copiados} archivos copiados de {len(corridas)} escenarios; "
          f"{destino}/ pesa {peso:,} bytes ({peso / 1_048_576:.1f} MB) con index.html incluido.")


if __name__ == "__main__":
    main()
