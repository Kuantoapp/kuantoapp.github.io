# Buenas prácticas oficiales de Claude Code

Lo que aplican las plantillas y el validador del repo, con su fuente. Comprobado el 2026-11-13; si la documentación cambia, manda la documentación y se actualiza este fichero y `.github/scripts/validar_claude.py`.

Fuentes: [BP] https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices · [SK] https://code.claude.com/docs/en/skills · [SA] https://code.claude.com/docs/en/sub-agents

## Skills

- **Descripción:** tercera persona; qué hace y cuándo usarla, con los términos clave; nada vago [BP]. En Claude Code, `description` + `when_to_use` se cortan a 1.536 caracteres en el listado, así que el caso de uso va primero [SK]. El repo fija 800 para que el listado de todas quepa en su presupuesto.
- **Siempre en contexto:** la descripción de cada skill ocupa contexto en cada turno, salvo con `disable-model-invocation: true` [SK]. Cada skill nueva tiene un coste fijo.
- **Concisión:** solo lo que Claude no sabe; `SKILL.md` de menos de 500 líneas; decir qué hacer [BP][SK].
- **Grados de libertad:** texto si hay varios caminos válidos; plantilla si hay un patrón preferido; script exacto si la operación es frágil [BP].
- **Divulgación progresiva:** `SKILL.md` como índice; referencias a un solo nivel (si están anidadas, Claude puede leerlas a medias); ficheros de más de 100 líneas con un índice al principio [BP].
- **Scripts:** que resuelvan el problema, con los errores tratados; dependencias listadas; rutas con `/`; decir si se ejecutan o se leen [BP].
- **Evaluaciones primero:** ver qué falla sin la skill, escribir al menos 3 escenarios, medir, escribir lo mínimo e iterar [BP].
- **Probar con varios modelos** (Haiku, Sonnet, Opus): lo que basta a Opus puede no bastar a Haiku [BP].
- **Bucles de validación:** validar, corregir, repetir; un plan validado antes de operaciones destructivas [BP].
- **Sin información que caduque** sin decirlo, y **un término por concepto** [BP].
- **Frontmatter** [SK]:
  - `disable-model-invocation: true`: solo se invoca con `/nombre` y su descripción sale del contexto.
  - `user-invocable: false`: oculta del menú `/`.
  - `context: fork` (con `agent`): se ejecuta en un subagente sin historial; una skill solo de pautas no devuelve nada útil así.
  - `allowed-tools`: preaprueba herramientas en el turno que la invoca; no restringe.
  - `paths`: se carga solo cuando se trabaja con ficheros que coinciden.

## Subagentes

- **Descripción:** dice cuándo delegar; «use proactively» (en el repo, «Úsalo de forma proactiva») para que Claude lo lance sin pedirlo. Corta: el detalle va al prompt [SA].
- **Herramientas mínimas:** `tools` es una lista de permitidas (sin ella hereda todas); `disallowedTools` es una lista de prohibidas [SA].
- **Modelo:** `sonnet`, `opus`, `haiku`, `fable`, un ID completo o `inherit` [SA].
- **`maxTurns` y `effort`:** acotan el gasto; al llegar a `maxTurns` la salida queda parcial [SA].
- **`skills`:** inyecta el contenido completo de cada skill al arrancar, no solo su descripción; las que tienen `disable-model-invocation` no se pueden precargar [SA].
- **`memory`:** `project` (versionable), `user` o `local`; activa lectura y escritura de su memoria [SA]. En el repo no se usa en revisores: su juicio debe salir del código y la evidencia, no de memorias.
- **`isolation: worktree`:** trabaja en un worktree temporal [SA].
- **Contexto aislado:** no ve la conversación, ni las skills invocadas, ni lo ya leído; recibe el mensaje con el que se lanza, que debe bastar por sí solo, y la jerarquía de `CLAUDE.md` (en este repo, `AGENTS.md`). `omitClaudeMd` se la quita, para agentes baratos que no la necesitan [SA].
- **Carga:** los cambios en `.claude/agents/` se detectan en segundos; hace falta reiniciar si es el primer fichero de un directorio `agents` nuevo. `/agents` los gestiona [SA]. Una skill nueva dentro de `.claude/skills/` también se detecta en la sesión; `/reload-skills` solo hace falta para un directorio de skills nuevo [SK].
- **Evaluaciones con ojos limpios:** prueba la pieza con una instancia que no la escribió y compárala con el resultado sin ella [BP].
