"""Hogares inquilinos en sobrecarga por zona (F3-06, #100). ESTIMADO: sale de un modelo, no de una encuesta.

Por sección, la renta por unidad de consumo (UC, escala OCDE modificada 1/0,5/0,3) de los inquilinos es una
log-normal con σ del Gini y, como diagnóstico, del P80/P20 (el rango entre las dos σ es el resultado). La media
fija el otro parámetro. El alquiler por UC es otra log-normal (P25 y P75 del SERPAVI), correlacionada con la renta
con el ρ de la ECV, y se le suma la cesta de suministros. Resultado: % de hogares inquilinos cuyo alquiler más
suministros supera el 30, 40 y 50 % de su renta, y el esfuerzo mediano, agregado a zona con pesos de inquilinos.

Fuentes: ADRH (INE: renta, Gini, P80/P20, menores, tamaño del hogar); SERPAVI (MIVAU: alquiler por sección);
Censo 2021 (INE, `C2021_Indicadores.csv`: t20_2 alquiler y t19_1 hogares principales); EPF (suministros por UC,
`hogares.cesta_uc`); ECV 2025, microdatos del INE (cociente de renta, ρ); catálogo 1912645 de la Comunidad de
Madrid (inquilinos 2025 frente a 2021). Cifra de control: ECV 2025 (`sobrecarga_ecv`), intervalos en
`docs/decisiones.md`.

Supuestos y sentido del sesgo:
- El SERPAVI se aplica a todos los inquilinos: sobrestima (el 16 % paga por debajo del mercado; cota inferior 0,84×).
- El cociente de renta inquilinos/propietarios es el regional y el mismo en todas las secciones.
- σ igual para inquilinos y para todos los hogares (ECV ES30: 0,62 frente a 0,62).
- ρ regional, probablemente mayor que dentro de una sección: infraestima (sensibilidad con ρ = 0).
- Menores de 18 en lugar de menores de 14 en la escala OCDE; hogares inquilinos del tamaño medio de la sección.
- Ayudas sin descontar (en la ECV baja el control de 36,0 a 35,5).
- La comunidad no está en la cesta de suministros: el resultado queda algo por debajo del control.
- Suministros de 2025 con renta de 2024; Gini de personas aplicado a hogares.
- Percentiles del SERPAVI de 2021 pasados a 2025 como media ponderada (aproximación), e inquilinos de 2021
  llevados a 2025 con un crecimiento uniforme. Solo 2024.
"""

import logging
from functools import cache
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.polynomial.hermite_e import hermegauss
from scipy.optimize import brentq
from scipy.stats import norm

from mesobra import contratos, hogares, paso_secciones, renta, sobrecarga_ecv

LOG = logging.getLogger(__name__)
RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data/raw"
PROCESSED = RAIZ / "data/processed"
ANIO = 2024
# el Gini del INE recorta el 1,5 % de cada cola
RECORTE = 0.015
CORTES = (0.30, 0.40, 0.50)
NODOS = 40
SIGMAS = ("sigma_gini", "sigma_p80")
CENSO = RAW / "ine_c2021_indicadores_seccion_2026-11-18.csv"
TENENCIA = RAW / "cm_ecv_tenencia_hogares_2026-11-18.csv"
DEMOGRAFICOS = "ine_adrh_demograficos_madrid_2026-11-15.csv"
MERCADO = "Hogares con la vivienda en regimen de alquiler a precio de mercado"
REDUCIDO = (
    "Hogares con la vivienda en regimen de alquiler inferior al precio de mercado"
)
# intervalos de docs/decisiones.md (2026-11-18), fijados antes de ejecutar el modelo
CONTROL = {
    "40": (28.6, 43.4),
    "<=30": (38.2, 53.8),
    "30-40": (12.5, 23.5),
    "40-50": (6.0, 14.8),
    ">50": (19.0, 32.2),
}


def sigma_p80p20(r):
    """σ de una log-normal con cociente P80/P20 igual a `r`."""
    return np.log(r) / (norm.ppf(0.8) - norm.ppf(0.2))


def gini_recortado(sigma, recorte=RECORTE):
    """Gini de una log-normal restringida a sus cuantiles [recorte, 1 − recorte], como el del INE.

    Cuantil x(u) en una rejilla de puntos medios de u; G = 2·media(u·x)/media(x) − 1.
    """
    u = (np.arange(20_000) + 0.5) / 20_000
    x = np.exp(np.asarray(sigma)[..., None] * norm.ppf(recorte + (1 - 2 * recorte) * u))
    return 2 * (u * x).mean(-1) / x.mean(-1) - 1


@cache
def _rejilla():
    sigmas = np.linspace(1e-3, 3, 600)
    return sigmas, gini_recortado(sigmas)


def sigma_gini(g):
    """σ cuyo Gini recortado es `g` (0-100); la relación es monótona y se interpola en una rejilla."""
    sigmas, ginis = _rejilla()
    g = np.asarray(g, dtype=float) / 100
    if (g < ginis[0]).any() or (g > ginis[-1]).any():
        raise ValueError(f"Gini fuera de la rejilla [{ginis[0]:.4f}, {ginis[-1]:.4f}]")
    return np.interp(g, ginis, sigmas)


def media_inquilinos(renta_uc, p, c):
    """Media por UC de los inquilinos: la media total es p·c·m + (1 − p)·m, con c = inquilinos/propietarios."""
    return renta_uc * c / (p * c + 1 - p)


def unidades_consumo(tam_hogar, pct_menores):
    """UC de la escala OCDE modificada de un hogar medio; los menores de 18 cuentan 0,3 (aproximación de 14)."""
    k = tam_hogar * pct_menores / 100
    return 1 + 0.5 * (tam_hogar - 1 - k) + 0.3 * k


def prob_supera(sec, sigma, rho, k):
    """P(alquiler más suministros por UC > k × renta por UC) en cada sección, integrando el alquiler.

    `sec` trae m_media (renta media por UC de los inquilinos, €/año), mu_a y sigma_a (log del alquiler €/mes),
    uc y sum_uc (suministros €/mes por UC). Con ε = ρz + √(1−ρ²)η, la condición es η < (…)/(σ√(1−ρ²)) y
    se promedia en z con Gauss-Hermite.
    """
    z, w = hermegauss(NODOS)
    w = w / np.sqrt(2 * np.pi)
    sigma = np.asarray(sigma)[:, None]
    m_log = np.log(sec["m_media"].to_numpy())[:, None] - sigma**2 / 2
    alquiler = np.exp(
        sec["mu_a"].to_numpy()[:, None] + sec["sigma_a"].to_numpy()[:, None] * z
    )
    coste = 12 * (
        alquiler / sec["uc"].to_numpy()[:, None] + sec["sum_uc"].to_numpy()[:, None]
    )
    x = (np.log(coste / k) - m_log - rho * sigma * z) / (sigma * np.sqrt(1 - rho**2))
    return norm.cdf(x) @ w


def esfuerzo_mediano(sec, sigma, rho, pesos):
    """Mediana (% de la renta) de la mezcla de secciones con `pesos`: el k con P(E > k) = 0,5."""
    pesos = np.asarray(pesos, dtype=float)

    def exceso(k):
        return np.average(prob_supera(sec, sigma, rho, k), weights=pesos) - 0.5

    return 100 * brentq(exceso, 1e-3, 20)


def tenencia_2025_2021(ruta=TENENCIA):
    """Factor de crecimiento de los hogares inquilinos (mercado + inferior) de 2021 a 2025."""
    d = pd.read_csv(ruta, sep=";", encoding="utf-8-sig", dtype=str)
    d = d[d["Año"].isin(["2021", "2025"]) & d["Concepto"].isin([MERCADO, REDUCIDO])]
    if len(d) != 4 or d.duplicated(["Año", "Concepto"]).any():
        raise ValueError(f"Hace falta una fila por año y concepto, hay {len(d)}")
    suma = d.assign(v=d["Valor"].astype(float)).groupby("Año")["v"].sum()
    return suma["2025"] / suma["2021"]


def _pasar_extensiva(paso, serie):
    """Pasa una extensiva a 2025 sin los orígenes sin dato ni los que no están en la tabla (se cuentan)."""
    fuera = ~serie.index.isin(paso["origen"])
    LOG.info(
        "orígenes del Censo fuera de la tabla de paso: %d; orígenes de la tabla sin dato: %d",
        fuera.sum(),
        paso["origen"].nunique() - (~fuera).sum(),
    )
    tabla = paso[paso["origen"].isin(serie.index)]
    return paso_secciones.pasar_extensiva(tabla, serie[~fuera])


def inquilinos_seccion(paso):
    """Hogares inquilinos (t20_2) y principales (t19_1) del Censo 2021 pasados a las secciones de 2025."""
    c = pd.read_csv(CENSO, dtype=str)
    c = c[c["cpro"] == "28"]
    c = c.assign(cusec=c["cpro"] + c["cmun"] + c["dist"] + c["secc"]).set_index("cusec")
    c = c[["t20_2", "t19_1"]].apply(pd.to_numeric, errors="raise")
    secreto = c.isna().any(axis=1)
    LOG.info(
        "secciones del Censo con t20_2 o t19_1 en secreto, excluidas: %d", secreto.sum()
    )
    c = c[~secreto]
    return pd.DataFrame(
        {
            "inquilinos": _pasar_extensiva(paso, c["t20_2"]),
            "principales": _pasar_extensiva(paso, c["t19_1"]),
        }
    )


def alquiler_2025(paso):
    """Parámetros log-normales del alquiler (€/mes) por sección de 2025, desde P25 y P75 del SERPAVI."""
    a = pd.read_parquet(PROCESSED / "alquiler_seccion.parquet")
    a = a[a["anio"] == ANIO].set_index("seccion_id")
    a = a[a.index.isin(paso["origen"])]
    testigos = a["testigos"].astype(float)
    p = {
        n: paso_secciones.pasar_intensiva(paso, a[f"cuantia_{n}"], testigos)
        for n in ("p25", "p50", "p75")
    }
    mu = (np.log(p["p25"]) + np.log(p["p75"])) / 2
    sigma = (np.log(p["p75"]) - np.log(p["p25"])) / (2 * norm.ppf(0.75))
    LOG.info("mediana de |ln P50 − mu_a|: %.4f", (np.log(p["p50"]) - mu).abs().median())
    return pd.DataFrame({"mu_a": mu, "sigma_a": sigma})


def parametros_ecv(h):
    """Cociente de renta por UC inquilinos/propietarios (c) y correlación ρ alquiler-renta de ES30."""
    h = h[h["DB040"] == sobrecarga_ecv.MADRID].assign(
        renta_uc=lambda d: d.HY020 / d.HX240
    )
    inq = h[h["HH021"].isin(sobrecarga_ecv.INQUILINOS)]
    prop = h[h["HH021"].isin((1, 2))]
    m_inq = np.average(inq["renta_uc"], weights=inq["peso_personas"])
    m_prop = np.average(prop["renta_uc"], weights=prop["peso_personas"])
    ok = inq[(inq["HH060"] > 0) & (inq["HY020"] > 0)]
    cov = np.cov(np.log(ok["HH060"]), np.log(ok["renta_uc"]), aweights=ok["DB090"])
    positivos = h[h["renta_uc"] > 0]
    return {
        "c": m_inq / m_prop,
        "media_inquilinos": m_inq,
        "rho": cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1]),
        "n": len(ok),
        "excluidos": len(inq) - len(ok),
        "sigma_inquilinos": np.sqrt(
            np.cov(np.log(ok["renta_uc"]), aweights=ok["peso_personas"])
        ),
        "sigma_total": np.sqrt(
            np.cov(np.log(positivos["renta_uc"]), aweights=positivos["peso_personas"])
        ),
    }


def _zona_de(cusec):
    return cusec.str[:7].where(cusec.str[:5] == "28079", cusec.str[:5])


def secciones(paso, f, c):
    """Una fila por sección de 2025 con todo lo que necesita el modelo; excluye y cuenta las que no lo tienen."""
    r = pd.read_parquet(PROCESSED / "renta.parquet")
    r = r[r["anio"] == ANIO]
    dem = renta._leer(
        renta.RAW / DEMOGRAFICOS,
        {"Porcentaje de población menor de 18 años": "pct_menores"},
    )
    dem = dem[dem["anio"] == ANIO]
    sec = (
        r[r["nivel"] == "seccion"]
        .set_index("unidad_id")
        .drop(columns=["nivel", "anio", "poblacion"])
        .join(dem[dem["nivel"] == "seccion"].set_index("unidad_id")["pct_menores"])
        .join(inquilinos_seccion(paso))
        .join(alquiler_2025(paso))
    )
    sec["zona_id"] = _zona_de(sec.index.to_series())
    for col, fuente in (("gini", r), ("p80p20", r), ("pct_menores", dem)):
        zona = fuente[fuente["nivel"] == "zona"].set_index("unidad_id")[col]
        sec[col] = sec[col].fillna(sec["zona_id"].map(zona).astype(float))
    obligatorias = [
        "renta_uc",
        "tam_hogar",
        "pct_menores",
        "gini",
        "p80p20",
        "mu_a",
        "sigma_a",
    ]
    valida = sec[obligatorias + ["inquilinos", "principales"]].notna().all(axis=1)
    valida &= sec["inquilinos"].fillna(0) > 0
    LOG.info(
        "secciones de 2025: %d; excluidas por falta de dato: %d",
        len(sec),
        (~valida).sum(),
    )
    sec = sec[valida].copy()
    p = f * sec["inquilinos"] / sec["principales"]
    LOG.info("secciones con proporción de inquilinos recortada a 1: %d", (p > 1).sum())
    sec["uc"] = unidades_consumo(sec["tam_hogar"], sec["pct_menores"])
    sec["m_media"] = media_inquilinos(sec["renta_uc"], p.clip(upper=1), c)
    sec["sum_uc"] = hogares.cesta_uc()["suministros"]
    sec["sigma_gini"] = sigma_gini(sec["gini"])
    sec["sigma_p80"] = sigma_p80p20(sec["p80p20"])
    sec["dif_sigma"] = sec["sigma_p80"] - sec["sigma_gini"]
    return sec


def _tasas(sec, sigma, rho):
    """% por encima de cada corte y esfuerzo mediano de las secciones de `sec`, con pesos de inquilinos."""
    w = sec["inquilinos"].to_numpy()
    tasas = {
        f"pct_{round(100 * k)}": 100
        * np.average(prob_supera(sec, sigma, rho, k), weights=w)
        for k in CORTES
    }
    tasas["esfuerzo_mediano"] = esfuerzo_mediano(sec, sigma, rho, w)
    return tasas


def _rango(sec, rho):
    """Mínimo y máximo de cada tasa entre las dos σ."""
    a, b = (_tasas(sec, sec[s].to_numpy(), rho) for s in SIGMAS)
    return {
        f"{k}_{lado}": fn(a[k], b[k])
        for k in a
        for lado, fn in (("inf", min), ("sup", max))
    }


def sobrecarga(sec, rho):
    """Tabla `sobrecarga` (contrato): una fila por zona de 2024, con nulos si no tiene ninguna sección válida."""
    zonas = pd.read_parquet(PROCESSED / "renta.parquet")
    zonas = zonas[(zonas["nivel"] == "zona") & (zonas["anio"] == ANIO)]["unidad_id"]
    filas = {
        z: {
            **_rango(g, rho),
            "dif_sigma": np.average(g["dif_sigma"], weights=g["inquilinos"]),
        }
        for z, g in sec.groupby("zona_id")
    }
    df = pd.DataFrame.from_dict(filas, orient="index").reindex(zonas.to_numpy())
    df = df.rename_axis("zona_id").reset_index().assign(anio=ANIO)
    df = df[list(contratos.CONTRATOS["sobrecarga"]["columnas"])].astype(
        contratos.dtypes("sobrecarga")
    )
    contratos.validar(df, "sobrecarga")
    return df


def comunidad(sec, rho):
    """Agregado de la Comunidad: rango de cada cifra y, con control, si el punto medio cae en su intervalo."""
    r = [_tasas(sec, sec[s].to_numpy(), rho) for s in SIGMAS]
    valores = {
        "30": [x["pct_30"] for x in r],
        "40": [x["pct_40"] for x in r],
        "50": [x["pct_50"] for x in r],
        "mediana": [x["esfuerzo_mediano"] for x in r],
        "<=30": [100 - x["pct_30"] for x in r],
        "30-40": [x["pct_30"] - x["pct_40"] for x in r],
        "40-50": [x["pct_40"] - x["pct_50"] for x in r],
        ">50": [x["pct_50"] for x in r],
    }
    salida = {}
    for nombre, v in valores.items():
        inf, sup = min(v), max(v)
        fila = {"inf": inf, "sup": sup, "medio": (inf + sup) / 2, "ancho": sup - inf}
        if nombre in CONTROL:
            lo, hi = CONTROL[nombre]
            fila |= {
                "control": (lo, hi),
                "pasa": lo <= fila["medio"] <= hi and fila["ancho"] <= hi - lo,
            }
        salida[nombre] = fila
    return salida


def _registrar(titulo, agregado):
    for nombre, v in agregado.items():
        LOG.info("%s %s: %s", titulo, nombre, v)


def main():
    logging.basicConfig(level=logging.INFO)
    par = parametros_ecv(sobrecarga_ecv.hogares())
    LOG.info("ECV: %s", par)
    f = tenencia_2025_2021()
    LOG.info("factor de inquilinos 2025/2021: %.4f", f)
    paso = pd.read_parquet(PROCESSED / "paso_secciones_2021_2025.parquet")
    sec = secciones(paso, f, par["c"])
    LOG.info(
        "cuantiles 5, 25, 50, 75, 95 de dif_sigma: %s",
        sec["dif_sigma"].quantile([0.05, 0.25, 0.5, 0.75, 0.95]).round(4).tolist(),
    )
    LOG.info(
        "mediana de (renta_hogar/renta_uc)/uc: %.4f",
        ((sec["renta_hogar"] / sec["renta_uc"]) / sec["uc"]).median(),
    )
    agregado = comunidad(sec, par["rho"])
    _registrar("Comunidad", agregado)
    sens = comunidad(sec, 0.0)
    LOG.info(
        "sensibilidad ρ=0: 40 %% %s, pasa %s", sens["40"]["medio"], sens["40"]["pasa"]
    )
    LOG.info(
        "cota inferior del catálogo (0,84 × 40 %%): %.2f",
        0.84 * agregado["40"]["medio"],
    )
    tabla = sobrecarga(sec, par["rho"])
    PROCESSED.mkdir(parents=True, exist_ok=True)
    tabla.to_parquet(PROCESSED / "sobrecarga.parquet")


if __name__ == "__main__":
    main()
