"""Tests de `mesobra.alquiler` con un recorte del Excel del SERPAVI."""

import geopandas as gpd
import openpyxl
import pandas as pd
import pytest
from shapely import Point, box

from mesobra import alquiler, api_estatica, pipeline_euros, sdm

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

EUR_OK = {"eur_m2_p25": [1.0], "eur_m2_p50": [2.0], "eur_m2_p75": [3.0]}
CUANTIA_OK = {"cuantia_p25": [1.0], "cuantia_p50": [2.0], "cuantia_p75": [3.0]}


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
    assert zona.loc[("28002", 2024), "cuantia_p50"] == 800
    assert pd.isna(fila["cuantia_p50"])


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
        {"eur_m2_p25": [13.0], "eur_m2_p50": [12.0], "eur_m2_p75": [15.0], **CUANTIA_OK}
    )
    with pytest.raises(ValueError, match="incoherentes"):
        alquiler._comprobar(df)


def test_comprobar_cuantia():
    df = pd.DataFrame(
        {
            "cuantia_p25": [900.0],
            "cuantia_p50": [800.0],
            "cuantia_p75": [1000.0],
            **EUR_OK,
        }
    )
    with pytest.raises(ValueError, match="incoherentes"):
        alquiler._comprobar(df)


def test_cuantia_nula_con_eur_m2():
    df = pd.DataFrame({**EUR_OK, **{k: [float("nan")] for k in CUANTIA_OK}})
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
        {
            "eur_m2_p25": [10.0],
            "eur_m2_p50": [float("nan")],
            "eur_m2_p75": [15.0],
            **{k: [float("nan")] for k in CUANTIA_OK},
        }
    )
    with pytest.raises(ValueError, match="incoherentes"):
        alquiler._comprobar(df)


def test_cache(xlsx, tmp_path):
    carpeta = tmp_path / "p"
    primera = alquiler.leer_serpavi(xlsx, carpeta)
    xlsx.unlink()
    segunda = alquiler.leer_serpavi(xlsx, carpeta)
    pd.testing.assert_frame_equal(primera["secciones"], segunda["secciones"])


def _zona(anio=2024, factor=1.0):
    return pd.DataFrame(
        {
            "zona_id": ["28001"], "anio": [anio], "eur_m2_p25": [10.0], "eur_m2_p50": [12.0],
            "eur_m2_p75": [14.0], "m2_p50": [70.0], "cuantia_p25": [700.0], "cuantia_p50": [800.0],
            "cuantia_p75": [900.0], "testigos": [20], "origen": ["observado"],
            "ic_inf": [float("nan")], "ic_sup": [float("nan")], "factor_ipc": [factor],
        }
    )  # fmt: skip


def _con_brecha(zona):
    return zona.assign(factor_brecha=1.2, brecha_ambito="municipio")


def _ipc():
    meses = [f"{a}M{m:02d}" for a in (2023, 2024) for m in range(1, 13)] + ["2025M01"]
    return pd.Series([95.0] * 12 + [100.0] * 12 + [105.0], index=meses)


def test_actualizar_ipc():
    zona = pd.concat([_zona(), _zona(2023).assign(zona_id="28002")], ignore_index=True)
    z = alquiler.actualizar_ipc(zona, _ipc())
    # factor por zona con su año (Titulcia lleva 2023, nota del 15-11 de #94), no uno único
    assert z["factor_ipc"].tolist() == pytest.approx([1.05, 105 / 95])
    assert z.attrs["ipc_hasta"] == "2025-01"
    assert z["eur_m2_p50"].iloc[0] == 12.0
    with pytest.raises(ValueError, match="2025"):
        alquiler.actualizar_ipc(_zona(2025), _ipc())


def test_actualizar_ipc_cifras_reales_desordenadas():
    # IPC297196 (INE, tabla 76137 actualizada el 2026-11-13): regresión de las cifras del PR #259
    meses = {
        2023: "93.669 93.761 93.971 94.154 94.282 94.364 94.501 94.594 94.739 94.969 95.213 95.375",
        2024: "95.563 95.739 96.017 96.327 96.722 96.923 97.140 97.397 97.699 98.133 98.440 98.649",
    }
    ipc = pd.Series(
        {
            f"{a}M{m:02d}": float(v)
            for a, txt in meses.items()
            for m, v in enumerate(txt.split(), 1)
        }
        | {"2026M10": 103.746}
    )
    zona = pd.concat([_zona(), _zona(2023).assign(zona_id="28002")], ignore_index=True)
    z = alquiler.actualizar_ipc(zona, ipc.iloc[::-1])
    assert z["factor_ipc"].tolist() == pytest.approx([1.068859, 1.098236], abs=1e-6)
    assert z.attrs["ipc_hasta"] == "2026-10"


def _csv_ipc(tmp_path, cm_valores):
    filas = ["Comunidades;Subgrupos;Tipo;Periodo;Total"]
    for ccaa, base in (("13 Madrid, Comunidad de", "100"), ("Nacional", "50")):
        for m in range(1, 13):
            filas.append(
                f"{ccaa};04.1 Alquiler de vivienda;Índice;2024M{m:02d};{base},5"
            )
    ine = tmp_path / "ine.csv"
    ine.write_text("\n".join(filas), encoding="utf-8-sig")
    cm = tmp_path / "cm.csv"
    cm.write_text(
        "Año;Concepto;Valor\n" + "\n".join(f"2024;x;{v}" for v in cm_valores),
        encoding="utf-8-sig",
    )
    return ine, cm


@pytest.mark.parametrize("orden", [(100.5, 50.5), (50.5, 100.5)])
def test_leer_ipc(tmp_path, orden):
    ipc = alquiler.leer_ipc(*_csv_ipc(tmp_path, orden))
    assert len(ipc) == 12 and (ipc == 100.5).all()
    assert ipc.index[-1] == "2024M12"


def test_leer_ipc_catalogo_no_casa(tmp_path):
    with pytest.raises(ValueError, match="2024"):
        alquiler.leer_ipc(*_csv_ipc(tmp_path, (90.0, 91.0)))


def test_leer_ipc_mes_vacio(tmp_path):
    ine, cm = _csv_ipc(tmp_path, (100.5, 50.5))
    texto = ine.read_text(encoding="utf-8-sig").replace("2024M12;100,5", "2024M12;")
    ine.write_text(texto, encoding="utf-8-sig")
    with pytest.raises(ValueError, match="huecos"):
        alquiler.leer_ipc(ine, cm)


def test_alquiler_json_con_ipc():
    obj = pipeline_euros.alquiler_json(
        _con_brecha(alquiler.actualizar_ipc(_zona(), _ipc()))
    )
    api_estatica.validar("alquiler.json", obj)
    assert obj["meta"]["ipc_hasta"] == "2025-01"
    assert sdm._citas_que_faltan(obj["meta"]) == []


def test_alquiler_json_sin_mes_falla():
    with pytest.raises(ValueError, match="ipc_hasta"):
        pipeline_euros.alquiler_json(_con_brecha(_zona(factor=1.05)))


def test_alquiler_json_lleva_la_brecha():
    z = pipeline_euros.alquiler_json(
        _con_brecha(alquiler.actualizar_ipc(_zona(), _ipc()))
    )["zonas"]
    assert z["28001"]["factor_brecha"] == 1.2
    assert z["28001"]["brecha_ambito"] == "municipio"


CABECERA = (
    "Localización de la vivienda", "Alquiler medio mensual",
    "Alquiler medio mensual (nuevos contratos)", "m2 medios", "m2 medios (nuevos contratos)",
)  # fmt: skip
CABECERA_DETALLE = [
    ("Localización de la vivienda", "Viviendas habituales arrendadas"),
    ("Número viviendas arrendadas", "Alquiler medio mensual"),
]


def _html(tmp_path, nombre, filas, cabeceras=(CABECERA,)):
    def tr(celdas):
        return "<tr>" + "".join(f"<td> {c} </td>" for c in celdas) + "</tr>"

    ruta = tmp_path / f"{nombre}.html"
    ruta.write_text(
        "<table>" + "".join(map(tr, [*cabeceras, *filas])) + "</table>",
        encoding="utf-8",
    )
    return ruta


def test_leer_aeat_miles_decimales_y_dos_cabeceras(tmp_path):
    una = alquiler.leer_aeat(
        _html(tmp_path, "a", [("Madrid-28079", "1.012", "1.167", "71", "68")])
    )
    assert una.loc["Madrid-28079", "Alquiler medio mensual (nuevos contratos)"] == 1167
    # cifras de la AEAT para Madrid capital en 2024: (1167/68)/(1012/71)
    assert alquiler.factor_nuevos(una).iloc[0] == pytest.approx(1.204037, abs=1e-6)
    dos = alquiler.leer_aeat(
        _html(
            tmp_path,
            "b",
            [("28001-Salamanca", "3.509", "21,7")],
            [("Localización de la vivienda", "Viviendas"), ("Número", "Alquiler m2")],
        )
    )
    assert dos.loc["28001-Salamanca"].tolist() == [3509, 21.7]


def test_leer_aeat_formato_inesperado(tmp_path):
    with pytest.raises(ValueError, match="formato"):
        alquiler.leer_aeat(_html(tmp_path, "a", [("x", "1")]))


def _aeat(tmp_path, detalle=(("28001-A", "100", "1.000"), ("28002-B", "300", "1.000"))):
    def fila(nombre, nuevos):
        return (nombre, "1.000", nuevos, "100", "100")

    return {
        "provincia": _html(tmp_path, "p", [fila("Madrid, Comunidad de", "1.190")]),
        "municipios": _html(
            tmp_path,
            "m",
            [
                fila("Getafe-28065", "1.150"),
                fila("Madrid", "1"),
                fila("Madrid-28079", "1.200"),
            ],
        ),
        "cp": _html(
            tmp_path, "c", [fila("28001-A", "1.100"), fila("28002-B", "1.300")]
        ),
        "cp_viviendas": _html(tmp_path, "v", detalle, CABECERA_DETALLE),
    }


def test_leer_brecha(tmp_path):
    b = alquiler.leer_brecha(_aeat(tmp_path))
    assert b["provincia"] == pytest.approx(1.19)
    assert b["municipio"].to_dict() == pytest.approx({"28065": 1.15, "28079": 1.2})
    assert b["cp"].loc["28002"].tolist() == pytest.approx([1.3, 300])


def test_leer_brecha_cp_distintos(tmp_path):
    with pytest.raises(ValueError, match="no coinciden"):
        alquiler.leer_brecha(_aeat(tmp_path, detalle=[("28001-A", "100", "1.000")]))


def test_tabla_paso_cp_cuenta_portales_en_madrid():
    secciones = gpd.GeoDataFrame(
        {"CUMUN": ["28079", "28079", "28065"], "CDIS": ["01", "02", "01"]},
        geometry=[box(0, 0, 10, 10), box(10, 0, 20, 10), box(20, 0, 30, 10)],
        crs=25830,
    )
    # 28001: 3 portales en el distrito 01 y 1 en el 02; 28002: 2 en el 02 y 2 fuera de Madrid, que no cuentan
    xy = [(1, 1), (2, 2), (3, 3), (11, 1), (12, 2), (13, 3), (21, 1), (22, 2)]
    portales = gpd.GeoDataFrame(
        {"cp": ["28001"] * 4 + ["28002"] * 4},
        geometry=[Point(x, y) for x, y in xy],
        crs=25830,
    )
    t = alquiler.tabla_paso_cp(portales, secciones).set_index(["origen", "destino"])
    assert t["peso"].to_dict() == pytest.approx(
        {
            ("28001", "2807901"): 0.75,
            ("28001", "2807902"): 0.25,
            ("28002", "2807902"): 1,
        }
    )
    assert t.loc[("28001", "2807902"), "peso_destino"] == pytest.approx(1 / 3)


def test_brecha_por_zona_precedencia(tmp_path):
    b = alquiler.leer_brecha(_aeat(tmp_path))
    tabla = pd.DataFrame(
        {
            "origen": ["28001", "28001", "28002"],
            "destino": ["2807901", "2807902", "2807902"],
            "peso": [0.75, 0.25, 1.0],
            "peso_destino": [1.0, 0.25, 0.75],
            "metodo": "portales",
        }
    )
    zona = pd.DataFrame(
        {"zona_id": ["2807901", "2807902", "28065", "28147", "2807903"]}
    )
    zona.attrs["ipc_hasta"] = "2026-10"
    z = alquiler.brecha_por_zona(zona, b, tabla)
    # distrito 02: viviendas × peso = 100 × 0,25 de 28001 (factor 1,1) y 300 de 28002 (1,3)
    esperado = (25 * 1.1 + 300 * 1.3) / 325
    assert z["factor_brecha"].tolist() == pytest.approx(
        [1.1, esperado, 1.15, 1.19, 1.2]
    )
    assert z["brecha_ambito"].tolist() == [
        "codigo_postal", "codigo_postal", "municipio", "comunidad", "municipio",
    ]  # fmt: skip
    assert z.attrs["ipc_hasta"] == "2026-10"
