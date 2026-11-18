# Resultados de la capacidad de IA · corrida del 17-11-2026

Copia **versionada** de la medición que cita [`docs/capacidad-ia.md`](../capacidad-ia.md), para que los números se puedan leer sin volver a correr nada y sin clave de API.

El arnés escribe estos archivos en `reportes/diagnostico_ia/`, que está en `.gitignore` porque el resultado de una medición se vuelve a medir, no se versiona. Esta carpeta es la excepción: es la evidencia de la corrida concreta que el informe cita, igual que `tests/performance/resultados/` guarda las corridas de k6 de la Parte 3.

| Archivo | Qué es |
|---|---|
| `evals-google.md` / `.json` | Evals contra el conjunto de oro con el modelo (`gemini-3.1-flash-lite`) |
| `evals-lineabase.md` / `.json` | El mismo conjunto con la línea base de reglas, sin IA: es el control |
| `inyeccion-google.json` | El experimento de inyección de prompts, 5 corridas por condición (LIM-IA-01) |
| `no-determinismo-google.json` / `-lineabase.json` | La varianza entre 5 corridas del mismo run |

Cómo se vuelven a generar (necesita `GOOGLE_API_KEY` en un `.env` local; tarda unos 8 minutos):

```
DIAGNOSTICO_IA_BACKEND=google .venv/bin/python -m pytest tests/diagnostico -q
```

Sin clave, la línea base se mide igual y en segundos:

```
.venv/bin/python -m pytest tests/diagnostico -q
```

Los números pueden cambiar de una corrida a otra: el modelo no es determinista, y eso está medido en `no-determinismo-google.json`.
