# Prompt: de la ficha «Cerca» al plan de desarrollo agéntico

Prompt para convertir [propuesta-B-unificada.md](propuesta-B-unificada.md) en un plan de desarrollo granular, ejecutable por agentes con la mínima intervención humana. Escrito siguiendo la guía de prompts de Claude Fable 5.2.

## Cómo usarlo

- **Sesión nueva** (o `/clear`) en la raíz del repo: el prompt cambia instrucciones y no debe mezclarse con una conversación previa.
- **Modelo y esfuerzo:** Claude Fable 5.2 (u Opus 5.5) con esfuerzo `high`. Es diseño largo y sin supervisión; sube a `xhigh` solo si la primera pasada deja huecos que `high` no cubre.
- **Rellena antes la sección «Equipo» del bloque** (perfil, horas disponibles y equipo de cada uno). Si la dejas vacía, el agente lo deduce del repo y declara el supuesto, pero el reparto sale peor.
- **Pega todo el bloque de abajo** como primer mensaje.
- **Al aprobar, sé específico.** En lugar de «adelante», responde por ejemplo «Sí, crea las issues de las fases 0 y 1» o «Sí, anota la idea y el stack en `docs/decisiones.md`».

---

````text
# Tarea

Convierte la ficha de la idea «Cerca» (ideas/plan2/idea-definitiva/propuesta-B-unificada.md) en un plan de desarrollo tan detallado que cada pieza la pueda ejecutar un agente sin contexto previo, de principio a fin, y que el equipo humano solo tenga que supervisar y decidir. El equipo ha elegido esta idea para DataMad 2026.

El resultado no es código: es el plan, con sus fases, sus unidades de trabajo listas para convertirse en issues, los contratos de datos entre fases y el calendario hasta la presentación. Lo construyes sobre la estructura agéntica que ya tiene el repo (AGENTS.md, .claude/, .github/), sin inventar otra.

El plan también reparte el trabajo entre las dos personas que lo van a llevar, Izan y Yeray, de la forma que antes lleve el producto al 26/11 con calidad. Además dice qué se hace en paralelo, pero solo donde paralelizar compensa de verdad.

# Equipo

<!-- Rellena lo que sepas. Lo que quede vacío, el agente lo deduce del repo y lo declara como supuesto. -->
- Izan (GitHub: izan-diaz). Perfil y fuertes: … · Horas disponibles por día hasta el 26/11: … · Equipo y sistema operativo: …
- Yeray (GitHub: yeraybc). Perfil y fuertes: … · Horas disponibles por día hasta el 26/11: … · Equipo y sistema operativo: …

Cada persona dirige varios agentes a la vez, cada uno en su worktree. Lo que limita es la atención de la persona: supervisar, decidir y revisar PR. Su capacidad para escribir código no es el límite.

Antes de empezar, di en una línea qué vas a hacer. Cada pocas llamadas a herramientas, da una actualización de una línea sobre dónde estás.

# Contexto que debes leer primero

Lee en este orden y solo lo necesario (busca con grep antes de abrir ficheros enteros):

1. AGENTS.md: el bucle agéntico, ramas y worktrees, tamaño de PR, revisores obligatorios, cifras con fuente, data/raw inmutable, documentación al día.
2. docs/decisiones.md: decisiones tomadas, decisiones pendientes y fechas clave (congelación de datos el 2026-11-22, presentación el 2026-11-26).
3. .claude/README.md: índice de skills y agentes `dm-*`, qué hace cada uno y sus reglas.
4. La ficha completa, incluidos los anexos B (registro de decisiones y correcciones del abogado del diablo), C (glosario) y D (fuentes).
5. data/README.md, .github/pull_request_template.md y .github/scripts/ por encima, para saber qué comprueba la CI.

src/ y app/ están vacíos: el plan parte de cero en código, pero no en reglas ni herramientas.

# Qué es fijo y qué decides tú

La ficha separa lo que define la idea de lo que es enfoque de partida. Respeta esa frontera:

- **Fijo:** los siete puntos de «Lo que define la idea» (necesidad y cercanía medidas por separado, la media esconde, personas y perfiles concretos, diagnosticar-proponer-medir el valor del detalle, el PIR 2027-2031 como decisión, datos abiertos con el catálogo regional en el centro, honestidad con los límites). Si el plan obliga a cambiar uno, no lo cambies: déjalo como pregunta para el humano.
- **Lo decides tú, como dueño del plan:** el desglose en fases y unidades, el orden, los contratos de datos, la estructura de módulos de src/ y app/, qué se paraleliza, los criterios de aceptación y el reparto de modelos. Si un método de partida de la ficha tiene un problema, propón la alternativa en el plan con su motivo.
- **Lo decide el humano:** lo que la ficha y docs/decisiones.md dejan pendiente (stack definitivo, bases del concurso) y los puntos de control de la sección «Puntos de decisión humana». Para cada uno, el plan propone una opción recomendada con su motivo, para que decidir sea elegir, no pensar desde cero.

No modifiques la ficha ni nada de .claude/, .github/, AGENTS.md o CLAUDE.md: son de otras tareas y requieren su propio PR. Si ves algo que cambiar ahí, anótalo en el plan como unidad o como propuesta.

# Análisis por roles

Antes de desglosar, analiza la ficha desde cada uno de estos roles. Cada preocupación de un rol tiene que acabar convertida en una unidad de trabajo, un criterio de aceptación, un contrato o un riesgo del plan, no en prosa suelta. Incluye en el plan una tabla «Rol → qué aporta → dónde queda en el plan».

- **Data scientist:** índice por sección (winsorize, z-score, Monte Carlo con pesos Dirichlet, agregación geométrica), quintiles ponderados por población, descomposición entre y dentro, Theil, referencia nula por tamaño de zona, índice de concentración con bootstrap, curva de valor de la información, validación externa (esperanza de vida, IGUALA, prueba temporal, validez convergente fuera de la capital).
- **Ingeniero de datos:** descargas reproducibles (skill dm-nueva-fuente), lo que se congela el 22/11, formatos intermedios en data/processed/, tiempos de cálculo, procesado por municipio y en lotes, reproducibilidad completa desde las fuentes.
- **Analista GIS:** CRS (medir en EPSG:25830, publicar en 4326), tablas de paso entre secciones de distintos años y entre códigos INE y Catastro (28079 frente a 28900), reparto de población a edificios, red peatonal de OSM, pendiente con el MDT del IGN y Tobler, DEGURBA.
- **Investigación operativa:** candidatos (rejilla de 250 m y equipamientos existentes), matrices de tiempos dentro del umbral, voraz de cobertura máxima, dos objetivos, abrir frente a ampliar, tamaño de las matrices en una web estática.
- **Frontend, UX y accesibilidad:** web estática con MapLibre y PMTiles, dos pestañas, buscador sin conexión, carga por municipio bajo demanda, peso de los ficheros, sliders, simulador, accesibilidad de la propia web.
- **Política pública y servicios sociales:** quién decide cada servicio (tabla 4.1), encaje con el PIR, tono de la auditoría, lenguaje sin estigma, variables delicadas.
- **Legal, licencias y privacidad:** CRTM (citas y prohibiciones), ODbL de OSM, Catastro y CartoCiudad por verificar, CC BY 4.0, nada publicado por edificio, la ubicación del usuario no sale del navegador.
- **Datos abiertos e interoperabilidad** (pensando en el jurado: Smart Data Models, APIs, MCP, reutilización): servidor MCP, esquema de Smart Data Models, publicación del conjunto de datos.
- **QA y verificación:** pruebas de referencia Python frente a web, valores de control, trazabilidad de cada cifra (dm-trazador-cifras), revisión espacial (dm-revisor-espacial), revisión de código (dm-revisor-codigo), seguridad (dm-revisor-seguridad).
- **Comunicación y pitch:** relato estrecho de la sección 14, guion, demo en directo, cifras con fuente, dm-humanizar.
- **Dirección del proyecto:** camino crítico, reparto entre Izan y Yeray, carriles en paralelo, qué cae primero si no llega (orden de la sección 14), calendario hasta el 26/11.

# Verificaciones que cambian la forma del plan

Algunas marcas «(verificar)» cambian qué unidades existen o en qué orden (por ejemplo: si la zonificación sanitaria está en abierto, si existe la tabla del Plan de Actuación del PIR, la licencia del Catastro, el id de la tabla de renta del ADRH, si r5py admite pendiente). Resuelve solo esas, delegando en el agente dm-verificador-fuentes. Lánzalas juntas en paralelo, en una o dos tandas, y pide a cada una un resumen corto con estado y evidencia. Las demás marcas no se resuelven ahora: se convierten en unidades de la fase 0 del plan.

La ficha tiene pendiente repetir la revisión de dm-abogado-del-diablo. No la repitas sobre la ficha. Al final, pasa el plan por dm-abogado-del-diablo (ver «Cierre»).

Cada subagente cuesta tokens y arranca sin contexto. No lances otros salvo que separen contexto de verdad o trabajen en paralelo; el resto lo haces tú.

# Qué debe contener el plan

## Estructura de ficheros

Escribe el plan en docs/plan-cerca/ (compartido, versionado):

- README.md: resumen en una pantalla, tabla de roles, mapa de fases, grafo de dependencias (texto o Mermaid), reparto entre Izan y Yeray, carriles en paralelo, calendario día a día del 2026-11-14 al 2026-11-26 con una columna por persona, puntos de decisión humana, riesgos y orden de caída.
- contratos.md: los contratos de datos entre fases (ver abajo). Es lo primero que se mergea, porque es lo que permite trabajar en paralelo sin pisarse.
- fases/NN-<nombre>.md: una por fase, con sus unidades de trabajo completas.

Si alguna estructura distinta es claramente mejor, úsala y explica por qué en el README.

## Fases

Parte del orden por capas de la sección 14 de la ficha y añade lo que falta para que un agente pueda ejecutarlo:

- **Fase 0, cimientos:** propuesta de stack (para decisión humana), estructura de módulos de src/ y app/, contratos de datos, dependencias en requirements.txt, descargas de todo lo que se congela el 22/11 con dm-nueva-fuente, diccionarios de datos con dm-diccionario-datos, verificaciones pendientes y la prueba de rendimiento de r5py o pandana en un municipio.
- **Fases 1 a 9:** las nueve capas de la sección 14, cada una partida en unidades.
- **Fase final, congelación y presentación:** congelación de datos y cálculos el 22/11, ejecución completa del pipeline, trazado de todas las cifras visibles, ensayo de la demo, guion, nota metodológica e informe.

Cada fase dice qué entrega, qué demo funciona al terminarla (para que siempre haya algo que enseñar) y qué se pierde si se recorta.

## Contratos de datos

Para cada artefacto que una fase entrega a otra: ruta en data/processed/, formato, columnas con tipo y unidad, clave (por ejemplo código de sección de 10 dígitos más año), CRS si es geográfico, cardinalidad esperada, función de src/ que lo produce y funciones que lo consumen. Incluye también la firma de las funciones públicas de src/ que usan varias unidades. Si dos unidades en paralelo cumplen el contrato, deben poder integrarse sin hablar entre ellas.

## Unidades de trabajo

Cada unidad es una issue y un PR de menos de 400 líneas (la CI falla por encima de 800). Escribe el cuerpo de cada unidad como el brief completo para un agente que no ha visto nada de esta conversación ni de la ficha: con él debe poder hacer la unidad entera sin preguntar. Usa siempre esta plantilla:

```
### U<fase>.<n> · <tipo(área): qué cambia>
- Responsable: Izan | Yeray   · Rama: <izan-diaz|yeraybc>/<tema-corto>
- Depende de: U…, U…   · Bloquea a: U…   · ¿Camino crítico?: sí | no
- Carril: <nombre>   · Ficheros que toca: <lista cerrada>
- En paralelo con: U… (motivo) | Secuencial: <por qué no compensa paralelizar>
- Modelo y esfuerzo: <opus|sonnet|haiku> · <low|medium|high>   · Motivo: …
- Skill del área: dm-…   · Revisores obligatorios: dm-… (según AGENTS.md)

Objetivo: una frase.
Contexto mínimo: lo que el agente necesita saber de la idea, con el enlace a la sección de la ficha.
Entradas: ficheros y contratos que consume.
Salidas: ficheros, funciones (firma) y contratos que produce.
Pasos: numerados y concretos.
Criterios de aceptación (comprobables por máquina):
  - comando o test que debe pasar;
  - valores de control con lo que deben dar (rangos, teoría, totales que cuadran, una segunda vía);
  - qué cifra o mapa se compara y contra qué.
Supuestos que puede tomar solo: …  (y que deja escritos en el código y en docs/decisiones.md si afectan a otros)
Cuándo parar y preguntar: …
Si no llega a tiempo: qué versión reducida vale y cómo se declara.
```

Los criterios de aceptación son lo que más autonomía da: tienen que permitir que el agente sepa sin humano si ha terminado bien. Ejemplos del tipo que busco: la población sumada de las secciones de un municipio coincide con la del Padrón municipal dentro de un margen que fijas; la varianza entre más la varianza dentro iguala la total; el voraz da el mismo resultado que la fuerza bruta en un caso pequeño generado; la web reproduce los casos de referencia de Python; el número de secciones cae en el rango esperado.

## Reparto de modelos

Asigna modelo y esfuerzo por unidad según AGENTS.md: opus para diseñar, modelizar y revisar; sonnet para implementar lo que ya está definido; haiku solo para búsquedas o resúmenes mecánicos. En las unidades que se ejecuten con esfuerzo low o medium, indica que el agente lleve en su prompt un bloque de «terminar la tarea completa» (al final del plan, en el README, deja ese bloque redactado una vez, en español, listo para pegar).

## Reparto entre Izan y Yeray

Reparte para que el producto llegue antes al 26/11, no para que cada uno tenga el mismo número de unidades. Criterios, por orden:

1. **Propiedad por carril.** Cada persona es dueña de carriles enteros (un conjunto de módulos de src/ o de app/ y sus contratos de salida), no de unidades sueltas mezcladas. Así cada uno decide y revisa lo suyo sin esperar al otro, y nadie toca los ficheros del otro.
2. **El camino crítico manda.** Las unidades del camino crítico van a quien tenga hueco antes y encaje mejor con su perfil. La carga de cada persona en los días del camino crítico va equilibrada; fuera de él, importa menos.
3. **Perfil y equipo.** Asigna según la sección «Equipo». Si está vacía, dedúcelo del repo: el historial de git, las skills y agentes que creó cada uno (columna «Origen» de .claude/README.md) y sus fichas en ideas/. Declara lo deducido como supuesto. Los cálculos pesados (r5py, matrices de tiempos, el pipeline completo) van a una sola máquina a la vez, la más adecuada, y su sistema operativo cuenta: r5py necesita Java y en Windows puede dar más problemas.
4. **Revisión cruzada donde aporte.** Cuando una unidad toca un contrato que consume el otro, el otro revisa ese PR. En lo demás bastan los revisores `dm-*`, sin coste de atención humana.
5. **Atención humana limitada.** Cuenta cuántos agentes y PR puede supervisar cada persona por día con sus horas disponibles, y no le asignes más.

Incluye en el README una tabla por persona: sus carriles, sus unidades por día, sus decisiones y los PR del otro que revisa. Añade el punto exacto donde los dos trabajos se integran y qué hace cada uno si el otro se retrasa.

## Paralelización

Paraleliza solo donde compense. Dos unidades van en paralelo si se cumplen todas estas condiciones:
- no tocan los mismos ficheros;
- el contrato que comparten ya está mergeado;
- ninguna necesita el resultado de la otra;
- el tiempo que se gana supera el coste de coordinar e integrar, y el de supervisar un agente más.

Si alguna no se cumple, van en secuencia, y el plan dice por qué en la unidad. Ten en cuenta también los límites reales: un solo cálculo pesado por máquina, data/raw compartido dentro de cada máquina pero descargado en cada una, y que cada revisor `dm-*` cuesta tokens. No paralelices para tener más carriles. Hazlo para acortar el camino crítico o para que nadie se quede parado.

Hay dos niveles, y el plan los distingue:
- **Entre personas:** qué carriles llevan Izan y Yeray a la vez.
- **Dentro de cada persona:** cuántos agentes en worktrees distintos lleva cada uno a la vez, y en qué unidades.

En el calendario, para cada día, di qué corre en paralelo y por qué compensa, qué va en secuencia y por qué, y qué unidades del camino crítico no pueden retrasarse.

## Puntos de decisión humana

Lista cerrada y corta. Para cada uno: qué se decide, quién lo decide (Izan, Yeray o los dos), cuándo hace falta, qué unidades bloquea, la opción recomendada con su motivo y la frase exacta con la que el humano aprueba. Como mínimo: anotar la idea elegida y el stack en docs/decisiones.md, las bases del concurso (criterios, formato, duración), aprobar el plan y la creación de issues, el sí o no de la congelación del 22/11 con el orden de caída, y el guion final. Todo lo que no esté en esta lista lo hacen los agentes sin pedir aprobación: crear ramas y worktrees, descargar fuentes nuevas a data/raw/, escribir código y tests, hacer commits en su rama, lanzar revisores, abrir PR draft y activar el auto-merge.

## Riesgos y orden de caída

Lleva la tabla de riesgos de la sección 15 de la ficha a unidades concretas: para cada riesgo, qué unidad lo detecta, con qué señal y qué unidad o recorte se activa. Respeta el orden de caída de la sección 14 (multimodal, pendiente, perfiles de movilidad reducida y familias, cobertura regional) y que el índice por sección, la vulnerabilidad oculta y la curva de valor no caen.

# Cómo trabajar

- Trabaja en una rama y un worktree propios, según AGENTS.md (por ejemplo <usuario>/plan-cerca). Crea la issue que cierra el PR si no existe.
- Parte el resultado en PR pequeños si pasa de 800 líneas: primero README y contratos, después las fases. Cada PR, draft y con auto-merge, según AGENTS.md.
- La documentación nueva en docs/ no tiene revisor obligatorio. Si alguna fila del plan dice una cifra pública, sigue la regla de cifras con fuente.
- Si una herramienta falla, un comando da tiempo agotado o un resultado viene vacío, diagnostica y sigue por otra vía (reintenta, corrige la petición, usa otra fuente). Si el mismo fallo resiste tres intentos, para y cuenta el diagnóstico.
- No te detengas mientras quede trabajo del plan que no depende de una respuesta humana. Si una decisión está abierta, deja la opción recomendada en el plan y sigue con lo que no depende de ella.
- Para crear las issues en GitHub, espera a que el humano apruebe el plan con una frase explícita: son muchas y cuesta deshacerlas. Hasta entonces, las unidades viven en los ficheros de fases.

# Cierre

1. Pasa el plan completo por dm-abogado-del-diablo y aplica lo que señale. Si da NO APTO, corrige y repite la revisión solo sobre lo cambiado.
2. Ejecuta `ruff check . && pytest -q` y python .github/scripts/docs_al_dia.py si toca, para que la CI no falle por el plan.
3. Abre los PR draft según AGENTS.md.
4. Escribe un informe final pensado para alguien inteligente que no ha visto tus llamadas a herramientas ni los ficheros que abriste. Pon lo clave en las primeras frases: cuántas fases y unidades, cuál es el camino crítico, cómo queda el reparto entre Izan y Yeray y qué se hace en paralelo, qué decisiones humanas hay y cuándo, qué marcas quedaron verificadas y cuáles siguen abiertas, y qué riesgo es el más serio para llegar al 22/11. Usa frases completas y palabras corrientes, sin términos que hayas inventado durante el trabajo. Prosa donde las ideas se conectan; listas solo para elementos separados. Termina con los enlaces a los PR y la frase exacta que el humano debe responder para crear las issues.
````
