"""Hook SessionStart de contexto: fechas clave, decisiones pendientes, «(verificar)» y descargas que faltan."""

import importlib.util
import io
import json
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parents[1] / ".claude/hooks")
)  # sincronizar.py importa contexto
_ruta = Path(__file__).parents[1] / ".claude/hooks/contexto.py"
_spec = importlib.util.spec_from_file_location("contexto", _ruta)
assert _spec and _spec.loader
ctx = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ctx)
_spec = importlib.util.spec_from_file_location(
    "sincronizar", _ruta.with_name("sincronizar.py")
)
assert _spec and _spec.loader
sinc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sinc)

DECISIONES = """# Registro
- 2026-11-12 · Flujo GitHub · porque · PR
- _Pendiente_ · Idea elegida (plan1 / plan2)

## Fechas clave

| Fecha | Hito |
|---|---|
| 2026-11-10 | Ya pasó |
| 2026-11-22 | Datos congelados |
| 2026-11-13 | Revisión |
"""

README = """# Datos

| Nombre | URL | Licencia | Cómo obtenerla | Fichero en `raw/` | SHA-256 |
|---|---|---|---|---|---|
| _ejemplo_ | https://… | CC BY 4.0 | x | `ejemplo.csv` | |
| Renta INE | https://ine.es | CC BY 4.0 | x | `ine_2026-11-13.csv` | abc |
| Paro | https://sepe.es | CC BY 4.0 | x | `paro.csv` | def |

Otra tabla:

| Campo | Fichero |
|---|---|
| renta | `otro.csv` |
"""


def proyecto(tmp_path: Path) -> Path:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/decisiones.md").write_text(DECISIONES, encoding="utf-8")
    (tmp_path / "data/raw").mkdir(parents=True)
    (tmp_path / "data/README.md").write_text(README, encoding="utf-8")
    (tmp_path / "data/raw/paro.csv").write_text("a\n", encoding="utf-8")
    (tmp_path / "data/raw/nota.md").write_text(
        "(verificar) en raw no cuenta\n", encoding="utf-8"
    )
    (tmp_path / "data/processed").mkdir()
    (tmp_path / "data/processed/ine.csv").write_bytes(
        "Móstoles;(verificar)\n".encode("latin-1")
    )
    (tmp_path / "ideas/plan1").mkdir(parents=True)
    (tmp_path / "ideas/plan1/raro.md").write_bytes(
        "Año (verificar)\n".encode("latin-1")
    )
    (tmp_path / "ideas/plan1/ficha.md").write_text(
        "Dato A (verificar)\nDato B (Verificar año)\n", encoding="utf-8"
    )
    # Estructura libre: cualquier carpeta cuenta, salvo tests/ y las menciones entre «»
    (tmp_path / "analisis").mkdir()
    (tmp_path / "analisis/notas.md").write_text(
        "Las marcas «(verificar)» se resuelven\n", encoding="utf-8"
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test_x.py").write_text("x = '(verificar)'\n", encoding="utf-8")
    return tmp_path


def test_contexto_completo(tmp_path):
    texto = ctx.contexto(proyecto(tmp_path), date(2026, 11, 13))
    assert (
        "2026-11-13 (HOY): Revisión; 2026-11-22 (en 9 días): Datos congelados" in texto
    )
    assert "Ya pasó" not in texto
    assert "Idea elegida (plan1 / plan2)" in texto
    assert (
        "abiertas: 3, sobre todo en ideas/plan1/ficha.md (2)" in texto
    )  # latin-1 no rompe nada; data/processed no cuenta
    assert "Faltan 1 descargas" in texto and "ine_2026-11-13.csv (Renta INE)" in texto
    assert (
        "ejemplo" not in texto and "paro.csv" not in texto and "otro.csv" not in texto
    )


def test_proyecto_vacio_no_dice_nada(tmp_path):
    assert ctx.contexto(tmp_path, date(2026, 11, 13)) == ""


def transcript(ruta: Path, tokens: int) -> Path:
    uso = {
        "input_tokens": 2,
        "cache_read_input_tokens": tokens - 2,
        "cache_creation_input_tokens": 0,
    }
    lineas = [
        {"type": "user", "message": {"content": "hola"}},
        {"type": "assistant", "message": {"usage": uso}},
        {"type": "system", "subtype": "stop_hook_summary"},
    ]
    ruta.write_text(
        "\n".join(json.dumps(x) for x in lineas) + "\nlínea rota\n", encoding="utf-8"
    )
    return ruta


def test_aviso_de_contexto(tmp_path):
    evento = {
        "transcript_path": str(tmp_path / "t.jsonl"),
        "session_id": f"prueba-{tmp_path.name}",
    }
    transcript(tmp_path / "t.jsonl", 90_000)
    assert ctx.aviso_contexto(evento) == ""
    transcript(tmp_path / "t.jsonl", 160_000)
    aviso = json.loads(ctx.aviso_contexto(evento))["systemMessage"]
    assert "160 mil tokens" in aviso and "/compact" in aviso and "/clear" in aviso
    assert ctx.aviso_contexto(evento) == ""  # una vez por tramo
    transcript(tmp_path / "t.jsonl", 260_000)
    assert ctx.aviso_contexto(evento)  # tramo nuevo
    transcript(tmp_path / "t.jsonl", 40_000)  # tras /compact
    assert ctx.aviso_contexto(evento) == ""
    transcript(tmp_path / "t.jsonl", 170_000)
    assert ctx.aviso_contexto(evento)  # vuelve a crecer: se avisa otra vez
    assert ctx.aviso_contexto({}) == ""  # sin transcript, nada


def test_avisa_solo_si_origin_main_te_afecta(tmp_path):
    def g(cwd, *a):
        subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", *a],
            cwd=cwd,
            check=True,
            capture_output=True,
        )

    def sube(fichero):
        (otra / fichero).parent.mkdir(exist_ok=True)
        (otra / fichero).write_text(
            str(len(list(otra.rglob("*")))) + fichero + str(time.time_ns()),
            encoding="utf-8",
        )
        (
            g(otra, "add", "."),
            g(otra, "commit", "-q", "-m", fichero),
            g(otra, "push", "-q", "origin", "HEAD:main"),
        )

    g(tmp_path, "init", "-q", "--bare", "-b", "main", "origen.git")
    for nombre in ("yo", "otra"):
        g(tmp_path, "clone", "-q", "origen.git", nombre)
    yo, otra = tmp_path / "yo", tmp_path / "otra"
    sube("src/a.py")
    g(yo, "pull", "-q", "origin", "main")
    (yo / "src/a.py").write_text("mio", encoding="utf-8")  # yo toco a.py sin confirmar
    assert ctx.remoto(yo) == ""  # al día
    sube("src/ajeno.py")
    assert ctx.remoto(yo) == ""  # main avanzó, pero en algo que no toco
    sube("src/a.py")
    aviso = ctx.remoto(yo)
    assert (
        "src/a.py" in aviso
        and "git pull --rebase" in aviso
        and "sin confirmar" in aviso
    )
    g(yo, "checkout", "-q", "--", "."), g(yo, "pull", "-q", "origin", "main")
    (yo / "app").mkdir()
    (yo / "app/mapa.py").write_text(
        "from mesobra import renta\nfrom .otro import f\n", encoding="utf-8"
    )
    sube("src/mesobra/renta.py")  # lo importa mapa.py, que toco
    assert "src/mesobra/renta.py" in ctx.remoto(yo)
    g(yo, "pull", "-q", "origin", "main")
    sube("app/otro.py")  # import relativo
    assert "app/otro.py" in ctx.remoto(yo)
    g(yo, "pull", "-q", "origin", "main")
    sube("AGENTS.md")
    assert "AGENTS.md" in ctx.remoto(yo)  # regla común: avisa aunque no la toque
    assert ctx.remoto(tmp_path / "no-existe") == ""  # sin repo, calla


def test_sincroniza_tras_el_pr(tmp_path):
    def g(cwd, *a):
        subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", *a],
            cwd=cwd,
            check=True,
            capture_output=True,
        )

    def commit(repo, fichero, texto, rama):
        (repo / fichero).write_text(texto, encoding="utf-8")
        (
            g(repo, "add", "."),
            g(repo, "commit", "-q", "-m", fichero),
            g(repo, "push", "-q", "origin", f"HEAD:{rama}"),
        )

    g(tmp_path, "init", "-q", "--bare", "-b", "main", "origen.git")
    for nombre in ("yo", "otra"):
        g(tmp_path, "clone", "-q", "origen.git", nombre)
    yo, otra = tmp_path / "yo", tmp_path / "otra"
    commit(otra, "a.txt", "1", "main")
    g(yo, "pull", "-q", "origin", "main")
    g(yo, "checkout", "-q", "-b", "u/tema")
    assert sinc.sincronizar(yo) == ""  # al día
    commit(otra, "b.txt", "2", "main")
    (yo / "sucio.txt").write_text("x", encoding="utf-8")
    assert sinc.sincronizar(yo) == ""  # árbol sucio: no toca nada
    (yo / "sucio.txt").unlink()
    assert (
        "1 commits de origin/main" in sinc.sincronizar(yo) and (yo / "b.txt").exists()
    )
    commit(otra, "a.txt", "3", "main")
    commit(yo, "a.txt", "mio", "u/tema")
    assert "chocan" in sinc.sincronizar(yo)
    assert git_estado(yo) == ""  # el merge fallido se deshizo
    g(yo, "checkout", "-q", "main")
    assert sinc.sincronizar(yo) == ""  # en main no hace nada


def test_avisa_al_crear_un_worktree(tmp_path):
    aviso = sinc.avisar_worktree
    esperada = f"EnterWorktree (path: {tmp_path.resolve() / 'x'})"
    assert esperada in aviso(
        "git worktree add ../x -b u/t origin/main", tmp_path / "repo"
    )
    abs_x = Path("/abs/x").resolve()  # en Windows añade la unidad: C:\abs\x
    assert f"path: {abs_x})" in aviso("git worktree add -q /abs/x", tmp_path)
    assert f"path: {abs_x})" in aviso(
        "cd r && git worktree add -b u/t /abs/x main && ls y", tmp_path
    )
    orden = 'gh pr create --title t --body "Tras git worktree add, entra"'
    assert aviso(orden, tmp_path) == ""  # comillas sin cerrar al cortar: no falla
    assert aviso("git worktree list", tmp_path) == ""
    assert aviso("git status", tmp_path) == ""
    assert aviso("git worktree add -q /abs/x", Path("/abs/x/src")) == ""  # ya dentro


def test_main_de_sincronizar_usa_el_cwd_del_evento(
    principal_y_worktree, monkeypatch, capsys
):
    principal, wt = principal_y_worktree
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(principal))
    (wt / "src").mkdir()
    assert sinc.raiz({"cwd": str(wt / "src")}) == wt.resolve()
    assert sinc.raiz({}) == principal
    evento = {"tool_input": {"command": "git worktree add ../x"}, "cwd": str(wt)}
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(evento)))
    assert sinc.main() == 0
    salida = json.loads(capsys.readouterr().out)
    assert "systemMessage" not in salida
    assert "EnterWorktree" in salida["hookSpecificOutput"]["additionalContext"]


def git_estado(repo):
    return ctx.git(repo, "status", "--porcelain")


def test_avisa_de_las_skills_de_la_issue(tmp_path):
    (tmp_path / ".claude/agents").mkdir(parents=True)
    (tmp_path / ".claude/agents/dm-ag.md").write_text("---\n---\n", encoding="utf-8")
    for n in ("dm-x", "dm-y"):
        (tmp_path / f".claude/skills/{n}/SKILL.md").parent.mkdir(parents=True)
        (tmp_path / f".claude/skills/{n}/SKILL.md").write_text(
            "---\n---\n", encoding="utf-8"
        )
    linea = "- **Skills:** dm-x, dm-codigo-minimo, dm-y, dm-ag, dm-nada · **Revisores:** dm-revisor-codigo"
    aviso = sinc.avisar_skills
    for salida in (f"title\n{linea}\nfin", json.dumps(f"a\n{linea}\nb")):
        texto = aviso("gh issue view 89", salida, tmp_path)
        assert "invoca con Skill: dm-x, dm-y" in texto
        assert ".claude/skills/dm-x/SKILL.md" in texto
        assert "dm-ag es un agente, no una skill" in texto
        assert "dm-codigo-minimo no es una skill" in texto
        assert "dm-nada no existe" in texto and "dm-revisor-codigo" not in texto
    assert aviso("gh issue view 89", "- **Revisores:** dm-x", tmp_path) == ""
    assert aviso("ls", linea, tmp_path) == ""


def test_main_avisa_de_skills_salvo_en_subagente(tmp_path, monkeypatch, capsys):
    (tmp_path / ".claude/skills/dm-x").mkdir(parents=True)
    (tmp_path / ".claude/skills/dm-x/SKILL.md").write_text(
        "---\n---\n", encoding="utf-8"
    )
    evento = {
        "tool_input": {"command": "gh issue view 89"},
        "tool_response": {"stdout": "- **Skills:** dm-x · otro"},
        "cwd": str(tmp_path),
    }
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    for extra, esperado in (({}, True), ({"agent_type": "general-purpose"}, False)):
        monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({**evento, **extra})))
        assert sinc.main() == 0
        salida = capsys.readouterr().out
        assert ("invoca con Skill: dm-x" in salida) is esperado
