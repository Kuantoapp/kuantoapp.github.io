# Reglas para agentes (y humanos) en este repo

Casi todo el código lo escriben agentes. Estas reglas existen para que tres personas con varios agentes cada una no se pisen y para que cada PR se pueda revisar en minutos.

## Antes de escribir código

1. Lee `docs/decisiones.md`: ahí está lo que el equipo ya ha decidido (stack, fuentes de datos, idea elegida). No lo contradigas sin abrir una issue.
2. Trabaja sobre **una issue**. Si no existe, pídesela al humano o créala (`gh issue create`). El PR la cierra con `Closes #N`.
3. Busca en `src/` antes de crear nada nuevo: reutiliza funciones existentes.

## Ramas y worktrees

- Rama: `<usuario-github>/<tema-corto>` (la CI lo exige). Ej.: `izan-diaz/carga-ine`.
- **Un agente = una rama = un worktree.** Nunca dos agentes en la misma rama ni en la misma carpeta:
  ```bash
  git worktree add ../dm-<tema> -b <usuario>/<tema> origin/main
  ```
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

## Revisión y merge

- Autores de confianza (`yeraybc`, `izan-diaz`): con la CI en verde, el PR se mergea solo (auto-merge). No esperan a nadie.
- Resto de autores: el check `revision` exige la aprobación de un autor de confianza sobre el último commit.
- Cambios en `.github/`, `.claude/`, `AGENTS.md` o `CLAUDE.md`: siempre los aprueba `@yeraybc`.
- Activa el auto-merge al abrir el PR: `gh pr merge --auto --squash`.

## Calidad mínima (lo que comprueba la CI)

- Python: `ruff check . && ruff format --check . && pytest -q`. Ejecútalo antes de hacer push. En Claude Code, un hook (`.claude/settings.json`) ya formatea y revisa cada `.py` al editarlo.
- Lógica nueva no trivial (cálculo de indicadores, joins, parsers) lleva al menos un test pequeño en `tests/`.
- Sin dependencias nuevas sin justificarlas en el PR. Si añades una, va a `requirements.txt` con versión fijada.

## Prohibido

- Versionar datos (`csv`, `parquet`, `geojson` grandes…), modelos entrenados o ficheros de más de 5 MB. Van en `data/` (ignorado) y su origen se documenta en `data/README.md`.
- Secretos, `.env`, tokens o claves. Usa `.env.example` con los nombres de las variables.
- `git push --force` sobre `main`, o saltarse la CI o el check `revision`.
- Reescribir código que no toca la issue "ya que estaba".

## Subagentes y skills

Antes de crear o modificar algo en `.claude/agents/` o `.claude/skills/`, lee `.claude/README.md`: índice, reglas y qué va en cada sitio. La CI lo valida.

## Al terminar

- Si tomaste una decisión que afecta a los demás (fuente de datos, formato, librería), añade una línea a `docs/decisiones.md` en el mismo PR.
- Borra el worktree al mergear: `git worktree remove ../dm-<tema>`.
