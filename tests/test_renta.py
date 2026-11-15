"""Tests de `mesobra.renta` con un recorte de los CSV del ADRH."""

import pandas as pd
import pytest

from mesobra import renta

CABECERAS = [
    "Indicadores de renta media y mediana",
    "Índice de Gini y Distribución de la renta P80/P20",
    "Indicadores demográficos",
]
MUN = "28001 Acebeda, La"
MAD = "28079 Madrid"
D05 = "2807905 Madrid distrito 05"
D13 = "2807913 Madrid distrito 13"
OTRO = "2806502 Otro distrito 02"
S1 = "2807905101 Madrid sección 05101"
S2 = "2807905102 Madrid sección 05102"
S3 = "2807905103 Madrid sección 05103"

# Columnas: municipio, distrito, sección, año y los seis indicadores en el orden de FICHEROS.
FILAS = [
    (MUN, "", "", 2023, "30.000", "15.000", ".", ".", "50", "2,5"),
    (MUN, "", "", 2024, "31.000", "15.500", ".", ".", "52", "2,4"),
    (MAD, "", "", 2023, "50.000", "25.000", "33,0", "5,0", "3.400.000", "2,6"),
    (MAD, "", "", 2024, "52.000", "26.000", "33,5", "5,1", "3.414.246", "2,6"),
    (MAD, D05, "", 2024, "79.274", "34.254", "37,5", "6,0", "150.000", "2,5"),
    (MAD, D13, "", 2024, "35.000", "14.000", "30,0", "4,5", "240.000", "2,9"),
    ("28065 Otro", OTRO, "", 2024, "40.000", "20.000", "31,0", "4,6", "9.000", "2,7"),
    (MAD, D05, S1, 2023, "60.000", "30.000", "29,0", "4,0", "1.500", "2,4"),
    (MAD, D05, S1, 2024, "61.000", "30.500", "29,5", "4,1", "1.510", "2,4"),
    (MAD, D05, S2, 2023, ".", ".", ".", ".", "1.200", "2,3"),
    (MAD, D05, S2, 2024, "55.000", "27.000", "28,0", "3,9", "1.210", "2,3"),
    (MAD, D05, S3, 2023, "70.000", "35.000", "30,0", "4,2", "1.300", "2,5"),
    (MAD, D05, S3, 2024, "", "", "", "", "", ""),  # sección que ya no existe
]


def _escribir(carpeta, filas):
    columnas = (slice(4, 6), slice(6, 8), slice(8, 10))
    ficheros = zip(renta.FICHEROS.items(), CABECERAS, columnas)
    for (nombre, indicadores), cabecera, cols in ficheros:
        lineas = [f"Municipios;Distritos;Secciones;{cabecera};Periodo;Total"]
        for f in filas:
            for ind, valor in zip(indicadores, f[cols]):
                lineas.append(";".join([*f[:3], ind, str(f[3]), valor]))
        (carpeta / nombre).write_text("\n".join(lineas), encoding="utf-8-sig")


@pytest.fixture
def tabla(tmp_path):
    _escribir(tmp_path, FILAS)
    return renta.renta(tmp_path).set_index(renta.CLAVE)


def test_claves_exactas(tabla):
    assert set(tabla.index) == {
        ("28001", "zona", 2023),
        ("28001", "zona", 2024),
        ("28079", "zona", 2023),
        ("28079", "zona", 2024),
        ("2807905", "zona", 2024),
        ("2807913", "zona", 2024),
        ("2807905101", "seccion", 2023),
        ("2807905101", "seccion", 2024),
        ("2807905102", "seccion", 2023),
        ("2807905102", "seccion", 2024),
        ("2807905103", "seccion", 2023),
    }


def test_numeros_en_formato_espanol(tabla):
    assert tabla.loc[("2807905", "zona", 2024), "renta_hogar"] == 79274.0
    assert tabla.loc[("2807905", "zona", 2024), "gini"] == 37.5
    assert tabla.loc[("28079", "zona", 2024), "poblacion"] == 3414246


def test_secreto_estadistico_es_nulo(tabla):
    assert tabla.loc[("28001", "zona", 2024)][["gini", "p80p20"]].isna().all()
    assert tabla.loc[("2807905102", "seccion", 2023)].isna().sum() == 4
    assert tabla.loc[("2807905102", "seccion", 2023), "poblacion"] == 1200


def test_valor_ilegible_falla(tmp_path):
    _escribir(tmp_path, [(MUN, "", "", 2024, "abc", "1", "1", "1", "1", "1")])
    with pytest.raises(ValueError):
        renta.renta(tmp_path)


def test_numero():
    serie = pd.Series(["3.414.246", "37,5", "."])
    assert renta._numero(serie).tolist()[:2] == [3414246, 37.5]
    assert renta._numero(serie).isna().tolist() == [False, False, True]


@pytest.mark.parametrize(
    "catalogo",
    [
        "2024;Municipios;0016;A;Per cápita;999;Euros;",
        "2023;Municipios;0016;A;Per cápita;999;Euros;",
    ],
)
def test_catalogo_distinto_o_sin_emparejar_falla(tmp_path, catalogo):
    cab = "Municipios;Distritos;Secciones;Indicadores de renta media y mediana;Periodo;Total"
    fila = "28001 Acebeda, La;;;Renta bruta media por persona;2024;1.000"
    (tmp_path / renta.RENTA).write_text(f"{cab}\n{fila}", encoding="utf-8-sig")
    (tmp_path / "cm_irpf_indicador_renta_2026-11-15.csv").write_text(
        "Año;Tipo territorio;Código territorio;Territorio;Medida;Valor;Unidad;Estado dato\n"
        + catalogo,
        encoding="utf-8-sig",
    )
    with pytest.raises(ValueError, match="Catálogo|distintas"):
        renta._comparar_catalogo(tmp_path)
