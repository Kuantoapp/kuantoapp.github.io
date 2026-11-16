"""Tabla de paso de las secciones censales de 2021 (las del SERPAVI) a las del INE a 1-1-2025 (las del ADRH 2024).

El INE no publica una correspondencia entre seccionados, así que se construye superponiendo las dos capas. Peso
dasimétrico (#167): dentro de cada sección de 2025 se supone la población repartida por igual en su superficie, y
la población de cada pieza `origen ∩ destino` es la de su destino por la fracción de área que ocupa la pieza.
Solo se conoce la población del seccionado de destino (tabla 31105), por eso la auxiliar es la suya.

`peso` suma 1 por origen: reparte las variables extensivas (testigos, viviendas). `peso_destino` suma 1 por
destino y reparte por área. Las intensivas (€/m²) se ponderan con `peso × denominador`; nunca se suman.
"""

import logging
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

from mesobra import zonas

LOG = logging.getLogger(__name__)
RAIZ = Path(__file__).resolve().parents[2]
ORIGEN = RAIZ / "data/raw/serpavi_capa_secciones_2026-11-16/ALQ_Secciones_2022_Web.shp"
# supuesto: una pieza menor que esta fracción del origen es borde que no coincide entre fuentes, no una partición
ASTILLA = 0.001
# supuesto: un origen o destino con un peso máximo menor que esto está partido o fusionado
ENTERA = 0.99
# tolerancia fijada de antemano para el total conservado por municipio (relativa; solo error de coma flotante)
TOLERANCIA_TOTAL = 1e-9
# supuesto: un origen con menos de esta fracción de su área en el destino cae en parte fuera del ámbito
COBERTURA_MINIMA = 0.99
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
    if any(c.crs is None or c.crs.to_epsg() != CRS_METRICO for c in (origen, destino)):
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
    es_astilla = piezas["area"] < ASTILLA * piezas["origen"].map(area_o)
    LOG.info("astillas descartadas: %d de %d piezas", es_astilla.sum(), len(piezas))
    piezas = piezas[~es_astilla]
    piezas["a"] = (
        poblacion.reindex(piezas["destino"]).to_numpy()
        * piezas["area"]
        / piezas["destino"].map(area_d)
    )
    sin_poblacion = piezas.groupby("origen")["a"].transform("sum") == 0
    piezas["metodo"] = np.where(sin_poblacion, "area", "poblacion")
    piezas["a"] = piezas["a"].where(~sin_poblacion, piezas["area"])
    piezas = piezas.groupby(["origen", "destino", "metodo"], as_index=False).agg(
        a=("a", "sum"), area_pieza=("area", "sum")
    )
    piezas["peso"] = piezas["a"] / piezas.groupby("origen")["a"].transform("sum")
    # un destino sin población (0/0) pondera por área, como el origen sin población
    a_destino = piezas["a"].where(
        piezas.groupby("destino")["a"].transform("sum") > 0, piezas["area_pieza"]
    )
    piezas["peso_destino"] = a_destino / a_destino.groupby(piezas["destino"]).transform(
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
    if not datos.index.isin(tabla["origen"]).all():
        raise ValueError("Hay datos de orígenes que no están en la tabla: se perderían")
    valor = tabla["origen"].map(datos)
    if valor.isna().any():
        raise ValueError("Hay orígenes de la tabla sin dato")
    return (tabla["peso"] * valor).groupby(tabla["destino"]).sum()


def pasar_intensiva(
    tabla: pd.DataFrame, datos: pd.Series, denominador: pd.Series
) -> pd.Series:
    """Pasa una intensiva (€/m²) como media ponderada por lo que aporta cada origen: `peso × denominador`.

    `denominador` es el extensivo del origen con el que se calculó el dato (testigos, m² alquilados). Con medianas
    es una aproximación, a presentar como «estimado». Orígenes sin dato o sin denominador se excluyen y los pesos
    se renormalizan; un destino sin ningún origen válido no aparece en el resultado. `peso_destino` no sirve aquí: reparte por área.
    """
    t = tabla.assign(
        valor=tabla["origen"].map(datos), aporta=tabla["origen"].map(denominador)
    ).dropna(subset=["valor", "aporta"])
    t["aporta"] = t["aporta"] * t["peso"]
    return (t["aporta"] * t["valor"]).groupby(t["destino"]).sum() / t.groupby(
        "destino"
    )["aporta"].sum()


def pureza(tabla: pd.DataFrame, denominador: pd.Series) -> pd.Series:
    """Parte de lo que llega a cada destino (`peso × denominador`) que viene de orígenes enteros (peso ≥ 0,99).

    Un destino con pureza baja depende del supuesto de reparto: su valor es una estimación. Nulo si no llega nada.
    """
    llega = tabla["peso"] * tabla["origen"].map(denominador)
    entera = llega.where(tabla["peso"] >= ENTERA, 0)
    return (
        entera.groupby(tabla["destino"]).sum() / llega.groupby(tabla["destino"]).sum()
    )


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
    if (cobertura < COBERTURA_MINIMA).any():
        raise ValueError(
            f"Orígenes con cobertura < 0,99:\n{cobertura[cobertura < 0.99]}"
        )
    datos = origen.set_index("CUSEC")
    total_por_municipio(tabla, datos["Num_VC"], datos["CUMUN"])
    zonas.PROCESSED.mkdir(parents=True, exist_ok=True)
    tabla.to_parquet(zonas.PROCESSED / "paso_secciones_2021_2025.parquet")
    cambiadas = secciones_cambiadas(
        tabla, pd.Index(origen["CUSEC"]), pd.Index(destino["CUSEC"])
    )
    pd.concat(
        [
            pd.Series(v, name="seccion").to_frame().assign(tipo=k)
            for k, v in cambiadas.items()
        ]
    ).to_parquet(zonas.PROCESSED / "paso_secciones_cambiadas.parquet")


if __name__ == "__main__":
    main()
