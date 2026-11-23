"""Frontera del umbral de testigos en los mapas del informe (#368)."""

import pandas as pd

from mesobra.figuras import MIN_TESTIGOS, _pocos


def test_pocos_marca_por_debajo_del_umbral_en_cualquiera_de_los_anios():
    tabla = pd.DataFrame(
        {
            "zona_id": ["a", "b", "c", "c"],
            "anio": [2024, 2024, 2015, 2024],
            "testigos": [MIN_TESTIGOS - 1, MIN_TESTIGOS, MIN_TESTIGOS - 1, 500],
        }
    )
    assert MIN_TESTIGOS == 70
    assert _pocos(tabla, [2024]).to_dict() == {"a": True, "b": False, "c": False}
    assert _pocos(tabla, [2015, 2024]).to_dict() == {"a": True, "b": False, "c": True}
