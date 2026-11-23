"""Escribe `app/datos/analisis.json` y las figuras de `app/img/` del informe de análisis (#90, #103).

Calcula el esfuerzo y la tabla del Bono desde `data/raw`, los titulares de sueldos, la simulación del Bono y el
fin del descuento (`simulacion.py`) con los módulos existentes, y les da la forma del contrato de `api_estatica`.
Registra en el log las cifras que cita `app/informe.html`, también la sobrecarga regional de la ECV, que no va al
JSON (la sobrecarga por zona no se publica, #100). Ejecutar con `python -m mesobra.pipeline_analisis`.
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
    matriz_trabajo,
    renta,
    simulacion,
    sobrecarga_ecv,
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
            (28201, "Encuesta Anual de Estructura Salarial"),
            (36846, "Encuesta de Estructura Salarial 2022"),
            (36850, "Encuesta de Estructura Salarial 2022"),
            (6061, "Encuesta Trimestral de Coste Laboral"),
        )
    ),
    {
        "nombre": "Basado en datos de la Agencia Estatal Boletín Oficial del Estado. Ley 6/2011, de 28 de diciembre, de Medidas Fiscales y Administrativas de la Comunidad de Madrid, DA 1.ª (BOE-A-2012-2980; jornada del SERMAS)",
        "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2012-2980",
        "licencia": "Reutilización con cita de la fuente (aviso legal del BOE): «Basado en datos de la Agencia Estatal Boletín Oficial del Estado»; texto original, sin versión consolidada en el BOE, vigente según su análisis jurídico (https://www.boe.es)",
    },
    {
        "nombre": "Orden de 3 de febrero de 2026, instrucciones de nóminas de la Comunidad de Madrid para 2026 (BOCM-20260209-6), anexo V (sueldo de los titulares)",
        "url": "https://www.bocm.es/boletin/CM_Orden_BOCM/2026/02/09/BOCM-20260209-6.PDF",
        "licencia": "Disposición oficial, sin derechos de propiedad intelectual (art. 13 del TRLPI)",
    },
    # bloque `simulacion` (#103): pesos de destino, tarifas, norma del descuento y del Bono
    {
        "nombre": "INE, Censo anual de población, matriz de municipio de residencia por municipio de trabajo (ocupados de 2023; pesos de destino de la simulación del Bono)",
        "url": "https://www.ine.es/metodologia/t20/matriz_ocu_anonim.xlsb",
        "licencia": "CC BY 4.0",
    },
    {
        "nombre": "Colectivo Empresarial, ocupados por distrito (Instituto de Estadística de la Comunidad de Madrid; reparto de Madrid como destino)",
        "url": "https://datos.comunidad.madrid/dataset/e40b7dd8-f76b-4c93-980e-12d2531a4e71/resource/fb2d9895-9a09-4e1d-adc1-dc9d0c5511c4/download/colectivo-empresarial.-base-2015.-unidades-productivas-y-ocupados-por-distrito-y-estrato-de-empl.csv",
        "licencia": "CC BY 4.0",
    },
    *(
        {
            "nombre": f"{nombre} ({bocm})",
            "url": f"https://www.bocm.es/boletin/CM_Orden_BOCM/{bocm[5:9]}/{bocm[9:11]}/{bocm[11:13]}/{bocm}.PDF",
            "licencia": "Disposición oficial, sin derechos de propiedad intelectual (art. 13 del TRLPI)",
        }
        for bocm, nombre in (
            ("BOCM-20251231-3", "Tarifas del transporte público de 2026, Resolución del CRTM (fin del descuento)"),
            ("BOCM-20130130-9", "Tarifas del transporte público desde el 1-2-2013, Resolución del CRTM (tarifa del 30-11-2025)"),
            ("BOCM-20211217-35", "Tarifas de las zonas B3, C1 y C2 desde el 1-1-2022, Resolución del CRTM (tarifa del 30-11-2025)"),
            ("BOCM-20250110-20", "Acuerdo del Consejo de Gobierno de 26-12-2024, Bono Alquiler Joven (topes y requisitos de la simulación)"),
        )
    ),
    {
        "nombre": "Basado en datos de la Agencia Estatal Boletín Oficial del Estado. Real Decreto-ley 17/2025, art. 8 (BOE-A-2025-26459; descuento del transporte en 2026)",
        "url": "https://www.boe.es/eli/es/rdl/2025/12/23/17",
        "licencia": "Reutilización con cita de la fuente (aviso legal del BOE): «Basado en datos de la Agencia Estatal Boletín Oficial del Estado»",
    },
]  # fmt: skip
NOTA = (
    "Esfuerzo: cuantía mediana mensual del alquiler de vivienda colectiva del SERPAVI entre la renta neta "
    "media mensual por hogar del ADRH, por zona y año (2015-2024), sin las filas con renta secreta. Bono: "
    "convocatoria 2022 frente al esfuerzo de 2023 y los jóvenes de 18 a 35 años a 1-1-2023. "
    + ORIGEN_SERPAVI
    + " Elaboración propia con datos extraídos del sitio web del INE: www.ine.es (tabla 31097 actualizada "
    "el 2026-10-15; tabla 68542 actualizada el 2025-12-02; tabla 28191 actualizada el 2026-05-28; tabla "
    "28201 actualizada el 2026-05-28; tabla 36850 actualizada el "
    "2024-09-23; tabla 36846 actualizada el 2024-09-23; tabla 6061 actualizada el 2026-09-17; tabla 76137 actualizada el 2026-11-13); el INE no participa ni patrocina este proyecto. "
    "Fuente de los datos: Comunidad de Madrid (Bono Alquiler Joven 2022, actualizado el 2026-02-03; IPC de "
    "alquiler 1934665, control, actualizado el 2026-11-05); la "
    "Comunidad de Madrid no participa ni patrocina este proyecto. Fuente: Boletín Oficial de la Comunidad de "
    "Madrid (BOCM-20260209-6, nóminas de 2026, consultado el 2026-11-23) y Boletín Oficial del Estado (Ley 6/2011 de la "
    "Comunidad de Madrid, DA 1.ª, BOE-A-2012-2980, jornada del SERMAS, consultado el 2026-11-23). "
    "Simulación del Bono y fin del descuento (bloque simulacion, todo estimado): matriz de residencia por trabajo "
    "del INE actualizada el 2025-12-02; Colectivo Empresarial (Comunidad de Madrid) actualizado el 2025-07-24; "
    "BOCM-20251231-3 consultado el 2026-11-20, BOCM-20130130-9 consultado el 2026-11-21, BOCM-20211217-35 "
    "consultado el 2026-11-21 y BOCM-20250110-20 consultado el 2026-11-19; RDL 17/2025 (BOE-A-2025-26459) "
    "consultado el 2026-11-20. Sin las filas de habitación; `_bruto` = ingresos medidos con el bruto (banda de la "
    "pareja y el joven); `_sin_imputar` = horas_viaje sin los pares con 120 min imputados; marcas de "
    "simulacion_calidad por municipio."
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


MARCAS = ["marca_imputada", "marca_excluida", "marca_pocos"]
# decisión 8 de `simulacion.py`: estos dos entran o no según se midan los ingresos, así que van siempre como banda
BANDA_INGRESOS = ("pareja_mediana", "joven_mediano")


def bloque_simulacion(
    base: pd.DataFrame,
    bruto: pd.DataFrame,
    sin_imputar: pd.DataFrame,
    fin: pd.DataFrame,
    calidad: pd.DataFrame,
) -> pd.DataFrame:
    """Filas publicadas de `simulacion`: sin habitación (no se presenta hasta #311), la banda de ingresos
    (`_bruto`) de la pareja y el joven, `horas_viaje` sin pares imputados (`_sin_imputar`) y el fin del
    descuento; las marcas de `simulacion_calidad` por municipio, nulas en el fin del descuento."""

    def vivienda(df: pd.DataFrame) -> pd.DataFrame:
        return df[~df["perfil"].str.endswith("_habitacion")]

    def sufijo(df: pd.DataFrame, s: str) -> pd.DataFrame:
        return df.assign(criterio=df["criterio"] + s)

    bruto, sin_imputar = vivienda(bruto), vivienda(sin_imputar)
    partes = pd.concat(
        [
            vivienda(base),
            sufijo(bruto[bruto["perfil"].isin(BANDA_INGRESOS)], "_bruto"),
            sufijo(
                sin_imputar[sin_imputar["criterio"] == "horas_viaje"], "_sin_imputar"
            ),
        ]
    ).merge(
        calidad[["municipio_id", *MARCAS]],
        on="municipio_id",
        how="left",
        validate="many_to_one",
    )
    if partes[MARCAS].isna().any().any():
        raise ValueError("Municipios simulados sin fila en simulacion_calidad")
    return pd.concat([partes, fin], ignore_index=True)


def analisis_json(
    tabla: pd.DataFrame,
    solicitudes: pd.DataFrame,
    sim: pd.DataFrame | None = None,
) -> dict:
    """Contrato `analisis.json`: quita las filas sin renta (secreto del INE) y los NaN pasan a `None`. Con
    `sim` (de `bloque_simulacion`), añade el bloque `simulacion`."""
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
    if sim is not None:
        bloques["simulacion"] = _registros(sim, api_estatica.BLOQUES["simulacion"][0])
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


def exceso_tope(pares: pd.DataFrame, base: pd.DataFrame, perfil: str) -> pd.Series:
    """€/mes en que el alquiler pasa del tope en los municipios donde `perfil` no cumple el Bono vigente; falla
    si alguno no cumple por otra causa que el tope (en los perfiles con ingresos y edad dentro)."""
    v = base[(base["perfil"] == perfil) & (base["criterio"] == "bono_vigente")]
    fuera = v.loc[~v["elegible"], "municipio_id"]
    zonas = pares[pares["perfil"] == perfil].drop_duplicates("zona_id")
    # como `simulacion._municipios`: el alquiler del municipio es la mediana de sus zonas
    renta = zonas.groupby("municipio_id")["alquiler"].median()[fuera]
    exceso = renta - [float(simulacion.tope(m, "vivienda")) for m in fuera]
    if (exceso <= 0).any():
        raise ValueError(
            f"{perfil}: fuera del Bono sin pasar del tope en {list(exceso[exceso <= 0].index)}"
        )
    return exceso


def _simular(api: dict) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Simulación del Bono y fin del descuento, como `simulacion.main` sin sus sensibilidades salvo las que publica
    el informe; escribe los mismos CSV en `data/processed/`. Devuelve el bloque, la tabla base y los pares."""
    matriz = matriz_trabajo.leer_matriz()
    w, excluida = matriz_trabajo.pesos(matriz, matriz_trabajo.leer_cuotas_distritos())
    pares = simulacion._pares(api, w)
    base = simulacion.simulacion(pares)
    bruto = simulacion.simulacion(pares, ingresos="bruto")
    sin_imputar = simulacion.simulacion(pares[~pares["imputado"]])
    cal = simulacion.calidad(
        pares, excluida, matriz_trabajo.ocupados_observados(matriz)
    )
    fin = simulacion.fin_descuento(api)
    simulacion.PROCESSED.mkdir(parents=True, exist_ok=True)
    for nombre, df in (
        ("simulacion", base),
        ("simulacion_calidad", cal),
        ("simulacion_fin_descuento", fin),
    ):
        df.to_csv(simulacion.PROCESSED / f"{nombre}.csv", index=False)
    una = pares[pares["perfil"] == simulacion.IDS[0]]
    LOG.info(
        "Pares (zona, destino) con peso: %d; con 120 min imputados: %d",
        (una["w"] > 0).sum(),
        una["imputado"].sum(),
    )
    LOG.info(
        "Marcas de calidad (de %d municipios): %s",
        len(cal),
        cal[MARCAS].sum().to_dict(),
    )
    for nombre, df in (
        ("base", base),
        ("ingresos = bruto", bruto),
        ("sin pares imputados", sin_imputar),
    ):
        LOG.info(
            "Simulación, %s:\n%s",
            nombre,
            simulacion.cambios(df).set_index(["perfil", "criterio"]).to_string(),
        )
    return bloque_simulacion(base, bruto, sin_imputar, fin, cal), base, pares  # fmt: skip


def _figuras_n1(api: dict, res: list, sim: tuple, zonas) -> None:
    """Figuras de titulares, tope del Bono y fin del descuento, con las cifras que las acompañan en el log."""
    bloque, base, pares = sim
    figuras.titulares_perfiles(res, APP_IMG / "titulares_perfiles.png")
    v = base[(base["perfil"] == "smi_30") & (base["criterio"] == "bono_vigente")]
    testigos = pd.Series(
        {z: d["testigos"] for z, d in api["alquiler"]["zonas"].items()}, dtype=float
    )
    sin, pocos = figuras.mapa_bono_tope(
        v.set_index("municipio_id")["elegible"],
        testigos.dropna(),
        zonas,
        APP_IMG / "bono_tope.png",
    )
    exceso = exceso_tope(pares, base, "smi_30")
    LOG.info(
        "Mapa del tope (smi_30): %d de %d municipios dentro; fuera %d, %d por menos de 80 €/mes; zonas sin dato %d, "
        "alquiler impreciso %d; exceso (€/mes):\n%s",
        v["elegible"].sum(),
        len(v),
        len(exceso),
        (exceso < 80).sum(),
        sin,
        pocos,
        exceso.sort_values().round(2).to_string(),
    )
    coronas = pd.Series(
        {
            f["properties"]["municipio_id"]: f["properties"]["corona"]
            for f in api["zonas"]["features"]
        }
    )
    fin = bloque[bloque["criterio"].str.startswith("fin_")]
    figuras.fin_descuento_coronas(fin, coronas, APP_IMG / "fin_descuento.png")
    LOG.info("Fin del descuento por corona (€/mes, media del año):\n%s", figuras.fin_por_corona(fin, coronas).to_string())  # fmt: skip


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    zona = alquiler.alquiler_zona(alquiler.leer_serpavi())
    tabla = esfuerzo.esfuerzo(zona, renta.renta())
    crudo = bono.leer_bono()
    solicitudes = bono._por_anio(
        crudo, bono.poblacion_joven(bono._edades()), tabla, bono.ANIO
    )
    _controlar(crudo, solicitudes, tabla)
    api = calculo.leer_api(APP_DATOS)
    sim = _simular(api)
    objeto = analisis_json(tabla, solicitudes, sim[0])
    LOG.info(
        "Filas de esfuerzo sin renta (secreto del INE) quitadas: %d",
        tabla["renta_hogar_mes"].isna().sum(),
    )
    for t in objeto["titulares"]:
        LOG.info("Titular: %s", t["texto"])
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
    _figuras_n1(api, res, sim, zonas)
    LOG.info(
        "Sobrecarga de los hogares inquilinos de la Comunidad, ECV 2025 (control de F3-06; estimado):\n%s",
        sobrecarga_ecv.control_f306(sobrecarga_ecv.hogares()).round(1).to_string(),
    )
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
