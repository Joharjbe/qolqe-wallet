"""Arma el conjunto de oro con el que se mide la capacidad de IA (punto 8 de la entrega).

Lee los artefactos que ya produce el proyecto (el JUnit por caso de `trazabilidad.py`, los
`.feature` y `docs/defectos.md`) y escribe `conjunto_oro.json`: por cada fallo, la ENTRADA que
verá el componente y la ETIQUETA correcta con su FUENTE (archivo y línea).

Dos reglas que gobiernan todo el script:

1. Lo real se lee del repositorio; nada se inventa. Los casos escritos a mano (reconstruidos a
   partir de lo documentado o sembrados) viven en `casos_escritos.json` y quedan marcados.
2. La entrada no puede traer la respuesta. El JUnit marca los fallos conocidos como
   `xfailed` y les pone la propiedad `defecto` y el mensaje "Defecto conocido DEF-xx
   (fallo esperado)": eso es una FUGA y el conjunto no mediría nada. Aquí se quita y
   `revisar_fugas` falla si algún rastro vuelve a entrar.

Uso:
    python tests/diagnostico/conjunto_oro/armar.py --junit reportes/junit-cp.xml
    python tests/diagnostico/conjunto_oro/armar.py --junit reportes/junit-cp.xml --verificar
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parents[2]
CLASES = ("defecto_real", "prueba_inestable", "error_entorno")

# Las 13 claves de la entrada: las que fija el contrato de lectura.py. Ni una más.
CLAVES_ENTRADA = (
    "caso", "titulo", "hu", "ca", "modulo", "nivel", "tipo",
    "estado", "ejecuciones", "archivo", "defecto_declarado", "mensaje", "salida",
)

# Lo que no puede aparecer dentro de una entrada. Cada patrón con el motivo que se explica en el README.
FUGAS = (
    (r"DEF-\d{2}", "trae el identificador del defecto, que es parte de la respuesta"),
    (r"(?i)defecto conocido", "es el mensaje con que el JUnit marca un fallo esperado"),
    (r"(?i)\bsembrad", "delataría que el caso fue construido a mano"),
    (r"(?i)conjunto de oro|etiqueta correcta", "habla del propio conjunto"),
    (r"defecto_real|prueba_inestable|error_entorno", "nombra una de las clases"),
    # /home/runner es la del runner de GitHub, no la de nadie: esa sí puede aparecer.
    (r"/Users/|/home/(?!runner\b)[a-z]|[A-Z]:\\\\", "trae una ruta local (privacidad)"),
)

# Dónde empieza otro escenario: ahí se corta el bloque de Gherkin. La línea de etiquetas lleva
# @DEF-xx y el comentario anterior puede nombrar el defecto, así que ninguno de los dos entra.
CORTES = ("@", "#", "Escenario", "Esquema", "Característica", "Antecedentes")


def leer_defectos(repo: Path) -> dict[str, dict]:
    """{'DEF-01': {'titulo': ..., 'linea': n}} desde los encabezados de docs/defectos.md."""
    ruta = repo / "docs" / "defectos.md"
    defectos = {}
    for n, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), start=1):
        m = re.match(r"^## (DEF-\d{2}): (.+)$", linea)
        if m:
            defectos[m.group(1)] = {"titulo": m.group(2).strip(), "linea": n}
    if not defectos:
        raise SystemExit(f"No se encontró ningún defecto en {ruta}")
    return defectos


def leer_escenario(repo: Path, archivo: str, linea: int,
                   quitar: tuple[str, ...] = (), cambios: dict[str, str] | None = None) -> list[str]:
    """El bloque Gherkin que empieza en `archivo:linea`, sin la línea de etiquetas ni comentarios."""
    lineas = (repo / archivo).read_text(encoding="utf-8").splitlines()
    cambios = cambios or {}
    bloque = []
    for i, texto in enumerate(lineas[linea - 1:]):
        pelado = texto.strip()
        if i and (not pelado or pelado.startswith(CORTES)):
            if not pelado:
                continue
            break
        if pelado in quitar:
            continue
        if pelado in cambios:
            texto = texto[: len(texto) - len(texto.lstrip())] + cambios[pelado]
        bloque.append(texto.rstrip())
    while bloque and not bloque[-1].strip():
        bloque.pop()
    return bloque


def leer_junit(ruta: Path) -> dict:
    """Los <testcase> del JUnit por caso, con sus propiedades y sus líneas de ejecución."""
    raiz = ET.parse(ruta).getroot()
    casos = {}
    for nodo in raiz.iter("testcase"):
        props = {p.get("name"): p.get("value") for p in nodo.iter("property")}
        nombre = nodo.get("name") or ""
        id_caso = nombre.split(" ", 1)[0]
        titulo = nombre.split(" ", 1)[1] if " " in nombre else ""
        salida = (nodo.findtext("system-out") or "").strip().splitlines()
        casos[id_caso] = {
            "caso": id_caso,
            "titulo": titulo,
            "props": props,
            "ejecuciones": [linea.split(": ", 1)[1] for linea in salida if ": " in linea],
        }
    datos = ruta.read_bytes()
    conteo: dict[str, int] = {}
    for c in casos.values():
        estado = c["props"].get("estado", "?")
        conteo[estado] = conteo.get(estado, 0) + 1
    return {
        "archivo": ruta.name,
        "nombre_run": raiz.get("name", ""),
        "casos_en_el_run": len(casos),
        "por_estado": dict(sorted(conteo.items())),
        "sha256": hashlib.sha256(datos).hexdigest(),
        "casos": casos,
    }


def construir_entrada(
    caso: dict,
    repo: Path,
    *,
    estado: str,
    pasaron: int,
    detalle: str = "",
    log: str = "",
    quitar_pasos: tuple[str, ...] = (),
    cambiar_pasos: dict[str, str] | None = None,
    con_lineas: bool = True,
) -> dict:
    """La entrada tal como la vería alguien que no sabe la respuesta.

    `mensaje` y las líneas de `salida` usan las mismas palabras que escribe `trazabilidad.py`
    para un caso que falla, no las del fallo esperado.
    """
    props = caso["props"]
    total = int(props.get("ejecuciones", "0/0").split("/")[1])
    fallaron = max(total - pasaron, 0)
    if estado == "flaky":
        mensaje = f"Inestable: falló {fallaron} de {total} ejecuciones"
    elif estado == "failed":
        mensaje = f"Fallaron {fallaron} de {total} ejecuciones"
    else:
        mensaje = f"{estado} en este run"

    lineas = []
    if con_lineas:
        for i, nombre in enumerate(caso["ejecuciones"]):
            marca = "failed" if i < fallaron else "passed"
            lineas.append(f"{marca}: {nombre}" + (f" {detalle}" if marca == "failed" and detalle else ""))
    partes = ["\n".join(lineas)] if lineas else []

    archivo = props.get("archivo", "")
    if archivo and ":" in archivo:
        ruta, numero = archivo.rsplit(":", 1)
        bloque = leer_escenario(repo, ruta, int(numero), quitar_pasos, cambiar_pasos)
        partes.append(f"Escenario en {archivo}\n" + "\n".join(bloque))
    if log:
        partes.append(log.strip("\n"))

    return {
        "caso": caso["caso"],
        "titulo": caso["titulo"],
        "hu": props.get("hu", ""),
        "ca": props.get("ca", ""),
        "modulo": props.get("modulo", ""),
        "nivel": props.get("nivel", ""),
        "tipo": props.get("tipo", ""),
        "estado": estado,
        "ejecuciones": f"{pasaron}/{total}",
        "archivo": archivo,
        # Redactado a propósito: el JUnit trae aquí el @DEF-xx del .feature y sería la respuesta.
        "defecto_declarado": None,
        "mensaje": mensaje,
        "salida": "\n\n".join(p for p in partes if p),
    }


def armar_reales(junit: dict, repo: Path, defectos: dict, extras: dict | None = None) -> list[dict]:
    """Un registro por cada fallo conocido del run: los `xfailed` con su propiedad `defecto`."""
    extras = extras or {}
    registros = []
    for id_caso, caso in sorted(junit["casos"].items(), key=lambda kv: clave_orden(kv[0])):
        props = caso["props"]
        if props.get("estado") != "xfailed":
            continue
        defs = [d.strip() for d in props.get("defecto", "").split(",") if d.strip()]
        if len(defs) != 1:
            raise SystemExit(f"{id_caso}: se esperaba un solo defecto declarado, hay {defs}")
        defecto = defs[0]
        if defecto not in defectos:
            raise SystemExit(f"{id_caso}: {defecto} no está en docs/defectos.md")
        extra = extras.get(id_caso, {})
        entrada = construir_entrada(caso, repo, estado="failed", pasaron=0, log=extra.get("log", ""))
        registros.append({
            "entrada": entrada,
            "etiqueta": {"clase": "defecto_real", "defecto": defecto},
            "fuente": extra.get("fuente", []) + [
                {
                    "archivo": "docs/defectos.md",
                    "linea": defectos[defecto]["linea"],
                    "cita": f"## {defecto}: {defectos[defecto]['titulo']}",
                },
                {
                    "archivo": junit["archivo"],
                    "en_el_repo": False,
                    "linea": None,
                    "cita": f'<testcase name="{id_caso} {caso["titulo"]}"> con estado=xfailed y defecto={defecto}',
                },
            ],
            "procedencia": {
                "origen": "artefacto",
                "sembrado": False,
                "artefactos": [junit["archivo"], props.get("archivo", "")],
                "redacciones": [
                    "estado: xfailed → failed",
                    "defecto_declarado: la propiedad `defecto` del JUnit se puso en null",
                    'mensaje: "Defecto conocido …" → el mensaje de un caso que falla',
                    "salida: el prefijo xfailed de cada ejecución pasó a failed",
                    "escenario: la línea de etiquetas (@DEF-xx) queda fuera del bloque",
                ],
            },
            "grupo_oro": None,
            "nota": extra.get("nota") or (
                f"El escenario afirma lo que {defecto} incumple; el producto es el que falla. "
                "La etiqueta lleva el DEF porque el componente tiene que proponerlo."
            ),
        })
    return registros


def aplicar_escritos(ruta: Path, junit: dict, repo: Path, defectos: dict) -> tuple[list[dict], list[dict]]:
    """Los casos escritos a mano: reconstruidos de lo documentado o sembrados, siempre marcados."""
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    registros = []
    for escrito in datos["casos"]:
        base = escrito.get("entrada", {})
        if "hereda_de" in escrito:
            id_caso = escrito["hereda_de"]
            caso = junit["casos"].get(id_caso)
            if caso is None:
                raise SystemExit(f"{escrito['clave']}: {id_caso} no está en el JUnit")
            entrada = construir_entrada(
                caso, repo,
                estado=escrito["estado"],
                pasaron=escrito.get("pasaron", 0),
                detalle=escrito.get("detalle", ""),
                log=escrito.get("log", ""),
                quitar_pasos=tuple(escrito.get("quitar_pasos", [])),
                cambiar_pasos=escrito.get("cambiar_pasos"),
                con_lineas=escrito.get("con_lineas", True),
            )
            entrada.update(base)
        else:
            faltan = set(CLAVES_ENTRADA) - set(base)
            if faltan:
                raise SystemExit(f"{escrito['clave']}: falta en la entrada {sorted(faltan)}")
            entrada = {k: base[k] for k in CLAVES_ENTRADA}
        defecto = escrito["etiqueta"].get("defecto")
        if defecto and defecto not in defectos:
            raise SystemExit(f"{escrito['clave']}: {defecto} no está en docs/defectos.md")
        registros.append({
            "entrada": entrada,
            "etiqueta": escrito["etiqueta"],
            "fuente": escrito["fuente"],
            "procedencia": escrito["procedencia"],
            "grupo_oro": escrito.get("grupo_oro"),
            "nota": escrito["nota"],
        })
    return registros, datos.get("casos_fuera", [])


def clave_orden(id_caso: str) -> tuple:
    m = re.match(r"CP-([A-Z]+)(\d+)", id_caso)
    return (m.group(1), int(m.group(2))) if m else (id_caso, 0)


def normalizar(texto: str) -> str:
    return re.sub(r"\s+", " ", texto).strip()


def revisar_fuentes(registros: list[dict], repo: Path) -> list[str]:
    """Comprueba que cada cita esté de verdad en el archivo y en la línea que dice.

    Es la revisión que hace creíble al conjunto: una etiqueta sin fuente comprobable no sirve
    de verdad de referencia. Se acepta una ventana de 4 líneas porque algunas citas resumen
    un bloque (una tabla, un objeto de configuración).
    """
    problemas = []
    for reg in registros:
        for fuente in reg["fuente"]:
            if not fuente.get("en_el_repo", True):
                continue
            ruta = repo / fuente["archivo"]
            if not ruta.exists():
                problemas.append(f"{reg['id']}: no existe {fuente['archivo']}")
                continue
            if fuente.get("linea") is None:
                continue
            lineas = ruta.read_text(encoding="utf-8").splitlines()
            n = fuente["linea"]
            ventana = normalizar(" ".join(lineas[max(n - 1, 0): n + 4]))
            aguja = normalizar(fuente["cita"])[:40]
            if aguja not in ventana:
                problemas.append(f"{reg['id']}: la cita no está en {fuente['archivo']}:{n} ({aguja!r})")
    return problemas


def revisar_fugas(registros: list[dict]) -> list[str]:
    """Falla si la entrada trae algún rastro de la respuesta o una ruta local."""
    problemas = []
    for reg in registros:
        entrada = reg["entrada"]
        id_oro = reg["id"]
        if sorted(entrada) != sorted(CLAVES_ENTRADA):
            problemas.append(f"{id_oro}: la entrada no tiene las {len(CLAVES_ENTRADA)} claves del contrato")
        if entrada["defecto_declarado"] is not None:
            problemas.append(f"{id_oro}: defecto_declarado tiene que ir en null")
        texto = "\n".join(str(v) for v in entrada.values())
        for patron, motivo in FUGAS:
            hallado = re.search(patron, texto)
            if hallado:
                problemas.append(f"{id_oro}: la entrada dice {hallado.group(0)!r} y {motivo}")
    return problemas


def revisar_conjunto(registros: list[dict]) -> list[str]:
    problemas = []
    vistos = set()
    for reg in registros:
        if reg["id"] in vistos:
            problemas.append(f"{reg['id']}: identificador repetido")
        vistos.add(reg["id"])
        if reg["etiqueta"]["clase"] not in CLASES:
            problemas.append(f"{reg['id']}: clase desconocida {reg['etiqueta']['clase']!r}")
        if not reg["fuente"]:
            problemas.append(f"{reg['id']}: sin fuente de la etiqueta")
    return problemas


def armar(repo: Path, ruta_junit: Path) -> dict:
    defectos = leer_defectos(repo)
    junit = leer_junit(ruta_junit)
    escritos_raw = json.loads((AQUI / "casos_escritos.json").read_text(encoding="utf-8"))
    reales = armar_reales(junit, repo, defectos, escritos_raw.get("logs_reales"))
    escritos, fuera = aplicar_escritos(AQUI / "casos_escritos.json", junit, repo, defectos)
    registros = reales + escritos
    for i, reg in enumerate(registros, start=1):
        reg["id"] = f"ORO-{i:02d}"
        reg_ordenado = {k: reg[k] for k in ("id", "entrada", "etiqueta", "fuente", "procedencia", "grupo_oro", "nota")}
        reg.clear()
        reg.update(reg_ordenado)

    problemas = revisar_conjunto(registros) + revisar_fugas(registros) + revisar_fuentes(registros, repo)
    if problemas:
        raise SystemExit("El conjunto no pasa sus propias revisiones:\n- " + "\n- ".join(problemas))

    por_clase: dict[str, int] = {c: 0 for c in CLASES}
    for reg in registros:
        por_clase[reg["etiqueta"]["clase"]] += 1
    por_origen: dict[str, int] = {}
    for reg in registros:
        origen = reg["procedencia"]["origen"]
        por_origen[origen] = por_origen.get(origen, 0) + 1
    defs = sorted({reg["etiqueta"]["defecto"] for reg in registros if reg["etiqueta"]["defecto"]})

    run = {k: v for k, v in junit.items() if k != "casos"}
    return {
        "version": 1,
        "armado_por": "tests/diagnostico/conjunto_oro/armar.py",
        "como_se_rearma": "python tests/diagnostico/conjunto_oro/armar.py --junit <ruta>/junit-cp.xml",
        "run_fuente": run,
        "regla_de_clase": {
            "defecto_real": "el fallo lo causa el producto (Qolqe); la acción es enlazar o abrir el DEF",
            "prueba_inestable": "el fallo lo causa la prueba (espera que falta, carrera que no siempre se "
                                "reproduce); volver a correrla sin tocar nada puede dar otro resultado; la "
                                "acción es estabilizarla o retirarla",
            "error_entorno": "el fallo lo causa el entorno (servidor, puerto, base, dependencias, navegador) "
                             "y no dice nada del producto; la acción es arreglar el entorno y volver a correr",
        },
        "conteo": {
            "casos": len(registros),
            "por_clase": por_clase,
            "por_origen": por_origen,
            "sembrados": sum(1 for r in registros if r["procedencia"]["sembrado"]),
            "defectos_cubiertos": len(defs),
            "defectos_en_el_catalogo": len(defectos),
        },
        "defectos_cubiertos": defs,
        "casos_fuera": fuera,
        "casos": registros,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Arma el conjunto de oro de la capacidad de IA.")
    p.add_argument("--repo", type=Path, default=REPO, help="Raíz del repositorio")
    p.add_argument("--junit", type=Path, default=None, help="JUnit por caso (por defecto reportes/junit-cp.xml)")
    p.add_argument("--salida", type=Path, default=AQUI / "conjunto_oro.json")
    p.add_argument("--verificar", action="store_true", help="No escribe: compara con el JSON versionado")
    args = p.parse_args()

    ruta_junit = args.junit or args.repo / "reportes" / "junit-cp.xml"
    if not ruta_junit.exists():
        print(f"No está {ruta_junit}. Se genera con .github/scripts/trazabilidad.py o se baja del "
              f"artefacto 'trazabilidad' de un run (gh run download <id> -n trazabilidad).", file=sys.stderr)
        return 2

    conjunto = armar(args.repo, ruta_junit)
    texto = json.dumps(conjunto, ensure_ascii=False, indent=2) + "\n"

    if args.verificar:
        actual = args.salida.read_text(encoding="utf-8") if args.salida.exists() else ""
        # El run de origen cambia en cada corrida; se compara lo que importa: los casos.
        a = json.loads(actual)["casos"] if actual else None
        if a != conjunto["casos"]:
            print(f"{args.salida.name} no coincide con lo que arma el script. Rearmar sin --verificar.", file=sys.stderr)
            return 1
        print(f"{args.salida.name}: {conjunto['conteo']['casos']} casos, iguales a los que arma el script.")
        return 0

    args.salida.write_text(texto, encoding="utf-8")
    c = conjunto["conteo"]
    print(f"{args.salida}: {c['casos']} casos "
          f"({', '.join(f'{k}={v}' for k, v in c['por_clase'].items())}; sembrados={c['sembrados']}) "
          f"sobre {c['defectos_cubiertos']} de {c['defectos_en_el_catalogo']} defectos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
