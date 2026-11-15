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


def test_cinco_dias_es_abono():
    for esc, joven, corona in product(t.ESCENARIOS, (False, True), t.ORDEN_CORONAS):
        assert (
            "Abono"
            in t.titulo_mas_barato(
                esc, joven=joven, corona=corona, dias=5, viajes_dia=2
            )[0]
        )


def test_dias_en_los_que_deja_de_ser_abono_en_zona_a():
    for dias in (1, 2, 3):
        assert (
            t.titulo_mas_barato(
                "vigente_2026", joven=False, corona="A", dias=dias, viajes_dia=2
            )[0]
            == "10 viajes"
        )
    assert t.titulo_mas_barato(
        "vigente_2026", joven=False, corona="A", dias=3, viajes_dia=2
    )[1] == D("21.90")
    for dias in (4, 5):
        assert t.titulo_mas_barato(
            "vigente_2026", joven=False, corona="A", dias=dias, viajes_dia=2
        ) == (
            "Abono anual",
            D("27.25"),
        )


def test_edad_joven():
    assert t.es_joven(25)
    assert not t.es_joven(26)
    assert t.titulo_mas_barato(
        "vigente_2026", joven=True, corona="A", dias=5, viajes_dia=2
    )[0].startswith("Abono Joven")


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
    assert fila.coste_mes.item() == 41.00


@pytest.mark.parametrize(("dias", "viajes"), [(0, 2), (3, 3)])
def test_fuera_de_dominio(dias, viajes):
    with pytest.raises(ValueError, match="fuera de"):
        t.titulo_mas_barato(
            "vigente_2026", joven=False, corona="A", dias=dias, viajes_dia=viajes
        )
