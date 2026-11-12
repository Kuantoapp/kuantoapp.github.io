import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "validar_claude", Path(__file__).parents[1] / ".github/scripts/validar_claude.py"
)
assert _spec and _spec.loader
validar_claude = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validar_claude)

AGENTE = "---\nname: revisor\ndescription: Revisa diffs. Úsalo de forma proactiva.\ntools: Read, Grep\nmodel: haiku\n---\nPrompt.\n"
SKILL = "---\ndescription: Abre un PR siguiendo AGENTS.md\ndisable-model-invocation: true\n---\nPasos.\n"
INDICE = "## Índice\n| Nombre | Tipo | Origen | Para qué |\n|---|---|---|---|\n| `revisor` | agente | proyecto | x |\n| `abrir-pr` | skill | proyecto | x |\n"


def repo(
    tmp_path: Path, agente=AGENTE, skill=SKILL, indice=INDICE, nombre_agente="revisor"
) -> Path:
    (tmp_path / ".claude/agents").mkdir(parents=True)
    (tmp_path / ".claude/skills/abrir-pr").mkdir(parents=True)
    (tmp_path / f".claude/agents/{nombre_agente}.md").write_text(agente)
    (tmp_path / ".claude/skills/abrir-pr/SKILL.md").write_text(skill)
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
    assert any("debe llamarse revisor.md" in e for e in errores)


def test_frontmatter_roto_y_sin_description(tmp_path):
    errores = "\n".join(
        validar_claude.validar(
            repo(
                tmp_path, agente="Sin frontmatter\n", skill="---\nname: abrir-pr\n---\n"
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
        "| `abrir-pr` | skill | proyecto | x |\n",
        "| `fantasma` | agente | yeray | x |\n",
    )
    errores = "\n".join(validar_claude.validar(repo(tmp_path, indice=indice)))
    assert "falta la fila de 'abrir-pr'" in errores
    assert "'fantasma' no corresponde" in errores


def test_commands_prohibido(tmp_path):
    (repo(tmp_path) / ".claude/commands").mkdir()
    assert any("commands" in e for e in validar_claude.validar(tmp_path))
