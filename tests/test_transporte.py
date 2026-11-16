from decimal import Decimal as D
from itertools import product

import pytest

from mesobra import transporte as t


def test_precios_de_control():
    vigente, oficial = "vigente_2026", "sin_descuento"
    assert (t.ABONO_30["A"][vigente], t.ABONO_30["C2"][vigente]) == (
        D("32.70"),
        D("49.20"),
    )
    assert (t.ABONO_30["A"][oficial], t.ABONO_30["C2"][oficial]) == (
        D("56.20"),
        D("84.40"),
    )
    assert t.ABONO_JOVEN["A"] == {vigente: D("10.00"), oficial: D("20.00")}


def titulo(esc, corona, dias, viajes, *, joven=False):
    return t.titulo_mas_barato(
        esc, joven=joven, corona=corona, dias=dias, viajes_dia=viajes
    )


def test_precios_de_10_viajes_y_sencillo():
    assert (
        t.DIEZ_VIAJES["A"]["vigente_2026"],
        t.DIEZ_VIAJES["A"]["sin_descuento"],
    ) == (D("7.30"), D("12.50"))
    assert (
        t.DIEZ_VIAJES["C2"]["vigente_2026"],
        t.DIEZ_VIAJES["C2"]["sin_descuento"],
    ) == (D("22.40"), D("38.50"))
    assert t.SENCILLO["A"]["vigente_2026"] == D("1.50")
    assert t.SENCILLO["C2"]["sin_descuento"] == D("3.00")


def test_calendario_laboral_de_2026():
    # 261 laborables - 10 festivos en laborable - 2 locales - 22 de vacaciones
    assert sum(f.weekday() < 5 for f in t.FESTIVOS_2026) == 10
    assert (t.LABORABLES_2026, t.DIAS_TRABAJO) == (261, 227)
    assert {(f.month, f.day) for f in t.FESTIVOS_2026 if f.weekday() >= 5} == {
        (5, 2),
        (8, 15),
    }


@pytest.mark.parametrize(
    ("dias_trabajo", "esperado"),
    [
        (
            228,
            ("10 viajes", D("29.20")),
        ),  # S4: un local en sábado, 38 viajes, 4 paquetes
        (240, ("10 viajes", D("29.20"))),  # 40 viajes, 4 paquetes
        (241, ("Abono 30 días", D("30.43"))),  # 40,17 viajes, 5 paquetes (36,50)
    ],
)
def test_umbral_del_10_viajes_en_zona_a(monkeypatch, dias_trabajo, esperado):
    monkeypatch.setattr(t, "SEMANAS_MES", D(dias_trabajo) / 5 / 12)
    assert titulo("vigente_2026", "A", 5, 2) == esperado


def test_joven_al_borde_en_b2_con_un_dia():
    # 10 × 335/360 = 9,31 frente a un paquete de B2 a 9,60
    assert titulo("vigente_2026", "B2", 1, 2, joven=True) == ("Abono Joven", D("9.31"))


def test_abono_de_la_zona_a_con_335_entre_30_al_anio():
    # 32,70 × 335/30 / 12 = 30,429 €/mes; con 3 días y 4 viajes gana el abono
    assert titulo("vigente_2026", "A", 3, 4) == ("Abono 30 días", D("30.43"))


@pytest.mark.parametrize("corona", ["B3", "C1", "C2"])
def test_cinco_dias_es_abono(corona):
    for esc, joven in product(t.ESCENARIOS, (False, True)):
        assert "Abono" in titulo(esc, corona, 5, 2, joven=joven)[0]


def test_b1_con_cinco_dias_gana_el_10_viajes():
    assert titulo("vigente_2026", "B1", 5, 2) == (
        "10 viajes",
        D("29.20"),
    )  # 3,7833 × 10 = 37,8 viajes, 4 paquetes × 7,30; el abono sale a 35,55


def test_zona_a_con_2_viajes_siempre_es_10_viajes():
    for dias in (1, 2, 3, 4, 5):
        assert titulo("vigente_2026", "A", dias, 2)[0] == "10 viajes"
    assert titulo("vigente_2026", "A", 3, 2)[1] == D("21.90")
    assert titulo("vigente_2026", "A", 4, 2)[1] == D("29.20")
    assert titulo("vigente_2026", "C2", 5, 2) == ("Abono 30 días", D("45.78"))


def test_cinco_dias_en_zona_a_y_b2_gana_el_10_viajes():
    # A: 37,8 viajes, 4 paquetes × 7,30 = 29,20 frente a 30,43 del abono
    assert titulo("vigente_2026", "A", 5, 2) == ("10 viajes", D("29.20"))
    # B2: 4 × 9,60 = 38,40 frente a 40,20 del abono
    assert titulo("vigente_2026", "B2", 5, 2) == ("10 viajes", D("38.40"))


def test_edad_joven():
    assert t.es_joven(15)
    assert not t.es_joven(14)
    assert t.es_joven(25)
    assert not t.es_joven(26)
    assert titulo("vigente_2026", "A", 5, 2, joven=True) == ("Abono Joven", D("9.31"))


def test_transbordo_a_precio_de_la_zona_a():
    assert titulo("vigente_2026", "A", 1, 4) == ("10 viajes", D("14.60"))
    # 1 paquete de C2 + 1 de A; los sencillos (34,05) y el abono (45,78) salen peor
    assert titulo("vigente_2026", "C2", 1, 4) == ("10 viajes", D("29.70"))


def test_corona_necesaria():
    assert t.corona_necesaria("A", "C1") == "C1"
    assert t.corona_necesaria("B2", "B1") == "B2"


def test_cuatro_viajes_no_cuestan_menos():
    for esc, joven, corona, dias in product(
        t.ESCENARIOS, (False, True), t.ORDEN_CORONAS, t.DIAS
    ):
        dos = t.titulo_mas_barato(
            esc, joven=joven, corona=corona, dias=dias, viajes_dia=2
        )[1]
        assert (
            t.titulo_mas_barato(
                esc, joven=joven, corona=corona, dias=dias, viajes_dia=4
            )[1]
            >= dos
        )


def test_tabla():
    df = t.tabla()
    assert len(df) == 240
    fila = df[
        (df.escenario == "vigente_2026")
        & ~df.joven
        & (df.corona == "C2")
        & (df.dias == 5)
        & (df.viajes_dia == 2)
    ]
    assert fila.coste_mes.item() == 45.78


@pytest.mark.parametrize(("dias", "viajes"), [(0, 2), (3, 3)])
def test_fuera_de_dominio(dias, viajes):
    with pytest.raises(ValueError, match="fuera de"):
        t.titulo_mas_barato(
            "vigente_2026", joven=False, corona="A", dias=dias, viajes_dia=viajes
        )
