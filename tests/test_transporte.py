from decimal import Decimal as D
from itertools import pairwise, product

import geopandas as gpd
import pytest
from shapely import Point, box

from mesobra import transporte as t

V, S = "vigente_2026", "sin_descuento"


def coste(clave, dias, no_laborables=0, *, edad="general", esc=V):
    return t.coste_mes(esc, edad, clave, dias, no_laborables)


def test_precios_de_control():
    assert (t.ABONO_30["A"][V], t.ABONO_30["C2"][V]) == (D("32.70"), D("49.20"))
    assert (t.ABONO_30["A"][S], t.ABONO_30["C2"][S]) == (D("56.20"), D("84.40"))
    assert {V: D("10.00"), S: D("20.00")} == t.ABONO_JOVEN
    assert t.ABONO_INTERZONAL["B2", "C1"] == {V: D("28.70"), S: D("49.30")}
    assert t.ABONO_INTERZONAL["B1", "C2"] == {V: D("32.70"), S: D("56.20")}
    assert (
        len(t.ABONO_INTERZONAL) == 10
    )  # todas las parejas de B1-C2 (BOCM-20251231-2 pág. 66)
    assert [p[V] for p in t.DIEZ_VIAJES_INTERURBANO] == [
        D(x) for x in ("5.10", "7.30", "9.60", "13.80", "17.80", "22.40")
    ]
    assert t.DIEZ_VIAJES["metro_b"] == {V: D("6.70"), S: D("11.50")}
    assert t.DIEZ_VIAJES["combinado"] == {V: D("10.90"), S: D("18.80")}
    assert t.SENCILLO["metro_a"][V] == D("1.50")
    assert t.SENCILLO["interurbano"][S] == D("3.00")


def test_calendario_laboral_de_2026():
    # 261 laborables - 10 festivos en laborable - 2 locales - 22 de vacaciones
    assert sum(f.weekday() < 5 for f in t.FESTIVOS_2026) == 10
    assert (t.LABORABLES_2026, t.DIAS_TRABAJO) == (261, 227)
    assert {(f.month, f.day) for f in t.FESTIVOS_2026 if f.weekday() >= 5} == {
        (5, 2),
        (8, 15),
    }


@pytest.mark.parametrize(
    ("cmin", "cmax", "sistemas", "validaciones", "esperada"),
    [
        ("A", "A", None, 1, "A-A|metro_a"),
        ("B2", "C1", None, 1, "B2-C1|interurbano"),
        ("A", "C2", "interurbano+metro", 2, "A-C2|interurbano+metro_a"),
        ("A", "B2", "metro", 1, "A-B2|combinado"),
        ("B1", "B2", "metro", 1, "B1-B2|metro_b"),
        ("A", "A", "emt+metro", 3, "A-A|metro_a+metro_a+metro_a"),
        ("A", "B1", "metro_ligero", 1, "A-B1|tfm_mlo"),
        ("B3", "B3", "urbano", 1, "B3-B3|urbano"),
        ("A", "C1", "cercanias", 1, "A-C1|cercanias"),
    ],
)
def test_clave_tarifa(cmin, cmax, sistemas, validaciones, esperada):
    assert t.clave_tarifa(cmin, cmax, sistemas, validaciones) == esperada


@pytest.mark.parametrize(
    ("args", "mensaje"),
    [
        (("C1", "B2"), "al revés"),
        (("A", "B1", "avion"), "fuera de"),
        (("A", "B1", "emt+metro", 1), "validaciones"),
    ],
)
def test_clave_tarifa_rechaza(args, mensaje):
    with pytest.raises(ValueError, match=mensaje):
        t.clave_tarifa(*args)


def test_control_interzonal_b2_c1():
    # abono B2-C1 de 28,70 €: 28,70 × 335/30 / 12 = 26,71 €/mes; el 10 viajes, 37,83 × 0,96 = 36,32
    assert coste("B2-C1|interurbano", 5) == ("Abono 30 días B2-C1", D("26.71"))


def test_control_dentro_de_una_corona():
    # B1-B2 (28,70 → 26,71 €/mes) frente al 10 viajes de zona única: 37,83 × 0,51 = 19,30
    assert t.clave_tarifa("B1", "B1") == "B1-B1|interurbano"
    assert coste("B1-B1|interurbano", 5) == ("10 viajes", D("19.30"))
    # con 16 viajes de ocio: 53,83 × 0,51 = 27,45 pasa del abono B1-B2
    assert coste("B1-B1|interurbano", 5, 16) == ("Abono 30 días B1-B2", D("26.71"))


def test_control_de_transbordo():
    # #80 daba 29,70 con paquetes enteros; prorrateado (no caduca): 7,567 / 10 × (22,40 + 7,30)
    clave = t.clave_tarifa("A", "C2", "interurbano+metro", 2)
    assert coste(clave, 1) == ("10 viajes", D("22.47"))


def test_umbral_del_abono_en_zona_a_con_8_viajes_de_ocio():
    # 4 días: (30,27 + 8) × 0,73 = 27,93; 5 días: (37,83 + 8) × 0,73 = 33,46 > 30,43 del abono
    titulos = [coste("A-A|metro_a", d, 8)[0] for d in t.DIAS]
    assert titulos == ["10 viajes"] * 4 + ["Abono 30 días"]
    assert coste("A-A|metro_a", 5, 0) == ("10 viajes", D("27.62"))


def test_ocio_en_el_producto_principal():
    # 8 viajes de ocio al interurbano A-C2: (7,57 + 8) × 2,24 + 7,57 × 0,73 = 40,39 (al Metro saldría 28,31)
    assert coste("A-C2|interurbano+metro_a", 1, 8) == ("10 viajes", D("40.39"))


def test_producto_sin_precio_falla():
    with pytest.raises(ValueError, match="sin precio"):
        coste("A-B1|avion", 1)


def test_mezcla_de_titulos_por_tramo():
    # sin descuento, por viaje: interurbano A-C2 sencillo 3,00 < 3,85 del 10 viajes; Metro 1,25 < 1,50
    clave = "A-C2|interurbano+metro_a"
    assert coste(clave, 1, esc=S) == ("10 viajes + Billete sencillo", D("32.16"))


def test_edades():
    assert coste("A-C2|interurbano", 5, edad="joven") == ("Abono Joven", D("9.31"))
    assert coste("A-C2|interurbano", 5, edad="mayor_65") == ("Abono +65", D("0.00"))
    # el 10 viajes de zona única con 1 día (3,86) gana al Abono Joven (9,31)
    assert coste("B1-B1|interurbano", 1, edad="joven")[0] == "10 viajes"
    assert t.es_joven(15) and t.es_joven(25)
    assert not t.es_joven(14) and not t.es_joven(26)


def test_cercanias():
    assert coste("A-C2|cercanias", 5) == ("Abono Renfe", D("18.61"))
    # sin descuento no hay precio de Renfe: solo el abono del CRTM
    assert coste("A-C2|cercanias", 5, esc=S) == ("Abono 30 días", D("78.54"))


def test_mas_dias_o_mas_ocio_no_cuestan_menos():
    claves = [
        "A-A|metro_a",
        "B1-B1|interurbano",
        "B2-C2|interurbano",
        "A-C2|interurbano+metro_a",
    ]
    for esc, edad, clave in product(t.ESCENARIOS, t.EDADES, claves):
        costes = [
            coste(clave, d, nl, edad=edad, esc=esc)[1]
            for d in t.DIAS
            for nl in t.NO_LABORABLES
        ]
        por_dias = [
            costes[i :: len(t.NO_LABORABLES)] for i in range(len(t.NO_LABORABLES))
        ]
        assert all(c == sorted(c) for c in por_dias)
        assert all(
            costes[i : i + 3] == sorted(costes[i : i + 3]) for i in range(0, 15, 3)
        )


@pytest.mark.parametrize(("dias", "nl"), [(0, 0), (3, 5)])
def test_fuera_de_dominio(dias, nl):
    with pytest.raises(ValueError, match="fuera de"):
        coste("A-A|metro_a", dias, nl)


def test_tabla():
    claves = ["A-A|metro_a", "B2-C1|interurbano"]
    df = t.tabla(claves)
    assert len(df) == 2 * 3 * 2 * 5 * 3
    fila = df.query(
        "escenario == @V and edad == 'general' and clave_tarifa == 'B2-C1|interurbano' "
        "and dias == 5 and no_laborables == 0"
    )
    assert fila.coste_mes.item() == 26.71


def test_tabla_v1_conserva_la_forma_de_80():
    df = t.tabla_v1()
    assert len(df) == 240
    assert t.clave_v1("C2", 4) == "A-C2|interurbano+metro_a"
    assert t.clave_v1("A", 4) == "A-A|metro_a+metro_a"
    fila = df.query(
        "escenario == @V and ~joven and corona == 'C2' and dias == 5 and viajes_dia == 2"
    )
    assert fila.coste_mes.item() == 45.78


def _coronas_concentricas():
    # anillos cuadrados centrados en 0: A hasta 1 km, B1 hasta 2, ..., C2 hasta 6 (EPSG:25830), y una
    # muesca de E1 que corta la franja de C2 por arriba, como un entrante de la Comunidad
    bordes = [box(-k * 1000, -k * 1000, k * 1000, k * 1000) for k in range(1, 7)]
    anillos = [bordes[0]] + [b.difference(a) for a, b in pairwise(bordes)]
    muesca = box(-1000, 5000, 1000, 6000)
    anillos[-1] = anillos[-1].difference(muesca)
    nombres = [*t.ORDEN_CORONAS, "E1"]
    return gpd.GeoDataFrame({"corona": nombres}, geometry=[*anillos, muesca], crs=25830)


def test_rango_coronas_por_la_recta_entre_centros():
    puntos = {  # (x, y) en metros
        "o_b2": (2500, 0),
        "d_c1": (4500, 500),  # B2 → C1 por fuera de A
        "op_b2": (-2500, 0),  # B2 al otro lado: la recta cruza A
        "c2_n": (-5500, 5500),  # C2 → C2 por la esquina de E1: E1 no cuenta
        "c2_e": (5500, 5500),
    }
    xy = gpd.GeoSeries([Point(p) for p in puntos.values()], crs=25830).to_crs(4326)
    zonas = gpd.GeoDataFrame(
        {
            "zona_id": list(puntos),
            "corona": ["B2", "C1", "B2", "C2", "C2"],
            "lon_centro": xy.x,
            "lat_centro": xy.y,
        }
    )
    r = t.rango_coronas(zonas, _coronas_concentricas()).set_index(
        ["zona_id", "destino_id"]
    )
    assert tuple(r.loc[("o_b2", "d_c1")]) == ("B2", "C1")
    assert tuple(r.loc[("o_b2", "op_b2")]) == ("A", "B2")
    assert tuple(r.loc[("d_c1", "d_c1")]) == ("C1", "C1")
    assert tuple(r.loc[("c2_n", "c2_e")]) == ("C2", "C2")
    assert len(r) == 25
