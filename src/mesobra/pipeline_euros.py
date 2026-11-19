"""Encadena alquiler, neto, transporte y hogares y escribe los cuatro JSON de `app/datos/`.

No calcula nada nuevo: solo da forma al contrato de `api_estatica`. Ejecutar con
`python -m mesobra.pipeline_euros`. Todos los valores salen en tipos nativos de Python.
"""

from datetime import date
from pathlib import Path

import geopandas as gpd
import pandas as pd

from mesobra import (
    alquiler,
    api_estatica,
    hogares,
    imputacion,
    neto,
    transporte,
    zonas,
)

APP_DATOS = Path(__file__).resolve().parents[2] / "app/datos"
PROCESSED = Path(__file__).resolve().parents[2] / "data/processed"
MADRID = "28079"
SERPAVI = {
    "nombre": "SERPAVI, Ministerio de Vivienda y Agenda Urbana. Origen de los datos: Ministerio de Vivienda y Agenda Urbana",
    "url": "https://cdn.mivau.gob.es/portal-web-mivau/vivienda/serpavi/2026-03_09_bd_SERPAVI_2011-2024%20-%20DEFINITIVO%20WEB_v2.xlsx",
    "licencia": "Condiciones generales para la reutilización de información del MIVAU (RD 1495/2011)",
}
IPC_INE = {
    "nombre": "INE, IPC base 2025 por comunidades autónomas y subgrupos ECOICOP (tabla 76137), serie IPC297196 «Madrid, Comunidad de. Alquiler de vivienda. Índice». Elaboración propia con datos extraídos del sitio web del INE: www.ine.es",
    "url": "https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/76137.csv",
    "licencia": "CC BY 4.0",
}
IPC_CM = {
    "nombre": "IPC de la vivienda en alquiler, base 2025 (catálogo de datos abiertos de la Comunidad de Madrid, 1934665), usado como control. Fuente de los datos: Comunidad de Madrid",
    "url": "https://datos.comunidad.madrid/dataset/fc22e79d-c04b-4537-8b4b-fe92516b989e/resource/3d1f3acc-98cc-4356-b9e1-4b9e5d999787/download/indice-de-precios-de-consumo.-vivienda-en-alquiler-base-2025.csv",
    "licencia": "CC BY 4.0",
}
AEAT_VIVIENDAS = {
    "nombre": "Estadística de viviendas declaradas en el IRPF 2024, comparativa con los nuevos contratos por "
    "provincia, municipio y código postal. Fuente: Agencia Tributaria",
    "url": "https://sede.agenciatributaria.gob.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/"
    "Publicaciones/sites/irpfvivienda/2024/home.html",
    "licencia": "Reutilización autorizada citando la fuente y sin desnaturalizar (aviso legal de la sede de la AEAT)",
}
# mismo extracto que `pipeline_territorio.OSM`, que importa este módulo
OSM_PORTALES = {
    "nombre": "OpenStreetMap, extracto de Geofabrik de la Comunidad de Madrid del 2026-11-13 (portales con "
    "código postal). © OpenStreetMap contributors",
    "url": "https://download.geofabrik.de/europe/spain/madrid-261113.osm.pbf",
    "licencia": "ODbL 1.0 (https://www.openstreetmap.org/copyright)",
}
LICENCIA_BOE = (
    "Reutilización con cita de la fuente (aviso legal del BOE): basado en datos de la Agencia "
    "Estatal Boletín Oficial del Estado; el texto consolidado tiene carácter meramente informativo"
)
LICENCIA_BOCM = "Disposición oficial, sin derechos de propiedad intelectual (art. 13 del TRLPI, BOE-A-1996-8930)"
ORIGEN_SERPAVI = (
    "Origen de los datos: Ministerio de Vivienda y Agenda Urbana, actualizado el 2026-07-09; "
    "el Ministerio no participa ni patrocina este proyecto."
)
CATALOGO = "https://datos.comunidad.madrid/dataset/"
EPF = (
    CATALOGO
    + "{}/download/gasto-medio-de-los-hogares-por-subgrupo-de-gasto-{}-digitos-coicopepf-base-2006.csv"
)


def _boe(nombre: str, url: str) -> dict[str, str]:
    return {"nombre": nombre, "url": url, "licencia": LICENCIA_BOE}


FUENTES_NETOS = [
    _boe(
        "LIRPF (BOE-A-2006-20764)",
        "https://www.boe.es/buscar/act.php?id=BOE-A-2006-20764",
    ),
    _boe(
        "Orden PJC/297/2026 (BOE-A-2026-7296)",
        "https://www.boe.es/buscar/doc.php?id=BOE-A-2026-7296",
    ),
    _boe(
        "RDL 5/2026 (BOE-A-2026-3810)",
        "https://www.boe.es/buscar/doc.php?id=BOE-A-2026-3810",
    ),
    _boe(
        "Decreto Legislativo 1/2010 de la Comunidad de Madrid, tributos cedidos (BOCM-m-2010-90068)",
        "https://www.boe.es/buscar/act.php?id=BOCM-m-2010-90068",
    ),
]
FUENTES_TARIFAS = (
    [
        {"nombre": nombre, "url": url, "licencia": LICENCIA_BOCM}
        for nombre, url in (
            (
                "BOCM nº 311 de 31-12-2025, BOCM-20251231-2: precios del transporte público en 2026 (copia del CRTM)",
                "https://www.crtm.es/media/s1qi0nmo/bocm-20251231-precios_transporte.pdf",
            ),
            (
                "BOCM nº 311 de 31-12-2025, BOCM-20251231-3: tarifas oficiales del transporte público (copia del CRTM)",
                "https://www.crtm.es/media/sjqj4ggj/bocm-20251231-tarifas_transporte.pdf",
            ),
            (
                "Decreto 75/2025, BOCM nº 229 de 25-09-2025, BOCM-20250925-16: fiestas laborales de 2026 en la Comunidad de Madrid",
                "https://www.bocm.es/bocm-20250925-16",
            ),
        )
    ]
    + [
        _boe(
            "Estatuto de los Trabajadores (BOE-A-2015-11430), arts. 37.2 (fiestas) y 38.1 (vacaciones)",
            "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430",
        ),
    ]
    + [
        {
            "nombre": nombre,
            "url": url,
            "licencia": "Licencia de datos abiertos del CRTM (https://www.crtm.es/licencia-de-uso/)",
        }
        for nombre, url in (
            (
                "Ficha del Abono Joven, Consorcio Regional de Transportes de Madrid",
                "https://www.crtm.es/billetes-y-tarifas/buscador/abono-joven/",
            ),
            (
                "Ficha de sencillos y 10 viajes (validez del 10 viajes), Consorcio Regional de Transportes de Madrid",
                "https://www.crtm.es/billetes-y-tarifas/buscador/sencillos-y-10-viajes/",
            ),
            (
                "Ficha del Abono +65, Consorcio Regional de Transportes de Madrid",
                "https://www.crtm.es/billetes-y-tarifas/buscador/abono-plus65/",
            ),
            (
                "CoronasTarifarias Vigentes CRTM (capa de coronas, abril de 2025)",
                "https://datos.crtm.es/datasets/crtm::coronastarifarias-vigentes-crtm",
            ),
        )
    ]
    + [
        {
            "nombre": "Abonos bonificados de Renfe 2026, preguntas frecuentes (Abono mensual de Cercanías)",
            "url": "https://www.renfe.com/es/es/promociones/abonos-renfe/abonos-bonificados/preguntas-frecuentes",
            "licencia": "Licencia no comprobada (verificar); solo se cita el precio del título",
        },
    ]
)
EPF_IDS = {
    3: "39d6f25b-e043-428f-b8f6-4a46214bf34e/resource/83b08257-b457-4fe4-a11b-0fd37a2c33f7",
    4: "87b3102d-79f3-44ab-8b33-3f347bbe048b/resource/88ed4858-b94e-40e5-aae5-8a2d786546b4",
}
FUENTES_HOGARES = [
    {
        "nombre": f"INE, Encuesta de Presupuestos Familiares, {d} dígitos. Fuente de los datos: Comunidad de Madrid",
        "url": EPF.format(i, d),
        "licencia": "CC BY 4.0",
    }
    for d, i in EPF_IDS.items()
] + [SERPAVI]


def _meta(
    anio_dato: int, fuentes: list[dict[str, str]], nota: str
) -> dict[str, object]:
    return {
        "generado": date.today().isoformat(),
        "anio_dato": anio_dato,
        "fuentes": fuentes,
        "nota": nota,
    }


def _ultimo_anio(zona: pd.DataFrame) -> pd.DataFrame:
    """Fila del último año con `eur_m2_p50` por zona, sin Madrid entero (28079)."""
    con_dato = zona[(zona["zona_id"] != MADRID) & zona["eur_m2_p50"].notna()]
    return con_dato.sort_values("anio").groupby("zona_id").tail(1)


def alquiler_json(zona: pd.DataFrame) -> dict:
    ultimo = _ultimo_anio(zona).set_index("zona_id")
    brecha = zona.drop_duplicates("zona_id").set_index("zona_id")
    zonas = {}
    for zid in sorted(set(zona["zona_id"]) - {MADRID}):
        b = brecha.loc[zid]
        zonas[zid] = {
            "factor_brecha": float(b["factor_brecha"]),
            "brecha_ambito": b["brecha_ambito"],
        }
        if zid not in ultimo.index:
            zonas[zid] |= dict.fromkeys(["anio", "p25", "p50", "p75", "m2", "ic"])
            zonas[zid] |= {"factor_ipc": 1.0, "origen": "sin_dato"}
            continue
        f = ultimo.loc[zid]
        zonas[zid] |= {
            "anio": int(f["anio"]),
            "p25": float(f["eur_m2_p25"]),
            "p50": float(f["eur_m2_p50"]),
            "p75": float(f["eur_m2_p75"]),
            "m2": None if pd.isna(f["m2_p50"]) else float(f["m2_p50"]),
            "factor_ipc": float(f["factor_ipc"]),
            "origen": f["origen"],
            "ic": [float(f["ic_inf"]), float(f["ic_sup"])]
            if f["origen"] == "estimado"
            else None,
        }
    anio = int(zona["anio"].max())
    if (mes := zona.attrs.get("ipc_hasta")) is None:
        raise ValueError(
            "Falta attrs['ipc_hasta']: pasa la zona por alquiler.actualizar_ipc"
        )
    nota = (
        "€/m² al mes de vivienda colectiva (sin unifamiliar), de contratos declarados a la Agencia "
        "Tributaria (Modelo 100 cruzado con el Catastro), no de anuncios: es un suelo del precio actual. "
        "Cada zona lleva el último año con dato y p25, p50 y p75 en euros de ese año; factor_ipc los "
        f"actualiza a {mes} con el IPC de alquiler de la Comunidad de Madrid (INE, serie IPC297196, "
        f"índice de {mes} entre la media del año de la zona), una estimación; las zonas cuyo último "
        f"dato es anterior a {anio} llevan su año en anio. Las zonas sin dato publicado van como "
        "sin_dato. Elaboración propia con datos extraídos del sitio web del INE: www.ine.es (tabla 76137 "
        "actualizada el 2026-11-13); el INE no participa ni patrocina este proyecto. "
        "Fuente de los datos: Comunidad de Madrid (IPC de alquiler 1934665, actualizado el 2026-11-05, "
        "usado como control). "
        + ORIGEN_SERPAVI
        + " factor_brecha (estimado) lleva ese precio al de los "
        "contratos formalizados en 2024: €/m² de los nuevos contratos ÷ €/m² de todos, con las medias de "
        "alquiler mensual y de m² de la Estadística de viviendas declaradas en el IRPF 2024 (misma base "
        "fiscal que el SERPAVI, pero medias y no medianas). brecha_ambito dice de dónde sale: municipio "
        "(los de más de 20.000 habitantes), codigo_postal (los distritos de Madrid, desde sus códigos "
        "postales ponderados por viviendas arrendadas y repartidos por portales de OpenStreetMap, que "
        "cruzan límites de distrito) o comunidad (el de la Comunidad de Madrid). p50 × factor_ipc es el "
        "precio de contrato y × factor_brecha el de contrato nuevo, que sigue siendo un suelo: el IPC de "
        "alquiler sigue los contratos en vigor, y los nuevos suben más. Fuente: Agencia Tributaria (la "
        "tabla no publica fecha de actualización; consultada el 2026-11-19). © OpenStreetMap contributors "
        "(extracto de Geofabrik actualizado el 2026-11-13, ODbL 1.0)."
    )
    fuentes = [SERPAVI, IPC_INE, IPC_CM, AEAT_VIVIENDAS, OSM_PORTALES]
    if n := int((zona["origen"] == "estimado").sum()):
        nota += (
            f" {n} zonas sin dato publicado llevan origen estimado: €/m² de vivienda colectiva de {anio} "
            "estimado con un modelo espacial (mesobra.imputacion, #99) a partir de las zonas vecinas, la "
            "renta media por hogar del ADRH (tabla 31097 actualizada el 2026-10-15), la población y los "
            "tiempos en transporte público de tiempos.json; ic es el intervalo de predicción conformal "
            f"al {imputacion.NIVEL * 100:.0f} % del p50 (cobertura medida, no garantizada) y p25 y p75 salen de los cocientes "
            "medianos observados. Sin cuantía mensual, así que esas zonas no tienen esfuerzo."
        )
        fuentes.append(imputacion.FUENTE_ADRH)
    meta = _meta(anio, fuentes, nota) | {"ipc_hasta": mes}
    return {"meta": meta, "zonas": zonas}


def m2_por_defecto(zona: pd.DataFrame) -> int:
    """Mediana ponderada por `testigos` de `m2_p50` en el último año con dato de cada zona.

    Se ordena por `m2_p50`, se acumulan los testigos y se toma el primer valor cuya suma
    acumulada llega a la mitad del total. Madrid entero (28079) no entra.
    """
    f = _ultimo_anio(zona[zona["origen"] == "observado"]).sort_values("m2_p50")
    acumulado = f["testigos"].cumsum()
    return round(float(f.loc[acumulado >= f["testigos"].sum() / 2, "m2_p50"].iloc[0]))


def netos_json(rejilla: pd.DataFrame) -> dict:
    pivot = rejilla.pivot(
        index="bruto_anual", columns=["hijos", "monoparental"], values="neto_anual"
    )
    if pivot.isna().any(axis=None):
        raise ValueError("La rejilla de netos no cubre todas las combinaciones")
    nota = (
        "Neto anual en € de 2026 desde el bruto anual: cotización del trabajador e IRPF estatal y de "
        "Madrid (cuota de la declaración). Tributación individual, sin deducciones reembolsables ni "
        "autonómicas (un monoparental con dos hijos queda hasta 1.200 €/año por debajo), contrato "
        "indefinido, menor de 65 años. Rejilla de 12.000 a 120.000 €: fuera de ella no se extrapola."
    )
    return {
        "meta": _meta(2026, FUENTES_NETOS, nota),
        "brutos": [int(b) for b in pivot.index],
        "configuraciones": [
            {"hijos": int(h), "monoparental": bool(m)} for h, m in pivot.columns
        ],
        "neto_anual": pivot.values.tolist(),
    }


def _filas(g: pd.DataFrame) -> list[dict]:
    return [
        {"titulo": t, "coste_mes": float(c)}
        for t, c in g.sort_values("dias")[["titulo", "coste_mes"]].itertuples(
            index=False
        )
    ]


def _matriz_claves(
    claves: pd.DataFrame, ids: list[str], lista: list[str]
) -> list[list[int | None]]:
    """Posición en `lista` de la clave de cada origen (filas) × destino (columnas), en el orden de `ids`."""
    if claves.duplicated(["zona_id", "destino_id"]).any():
        raise ValueError("pares origen-destino repetidos en las claves de tarifa")
    m = claves.pivot(index="zona_id", columns="destino_id", values="clave_tarifa")
    if set(m.index) != set(ids) or set(m.columns) != set(ids):
        raise ValueError("las claves de tarifa no tienen los mismos ids que las zonas")
    m = m.loc[ids, ids]
    pos = {c: i for i, c in enumerate(lista)}
    return [[None if pd.isna(c) else pos[c] for c in fila] for fila in m.to_numpy()]


def tarifas_json(
    v1: pd.DataFrame, v2: pd.DataFrame, claves: pd.DataFrame, ids: list[str]
) -> dict:
    """`tarifas.json`: la forma v1 de #80 (`escenarios`) y la v2 por ruta (`clave_tarifa`, `tarifas_ruta`).

    `claves`: `zona_id`, `destino_id`, `clave_tarifa` y `clave_estimada`; `ids`, en el orden de `tiempos.json`.
    """
    escenarios = {}
    for (esc, joven, viajes, corona), g in v1.groupby(
        ["escenario", "joven", "viajes_dia", "corona"]
    ):
        edad = "joven" if joven else "general"
        por_viajes = escenarios.setdefault(esc, {}).setdefault(edad, {})
        por_viajes.setdefault(str(viajes), {})[corona] = _filas(g)
    ruta = {}
    for (esc, col, edad, clave, nl), g in v2.groupby(
        ["escenario", "colectivo", "edad", "clave_tarifa", "no_laborables"]
    ):
        por_edad = ruta.setdefault(esc, {}).setdefault(col, {}).setdefault(edad, {})
        por_edad.setdefault(clave, {})[str(nl)] = _filas(g)
    lista = sorted(v2["clave_tarifa"].unique())
    nota = (
        "Título más barato al mes (€/mes) con los precios de 2026 del BOCM de 31-12-2025. vigente_2026 "
        "lleva el descuento del RDL 17/2025, que solo vale para 2026; sin_descuento, los precios "
        "oficiales. coste_mes es la media mensual del año (1/12), estimada con supuestos: 227 días de "
        "trabajo al año (calendario laboral de 2026 de la Comunidad de Madrid, Decreto 75/2025; supuestos: "
        "2 festivos locales en laborable y 22 laborables de vacaciones en un bloque); el Abono 30 días y "
        "el Abono Joven se compran 335/30 veces al año; sin abono anual (venta a particulares suspendida "
        "desde 2023); el 10 viajes se prorratea porque no caduca (ficha del CRTM: «Validez: Ilimitada»); "
        "el billete sencillo de la zona A, a 1,50 € (EMT o Metro de hasta 5 estaciones). "
        "tarifas_ruta (#162): clave_tarifa da, para cada par origen × destino, la posición en claves de su clave, que junta el rango de coronas que "
        "atraviesa la ruta y un producto por validación; se compara el abono que cubre el rango (normal "
        "con A, interzonal sin A) con el sencillo o el 10 viajes de cada producto, el Abono Joven y el "
        "Abono +65 (gratuito; desde los 65 años, edad por verificar). Cercanías: abono del CRTM o Abono "
        "mensual de Renfe (20 €, solo con descuento). no_laborables: viajes de ocio al mes, cobrados en el "
        "producto principal de la ruta. Colectivos: precio de su columna en el BOCM (discapacidad igual o "
        "superior al 65 %, familia numerosa general o especial, y las dos con discapacidad); el Abono de "
        "Renfe, igual para todos. "
        + (
            "Rango de coronas estimado: coronas que cruza la recta entre los centros de las zonas, con "
            "una validación (heurística de #161 hasta tener la ruta de r5py). Subestima el coste entre "
            "periferias: la recta deja sin zona A el 79 % de esos pares, aunque en la red radial suelen pasar "
            "por Madrid, y les aplica el abono interzonal. "
            if claves["clave_estimada"].any()
            else ""
        )
        + "escenarios (forma v1 de #80, hasta #164): viajes_dia 2, ida y vuelta pasando por la zona A; "
        "4, con cambio a Metro de la zona A en cada sentido. "
        f"Abono Joven de {transporte.EDAD_MIN_JOVEN} a {transporte.EDAD_MAX_JOVEN} años."
    )
    return {
        "meta": _meta(2026, FUENTES_TARIFAS, nota),
        "orden_coronas": [c for c in api_estatica.CORONAS if c in set(v1["corona"])],
        "edad_max_joven": transporte.EDAD_MAX_JOVEN,
        "viajes_dia": list(api_estatica.VIAJES_DIA),
        "semanas_mes": float(transporte.SEMANAS_MES),
        "escenarios": escenarios,
        "clave_estimada": bool(claves["clave_estimada"].any()),
        "origenes": ids,
        "destinos": ids,
        "claves": lista,
        "colectivos": list(api_estatica.COLECTIVOS),
        "edades": list(api_estatica.EDADES),
        "no_laborables": list(api_estatica.NO_LABORABLES),
        "clave_tarifa": _matriz_claves(claves, ids, lista),
        "tarifas_ruta": ruta,
    }


def rutas() -> tuple[pd.DataFrame, list[str]]:
    """Clave de tarifa de cada par de zonas: con las columnas de #161 si `tiempos` ya las trae; si no, la heurística."""
    z = gpd.read_parquet(PROCESSED / "zonas.parquet").sort_values("zona_id")
    tiempos = PROCESSED / "tiempos.parquet"
    tp = pd.read_parquet(tiempos).query("modo == 'tp'") if tiempos.exists() else None
    # la columna `estimado` de tiempos es otra cosa (línea base o líneas reconstruidas, #173)
    estimada = tp is None or "corona_min" not in tp
    if estimada:
        tp = transporte.rango_coronas(z, zonas.leer_coronas())
    tp = tp.reset_index(drop=True)
    tp["clave_tarifa"] = transporte.claves(tp)
    tp["clave_estimada"] = estimada
    return tp, z["zona_id"].tolist()


def hogares_json(tabla: pd.DataFrame, cesta: pd.Series, m2: int) -> dict:
    columnas = ["adultos", "hijos", "personas_comparten", "alimentacion", "suministros"]
    perfiles = {
        f["perfil"]: {"m2": m2, **{c: f[c] for c in columnas}}
        for f in tabla.to_dict("records")
    }
    nota = (
        f"{tabla.attrs['nota']}. m² por defecto: {m2} para todos los perfiles, la mediana de la "
        "superficie mediana (m2_p50) de cada zona en su último año con dato del SERPAVI, ponderada por "
        "testigos; el formulario permite cambiarlo. Un mismo m² para todos sobreestima el alquiler de "
        "quien vive solo. EPF del catálogo de la Comunidad de Madrid actualizada el 2026-11-05 "
        "(fuente de los datos: Comunidad de Madrid); alimentación = 01.1 + 01.2 y suministros = "
        "04.5 + 04.4.1, gasto anual por unidad de consumo entre 12. " + ORIGEN_SERPAVI
    )
    return {
        "meta": _meta(int(tabla["anio"].iloc[0]), FUENTES_HOGARES, nota),
        "perfiles": perfiles,
        "cesta_uc": {k: float(v) for k, v in cesta.items()},
    }


def main() -> None:
    claves, ids = rutas()
    zona = alquiler.actualizar_ipc(
        alquiler.alquiler_zona(alquiler.leer_serpavi()), alquiler.leer_ipc()
    )
    zona = imputacion.imputar(zona, *imputacion.leer_entradas())
    tabla_cp = alquiler.tabla_paso_cp(alquiler.leer_portales(), zonas.leer_secciones())
    zona = alquiler.brecha_por_zona(zona, alquiler.leer_brecha(), tabla_cp)
    salidas = {
        "alquiler.json": alquiler_json(zona),
        "netos.json": netos_json(neto.rejilla()),
        "tarifas.json": tarifas_json(
            transporte.tabla_v1(),
            transporte.tabla(claves["clave_tarifa"].dropna().unique().tolist()),
            claves,
            ids,
        ),
        "hogares.json": hogares_json(
            hogares.hogares(), hogares.cesta_uc(), m2_por_defecto(zona)
        ),
    }
    for nombre, objeto in salidas.items():
        api_estatica.escribir(nombre, objeto, APP_DATOS)


if __name__ == "__main__":
    main()
