"""Versión Windows de raw_inmutable.py. La elige .claude/hooks/py-windows en Git Bash, MSYS o Cygwin.

Reutiliza toda la lógica de raw_inmutable.py (mismos modos pre, post y enlazar) y cubre lo que cambia en Windows:
- rutas con «\\» (data\\raw\\x.csv) y rutas MSYS (/c/proyecto/data/raw): se normalizan antes de comprobar;
- intérpretes con ruta o extensión (.venv\\Scripts\\python.exe -c …, py -c …) y órdenes con .exe;
- la herramienta PowerShell de Claude Code (Remove-Item, Move-Item, Set-Content, Copy-Item, Invoke-WebRequest,
  Expand-Archive -Force, [IO.File]::…, cmd /c del, powershell -EncodedCommand…);
- data/raw compartida entre worktrees con una unión de directorio (junction), que no pide permisos de administrador.
"""

from __future__ import annotations  # puede ejecutarse con un Python antiguo del sistema

import base64
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import raw_inmutable as comun

RAW = comun.RAW
RAW_EN_TEXTO = re.compile(r"data(?:/|\\)+raw", re.IGNORECASE)
UNIDAD_MSYS = re.compile(r"(?<![\w.:/-])/([a-zA-Z])(?=/)")
EXE = re.compile(r"(?<=\w)\.exe(?=[\s;&|)'\"]|$)", re.IGNORECASE)
INTERPRETE = re.compile(
    r"(^|[\s;&|(])(?:[^\s;&|()'\"]*/)?(python3?(?:\.\d+)?|py|node|perl|ruby|Rscript)(?=\s)",
    re.IGNORECASE,
)

# PowerShell: alias incluidos (PS 5.1 y 7). Se comparan en minúsculas.
PS_DESTRUCTIVAS = {
    "remove-item", "rm", "ri", "del", "erase", "rd", "rmdir",
    "move-item", "mv", "mi", "move",
    "rename-item", "ren", "rni",
    "clear-content", "clc", "clear-item", "cli",
    "set-itemproperty", "sp", "clear-itemproperty", "clp",
    "attrib", "icacls", "takeown", "set-acl",
}  # fmt: skip
# Nombres largos que se buscan en cualquier posición (dentro de ForEach-Object { … }, por ejemplo)
PS_LARGAS = {
    "remove-item", "move-item", "rename-item", "clear-content", "clear-item",
    "set-itemproperty", "clear-itemproperty", "set-acl",
}  # fmt: skip
PS_COPIAS = {"copy-item", "cp", "cpi", "copy"}
PS_ESCRITURAS = {
    "set-content",
    "sc",
    "add-content",
    "ac",
    "out-file",
    "tee-object",
    "tee",
}
PS_DESCARGAS = {
    "invoke-webrequest",
    "iwr",
    "invoke-restmethod",
    "irm",
    "curl",
    "wget",
    "start-bitstransfer",
}
PS_INTERRUPTORES = {
    "-force", "-recurse", "-noclobber", "-whatif", "-confirm", "-passthru", "-append",
    "-nonewline", "-usebasicparsing", "-container", "-asbytestream", "-raw",
}  # fmt: skip
NET = re.compile(
    r"\[(?:system\.)?io\.(?:file|directory|fileinfo|directoryinfo)\]::\s*\w*"
    r"(?:write|append|delete|move|copy|replace|create|setattributes|encrypt)",
    re.IGNORECASE,
)
TOKEN = re.compile(r"\"[^\"]*\"|'[^']*'|[^\s]+")


def normalizar_ruta(ruta: str) -> str:
    return UNIDAD_MSYS.sub(lambda m: m.group(1).upper() + ":", ruta.replace("\\", "/"))


def normalizar(orden: str) -> str:
    """Orden de Windows → forma que entiende raw_inmutable.py. Solo sirve para detectar: no se ejecuta."""
    texto = EXE.sub("", normalizar_ruta(orden))
    return INTERPRETE.sub(
        lambda m: (
            m.group(1)
            + ("python" if m.group(2).lower().startswith("py") else m.group(2))
        ),
        texto,
    )


def _tokens(texto: str) -> list[str]:
    return [t.strip("\"'").rstrip(",") for t in TOKEN.findall(texto)]


def _valor(args: list[str], nombres: tuple[str, ...]) -> str | None:
    """Valor de un parámetro de PowerShell, admitiendo abreviaturas (-Dest) y la forma -Path:valor."""
    for i, a in enumerate(args):
        if not a.startswith("-"):
            continue
        nombre, _, pegado = a.partition(":")
        nombre = nombre.lower()
        if len(nombre) >= 3 and any(n.startswith(nombre) for n in nombres):
            if pegado:
                return pegado
            if i + 1 < len(args):
                return args[i + 1]
    return None


def _posicionales(args: list[str]) -> list[str]:
    out, salta = [], False
    for a in args:
        if salta:
            salta = False
            continue
        if a.startswith("-"):
            salta = ":" not in a and a.lower() not in PS_INTERRUPTORES
            continue
        out.append(a)
    return out


def _pisa(ruta: str | None, base: Path) -> bool:
    """La ruta está en data/raw y escribir en ella cambiaría algo ya descargado (o no se puede saber: comodines)."""
    if not ruta:
        return False
    p = comun.en_raw(ruta, base)
    return p is not None and (
        bool(re.search(r"[*?\[]", ruta)) or (p.exists() and not p.is_dir())
    )


def _motivo_ps(texto: str, base: Path, profundidad: int = 0) -> str | None:
    if profundidad > 3:
        return None
    for tramo in re.split(r"&&|\|\||;|\n", texto):
        todos = _tokens(tramo)
        menciona = bool(RAW_EN_TEXTO.search(tramo)) or any(
            comun.en_raw(t, base) for t in todos if t and not t.startswith("-")
        )
        if menciona and NET.search(tramo):
            return "método .NET de [IO.File] o [IO.Directory] que escribe o borra en data/raw"
        if menciona and PS_LARGAS & {t.lower().lstrip("{($") for t in todos}:
            return "cmdlet que borra o cambia ficheros en un tramo que toca data/raw"
        for segmento in tramo.split("|"):
            toks = _tokens(segmento)
            while toks and toks[0] in {"&", "."}:
                toks = toks[1:]
            if not toks:
                continue
            cmd, args = toks[0].lower().rsplit("/", 1)[-1], toks[1:]
            minus = [a.lower() for a in args]
            if cmd == "cmd" and minus[:1] in (["/c"], ["/k"]):
                m = _motivo_ps(" ".join(args[1:]), base, profundidad + 1)
                if m:
                    return m
                continue
            if cmd in {"powershell", "pwsh"}:
                for i, a in enumerate(minus):
                    if a in {"-command", "-c"}:
                        m = motivo_powershell(
                            " ".join(args[i + 1 :]), base, profundidad + 1
                        )
                        if m:
                            return m
                    if a in {"-encodedcommand", "-enc", "-ec", "-e"} and i + 1 < len(
                        args
                    ):
                        try:
                            claro = base64.b64decode(args[i + 1]).decode("utf-16-le")
                        except ValueError:
                            continue
                        m = motivo_powershell(claro, base, profundidad + 1)
                        if m:
                            return m
                continue
            if not menciona:
                continue
            pos = _posicionales(args)
            if cmd in PS_DESTRUCTIVAS:
                return f"{toks[0]} sobre data/raw"
            if cmd in PS_COPIAS:
                destino = _valor(args, ("-destination",)) or (
                    pos[1] if len(pos) > 1 else None
                )
                if _pisa(destino, base):
                    return f"{toks[0]} sobrescribiría {destino}"
            if cmd in PS_ESCRITURAS:
                destino = _valor(args, ("-path", "-literalpath", "-filepath")) or (
                    pos[0] if pos else None
                )
                if _pisa(destino, base):
                    return f"{toks[0]} sobre {destino}, que ya existe"
            if cmd in PS_DESCARGAS:
                destino = _valor(args, ("-outfile", "-destination"))
                if _pisa(destino, base):
                    return f"{toks[0]} sobrescribiría {destino}"
            if cmd == "expand-archive" and "-force" in minus:
                return (
                    "Expand-Archive -Force en data/raw (sobrescribiría lo descargado)"
                )
            if cmd in {"new-item", "ni"} and "-force" in minus:
                destino = _valor(args, ("-path",)) or (pos[0] if pos else None)
                if _pisa(destino, base):
                    return f"New-Item -Force vaciaría {destino}"
    return None


def motivo_powershell(orden: str, base: Path, profundidad: int = 0) -> str | None:
    texto = normalizar(orden)
    # Las órdenes de estilo POSIX (rm, mv, cp, curl -o, git clean, python -c, redirecciones) ya las cubre el original
    return comun.motivo_bash(texto, base) or _motivo_ps(texto, base, profundidad)


def motivo(evento: dict, base: Path) -> str | None:
    herramienta = evento.get("tool_name", "")
    entrada = dict(evento.get("tool_input", {}) or {})
    if herramienta == "PowerShell":
        return motivo_powershell(entrada.get("command", "") or "", base)
    if herramienta == "Bash":
        return comun.motivo_bash(normalizar(entrada.get("command", "") or ""), base)
    for clave in ("file_path", "notebook_path"):
        if entrada.get(clave):
            entrada[clave] = normalizar_ruta(str(entrada[clave]))
    return comun.motivo({"tool_name": herramienta, "tool_input": entrada}, base)


def _mismo(a: Path, b: Path) -> bool:
    return os.path.normcase(os.path.realpath(a)) == os.path.normcase(
        os.path.realpath(b)
    )


def _enlazar(enlace: Path, destino: Path) -> None:
    """Unión de directorio en Windows (sin permisos de administrador); enlace simbólico en el resto."""
    try:
        import _winapi

        _winapi.CreateJunction(str(destino), str(enlace))
    except (ImportError, AttributeError):
        enlace.symlink_to(destino, target_is_directory=True)


def compartir_raw(base: Path) -> str:
    """Igual que raw_inmutable.compartir_raw, con una unión de directorio en lugar de un enlace simbólico."""

    def git(*args: str) -> str:
        r = subprocess.run(
            ["git", "-C", str(base), *args], capture_output=True, check=False, text=True
        )
        return r.stdout.strip()

    arriba, comun_dir = (
        git("rev-parse", "--show-toplevel"),
        git("rev-parse", "--git-common-dir"),
    )
    if not arriba or not comun_dir or Path(comun_dir).name != ".git":
        return ""
    comun_abs = Path(comun_dir) if Path(comun_dir).is_absolute() else base / comun_dir
    principal, aqui = comun_abs.parent.resolve(), Path(arriba).resolve()
    destino = principal / RAW
    destino.mkdir(parents=True, exist_ok=True)
    if _mismo(aqui, principal):
        return ""
    enlace = aqui / RAW
    if (enlace.exists() or enlace.is_symlink()) and _mismo(enlace, destino):
        return ""
    if enlace.exists():
        if enlace.is_dir() and not any(enlace.iterdir()):
            enlace.rmdir()
        else:
            return f"{enlace} tiene ficheros propios: muévelos a {destino} y bórrala para compartir los datos originales"
    enlace.parent.mkdir(parents=True, exist_ok=True)
    _enlazar(enlace, destino)
    return f"data/raw de este worktree enlazada a {destino} (una sola copia de los datos originales)"


def main() -> int:
    modo = sys.argv[1] if len(sys.argv) > 1 else "pre"
    texto, evento = comun.leer_evento()
    base = comun.raiz(evento)
    if modo == "enlazar":
        try:
            aviso = compartir_raw(base)
        except OSError as e:
            aviso = f"no se pudo enlazar data/raw con el checkout principal ({e!r})"
        if aviso:
            print(aviso)
        return 0
    if modo == "post":
        for b in {base, comun.raiz()}:  # la sesión y la carpeta del proyecto
            comun.solo_lectura(b)
        return 0
    if not (base / RAW).exists():
        try:
            compartir_raw(base)
        except OSError:
            pass
    try:
        ev = json.loads(texto)
        # Se mira también CLAUDE_PROJECT_DIR: el cwd de la sesión puede ser otro repo o un worktree sin enlazar
        m = next((r for b in {base, comun.raiz()} if (r := motivo(ev, b))), None)
    except Exception as e:  # noqa: BLE001 — falla cerrado solo si la acción podía tocar data/raw
        if RAW_EN_TEXTO.search(texto):
            print(
                f"Bloqueado: el hook de data/raw falló ({e!r}) y no puede garantizar nada. {comun.AYUDA}",
                file=sys.stderr,
            )
            return 2
        return 0
    if m:
        print(f"Bloqueado: {m}. {comun.AYUDA}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
