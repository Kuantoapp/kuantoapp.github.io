"""Descarga reproducible a data/raw y comprobación de que todos tienen los mismos datos. Solo stdlib.

descargar.py URL --nombre ine_renta [--ext csv]
    Guarda data/raw/<nombre>_<AAAA-MM-DD>.<ext> sin sobrescribir nada, calcula su SHA-256
    e imprime la fila para la tabla de data/README.md.
descargar.py --comprobar
    Compara el SHA-256 de cada fichero de la tabla de data/README.md con el de data/raw.
    Sale con 1 si alguno difiere (el publicador cambió el fichero o la descarga está corrupta).
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

NOMBRE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for trozo in iter(lambda: f.read(1 << 20), b""):
            h.update(trozo)
    return h.hexdigest()


def descargar(
    url: str,
    nombre: str,
    ext: str,
    raw: Path,
    hoy: date,
    abrir=urllib.request.urlopen,
) -> Path:
    if urlparse(url).scheme != "https":
        raise SystemExit(f"Solo https: {url}")
    if not NOMBRE.match(nombre):
        raise SystemExit(f"Nombre no válido (minúsculas, cifras, _ y -): {nombre}")
    raw.mkdir(parents=True, exist_ok=True)
    final = raw / f"{nombre}_{hoy.isoformat()}.{ext.lstrip('.')}"
    if final.exists():
        raise SystemExit(
            f"Ya existe {final}: data/raw no se sobrescribe. Usa ese fichero."
        )
    # Se descarga fuera de data/raw y se enlaza al final: nunca queda un fichero a medias en raw
    parcial = (
        raw.resolve().parent / f".{final.name}.parcial"
    )  # mismo disco que raw aunque sea un enlace
    peticion = urllib.request.Request(
        url, headers={"User-Agent": "dm-nueva-fuente/1.0"}
    )
    try:
        try:
            with abrir(peticion, timeout=120) as r, parcial.open("wb") as f:
                if urlparse(getattr(r, "url", None) or url).scheme != "https":
                    raise SystemExit(f"{url} redirige a una dirección sin https.")
                for trozo in iter(lambda: r.read(1 << 20), b""):
                    f.write(trozo)
        except (urllib.error.URLError, TimeoutError) as e:
            raise SystemExit(f"No se pudo descargar {url}: {e}") from None
        if parcial.stat().st_size == 0:
            raise SystemExit(f"La descarga de {url} está vacía.")
        os.link(parcial, final)  # falla si alguien lo creó entretanto: nunca pisa
    finally:
        parcial.unlink(missing_ok=True)
    return final


def tabla_fuentes(readme: Path) -> tuple[list[str], list[list[str]]]:
    filas = [
        [c.strip() for c in linea.strip().strip("|").split("|")]
        for linea in readme.read_text(encoding="utf-8").splitlines()
        if linea.startswith("|") and not linea.startswith("|---")
    ]
    return (filas[0], filas[1:]) if filas else ([], [])


def comprobar(readme: Path, raw: Path) -> list[str]:
    cabecera, filas = tabla_fuentes(readme)
    try:
        c_fich = next(i for i, c in enumerate(cabecera) if c.startswith("Fichero"))
        c_sha = cabecera.index("SHA-256")
    except (StopIteration, ValueError):
        return ["data/README.md no tiene las columnas «Fichero en `raw/`» y «SHA-256»"]
    problemas = []
    for fila in filas:
        if fila[0].startswith("_") or len(fila) <= max(c_fich, c_sha):
            continue
        fichero, esperado = fila[c_fich].strip("`"), fila[c_sha].strip("`")
        ruta = raw / fichero
        if not esperado:
            problemas.append(f"{fichero}: sin SHA-256 en data/README.md")
        elif not ruta.exists():
            print(
                f"aviso: falta {fichero} en data/raw (descárgalo con «Cómo obtenerla»)"
            )
        elif sha256(ruta) != esperado:
            problemas.append(
                f"{fichero}: SHA-256 distinto del de data/README.md. El publicador cambió el fichero "
                "o la descarga está corrupta: no lo uses; descarga de nuevo con la fecha de hoy y actualiza la fila"
            )
    return problemas


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("url", nargs="?")
    p.add_argument("--nombre", help="fuente en minúsculas: ine_renta, madrid_barrios…")
    p.add_argument("--ext", help="extensión si la URL no la trae (csv, zip, json…)")
    p.add_argument("--comprobar", action="store_true")
    p.add_argument(
        "--raiz",
        type=Path,
        default=Path.cwd(),
        help="raíz del repo (por defecto, la actual)",
    )
    a = p.parse_args()
    raw, readme = a.raiz / "data/raw", a.raiz / "data/README.md"
    if a.comprobar:
        problemas = comprobar(readme, raw)
        print("\n".join(problemas) or "Todo coincide con data/README.md.")
        return 1 if problemas else 0
    if not (a.url and a.nombre):
        p.error("hace falta URL y --nombre (o --comprobar)")
    ext = a.ext or Path(urlparse(a.url).path).suffix.lstrip(".")
    if not ext:
        p.error("la URL no trae extensión: pasa --ext")
    final = descargar(a.url, a.nombre, ext, raw, date.today())
    huella = sha256(final)
    orden = f"`python .claude/skills/dm-nueva-fuente/scripts/descargar.py {a.url} --nombre {a.nombre}`"
    print(f"Guardado {final} ({final.stat().st_size} bytes)\nSHA-256 {huella}\n")
    print("Fila para data/README.md (completa nombre y licencia):")
    print(
        f"| <Nombre> | {a.url} | <licencia> | {orden} | `{final.name}` | `{huella}` |"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
