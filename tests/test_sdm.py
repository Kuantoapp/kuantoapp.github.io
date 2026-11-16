"""Indicadores en Smart Data Models: la salida con los ejemplos cumple el esquema y el recuento sale de contar a mano."""

import importlib.util
import json
from pathlib import Path

import pytest
from jsonschema import ValidationError

from mesobra import sdm

RAIZ = Path(__file__).parent
EJEMPLOS = RAIZ / "fixtures/api"
ESQUEMA = json.loads((RAIZ / "fixtures/sdm_esquema.json").read_text("utf-8"))
ANALISIS = json.loads((EJEMPLOS / "analisis.json").read_text("utf-8"))
ALQUILER = json.loads((EJEMPLOS / "alquiler.json").read_text("utf-8"))
# Contado a mano sobre los ejemplos (2024, una sola vez cada zona): zonas con dato por indicador.
# alquiler: 4 de 5 (28001 sin dato); esfuerzo: 5 de 6 (una sin esfuerzo);
# sobrecarga: 4 de 5 en cada umbral (una fila sin nada).
ESPERADAS = {
    "alquiler_eur_m2_p50": 4,
    "esfuerzo": 5,
    "sobrecarga_40": 4,
    "sobrecarga_30": 4,
}


@pytest.fixture
def salida():
    return sdm.entidades(ANALISIS, ALQUILER)


def test_numero_de_entidades_por_indicador(salida):
    assert {k: len(v) for k, v in salida.items()} == ESPERADAS
    assert sum(len(v) for v in salida.values()) == 17


def test_la_salida_cumple_el_esquema(salida):
    sdm.validar(salida, ESQUEMA)


def test_un_esquema_que_exige_mas_lo_rechaza(salida):
    estricto = {**ESQUEMA, "required": [*ESQUEMA["required"], "product"]}
    with pytest.raises(ValidationError):
        sdm.validar(salida, estricto)


def test_id_repetido_falla(salida):
    salida["esfuerzo"].append(salida["esfuerzo"][0])
    with pytest.raises(ValueError, match="id repetido"):
        sdm.validar(salida, ESQUEMA)


def test_entidad_de_esfuerzo_literal(salida):
    e = next(e for e in salida["esfuerzo"] if e["area"] == "2807901")
    assert e["id"] == "urn:ngsi-ld:KeyPerformanceIndicator:esfuerzo-2807901-2024"
    assert e["kpiValue"] == 0.379
    assert e["calculationPeriod"] == {"from": "2024-01-01", "to": "2024-12-31"}
    assert e["process"] == "esfuerzo"


def test_sin_dato_no_se_publica_y_estimado_se_marca(salida):
    zonas = {e["area"] for e in salida["alquiler_eur_m2_p50"]}
    assert "28001" not in zonas
    e = next(e for e in salida["alquiler_eur_m2_p50"] if e["area"] == "28092")
    assert e["description"].endswith(", estimado")


def test_sobrecarga_es_un_intervalo(salida):
    e = next(e for e in salida["sobrecarga_40"] if e["area"] == "2807901")
    assert e["kpiValue"] == {"inf": 14.0, "sup": 19.5}


def test_escribir_deja_ficheros_validos_y_borra_los_viejos(tmp_path):
    (tmp_path / "viejo.json").write_text("[]")
    sdm.escribir(ANALISIS, ALQUILER, tmp_path, ESQUEMA)
    assert not (tmp_path / "viejo.json").exists()
    assert sorted(p.name for p in tmp_path.glob("*.json")) == sorted(
        f"{n}.json" for n in ESPERADAS
    )
    leidas = json.loads((tmp_path / "esfuerzo.json").read_text("utf-8"))
    assert len(leidas) == ESPERADAS["esfuerzo"]


def test_entrada_fuera_de_contrato_falla_sin_escribir(tmp_path):
    roto = {**ALQUILER, "zonas": {"no-es-zona": {}}}
    with pytest.raises(ValueError, match="alquiler.json"):
        sdm.escribir(ANALISIS, roto, tmp_path, ESQUEMA)
    assert not list(tmp_path.iterdir())


def test_leeme_nombra_modelo_y_version_exacta(tmp_path):
    sdm.escribir(ANALISIS, ALQUILER, tmp_path, ESQUEMA)
    texto = (tmp_path / "LEEME.md").read_text("utf-8")
    assert "KeyPerformanceIndicator" in texto
    assert ESQUEMA["$schemaVersion"] == "0.2.1"
    assert "versión 0.2.1 del esquema" in texto
    assert "CC BY 4.0" in texto
    assert "www.ine.es" in texto  # los ejemplos citan al INE


def test_leeme_cumple_cifras_con_fuente(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "cifras", RAIZ.parent / ".github/scripts/cifras_con_fuente.py"
    )
    cifras = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cifras)
    sdm.escribir(ANALISIS, ALQUILER, tmp_path, ESQUEMA)
    assert cifras.revisar(tmp_path / "LEEME.md") == []
