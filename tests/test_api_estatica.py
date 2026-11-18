"""Contrato de la API estática: los ejemplos lo cumplen, `validar` detecta cada incumplimiento y `escribir` es seguro."""

import copy
import json
import warnings
from pathlib import Path

import pandas as pd
import pytest

from mesobra.api_estatica import FICHEROS, escribir, validar

RAIZ = Path(__file__).parent
EJEMPLOS = RAIZ / "fixtures" / "api"
PROCESSED = RAIZ / "fixtures" / "processed"
APP_DATOS = RAIZ.parent / "app" / "datos"
ZONAS = ["2807901", "2807913", "28065", "28092", "28001"]


def _leer(nombre, carpeta=EJEMPLOS):
    return json.loads((carpeta / nombre).read_text(encoding="utf-8"))


def _csv(nombre):
    return pd.read_csv(
        PROCESSED / f"{nombre}.csv", dtype={"zona_id": str, "destino_id": str}
    )


@pytest.mark.parametrize("nombre", FICHEROS)
def test_ejemplo_cumple_su_contrato(nombre):
    validar(nombre, _leer(nombre), _leer("zonas.geojson"))


def test_las_cinco_zonas():
    zonas = _leer("zonas.geojson")
    assert [f["properties"]["zona_id"] for f in zonas["features"]] == ZONAS
    assert list(_leer("alquiler.json")["zonas"]) == ZONAS
    assert _leer("tiempos.json")["origenes"] == ZONAS


def test_alquiler_coincide_con_processed():
    esperado = _csv("alquiler_zona").set_index("zona_id")
    for zona, z in _leer("alquiler.json")["zonas"].items():
        fila = esperado.loc[zona]
        for clave, col in (
            ("p25", "eur_m2_p25"),
            ("p50", "eur_m2_p50"),
            ("p75", "eur_m2_p75"),
        ):
            assert pd.isna(fila[col]) if z[clave] is None else z[clave] == fila[col]


def test_tp_coincide_con_processed():
    t = _leer("tiempos.json")
    esperado = (
        _csv("tiempos")
        .query("modo == 'tp'")
        .set_index(["zona_id", "destino_id"])["minutos"]
    )
    for i, origen in enumerate(t["origenes"]):
        for j, destino in enumerate(d["destino_id"] for d in t["destinos"]):
            v = esperado[(origen, destino)]
            assert pd.isna(v) if t["tp"][i][j] is None else t["tp"][i][j] == v


def _modificar(nombre, ruta, valor=...):
    """Copia del ejemplo con `valor` en `ruta` («.» separa claves; en una lista, el número es un índice); sin valor, la quita."""
    raiz = copy.deepcopy(_leer(nombre))
    *camino, ultimo = ruta.split(".")
    nodo = raiz
    for k in camino:
        nodo = nodo[int(k) if isinstance(nodo, list) else k]
    ultimo = int(ultimo) if isinstance(nodo, list) else ultimo
    if valor is ...:
        del nodo[ultimo]
    else:
        nodo[ultimo] = valor
    return raiz


def _anillo(*pos):
    return [list(pos) + [pos[0]]]


UTM = _anillo(
    [440000, 4474000], [441000, 4474000], [441000, 4475000], [440000, 4475000]
)
BIEN = [[-3.7, 40.4], [-3.6, 40.4], [-3.6, 40.5], [-3.7, 40.4]]
MADRID = {
    "zona_id": "28079",
    "nombre": "Madrid",
    "tipo": "municipio",
    "municipio_id": "28079",
    "corona": "A",
    "poblacion": 3400000,
}
# fmt: off
# nombre, fichero, ruta del cambio (sin valor: se quita la clave), valor, mensaje esperado
FALLOS = [
    ("ipc_hasta con formato del INE", "alquiler.json", "meta.ipc_hasta", "2026M10", "meta.ipc_hasta: se esperaba mes"),
    ("ejemplo que no es booleano", "alquiler.json", "meta.ejemplo", "sí", "meta.ejemplo: se esperaba booleano"),
    ("zona_id desconocido", "tiempos.json", "origenes.0", "28999", "desconocidos"),
    ("NaN", "tiempos.json", "km_coche.0.0", float("nan"), "km_coche.*NaN, usa null"),
    ("sin fuentes", "netos.json", "meta.fuentes", [], "meta.fuentes: se esperaba una lista no vacía"),
    ("texto vacío", "hogares.json", "meta.fuentes.0.nombre", "  ", "se esperaba texto"),
    ("vértice en EPSG:25830", "zonas.geojson", "features.0.geometry.coordinates", UTM, "vértices fuera de la Comunidad"),
    ("bbox", "zonas.geojson", "bbox", [1, 2, 3, 4], r"sobran claves \['bbox'\]"),
    ("id de feature", "zonas.geojson", "features.0.id", "2807901", r"sobran claves \['id'\]"),
    ("vértice 3D", "zonas.geojson", "features.0.geometry.coordinates", [[[-3.7, 40.4, 0], *BIEN[1:]]], "al menos 4 posiciones"),
    ("coordenada en texto", "zonas.geojson", "features.0.geometry.coordinates", [[["-3.7", "40.4"], *BIEN[1:]]], "al menos 4 posiciones"),
    ("anillo abierto", "zonas.geojson", "features.0.geometry.coordinates", [[*BIEN[:3], [-3.7, 40.5]]], "anillo abierto"),
    ("Polygon con coordenadas de MultiPolygon", "zonas.geojson", "features.0.geometry.coordinates", [[BIEN]], "al menos 4 posiciones"),
    ("MultiPolygon con coordenadas de Polygon", "zonas.geojson", "features.0.geometry.type", "MultiPolygon", "al menos 4 posiciones"),
    ("municipio de otra comunidad", "zonas.geojson", "features.2.properties.municipio_id", "08019", "municipio_id: se esperaba municipio"),
    ("anio fuera de rango", "analisis.json", "esfuerzo.0.anio", 1, "fuera del rango"),
    ("municipio con zona_id distinto", "zonas.geojson", "features.2.properties.zona_id", "28066", "no casan con tipo municipio"),
    ("Madrid entero como municipio", "zonas.geojson", "features.2.properties", MADRID, "no casan con tipo municipio"),
    ("distrito inexistente", "zonas.geojson", "features.0.properties.zona_id", "2807999", "zona_id: se esperaba zona"),
    ("municipio_id que no casa con el distrito", "zonas.geojson", "features.0.properties.municipio_id", "28001", "no casan con tipo distrito"),
    ("cesta_uc ausente", "hogares.json", "cesta_uc", ..., r"faltan claves \['cesta_uc'\]"),
    ("cesta_uc negativa", "hogares.json", "cesta_uc.suministros", -1, "fuera del rango"),
    ("orden de coronas", "tarifas.json", "orden_coronas", ["B1", "A"], "debe seguir el orden de CORONAS"),
    ("semanas_mes fuera de rango", "tarifas.json", "semanas_mes", 7, "fuera del rango"),
    ("feature que no es objeto", "zonas.geojson", "features.0", 5, r"features\[0\]: se esperaba un objeto"),
    ("matriz mal dimensionada", "tiempos.json", "tp.0", [9], r"tp\[0\]: se esperaban 2 columnas"),
    ("p25 > p50", "alquiler.json", "zonas.28065.p25", 13.0, "p25 <= p50 <= p75"),
    ("sin_dato con percentiles", "alquiler.json", "zonas.28065.origen", "sin_dato", "origen: sin_dato si y solo si"),
    ("neto mayor que el bruto", "netos.json", "neto_anual.0.0", 16000.0, "mayor que el bruto 15000"),
    ("corona que falta", "tarifas.json", "escenarios.vigente_2026.general.2.B1", ..., r"faltan claves \['B1'\]"),
    ("viajes_dia que falta", "tarifas.json", "escenarios.vigente_2026.general.4", ..., r"faltan claves \['4'\]"),
    ("viajes_dia de la raíz incompleto", "tarifas.json", "viajes_dia", [2], "viajes_dia: .* no está en"),
    ("municipio_id de distrito", "zonas.geojson", "features.0.properties.municipio_id", "2807901", "municipio_id: se esperaba municipio"),
]
# fmt: on


@pytest.mark.parametrize(
    ("fichero", "ruta", "valor", "mensaje"),
    [f[1:] for f in FALLOS],
    ids=[f[0] for f in FALLOS],
)
def test_falla_con_su_mensaje(fichero, ruta, valor, mensaje):
    with pytest.raises(ValueError, match=mensaje):
        validar(fichero, _modificar(fichero, ruta, valor), _leer("zonas.geojson"))


def test_fichero_fuera_del_contrato():
    with pytest.raises(ValueError, match="fuera del contrato"):
        validar("otro.json", {})


def test_escribir_json_compacto_utf8(tmp_path):
    zonas = _leer("zonas.geojson")
    destino = escribir("zonas.geojson", zonas, tmp_path)
    texto = destino.read_text(encoding="utf-8")
    assert json.loads(texto) == zonas
    assert "Móstoles" in texto
    assert ": " not in texto.split('"features"')[0]
    assert "\n" not in texto


def test_escribir_nan_como_null(tmp_path):
    tiempos = _modificar("tiempos.json", "km_coche.0.0", float("nan"))
    destino = escribir("tiempos.json", tiempos, tmp_path)
    assert json.loads(destino.read_text(encoding="utf-8"))["km_coche"][0][0] is None


def test_escribir_no_crea_nada_si_no_valida(tmp_path):
    with pytest.raises(ValueError, match="meta.fuentes"):
        escribir("netos.json", _modificar("netos.json", "meta.fuentes", []), tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_escribir_comprueba_ids_con_las_zonas_de_la_carpeta(tmp_path):
    escribir("zonas.geojson", _leer("zonas.geojson"), tmp_path)
    with pytest.raises(ValueError, match="desconocidos"):
        escribir(
            "tiempos.json", _modificar("tiempos.json", "origenes.0", "28999"), tmp_path
        )
    assert not (tmp_path / "tiempos.json").exists()
    escribir("tiempos.json", _leer("tiempos.json"), tmp_path)


def test_app_datos_cumple_el_contrato():
    if not APP_DATOS.exists():
        pytest.skip("app/datos/ todavía no existe")
    ficheros = sorted([*APP_DATOS.glob("*.json"), *APP_DATOS.glob("*.geojson")])
    zonas = (
        _leer("zonas.geojson", APP_DATOS)
        if (APP_DATOS / "zonas.geojson").exists()
        else None
    )
    if ficheros and zonas is None:
        warnings.warn(
            "app/datos/ sin zonas.geojson: no se comprueban los zona_id", stacklevel=1
        )
    for fichero in ficheros:
        datos = _leer(fichero.name, APP_DATOS)
        validar(fichero.name, datos, zonas)
        # La marca es solo de las fixtures: en datos reales quitaría las fuentes de la leyenda sin avisar.
        assert "ejemplo" not in datos["meta"], fichero.name
