"""Tests de `mesobra.neto`: parámetros, límites y propiedades de la rejilla."""

from decimal import Decimal as D

import numpy as np
import pytest

from mesobra import neto
from mesobra import parametros_2026 as p

CONFIGS = [(h, m) for h in neto.HIJOS for m in (False, True)]


@pytest.fixture(scope="module")
def netos():
    return neto.rejilla()


def test_cotizacion_de_control():
    assert neto.cotizacion(D(30000)) == D("1950.00")


def test_smi_anual():
    assert p.SMI_ANUAL == 17094


def test_base_maxima_y_solidaridad():
    tope = p.BASE_MAXIMA_MES * 12
    assert neto.cotizacion(tope) == D("3978.94")  # 6,5 % de 61.214,40 sin solidaridad
    # +100 €/mes sobre el tope: la base no crece, suma 100 × 0,19 % × 12 = 2,28 €
    assert neto.cotizacion(tope + 1200) == D("3981.22")


@pytest.mark.parametrize(
    ("rnt", "esperada"),
    [
        (p.RED20_UMBRAL_1, p.RED20_FIJA),
        (p.RED20_UMBRAL_2, p.RED20_TRAMO_2),
        (p.RED20_UMBRAL_3, D(0)),
    ],
)
def test_umbrales_art20(rnt, esperada):
    assert neto._reduccion_art20(rnt) == esperada
    assert neto._reduccion_art20(rnt - D("0.01")) == pytest.approx(
        esperada, abs=D("0.03")
    )


def test_cero_hijos_monoparental_igual():
    assert neto.neto_anual(30000, hijos=0, monoparental=True) == neto.neto_anual(
        30000, hijos=0, monoparental=False
    )


@pytest.mark.parametrize("hijos", [-1, 3])
def test_hijos_fuera_de_rango(hijos):
    with pytest.raises(ValueError, match="hijos"):
        neto.cuota_irpf(D(30000), D(1950), hijos=hijos, monoparental=False)


def test_bruto_float_sin_imprecision():
    assert neto.neto_anual(30000.1, hijos=0, monoparental=False) == neto.neto_anual(
        "30000.10", hijos=0, monoparental=False
    )


def test_pagas_invalidas():
    with pytest.raises(ValueError, match="pagas"):
        neto.neto_mensual(30000, 13, hijos=0, monoparental=False)
    assert neto.neto_mensual(30000, 14, hijos=0, monoparental=False) == D("1675.14")


def test_rejilla_propiedades(netos):
    assert len(netos) == len(neto.BRUTOS) * 6
    assert (netos.bruto_anual.min(), netos.bruto_anual.max()) == (12_000, 120_000)
    assert ((netos.neto_anual > 0) & (netos.neto_anual <= netos.bruto_anual)).all()
    for _, g in netos.groupby(["hijos", "monoparental"]):
        assert g.sort_values("bruto_anual").neto_anual.diff().dropna().gt(0).all()


def test_interpolacion_lineal_menos_de_un_euro_al_mes(netos):
    puntos = range(12_000, 120_000, 10)
    for (h, m), g in netos.groupby(["hijos", "monoparental"]):
        lineal = np.interp(puntos, g.bruto_anual, g.neto_anual)
        exacto = [float(neto.neto_anual(b, hijos=h, monoparental=m)) for b in puntos]
        assert np.abs(lineal - exacto).max() / 12 < 1, (h, m)


# Casos de control calculados de forma independiente por dm-auditor-calculos-normativos
# el 15/11/2026 a mano con Decimal sobre el texto consolidado del BOE (LIRPF arts. 19, 20, 56,
# 57, 58, 61, 63, DA 61.ª; DL 1/2010 Madrid arts. 1, 2, 2 bis; Orden PJC/297/2026 arts. 2, 4,
# 16, 17, 33), cada concepto redondeado al céntimo. No contrastados con Renta Web.
@pytest.mark.parametrize(
    ("caso", "esperado"),
    [
        (
            (17094, 0, False),
            ("1111.11", "0.00", "15982.89"),
        ),  # DA 61.ª limitada a la cuota
        ((19000, 2, True), ("1235.00", "267.38", "17497.62")),  # tramo 2.º del art. 20
        ((30000, 0, False), ("1950.00", "4598.02", "23451.98")),
        (
            (80000, 1, False),
            ("4017.17", "21906.75", "54076.08"),
        ),  # base máxima + solidaridad
    ],
)
def test_casos_del_auditor(caso, esperado):
    bruto, hijos, mono = caso
    c = neto.cotizacion(D(bruto))
    cuota = neto.cuota_irpf(D(bruto), c, hijos=hijos, monoparental=mono)
    total = neto.neto_anual(bruto, hijos=hijos, monoparental=mono)
    assert (c, cuota, total) == tuple(D(x) for x in esperado)


@pytest.mark.parametrize(
    ("bruto", "esperada"),
    [
        ("17094", "590.89"),
        ("17094.01", "590.89"),
        ("20048.44", "0.00"),
        ("20048.45", "0"),
    ],
)
def test_umbrales_deduccion_smi(bruto, esperada):
    assert neto.deduccion_smi(D(bruto)) == D(esperada)


@pytest.mark.parametrize(
    ("mensual", "solidaridad_mes"),
    [
        ("5101.20", "0"),
        ("5611.32", "0.969228"),
        ("7651.80", "5.254236"),
        ("8651.80", "7.654236"),
    ],
)
def test_tramos_solidaridad(mensual, solidaridad_mes):
    # Orden PJC/297/2026, art. 17.1: 0,19 % hasta 5.611,32; 0,21 % hasta 7.651,80; 0,24 % después
    bruto = D(mensual) * 12
    ordinaria = (p.TIPO_COTIZACION * p.BASE_MAXIMA_MES * 12).quantize(D("0.01"))
    assert neto.cotizacion(bruto) - ordinaria == (D(solidaridad_mes) * 12).quantize(
        D("0.01")
    )


# Casos oficiales de la AEAT, Manual práctico de Renta 2024 y 2025 (consultados el 15/11/2026), en
# https://sede.agenciatributaria.gob.es/Sede/ayuda/manuales-videos-folletos/manuales-practicos/. Ninguno
# parte solo de rendimientos del trabajo de 2026, así que contrastan cada pieza por separado; la escala
# estatal, la de Madrid y el art. 20 no cambian de 2024 a 2026. No contrastan la cotización ni la DA 61.ª.
def test_aeat_cuota_estatal():
    """Fuente: AEAT, manuales-practicos/irpf-2024/c15-…/ejemplo-practico-calculo-cuotas-integras-autonomica."""
    # base liquidable general 23.900 y mínimo 5.550: cuota íntegra general estatal 2.140,50
    assert neto._escala(D(23900), p.ESCALA_ESTATAL) == D("2667.75")
    assert neto._cuota(D(23900), D(5550), p.ESCALA_ESTATAL) == D("2140.50")


def test_aeat_escala_madrid():
    """Fuente: AEAT, manuales-practicos/irpf-2024/c15-…/supuestos-especiales-concurrencia-rentas."""
    # Madrid: 24.050 → 2.385,33 y 7.757,55 → 659,39. La AEAT trunca el parcial (645,807 → 645,80),
    # de ahí la tolerancia de un céntimo. Su mínimo autonómico (5.777,55) es el de 2022: el DL 1/2010,
    # art. 2.a, fija 5.956,65 desde 2023 (Ley 13/2023), así que solo se contrasta la escala.
    assert abs(neto._escala(D(24050), p.ESCALA_MADRID) - D("2385.33")) <= D("0.01")
    assert neto._redondea(neto._escala(D("7757.55"), p.ESCALA_MADRID)) == D("659.39")


def test_aeat_reduccion_art20():
    """Fuente: AEAT, manuales-practicos/irpf-2025/c03-rendimientos-trabajo/caso-practico."""
    # rendimiento neto previo 13.640 → 7.302
    # Aquí da 7.302 con los 2.000 € antes o después: el orden (sin los 2.000 €, art. 20 último párrafo)
    # lo comprueba el caso del auditor de 17.094 €, que con el orden cambiado daría 7.302 y no 5.322,94.
    assert neto._reduccion_art20(D(13640)) == D(7302)
