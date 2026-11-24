# Colaborar en Kuanto

Cómo está organizado el repositorio y cómo se trabaja en él. Es la guía para quien vaya a tocar código, datos o textos. Las reglas completas, que siguen también los agentes de IA, están en [AGENTS.md](AGENTS.md).

## Estructura

```
app/                      la web que se publica, tal cual, sin compilar
app/datos/                los datos abiertos que lee la web (LEEME.md los describe)
src/mesobra/              el código de Kuanto: carga, cálculo, pipeline y servidor MCP
tests/                    tests de src/ (los de app/ son app/*.test.js)
data/                     descargas y salidas locales, no versionadas; fuentes en data/README.md
docs/                     documentación: índice en docs/README.md
docs/decisiones.md        registro de lo que ha decidido el equipo: léelo antes de cambiar nada
docs/verificaciones/      contraste de fuentes y normas con el publicador original
docs/datos/               diccionarios de los ficheros grandes (generados)
notebooks/<usuario>/      exploración personal
ideas/<plan>/<usuario>/   fichas de las ideas que se valoraron antes de elegir Kuanto
.claude/                  agentes, skills y hooks (ver .claude/README.md)
```

## Primera vez

Todo el equipo usa el mismo Python (el de `.python-version`) y las mismas herramientas, con [uv](https://docs.astral.sh/uv/getting-started/installation/), que descarga esa versión de Python sola:

```bash
uv venv && uv pip install -r requirements-dev.txt
source .venv/bin/activate         # Windows (Git Bash): source .venv/Scripts/activate
```

Después, abre `claude` en la raíz y acepta el diálogo de confianza (ver [.claude/README.md](.claude/README.md#uso-en-equipo); en Windows, [su apartado](.claude/README.md#windows)).

## Dependencias

- Las de ejecución están en `requirements.txt` con versión fijada; las de desarrollo, en `requirements-dev.txt`. `pyproject.toml` no declara dependencias: la lista única es `requirements.txt`.
- El paquete `mesobra` vive en `src/mesobra/`. Para importarlo fuera de pytest: `uv pip install -e .`.
- `r5py` arranca Java al importarse: necesita JDK 21 y `JAVA_HOME` apuntando a él. Solo se usa en local, no en la CI.
- Una dependencia nueva se justifica en el PR y se anota en `docs/decisiones.md`.

## Antes de subir un cambio

```bash
ruff check . && ruff format --check . && pytest -q
npm test                          # la lógica de app/
```

`tests/test_codificacion.py` falla si un `read_text`, `write_text` u `open` de texto no lleva `encoding`: en Windows el defecto es cp1252 (#291).

## Cómo trabajamos (GitHub Flow)

El repositorio está pensado para bucles agénticos: los agentes cierran el ciclo solos y la calidad la aseguran hooks, CI y agentes revisores. Las personas deciden y aprueban lo sensible. Detalle en [AGENTS.md](AGENTS.md#el-bucle-agéntico).

1. **Issue** con la plantilla «Tarea»: qué hay que hacer y cuándo está hecho. Asígnatela.
2. **Rama** `<usuario>/<tema>` desde `main`, en su propio worktree si la trabaja un agente:
   ```bash
   git worktree add ../dm-<tema> -b <usuario>/<tema> origin/main
   ```
3. **PR en borrador** pronto, con título `tipo(área): qué cambia` y `Closes #N`. Si el cambio toca un área con revisor obligatorio (espacial, cálculos normativos, cifras públicas, fuentes o código), su veredicto va en el PR ([AGENTS.md](AGENTS.md#revisores-obligatorios)).
4. **CI en verde** y auto-merge con squash (`gh pr merge --auto --squash`). Los PR de autores que no son de confianza necesitan la aprobación de Yeray o Izan; los cambios en reglas y CI los aprueba Yeray. La rama se borra sola.

## Cifras y datos

- Ninguna cifra llega al público sin su fuente, y lo estimado lo dice ([AGENTS.md](AGENTS.md#cifras-con-fuente)).
- `data/raw/` no se edita: una fuente nueva se añade con la skill `dm-nueva-fuente`, con fecha en el nombre y SHA-256 en `data/README.md`.

## Web publicada

La carpeta `app/` se publica tal cual en <https://yeraybc.github.io/DataMad-hackaton-2026/>. La publica [`.github/workflows/pages.yml`](.github/workflows/pages.yml) en cada push a `main` que cambie `app/`; para publicar sin cambios, *Actions → Pages → Run workflow*. Requiere el repositorio público y Pages con origen «GitHub Actions» (decisión D5). Solo se publica `app/`: los ejemplos de `tests/fixtures/` no están en la web.
