"""Versiones Windows de los hooks: py-windows, raw_inmutable_windows.py, entorno_windows.py y ruff_windows.py.

Se ejecutan en macOS, Linux y la CI simulando Windows (rutas con «\\», .venv/Scripts, uname de Git Bash),
así que un cambio en los hooks de macOS que rompa los de Windows se ve aquí.
"""

import base64
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).parents[1]
HOOKS = RAIZ / ".claude/hooks"
sin_sh = pytest.mark.skipif(shutil.which("sh") is None, reason="necesita sh")
# Los .exe falsos de estas pruebas son scripts sh: Windows no puede ejecutarlos (WinError 216).
simulado = pytest.mark.skipif(
    sys.platform == "win32",
    reason="simula Windows con scripts sh; en Windows real no se ejecutan",
)


def cargar(ruta: Path):
    sys.path.insert(0, str(ruta.parent))
    spec = importlib.util.spec_from_file_location(ruta.stem, ruta)
    assert spec and spec.loader
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


win = cargar(HOOKS / "raw_inmutable_windows.py")
entorno_win = cargar(HOOKS / "entorno_windows.py")


def proyecto(tmp_path: Path) -> Path:
    (tmp_path / "data/raw").mkdir(parents=True)
    (tmp_path / "data/processed").mkdir()
    (tmp_path / "data/raw/ine.csv").write_text("a\n")
    return tmp_path


def ejecutable(ruta: Path, cuerpo: str) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("#!/bin/sh\n" + cuerpo + "\n")
    ruta.chmod(0o755)


# --- normalización de rutas y órdenes ---


def test_normalizar():
    assert win.normalizar_ruta(r"data\raw\ine.csv") == "data/raw/ine.csv"
    assert win.normalizar_ruta("/c/Users/a/data/raw/x") == "C:/Users/a/data/raw/x"
    assert win.normalizar_ruta("https://x.es/c/d") == "https://x.es/c/d"
    assert win.normalizar(r".venv\Scripts\python.exe -c 1").startswith("python -c")
    assert win.normalizar("py -3 -c 1").startswith("python -3")
    assert win.normalizar("rm.exe a").startswith("rm a")


# --- Bash (Git Bash) con rutas de Windows ---


@pytest.mark.parametrize(
    "orden",
    [
        r"rm 'data\raw\ine.csv'",
        r'mv "data\raw\ine.csv" data/processed/',
        r".venv\Scripts\python.exe -c \"import os; os.remove('data/raw/ine.csv')\"",
        "py -c \"open('data/raw/ine.csv', 'w')\"",
        r"sed -i s/a/b/ 'data\raw\ine.csv'",
    ],
)
def test_bash_windows_bloquea(tmp_path, orden):
    base = proyecto(tmp_path)
    assert win.motivo({"tool_name": "Bash", "tool_input": {"command": orden}}, base)


def test_edit_con_ruta_windows_bloquea(tmp_path):
    base = proyecto(tmp_path)
    evento = {"tool_name": "Edit", "tool_input": {"file_path": r"data\raw\ine.csv"}}
    assert win.motivo(evento, base)
    nuevo = {"tool_name": "Write", "tool_input": {"file_path": r"data\raw\nuevo.csv"}}
    assert win.motivo(nuevo, base) is None


# --- herramienta PowerShell ---

CODIFICADA = base64.b64encode(
    "Remove-Item data/raw/ine.csv".encode("utf-16-le")
).decode()


@pytest.mark.parametrize(
    "orden",
    [
        r"Remove-Item data\raw\ine.csv",
        "Remove-Item -Path 'data/raw' -Recurse -Force",
        "Get-ChildItem data/raw | Remove-Item",
        "Get-ChildItem data/raw | ForEach-Object { Remove-Item $_ }",
        r"Move-Item data\raw\ine.csv data\processed\ine.csv",
        r"Rename-Item data\raw\ine.csv viejo.csv",
        r"attrib -r data\raw\ine.csv",
        "Set-ItemProperty data/raw/ine.csv -Name IsReadOnly -Value $false",
        "Set-Content data/raw/ine.csv 'x'",
        "'x' | Out-File -FilePath data/raw/ine.csv",
        "Add-Content -Path data/raw/*.csv -Value x",
        r"Copy-Item otro.csv data\raw\ine.csv",
        "Copy-Item otro.csv -Destination data/raw/ine.csv -Force",
        "Invoke-WebRequest https://x.es/a.csv -OutFile data/raw/ine.csv",
        "Expand-Archive datos.zip -DestinationPath data/raw -Force",
        "New-Item data/raw/ine.csv -Force",
        "[System.IO.File]::WriteAllText('data/raw/ine.csv', 'x')",
        "[IO.File]::Delete('data\\raw\\ine.csv')",
        r'cmd /c "del data\raw\ine.csv"',
        "powershell -NoProfile -Command Remove-Item data/raw/ine.csv",
        f"pwsh -EncodedCommand {CODIFICADA}",
        "rm data/raw/ine.csv",
        "python -c \"import os; os.remove('data/raw/ine.csv')\"",
        "git clean -fdx",
    ],
)
def test_powershell_bloquea(tmp_path, orden):
    base = proyecto(tmp_path)
    assert win.motivo(
        {"tool_name": "PowerShell", "tool_input": {"command": orden}}, base
    ), orden


@pytest.mark.parametrize(
    "orden",
    [
        "Get-Content data/raw/ine.csv",
        "Get-ChildItem data/raw",
        "Copy-Item data/raw/ine.csv data/processed/ine.csv",
        "Invoke-WebRequest https://x.es/a.csv -OutFile data/raw/nuevo.csv",
        "Set-Content data/raw/nuevo.csv 'x'",
        "Expand-Archive datos.zip -DestinationPath data/raw",
        "New-Item -ItemType Directory -Force data/raw/sub",
        "Remove-Item data/processed/ine.parquet",
        "python -m src.descargas ine",
    ],
)
def test_powershell_permite(tmp_path, orden):
    base = proyecto(tmp_path)
    assert (
        win.motivo({"tool_name": "PowerShell", "tool_input": {"command": orden}}, base)
        is None
    ), orden


def lanzar_hook(base: Path, evento: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, HOOKS / "raw_inmutable_windows.py", "pre"],
        input=evento,
        capture_output=True,
        check=False,
        text=True,
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(base)},
    )


def test_hook_windows_por_stdin_y_falla_cerrado(tmp_path):
    base = proyecto(tmp_path)
    evento = json.dumps(
        {"tool_name": "PowerShell", "tool_input": {"command": r"del data\raw\ine.csv"}}
    )
    r = lanzar_hook(base, evento)
    assert r.returncode == 2 and "Bloqueado" in r.stderr
    assert lanzar_hook(base, '{"tool_name": roto data\\\\raw').returncode == 2
    assert lanzar_hook(base, '{"tool_name": roto').returncode == 0


def test_enlazar_en_worktree(tmp_path):
    if not shutil.which("git"):
        pytest.skip("necesita git")
    principal = tmp_path / "principal"
    principal.mkdir()

    def git(*args, cwd=principal):
        subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True)

    git("init", "-q")
    git(
        "-c",
        "user.email=a@b",
        "-c",
        "user.name=a",
        "commit",
        "-q",
        "--allow-empty",
        "-m",
        "x",
    )
    git("worktree", "add", "-q", str(tmp_path / "wt"), "-b", "tema")
    aviso = win.compartir_raw(tmp_path / "wt")
    assert "enlazada" in aviso
    assert win._mismo(tmp_path / "wt/data/raw", principal / "data/raw")
    assert win.compartir_raw(tmp_path / "wt") == ""  # idempotente


def test_hook_windows_usa_el_cwd_del_evento(principal_y_worktree):
    principal, wt = principal_y_worktree
    evento = {
        "tool_name": "Edit",
        "tool_input": {"file_path": str(wt / "data/raw/ine.csv")},
        "cwd": str(wt),
    }
    r = lanzar_hook(principal, json.dumps(evento))
    assert r.returncode == 2 and "Bloqueado" in r.stderr


def test_hook_windows_sigue_protegido_con_cwd_en_otro_repo(tmp_path):
    base = proyecto(tmp_path / "principal")
    otro = tmp_path / "otro"
    otro.mkdir()
    subprocess.run(["git", "-C", str(otro), "init", "-q"], check=True)
    evento = {
        "tool_name": "Edit",
        "tool_input": {"file_path": str(base / "data/raw/ine.csv")},
        "cwd": str(otro),
    }
    assert lanzar_hook(base, json.dumps(evento)).returncode == 2


# --- entorno_windows.py ---


@simulado
def test_entorno_windows(tmp_path):
    (tmp_path / ".python-version").write_text("3.14\n")
    assert any("no hay .venv" in a for a in entorno_win.avisos(tmp_path))
    scripts = tmp_path / ".venv/Scripts"
    ejecutable(scripts / "python.exe", "echo 3.14")
    for herramienta in ("ruff.exe", "pytest.exe"):
        ejecutable(scripts / herramienta, "exit 0")
    avisos = entorno_win.avisos(tmp_path)
    assert not any(".venv" in a for a in avisos), avisos
    assert not any("jq" in a for a in avisos)


# --- lanzador py-windows y despacho desde py ---


def path_minimo(tmp_path: Path, *extra: str) -> str:
    bin_ = tmp_path / "bin"
    bin_.mkdir(exist_ok=True)
    for herramienta in ("sh", "cat", "grep", "dirname", *extra):
        ruta = shutil.which(herramienta)
        assert ruta, herramienta
        (bin_ / herramienta).symlink_to(ruta)
    return str(bin_)


def lanzar(
    lanzador: str, proyecto_: Path, evento: str, *args: str, path: str
) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["sh", str(HOOKS / lanzador), *args],
        input=evento,
        capture_output=True,
        check=False,
        text=True,
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(proyecto_), "PATH": path},
    )


@sin_sh
@simulado
def test_py_windows_usa_scripts_utf8_y_version_windows(tmp_path):
    ejecutable(
        tmp_path / ".venv/Scripts/python.exe",
        'cat >/dev/null; echo "utf8=$PYTHONUTF8 $*"',
    )
    (tmp_path / "x.py").write_text("")
    (tmp_path / "x_windows.py").write_text("")
    r = lanzar(
        "py-windows", tmp_path, "{}", str(tmp_path / "x.py"), path=path_minimo(tmp_path)
    )
    assert r.returncode == 0 and "utf8=1" in r.stdout and "x_windows.py" in r.stdout, r


@sin_sh
@simulado
def test_py_windows_salta_el_alias_de_la_store_y_bloquea(tmp_path):
    path = path_minimo(tmp_path)
    ejecutable(Path(path) / "python", "exit 9009")  # alias de la Microsoft Store
    ejecutable(Path(path) / "python3", "exit 9009")
    evento = '{"tool_name": "Edit", "tool_input": {"file_path": "C:\\\\p\\\\data\\\\raw\\\\ine.csv"}}'
    r = lanzar("py-windows", tmp_path, evento, "--critico", "script.py", path=path)
    assert r.returncode == 2 and "Bloqueado" in r.stderr
    r = lanzar("py-windows", tmp_path, "{}", "--critico", "script.py", path=path)
    assert r.returncode == 1  # no toca data/raw: avisa sin bloquear


@sin_sh
@simulado
def test_py_delega_en_py_windows_en_git_bash(tmp_path):
    path = path_minimo(tmp_path)
    ejecutable(Path(path) / "uname", "echo MINGW64_NT-10.0-26100")
    ejecutable(
        tmp_path / ".venv/Scripts/python.exe", "cat >/dev/null; echo soy-windows"
    )
    r = lanzar("py", tmp_path, "{}", "script.py", path=path)
    assert r.returncode == 0 and "soy-windows" in r.stdout, r


@sin_sh
@simulado
def test_formatear_windows(tmp_path):
    (tmp_path / "a.py").write_text("x=1\n")
    ruff = tmp_path / ".venv/Scripts/ruff.exe"
    ejecutable(ruff, '[ "$1" = check ] && { echo "E999 fallo" >&2; exit 1; }; exit 0')
    ejecutable(tmp_path / ".venv/Scripts/python.exe", f'exec "{sys.executable}" "$@"')
    path = path_minimo(tmp_path)
    ejecutable(Path(path) / "uname", "echo MINGW64_NT-10.0-26100")
    evento = json.dumps({"tool_input": {"file_path": str(tmp_path / "a.py")}})
    r = lanzar("formatear-windows", tmp_path, evento, path=path)
    assert r.returncode == 2 and "E999" in r.stderr, r
    otro = json.dumps({"tool_input": {"file_path": str(tmp_path / "a.md")}})
    assert lanzar("formatear-windows", tmp_path, otro, path=path).returncode == 0
