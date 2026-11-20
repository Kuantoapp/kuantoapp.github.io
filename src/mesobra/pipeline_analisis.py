"""Escribe `app/datos/analisis.json` y las tres figuras de `app/img/` del informe de análisis (#90).

Calcula el esfuerzo y la tabla del Bono desde `data/raw` con los módulos existentes y les da la forma del
contrato de `api_estatica`. Ejecutar con `python -m mesobra.pipeline_analisis`.
"""

import logging
from datetime import date

import pandas as pd

from mesobra import (
    alquiler,
    api_estatica,
    bono,
    calculo,
    esfuerzo,
    figuras,
    renta,
)
from mesobra import titulares as titulares_sueldos
from mesobra.figuras import es
from mesobra.pipeline_euros import (
    APP_DATOS,
    IPC_CM,
    IPC_INE,
    MADRID,
    ORIGEN_SERPAVI,
    SERPAVI,
)

LOG = logging.getLogger(__name__)
APP_IMG = APP_DATOS.parent / "img"
FUENTE_ESFUERZO = "SERPAVI (MIVAU) y ADRH (INE), elaboración propia"
FUENTE_BONO = "Bono Alquiler Joven 2022, Comunidad de Madrid"
FUENTES = [
    SERPAVI,
    IPC_INE,
    IPC_CM,
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
    *(
        {
            "nombre": f"INE, {nombre}, tabla {t} (sueldos de los titulares)",
            "url": f"https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/{t}.csv",
            "licencia": "CC BY 4.0",
        }
        for t, nombre in (
            (28191, "Encuesta Anual de Estructura Salarial"),
            (28186, "Encuesta Anual de Estructura Salarial"),
            (28201, "Encuesta Anual de Estructura Salarial"),
            (36850, "Encuesta de Estructura Salarial 2022"),
        )
    ),
]
NOTA = (
    "Esfuerzo: cuantía mediana mensual del alquiler de vivienda colectiva del SERPAVI entre la renta neta "
    "media mensual por hogar del ADRH, por zona y año (2015-2024), sin las filas con renta secreta. Bono: "
    "convocatoria 2022 frente al esfuerzo de 2023 y los jóvenes de 18 a 35 años a 1-1-2023. "
    + ORIGEN_SERPAVI
    + " Elaboración propia con datos extraídos del sitio web del INE: www.ine.es (tabla 31097 actualizada "
    "el 2026-10-15; tabla 68542 actualizada el 2025-12-02; tabla 28191 actualizada el 2026-05-28; tabla "
    "28186 actualizada el 2026-05-28; tabla 28201 actualizada el 2026-05-28; tabla 36850 actualizada el "
    "2024-09-23; tabla 76137 actualizada el 2026-11-13); el INE no participa ni patrocina este proyecto. "
    "Fuente de los datos: Comunidad de Madrid (Bono Alquiler Joven 2022, actualizado el 2026-02-03; IPC de "
    "alquiler 1934665, control, actualizado el 2026-11-05); la "
    "Comunidad de Madrid no participa ni patrocina este proyecto."
)


def _pct(x: float) -> str:
    return es(100 * x) + " %"


def titulares(tabla: pd.DataFrame, solicitudes: pd.DataFrame) -> list[dict]:
    """Tres cifras del informe, calculadas de las tablas `esfuerzo` y `bono`."""
    madrid = tabla[tabla["zona_id"] == MADRID].set_index("anio")["esfuerzo"]
    cambio = esfuerzo.cambio(tabla).drop(MADRID, errors="ignore").dropna()
    desde, hasta = int(tabla["anio"].min()), int(tabla["anio"].max())
    tasa = solicitudes["aceptadas"].sum() / solicitudes["solicitudes"].sum()
    otro = es(bono.TOTALES[2], 0)
    return [
        {
            "texto": f"El alquiler mediano de Madrid pesa el {_pct(madrid[hasta])} de la renta neta media mensual de sus hogares en "
            f"{hasta}, frente al {_pct(madrid[desde])} en {desde} y el {_pct(madrid[2020])} en 2020.",
            "fuente": FUENTE_ESFUERZO,
        },
        {
            "texto": f"Entre {desde} y {hasta} el esfuerzo sube en {(cambio > 0).sum()} de las {len(cambio)} zonas con dato "
            f"en ambos años (sin Madrid entero, que va por sus distritos); la mediana del cambio es "
            f"{es(100 * cambio.median(), 2)} puntos porcentuales.",
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
    quitadas = tabla[
        tabla["renta_hogar_mes"].isna() & tabla["alquiler_mes_p50"].notna()
    ]
    if not quitadas.empty:
        raise ValueError(
            f"Filas con alquiler y sin renta que se perderían:\n{quitadas}"
        )
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


def _controlar(
    crudo: pd.DataFrame, solicitudes: pd.DataFrame, tabla: pd.DataFrame
) -> None:
    """Los mismos controles que `bono.main` y `esfuerzo.main`: totales del CSV, 159 municipios, 200 zonas por año."""
    otro = crudo[crudo["municipio_id"].isna()]
    totales = (
        int(crudo["solicitudes"].sum()),
        int(crudo["aceptadas"].sum()),
        int(otro["solicitudes"].sum()),
    )
    if totales != bono.TOTALES or otro["aceptadas"].sum() != 0:
        raise ValueError(
            f"Totales {totales} distintos de {bono.TOTALES} (solicitudes, aceptadas, «Otro»)"
        )
    if len(solicitudes) != 159:
        raise ValueError(f"Se esperaban 159 municipios y hay {len(solicitudes)}")
    por_anio = tabla.groupby("anio").size()
    if (por_anio != 200).any():
        raise ValueError(f"No hay 200 zonas por año:\n{por_anio}")


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    zona = alquiler.alquiler_zona(alquiler.leer_serpavi())
    tabla = esfuerzo.esfuerzo(zona, renta.renta())
    crudo = bono.leer_bono()
    solicitudes = bono._por_anio(
        crudo, bono.poblacion_joven(bono._edades()), tabla, bono.ANIO
    )
    _controlar(crudo, solicitudes, tabla)
    objeto = analisis_json(tabla, solicitudes)
    LOG.info(
        "Filas de esfuerzo sin renta (secreto del INE) quitadas: %d",
        tabla["renta_hogar_mes"].isna().sum(),
    )
    for t in objeto["titulares"]:
        LOG.info("Titular: %s", t["texto"])
    api = calculo.leer_api(APP_DATOS)
    res = titulares_sueldos.resumenes(api)
    objeto["titulares"] += titulares_sueldos.titulares(res)
    for perfil, r in res:
        LOG.info("Resumen %s: %s", perfil["nombre"], r)
    api_estatica.escribir("analisis.json", objeto, APP_DATOS)
    zonas = figuras.leer_zonas()
    APP_IMG.mkdir(exist_ok=True)
    con_testigos = tabla.merge(
        zona[["zona_id", "anio", "testigos"]],
        on=["zona_id", "anio"],
        how="left",
        validate="one_to_one",
    )
    sin1, pocos1 = figuras.mapa_esfuerzo(
        con_testigos, zonas, APP_IMG / "esfuerzo_ultimo.png"
    )
    sin2, pocos2 = figuras.mapa_cambio(
        con_testigos, zonas, APP_IMG / "esfuerzo_cambio.png"
    )
    figuras.dispersion_bono(solicitudes, zonas, APP_IMG / "bono_dispersion.png")
    grupos = solicitudes["grupo"].value_counts()
    LOG.info(
        "Mapa 1: sin dato %d, pocos contratos (< %d) %d",
        sin1,
        figuras.MIN_TESTIGOS,
        pocos1,
    )
    LOG.info(
        "Mapa 2: sin dato %d, pocos contratos (< %d) %d",
        sin2,
        figuras.MIN_TESTIGOS,
        pocos2,
    )
    LOG.info(
        "Bono con esfuerzo: %d, sin dato: %d, necesidad alta y ayuda baja: %d",
        (solicitudes["grupo"] != "sin_dato").sum(),
        grupos.get("sin_dato", 0),
        grupos.get("necesidad_alta_ayuda_baja", 0),
    )


if __name__ == "__main__":
    main()
