"""Ajustes de pytest por plataforma."""

import subprocess
import sys
from pathlib import Path

import pytest

# test_lanzador.py prueba el lanzador de macOS y Linux con /bin/sh y enlaces simbólicos, que en Windows no hay.
# El de Windows (py-windows) lo prueba test_windows.py.
collect_ignore = ["test_lanzador.py"] if sys.platform == "win32" else []


@pytest.fixture
def principal_y_worktree(tmp_path: Path) -> tuple[Path, Path]:
    """Checkout principal (con data/raw/ine.csv) y un worktree suyo, como manda AGENTS.md."""
    principal, wt = tmp_path / "principal", tmp_path / "wt"
    (principal / "data/raw").mkdir(parents=True)
    (principal / "data/raw/ine.csv").write_text("a\n", encoding="utf-8")
    git = ["git", "-C", str(principal), "-c", "user.email=a@b", "-c", "user.name=a"]
    for a in (["init", "-q"], ["commit", "-q", "--allow-empty", "-m", "x"]):
        subprocess.run([*git, *a], check=True, capture_output=True)
    subprocess.run(
        [*git, "worktree", "add", "-q", str(wt), "-b", "tema"],
        check=True,
        capture_output=True,
    )
    return principal, wt
