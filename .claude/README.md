# Agentes y skills del proyecto

Índice central de los subagentes y skills de Claude Code que usa el equipo, y reglas para añadirlos.
`.github/scripts/validar_claude.py` comprueba que todo lo de esta carpeta cumple estas reglas y aparece en el índice: un hook lo ejecuta en cuanto un agente edita algo de `.claude/`, `AGENTS.md` o `CLAUDE.md` (y le devuelve los errores para que los corrija), y la CI lo repite en cada PR.
Claude Code no carga este fichero: es para las personas y para revisar los PR.

## Uso en equipo

Todo lo de `.claude/` está versionado: quien abra Claude Code en este repo tiene los mismos agentes, skills, permisos y hooks. Para que de verdad sea igual para los tres:

1. **Primera vez:** `git pull`, prepara el entorno (`uv venv && uv pip install -r requirements-dev.txt`, ver el README del repo), abre `claude` en la raíz del repo y acepta el diálogo de confianza. Sin eso no se activan los hooks ni los permisos `allow` (los `deny` sí, desde el principio). Instala también `jq`. Al abrir sesión, un hook (`.claude/hooks/entorno.py`) avisa si falta algo y dice cómo arreglarlo, y otro (`.claude/hooks/contexto.py`) da a Claude el estado del proyecto: próximos hitos con los días que faltan, decisiones pendientes, marcas «(verificar)» abiertas y descargas de `data/README.md` que faltan en tu equipo. En Windows, ver «Windows» más abajo.
2. **Comprueba** que ves los del índice: `/agents` lista los agentes y escribir `/dm-` lista las skills.
3. **Usa los del proyecto, no tus copias.** Si una skill personal de `~/.claude/skills/` se llama igual que una del proyecto, gana la personal. Por eso todo lo del proyecto empieza por `dm-`. Si mejoras algo, hazlo en el repo con un PR, no en tu copia.
4. **Lo personal no se comparte:** tu `~/.claude/CLAUDE.md` y `CLAUDE.local.md` se suman a `AGENTS.md`. No metas ahí reglas que contradigan las del proyecto.
5. **Tras un pull que cambie `.claude/`:** los agentes y skills editados se recargan solos. Si aparece una carpeta nueva, ejecuta `/reload-skills` o reinicia `claude`.

### Windows

Claude Code en Windows ejecuta los comandos de los hooks con **Git Bash** (lo instala Git for Windows, que Claude Code ya exige). Los hooks de macOS y Linux siguen igual; en Windows se usan estas versiones:

| Pieza | macOS y Linux | Windows | Qué cambia |
|---|---|---|---|
| Lanzador | `.claude/hooks/py` | `.claude/hooks/py-windows` | `py` detecta Git Bash, MSYS o Cygwin (`uname`) y delega. Busca `.venv/Scripts/python.exe`, después `uv`, `py -3`, `python` y `python3`, y descarta el alias de la Microsoft Store. Fuerza UTF-8. Si existe `<script>_windows.py`, ejecuta ese |
| Formatear `.py` | comando en línea con `jq` | `.claude/hooks/formatear-windows` → `.claude/hooks/ruff_windows.py` | Sin `jq`; ruff de `.venv/Scripts/ruff.exe` |
| `data/raw` inmutable | `.claude/hooks/raw_inmutable.py` | `.claude/hooks/raw_inmutable_windows.py` | Reutiliza el original y añade rutas con `\` y `/c/…`, `python.exe` y `py`, la herramienta **PowerShell** (`Remove-Item`, `Set-Content`, `Copy-Item`, `Invoke-WebRequest -OutFile`, `Expand-Archive -Force`, `[IO.File]::…`, `cmd /c del`, `-EncodedCommand`) y comparte `data/raw` entre worktrees con una unión de directorio, sin permisos de administrador |
| Entorno al abrir sesión | `.claude/hooks/entorno.py` | `.claude/hooks/entorno_windows.py` | Comprueba `.venv/Scripts/*.exe`, no pide `jq` y avisa del alias de la Store |

La herramienta PowerShell de Claude Code no la cubren los matchers `Bash`: `settings.json` tiene además entradas `PowerShell` para `raw_inmutable` (pre y post). En macOS no hacen nada salvo que se active esa herramienta.

Primera vez en Windows, desde Git Bash en la raíz del repo: instala uv (`powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`), ejecuta `uv venv && uv pip install -r requirements-dev.txt` y activa con `source .venv/Scripts/activate`. Si los hooks no se ejecutan (Claude Code no encuentra Git Bash), define `CLAUDE_CODE_GIT_BASH_PATH=C:\Program Files\Git\bin\bash.exe`. `pytest` en Windows omite `tests/test_lanzador.py` (es del lanzador de macOS; ver `tests/conftest.py`) y las pruebas de `tests/test_windows.py` que simulan Windows con scripts `sh` (esas corren en macOS, Linux y la CI). Define también la variable de usuario `PYTHONUTF8=1` (Python 3.14 aún lee los ficheros en cp1252 por defecto en Windows y varios tests fallan con tildes).

## Índice

<!-- Una fila por agente o skill. La CI falla si falta alguno o sobra una fila. -->

| Nombre | Tipo | Origen | Para qué |
|---|---|---|---|
| `dm-cartografia` | skill | proyecto | CRS, uniones por código oficial y mapas de la demo |
| `dm-tablas-de-paso` | skill | proyecto | Pasar datos entre unidades que no coinciden (código postal, secciones de otro año, barrios, zonas de transporte): anidamiento, pesos por población, viviendas o portales, extensivas frente a intensivas, controles y pureza |
| `dm-eda-espacial` | skill | proyecto | Exploración espacial: W, Moran y LISA (también bivariantes), mapas de caja y tasas con Bayes empírico |
| `dm-modelado-espacial` | skill | proyecto | Imputar, predecir y explicar: validación A o B, `Wy` sin fuga, selección espacial de variables, intervalos por grupo, equidad del error, regresión espacial |
| `dm-calculos-normativos` | skill | proyecto | Cualquier cálculo que aplica una norma, tarifa o convocatoria (bruto a neto, indicadores legales, ayudas, precios públicos, impuestos), con parámetros citados a la fuente primaria, casos de referencia y escenarios. Incluye una referencia de 2026 para España y Madrid |
| `dm-auditor-calculos-normativos` | agente | proyecto | Auditoría estricta (sin corregir) de esos cálculos contra la fuente primaria vigente, con tabla de parámetros, casos de test propuestos y veredicto. Precarga `dm-calculos-normativos` |
| `dm-verificacion-fuentes` | skill | proyecto | Cruzar con el publicador original cualquier afirmación sobre datos, normas o licencias: existencia, cobertura, año, nivel territorial, descarga, licencia frente al uso previsto y cifras publicadas, con estados y evidencia reproducible |
| `dm-verificador-fuentes` | agente | proyecto | Verificación estricta de solo lectura (sin `Bash`, `Edit` ni `Write`) de marcas «(verificar)», fuentes nuevas y cifras citadas; propone el texto corregido. Precarga `dm-verificacion-fuentes` |
| `dm-trazador-cifras` | agente | proyecto | Rastrea cada cifra que ve el público hasta el código, la consulta y el dato que la producen; comprueba fuente y marca de estimado. Precarga `dm-verificacion-fuentes` |
| `dm-nueva-fuente` | skill | proyecto | Incorporar o actualizar una fuente de datos de principio a fin: descarga reproducible a `data/raw` con fecha y SHA-256 (script solo stdlib), fila en `data/README.md`, verificación, perfil y carga en `src/` con test; comprueba que todo el equipo tiene los mismos ficheros |
| `dm-diccionario-datos` | skill | izan | Diccionario `<nombre>.DATA.md` de un CSV pesado en `docs/datos/` (tipos, nulos, rangos, muestras, avisos de latin-1 y de formato numérico español) para trabajar sin leer el fichero entero. Solo stdlib |
| `dm-revisor-codigo` | agente | izan | Revisión estricta (sin corregir) de código Python: corrección, fallos silenciosos en pipelines de datos, convenciones del repo, tests y simplicidad. Adaptado de los revisores de ECC |
| `dm-revisor-seguridad` | agente | izan | Revisión de seguridad de solo lectura: secretos, entradas no confiables, SSRF, deserialización, HTML inseguro en la demo, prompt injection y dependencias. Adaptado de `security-reviewer` de ECC |
| `dm-revisor-espacial` | agente | proyecto | Revisión estricta (sin corregir) de cartografía, exploración, modelos e interpretación, con veredicto APTO, APTO CON RESERVAS o NO APTO. Precarga las cuatro skills espaciales |

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
| Algo que **nunca** debe pasar | regla `deny` o hook, no texto | `.claude/settings.json`; el script del hook, en `.claude/hooks/` con su test en `tests/`. En `settings.json` se lanza con `sh "$CLAUDE_PROJECT_DIR/.claude/hooks/py" [--critico] <script>`: usa el Python del proyecto (`.venv` o, si aún no existe, `uv`) y solo como último recurso el `python3` del sistema (el 3.9 de macOS); con `--critico`, si no puede ejecutar el hook y la acción toca `data/raw`, bloquea y explica cómo arreglarlo. Por ese último recurso el script sigue siendo compatible con 3.9: `ruff.toml` lo fija y `tests/test_hooks.py` ejecuta todos los hooks con él; `tests/test_settings.py` comprueba que cada uno está en su evento. Si el hook necesita otra lógica en Windows, va en `<script>_windows.py` junto al original y `tests/test_windows.py` lo prueba |
| Preferencias personales | `CLAUDE.local.md` (no se versiona) | raíz |

`.claude/commands/` está prohibido: las skills lo sustituyen y admiten ficheros de apoyo.

## Reglas para subagentes (`.claude/agents/<nombre>.md`)

1. El fichero se llama igual que `name`, con prefijo `dm-`, en minúsculas y con guiones: `dm-revisor-datos.md` → `name: dm-revisor-datos`.
2. `name` y `description` son obligatorios. La `description` dice **qué hace y cuándo** delegar en él, en dos o tres frases (máx. 400 caracteres, lo valida la CI): el detalle va en el cuerpo, que solo se carga al ejecutarse. Si debe usarse sin pedirlo, incluye "Úsalo de forma proactiva…".
3. `tools` es obligatorio y mínimo: solo lo que necesita. Un revisor, auditor, verificador o trazador no lleva `Edit`, `Write`, `MultiEdit` ni `NotebookEdit` (lo valida la CI). Las skills de `skills:` deben existir y no tener `disable-model-invocation`.
4. Una sola responsabilidad por agente. Si hace dos cosas, son dos agentes.
5. `model` según la tarea: `opus` para razonar, diseñar, modelizar o revisar con criterio (los revisores, siempre); `sonnet` para implementar o ejecutar procedimientos ya definidos; `haiku` solo para búsquedas o resúmenes mecánicos. Nada de `permissionMode: bypassPermissions`.
6. El cuerpo es su prompt de sistema completo: el subagente no ve la conversación ni el prompt de Claude Code. Pide que devuelva un resumen corto.
7. Solo campos documentados (la CI rechaza los demás, porque Claude Code los ignora sin avisar).

## Reglas para skills (`.claude/skills/<nombre>/SKILL.md`)

1. La carpeta se llama como la skill, con prefijo `dm-`, en minúsculas y con guiones (`dm-abrir-pr`). Si pones `name`, debe coincidir con la carpeta.
2. `description` obligatoria, en tercera persona («Prepara…», «Verifica…»): primero el caso de uso clave, después los términos concretos que diría alguien del equipo y al final para qué **no** es (y qué skill usar). `when_to_use` lleva frases o preguntas de ejemplo que la disparan. Juntas, máx. 800 caracteres (lo valida la CI): Claude Code corta cada entrada a 1.536 y, si el listado de todas las skills no cabe en su presupuesto, quita la descripción entera de las menos usadas. Por eso `.claude/settings.json` sube ese presupuesto al 2 % (`skillListingBudgetFraction`).
3. `SKILL.md` de menos de 500 líneas. El detalle va en ficheros de apoyo dentro de la carpeta (`referencia/…`, `scripts/…`), **todos enlazados directamente desde `SKILL.md`** (un solo nivel; lo que no se enlaza, Claude no lo encuentra) y sin enlaces rotos. Los de más de 100 líneas empiezan con una línea «Contenido» que lista sus secciones. `when_to_use` es obligatorio en el proyecto.
4. Skills con efectos (push, abrir PR, borrar datos, desplegar) llevan `disable-model-invocation: true`: solo se lanzan a mano con `/<nombre>`.
5. `allowed-tools` solo con lo que la skill necesita.

## Cómo añadir uno

1. Rama `<usuario>/claude-<nombre>` y PR como cualquier otro cambio.
2. Fichero nuevo + fila en el índice.
3. Si viene de tu `~/.claude/`, cópialo y adáptalo: quita rutas y datos personales y pon `Origen` a tu nombre.
4. Todo lo de `.claude/` lo aprueba @yeraybc (CODEOWNERS).
