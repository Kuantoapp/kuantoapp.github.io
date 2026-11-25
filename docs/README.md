# Mapa de la documentación

Qué documento leer según lo que busques. Si no sabes nada de Kuanto, empieza por el [README](../README.md).

## Por público

| Si eres… | Lee |
|---|---|
| Alguien que quiere saber qué es y cómo se usa | [Cómo funciona Kuanto](como-funciona.md), [preguntas frecuentes](preguntas-frecuentes.md), [Kuanto frente a preguntar a una IA](kuanto-frente-a-ia.md) y [glosario](glosario.md) |
| Economista o analista | [Datos y fuentes](datos-y-fuentes.md), [nota metodológica](https://yeraybc.github.io/DataMad-hackaton-2026/metodologia.html) (cálculo, supuestos, límites y validación), [informe de análisis](https://yeraybc.github.io/DataMad-hackaton-2026/informe.html), [verificaciones](verificaciones/README.md) y [decisiones clave](decisiones-clave.md) |
| Quien reutiliza los datos | [Datos y fuentes](datos-y-fuentes.md), [datos abiertos de Kuanto](../app/datos/LEEME.md) (licencias, cita y diccionario de cada fichero), [fuentes descargadas](../data/README.md) y [diccionarios de los ficheros grandes](datos/) |
| Desarrollador | [Arquitectura](arquitectura.md), [trazabilidad](trazabilidad.md), [reproducir Kuanto](reproducir.md), [CONTRIBUTING.md](../CONTRIBUTING.md) y [AGENTS.md](../AGENTS.md) |
| Diseñador | La dirección visual, resumida en [decisiones clave](decisiones-clave.md#la-publicación) y completa en el [registro de decisiones](decisiones.md) (entradas del 2026-11-21 y 2026-11-24), y las pautas en la skill [`dm-diseno-web`](../.claude/skills/dm-diseno-web/SKILL.md) |

## Qué hay en `docs/`

| Ruta | Qué es |
|---|---|
| [`como-funciona.md`](como-funciona.md) | La cuenta de Kuanto en llano, con un ejemplo, qué es «estimado» y lo que no sabe |
| [`kuanto-frente-a-ia.md`](kuanto-frente-a-ia.md) | Prueba con dos asistentes de IA: métricas de error, conclusiones y cómo combinarlos con Kuanto por MCP |
| [`datos-y-fuentes.md`](datos-y-fuentes.md) | Qué fuente aporta cada pieza, de qué año, a qué escala y con qué licencia |
| [`glosario.md`](glosario.md) | Los términos de economía, datos y territorio, en una o dos frases |
| [`preguntas-frecuentes.md`](preguntas-frecuentes.md) | Las dudas más habituales, con su respuesta y dónde ampliarla |
| [`arquitectura.md`](arquitectura.md) | Cómo está construido Kuanto: capas, módulos, web, reglas que no se rompen y tests |
| [`trazabilidad.md`](trazabilidad.md) | Cómo se sigue una cifra hasta su descarga original y cómo comprobarla |
| [`reproducir.md`](reproducir.md) | Guía para regenerar los datos, ejecutar los tests y usar el asistente MCP |
| [`decisiones-clave.md`](decisiones-clave.md) | Las decisiones que dan forma a Kuanto, en llano y por tema |
| [`decisiones.md`](decisiones.md) | Registro de todo lo que ha decidido el equipo, con fecha, motivo y PR. Es un registro de trabajo, extenso y técnico |
| [`verificaciones/`](verificaciones/README.md) | Contraste de fuentes, normas y licencias con el publicador original: qué se comprobó, con qué evidencia y qué se corrigió |
| [`datos/`](datos/) | Diccionarios de columnas de los ficheros descargados más grandes, generados con la skill `dm-diccionario-datos` |
| [`img/`](img/) | Imágenes de la documentación |

## Fuera de `docs/`

| Ruta | Qué es |
|---|---|
| [`app/metodologia.html`](../app/metodologia.html), [`app/saber-mas.html`](../app/saber-mas.html), [`app/informe.html`](../app/informe.html) | Las explicaciones públicas, publicadas con la web |
| [`app/datos/LEEME.md`](../app/datos/LEEME.md) | Referencia de los datos abiertos que publica Kuanto |
| [`data/README.md`](../data/README.md) | Cada fuente descargada: URL, licencia, cómo obtenerla y SHA-256 |
| [`ideas/`](../ideas/README.md) | Fichas de las ideas que se valoraron antes de elegir Kuanto. Es historial: lo vigente es la web y esta carpeta |
| [`.claude/README.md`](../.claude/README.md) | Los agentes, skills y hooks que usa el equipo |
