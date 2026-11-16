"""Alquiler por zona y por sección censal desde el Excel del SERPAVI (MIVAU), vivienda colectiva.

Lee el Excel una vez, se queda con la Comunidad de Madrid y guarda un intermedio por hoja en
`data/processed/`. Produce `alquiler_zona` y `alquiler_seccion` (contratos en `contratos.py`).
Las celdas que el SERPAVI no publica (pocos testigos) quedan nulas, nunca en cero.
"""

from pathlib import Path

import pandas as pd

from mesobra import contratos

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data/raw/serpavi_bd_2011_2024_2026-11-15.xlsx"
PROCESSED = RAIZ / "data/processed"

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


def alquiler_seccion(hojas: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Secciones censales (Censo 2021) de la Comunidad de Madrid, por año."""
    secciones = _largo(hojas["secciones"], "CUSEC", {**TESTIGOS, **EUR_M2, **CUANTIA})
    return _tipado(
        secciones.rename(columns={"CUSEC": "seccion_id"}), "alquiler_seccion"
    )


def main() -> None:
    hojas = leer_serpavi()
    zona, seccion = alquiler_zona(hojas), alquiler_seccion(hojas)
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
