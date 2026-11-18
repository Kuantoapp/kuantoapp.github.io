"""Título de transporte más barato al mes en la Comunidad de Madrid por la ruta real, con los precios de 2026.

La ruta se resume en una `clave_tarifa`: el rango de coronas que atraviesa y un producto por validación
(«B2-C1|interurbano», «A-C2|interurbano+metro_a»). Con ella se compara el abono que cubre el rango
(normal si entra en A, interzonal si no) con el sencillo o el 10 viajes de cada producto, más el Abono
Joven (15 a 25 años) y el Abono +65 (gratuito). Supuestos: sin descuentos de familia numerosa ni
discapacidad (#163); los precios con descuento (`vigente_2026`) dependen del RDL 17/2025, que es
temporal (solo 2026); el 10 viajes se prorratea (viajes ÷ 10 × precio), porque no caduca: la ficha
del CRTM dice «Validez: Ilimitada» (https://www.crtm.es/billetes-y-tarifas/buscador/sencillos-y-10-viajes/,
consultada el 18-11-2026; #162 sustituye a los paquetes enteros de #80).
Cercanías: vale el abono del CRTM de la corona, o el Abono mensual de Renfe (20 €, todos los núcleos,
solo 2026); sin descuento no hay precio publicado de Renfe y solo cuenta el abono del CRTM. El Bonotren
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
from mesobra.api_estatica import CORONAS as ORDEN_CORONAS
from mesobra.api_estatica import EDADES, NO_LABORABLES, VIAJES_DIA

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
# mismas páginas: abonos interzonales, sin pasar por la zona A
ABONO_INTERZONAL = {
    **dict.fromkeys(
        [("B1", "B2"), ("B2", "B3"), ("B2", "C1"), ("B2", "C2"), ("B3", "C1"), ("B3", "C2"), ("C1", "C2")],
        _p("28.70", "49.30"),
    ),
    **dict.fromkeys([("B1", "B3"), ("B1", "C1"), ("B1", "C2")], _p("32.70", "56.20")),
}  # fmt: skip
# abono que cubre de la primera corona a la segunda: el normal de A a c, o el interzonal
ABONOS = {("A", c): p for c, p in ABONO_30.items()} | ABONO_INTERZONAL
# mismas páginas, todas las zonas
ABONO_JOVEN = _p("10.00", "20.00")
# gratuito, 365 días (BOCM-20251231-2 pág. 66; -3 pág. 70); «hasta la zona C2», que cubre todas las coronas
# de las zonas: https://www.crtm.es/billetes-y-tarifas/buscador/abono-plus65/ (consultada el 18-11-2026)
ABONO_65 = _p("0.00", "0.00")
# BOCM-20251231-2 pág. 67 y BOCM-20251231-3 pág. 72
DIEZ_VIAJES = {
    "metro_a": _p("7.30", "12.50"),  # Metro zona A, EMT y ML1
    "metro_b": _p("6.70", "11.50"),  # MetroEste, MetroNorte y MetroSur
    "tfm_mlo": _p("7.30", "12.50"),  # TFM y Metro Ligero Oeste
    "combinado": _p("10.90", "18.80"),  # Metro de la zona A y de la B
    "urbano": _p(
        "5.10", "8.70"
    ),  # fila de una sola zona; dentro de A vale el de Metro y EMT
}
# autobús interurbano por par de zonas, según los saltos de corona; 0 = dentro de una zona B1-C2
DIEZ_VIAJES_INTERURBANO = [
    _p("5.10", "8.70"),
    _p("7.30", "12.50"),
    _p("9.60", "16.50"),
    _p("13.80", "23.60"),
    _p("17.80", "30.50"),
    _p("22.40", "38.50"),
]
# BOCM-20251231-2 pág. 68 = BOCM-20251231-3 pág. 71: el sencillo no tiene descuento
# shortcut: el Metro de la zona A va de 1,50 € (hasta 5 estaciones) a 2,00 € (10 o más; ficha del CRTM de
# sencillos) y se usa el mínimo, el de la EMT; mejorar si `tiempos` da el número de estaciones
SENCILLO = {
    "metro_a": _p("1.50", "1.50"),
    "metro_b": _p("1.50", "1.50"),
    "tfm_mlo": _p("2.00", "2.00"),
    "combinado": _p("3.00", "3.00"),
    "interurbano": _p("3.00", "3.00"),
    "urbano": _p("1.50", "1.50"),
}
# Abono mensual de Renfe Cercanías en 2026 (todos los núcleos, hasta el 31-1-2027), solo con descuento
# https://www.renfe.com/es/es/promociones/abonos-renfe/abonos-bonificados/preguntas-frecuentes (18-11-2026)
ABONO_RENFE = {"vigente_2026": D("20.00")}
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


def _diez_viajes(producto: str, cmin: str, cmax: str) -> dict[str, D] | None:
    if producto == "interurbano":
        return DIEZ_VIAJES_INTERURBANO[_i(cmax) - _i(cmin)]
    return DIEZ_VIAJES.get(producto)


def _opciones(
    producto: str, viajes: D, cmin: str, cmax: str, escenario: str
) -> dict[str, D]:
    """Coste de `viajes` de un producto con su sencillo y con su 10 viajes (prorrateado)."""
    opciones = {}
    if producto in SENCILLO:
        opciones["Billete sencillo"] = viajes * SENCILLO[producto][escenario]
    if diez := _diez_viajes(producto, cmin, cmax):
        opciones["10 viajes"] = viajes / 10 * diez[escenario]
    return opciones


def _por_viaje(
    escenario: str, clave: str, dias: int, no_laborables: int
) -> tuple[str, D]:
    """Título y coste de pagar cada producto con su sencillo o su 10 viajes; infinito si alguno no tiene."""
    cmin, cmax, productos = _partes(clave)
    viajes = dict.fromkeys(productos, D(0))
    for p in productos:
        viajes[p] += 2 * dias * SEMANAS_MES
    viajes[productos[0]] += no_laborables
    titulos, total = set(), D(0)
    for p, v in viajes.items():
        opciones = _opciones(p, v, cmin, cmax, escenario)
        if p == "cercanias" and escenario in ABONO_RENFE:
            opciones["Abono Renfe"] = ABONO_RENFE[escenario] * ABONOS_RENFE_ANIO / 12
        if not opciones:
            if p != "cercanias":
                raise ValueError(f"producto sin precio por viaje: {p!r} en {clave!r}")
            return "", D("Infinity")  # Cercanías sin descuento: solo con abono del CRTM
        titulo = min(opciones, key=opciones.get)
        titulos.add(titulo)
        total += opciones[titulo]
    return " + ".join(sorted(titulos)), total


def _abono(clave: str) -> tuple[str, dict[str, D]]:
    """El abono más barato (con descuento) que cubre el rango de coronas de la clave."""
    cmin, cmax, _ = _partes(clave)
    cubren = {
        (a, b): p
        for (a, b), p in ABONOS.items()
        if _i(a) <= _i(cmin) and _i(b) >= _i(cmax)
    }
    a, b = min(cubren, key=lambda k: (cubren[k]["vigente_2026"], _i(k[1]) - _i(k[0])))
    return ("Abono 30 días" if a == "A" else f"Abono 30 días {a}-{b}"), cubren[a, b]


def coste_mes(
    escenario: str, edad: str, clave: str, dias: int, no_laborables: int
) -> tuple[str, D]:
    """Título y coste mensual del más barato; en un empate gana el de menor compromiso."""
    if dias not in DIAS or no_laborables not in NO_LABORABLES:
        raise ValueError(
            f"dias {dias} o no_laborables {no_laborables} fuera de {DIAS} y {NO_LABORABLES}"
        )
    if escenario not in ESCENARIOS or edad not in EDADES:
        raise ValueError(f"escenario {escenario!r} o edad {edad!r} desconocidos")
    titulo, precio = _abono(clave)
    cmin, cmax, productos = _partes(clave)
    # el mes sin abono (vacaciones) el ocio se paga por viaje en el producto principal
    # shortcut: con Cercanías de principal no hay precio por viaje y ese ocio no se cobra
    ocio = _opciones(productos[0], D(no_laborables), cmin, cmax, escenario)
    ocio_vacaciones = min(ocio.values(), default=D(0)) / 12
    candidatos = {
        **dict([_por_viaje(escenario, clave, dias, no_laborables)]),
        titulo: precio[escenario] * ABONOS_ANIO / 12 + ocio_vacaciones,
    }
    if edad == "joven":
        candidatos["Abono Joven"] = (
            ABONO_JOVEN[escenario] * ABONOS_ANIO / 12 + ocio_vacaciones
        )
    if edad == "mayor_65":
        candidatos["Abono +65"] = ABONO_65[escenario]
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
    """Tabla `tarifas` v2: escenario × edad × clave × días × viajes no laborables, validada."""
    filas = [
        (esc, edad, clave, dias, nl, *coste_mes(esc, edad, clave, dias, nl))
        for esc, edad, clave, dias, nl in product(
            ESCENARIOS, EDADES, claves, DIAS, NO_LABORABLES
        )
    ]
    df = pd.DataFrame(
        filas,
        columns=[
            "escenario",
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
    """Forma v1 de `tarifas` (escenario × joven × corona × días × viajes al día) que lee `calculo.py`.

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
                esc, "joven" if joven else "general", clave_v1(corona, viajes), dias, 0
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
