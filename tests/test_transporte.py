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


@pytest.mark.parametrize("corona", ["A", "B2", "B3", "C1", "C2"])
def test_cinco_dias_es_abono(corona):
    for esc, joven in product(t.ESCENARIOS, (False, True)):
        assert "Abono" in titulo(esc, corona, 5, 2, joven=joven)[0]


def test_b1_con_cinco_dias_gana_el_10_viajes():
    assert titulo("vigente_2026", "B1", 5, 2) == (
        "10 viajes",
        D("36.50"),
    )  # frente a 38,20 del abono


def test_dias_en_los_que_deja_de_ser_10_viajes_en_zona_a():
    for dias in (1, 2, 3, 4):
        assert titulo("vigente_2026", "A", dias, 2)[0] == "10 viajes"
    assert titulo("vigente_2026", "A", 3, 2)[1] == D("21.90")
    assert titulo("vigente_2026", "A", 4, 2)[1] == D("29.20")
    assert titulo("vigente_2026", "A", 5, 2) == ("Abono 30 días", D("32.70"))
    assert titulo("vigente_2026", "C2", 5, 2) == ("Abono 30 días", D("49.20"))


def test_edad_joven():
    assert t.es_joven(15)
    assert not t.es_joven(14)
    assert t.es_joven(25)
    assert not t.es_joven(26)
    assert titulo("vigente_2026", "A", 5, 2, joven=True) == ("Abono Joven", D("10.00"))


def test_transbordo_a_precio_de_la_zona_a():
    assert titulo("vigente_2026", "A", 1, 4) == ("10 viajes", D("14.60"))
    # 1 paquete de C2 + 1 de A; los sencillos (38,97) y el abono (49,20) salen peor
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
    assert fila.coste_mes.item() == 49.20


@pytest.mark.parametrize(("dias", "viajes"), [(0, 2), (3, 3)])
def test_fuera_de_dominio(dias, viajes):
    with pytest.raises(ValueError, match="fuera de"):
        t.titulo_mas_barato(
            "vigente_2026", joven=False, corona="A", dias=dias, viajes_dia=viajes
        )
