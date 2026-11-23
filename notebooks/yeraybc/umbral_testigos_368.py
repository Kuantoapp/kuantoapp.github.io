"""Cifras del umbral de testigos del SERPAVI (#368, decisión del 2026-11-23 en docs/decisiones.md).

1. Semiancho del IC del 95 % de la mediana con n testigos: estadísticos de orden con binomial exacta
   (rangos l y n+1-l, percentiles r/n), interpolado entre p25, p50 y p75 de cada zona (método de #246),
   y segunda vía con una log-normal ajustada a p25 y p75 (10.000 réplicas).
2. Extremos del informe (esfuerzo más bajo de 2024; mayores bajadas y subidas de 2015 a 2024) con 50, 70 y 100.

Uso, desde la raíz del repo: `PYTHONPATH=src python notebooks/yeraybc/umbral_testigos_368.py`
Lee `data/processed/{alquiler_zona,esfuerzo,zonas}.parquet` (de `python -m mesobra`). Tarda ~1 min.
"""

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.stats import binom

PROCESSED = Path(__file__).resolve().parents[2] / "data/processed"


def ultimo_anio(zona: pd.DataFrame) -> pd.DataFrame:
    """Zonas observadas (sin 28079) en su último año con dato: las 158 de la herramienta."""
    z = zona[(zona.origen == "observado") & (zona.zona_id != "28079")]
    z = z.dropna(subset=["eur_m2_p50"])
    return z.sort_values("anio").groupby("zona_id").tail(1)


def rangos(n: int) -> tuple[int, int, float]:
    """Mayor rango l con P(X <= l-1) <= 0,025; u = n+1-l; y la cobertura del intervalo."""
    lo = 1
    while binom.cdf(lo, n, 0.5) <= 0.025:
        lo += 1
    return lo, n + 1 - lo, 1 - 2 * binom.cdf(lo - 1, n, 0.5)


def interp(p, q25, q50, q75):
    return np.where(
        p <= 0.5,
        q25 + (p - 0.25) / 0.25 * (q50 - q25),
        q50 + (p - 0.5) / 0.25 * (q75 - q50),
    )


def semiancho(u: pd.DataFrame, n: int, pre: str) -> np.ndarray:
    """Semiancho relativo (%) por zona, interpolando entre los cuartiles publicados."""
    lo, hi, _ = rangos(n)
    q = [u[f"{pre}_p{k}"].to_numpy() for k in (25, 50, 75)]
    return (interp(hi / n, *q) - interp(lo / n, *q)) / 2 / q[1] * 100


def simulado(u: pd.DataFrame, n: int, pre: str, reps: int = 10_000) -> np.ndarray:
    """Semiancho relativo (%) medio con una log-normal por zona; solo depende de su sigma."""
    rng = np.random.default_rng(368)
    lo, hi, _ = rangos(n)
    q25, q75 = (u[f"{pre}_p{k}"].to_numpy() for k in (25, 75))
    out = []
    for s in (np.log(q75) - np.log(q25)) / (2 * 0.67449):
        x = np.sort(rng.lognormal(0, s, (reps, n)), axis=1)
        out.append(((x[:, hi - 1] - x[:, lo - 1]) / 2).mean() * 100)
    return np.array(out)


def tabla_umbral(u: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for n in (30, 50, 60, 70, 80, 90, 100, 110, 120):
        lo, hi, cob = rangos(n)
        c, e, s = (
            semiancho(u, n, "cuantia"),
            semiancho(u, n, "eur_m2"),
            simulado(u, n, "eur_m2"),
        )
        m = u.testigos < n
        filas.append(
            {
                "n": n, "rangos": f"{lo}-{hi}", "cobertura": f"{cob:.3f}",
                "cuantia_med": np.median(c), "cuantia_p90": np.percentile(c, 90),
                "eur_m2_med": np.median(e), "eur_m2_p90": np.percentile(e, 90),
                "sim_med": np.median(s), "sim_p90": np.percentile(s, 90),
                "zonas_bajo_n": int(m.sum()), "testigos_bajo_n": int(u.testigos[m].sum()),
                "cuantia_mas_12": round((c > 12).mean() * 100, 1),
            }
        )  # fmt: skip
    return pd.DataFrame(filas).round(1)


def extremos(zona: pd.DataFrame, umbral: int) -> dict[str, str]:
    e = pd.read_parquet(PROCESSED / "esfuerzo.parquet")
    nombres = gpd.read_parquet(PROCESSED / "zonas.parquet")[["zona_id", "nombre"]]
    t = e.merge(
        zona[["zona_id", "anio", "testigos"]],
        on=["zona_id", "anio"],
        how="left",
        validate="one_to_one",
    )
    t = t.merge(nombres, on="zona_id", validate="many_to_one")
    t = t[t.zona_id != "28079"].dropna(subset=["esfuerzo"])
    a24 = t[t.anio == 2024]
    c = a24.merge(t[t.anio == 2015], on=["zona_id", "nombre"], suffixes=("", "_15"))
    c["cambio"] = (c.esfuerzo - c.esfuerzo_15) * 100
    c["tmin"] = c[["testigos", "testigos_15"]].min(axis=1)
    ok = c[c.tmin >= umbral]

    def lista(df, col, escala=1):
        return ", ".join(
            f"{r.nombre} {getattr(r, col) * escala:.1f}" for r in df.itertuples()
        )

    return {
        "2024 más bajos": lista(
            a24[a24.testigos >= umbral].nsmallest(3, "esfuerzo"), "esfuerzo", 100
        ),
        "2024 imprecisos más bajos": lista(
            a24[a24.testigos < umbral].nsmallest(3, "esfuerzo"), "esfuerzo", 100
        ),
        "mayores bajadas": lista(ok.nsmallest(3, "cambio"), "cambio"),
        "mayores subidas": lista(ok.nlargest(3, "cambio"), "cambio"),
        "zonas marcadas 2024 / cambio": f"{(a24.testigos < umbral).sum()} / {(c.tmin < umbral).sum()}",
    }


if __name__ == "__main__":
    zona = pd.read_parquet(PROCESSED / "alquiler_zona.parquet")
    u = ultimo_anio(zona)
    assert len(u) == 158, len(u)
    tabla = tabla_umbral(u)
    # control: con 50 reproduce #246 (€/m² 12,0 / 16,4 %, 33 zonas)
    fila50 = tabla.set_index("n").loc[50]
    assert (fila50.eur_m2_med, fila50.zonas_bajo_n) == (12.0, 33), fila50
    print(tabla.to_string(index=False))
    for umbral in (50, 70, 100):
        print(f"\n== umbral {umbral}")
        for k, v in extremos(zona, umbral).items():
            print(f"  {k}: {v}")
