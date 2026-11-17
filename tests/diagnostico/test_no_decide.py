"""CP-IA-07: la IA no decide. El guardrail más importante de los ocho.

Conceptos de la clase 15: **guardrails** y **human-in-the-loop** («la IA
propone, el tester decide»). De nada sirve que el diagnóstico acierte si para
lograrlo se le deja mover el veredicto del run, reescribir un caso de prueba o
marcar un fallo como «ya explicado». El límite tiene que estar en el diseño y
poder comprobarse, no ser una promesa del README.

Lo que se comprueba, en orden de importancia:

1. El `quality-gate` del pipeline NO depende del diagnóstico: su veredicto sale
   de los cuatro jobs de pruebas y el componente no aparece en `.github/`.
2. Correr el diagnóstico no modifica NI UN archivo del repositorio: ni el
   pipeline, ni los `.feature`, ni las suites, ni la documentación, ni la
   aplicación bajo prueba. Se comprueba con el sha256 de cada archivo antes y
   después.
3. Un diagnóstico que falla no pone el run en rojo: el comando termina en 0
   aunque el backend no contesta ni una vez. Si pudiera tumbar el pipeline,
   sería una herramienta que decide.
4. El componente no tiene con qué: no ejecuta procesos, no borra, no escribe
   fuera de la carpeta de salida y no habla con las variables del runner.
5. El reporte dice en su cara que es una propuesta.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from herramientas.diagnostico_ia import __main__ as cli
from herramientas.diagnostico_ia import diagnostico

# Lo que el diagnóstico no puede tocar: el pipeline, los casos, las suites, la
# documentación y la aplicación bajo prueba.
VIGILADO = (".github", "features", "tests/api", "tests/e2e", "docs", "qolqe", "herramientas/diagnostico_ia",
            "tests/diagnostico/conjunto_oro")
ARCHIVOS_SUELTOS = ("pytest.ini", "playwright.config.ts", "ruff.toml", "schemathesis.toml", ".gitignore")

# Nada de esto aparece en el componente: son las maneras de decidir algo en un
# pipeline de GitHub Actions o de alterar el repositorio.
PROHIBIDO_EN_EL_COMPONENTE = ("subprocess", "os.system", "shutil", "os.remove", "unlink(", "GITHUB_OUTPUT",
                              "GITHUB_STEP_SUMMARY", "GITHUB_ENV", "::error", "git ")


def _huellas(raiz: Path) -> dict[str, str]:
    """sha256 de cada archivo vigilado, por ruta relativa."""
    huellas = {}
    rutas = [ruta for carpeta in VIGILADO for ruta in (raiz / carpeta).rglob("*")]
    rutas += [raiz / nombre for nombre in ARCHIVOS_SUELTOS]
    for ruta in rutas:
        if not ruta.is_file() or "__pycache__" in ruta.parts:
            continue
        huellas[str(ruta.relative_to(raiz))] = hashlib.sha256(ruta.read_bytes()).hexdigest()
    return huellas


def test_cp_ia_07_el_quality_gate_no_depende_del_diagnostico(raiz_repo):
    """CP-IA-07 · El veredicto del run lo dan las pruebas, no el diagnóstico.

    El `quality-gate` de `.github/workflows/pruebas.yml` evalúa cuatro jobs:
    `estatico`, `api`, `contrato` y `web`. El componente de IA no es uno de
    ellos y no se menciona en ninguna parte del pipeline, así que no hay por
    dónde que su resultado cambie el veredicto.
    """
    flujo = (raiz_repo / ".github" / "workflows" / "pruebas.yml").read_text(encoding="utf-8")

    necesita = re.search(r"quality-gate:\n(?:.*\n)*?\s+needs: \[([^\]]+)\]", flujo)
    assert necesita, "no se encontró el quality-gate en el flujo"
    assert [job.strip() for job in necesita.group(1).split(",")] == ["estatico", "api", "contrato", "web"]

    for carpeta in (".github/workflows", ".github/scripts"):
        for ruta in (raiz_repo / carpeta).glob("*"):
            if ruta.is_file():
                assert "diagnostico_ia" not in ruta.read_text(encoding="utf-8", errors="replace"), ruta


def test_cp_ia_07_correr_el_diagnostico_no_cambia_ningun_archivo(run_sintetico, caso_base, raiz_repo, tmp_path):
    """CP-IA-07 · Antes y después: el repositorio queda igual.

    El diagnóstico lee artefactos y `docs/defectos.md`, y escribe en la carpeta
    de salida que se le pasa. Nada más. Se compara el sha256 de cada archivo del
    pipeline, de los casos, de las suites, de la documentación, de la aplicación
    bajo prueba y del propio componente.
    """
    carpeta = run_sintetico([caso_base(), caso_base(name="CP-A79 El alias admite espacios", defecto="DEF-02",
                                                    archivo="features/contactos_api.feature:60")])
    antes = _huellas(raiz_repo)
    assert len(antes) > 100, "la lista de archivos vigilados quedó vacía o casi"

    resultado = diagnostico.diagnosticar(carpeta, backend="lineabase", raiz_repo=raiz_repo)
    salida = tmp_path / "salida"
    ruta_json, ruta_md = diagnostico.escribir(resultado, salida)

    despues = _huellas(raiz_repo)
    cambiados = [ruta for ruta in antes if antes[ruta] != despues.get(ruta)]
    assert cambiados == [], f"el diagnóstico modificó archivos del repositorio: {cambiados}"
    assert set(despues) == set(antes), "el diagnóstico agregó o quitó archivos del repositorio"

    # Y lo que escribió está donde se le pidió, con esos dos nombres y nada más.
    assert ruta_json.is_file() and ruta_md.is_file()
    assert sorted(p.name for p in salida.iterdir()) == ["diagnostico.json", "diagnostico.md"]


def test_cp_ia_07_un_diagnostico_que_falla_no_pone_el_run_en_rojo(run_sintetico, caso_base, raiz_repo, tmp_path,
                                                                 capsys):
    """CP-IA-07 · El comando termina en 0 aunque el backend no conteste nunca.

    Se corre la CLI de verdad con `--modelo grabado` y la carpeta de grabados
    vacía, que es el peor caso sin red: cero clasificaciones. El código de salida
    es 0, porque un rechazo o un error del backend son DATOS del reporte, no el
    veredicto de nada. Si devolviera 1, bastaría con que se cayera la API del
    modelo para bloquear un merge, y entonces la IA sí estaría decidiendo.
    """
    carpeta = run_sintetico([caso_base()])
    vacia = tmp_path / "sin-grabados"
    vacia.mkdir()

    codigo = cli.main(["--run", str(carpeta), "--modelo", "grabado", "--grabados", str(vacia),
                       "--repo", str(raiz_repo), "--salida", str(tmp_path / "salida")])

    assert codigo == 0
    impreso = capsys.readouterr().out
    assert "0 clasificados" in impreso
    assert "2 errores del backend" in impreso  # el del único grupo y el del resumen del run

    # Y el reporte se escribió igual, con el hueco a la vista en vez de relleno.
    reporte = (tmp_path / "salida" / "diagnostico.md").read_text(encoding="utf-8")
    assert "| Clasificaciones aceptadas | 0 |" in reporte
    assert "_(sin resumen: la petición se rechazó, ver «Rechazos»)_" in reporte


def test_cp_ia_07_el_componente_no_tiene_con_que_decidir(raiz_repo):
    """CP-IA-07 · Revisión del código: no hay por dónde.

    Un guardrail que depende de que nadie agregue una línea no es un guardrail.
    Esta prueba lee los módulos del componente y falla si aparece una manera de
    ejecutar algo, de borrar algo o de hablar con las variables del runner de
    GitHub, que es como un paso de Actions decide.
    """
    carpeta = raiz_repo / "herramientas" / "diagnostico_ia"
    modulos = sorted(carpeta.glob("*.py"))
    assert len(modulos) == 7, [ruta.name for ruta in modulos]

    for ruta in modulos:
        codigo = ruta.read_text(encoding="utf-8")
        for prohibido in PROHIBIDO_EN_EL_COMPONENTE:
            assert prohibido not in codigo, f"{ruta.name} usa {prohibido!r}"

    # Lo único que escribe archivos son las dos funciones que lo declaran.
    escriben = {ruta.name for ruta in modulos if "write_text(" in ruta.read_text(encoding="utf-8")}
    assert escriben == {"diagnostico.py", "modelo.py"}  # escribir() y guardar_respuesta()


def test_cp_ia_07_el_reporte_dice_que_la_ia_no_decide(run_sintetico, caso_base, raiz_repo):
    """CP-IA-07 · Human-in-the-loop, escrito donde se lee.

    Quien abra el reporte en la pestaña de artefactos del run tiene que ver, sin
    buscarlo, que eso es una propuesta y que la decisión sigue siendo de una
    persona. Está en el JSON, en el reporte y en la ayuda del comando.
    """
    carpeta = run_sintetico([caso_base()])
    resultado = diagnostico.diagnosticar(carpeta, backend="lineabase", raiz_repo=raiz_repo)

    assert resultado["aviso"] == ("La IA propone, el tester decide. Este reporte no cambia el veredicto del "
                                 "quality gate.")
    reporte = diagnostico.a_markdown(resultado)
    assert f"> {resultado['aviso']}" in reporte
    assert "La agrupación es determinista" in reporte
    assert "son propuestas del backend indicado arriba" in reporte

    assert "LA IA NO DECIDE NADA" in cli.AYUDA
    assert "La IA propone, el tester decide" in cli.AYUDA
    # El prompt del sistema le dice lo mismo al modelo, para que no escriba
    # veredictos: si la información no alcanza, lo dice con confianza baja.
    assert "No decides nada" in diagnostico.SISTEMA
