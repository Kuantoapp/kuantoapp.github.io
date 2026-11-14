import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / ".github/scripts/docs_al_dia.py"
_spec = importlib.util.spec_from_file_location("docs_al_dia", SCRIPT)
assert _spec and _spec.loader
docs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(docs)


def test_cambios_sin_su_documentacion():
    errores = docs.sin_documentar({".claude/hooks/x.py", ".python-version"}, [])
    assert any("hooks" in e for e in errores)
    assert any("dependencias" in e for e in errores)


def test_cambios_con_su_documentacion():
    nombres = {
        ".claude/hooks/x.py",
        "AGENTS.md",
        "requirements.txt",
        "docs/decisiones.md",
    }
    assert docs.sin_documentar(nombres, []) == []


def test_url_nueva_exige_data_readme():
    nuevas = ['URL = "https://datos.ejemplo.es/renta.csv"']
    assert "data/README.md" in docs.sin_documentar({"src/carga.py"}, nuevas)[0]
    assert docs.sin_documentar({"src/carga.py", "data/README.md"}, nuevas) == []


def test_referencias_rotas(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src/existe.py").write_text("")
    (tmp_path / "AGENTS.md").write_text(
        "Usa `src/existe.py` y `src/borrado.py`; plantilla `src/<paquete>/x.py`.\n"
        "Ver [guía](docs/guia.md) y [web](https://x.es).\n"
        "```\ncat src/en_codigo.py\n```\n"
    )
    errores = docs.referencias_rotas(tmp_path)
    assert len(errores) == 2
    assert "src/borrado.py" in errores[0] and "docs/guia.md" in errores[1]


def test_hook_stop_recuerda_una_vez(tmp_path):
    def git(*a: str) -> None:
        subprocess.run(["git", *a], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    (tmp_path / "AGENTS.md").write_text("Reglas.\n")
    git("add", ".")
    git("commit", "-qm", "base")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    (tmp_path / ".claude/hooks").mkdir(parents=True)
    (tmp_path / ".claude/hooks/nuevo.py").write_text("")
    entorno = {**os.environ, "CLAUDE_PROJECT_DIR": str(tmp_path)}
    entorno.pop("GITHUB_BASE_REF", None)

    def stop(activo: bool) -> str:
        return subprocess.run(
            [sys.executable, SCRIPT, "--stop"],
            input=json.dumps({"stop_hook_active": activo}),
            capture_output=True,
            check=False,
            text=True,
            env=entorno,
        ).stdout

    salida = json.loads(stop(activo=False))
    assert salida["decision"] == "block" and "hooks" in salida["reason"]
    assert stop(activo=True) == ""


def test_hook_stop_usa_el_cwd_del_evento(tmp_path):
    def git(repo: Path, *a: str) -> None:
        subprocess.run(["git", *a], cwd=repo, check=True, capture_output=True)

    otra, repo = tmp_path / "otra", tmp_path / "repo"
    for carpeta in (otra, repo):
        carpeta.mkdir()
        git(carpeta, "init", "-q", "-b", "main")
        git(
            carpeta,
            "-c",
            "user.email=t@t",
            "-c",
            "user.name=t",
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            "base",
        )
        git(carpeta, "update-ref", "refs/remotes/origin/main", "HEAD")
    (repo / "src").mkdir()
    (repo / ".claude/hooks").mkdir(parents=True)
    (repo / ".claude/hooks/nuevo.py").write_text("")  # sin documentar
    entorno = {
        **os.environ,
        "CLAUDE_PROJECT_DIR": str(otra),
    }  # el checkout principal, sin cambios
    entorno.pop("GITHUB_BASE_REF", None)
    salida = subprocess.run(
        [sys.executable, SCRIPT, "--stop"],
        input=json.dumps({"cwd": str(repo / "src")}),
        capture_output=True,
        check=False,
        text=True,
        env=entorno,
    ).stdout
    assert json.loads(salida)["decision"] == "block"
    assert docs.raiz_de(str(repo / "src")) == repo.resolve()
