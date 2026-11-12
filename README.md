# DataMad-hackaton-2026

Repositorio del equipo para el hackathon DataMad 2026.

## Estructura

```
ideas/<plan>/<usuario>/   fichas de ideas (cada uno la suya)
docs/decisiones.md        lo que el equipo ha decidido: léelo primero
data/                     datos locales, no versionados; fuentes en data/README.md
src/                      código reutilizable (carga, limpieza, indicadores, modelos)
tests/                    tests de src/
notebooks/<usuario>/      exploración personal
app/                      la demo
```

## Cómo trabajamos (GitHub Flow)

1. **Issue** con la plantilla "Tarea": qué hay que hacer y cuándo está hecho. Asígnatela.
2. **Rama** `<usuario>/<tema>` desde `main`, en su propio worktree si la trabaja un agente.
3. **PR draft** pronto, título `tipo(área): qué cambia`, con `Closes #N`.
4. **CI en verde** → auto-merge con squash (`gh pr merge --auto --squash`). Los PR de autores que no son de confianza necesitan además la aprobación de Yeray o Izan. Los cambios en reglas y CI los aprueba Yeray. La rama se borra sola.

Las reglas completas (también para agentes) están en [AGENTS.md](AGENTS.md).

```bash
git worktree add ../dm-<tema> -b <usuario>/<tema> origin/main
```

