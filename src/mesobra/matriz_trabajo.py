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
AFILIACION = (
    calculo.RAIZ / "data/raw/cm_afiliados_centro_trabajo_regimen_2026-11-24.csv"
)
AFILIACION_CUENTA = (
    calculo.RAIZ / "data/raw/cm_afiliados_cuenta_cotizacion_municipio_2026-11-24.csv"
)
EDM_INDIVIDUOS = calculo.RAIZ / "data/raw/crtm_edm2018_individuos_2026-11-24.xlsx"
EDM_HOGARES = calculo.RAIZ / "data/raw/crtm_edm2018_hogares_2026-11-24.xlsx"
DISTRITOS_MADRID = 21
# errata del fichero de cuentas de cotización (leído el 2026-11-24) frente al nombre oficial, ya pasada por `_clave`
ERRATAS_CUENTA = {"readuena": "reduena"}
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


def _hoja(ruta: Path = RAW) -> pd.DataFrame:
    return pd.read_excel(ruta, HOJA, header=1, engine="calamine", dtype=str)


def leer_matriz(ruta: Path = RAW) -> pd.DataFrame:
    """Matriz de la Comunidad de `ruta`, validada: un origen por municipio de la Comunidad."""
    df = ordenar(_hoja(ruta))
    if (n := df["origen"].nunique()) != MUNICIPIOS:
        raise ValueError(
            f"la matriz trae {n} municipios de residencia de la Comunidad, no {MUNICIPIOS}"
        )
    return df


def _clave(nombre: str) -> str:
    """Nombre sin tildes, en minúsculas y sin guiones: «Fuencarral - El Pardo» = «Fuencarral-El Pardo»."""
    sin = unicodedata.normalize("NFD", nombre.lower().replace("-", " "))
    return " ".join("".join(c for c in sin if not unicodedata.combining(c)).split())


def leer_cuotas_distritos(
    ruta: Path = DISTRITOS, zonas: Path = ZONAS, año: int = 2023
) -> pd.Series:
    """Cuota de los ocupados de `año` (2023 en los pesos) de cada distrito de Madrid (`zona_id` 2807901…) en el
    Colectivo Empresarial (Total, sin «no consta distrito»). Falla si no salen los 21 distritos de `zonas`."""
    props = [f["properties"] for f in json.loads(zonas.read_text("utf-8"))["features"]]
    # shortcut: une por nombre porque el CSV no trae código de distrito; si lo trae, unir por código
    ids = {
        _clave(p["nombre"]): p["zona_id"]
        for p in props
        if p["municipio_id"] == MUNICIPIO_MADRID and p["tipo"] == "distrito"
    }
    df = pd.read_csv(ruta, sep=";", encoding="utf-8-sig", dtype=str)
    df = df[
        (df["Medida"] == "Ocupados")
        & (df["Estrato Empleo"] == "Total")
        & (df["Año"] == str(año))
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


def _dentro(m: pd.DataFrame) -> pd.DataFrame:
    """Filas con destino en la Comunidad y municipio conocido: la base común de `pesos` y `ocupados_observados`."""
    return m[(m["prov_destino"] == MADRID) & m["destino"].notna()]


def ocupados_observados(m: pd.DataFrame) -> pd.Series:
    """Por origen, ocupados que trabajan en la Comunidad con municipio conocido: la base de los pesos (0 si no hay)."""
    observados = _dentro(m).groupby("origen")["ocupados"].sum()
    return observados.reindex(m["origen"].unique(), fill_value=0)


def pesos(m: pd.DataFrame, cuotas: pd.Series) -> tuple[pd.DataFrame, pd.Series]:
    """(w, excluida): `w` con columnas `origen`, `destino` (código de municipio, o `zona_id` de distrito si es Madrid)
    y `w` = ocupados ÷ total de los que trabajan en la Comunidad con municipio conocido, que suma 1 por origen;
    `excluida`, por origen, la fracción de sus ocupados que queda fuera (otras provincias o «No consta»).
    Las celdas suprimidas no se imputan: no se distinguen de los ceros."""
    dentro = _dentro(m).groupby(["origen", "destino"], as_index=False)["ocupados"].sum()
    por_origen = ocupados_observados(m)
    excluida = 1 - por_origen / m.groupby("origen")["ocupados"].sum()
    dentro["w"] = dentro["ocupados"] / dentro["origen"].map(por_origen)
    madrid = dentro["destino"] == MUNICIPIO_MADRID
    reparto = dentro[madrid].merge(
        cuotas.rename("cuota").rename_axis("zona").reset_index(), how="cross"
    )
    reparto = reparto.assign(destino=reparto["zona"], w=reparto["w"] * reparto["cuota"])
    w = pd.concat([dentro[~madrid], reparto], ignore_index=True)
    return w[["origen", "destino", "w"]], excluida.rename("excluida")


def entradas(hoja: pd.DataFrame) -> pd.Series:
    """Ocupados que trabajan en cada municipio de la Comunidad (código de 5 cifras) desde todos los orígenes, también
    de otras provincias, sin «No consta»: lo comparable con la afiliación por centro de trabajo (#357)."""
    m = hoja[
        (hoja["Provincia de trabajo"] == MADRID)
        & hoja["Municipio de trabajo"].str.fullmatch(r"\d{3}", na=False)
    ]
    ocupados = pd.to_numeric(m["Ocupados de 16 y más años"], errors="raise")
    return ocupados.groupby(MADRID + m["Municipio de trabajo"]).sum().rename("ocupados")


def leer_afiliacion_centro(ruta: Path = AFILIACION, año: int = 2022) -> pd.Series:
    """Afiliados en alta a 31-12-`año` por municipio del centro de trabajo (código de 5 cifras), suma de los
    regímenes, sin «Sin municipio asignado» (9999). Falla si no salen los 179 municipios o si los municipios no
    cuadran con la fila de la Comunidad más allá del redondeo a 5 de cada celda (desde 2021)."""
    df = pd.read_csv(ruta, sep=";", encoding="utf-8-sig", dtype=str)
    df = df[df["Año"] == str(año)]
    valor = pd.to_numeric(df["Valor"], errors="raise")
    mun = df["Tipo territorio"] == "Municipios"
    por_codigo = valor[mun].groupby(df.loc[mun, "Código territorio"]).sum()
    total = valor[df["Tipo territorio"] == "Comunidad de Madrid"].sum()
    if abs(por_codigo.sum() - total) > 2.5 * mun.sum():
        raise ValueError(
            f"la afiliación de los municipios ({por_codigo.sum()}) no cuadra con la Comunidad ({total})"
        )
    afil = por_codigo.drop("9999")
    afil.index = (
        MADRID + afil.index.str[:3]
    )  # 4 cifras: municipio del INE + dígito de control
    if len(afil) != MUNICIPIOS or afil.index.duplicated().any():
        raise ValueError(f"la afiliación trae {len(afil)} municipios, no {MUNICIPIOS}")
    return afil.rename("afiliados")


def leer_afiliacion_cuenta(
    ruta: Path = AFILIACION_CUENTA, centro: Path = AFILIACION, año: int = 2022
) -> pd.Series:
    """Afiliados en alta a 31-12-`año` por municipio de la **cuenta de cotización** (código de 5 cifras), sin «No
    distribuidos». El fichero no trae código: se une por el nombre, con los códigos de la afiliación por centro de
    trabajo (`centro`, mismo publicador y misma forma de los nombres). Falla si un nombre no casa o no salen 179."""
    c = pd.read_csv(centro, sep=";", encoding="utf-8-sig", dtype=str)
    c = c[(c["Tipo territorio"] == "Municipios") & (c["Código territorio"] != "9999")]
    codigos = dict(
        zip(c["Territorio"].map(_clave), MADRID + c["Código territorio"].str[:3])
    )
    df = pd.read_csv(ruta, sep=";", encoding="utf-8-sig", dtype=str)
    df = df[
        (df["Año"] == str(año))
        & (df["Periodo"] == "M12")
        & (df["Territorio"] != "No distribuidos")
    ]
    claves = df["Territorio"].map(_clave).replace(ERRATAS_CUENTA)
    if faltan := sorted(set(claves) - set(codigos)):
        raise ValueError(f"municipios de la cuenta de cotización sin código: {faltan}")
    afil = pd.to_numeric(df["Valor"], errors="raise").set_axis(claves.map(codigos))
    if len(afil) != MUNICIPIOS or afil.index.duplicated().any():
        raise ValueError(
            f"la cuenta de cotización trae {len(afil)} municipios, no {MUNICIPIOS}"
        )
    return afil.rename("afiliados")


def leer_edm_trabajo(
    individuos: Path = EDM_INDIVIDUOS, hogares: Path = EDM_HOGARES
) -> pd.DataFrame:
    """Personas del EDM2018 (CRTM) que trabajan (`C8ACTIV` 1 o 2) con centro de trabajo (`C11ZT1259`) en Madrid:
    `hogar`, `residencia` (zona ZT1259 del hogar), `municipio` (de residencia, 5 cifras), `distrito` de trabajo
    (`zona_id` 28079DD, del código de zona `079-DD-…`), `peso` («Elevador de individuos»), `cuenta_propia` (`C9PROF`
    3 o 4) y `en_casa` (centro de trabajo en la zona del hogar). Falla si una zona de Madrid no trae distrito, falta
    alguno de los 21 o una persona no tiene hogar."""
    ind = pd.read_excel(individuos, "INDIVIDUOS", engine="calamine", dtype=str)
    hog = pd.read_excel(hogares, "HOGARES", engine="calamine", dtype=str)
    ind = ind[ind["C8ACTIV"].isin(["1", "2"])]
    ind = ind[ind["C11ZT1259"].str.startswith("079", na=False)]
    dd = ind["C11ZT1259"].str.extract(r"^079-(\d{2})-")[0]
    if dd.isna().any():
        raise ValueError(
            "zonas de trabajo de Madrid del EDM2018 sin distrito en el código"
        )
    df = ind.merge(hog[["ID_HOGAR", "CODMUNI", "ZT1259"]], on="ID_HOGAR", how="left")
    if df["ZT1259"].isna().any():
        raise ValueError("personas del EDM2018 sin hogar en la tabla HOGARES")
    out = pd.DataFrame(
        {
            "hogar": df["ID_HOGAR"],
            "residencia": df["ZT1259"],
            "municipio": MADRID + df["CODMUNI"],
            "distrito": MUNICIPIO_MADRID + dd.to_numpy(),
            "peso": pd.to_numeric(df["ELE_G_POND"], errors="raise"),
            "cuenta_propia": df["C9PROF"].isin(["3", "4"]),
            "en_casa": df["C11ZT1259"] == df["ZT1259"],
        }
    )
    if (n := out["distrito"].nunique()) != DISTRITOS_MADRID:
        raise ValueError(
            f"el EDM2018 trae {n} distritos de trabajo, no {DISTRITOS_MADRID}"
        )
    return out


def cuotas_edm(edm: pd.DataFrame) -> pd.Series:
    """Cuota de cada distrito en las personas ponderadas de `edm`."""
    por_distrito = edm.groupby("distrito")["peso"].sum()
    return por_distrito / por_distrito.sum()


def disimilitud(a: pd.Series, b: pd.Series) -> float:
    """Índice de disimilitud ½ Σ |a − b| entre dos repartos que suman 1: la parte que habría que mover."""
    if set(a.index) != set(b.index):
        raise ValueError("los dos repartos no tienen las mismas unidades")
    return float((a - b).abs().sum() / 2)


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
