"""Hook: data/raw/ admite descargas nuevas, pero nada de lo descargado se cambia ni se borra.

pre  (PreToolUse, Edit|Write|MultiEdit|NotebookEdit|Bash): bloquea con exit 2 y explica por qué.
post (PostToolUse, Bash): deja en solo lectura lo descargado, para que tampoco un script lo pise.
"""

import json
import os
import re
import shlex
import sys
from pathlib import Path

RAW = "data/raw"
AYUDA = (
    "data/raw/ es inmutable: descarga con un nombre nuevo (por ejemplo con la fecha) y escribe "
    "lo derivado en data/processed/. Para borrar una descarga vieja, pídeselo a una persona."
)
# Órdenes que cambian o borran lo que tocan, apunten donde apunten dentro de data/raw
DESTRUCTIVAS = {
    "rm",
    "rmdir",
    "unlink",
    "mv",
    "truncate",
    "shred",
    "chmod",
    "chown",
    "touch",
}
# Órdenes que escriben en su último argumento: solo se permiten si el fichero aún no existe
COPIAS = {"cp", "rsync", "ln", "install"}
SALIDA = {"-o", "--output", "-O", "--output-document"}


def raiz() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())


def en_raw(ruta: str, base: Path) -> Path | None:
    p = Path(ruta).expanduser()
    p = (p if p.is_absolute() else base / p).resolve()
    raw = (base / RAW).resolve()
    return p if p == raw or raw in p.parents else None


def motivo_fichero(ruta: str, herramienta: str, base: Path) -> str | None:
    p = en_raw(ruta, base)
    if p is None:
        return None
    if herramienta == "Write" and not p.exists():
        return None  # fichero nuevo: es una descarga
    return f"{herramienta} sobre {ruta}"


def motivo_bash(orden: str, base: Path) -> str | None:
    # shortcut: no sigue `cd` ni rutas dentro de scripts; lo cubre el modo post (solo lectura en disco)
    for tramo in re.split(r"&&|\|\||;|\||\n", orden):
        # Redirecciones: crear un fichero nuevo vale; sobrescribir o añadir a uno existente, no
        for destino in re.findall(r">>?\s*([^\s;&|<>]+)", tramo):
            p = en_raw(destino, base)
            if p is not None and p.exists():
                return f"redirección sobre {destino}, que ya existe"
        try:
            partes = shlex.split(tramo)
        except ValueError:
            partes = tramo.split()
        while partes and (partes[0] in {"sudo", "env", "command"} or "=" in partes[0]):
            partes = partes[1:]
        if not partes:
            continue
        cmd, args = Path(partes[0]).name, partes[1:]
        rutas = [a for a in args if not a.startswith("-")]
        if (
            cmd == "git"
            and args[:1] == ["clean"]
            and any("x" in a.lower() for a in args if a.startswith("-"))
        ):
            return "git clean con -x o -X borra data/ (está ignorado por git)"
        if cmd == "sed" and any(a.startswith("-i") or a == "--in-place" for a in args):
            if any(en_raw(r, base) for r in rutas):
                return "sed -i sobre data/raw"
        if cmd in DESTRUCTIVAS and any(en_raw(r, base) for r in rutas):
            return f"{cmd} sobre data/raw"
        if cmd in COPIAS and rutas:
            p = en_raw(rutas[-1], base)
            if p is not None and p.exists() and not p.is_dir():
                return f"{cmd} sobrescribiría {rutas[-1]}"
        if cmd in {"curl", "wget", "tee"}:
            destinos = [args[i + 1] for i, a in enumerate(args[:-1]) if a in SALIDA]
            destinos += rutas if cmd == "tee" else []
            for d in destinos:
                p = en_raw(d, base)
                if p is not None and p.exists():
                    return f"{cmd} sobrescribiría {d}"
    return None


def main() -> int:
    modo = sys.argv[1] if len(sys.argv) > 1 else "pre"
    base = raiz()
    if modo == "post":
        raw = base / RAW
        if raw.is_dir():
            for f in raw.rglob("*"):
                if f.is_file() and os.access(f, os.W_OK):
                    f.chmod(f.stat().st_mode & ~0o222)
        return 0
    evento = json.load(sys.stdin)
    herramienta, entrada = evento.get("tool_name", ""), evento.get("tool_input", {})
    if herramienta == "Bash":
        motivo = motivo_bash(entrada.get("command", ""), base)
    else:
        ruta = entrada.get("file_path") or entrada.get("notebook_path") or ""
        motivo = motivo_fichero(ruta, herramienta, base) if ruta else None
    if motivo:
        print(f"Bloqueado: {motivo}. {AYUDA}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
