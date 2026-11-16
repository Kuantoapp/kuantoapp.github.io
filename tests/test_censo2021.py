"""`mesobra.censo2021` con un XML sintético en el formato del INE (107 valores por fila, sin etiquetas de columna)."""

import xml.etree.ElementTree as ET
from datetime import date

import numpy as np
import pandas as pd
import pytest

from mesobra import censo2021 as c

META = ["Municipios: (...)", *c.METADATOS]


@pytest.fixture(autouse=True)
def _pocos_municipios(monkeypatch):
    monkeypatch.setattr(c, "MUNICIPIOS", 5)


def _grupo(total, alquiler):
    """Cinco columnas de un grupo de edad: Total, propiedad, alquiler, otro y no consta (todo lo demás, a propiedad)."""
    return [total, total - alquiler, alquiler, 0, 0]


def _fila(jovenes):
    """Tres grupos de 20-34 con (total, alquiler) cada uno; el resto de edades, vacío (ceros)."""
    v = [0] * 5 + [0] * 5 * 4  # Total y 0-19
    for t, a in jovenes:
        v += _grupo(t, a) if t is not None else [None] * 5
    return v + [0] * 5 * 11 + [0] * 4 * 3  # 35-89 y 90+, sin «No consta»


def _xml(ruta, filas):
    """Escribe el XML con la fila «Total» (suma de las demás) y `filas` {etiqueta: 107 valores}."""
    total = np.nansum(
        np.array([[*v, *[0] * (107 - len(v))] for v in filas.values()], float), axis=0
    )
    total[0] = (
        total[5:95:5].sum() + total[95::4].sum()
    )  # el Total de edades es la suma de los grupos

    def celda(v):
        texto = "" if v is None or pd.isna(v) else f"{v:.0f},00"
        return f'<Cell><Data ss:Type="String">{texto}</Data></Cell>'

    def fila(etiqueta, valores):
        return f"<Row><Cell><Data>{etiqueta}</Data></Cell>{''.join(map(celda, valores))}</Row>"

    meta = "".join(
        f"<Row>{celda(None)}<Cell><Data>{m}</Data></Cell></Row>" for m in META
    )
    cuerpo = fila("Total", total) + "".join(fila(k, v) for k, v in filas.items())
    ruta.write_text(
        '<?xml version="1.0" encoding="ISO-8859-1"?><Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet" '
        'xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"><Worksheet><Table>'
        f"{meta}{cuerpo}</Table></Worksheet></Workbook>",
        encoding="iso-8859-1",
    )
    return ruta


RESTO = {f"2800{i} X": _fila([(200, 100)] * 3) for i in range(2, 6)}


def test_porcentaje_umbral_supresion_y_cero(tmp_path):
    filas = {
        "28001 A": _fila([(200, 100), (200, 100), (200, 100)]),  # 600 y 300 en alquiler
        "28002 B": _fila(
            [(90, 30), (90, 30), (90, 30)]
        ),  # 270 < 300: nulo por el umbral
        "28003 C": _fila([(200, 100), (None, None), (200, 100)]),  # una pieza suprimida
        "28004 D": _fila([(100, 0), (100, 0), (100, 0)]),  # cero publicado: 0, no nulo
        "28005 E": _fila([(100, 50)] * 3),  # justo 300: no cae por el umbral
    }
    pct = c.pct_alquiler_joven(_xml(tmp_path / "c.xml", filas))
    assert pct["28001"] == pytest.approx(0.5)
    assert pd.isna(pct["28002"]) and pd.isna(pct["28003"])
    assert pct["28004"] == 0
    assert pct["28005"] == pytest.approx(0.5)
    assert list(pct.index) == [f"2800{i}" for i in range(1, 6)]
    assert c.recuento(tmp_path / "c.xml") == {
        "suprimidos": 1,
        "bajo_umbral": 1,
        "con_porcentaje": 3,
    }


def test_error_si_la_tenencia_no_suma_el_total(tmp_path):
    fila = _fila([(200, 100)] * 3)
    fila[5 * 5 + 1] += 30  # propiedad de 20-24 inflada: Total distinto de la suma
    with pytest.raises(ValueError, match="distinto de propiedad"):
        c.pct_alquiler_joven(_xml(tmp_path / "c.xml", {"28001 A": fila} | RESTO))


def test_error_si_cambia_el_formato(tmp_path):
    fila = _fila([(200, 100)] * 3)
    with pytest.raises(ValueError, match="107 valores"):
        c.pct_alquiler_joven(_xml(tmp_path / "c.xml", {"28001 A": fila[:-1]} | RESTO))


def test_error_si_los_municipios_no_son_los_esperados(tmp_path):
    fila = _fila([(200, 100)] * 3)
    cuatro = {f"2800{i} X": fila for i in range(1, 5)}
    with pytest.raises(ValueError, match="5 municipios"):
        c.pct_alquiler_joven(_xml(tmp_path / "a.xml", cuatro))
    de_mas = {**cuatro, "28001 X ": fila, "28001 Y": fila}
    with pytest.raises(ValueError, match="5 municipios"):
        c.pct_alquiler_joven(_xml(tmp_path / "b.xml", de_mas))
    dup = {**cuatro, "28001 Y": fila}
    with pytest.raises(ValueError, match="únicos"):
        c.pct_alquiler_joven(_xml(tmp_path / "d.xml", dup))
    mal = {**cuatro, "29005 X": fila}
    with pytest.raises(ValueError, match="28xxx"):
        c.pct_alquiler_joven(_xml(tmp_path / "c.xml", mal))


def test_abrir_solo_https_a_ine():
    with pytest.raises(ValueError, match="Solo"):
        c._abrir(None, "http://www.ine.es/Censo2021/Inicio.do")
    with pytest.raises(ValueError, match="Solo"):
        c._abrir(None, "https://example.com/")


def test_descargar_valida_antes_de_escribir_y_no_sobrescribe(tmp_path, monkeypatch):
    monkeypatch.setattr(c, "_consulta", lambda: b"<html>error</html>")
    with pytest.raises((ET.ParseError, ValueError)):
        c.descargar(tmp_path, date(2026, 11, 16))
    assert list(tmp_path.iterdir()) == []
    ok = _xml(tmp_path / "ok.xml", {"28001 A": _fila([(200, 100)] * 3)} | RESTO)
    monkeypatch.setattr(c, "_consulta", ok.read_bytes)
    destino = tmp_path / "raw"
    destino.mkdir()
    final = c.descargar(destino, date(2026, 11, 16))
    assert final.name == "ine_censo2021_tenencia_edad_municipios_2026-11-16.xml"
    assert final.read_bytes() == ok.read_bytes()
    with pytest.raises(FileExistsError):
        c.descargar(destino, date(2026, 11, 16))
