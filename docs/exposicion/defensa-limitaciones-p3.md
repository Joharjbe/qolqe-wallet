# Defensa de las limitaciones de la Parte 3

Son las limitaciones que el propio informe declara (`docs/informe.md:247` y `:337`; detalle en `docs/Informe_Rendimiento_Qolqe.pdf`, §5, §6 y §8). Las 1 a 7 son las de `docs/informe.md`; las 8 a 10 no están en esa lista, pero el informe en PDF las declara y son probables en la defensa oral. Cada una tiene la respuesta en dos frases y el archivo que la sostiene. No es material nuevo: ordena lo que ya está escrito, para no improvisarlo.

**1. La resistencia duró 60 minutos, no 18 horas.**
Lo que busca la resistencia es deriva, y en 60 min no la hubo: las 12 ventanas de 5 min cumplen y el p95 final entre el inicial da 0,98 × en consultas y 1,01 × en dinero. Las 18 h se proyectan y lo digo como lo que es, una extrapolación lineal: el RSS a 54 000 sesiones da 92 MB frente a 700, con r² de 0,53, bajo pero sobre una recta casi plana (el RSS fue de 60,6 a 63,1 MB en la hora).
Lo sostiene: `tests/performance/resultados/resistencia/20261111-1958/veredicto.md:67-72` · `docs/Informe_Rendimiento_Qolqe.pdf`, Prueba 4 (pág. 32-33). Correr las 18 h en un entorno dedicado es la recomendación escrita (`docs/informe.md:361`).

**2. V-04 y V-01 se ajustaron durante la ejecución.**
V-04 pedía carga de 1 min < 1,5, y esta Mac no baja de ~3-4 sin nada corriendo: no se habría cumplido nunca, así que pasó a CPU ocioso ≥ 65 % (commit `5adb217`) y en las 8 corridas analizadas se midió entre 69,4 % y 93,3 %. V-01 pasó a decidir solo con el CPU de k6, que es el criterio del enunciado; ese cambio lo hice después de ver los datos y así está declarado: con el criterio original, el pico y el estrés se habrían repetido.
Lo sostiene: `docs/Informe_Rendimiento_Qolqe.pdf`, §5, «Cambios de criterio hechos durante la ejecución» (pág. 14) y tabla «Condiciones de la máquina en cada corrida» (pág. 15) · `tests/performance/README.md:122` · fila V-04 del `veredicto.md` de las 8 corridas analizadas (las de `tests/performance/resultados/`, sin `descartadas/`).

**3. El login con 1 usuario dio 92 ms frente al límite de 80 ms (V-06).**
V-06 es un criterio mío de validez, no un umbral del cliente: 92 ms es el 11,5 % del umbral de 800 ms y no cambia ningún veredicto. La explicación probable es que con 1 usuario el PBKDF2 corre en una vCPU ociosa que macOS manda a los núcleos de eficiencia: bajo carga, el CPU por sesión baja de 157 ms a ≈ 103 ms.
Lo sostiene: `tests/performance/resultados/referencia/20261111-1828/veredicto.md:25` · `docs/Informe_Rendimiento_Qolqe.pdf`, §6 (pág. 16) · `tests/performance/README.md:128`. Es también el dato que dejo fuera del pipeline (`docs/pipeline.md:52`).

**4. El estrés lo cortó la red de seguridad de k6 antes de la meseta.**
La red de seguridad es técnica (20 % de fallas acumulado desde el inicio), no un umbral del SLA, y la capacidad no la decide k6: la calcula el análisis por ventanas de 30 s. Cuando cortó, la rodilla ya estaba pasada (última ventana que cumple con 876 simultáneos, primera falla sostenida con 946, y k6 cortó unos 3,8 min después de la primera ventana con fallas); lo que se perdió es la meseta y la foto de hilos con 1 CPU, por eso la de las 40 plazas es de la corrida con 2 CPU.
Lo sostiene: `tests/performance/resultados/estres/20261111-1940/veredicto.md:31`, `:40` · `tests/performance/README.md:124` · `tests/performance/resultados/escalabilidad/20261111-2103/hilos_meseta.txt` · `docs/Informe_Rendimiento_Qolqe.pdf`, §6 (pág. 16-17).

**5. La hipótesis de capacidad (1 500 ± 300) quedó refutada por los 850.**
Una hipótesis escrita antes de medir está para eso, y la dejé escrita como refutada. La había calculado suponiendo que el cuello era el CPU del PBKDF2; la medición confirmó que es el mayor consumo, pero no el disparador: el colapso llega con Qolqe al 75,5 % de CPU, es brusco, 2 CPU dan × 1,53 y no × 2, y 733 de las 829 excepciones son el bloqueo de SQLite en el INSERT de la sesión.
Lo sostiene: `tests/performance/resultados/estres/20261111-1940/veredicto.md:31`, `:42` · `tests/performance/resultados/escalabilidad/20261111-2103/veredicto.md:31` · `docs/informe.md:226`, `:239`, `:243` · `docs/Informe_Rendimiento_Qolqe.pdf`, §8, Tabla 14 (pág. 38).

**6. La laptop estaba compartida con procesos de macOS.**
El CPU total del equipo pasó del 80 % en ventanas del pico (90,2 %) y del estrés (82,3 %), siempre por procesos de macOS y nunca por k6, que no pasó de 1,7 % por ventana en ninguna corrida. En el estrés fue en el minuto 2,25, con 100 usuarios y lejos de la rodilla; en el pico coincidió con el login subiendo de ~85 a 145 ms, lejos de los 1 600 permitidos.
Lo sostiene: `tests/performance/resultados/pico/20261111-1918/veredicto.md:13` · `tests/performance/resultados/estres/20261111-1940/veredicto.md:13` · `docs/Informe_Rendimiento_Qolqe.pdf`, §5 (pág. 14) y §6 (pág. 16).

**7. Es una línea base relativa, no la capacidad de producción.**
Lo digo antes de que lo pregunten: es Qolqe en 1 CPU y 1 GB dentro de una laptop. Sirve para comparar versiones y configuraciones, como 1 contra 2 CPU, y para ubicar el primer cuello de botella; no se extrapola a producción.
Lo sostiene: `docs/informe.md:337` · `tests/performance/README.md:42` · `docs/Informe_Rendimiento_Qolqe.pdf`, §6, «Línea base relativa» (pág. 17).

**8. k6 y Qolqe corrieron en la misma laptop.**
La clase 13 dice que generar la carga desde la misma máquina distorsiona las mediciones, y por eso está declarado como limitación. Lo que lo controla: Qolqe va con una cuota de 1 CPU, la referencia de 1 VU se mide en Docker (V-06) y V-01 vigila el CPU de k6, que no pasó de 1,2 % por ventana en la carga y el estrés ni de 1,7 % en ninguna corrida.
Lo sostiene: `docs/Informe_Rendimiento_Qolqe.pdf`, §6, «Limitaciones conocidas» (pág. 16) · fila V-01 de `tests/performance/resultados/carga/20261111-1833/veredicto.md:12` y de `tests/performance/resultados/estres/20261111-1940/veredicto.md:12` · lámina 4, tarjeta de abajo.

**9. La capacidad de 850 no se confirmó a carga constante.**
850 sale de las ventanas de 30 s de una rampa. La corrida que la confirmaría sostenida, `L_CAP=850`, era opcional y no se ejecutó: queda como recomendación, junto a repetir el estrés tras cada corrección.
Lo sostiene: `docs/Informe_Rendimiento_Qolqe.pdf`, §6, «Diferencias entre el plan y la ejecución real» (pág. 17) y §8 (pág. 41).

**10. El pico sostuvo los 300 simultáneos unos 3 minutos, no los 15 de la campaña.**
El requerimiento dice «el triple de usuarios» y lo tomé como máximo (S-07): ~300 de 12:02 a 12:05. Si el triple durara los 15 min, la evidencia más cercana es el estrés: estuvo 6 min seguidos por encima de 300 simultáneos con p95 de consultas ≤ 76 ms, dinero ≤ 126 ms y 0 % de error, lejos de los 1 600 / 3 000 ms de U-06.
Lo sostiene: `docs/Informe_Rendimiento_Qolqe.pdf`, S-07 (pág. 13) y §8 (pág. 38) · `docs/informe.md:224` · `tests/performance/resultados/estres/20261111-1940/ventanas.csv`.

El rendimiento fuera del pipeline no es una limitación declarada sino una decisión: se defiende en `banco-preguntas.md`, pregunta 13.
