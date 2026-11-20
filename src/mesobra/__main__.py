"""`python -m mesobra`: comprueba las fuentes, regenera la API estática y valida `app/datos/` (#104)."""

import json
import logging
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from mesobra.api_estatica import FICHEROS, validar

RAIZ = Path(__file__).resolve().parents[2]
DESCARGAR = RAIZ / ".claude/skills/dm-nueva-fuente/scripts/descargar.py"
PASOS = ("pipeline_territorio", "pipeline_euros", "pipeline_analisis", "sdm")

log = logging.getLogger("mesobra")


def comprobar_fuentes(readme: Path, raw: Path) -> None:
    """Se detiene si falta una fuente de `readme` en `raw` o su SHA-256 no coincide.

    Reutiliza el script de `dm-nueva-fuente`, cuya `comprobar` solo avisa de los ausentes.
    """
    spec = spec_from_file_location("descargar", DESCARGAR)
    script = module_from_spec(spec)
    spec.loader.exec_module(script)
    cabecera, filas = script.tabla_fuentes(readme)
    if "Cómo obtenerla" not in cabecera:
        raise SystemExit(f"{readme} no tiene la columna «Cómo obtenerla»")
    c_como = cabecera.index("Cómo obtenerla")
    c_fich = next(i for i, c in enumerate(cabecera) if c.startswith("Fichero"))
    faltan = [
        f"{f[c_fich].strip('`')}: {f[c_como]}"
        for f in filas
        if not f[0].startswith("_")
        and len(f) == len(cabecera)
        and f[c_fich].strip("`")
        and not (raw / f[c_fich].strip("`")).exists()
    ]
    if faltan:
        raise SystemExit(
            f"Faltan {len(faltan)} ficheros en {raw} (fichero: cómo obtenerlo):\n"
            + "\n".join(faltan)
        )
    if problemas := script.comprobar(readme, raw):
        raise SystemExit(
            "Fuentes distintas de data/README.md:\n" + "\n".join(problemas)
        )


def validar_api(carpeta: Path) -> None:
    """Valida cada fichero de `carpeta` contra el contrato de `api_estatica`."""
    leidos = {n: json.loads((carpeta / n).read_text("utf-8")) for n in FICHEROS}
    for nombre, objeto in leidos.items():
        validar(nombre, objeto, leidos["zonas.geojson"])


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    comprobar_fuentes(RAIZ / "data/README.md", RAIZ / "data/raw")
    for paso in PASOS:
        log.info("Ejecutando %s", paso)
        import_module(f"mesobra.{paso}").main()
    validar_api(RAIZ / "app/datos")
    log.info("API estática regenerada y válida")


if __name__ == "__main__":
    main()
