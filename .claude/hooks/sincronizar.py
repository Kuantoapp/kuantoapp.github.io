"""Hook PostToolUse (Bash): tras `gh pr create`, trae origin/main a la rama con un merge, si es seguro.

Solo actúa con el árbol limpio y fuera de main; si el merge da conflicto lo deshace y avisa. Nunca hace push
(la rama ya está subida: reescribirla exigiría force push) ni se dispara solo: un merge al día no hace nada.
El PR se mergea con squash, así que el commit de merge no llega a main.
"""

from __future__ import annotations  # puede ejecutarse con el Python 3.9 de macOS

import json
import os
import re
import sys
from pathlib import Path

from contexto import git

PR = re.compile(r"\bgh\s+pr\s+create\b")


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
        if not PR.search((evento.get("tool_input") or {}).get("command", "")):
            return 0
        texto = sincronizar(Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()))
    except Exception:  # noqa: BLE001 — sincronizar es una ayuda; si falla, el PR ya está creado
        return 0
    if texto:
        print(
            json.dumps(
                {
                    "systemMessage": texto,
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": texto,
                    },
                },
                ensure_ascii=False,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
