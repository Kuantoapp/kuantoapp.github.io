"""Tabla de paso de las secciones censales de 2021 (las del SERPAVI) a las del INE a 1-1-2025 (las del ADRH 2024).

El INE no publica una correspondencia entre seccionados, así que se construye superponiendo las dos capas. Peso
dasimétrico (#167): dentro de cada sección de 2025 se supone la población repartida por igual en su superficie, y
la población de cada pieza `origen ∩ destino` es la de su destino por la fracción de área que ocupa la pieza.
Solo se conoce la población del seccionado de destino (tabla 31105), por eso la auxiliar es la suya.

`peso` suma 1 por origen: reparte las variables extensivas (testigos, viviendas). `peso_destino` suma 1 por
destino: pondera las intensivas (€/m²); nunca se suman.
"""

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

from mesobra import zonas

RAIZ = Path(__file__).resolve().parents[2]
ORIGEN = RAIZ / "data/raw/serpavi_capa_secciones_2026-11-16/ALQ_Secciones_2022_Web.shp"
# supuesto: una pieza menor que esta fracción del origen es borde que no coincide entre fuentes, no una partición
ASTILLA = 0.001
# supuesto: un origen o destino con un peso máximo menor que esto está partido o fusionado
ENTERA = 0.99
# tolerancia fijada de antemano para el total conservado por municipio (relativa; solo error de coma flotante)
TOLERANCIA_TOTAL = 1e-9
CRS_METRICO = 25830


def leer_origen(ruta: Path = ORIGEN) -> gpd.GeoDataFrame:
    """Secciones de 2021 de la Comunidad de Madrid (`CPRO = 28`) en EPSG:25830; el fichero viene en EPSG:3857."""
    origen = gpd.read_file(
        ruta, where="CPRO = '28'", columns=["CPRO", "CUSEC", "CUMUN", "Num_VC"]
    )
    if origen.empty:
        raise ValueError(f"{ruta.name} no tiene secciones con CPRO = 28")
    if origen.crs is None:
        raise ValueError(f"{ruta.name} no declara CRS")
    if not origen["CUSEC"].is_unique:
        raise ValueError(f"Secciones repetidas en {ruta.name}")
    return origen.to_crs(CRS_METRICO)


def tabla_paso(
    origen: gpd.GeoDataFrame, destino: gpd.GeoDataFrame, poblacion: pd.Series
) -> tuple[pd.DataFrame, pd.Series]:
    """Tabla `origen, destino, peso, peso_destino, metodo` y cobertura (fracción del área de cada origen que cae en destino).

    `origen` y `destino` llevan `CUSEC` y geometría en EPSG:25830; `poblacion` es `CUSEC` de destino → personas.
    Un origen cuyos destinos suman población 0 se reparte por área (`metodo = "area"`), declarado en la tabla.
    """
    if origen.crs.to_epsg() != CRS_METRICO or destino.crs.to_epsg() != CRS_METRICO:
        raise ValueError(f"Origen y destino deben estar en EPSG:{CRS_METRICO}")
    if set(destino["CUSEC"]) != set(poblacion.index):
        raise ValueError(
            "La población y el seccionado de destino no tienen las mismas secciones"
        )
    o = origen[["CUSEC", "geometry"]].rename(columns={"CUSEC": "origen"})
    d = destino[["CUSEC", "geometry"]].rename(columns={"CUSEC": "destino"})
    piezas = gpd.overlay(o, d, how="intersection", keep_geom_type=True)
    piezas["area"] = piezas.area
    area_o = o.set_index("origen").area
    area_d = d.set_index("destino").area
    cobertura = (
        piezas.groupby("origen")["area"].sum().reindex(area_o.index, fill_value=0)
        / area_o
    )
    piezas = piezas[piezas["area"] >= ASTILLA * piezas["origen"].map(area_o)]
    piezas["a"] = (
        poblacion.reindex(piezas["destino"]).to_numpy()
        * piezas["area"]
        / piezas["destino"].map(area_d)
    )
    sin_poblacion = piezas.groupby("origen")["a"].transform("sum") == 0
    piezas["metodo"] = np.where(sin_poblacion, "area", "poblacion")
    piezas["a"] = piezas["a"].where(~sin_poblacion, piezas["area"])
    piezas = piezas.groupby(["origen", "destino", "metodo"], as_index=False)["a"].sum()
    piezas["peso"] = piezas["a"] / piezas.groupby("origen")["a"].transform("sum")
    piezas["peso_destino"] = piezas["a"] / piezas.groupby("destino")["a"].transform(
        "sum"
    )
    return piezas[["origen", "destino", "peso", "peso_destino", "metodo"]], cobertura


def comprobar_tabla(tabla: pd.DataFrame) -> None:
    """Pesos sin nulos, en [0, 1], sin pares repetidos y con suma 1 por origen (`peso`) y por destino (`peso_destino`)."""
    for col, por in (("peso", "origen"), ("peso_destino", "destino")):
        if tabla[col].isna().any() or not tabla[col].between(0, 1).all():
            raise ValueError(f"`{col}` con nulos o fuera de [0, 1]")
        suma = tabla.groupby(por)[col].sum()
        if not np.allclose(suma, 1, atol=1e-6):
            raise ValueError(
                f"`{col}` no suma 1 por {por}: {suma[~np.isclose(suma, 1, atol=1e-6)].head()}"
            )
    if tabla.duplicated(["origen", "destino"]).any():
        raise ValueError("Pares origen-destino repetidos")


def pasar_extensiva(tabla: pd.DataFrame, datos: pd.Series) -> pd.Series:
    """Reparte una extensiva (`CUSEC` de origen → valor) entre los destinos: `y_j = Σ_i w_ij · y_i`."""
    if datos.isna().any():
        raise ValueError("Orígenes sin dato: decide antes de repartir")
    valor = tabla["origen"].map(datos)
    if valor.isna().any():
        raise ValueError("Hay orígenes de la tabla sin dato")
    return (tabla["peso"] * valor).groupby(tabla["destino"]).sum()


def pasar_intensiva(tabla: pd.DataFrame, datos: pd.Series) -> pd.Series:
    """Pasa una intensiva (€/m²) con la media ponderada por `peso_destino`; nunca la suma ni la media simple.

    Orígenes sin dato (huecos del SERPAVI) se excluyen y los pesos se renormalizan sobre los que sí lo tienen;
    un destino sin ningún origen con dato queda nulo.
    """
    t = tabla.assign(valor=tabla["origen"].map(datos)).dropna(subset=["valor"])
    suma = t.groupby("destino")["peso_destino"].sum()
    return (t["peso_destino"] * t["valor"]).groupby(t["destino"]).sum() / suma


def secciones_cambiadas(
    tabla: pd.DataFrame, origenes: pd.Index, destinos: pd.Index
) -> dict[str, pd.Index]:
    """Secciones que no pasan enteras: orígenes `partidos` y destinos `fusionados` (peso máximo < 0,99) y las que
    solo existen en un seccionado (`sin_destino`: origen que no cae en ninguno; `sin_origen`: destino sin origen)."""
    return {
        "partidos": pd.Index(
            tabla.groupby("origen")["peso"].max().loc[lambda s: s < ENTERA].index
        ),
        "fusionados": pd.Index(
            tabla.groupby("destino")["peso_destino"]
            .max()
            .loc[lambda s: s < ENTERA]
            .index
        ),
        "sin_destino": origenes.difference(tabla["origen"]),
        "sin_origen": destinos.difference(tabla["destino"]),
    }


def total_por_municipio(
    tabla: pd.DataFrame, datos: pd.Series, municipio_origen: pd.Series
) -> pd.DataFrame:
    """Total de una extensiva por municipio antes y después del paso (`CUSEC` → `CUMUN`, 5 primeros dígitos).

    Lanza si algún municipio difiere más de `TOLERANCIA_TOTAL` (relativa) o si un destino cae en otro municipio.
    """
    despues = pasar_extensiva(tabla, datos)
    antes = datos.groupby(municipio_origen.reindex(datos.index)).sum()
    despues = despues.groupby(despues.index.str[:5]).sum()
    cuadro = pd.DataFrame({"antes": antes, "despues": despues}).fillna(0)
    mal = ~np.isclose(cuadro["antes"], cuadro["despues"], rtol=TOLERANCIA_TOTAL, atol=0)
    if mal.any():
        raise ValueError(
            f"Total no conservado en {mal.sum()} municipios:\n{cuadro[mal].head(10)}"
        )
    return cuadro


def main() -> None:
    origen, destino = leer_origen(), zonas.leer_secciones()
    tabla, cobertura = tabla_paso(origen, destino, zonas.poblacion_secciones())
    comprobar_tabla(tabla)
    if (cobertura < 0.99).any():
        raise ValueError(
            f"Orígenes con cobertura < 0,99:\n{cobertura[cobertura < 0.99]}"
        )
    datos = origen.set_index("CUSEC")
    total_por_municipio(tabla, datos["Num_VC"], datos["CUMUN"])
    zonas.PROCESSED.mkdir(parents=True, exist_ok=True)
    tabla.to_parquet(zonas.PROCESSED / "paso_secciones_2021_2025.parquet")


if __name__ == "__main__":
    main()
