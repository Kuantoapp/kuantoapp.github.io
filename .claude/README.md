# Agentes y skills del proyecto

Índice central de los subagentes y skills de Claude Code que usa el equipo, y reglas para añadirlos.
La CI (`.github/scripts/validar_claude.py`) comprueba que todo lo de esta carpeta cumple estas reglas y aparece en el índice.
Claude Code no carga este fichero: es para las personas y para revisar los PR.

## Uso en equipo

Todo lo de `.claude/` está versionado: quien abra Claude Code en este repo tiene los mismos agentes, skills, permisos y hooks. Para que de verdad sea igual para los tres:

1. **Primera vez:** `git pull`, abre `claude` en la raíz del repo y acepta el diálogo de confianza. Sin eso no se activan los hooks ni los permisos `allow` (los `deny` sí, desde el principio). Instala `ruff` y `jq` para que funcione el hook.
2. **Comprueba** que ves los del índice: `/agents` lista los agentes y escribir `/dm-` lista las skills.
3. **Usa los del proyecto, no tus copias.** Si una skill personal de `~/.claude/skills/` se llama igual que una del proyecto, gana la personal. Por eso todo lo del proyecto empieza por `dm-`. Si mejoras algo, hazlo en el repo con un PR, no en tu copia.
4. **Lo personal no se comparte:** tu `~/.claude/CLAUDE.md` y `CLAUDE.local.md` se suman a `AGENTS.md`. No metas ahí reglas que contradigan las del proyecto.
5. **Tras un pull que cambie `.claude/`:** los agentes y skills editados se recargan solos. Si aparece una carpeta nueva, ejecuta `/reload-skills` o reinicia `claude`.

## Índice

<!-- Una fila por agente o skill. La CI falla si falta alguno o sobra una fila. -->

| Nombre | Tipo | Origen | Para qué |
|---|---|---|---|
| `dm-cartografia` | skill | proyecto | CRS, uniones por código oficial, tablas de paso de código postal y mapas de la demo |
| `dm-eda-espacial` | skill | proyecto | Exploración espacial: W, Moran y LISA (también bivariantes), mapas de caja y tasas con Bayes empírico |
| `dm-modelado-espacial` | skill | proyecto | Imputar, predecir y explicar: validación A o B, `Wy` sin fuga, selección espacial de variables, intervalos por grupo, equidad del error, regresión espacial |
| `dm-calculos-normativos` | skill | proyecto | Cálculos que aplican una norma o tarifa: bruto a neto (Seguridad Social e IRPF de Madrid), SMI, IPREM, IMV, umbrales de pobreza y sobrecarga, ayudas al alquiler, tarifas de transporte y valor del tiempo, con parámetros citados y casos de referencia |
| `dm-auditor-calculos-normativos` | agente | proyecto | Auditoría estricta (sin corregir) de esos cálculos contra la fuente primaria vigente, con tabla de parámetros, casos de test propuestos y veredicto. Precarga `dm-calculos-normativos` |
| `dm-revisor-espacial` | agente | proyecto | Revisión estricta (sin corregir) de cartografía, exploración, modelos e interpretación, con veredicto APTO, APTO CON RESERVAS o NO APTO. Precarga las tres skills espaciales |

Tipo: `agente` o `skill`. Origen: `yeray`, `izan` o `proyecto` (hecho para este repo).

## Principios de diseño

Cada agente y skill existe para que los bucles agénticos sean **baratos, precisos y autónomos sin perder calidad ni seguridad**. Un PR que añada o cambie uno debe cumplir:

| Principio | Cómo se cumple |
|---|---|
| **Barato** | La descripción solo se activa cuando toca (casos concretos y para qué *no* es). `SKILL.md` corto; el detalle en `referencia/`, que solo se lee si hace falta. Agentes con `tools` mínimas y el modelo adecuado a la tarea: el coste que cuenta es el total, y uno que acierta a la primera evita repeticiones. Salidas cortas y con estructura fija |
| **Preciso** | Procedimiento paso a paso, no consejos sueltos. Cada resultado se contrasta con lo que debe dar (teoría, valores de control, segunda vía) antes de aceptarlo |
| **Autónomo** | Lee el estado del proyecto (`docs/decisiones.md`, `data/README.md`, `src/`) en lugar de preguntar lo que ya está escrito. Condición de parada clara: cuándo terminar, cuándo preguntar |
| **General** | Nada atado a una idea o a datos concretos: los ejemplos son orientativos y lo específico se lee del proyecto |
| **Seguro** | Sin permisos de más; los efectos (push, PR, borrar) solo con `disable-model-invocation: true` o con aprobación; lo que no puede fallar, en `deny` o hooks |
| **Verificable** | Termina en algo comprobable: un test, una salida, un veredicto con evidencia |

## Dónde va cada cosa

| Necesito… | Usa | Ubicación |
|---|---|---|
| Un hecho o una regla que Claude debe tener en cada sesión | `AGENTS.md` (lo importa `CLAUDE.md`) | raíz |
| Una regla que solo aplica a parte del repo | regla con `paths` | `.claude/rules/<tema>.md` |
| Un procedimiento de varios pasos (PR, descargar datos, preparar demo) | skill | `.claude/skills/<nombre>/SKILL.md` |
| Una tarea delegable con su propio contexto y herramientas limitadas (revisar, auditar, explorar) | subagente | `.claude/agents/<nombre>.md` |
| Algo que **nunca** debe pasar | regla `deny` o hook, no texto | `.claude/settings.json` |
| Preferencias personales | `CLAUDE.local.md` (no se versiona) | raíz |

`.claude/commands/` está prohibido: las skills lo sustituyen y admiten ficheros de apoyo.

## Reglas para subagentes (`.claude/agents/<nombre>.md`)

1. El fichero se llama igual que `name`, con prefijo `dm-`, en minúsculas y con guiones: `dm-revisor-datos.md` → `name: dm-revisor-datos`.
2. `name` y `description` son obligatorios. La `description` dice **cuándo** delegar en él, en una o dos frases (máx. 500 caracteres). Si debe usarse sin pedirlo, incluye "Úsalo de forma proactiva…".
3. `tools` es obligatorio y mínimo: solo lo que necesita. Un revisor no lleva `Edit` ni `Write`.
4. Una sola responsabilidad por agente. Si hace dos cosas, son dos agentes.
5. `model` según la tarea: `opus` para razonar, diseñar, modelizar o revisar con criterio (los revisores, siempre); `sonnet` para implementar o ejecutar procedimientos ya definidos; `haiku` solo para búsquedas o resúmenes mecánicos. Nada de `permissionMode: bypassPermissions`.
6. El cuerpo es su prompt de sistema completo: el subagente no ve la conversación ni el prompt de Claude Code. Pide que devuelva un resumen corto.
7. Solo campos documentados (la CI rechaza los demás, porque Claude Code los ignora sin avisar).

## Reglas para skills (`.claude/skills/<nombre>/SKILL.md`)

1. La carpeta se llama como la skill, con prefijo `dm-`, en minúsculas y con guiones (`dm-abrir-pr`). Si pones `name`, debe coincidir con la carpeta.
2. `description` obligatoria: primero el caso de uso, con las palabras que diría alguien del equipo. `description` + `when_to_use` ≤ 1.536 caracteres.
3. `SKILL.md` de menos de 500 líneas. El detalle va en ficheros de apoyo dentro de la carpeta (`referencia.md`, `scripts/…`), enlazados desde `SKILL.md`.
4. Skills con efectos (push, abrir PR, borrar datos, desplegar) llevan `disable-model-invocation: true`: solo se lanzan a mano con `/<nombre>`.
5. `allowed-tools` solo con lo que la skill necesita.

## Cómo añadir uno

1. Rama `<usuario>/claude-<nombre>` y PR como cualquier otro cambio.
2. Fichero nuevo + fila en el índice.
3. Si viene de tu `~/.claude/`, cópialo y adáptalo: quita rutas y datos personales y pon `Origen` a tu nombre.
4. Todo lo de `.claude/` lo aprueba @yeraybc (CODEOWNERS).
