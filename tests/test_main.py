"""`python -m mesobra`: se detiene si falta una fuente y encadena los cuatro pasos en orden."""

from types import SimpleNamespace

import pytest

from mesobra import __main__ as comando

README = """| Nombre | URL | Licencia | Cómo obtenerla | Fichero en `raw/` | SHA-256 |
|---|---|---|---|---|---|
| A | https://a | MIT | `descargar.py https://a --nombre a` | `a.csv` | `{sha}` |
"""
SHA_ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


@pytest.fixture
def raiz(tmp_path, monkeypatch):
    (tmp_path / "data/raw").mkdir(parents=True)
    (tmp_path / "data/README.md").write_text(README.format(sha=SHA_ABC), "utf-8")
    monkeypatch.setattr(comando, "RAIZ", tmp_path)
    return tmp_path


def _pasos(monkeypatch):
    llamadas = []
    monkeypatch.setattr(
        comando,
        "import_module",
        lambda n: SimpleNamespace(main=lambda: llamadas.append(n)),
    )
    return llamadas


def test_fuente_ausente_se_detiene_sin_ejecutar_pasos(raiz, monkeypatch):
    llamadas = _pasos(monkeypatch)
    with pytest.raises(SystemExit) as e:
        comando.main()
    assert "a.csv" in str(e.value) and "--nombre a" in str(e.value)
    assert llamadas == []


def test_con_todo_presente_ejecuta_en_orden_y_valida(raiz, monkeypatch):
    (raiz / "data/raw/a.csv").write_bytes(b"abc")
    llamadas = _pasos(monkeypatch)
    validadas = []
    monkeypatch.setattr(comando, "validar_api", validadas.append)
    comando.main()
    assert llamadas == [f"mesobra.{p}" for p in comando.PASOS]
    assert comando.PASOS[-1] == "sdm" and validadas == [raiz / "app/datos"]
