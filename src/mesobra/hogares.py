"""Cesta básica (alimentación, suministros e internet y móvil) por perfil de hogar, en €/mes, estimada.

Fuente: EPF del INE, gasto medio de los hogares de Madrid, año 2025, medida «Gasto medio unidad
consumo» (€ por unidad de consumo y año), en dos tablas del catálogo de la Comunidad de Madrid:
- 3 dígitos COICOP, `gasto_por_subgrupo_gasto_3_digitos_coicop_epf_base_2006`
  (`cm_epf_gasto_subgrupo`, igual a INE t=73992): 01.1 alimentos 3.115,68; 01.2 bebidas no
  alcohólicas 188,78; 04.5 electricidad, gas y otros combustibles 806,38.
- 4 dígitos, `gasto_por_subgrupo_gasto_4_digitos_coicop_epf_base_2006`
  (`cm_epf_gasto_subgrupo4`): 04.4.1 suministro de agua 166,63; 08.2.1 servicios de telefonía y
  relacionados con Internet 524,62. El 04.4 de 3 dígitos (776,78) lo
  mezcla con gastos comunitarios (600,38), basura (7,06) y saneamiento (2,71).
Fuente de los datos: Comunidad de Madrid (INE, Encuesta de Presupuestos Familiares)
Actualización: IPC de la Comunidad de Madrid por subgrupo (INE t=76137, `ine_ipc_ccaa_subgrupos`) y,
para el agua, IPC nacional por clase (INE t=76127, `ine_ipc_clases_nacional`).

Supuestos y límites:
- Unidades de consumo (UC) de la escala OCDE modificada de la EPF: 1 + 0,5 por cada adulto más
  + 0,3 por cada hijo (menor de 14 años). Alimentación = gasto por UC × UC del perfil.
  `cesta_uc` da el gasto por UC para recalcular la cesta con otro hogar (#180).
- Cada hogar compra su comida, también en piso compartido. Los suministros y las comunicaciones del
  piso se reparten: UC del piso (UC del perfil + 0,5 por cada hogar más) entre `personas_comparten`.
  Supuesto: cada hogar más cuenta como un adulto (0,5 UC); infraestima si el otro hogar es una pareja
  o tiene hijos. Si vives solo y compartes con una pareja, tu parte de suministros y comunicaciones
  sale 96,10 €/mes en vez de 128,13 (estimado, `cesta_uc` de 2025; #323).
  Supuesto para las comunicaciones: en piso compartido cada uno suele tener su móvil; por persona
  serían ≈15 €/mes más en «comparte». El reparto sale de que la EPF nacional (t=75006) da el 89 % del
  gasto en servicios integrados por hogar.
- Comunicaciones = 08.2.1 de 4 dígitos (COICOP 2018/EPF) (telefonía e Internet): sin equipos ni otros servicios (streaming).
- `personas_comparten` cuenta los hogares que pagan el alquiler, el tuyo incluido: la pareja suma sus dos
  sueldos y paga el piso entero (1), y en la monoparental el hijo no paga (1).
- Sin gastos comunitarios, basura ni saneamiento: en alquiler van con la renta y contarlos
  duplicaría el alquiler.
- Es el gasto medio de todos los hogares, no un mínimo: sobreestima en hogares jóvenes con poca renta.
- Euros de 2025 actualizados con el IPC de Madrid por subgrupo (INE t=76137): media de los 12 últimos
  meses entre la media de 2025. La cesta es un gasto anual y la energía oscila: 04.5 vale 1,140 en
  oct-26 y 1,035 en media de 12 meses. El agua va con la clase nacional 04.4.1 (INE t=76127, sin
  dato por comunidad): el 04.4 de Madrid sube un 9 % por la recogida de basuras, que la cesta excluye.
  El 08.3 del IPC incluye «otros servicios», que la partida de telefonía no recoge (< 0,5 €/mes).
- Misma cesta en todas las zonas (la EPF no baja de la Comunidad). Sin renta, tamaño del piso ni
  comidas fuera de casa (motivos en docs/decisiones.md, #178).
- Escenario de renta (#312): `factores_tramo` da, para cada tramo de ingresos netos regulares del
  hogar, la alimentación por UC del tramo entre la media (EPF de España 2025, INE t=73809 y t=73795;
  Madrid no la publica por tramo). Estimado: se aplica a la alimentación de Madrid; la media sigue
  siendo la referencia.
"""

from pathlib import Path

import pandas as pd

from mesobra import contratos
from mesobra.alquiler import _numero

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data/raw"
PROCESSED = RAIZ / "data/processed"

ANIO = 2025
PREFIJO = "Gasto medio por unidad de consumo de los hogares en "
IPC = "ine_ipc_ccaa_subgrupos_2026-11-15.csv"
# El 04.4 de las CCAA mete la basura (+14 % en sep-25), que la cesta excluye: el agua va con la clase nacional.
IPC_NACIONAL = "ine_ipc_clases_nacional_2026-11-19.csv"
# fichero → concepto de la EPF → (cesta, subgrupo del IPC con el que se actualiza)
CONCEPTOS = {
    "cm_epf_gasto_subgrupo_2026-11-15.csv": {
        PREFIJO + "productos alimenticios": ("alimentacion", "01.1 Alimentos"),
        PREFIJO + "bebidas no alcohólicas": (
            "alimentacion",
            "01.2 Bebidas no alcohólicas",
        ),
        PREFIJO + "electricidad, gas y otros combustibles": (
            "suministros",
            "04.5 Electricidad, gas y otros combustibles",
        ),
    },
    "cm_epf_gasto_subgrupo4_2026-11-15.csv": {
        PREFIJO + "suministro de agua": (
            "suministros",
            "04.4.1 Suministro de agua",
        ),
        PREFIJO + "servicios de telefonía y relacionados con Internet": (
            "comunicaciones",
            "08.3 Servicios de información y comunicaciones",
        ),
    },
}
# EPF de España por tramo de ingresos netos regulares del hogar (INE t=73809 y t=73795).
EPF_TRAMOS = "ine_epf_grupos_tramo_ingresos_2026-11-20.csv"
EPF_TRAMOS_UC = "ine_epf_uc_tramo_ingresos_2026-11-20.csv"
# tramo de la EPF → €/mes en que empieza
TRAMOS = {
    "Hasta 499 euros": 0,
    "De 500 a 999 euros": 500,
    "De 1.000 a 1.499 euros": 1000,
    "De 1.500 a 1.999 euros": 1500,
    "De 2.000 a 2.499 euros": 2000,
    "De 2.500 a 2.999 euros": 2500,
    "De 3.000 a 4.999 euros": 3000,
    "5.000 euros o más": 5000,
}
# Perfil → adultos, hijos y personas_comparten.
PERFILES = {
    "solo": (1, 0, 1),
    "comparte": (1, 0, 3),
    "pareja": (2, 0, 1),
    "monoparental": (1, 1, 1),
}
NOTA = (
    "Estimado: gasto medio (no mínimo) de los hogares de Madrid en euros de 2025 "
    "actualizados con el IPC, por unidades de consumo OCDE modificada"
)


def _mes(periodo: str) -> int:
    """Meses desde el año 0 de un periodo `AAAAMmm`."""
    return int(periodo[:4]) * 12 + int(periodo[5:])


def _leer(ruta: Path) -> pd.DataFrame:
    return pd.read_csv(ruta, sep=";", encoding="utf-8-sig", dtype=str)


def factores_ipc(carpeta: Path = RAW) -> pd.Series:
    """Factor por subgrupo: media de los 12 últimos meses ÷ media de 2025; `attrs["ipc_hasta"]` = último mes."""
    subgrupos = [sub for c in CONCEPTOS.values() for _, sub in c.values()]
    columnas = ["subgrupo", "Tipo de dato", "Periodo", "Total"]
    madrid = _leer(carpeta / IPC)
    madrid = madrid[madrid.iloc[:, 0] == "13 Madrid, Comunidad de"].iloc[:, 1:]
    nacional = _leer(carpeta / IPC_NACIONAL).set_axis(columnas, axis=1)
    df = pd.concat(
        [
            madrid.set_axis(columnas, axis=1),
            nacional[nacional["subgrupo"] == "04.4.1 Suministro de agua"],
        ]
    )
    df = df[(df["Tipo de dato"] == "Índice") & df["subgrupo"].isin(subgrupos)]
    df = df.assign(Total=_numero(df["Total"]))
    # los primeros años de alguna serie vienen vacíos; un hueco en los 24 meses que se usan falla abajo
    df = df.dropna(subset="Total")
    if falta := sorted(set(subgrupos) - set(df["subgrupo"])):
        raise ValueError(f"IPC: faltan los subgrupos {falta}")
    if df.duplicated(["subgrupo", "Periodo"]).any():
        raise ValueError("IPC: periodos repetidos")
    ultimo = df["Periodo"].max()
    recientes = range(_mes(ultimo) - 11, _mes(ultimo) + 1)
    factores = {}
    for sub, g in df.groupby("subgrupo"):
        p = g.set_index("Periodo")["Total"]
        base = p[p.index.str[:4] == str(ANIO)]
        ult = p[[_mes(i) in recientes for i in p.index]]
        if len(base) != 12:
            raise ValueError(f"IPC: {sub} no tiene los 12 meses de {ANIO}")
        if len(ult) != 12:
            raise ValueError(
                f"IPC: {sub} no tiene 12 meses consecutivos hasta {ultimo}"
            )
        if abs(base.mean() - 100) > 0.05:
            raise ValueError(
                f"IPC: {sub} media de {ANIO} = {base.mean():.3f}, debería ser 100 (base {ANIO})"
            )
        factores[sub] = ult.mean() / base.mean()
    serie = pd.Series(factores)
    serie.attrs["ipc_hasta"] = f"{ultimo[:4]}-{ultimo[5:]}"
    return serie


def _gasto_uc(carpeta: Path) -> pd.Series:
    """€/UC·año por cesta, de 2025 actualizado con el IPC ("alimentacion", "suministros", "comunicaciones")."""
    factores = factores_ipc(carpeta)
    gasto = {}
    for fichero, conceptos in CONCEPTOS.items():
        df = pd.read_csv(
            carpeta / fichero, sep=";", encoding="utf-8-sig", dtype=str
        ).query(f"Año == '{ANIO}' and Medida == 'Gasto medio unidad consumo'")
        for concepto, (columna, subgrupo) in conceptos.items():
            valor = pd.to_numeric(
                df.loc[df["Concepto"] == concepto, "Valor"], errors="coerce"
            )
            if len(valor) != 1 or valor.isna().any():
                raise ValueError(
                    f"{fichero}: «{concepto}» debe salir una vez con valor numérico "
                    f"en 2025, sale {len(valor)} ({valor.tolist()})"
                )
            gasto[columna] = gasto.get(columna, 0) + valor.iloc[0] * factores[subgrupo]
    serie = pd.Series(gasto)
    serie.attrs["ipc_hasta"] = factores.attrs["ipc_hasta"]
    return serie


def cesta_uc(carpeta: Path = RAW) -> pd.Series:
    """€/mes por unidad de consumo (2025 con IPC): alimentacion, suministros y comunicaciones; la fórmula por hogar está en `hogares`."""
    gasto = _gasto_uc(carpeta)
    serie = gasto / 12
    serie.attrs["ipc_hasta"] = gasto.attrs["ipc_hasta"]
    return serie


def hogares(carpeta: Path = RAW) -> pd.DataFrame:
    """Alimentación, suministros y comunicaciones €/mes por perfil de hogar (contrato `hogares`)."""
    gasto = cesta_uc(carpeta)
    df = pd.DataFrame(
        PERFILES, index=["adultos", "hijos", "personas_comparten"]
    ).T.rename_axis("perfil")
    df = df.reset_index()
    uc = 1 + 0.5 * (df["adultos"] - 1) + 0.3 * df["hijos"]
    uc_piso = uc + 0.5 * (df["personas_comparten"] - 1)
    df["alimentacion"] = gasto["alimentacion"] * uc
    df["suministros"] = gasto["suministros"] * uc_piso / df["personas_comparten"]
    df["comunicaciones"] = gasto["comunicaciones"] * uc_piso / df["personas_comparten"]
    df["anio"] = ANIO
    df = df.astype(contratos.dtypes("hogares"))
    contratos.validar(df, "hogares")
    df.attrs["nota"] = NOTA
    df.attrs["ipc_hasta"] = gasto.attrs["ipc_hasta"]
    return df


def factores_tramo(carpeta: Path = RAW) -> pd.Series:
    """Alimentación por UC de cada tramo de ingresos ÷ la de todos los hogares, España, EPF 2025 (estimado).

    Índice: euros/mes de ingresos netos regulares del hogar donde empieza el tramo. UC por hogar =
    gasto total por hogar ÷ gasto total por UC (t=73795), porque t=73809 no da la alimentación por UC.
    """
    nivel = "Nivel de ingresos mensuales netos regulares del hogar"
    g = _leer(carpeta / EPF_TRAMOS).set_axis(
        [nivel, "medida", "grupo", "anio", "v"], axis=1
    )
    g = g[(g["medida"] == "Gasto medio por hogar") & g["grupo"].str.startswith("01 ")]
    u = _leer(carpeta / EPF_TRAMOS_UC).set_axis(
        [nivel, "tipo", "medida", "anio", "v"], axis=1
    )
    u = u[u["tipo"] == "Dato base"]
    series = [
        df[(df["anio"] == str(ANIO)) & (df["medida"] == medida)].set_index(nivel)["v"]
        for df, medida in [
            (g, "Gasto medio por hogar"),
            (u, "Gasto medio por hogar"),
            (u, "Gasto medio por unidad de consumo"),
        ]
    ]
    for s in series:
        if falta := [t for t in ["Total", *TRAMOS] if t not in s.index]:
            raise ValueError(f"EPF por tramo de ingresos {ANIO}: faltan {falta}")
        if s.index.duplicated().any():
            raise ValueError(f"EPF por tramo de ingresos {ANIO}: tramos repetidos")
    alim, gasto_hogar, gasto_uc = (_numero(s) for s in series)
    por_uc = alim / (gasto_hogar / gasto_uc)
    # `_numero` deja en nulo una celda vacía: un tramo sin dato no puede dar un factor
    if vacios := por_uc.index[por_uc.isna()].tolist():
        raise ValueError(f"EPF por tramo de ingresos {ANIO}: sin valor en {vacios}")
    return pd.Series(
        (por_uc[list(TRAMOS)] / por_uc["Total"]).to_numpy(),
        index=pd.Index(TRAMOS.values(), name="desde"),
    )


def main() -> None:
    tabla = hogares()
    PROCESSED.mkdir(parents=True, exist_ok=True)
    tabla.to_parquet(PROCESSED / "hogares.parquet")


if __name__ == "__main__":
    main()
