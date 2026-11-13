"""Hook SessionStart (Windows): la versión de entorno.py para Git Bash. La elige .claude/hooks/py-windows.

Cambia respecto a macOS y Linux: el venv tiene sus ejecutables en .venv/Scripts/*.exe, jq no hace falta
(el formateo usa ruff_windows.py) y avisa si el Python del sistema es el alias de la Microsoft Store.
Nunca bloquea: lo que imprime llega a Claude como contexto para que avise a la persona.
"""

from __future__ import annotations  # puede ejecutarse con un Python antiguo del sistema

import os
import shutil
import subprocess
import sys
from pathlib import Path

ARREGLO = "uv venv && uv pip install -r requirements-dev.txt"


def avisos(base: Path) -> list[str]:
    fijada = (
        (base / ".python-version").read_text(encoding="utf-8").strip()
        if (base / ".python-version").exists()
        else ""
    )
    scripts = base / ".venv/Scripts"
    venv = scripts / "python.exe"
    out = []
    actual = f"{sys.version_info[0]}.{sys.version_info[1]}"
    if fijada and actual != fijada:
        out.append(
            f"los hooks del proyecto se están ejecutando con Python {actual} ({sys.executable}), no con el {fijada} del equipo: "
            f"siguen funcionando, pero ejecuta `{ARREGLO}` para que usen el del proyecto"
        )
    if not shutil.which("uv"):
        out.append(
            "falta uv (instala Python y dependencias): "
            'powershell -c "irm https://astral.sh/uv/install.ps1 | iex" o https://docs.astral.sh/uv/getting-started/installation/'
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
            if not (scripts / f"{herramienta}.exe").exists():
                out.append(
                    f"falta {herramienta} en .venv: ejecuta `uv pip install -r requirements-dev.txt`"
                )
    sistema = shutil.which("python3") or shutil.which("python") or ""
    if "WindowsApps" in sistema and not venv.exists():
        out.append(
            "el python del PATH es el alias de la Microsoft Store (no ejecuta nada): "
            "los hooks necesitan el .venv o uv"
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
            "Entorno del proyecto incompleto (Windows). Avisa a la persona antes de empezar:\n- "
            + "\n- ".join(lista)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
