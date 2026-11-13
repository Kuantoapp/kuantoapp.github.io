# Datos

Nada de esta carpeta se versiona salvo este fichero. Cada fuente se documenta aquí para que cualquiera (o cualquier agente) pueda reproducirla.

- `data/raw/`: descargas tal cual. Se añaden ficheros nuevos, pero no se editan ni se borran (un hook de Claude Code lo impide y los deja en solo lectura). Para actualizar una fuente, descárgala con la fecha en el nombre.
- `data/processed/`: salidas de `src/`, regenerables. Cada worktree tiene la suya; `data/raw/` es compartida: al abrir sesión, un hook de Claude Code la enlaza a la del checkout principal (macOS y Linux; si la del worktree ya tiene ficheros, avisa y no enlaza). Sin Claude Code, enlázala tú desde el worktree con `python3 .claude/hooks/raw_inmutable.py enlazar`.

## Fuentes

| Nombre | URL | Licencia | Cómo obtenerla | Fichero en `raw/` |
|---|---|---|---|---|
| _ejemplo_ | https://… | CC BY 4.0 | `python -m src.descargas ine` | `ine_renta.csv` |
