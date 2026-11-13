# Datos

Nada de esta carpeta se versiona salvo este fichero. Cada fuente se documenta aquí para que cualquiera (o cualquier agente) pueda reproducirla.

- `data/raw/`: descargas tal cual. Se añaden ficheros nuevos, pero no se editan ni se borran (un hook de Claude Code lo impide y los deja en solo lectura). Para actualizar una fuente, descárgala con la fecha en el nombre.
- `data/processed/`: salidas de `src/`, regenerables.

## Fuentes

| Nombre | URL | Licencia | Cómo obtenerla | Fichero en `raw/` |
|---|---|---|---|---|
| _ejemplo_ | https://… | CC BY 4.0 | `python -m src.descargas ine` | `ine_renta.csv` |
