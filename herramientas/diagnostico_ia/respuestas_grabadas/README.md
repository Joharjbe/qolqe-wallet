# Respuestas grabadas

Esta carpeta tiene las **31 respuestas** de la corrida real del 17-nov-2026 con `google` (`gemini-3.1-flash-lite`), las que usa `docs/capacidad-ia.md`.

El backend `grabado` lee de aquí las respuestas de una corrida real del modelo, para
poder regenerar el mismo reporte sin volver a llamar a la API y sin depender de la red
(corridas reproducibles).

Se llena con una corrida real:

```bash
python -m herramientas.diagnostico_ia --run <carpeta-del-run> --modelo anthropic --grabar \
  --salida /tmp/diagnostico-ia
```

Cada archivo se llama `<clave>.json`, donde la clave es el hash de la petición
(sistema + prompt). Si el prompt cambia, la clave cambia y hay que volver a grabar.

**No se escriben a mano.** Una respuesta inventada por una persona y guardada aquí haría
que el reporte y sus métricas mientan: el reporte diría que el modelo clasificó algo que
nunca clasificó. Mientras no haya clave de API, el backend `grabado` falla con un mensaje
que dice justamente esto.
