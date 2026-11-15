"""Renta, desigualdad y hogares del ADRH (INE) por zona y por sección censal, 2015-2024.

Unidades (verificadas en F0-04, `docs/verificaciones/renta-vivienda.md`):
- renta_hogar: renta neta media por hogar, €/año (t=31097).
- renta_uc: media de la renta neta por unidad de consumo, escala OCDE modificada 1/0,5/0,3, €/año (t=31097).
- gini: índice de Gini (0-100) sobre la renta por unidad de consumo de las personas, con colas
  recortadas el 1,5 % por lado (t=37727).
- p80p20: cociente P80/P20 de la renta por unidad de consumo (t=37727).
- poblacion y tam_hogar: personas, y personas por hogar (t=31105).
Gini y P80/P20 solo se publican con 100 residentes o más y admiten nulos. En el CSV, "." es secreto
estadístico (nulo, la fila se conserva) y "" es una sección que no existía ese año (sin fila).
Una fila sección-año puede venir de un solo fichero: hay 6 en 2015-2017 que solo trae el de renta
y salen con todo nulo.
Desde 2020 varios municipios pequeños comparten exactamente el mismo valor (p. ej. 6 con renta_hogar
31.953 € en 2024): el INE parece publicar un valor de grupo; no usarlo como dato propio del
municipio sin comprobarlo.
Fuente: Elaboración propia con datos extraídos del sitio web del INE: www.ine.es
"""

from pathlib import Path

import pandas as pd

from mesobra import contratos

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data/raw"
PROCESSED = RAIZ / "data/processed"
CLAVE = ["unidad_id", "nivel", "anio"]

RENTA = "ine_adrh_renta_madrid_2026-11-15.csv"
FICHEROS = {
    RENTA: {
        "Renta neta media por hogar": "renta_hogar",
        "Media de la renta por unidad de consumo": "renta_uc",
    },
    "ine_adrh_gini_madrid_2026-11-15.csv": {
        "Índice de Gini": "gini",
        "Distribución de la renta P80/P20": "p80p20",
    },
    "ine_adrh_demograficos_madrid_2026-11-15.csv": {
        "Población": "poblacion",
        "Tamaño medio del hogar": "tam_hogar",
    },
}


def _numero(serie: pd.Series) -> pd.Series:
    """Formato español ("3.414.246", "37,5") a número; "." es nulo y un valor ilegible falla."""
    limpio = serie.replace(".", pd.NA).str.replace(".", "", regex=False)
    return pd.to_numeric(limpio.str.replace(",", ".", regex=False), errors="raise")


def _leer(ruta: Path, indicadores: dict[str, str]) -> pd.DataFrame:
    """Tabla ancha por unidad y año con las columnas de `indicadores`."""
    columnas = ["municipio", "distrito", "seccion", "indicador", "anio", "valor"]
    df = pd.read_csv(
        ruta,
        sep=";",
        encoding="utf-8-sig",
        header=0,
        names=columnas,
        dtype=str,
        keep_default_na=False,
    )
    df = df[df["indicador"].isin(indicadores) & (df["valor"] != "")]
    codigos = df[["municipio", "distrito", "seccion"]].apply(
        lambda c: c.str.split(" ").str[0]
    )
    df = df.assign(
        nivel=(codigos["seccion"] == "").map({True: "zona", False: "seccion"}),
        unidad_id=codigos["seccion"]
        .where(codigos["seccion"] != "", codigos["distrito"])
        .where(lambda s: s != "", codigos["municipio"]),
        anio=df["anio"].astype(int),
    )
    # los distritos de otros municipios no son zona
    otros = (df["nivel"] == "zona") & (df["unidad_id"].str.len() == 7)
    df = df[~otros | df["unidad_id"].str.startswith("28079")]
    ancho = df.pivot(index=CLAVE, columns="indicador", values="valor")
    return ancho.rename(columns=indicadores).apply(_numero).reset_index()


def renta(carpeta: Path = RAW) -> pd.DataFrame:
    """Renta, desigualdad y hogares por zona y sección y año (contrato `renta`)."""
    tablas = [_leer(carpeta / f, ind) for f, ind in FICHEROS.items()]
    df = (
        tablas[0]
        .merge(tablas[1], on=CLAVE, how="outer")
        .merge(tablas[2], on=CLAVE, how="outer")
    )
    df = df[list(contratos.CONTRATOS["renta"]["columnas"])].astype(
        contratos.dtypes("renta")
    )
    contratos.validar(df, "renta")
    return df.sort_values(CLAVE).reset_index(drop=True)


def _comparar_catalogo(carpeta: Path) -> None:
    """La renta bruta por persona del INE debe coincidir con «Per cápita» del catálogo regional."""
    ine = _leer(carpeta / RENTA, {"Renta bruta media por persona": "bruta"})
    ine = ine[(ine["nivel"] == "zona") & (ine["unidad_id"].str.len() == 5)]
    cm = pd.read_csv(
        carpeta / "cm_irpf_indicador_renta_2026-11-15.csv",
        sep=";",
        encoding="utf-8-sig",
        dtype=str,
    )
    cm = cm[(cm["Tipo territorio"] == "Municipios") & (cm["Medida"] == "Per cápita")]
    cm = cm[cm["Valor"] != "-"]
    cm = pd.DataFrame(
        {
            "unidad_id": "28" + cm["Código territorio"].str[:3],
            "anio": cm["Año"].astype(int),
            "cm": cm["Valor"].astype(int),
        }
    )
    junto = ine.dropna(subset=["bruta"]).merge(cm, on=["unidad_id", "anio"])
    if len(junto) != len(cm):
        raise ValueError(
            f"Catálogo regional: {len(junto)} de {len(cm)} municipio-año emparejados"
        )
    distintos = junto[junto["bruta"] != junto["cm"]]
    if not distintos.empty:
        raise ValueError(
            f"{len(distintos)} de {len(junto)} rentas distintas del catálogo regional:\n"
            f"{distintos.head()}"
        )


def main() -> None:
    tabla = renta()
    zonas = tabla[tabla["nivel"] == "zona"]
    por_anio = zonas.groupby("anio").size()
    if (por_anio != 200).any():
        raise ValueError(f"No hay 200 zonas por año:\n{por_anio}")
    r23 = zonas[zonas["anio"] == 2023].set_index("unidad_id")["renta_hogar"]
    if not r23["2807905"] > 2 * r23["2807913"]:
        raise ValueError(
            f"Chamartín ({r23['2807905']}) no supera el doble de Puente de Vallecas ({r23['2807913']})"
        )
    _comparar_catalogo(RAW)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    tabla.to_parquet(PROCESSED / "renta.parquet")


if __name__ == "__main__":
    main()
