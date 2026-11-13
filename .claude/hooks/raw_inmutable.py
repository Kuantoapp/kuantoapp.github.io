"""Hook: data/raw/ admite descargas nuevas, pero nada de lo descargado se cambia ni se borra.

pre      (PreToolUse, Edit|Write|MultiEdit|NotebookEdit|Bash): bloquea con exit 2 y explica por qué.
enlazar  (SessionStart): en un worktree, data/raw apunta a la del checkout principal (una sola copia original).
post (PostToolUse, Bash|Write): deja en solo lectura lo descargado, para que tampoco un script lo pise.
Falla cerrado: si el propio hook falla y la acción menciona data/raw, la bloquea.
"""

from __future__ import annotations  # Python 3.9 (el de macOS) no entiende `Path | None`

import json
import os
import re
import shlex
import subprocess
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
# Código en línea: borrar algo cuando se menciona data/raw, o escribir en una ruta de data/raw
BORRA = re.compile(
    r"\b(?:os\.remove|os\.unlink|os\.rename|os\.replace|shutil\.rmtree|shutil\.move|\.unlink|\.rmdir|unlinkSync|rmSync|renameSync)\s*\("
)
ESCRIBE_EN_RAW = re.compile(
    r"(?:to_csv|to_parquet|to_excel|to_json|write_text|write_bytes|writeFileSync)\s*\(\s*[rfb]?['\"][^'\"]*data/raw"
    r"|open\(\s*[rfb]?['\"][^'\"]*data/raw[^'\"]*['\"]\s*,\s*[rfb]?['\"][^'\"]*[wax+]"
)


def raiz() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())


def en_raw(ruta: str, base: Path) -> Path | None:
    p = Path(ruta).expanduser()
    p = (p if p.is_absolute() else base / p).resolve()
    raw = (base / RAW).resolve()
    return p if p == raw or raw in p.parents else None


def toca_raw(args: list[str], base: Path) -> bool:
    return any(en_raw(a, base) for a in args if not a.startswith("-"))


def motivo_fichero(ruta: str, herramienta: str, base: Path) -> str | None:
    p = en_raw(ruta, base)
    if p is None:
        return None
    if herramienta == "Write" and not p.exists():
        return None  # fichero nuevo: es una descarga
    return f"{herramienta} sobre {ruta}"


def motivo_bash(orden: str, base: Path) -> str | None:
    # shortcut: no sigue `cd` ni lo que hace un script por dentro; lo cubre el modo post (solo lectura)
    # El código en línea se mira entero: contiene `;` y se partiría en tramos
    interprete = re.search(
        r"(?:^|[\s;&|(])(?:python3?|node|perl|ruby|Rscript)\s[^\n]*?-[ce]\s", orden
    )
    if interprete and (
        (RAW in orden and BORRA.search(orden)) or ESCRIBE_EN_RAW.search(orden)
    ):
        return "código en línea que escribe o borra en data/raw"
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
        while partes and (
            partes[0] in {"sudo", "env", "command", "nohup"} or "=" in partes[0]
        ):
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
        if (
            cmd == "sed"
            and any(a.startswith("-i") or a == "--in-place" for a in args)
            and toca_raw(args, base)
        ):
            return "sed -i sobre data/raw"
        if cmd in DESTRUCTIVAS and toca_raw(args, base):
            return f"{cmd} sobre data/raw"
        if (
            cmd == "find"
            and toca_raw(args, base)
            and {"-delete", "-exec", "-execdir", "-ok"} & set(args)
        ):
            return "find con -delete o -exec sobre data/raw"
        if (
            cmd == "xargs"
            and DESTRUCTIVAS & {Path(a).name for a in args}
            and RAW in orden
        ):
            return "xargs con una orden destructiva sobre data/raw"
        if (
            cmd == "tar"
            and toca_raw(args, base)
            and any(a.startswith("-") and "x" in a or a == "--extract" for a in args)
        ):
            conserva = {"--keep-old-files", "--skip-old-files"} & set(args) or any(
                re.fullmatch(r"-[a-zA-Z]*k[a-zA-Z]*", a) for a in args
            )
            if not conserva:
                return "tar -x en data/raw sin -k (sobrescribiría lo descargado)"
        if cmd == "unzip" and toca_raw(args, base) and "-n" not in args:
            return "unzip en data/raw sin -n (sobrescribiría lo descargado)"
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


def solo_lectura(base: Path) -> None:
    raw = base / RAW
    if raw.is_dir():
        for f in raw.rglob("*"):
            if f.is_file() and os.access(f, os.W_OK):
                f.chmod(f.stat().st_mode & ~0o222)


def motivo(evento: dict, base: Path) -> str | None:
    herramienta, entrada = (
        evento.get("tool_name", ""),
        evento.get("tool_input", {}) or {},
    )
    if herramienta == "Bash":
        return motivo_bash(entrada.get("command", ""), base)
    ruta = entrada.get("file_path") or entrada.get("notebook_path") or ""
    return motivo_fichero(ruta, herramienta, base) if ruta else None


def compartir_raw(base: Path) -> str:
    """En un worktree, data/raw es un enlace a la del checkout principal; data/processed sigue siendo propia de la rama."""

    def git(*args: str) -> str:
        r = subprocess.run(
            ["git", "-C", str(base), *args], capture_output=True, check=False, text=True
        )
        return r.stdout.strip()

    arriba, comun = (
        git("rev-parse", "--show-toplevel"),
        git("rev-parse", "--git-common-dir"),
    )
    if not arriba or not comun or Path(comun).name != ".git":
        return ""
    comun_abs = (
        Path(comun) if Path(comun).is_absolute() else base / comun
    )  # git antiguo: sin --path-format
    principal, aqui = comun_abs.parent.resolve(), Path(arriba).resolve()
    destino = principal / RAW
    destino.mkdir(parents=True, exist_ok=True)
    if aqui == principal:
        return ""
    # shortcut: enlaces simbólicos de macOS y Linux; en Windows haría falta modo desarrollador o una unión
    enlace = aqui / RAW
    if enlace.is_symlink() and enlace.resolve() == destino.resolve():
        return ""
    if enlace.exists():
        if enlace.is_dir() and not any(enlace.iterdir()):
            enlace.rmdir()
        else:
            return f"{enlace} tiene ficheros propios: muévelos a {destino} y bórrala para compartir los datos originales"
    enlace.parent.mkdir(parents=True, exist_ok=True)
    enlace.symlink_to(destino, target_is_directory=True)
    return f"data/raw de este worktree enlazada a {destino} (una sola copia de los datos originales)"


def main() -> int:
    modo = sys.argv[1] if len(sys.argv) > 1 else "pre"
    base = raiz()
    if modo == "enlazar":
        try:
            aviso = compartir_raw(base)
        except OSError as e:
            aviso = f"no se pudo enlazar data/raw con el checkout principal ({e!r})"
        if aviso:
            print(aviso)
        return 0
    if modo == "post":
        solo_lectura(base)
        return 0
    texto = sys.stdin.read()
    if not (
        base / RAW
    ).exists():  # sesión que no pasó por SessionStart (p. ej. un worktree nuevo)
        try:
            compartir_raw(base)
        except OSError:
            pass
    try:
        m = motivo(json.loads(texto), base)
    except Exception as e:  # noqa: BLE001 — falla cerrado solo si la acción podía tocar data/raw
        if RAW in texto:
            print(
                f"Bloqueado: el hook de data/raw falló ({e!r}) y no puede garantizar nada. {AYUDA}",
                file=sys.stderr,
            )
            return 2
        return 0
    if m:
        print(f"Bloqueado: {m}. {AYUDA}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
