"""Tabla `tiempos` en coche (`modo = coche`) entre los mismos orígenes y destinos que el transporte público (#96).

- Minutos: `TravelTimeMatrix` de r5py sobre la red viaria de OpenStreetMap (sin GTFS), con las velocidades de OSM.
  **Sin tráfico**: no hay fuente primaria de congestión y no se inventa un factor, así que en hora punta el tiempo
  real es mayor (limitación declarada en `tiempos.json`). Dentro de la zona y del polo de la propia zona, mediana
  desde las secciones, como en transporte público (`tiempos._tabla`); por encima de `MAX_MINUTOS`, nulo.
- Kilómetros: línea recta × `FACTOR_RODEO`, siempre `estimado = verdadero`; dentro de la zona y hasta el polo de la
  propia zona, mediana de la distancia de los edificios de la zona (a su centro o al polo) × `FACTOR_RODEO`, para
  que ninguna zona dé 0 km. `DetailedItineraries` de r5py sí da la distancia, pero se descartó: su ruta no
  coincide con la de la matriz y no encontraba ruta al centro del distrito Centro (sin diagnosticar). El contrato solo
  tiene una marca `estimado`, y los km no salen del enrutado: cada fila la lleva.
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
# Supuesto: se usa como aproximación del coste por km del trayecto de casa al trabajo; la norma la fija para los
# desplazamientos por trabajo fuera del centro que compensa la empresa, no para ir al trabajo. Es una compensación
# fiscal del uso del vehículo propio, no un coste medido; no incluye peajes ni aparcamiento, que la orden suma aparte.
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
# 120 km/h: límite genérico de autopistas y autovías en España (art. 48 del Reglamento General de Circulación); una
# velocidad media implícita km / minutos por encima delata un tiempo o una distancia mal calculados
VELOCIDAD_MAX_KMH = 120.0


def edificios_por_zona(
    edificios: gpd.GeoSeries, poligonos: gpd.GeoDataFrame
) -> pd.DataFrame:
    """Columnas `x`, `y` (EPSG:25830) y `zona_id` de los edificios dentro de las secciones (`poligonos`)."""
    dentro = gpd.sjoin(
        gpd.GeoDataFrame(geometry=edificios),
        poligonos[["zona_id", "geometry"]],
        predicate="within",
    )
    return pd.DataFrame(
        {"x": dentro.geometry.x, "y": dentro.geometry.y, "zona_id": dentro["zona_id"]}
    )


def _mediana_km(
    edificios: pd.DataFrame, destinos: pd.DataFrame, por: pd.DataFrame
) -> pd.Series:
    """Mediana en km de la distancia de cada edificio al punto de `destinos` de su fila en `por`.

    `por` trae `zona_id` y `destino_id` (qué zona de edificios va a qué punto); `destinos` trae `x` e `y`.
    """
    e = por.merge(edificios, on="zona_id").merge(
        destinos, left_on="destino_id", right_index=True, suffixes=("", "_d")
    )
    d = np.hypot(e["x"] - e["x_d"], e["y"] - e["y_d"]) / 1000
    return d.groupby([e["zona_id"], e["destino_id"]]).median()


def _km_rodeo(
    centros: pd.DataFrame,
    destinos: pd.DataFrame,
    edificios: pd.DataFrame,
    polos: pd.DataFrame,
) -> pd.Series:
    """Km por par (`zona_id`, `destino_id`): línea recta × `FACTOR_RODEO`.

    En la diagonal y hacia el polo de la propia zona, la mediana de la distancia de los edificios de la zona al
    centro o al polo. `centros` y `destinos` traen `x` e `y` en metros; `edificios`, `x`, `y` y `zona_id`; `polos`,
    `destino_id` y `zona_id`.
    """
    o, d = centros.to_numpy(), destinos.to_numpy()
    recta = np.hypot(o[:, None, 0] - d[None, :, 0], o[:, None, 1] - d[None, :, 1])
    clave = pd.MultiIndex.from_product(
        [centros.index, destinos.index], names=["zona_id", "destino_id"]
    )
    km = pd.Series(recta.ravel() / 1000, index=clave)
    propios = pd.concat(
        [
            pd.DataFrame({"zona_id": centros.index, "destino_id": centros.index}),
            polos[["zona_id", "destino_id"]],
        ]
    )
    medianas = _mediana_km(edificios, destinos, propios)
    km[medianas.index] = medianas.to_numpy()
    return km * FACTOR_RODEO


# shortcut: repite el ensamblado de tiempos.matriz_r5py e importa sus funciones privadas porque #161 y #164 están cambiando tiempos.py; generalizar tiempos.matriz_r5py(red, parámetros) cuando se mergeen
def matriz_r5py(
    zonas: pd.DataFrame,
    secciones: gpd.GeoDataFrame,
    polos: pd.DataFrame,
    edificios: pd.DataFrame,
) -> pd.DataFrame:
    """Tabla `tiempos` en coche: minutos de r5py y km por línea recta × `FACTOR_RODEO`, todo `estimado = verdadero`.

    Mismos orígenes y destinos que `tiempos.matriz_r5py`; `secciones` y `polos`, como allí; `edificios`, de
    `edificios_por_zona`.
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
    km = _km_rodeo(xy_centros, pd.concat([xy_centros, xy_polos]), edificios, polos)
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
    """Falla si falta una coordenada, un tiempo o un km no nulo es <= 0, un km baja de la recta o la velocidad pasa de `VELOCIDAD_MAX_KMH`.

    `xy` trae `x` e `y` en metros (EPSG:25830) de zonas y polos; `polos`, `destino_id` y `zona_id`. La diagonal y el
    polo de la propia zona se miden con medianas de métodos distintos (minutos desde los puntos de población de las
    secciones, km desde los edificios), así que no se comparan con la recta ni se les pone tope de velocidad: en 5
    zonas el tiempo interno es el suelo de 1 min y el km pasa de 2 (velocidad implícita de hasta 372 km/h).
    """
    o = xy.reindex(tabla["zona_id"]).to_numpy()
    d = xy.reindex(tabla["destino_id"]).to_numpy()
    sin_xy = np.isnan(o).any(axis=1) | np.isnan(d).any(axis=1)
    if sin_xy.any():
        raise ValueError(
            f"Sin coordenadas para {int(sin_xy.sum())} pares, p. ej. "
            f"{tabla.loc[sin_xy, ['zona_id', 'destino_id']].head(3).values.tolist()}"
        )
    propio = tabla["zona_id"] == tabla["destino_id"]
    en_zona = tabla["destino_id"].map(polos.set_index("destino_id")["zona_id"])
    comparable = ~propio & (en_zona != tabla["zona_id"])
    recta = np.hypot(o[:, 0] - d[:, 0], o[:, 1] - d[:, 1]) / 1000
    km, minutos = tabla["km"], tabla["minutos"]
    causas = {
        "tiempo <= 0": minutos <= 0,
        "km <= 0": km <= 0,
        "km por debajo de la línea recta": comparable & (km < recta - TOLERANCIA_KM),
        f"velocidad > {VELOCIDAD_MAX_KMH:.0f} km/h": comparable
        & (km / (minutos / 60) > VELOCIDAD_MAX_KMH),
    }
    if malos := {c: m for c, m in causas.items() if m.any()}:
        detalle = "; ".join(
            f"{c}: {int(m.sum())}, p. ej. "
            f"{tabla.loc[m, ['zona_id', 'destino_id']].head(3).values.tolist()}"
            for c, m in malos.items()
        )
        raise ValueError(f"Pares en coche inválidos. {detalle}")


def main() -> None:
    """Escribe `data/processed/tiempos_coche.parquet`."""
    zonas = gpd.read_parquet(PROCESSED / "zonas.parquet")
    poligonos = secciones_por_zona(leer_secciones(), poblacion_secciones())
    edificios = leer_edificios()
    secciones = poligonos.assign(geometry=puntos_poblacion(poligonos, edificios))
    lista = ubicar(leer(), zonas)
    tabla = matriz_r5py(
        zonas, secciones, lista, edificios_por_zona(edificios, poligonos)
    )
    comprobar(tabla, pd.concat([_centros(zonas), _xy_polos(lista)]), lista)
    LOG.info("%.1f %% de pares nulos", 100 * tabla["minutos"].isna().mean())
    tabla.to_parquet(PROCESSED / "tiempos_coche.parquet")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
