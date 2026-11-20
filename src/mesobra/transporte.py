"""Título de transporte más barato al mes en la Comunidad de Madrid por la ruta real, con los precios de 2026.

La ruta se resume en una `clave_tarifa`: el rango de coronas que atraviesa y un producto por validación
(«B2-C1|interurbano», «A-C2|interurbano+metro_a»). Con ella se compara el abono que cubre el rango
(normal si entra en A, interzonal si no) con el sencillo o el 10 viajes de cada producto, más el Abono
Joven (15 a 25 años) y el Abono +65 (gratuito). Cada título tiene su precio por colectivo (#163):
ordinario, discapacidad igual o superior al 65 %, familia numerosa general o especial, y las dos con
discapacidad; se toma la columna del BOCM, no un porcentaje, porque el BOCM redondea a 0,10 € (sencillo
de 1,50 € para FN especial: 0,70 €). La discapacidad del 33 al 64 % no tiene columna y no se modela.
Familia monoparental: sin descuento del CRTM en 2026 (no figura en el BOCM y el decreto de Madrid de 2020
se archivó); desde el 1-1-2027 el RDL 35/2026 (BOE-A-2026-23604) hace numerosa a la familia con una sola
persona progenitora y dos hijos (nuevo art. 2.2.c de la Ley 40/2003). Con 2 hijos, en 2026 la familia es
numerosa si un hijo tiene discapacidad o incapacidad para trabajar, si los dos progenitores la tienen (o
uno con al menos el 65 %), si falleció el otro progenitor o si son hermanos huérfanos (Ley 40/2003, art.
2.2); es general salvo que los dos hijos tengan discapacidad, que cuentan como 4 (art. 4.3) y la hacen
especial con renta por miembro de hasta el 75 % del SMI (art. 4.2). Quién pertenece a qué colectivo lo
decide quien usa la tabla.
Los precios con descuento (`vigente_2026`) dependen del RDL 17/2025, que es temporal (solo 2026); el 10
viajes se prorratea (viajes ÷ 10 × precio), porque no caduca: la ficha
del CRTM dice «Validez: Ilimitada» (https://www.crtm.es/billetes-y-tarifas/buscador/sencillos-y-10-viajes/,
consultada el 18-11-2026; #162 sustituye a los paquetes enteros de #80).
Cercanías: vale el abono del CRTM de la corona, o el Abono mensual de Renfe (RDL 17/2025, art. 3.2.a).2.º:
20 €, todos los núcleos con tarificación zonal, solo 2026); sin descuento no hay precio publicado de Renfe y
solo cuenta el abono del CRTM. Los jóvenes nacidos de 2000 a 2011 tienen uno de 10 € (art. 3.2.a).3.º), que
se aplica a todo el colectivo joven (15 a 25 años) porque nació en esos años. Supuestos: quien nació en 2000
y ya cumplió 26 cuenta como general y no recibe los 10 € (se sobrestima su coste en Cercanías); se supone
nacionalidad española o residencia legal; Madrid es núcleo con tarificación zonal. Los 20 € valen para todos
los colectivos: según Renfe (preguntas frecuentes de los abonos bonificados, consultadas el 18-11-2026) admite
el descuento de familia numerosa pero no publica su importe (cota superior para FN) y no tiene descuento por
discapacidad. El Bonotren
va por zonas de Renfe, que no son las coronas, y no se modela.
Abono +65 desde los 65 años: el CRTM escribe «más de 65 años» y ninguna norma fija si basta con 65
cumplidos (verificar).
Viajes al mes por producto = 2 × días × semanas al mes por cada validación; los viajes no laborables
(ocio y fin de semana: 0, 8 o 16 al mes, #162) se suman al producto principal de la ruta (el interurbano
si lo hay): se supone que el ocio sigue la ruta del trabajo, lo que encarece los títulos por viaje en las
rutas largas y favorece al abono. En el mes de vacaciones sin abono, ese ocio se paga por viaje. Cada producto se paga con su sencillo o su 10 viajes, el más barato; el abono o el Abono
Joven, frente a la suma.
Calendario: 227 días de trabajo al año (261 laborables de 2026, menos 10 festivos en laborable, 2
locales y 22 laborables de vacaciones), es decir 3,7833 semanas al mes. El abono de 30 días se compra
335/30 veces al año: no se compra en los 30 días de vacaciones. Supuestos del calendario:
S1 30 días naturales de vacaciones son 22 laborables (el máximo posible: 20 a 22, media 21,43);
S2 vacaciones en un solo bloque sin abono (si se parten el abono cuesta más, y favorece al abono);
S3 festivos y vacaciones repartidos por igual entre los días de la semana;
S4 los 2 locales caen en laborable (BOCM-20251212-34; en Madrid, 15-may y 9-nov; en Móstoles,
Fuenlabrada, Alcobendas o Tres Cantos uno cae en sábado: 228 días, sin cambio de título);
S5 `sin_descuento` usa también el calendario de 2026;
S8 sin turnos en festivos ni teletrabajo;
S9 un mes es 1/12 del año, igual para el coste y para las horas;
S10 335/30 abonos es la media continua y una cota inferior: 11 abonos enteros más el resto de días
cuestan de 0 a 0,2 €/mes más (zona A: 30,58 frente a 30,43); el sesgo va contra el 10 viajes.
Sin abono anual: el BOCM le pone precio (10 × 30 días) pero su venta a particulares está suspendida
desde 2023 (crtm.es/billetes-y-tarifas).
"""

from datetime import date, timedelta
from decimal import ROUND_HALF_UP
from decimal import Decimal as D
from itertools import product

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from mesobra import contratos
from mesobra.api_estatica import COLECTIVOS, EDADES, NO_LABORABLES, VIAJES_DIA
from mesobra.api_estatica import CORONAS as ORDEN_CORONAS

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
# Sistemas de una ruta (#161 los toma de aquí) y producto con el que se paga cada uno
SISTEMAS = ("cercanias", "emt", "interurbano", "metro", "metro_ligero", "urbano")
# en orden de prioridad: el primero de una ruta es su producto principal
PRODUCTOS = (
    "interurbano", "cercanias", "combinado", "metro_b", "tfm_mlo", "metro_a", "urbano",
)  # fmt: skip


def _p(vigente: str, oficial: str) -> dict[tuple[str, str], D]:
    """Precio por tarifa (escenario, colectivo): las 6 columnas del BOCM en el orden de COLECTIVOS."""
    columnas = {"vigente_2026": vigente.split(), "sin_descuento": oficial.split()}
    if any(len(c) != len(COLECTIVOS) for c in columnas.values()):
        raise ValueError(f"se esperaban {len(COLECTIVOS)} columnas: {columnas}")
    return {
        (esc, col): D(x)
        for esc, fila in columnas.items()
        for col, x in zip(COLECTIVOS, fila)
    }


# BOCM-20251231-2 pág. 66 y BOCM-20251231-3 pág. 70; columnas en el orden de COLECTIVOS
ABONO_30 = {
    "A": _p("32.70 26.10 26.10 16.30 19.60 9.70", "56.20 44.90 44.90 28.10 33.70 16.80"),
    "B1": _p("38.20 30.50 30.50 19.00 22.90 11.40", "65.60 52.40 52.40 32.80 39.30 19.60"),
    "B2": _p("43.20 34.50 34.50 21.60 25.90 12.90", "74.10 59.20 59.20 37.00 44.40 22.20"),
    "B3": _p("49.20 39.30 39.30 24.60 29.50 14.70", "84.40 67.50 67.50 42.20 50.60 25.30"),
    "C1": _p("49.20 39.30 39.30 24.60 29.50 14.70", "84.40 67.50 67.50 42.20 50.60 25.30"),
    "C2": _p("49.20 39.30 39.30 24.60 29.50 14.70", "84.40 67.50 67.50 42.20 50.60 25.30"),
}  # fmt: skip
# mismas páginas: abonos interzonales, sin pasar por la zona A
ABONO_INTERZONAL = {
    **dict.fromkeys(
        [("B1", "B2"), ("B2", "B3"), ("B2", "C1"), ("B2", "C2"), ("B3", "C1"), ("B3", "C2"), ("C1", "C2")],
        _p("28.70 22.90 22.90 14.30 17.20 8.50", "49.30 39.40 39.40 24.60 29.50 14.70"),
    ),
    **dict.fromkeys(
        [("B1", "B3"), ("B1", "C1"), ("B1", "C2")],
        _p("32.70 26.10 26.10 16.30 19.60 9.70", "56.20 44.90 44.90 28.10 33.70 16.80"),
    ),
}  # fmt: skip
# abono que cubre de la primera corona a la segunda: el normal de A a c, o el interzonal
ABONOS = {("A", c): p for c, p in ABONO_30.items()} | ABONO_INTERZONAL
# mismas páginas, todas las zonas
ABONO_JOVEN = _p("10.00 8.00 8.00 5.00 6.00 3.00", "20.00 16.00 16.00 10.00 12.00 6.00")
# gratuito, 365 días (BOCM-20251231-2 pág. 66; -3 pág. 70); «hasta la zona C2», que cubre todas las coronas
# de las zonas: https://www.crtm.es/billetes-y-tarifas/buscador/abono-plus65/ (consultada el 18-11-2026)
# «Tercera edad: Gratuita» en BOCM-20251231-3 pág. 70
ABONO_65 = _p("0 0 0 0 0 0", "0 0 0 0 0 0")
# BOCM-20251231-2 pág. 67 y BOCM-20251231-3 pág. 72
UNA_ZONA = _p("5.10 4.00 4.00 2.50 3.00 1.50", "8.70 6.90 6.90 4.30 5.20 2.60")
DIEZ_VIAJES = {
    # Metro zona A, EMT y ML1
    "metro_a": _p("7.30 5.80 5.80 3.60 4.30 2.10", "12.50 10.00 10.00 6.20 7.50 3.70"),
    # MetroEste, MetroNorte y MetroSur
    "metro_b": _p("6.70 5.30 5.30 3.30 4.00 1.90", "11.50 9.20 9.20 5.70 6.90 3.40"),
    # TFM y Metro Ligero Oeste
    "tfm_mlo": _p("7.30 5.80 5.80 3.60 4.30 2.10", "12.50 10.00 10.00 6.20 7.50 3.70"),
    # Metro de la zona A y de la B
    "combinado": _p("10.90 8.70 8.70 5.40 6.50 3.20", "18.80 15.00 15.00 9.40 11.20 5.60"),
    "urbano": UNA_ZONA,  # fila de una sola zona; dentro de A vale el de Metro y EMT
}  # fmt: skip
# autobús interurbano por par de zonas, según los saltos de corona; 0 = dentro de una zona B1-C2
DIEZ_VIAJES_INTERURBANO = [
    UNA_ZONA,
    _p("7.30 5.80 5.80 3.60 4.30 2.10", "12.50 10.00 10.00 6.20 7.50 3.70"),
    _p("9.60 7.60 7.60 4.80 5.70 2.80", "16.50 13.20 13.20 8.20 9.90 4.90"),
    _p("13.80 11.00 11.00 6.90 8.20 4.10", "23.60 18.80 18.80 11.80 14.10 7.00"),
    _p("17.80 14.20 14.20 8.80 10.60 5.30", "30.50 24.40 24.40 15.20 18.30 9.10"),
    _p("22.40 17.90 17.90 11.20 13.40 6.70", "38.50 30.80 30.80 19.20 23.10 11.50"),
]  # fmt: skip
# BOCM-20251231-2 pág. 68 = BOCM-20251231-3 pág. 71: el sencillo no lleva la bonificación del RDL, pero
# sí tiene precio por colectivo
# shortcut: el Metro de la zona A va de 1,50 € (hasta 5 estaciones) a 2,00 € (10 o más; ficha del CRTM de
# sencillos) y se usa el mínimo, el de la EMT; mejorar si `tiempos` da el número de estaciones
SENCILLO_150 = _p(*["1.50 1.20 1.20 0.70 0.90 0.40"] * 2)
SENCILLO_300 = _p(*["3.00 2.40 2.40 1.50 1.80 0.90"] * 2)
SENCILLO = {
    "metro_a": SENCILLO_150,
    "metro_b": SENCILLO_150,
    "tfm_mlo": _p(*["2.00 1.60 1.60 1.00 1.20 0.60"] * 2),
    "combinado": SENCILLO_300,
    "interurbano": SENCILLO_300,
    "urbano": SENCILLO_150,
}
# Abono mensual de Renfe Cercanías de 20 € (todos los núcleos), solo con descuento: RDL 17/2025
# (BOE-A-2025-26459), art. 3.2.a).2.º, https://www.boe.es/eli/es/rdl/2025/12/23/17
# Se vende hasta el 31-12-2026 y vale un mes desde su inicio, de ahí «hasta el 31-1-2027».
ABONO_RENFE = {("vigente_2026", c): D("20.00") for c in COLECTIVOS}
# Abono de 10 € para nacidos de 2000 a 2011: RDL 17/2025, art. 3.2.a).3.º (misma URL)
ABONO_RENFE_JOVEN = {("vigente_2026", c): D("10.00") for c in COLECTIVOS}
ANIOS_NACIMIENTO_RENFE_JOVEN = (2000, 2011)  # RDL 17/2025, art. 3.2.a).3.º
ABONOS_RENFE_ANIO = 11  # vale un mes natural desde su inicio: 11 al año con 30 días de vacaciones en bloque


def _i(corona: str) -> int:
    return ORDEN_CORONAS.index(corona)


def es_joven(edad: int) -> bool:
    # menores de 15 no se modelan: el abono de 7 a 14 años es gratuito (BOCM-20251231-2 pág. 66)
    return EDAD_MIN_JOVEN <= edad <= EDAD_MAX_JOVEN


def _producto(sistema: str, cmin: str, cmax: str, n_sistemas: int) -> str:
    """Producto con el que se paga un sistema de una ruta de `cmin` a `cmax`."""
    en_a = cmin == "A"
    if sistema == "metro":
        # shortcut: con otros sistemas se supone el Metro dentro de A; mejorar con el rango de cada tramo
        if not en_a:
            return "metro_b"
        return "combinado" if n_sistemas == 1 and cmax != "A" else "metro_a"
    if sistema == "metro_ligero":
        return "metro_a" if cmax == "A" else "tfm_mlo"
    if sistema in ("interurbano", "urbano") and cmax == "A":
        return "metro_a"  # dentro de la zona A vale el billete de Metro y EMT
    return {"emt": "metro_a"}.get(sistema, sistema)


def clave_tarifa(
    cmin: str, cmax: str, sistemas: str | None = None, validaciones: int = 1
) -> str:
    """Clave de una ruta: rango de coronas y un producto por validación.

    Sin `sistemas` (la heurística de #161): Metro en la zona A y autobús interurbano fuera.
    Las validaciones que pasan del número de sistemas se cobran en el producto principal.
    """
    if _i(cmin) > _i(cmax):
        raise ValueError(f"rango de coronas al revés: {cmin}-{cmax}")
    lista = sistemas.split("+") if sistemas else ["interurbano"]
    if desconocidos := set(lista) - set(SISTEMAS):
        raise ValueError(f"sistemas {sorted(desconocidos)} fuera de {SISTEMAS}")
    if validaciones < len(lista):
        raise ValueError(f"{validaciones} validaciones para {len(lista)} sistemas")
    productos = sorted(
        (_producto(s, cmin, cmax, len(lista)) for s in lista), key=PRODUCTOS.index
    )
    productos += productos[:1] * (validaciones - len(lista))
    return f"{cmin}-{cmax}|" + "+".join(sorted(productos, key=PRODUCTOS.index))


def claves(rutas: pd.DataFrame) -> pd.Series:
    """`clave_tarifa` de cada ruta con `corona_min` y `corona_max`, y si las hay `sistemas` y `validaciones`
    (#161); un par sin rango de coronas queda sin clave."""
    sistemas = (
        rutas["sistemas"] if "sistemas" in rutas else pd.Series(None, rutas.index)
    )
    v = pd.Series(rutas.get("validaciones", 1), rutas.index)
    return pd.Series(
        [
            None
            if pd.isna(a) or pd.isna(b)
            else clave_tarifa(a, b, None if pd.isna(s) else s, int(n))
            for a, b, s, n in zip(rutas["corona_min"], rutas["corona_max"], sistemas, v)
        ],
        index=rutas.index,
        dtype=object,
    )


def _partes(clave: str) -> tuple[str, str, list[str]]:
    rango, productos = clave.split("|")
    cmin, cmax = rango.split("-")
    return cmin, cmax, productos.split("+")


def _redondea(x: D) -> D:
    return x.quantize(CENTIMO, rounding=ROUND_HALF_UP)


def _diez_viajes(
    producto: str, cmin: str, cmax: str
) -> dict[tuple[str, str], D] | None:
    if producto == "interurbano":
        return DIEZ_VIAJES_INTERURBANO[_i(cmax) - _i(cmin)]
    return DIEZ_VIAJES.get(producto)


def _opciones(
    producto: str, viajes: D, cmin: str, cmax: str, tarifa: tuple[str, str]
) -> dict[str, D]:
    """Coste de `viajes` de un producto con su sencillo y con su 10 viajes (prorrateado)."""
    opciones = {}
    if producto in SENCILLO:
        opciones["Billete sencillo"] = viajes * SENCILLO[producto][tarifa]
    if diez := _diez_viajes(producto, cmin, cmax):
        opciones["10 viajes"] = viajes / 10 * diez[tarifa]
    return opciones


def _por_viaje(
    tarifa: tuple[str, str], clave: str, dias: int, no_laborables: int, edad: str
) -> tuple[str, D]:
    """Título y coste de pagar cada producto con su sencillo o su 10 viajes; infinito si alguno no tiene."""
    cmin, cmax, productos = _partes(clave)
    viajes = dict.fromkeys(productos, D(0))
    for p in productos:
        viajes[p] += 2 * dias * SEMANAS_MES
    viajes[productos[0]] += no_laborables
    titulos, total = set(), D(0)
    for p, v in viajes.items():
        opciones = _opciones(p, v, cmin, cmax, tarifa)
        if p == "cercanias" and tarifa in ABONO_RENFE:
            opciones["Abono Renfe"] = ABONO_RENFE[tarifa] * ABONOS_RENFE_ANIO / 12
        if p == "cercanias" and edad == "joven" and tarifa in ABONO_RENFE_JOVEN:
            # quien tiene de 15 a 25 años algún día de 2026 nació de 2000 a 2011 (lo prueba un test)
            opciones["Abono Renfe Joven"] = (
                ABONO_RENFE_JOVEN[tarifa] * ABONOS_RENFE_ANIO / 12
            )
        if not opciones:
            if p != "cercanias":
                raise ValueError(f"producto sin precio por viaje: {p!r} en {clave!r}")
            return "", D("Infinity")  # Cercanías sin descuento: solo con abono del CRTM
        titulo = min(opciones, key=opciones.get)
        titulos.add(titulo)
        total += opciones[titulo]
    return " + ".join(sorted(titulos)), total


def _abono(tarifa: tuple[str, str], clave: str) -> tuple[str, D]:
    """El abono más barato que cubre el rango de coronas de la clave."""
    cmin, cmax, _ = _partes(clave)
    cubren = {
        (a, b): p
        for (a, b), p in ABONOS.items()
        if _i(a) <= _i(cmin) and _i(b) >= _i(cmax)
    }
    a, b = min(cubren, key=lambda k: (cubren[k][tarifa], _i(k[1]) - _i(k[0])))
    return ("Abono 30 días" if a == "A" else f"Abono 30 días {a}-{b}"), cubren[a, b][
        tarifa
    ]


def coste_mes(
    tarifa: tuple[str, str], edad: str, clave: str, dias: int, no_laborables: int
) -> tuple[str, D]:
    """Título y coste mensual del más barato para la tarifa (escenario, colectivo); en un empate gana el
    de menor compromiso."""
    if dias not in DIAS or no_laborables not in NO_LABORABLES:
        raise ValueError(
            f"dias {dias} o no_laborables {no_laborables} fuera de {DIAS} y {NO_LABORABLES}"
        )
    escenario, colectivo = tarifa
    if escenario not in ESCENARIOS or colectivo not in COLECTIVOS or edad not in EDADES:
        raise ValueError(
            f"escenario {escenario!r}, colectivo {colectivo!r} o edad {edad!r} desconocidos"
        )
    titulo, precio = _abono(tarifa, clave)
    cmin, cmax, productos = _partes(clave)
    # el mes sin abono (vacaciones) el ocio se paga por viaje en el producto principal
    # shortcut: con Cercanías de principal no hay precio por viaje y ese ocio no se cobra
    ocio = _opciones(productos[0], D(no_laborables), cmin, cmax, tarifa)
    ocio_vacaciones = min(ocio.values(), default=D(0)) / 12
    candidatos = {
        **dict([_por_viaje(tarifa, clave, dias, no_laborables, edad)]),
        titulo: precio * ABONOS_ANIO / 12 + ocio_vacaciones,
    }
    if edad == "joven":
        candidatos["Abono Joven"] = (
            ABONO_JOVEN[tarifa] * ABONOS_ANIO / 12 + ocio_vacaciones
        )
    if edad == "mayor_65":
        candidatos["Abono +65"] = ABONO_65[tarifa]
    titulo = min(candidatos, key=candidatos.get)
    return titulo, _redondea(candidatos[titulo])


def rango_coronas(zonas: gpd.GeoDataFrame, coronas: gpd.GeoDataFrame) -> pd.DataFrame:
    """Heurística de #161: coronas que cruza la recta entre los centros de cada par de zonas.

    `zonas`: `zona_id`, `corona`, `lon_centro`, `lat_centro`; `coronas`: `corona` y polígono en
    EPSG:25830. Solo cuentan las coronas de la Comunidad (A-C2); el origen y el destino aportan
    siempre su propia corona. Devuelve `zona_id`, `destino_id`, `corona_min` y `corona_max`.
    """
    centros = gpd.points_from_xy(zonas["lon_centro"], zonas["lat_centro"], crs=4326)
    xy = gpd.GeoSeries(centros).to_crs(25830)
    pares = pd.DataFrame(
        product(range(len(zonas)), repeat=2), columns=["o", "d"]
    ).query("o != d")
    x, y = xy.x.to_numpy(), xy.y.to_numpy()
    o, d = pares["o"].to_numpy(), pares["d"].to_numpy()
    puntas = np.stack([x[o], y[o], x[d], y[d]], axis=1).reshape(-1, 2, 2)
    rectas = gpd.GeoDataFrame(pares, geometry=shapely.linestrings(puntas), crs=25830)
    cm = coronas[coronas["corona"].isin(ORDEN_CORONAS)]
    # shortcut: un roce cuenta como cruce (14 pares no dirigidos cambian con 100 m mínimos dentro); vale hasta #161
    cruces = gpd.sjoin(rectas, cm[["corona", "geometry"]], predicate="intersects")
    propias = pd.concat(
        [
            pd.DataFrame({"o": o, "d": d, "corona": zonas["corona"].iloc[i].values})
            for o, d, i in [(pares.o, pares.d, pares.o), (pares.o, pares.d, pares.d)]
        ]
        + [
            pd.DataFrame(
                {
                    "o": range(len(zonas)),
                    "d": range(len(zonas)),
                    "corona": zonas["corona"].values,
                }
            )
        ]
    )
    todas = pd.concat([cruces[["o", "d", "corona"]], propias])
    todas["i"] = todas["corona"].map(ORDEN_CORONAS.index)
    rango = todas.groupby(["o", "d"])["i"].agg(["min", "max"]).reset_index()
    ids = zonas["zona_id"].to_numpy()
    return pd.DataFrame(
        {
            "zona_id": ids[rango["o"]],
            "destino_id": ids[rango["d"]],
            "corona_min": [ORDEN_CORONAS[i] for i in rango["min"]],
            "corona_max": [ORDEN_CORONAS[i] for i in rango["max"]],
        }
    )


def tabla(claves: list[str]) -> pd.DataFrame:
    """Tabla `tarifas` v2: escenario × colectivo × edad × clave × días × viajes no laborables, validada."""
    filas = [
        (esc, col, edad, clave, dias, nl, *coste_mes((esc, col), edad, clave, dias, nl))
        for esc, col, edad, clave, dias, nl in product(
            ESCENARIOS, COLECTIVOS, EDADES, claves, DIAS, NO_LABORABLES
        )
    ]
    df = pd.DataFrame(
        filas,
        columns=[
            "escenario",
            "colectivo",
            "edad",
            "clave_tarifa",
            "dias",
            "no_laborables",
            "titulo",
            "coste_mes",
        ],
    )
    df["coste_mes"] = df["coste_mes"].astype(float)
    contratos.validar(df, "tarifas")
    return df


def clave_v1(corona: str, viajes_dia: int) -> str:
    """Clave de la forma v1 (#80): ida por la corona pasando por A; con 4 viajes, más Metro de A."""
    clave = clave_tarifa("A", corona)
    return clave + "+metro_a" * (viajes_dia == 4)


def tabla_v1() -> pd.DataFrame:
    """Forma v1 de `tarifas` (escenario × joven × corona × días × viajes al día) que lee `calculo.py`,
    con el precio ordinario.

    shortcut: se mantiene hasta que #164 lea la v2; entonces se borra.
    """
    filas = [
        (
            esc,
            joven,
            corona,
            dias,
            viajes,
            *coste_mes(
                (esc, "ordinario"),
                "joven" if joven else "general",
                clave_v1(corona, viajes),
                dias,
                0,
            ),
        )
        for esc, joven, corona, dias, viajes in product(
            ESCENARIOS, (False, True), ORDEN_CORONAS, DIAS, VIAJES_DIA
        )
    ]
    columnas = ["escenario", "joven", "corona", "dias", "viajes_dia", "titulo"]
    df = pd.DataFrame(filas, columns=[*columnas, "coste_mes"])
    df["coste_mes"] = df["coste_mes"].astype(float)
    return df
