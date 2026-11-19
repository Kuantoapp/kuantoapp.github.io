"""Alquiler por zona y por sección censal desde el Excel del SERPAVI (MIVAU), vivienda colectiva.

Lee el Excel una vez, se queda con la Comunidad de Madrid y guarda un intermedio por hoja en
`data/processed/`. Produce `alquiler_zona` y `alquiler_seccion` (contratos en `contratos.py`).
Las celdas que el SERPAVI no publica (pocos testigos) quedan nulas, nunca en cero.
"""

import html
import logging
import re
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

from mesobra import contratos, paso_secciones, zonas

LOG = logging.getLogger(__name__)

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data/raw/serpavi_bd_2011_2024_2026-11-15.xlsx"
PROCESSED = RAIZ / "data/processed"
RAW_IPC = RAIZ / "data/raw/ine_ipc_ccaa_subgrupos_2026-11-15.csv"
RAW_IPC_CM = RAIZ / "data/raw/cm_ipc_alquiler_base2025_2026-11-15.csv"
SERIE_IPC = (
    "13 Madrid, Comunidad de",
    "04.1 Alquiler de vivienda",
    "Índice",
)  # IPC297196
# AEAT, Estadística de viviendas declaradas en el IRPF 2024: comparativa con los nuevos contratos (#251)
RAW_AEAT = {
    k: RAIZ / f"data/raw/aeat_irpfvivienda2024_nuevos_{k}_2026-11-19.html"
    for k in ("provincia", "municipios", "cp", "cp_viviendas")
}
PROVINCIA = "Madrid, Comunidad de"

# clave -> (hoja, columna de código, ancho del código INE)
HOJAS = {
    "municipios": ("Municipios", "CUMUN", 5),
    "distritos": ("Distritos", "CUDIS", 7),
    "secciones": ("Secciones censales", "CUSEC", 10),
}
TESTIGOS = {"BI_ALVHEPCO_TVC": "testigos"}
EUR_M2 = {
    "ALQM2_LV_25_VC": "eur_m2_p25",
    "ALQM2_LV_M_VC": "eur_m2_p50",
    "ALQM2_LV_75_VC": "eur_m2_p75",
}
CUANTIA = {
    "ALQTBID12_25_VC": "cuantia_p25",
    "ALQTBID12_M_VC": "cuantia_p50",
    "ALQTBID12_75_VC": "cuantia_p75",
}
M2 = {"SLVM2_M_VC": "m2_p50"}
PATRON_MEDIDA = rf"^({'|'.join({**TESTIGOS, **EUR_M2, **CUANTIA, **M2})})_\d{{2}}$"


def _limpio(v):
    """Vacío a nulo; formato español ("1.234,5") a decimal; el resto, tal cual."""
    if not isinstance(v, str):
        return v
    v = v.strip()
    # shortcut: "1.234" sin coma se lee como decimal, el SERPAVI publica números; revisar si cambia
    return v.replace(".", "").replace(",", ".") if "," in v else (v or pd.NA)


def _numero(serie: pd.Series) -> pd.Series:
    """Serie numérica: un valor ilegible falla, nunca se convierte en nulo."""
    return pd.to_numeric(serie.map(_limpio), errors="raise")


def leer_serpavi(
    ruta: Path = RAW, carpeta: Path = PROCESSED
) -> dict[str, pd.DataFrame]:
    """Hojas de la Comunidad de Madrid (código y medidas numéricas), con caché en parquet."""
    cache = {k: carpeta / f"{ruta.stem}_{k}.parquet" for k in HOJAS}
    if all(p.exists() for p in cache.values()):
        return {k: pd.read_parquet(p) for k, p in cache.items()}
    dtype = {col: str for _, col, _ in HOJAS.values()}
    excel = pd.read_excel(
        ruta, sheet_name=[h for h, _, _ in HOJAS.values()], dtype=dtype
    )
    carpeta.mkdir(parents=True, exist_ok=True)
    hojas = {}
    for clave, (hoja, col, ancho) in HOJAS.items():
        df = excel[hoja]
        df[col] = df[col].str.strip().str.zfill(ancho)
        df = df[df[col].str.startswith("28")]
        medidas = df.filter(regex=PATRON_MEDIDA).apply(_numero)
        hojas[clave] = pd.concat([df[[col]], medidas], axis=1).reset_index(drop=True)
        hojas[clave].to_parquet(cache[clave])
    return hojas


def _largo(df: pd.DataFrame, id_col: str, renombre: dict[str, str]) -> pd.DataFrame:
    """De una columna por variable y año (`VAR_24`) a una fila por unidad y año."""
    columnas = [c for c in df if c.rsplit("_", 1)[0] in renombre]
    # wide_to_long rellena con NaN una variable o un año que falte: exige variable × año completo
    anios = {c.rsplit("_", 1)[1] for c in columnas}
    if not columnas or len(columnas) != len(renombre) * len(anios):
        raise ValueError(f"Faltan variables o años del SERPAVI: {sorted(columnas)}")
    largo = pd.wide_to_long(
        df[[id_col, *columnas]],
        stubnames=list(renombre),
        i=id_col,
        j="aa",
        sep="_",
        suffix=r"\d{2}",
    ).reset_index()
    largo["anio"] = 2000 + largo.pop("aa").astype(int)
    return largo.rename(columns=renombre)


def _comprobar(df: pd.DataFrame) -> None:
    """P25 <= mediana <= P75 con los tres nulos a la vez, en €/m² y en cuantía, y ambos nulos a la vez."""
    mal = df["cuantia_p50"].isna() != df["eur_m2_p50"].isna()
    for prefijo in ("eur_m2", "cuantia"):
        p25, p50, p75 = (df[f"{prefijo}_p{p}"] for p in (25, 50, 75))
        mal |= (
            (p25 > p50)
            | (p50 > p75)
            | (p25.isna() != p50.isna())
            | (p75.isna() != p50.isna())
        )
    if mal.any():
        raise ValueError(
            f"{int(mal.sum())} filas con percentiles incoherentes:\n{df[mal].head()}"
        )


def _tipado(df: pd.DataFrame, nombre: str) -> pd.DataFrame:
    contrato = contratos.CONTRATOS[nombre]
    df = df[list(contrato["columnas"])].astype(contratos.dtypes(nombre))
    _comprobar(df)
    contratos.validar(df, nombre)
    return df.sort_values(list(contrato["clave"])).reset_index(drop=True)


def alquiler_zona(hojas: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """178 municipios, Madrid (28079) y sus 21 distritos, por año."""
    renombre = {**TESTIGOS, **EUR_M2, **CUANTIA, **M2}
    distritos = hojas["distritos"][hojas["distritos"]["CUDIS"].str.startswith("28079")]
    zonas = pd.concat(
        [
            _largo(hojas["municipios"], "CUMUN", renombre).rename(
                columns={"CUMUN": "zona_id"}
            ),
            _largo(distritos, "CUDIS", renombre).rename(columns={"CUDIS": "zona_id"}),
        ],
        ignore_index=True,
    )
    zonas["origen"] = (
        zonas["eur_m2_p50"].notna().map({True: "observado", False: "sin_dato"})
    )
    zonas["ic_inf"] = zonas["ic_sup"] = float("nan")
    zonas["factor_ipc"] = 1.0
    return _tipado(zonas, "alquiler_zona")


def leer_ipc(ruta: Path = RAW_IPC, ruta_cm: Path = RAW_IPC_CM) -> pd.Series:
    """Índice mensual del IPC de alquiler de Madrid (INE, IPC297196) por periodo `AAAAMmm`, contrastado con el catálogo regional."""
    df = pd.read_csv(ruta, sep=";", encoding="utf-8-sig", dtype=str)
    df = df[(df.iloc[:, :3] == list(SERIE_IPC)).all(axis=1)]
    ipc = pd.Series(_numero(df["Total"]).to_numpy(), index=df["Periodo"]).sort_index()
    if ipc.empty or ipc.isna().any() or ipc.index.has_duplicates:
        raise ValueError(
            f"La serie {SERIE_IPC} está vacía, tiene huecos o repite periodos"
        )
    cm = pd.read_csv(ruta_cm, sep=";", encoding="utf-8-sig", dtype={"Año": str})
    medias = ipc.groupby(ipc.index.str[:4]).mean()
    # las dos filas de cada año (Madrid y Nacional) vienen en orden variable: basta con que una case
    casa = (
        (cm["Valor"] - cm["Año"].map(medias)).abs().le(0.0015).groupby(cm["Año"]).any()
    )
    if not casa.all():
        raise ValueError(
            f"El catálogo de la CM no casa con el INE en {list(casa.index[~casa])}"
        )
    return ipc


def actualizar_ipc(zona: pd.DataFrame, ipc: pd.Series) -> pd.DataFrame:
    """`factor_ipc` = índice del último mes ÷ media anual del año de cada fila (ficha §6.2, #94); p25/p50/p75 no cambian."""
    # `iloc[-1]` tiene que ser el último mes aunque la serie llegue desordenada
    ipc = ipc.sort_index()
    anios = ipc.index.str[:4].astype(int)
    medias = ipc.groupby(anios).agg(["mean", "size"])
    medias = medias.loc[medias["size"] == 12, "mean"]
    if falta := sorted(set(zona["anio"]) - set(medias.index)):
        raise ValueError(f"Sin media anual del IPC (12 meses) para {falta}")
    df = zona.copy()
    df["factor_ipc"] = ipc.iloc[-1] / df["anio"].map(medias)
    df.attrs["ipc_hasta"] = f"{ipc.index[-1][:4]}-{ipc.index[-1][5:]}"
    contratos.validar(df, "alquiler_zona")
    return df


def leer_aeat(ruta: Path) -> pd.DataFrame:
    """Tabla HTML de la estadística de viviendas del IRPF de la AEAT: una fila por territorio, columnas numéricas.

    La tabla de detalle por código postal trae dos filas de cabecera; la comparativa, una.
    """
    texto = ruta.read_text(encoding="utf-8")
    filas = [
        [
            " ".join(html.unescape(re.sub(r"<[^>]+>", " ", c)).split())
            for c in re.findall(r"(?s)<t[hd][^>]*>.*?</t[hd]>", fila)
        ]
        for fila in re.findall(r"(?s)<tr.*?</tr>", texto)
    ]
    filas = [f for f in filas if f]
    ancho = max(len(f) for f in filas)
    dos = len(filas[0]) < ancho
    cabecera = filas[0][:1] + filas[1] if dos else filas[0]
    datos = filas[2 if dos else 1 :]
    if cabecera[0] != "Localización de la vivienda" or {len(cabecera)} | {
        len(f) for f in datos
    } != {ancho}:
        raise ValueError(f"{ruta.name}: la tabla no tiene el formato esperado")
    df = pd.DataFrame(datos, columns=cabecera).set_index(cabecera[0])
    # «1.167» son miles y «6,2» decimales: formato español sin excepciones
    return df.apply(
        lambda s: pd.to_numeric(
            s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
            errors="raise",
        )
    )


def factor_nuevos(df: pd.DataFrame) -> pd.Series:
    """€/m² de los contratos formalizados en el año ÷ €/m² de todos, con las medias de alquiler y m² de la AEAT."""
    nuevos = (
        df["Alquiler medio mensual (nuevos contratos)"]
        / df["m2 medios (nuevos contratos)"]
    )
    return nuevos / (df["Alquiler medio mensual"] / df["m2 medios"])


def leer_brecha(rutas: dict[str, Path] = RAW_AEAT) -> dict:
    """Factores de la AEAT: `municipio` (código INE), `cp` (factor y viviendas arrendadas) y `provincia`."""
    mun = factor_nuevos(leer_aeat(rutas["municipios"]))
    mun = mun[mun.index.str.contains(r"-28\d{3}$")]
    mun.index = mun.index.str[-5:]
    cp = leer_aeat(rutas["cp"])
    cp = cp[cp.index.str.match(r"28\d{3}-")]
    viviendas = leer_aeat(rutas["cp_viviendas"])["Número viviendas arrendadas"]
    viviendas = viviendas[viviendas.index.str.match(r"28\d{3}-")]
    if set(viviendas.index) != set(cp.index):
        raise ValueError(
            "Los códigos postales de la comparativa y del detalle no coinciden"
        )
    cp = pd.DataFrame({"factor": factor_nuevos(cp), "viviendas": viviendas})
    cp.index = cp.index.str[:5]
    provincia = factor_nuevos(leer_aeat(rutas["provincia"]).loc[[PROVINCIA]])
    if len(provincia) != 1 or mun.index.has_duplicates or cp.index.has_duplicates:
        raise ValueError("Territorios repetidos o ausentes en las tablas de la AEAT")
    return {"municipio": mun, "cp": cp, "provincia": float(provincia.iloc[0])}


def leer_portales(ruta: Path = zonas.OSM) -> gpd.GeoDataFrame:
    """Portales de OpenStreetMap (con número y código postal 280xx), como puntos en EPSG:25830, con su `cp`."""
    capas = []
    for capa in ("points", "multipolygons"):
        g = gpd.read_file(
            ruta,
            layer=capa,
            columns=["other_tags"],
            where="other_tags LIKE '%addr:postcode%'",
        )
        g["cp"] = g["other_tags"].str.extract(r'"addr:postcode"=>"(280\d\d)"')[0]
        con_numero = g["other_tags"].str.contains('"addr:housenumber"', regex=False)
        g = g[g["cp"].notna() & con_numero].to_crs(paso_secciones.CRS_METRICO)
        capas.append(g.assign(geometry=g.geometry.representative_point()))
    portales = pd.concat(capas, ignore_index=True)[["cp", "geometry"]]
    if portales.empty:
        raise ValueError(f"{ruta.name} no tiene portales con código postal 280xx")
    return portales


def tabla_paso_cp(
    portales: gpd.GeoDataFrame, secciones: gpd.GeoDataFrame
) -> pd.DataFrame:
    """Tabla código postal → distrito de Madrid (`origen, destino, peso, peso_destino, metodo`) contando portales.

    Los portales de un código postal que caen fuera del municipio de Madrid no cuentan: el dato de la AEAT por
    código postal es solo el de Madrid capital. Esa cobertura se registra en el log.
    """
    madrid = secciones[secciones["CUMUN"] == zonas.MADRID]
    dentro = gpd.sjoin(portales, madrid[["CDIS", "geometry"]], predicate="within")
    cobertura = dentro.groupby("cp").size() / portales.groupby("cp").size()
    LOG.info(
        "códigos postales con menos del 99 %% de sus portales en Madrid: %s",
        cobertura[cobertura.fillna(0) < 0.99].round(3).to_dict(),
    )
    pares = (
        dentro.assign(destino=zonas.MADRID + dentro["CDIS"])
        .groupby(["cp", "destino"])
        .size()
        .rename("n")
        .reset_index()
        .rename(columns={"cp": "origen"})
    )
    pares["peso"] = pares["n"] / pares.groupby("origen")["n"].transform("sum")
    pares["peso_destino"] = pares["n"] / pares.groupby("destino")["n"].transform("sum")
    pares["metodo"] = "portales"
    tabla = pares.drop(columns="n")
    paso_secciones.comprobar_tabla(tabla)
    return tabla


def brecha_por_zona(
    zona: pd.DataFrame, brecha: dict, tabla_cp: pd.DataFrame
) -> pd.DataFrame:
    """`zona` con `factor_brecha` y `brecha_ambito` (ficha §6.2, #251): el del municipio en la AEAT; en un distrito,
    el de sus códigos postales (media ponderada por viviendas arrendadas × peso de portales); si no, el de la
    Comunidad de Madrid. Es del año de la AEAT (2024) para todas las filas.
    """
    cp = brecha["cp"]
    distritos = paso_secciones.pasar_intensiva(tabla_cp, cp["factor"], cp["viviendas"])
    pureza = paso_secciones.pureza(tabla_cp, cp["factor"], cp["viviendas"])
    LOG.info(
        "pureza de los distritos (código postal entero): %s", pureza.round(2).to_dict()
    )
    factor = zona["zona_id"].map(distritos)
    mun = zona["zona_id"].map(brecha["municipio"])
    df = zona.copy()
    df["brecha_ambito"] = np.select(
        [factor.notna(), mun.notna()], ["codigo_postal", "municipio"], "comunidad"
    )
    df["factor_brecha"] = factor.fillna(mun).fillna(brecha["provincia"])
    return df


def alquiler_seccion(hojas: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Secciones censales (Censo 2021) de la Comunidad de Madrid, por año."""
    secciones = _largo(hojas["secciones"], "CUSEC", {**TESTIGOS, **EUR_M2, **CUANTIA})
    return _tipado(
        secciones.rename(columns={"CUSEC": "seccion_id"}), "alquiler_seccion"
    )


def main() -> None:
    hojas = leer_serpavi()
    zona = actualizar_ipc(alquiler_zona(hojas), leer_ipc())
    seccion = alquiler_seccion(hojas)
    por_anio = zona.groupby("anio").size()
    if (por_anio != 200).any():
        raise ValueError(f"No hay 200 zonas por año:\n{por_anio}")
    distritos = zona[zona["zona_id"].str.len() == 7].groupby("anio")["testigos"].sum()
    madrid = zona[zona["zona_id"] == "28079"].set_index("anio")["testigos"]
    if not distritos.eq(madrid).all():
        raise ValueError(
            f"Los testigos de los distritos no suman los de 28079:\n{distritos - madrid}"
        )
    PROCESSED.mkdir(parents=True, exist_ok=True)
    zona.to_parquet(PROCESSED / "alquiler_zona.parquet")
    seccion.to_parquet(PROCESSED / "alquiler_seccion.parquet")


if __name__ == "__main__":
    main()
