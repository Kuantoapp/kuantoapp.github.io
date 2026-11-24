# Mapa de la documentación

Qué documento leer según lo que busques. Si no sabes nada de Kuanto, empieza por el [README](../README.md).

## Por público

| Si eres… | Lee |
|---|---|
| Alguien que quiere saber qué es y cómo se usa | [Cómo funciona](https://yeraybc.github.io/DataMad-hackaton-2026/saber-mas.html), en la web |
| Economista o analista | [Nota metodológica](https://yeraybc.github.io/DataMad-hackaton-2026/metodologia.html) (cálculo, supuestos, límites y validación), [informe de análisis](https://yeraybc.github.io/DataMad-hackaton-2026/informe.html), [verificaciones](verificaciones/) y [registro de decisiones](decisiones.md) |
| Quien reutiliza los datos | [Datos abiertos de Kuanto](../app/datos/LEEME.md) (licencias, cita y diccionario de cada fichero), [fuentes descargadas](../data/README.md) y [diccionarios de los ficheros grandes](datos/) |
| Desarrollador | [Reproducir Kuanto](reproducir.md), [CONTRIBUTING.md](../CONTRIBUTING.md) y [AGENTS.md](../AGENTS.md) |
| Diseñador | La dirección visual está en el [registro de decisiones](decisiones.md) (entradas del 2026-11-21 y 2026-11-24) y las pautas en la skill [`dm-diseno-web`](../.claude/skills/dm-diseno-web/SKILL.md) |

## Qué hay en `docs/`

| Ruta | Qué es |
|---|---|
| [`reproducir.md`](reproducir.md) | Guía para regenerar los datos, ejecutar los tests y usar el asistente MCP |
| [`decisiones.md`](decisiones.md) | Registro de todo lo que ha decidido el equipo, con fecha, motivo y PR. Es un registro de trabajo, extenso y técnico |
| [`verificaciones/`](verificaciones/) | Contraste de fuentes, normas y licencias con el publicador original: qué se comprobó, con qué evidencia y qué se corrigió |
| [`datos/`](datos/) | Diccionarios de columnas de los ficheros descargados más grandes, generados con la skill `dm-diccionario-datos` |
| [`img/`](img/) | Imágenes de la documentación |

## Fuera de `docs/`

| Ruta | Qué es |
|---|---|
| [`app/metodologia.html`](../app/metodologia.html), [`app/saber-mas.html`](../app/saber-mas.html), [`app/informe.html`](../app/informe.html) | Las explicaciones públicas, publicadas con la web |
| [`app/datos/LEEME.md`](../app/datos/LEEME.md) | Referencia de los datos abiertos que publica Kuanto |
| [`data/README.md`](../data/README.md) | Cada fuente descargada: URL, licencia, cómo obtenerla y SHA-256 |
| [`ideas/`](../ideas/) | Fichas de las ideas que se valoraron antes de elegir Kuanto. Es historial: lo vigente es la web y esta carpeta |
| [`.claude/README.md`](../.claude/README.md) | Los agentes, skills y hooks que usa el equipo |
