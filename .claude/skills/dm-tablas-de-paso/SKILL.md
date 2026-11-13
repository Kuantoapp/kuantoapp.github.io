---
description: "Construye, comprueba y aplica tablas de paso entre unidades territoriales que no coinciden (código postal, sección censal de un año u otro, barrio, distrito, municipio, zona de transporte, rejilla): anidamiento, pesos por población, viviendas o portales, variables extensivas frente a intensivas, totales conservados e incertidumbre del reparto. No carga ni reproyecta capas (dm-cartografia) ni explora patrones (dm-eda-espacial)."
when_to_use: "El dato viene por código postal y lo necesito por sección o barrio; pasar secciones de 2021 a las de 2025; agregar secciones a distritos; ¿estas unidades anidan?; ¿reparto por área o por población?; ¿cómo paso una renta media o una mediana?; el total no cuadra tras el paso; ¿cuánto me puedo fiar del valor de este barrio?"
---

# Tablas de paso entre unidades

Una tabla de paso dice qué parte de cada unidad de origen cae en cada unidad de destino. Si los pesos están mal, cada cifra que pasa por ella está mal sin que nada falle: hay que construirla con método y comprobarla siempre.

## Antes de empezar: conectar con el desarrollo del proyecto

1. **Qué unidades:** lee `docs/decisiones.md` (unidad de análisis y de presentación, año de la cartografía). Si no está decidido, pregunta; si supones, escríbelo.
2. **Qué hay hecho:** reutiliza tablas y funciones existentes antes de crear otra:
   `grep -rnE "tabla_paso|crosswalk|overlay|peso" src tests`.
3. **Qué capas:** las geometrías de origen y destino, y la variable auxiliar para los pesos, documentadas en `data/README.md` (si falta alguna, `dm-nueva-fuente`). Cargarlas y reproyectarlas es de `dm-cartografia`.

## Flujo

1. **¿Anidan?** Si cada origen cae entero en un destino (secciones en distritos o en municipios), no hace falta reparto: se agrega por el código. Compruébalo siempre con la superposición, no lo supongas: anida si la fracción mayor de cada origen es ≥ 0,99.
2. **¿Hay una correspondencia oficial?** Antes de construirla, busca si el publicador la da y confírmalo con `dm-verificacion-fuentes`. Para el seccionado, el INE no publica una correspondencia entre secciones de años distintos (no encontrada el 2026-11-13): sí la geometría de cada año y, con cada callejero del censo electoral, un fichero de variaciones respecto al anterior.
3. **Si no anidan, elige el peso**, de mejor a peor:
   - **Puntos** con la unidad de destino y de origen (portales, edificios con viviendas): se cuentan los puntos de cada par.
   - **Dasimétrico:** variable auxiliar (población en rejilla, viviendas) repartida en cada pieza de la superposición.
   - **Área:** solo si no hay nada más, y se declara como supuesto fuerte (supone población uniforme, falso en cuanto hay parques, polígonos o vías).
4. **Construye la tabla** `origen, destino, peso, peso_destino` y la **cobertura** de cada origen con la superposición en un CRS métrico (EPSG:25830 en la España peninsular), los códigos como texto y el **mismo año** de cartografía que el dato.
5. **Aplícala según el tipo de variable** (fórmulas en [metodos-y-controles.md](referencia/metodos-y-controles.md)):
   - **Extensivas** (recuentos, sumas: personas, hogares, euros totales): se reparten con `peso` (suma 1 en cada **origen**).
   - **Intensivas** (tasas, medias, porcentajes): se recalculan desde su numerador y su denominador extensivos. Si solo hay la tasa, media ponderada con `peso_destino` (suma 1 en cada **destino**).
   - **Medianas y percentiles** no se pueden pasar exactamente: valor aproximado marcado como «estimado», o microdatos.
6. **Comprueba** los controles de abajo. Si alguno falla, se corrige antes de usar la tabla.
7. **Mide la incertidumbre:** la **pureza** de cada destino (parte de su peso que viene de orígenes enteros, sin repartir). Un valor de un destino con pureza baja es una estimación y se presenta como tal.

## Contrastar cada resultado con lo que debe salir

Todos, cada vez:

| Comprobación | Lo correcto | Si no se cumple |
|---|---|---|
| Suma de `peso` por origen y de `peso_destino` por destino | 1 (tolerancia 1e-6), sin `NaN` | Piezas perdidas, duplicadas, mal normalizadas u orígenes sin auxiliar |
| Cobertura de cada origen (lo que cae en algún destino) | ≥ 0,99, o explicada | Parte del origen fuera del ámbito: su valor inflaría los destinos que toca. Se decide caso a caso ([cobertura](referencia/metodos-y-controles.md#cobertura)) |
| Total de una variable extensiva antes y después | Igual | Pesos o uniones mal |
| Orígenes sin destino y destinos sin origen | Ninguno, o cada uno explicado (fuera del ámbito, mar, otro municipio) | Límites de fuentes distintas, años distintos, CRS distinto |
| Piezas astilla (diminutas respecto al origen, por bordes que no coinciden) | Eliminadas (umbral relativo al origen), contadas y pesos renormalizados | Pesos residuales que reparten en destinos vecinos |
| Número de destinos | El del ámbito oficial | Ver `dm-cartografia` |
| Segunda vía | Un total oficial del destino (por ejemplo, población por distrito publicada) se parece al reconstruido | El peso no representa bien lo que se reparte |

Código de los controles y de la pureza en [metodos-y-controles.md](referencia/metodos-y-controles.md). Va a `src/` como función con su test. Errores frecuentes, al final de esa referencia.

## Casos frecuentes

- **Código postal:** responde a la logística del reparto, no a un marco estadístico, y sus límites no forman parte de la cartografía estadística oficial. La capa de polígonos es de Correos y el CNIG solo puede mostrarla, no darla en descarga (convenio CNIG-Correos, BOE-A-2023-11522, cláusulas 2.ª y 4.ª; comprobado el 2026-11-13). El mejor peso son los portales con su código postal: CartoCiudad los trae (campo `cod_postal` de la capa `portalpk_publi`, CC BY 4.0, descarga por provincia en el CNIG). Los tramos del callejero del INE traen sección y, según el diseño de 1997, código postal (verificar en el diseño actual). Cualquier capa de polígonos de código postal en descarga es una aproximación no oficial: declara cuál usas.
- **Seccionado de años distintos:** las secciones se dividen, se fusionan y a veces reutilizan un código con otra geometría. Nunca unas años distintos por el código sin comprobar la geometría: superpón las dos capas con pesos de población.
- **Zonas de transporte o rejillas:** igual que cualquier unidad que no anida. Para rejillas de población, la propia rejilla es el peso.

## Al terminar: dejar el trabajo conectado

- La tabla se guarda en `data/processed/` con columnas `origen, destino, peso, peso_destino, metodo` y la función que la construye va a `src/`, con un test de los controles (suma de pesos y total conservado) sobre un ejemplo pequeño.
- El método, la variable auxiliar y su año, y las zonas excluidas, en `docs/decisiones.md`; en la nota metodológica, el supuesto y la pureza de los destinos que se presentan.
- Antes de usarla en resultados o de abrir el PR, revisión de `dm-revisor-espacial` (obligatoria si el código usa geometrías).

## Python

Funciones de [metodos-y-controles.md](referencia/metodos-y-controles.md), listas para copiar a `src/`:

| Tarea | Función |
|---|---|
| Tabla por área, dasimétrica o por puntos (con cobertura) | `tabla_paso_area`, `tabla_paso_dasimetrica`, `tabla_paso_puntos` |
| Pasar una extensiva | `pasar_extensiva` |
| Controles y pureza | `comprobar_tabla`, `pureza` |

Si el equipo prefiere una librería, `tobler` (PySAL) hace interpolación areal y dasimétrica; no está en el proyecto y añadirla exige justificarla en el PR.
