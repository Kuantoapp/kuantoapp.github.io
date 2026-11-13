---
description: "Crea o actualiza el diccionario de datos (`<nombre>.DATA.md`) de un CSV o TSV pesado (más de ~5 MB) y trabaja a partir de él sin leer el fichero entero: tipos, nulos, rangos, cardinalidad, muestras y avisos de codificación (latin-1) y de números en formato español. Solo stdlib. No verifica la fuente ni la licencia (dm-verificacion-fuentes) ni cruza tablas (dm-cartografia)."
when_to_use: "Antes de explorar, limpiar o modelar un fichero grande recién descargado; acabo de bajar un CSV, ¿qué columnas tiene?, perfila este dataset, diccionario de datos, ¿hay nulos?, salen tildes rotas, ¿esta columna es numérica?"
---

# Diccionario de datos

Objetivo: trabajar con datos pesados gastando pocos tokens. El diccionario resume el fichero; el fichero completo solo se lee si la tarea lo exige.

## Dónde va

Las descargas originales son inmutables (un hook impide reescribirlas) y `data/` no se versiona. Los diccionarios van a **`docs/datos/<nombre>.DATA.md`**: se versionan y los ve todo el equipo. Pasa siempre `--out`.

## Flujo

Script: [scripts/perfilar.py](scripts/perfilar.py). Solo stdlib: vale el Python del proyecto (`.venv/bin/python` en macOS y Linux, `.venv\Scripts\python` en Windows) o cualquier `python3`. En los ejemplos, `S=.claude/skills/dm-diccionario-datos/scripts/perfilar.py` y `F` es la ruta del CSV.

1. **Busca** `docs/datos/<nombre>.DATA.md`.
2. **¿Al día?** `python $S $F --out docs/datos/<nombre>.DATA.md --check` (0 = al día, 1 = desfasado, 2 = no existe).
3. **Si falta o está desfasado, genéralo** con la misma orden sin `--check`.
   - Ficheros enormes: perfila una fila de cada N repartidas por todo el fichero (`--max-rows`, 200000 por defecto), con semilla fija (`--seed 42`).
   - Si el aviso dice «no decodificables», repite con `--encoding latin-1` (o `cp1252`): muchos CSV de portales públicos no vienen en UTF-8.
   - Regenerar conserva las descripciones de columna y la sección `## Notas` escritas a mano.
4. **Lee el `.DATA.md`**, no el dataset. Si es muy ancho, lee la cabecera y `## Avisos` y busca columnas concretas con `grep`.
5. **Completa lo «POR COMPLETAR»** (origen y significado) con `data/README.md`, los metadatos del portal o lo que diga el equipo. No inventes significados: si no consta, se queda marcado.
6. **Lectura completa solo si hace falta** (cálculo exacto, entrenar, buscar un registro). Avísalo y hazlo por trozos (`chunksize`, `scan_csv`) desde un script, nunca volcando el fichero al contexto.

## Reglas

- Ni `Read` ni `cat` sobre el dataset: usa el diccionario, `head -n 5` o scripts que impriman agregados.
- El perfil es una muestra: nulos, constantes o tipos mixtos son indicios. Si una decisión depende de ello (imputar, descartar una columna), compruébalo sobre el fichero completo.
- Un aviso de formato español significa que hay que normalizar (quitar punto de miles, coma → punto) en `src/` antes de convertir a número; anótalo en `## Notas`.
- Los códigos oficiales (INE, sección censal) aparecen como `int` si no tienen ceros a la izquierda en la muestra: léelos como texto igualmente.
- El perfil no hace split train/test: decide el preprocesado después del split.

## Límites conocidos

- Solo CSV/TSV (separador detectado: coma, punto y coma, tabulador o barra). Parquet, Excel o JSON no: conviértelos o perfílalos por trozos con pandas o polars.
- No detecta fechas: las ve como texto.
- «1.234» sin coma es ambiguo (mil doscientos o uno coma dos): se lee como decimal anglosajón. Revisa los rangos.
- Con saltos de línea dentro de campos entrecomillados, el paso de muestreo es aproximado; el conteo final de filas es exacto.

## Autocomprobación

`pytest -q tests/test_diccionario_datos.py`
