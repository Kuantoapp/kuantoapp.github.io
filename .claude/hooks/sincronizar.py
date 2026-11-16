"""Hook PostToolUse (Bash) del flujo de ramas: trabaja sobre la raíz git del `cwd` del evento (en un worktree,
CLAUDE_PROJECT_DIR sigue siendo el checkout principal) y hace tres cosas.

1. Tras `git worktree add <ruta>`, recuerda al agente entrar en el worktree: los hooks miran la carpeta de la sesión.
2. Tras `gh pr create`, trae origin/main a la rama con un merge, si es seguro.
3. Tras `gh issue view`, avisa de las skills de la línea `**Skills:**` de la issue: que se invoquen con Skill y se
   pasen al subagente, y de los nombres que no son skills.

Solo actúa con el árbol limpio y fuera de main; si el merge da conflicto lo deshace y avisa. Nunca hace push
(la rama ya está subida: reescribirla exigiría force push) ni se dispara solo: un merge al día no hace nada.
El PR se mergea con squash, así que el commit de merge no llega a main.
"""

from __future__ import annotations  # puede ejecutarse con el Python 3.9 de macOS

import json
import os
import re
import shlex
import sys
from pathlib import Path

from contexto import git

PR = re.compile(r"\bgh\s+pr\s+create\b")
# shortcut: ignora cd y git -C previos; si se usa ese patrón, resolver la ruta con git worktree list
WORKTREE = re.compile(r"\bgit\s+worktree\s+add\b")
ISSUE = re.compile(r"\bgh\s+issue\s+view\b")
SKILLS = re.compile(
    r"\*\*Skills:\*\*((?:(?!·|\\u00b7|\\n)[^\n])*)"
)  # hasta «·», fin de línea o `\n` literal
CON_VALOR = {
    "-b",
    "-B",
    "--reason",
}  # opciones de `worktree add` que llevan un valor aparte


def raiz(evento: dict) -> Path:
    cwd = evento.get("cwd")
    return Path(
        (cwd and git(Path(cwd), "rev-parse", "--show-toplevel"))
        or os.environ.get("CLAUDE_PROJECT_DIR")
        or os.getcwd()
    )


def avisar_worktree(orden: str, cwd: Path) -> str:
    """Aviso si `orden` crea un worktree en el que la sesión (cwd) aún no está; la ruta es el primer posicional."""
    m = WORKTREE.search(orden)
    if not m:
        return ""
    try:
        args = iter(shlex.split(re.split(r"&&|\|\||;|\|", orden[m.end() :])[0]))
    except ValueError:  # comillas sin cerrar (el texto cortado cae dentro de un argumento): no es un aviso fiable
        return ""
    for a in args:
        if a in CON_VALOR:
            next(args, None)
        elif not a.startswith("-"):
            ruta, cwd = (cwd / a).resolve(), cwd.resolve()
            if ruta in (cwd, *cwd.parents):
                return ""
            return f"Entra en el worktree con la herramienta EnterWorktree (path: {ruta}) o abre Claude Code dentro de él: los hooks (data/raw, revisiones, documentación) miran la carpeta de la sesión."
    return ""


def avisar_skills(orden: str, salida: str, base: Path) -> str:
    """Aviso si `orden` lee una issue (también con `--json body`, donde el salto de línea llega como `\\n`) cuya línea
    `**Skills:**` nombra skills `dm-…`."""
    m = ISSUE.search(orden) and SKILLS.search(salida)
    if not m:
        return ""
    nombres = re.findall(r"dm-[a-z0-9-]+", m.group(1))
    reglas = [n for n in nombres if n == "dm-codigo-minimo"]
    skills = [
        n for n in nombres if (base / ".claude/skills" / n / "SKILL.md").is_file()
    ]
    faltan = [n for n in nombres if n not in skills and n not in reglas]
    if not skills and not reglas and not faltan:
        return ""
    partes = []
    if skills:
        partes.append(
            f"La issue nombra las skills {', '.join(skills)}: invócalas con la herramienta Skill antes de planificar o implementar, y si delegas en un subagente, dile que lea su SKILL.md y sus referencias (no las ve)."
        )
    if reglas:
        partes.append(
            "dm-codigo-minimo no es una skill: es la regla .claude/rules/codigo-minimo.md, ya cargada."
        )
    if faltan:
        partes.append(f"{', '.join(faltan)} no existe en .claude/skills.")
    return " ".join(partes)


def sincronizar(base: Path) -> str:
    rama = git(base, "branch", "--show-current")
    if not rama or rama == "main" or git(base, "status", "--porcelain") != "":
        return ""  # sin rama, en main o con cambios sin confirmar: no se toca nada
    if git(base, "fetch", "--quiet", "origin", "main", espera=10) is None:
        return ""
    detras = git(base, "rev-list", "--count", "HEAD..origin/main")
    if not detras or detras == "0":
        return ""
    if git(base, "merge", "--no-edit", "origin/main", espera=30) is None:
        git(base, "merge", "--abort")
        return f"origin/main tiene {detras} commits nuevos y chocan con tu rama: no he hecho nada. Resuélvelo con `git rebase origin/main`."
    return f"He traído {detras} commits de origin/main a «{rama}» con un merge. No he hecho push: súbelo con `git push` para que el PR los incluya."


def main() -> int:
    try:
        evento = json.load(sys.stdin)
        orden = (evento.get("tool_input") or {}).get("command", "")
        texto = sincronizar(raiz(evento)) if PR.search(orden) else ""
        aviso = avisar_worktree(orden, Path(evento.get("cwd") or os.getcwd()))
        salida = (evento.get("tool_response") or {}).get("stdout", "")
        aviso = "\n".join(
            t for t in (aviso, avisar_skills(orden, salida, raiz(evento))) if t
        )
    except Exception:  # noqa: BLE001 — son ayudas; si fallan, el comando ya se ejecutó
        return 0
    contexto = "\n".join(t for t in (texto, aviso) if t)
    if contexto:
        print(
            json.dumps(
                {
                    **({"systemMessage": texto} if texto else {}),
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": contexto,
                    },
                },
                ensure_ascii=False,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
