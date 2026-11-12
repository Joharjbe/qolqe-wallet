"""Escribe las tablas de cada corrida en Markdown y CSV (diseño §7.1): tabla_resumen, veredicto y, en estrés, tabla_estres."""
from dataclasses import asdict
from datetime import datetime

import pandas as pd
from corrida import Corrida
from lectura import LIMA, epoca, umbrales_k6
from metricas import estadisticas, fmt

MARCA = {"PASA": "✓ PASA", "FALLA": "✗ FALLA"}


def _md(df: pd.DataFrame) -> str:
    """DataFrame → tabla Markdown sin dependencias extra (los números ya vienen formateados)."""
    columnas = list(df.columns)
    lineas = ["| " + " | ".join(columnas) + " |", "|" + "---|" * len(columnas)]
    lineas += ["| " + " | ".join(str(x).replace("|", "\\|") for x in fila) + " |" for fila in df.itertuples(index=False)]
    return "\n".join(lineas)


def _orden(ep: str, grupo: str) -> tuple:
    return (0 if ep == "login" else 1 if grupo == "consulta" else 2, ep)


def tabla_resumen(c: Corrida) -> pd.DataFrame:
    """Formato de S14: endpoint, peticiones, promedio, p50, p90, p95, p99, error y throughput, por subconjunto medido."""
    filas = []
    medidas = list(c.perfil.medidas)
    if not any(c.mascara(c.pet, e, v).any() for _, e, v in medidas):   # p. ej. humo: no llegó a la fase medida
        medidas.append(("toda la corrida (no hay peticiones en la fase medida)", None, None))
    for titulo, etiqueta, valores in medidas:
        pet = c.pet[c.mascara(c.pet, etiqueta, valores)]
        ini, fin = c.intervalo(etiqueta, valores)
        duracion = max(fin - ini, 1e-9)
        grupos = [(ep, d) for ep, d in pet.groupby("ep")]
        grupos.sort(key=lambda par: _orden(par[0], par[1]["grupo"].iloc[0]))
        grupos += [(f"grupo {g}", pet[pet["grupo"] == g]) for g in ("consulta", "dinero")] + [("total", pet)]
        for ep, d in grupos:
            if d.empty:
                continue
            e = estadisticas(d["dur"])
            filas.append({"subconjunto": titulo, "endpoint": d["name"].iloc[0] if not ep.startswith(("grupo", "total")) else "",
                          "ep": ep, "grupo": d["grupo"].iloc[0] if not ep.startswith(("grupo", "total")) else "",
                          "peticiones": e["n"], "promedio_ms": e["promedio"], "p50_ms": e["p50"], "p90_ms": e["p90"],
                          "p95_ms": e["p95"], "p99_ms": e["p99"], "max_ms": e["max"],
                          "error_rendimiento_%": 100 * d["error_rend"].mean(), "error_datos_%": 100 * d["error_datos"].mean(),
                          "throughput_req_s": len(d) / duracion})
    return pd.DataFrame(filas)


def escribir_tabla_resumen(c: Corrida) -> pd.DataFrame:
    t = tabla_resumen(c)
    t.to_csv(c.carpeta / "tabla_resumen.csv", index=False, float_format="%.2f")
    nota = ("Formato de S14. Tiempos en ms (percentil por rango más cercano). Error de rendimiento = 5xx y status 0; "
            "error de datos = 4xx de regla de negocio (se reportan por separado, enunciado §5).")
    partes = [f"# Tabla resumen · {c.nombre}", "", nota, ""]
    for titulo, d in t.groupby("subconjunto", sort=False):
        vista = pd.DataFrame({
            "Endpoint": [f"`{ep}` {nombre}".strip() if nombre else f"**{ep}**" for ep, nombre in zip(d["ep"], d["endpoint"], strict=True)],
            "Peticiones": d["peticiones"].map(fmt), "Promedio": d["promedio_ms"].map(fmt), "p50": d["p50_ms"].map(fmt),
            "p90": d["p90_ms"].map(fmt), "p95": d["p95_ms"].map(fmt), "p99": d["p99_ms"].map(fmt),
            "Error rend.": d["error_rendimiento_%"].map(lambda x: fmt(x, 2, "%")),
            "Error datos": d["error_datos_%"].map(lambda x: fmt(x, 2, "%")),
            "Throughput (req/s)": d["throughput_req_s"].map(lambda x: fmt(x, 2))})
        partes += [f"## {titulo}", "", _md(vista), ""]
    (c.carpeta / "tabla_resumen.md").write_text("\n".join(partes), encoding="utf-8")
    return t


def _hora(ts: float | None) -> str:
    return datetime.fromtimestamp(ts, LIMA).strftime("%Y-%m-%d %H:%M:%S") if ts else "—"


def _cabecera(c: Corrida) -> list[str]:
    ini, fin = epoca(c.meta, "inicio"), epoca(c.meta, "fin")
    hora = _hora
    salida = c.meta.get("codigo_salida_k6", c.meta.get("exit_code", "—"))
    e = c.perfil.escala
    aviso = ([(f"- **Ensayo comprimido (ESCALA = {e:g})**: duraciones, fases, ventanas y think time × {e:g}, con la misma "
               "tasa de llegada; valida la cadena completa y **no es evidencia**")] if e != 1 else [])
    return aviso + [f"- Inicio: {hora(ini)} · fin: {hora(fin)} (hora de Lima) · primera petición: {hora(c.t0)}",
            f"- Duración con muestras: {fmt(c.duracion / 60, 1)} min · peticiones: {fmt(len(c.pet))} · sesiones: {fmt(len(c.sesiones))}",
            f"- Código de salida de k6: {salida} (0 = todos los umbrales de k6 pasan; 99 = alguno falla)"]


def _vista(filas, con_n: bool = True) -> pd.DataFrame:
    df = pd.DataFrame([asdict(f) for f in filas])
    df["resultado"] = df["resultado"].map(lambda r: MARCA.get(r, r))
    columnas = ["id", "criterio", "medido", "umbral", "resultado"] + (["n"] if con_n else []) + ["nota"]
    return df[columnas].rename(columns={"id": "ID", "criterio": "Criterio", "medido": "Medido", "umbral": "Umbral",
                                        "resultado": "Resultado", "n": "n", "nota": "Nota"})


def tabla_errores(c: Corrida) -> pd.DataFrame:
    """Enunciado §5: un 4xx de regla de negocio es un problema de datos, no de rendimiento. Se cuentan por separado."""
    filas = []
    rend = c.otras[c.otras["metrica"] == "errores_rendimiento"]
    if len(rend):
        filas += [{"Clase": "rendimiento (U-03)", "Tipo o código": t, "Cantidad": fmt(n)} for t, n in rend.groupby("tipo")["valor"].sum().items()]
    else:
        filas += [{"Clase": "rendimiento (U-03)", "Tipo o código": t, "Cantidad": fmt(n)}
                  for t, n in c.pet[c.pet["tipo_error"] != ""].groupby("tipo_error").size().items()]
    datos = c.otras[c.otras["metrica"] == "errores_datos"]
    filas += [{"Clase": "datos (V-02)", "Tipo o código": t, "Cantidad": fmt(n)} for t, n in datos.groupby("codigo")["valor"].sum().items()]
    return pd.DataFrame(filas or [{"Clase": "—", "Tipo o código": "sin errores", "Cantidad": "0"}])


def escribir_veredicto(c: Corrida, ev: dict) -> None:
    filas = ([("validez", f) for f in ev["validez"]] + [("umbral", f) for f in ev["umbrales"]]
             + [("detalle", f) for f in ev["detalle"]])
    csv = pd.DataFrame([{"seccion": s} | asdict(f) for s, f in filas])
    csv.to_csv(c.carpeta / "veredicto.csv", index=False)

    valida = all(f.resultado != "FALLA" for f in ev["validez"] if f.decide)
    partes = [f"# Veredicto · {c.nombre}", "", *_cabecera(c),
              f"- **Corrida {'válida' if valida else 'NO válida: se repite y no se analiza (paso 1 de S14)'}** según V-01 a V-07", "",
              "## 1. Validez de la corrida (V-01 a V-07)", "", _md(_vista(ev["validez"], False)), "",
              "## 2. Umbrales (U-01 a U-09)", "", _md(_vista(ev["umbrales"], False)), "",
              "## 3. Detalle por grupo, endpoint y ventana", "",
              "Las filas *informativas* no cambian el veredicto del umbral (por ejemplo, los endpoints de `otras` con < 100 muestras).", "",
              _md(_vista(ev["detalle"])), ""]
    if ev["mezcla"] is not None:
        m = ev["mezcla"]
        vista = pd.DataFrame({"Operación": m["operacion"], "Pedida (%)": m["pedida_%"].map(lambda x: fmt(x, 1)),
                              "Lograda (%)": m["lograda_%"].map(lambda x: fmt(x, 1)),
                              "Diferencia (pp)": m["diferencia_pp"].map(lambda x: fmt(x, 2))})
        partes += ["## 4. Mezcla lograda (V-03, M-06)", "", _md(vista), ""]
    partes += ["## 5. Errores de rendimiento y de datos, por separado (toda la corrida)", "", _md(tabla_errores(c)), ""]
    umbrales = umbrales_k6(c.resumen)
    if umbrales:
        vista = pd.DataFrame([{"Umbral": u["descripcion"], "Métrica": f"`{u['metrica']}`", "Condición": f"`{u['condicion']}`",
                               "Medido por k6": u["valor"], "k6": u["estado"]} for u in umbrales])
        partes += ["## 6. Umbrales evaluados por k6 (resumen.json; ✓ cumple, ✗ falla, ○ sin muestras)", "", _md(vista), ""]
    (c.carpeta / "veredicto.md").write_text("\n".join(partes), encoding="utf-8")


def escribir_tabla_estres(c: Corrida, tabla: pd.DataFrame, cap: dict) -> None:
    tabla.to_csv(c.carpeta / "tabla_estres.csv", index=False, float_format="%.2f")
    vista = tabla.copy()
    for columna in vista.columns[2:]:
        vista[columna] = vista[columna].map(lambda x: fmt(x, 1 if isinstance(x, float) and abs(x) < 100 else 0))
    texto = (f"# Estrés: un momento cada 100 usuarios (formato del ejercicio 3 de S14) · {c.nombre}\n\n"
             f"Capacidad (U-08): **{fmt(cap['capacidad'])} usuarios simultáneos**"
             f"{'' if cap['limite_alcanzado'] else ' o más (no hubo falla sostenida)'}.\n\n{_md(vista)}\n")
    (c.carpeta / "tabla_estres.md").write_text(texto, encoding="utf-8")
