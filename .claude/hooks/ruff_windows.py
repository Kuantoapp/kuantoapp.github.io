"""Hook PostToolUse (Windows): formatea y revisa con ruff el .py editado, sin jq.

Equivale al comando en línea de .claude/settings.json que usan macOS y Linux:
ruff del .venv (o del PATH) → `ruff format` → `ruff check --fix`; si quedan errores, exit 2 con ellos en stderr.
"""

from __future__ import annotations  # puede ejecutarse con un Python antiguo del sistema

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def ruff(base: Path) -> str | None:
    for candidato in (base / ".venv/Scripts/ruff.exe", base / ".venv/bin/ruff"):
        if candidato.is_file():
            return str(candidato)
    return shutil.which("ruff")


def main() -> int:
    try:
        evento = json.load(sys.stdin)
    except ValueError:
        return 0
    fichero = str((evento.get("tool_input") or {}).get("file_path") or "")
    if not fichero.endswith(".py"):
        return 0
    base = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    exe = ruff(base)
    if exe is None:
        return 0  # igual que en macOS: sin ruff no se formatea, pero no se bloquea
    subprocess.run([exe, "format", "-q", fichero], capture_output=True, check=False)
    r = subprocess.run(
        [exe, "check", "--fix", "-q", fichero],
        capture_output=True,
        check=False,
        text=True,
    )
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
