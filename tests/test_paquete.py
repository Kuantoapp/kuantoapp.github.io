"""El paquete y todas sus dependencias fijadas se importan con el Python del repo."""

import importlib

import pytest

# r5py arranca Java al importarse y la CI no lo tiene: se comprueba solo en local (JDK 21).
DEPENDENCIAS = [
    "pandas",
    "pyarrow",
    "geopandas",
    "openpyxl",
    "scipy",
    "matplotlib",
    "lightgbm",
    "mcp",
]


def test_mesobra_importable() -> None:
    assert importlib.import_module("mesobra")


@pytest.mark.parametrize("modulo", DEPENDENCIAS)
def test_dependencia_importable(modulo: str) -> None:
    assert importlib.import_module(modulo)
