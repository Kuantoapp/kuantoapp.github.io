"""El lanzador de hooks (.claude/hooks/py): usa el Python del proyecto y, si no puede, el hook crítico bloquea."""

import os
import shutil
import subprocess
from pathlib import Path

LANZADOR = Path(__file__).parents[1] / ".claude/hooks/py"
EVENTO_RAW = '{"tool_name": "Bash", "tool_input": {"command": "rm data/raw/ine.csv"}}'
EVENTO_OTRO = '{"tool_name": "Bash", "tool_input": {"command": "ls"}}'


def sin_python(tmp_path: Path) -> str:
    """PATH con lo justo para el lanzador (sh, cat, grep), sin python3 ni uv."""
    bin_ = tmp_path / "bin"
    bin_.mkdir()
    for herramienta in ("sh", "cat", "grep"):
        ruta = shutil.which(herramienta)
        assert ruta, herramienta
        (bin_ / herramienta).symlink_to(ruta)
    return str(bin_)


def python_falso(proyecto: Path, codigo: int, salida: str = "") -> None:
    exe = proyecto / ".venv/bin/python"
    exe.parent.mkdir(parents=True)
    exe.write_text(f"#!/bin/sh\ncat >/dev/null\necho '{salida}'\nexit {codigo}\n")
    exe.chmod(0o755)


def lanzar(
    proyecto: Path, evento: str, *args: str, path: str | None = None
) -> subprocess.CompletedProcess:
    entorno = {**os.environ, "CLAUDE_PROJECT_DIR": str(proyecto)}
    if path:
        entorno["PATH"] = path
    return subprocess.run(
        ["/bin/sh", LANZADOR, *args, "script.py"],
        input=evento,
        capture_output=True,
        check=False,
        text=True,
        env=entorno,
    )


def test_usa_el_python_del_venv(tmp_path):
    python_falso(tmp_path, 0, "soy el del venv")
    r = lanzar(tmp_path, EVENTO_OTRO)
    assert r.returncode == 0 and "soy el del venv" in r.stdout


def test_sin_python_el_critico_bloquea_y_avisa(tmp_path):
    path = sin_python(tmp_path)
    r = lanzar(tmp_path, EVENTO_RAW, "--critico", path=path)
    assert r.returncode == 2 and "Bloqueado" in r.stderr and "uv venv" in r.stderr
    r = lanzar(tmp_path, EVENTO_OTRO, "--critico", path=path)
    assert (
        r.returncode == 1 and "uv venv" in r.stderr
    )  # no toca data/raw: avisa sin bloquear
    r = lanzar(tmp_path, EVENTO_RAW, path=path)
    assert r.returncode == 1  # un hook no crítico nunca bloquea


def test_si_el_interprete_falla_el_critico_bloquea(tmp_path):
    python_falso(tmp_path, 1)
    assert lanzar(tmp_path, EVENTO_RAW, "--critico").returncode == 2
    assert lanzar(tmp_path, EVENTO_OTRO, "--critico").returncode == 1


def test_respeta_la_decision_del_script(tmp_path):
    python_falso(tmp_path, 2, "decisión")
    r = lanzar(tmp_path, EVENTO_OTRO, "--critico")
    assert r.returncode == 2 and "decisión" in r.stdout
