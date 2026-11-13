import importlib.util
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "perfilar",
    Path(__file__).parents[1]
    / ".claude/skills/dm-diccionario-datos/scripts/perfilar.py",
)
assert _spec and _spec.loader
perfilar = importlib.util.module_from_spec(_spec)
sys.modules["perfilar"] = perfilar  # @dataclass busca su módulo en sys.modules
_spec.loader.exec_module(perfilar)


def _csv(tmp_path: Path) -> Path:
    filas = ["id;x;cat;empty"] + [
        f"{i};{i * 1.5};{'a' if i % 4 else 'b'};" for i in range(100)
    ]
    filas.append("100;oops;a;")  # tipo mezclado
    ruta = tmp_path / "d.csv"
    ruta.write_text("\n".join(filas), encoding="utf-8")
    return ruta


def test_perfil_y_conserva_texto_manual(tmp_path: Path) -> None:
    ruta = _csv(tmp_path)
    assert perfilar.main([str(ruta)]) == 0
    salida = tmp_path / "d.DATA.md"
    texto = salida.read_text(encoding="utf-8")
    for esperado in (
        "Filas: 101",
        "| id | int |",
        "| x | mixto |",
        "| empty | vacia |",
        "top: a (75%)",
    ):
        assert esperado in texto
    fila = "| id | int | 0.0 | >=50 | 0..100 (media 50) |"
    salida.write_text(
        texto.replace(f"{fila} POR COMPLETAR |", f"{fila} identificador |")
        + "\nnota manual\n",
        encoding="utf-8",
    )
    perfilar.main([str(ruta)])
    otra = salida.read_text(encoding="utf-8")
    assert "identificador" in otra and "nota manual" in otra


def test_check_detecta_cambios(tmp_path: Path) -> None:
    ruta = _csv(tmp_path)
    assert perfilar.main([str(ruta), "--check"]) == 2
    perfilar.main([str(ruta)])
    assert perfilar.main([str(ruta), "--check"]) == 0
    ruta.write_text(ruta.read_text(encoding="utf-8") + "\n101;1;a;", encoding="utf-8")
    assert perfilar.main([str(ruta), "--check"]) == 1


def test_muestrea_todo_el_fichero(tmp_path: Path) -> None:
    res = perfilar.profile(_csv(tmp_path), max_rows=20, seed=1)
    assert res["rows_total"] == 101
    assert res["profiled"] <= 21


def test_avisa_de_latin1_y_formato_espanol(tmp_path: Path) -> None:
    ruta = tmp_path / "m.csv"
    filas = ["municipio;renta"] + [f"Móstoles;{i}.234,5" for i in range(1, 30)]
    ruta.write_bytes("\n".join(filas).encode("latin-1"))
    salida = tmp_path / "otra/m.DATA.md"
    assert perfilar.main([str(ruta), "--out", str(salida)]) == 0
    texto = salida.read_text(encoding="utf-8")
    assert "--encoding latin-1" in texto
    assert "formato espanol" in texto and "`renta`" in texto
    perfilar.main([str(ruta), "--out", str(salida), "--encoding", "latin-1"])
    texto = salida.read_text(encoding="utf-8")
    assert "Móstoles" in texto and "no decodificables" not in texto
