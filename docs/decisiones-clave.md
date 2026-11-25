# Decisiones clave

Las decisiones que dan forma a Kuanto, en lenguaje llano y agrupadas por tema. Es la forma corta de entender por qué el proyecto es como es. El [registro de decisiones](decisiones.md) tiene cada una completa, con su motivo, sus alternativas y su PR, ordenadas por fecha: para encontrar una, busca su fecha y el texto en negrita que la abre.

## La idea

- **Qué se construye (2026-11-14).** Entre las ideas valoradas, el equipo eligió una herramienta que calcula lo que sobra al mes en cada zona según el sueldo, el alquiler y el transporte. La ficha de la idea pasó antes por una revisión adversaria que buscaba sus puntos débiles. Las fichas descartadas están en [`ideas/`](../ideas/).
- **El nombre (2026-11-20).** El proyecto se llama Kuanto. «¿Me sobra?» fue el nombre de trabajo, y de ahí viene el nombre del paquete de Python, `mesobra`.

## Los datos

- **Primero el catálogo de la Comunidad (2026-11-14).** Lo que publica el portal de datos abiertos de la Comunidad de Madrid se descarga de ahí. Solo se va a la fuente original si el catálogo no lo tiene o si la original es más reciente o más detallada, y entonces se dice por qué.
- **199 zonas (2026-11-15).** Los municipios y los distritos de Madrid capital. Cada zona se representa por su centro de población, donde vive la gente, y no por su centro geográfico; de ahí salen su corona tarifaria y sus viajes.
- **Sin dato antes que inventado (2026-11-18).** Las zonas sin alquiler publicado siguen sin cifra. Se probó a estimarlas con un modelo, pero no había pruebas suficientes de que acertara en los municipios más pequeños, que son casi todos los que faltan.
- **Lo que no pasa el control no se publica (2026-11-18).** Se construyó un modelo para estimar, zona a zona, cuántos inquilinos dedican más del 40 % de su renta a la vivienda. Antes de fiarse de él, se comparó su total para toda la Comunidad con el de la encuesta oficial del INE. El modelo daba alrededor del 47 % y la encuesta, el 36 %, con un margen de error de 28,6 % a 43,4 % (estimado; fuente: [registro de decisiones](decisiones.md), 2026-11-18; ECV 2025 del INE). Como el modelo se salía de ese margen, no se publica por zona, y el informe da solo la cifra regional de la encuesta.

## El cálculo

- **El neto, con la declaración de la renta (2026-11-15).** Se usa la cuota anual del IRPF, lo que de verdad se paga, y no la retención de la nómina. No se restan deducciones como la de familia numerosa o las autonómicas (por ejemplo, la de Madrid por alquiler), así que, si tienes alguna, tu neto real será igual o mayor que el de Kuanto: el error, si lo hay, va del lado prudente.
- **El alquiler, como si firmaras hoy (2026-11-20).** La cifra principal usa el precio de un contrato nuevo, que suele ser más alto que lo que pagan los inquilinos de siempre. Lo que pagan estos últimos sale como referencia. La horquilla va del alquiler barato al caro de la zona.
- **El transporte, por la ruta real (2026-11-15 y 2026-11-18).** Se busca el título más barato para el recorrido de cada persona, con las coronas que cruza y los descuentos de su colectivo (joven, familia numerosa, discapacidad).
- **Tiempos de viaje con r5py (2026-11-15).** Se calculan con los horarios reales del Consorcio de Transportes. Las líneas que el Consorcio publica sin horarios se reconstruyen y se marcan como estimadas.
- **El coche, sin tráfico (2026-11-20).** Se usa el coste por kilómetro que Hacienda acepta sin tributar, sin aparcamiento ni peajes. No hay una fuente pública de atascos, así que el tiempo en hora punta sale corto, y se avisa.
- **La cesta, con la media de Madrid (2026-11-20).** Por defecto se usa el gasto medio de los hogares de Madrid. Hay un escenario aparte con la cesta de cada tramo de ingresos.

## La publicación

- **Sin servidor (2026-11-14).** Python para el cálculo y una web estática que hace la última cuenta en el navegador. No hace falta base de datos, y el sueldo de nadie sale de su dispositivo.
- **Datos abiertos con licencia (2026-11-16, 2026-11-20 y 2026-11-24).** Lo que publica Kuanto lleva CC BY 4.0, y ODbL 1.0 lo que deriva de OpenStreetMap, como exige esa licencia. Cada fuente conserva sus condiciones y su cita.
- **Repositorio público (2026-11-21).** El código y los datos son públicos, y la web se publica en GitHub Pages con cada cambio.
- **Dirección visual (2026-11-21 y 2026-11-24).** En la portada busca convencer; en el mapa y los datos, precisión y calma. Neutros claros, un solo azul de acento y titulares en Instrument Serif. Los colores del mapa se leen respecto a lo que gana cada hogar, con un amarillo para «llega justo» (2026-11-23): que sobren 100 € no significa lo mismo con 1.000 € de neto que con 4.000 €, así que el color mide el sobrante en proporción a tu sueldo y un mismo color dice lo mismo a cualquiera.

## Cómo se trabaja

- **Agentes que escriben, máquinas que revisan (2026-11-12 y 2026-11-13).** Casi todo el código lo escriben agentes de IA. La calidad la aseguran tests, hooks, CI y agentes revisores obligatorios según el área (cálculos normativos, trabajo espacial, cifras públicas, fuentes y código), y la CI no deja mergear sin su veredicto. Las personas deciden. Detalle en [AGENTS.md](../AGENTS.md).
- **Descargas intocables y con huella (2026-11-13).** Cada fuente se guarda tal cual con su SHA-256, y nadie puede editarla. Así todo el equipo trabaja con los mismos ficheros y cualquiera puede comprobarlo.
- **Registro previo (2026-11-18 en adelante).** En los análisis delicados, la regla para dar por bueno un resultado se escribe antes de calcularlo, para que el resultado no pueda mover la regla. Es como fijar la nota de aprobado antes de corregir el examen, y no después de ver qué ha sacado cada uno.
