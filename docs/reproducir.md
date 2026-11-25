# Reproducir Kuanto

Cómo regenerar todos los datos de Kuanto desde las fuentes oficiales, ejecutar los tests y usar el asistente MCP. Es para quien quiera comprobar los resultados o reutilizar el código. Para solo ver la web basta con el [inicio rápido del README](../README.md#inicio-rápido).

El código de Kuanto es un paquete de Python llamado `mesobra`, en [`src/mesobra/`](../src/mesobra/). De ahí salen los comandos `python -m mesobra` y `mesobra-mcp`.

## Requisitos

- [uv](https://docs.astral.sh/uv/getting-started/installation/), que instala el Python de `.python-version`.
- JDK 21 con `JAVA_HOME` apuntando a él, para [r5py](https://r5py.readthedocs.io/), que calcula los tiempos de viaje. r5py solo corre en local: la CI no lo ejecuta.
- Las descargas de [`data/README.md`](../data/README.md) en `data/raw/`. Cada fila dice cómo obtener el fichero y su SHA-256.

```bash
uv venv && uv pip install -r requirements.txt
source .venv/bin/activate         # Windows (Git Bash): source .venv/Scripts/activate
```

## 1. Tiempos de viaje (una vez)

`python -m mesobra` lee estas matrices ya calculadas y no relanza r5py, así que se generan antes, a mano:

```bash
python -m mesobra.zonas           # las 199 zonas y su centro → data/processed/zonas.parquet
python -m mesobra.tiempos         # transporte público → data/processed/tiempos.parquet
python -m mesobra.coche           # opcional: coche → data/processed/tiempos_coche.parquet
```

Sin `tiempos_coche.parquet`, `tiempos.json` sale sin el modo coche. La duración medida de estos pasos está en la [nota metodológica](https://yeraybc.github.io/DataMad-hackaton-2026/metodologia.html#titulo-mantenimiento).

## 2. Todos los datos de la web

```bash
python -m mesobra
```

No tiene opciones. Hace, en este orden:

1. Comprueba que `data/raw/` tiene todos los ficheros de `data/README.md` con su SHA-256. Si falta uno, se detiene y dice cuál es y cómo descargarlo.
2. Ejecuta los pasos de `PASOS` en [`__main__.py`](../src/mesobra/__main__.py):
   - `fondo`: el mapa base propio, que funciona sin red (`app/mapa/fondo.geojson`).
   - `pipeline_territorio`: zonas y tiempos de viaje (`zonas.geojson`, `tiempos.json`).
   - `pipeline_euros`: neto, alquiler, tarifas y cesta del hogar (`netos.json`, `alquiler.json`, `tarifas.json`, `hogares.json`).
   - `pipeline_analisis`: el informe de análisis (`analisis.json` y las figuras de `app/img/`).
   - `sdm`: los indicadores de alquiler y esfuerzo en el esquema [Smart Data Models](https://smartdatamodels.org/) (`app/datos/sdm/`).
3. Valida todo `app/datos/` con `api_estatica.validar`, el contrato que la web espera.

Después, `git status` muestra qué ha cambiado en `app/datos/`. El tiempo total de una ejecución completa está sin medir.

## 3. La web en local

```bash
python -m http.server -d app      # y abre http://localhost:8000/
```

Funciona sin red: la web solo carga ficheros propios.

## 4. Tests

```bash
pytest -q                         # el código de Python
npm test                          # la lógica de la web (app/*.test.js)
```

La cuenta final está escrita dos veces, en Python (`src/mesobra/calculo.py`) y en JavaScript (`app/calculo.js`), y `tests/test_paridad.py` comprueba que las dos dan lo mismo.

## 5. Asistente MCP

`mesobra-mcp` es un servidor [MCP](https://modelcontextprotocol.io/) local (stdio) con tres herramientas: `calcular_sobrante`, `ranking_zonas` e `indicadores_zona`. Lee los mismos ficheros de `app/datos/` que la web, sin red, y cada respuesta lleva unidades, año del dato, fuentes y supuestos.

La ventaja de combinarlo con una IA es que ella entiende la pregunta y explica, y las cifras las calcula Kuanto con su fuente ([Kuanto frente a preguntar a una IA](kuanto-frente-a-ia.md#kuanto-y-la-ia-juntos-con-mcp)). Sobre la privacidad: el servidor no envía nada, pero lo que escribes en el chat llega al proveedor del modelo. El sueldo solo se queda en tu equipo si el modelo también es local.

Con uv no hace falta clonar nada:

```bash
claude mcp add mesobra -- uvx --from git+https://github.com/yeraybc/DataMad-hackaton-2026 mesobra-mcp
```

Para otros clientes MCP, el mismo comando en su bloque de configuración:

```json
{ "mcpServers": { "mesobra": { "command": "uvx", "args": ["--from", "git+https://github.com/yeraybc/DataMad-hackaton-2026", "mesobra-mcp"] } } }
```

Desde un clon, `uvx --from . mesobra-mcp` arranca el mismo servidor. Pregunta de ejemplo: «Tengo 30 años, vivo solo, gano 24.000 € brutos al año y trabajo en Getafe cinco días a la semana en transporte público. ¿En qué zonas me sobra más dinero al mes y cuántas horas de viaje implican?». El destino va por código INE: Getafe es 28065.

## En Windows

- Todo texto se lee y escribe con `encoding` explícito: el defecto de Windows es cp1252 y `tests/test_codificacion.py` lo vigila (#291).
- Si `python -c "import pyarrow.parquet"` falla con «Una directiva de Control de aplicaciones bloqueó este archivo», es Smart App Control o WDAC del equipo, no el repositorio. Hasta que se permita esa DLL, nada que lea o escriba Parquet funciona en ese equipo (#291).
