"""Toda cifra que ve el público (guion del pitch y textos de la app) lleva su fuente en la misma línea.

Uso: python cifras_con_fuente.py [ficheros…]   (sin argumentos revisa todo lo vigilado)
     python cifras_con_fuente.py --hook          (PostToolUse: lee el evento de Claude Code por stdin)
Marcas válidas en la línea: una nota al pie [^id] definida en el mismo fichero, o «fuente:».
Una línea sin cifras reales se exime con <!-- sin-fuente: motivo -->.
"""

import json
import os
import re
import sys
from pathlib import Path

VIGILADO = ("docs/pitch/", "app/")
# shortcut: solo textos; cuando se decida el stack de app/, añade aquí sus ficheros de texto visibles
EXTENSIONES = {".md", ".html", ".txt"}

CIFRA = re.compile(
    r"(?<![\w.,/:-])\d{1,3}(?:[.\s]\d{3})*(?:,\d+)?(?:\s?(?:%|€|euros?\b))?(?![\w/:])"
)
NO_ES_CIFRA = [
    re.compile(r"\b\d{1,2}:\d{2}\b"),  # horas o minutos del guion
    re.compile(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b"),  # fechas
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),  # fechas ISO
    re.compile(r"\bv?\d+\.\d+\.\d+\b"),  # versiones
]
NOTA = re.compile(r"\[\^([\w-]+)\](?!:)")
DEF_NOTA = re.compile(r"^\[\^([\w-]+)\]:", re.MULTILINE)


def es_cifra(texto: str) -> bool:
    """Un año suelto, un número de lista o un número de una cifra no cuentan; % y € siempre."""
    if "%" in texto or "€" in texto or "euro" in texto:
        return True
    n = texto.replace(".", "").replace(" ", "").replace(",", "")
    if not n.isdigit():
        return False
    valor = int(n)
    return valor >= 10 and not (1900 <= valor <= 2099 and "," not in texto)


def revisar(ruta: Path) -> list[str]:
    texto = ruta.read_text(encoding="utf-8")
    definidas = set(DEF_NOTA.findall(texto))
    errores, en_codigo = [], False
    for n, linea in enumerate(texto.splitlines(), 1):
        if linea.lstrip().startswith("```"):
            en_codigo = not en_codigo
            continue
        if (
            en_codigo
            or "sin-fuente:" in linea
            or DEF_NOTA.match(linea)
            or re.fullmatch(r"[\s|:-]*", linea)
        ):
            continue
        limpia = re.sub(
            r"<!--.*?-->|<[^>]*>|\[\^[\w-]+\]|\]\([^)]*\)|`[^`]*`", " ", linea
        )
        limpia = re.sub(r"^\s*(?:#+|\d+[.)]|[-*+])\s+", "", limpia)
        for patron in NO_ES_CIFRA:
            limpia = patron.sub(" ", limpia)
        cifras = [m.group(0) for m in CIFRA.finditer(limpia) if es_cifra(m.group(0))]
        if not cifras:
            continue
        notas = NOTA.findall(linea)
        sin_definir = [x for x in notas if x not in definidas]
        if sin_definir:
            errores.append(
                f"{ruta}:{n}: nota [^{sin_definir[0]}] sin definir en el fichero"
            )
        elif not notas and "fuente:" not in linea.lower():
            errores.append(
                f"{ruta}:{n}: cifra sin fuente ({', '.join(cifras[:3])}): añade [^id] o «fuente:»"
            )
    return errores


def vigilado(ruta: Path, raiz: Path) -> bool:
    try:
        rel = ruta.resolve().relative_to(raiz.resolve()).as_posix()
    except ValueError:
        return False
    return rel.startswith(VIGILADO) and ruta.suffix in EXTENSIONES


def desde_hook() -> int:
    """PostToolUse: revisa el fichero editado. Si el evento no se entiende, no bloquea (la CI lo cubre)."""
    try:
        ruta = json.load(sys.stdin).get("tool_input", {}).get("file_path") or ""
    except Exception:  # noqa: BLE001 — un hook no debe romper la sesión
        return 0
    return main([ruta]) if ruta else 0


def main(argv: list[str]) -> int:
    raiz = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())
    if argv:
        rutas = [Path(a) for a in argv]
    else:
        rutas = [
            p for d in VIGILADO if (raiz / d).is_dir() for p in (raiz / d).rglob("*")
        ]
    errores = [
        e for r in rutas if r.is_file() and vigilado(r, raiz) for e in revisar(r)
    ]
    if errores:
        print("\n".join(errores), file=sys.stderr)
        print(
            "Cada cifra que ve el público lleva su fuente en la misma línea (y «estimado» si lo es). "
            "Ver AGENTS.md, «Cifras con fuente».",
            file=sys.stderr,
        )
        return 2 if argv else 1
    return 0


if __name__ == "__main__":
    sys.exit(desde_hook() if sys.argv[1:] == ["--hook"] else main(sys.argv[1:]))
