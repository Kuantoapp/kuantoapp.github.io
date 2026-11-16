"""Indicadores en Smart Data Models: la salida con los ejemplos cumple el esquema y el recuento sale de contar a mano."""

import importlib.util
import json
from pathlib import Path

import pytest
from jsonschema import ValidationError

from mesobra import sdm
from mesobra.pipeline_euros import ORIGEN_SERPAVI, SERPAVI

RAIZ = Path(__file__).parent
EJEMPLOS = RAIZ / "fixtures/api"
ESQUEMA = json.loads((RAIZ / "fixtures/sdm_esquema.json").read_text("utf-8"))
# Las fuentes de los ejemplos son el INE y la Comunidad de Madrid: su nota lleva lo que exigen.
CITAS = (
    "Elaboración propia con datos extraídos del sitio web del INE: www.ine.es, actualizado el 2026-10-30. "
    "Fuente de los datos: Comunidad de Madrid, actualizado el 2026-11-05."
)


def _con_nota(nombre, nota):
    o = json.loads((EJEMPLOS / nombre).read_text("utf-8"))
    o["meta"]["nota"] = nota
    return o


ANALISIS = _con_nota("analisis.json", CITAS)
ALQUILER = _con_nota("alquiler.json", CITAS)
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
    # Sin la palabra «Key» pegada a un literal: gitleaks la toma por una clave de API.
    assert e["id"] == f"urn:ngsi-ld:{sdm.TIPO}:esfuerzo-2807901-2024"
    assert e["kpiValue"] == 0.379
    assert e["calculationPeriod"] == {"from": "2024-01-01", "to": "2024-12-31"}
    assert e["process"] == "esfuerzo"


def test_sin_dato_no_se_publica_y_estimado_se_marca(salida):
    zonas = {e["area"] for e in salida["alquiler_eur_m2_p50"]}
    assert "28001" not in zonas
    e = next(e for e in salida["alquiler_eur_m2_p50"] if e["area"] == "28092")
    assert e["description"].endswith(", estimado")


def test_esfuerzo_no_hereda_el_estimado_del_alquiler_en_m2(salida):
    # 28092 tiene el €/m² estimado, pero el esfuerzo usa la cuantía mensual del SERPAVI, no ese €/m².
    e = next(e for e in salida["esfuerzo"] if e["area"] == "28092")
    assert "estimado" not in e["description"]


def test_sobrecarga_sale_de_un_modelo_y_siempre_es_estimada(salida):
    sobrecarga = salida["sobrecarga_40"] + salida["sobrecarga_30"]
    assert sobrecarga
    for e in sobrecarga:
        assert e["description"].endswith(", estimado")
        assert "inquilinos" in e["description"]
    # #100: el 40 % cuenta alquiler y suministros; el 30 %, solo alquiler.
    assert "suministros" in salida["sobrecarga_40"][0]["description"]
    assert "suministros" not in salida["sobrecarga_30"][0]["description"]


def test_sin_bloque_de_sobrecarga_no_se_publica_vacio(tmp_path):
    sin = {k: v for k, v in ANALISIS.items() if k != "sobrecarga"}
    sdm.escribir(sin, ALQUILER, tmp_path, ESQUEMA)
    assert not (tmp_path / "sobrecarga_40.json").exists()
    assert "sobrecarga_40" not in (tmp_path / "LEEME.md").read_text("utf-8")


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
    assert "www.ine.es" in texto  # los ejemplos citan al INE


def test_leeme_separa_la_licencia_del_modelo_de_la_de_los_datos(tmp_path):
    sdm.escribir(ANALISIS, ALQUILER, tmp_path, ESQUEMA)
    texto = (tmp_path / "LEEME.md").read_text("utf-8")
    assert "El modelo y su esquema tienen licencia CC BY 4.0" in texto
    assert "Datos: no llevan la licencia del modelo" in texto
    for meta in (ANALISIS["meta"], ALQUILER["meta"]):
        for f in meta["fuentes"]:
            assert f"Licencia: {f['licencia']}." in texto


# Nota como la del `alquiler.json` real: origen, fecha de actualización, «no participa» y una cifra.
# Con un salto de línea: el LEEME la aplana para que la marca «fuente:» cubra toda la nota.
NOTA_REAL = "Cada zona va en euros de su año\n(factor_ipc 1,0). " + ORIGEN_SERPAVI


@pytest.fixture
def leeme_real(tmp_path):
    meta = {**ALQUILER["meta"], "fuentes": [SERPAVI], "nota": NOTA_REAL}
    sdm.escribir(ANALISIS, {**ALQUILER, "meta": meta}, tmp_path, ESQUEMA)
    return tmp_path / "LEEME.md"


@pytest.mark.parametrize(
    ("quitar", "error"),
    [
        ("Fuente de los datos: Comunidad de Madrid", "Comunidad de Madrid"),
        ("www.ine.es", "www.ine.es"),
        (", actualizado el 2026-11-05", "actualizado el AAAA-MM-DD"),
    ],
)
def test_sin_una_cita_obligatoria_falla_sin_escribir(tmp_path, quitar, error):
    (tmp_path / "viejo.json").write_text("[]")
    analisis = _con_nota("analisis.json", CITAS.replace(quitar, ""))
    with pytest.raises(ValueError, match=error):
        sdm.escribir(analisis, ALQUILER, tmp_path, ESQUEMA)
    assert [p.name for p in tmp_path.iterdir()] == ["viejo.json"]


def test_serpavi_exige_su_origen():
    meta = {
        **ALQUILER["meta"],
        "fuentes": [SERPAVI],
        "nota": "actualizado el 2026-07-09",
    }
    # El nombre de la fuente del SERPAVI ya lleva «Origen de los datos: …»: sin él, falta.
    sin_origen = {**SERPAVI, "nombre": "SERPAVI"}
    assert sdm._citas_que_faltan(meta) == []
    assert sdm._citas_que_faltan({**meta, "fuentes": [sin_origen]}) == [
        "«Origen de los datos: Ministerio de Vivienda y Agenda Urbana»"
    ]


def test_leeme_lleva_fecha_y_nota_de_origen_de_cada_fichero(leeme_real):
    texto = leeme_real.read_text("utf-8")
    # «Origen de los datos: …, actualizado el …; el Ministerio no participa ni patrocina…»
    assert ORIGEN_SERPAVI in texto
    assert f"`analisis.json`, generado el {ANALISIS['meta']['generado']}" in texto
    assert f"`alquiler.json`, generado el {ALQUILER['meta']['generado']}" in texto
    assert ANALISIS["meta"]["nota"] in texto


def test_leeme_cumple_cifras_con_fuente(leeme_real):
    spec = importlib.util.spec_from_file_location(
        "cifras", RAIZ.parent / ".github/scripts/cifras_con_fuente.py"
    )
    cifras = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cifras)
    assert cifras.revisar(leeme_real) == []
