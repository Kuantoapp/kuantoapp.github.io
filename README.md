# Kuanto

Kuanto calcula cuánto dinero sobra al mes viviendo en cada una de las 199 zonas de la Comunidad de Madrid (los 178 municipios y los 21 distritos de Madrid capital, según `zonas.geojson`), a partir del sueldo, el alquiler y el transporte del trabajo. Al neto del sueldo se le restan el alquiler de la zona, el título de transporte más barato y una cesta de gasto del hogar, y se muestran las horas de viaje al trabajo para que se vea lo que cuesta vivir lejos. Cada cifra lleva su fuente, y las que salen de un modelo o de un supuesto se marcan como «estimado».

Es el proyecto del equipo para DataMad 2026, el datathon de datos abiertos de la Comunidad de Madrid. Usa datos de su catálogo regional y los cruza con los del INE, el Ministerio de Vivienda, la Agencia Tributaria, el Consorcio Regional de Transportes y OpenStreetMap.

- Web: <https://yeraybc.github.io/DataMad-hackaton-2026/>
- Informe de análisis: <https://yeraybc.github.io/DataMad-hackaton-2026/informe.html> (en el repositorio, `app/informe.html`)

## Reproducirlo todo

Requisitos: [uv](https://docs.astral.sh/uv/getting-started/installation/) (instala el Python de `.python-version`), JDK 21 con `JAVA_HOME` para r5py y las fuentes de [`data/README.md`](data/README.md) en `data/raw/`.

```bash
uv venv && uv pip install -r requirements.txt
source .venv/bin/activate   # en Windows, desde Git Bash: source .venv/Scripts/activate
python -m mesobra
```

`python -m mesobra` comprueba que `data/raw/` tiene todos los ficheros de `data/README.md` con su SHA-256 (si falta uno, se detiene diciendo cuál es y cómo descargarlo), ejecuta `pipeline_territorio`, `pipeline_euros`, `pipeline_analisis` y `sdm` en ese orden y valida todo `app/datos/` con `api_estatica.validar`. No tiene opciones. Después, `git status` muestra qué ha cambiado en `app/datos/`.

Antes hacen falta `data/processed/zonas.parquet` y `tiempos.parquet`, que `pipeline_territorio` lee sin relanzar r5py. Se generan con `python -m mesobra.zonas` y `python -m mesobra.tiempos`, que sí usan r5py (unos 30 min, #105). Para el modo coche, `python -m mesobra.coche` (también r5py) genera `tiempos_coche.parquet`; sin él, `tiempos.json` sale sin coche. Tiempo de `python -m mesobra`: pendiente de medir en la primera ejecución completa.

Para ver la web en local sin red: `python -m http.server -d app` y abrir <http://localhost:8000/>.

Tests: `pytest -q` (Python) y `npm test` (la lógica de `app/`). `tests/test_codificacion.py` falla si un `read_text`, `write_text` u `open` de texto no lleva `encoding`: en Windows el defecto es cp1252 (#291).

`python -m mesobra.sdm` publica además los indicadores de alquiler y sobrecarga en el esquema [Smart Data Models](https://smartdatamodels.org/) (`KeyPerformanceIndicator`), y ya forma parte de `python -m mesobra`.

## Servidor MCP

`mesobra-mcp` es un servidor [MCP](https://modelcontextprotocol.io/) local (stdio) con tres herramientas: `calcular_sobrante`, `ranking_zonas` e `indicadores_zona`. Lee los mismos ficheros de `app/datos/` que la web, sin red y sin que el sueldo salga del equipo, y cada respuesta lleva unidades, año del dato, fuentes y supuestos.

Con [uv](https://docs.astral.sh/uv/getting-started/installation/) no hay que clonar nada, una vez que el repositorio sea público:

```bash
claude mcp add mesobra -- uvx --from git+https://github.com/yeraybc/DataMad-hackaton-2026 mesobra-mcp
```

Para otros clientes MCP, el mismo comando en su bloque de configuración:

```json
{ "mcpServers": { "mesobra": { "command": "uvx", "args": ["--from", "git+https://github.com/yeraybc/DataMad-hackaton-2026", "mesobra-mcp"] } } }
```

Desde un clon del repositorio, `uvx --from . mesobra-mcp` arranca el mismo servidor. Ejemplo de pregunta al asistente: «Tengo 30 años, vivo solo, gano 24.000 € brutos al año y trabajo en Getafe cinco días a la semana en transporte público. ¿En qué zonas me sobra más dinero al mes y cuántas horas de viaje implican?» (el destino va por código INE: Getafe es 28065).

## Datos, licencias y fuentes

- **Datos derivados** (`app/datos/*.json` y `zonas.geojson`): CC BY 4.0. Cada fichero lista en `meta.fuentes` sus fuentes con su licencia y en `meta.nota` su método. La licencia va por fichero: los tres que usan datos de OpenStreetMap (`tiempos.json`, `zonas.geojson` y `alquiler.json`) llevan ODbL 1.0, y las condiciones de cada fuente de terceros se mantienen. Decisiones en [`docs/decisiones.md`](docs/decisiones.md) (16-11-2026 y 20-11-2026).
- **Código**: MIT ([`LICENSE`](LICENSE)).

Fuentes y cita que exige cada licencia. El detalle por fichero descargado, con URL y SHA-256, está en [`data/README.md`](data/README.md).

| Fuente | Para qué se usa | Licencia | Cita exigida |
|---|---|---|---|
| INE (Atlas de renta, censos, IPC, EPF, salarios, secciones censales) | Renta y población por sección, sueldos, precios y gasto de los hogares | CC BY 4.0 | «Elaboración propia con datos extraídos del sitio web del INE: www.ine.es», con la fecha de la última actualización del original y sin sugerir que el INE participa o patrocina el proyecto |
| Catálogo de datos abiertos de la Comunidad de Madrid | Renta bruta municipal, Bono Alquiler Joven, gasto de los hogares (EPF), IPC de la vivienda en alquiler, población y tenencia | CC BY 4.0 y condiciones del portal | «Fuente de los datos: Comunidad de Madrid», con la fecha de actualización, e identificando las modificaciones |
| SERPAVI (Ministerio de Vivienda y Agenda Urbana), fichero modificado el 2026-07-09 | Alquiler por sección censal | Condiciones generales de reutilización del Ministerio | «Origen de los datos: Ministerio de Vivienda y Agenda Urbana», con la fecha de actualización del fichero, sin sugerir que el Ministerio avala el proyecto y conservando los metadatos de fecha y condiciones |
| Agencia Tributaria (viviendas declaradas en el IRPF 2024) | Banda del alquiler de contratos nuevos | Reutilización autorizada, sin desnaturalizar | Citar la fuente («Agencia Tributaria») y dar la fecha de actualización |
| Consorcio Regional de Transportes de Madrid (GTFS, coronas y fichas de títulos) | Horarios y rutas de transporte público, coronas tarifarias | Licencia de datos abiertos del CRTM | Citar al CRTM como origen de los datos explotados, con «Powered by CRTM», enlace y la fecha del GTFS |
| OpenStreetMap (extracto de Geofabrik) | Red viaria, edificios y polos de empleo para calcular los tiempos de viaje | ODbL 1.0 | «© OpenStreetMap contributors»; lo derivado lleva un aviso de que los datos son de OpenStreetMap bajo ODbL |
| BOE y BOCM (IRPF, cotizaciones, tarifas de transporte, fiestas laborales) | Neto del sueldo, precio de los títulos de transporte y días de trabajo | Disposiciones oficiales sin derechos de propiedad intelectual (art. 13 del TRLPI); reutilización del BOE con cita | «basado en datos de la Agencia Estatal Boletín Oficial del Estado» |

---

# Para el equipo

Lo que sigue es el funcionamiento interno del repositorio.

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

Las de ejecución están en `requirements.txt` con versión fijada (`uv pip install -r requirements.txt`); las de desarrollo, en `requirements-dev.txt`. El paquete `mesobra` vive en `src/mesobra/` y `pyproject.toml` no declara dependencias: la lista única es `requirements.txt`. Para importar `mesobra` fuera de pytest: `uv pip install -e .`. `r5py` arranca Java al importarse (necesita JDK 21 y `JAVA_HOME` apuntando a él): solo se comprueba en local, no en la CI. En Windows, si `python -c "import pyarrow.parquet"` falla con «Una directiva de Control de aplicaciones bloqueó este archivo», es Smart App Control o WDAC del equipo, no el repo: hasta que se permita esa DLL, nada que lea o escriba Parquet funciona en ese equipo (#291). Licencia: MIT (`LICENSE`).

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
