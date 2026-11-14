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

## Primera vez

Todo el equipo usa el mismo Python (el de `.python-version`) y las mismas herramientas, con [uv](https://docs.astral.sh/uv/getting-started/installation/), que descarga esa versión de Python sola:

```bash
uv venv && uv pip install -r requirements-dev.txt
```

Activa el entorno con `source .venv/bin/activate` (en Windows, desde Git Bash: `source .venv/Scripts/activate`; ver [Windows](.claude/README.md#windows)). Después, abre `claude` en la raíz y acepta el diálogo de confianza (ver [.claude/README.md](.claude/README.md#uso-en-equipo)).

## Dependencias

Las de ejecución están en `requirements.txt` con versión fijada (`uv pip install -r requirements.txt`); las de desarrollo, en `requirements-dev.txt`. El paquete `mesobra` vive en `src/mesobra/` y `pyproject.toml` no declara dependencias: la lista única es `requirements.txt`. `r5py` arranca Java al importarse (necesita JDK 21): solo se comprueba en local, no en la CI. Licencia: MIT (`LICENSE`).

## Cómo trabajamos (GitHub Flow)

El repo está pensado para **bucles agénticos**: los agentes cierran el ciclo solos, con el menor coste posible, y la calidad, la seguridad y la precisión las aseguran hooks, CI y agentes revisores. Las personas deciden y aprueban lo sensible. Detalle en [AGENTS.md](AGENTS.md#el-bucle-agéntico).

1. **Issue** con la plantilla "Tarea": qué hay que hacer y cuándo está hecho. Asígnatela.
2. **Rama** `<usuario>/<tema>` desde `main`, en su propio worktree si la trabaja un agente.
3. **PR draft** pronto, título `tipo(área): qué cambia`, con `Closes #N`.
4. **CI en verde** → auto-merge con squash (`gh pr merge --auto --squash`). Los PR de autores que no son de confianza necesitan además la aprobación de Yeray o Izan. Los cambios en reglas y CI los aprueba Yeray. La rama se borra sola.

Las reglas completas (también para agentes) están en [AGENTS.md](AGENTS.md).

```bash
git worktree add ../dm-<tema> -b <usuario>/<tema> origin/main
```
