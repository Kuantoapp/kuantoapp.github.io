"""El cableado de hooks en .claude/settings.json: cada script, en su evento. Una fusión mal hecha del JSON no se nota al usarlo."""

import json
from pathlib import Path

HOOKS = json.loads((Path(__file__).parents[1] / ".claude/settings.json").read_text())[
    "hooks"
]

# (fragmento del comando, evento, matcher) que debe existir; y nada de esos scripts fuera de su sitio
ESPERADO = {
    ('raw_inmutable.py" pre', "PreToolUse", "Edit|Write|MultiEdit|NotebookEdit|Bash"),
    ('raw_inmutable.py" post', "PostToolUse", "Bash|Write"),
    # Herramienta PowerShell de Claude Code en Windows (Bash no la cubre)
    ('raw_inmutable.py" pre', "PreToolUse", "PowerShell"),
    ('raw_inmutable.py" post', "PostToolUse", "PowerShell"),
    ('raw_inmutable.py" enlazar', "SessionStart", None),
    ('entorno.py"', "SessionStart", None),
    ('contexto.py"', "SessionStart", None),
    ("ruff", "PostToolUse", "Edit|Write|MultiEdit"),
    ('cifras_con_fuente.py" --hook', "PostToolUse", "Edit|Write|MultiEdit"),
    ('validar_claude.py" --hook', "PostToolUse", "Edit|Write|MultiEdit"),
    ('docs_al_dia.py" --stop', "Stop", None),
    ('revisiones.py" --stop', "Stop", None),
    ('revisiones.py" --registrar', "PreToolUse", "SubagentHandback"),
    (
        'revisiones.py" --registrar',
        "SubagentStop",
        "dm-revisor-espacial|dm-auditor-calculos-normativos|dm-verificador-fuentes|dm-trazador-cifras|dm-revisor-codigo",
    ),
}


def cableado() -> set[tuple[str, str, str | None]]:
    return {
        (h["command"], evento, entrada.get("matcher"))
        for evento, entradas in HOOKS.items()
        for entrada in entradas
        for h in entrada["hooks"]
    }


def test_cada_hook_en_su_evento():
    real = cableado()
    for fragmento, evento, matcher in ESPERADO:
        assert any(
            fragmento in c and e == evento and m == matcher for c, e, m in real
        ), (fragmento, evento)


def test_sin_hooks_duplicados_ni_fuera_de_sitio():
    real = cableado()
    for comando, evento, matcher in real:
        sitios = [(e, m) for f, e, m in ESPERADO if f in comando]
        assert (evento, matcher) in sitios, f"{comando[:60]} en {evento}/{matcher}"
    assert len(real) == len(ESPERADO)
