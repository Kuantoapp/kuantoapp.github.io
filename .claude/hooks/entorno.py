"""Hook SessionStart: comprueba que el entorno es el del equipo y, si no, dice cómo arreglarlo.

Nunca bloquea: lo que imprime llega a Claude como contexto para que avise a la persona.
"""

from __future__ import annotations  # puede ejecutarse con el Python 3.9 de macOS

import os
import shutil
import subprocess
import sys
from pathlib import Path

# shortcut: rutas de .venv de macOS y Linux; en Windows serían .venv/Scripts
ARREGLO = "uv venv && uv pip install -r requirements-dev.txt"


def avisos(base: Path) -> list[str]:
    fijada = (
        (base / ".python-version").read_text().strip()
        if (base / ".python-version").exists()
        else ""
    )
    venv = base / ".venv/bin/python"
    out = []
    actual = f"{sys.version_info[0]}.{sys.version_info[1]}"
    if fijada and actual != fijada:
        out.append(
            f"los hooks del proyecto se están ejecutando con Python {actual} ({sys.executable}), no con el {fijada} del equipo: "
            f"siguen funcionando, pero ejecuta `{ARREGLO}` para que usen el del proyecto"
        )
    if not shutil.which("uv"):
        out.append(
            "falta uv (instala Python y dependencias): https://docs.astral.sh/uv/getting-started/installation/"
        )
    if not venv.exists():
        out.append(f"no hay .venv con Python {fijada}: ejecuta `{ARREGLO}`")
    else:
        r = subprocess.run(
            [str(venv), "-c", "import sys; print('%d.%d' % sys.version_info[:2])"],
            capture_output=True,
            check=False,
            text=True,
        )
        version = r.stdout.strip()
        if fijada and version != fijada:
            out.append(
                f".venv usa Python {version} y el equipo usa {fijada}: borra .venv y ejecuta `{ARREGLO}`"
            )
        for herramienta in ("ruff", "pytest"):
            if not (base / ".venv/bin" / herramienta).exists():
                out.append(
                    f"falta {herramienta} en .venv: ejecuta `uv pip install -r requirements-dev.txt`"
                )
    if not shutil.which("jq"):
        out.append(
            "falta jq: el hook que formatea los .py no funcionará (brew install jq / apt install jq)"
        )
    return out


def main() -> int:
    base = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    try:
        lista = avisos(base)
    except Exception as e:  # noqa: BLE001 — un aviso que falla no debe impedir trabajar
        lista = [f"no se pudo comprobar el entorno ({e!r})"]
    if lista:
        print(
            "Entorno del proyecto incompleto. Avisa a la persona antes de empezar:\n- "
            + "\n- ".join(lista)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
