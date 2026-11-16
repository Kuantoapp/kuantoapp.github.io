"""Esfuerzo de alquiler por zona y año: alquiler mediano mensual sobre la renta del hogar.

Fórmula: esfuerzo = alquiler mediano mensual ÷ (renta neta media por hogar ÷ 12), por zona
(178 municipios, 21 distritos de Madrid y la fila de Madrid entero, 28079) y año, en la ventana
común de las dos series (SERPAVI 2011-2024, ADRH 2015-2024 → 2015-2024).
Fuentes: SERPAVI (MIVAU), vivienda colectiva; ADRH (INE).

Es un índice territorial para comparar zonas y años, no la parte del sueldo de nadie: el cálculo
por persona va en la herramienta (pipeline_euros).

Limitaciones:
- Ficha §7.1: la renta media incluye a los propietarios, que suelen ganar más que los inquilinos,
  así que el indicador subestima el esfuerzo de quien alquila. Además es una media (los ingresos
  altos la suben) y el SERPAVI recoge contratos declarados, no precios de oferta (va por detrás
  del mercado).
- Numerador: alquiler_zona no trae la cuantía mensual, así que se usa €/m² mediano × superficie
  mediana. Ese producto de medianas no es la mediana del alquiler: en 2024, en los 137 municipios
  con los dos datos, producto ÷ cuantía mediana da mediana 1,061, P10 0,984 y P90 1,173 (Madrid
  capital 1,061); el esfuerzo sale en torno a un 6 % más alto, hasta un 17 % en algunas zonas
  (#151).
- Desde los datos de 2020, las zonas de menos de 100 residentes tienen en el ADRH la renta común
  de su comarca agraria, no la suya (#166): su esfuerzo queda nulo; renta_hogar_mes conserva el
  valor publicado.
- Zonas sin dato de alquiler: esfuerzo nulo. factor_ipc no se aplica (euros de cada año).
"""

from pathlib import Path

import pandas as pd

from mesobra import contratos

RAIZ = Path(__file__).resolve().parents[2]
PROCESSED = RAIZ / "data/processed"
CLAVE = ["zona_id", "anio"]
MIN_RESIDENTES = 100
ANIO_RENTA_COMUN = 2020


def esfuerzo(alquiler: pd.DataFrame, renta: pd.DataFrame) -> pd.DataFrame:
    """Esfuerzo por zona y año en la ventana común (contrato `esfuerzo`)."""
    zonas = renta[renta["nivel"] == "zona"].rename(columns={"unidad_id": "zona_id"})
    # el inner deja la ventana común de las dos series
    df = alquiler.merge(zonas, on=CLAVE, how="inner", validate="one_to_one")
    df["alquiler_mes_p50"] = df["eur_m2_p50"] * df["m2_p50"]
    df["renta_hogar_mes"] = df["renta_hogar"] / 12
    # población nula no es valor de grupo: conserva su esfuerzo
    pequena = df["poblacion"].fillna(MIN_RESIDENTES) < MIN_RESIDENTES
    renta_comun = pequena & (df["anio"] >= ANIO_RENTA_COMUN)
    df["esfuerzo"] = (df["alquiler_mes_p50"] / df["renta_hogar_mes"]).mask(renta_comun)
    columnas = list(contratos.CONTRATOS["esfuerzo"]["columnas"])
    df = df[columnas].astype(contratos.dtypes("esfuerzo"))
    contratos.validar(df, "esfuerzo")
    return df.sort_values(CLAVE).reset_index(drop=True)


def cambio(tabla: pd.DataFrame) -> pd.Series:
    """Cambio del esfuerzo por zona entre el primer y el último año de `tabla` (último − primero).

    Es nulo si la zona no tiene esfuerzo en alguno de los dos años.
    """
    ancho = tabla.pivot(index="zona_id", columns="anio", values="esfuerzo")
    if len(ancho.columns) < 2:
        raise ValueError(f"cambio necesita al menos dos años, hay {len(ancho.columns)}")
    return (ancho[ancho.columns.max()] - ancho[ancho.columns.min()]).rename("cambio")


def main() -> None:
    tabla = esfuerzo(
        pd.read_parquet(PROCESSED / "alquiler_zona.parquet"),
        pd.read_parquet(PROCESSED / "renta.parquet"),
    )
    por_anio = tabla.groupby("anio").size()
    if (por_anio != 200).any():
        raise ValueError(f"No hay 200 zonas por año:\n{por_anio}")
    tabla.to_parquet(PROCESSED / "esfuerzo.parquet")


if __name__ == "__main__":
    main()
