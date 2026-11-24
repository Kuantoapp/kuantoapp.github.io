from datetime import date, timedelta
from decimal import ROUND_HALF_UP, localcontext
from decimal import Decimal as D
from fractions import Fraction as F
from itertools import pairwise, product

import geopandas as gpd
import pytest
from shapely import Point, box

from mesobra import transporte as t

O = "ordinario"
V, S = ("vigente_2026", O), ("sin_descuento", O)  # tarifa (escenario, colectivo)


def coste(clave, dias, no_laborables=0, *, edad="general", esc=V):
    return t.coste_mes(esc, edad, clave, dias, no_laborables)


def test_precios_de_control():
    assert (t.ABONO_30["A"][V], t.ABONO_30["C2"][V]) == (D("32.70"), D("49.20"))
    assert (t.ABONO_30["A"][S], t.ABONO_30["C2"][S]) == (D("56.20"), D("84.40"))
    assert (t.ABONO_JOVEN[V], t.ABONO_JOVEN[S]) == (D("10.00"), D("20.00"))
    assert t.ABONO_INTERZONAL["B2", "C1"][V] == D("28.70")
    assert t.ABONO_INTERZONAL["B2", "C1"][S] == D("49.30")
    assert t.ABONO_INTERZONAL["B1", "C2"][S] == D("56.20")
    assert (
        len(t.ABONO_INTERZONAL) == 10
    )  # todas las parejas de B1-C2 (BOCM-20251231-2 pág. 66)
    assert [p[V] for p in t.DIEZ_VIAJES_INTERURBANO] == [
        D(x) for x in ("5.10", "7.30", "9.60", "13.80", "17.80", "22.40")
    ]
    assert (t.DIEZ_VIAJES["metro_b"][V], t.DIEZ_VIAJES["metro_b"][S]) == (
        D("6.70"),
        D("11.50"),
    )
    assert t.DIEZ_VIAJES["combinado"][S] == D("18.80")
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
    # con 16 viajes de ocio: 53,83 × 0,51 = 27,45 pasa del abono B1-B2 más el ocio del mes de
    # vacaciones (26,71 + 16 × 0,51 / 12 = 27,39)
    assert coste("B1-B1|interurbano", 5, 16) == ("Abono 30 días B1-B2", D("27.39"))


def test_control_de_transbordo():
    # #80 daba 29,70 con paquetes enteros; prorrateado (no caduca): 7,567 / 10 × (22,40 + 7,30)
    clave = t.clave_tarifa("A", "C2", "interurbano+metro", 2)
    assert coste(clave, 1) == ("10 viajes", D("22.47"))


def test_transbordo_al_aeropuerto_paga_el_suplemento_una_vez():
    # #438: el Metro que añade el transbordo es el tramo hasta la terminal; si la ruta ya lo paga, no se duplica
    assert (
        t.clave_transbordo_aeropuerto("A-B1|interurbano")
        == "A-B1|interurbano+metro_aeropuerto"
    )
    assert (
        t.clave_transbordo_aeropuerto("A-A|metro_aeropuerto")
        == "A-A|metro_aeropuerto+metro_a"
    )
    # A-B1 → T4 con 4 viajes: 1 día, 10 viajes (11,05 sin suplemento); 2 y 3 días, ya gana el abono
    clave = t.clave_transbordo_aeropuerto("A-B1|interurbano")
    assert [coste(clave, d) for d in (1, 2, 3)] == [
        ("10 viajes", D("33.75")),
        ("Abono 30 días", D("35.55")),
        ("Abono 30 días", D("35.55")),
    ]


def test_transbordo_al_aeropuerto_en_otros_colectivos_y_sin_descuento():
    # A-B1 → T4, 1 día (BOCM-20251231-2 págs. 66-68; -3 págs. 70-72): 0,75667 viajes/mes por trayecto
    clave = t.clave_transbordo_aeropuerto("A-B1|interurbano")
    fn = ("vigente_2026", "fn_especial")
    assert coste(clave, 1, esc=fn) == (
        "10 viajes",
        D("16.80"),
    )  # (3,60 + 3,60 + 10 × 1,50) × 0,7567
    assert coste(clave, 1, esc=S) == (
        "10 viajes",
        D("41.62"),
    )  # (12,50 + 12,50 + 30) × 0,7567


def test_umbral_del_abono_en_zona_a_con_8_viajes_de_ocio():
    # 4 días: (30,27 + 8) × 0,73 = 27,93; 5 días: (37,83 + 8) × 0,73 = 33,46 > 30,43 del abono
    titulos = [coste("A-A|metro_a", d, 8)[0] for d in t.DIAS]
    assert titulos == ["10 viajes"] * 4 + ["Abono 30 días"]
    assert coste("A-A|metro_a", 5, 0) == ("10 viajes", D("27.62"))


def test_ocio_en_el_producto_principal():
    # 8 viajes de ocio al interurbano A-C2: (7,57 + 8) × 2,24 + 7,57 × 0,73 = 40,39 (al Metro saldría 28,31)
    assert coste("A-C2|interurbano+metro_a", 1, 8) == ("10 viajes", D("40.39"))


def test_el_abono_paga_el_ocio_del_mes_de_vacaciones():
    # sin cobrarlo ganaba el abono (45,78); con 16 × 1,78 / 12 = 2,37 más, gana el 10 viajes
    assert coste("A-C1|interurbano+metro_a", 1, 16) == ("10 viajes", D("47.47"))
    # zona A, 5 días y 8 de ocio: 30,43 + 8 × 0,73 / 12 = 30,92
    assert coste("A-A|metro_a", 5, 8) == ("Abono 30 días", D("30.92"))


def test_interzonal_de_32_70_y_empate_del_mas_estrecho():
    assert coste("B1-C2|interurbano", 5) == ("Abono 30 días B1-C2", D("30.43"))
    assert coste("C2-C2|interurbano", 5, 16) == ("Abono 30 días C1-C2", D("27.39"))


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
    # vale un mes desde su inicio: 11 al año con las vacaciones en bloque, 20 × 11 / 12
    assert coste("A-C2|cercanias", 5) == ("Abono Renfe", D("18.33"))
    # sin descuento no hay precio de Renfe: solo el abono del CRTM
    assert coste("A-C2|cercanias", 5, esc=S) == ("Abono 30 días", D("78.54"))
    # joven: 10 × 11 / 12 = 9,17 < Abono Joven del CRTM, 10 × 335/30 / 12 = 9,31 (mismo precio, otra
    # validez: un mes frente a 30 días); sin descuento no hay abono de Renfe
    assert coste("A-C2|cercanias", 5, edad="joven") == ("Abono Renfe Joven", D("9.17"))
    assert coste("B1-B1|cercanias", 5, edad="joven") == ("Abono Renfe Joven", D("9.17"))
    # FN especial: su Abono Joven del CRTM, 5 × 335/30 / 12 = 4,65, gana a los 10 € de Renfe
    assert coste(
        "A-C2|cercanias", 5, edad="joven", esc=("vigente_2026", "fn_especial")
    ) == (
        "Abono Joven",
        D("4.65"),
    )
    assert "Renfe" not in coste("A-C2|cercanias", 5, edad="joven", esc=S)[0]
    # ruta mixta: el Abono Joven cubre las dos partes y gana al Renfe Joven más el metro
    assert coste("A-C2|cercanias+metro_a", 5, edad="joven") == (
        "Abono Joven",
        D("9.31"),
    )


def test_anios_de_nacimiento_del_abono_renfe_joven():
    # la edad cumplida no decrece en el año: los extremos 1-1 y 31-12 de 2026 bastan
    def es_joven_en_2026(nac):
        edades = [
            f.year - nac.year - ((f.month, f.day) < (nac.month, nac.day))
            for f in (date(2026, 1, 1), date(2026, 12, 31))
        ]
        return any(t.EDAD_MIN_JOVEN <= e <= t.EDAD_MAX_JOVEN for e in edades)

    nacimientos = (date(1999, 1, 1) + timedelta(i) for i in range(14 * 366))
    jovenes = {n.year for n in nacimientos if n.year <= 2012 and es_joven_en_2026(n)}
    desde, hasta = t.ANIOS_NACIMIENTO_RENFE_JOVEN
    assert jovenes == set(range(desde, hasta + 1))  # incluidos y ajustados


def test_mas_dias_o_mas_ocio_no_cuestan_menos():
    claves = [
        "A-A|metro_a",
        "B1-B1|interurbano",
        "B2-C2|interurbano",
        "A-C2|interurbano+metro_a",
        "A-C2|cercanias",
        "A-C2|cercanias+metro_a",
    ]
    for tarifa, edad, clave in product(
        product(t.ESCENARIOS, t.COLECTIVOS), t.EDADES, claves
    ):
        costes = [
            coste(clave, d, nl, edad=edad, esc=tarifa)[1]
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


def test_joven_no_paga_mas_que_general_y_el_abono_renfe_joven_es_de_2026():
    for tarifa, clave, d, nl in product(
        product(t.ESCENARIOS, t.COLECTIVOS),
        ["A-C2|cercanias", "A-C2|cercanias+metro_a"],
        t.DIAS,
        t.NO_LABORABLES,
    ):
        joven = coste(clave, d, nl, edad="joven", esc=tarifa)
        assert joven[1] <= coste(clave, d, nl, esc=tarifa)[1]
        if "Abono Renfe Joven" in joven[0]:
            assert tarifa[0] == "vigente_2026"
            assert "Abono Renfe Joven" not in coste(clave, d, nl, esc=tarifa)[0]


@pytest.mark.parametrize(("dias", "nl"), [(0, 0), (3, 5)])
def test_fuera_de_dominio(dias, nl):
    with pytest.raises(ValueError, match="fuera de"):
        coste("A-A|metro_a", dias, nl)


def test_tabla():
    claves = ["A-A|metro_a", "B2-C1|interurbano"]
    df = t.tabla(claves)
    assert len(df) == 2 * 6 * 3 * 2 * 5 * 3
    filas = df.query(
        "escenario == 'vigente_2026' and edad == 'general' "
        "and clave_tarifa == 'B2-C1|interurbano' and dias == 5 and no_laborables == 0"
    ).set_index("colectivo")
    # 28,70 € y 14,30 € (FN especial) × 335/30 / 12
    assert filas.loc[O, "coste_mes"] == 26.71
    assert filas.loc["fn_especial", "coste_mes"] == 13.31


def test_tabla_v1_conserva_la_forma_de_80():
    df = t.tabla_v1()
    assert len(df) == 240
    assert t.clave_v1("C2", 4) == "A-C2|interurbano+metro_a"
    assert t.clave_v1("A", 4) == "A-A|metro_a+metro_a"
    fila = df.query(
        "escenario == 'vigente_2026' and ~joven and corona == 'C2' and dias == 5 "
        "and viajes_dia == 2"
    )
    assert fila.coste_mes.item() == 45.78


def test_b2_sin_descuento_redondea_el_empate_hacia_arriba():
    # 2 × 5 × 227/60 viajes × 16,50 € (BOCM-20251231-3 pág. 72, 2 saltos) / 10 = 62,425 exacto (#374)
    assert coste("A-B2|interurbano", 5, esc=S) == ("10 viajes", D("62.43"))
    v1 = t.tabla_v1().query(
        "escenario == 'sin_descuento' and ~joven and corona == 'B2' and dias == 5 "
        "and viajes_dia == 2"
    )
    assert v1.coste_mes.item() == 62.43


@pytest.mark.parametrize(
    ("tarifa", "clave", "dias", "nl", "esperado"),
    [
        # 2270 × 2,10 / 600 = 7,945 (BOCM-20251231-2 pág. 67, FN especial con discapacidad)
        (("vigente_2026", "fn_especial_discapacidad"), "A-A|metro_a", 5, 0, ("10 viajes", "7.95")),
        # (2270/60 + 8) × 2,10 / 10 = 9,625
        (("vigente_2026", "fn_especial_discapacidad"), "A-B1|interurbano", 5, 8, ("10 viajes", "9.63")),
        # suma de productos: 908 × 1,80 / 60 + 454 × 7,50 / 600 = 27,24 + 5,675 = 32,915 (pág. 71 y 72)
        (
            ("sin_descuento", "fn_general_discapacidad"),
            "A-C1|interurbano+interurbano+metro_a",
            1,
            0,
            ("10 viajes + Billete sencillo", "32.92"),
        ),
    ],
)  # fmt: skip
def test_empates_en_medio_centimo(tarifa, clave, dias, nl, esperado):
    assert coste(clave, dias, nl, esc=tarifa) == (esperado[0], D(esperado[1]))


def test_redondea_en_el_limite():
    assert t._redondea(F(62425, 1000)) == D("62.43")
    assert t._redondea(F(62425, 1000) - F(1, 10**30)) == D("62.42")
    assert str(t._redondea(F(0))) == "0.00"


def _mitad_arriba(x: F) -> D:
    # otra vía que _redondea: un empate exacto termina y cabe en 60 cifras; lo demás queda lejos de ,xx5
    with localcontext() as c:
        c.prec = 60
        return (D(x.numerator) / x.denominator).quantize(D("0.01"), ROUND_HALF_UP)


def _exacto(f) -> F:
    """Coste exacto del título de una fila de una clave de un solo producto, con la fórmula a mano:
    los precios salen de las tablas del módulo, la aritmética no."""
    tarifa = (f.escenario, f.colectivo)
    cmin, cmax, (producto,) = t._partes(f.clave_tarifa)
    diez = t._diez_viajes(producto, cmin, cmax)

    def por_viaje(viajes):
        opciones = {}
        if producto in t.SENCILLO:
            opciones["Billete sencillo"] = viajes * F(t.SENCILLO[producto][tarifa])
        if diez:
            opciones["10 viajes"] = viajes / 10 * F(diez[tarifa])
        return opciones

    fijos = {
        **por_viaje(F(2 * f.dias * t.DIAS_TRABAJO, 60) + f.no_laborables),
        "Abono Renfe": F(20) * 11 / 12,  # RDL 17/2025, 11 abonos al año
        "Abono Renfe Joven": F(10) * 11 / 12,
        "Abono +65": F(0),
    }
    if f.titulo in fijos:
        return fijos[f.titulo]
    # abono: 335/30 al año entre 12 meses, más el ocio del mes de vacaciones por viaje
    titulo, precio = t._abono(tarifa, f.clave_tarifa)
    precio = precio if f.titulo == titulo else t.ABONO_JOVEN[tarifa]
    ocio = min(por_viaje(F(f.no_laborables)).values(), default=F(0))
    return F(precio) * 335 / 360 + ocio / 12


def test_ninguna_celda_difiere_del_calculo_exacto():
    # criterio de #374 en las claves de un solo producto de todos los rangos y sistemas; las de varios
    # productos las cubren el caso de suma de test_empates_en_medio_centimo y la rejilla completa del PR
    # #408 (código anterior a precisión 90 cuantizado a 1e-50 antes del céntimo: 0 diferencias)
    pares = [
        (a, b) for a, b in product(t.ORDEN_CORONAS, repeat=2) if t._i(a) <= t._i(b)
    ]
    claves = sorted(
        {t.clave_tarifa(a, b, s) for (a, b), s in product(pares, t.SISTEMAS)}
    )
    v2 = t.tabla(claves)
    v1 = (
        t.tabla_v1()
        .query("viajes_dia == 2")
        .assign(
            colectivo=O,
            edad=lambda d: d.joven.map({True: "joven", False: "general"}),
            clave_tarifa=lambda d: d.corona.map(lambda c: t.clave_v1(c, 2)),
            no_laborables=0,
        )
    )
    for df in (v1, v2):
        for f in df.itertuples():
            assert f.coste_mes == float(_mitad_arriba(_exacto(f))), f


def test_control_por_colectivo():
    # control de la issue (referencia de dm-calculos-normativos §1.3): BOCM-20251231-2 págs. 66-68
    a, joven = t.ABONO_30["A"], t.ABONO_JOVEN
    assert [a[V[0], c] for c in ("ordinario", "fn_general", "fn_especial")] == [
        D("32.70"),
        D("26.10"),
        D("16.30"),
    ]
    assert joven[V[0], "fn_especial"] == D("5.00")
    assert (
        a[V[0], "fn_especial_discapacidad"],
        a[S[0], "fn_especial_discapacidad"],
    ) == (
        D("9.70"),
        D("16.80"),
    )
    assert t.ABONO_INTERZONAL["B2", "C1"][V[0], "fn_general_discapacidad"] == D("17.20")
    assert t.DIEZ_VIAJES_INTERURBANO[5][S[0], "discapacidad"] == D("30.80")


def test_precio_de_la_columna_y_no_del_factor():
    # el BOCM redondea a 0,10 €: 1,50 × 0,5 = 0,75 y 7,30 × 0,5 = 3,65, pero las columnas dicen 0,70 y 3,60
    assert t.SENCILLO["metro_a"][V[0], "fn_especial"] == D("0.70")
    assert t.DIEZ_VIAJES["metro_a"][V[0], "fn_especial"] == D("3.60")
    assert t.SENCILLO["interurbano"][S[0], "fn_especial_discapacidad"] == D("0.90")
    assert coste("A-A|metro_a", 1, esc=("vigente_2026", "fn_especial")) == (
        "10 viajes",
        D("2.72"),  # 7,5667 viajes ÷ 10 × 3,60
    )


# factores deducidos de las tablas del BOCM (no los publica); solo para comprobar la transcripción, nunca
# para calcular un precio (docs/verificaciones/transporte-colectivos.md, fila 1)
FACTOR = dict(zip(t.COLECTIVOS, map(D, ("1", "0.8", "0.8", "0.5", "0.6", "0.3"))))
# orden estricto de cada fila del BOCM; discapacidad y FN general valen lo mismo
ORDEN = (
    "ordinario",
    "fn_general",
    "fn_general_discapacidad",
    "fn_especial",
    "fn_especial_discapacidad",
)
PRECIOS = [
    *t.ABONOS.values(),
    t.ABONO_JOVEN,
    *t.DIEZ_VIAJES.values(),
    *t.DIEZ_VIAJES_INTERURBANO,
    *t.SENCILLO.values(),
]


def _fuera_de_banda_o_de_orden(fila: dict[str, D]) -> list[str]:
    """Columnas que no están entre factor × ordinario − 0,11 € y factor × ordinario, o que rompen el orden."""
    banda = [
        c
        for c, f in FACTOR.items()
        if not D(0) <= fila["ordinario"] * f - fila[c] <= D("0.11")
    ]
    orden = [a for a, b in pairwise(ORDEN) if not fila[a] > fila[b]]
    return (
        banda + orden + ["discapacidad"] * (fila["discapacidad"] != fila["fn_general"])
    )


def test_colectivos_en_banda_y_en_orden():
    # detecta columnas intercambiadas y erratas sin volver a copiar las tablas del BOCM
    for p, esc in product(PRECIOS, t.ESCENARIOS):
        assert len(p) == len(t.ESCENARIOS) * len(t.COLECTIVOS)
        assert _fuera_de_banda_o_de_orden({c: p[esc, c] for c in t.COLECTIVOS}) == [], p
    sencillo = {c: t.SENCILLO["metro_a"][V[0], c] for c in t.COLECTIVOS}
    cambiada = sencillo | {
        "fn_especial": sencillo["fn_general_discapacidad"],
        "fn_general_discapacidad": sencillo["fn_especial"],
    }
    assert _fuera_de_banda_o_de_orden(cambiada)
    assert _fuera_de_banda_o_de_orden(
        sencillo | {"fn_especial": D("0.60")}
    )  # errata de 0,10 €


def test_cada_colectivo_paga_menos_o_igual():
    for clave, d in product(["A-A|metro_a", "B2-C2|interurbano"], t.DIAS):
        costes = [coste(clave, d, esc=(V[0], c))[1] for c in t.COLECTIVOS]
        assert max(costes) == costes[0]


def test_colectivo_desconocido_o_columnas_que_faltan():
    with pytest.raises(ValueError, match="colectivo 'monoparental'"):
        coste("A-A|metro_a", 1, esc=("vigente_2026", "monoparental"))
    with pytest.raises(ValueError, match="6 columnas"):
        t._p("1.50 1.20", "1.50 1.20")


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


def test_suplemento_del_aeropuerto_en_los_precios_por_viaje():
    # BOCM-20251231-2 pág. 68: 3,00 € ordinario y por viaje y sin bonificación del RDL
    assert t.SUPLEMENTO_AEROPUERTO[V] == t.SUPLEMENTO_AEROPUERTO[S] == D("3.00")
    assert t.SENCILLO["metro_aeropuerto"][V] == D("4.50")  # 1,50 + 3,00
    assert t.DIEZ_VIAJES["metro_aeropuerto"][V] == D("37.30")  # 7,30 + 10 × 3,00
    assert t.DIEZ_VIAJES["metro_aeropuerto"][S] == D("42.50")  # 12,50 + 10 × 3,00


def test_el_aeropuerto_encarece_el_10_viajes_y_no_el_abono():
    # 1 día: 7,567 viajes × (7,30 + 30,00) / 10 = 28,22 frente a 5,52 sin suplemento
    assert coste("A-A|metro_a", 1) == ("10 viajes", D("5.52"))
    assert coste("A-A|metro_aeropuerto", 1) == ("10 viajes", D("28.22"))
    # 3 días: 22,7 viajes × 3,73 = 84,67 > abono de A, 32,70 × 335/30/12 = 30,43 (exento)
    assert coste("A-A|metro_aeropuerto", 3) == ("Abono 30 días", D("30.43"))
    # el Abono Joven, 10 € × 335/30/12, tampoco lo paga
    assert coste("A-A|metro_aeropuerto", 1, edad="joven") == ("Abono Joven", D("9.31"))


def test_el_combinado_paga_el_suplemento_y_el_ocio_no():
    assert t.SENCILLO["combinado_aeropuerto"][V] == D("6.00")  # 3,00 + 3,00
    assert t.DIEZ_VIAJES["combinado_aeropuerto"][V] == D("40.90")  # 10,90 + 10 × 3,00
    assert t.DIEZ_VIAJES["combinado_aeropuerto"][S] == D("48.80")  # 18,80 + 10 × 3,00
    # 1 día: 7,567 × 4,09 = 30,95 frente al abono B1, 38,20 × 335/360 = 35,55
    assert coste("A-B1|combinado_aeropuerto", 1) == ("10 viajes", D("30.95"))
    # el ocio (8 viajes) se paga sin suplemento: gana el abono, 30,43 + 8 × 0,73 / 12 = 30,92
    assert coste("A-A|metro_aeropuerto", 1, 8) == ("Abono 30 días", D("30.92"))
    # el ocio también sin suplemento en el pago por viaje: 28,22 + 8 × 0,73 = 34,06 (con suplemento, 58,06)
    por_viaje = t._por_viaje(V, "A-A|metro_aeropuerto", 1, 8, "general")[1]
    assert t._redondea(por_viaje) == D("34.06")
    # 2 días: 15,13 viajes × 3,73 = 56,45 > 30,43
    assert coste("A-A|metro_aeropuerto", 2) == ("Abono 30 días", D("30.43"))
    # FN especial: 7,567 × (3,60 + 15,00) / 10 = 14,07, bajo su abono (15,17)
    assert t.coste_mes(
        ("vigente_2026", "fn_especial"), "general", "A-A|metro_aeropuerto", 1, 0
    ) == ("10 viajes", D("14.07"))


@pytest.mark.parametrize(
    ("clave", "esperada"),
    [
        ("A-B1|combinado", "A-B1|combinado_aeropuerto"),
        ("A-A|metro_a", "A-A|metro_aeropuerto"),
        ("A-B2|interurbano+metro_a", "A-B2|interurbano+metro_aeropuerto"),
        ("A-A|metro_a+metro_a", "A-A|metro_aeropuerto+metro_a"),
        ("A-B2|interurbano", "A-B2|interurbano"),  # sin Metro no hay suplemento
    ],
)
def test_con_aeropuerto(clave, esperada):
    assert t.con_aeropuerto(clave) == esperada
