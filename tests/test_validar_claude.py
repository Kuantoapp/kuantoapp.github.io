import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "validar_claude", Path(__file__).parents[1] / ".github/scripts/validar_claude.py"
)
assert _spec and _spec.loader
validar_claude = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validar_claude)

AGENTE = "---\nname: dm-revisor\ndescription: Revisa diffs. Úsalo de forma proactiva.\ntools: Read, Grep\nmodel: haiku\n---\nPrompt.\n"
SKILL = "---\ndescription: Abre un PR siguiendo AGENTS.md\nwhen_to_use: Abrir un PR, subir la rama\ndisable-model-invocation: true\n---\nPasos.\n"
INDICE = "## Índice\n| Nombre | Tipo | Origen | Para qué |\n|---|---|---|---|\n| `dm-revisor` | agente | proyecto | x |\n| `dm-abrir-pr` | skill | proyecto | x |\n"


def repo(
    tmp_path: Path,
    agente=AGENTE,
    skill=SKILL,
    indice=INDICE,
    nombre_agente="dm-revisor",
) -> Path:
    (tmp_path / ".claude/agents").mkdir(parents=True)
    (tmp_path / ".claude/skills/dm-abrir-pr").mkdir(parents=True)
    (tmp_path / f".claude/agents/{nombre_agente}.md").write_text(agente)
    (tmp_path / ".claude/skills/dm-abrir-pr/SKILL.md").write_text(skill)
    (tmp_path / ".claude/README.md").write_text(indice)
    return tmp_path


def test_repo_valido(tmp_path):
    assert validar_claude.validar(repo(tmp_path)) == []


def test_repo_actual_valido():
    assert validar_claude.validar(Path(__file__).parents[1]) == []


def test_agente_sin_tools_campo_raro_y_bypass(tmp_path):
    agente = AGENTE.replace(
        "tools: Read, Grep\n", "permissionMode: bypassPermissions\ntool: Read\n"
    )
    errores = "\n".join(validar_claude.validar(repo(tmp_path, agente=agente)))
    assert "falta tools" in errores
    assert "campo desconocido 'tool'" in errores
    assert "bypassPermissions" in errores


def test_agente_fichero_distinto_de_name(tmp_path):
    errores = validar_claude.validar(repo(tmp_path, nombre_agente="otro"))
    assert any("debe llamarse dm-revisor.md" in e for e in errores)


def test_frontmatter_roto_y_sin_description(tmp_path):
    errores = "\n".join(
        validar_claude.validar(
            repo(
                tmp_path,
                agente="Sin frontmatter\n",
                skill="---\nname: dm-abrir-pr\n---\n",
            )
        )
    )
    assert "línea 1" in errores
    assert "falta description" in errores


def test_skill_name_distinto_de_carpeta(tmp_path):
    skill = SKILL.replace("---\n", "---\nname: otra\n", 1)
    assert any(
        "no coincide con la carpeta" in e
        for e in validar_claude.validar(repo(tmp_path, skill=skill))
    )


def test_indice_desincronizado(tmp_path):
    indice = INDICE.replace(
        "| `dm-abrir-pr` | skill | proyecto | x |\n",
        "| `fantasma` | agente | yeray | x |\n",
    )
    errores = "\n".join(validar_claude.validar(repo(tmp_path, indice=indice)))
    assert "falta la fila de 'dm-abrir-pr'" in errores
    assert "'fantasma' no corresponde" in errores


def test_commands_prohibido(tmp_path):
    (repo(tmp_path) / ".claude/commands").mkdir()
    assert any("commands" in e for e in validar_claude.validar(tmp_path))


def test_sin_prefijo_dm(tmp_path):
    agente = AGENTE.replace("name: dm-revisor", "name: revisor")
    errores = validar_claude.validar(
        repo(tmp_path, agente=agente, nombre_agente="revisor")
    )
    assert any("debe empezar por dm-" in e for e in errores)


def test_descripciones_largas(tmp_path):
    agente = AGENTE.replace(
        "Revisa diffs. Úsalo de forma proactiva.",
        "x" * (validar_claude.MAX_DESC_AGENTE + 1),
    )
    skill = SKILL.replace(
        "Abre un PR siguiendo AGENTS.md", "y" * (validar_claude.MAX_DESC_SKILL + 1)
    )
    errores = " ".join(
        validar_claude.validar(repo(tmp_path, agente=agente, skill=skill))
    )
    assert "el detalle va en el cuerpo" in errores
    assert f"> {validar_claude.MAX_DESC_SKILL} caracteres" in errores


def test_reglas_de_la_guia_en_skills(tmp_path):
    skill = SKILL.replace(
        "Abre un PR siguiendo AGENTS.md", "Úsala para abrir un PR"
    ).replace("when_to_use: Abrir un PR, subir la rama\n", "")
    skill += "Ver [detalle](referencia/detalle.md) y [roto](referencia/no-existe.md).\n"
    base = repo(tmp_path, skill=skill)
    ref = base / ".claude/skills/dm-abrir-pr/referencia"
    ref.mkdir()
    (ref / "detalle.md").write_text("# Detalle\n" + "línea\n" * 120)
    (ref / "huerfano.md").write_text("# Nadie me enlaza\n")
    errores = "\n".join(validar_claude.validar(base))
    assert "falta when_to_use" in errores
    assert "tercera persona" in errores
    assert "enlace roto a referencia/no-existe.md" in errores
    assert "huerfano.md: no se enlaza" in errores
    assert "detalle.md: más de 100 líneas sin índice" in errores


def test_reglas_de_agentes(tmp_path):
    agente = AGENTE.replace(
        "tools: Read, Grep",
        "tools: Read, Grep, Edit\nskills:\n  - dm-no-existe\n  - dm-abrir-pr",
    )
    errores = "\n".join(validar_claude.validar(repo(tmp_path, agente=agente)))
    assert "un revisor solo lee" in errores
    assert "precarga la skill 'dm-no-existe'" in errores
    assert "disable-model-invocation y no se puede precargar" in errores


def test_validador_desde_hook(tmp_path):
    import json
    import os
    import subprocess
    import sys

    base = repo(tmp_path, agente=AGENTE.replace("tools: Read, Grep\n", ""))
    script = Path(__file__).parents[1] / ".github/scripts/validar_claude.py"
    entorno = {**os.environ, "CLAUDE_PROJECT_DIR": str(base)}

    def lanzar(ruta: Path) -> subprocess.CompletedProcess:
        evento = json.dumps({"tool_input": {"file_path": str(ruta)}})
        return subprocess.run(
            [sys.executable, script, "--hook"],
            input=evento,
            capture_output=True,
            check=False,
            text=True,
            env=entorno,
        )

    r = lanzar(base / ".claude/agents/dm-revisor.md")
    assert r.returncode == 2 and "falta tools" in r.stderr
    assert lanzar(base / "src/otro.py").returncode == 0
