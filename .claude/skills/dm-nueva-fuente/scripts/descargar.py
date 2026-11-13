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
import http.client
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

NOMBRE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
EXT = re.compile(r"^[a-z0-9]{1,8}$")


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
    ext = ext.lstrip(".").lower()
    if not EXT.match(ext):
        raise SystemExit(f"Extensión no válida: {ext}")
    raw.mkdir(parents=True, exist_ok=True)
    final = raw / f"{nombre}_{hoy.isoformat()}.{ext}"
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
                declarado = getattr(r, "headers", {}).get("Content-Length")
                for trozo in iter(lambda: r.read(1 << 20), b""):
                    f.write(trozo)
            # http.client no avisa si la conexión se corta antes de tiempo: se compara con lo anunciado
            if declarado and parcial.stat().st_size != int(declarado):
                raise SystemExit(
                    f"Descarga incompleta de {url}: {parcial.stat().st_size} de {declarado} bytes."
                )
        except (OSError, http.client.HTTPException) as e:
            raise SystemExit(f"No se pudo descargar {url}: {e}") from None
        if parcial.stat().st_size == 0:
            raise SystemExit(f"La descarga de {url} está vacía.")
        os.link(parcial, final)  # falla si alguien lo creó entretanto: nunca pisa
    finally:
        parcial.unlink(missing_ok=True)
    return final


def tabla_fuentes(readme: Path) -> tuple[list[str], list[list[str]]]:
    """La primera tabla de data/README.md (la de fuentes): termina en la primera línea que no es fila."""
    filas = []
    for linea in readme.read_text(encoding="utf-8").splitlines():
        if not linea.startswith("|"):
            if filas:
                break
            continue
        if not linea.startswith("|---"):
            filas.append([c.strip() for c in linea.strip().strip("|").split("|")])
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
        if fila[0].startswith("_"):
            continue
        if len(fila) != len(cabecera):
            problemas.append(
                f"fila mal formada (¿un | dentro de una celda?): {fila[0]}"
            )
            continue
        fichero, esperado = fila[c_fich].strip("`"), fila[c_sha].strip("`")
        ruta = raw / fichero
        if not fichero:
            problemas.append(f"{fila[0]}: sin fichero en data/README.md")
        elif not esperado:
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
