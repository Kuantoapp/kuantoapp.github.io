"""Tasa de sobrecarga del gasto en vivienda con los microdatos de la ECV 2025 del INE.

Fichero de uso público, renta de 2024. Fuente: INE, www.ine.es; cálculos propios.
Fórmula de Eurostat (ilc_lvho07c, ilc_lvho07_r): `(HH070·12 − HY070N) / (HY020 − HY070N) > 0,40`.
Eurostat la escribe con HY070G; en la ECV 2025 HY070G = HY070N en los 29.369 hogares.
- HH070 son gastos de vivienda MENSUALES: se multiplican por 12.
- El «reducido» de Eurostat es HH021 4 o 5 (alquiler inferior al de mercado o cesión gratuita).
- Denominador ≤ 0 cuenta como sobrecargado, también en la cifra de control: por eso sale 36,0 % y
  no el 35,9 % de #190, que dejaba fuera un hogar con HY020 = −2.501 €.
- Los blancos son «no aplicable»: se excluyen (resultado NaN).
- El fichero público no trae DB050 ni DB060: el error estándar va por linealización con el hogar
  como unidad, y el intervalo usa un efecto de diseño 2 (supuesto).

Cifra de control de F3-06 (#100): hogares inquilinos (HH021 3 o 4) de Madrid (ES30), ponderados con
DB090, con gasto HH070·12/HY020 > 0,40 (sin descontar ayudas, definición de
docs/verificaciones/renta-vivienda.md) y alquiler HH060·12/HY020 > 0,30. Es ESTIMADO.
"""

from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data/raw/ine_ecv_microdatos_2025_2026-11-18"
MADRID = "ES30"
INQUILINOS = (3, 4)
# shortcut: sin estrato ni sección (DB050, DB060) en el fichero público, efecto de diseño supuesto; mejorar si el INE los publica
EFECTO_DISENO = 2
Z95 = 1.96


def _leer(ruta: Path, columnas: list[str]) -> pd.DataFrame:
    return pd.read_csv(ruta, usecols=columnas, skipinitialspace=True)


def hogares(carpeta: Path = RAW) -> pd.DataFrame:
    """Una fila por hogar: región, peso del hogar, tenencia, rentas, gastos y peso de sus personas."""
    d = _leer(carpeta / "ECV_Td_2025/CSV/esudb25d.csv", ["DB030", "DB040", "DB090"])
    h = _leer(
        carpeta / "ECV_Th_2025/CSV/esudb25h.csv",
        ["HB030", "HH021", "HH060", "HH070", "HY020", "HY070N", "HX240"],
    )
    r = _leer(carpeta / "ECV_Tr_2025/CSV/esudb25r.csv", ["RB030", "RB050"])
    m = d.merge(
        h,
        left_on="DB030",
        right_on="HB030",
        how="outer",
        validate="1:1",
        indicator=True,
    )
    if (m["_merge"] != "both").any():
        raise ValueError("hay hogares que no están a la vez en el fichero D y en el H")
    peso = r.groupby(r["RB030"] // 100)["RB050"].sum().rename("peso_personas")
    if set(peso.index) != set(m["DB030"]):
        raise ValueError("hay hogares sin personas o personas sin hogar")
    return m.drop(columns=["_merge", "HB030"]).join(peso, on="DB030")


def _supera(num: pd.Series, den: pd.Series, umbral: float) -> pd.Series:
    """1.0 si num/den > umbral o den <= 0; 0.0 si no; NaN si falta num o den."""
    # Eurostat: num <= 0 → 0 sale de la división (con den > 0); con den <= 0 manda la regla de den
    y = ((num / den > umbral) | (den <= 0)).astype(float)
    return y.where(num.notna() & den.notna())


def sobrecarga_eurostat(h: pd.DataFrame) -> pd.Series:
    return _supera(h.HH070 * 12 - h.HY070N, h.HY020 - h.HY070N, 0.40)


def sobrecarga_control(h: pd.DataFrame) -> pd.Series:
    return _supera(h.HH070 * 12, h.HY020, 0.40)


def alquiler_30(h: pd.DataFrame) -> pd.Series:
    return _supera(h.HH060 * 12, h.HY020, 0.30)


def tasa(y: pd.Series, w: pd.Series) -> tuple[float, float, int]:
    """Tasa ponderada (%), error estándar (puntos) por linealización y n, sin los NaN de y."""
    ok = y.notna()
    y, w = y[ok], w[ok]
    n = len(y)
    if n < 2:
        raise ValueError(f"hacen falta al menos 2 observaciones, hay {n}")
    p = np.average(y, weights=w)
    ee = np.sqrt(n / (n - 1) * ((w * (y - p)) ** 2).sum()) / w.sum()
    return 100 * p, 100 * ee, n


def control_f306(h: pd.DataFrame) -> pd.DataFrame:
    """Cifras de control de F3-06: inquilinos de Madrid, ponderados con DB090. ESTIMADO."""
    q = h[(h.DB040 == MADRID) & h.HH021.isin(INQUILINOS)]
    filas = {}
    for nombre, y in {
        "gasto_40": sobrecarga_control(q),
        "alquiler_30": alquiler_30(q),
    }.items():
        t, ee, n = tasa(y, q.DB090)
        e = Z95 * ee * np.sqrt(EFECTO_DISENO)
        filas[nombre] = {"tasa": t, "ee": ee, "ic_inf": t - e, "ic_sup": t + e, "n": n}
    return pd.DataFrame.from_dict(filas, orient="index")
