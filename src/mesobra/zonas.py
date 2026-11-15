"""Las 199 zonas del plan: 178 municipios y los 21 distritos de Madrid capital.

Disuelve las secciones del seccionado INE a 1-1-2025 (el del ADRH 2024), pesa cada zona con la población
de la tabla 31105 del ADRH (2024), calcula el centro de población (media de los centroides de sus secciones
ponderada por población, medida en EPSG:25830) y le asigna la corona tarifaria del CRTM en la que cae
ese centro. Produce la tabla `zonas` (contrato en `contratos.py`).
"""

from pathlib import Path

import geopandas as gpd
import pandas as pd

from mesobra import contratos

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data/raw"
SECCIONADO = RAW / "ine_seccionado_2025_2026-11-15/SECC_CE_20250101.shp"
POBLACION = RAW / "ine_adrh_demograficos_madrid_2026-11-15.csv"
CORONAS = RAW / "crtm_coronas_2026-11-15.geojson"
PROCESSED = RAIZ / "data/processed"

MADRID = "28079"
ANIO_POBLACION = "2024"
CORONAS_CM = ("A", "B1", "B2", "B3", "C1", "C2")  # E1 y E2 están fuera de la Comunidad
# supuesto: corona dudosa si vive en ella menos del 90 % de la zona o el centro está a menos de 1 km del borde
CUOTA_MINIMA = 0.9
DISTANCIA_MINIMA_M = 1000
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


def _centros(secciones: gpd.GeoDataFrame) -> gpd.GeoSeries:
    """Media de los centroides de las secciones de cada zona, ponderada por población (EPSG:25830)."""
    centroide = secciones.centroid
    pesos = (
        pd.DataFrame(
            {
                "zona_id": secciones["zona_id"],
                "px": centroide.x * secciones["poblacion"],
                "py": centroide.y * secciones["poblacion"],
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
    secciones: gpd.GeoDataFrame, poblacion: pd.Series, coronas: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """Tabla `zonas`: una fila por municipio o distrito de Madrid, validada con su contrato."""
    secciones = secciones_por_zona(secciones, poblacion)
    centros = _centros(secciones)
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
    """Zonas cuya corona conviene revisar a mano: poca población en ella o centro cerca del borde.

    `secciones` es la salida de `secciones_por_zona`. La capa del CRTM son bandas que no siguen los
    términos municipales, así que se mide la cuota de población de la corona asignada, no la de área.
    """
    punto = gpd.GeoDataFrame(
        secciones[["zona_id", "poblacion"]], geometry=secciones.representative_point()
    )
    # shortcut: un punto en un solape de borde entre coronas (1 km² en total) cuenta en la primera
    en_corona = gpd.sjoin(punto, coronas, how="left", predicate="intersects")
    en_corona = en_corona[~en_corona.index.duplicated()]
    z = zona.set_index("zona_id")
    misma = en_corona["corona"].eq(en_corona["zona_id"].map(z["corona"]))
    cuota = (
        en_corona["poblacion"].where(misma, 0).groupby(en_corona["zona_id"]).sum()
        / z["poblacion"]
    )
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
            "cuota_poblacion": cuota.round(3),
            "distancia_borde_m": distancia.round(0),
        }
    )
    dudosa = (tabla["cuota_poblacion"] < CUOTA_MINIMA) | (
        tabla["distancia_borde_m"] < DISTANCIA_MINIMA_M
    )
    return tabla[dudosa].sort_values("cuota_poblacion")


def main() -> None:
    poblacion = poblacion_secciones()
    zona = zonas(leer_secciones(), poblacion, leer_coronas())
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
