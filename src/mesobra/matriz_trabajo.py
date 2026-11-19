"""Dónde trabajan los residentes de cada municipio de la Comunidad de Madrid (#301).

Fuente: INE, Censo anual de población (ocupación y actividad) 2021-2023, «Matriz de municipio de residencia por
municipio de trabajo» (`matriz_ocu_anonim.xlsb`, publicada el 02-12-2025, CC BY 4.0). Elaboración propia con datos
extraídos del sitio web del INE: www.ine.es. Se usa la hoja `C23` (ocupados de 2023), la más reciente.

Formato: una hoja por año (`C21`, `C22`, `C23`), en largo. La fila 0 agrupa «Lugar de residencia» y «Lugar de
trabajo»; la 1 trae las columnas de `COLUMNAS`; después, una fila por par (residencia, trabajo) con los «Ocupados de
16 y más años». El mínimo publicado es 5: probable supresión de las celdas menores (el fichero se llama «anonim»;
el INE no lo dice en lo leído), así que un par que falta no es un cero. «No consta» como municipio, o como provincia,
de trabajo es lugar desconocido, no un destino.

En la Comunidad de Madrid, 2023, leído del fichero original el 19-11-2026: 179 municipios de residencia, 3.067.380
ocupados, el 94,19 % trabaja en la provincia y el 9,47 % tiene municipio de trabajo «No consta». El INE obtiene los
ocupados sobre todo de la afiliación a la Seguridad Social (el 94,2 % de los del censo, metodología del Censo anual,
abril de 2026): el lugar de trabajo puede ser la sede de la empresa y no el centro real (sin comprobar).
"""

import json
import logging
import unicodedata
from pathlib import Path

import pandas as pd

from mesobra import calculo

LOG = logging.getLogger(__name__)
RAW = (
    calculo.RAIZ / "data/raw/ine_censo_anual_matriz_residencia_trabajo_2026-11-19.xlsb"
)
PROCESSED = calculo.RAIZ / "data/processed/matriz_trabajo_2023.csv"
DISTRITOS = calculo.RAIZ / "data/raw/cm_colectivo_empresarial_distrito_2026-11-19.csv"
ZONAS = calculo.RAIZ / "app/datos/zonas.geojson"
MUNICIPIO_MADRID = "28079"
HOJA = "C23"
MADRID = "28"
MUNICIPIOS = 179  # municipios de la Comunidad de Madrid
COLUMNAS = [
    "Provincia de residencia",
    "Nombre",
    "Municipio de residencia",
    "Nombre.1",
    "Provincia de trabajo",
    "Nombre.2",
    "Municipio de trabajo",
    "Nombre.3",
    "Ocupados de 16 y más años",
]


def ordenar(hoja: pd.DataFrame) -> pd.DataFrame:
    """Pares con origen en la Comunidad: `origen` y `destino` (código INE de 5 cifras, nulo si no consta),
    `prov_destino` (2 cifras, nula si no consta) y `ocupados`. Falla si cambia el formato."""
    if faltan := [c for c in COLUMNAS if c not in hoja.columns]:
        raise ValueError(f"la matriz del INE no trae las columnas {faltan}")
    m = hoja[hoja["Provincia de residencia"] == MADRID]
    ocupados = pd.to_numeric(m["Ocupados de 16 y más años"], errors="coerce")
    if ocupados.isna().any() or (ocupados < 0).any() or (ocupados % 1 != 0).any():
        raise ValueError(
            "ocupados no enteros, no numéricos o negativos en la matriz del INE"
        )
    prov = m["Provincia de trabajo"].where(
        m["Provincia de trabajo"].str.fullmatch(r"\d{2}", na=False)
    )
    mun = m["Municipio de trabajo"].where(
        m["Municipio de trabajo"].str.fullmatch(r"\d{3}", na=False)
    )
    return pd.DataFrame(
        {
            "origen": m["Provincia de residencia"] + m["Municipio de residencia"],
            "prov_destino": prov,
            "destino": prov + mun,  # nulo si no consta la provincia o el municipio
            "ocupados": ocupados.astype(int),
        }
    ).reset_index(drop=True)


def leer_matriz(ruta: Path = RAW) -> pd.DataFrame:
    """Matriz de la Comunidad de `ruta`, validada: un origen por municipio de la Comunidad."""
    df = ordenar(pd.read_excel(ruta, HOJA, header=1, engine="calamine", dtype=str))
    if (n := df["origen"].nunique()) != MUNICIPIOS:
        raise ValueError(
            f"la matriz trae {n} municipios de residencia de la Comunidad, no {MUNICIPIOS}"
        )
    return df


def _clave(nombre: str) -> str:
    """Nombre sin tildes, en minúsculas y sin guiones: «Fuencarral - El Pardo» = «Fuencarral-El Pardo»."""
    sin = unicodedata.normalize("NFD", nombre.lower().replace("-", " "))
    return " ".join("".join(c for c in sin if not unicodedata.combining(c)).split())


def leer_cuotas_distritos(ruta: Path = DISTRITOS, zonas: Path = ZONAS) -> pd.Series:
    """Cuota de los ocupados de 2023 de cada distrito de Madrid (`zona_id` 2807901…) en el Colectivo Empresarial
    (Total, sin «no consta distrito»). Falla si no salen los 21 distritos de `zonas`."""
    props = [f["properties"] for f in json.loads(zonas.read_text("utf-8"))["features"]]
    ids = {
        _clave(p["nombre"]): p["zona_id"]
        for p in props
        if p["municipio_id"] == MUNICIPIO_MADRID and p["tipo"] == "distrito"
    }
    df = pd.read_csv(ruta, sep=";", encoding="utf-8-sig", dtype=str)
    df = df[
        (df["Medida"] == "Ocupados")
        & (df["Estrato Empleo"] == "Total")
        & (df["Año"] == "2023")
    ]
    nombre = df["Concepto"].str.extract(
        r"en el distrito de (.+) del municipio de Madrid$"
    )[0]
    if nombre.isna().any():
        raise ValueError(
            "el Colectivo Empresarial trae conceptos sin distrito de Madrid"
        )
    ocupados = pd.to_numeric(df["Valor"].set_axis(nombre.map(_clave)), errors="raise")
    ocupados = ocupados.drop(_clave("las que no consta distrito"), errors="ignore")
    if sorted(ocupados.index) != sorted(ids) or ocupados.index.duplicated().any():
        raise ValueError(
            f"no salen los {len(ids)} distritos de Madrid: {sorted(ocupados.index)}"
        )
    cuotas = ocupados.rename(index=ids)
    return (cuotas / cuotas.sum()).sort_index()


def pesos(m: pd.DataFrame, cuotas: pd.Series) -> tuple[pd.DataFrame, pd.Series]:
    """(w, excluida): `w` con columnas `origen`, `destino` (código de municipio, o `zona_id` de distrito si es Madrid)
    y `w` = ocupados ÷ total de los que trabajan en la Comunidad con municipio conocido, que suma 1 por origen;
    `excluida`, por origen, la fracción de sus ocupados que queda fuera (otras provincias o «No consta»).
    Las celdas suprimidas no se imputan: no se distinguen de los ceros."""
    dentro = m[(m["prov_destino"] == MADRID) & m["destino"].notna()]
    dentro = dentro.groupby(["origen", "destino"], as_index=False)["ocupados"].sum()
    por_origen = dentro.groupby("origen")["ocupados"].sum()
    excluida = (
        1
        - por_origen.reindex(m["origen"].unique(), fill_value=0)
        / m.groupby("origen")["ocupados"].sum()
    )
    dentro["w"] = dentro["ocupados"] / dentro["origen"].map(por_origen)
    madrid = dentro["destino"] == MUNICIPIO_MADRID
    reparto = dentro[madrid].merge(
        cuotas.rename("cuota").rename_axis("zona").reset_index(), how="cross"
    )
    reparto = reparto.assign(destino=reparto["zona"], w=reparto["w"] * reparto["cuota"])
    w = pd.concat([dentro[~madrid], reparto], ignore_index=True)
    return w[["origen", "destino", "w"]], excluida.rename("excluida")


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    df = leer_matriz()
    total = df["ocupados"].sum()
    LOG.info(
        "ocupados %d; trabajan en la provincia %.1f %%; municipio de trabajo no consta %.2f %%",
        total,
        100 * df.loc[df["prov_destino"] == MADRID, "ocupados"].sum() / total,
        100 * df.loc[df["destino"].isna(), "ocupados"].sum() / total,
    )
    PROCESSED.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED, index=False)
    LOG.info("%s: %d pares", PROCESSED, len(df))


if __name__ == "__main__":
    main()
