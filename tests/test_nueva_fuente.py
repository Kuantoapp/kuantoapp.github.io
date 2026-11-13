"""Script de descarga de dm-nueva-fuente: nombre con fecha, nunca sobrescribe, SHA-256 y comprobación del equipo."""

import hashlib
import importlib.util
import io
from datetime import date
from pathlib import Path

import pytest

_ruta = (
    Path(__file__).parents[1] / ".claude/skills/dm-nueva-fuente/scripts/descargar.py"
)
_spec = importlib.util.spec_from_file_location("descargar", _ruta)
assert _spec and _spec.loader
dsc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dsc)

HOY = date(2026, 11, 13)


def servidor(contenido: bytes):
    return lambda peticion, timeout: io.BytesIO(contenido)


def test_descarga_con_fecha_y_sin_sobrescribir(tmp_path):
    raw = tmp_path / "data/raw"
    f = dsc.descargar(
        "https://x.es/a.csv", "ine_renta", "csv", raw, HOY, servidor(b"a;b\n1;2\n")
    )
    assert f == raw / "ine_renta_2026-11-13.csv" and f.read_bytes() == b"a;b\n1;2\n"
    assert dsc.sha256(f) == hashlib.sha256(b"a;b\n1;2\n").hexdigest()
    assert list((tmp_path / "data").glob(".*parcial")) == []
    with pytest.raises(SystemExit, match="no se sobrescribe"):
        dsc.descargar(
            "https://x.es/a.csv", "ine_renta", "csv", raw, HOY, servidor(b"otro")
        )
    assert f.read_bytes() == b"a;b\n1;2\n"


def test_rechaza_http_nombres_raros_y_vacios(tmp_path):
    raw = tmp_path / "data/raw"
    for url, nombre in [("http://x.es/a.csv", "a"), ("https://x.es/a.csv", "../a")]:
        with pytest.raises(SystemExit):
            dsc.descargar(url, nombre, "csv", raw, HOY, servidor(b"x"))
    with pytest.raises(SystemExit, match="vacía"):
        dsc.descargar("https://x.es/a.csv", "a", "csv", raw, HOY, servidor(b""))
    assert (
        list(raw.iterdir()) == [] and list((tmp_path / "data").glob(".*parcial")) == []
    )


def test_comprobar_mismos_datos(tmp_path):
    raw = tmp_path / "data/raw"
    raw.mkdir(parents=True)
    (raw / "bien.csv").write_bytes(b"1\n")
    (raw / "cambiado.csv").write_bytes(b"2\n")
    h = hashlib.sha256(b"1\n").hexdigest()
    readme = tmp_path / "data/README.md"
    readme.write_text(
        "| Nombre | URL | Licencia | Cómo obtenerla | Fichero en `raw/` | SHA-256 |\n"
        "|---|---|---|---|---|---|\n"
        "| _ejemplo_ | x | x | x | `ejemplo.csv` | `abc` |\n"
        f"| Bien | x | x | x | `bien.csv` | `{h}` |\n"
        f"| Cambiado | x | x | x | `cambiado.csv` | `{h}` |\n"
        f"| Falta | x | x | x | `falta.csv` | `{h}` |\n"
        "| Sin huella | x | x | x | `bien.csv` | |\n",
        encoding="utf-8",
    )
    problemas = dsc.comprobar(readme, raw)
    assert len(problemas) == 2
    assert problemas[0].startswith("cambiado.csv: SHA-256 distinto")
    assert "sin SHA-256" in problemas[1]


def test_error_de_red_no_deja_nada(tmp_path):
    import urllib.error

    def caido(peticion, timeout):
        raise urllib.error.URLError("sin red")

    raw = tmp_path / "data/raw"
    with pytest.raises(SystemExit, match="No se pudo descargar"):
        dsc.descargar("https://x.es/a.csv", "a", "csv", raw, HOY, caido)
    assert (
        list(raw.iterdir()) == [] and list((tmp_path / "data").glob(".*parcial")) == []
    )


class Respuesta(io.BytesIO):
    def __init__(
        self, contenido: bytes, url: str = "https://x.es/a.csv", longitud=None
    ):
        super().__init__(contenido)
        self.url = url
        self.headers = {"Content-Length": str(longitud)} if longitud else {}


def test_corte_redireccion_y_extension(tmp_path):
    raw = tmp_path / "data/raw"
    casos = [
        (lambda p, timeout: Respuesta(b"abc", longitud=10), "csv", "incompleta"),
        (
            lambda p, timeout: Respuesta(b"abc", url="http://x.es/a.csv"),
            "csv",
            "sin https",
        ),
        (servidor(b"abc"), "csv/../../fuera", "Extensión no válida"),
    ]
    for abrir, ext, error in casos:
        with pytest.raises(SystemExit, match=error):
            dsc.descargar("https://x.es/a.csv", "a", ext, raw, HOY, abrir)
    assert (
        list(raw.iterdir()) == [] and list((tmp_path / "data").glob(".*parcial")) == []
    )
    f = dsc.descargar(
        "https://x.es/a.csv",
        "a",
        "CSV",
        raw,
        HOY,
        lambda p, timeout: Respuesta(b"abc", longitud=3),
    )
    assert f.name == "a_2026-11-13.csv"


def test_comprobar_solo_la_tabla_de_fuentes(tmp_path):
    raw = tmp_path / "data/raw"
    raw.mkdir(parents=True)
    readme = tmp_path / "data/README.md"
    readme.write_text(
        "# Datos\n\n| Nombre | Fichero en `raw/` | SHA-256 |\n|---|---|---|\n"
        "| Vacía | | `abc` |\n| Rota | `a|b.csv` | `abc` |\n\n"
        "| Campo | Fichero en `raw/` | SHA-256 |\n|---|---|---|\n| renta | `x.csv` | `abc` |\n",
        encoding="utf-8",
    )
    problemas = dsc.comprobar(readme, raw)
    assert problemas == [
        "Vacía: sin fichero en data/README.md",
        "fila mal formada (¿un | dentro de una celda?): Rota",
    ]
