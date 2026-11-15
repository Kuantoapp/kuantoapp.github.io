"""Cesta básica (alimentación y suministros) por perfil de hogar, en €/mes de 2025, estimada.

Fuente: EPF del INE, gasto medio de los hogares de Madrid, año 2025, medida «Gasto medio unidad
consumo» (€ por unidad de consumo y año), en dos tablas del catálogo de la Comunidad de Madrid:
- 3 dígitos COICOP, `gasto-medio-de-los-hogares-por-subgrupo-de-gasto-3-digitos-coicopepf-base-2006`
  (`cm_epf_gasto_subgrupo`, igual a INE t=73992): 01.1 alimentos 3.115,68; 01.2 bebidas no
  alcohólicas 188,78; 04.5 electricidad, gas y otros combustibles 806,38.
- 4 dígitos, `gasto-medio-de-los-hogares-por-subgrupo-de-gasto-4-digitos-coicopepf-base-2006`
  (`cm_epf_gasto_subgrupo4`): 04.4.1 suministro de agua 166,63. El 04.4 de 3 dígitos (776,78) lo
  mezcla con gastos comunitarios (600,38), basura (7,06) y saneamiento (2,71).
Fuente de los datos: Comunidad de Madrid (INE, Encuesta de Presupuestos Familiares)

Supuestos y límites:
- Unidades de consumo (UC) de la escala OCDE modificada de la EPF: 1 + 0,5 por cada adulto más
  + 0,3 por cada hijo (menor de 14 años). Alimentación = gasto por UC × UC del perfil.
- Cada persona compra su comida, también en piso compartido. Los suministros del piso se reparten:
  UC del piso (UC del perfil + 0,5 por cada persona más) entre `personas_comparten`.
- `personas_comparten` cuenta las unidades que pagan el alquiler: la pareja suma sus dos
  sueldos y paga el piso entero (1), y en la monoparental el hijo no paga (1).
- Sin gastos comunitarios, basura ni saneamiento: en alquiler van con la renta y contarlos
  duplicaría el alquiler.
- Es el gasto medio de todos los hogares, no un mínimo: sobreestima en hogares jóvenes con poca renta.
- Euros de 2025, sin actualizar con el IPC de 2026. Misma cesta en todas las zonas (la EPF no baja
  de la Comunidad). Sin comidas fuera de casa.
"""

from pathlib import Path

import pandas as pd

from mesobra import contratos

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data/raw"
PROCESSED = RAIZ / "data/processed"

PREFIJO = "Gasto medio por unidad de consumo de los hogares en "
CONCEPTOS = {
    "cm_epf_gasto_subgrupo_2026-11-15.csv": {
        PREFIJO + "productos alimenticios": "alimentacion",
        PREFIJO + "bebidas no alcohólicas": "alimentacion",
        PREFIJO + "electricidad, gas y otros combustibles": "suministros",
    },
    "cm_epf_gasto_subgrupo4_2026-11-15.csv": {
        PREFIJO + "suministro de agua": "suministros",
    },
}
# Perfil → adultos, hijos y personas_comparten.
PERFILES = {
    "solo": (1, 0, 1),
    "comparte": (1, 0, 3),
    "pareja": (2, 0, 1),
    "monoparental": (1, 1, 1),
}
NOTA = (
    "Estimado: gasto medio (no mínimo) de los hogares de Madrid en euros de 2025, "
    "por unidades de consumo OCDE modificada"
)


def _gasto_uc(carpeta: Path) -> pd.Series:
    """€/UC·año de 2025 por cesta ("alimentacion", "suministros")."""
    gasto = {}
    for fichero, conceptos in CONCEPTOS.items():
        df = pd.read_csv(
            carpeta / fichero, sep=";", encoding="utf-8-sig", dtype=str
        ).query("Año == '2025' and Medida == 'Gasto medio unidad consumo'")
        for concepto, columna in conceptos.items():
            valor = pd.to_numeric(
                df.loc[df["Concepto"] == concepto, "Valor"], errors="coerce"
            )
            if len(valor) != 1 or valor.isna().any():
                raise ValueError(
                    f"{fichero}: «{concepto}» debe salir una vez con valor numérico "
                    f"en 2025, sale {len(valor)} ({valor.tolist()})"
                )
            gasto[columna] = gasto.get(columna, 0) + valor.iloc[0]
    return pd.Series(gasto)


def hogares(carpeta: Path = RAW) -> pd.DataFrame:
    """Alimentación y suministros €/mes por perfil de hogar (contrato `hogares`)."""
    gasto = _gasto_uc(carpeta)
    df = pd.DataFrame(
        PERFILES, index=["adultos", "hijos", "personas_comparten"]
    ).T.rename_axis("perfil")
    df = df.reset_index()
    uc = 1 + 0.5 * (df["adultos"] - 1) + 0.3 * df["hijos"]
    uc_piso = uc + 0.5 * (df["personas_comparten"] - 1)
    df["alimentacion"] = gasto["alimentacion"] * uc / 12
    df["suministros"] = gasto["suministros"] * uc_piso / df["personas_comparten"] / 12
    df["anio"] = 2025
    df = df.astype(contratos.dtypes("hogares"))
    contratos.validar(df, "hogares")
    df.attrs["nota"] = NOTA
    return df


def main() -> None:
    tabla = hogares()
    PROCESSED.mkdir(parents=True, exist_ok=True)
    tabla.to_parquet(PROCESSED / "hogares.parquet")


if __name__ == "__main__":
    main()
