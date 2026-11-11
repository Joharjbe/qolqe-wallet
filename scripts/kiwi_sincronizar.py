"""Importa las ejecuciones del pipeline de GitHub Actions en Kiwi TCMS: un TestRun por cada run de GitHub.

Modo pull: Kiwi corre en la máquina del equipo y los runners de GitHub no llegan a ella, así que este script
descarga con `gh` el artefacto `trazabilidad` de cada run (JUnit por CP, run.json y evidencias) y lo importa con
el plugin oficial kiwitcms-junit.xml-plugin. Los runs viejos (#1 a #15) solo tienen reportes-api y reportes-web:
con ellos se reconstruye el mismo JUnit por CP, con las etiquetas de los .feature de ese commit.

En Kiwi: producto "Qolqe Wallet", plan KIWI_PLAN_ID y build run-N (run-N.k si es un reintento) dentro de la
versión del plan, porque Kiwi solo acepta en un TestRun builds de esa versión; el commit va en el resumen del TestRun
y en la etiqueta commit:<sha7>. Cada caso es su CP ("CP-A01 <título>"); la HU va como requisito y etiqueta, cada DEF
como enlace de defecto en la ejecución y cada captura como adjunto de su ejecución. El reporte HTML de API no se
sube (Kiwi rechaza archivos con <html> o <script>): las notas del TestRun enlazan Pages y los artefactos del run.
Por defecto solo se importan los runs de main, los mismos que suma el historial de Pages (--rama "" importa todos).
Un run ya importado (etiqueta gh-run-<id>-<intento>) no se repite; uno que se cortó a la mitad (etiqueta
incompleto:gh-run-<id>-<intento>) se retoma en el mismo TestRun.

Uso (desde la raíz del repositorio):
  GH_TOKEN=$(gh auth token --user Joharjbe) python scripts/kiwi_sincronizar.py --simular --ultimos 20
  python scripts/kiwi_sincronizar.py --crear-plan
  GH_TOKEN=$(gh auth token --user Joharjbe) KIWI_PLAN_ID=1 python scripts/kiwi_sincronizar.py --ultimos 20
  python scripts/kiwi_sincronizar.py --desde-carpeta trazabilidad      (job gestion-casos del pipeline)
Kiwi se configura en ~/.tcms.conf (url, username, password); su certificado lo crea herramientas/kiwi/generar-certificado.sh.
"""
import argparse
import base64
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import xml.etree.ElementTree as ET
import xmlrpc.client
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / ".github" / "scripts"))
import trazabilidad
from casos import (
    CP_CONTRATO,
    caso_contrato,
    leer_casos,
    leer_defectos,
    leer_resultados,
    metadatos_run,
    normalizar_cp,
    resultados_por_caso,
)

PRODUCTO = "Qolqe Wallet"
NOMBRE_PLAN = "Qolqe · Pruebas automatizadas (entrega final)"
ESTADO_KIWI = {"passed": "PASSED", "failed": "FAILED", "flaky": "FAILED", "xfailed": "WAIVED", "skipped": "WAIVED",
               "sin ejecutar": "IDLE"}
LIMITE_ADJUNTO = 5 * 1024 * 1024  # FILE_UPLOAD_MAX_SIZE por defecto de Kiwi
ARTEFACTOS_VIEJOS = ("reportes-api", "reportes-web", "reportes-contrato")


# ---------- GitHub ----------

def entorno_gh() -> dict:
    """gh es un binario Go y también lee SSL_CERT_FILE: se le pasa el entorno sin el certificado de Kiwi."""
    return {k: v for k, v in os.environ.items() if k not in ("SSL_CERT_FILE", "REQUESTS_CA_BUNDLE")}


def gh(*argumentos: str) -> str:
    r = subprocess.run(["gh", *argumentos], env=entorno_gh(), capture_output=True, text=True, check=False)
    if r.returncode != 0:
        sys.exit(f"gh {' '.join(argumentos[:3])} falló: {r.stderr.strip()}")
    return r.stdout


def bajar_artefacto(repo: str, run_id: int, nombre: str, destino: Path) -> None:
    """gh no sobrescribe archivos: una descarga anterior completa se reutiliza."""
    if destino.exists() and any(destino.iterdir()):
        return
    gh("run", "download", str(run_id), "-R", repo, "-n", nombre, "-D", str(destino))


def listar_runs(repo: str, workflow: str, ultimos: int, numeros: list[int], rama: str) -> list[dict]:
    """gh run list devuelve el último intento de cada run: un intento anterior solo queda si ya se importó."""
    campos = "databaseId,number,attempt,headSha,headBranch,event,conclusion,status,createdAt,updatedAt"
    filtro = ["--branch", rama] if rama else []
    runs = json.loads(gh("run", "list", "-R", repo, "--workflow", workflow, *filtro, "-L", str(max(ultimos, 100)),
                         "--json", campos))
    runs = [r for r in runs if r["status"] == "completed" and (not numeros or r["number"] in numeros)]
    return sorted(runs[: ultimos if not numeros else len(runs)], key=lambda r: (r["number"], r["attempt"]))


def artefactos(repo: str, run_id: int) -> dict[str, bool]:
    salida = gh("api", f"repos/{repo}/actions/runs/{run_id}/artifacts", "--paginate", "--jq", r'.artifacts[] | "\(.name)\t\(.expired)"')
    return {nombre: vencido == "true" for nombre, vencido in (linea.split("\t") for linea in salida.splitlines() if linea)}


def fuentes_del_commit(sha: str, destino: Path) -> Path:
    """features/ y docs/ tal como estaban en el commit del run; si el commit no está en el clon local, los actuales."""
    try:
        contenido = subprocess.run(["git", "-C", str(RAIZ), "archive", sha, "features", "docs/requisitos.md", "docs/defectos.md"],
                                   check=True, capture_output=True).stdout
    except subprocess.CalledProcessError:
        return RAIZ
    destino.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile() as archivo:
        archivo.write(contenido)
        archivo.seek(0)
        with tarfile.open(fileobj=archivo) as tar:
            tar.extractall(destino, filter="data")
    return destino


def reconstruir(carpeta: Path, run: dict, repo: str) -> Path:
    """JUnit por CP y run.json de un run viejo, a partir de reportes-api y reportes-web."""
    salida = carpeta / "trazabilidad"
    fuentes = fuentes_del_commit(run["headSha"], carpeta / "fuentes")
    casos, _ = leer_casos(fuentes / "features", fuentes)
    resultados = leer_resultados(carpeta)
    casos[CP_CONTRATO] = caso_contrato(list(resultados["operaciones"]))
    por_caso = resultados_por_caso(casos, resultados)
    datos = metadatos_run(numero=str(run["number"]), intento=run["attempt"], run_id=run["databaseId"], sha=run["headSha"],
                          rama=run["headBranch"], evento=run["event"], conclusion=run["conclusion"], repo=repo,
                          fecha=run["updatedAt"], evidencia="sin-imagenes")
    api = next((p.parent.parent for p in carpeta.glob("reportes-*/api/reporte.html")), carpeta)
    evidencias = trazabilidad.copiar_evidencias(salida / "evidencias", resultados["evidencias"], api)
    trazabilidad.escribir_junit_cp(salida / "junit-cp.xml", casos, por_caso, resultados, datos, evidencias)
    resumen = trazabilidad.armar_run(datos, casos, por_caso)
    resumen["origen"] = "reconstruido de " + ", ".join(sorted(p.name for p in carpeta.glob("reportes-*")))
    resumen["etiquetas_de"] = run["headSha"][:7] if fuentes != RAIZ else "features actuales"
    (salida / "run.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")
    return salida


def descargar(repo: str, run: dict, base: Path) -> Path | None:
    carpeta = base / f"run-{run['number']}.{run['attempt']}"
    salida = carpeta / "trazabilidad"
    if (salida / "run.json").exists() and (salida / "junit-cp.xml").exists():
        return salida
    disponibles = {n: v for n, v in artefactos(repo, run["databaseId"]).items() if not v}
    if "trazabilidad" in disponibles:
        bajar_artefacto(repo, run["databaseId"], "trazabilidad", salida)
        return salida
    viejos = [n for n in ARTEFACTOS_VIEJOS if n in disponibles]
    if not viejos:
        return None
    for nombre in viejos:
        bajar_artefacto(repo, run["databaseId"], nombre, carpeta / nombre)
    return reconstruir(carpeta, run, repo)


# ---------- Lectura del artefacto ----------

def leer_carpeta(carpeta: Path) -> tuple[dict, list[dict]]:
    run = json.loads((carpeta / "run.json").read_text(encoding="utf-8"))
    casos = []
    for caso in ET.parse(carpeta / "junit-cp.xml").getroot().iter("testcase"):
        propiedades = {}
        for p in caso.iter("property"):
            propiedades.setdefault(p.get("name"), []).append(p.get("value", ""))
        casos.append({
            "cp": normalizar_cp(caso.get("name", "")), "summary": caso.get("name", ""), "grupo": caso.get("classname", ""),
            "estado": propiedades.get("estado", ["passed"])[0], "defectos": [d for v in propiedades.get("defecto", []) for d in v.split(", ") if d],
            "hu": propiedades.get("hu", [""])[0], "ca": propiedades.get("ca", [""])[0],
            "ejecuciones": propiedades.get("ejecuciones", [""])[0],
            "etiquetas": [f"{k}:{propiedades[k][0]}" for k in ("nivel", "tipo", "modulo") if k in propiedades],
            "evidencias": propiedades.get("evidencia", []),
        })
    return run, casos


def adjuntos(carpeta: Path, casos: list[dict]) -> list[Path]:
    """Capturas por ejecución. El reporte HTML de API no se adjunta: Kiwi rechaza archivos con etiquetas HTML."""
    return [r for r in (carpeta / e for c in casos for e in c["evidencias"]) if r.exists()]


def nombre_build(run: dict) -> str:
    return f"run-{run['numero']}" + (f".{run['intento']}" if int(run["intento"]) > 1 else "")


def resumen_testrun(run: dict) -> str:
    rama = f" {run['rama']}" if run.get("rama") else ""
    return f"Qolqe · run #{run['numero']}.{run['intento']} · {run['sha'][:7]} · {run['evento']}{rama} · evidencia: {run['evidencia']}"


def etiquetas_run(run: dict) -> list[str]:
    valores = [f"gh-run-{run['run_id']}-{run['intento']}", f"commit:{run['sha'][:7] or '-'}", f"evento:{run['evento']}",
               f"rama:{run.get('rama') or '-'}", f"evidencia:{run['evidencia']}"]
    return valores + ([f"conclusion:{run['conclusion']}"] if run.get("conclusion") else [])


def notas_testrun(run: dict, repo: str) -> str:
    duenio, nombre = repo.split("/")
    pages = f"https://{duenio.lower()}.github.io/{nombre}/"
    artefactos = f"{run['url']}#artifacts" if run.get("url") else "(run local, sin artefactos)"
    return (f"Run de GitHub Actions: {run.get('url') or '-'}\nCommit: {run['sha'] or '-'}\n"
            f"Artefactos del run (reportes y trazabilidad): {artefactos}\n"
            f"Portada y reportes del último run de main: {pages} (API: {pages}api/ · web: {pages}web/)")


def adjuntar(funcion, objeto_id: int, archivo: Path) -> bool:
    """Un adjunto rechazado por Kiwi (tamaño o contenido) se avisa y no corta la importación."""
    try:
        funcion(objeto_id, archivo.name, base64.b64encode(archivo.read_bytes()).decode())
        return True
    except xmlrpc.client.Fault as error:
        print(f"  Aviso: Kiwi no aceptó {archivo.name}: {error.faultString[:200]}")
        return False


def enlace_defecto(repo: str, defecto: str, anclas: dict) -> str:
    url = f"https://github.com/{repo}/blob/main/docs/defectos.md"
    return f"{url}#{anclas[defecto]}" if defecto in anclas else url


# ---------- Simulación ----------

def simular(run: dict, casos: list[dict], carpeta: Path, plan: str | None) -> None:
    estados = Counter(ESTADO_KIWI[c["estado"]] for c in casos)
    modulos = Counter(c["grupo"] for c in casos)
    defectos = [(d, c["cp"]) for c in casos if c["estado"] == "xfailed" for d in c["defectos"]]
    inestables = [c["cp"] for c in casos if c["estado"] == "flaky"]
    print(f"\nRun #{run['numero']}.{run['intento']} · {run['sha'][:7]} · {run['evento']} {run.get('rama', '')} · "
          f"conclusión: {run.get('conclusion') or '?'}{' · ' + run['origen'] if run.get('origen') else ''}")
    print(f'  TestRun   "{resumen_testrun(run)}"')
    print(f"  Build {nombre_build(run)} · versión del plan · commit {run['sha'][:7]} · producto {PRODUCTO} · "
          f"plan {plan or '(falta KIWI_PLAN_ID)'}")
    print(f"  Etiquetas {', '.join(etiquetas_run(run))}")
    print(f"  Ejecuciones {len(casos)}: " + ", ".join(f"{k} {v}" for k, v in estados.most_common())
          + " · por grupo: " + ", ".join(f"{k} {v}" for k, v in sorted(modulos.items())))
    if defectos:
        print(f"  Enlaces de defecto ({len(defectos)}): " + ", ".join(f"{d}→{cp}" for d, cp in defectos))
    if inestables:
        print(f"  Inestables: {', '.join(inestables)}")
    archivos = adjuntos(carpeta, casos)
    if archivos:
        print(f"  Adjuntos ({len(archivos)}): " + ", ".join(f"{a.name} ({a.stat().st_size // 1024} KB)" for a in archivos[:6])
              + (" ..." if len(archivos) > 6 else ""))


# ---------- Kiwi TCMS ----------

def conectar(certificado: Path):
    """tcms-api verifica el certificado: se usa el de Kiwi solo en este proceso (gh recibe el entorno sin él)."""
    try:
        from tcms_api import TCMS
    except ImportError:
        sys.exit("Falta tcms-api: pip install -r requirements-gestion.txt")
    if not (Path.home() / ".tcms.conf").exists():
        sys.exit("Falta ~/.tcms.conf con url, username y password de Kiwi (ver docs/gestion-casos.md).")
    if certificado.exists():
        os.environ["SSL_CERT_FILE"] = str(certificado)
    return TCMS().exec


def obtener_o_crear(rpc_objeto, filtro: dict, valores: dict | None = None) -> dict:
    encontrados = rpc_objeto.filter(filtro)
    return encontrados[0] if encontrados else rpc_objeto.create(valores or filtro)


def crear_plan(rpc) -> int:
    clasificaciones = rpc.Classification.filter({})
    clasificacion = clasificaciones[0]["id"] if clasificaciones else rpc.Classification.create({"name": "Proyectos"})["id"]
    producto = obtener_o_crear(rpc.Product, {"name": PRODUCTO}, {"name": PRODUCTO, "classification": clasificacion})
    version = obtener_o_crear(rpc.Version, {"product": producto["id"], "value": "base"})
    tipos = rpc.PlanType.filter({"name": "Integration"}) or rpc.PlanType.filter({}) or [rpc.PlanType.create({"name": "Integration"})]
    plan = obtener_o_crear(rpc.TestPlan, {"name": NOMBRE_PLAN, "product": producto["id"]}, {
        "name": NOMBRE_PLAN, "product": producto["id"], "product_version": version["id"], "type": tipos[0]["id"],
        "is_active": True, "text": "Casos automatizados del núcleo y de G4 (API, web y contrato). Cada TestRun es un run "
                                   "de GitHub Actions importado por scripts/kiwi_sincronizar.py.",
    })
    print(f"Plan de Kiwi: {plan['id']} · {NOMBRE_PLAN}. Usar KIWI_PLAN_ID={plan['id']}.")
    return plan["id"]


def renombrar_casos(rpc, producto: int, casos_run: list[dict]) -> None:
    """Mantiene el caso por CP: si cambió el título se renombra (no se parte el historial) y se completan sus datos."""
    for c in casos_run:
        existentes = rpc.TestCase.filter({"summary__startswith": f"{c['cp']} ", "category__product": producto})
        if existentes and existentes[0]["summary"] != c["summary"][:255]:
            rpc.TestCase.update(existentes[0]["id"], {"summary": c["summary"][:255]})


def completar_caso(rpc, caso_kiwi: dict, c: dict, definicion: dict | None, repo: str) -> None:
    deseado = {"requirement": c["hu"][:255], "is_automated": True}
    if definicion:
        deseado |= {"text": "\n".join(definicion["pasos"]), "script": definicion["archivo"],
                    "extra_link": f"https://github.com/{repo}/blob/main/{definicion['archivo']}#L{definicion['linea']}"}
    cambios = {k: v for k, v in deseado.items() if caso_kiwi.get(k) != v}
    if cambios:
        rpc.TestCase.update(caso_kiwi["id"], cambios)
    tiene = {t["name"] for t in rpc.Tag.filter({"case": caso_kiwi["id"]})}
    hu_ca = (definicion or {}).get("hu_ca") or [x for x in c["ca"].split(", ") if x]
    nuevas = [*[h for h in c["hu"].split(", ") if h], *hu_ca, *c["etiquetas"], *c["defectos"]]
    if c["estado"] == "flaky":
        nuevas.append("inestable")
    for etiqueta in dict.fromkeys(nuevas):
        if etiqueta not in tiene:
            rpc.TestCase.add_tag(caso_kiwi["id"], etiqueta)


def sincronizar(rpc, plan_id: int, run: dict, casos_run: list[dict], carpeta: Path, repo: str) -> None:
    from tcms_junit_plugin import Plugin

    etiqueta_run = etiquetas_run(run)[0]
    if rpc.TestRun.filter({"tag__name": etiqueta_run}):
        print(f"Run #{run['numero']}.{run['intento']}: ya estaba en Kiwi ({etiqueta_run}).")
        return
    plan = rpc.TestPlan.filter({"pk": plan_id})[0]
    producto = plan["product"]
    inicio = run["fecha"][:19].replace("T", " ")
    # La etiqueta definitiva va al final: si la importación se corta, el TestRun queda "incompleto" y se retoma.
    incompleto = f"incompleto:{etiqueta_run}"
    pendientes = rpc.TestRun.filter({"tag__name": incompleto})
    if pendientes:
        testrun = pendientes[0]
        print(f"Run #{run['numero']}.{run['intento']}: se retoma el TestRun {testrun['id']} que quedó incompleto.")
    else:
        # Kiwi solo acepta builds de la versión del plan (NewRunForm): el commit va en el resumen y en commit:<sha7>.
        build = obtener_o_crear(rpc.Build, {"name": nombre_build(run), "version": plan["product_version"]})
        testrun = rpc.TestRun.create({
            "summary": resumen_testrun(run)[:255], "plan": plan_id, "build": build["id"], "manager": plan["author"],
            "default_tester": plan["author"], "start_date": inicio, "notes": notas_testrun(run, repo),
        })
        rpc.TestRun.add_tag(testrun["id"], incompleto)

    renombrar_casos(rpc, producto, casos_run)
    os.environ.update(TCMS_RUN_ID=str(testrun["id"]), TCMS_PRODUCT=PRODUCTO)
    Plugin(summary_template="${name}").parse([str(carpeta / "junit-cp.xml")])
    rpc.TestRun.update(testrun["id"], {"stop_date": inicio})

    definiciones, _ = leer_casos(RAIZ / "features", RAIZ)
    anclas = leer_defectos(RAIZ / "docs" / "defectos.md")
    por_cp = {c["cp"]: c for c in casos_run}
    idle = rpc.TestExecutionStatus.filter({"name": "IDLE"})
    subidos = 0
    for ejecucion in rpc.TestExecution.filter({"run": testrun["id"]}):
        c = por_cp.get(normalizar_cp(ejecucion.get("case__summary", "")))
        if not c:
            continue
        caso_kiwi = rpc.TestCase.filter({"pk": ejecucion["case"]})[0]
        completar_caso(rpc, caso_kiwi, c, definiciones.get(c["cp"]), repo)
        if c["estado"] == "xfailed":
            for defecto in c["defectos"]:
                rpc.TestExecution.add_link({"execution_id": ejecucion["id"], "name": defecto, "is_defect": True,
                                            "url": enlace_defecto(repo, defecto, anclas)})
        elif c["estado"] == "sin ejecutar" and idle:
            rpc.TestExecution.update(ejecucion["id"], {"status": idle[0]["id"]})
        elif c["estado"] == "flaky":
            rpc.TestExecution.add_comment(ejecucion["id"], f"Inestable: pasaron {c['ejecuciones']} ejecuciones.")
        # Kiwi 17 acepta adjuntos por ejecución: cada captura queda junto al resultado de su CP.
        for evidencia in c["evidencias"]:
            archivo = carpeta / evidencia
            if archivo.exists() and archivo.stat().st_size <= LIMITE_ADJUNTO:
                subidos += adjuntar(rpc.TestExecution.add_attachment, ejecucion["id"], archivo)
    for etiqueta in etiquetas_run(run):
        rpc.TestRun.add_tag(testrun["id"], etiqueta)
    rpc.TestRun.remove_tag(testrun["id"], incompleto)
    print(f"Run #{run['numero']}.{run['intento']} → TestRun {testrun['id']} ({len(casos_run)} casos, {subidos} adjuntos).")


# ---------- Programa ----------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", default="Joharjbe/qolqe-wallet")
    parser.add_argument("--workflow", default="pruebas.yml")
    parser.add_argument("--rama", default="main", help='Rama de los runs (por defecto main, como el historial de Pages; "" = todas)')
    parser.add_argument("--ultimos", type=int, default=20, help="Cuántos runs recientes revisar (por defecto 20)")
    parser.add_argument("--run", type=int, nargs="*", default=[], help="Números de run específicos")
    parser.add_argument("--desde-carpeta", type=Path, help="Importa una carpeta con junit-cp.xml y run.json (sin GitHub)")
    parser.add_argument("--descargas", type=Path, default=RAIZ / "reportes" / "kiwi" / "runs")
    parser.add_argument("--simular", action="store_true", help="Muestra lo que crearía en Kiwi sin conectarse")
    parser.add_argument("--crear-plan", action="store_true", help="Crea (o encuentra) el producto y el plan, y muestra su id")
    parser.add_argument("--plan", default=os.environ.get("KIWI_PLAN_ID"), help="Id del TestPlan (por defecto KIWI_PLAN_ID)")
    parser.add_argument("--certificado", type=Path, default=RAIZ / "herramientas" / "kiwi" / "ssl" / "localhost.crt")
    parser.add_argument("--historial", type=Path, help="Además escribe historial.json y historial.html de estos runs")
    args = parser.parse_args()

    rpc = None if args.simular else conectar(args.certificado)
    if args.crear_plan:
        crear_plan(rpc)
        return
    if not args.simular and not args.plan:
        sys.exit("Falta el plan: KIWI_PLAN_ID=<id> o --plan <id> (se obtiene con --crear-plan).")

    if args.desde_carpeta:
        carpetas = [args.desde_carpeta]
    else:
        carpetas = []
        for run in listar_runs(args.repo, args.workflow, args.ultimos, args.run, args.rama):
            carpeta = descargar(args.repo, run, args.descargas)
            if carpeta is None:
                print(f"Run #{run['number']}: sin artefactos (vencidos o el run no llegó a las pruebas); se omite.")
            else:
                carpetas.append(carpeta)

    runs = []
    for carpeta in carpetas:
        run, casos_run = leer_carpeta(carpeta)
        runs.append(run)
        if args.simular:
            simular(run, casos_run, carpeta, args.plan)
        else:
            sincronizar(rpc, int(args.plan), run, casos_run, carpeta, args.repo)
    if args.historial:
        historial = trazabilidad.armar_historial(runs, maximo=max(len(runs), 1))
        trazabilidad.escribir_historial(args.historial, historial)
        print(f"\nHistorial de {len(runs)} runs en {args.historial / 'historial.html'}")
    print(f"\n{len(runs)} runs {'revisados (simulación: no se creó nada en Kiwi)' if args.simular else 'sincronizados con Kiwi TCMS'}.")


if __name__ == "__main__":
    main()
