"""Toda lectura o escritura de texto lleva encoding: en Windows el defecto es cp1252 (#291)."""

import ast
from pathlib import Path

RAIZ = Path(__file__).parents[1]
CARPETAS = ["src", "app", "tests", "notebooks", ".github", ".claude"]
# posición del argumento encoding si se pasa sin nombre
POSICION = {"read_text": 0, "write_text": 1}


def sin_encoding(codigo: str) -> list[int]:
    """Líneas con read_text, write_text u open de texto sin encoding."""
    lineas = []
    # shortcut: no ve io.open, gzip.open(r, "rt") ni un modo en variable, y marca
    # z.open("a.csv") de zipfile; ampliarlo si aparece alguno en el repo
    for n in ast.walk(ast.parse(codigo)):
        if not isinstance(n, ast.Call):
            continue
        claves = {k.arg: k.value for k in n.keywords}
        enc = claves.get("encoding")
        if (
            enc is not None and getattr(enc, "value", 0) is not None
        ):  # encoding=None falta
            continue
        nombre = getattr(n.func, "attr", getattr(n.func, "id", None))
        if nombre in POSICION:
            falta = len(n.args) <= POSICION[nombre]
        elif nombre == "open":
            # open(ruta, modo) o ruta.open(modo); otro .open (urllib) no lleva modo literal
            suelto = isinstance(n.func, ast.Name)
            if suelto and len(n.args) > 3:  # open(r, modo, buffering, encoding)
                continue
            modo = n.args[1:2] if suelto else n.args[:1]
            modo = modo or ([claves["mode"]] if "mode" in claves else [])
            literal = (
                modo[0].value if modo and isinstance(modo[0], ast.Constant) else None
            )
            falta = (not modo or isinstance(literal, str)) and "b" not in (
                literal or ""
            )
        else:
            continue
        if falta:
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
"""
    assert sin_encoding(codigo) == [2, 3, 4, 5, 12, 14]


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
