"""Neto anual desde el bruto anual con los parámetros de 2026 (Comunidad de Madrid).

`cuota_irpf` es la cuota anual de la declaración de 2026, no la retención de la nómina.
Supuestos: sin deducciones reembolsables (arts. 81 y 81 bis LIRPF) ni autonómicas, así que
neto <= bruto (lo exige `_netos` de `api_estatica`); sin el art. 81 bis el neto de un monoparental
con dos hijos queda hasta 1.200 €/año por debajo del real (la app debe decirlo); tributación individual; menor de 65 años;
contrato indefinido; hijos de 3 a 24 años; sin otras rentas; bajo el SMI se supone jornada parcial y
se cotiza por el bruto, sin base mínima; el mínimo por descendientes se prorratea (1/2 cada uno si
no es monoparental, entero si lo es: convivencia solo con este progenitor, sin custodia compartida);
el art. 20 se calcula antes de los 2.000 € del art. 19.2.f; cada concepto se redondea al céntimo; quien no está obligado a declarar paga la retención, no la cuota.
La rejilla va cada 250 € y cada 50 € entre 16.500 y 21.500 € (quiebros del art. 20 y de la DA 61.ª),
para que la interpolación lineal se aparte menos de 1 €/mes.
"""

from decimal import ROUND_HALF_UP
from decimal import Decimal as D
from itertools import product

import pandas as pd

from mesobra import contratos
from mesobra import parametros_2026 as p

CENTIMO = D("0.01")
MESES = 12
PAGAS = (12, 14)
HIJOS = (0, 1, 2)
BRUTOS = sorted({*range(12_000, 120_001, 250), *range(16_500, 21_501, 50)})


def _redondea(x: D) -> D:
    return x.quantize(CENTIMO, rounding=ROUND_HALF_UP)


def cotizacion(bruto: D) -> D:
    """Cotización anual del trabajador: tipo común hasta la base máxima y solidaridad por tramos."""
    mensual = bruto / MESES
    techos = [desde for desde, _ in p.SOLIDARIDAD[1:]] + [mensual]
    solidaridad = sum(
        (
            (min(mensual, techo) - desde) * tipo
            for (desde, tipo), techo in zip(p.SOLIDARIDAD, techos, strict=True)
            if mensual > desde
        ),
        D(0),
    )
    # cada concepto se redondea por separado, como se liquida (criterio del auditor en #79)
    return _redondea(
        p.TIPO_COTIZACION * min(bruto, p.BASE_MAXIMA_MES * MESES)
    ) + _redondea(solidaridad * MESES)


def _reduccion_art20(rnt: D) -> D:
    if rnt <= p.RED20_UMBRAL_1:
        red = p.RED20_FIJA
    elif rnt <= p.RED20_UMBRAL_2:
        red = p.RED20_FIJA - p.RED20_PENDIENTE_1 * (rnt - p.RED20_UMBRAL_1)
    elif rnt < p.RED20_UMBRAL_3:
        red = p.RED20_TRAMO_2 - p.RED20_PENDIENTE_2 * (rnt - p.RED20_UMBRAL_2)
    else:
        red = D(0)
    return red.quantize(CENTIMO, rounding=ROUND_HALF_UP)


def _escala(base: D, tramos) -> D:
    desde, acumulada, tipo = max(t for t in tramos if t[0] <= base)
    return acumulada + (base - desde) * tipo


def _cuota(base: D, minimo: D, tramos) -> D:
    # cuota íntegra estatal y autonómica al céntimo, cada una en su casilla del Modelo 100
    return _redondea(
        max(_escala(base, tramos) - _escala(min(minimo, base), tramos), D(0))
    )


def _minimo(contribuyente: D, descendientes: tuple[D, ...], hijos: int, factor: D) -> D:
    return contribuyente + factor * sum(descendientes[:hijos], D(0))


def cuota_irpf(bruto: D, cotiza: D, *, hijos: int, monoparental: bool) -> D:
    """Cuota anual de IRPF (estatal + Madrid) tras la deducción por SMI, redondeada al céntimo."""
    # el art. 20 se calcula sobre bruto − cotizaciones, sin los 2.000 € del art. 19.2.f (art. 20, último párrafo)
    rnt = max(bruto - cotiza, D(0))
    base = max(rnt - min(p.GASTOS_OTROS, rnt) - _reduccion_art20(rnt), D(0))
    factor = D(1) if monoparental else D("0.5")
    estatal = _cuota(
        base,
        _minimo(p.MINIMO_ESTATAL, p.DESCENDIENTES_ESTATAL, hijos, factor),
        p.ESCALA_ESTATAL,
    )
    madrid = _cuota(
        base,
        _minimo(p.MINIMO_MADRID, p.DESCENDIENTES_MADRID, hijos, factor),
        p.ESCALA_MADRID,
    )
    integra = estatal + madrid
    return _redondea(integra - min(deduccion_smi(bruto), integra))


def deduccion_smi(bruto: D) -> D:
    """Deducción de la DA 61.ª LIRPF antes de limitarla a la cuota íntegra."""
    if bruto >= p.DEDUCCION_SMI_LIMITE:  # «inferiores a» 20.048,45 €
        return D(0)
    return p.DEDUCCION_SMI - p.DEDUCCION_SMI_PENDIENTE * max(bruto - p.SMI_ANUAL, D(0))


def neto_anual(bruto, *, hijos: int, monoparental: bool) -> D:
    """Neto anual en € (Decimal) de un bruto anual, tributación individual."""
    if hijos not in HIJOS:
        raise ValueError(f"hijos debe estar en {HIJOS}, no {hijos}")
    bruto = D(bruto)
    if bruto <= 0:
        raise ValueError(f"el bruto debe ser positivo, no {bruto}")
    cotiza = cotizacion(bruto)
    return (
        bruto
        - cotiza
        - cuota_irpf(bruto, cotiza, hijos=hijos, monoparental=monoparental)
    )


def neto_mensual(bruto, pagas: int, *, hijos: int, monoparental: bool) -> D:
    """Neto mensual en € con 12 o 14 pagas (el prorrateo no cambia el neto anual)."""
    if pagas not in PAGAS:
        raise ValueError(f"pagas debe estar en {PAGAS}, no {pagas}")
    return _redondea(neto_anual(bruto, hijos=hijos, monoparental=monoparental) / pagas)


def rejilla() -> pd.DataFrame:
    """Tabla `netos`: bruto de la rejilla x 6 configuraciones, validada con su contrato."""
    filas = []
    for bruto, hijos, mono in product(BRUTOS, HIJOS, (False, True)):
        cotiza = cotizacion(D(bruto))
        cuota = cuota_irpf(D(bruto), cotiza, hijos=hijos, monoparental=mono)
        neto = D(bruto) - cotiza - cuota
        filas.append((bruto, hijos, mono, float(cotiza), float(cuota), float(neto)))
    df = pd.DataFrame(filas, columns=list(contratos.CONTRATOS["netos"]["columnas"]))
    contratos.validar(df, "netos")
    return df
