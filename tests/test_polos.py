"""`mesobra.polos`: validación del CSV, polos dentro de la Comunidad y corona de cada polo."""

from pathlib import Path

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box

from mesobra import polos, zonas

ZONAS_GEOJSON = Path(__file__).parent.parent / "app" / "datos" / "zonas.geojson"


def _fila(slug: str = "uno", lon: float = 0.5, lat: float = 0.5) -> dict[str, str]:
    return {
        "slug": slug,
        "nombre": slug.title(),
        "tipo": "hospital",
        "lon": str(lon),
        "lat": str(lat),
        "osm_id": "way/1",
        "motivo": "prueba",
    }


def _csv(tmp_path: Path, filas: list[dict[str, str]]) -> Path:
    ruta = tmp_path / "polos.csv"
    pd.DataFrame(filas, columns=polos.COLUMNAS).to_csv(ruta, index=False)
    return ruta


def _zonas() -> gpd.GeoDataFrame:
    """Dos zonas contiguas en EPSG:4326: `A` (x de 0 a 1) y `B` (x de 1 a 2)."""
    return gpd.GeoDataFrame(
        {"zona_id": ["A", "B"]}, geometry=[box(0, 0, 1, 1), box(1, 0, 2, 1)], crs=4326
    )


def test_polos_reales_traen_los_lugares_de_los_personajes():
    lista = polos.leer()
    assert 10 <= len(lista) <= 20
    assert lista["slug"].is_unique
    assert {"hospital-la-paz", "hospital-12-de-octubre"} <= set(lista["slug"])
    assert (
        lista["tipo"] == "poligono_industrial"
    ).any()  # el polígono del sur de la ficha §3
    assert (lista["destino_id"] == "polo:" + lista["slug"]).all()


def test_polos_reales_caen_dentro_del_contorno_de_la_comunidad():
    if not ZONAS_GEOJSON.exists():
        pytest.skip("app/datos/zonas.geojson todavía no existe")
    lista = polos.ubicar(
        polos.leer(), gpd.read_file(ZONAS_GEOJSON)
    )  # falla si cae alguno fuera
    assert lista["zona_id"].notna().all()


def test_la_corona_del_polo_es_la_de_su_zona():
    if not (ZONAS_GEOJSON.exists() and zonas.CORONAS.exists()):
        pytest.skip(
            "faltan app/datos/zonas.geojson o la capa de coronas del CRTM en data/raw"
        )
    capa = gpd.read_file(ZONAS_GEOJSON)
    lista = polos.ubicar(polos.leer(), capa)
    puntos = gpd.GeoDataFrame(
        lista[["destino_id"]],
        geometry=gpd.points_from_xy(lista["lon"], lista["lat"], crs=4326),
    ).to_crs(25830)
    del_punto = gpd.sjoin(puntos, zonas.leer_coronas(), predicate="intersects")[
        "corona"
    ]
    de_la_zona = lista["zona_id"].map(capa.set_index("zona_id")["corona"])
    assert (del_punto == de_la_zona.loc[del_punto.index]).all()


def test_leer_rechaza_slug_repetido(tmp_path):
    ruta = _csv(tmp_path, [_fila("uno"), _fila("uno")])
    with pytest.raises(ValueError, match="slug repetido"):
        polos.leer(ruta)


@pytest.mark.parametrize("slug", ["Con Mayusculas", "con espacio", "tilde-é"])
def test_leer_rechaza_slug_que_no_vale_en_polo_slug(tmp_path, slug):
    with pytest.raises(ValueError, match="slug no válido"):
        polos.leer(_csv(tmp_path, [_fila(slug)]))


def test_leer_rechaza_osm_id_mal_formado(tmp_path):
    fila = _fila() | {"osm_id": "node/abc"}
    with pytest.raises(ValueError, match="osm_id no válido"):
        polos.leer(_csv(tmp_path, [fila]))


def test_leer_rechaza_celdas_sin_valor_y_columnas_distintas(tmp_path):
    with pytest.raises(ValueError, match="sin valor"):
        polos.leer(_csv(tmp_path, [_fila() | {"motivo": ""}]))
    ruta = tmp_path / "mal.csv"
    ruta.write_text("slug,nombre\nuno,Uno\n", encoding="utf-8")
    with pytest.raises(ValueError, match="columnas"):
        polos.leer(ruta)


def test_leer_rechaza_coordenadas_que_no_son_numeros(tmp_path):
    with pytest.raises(ValueError):
        polos.leer(_csv(tmp_path, [_fila(lon="este")]))


def test_ubicar_asigna_la_zona_donde_cae(tmp_path):
    lista = polos.leer(_csv(tmp_path, [_fila("a", 0.5), _fila("b", 1.5)]))
    ubicados = polos.ubicar(lista, _zonas())
    assert ubicados["zona_id"].tolist() == ["A", "B"]


def test_ubicar_acepta_zonas_en_metros(tmp_path):
    lista = polos.leer(_csv(tmp_path, [_fila("a", 0.5)]))
    assert polos.ubicar(lista, _zonas().to_crs(25830))["zona_id"].tolist() == ["A"]


def test_ubicar_rechaza_un_polo_fuera_de_las_zonas(tmp_path):
    lista = polos.leer(_csv(tmp_path, [_fila("a", 0.5), _fila("lejos", 5.0)]))
    with pytest.raises(ValueError, match=r"fuera.*polo:lejos"):
        polos.ubicar(lista, _zonas())


def test_ubicar_rechaza_un_polo_en_el_borde_de_dos_zonas(tmp_path):
    lista = polos.leer(_csv(tmp_path, [_fila("borde", 1.0)]))
    with pytest.raises(ValueError, match=r"borde.*polo:borde"):
        polos.ubicar(lista, _zonas())
