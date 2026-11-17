"""Escribe `app/datos/analisis.json` y las tres figuras de `app/img/` del informe de análisis (#90).

Calcula el esfuerzo y la tabla del Bono desde `data/raw` con los módulos existentes y les da la forma del
contrato de `api_estatica`. Ejecutar con `python -m mesobra.pipeline_analisis`.
"""

import logging
from datetime import date

import pandas as pd

from mesobra import alquiler, api_estatica, bono, esfuerzo, figuras, renta
from mesobra.pipeline_euros import APP_DATOS, MADRID, ORIGEN_SERPAVI, SERPAVI

LOG = logging.getLogger(__name__)
APP_IMG = APP_DATOS.parent / "img"
FUENTE_ESFUERZO = "SERPAVI (MIVAU) y ADRH (INE), elaboración propia"
FUENTE_BONO = "Bono Alquiler Joven 2022, Comunidad de Madrid"
FUENTES = [
    SERPAVI,
    {
        "nombre": "INE, Atlas de Distribución de Renta de los Hogares, tabla 31097 (renta neta media por hogar)",
        "url": "https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/31097.csv",
        "licencia": "CC BY 4.0",
    },
    {
        "nombre": "INE, Censo anual de población, tabla 68542 (población por sexo y edad año a año)",
        "url": "https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/68542.csv",
        "licencia": "CC BY 4.0",
    },
    {
        "nombre": "Bono Alquiler Joven 2022, portal de datos abiertos de la Comunidad de Madrid",
        "url": "https://datos.comunidad.madrid/dataset/ff697366-36f4-41a1-a966-f5ccf3b6db7c/resource/6fbda6ce-b479-4319-83c6-0b977d3fa8d5/download/spacm_bono_alquiler_joven_2022.csv",
        "licencia": "CC BY 4.0",
    },
]
NOTA = (
    "Esfuerzo: cuantía mediana mensual del alquiler de vivienda colectiva del SERPAVI entre la renta neta "
    "media mensual por hogar del ADRH, por zona y año (2015-2024), sin las filas con renta secreta. Bono: "
    "convocatoria 2022 frente al esfuerzo de 2023 y los jóvenes de 18 a 35 años a 1-1-2023. "
    + ORIGEN_SERPAVI
    + " Elaboración propia con datos extraídos del sitio web del INE: www.ine.es (tabla 31097 actualizada "
    "el 2026-10-15; tabla 68542 actualizada el 2025-12-02); el INE no participa ni patrocina este proyecto. "
    "Fuente de los datos: Comunidad de Madrid (Bono Alquiler Joven 2022, actualizado el 2026-02-03); la "
    "Comunidad de Madrid no participa ni patrocina este proyecto."
)


def _es(x: float, decimales: int = 1) -> str:
    return f"{x:,.{decimales}f}".translate(str.maketrans(",.-", ".,−"))


def _pct(x: float) -> str:
    return _es(100 * x) + " %"


def titulares(tabla: pd.DataFrame, solicitudes: pd.DataFrame) -> list[dict]:
    """Tres cifras del informe, calculadas de las tablas `esfuerzo` y `bono`."""
    madrid = tabla[tabla["zona_id"] == MADRID].set_index("anio")["esfuerzo"]
    cambio = esfuerzo.cambio(tabla).drop(MADRID, errors="ignore").dropna()
    desde, hasta = int(tabla["anio"].min()), int(tabla["anio"].max())
    tasa = solicitudes["aceptadas"].sum() / solicitudes["solicitudes"].sum()
    otro = _es(bono.TOTALES[2], 0)
    return [
        {
            "texto": f"El alquiler mediano de Madrid pesa el {_pct(madrid[hasta])} de la renta neta mensual de un hogar en "
            f"{hasta}, frente al {_pct(madrid[desde])} en {desde} y el {_pct(madrid[2020])} en 2020.",
            "fuente": FUENTE_ESFUERZO,
        },
        {
            "texto": f"Entre {desde} y {hasta} el esfuerzo sube en {(cambio > 0).sum()} de las {len(cambio)} zonas con dato "
            f"en ambos años (sin Madrid entero, que va por sus distritos); la mediana del cambio es "
            f"{_es(100 * cambio.median(), 2)} puntos porcentuales.",
            "fuente": FUENTE_ESFUERZO,
        },
        {
            "texto": f"El Bono Alquiler Joven 2022 aceptó el {_pct(tasa)} de las solicitudes, sin las {otro} "
            "solicitudes sin municipio (fila «Otro»).",
            "fuente": FUENTE_BONO,
        },
    ]


def _registros(df: pd.DataFrame, columnas: dict) -> list[dict]:
    df = df[list(columnas)].astype(object)
    return df.where(df.notna(), None).to_dict("records")


def analisis_json(tabla: pd.DataFrame, solicitudes: pd.DataFrame) -> dict:
    """Contrato `analisis.json`: quita las filas sin renta (secreto del INE) y los NaN pasan a `None`."""
    sin_secreto = tabla[tabla["renta_hogar_mes"].notna()]
    bloques = {
        nombre: _registros(df, api_estatica.BLOQUES[nombre][0])
        for nombre, df in (("esfuerzo", sin_secreto), ("bono", solicitudes))
    }
    meta = {
        "generado": date.today().isoformat(),
        "anio_dato": int(tabla["anio"].max()),
        "fuentes": FUENTES,
        "nota": NOTA,
    }
    return {"meta": meta, **bloques, "titulares": titulares(tabla, solicitudes)}


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    tabla = esfuerzo.esfuerzo(
        alquiler.alquiler_zona(alquiler.leer_serpavi()), renta.renta()
    )
    solicitudes = bono._por_anio(
        bono.leer_bono(), bono.poblacion_joven(bono._edades()), tabla, bono.ANIO
    )
    objeto = analisis_json(tabla, solicitudes)
    for t in objeto["titulares"]:
        LOG.info("Titular: %s", t["texto"])
    api_estatica.escribir("analisis.json", objeto, APP_DATOS)
    zonas = figuras.leer_zonas()
    APP_IMG.mkdir(exist_ok=True)
    sin_dato = figuras.mapa_esfuerzo(tabla, zonas, APP_IMG / "esfuerzo_ultimo.png")
    figuras.mapa_cambio(tabla, zonas, APP_IMG / "esfuerzo_cambio.png")
    figuras.dispersion_bono(solicitudes, zonas, APP_IMG / "bono_dispersion.png")
    grupos = solicitudes["grupo"].value_counts()
    LOG.info(
        "Mapa 1 sin dato: %d; Bono con esfuerzo: %d, sin dato: %d, necesidad alta y ayuda baja: %d",
        sin_dato,
        (solicitudes["grupo"] != "sin_dato").sum(),
        grupos.get("sin_dato", 0),
        grupos.get("necesidad_alta_ayuda_baja", 0),
    )


if __name__ == "__main__":
    main()
