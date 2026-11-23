"""Descripción DCAT-AP de `app/datos/`: cada fichero publicado tiene su distribución, con licencia, fuentes, fecha y tamaño que casan con el fichero y con `data/README.md`."""

import json
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).parent.parent
APP_DATOS = RAIZ / "app" / "datos"
BASE = "https://yeraybc.github.io/DataMad-hackaton-2026/datos/"
ODBL = "https://opendatacommons.org/licenses/odbl/1-0/"
CC_BY = "https://creativecommons.org/licenses/by/4.0/"
ESQUEMA_KPI = "https://raw.githubusercontent.com/smart-data-models/dataModel.KeyPerformanceIndicator/master/KeyPerformanceIndicator/schema.json"
FICHEROS = sorted(
    p.relative_to(APP_DATOS).as_posix()
    for p in APP_DATOS.rglob("*")
    if p.suffix in {".json", ".geojson"}
)
CON_META = [f for f in FICHEROS if not f.startswith("sdm/")]
# usan OpenStreetMap sin citarlo en meta.fuentes (docs/decisiones.md, 2026-11-24, #110)
DERIVA_DE_OSM = {"analisis.json", "tarifas.json"}
SDM = [f for f in FICHEROS if f.startswith("sdm/")]
# cita obligatoria de cada publicador, según un trozo de la URL de su fuente
CITAS = {
    "ine.es": "Elaboración propia con datos extraídos del sitio web del INE: www.ine.es",
    "mivau.gob.es": "Origen de los datos: Ministerio de Vivienda y Agenda Urbana",
    "datos.comunidad.madrid": "Fuente de los datos: Comunidad de Madrid",
    "geofabrik.de": "© OpenStreetMap contributors",
    "crtm.es": "Powered by CRTM",
    "arcgis.com": "Powered by CRTM",
    "boe.es": "Basado en datos de la Agencia Estatal Boletín Oficial del Estado",
    "agenciatributaria.gob.es": "Fuente: Agencia Tributaria",
}


def _lista(x):
    return x if isinstance(x, list) else [x]


def _leer(ruta):
    return json.loads((APP_DATOS / ruta).read_text(encoding="utf-8"))


def _meta(fichero):
    return _leer(fichero)["meta"]


def _fuentes(fichero):
    # fuentes_ruta (tarifas) también son fuentes del fichero
    meta = _meta(fichero)
    return meta["fuentes"] + meta.get("fuentes_ruta", [])


@pytest.fixture(scope="module")
def dcat():
    return json.loads((APP_DATOS / "dcat.jsonld").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def nodos(dcat):
    return dcat["@graph"]


def _tipos(nodo):
    return _lista(nodo.get("@type", []))


@pytest.fixture(scope="module")
def dataset(nodos):
    return next(n for n in nodos if "dcat:Dataset" in _tipos(n))


@pytest.fixture(scope="module")
def distribuciones(dataset):
    return _lista(dataset["dcat:distribution"])


def _distribucion(distribuciones, fichero):
    return [d for d in distribuciones if d["dcat:downloadURL"]["@id"] == BASE + fichero]


def _prefijos_usados(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k != "@context":
                if ":" in k and not k.startswith("@"):
                    yield k.split(":")[0]
                if k in ("@type", "@id"):
                    for x in _lista(v):
                        if isinstance(x, str) and re.match(r"^[a-z]+:(?!//)", x):
                            yield x.split(":")[0]
                yield from _prefijos_usados(v)
    elif isinstance(o, list):
        for x in o:
            yield from _prefijos_usados(x)


def test_jsonld_valido_y_con_sus_prefijos(dcat):
    assert "@context" in dcat
    sin_declarar = set(_prefijos_usados(dcat)) - set(dcat["@context"])
    assert not sin_declarar, f"prefijos sin declarar en @context: {sin_declarar}"


def test_un_solo_dataset_con_lo_obligatorio(nodos):
    datasets = [n for n in nodos if "dcat:Dataset" in _tipos(n)]
    assert len(datasets) == 1
    campos = ("dct:title", "dct:description", "dct:publisher", "dcat:contactPoint")
    campos += ("dct:spatial", "dct:temporal", "dct:issued", "dcat:distribution")
    faltan = [c for c in campos if not datasets[0].get(c)]
    assert not faltan, f"al dataset le faltan {faltan}"


@pytest.mark.parametrize("fichero", FICHEROS)
def test_una_distribucion_por_fichero(distribuciones, fichero):
    assert len(_distribucion(distribuciones, fichero)) == 1


def test_ninguna_distribucion_apunta_a_un_fichero_inexistente(distribuciones):
    for d in distribuciones:
        url = d["dcat:downloadURL"]["@id"]
        assert url.startswith(BASE)
        assert (APP_DATOS / url.removeprefix(BASE)).is_file(), url


@pytest.mark.parametrize("fichero", CON_META)
def test_licencia_odbl_si_usa_openstreetmap(distribuciones, fichero):
    osm = fichero in DERIVA_DE_OSM or any(
        "openstreetmap" in (s["nombre"] + s["licencia"] + s["url"]).lower()
        for s in _fuentes(fichero)
    )
    (d,) = _distribucion(distribuciones, fichero)
    assert d["dct:license"]["@id"] == (ODBL if osm else CC_BY)


@pytest.mark.parametrize("fichero", SDM)
def test_licencia_de_sdm_cc_by(distribuciones, fichero):
    # decisión del equipo: ni esfuerzo ni p50 usan OSM, aunque alquiler.json, de donde sale p50, lo cite
    (d,) = _distribucion(distribuciones, fichero)
    assert d["dct:license"]["@id"] == CC_BY


@pytest.mark.parametrize("fichero", CON_META)
def test_fuentes_de_la_distribucion_son_las_del_meta(distribuciones, fichero):
    (d,) = _distribucion(distribuciones, fichero)
    derivadas = {x["@id"] for x in _lista(d["prov:wasDerivedFrom"])}
    assert derivadas == {s["url"] for s in _fuentes(fichero)}


def test_nodos_fuente_con_su_licencia_y_en_el_readme(nodos):
    por_url = {}
    for fichero in CON_META:
        for s in _fuentes(fichero):
            por_url.setdefault(s["url"], set()).add(s["licencia"])
    nodos_fuente = {n["@id"]: n for n in nodos if "dcat:Resource" in _tipos(n)}
    assert set(nodos_fuente) == set(por_url)
    readme = (RAIZ / "data" / "README.md").read_text(encoding="utf-8")
    for url, textos in por_url.items():
        assert set(_lista(nodos_fuente[url]["dct:license"])) == textos, url
        assert url in readme, f"{url} no está en data/README.md"


@pytest.mark.parametrize("fichero", SDM)
def test_sdm_deriva_de_su_origen_y_declara_su_esquema(distribuciones, fichero):
    (d,) = _distribucion(distribuciones, fichero)
    (origen,) = _lista(d["prov:wasDerivedFrom"])
    assert origen["@id"].removeprefix(BASE) in CON_META
    assert d["dct:conformsTo"]["@id"] == ESQUEMA_KPI


def _origen(d):
    (o,) = _lista(d["prov:wasDerivedFrom"])
    return o["@id"].removeprefix(BASE)


@pytest.mark.parametrize("fichero", FICHEROS)
def test_fecha_y_tamano_son_los_del_fichero(distribuciones, fichero):
    (d,) = _distribucion(distribuciones, fichero)
    generado = (
        _meta(_origen(d))["generado"] if fichero in SDM else _meta(fichero)["generado"]
    )
    assert d["dct:issued"] == {"@value": generado, "@type": "xsd:date"}
    assert d["dcat:byteSize"]["@value"] == (APP_DATOS / fichero).stat().st_size


@pytest.mark.parametrize("fichero", SDM)
def test_fecha_de_sdm_figura_en_su_leeme(distribuciones, fichero):
    (d,) = _distribucion(distribuciones, fichero)
    leeme = (APP_DATOS / "sdm" / "LEEME.md").read_text(encoding="utf-8")
    assert f"`{_origen(d)}`, generado el {d['dct:issued']['@value']}" in leeme


@pytest.mark.parametrize("fichero", CON_META)
def test_periodo_incluye_el_anio_del_dato(distribuciones, fichero):
    (d,) = _distribucion(distribuciones, fichero)
    t = d["dct:temporal"]
    inicio, fin = (int(t[k]["@value"][:4]) for k in ("dcat:startDate", "dcat:endDate"))
    assert inicio <= _meta(fichero)["anio_dato"] <= fin


@pytest.mark.parametrize("fichero", CON_META)
def test_cita_obligatoria_de_cada_publicador(distribuciones, fichero):
    (d,) = _distribucion(distribuciones, fichero)
    derechos = " ".join(r["rdfs:label"] for r in _lista(d["dct:rights"]))
    for s in _fuentes(fichero):
        for trozo, cita in CITAS.items():
            if trozo in s["url"]:
                assert cita in derechos, f"{fichero}: falta «{cita}»"
    if fichero in DERIVA_DE_OSM:
        assert CITAS["geofabrik.de"] in derechos


@pytest.mark.parametrize("fichero", SDM)
def test_cita_obligatoria_en_sdm(distribuciones, fichero):
    (d,) = _distribucion(distribuciones, fichero)
    derechos = " ".join(r["rdfs:label"] for r in _lista(d["dct:rights"]))
    assert CITAS["mivau.gob.es"] in derechos
    assert (CITAS["ine.es"] in derechos) == fichero.endswith("esfuerzo.json")
