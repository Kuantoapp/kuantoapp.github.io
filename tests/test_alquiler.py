"""Tests de `mesobra.alquiler` con un recorte del Excel del SERPAVI."""

import openpyxl
import pandas as pd
import pytest

from mesobra import alquiler

VARIABLES = [*alquiler.TESTIGOS, *alquiler.EUR_M2, *alquiler.CUANTIA, *alquiler.M2]
MEDIDAS = [f"{v}_{aa}" for aa in (23, 24) for v in VARIABLES]
# las celdas ausentes de SIN_PRECIO son celdas no publicadas ('')
SIN_PRECIO = {"BI_ALVHEPCO_TVC": 0}
OK = {
    "BI_ALVHEPCO_TVC": 20,
    "ALQM2_LV_25_VC": 10,
    "ALQM2_LV_M_VC": "12,5",
    "ALQM2_LV_75_VC": 15.0,
    "SLVM2_M_VC": 70,
    "ALQTBID12_25_VC": 700,
    "ALQTBID12_M_VC": 800,
    "ALQTBID12_75_VC": 900,
}


def _fila(codigos, valores):
    return [*codigos, *(valores.get(m[:-3], "") for m in MEDIDAS)]


@pytest.fixture
def xlsx(tmp_path):
    wb = openpyxl.Workbook()
    wb.active.title = "Metadatos"
    hojas = {
        "Municipios": (
            ["CPRO", "CUMUN"],
            [[28, "28001"], ["28", 28002], [28, "28079"], [1, "01001"]],
        ),
        "Distritos": (
            ["CPRO", "CUMUN", "CUDIS"],
            [
                [28, "28079", "2807901"],
                [28, "28005", "2800501"],
                [1, "01001", "0100101"],
            ],
        ),
        "Secciones censales": (
            ["CPRO", "CUMUN", "CUSEC"],
            [
                [28, "28001", "2800101001"],
                [28, "28079", "2807901001"],
                [1, "01001", "0100101001"],
            ],
        ),
    }
    valores = {
        "28001": SIN_PRECIO,
        "2800101001": SIN_PRECIO,
        "01001": OK,
        "0100101": OK,
    }
    for nombre, (cabecera, filas) in hojas.items():
        ws = wb.create_sheet(nombre)
        ws.append([*cabecera, *MEDIDAS])
        for f in filas:
            ws.append(_fila(f, valores.get(str(f[-1]), OK)))
    ruta = tmp_path / "serpavi.xlsx"
    wb.save(ruta)
    return ruta


def test_formato_codigos_y_filtro(xlsx, tmp_path):
    hojas = alquiler.leer_serpavi(xlsx, tmp_path / "p")
    mun = hojas["municipios"]
    assert sorted(mun["CUMUN"]) == [
        "28001",
        "28002",
        "28079",
    ]  # sin otra provincia, código int a texto
    assert sorted(hojas["distritos"]["CUDIS"]) == ["2800501", "2807901"]
    assert (hojas["secciones"]["CUSEC"].str.len() == 10).all()
    assert mun.set_index("CUMUN").loc["28002", "ALQM2_LV_M_VC_24"] == 12.5
    assert pd.isna(mun.set_index("CUMUN").loc["28001", "ALQM2_LV_M_VC_24"])


def test_sin_dato_nulo_y_no_cero(xlsx, tmp_path):
    zona = alquiler.alquiler_zona(
        alquiler.leer_serpavi(xlsx, tmp_path / "p")
    ).set_index(["zona_id", "anio"])
    fila = zona.loc[("28001", 2024)]
    assert fila["origen"] == "sin_dato" and fila["testigos"] == 0
    assert pd.isna(fila[["eur_m2_p25", "eur_m2_p50", "eur_m2_p75", "m2_p50"]]).all()
    assert zona.loc[("28002", 2024), "origen"] == "observado"


def test_formato_largo(xlsx, tmp_path):
    hojas = alquiler.leer_serpavi(xlsx, tmp_path / "p")
    zona, seccion = alquiler.alquiler_zona(hojas), alquiler.alquiler_seccion(hojas)
    assert sorted(zona["anio"].unique()) == [2023, 2024]
    assert (
        len(zona) == 4 * 2
    )  # 28001, 28002, 28079 y el distrito 2807901; 2800501 no es de Madrid
    assert (zona["factor_ipc"] == 1.0).all()
    assert len(seccion) == 2 * 2
    assert seccion["cuantia_p50"].dropna().eq(800).all()


def test_comprobar_percentiles():
    df = pd.DataFrame(
        {"eur_m2_p25": [13.0], "eur_m2_p50": [12.0], "eur_m2_p75": [15.0]}
    )
    with pytest.raises(ValueError, match="incoherentes"):
        alquiler._comprobar(df)


def test_falta_variable_o_anio(xlsx, tmp_path):
    hojas = alquiler.leer_serpavi(xlsx, tmp_path / "p")
    hojas["municipios"] = hojas["municipios"].drop(columns="ALQM2_LV_M_VC_24")
    with pytest.raises(ValueError, match="Faltan variables o años"):
        alquiler.alquiler_zona(hojas)


def test_mismos_recuentos_otros_anios():
    df = pd.DataFrame(
        {"id": ["1"], "A_23": [1.0], "A_24": [1.0], "B_22": [1.0], "B_24": [1.0]}
    )
    with pytest.raises(ValueError, match="Faltan variables o años"):
        alquiler._largo(df, "id", {"A": "a", "B": "b"})


def test_cuartil_sin_mediana():
    df = pd.DataFrame(
        {"eur_m2_p25": [10.0], "eur_m2_p50": [float("nan")], "eur_m2_p75": [15.0]}
    )
    with pytest.raises(ValueError, match="incoherentes"):
        alquiler._comprobar(df)


def test_cache(xlsx, tmp_path):
    carpeta = tmp_path / "p"
    primera = alquiler.leer_serpavi(xlsx, carpeta)
    xlsx.unlink()
    segunda = alquiler.leer_serpavi(xlsx, carpeta)
    pd.testing.assert_frame_equal(primera["secciones"], segunda["secciones"])
