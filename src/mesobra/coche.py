"""Tabla `tiempos` en coche (`modo = coche`) entre los mismos orígenes y destinos que el transporte público (#96).

- Minutos: `TravelTimeMatrix` de r5py sobre la red viaria de OpenStreetMap (sin GTFS), con las velocidades de OSM.
  **Sin tráfico**: no hay fuente primaria de congestión y no se inventa un factor, así que en hora punta el tiempo
  real es mayor (limitación declarada en `tiempos.json`). Dentro de la zona y del polo de la propia zona, mediana
  desde las secciones, como en transporte público (`tiempos._tabla`); por encima de `MAX_MINUTOS`, nulo.
- Kilómetros: línea recta × `FACTOR_RODEO`, siempre `estimado = verdadero`. `DetailedItineraries` de r5py sí da la
  distancia, pero se descartó (medido el 2026-11-20 sobre 400 pares): su ruta no es la de la matriz (distancia 1,5
  veces la recta, mediana, y 2 veces el tiempo de la matriz) y tarda ~40 ms por par, unos 30 min en total. Por eso
  cada fila lleva `estimado = verdadero`: el contrato solo tiene una marca y los km no salen del enrutado.
- Coste: `EUR_KM`; la fórmula (2 × km × días × semanas/mes × €/km) ya está en `calculo.viaje`.
  El coste en coche no incluye aparcamiento ni peajes: no hay fuente primaria general y queda como supuesto declarado.

r5py se importa dentro de la función para que el módulo y sus tests funcionen sin Java.
"""

import datetime as dt
import logging

import geopandas as gpd
import numpy as np
import pandas as pd

from mesobra import contratos
from mesobra.polos import leer, ubicar
from mesobra.tiempos import (
    FACTOR_RODEO,
    MAX_MINUTOS,
    OSM,
    _centros,
    _en_metros,
    _interno_mediana,
    _minutos_r5py,
    _propios_polo,
    _puntos,
    _sustituir,
    _tabla,
    _xy_polos,
)
from mesobra.zonas import (
    PROCESSED,
    leer_edificios,
    leer_secciones,
    poblacion_secciones,
    puntos_poblacion,
    secciones_por_zona,
)

LOG = logging.getLogger(__name__)

# Cuantía de gastos de locomoción en vehículo propio exceptuada de gravamen: 0,26 €/km (Orden HFP/792/2023, de 12 de
# julio, art. único.1, que revisa el art. 9.A.2.b del Reglamento del IRPF, RD 439/2007; BOE-A-2023-16461, en vigor
# desde el 17-07-2023; el texto consolidado del reglamento, BOE-A-2007-6820, aún dice 0,19 y remite a la orden).
# Es una compensación fiscal del uso del vehículo propio (combustible y desgaste), no un coste medido; no incluye
# peajes ni aparcamiento, que la orden suma aparte.
EUR_KM = 0.26
NORMA_EUR_KM = {
    "nombre": "Orden HFP/792/2023, de 12 de julio, art. único.1: 0,26 € por kilómetro recorrido en vehículo propio "
    "(BOE-A-2023-16461)",
    "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2023-16461",
    "licencia": "Reutilización con cita de la fuente: basado en datos de la Agencia Estatal Boletín Oficial del Estado "
    "(https://www.boe.es/informacion/aviso_legal/index.php)",
}
# la distancia sale de la línea recta × FACTOR_RODEO, así que nunca baja de la recta; solo absorbe el redondeo de coma flotante
TOLERANCIA_KM = 1e-6


def _km_rodeo(
    centros: pd.DataFrame,
    destinos: pd.DataFrame,
    secciones: gpd.GeoDataFrame,
    polos: pd.DataFrame,
) -> pd.Series:
    """Km por par (`zona_id`, `destino_id`): línea recta × `FACTOR_RODEO`.

    En la diagonal y hacia el polo de la propia zona, la mediana de la distancia desde las secciones de la zona.
    `centros` y `destinos` traen `x` e `y` en metros; `polos`, `destino_id` y `zona_id`.
    """
    o, d = centros.to_numpy(), destinos.to_numpy()
    recta = np.hypot(o[:, None, 0] - d[None, :, 0], o[:, None, 1] - d[None, :, 1])
    clave = pd.MultiIndex.from_product(
        [centros.index, destinos.index], names=["zona_id", "destino_id"]
    )
    km = pd.Series(recta.ravel() / 1000, index=clave)
    c = secciones.centroid
    s = pd.DataFrame(
        {"x": c.x.to_numpy(), "y": c.y.to_numpy(), "zona_id": secciones["zona_id"]}
    )
    a_centro = s.merge(
        centros, left_on="zona_id", right_index=True, suffixes=("", "_d")
    )
    interno = np.hypot(a_centro.x - a_centro.x_d, a_centro.y - a_centro.y_d) / 1000
    interno = interno.groupby(a_centro["zona_id"]).median()
    km[pd.MultiIndex.from_arrays([interno.index, interno.index])] = interno.to_numpy()
    p = polos.join(destinos, on="destino_id").merge(
        s, on="zona_id", suffixes=("_d", "")
    )
    a_polo = np.hypot(p.x - p.x_d, p.y - p.y_d) / 1000
    propio = a_polo.groupby([p["zona_id"], p["destino_id"]]).median()
    km[propio.index] = propio.to_numpy()
    return km * FACTOR_RODEO


def matriz_r5py(
    zonas: pd.DataFrame, secciones: gpd.GeoDataFrame, polos: pd.DataFrame
) -> pd.DataFrame:
    """Tabla `tiempos` en coche: minutos de r5py y km por línea recta × `FACTOR_RODEO`, todo `estimado = verdadero`.

    Mismos orígenes y destinos que `tiempos.matriz_r5py`; `secciones` y `polos`, como allí.
    """
    from r5py import TransportMode, TransportNetwork, TravelTimeMatrix

    _en_metros(secciones)
    centros = _puntos(zonas["zona_id"], zonas["lon_centro"], zonas["lat_centro"])
    puntos_polo = _puntos(polos["destino_id"], polos["lon"], polos["lat"])
    puntos_seccion = secciones.centroid.to_crs(4326)
    sec = _puntos(secciones["CUSEC"], puntos_seccion.x, puntos_seccion.y)
    red = TransportNetwork(OSM, [])
    calculo = {
        "transport_modes": [TransportMode.CAR],
        "max_time": dt.timedelta(minutes=MAX_MINUTOS),
    }
    m = _minutos_r5py(
        TravelTimeMatrix(
            red,
            origins=centros,
            destinations=pd.concat([centros, puntos_polo, sec], ignore_index=True),
            **calculo,
        )
    )
    desde_polos = _minutos_r5py(
        TravelTimeMatrix(red, origins=puntos_polo, destinations=sec, **calculo)
    )
    a_seccion = m["to_id"].isin(sec["id"])
    ids = pd.Index(zonas["zona_id"])
    interno = _interno_mediana(
        m[a_seccion].rename(columns={"from_id": "to_id", "to_id": "from_id"}),
        secciones,
        ids,
    )
    propios = _propios_polo(
        desde_polos.rename(columns={"from_id": "to_id", "to_id": "from_id"}),
        secciones,
        polos,
    )
    tabla = _tabla(
        _sustituir(m[~a_seccion], propios), interno, pd.Index(polos["destino_id"])
    )
    xy_centros, xy_polos = _centros(zonas), _xy_polos(polos)
    km = _km_rodeo(xy_centros, pd.concat([xy_centros, xy_polos]), secciones, polos)
    clave = pd.MultiIndex.from_frame(tabla[["zona_id", "destino_id"]])
    # sin ruta en 120 min no hay km: el par queda nulo en las dos columnas
    tabla["km"] = km.reindex(clave).to_numpy()
    tabla["km"] = tabla["km"].where(tabla["minutos"].notna())
    tabla = tabla.assign(modo="coche", estimado=True)[
        list(contratos.CONTRATOS["tiempos"]["columnas"])
    ].astype(contratos.dtypes("tiempos"))
    contratos.validar(tabla, "tiempos")
    return tabla


def comprobar(tabla: pd.DataFrame, xy: pd.DataFrame, polos: pd.DataFrame) -> None:
    """Falla si un tiempo no nulo es <= 0 o si un km no nulo baja de la línea recta entre el origen y el destino.

    `xy` trae `x` e `y` en metros (EPSG:25830) de zonas y polos; `polos`, `destino_id` y `zona_id`. La diagonal y el
    polo de la propia zona se miden como mediana desde las secciones, no centro a centro: no se comparan con la recta.
    """
    propio = tabla["zona_id"] == tabla["destino_id"]
    en_zona = tabla["destino_id"].map(polos.set_index("destino_id")["zona_id"])
    comparable = ~propio & (en_zona != tabla["zona_id"])
    o = xy.reindex(tabla["zona_id"]).to_numpy()
    d = xy.reindex(tabla["destino_id"]).to_numpy()
    recta = np.hypot(o[:, 0] - d[:, 0], o[:, 1] - d[:, 1]) / 1000
    malos = (tabla["minutos"] <= 0) | (
        comparable & (tabla["km"] < recta - TOLERANCIA_KM)
    )
    if malos.any():
        raise ValueError(
            f"Pares en coche con tiempo <= 0 o km por debajo de la línea recta: {int(malos.sum())}, "
            f"p. ej. {tabla.loc[malos, ['zona_id', 'destino_id']].head(3).values.tolist()}"
        )


def main() -> None:
    """Escribe `data/processed/tiempos_coche.parquet`."""
    zonas = gpd.read_parquet(PROCESSED / "zonas.parquet")
    secciones = secciones_por_zona(leer_secciones(), poblacion_secciones())
    secciones = secciones.assign(geometry=puntos_poblacion(secciones, leer_edificios()))
    lista = ubicar(leer(), zonas)
    tabla = matriz_r5py(zonas, secciones, lista)
    comprobar(tabla, pd.concat([_centros(zonas), _xy_polos(lista)]), lista)
    LOG.info("%.1f %% de pares nulos", 100 * tabla["minutos"].isna().mean())
    tabla.to_parquet(PROCESSED / "tiempos_coche.parquet")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
