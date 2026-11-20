"""Toda lectura o escritura de texto lleva encoding: en Windows el defecto es cp1252 (#291)."""

import ast
import re
from pathlib import Path

RAIZ = Path(__file__).parents[1]
CARPETAS = ["src", "app", "tests", "notebooks", ".github", ".claude"]
# posición del argumento encoding si se pasa sin nombre
POSICION = {"read_text": 0, "write_text": 1}
MODO = re.compile(r"[rwaxbtU+]+")
COMPRIMIDOS = {"gzip", "bz2", "lzma"}  # binarios por defecto: texto solo con "t"
AJENOS = {"tarfile", "zipfile", "webbrowser"}  # su .open no abre texto
# (posición del modo, posición del encoding) de módulo.open(ruta, ...); Path.open: (0, 2)
POSICIONES = {"io": (1, 3), "codecs": (1, 2)} | dict.fromkeys(COMPRIMIDOS, (1, 3))


def abre_texto(n: ast.Call, claves: dict[str | None, ast.expr]) -> bool:
    """open, io.open, codecs.open, Path.open o gzip/bz2/lzma.open en modo texto (sin mirar encoding)."""
    # shortcut: no sigue alias (import gzip as gz, from gzip import open); ampliarlo si el repo los usa
    f = n.func
    modulo = getattr(getattr(f, "value", None), "id", None)
    if modulo in AJENOS:
        return False
    pos_modo, pos_enc = (
        (1, 3) if isinstance(f, ast.Name) else POSICIONES.get(modulo, (0, 2))
    )
    if len(n.args) > pos_enc:
        return False
    por_nombre = len(n.args) <= pos_modo
    modo = claves.get("mode") if por_nombre else n.args[pos_modo]
    if modo is None:
        return modulo not in COMPRIMIDOS
    if not isinstance(modo, ast.Constant) or not isinstance(modo.value, str):
        # modo en variable: puede ser texto si es el modo seguro; en x.open(a), a no lo es
        return (por_nombre or pos_modo == 1) and modulo not in COMPRIMIDOS
    if not MODO.fullmatch(modo.value):  # z.open("a.csv"): un nombre, no un modo
        return False
    return ("t" in modo.value) if modulo in COMPRIMIDOS else ("b" not in modo.value)


def sin_encoding(codigo: str) -> list[int]:
    """Líneas con read_text, write_text u open de texto sin encoding (o con encoding=None)."""
    lineas = []
    for n in ast.walk(ast.parse(codigo)):
        if not isinstance(n, ast.Call):
            continue
        claves = {k.arg: k.value for k in n.keywords}
        enc = claves.get("encoding")
        if enc is not None and not (
            isinstance(enc, ast.Constant) and enc.value is None
        ):
            continue
        nombre = getattr(n.func, "attr", getattr(n.func, "id", None))
        if (nombre in POSICION and len(n.args) <= POSICION[nombre]) or (
            nombre == "open" and abre_texto(n, claves)
        ):
            lineas.append(n.lineno)
    return lineas


def test_detecta_lo_que_falta():
    codigo = """
p.read_text()
p.write_text("ñ")
open(r)
p.open("w")
p.read_text("utf-8")
p.write_text("ñ", "utf-8")
p.write_text("ñ", encoding="utf-8")
open(r, "rb")
p.open("rb")
opener.open(url, cuerpo)
p.read_text(encoding=None)
open(r, mode="rb")
p.open(mode="w")
open(r, "r", -1, "utf-8")
io.open(r)
gzip.open(r, "rt")
open(r, modo)
z.open("a.csv")
gzip.open(r)
gzip.open(r, "rt", encoding="utf-8")
tarfile.open(r, "r")
webbrowser.open("http://x")
bz2.open(r, mode="wt")
io.open(r, "rb")
codecs.open(r)
codecs.open(r, "r", "utf-8")
p.open(mode=m)
"""
    assert sin_encoding(codigo) == [2, 3, 4, 5, 12, 14, 16, 17, 18, 24, 26, 28]


def test_todo_el_repo_lleva_encoding():
    fallos = [
        f"{f.relative_to(RAIZ)}:{linea}"
        for carpeta in CARPETAS
        for f in sorted((RAIZ / carpeta).rglob("*.py"))
        if not {"worktrees", ".venv"}
        & set(f.relative_to(RAIZ).parts)  # otros checkouts
        for linea in sin_encoding(f.read_text(encoding="utf-8"))
    ]
    assert not fallos, "falta encoding='utf-8':\n" + "\n".join(fallos)
