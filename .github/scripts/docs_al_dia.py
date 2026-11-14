"""Documentación al día: lo que cambia arrastra su documentación, y la documentación no apunta a nada que no exista.

Dos comprobaciones:
1. Cambios sin su documentación: si cambian ciertas rutas, tiene que cambiar al menos uno de sus documentos (REGLAS),
   y una URL nueva en el código exige tocar data/README.md (cada fuente se documenta allí).
2. Referencias rotas: rutas entre comillas invertidas y enlaces de los .md que ya no existen.

Uso: python docs_al_dia.py            (CI: compara con la rama base del PR; acepta «Docs: sin cambios — motivo» en el PR)
     python docs_al_dia.py --stop     (hook Stop: recuerda una vez al agente lo que falta antes de terminar)
"""

from __future__ import annotations  # puede ejecutarse con el Python 3.9 de macOS

import json
import os
import re
import subprocess
import sys
from pathlib import Path

# (qué cambió, documentos de los que basta con tocar uno, por qué)
REGLAS = [
    (
        r"^\.claude/(hooks/|settings\.json$)",
        ("AGENTS.md", ".claude/README.md"),
        "hooks o permisos de Claude Code",
    ),
    (
        r"^\.github/(workflows|scripts)/",
        ("AGENTS.md", "README.md", ".claude/README.md"),
        "CI o comprobaciones",
    ),
    (
        r"^(requirements[^/]*\.txt|\.python-version|pyproject\.toml)$",
        ("docs/decisiones.md", "README.md"),
        "dependencias",
    ),
    (
        r"^\.claude/(agents|skills)/",
        (".claude/README.md", "AGENTS.md"),
        "agentes o skills (índice y reglas)",
    ),
]
CODIGO = ("src/", "app/", "notebooks/")
EXENCION = re.compile(r"^\s*docs:\s*sin cambios\b", re.IGNORECASE | re.MULTILINE)
DOCS = ["README.md", "AGENTS.md", "CLAUDE.md", ".claude/README.md", "data/README.md"]
DIRS_DOCS = ["docs", ".claude/skills", ".claude/agents"]
RUTA = re.compile(
    r"`((?:\.github|\.claude|src|app|tests|docs|notebooks)/[^`\s]+\.[a-z]{1,5})`"
)
ENLACE = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=False
    ).stdout


def cambios(base: str, con_trabajo: bool) -> tuple[set[str], list[str]]:
    """Ficheros cambiados y líneas añadidas en el código desde la base (con lo no confirmado si con_trabajo)."""
    desde = git("merge-base", base, "HEAD").strip() or base
    rango = [desde] if con_trabajo else [f"{desde}...HEAD"]
    nombres = set(git("diff", "--name-only", *rango).split())
    if con_trabajo:
        nombres |= set(git("ls-files", "--others", "--exclude-standard").split())
    nuevas = [
        linea[1:]
        for linea in git("diff", "-U0", *rango, "--", *CODIGO).splitlines()
        if linea.startswith("+") and not linea.startswith("+++")
    ]
    return nombres, nuevas


def sin_documentar(nombres: set[str], nuevas: list[str]) -> list[str]:
    errores = []
    for patron, docs, motivo in REGLAS:
        tocados = sorted(n for n in nombres if re.search(patron, n))
        if tocados and not set(docs) & nombres:
            errores.append(
                f"Cambian {motivo} ({', '.join(tocados[:3])}) y no se actualizó {' ni '.join(docs)}"
            )
    urls = sorted(
        {u for linea in nuevas for u in re.findall(r"https?://[^\s'\"<>)]+", linea)}
    )
    if urls and "data/README.md" not in nombres:
        errores.append(
            f"Hay URLs nuevas en el código ({', '.join(urls[:2])}) y no se documentaron en data/README.md"
        )
    return errores


def referencias_rotas(raiz: Path) -> list[str]:
    ficheros = [raiz / d for d in DOCS if (raiz / d).exists()]
    for d in DIRS_DOCS:
        if (raiz / d).is_dir():
            ficheros += sorted((raiz / d).rglob("*.md"))
    errores = []
    for f in ficheros:
        texto = re.sub(r"```.*?```", "", f.read_text(encoding="utf-8"), flags=re.DOTALL)
        rel = f.relative_to(raiz)
        for ruta in RUTA.findall(texto):
            if not re.search(r"[<>*{}$…]|\.\.\.", ruta) and not (raiz / ruta).exists():
                errores.append(f"{rel}: menciona `{ruta}`, que no existe")
        for destino in ENLACE.findall(texto):
            if (
                "://" in destino
                or destino.startswith("mailto:")
                or re.search(r"[<>*{}]", destino)
            ):
                continue
            if not (f.parent / destino).exists():
                errores.append(f"{rel}: enlace roto a {destino}")
    return errores


def cuerpo_pr() -> str:
    try:
        evento = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
        return (evento.get("pull_request") or {}).get("body") or ""
    except (KeyError, OSError, ValueError):
        return ""


def raiz_de(cwd: str | None) -> Path:
    """Raíz git del `cwd` de la sesión; en un worktree CLAUDE_PROJECT_DIR sigue siendo el checkout principal."""
    if cwd:
        r = subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
        if r.stdout.strip():
            return Path(r.stdout.strip())
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or ".").resolve()


def main(argv: list[str]) -> int:
    base = "origin/" + (os.environ.get("GITHUB_BASE_REF") or "main")
    if argv == ["--stop"]:
        try:
            evento = json.load(sys.stdin)
        except ValueError:
            evento = {}
        if evento.get("stop_hook_active"):
            return 0  # ya se recordó una vez: no encadenar
        raiz = raiz_de(evento.get("cwd"))
        os.chdir(raiz)
        errores = sin_documentar(*cambios(base, con_trabajo=True)) + referencias_rotas(
            raiz
        )
        if errores:
            razon = (
                "Antes de terminar, deja la documentación al día:\n- "
                + "\n- ".join(errores)
            )
            razon += "\nSi de verdad no hace falta, explícalo en el PR con «Docs: sin cambios — motivo»."
            print(
                json.dumps({"decision": "block", "reason": razon}, ensure_ascii=False)
            )
        return 0
    raiz = raiz_de(None)
    os.chdir(raiz)
    errores = referencias_rotas(raiz)
    pendientes = sin_documentar(*cambios(base, con_trabajo=False))
    if pendientes and EXENCION.search(cuerpo_pr()):
        print(
            "Documentación: el PR declara «Docs: sin cambios»; se acepta:\n- "
            + "\n- ".join(pendientes)
        )
        pendientes = []
    errores += pendientes
    if errores:
        print("\n".join(errores), file=sys.stderr)
        print(
            "Actualiza la documentación relacionada (ver AGENTS.md, «Documentación al día»).",
            file=sys.stderr,
        )
        return 1
    print("Documentación al día")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
