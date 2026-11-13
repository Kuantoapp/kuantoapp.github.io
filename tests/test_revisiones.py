import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / ".github/scripts/revisiones.py"
HOOK_RAW = Path(__file__).parents[1] / ".claude/hooks/raw_inmutable.py"


def cargar(ruta: Path):
    spec = importlib.util.spec_from_file_location(ruta.stem, ruta)
    assert spec and spec.loader
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


rev = cargar(SCRIPT)
raw = cargar(HOOK_RAW)


def git(raiz: Path, *args: str) -> str:
    r = subprocess.run(
        ["git", *args], cwd=raiz, capture_output=True, check=True, text=True
    )
    return r.stdout.strip()


def repo(tmp_path: Path) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "user.email", "t@t")
    git(tmp_path, "config", "user.name", "t")
    (tmp_path / "README.md").write_text("x\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-qm", "base")
    git(tmp_path, "update-ref", "refs/remotes/origin/main", "HEAD")
    return tmp_path


def commit(raiz: Path, ruta: str, texto: str) -> str:
    f = raiz / ruta
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(texto)
    git(raiz, "add", ".")
    git(raiz, "commit", "-qm", ruta)
    return git(raiz, "rev-parse", "--short", "HEAD")


def test_disparadores_por_area(tmp_path):
    base = repo(tmp_path)
    commit(base, "src/mapa.py", "import geopandas as gpd\n")
    commit(base, "src/nomina.py", "def neto(bruto): return bruto * 0.8\n")
    commit(base, "src/util.py", "def suma(a, b): return a + b\n")
    commit(base, "app/inicio.md", "Hola\n")
    commit(base, "data/README.md", "fuentes\n")
    commit(base, "tests/test_mapa.py", "import geopandas\n")
    exigidos = rev.exigidos(rev.cambiados("origin/main", base), base)
    assert set(exigidos) == set(rev.REVISORES)
    assert exigidos["dm-revisor-espacial"] == {"src/mapa.py"}
    assert exigidos["dm-auditor-calculos-normativos"] == {"src/nomina.py"}


def test_pr_sin_veredicto_falla_y_con_veredicto_vigente_pasa(tmp_path):
    base = repo(tmp_path)
    sha = commit(base, "src/mapa.py", "import geopandas as gpd\n")
    exigidos = rev.exigidos(rev.cambiados("origin/main", base), base)
    assert (
        "Falta el veredicto de dm-revisor-espacial"
        in rev.comprobar_pr("", exigidos, base)[0]
    )
    cuerpo = f"## Revisión por agentes\n- dm-revisor-espacial: APTO ({sha}) — CRS y W correctos\n"
    assert rev.comprobar_pr(cuerpo, exigidos, base) == []


def test_veredicto_caducado_no_apto_y_no_aplica(tmp_path):
    base = repo(tmp_path)
    sha = commit(base, "src/mapa.py", "import geopandas as gpd\n")
    commit(base, "src/mapa.py", "import geopandas as gpd\nx = 1\n")
    exigidos = rev.exigidos(rev.cambiados("origin/main", base), base)
    assert (
        "caducado"
        in rev.comprobar_pr(f"- dm-revisor-espacial: APTO ({sha})", exigidos, base)[0]
    )
    assert (
        "NO APTO"
        in rev.comprobar_pr("- dm-revisor-espacial: NO APTO (abc1234)", exigidos, base)[
            0
        ]
    )
    assert (
        "motivo"
        in rev.comprobar_pr("- dm-revisor-espacial: NO APLICA", exigidos, base)[0]
    )
    aplica = (
        "- dm-revisor-espacial: NO APLICA — solo cambia un comentario de importación"
    )
    assert rev.comprobar_pr(aplica, exigidos, base) == []


def test_cambio_fuera_del_area_no_caduca(tmp_path):
    base = repo(tmp_path)
    sha = commit(base, "src/mapa.py", "import geopandas as gpd\n")
    commit(base, "docs/notas.md", "nota\n")
    exigidos = rev.exigidos(rev.cambiados("origin/main", base), base)
    assert (
        rev.comprobar_pr(
            f"- dm-revisor-espacial: APTO CON RESERVAS ({sha})", exigidos, base
        )
        == []
    )


def hook(base: Path, modo: str, evento: dict) -> subprocess.CompletedProcess:
    entorno = {**os.environ, "CLAUDE_PROJECT_DIR": str(base)}
    entorno.pop("GITHUB_BASE_REF", None)
    return subprocess.run(
        [sys.executable, SCRIPT, modo],
        input=json.dumps(evento),
        capture_output=True,
        check=False,
        text=True,
        env=entorno,
        cwd=base,
    )


def test_registro_resumen_y_stop(tmp_path):
    base = repo(tmp_path)
    commit(base, "src/mapa.py", "import geopandas as gpd\n")
    # Sin veredicto: el Stop lo recuerda una vez y el resumen dice que falta
    salida = json.loads(hook(base, "--stop", {"cwd": str(base)}).stdout)
    assert salida["decision"] == "block" and "dm-revisor-espacial" in salida["reason"]
    assert (
        hook(base, "--stop", {"cwd": str(base), "stop_hook_active": True}).stdout == ""
    )
    # Si el revisor que falta ya está corriendo en segundo plano, no se insiste
    corriendo = {
        "cwd": str(base),
        "background_tasks": [{"type": "subagent", "agent_type": "dm-revisor-espacial"}],
    }
    assert hook(base, "--stop", corriendo).stdout == ""
    # El agente entrega su informe por SubagentHandback: queda registrado
    informe = "## Veredicto: APTO CON RESERVAS\nFalta probar otra W.\n## Resumen…"
    evento = {
        "hook_event_name": "PreToolUse",
        "agent_type": "dm-revisor-espacial",
        "tool_input": {"message": informe},
        "cwd": str(base),
    }
    assert hook(base, "--registrar", evento).returncode == 0
    r = hook(base, "--resumen", {})
    assert (
        r.returncode == 0 and "- dm-revisor-espacial: APTO CON RESERVAS (" in r.stdout
    )
    assert "Falta probar otra W." in r.stdout
    assert hook(base, "--stop", {"cwd": str(base)}).stdout == ""
    # Un agente que no es revisor no registra nada
    otro = {**evento, "agent_type": "Explore"}
    hook(base, "--registrar", otro)
    assert len(rev.registro(base).read_text().splitlines()) == 1


def test_stop_no_interrumpe_mientras_se_trabaja(tmp_path):
    base = repo(tmp_path)
    commit(base, "src/mapa.py", "import geopandas as gpd\n")
    (base / "src/mapa.py").write_text("import geopandas as gpd\ny = 2\n")
    assert hook(base, "--stop", {"cwd": str(base)}).stdout == ""


def test_worktree_comparte_data_raw(tmp_path):
    principal = repo(tmp_path / "principal")
    otro = tmp_path / "dm-tema"
    git(principal, "worktree", "add", "-q", str(otro), "-b", "yo/tema")
    assert "enlazada" in raw.compartir_raw(otro)
    assert (otro / "data/raw").is_symlink()
    (otro / "data/raw/ine.csv").write_text("a\n")
    assert (principal / "data/raw/ine.csv").exists()  # una sola copia
    assert raw.compartir_raw(otro) == ""  # idempotente
    assert raw.compartir_raw(principal) == ""  # en el principal no enlaza nada
    # El hook sigue protegiendo lo descargado a través del enlace
    assert raw.motivo_bash("rm data/raw/ine.csv", otro)
    assert raw.motivo_fichero(str(otro / "data/raw/ine.csv"), "Edit", otro)


def test_worktree_con_datos_propios_no_se_toca(tmp_path):
    principal = repo(tmp_path / "principal")
    otro = tmp_path / "dm-tema"
    git(principal, "worktree", "add", "-q", str(otro), "-b", "yo/tema")
    (otro / "data/raw").mkdir(parents=True)
    (otro / "data/raw/propio.csv").write_text("a\n")
    assert "ficheros propios" in raw.compartir_raw(otro)
    assert not (otro / "data/raw").is_symlink()


def test_informe_sin_veredicto_valido_se_rechaza(tmp_path):
    """Caso real: un revisor escribió «## Veredicto: PARCIAL» y su revisión se perdía sin avisar."""
    base = repo(tmp_path)
    commit(base, "data/README.md", "fuentes\n")
    malo = {
        "hook_event_name": "PreToolUse",
        "agent_type": "dm-verificador-fuentes",
        "agent_id": "a1",
        "tool_input": {"message": "## Veredicto: PARCIAL. La nota describe bien…"},
        "cwd": str(base),
    }
    salida = json.loads(hook(base, "--registrar", malo).stdout)["hookSpecificOutput"]
    assert (
        salida["permissionDecision"] == "deny"
        and "APTO CON RESERVAS" in salida["permissionDecisionReason"]
    )
    assert not rev.registro(base).exists()
    # Sin SubagentHandback: al terminar sin veredicto registrado, se le pide una vez
    parada = {
        "hook_event_name": "SubagentStop",
        "agent_type": "dm-verificador-fuentes",
        "agent_id": "a1",
        "cwd": str(base),
    }
    assert (
        json.loads(
            hook(
                base, "--registrar", {**parada, "last_assistant_message": "listo"}
            ).stdout
        )["decision"]
        == "block"
    )
    assert (
        hook(
            base,
            "--registrar",
            {**parada, "last_assistant_message": "listo", "stop_hook_active": True},
        ).stdout
        == ""
    )
    # Corregido: se registra, y el SubagentStop posterior (texto de cierre) ya no insiste
    bueno = {
        **malo,
        "tool_input": {"message": "## Veredicto: APTO CON RESERVAS\nMatizar la nota."},
    }
    assert hook(base, "--registrar", bueno).stdout == ""
    assert (
        hook(
            base,
            "--registrar",
            {**parada, "last_assistant_message": "Informe entregado."},
        ).stdout
        == ""
    )
    assert (
        "dm-verificador-fuentes: APTO CON RESERVAS"
        in hook(base, "--resumen", {}).stdout
    )
