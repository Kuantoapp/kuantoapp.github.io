"""Hook SessionStart de contexto: hitos, decisiones pendientes, «(verificar)» y descargas que faltan."""

import importlib.util
from datetime import date
from pathlib import Path

_ruta = Path(__file__).parents[1] / ".claude/hooks/contexto.py"
_spec = importlib.util.spec_from_file_location("contexto", _ruta)
assert _spec and _spec.loader
ctx = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ctx)

DECISIONES = """# Registro
- 2026-11-12 · Flujo GitHub · porque · PR
- _Pendiente_ · Idea elegida (plan1 / plan2)

## Hitos

| Fecha | Hito |
|---|---|
| 2026-11-10 | Ya pasó |
| 2026-11-22 | Datos congelados |
| 2026-11-13 | Revisión |
"""

README = """| Nombre | URL | Licencia | Cómo obtenerla | Fichero en `raw/` | SHA-256 |
|---|---|---|---|---|---|
| _ejemplo_ | https://… | CC BY 4.0 | x | `ejemplo.csv` | |
| Renta INE | https://ine.es | CC BY 4.0 | x | `ine_2026-11-13.csv` | abc |
| Paro | https://sepe.es | CC BY 4.0 | x | `paro.csv` | def |
"""


def proyecto(tmp_path: Path) -> Path:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/decisiones.md").write_text(DECISIONES, encoding="utf-8")
    (tmp_path / "data/raw").mkdir(parents=True)
    (tmp_path / "data/README.md").write_text(README, encoding="utf-8")
    (tmp_path / "data/raw/paro.csv").write_text("a\n")
    (tmp_path / "data/raw/nota.md").write_text("(verificar) en raw no cuenta\n")
    (tmp_path / "ideas/plan1").mkdir(parents=True)
    (tmp_path / "ideas/plan1/ficha.md").write_text(
        "Dato A (verificar)\nDato B (Verificar año)\n"
    )
    return tmp_path


def test_contexto_completo(tmp_path):
    texto = ctx.contexto(proyecto(tmp_path), date(2026, 11, 13))
    assert (
        "2026-11-13 (HOY): Revisión; 2026-11-22 (en 9 días): Datos congelados" in texto
    )
    assert "Ya pasó" not in texto
    assert "Idea elegida (plan1 / plan2)" in texto
    assert "abiertas: 2, sobre todo en ideas/plan1/ficha.md (2)" in texto
    assert "Faltan 1 descargas" in texto and "ine_2026-11-13.csv (Renta INE)" in texto
    assert "ejemplo" not in texto and "paro.csv" not in texto


def test_proyecto_vacio_no_dice_nada(tmp_path):
    assert ctx.contexto(tmp_path, date(2026, 11, 13)) == ""
