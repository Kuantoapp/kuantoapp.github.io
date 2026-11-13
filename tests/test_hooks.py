import importlib.util
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).parents[1]
HOOK_RAW = RAIZ / ".claude/hooks/raw_inmutable.py"
CIFRAS = RAIZ / ".github/scripts/cifras_con_fuente.py"


def cargar(ruta: Path):
    spec = importlib.util.spec_from_file_location(ruta.stem, ruta)
    assert spec and spec.loader
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


raw = cargar(HOOK_RAW)
cifras = cargar(CIFRAS)


def proyecto(tmp_path: Path) -> Path:
    (tmp_path / "data/raw").mkdir(parents=True)
    (tmp_path / "data/processed").mkdir()
    (tmp_path / "data/raw/ine.csv").write_text("a\n")
    return tmp_path


def hook(tmp_path: Path, herramienta: str, entrada: dict) -> int:
    evento = json.dumps({"tool_name": herramienta, "tool_input": entrada})
    entorno = {**os.environ, "CLAUDE_PROJECT_DIR": str(tmp_path)}
    r = subprocess.run(
        [sys.executable, HOOK_RAW, "pre"],
        input=evento,
        capture_output=True,
        check=False,
        text=True,
        env=entorno,
    )
    return r.returncode


def test_raw_permite_descargas_nuevas(tmp_path):
    base = proyecto(tmp_path)
    assert hook(base, "Write", {"file_path": str(base / "data/raw/nuevo.csv")}) == 0
    for orden in [
        "curl -sL https://x.es/a.csv -o data/raw/nuevo.csv",
        "wget -O data/raw/nuevo.zip https://x.es/a.zip",
        "curl -s https://x.es/a.json > data/raw/nuevo.json",
        "cp data/raw/ine.csv data/processed/ine.csv",
        "python -m src.descargas ine",
        "ls -l data/raw && head data/raw/ine.csv",
        "tar -xkf datos.tar -C data/raw",
        "unzip -n datos.zip -d data/raw",
        "python -c \"import pandas as pd; pd.read_csv('data/raw/ine.csv').to_parquet('data/processed/ine.parquet')\"",
        "find data/raw -name '*.csv'",
    ]:
        assert raw.motivo_bash(orden, base) is None, orden


def test_raw_bloquea_cambiar_o_borrar(tmp_path):
    base = proyecto(tmp_path)
    assert hook(base, "Write", {"file_path": str(base / "data/raw/ine.csv")}) == 2
    assert hook(base, "Edit", {"file_path": "data/raw/ine.csv"}) == 2
    for orden in [
        "rm data/raw/ine.csv",
        "rm -rf data/raw",
        "mv data/raw/ine.csv data/processed/",
        "sed -i '' 's/a/b/' data/raw/ine.csv",
        "curl -s https://x.es/a.csv -o data/raw/ine.csv",
        "echo x >> data/raw/ine.csv",
        "cp otro.csv data/raw/ine.csv",
        "git clean -fdx",
        "chmod u+w data/raw/ine.csv",
        "find data/raw -name '*.csv' -delete",
        "ls data/raw/*.csv | xargs rm",
        "python3 -c \"import os; os.remove('data/raw/ine.csv')\"",
        "python -c \"open('data/raw/ine.csv', 'w').write('x')\"",
        "tar -xf datos.tar -C data/raw",
        "unzip -o datos.zip -d data/raw",
    ]:
        assert raw.motivo_bash(orden, base), orden


def test_raw_falla_cerrado(tmp_path):
    entorno = {**os.environ, "CLAUDE_PROJECT_DIR": str(proyecto(tmp_path))}
    roto = '{"tool_name": "Bash", "tool_input": {"command": "rm data/raw/ine.csv"'
    r = subprocess.run(
        [sys.executable, HOOK_RAW, "pre"],
        input=roto,
        capture_output=True,
        check=False,
        text=True,
        env=entorno,
    )
    assert r.returncode == 2
    r = subprocess.run(
        [sys.executable, HOOK_RAW, "pre"],
        input="{roto",
        capture_output=True,
        check=False,
        text=True,
        env=entorno,
    )
    assert r.returncode == 0  # no menciona data/raw: no bloquea el resto del trabajo


def test_hooks_funcionan_con_python_de_macos(tmp_path):
    """macOS trae Python 3.9: si un hook no arranca, Claude Code lo trata como aviso y no bloquea nada.

    Recorre todos los hooks de .claude/settings.json que ejecutan python3, en todos sus modos.
    """
    py39 = Path("/usr/bin/python3")
    if not py39.exists():
        return
    raiz = Path(__file__).parents[1]
    hooks = json.loads((raiz / ".claude/settings.json").read_text())["hooks"]
    # Último recurso del lanzador (.claude/hooks/py): el python3 del sistema ejecuta el script directamente
    comandos = {
        h["command"]
        for es in hooks.values()
        for e in es
        for h in e["hooks"]
        if "hooks/py" in h["command"]
    }
    assert len(comandos) >= 8
    base = proyecto(tmp_path)
    evento = json.dumps(
        {
            "tool_name": "Edit",
            "tool_input": {"file_path": str(base / "data/raw/ine.csv")},
            "cwd": str(base),
        }
    )
    entorno = {**os.environ, "CLAUDE_PROJECT_DIR": str(raiz)}
    for comando in sorted(comandos):
        partes = shlex.split(comando.replace("$CLAUDE_PROJECT_DIR", str(raiz)))
        script_y_args = [x for x in partes[2:] if x != "--critico"]
        r = subprocess.run(
            [str(py39), *script_y_args],
            input=evento,
            capture_output=True,
            check=False,
            text=True,
            env=entorno,
            cwd=base,
        )
        assert "Traceback" not in r.stderr, f"{comando}: {r.stderr[-300:]}"


def test_raw_post_deja_solo_lectura(tmp_path):
    base = proyecto(tmp_path)
    entorno = {**os.environ, "CLAUDE_PROJECT_DIR": str(base)}
    subprocess.run([sys.executable, HOOK_RAW, "post"], env=entorno, check=True)
    assert not os.access(base / "data/raw/ine.csv", os.W_OK)


def guion(tmp_path: Path, texto: str) -> list[str]:
    ruta = tmp_path / "docs/pitch/guion.md"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto)
    return cifras.revisar(ruta)


def test_cifras_sin_fuente(tmp_path):
    errores = guion(tmp_path, "De 51.735 solicitudes se aceptó el 22 %.\n")
    assert len(errores) == 1 and "51.735" in errores[0]


def test_cifras_con_fuente(tmp_path):
    texto = (
        "De 51.735 solicitudes se aceptó el 22 % [^bono].\n"
        "Te sobran 340 € al mes (estimado; fuente: modelo de alquiler v1).\n\n"
        "[^bono]: Catálogo regional, conjunto del Bono, 2022.\n"
    )
    assert guion(tmp_path, texto) == []


def test_cifras_nota_sin_definir(tmp_path):
    assert "sin definir" in guion(tmp_path, "Un 22 % [^falta].\n")[0]


def test_cifras_que_no_son_cifras(tmp_path):
    texto = (
        "# Guion de 2026\n"
        "1. **0:00** Apertura el 26/11/2026\n"
        "2. Tres escenarios y 5 perfiles, versión 1.2.0\n"
        "```\nprint(51735)\n```\n"
        "Página 123 del anexo <!-- sin-fuente: es una referencia, no un dato -->\n"
    )
    assert guion(tmp_path, texto) == []


def test_cifras_ignora_etiquetas_html(tmp_path):
    ruta = tmp_path / "app/inicio.html"
    ruta.parent.mkdir(parents=True)
    ruta.write_text(
        '<div style="width: 300px" data-n="120">Hola</div>\n<p>Te sobran 340 €</p>\n'
    )
    errores = cifras.revisar(ruta)
    assert len(errores) == 1 and ":2:" in errores[0]


def test_cifras_desde_hook(tmp_path):
    ruta = tmp_path / "docs/pitch/guion.md"
    ruta.parent.mkdir(parents=True)
    ruta.write_text("Un 22 %.\n")
    entorno = {**os.environ, "CLAUDE_PROJECT_DIR": str(tmp_path)}
    evento = json.dumps({"tool_input": {"file_path": str(ruta)}})
    r = subprocess.run(
        [sys.executable, CIFRAS, "--hook"],
        input=evento,
        capture_output=True,
        check=False,
        text=True,
        env=entorno,
    )
    assert r.returncode == 2 and "sin fuente" in r.stderr


def test_cifras_solo_en_lo_vigilado(tmp_path):
    otro = tmp_path / "docs/decisiones.md"
    otro.parent.mkdir(parents=True)
    otro.write_text("Un 22 %.\n")
    assert not cifras.vigilado(otro, tmp_path)
    assert cifras.vigilado(tmp_path / "app/textos/inicio.md", tmp_path)
