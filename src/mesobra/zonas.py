"""Las 199 zonas del plan: 178 municipios y los 21 distritos de Madrid capital.

Disuelve las secciones del seccionado INE a 1-1-2025 (el del ADRH 2024), pesa cada zona con la población
de la tabla 31105 del ADRH (2024), calcula el centro de población (media de los puntos de población de sus
secciones ponderada por población, medida en EPSG:25830) y le asigna la corona tarifaria del CRTM en la que cae
ese centro. Produce la tabla `zonas` (contrato en `contratos.py`).

El punto de población de una sección es la media de los centroides de sus edificios de OpenStreetMap (© los
colaboradores de OpenStreetMap, ODbL), sin los que no son vivienda; una sección sin edificios usa su punto
representativo. El centroide geométrico no sirve: en una sección rural grande cae en el campo (#175).
"""

import logging
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

from mesobra import contratos

LOG = logging.getLogger(__name__)
RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data/raw"
SECCIONADO = RAW / "ine_seccionado_2025_2026-11-15/SECC_CE_20250101.shp"
POBLACION = RAW / "ine_adrh_demograficos_madrid_2026-11-15.csv"
CORONAS = RAW / "crtm_coronas_2026-11-15.geojson"
OSM = RAW / "osm_madrid_2026-11-15.pbf"
# supuesto: estos valores de `building` no son vivienda; `yes` (sin tipo) sí cuenta, porque es el más frecuente
NO_VIVIENDA = (
    "industrial", "warehouse", "commercial", "retail", "office", "farm_auxiliary", "barn",
    "shed", "garage", "garages", "roof", "greenhouse", "hangar", "construction", "ruins",
    "service", "transformer_tower", "parking", "church", "chapel", "school", "hospital",
    "university", "sports_hall", "stadium", "kiosk", "no",
)  # fmt: skip
PROCESSED = RAIZ / "data/processed"

MADRID = "28079"
ANIO_POBLACION = "2024"
CORONAS_CM = ("A", "B1", "B2", "B3", "C1", "C2")  # E1 y E2 están fuera de la Comunidad
# supuesto: corona dudosa si vive en ella menos del 90 % de la zona o el centro está a menos de 1 km del borde
CUOTA_MINIMA = 0.9
DISTANCIA_MINIMA_M = 1000
# supuesto: un centro a más de 1 km de todo punto de población de su zona está en un hueco entre núcleos
HUECO_MAX_M = 1000
# Nombres oficiales de los distritos (Ayuntamiento de Madrid, Distritos.csv del geoportal); el INE solo da el código
DISTRITOS = {
    "01": "Centro",
    "02": "Arganzuela",
    "03": "Retiro",
    "04": "Salamanca",
    "05": "Chamartín",
    "06": "Tetuán",
    "07": "Chamberí",
    "08": "Fuencarral-El Pardo",
    "09": "Moncloa-Aravaca",
    "10": "Latina",
    "11": "Carabanchel",
    "12": "Usera",
    "13": "Puente de Vallecas",
    "14": "Moratalaz",
    "15": "Ciudad Lineal",
    "16": "Hortaleza",
    "17": "Villaverde",
    "18": "Villa de Vallecas",
    "19": "Vicálvaro",
    "20": "San Blas-Canillejas",
    "21": "Barajas",
}


def _entero(serie: pd.Series) -> pd.Series:
    """Entero en formato español ("6.995.318"); un valor ilegible falla, nunca se convierte en nulo."""
    return pd.to_numeric(serie.str.replace(".", ""), errors="raise")


def poblacion_secciones(ruta: Path = POBLACION) -> pd.Series:
    """Población 2024 por sección (`CUSEC` → personas); comprueba que suma lo mismo que los municipios."""
    df = pd.read_csv(ruta, sep=";", dtype=str, encoding="utf-8-sig")
    df = df[
        (df["Indicadores demográficos"] == "Población")
        & (df["Periodo"] == ANIO_POBLACION)
    ]
    if (df["Total"] == ".").any():
        raise ValueError(f"Población sin dato («.») en {ruta.name}")
    # una sección sin valor en 2024 ya no existe en ese seccionado; zonas() exige luego el mismo conjunto
    secciones = df[df["Secciones"].notna() & df["Total"].notna()]
    municipios = df[df["Distritos"].isna()]
    poblacion = pd.Series(
        _entero(secciones["Total"]).to_numpy(),
        index=secciones["Secciones"].str.split(" ").str[0].rename("CUSEC"),
        name="poblacion",
    )
    if not poblacion.index.is_unique:
        raise ValueError("Secciones repetidas en la tabla de población")
    if (total := _entero(municipios["Total"]).sum()) != poblacion.sum():
        raise ValueError(
            f"Las secciones suman {poblacion.sum()} y los municipios {total}"
        )
    return poblacion


def leer_secciones(ruta: Path = SECCIONADO) -> gpd.GeoDataFrame:
    """Secciones de la Comunidad de Madrid (`CPRO = 28`) en EPSG:25830."""
    secciones = gpd.read_file(
        # el `where` de pyogrio solo filtra por columnas leídas: sin CPRO devuelve 0 filas sin avisar
        ruta,
        where="CPRO = '28'",
        columns=["CPRO", "CUSEC", "CUMUN", "CDIS", "NMUN"],
    )
    if secciones.empty:
        raise ValueError(f"{ruta.name} no tiene secciones con CPRO = 28")
    if secciones.crs is None or secciones.crs.to_epsg() != 25830:
        raise ValueError(f"Se esperaba EPSG:25830 en {ruta.name} y hay {secciones.crs}")
    return secciones


def leer_coronas(ruta: Path = CORONAS) -> gpd.GeoDataFrame:
    """Coronas del CRTM (`corona`, polígono) en EPSG:25830; el fichero viene en EPSG:3857."""
    coronas = gpd.read_file(ruta, columns=["CCORONATAR"])
    if coronas.crs is None:
        raise ValueError(f"{ruta.name} no declara CRS")
    coronas = coronas.rename(columns={"CCORONATAR": "corona"}).to_crs(25830)
    coronas["geometry"] = coronas.make_valid()  # la capa trae anillos no válidos
    return coronas


def comprobar_distritos(secciones: gpd.GeoDataFrame) -> None:
    """Los distritos censales de Madrid son los 21 municipales y cada sección lleva su prefijo (F0-05)."""
    madrid = secciones[secciones["CUMUN"] == MADRID]
    distritos = set(madrid["CDIS"])
    prefijo_mal = madrid["CUSEC"].str[5:7] != madrid["CDIS"]
    if distritos != set(DISTRITOS) or prefijo_mal.any():
        raise ValueError(
            f"Los distritos censales de Madrid no son los 21 municipales: {sorted(distritos)}, "
            f"{int(prefijo_mal.sum())} secciones con otro prefijo. Plan B de #71: capas del SERPAVI"
        )


def leer_edificios(ruta: Path = OSM) -> gpd.GeoSeries:
    """Centroides (EPSG:25830) de los edificios de OpenStreetMap que pueden ser vivienda (sin `NO_VIVIENDA`)."""
    edificios = gpd.read_file(
        ruta, layer="multipolygons", columns=["building"], where="building IS NOT NULL"
    )
    edificios = edificios[~edificios["building"].isin(NO_VIVIENDA)]
    if edificios.empty:
        raise ValueError(
            f"{ruta.name} no tiene edificios de vivienda en la capa multipolygons"
        )
    return edificios.to_crs(25830).centroid.reset_index(drop=True)


def puntos_poblacion(
    secciones: gpd.GeoDataFrame, edificios: gpd.GeoSeries
) -> gpd.GeoSeries:
    """Punto de población de cada sección, siempre dentro de ella.

    Es la media de sus edificios; si cae fuera de la sección, el edificio más cercano a esa media; y si la sección
    no tiene edificios, su punto representativo.
    """
    dentro = gpd.sjoin(
        gpd.GeoDataFrame(geometry=edificios.to_crs(secciones.crs)),
        secciones[["geometry"]],
        predicate="within",
    )
    media = (
        dentro.assign(x=dentro.geometry.x, y=dentro.geometry.y)
        .groupby("index_right")[["x", "y"]]
        .mean()
    )
    centro = gpd.GeoSeries.from_xy(
        media["x"], media["y"], crs=secciones.crs, index=media.index
    )
    # sección con varios núcleos (Puentes Viejas): la media cae entre ellos; se usa el edificio más cercano
    fuera = centro.index[~centro.within(secciones.geometry.loc[centro.index])]
    if fuera.size:
        cand = dentro[dentro["index_right"].isin(fuera)]
        distancia = cand.distance(centro.loc[cand["index_right"]].set_axis(cand.index))
        cercano = distancia.groupby(cand["index_right"]).idxmin()
        centro.loc[cercano.index] = cand.geometry.loc[cercano.to_numpy()].set_axis(
            cercano.index
        )
    puntos = secciones.representative_point()
    puntos.loc[centro.index] = centro
    if (sin := secciones.index.difference(centro.index)).size:
        # un PBF incompleto degradaría el punto sin fallar: que se vea cuántas secciones caen al respaldo
        LOG.info(
            "%d secciones sin edificios usan su punto representativo: %s",
            sin.size,
            secciones.loc[sin, "CUSEC"].tolist(),
        )
    return puntos


def _centros(secciones: gpd.GeoDataFrame, puntos: gpd.GeoSeries) -> gpd.GeoSeries:
    """Media de los puntos de población de las secciones de cada zona, ponderada por población (EPSG:25830)."""
    pesos = (
        pd.DataFrame(
            {
                "zona_id": secciones["zona_id"],
                "px": puntos.x * secciones["poblacion"],
                "py": puntos.y * secciones["poblacion"],
                "p": secciones["poblacion"],
            }
        )
        .groupby("zona_id")[["px", "py", "p"]]
        .sum()
    )
    if (vacias := pesos.index[pesos["p"] <= 0]).size:
        raise ValueError(f"Zonas sin población: {vacias.tolist()}")
    return gpd.GeoSeries.from_xy(
        pesos["px"] / pesos["p"],
        pesos["py"] / pesos["p"],
        crs=secciones.crs,
        index=pesos.index,
    )


def _en_un_nucleo(
    secciones: gpd.GeoDataFrame,
    puntos: gpd.GeoSeries,
    centros: gpd.GeoSeries,
    zona: gpd.GeoDataFrame,
) -> gpd.GeoSeries:
    """Si el centro cae fuera de su zona o en un hueco, lo lleva al punto de población más central de la zona.

    En un municipio de varios núcleos (Puentes Viejas, El Escorial) la media cae entre ellos, lejos de todo
    punto de población; a más de `HUECO_MAX_M` se considera hueco. El más central es el punto de sección que
    minimiza la distancia ponderada por población a las demás secciones: el pueblo grande, no un diseminado.
    """
    zona_de = secciones["zona_id"]
    distancia = puntos.distance(centros.reindex(zona_de).set_axis(puntos.index))
    hueco = distancia.groupby(zona_de).min().reindex(zona.index) > HUECO_MAX_M
    mover = zona.index[~centros.within(zona.geometry) | hueco]
    if mover.size:
        LOG.warning(
            "Centro fuera de un núcleo, pasa al más central: %s", mover.tolist()
        )
    centros = centros.copy()
    for zona_id in mover:  # pocas zonas; cada una, vectorizada
        propios = puntos[zona_de == zona_id]
        xy = np.column_stack([propios.x, propios.y])
        d = np.hypot(*(xy[:, None, :] - xy[None, :, :]).transpose(2, 0, 1))
        peso = secciones.loc[propios.index, "poblacion"].to_numpy(dtype=float)
        centros.loc[zona_id] = propios.iloc[int(np.argmin(d @ peso))]
    return centros


def _corona(centros: gpd.GeoSeries, coronas: gpd.GeoDataFrame) -> pd.Series:
    """Corona en la que cae cada centro; ninguna, varias o una fuera de la Comunidad es un error."""
    union = gpd.sjoin(
        gpd.GeoDataFrame(geometry=centros), coronas, how="left", predicate="intersects"
    )
    if not union.index.is_unique:
        raise ValueError(
            f"Centros en dos coronas: {union.index[union.index.duplicated()].tolist()}"
        )
    if (mal := union.index[~union["corona"].isin(CORONAS_CM)]).size:
        raise ValueError(
            f"Centros sin corona de la Comunidad: {union.loc[mal, 'corona'].to_dict()}"
        )
    return union["corona"]


def secciones_por_zona(
    secciones: gpd.GeoDataFrame, poblacion: pd.Series
) -> gpd.GeoDataFrame:
    """Secciones con su población, `zona_id`, `nombre` y `tipo` de zona."""
    comprobar_distritos(secciones)
    if set(secciones["CUSEC"]) != set(poblacion.index):
        faltan = set(secciones["CUSEC"]) ^ set(poblacion.index)
        raise ValueError(
            f"Secciones y población no casan: {len(faltan)}, p. ej. {sorted(faltan)[:5]}"
        )
    secciones = secciones.merge(
        poblacion, left_on="CUSEC", right_index=True, validate="one_to_one"
    )
    es_madrid = secciones["CUMUN"] == MADRID
    return secciones.assign(
        zona_id=secciones["CUMUN"].where(
            ~es_madrid, secciones["CUMUN"] + secciones["CDIS"]
        ),
        nombre=secciones["NMUN"].where(~es_madrid, secciones["CDIS"].map(DISTRITOS)),
        tipo=es_madrid.map({True: "distrito", False: "municipio"}),
    )


def zonas(
    secciones: gpd.GeoDataFrame,
    poblacion: pd.Series,
    coronas: gpd.GeoDataFrame,
    edificios: gpd.GeoSeries,
) -> gpd.GeoDataFrame:
    """Tabla `zonas`: una fila por municipio o distrito de Madrid, validada con su contrato."""
    secciones = secciones_por_zona(secciones, poblacion)
    puntos = puntos_poblacion(secciones, edificios)
    centros = _centros(secciones, puntos)
    zona = secciones.dissolve(
        "zona_id",
        aggfunc={
            "CUMUN": "first",
            "nombre": "first",
            "tipo": "first",
            "poblacion": "sum",
        },
    )
    # en una zona cóncava o partida el centro podría caer en el vecino y tomar su corona
    centros = _en_un_nucleo(secciones, puntos, centros, zona)
    if (fuera := zona.index[~centros.within(zona.geometry)]).size:
        raise ValueError(f"Centros fuera de su zona: {fuera.tolist()}")
    lonlat = centros.to_crs(4326)
    zona = zona.assign(
        corona=_corona(centros, coronas),
        lon_centro=lonlat.x,
        lat_centro=lonlat.y,
    ).rename(columns={"CUMUN": "municipio_id"})
    zona = zona.reset_index()[list(contratos.CONTRATOS["zonas"]["columnas"])]
    zona = zona.astype(
        {c: t for c, t in contratos.dtypes("zonas").items() if c != "geometry"}
    )
    contratos.validar(zona, "zonas")
    return zona


def coronas_dudosas(
    secciones: gpd.GeoDataFrame, zona: gpd.GeoDataFrame, coronas: gpd.GeoDataFrame
) -> pd.DataFrame:
    """Zonas cuya corona conviene revisar a mano.

    Dudosa si vive en la corona asignada menos de `CUOTA_MINIMA` de la población por cualquiera de dos
    vías (cada sección entera en su punto representativo, o repartida por área entre las coronas que la
    cortan; ninguna es la verdad y así la lista no depende del método) o si el centro está a menos de
    `DISTANCIA_MINIMA_M` del borde de su corona (el límite exterior de la capa cuenta como borde).
    `secciones` es la salida de `secciones_por_zona`. Los distritos de Madrid pueden salir aunque la
    norma los ponga a todos en A: la capa del CRTM son bandas que no siguen los términos municipales.
    """
    z = zona.set_index("zona_id")
    punto = gpd.GeoDataFrame(
        secciones[["zona_id", "poblacion"]], geometry=secciones.representative_point()
    )
    # shortcut: en un solape de borde entre coronas (1 km² en total) un punto cuenta en la primera y un
    # trozo, en las dos (cubre hasta el 100,4 % de su sección); quitar los solapes si la capa empeora
    en_punto = gpd.sjoin(punto, coronas, how="left", predicate="intersects")
    en_punto = en_punto[~en_punto.index.duplicated()]
    trozos = gpd.overlay(
        secciones[["CUSEC", "zona_id", "poblacion", "geometry"]],
        coronas,
        how="intersection",
        keep_geom_type=False,  # los contactos entre bordes salen como líneas de área 0
    )
    area = secciones.set_index("CUSEC").area
    trozos["poblacion"] = (
        trozos["poblacion"] * trozos.area / trozos["CUSEC"].map(area).to_numpy()
    )
    cuotas = {
        nombre: df["poblacion"]
        .where(df["corona"].eq(df["zona_id"].map(z["corona"])), 0)
        .groupby(df["zona_id"])
        .sum()
        .reindex(
            z.index, fill_value=0
        )  # una zona sin trozo en ninguna corona tiene cuota 0
        / z["poblacion"]
        for nombre, df in {"cuota_punto": en_punto, "cuota_area": trozos}.items()
    }
    centros = gpd.GeoSeries.from_xy(
        z["lon_centro"], z["lat_centro"], crs=4326, index=z.index
    ).to_crs(coronas.crs)
    borde = coronas.set_index("corona").boundary
    distancia = centros.distance(
        gpd.GeoSeries(borde.loc[z["corona"]].values, index=z.index)
    )
    tabla = pd.DataFrame(
        {
            "nombre": z["nombre"],
            "corona": z["corona"],
            **cuotas,
            "distancia_borde_m": distancia,
        }
    )
    dudosa = (tabla[list(cuotas)].min(axis=1) < CUOTA_MINIMA) | (
        tabla["distancia_borde_m"] < DISTANCIA_MINIMA_M
    )
    redondeo = {"cuota_punto": 3, "cuota_area": 3, "distancia_borde_m": 0}
    return tabla[dudosa].round(redondeo).sort_values("cuota_punto")


def main() -> None:
    poblacion = poblacion_secciones()
    zona = zonas(leer_secciones(), poblacion, leer_coronas(), leer_edificios())
    distritos = zona[zona["tipo"] == "distrito"]
    if len(zona) != 199 or len(distritos) != 21:
        raise ValueError(
            f"Se esperaban 199 zonas y 21 distritos: {len(zona)}, {len(distritos)}"
        )
    if (distritos["corona"] != "A").any():
        raise ValueError(
            f"Distritos fuera de la corona A:\n{distritos[distritos['corona'] != 'A']}"
        )
    if zona["poblacion"].sum() != poblacion.sum():
        raise ValueError(
            f"Población no conservada: {zona['poblacion'].sum()} != {poblacion.sum()}"
        )
    PROCESSED.mkdir(parents=True, exist_ok=True)
    zona.to_parquet(PROCESSED / "zonas.parquet")


if __name__ == "__main__":
    main()
