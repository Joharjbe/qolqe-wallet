# Veredicto · calibracion · 20261111-1830

- Inicio: 2026-11-11 18:30:41 · fin: 2026-11-11 18:32:56 (hora de Lima) · primera petición: 2026-11-11 18:30:45
- Duración con muestras: 2.2 min · peticiones: 470 · sesiones: 40
- Código de salida de k6: 0 (0 = todos los umbrales de k6 pasan; 99 = alguno falla)
- **Corrida válida** según V-01 a V-07

## 1. Validez de la corrida (V-01 a V-07)

| ID | Criterio | Medido | Umbral | Resultado | Nota |
|---|---|---|---|---|---|
| V-01 | CPU del generador k6 (% del equipo, máximo de las ventanas) | 0.1 % | < 80 % | ✓ PASA | pico de 1 s: 0.3 % del equipo (3 % de un núcleo) |
| V-01 | CPU total del equipo (máximo de las ventanas) | 26.4 % | < 80 % | ✓ PASA | informativo: lo mueven procesos de macOS; ninguna ventana ≥ 80 % |
| V-02 | errores de datos · toda la corrida | 0 (0.00 %) | = 0 (repetir si > 0.1 %) | ✓ PASA |  |
| V-04 | CPU ocioso del equipo antes de empezar (top, 3 s) | 81.4 % | ≥ 65 % | ✓ PASA | carga de 1 min: 6.55 (diseño < 1.5; solo se registra) |
| V-05 | base restaurada idéntica y cpu.max del contenedor | base True, cpu.max 100000 100000 | base idéntica y 100000 100000 | ✓ PASA |  |
| V-07 | avisos de k6 'Insufficient VUs' | 0 | 0 | ✓ PASA | solo decide en carga y resistencia |

## 2. Umbrales (U-01 a U-09)

| ID | Criterio | Medido | Umbral | Resultado | Nota |
|---|---|---|---|---|---|
| U-01 | Consultas e inicio de sesión: el 95 % en menos de 800 ms | — | — | NO APLICA | se evalúa en carga y resistencia |
| U-02 | Operaciones de dinero: el 95 % en menos de 1.5 s | — | — | NO APLICA | se evalúa en carga y resistencia |
| U-03 | En hora punta, no más del 1 % de operaciones fallidas | — | — | NO APLICA | se evalúa en carga y resistencia |
| U-04 | Sostener el volumen de la hora punta | — | — | NO APLICA | se evalúa en carga y resistencia |
| U-05 | …sin acumular retrasos | — | — | NO APLICA | se evalúa en carga y resistencia |
| U-06 | Campaña: degradación razonable del servicio | — | — | NO APLICA | se evalúa en pico |
| U-07 | Ninguna operación de dinero a medias ni aplicada dos veces | 0 | = 0 | ✓ PASA | 1 criterio (ver detalle) |
| U-08 | Hasta cuántos usuarios simultáneos podemos crecer | — | — | NO APLICA | se evalúa en estrés |
| U-09 | Opera de 6:00 a 24:00 sin reinicios | — | — | NO APLICA | se evalúa en resistencia |

## 3. Detalle por grupo, endpoint y ventana

Las filas *informativas* no cambian el veredicto del umbral (por ejemplo, los endpoints de `otras` con < 100 muestras).

| ID | Criterio | Medido | Umbral | Resultado | n | Nota |
|---|---|---|---|---|---|---|
| M-14 | D_sesión (s de CPU por sesión) | 157.4 ms | se mide | MEDIDO | 40 |  |
| M-14 | L_sat = W ÷ D | 763 | se calcula | MEDIDO |  |  |
| M-14 | TOP para el estrés | 1,100 | ⌈1.33 × L_sat⌉ a la centena | MEDIDO |  | TOP=1100 correr.sh estres |
| U-07 | descuadres en C1–C6 (verificacion_dinero.txt) | 0 | = 0 | ✓ PASA |  | línea TOTAL |
| U-07 | operaciones de dinero sin respuesta (status 0) | 0 | se concilian en C6 | INFO |  |  |
| §2.1 | p95 de http_req_connecting | 0.0 ms | ≤ 10 ms (si no, se suma) | INFO |  | no se suma |
| §6.3 | throttling del cgroup en la corrida | 0 períodos, 0.0 s | diagnóstico (H1) | INFO |  |  |

## 5. Errores de rendimiento y de datos, por separado (toda la corrida)

| Clase | Tipo o código | Cantidad |
|---|---|---|
| — | sin errores | 0 |

## 6. Umbrales evaluados por k6 (resumen.json; ✓ cumple, ✗ falla, ○ sin muestras)

| Umbral | Métrica | Condición | Medido por k6 | k6 |
|---|---|---|---|---|
| validez: sin errores de rendimiento | `operacion_fallida` | `rate==0` | 0.00 % | ✓ |
| V-02 sin errores de datos | `errores_datos` | `count==0` | 0 | ✓ |
