# Reglas para agentes (y humanos) en este repo

Casi todo el código lo escriben agentes. Estas reglas existen para que tres personas con varios agentes cada una no se pisen y para que cada PR se pueda revisar en minutos.

## El bucle agéntico

Todo el repo está montado para que un agente cierre el ciclo solo, **barato y bien**, y que el humano solo tenga que decidir. La calidad, la seguridad y la precisión las garantizan máquinas (hooks, CI, revisores), no la vigilancia humana.

**Ciclo:** issue → rama y worktree → implementar con la skill del área → hook de ruff y tests locales → **commit** → revisor del área (obligatorio, ver «Revisores obligatorios») → PR draft con su veredicto y auto-merge → CI → merge.

**El humano solo interviene para:** decidir (y queda en `docs/decisiones.md`), aprobar PRs de autores que no son de confianza o que tocan reglas (`.github/`, `.claude/`, `AGENTS.md`), y responder ambigüedades reales.

### Coste mínimo

- **Lee lo justo:** busca con `grep` antes de abrir ficheros; lee el rango que necesitas, no ficheros enteros; no releas lo que ya tienes.
- **Reutiliza:** funciones de `src/` y decisiones ya tomadas. Para cambiar unas líneas, edita; no reescribas el fichero.
- **Agrupa** comandos independientes en una sola llamada. Nada de sondeos en bucle: `gh pr checks --watch` espera por ti.
- **Subagentes** solo si separan contexto o trabajan en paralelo de verdad, pidiendo un resumen corto.
- **Modelo según la tarea, no el más barato:** lo que cuesta es el total, y un modelo que acierta a la primera ahorra repeticiones y revisiones. `opus` para razonar, diseñar, modelizar y revisar; `sonnet` para implementar lo que ya está definido; `haiku` solo para búsquedas o resúmenes mecánicos.
- **Datos:** desarrolla con una muestra pequeña; la ejecución completa, una vez y al final.
- **Corta a tiempo:** si el mismo fallo resiste tres intentos, para y pregunta con el diagnóstico. No sigas probando a ciegas.

### Precisión y calidad sin humano en medio

- **Nada está hecho sin prueba:** un test en verde, una salida o una cifra comprobada. Si algo no se pudo verificar, se dice.
- **Resultados contrastados** con lo que deben dar (teoría, valores de control, una segunda vía) antes de darlos por buenos. Las skills `dm-*` traen el procedimiento.
- **Las reglas que no pueden fallar son hooks, `deny` o CI**, no texto: si una regla de este fichero se incumple dos veces, se convierte en una de esas.
- **Cambios pequeños y verificables:** un PR, un cambio; cuanto más pequeño, más barato de revisar y de deshacer.
- **Pregunta solo si la respuesta cambia lo que haces y no está en el repo.** Si supones, deja el supuesto escrito en el código y en `docs/decisiones.md`.

## Antes de escribir código

1. Lee `docs/decisiones.md`: ahí está lo que el equipo ya ha decidido (stack, fuentes de datos, idea elegida) y las fechas clave. No lo contradigas sin abrir una issue. Al abrir sesión, un hook te resume lo pendiente: próximas fechas clave, decisiones sin tomar, marcas «(verificar)» y descargas que te faltan.
2. Trabaja sobre **una issue**. Si no existe, pídesela al humano o créala (`gh issue create`). El PR la cierra con `Closes #N`.
3. Busca en `src/` antes de crear nada nuevo: reutiliza funciones existentes.
4. **Código mínimo:** la primera opción que funcione entera (¿hace falta?, ¿ya está en `src/`?, librería estándar o ya instalada, una línea, lo mínimo). Sin abstracciones de un solo uso ni opciones que nadie pidió; nunca silencies un error; un atajo con límite lleva `# shortcut: <límite>, <cuándo mejorarlo>`. Es el estándar para todo el código; ruff rechaza lo que puede detectar una máquina (argumentos sin usar, código comentado, funciones de complejidad mayor que 10, más de 5 parámetros, `print` fuera de notebooks). Detalle en la skill `dm-codigo-minimo`.

## Ramas y worktrees

- Rama: `<usuario-github>/<tema-corto>` (la CI lo exige). Ej.: `izan-diaz/carga-ine`.
- **Un agente = una rama = un worktree.** Nunca dos agentes en la misma rama ni en la misma carpeta:
  ```bash
  git worktree add ../dm-<tema> -b <usuario>/<tema> origin/main
  ```
- **Datos en worktrees:** `data/raw/` es una sola copia para todos. En un worktree, un hook enlaza su `data/raw` con la del checkout principal al abrir Claude Code, así nadie descarga dos veces (sin Claude Code: `python3 .claude/hooks/raw_inmutable.py enlazar` desde el worktree). Antes de descargar, mira si ya está. `data/processed/` es propia de cada worktree, porque depende del código de su rama.
- Ramas cortas: vive horas, no días. Antes de abrir o actualizar el PR: `git fetch && git rebase origin/main`.

## Dónde va cada cosa

| Carpeta | Qué contiene | Propiedad |
|---|---|---|
| `src/` | Código reutilizable: carga de datos, limpieza, indicadores, modelos | compartida |
| `app/` | La demo que se presenta (dashboard, mapa, web) | compartida |
| `notebooks/<usuario>/` | Exploración personal | solo su dueño |
| `ideas/<plan>/<usuario>/` | Fichas de ideas | solo su dueño |
| `data/` | Nada versionado salvo `data/README.md` (fuentes y cómo descargarlas) | — |
| `docs/` | `decisiones.md` y material del pitch | compartida |
| `tests/` | Tests de `src/` | compartida |

No edites carpetas personales de otra persona. Si un notebook ya funciona, su lógica se mueve a `src/` y el notebook la importa.

## Tamaño y forma del PR

- **Un PR = un cambio con sentido.** Objetivo: menos de 400 líneas cambiadas. La CI falla por encima de 800 (sin contar lockfiles) salvo que el PR lleve la etiqueta `pr-grande`.
- Si el cambio es grande, pártelo por capas: datos → lógica → app.
- Título del PR = mensaje del commit en `main` (se hace squash): `tipo(área): qué cambia`.
  Tipos: `feat`, `fix`, `data`, `docs`, `refactor`, `test`, `chore`. Ej.: `feat(src): índice de vulnerabilidad por municipio`.
- Abre el PR como **draft** pronto; pásalo a "ready" cuando la CI esté en verde.
- Rellena la plantilla del PR, incluida la sección de agente.

## Revisores obligatorios

Si un PR toca un área con revisor, su veredicto tiene que estar en el PR y ser del código actual. La CI lo exige (`.github/scripts/revisiones.py`).

| Si el PR cambia… | Revisor |
|---|---|
| Código de `src/`, `app/` o `notebooks/` que usa geometrías, W o modelos espaciales (geopandas, pysal, kriging, `to_crs`…) | `dm-revisor-espacial` |
| Código con cálculos normativos (IRPF, cotizaciones, SMI, IPREM, ayudas, tarifas, bruto y neto) | `dm-auditor-calculos-normativos` |
| Textos que ve el público (`app/`, `docs/pitch/`) | `dm-trazador-cifras` |
| Fuentes de datos (`data/README.md`) | `dm-verificador-fuentes` |
| Código Python de `src/` o `app/` (corrección, fallos silenciosos, código mínimo) | `dm-revisor-codigo` |

1. **Haz commit antes de pedir la revisión:** el veredicto vale para ese commit. Si después cambia algo de su área, caduca y hay que repetirla.
2. Lanza el revisor. Un hook registra su veredicto solo (en `.git/`, sin versionar).
3. Ejecuta `python .github/scripts/revisiones.py --resumen` y pega su salida en el PR (sección «Revisión por agentes»). Si falta un revisor, lo dice.
4. **NO APTO** bloquea el merge: corrige y repite. **APTO CON RESERVAS** pasa, con las reservas a la vista.
5. Si el área se detectó por error (por ejemplo, un comentario que nombra «neto»), escribe `- dm-…: NO APLICA — motivo`. Queda visible en el PR para quien lo revise.

Antes de terminar, un hook `Stop` recuerda las revisiones que faltan sobre el trabajo ya confirmado. No insiste con lo que ya está en `main` (tras mergear, aunque no hayas hecho `git pull`).

## Revisión y merge

- Autores de confianza (`yeraybc`, `izan-diaz`): con la CI en verde, el PR se mergea solo (auto-merge). No esperan a nadie.
- Resto de autores: el check `revision` exige la aprobación de un autor de confianza sobre el último commit.
- Cambios en `.github/`, `.claude/`, `AGENTS.md` o `CLAUDE.md`: siempre los aprueba `@yeraybc`.
- Activa el auto-merge al abrir el PR: `gh pr merge --auto --squash`.

## Calidad mínima (lo que comprueba la CI)

- Entorno: Python de `.python-version` y herramientas de `requirements-dev.txt`, en `.venv` (`uv venv && uv pip install -r requirements-dev.txt`): local, CI y hooks usan las mismas versiones. Si al abrir sesión un hook avisa de que falta algo, arréglalo como dice.
- **Windows:** los hooks tienen versión para Windows (`*_windows.py`). Si cambias un hook, revisa la suya; detalle en `.claude/README.md`.
- Python: `ruff check . && ruff format --check . && pytest -q`. Ejecútalo antes de hacer push. En Claude Code, un hook (`.claude/settings.json`) ya formatea y revisa cada `.py` al editarlo.
- Lógica nueva no trivial (cálculo de indicadores, joins, parsers) lleva al menos un test pequeño en `tests/`.
- Sin dependencias nuevas sin justificarlas en el PR. Si añades una, va a `requirements.txt` con versión fijada.

## Cifras con fuente

- **Ningún número llega al público sin su fuente.** En `app/` y `docs/pitch/` (`.md`, `.html`, `.txt`), cada línea con una cifra lleva una nota `[^id]` definida en el mismo fichero o «fuente: …». Si la cifra sale de un modelo, una imputación o un supuesto, dice además «estimado». Un hook lo comprueba al editar y la CI en cada PR.
- Una línea con números que no son datos (una página, un identificador) se exime con `<!-- sin-fuente: motivo -->`.
- Antes de una demo, un ensayo o un PR que cambie cifras visibles, pasa `dm-trazador-cifras`: rastrea cada cifra hasta la consulta y el dato que la producen.

## Datos originales intocables

- `data/raw/` guarda las descargas tal cual: se puede **descargar un fichero nuevo**, pero no editarlo, sobrescribirlo, moverlo ni borrarlo. Un hook lo impide y deja lo descargado en solo lectura.
- Para añadir o actualizar una fuente, sigue la skill `dm-nueva-fuente`: descarga con la fecha en el nombre, deja su SHA-256 en `data/README.md` y comprueba con `--comprobar` que tienes los mismos ficheros que el resto. Lo derivado va a `data/processed/`.
- Para descomprimir dentro de `data/raw/`, sin sobrescribir: `tar -xkf` o `unzip -n`.

## Prohibido

- Versionar datos (`csv`, `parquet`, `geojson` grandes…), modelos entrenados o ficheros de más de 5 MB. Van en `data/` (ignorado) y su origen se documenta en `data/README.md`.
- Secretos, `.env`, tokens o claves. Usa `.env.example` con los nombres de las variables.
- `git push --force` sobre `main`, o saltarse la CI o el check `revision`.
- Reescribir código que no toca la issue "ya que estaba".

## Subagentes y skills

Antes de crear o modificar algo en `.claude/agents/` o `.claude/skills/`, lee `.claude/README.md`: índice, reglas y qué va en cada sitio. La CI lo valida.

## Documentación al día

Cada cambio arrastra su documentación en el mismo PR. Qué tocar según lo que cambies:

| Si cambias… | Actualiza |
|---|---|
| Hooks o `.claude/settings.json` | `AGENTS.md` o `.claude/README.md` |
| CI o `.github/scripts/` | `AGENTS.md`, `README.md` o `.claude/README.md` |
| Dependencias o `.python-version` | `docs/decisiones.md` o `README.md` |
| Agentes o skills | su fila del índice en `.claude/README.md` |
| Una fuente de datos (una URL nueva en el código) | `data/README.md` |
| Una decisión que afecta a los demás | `docs/decisiones.md` |
| Un fichero que se nombra en la documentación (mover, renombrar, borrar) | Los documentos que lo nombran |

`.github/scripts/docs_al_dia.py` lo comprueba en la CI, junto con las rutas y enlaces rotos de la documentación. En Claude Code, un hook `Stop` te lo recuerda antes de terminar. Si de verdad no hace falta, escribe en el PR «Docs: sin cambios — motivo».

## Al terminar

- Si tomaste una decisión que afecta a los demás (fuente de datos, formato, librería), añade una línea a `docs/decisiones.md` en el mismo PR. Si es de las que cuestan deshacer (idea, fuente principal, método), pásala antes por `dm-abogado-del-diablo`.
- Borra el worktree al mergear: `git worktree remove ../dm-<tema>`.
