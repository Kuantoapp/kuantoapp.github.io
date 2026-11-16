"""`mesobra.censo2021` con un XML sintético en el formato del INE (107 valores por fila, sin etiquetas de columna)."""

import numpy as np
import pandas as pd
import pytest

from mesobra import censo2021 as c

META = ["Municipios: (...)", *c.METADATOS]


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
    total = np.nansum(np.array(list(filas.values()), float), axis=0)
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


def test_porcentaje_umbral_supresion_y_cero(tmp_path):
    filas = {
        "28001 A": _fila([(200, 100), (200, 100), (200, 100)]),  # 600 y 300 en alquiler
        "28002 B": _fila(
            [(90, 30), (90, 30), (90, 30)]
        ),  # 270 < 300: nulo por el umbral
        "28003 C": _fila([(200, 100), (None, None), (200, 100)]),  # una pieza suprimida
        "28004 D": _fila([(100, 0), (100, 0), (100, 0)]),  # cero publicado: 0, no nulo
    }
    pct = c.pct_alquiler_joven(_xml(tmp_path / "c.xml", filas))
    assert pct["28001"] == pytest.approx(0.5)
    assert pd.isna(pct["28002"]) and pd.isna(pct["28003"])
    assert pct["28004"] == 0
    assert list(pct.index) == ["28001", "28002", "28003", "28004"]


def test_error_si_la_tenencia_no_suma_el_total(tmp_path):
    fila = _fila([(200, 100)] * 3)
    fila[5 * 5 + 1] += 30  # propiedad de 20-24 inflada: Total distinto de la suma
    with pytest.raises(ValueError, match="distinto de propiedad"):
        c.pct_alquiler_joven(_xml(tmp_path / "c.xml", {"28001 A": fila}))


def test_error_si_cambia_el_formato(tmp_path):
    fila = _fila([(200, 100)] * 3)
    with pytest.raises(ValueError, match="107 valores"):
        c.pct_alquiler_joven(_xml(tmp_path / "c.xml", {"28001 A": fila[:-1]}))
