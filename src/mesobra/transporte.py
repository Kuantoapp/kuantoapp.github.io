"""Título de transporte más barato al mes en la Comunidad de Madrid, con los precios de 2026.

Supuestos: sin descuentos de familia numerosa ni discapacidad; el viaje pasa por la zona A; los
precios con descuento (`vigente_2026`) dependen del RDL 17/2025, que es temporal (solo 2026); el 10
viajes se compra en paquetes enteros cada mes sobre los viajes medios, aunque en la realidad los que
sobran pasan al mes siguiente (decisión del equipo).
Calendario: 227 días de trabajo al año (261 laborables de 2026, menos 10 festivos en laborable, 2
locales y 22 laborables de vacaciones), es decir 3,7833 semanas al mes. El abono de 30 días se compra
335/30 veces al año: no se compra en los 30 días de vacaciones. Supuestos del calendario:
S1 30 días naturales de vacaciones son 22 laborables (el máximo; pocos días de trabajo de más);
S2 vacaciones en un solo bloque sin abono (si se parten el abono cuesta más, y favorece al abono);
S3 festivos y vacaciones repartidos por igual entre los días de la semana;
S4 los 2 locales caen en laborable (BOCM-20251212-34; en Madrid, 15-may y 9-nov; en Móstoles,
Fuenlabrada, Alcobendas o Tres Cantos uno cae en sábado: 228 días, sin cambio de título);
S5 `sin_descuento` usa también el calendario de 2026;
S6 solo viajes al trabajo, sin ocio ni fin de semana (favorece a los títulos por viaje);
S7 el 10 viajes se compra en paquetes mensuales enteros (con paquetes anuales, la zona A saldría a
27,98 €; #162);
S8 sin turnos en festivos ni teletrabajo;
S9 un mes es 1/12 del año, igual para el coste y para las horas.
Sin abono anual: el BOCM le pone precio (10 × 30 días) pero su venta a particulares está suspendida
desde 2023 (crtm.es/billetes-y-tarifas).
Viajes al día: 2 (ida y vuelta directa) o 4 (un transbordo en cada sentido); 2 viajes se cobran a
precio de la corona y los demás a precio de la zona A (el transbordo es a Metro o EMT de la zona A).
Se compra un único tipo de título al mes: no se combina el sencillo en un tramo con el 10 viajes en
el otro (sin descuento, en C1 y C2 con 1 o 2 días y 4 viajes, la combinación sería menos de 1 €/mes
más barata).
"""

from datetime import date, timedelta
from decimal import ROUND_CEILING, ROUND_HALF_UP
from decimal import Decimal as D
from itertools import product

import pandas as pd

from mesobra import contratos
from mesobra.api_estatica import CORONAS as ORDEN_CORONAS
from mesobra.api_estatica import VIAJES_DIA

CENTIMO = D("0.01")
# Decreto 75/2025, BOCM-20250925-16 pág. 103: 12 fiestas, con el 1-nov y el 6-dic trasladados al lunes
FESTIVOS_2026 = [
    date(2026, m, d)
    for m, d in (
        (1, 1), (1, 6), (4, 2), (4, 3), (5, 1), (5, 2),
        (8, 15), (10, 12), (11, 2), (12, 7), (12, 8), (12, 25),
    )
]  # fmt: skip
LABORABLES_2026 = sum(
    (date(2026, 1, 1) + timedelta(i)).weekday() < 5 for i in range(365)
)
FESTIVOS_LOCALES = 2  # ET art. 37.2: hasta 2 locales; cambian por municipio
VACACIONES = 22  # laborables; ET art. 38.1: 30 días naturales como mínimo
DIAS_TRABAJO = (
    LABORABLES_2026
    - sum(f.weekday() < 5 for f in FESTIVOS_2026)
    - FESTIVOS_LOCALES
    - VACACIONES
)
SEMANAS_MES = D(DIAS_TRABAJO) / 5 / 12
ABONOS_ANIO = D(365 - 30) / 30  # el abono no se compra en los 30 días de vacaciones
DIAS = range(1, 6)
EDAD_MIN_JOVEN = 15
# ficha CRTM: desde los 15 años hasta la fecha en que se cumplen 26
# https://www.crtm.es/billetes-y-tarifas/buscador/abono-joven/
EDAD_MAX_JOVEN = 25
ESCENARIOS = ("vigente_2026", "sin_descuento")


def _p(vigente: str, oficial: str) -> dict[str, D]:
    return {"vigente_2026": D(vigente), "sin_descuento": D(oficial)}


# BOCM-20251231-2 pág. 66 y BOCM-20251231-3 pág. 70
ABONO_30 = {
    "A": _p("32.70", "56.20"),
    "B1": _p("38.20", "65.60"),
    "B2": _p("43.20", "74.10"),
    "B3": _p("49.20", "84.40"),
    "C1": _p("49.20", "84.40"),
    "C2": _p("49.20", "84.40"),
}
# mismas páginas, todas las zonas
ABONO_JOVEN = {c: _p("10.00", "20.00") for c in ORDEN_CORONAS}
# A: Metro zona A, EMT y ML1; B1-C2: autobús interurbano del par A-corona
# BOCM-20251231-2 pág. 67 y BOCM-20251231-3 pág. 72
DIEZ_VIAJES = {
    "A": _p("7.30", "12.50"),
    "B1": _p("7.30", "12.50"),
    "B2": _p("9.60", "16.50"),
    "B3": _p("13.80", "23.60"),
    "C1": _p("17.80", "30.50"),
    "C2": _p("22.40", "38.50"),
}
# A: EMT; B1-C2: autobús interurbano. BOCM-20251231-2 pág. 68 = BOCM-20251231-3 pág. 71
# shortcut: el Metro de la zona A va de 1,50 a 2,00 € por tramos y se usa el mínimo; no cambia el
# resultado en la zona A porque su 10 viajes sale a 0,73 o 1,25 € por viaje
SENCILLO = {
    c: _p("1.50", "1.50") if c == "A" else _p("3.00", "3.00") for c in ORDEN_CORONAS
}


def corona_necesaria(origen: str, destino: str) -> str:
    # shortcut: supone que el viaje pasa por la zona A, sin abonos interzonales; mejorar si se modelan viajes entre coronas exteriores
    return max(origen, destino, key=ORDEN_CORONAS.index)


def es_joven(edad: int) -> bool:
    # menores de 15 no se modelan: el abono de 7 a 14 años es gratuito (BOCM-20251231-2 pág. 66)
    return EDAD_MIN_JOVEN <= edad <= EDAD_MAX_JOVEN


def _redondea(x: D) -> D:
    return x.quantize(CENTIMO, rounding=ROUND_HALF_UP)


def _paquetes(viajes: D) -> D:
    return (viajes / 10).to_integral_value(rounding=ROUND_CEILING)


def titulo_mas_barato(
    escenario: str, *, joven: bool, corona: str, dias: int, viajes_dia: int
) -> tuple[str, D]:
    """Título y coste mensual del más barato; en un empate gana el de menor compromiso."""
    if dias not in DIAS or viajes_dia not in VIAJES_DIA:
        raise ValueError(
            f"dias {dias} o viajes_dia {viajes_dia} fuera de {DIAS} y {VIAJES_DIA}"
        )
    if corona not in ORDEN_CORONAS or escenario not in ESCENARIOS:
        raise ValueError(f"corona {corona!r} o escenario {escenario!r} desconocidos")
    v = SEMANAS_MES * dias * 2
    e = SEMANAS_MES * dias * (viajes_dia - 2)
    abono = ABONO_30[corona][escenario] * ABONOS_ANIO / 12
    candidatos = {
        "Billete sencillo": v * SENCILLO[corona][escenario]
        + e * SENCILLO["A"][escenario],
        "10 viajes": _paquetes(v) * DIEZ_VIAJES[corona][escenario]
        + _paquetes(e) * DIEZ_VIAJES["A"][escenario],
        "Abono 30 días": abono,
    }
    if joven:
        candidatos["Abono Joven"] = ABONO_JOVEN[corona][escenario] * ABONOS_ANIO / 12
    titulo = min(candidatos, key=candidatos.get)
    return titulo, _redondea(candidatos[titulo])


def tabla() -> pd.DataFrame:
    """Tabla `tarifas`: escenario x joven x corona x días x viajes al día, validada con su contrato."""
    filas = [
        (
            esc,
            joven,
            corona,
            dias,
            viajes,
            *titulo_mas_barato(
                esc, joven=joven, corona=corona, dias=dias, viajes_dia=viajes
            ),
        )
        for esc, joven, corona, dias, viajes in product(
            ESCENARIOS, (False, True), ORDEN_CORONAS, DIAS, VIAJES_DIA
        )
    ]
    df = pd.DataFrame(
        filas,
        columns=[
            "escenario",
            "joven",
            "corona",
            "dias",
            "viajes_dia",
            "titulo",
            "coste_mes",
        ],
    )
    df["coste_mes"] = df["coste_mes"].astype(float)
    contratos.validar(df, "tarifas")
    return df
