"""Título de transporte más barato al mes en la Comunidad de Madrid, con los precios de 2026.

Supuestos: el abono de 30 días cuenta como un mes; 4,33 semanas al mes; sin descuentos de familia
numerosa ni discapacidad; el viaje pasa por la zona A; los precios con descuento (`vigente_2026`)
dependen del RDL 17/2025, que es temporal (solo 2026); el 10 viajes se compra en paquetes enteros,
aunque en la realidad los viajes que sobran pasan al mes siguiente (decisión del equipo); el abono
anual vale 10 veces el de 30 días (referencia §1.2) y se reparte en 12 meses.
Viajes al día: 2 (ida y vuelta directa) o 4 (un transbordo en cada sentido).
"""

from decimal import ROUND_CEILING, ROUND_HALF_UP
from decimal import Decimal as D
from itertools import product

import pandas as pd

from mesobra import contratos
from mesobra.api_estatica import CORONAS as ORDEN_CORONAS

CENTIMO = D("0.01")
SEMANAS_MES = D("4.33")
DIAS = range(1, 6)
VIAJES_DIA = (2, 4)
EDAD_MIN_JOVEN = 15
EDAD_MAX_JOVEN = 25  # ficha CRTM: desde los 15 años hasta la fecha en que se cumplen 26
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
# BOCM-20251231-2 págs. 67-68 y BOCM-20251231-3 pág. 72
DIEZ_VIAJES = {
    "A": _p("7.30", "12.50"),
    "B1": _p("7.30", "12.50"),
    "B2": _p("9.60", "16.50"),
    "B3": _p("13.80", "23.60"),
    "C1": _p("17.80", "30.50"),
    "C2": _p("22.40", "38.50"),
}
# A: EMT; B1-C2: autobús interurbano. BOCM-20251231-2 pág. 68 = BOCM-20251231-3 pág. 71
# shortcut: el Metro de la zona A va de 1,50 a 2,00 € por tramos; se usa el mínimo, y no cambia
# el resultado porque el 10 viajes siempre sale más barato por viaje
SENCILLO = {
    c: _p("1.50", "1.50") if c == "A" else _p("3.00", "3.00") for c in ORDEN_CORONAS
}


def corona_necesaria(origen: str, destino: str) -> str:
    # shortcut: supone que el viaje pasa por la zona A, sin abonos interzonales; mejorar si se modelan viajes entre coronas exteriores
    return max(origen, destino, key=ORDEN_CORONAS.index)


def es_joven(edad: int) -> bool:
    return EDAD_MIN_JOVEN <= edad <= EDAD_MAX_JOVEN


def _redondea(x: D) -> D:
    return x.quantize(CENTIMO, rounding=ROUND_HALF_UP)


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
    viajes = SEMANAS_MES * dias * viajes_dia
    paquetes = (viajes / 10).to_integral_value(rounding=ROUND_CEILING)
    abono = ABONO_30[corona][escenario]
    candidatos = {
        "Billete sencillo": viajes * SENCILLO[corona][escenario],
        "10 viajes": paquetes * DIEZ_VIAJES[corona][escenario],
        "Abono 30 días": abono,
        "Abono anual": 10 * abono / 12,
    }
    if joven:
        joven_30 = ABONO_JOVEN[corona][escenario]
        candidatos |= {"Abono Joven": joven_30, "Abono Joven anual": 10 * joven_30 / 12}
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
    df = pd.DataFrame(filas, columns=list(contratos.CONTRATOS["tarifas"]["columnas"]))
    df["coste_mes"] = df["coste_mes"].astype(float)
    contratos.validar(df, "tarifas")
    return df
