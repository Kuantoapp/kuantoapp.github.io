"""Tests de `mesobra.hogares` con un recorte de los CSV de la EPF y del IPC."""

import pytest

from mesobra import hogares

P = hogares.PREFIJO
CAB = "Año;Concepto;Tipo territorio;Código territorio;Territorio;Medida;Valor;Unidad;Estado dato"
UC = "Gasto medio unidad consumo"
F3, F4 = hogares.CONCEPTOS
# (año, concepto, medida, valor), con distractores: 04.4 completo, agua embotellada, 2024 y otra medida
TRES = [
    (2025, P + "productos alimenticios", UC, "3115.68"),
    (2025, P + "bebidas no alcohólicas", UC, "188.78"),
    (2025, P + "electricidad, gas y otros combustibles", UC, "806.38"),
    (
        2025,
        P + "suministro de agua y otros servicios relacionados con la vivienda",
        UC,
        "776.78",
    ),
    (2024, P + "productos alimenticios", UC, "1"),
    (2025, P + "productos alimenticios", "Gasto medio", "9999"),
]
TELEFONIA = P + "servicios de telefonía y relacionados con Internet"
CUATRO = [
    (2025, P + "suministro de agua", UC, "166.63"),
    (2025, TELEFONIA, UC, "524.62"),
    (2025, P + "agua", UC, "24.80"),
    (2024, P + "suministro de agua", UC, "1"),
    (2025, P + "suministro de agua", "Gasto medio", "9999"),
]
SUBGRUPOS = [s for c in hogares.CONCEPTOS.values() for _, s in c.values()]
# Índice de 2025: 100 todo el año; de 2026M01 a 2026M10 sube a `alto` (media de 12 meses = (2 * 100 + 10 * alto) / 12).
ALTOS = dict(zip(SUBGRUPOS, [102.0, 104.0, 112.0, 106.0, 100.0], strict=True))
AGUA = "04.4.1 Suministro de agua"
FACTOR = {s: (200 + 10 * a) / 1200 for s, a in ALTOS.items()}


def _ipc(carpeta, omitir=None, dic25=True, hueco=None):
    filas = [
        "Comunidades y Ciudades Autónomas;Subgrupos ECOICOP ver.2;Tipo de dato;Periodo;Total"
    ]
    nacional = ["Clases  ECOICOP ver.2;Tipo de dato;Periodo;Total"]
    for sub, alto in ALTOS.items():
        if sub == omitir:
            continue
        for a, m in [(2025, m) for m in range(1, 13 if dic25 else 12)] + [
            (2026, m) for m in range(1, 11)
        ]:
            v = 100 if a == 2025 else alto
            if (sub, f"{a}M{m:02d}") == hueco:
                continue
            num = f"{v:.3f}".replace(".", ",")
            if sub == AGUA:
                nacional.append(f"{sub};Índice;{a}M{m:02d};{num}")
                nacional.append(
                    f"04.4.2 Recogida de basuras;Índice;{a}M{m:02d};500,000"
                )
                continue
            filas.append(f"13 Madrid, Comunidad de;{sub};Índice;{a}M{m:02d};{num}")
            # distractores: otra comunidad y variación anual
            filas.append(f"07 Castilla y León;{sub};Índice;{a}M{m:02d};500,000")
            filas.append(
                f"13 Madrid, Comunidad de;{sub};Variación anual;{a}M{m:02d};9,9"
            )
    (carpeta / hogares.IPC).write_text("\n".join(filas), encoding="utf-8-sig")
    (carpeta / hogares.IPC_NACIONAL).write_text(
        "\n".join(nacional), encoding="utf-8-sig"
    )


def _escribir(carpeta, cuatro=CUATRO, **ipc):
    for nombre, filas in ((F3, TRES), (F4, cuatro)):
        lineas = [CAB] + [f"{a};{c};Otros;;;{m};{v};Euros;" for a, c, m, v in filas]
        (carpeta / nombre).write_text("\n".join(lineas), encoding="utf-8-sig")
    _ipc(carpeta, **ipc)


def _esperado():
    f = FACTOR
    return {
        "alimentacion": (3115.68 * f[SUBGRUPOS[0]] + 188.78 * f[SUBGRUPOS[1]]) / 12,
        "suministros": (806.38 * f[SUBGRUPOS[2]] + 166.63 * f[SUBGRUPOS[3]]) / 12,
        "comunicaciones": 524.62 * f[SUBGRUPOS[4]] / 12,
    }


def test_factores_ipc(tmp_path):
    _escribir(tmp_path)
    f = hogares.factores_ipc(tmp_path)
    assert f.to_dict() == pytest.approx(FACTOR)
    assert f.attrs["ipc_hasta"] == "2026-10"


def test_perfiles(tmp_path):
    _escribir(tmp_path)
    esp = _esperado()
    df = hogares.hogares(tmp_path)
    assert "Estimado" in df.attrs["nota"]
    assert df.attrs["ipc_hasta"] == "2026-10"
    df = df.set_index("perfil")
    assert len(df) == 4
    assert not df.isna().any().any()
    columnas = ["alimentacion", "suministros", "comunicaciones"]
    assert (df[columnas] > 0).all().all()
    solo = df.loc["solo"]
    for col in columnas:
        assert solo[col] == pytest.approx(esp[col])
        assert df.loc["pareja", col] == pytest.approx(1.5 * solo[col])
        assert df.loc["monoparental", col] == pytest.approx(1.3 * solo[col])
    for col in ("suministros", "comunicaciones"):
        assert df.loc["comparte", col] == pytest.approx(esp[col] * 2 / 3)


def test_cesta_uc(tmp_path):
    _escribir(tmp_path)
    cesta = hogares.cesta_uc(tmp_path)
    assert cesta.to_dict() == pytest.approx(_esperado())
    assert cesta.attrs["ipc_hasta"] == "2026-10"


def test_falta_un_concepto(tmp_path):
    _escribir(tmp_path, cuatro=CUATRO[1:])
    with pytest.raises(ValueError, match="suministro de agua"):
        hogares.hogares(tmp_path)


def test_falta_un_subgrupo_del_ipc(tmp_path):
    _escribir(tmp_path, omitir="08.3 Servicios de información y comunicaciones")
    with pytest.raises(ValueError, match="faltan los subgrupos"):
        hogares.factores_ipc(tmp_path)


def test_ipc_sin_los_12_meses_de_2025(tmp_path):
    _escribir(tmp_path, dic25=False)
    with pytest.raises(ValueError, match="12 meses"):
        hogares.factores_ipc(tmp_path)


def test_ipc_con_un_hueco_en_los_ultimos_12_meses(tmp_path):
    _escribir(tmp_path, hueco=("01.1 Alimentos", "2026M05"))
    with pytest.raises(ValueError, match="consecutivos"):
        hogares.factores_ipc(tmp_path)


TRAMOS = [
    "Hasta 499 euros",
    "De 500 a 999 euros",
    "De 1.000 a 1.499 euros",
    "De 1.500 a 1.999 euros",
    "De 2.000 a 2.499 euros",
    "De 2.500 a 2.999 euros",
    "De 3.000 a 4.999 euros",
    "5.000 euros o más",
]
NIVEL = "Nivel de ingresos mensuales netos regulares del hogar"


def _tramos(carpeta, omitir=None, vacio=None):
    """Tramo k (1 a 8): alimentos por hogar 1000·k y 1 + (k − 1)/10 UC; total: 4000 y 2 UC (2000 €/UC)."""
    grupos = [
        f"{NIVEL};Gastos medios y distribución porcentual;Grupos de gasto (2 dígitos);Periodo;Total"
    ]
    uc = [f"{NIVEL};Tipo de dato;Gastos medios, distribución e índice;Periodo;Total"]
    for i, t in enumerate(["Total", *TRAMOS]):
        if t == omitir:
            continue
        alim, n = (4000, 2) if t == "Total" else (1000 * i, 1 + (i - 1) / 10)
        alim_txt = "" if t == vacio else f"{alim:.2f}".replace(".", ",")
        grupos += [
            f"{t};Gasto medio por hogar;01 Alimentos y bebidas no alcohólicas;2025;{alim_txt}",
            f"{t};Gasto medio por hogar;01 Alimentos y bebidas no alcohólicas;2024;1,00",
            f"{t};Gasto medio por persona;01 Alimentos y bebidas no alcohólicas;2025;1,00",
            f"{t};Gasto medio por hogar;03 Vestido y calzado;2025;1,00",
        ]
        total = 30000.0
        uc += [
            f"{t};Dato base;Gasto medio por hogar;2025;"
            + f"{total:.2f}".replace(".", ","),
            f"{t};Dato base;Gasto medio por unidad de consumo;2025;"
            + f"{total / n:.4f}".replace(".", ","),
            f"{t};Dato base;Gasto medio por unidad de consumo;2024;1,00",
            f"{t};Variación respecto al año anterior;Gasto medio por hogar;2025;1,00",
        ]
    (carpeta / hogares.EPF_TRAMOS).write_text("\n".join(grupos), encoding="utf-8-sig")
    (carpeta / hogares.EPF_TRAMOS_UC).write_text("\n".join(uc), encoding="utf-8-sig")


def test_factores_tramo(tmp_path):
    _tramos(tmp_path)
    f = hogares.factores_tramo(tmp_path)
    assert f.index.tolist() == [0, 500, 1000, 1500, 2000, 2500, 3000, 5000]
    esperado = [1000 * i / (1 + (i - 1) / 10) / 2000 for i in range(1, 9)]
    assert f.tolist() == pytest.approx(esperado)


def test_factores_tramo_falta_un_tramo(tmp_path):
    _tramos(tmp_path, omitir="De 2.000 a 2.499 euros")
    with pytest.raises(ValueError, match="2.000 a 2.499"):
        hogares.factores_tramo(tmp_path)


def test_factores_tramo_con_un_valor_vacio(tmp_path):
    _tramos(tmp_path, vacio="Hasta 499 euros")
    with pytest.raises(ValueError, match="Hasta 499"):
        hogares.factores_tramo(tmp_path)
