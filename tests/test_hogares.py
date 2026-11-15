"""Tests de `mesobra.hogares` con un recorte de los CSV de la EPF."""

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
CUATRO = [
    (2025, P + "suministro de agua", UC, "166.63"),
    (2025, P + "agua", UC, "24.80"),
    (2024, P + "suministro de agua", UC, "1"),
    (2025, P + "suministro de agua", "Gasto medio", "9999"),
]


def _escribir(carpeta, cuatro=CUATRO):
    for nombre, filas in ((F3, TRES), (F4, cuatro)):
        lineas = [CAB] + [f"{a};{c};Otros;;;{m};{v};Euros;" for a, c, m, v in filas]
        (carpeta / nombre).write_text("\n".join(lineas), encoding="utf-8-sig")


def test_perfiles(tmp_path):
    _escribir(tmp_path)
    df = hogares.hogares(tmp_path).set_index("perfil")
    assert len(df) == 4
    assert not df.isna().any().any()
    assert (df[["alimentacion", "suministros"]] > 0).all().all()
    solo = df.loc["solo"]
    assert solo["alimentacion"] == pytest.approx(3304.46 / 12)
    assert solo["suministros"] == pytest.approx(973.01 / 12)
    for col in ("alimentacion", "suministros"):
        assert df.loc["pareja", col] == pytest.approx(1.5 * solo[col])
        assert df.loc["monoparental", col] == pytest.approx(1.3 * solo[col])
    assert df.loc["comparte", "suministros"] == pytest.approx(973.01 * 2 / 3 / 12)


def test_falta_un_concepto(tmp_path):
    _escribir(tmp_path, cuatro=CUATRO[1:])
    with pytest.raises(ValueError, match="suministro de agua"):
        hogares.hogares(tmp_path)
