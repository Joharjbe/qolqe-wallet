"""Diagnóstico asistido por IA de los fallos de un run del pipeline.

Capacidad de IA del proyecto (entrega final, punto 8). Enfoque de la clase 15:
«IA para probar», en la fase de **Reporte** del ciclo de pruebas (resumir
resultados y agrupar fallos parecidos).

Lo que hace: lee los artefactos que el pipeline ya genera (el JUnit por caso y
los logs del run), agrupa los fallos parecidos con código determinista y, por
cada grupo, le pide a un modelo que proponga la clase del fallo
(defecto real / prueba inestable / error de entorno), el DEF-xx asociado y un
nombre para el grupo.

Lo que NO hace: decidir. El componente escribe un reporte; no cambia el
veredicto del quality gate, no toca ningún archivo del pipeline y no modifica
ningún caso de prueba. La IA propone, el tester decide (human-in-the-loop).
"""
