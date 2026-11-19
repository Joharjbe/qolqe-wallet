# Exposición final · qué hay en esta carpeta

Material de la exposición del sábado 21-nov. Rutas desde esta carpeta.

## El deck

- [`deck.pdf`](deck.pdf): las 23 láminas, una por página de 1920 × 1080, sin notas de orador. Las tres primeras abren: la portada, el contexto de G4 y lo que pidió la profesora; de la 4 a la 7, el foco de la Parte 3 (cuatro láminas); de la 8 a la 23, el consolidado. Se abre con cualquier visor de PDF, a pantalla completa, y no necesita internet.
- [`deck/project/`](deck/project/): la fuente editable. `deck.json` da el orden de las láminas, `deck.css` el estilo común y cada `slides/<id>.html` es una lámina, con sus notas de orador en el `<aside>` del final. Se lee con cualquier editor. Una lámina suelta se abre en el navegador, pero sin `deck.css` ni las fuentes y con las notas a la vista; para verla como lámina, usar `deck.pdf`.
- [`deck/descartadas/`](deck/descartadas/): las láminas que salieron del deck al dejar el foco en cuatro (`p3-flujos`, `p3-capacidad` y `proyecto`). No están en `deck.json` y no se exportan.

**Maquetación:** la primera exportación traía dos defectos del deck: contenido sobre el pie «Entrega final · Pruebas de Qolqe» y cifras grandes a 28 px en vez de 72 px. Se corrigieron en `deck.css` (`section.pie` y `.tarjeta .dato`). `deck.pdf` se volvió a exportar el 19-nov-2026 con el deck de 23 láminas. Medida de nuevo ese día sobre la misma fuente, en esa exportación ningún texto pasa de y = 920 en las láminas con pie, ninguno toca el pie, la letra mínima es 24 px y todas las cifras de las tarjetas (`api`, `web` e `ia-inyeccion`, hoy láminas 11, 12 y 21) salen a 72 px.

El PDF se exportó con el Playwright del repositorio (Chromium, 1920 × 1080), con `deck.css` y las fuentes que declara `deck.json`. Si cambia una lámina, hay que volver a exportarlo igual: una sola página HTML con el CSS base del visor de Slides (cada `<section>` fija en 1920 × 1080 y con `overflow: hidden`), `deck.css` y las fuentes de `deck.json`. Lleva las 23 `<section>` en el orden de `deck.json`, sin sus `<aside>`, y, como el visor, `min-height: 0` en los hijos que crecen dentro de una columna flex. Luego `page.pdf` de ese Chromium, a 1920 × 1080 px, sin márgenes y con fondos.

## Lo que se usa para hablar

Son Markdown: se leen en GitHub o en el editor.

- [`guion.md`](guion.md): qué se dice en cada lámina, en qué minuto y los pasos de la demo.
- [`hoja-demo.md`](hoja-demo.md): qué se corre antes y durante la demo, en qué orden, y cómo servir el respaldo del sitio si no hay red.
- [`guion-patron-90s.md`](guion-patron-90s.md): el recorrido del patrón en el código, del paso de Gherkin al Page Object y al componente. Tiene dos versiones: la de 40 s, que va en la demo de 15 minutos, y la de 90 s, para las preguntas.
- [`guion-capacidad-ia.md`](guion-capacidad-ia.md): la versión larga de las láminas de la capacidad de IA, con su demo sin red.
- [`chuleta-cifras.md`](chuleta-cifras.md): cada cifra de las láminas con el archivo y la línea de donde sale.
- [`banco-preguntas.md`](banco-preguntas.md): preguntas probables, en el orden del deck, con la respuesta y su evidencia.
- [`defensa-limitaciones-p3.md`](defensa-limitaciones-p3.md): las limitaciones que declara la Parte 3 y el archivo que sostiene cada respuesta.

## El diagrama de las tres partes

Está en [`../img/arquitectura-tres-partes.svg`](../img/arquitectura-tres-partes.svg), que se abre en el navegador, y en [`../img/arquitectura-tres-partes.png`](../img/arquitectura-tres-partes.png), para proyectarlo o pegarlo. El SVG pide IBM Plex Sans y JetBrains Mono a Google Fonts; sin internet se ve con Arial y Courier New, y el texto sigue entrando en sus cajas.
