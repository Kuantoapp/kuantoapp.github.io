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

Las de ejecución están en `requirements.txt` con versión fijada (`uv pip install -r requirements.txt`); las de desarrollo, en `requirements-dev.txt`. El paquete `mesobra` vive en `src/mesobra/` y `pyproject.toml` no declara dependencias: la lista única es `requirements.txt`. Para importar `mesobra` fuera de pytest: `uv pip install -e .`. `r5py` arranca Java al importarse (necesita JDK 21 y `JAVA_HOME` apuntando a él): solo se comprueba en local, no en la CI. Licencia: MIT (`LICENSE`).

## Regenerar la API estática

```bash
python -m mesobra
```

Comprueba que `data/raw/` tiene todos los ficheros de `data/README.md` con su SHA-256 (si falta uno, se detiene diciendo cuál es y cómo obtenerlo), ejecuta `pipeline_territorio`, `pipeline_euros`, `pipeline_analisis` y `sdm` en ese orden y valida todo `app/datos/` con `api_estatica.validar`. No tiene opciones. Después, `git status` muestra qué ha cambiado en `app/datos/`.

Requisitos: las fuentes de `data/README.md` descargadas y `data/processed/zonas.parquet` y `tiempos.parquet`, que `pipeline_territorio` lee sin relanzar r5py. Esas dos tablas se generan antes con `python -m mesobra.zonas` y `python -m mesobra.tiempos`, que sí usan r5py (JDK 21 con `JAVA_HOME`, unos 30 min, #105). Si se quiere el modo coche, `python -m mesobra.coche` (r5py, JDK 21) genera antes `tiempos_coche.parquet`; sin él, `tiempos.json` sale sin coche. Tiempo de `python -m mesobra`: pendiente de medir en la primera ejecución completa.

## Demo publicada

La carpeta `app/` se publica tal cual, sin compilar, en **https://yeraybc.github.io/DataMad-hackaton-2026/**. La publica [`.github/workflows/pages.yml`](.github/workflows/pages.yml) en cada push a `main` que cambie `app/`; para publicar sin cambios, *Actions → Pages → Run workflow*. Requiere el repositorio público y Pages con origen «GitHub Actions» (decisión D5). Solo se publica `app/`: los ejemplos de `tests/fixtures/` no están en la web. Sin red, la demo se sirve en local con `python -m http.server -d app`.

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
