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
- El cociente de renta por UC inquilinos/propietarios (por hogar, ECV ES30) es el regional y el mismo en todas
  las secciones. El 4 % de hogares en cesión (HH021 = 5) se ignora en la mezcla de dos grupos.
- La renta del ADRH es por persona y la tasa es de hogares: se pasa a media por hogar con el cociente de la ECV.
- σ igual para inquilinos y para todos los hogares (ECV ES30: 0,62 frente a 0,62); Gini de personas aplicado a hogares.
- La renta del ADRH es fiscal: no recoge la economía informal ni las transferencias entre hogares, lo que engorda
  la cola baja y sobrestima.
- Menores de 18 (no de 14) a 0,3 en la escala OCDE, hogares inquilinos del tamaño medio de la sección: bajan la UC
  y sobrestiman.
- La cesta de suministros no incluye comunidad, basuras, alcantarillado, mantenimiento ni seguro: infraestima.
  Son de 2025 actualizados con el IPC (`hogares.cesta_uc`, attrs `ipc_hasta`) frente a la renta de 2024: sobrestima.
- ρ regional, probablemente mayor que dentro de una sección. El sentido depende de la tasa: con una tasa por encima
  del 50 %, un ρ mayor la sube; por debajo, la baja (sensibilidad con ρ = 0).
- Ayudas sin descontar (en la ECV baja el control de 36,0 a 35,5).
- Percentiles del SERPAVI de 2021 pasados a 2025 como media ponderada (aproximación), e inquilinos de 2021
  llevados a 2025 con un crecimiento uniforme. Solo 2024.
- Las secciones de menos de 100 residentes heredan del INE el valor de su municipio o distrito; las que siguen
  sin Gini, P80/P20 o menores se excluyen y se cuentan, y la `cobertura` de la zona lo dice.
- La `cobertura` no cuenta las 8 secciones del Censo en secreto y, en 28079, solo suma los distritos con alguna
  sección válida (en 2024 lo son los 21): si eso cambia, la sobrestima.
- No se calcula la pureza del paso de 2021 a 2025 (283 de 4.299 destinos por debajo de 0,8): la tabla no se
  publica; si llegara a publicarse, la pureza por zona sería obligatoria (`paso_secciones.pureza`).
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
# el Gini del INE winsoriza el 1,5 % de cada cola (Metodología ADRH §3): sustituye por el valor más próximo
RECORTE = 0.015
# 40 %: Eurostat (housing cost overburden rate: "more than 40 % of disposable income"); 30 %: por analogía con la
# Ley 12/2023, art. 18.3.a, que mide la carga media de la zona, no la de cada hogar; 50 %: convención propia
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


def sigma_p80p20(r: np.ndarray | float) -> np.ndarray | float:
    """σ de una log-normal con cociente P80/P20 igual a `r`."""
    return np.log(r) / (norm.ppf(0.8) - norm.ppf(0.2))


def gini_recortado(sigma: np.ndarray | float, recorte: float = RECORTE) -> np.ndarray:
    """Gini de una log-normal winsorizada en los cuantiles `recorte` y 1 − `recorte`, como el del INE.

    Cuantil x(u) en una rejilla de puntos medios de u; G = 2·media(u·x)/media(x) − 1.
    """
    u = (np.arange(20_000) + 0.5) / 20_000
    x = np.exp(
        np.asarray(sigma)[..., None] * norm.ppf(np.clip(u, recorte, 1 - recorte))
    )
    return 2 * (u * x).mean(-1) / x.mean(-1) - 1


@cache
def _rejilla() -> tuple[np.ndarray, np.ndarray]:
    sigmas = np.linspace(1e-3, 3, 600)
    return sigmas, gini_recortado(sigmas)


def sigma_gini(g: np.ndarray | float) -> np.ndarray:
    """σ cuyo Gini winsorizado es `g` (0-100); la relación es monótona y se interpola en una rejilla."""
    sigmas, ginis = _rejilla()
    g = np.asarray(g, dtype=float) / 100
    if (g < ginis[0]).any() or (g > ginis[-1]).any():
        raise ValueError(f"Gini fuera de la rejilla [{ginis[0]:.4f}, {ginis[-1]:.4f}]")
    return np.interp(g, ginis, sigmas)


def media_inquilinos(renta_uc: pd.Series, p: pd.Series, c: float) -> pd.Series:
    """Media por UC y por hogar de los inquilinos: la media total es p·c·m + (1 − p)·m, con c = inquilinos/propietarios.

    Mezcla de dos grupos: el 4 % de hogares en cesión gratuita (HH021 = 5) se ignora.
    """
    return renta_uc * c / (p * c + 1 - p)


def unidades_consumo(tam_hogar: pd.Series, pct_menores: pd.Series) -> pd.Series:
    """UC de la escala OCDE modificada de un hogar medio; los menores de 18 cuentan 0,3 (aproximación de 14)."""
    k = tam_hogar * pct_menores / 100
    return 1 + 0.5 * (tam_hogar - 1 - k) + 0.3 * k


def prob_supera(
    sec: pd.DataFrame, sigma: np.ndarray, rho: float, k: float
) -> np.ndarray:
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


def esfuerzo_mediano(
    sec: pd.DataFrame, sigma: np.ndarray, rho: float, pesos: np.ndarray
) -> float:
    """Mediana (% de la renta) de la mezcla de secciones con `pesos`: el k con P(E > k) = 0,5."""
    pesos = np.asarray(pesos, dtype=float)

    def exceso(k: float) -> float:
        return np.average(prob_supera(sec, sigma, rho, k), weights=pesos) - 0.5

    return 100 * brentq(exceso, 1e-3, 20)


def tenencia_2025_2021(ruta: Path = TENENCIA) -> float:
    """Factor de crecimiento de los hogares inquilinos (mercado + inferior) de 2021 a 2025."""
    d = pd.read_csv(ruta, sep=";", encoding="utf-8-sig", dtype=str)
    d = d[d["Año"].isin(["2021", "2025"]) & d["Concepto"].isin([MERCADO, REDUCIDO])]
    if len(d) != 4 or d.duplicated(["Año", "Concepto"]).any():
        raise ValueError(f"Hace falta una fila por año y concepto, hay {len(d)}")
    suma = d.assign(v=d["Valor"].astype(float)).groupby("Año")["v"].sum()
    return suma["2025"] / suma["2021"]


def _pasar_extensiva(paso: pd.DataFrame, serie: pd.Series) -> pd.Series:
    """Pasa una extensiva a 2025; cuenta los orígenes de la tabla sin dato. Un dato fuera de la tabla falla."""
    en_tabla = serie.index.isin(paso["origen"]).sum()
    LOG.info(
        "orígenes de la tabla de paso sin dato del Censo: %d",
        paso["origen"].nunique() - en_tabla,
    )
    return paso_secciones.pasar_extensiva(paso[paso["origen"].isin(serie.index)], serie)


def inquilinos_seccion(paso: pd.DataFrame) -> pd.DataFrame:
    """Hogares inquilinos (t20_2) y principales (t19_1) del Censo 2021 pasados a las secciones de 2025."""
    c = pd.read_csv(CENSO, dtype=str, encoding="utf-8")
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


def alquiler_2025(paso: pd.DataFrame) -> pd.DataFrame:
    """Parámetros log-normales del alquiler (€/mes) por sección de 2025, desde P25 y P75 del SERPAVI."""
    a = pd.read_parquet(PROCESSED / "alquiler_seccion.parquet")
    a = a[a["anio"] == ANIO].set_index("seccion_id")
    testigos = a["testigos"].astype(float)
    p = {
        n: paso_secciones.pasar_intensiva(paso, a[f"cuantia_{n}"], testigos)
        for n in ("p25", "p50", "p75")
    }
    mu = (np.log(p["p25"]) + np.log(p["p75"])) / 2
    sigma = (np.log(p["p75"]) - np.log(p["p25"])) / (2 * norm.ppf(0.75))
    LOG.info("mediana de |ln P50 − mu_a|: %.4f", (np.log(p["p50"]) - mu).abs().median())
    return pd.DataFrame({"mu_a": mu, "sigma_a": sigma})


def parametros_ecv(h: pd.DataFrame) -> dict[str, float]:
    """De ES30: cociente c de renta por UC inquilinos/propietarios (hogares, DB090), k_hogar (media por hogar
    entre media por persona de todos los hogares), ρ alquiler-renta y diagnósticos (medias por persona, σ).
    """
    h = h[h["DB040"] == sobrecarga_ecv.MADRID].assign(
        renta_uc=lambda d: d.HY020 / d.HX240
    )
    inq = h[h["HH021"].isin(sobrecarga_ecv.INQUILINOS)]
    prop = h[h["HH021"].isin((1, 2))]
    ok = inq[(inq["HH060"] > 0) & (inq["HY020"] > 0)]
    cov = np.cov(np.log(ok["HH060"]), np.log(ok["renta_uc"]), aweights=ok["DB090"])
    positivos = h[h["renta_uc"] > 0]
    return {
        "c": np.average(inq["renta_uc"], weights=inq["DB090"])
        / np.average(prop["renta_uc"], weights=prop["DB090"]),
        "k_hogar": np.average(h["renta_uc"], weights=h["DB090"])
        / np.average(h["renta_uc"], weights=h["peso_personas"]),
        "media_inquilinos_persona": np.average(
            inq["renta_uc"], weights=inq["peso_personas"]
        ),
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


def _zona_de(cusec: pd.Series) -> pd.Series:
    """Zona de una sección: distrito (7 dígitos) en Madrid capital, municipio (5) en el resto."""
    return cusec.str[:7].where(cusec.str[:5] == "28079", cusec.str[:5])


def secciones(paso: pd.DataFrame, f: float, par: dict[str, float]) -> pd.DataFrame:
    """Una fila por sección de 2025 con lo que necesita el modelo; excluye y cuenta las que no lo tienen.

    `f` es el crecimiento de los inquilinos 2021-2025 y `par` el resultado de `parametros_ecv`. Las secciones
    de menos de 100 residentes ya traen del INE el valor heredado de su municipio o distrito; las que aun así
    no tienen Gini, P80/P20, menores, alquiler o inquilinos se excluyen. `inq_zona` es el total de inquilinos
    de la zona de la sección, con las excluidas, para la cobertura.
    """
    r = pd.read_parquet(PROCESSED / "renta.parquet")
    r = r[(r["anio"] == ANIO) & (r["nivel"] == "seccion")]
    dem = renta._leer(
        renta.RAW / DEMOGRAFICOS,
        {"Porcentaje de población menor de 18 años": "pct_menores"},
    )
    dem = dem[(dem["anio"] == ANIO) & (dem["nivel"] == "seccion")]
    sec = (
        r.set_index("unidad_id")
        .drop(columns=["nivel", "anio", "poblacion"])
        .join(dem.set_index("unidad_id")["pct_menores"])
        .join(inquilinos_seccion(paso))
        .join(alquiler_2025(paso))
    )
    sec["zona_id"] = _zona_de(sec.index.to_series())
    sec["inq_zona"] = sec.groupby("zona_id")["inquilinos"].transform("sum")
    obligatorias = ["renta_uc", "tam_hogar", "pct_menores", "gini", "p80p20"]
    obligatorias += ["mu_a", "sigma_a", "inquilinos", "principales"]
    valida = sec[obligatorias].notna().all(axis=1) & (sec["inquilinos"] > 0)
    LOG.info(
        "secciones de 2025: %d; excluidas por falta de dato: %d; inquilinos que pesan: %.0f de %.0f (%.2f %%)",
        len(sec),
        (~valida).sum(),
        sec.loc[~valida, "inquilinos"].sum(),
        sec["inquilinos"].sum(),
        100 * sec.loc[~valida, "inquilinos"].sum() / sec["inquilinos"].sum(),
    )
    sec = sec[valida].copy()
    p = f * sec["inquilinos"] / sec["principales"]
    LOG.info("secciones con proporción de inquilinos recortada a 1: %d", (p > 1).sum())
    sec["uc"] = unidades_consumo(sec["tam_hogar"], sec["pct_menores"])
    sec["m_media"] = media_inquilinos(
        sec["renta_uc"] * par["k_hogar"], p.clip(upper=1), par["c"]
    )
    sec["sum_uc"] = hogares.cesta_uc()["suministros"]
    sec["sigma_gini"] = sigma_gini(sec["gini"])
    sec["sigma_p80"] = sigma_p80p20(sec["p80p20"])
    sec["dif_sigma"] = sec["sigma_p80"] - sec["sigma_gini"]
    return sec


def _tasas(sec: pd.DataFrame, sigma: np.ndarray, rho: float) -> dict[str, float]:
    """% por encima de cada corte y esfuerzo mediano de las secciones de `sec`, con pesos de inquilinos."""
    w = sec["inquilinos"].to_numpy()
    tasas = {
        f"pct_{round(100 * k)}": 100
        * np.average(prob_supera(sec, sigma, rho, k), weights=w)
        for k in CORTES
    }
    tasas["esfuerzo_mediano"] = esfuerzo_mediano(sec, sigma, rho, w)
    return tasas


def _rango(sec: pd.DataFrame, rho: float) -> dict[str, float]:
    """Mínimo y máximo de cada tasa entre las dos σ."""
    a, b = (_tasas(sec, sec[s].to_numpy(), rho) for s in SIGMAS)
    return {
        f"{k}_{lado}": fn(a[k], b[k])
        for k in a
        for lado, fn in (("inf", min), ("sup", max))
    }


def sobrecarga(sec: pd.DataFrame, rho: float) -> pd.DataFrame:
    """Tabla `sobrecarga` (contrato): una fila por zona de 2024, con nulos si no tiene ninguna sección válida.

    La zona 28079 (Madrid) agrega las secciones de sus distritos. `cobertura` es la fracción de los inquilinos
    de la zona que están en secciones válidas.
    """
    zonas = pd.read_parquet(PROCESSED / "renta.parquet")
    zonas = zonas[(zonas["nivel"] == "zona") & (zonas["anio"] == ANIO)]["unidad_id"]
    grupos = dict(list(sec.groupby("zona_id")))
    madrid = sec[sec["zona_id"].str[:5] == "28079"]
    if len(madrid):
        grupos["28079"] = madrid
    filas = {
        z: {
            **_rango(g, rho),
            "dif_sigma": np.average(g["dif_sigma"], weights=g["inquilinos"]),
            # min: dos sumas de los mismos números en distinto orden pueden dar 1 + 2e-16
            "cobertura": min(
                g["inquilinos"].sum() / g.drop_duplicates("zona_id")["inq_zona"].sum(),
                1.0,
            ),
        }
        for z, g in grupos.items()
    }
    df = pd.DataFrame.from_dict(filas, orient="index").reindex(zonas.to_numpy())
    df = df.rename_axis("zona_id").reset_index().assign(anio=ANIO)
    df = df[list(contratos.CONTRATOS["sobrecarga"]["columnas"])].astype(
        contratos.dtypes("sobrecarga")
    )
    contratos.validar(df, "sobrecarga")
    return df


def comunidad(sec: pd.DataFrame, rho: float) -> dict[str, dict]:
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


def _mediana_ponderada(x: pd.Series, w: pd.Series) -> float:
    o = np.argsort(x.to_numpy())
    acumulado = np.cumsum(w.to_numpy()[o])
    return x.to_numpy()[o][np.searchsorted(acumulado, acumulado[-1] / 2)]


def _mediana_mezcla(mu: np.ndarray, sigma: np.ndarray, w: np.ndarray) -> float:
    """Mediana (en logaritmo) de una mezcla de log-normales con pesos `w`."""

    def exceso(x: float) -> float:
        return np.average(norm.cdf((x - mu) / np.maximum(sigma, 1e-9)), weights=w) - 0.5

    return brentq(exceso, mu.min() - 6, mu.max() + 6)


def _diagnostico(sec: pd.DataFrame, h: pd.DataFrame, rho: float) -> None:
    """Solo log: el 40 % de la Comunidad con σ del Gini y cada ajuste por separado frente a la base.

    Los efectos no se suman: cada uno parte de la base y los ajustes interactúan.
    """
    sigma = sec["sigma_gini"].to_numpy()
    w = sec["inquilinos"]
    q = h[(h["DB040"] == sobrecarga_ecv.MADRID)]
    inq = q[q["HH021"].isin(sobrecarga_ecv.INQUILINOS)]
    renta_ecv = inq["HY020"] / inq["HX240"]
    alquiler_ecv = inq[inq["HH060"] > 0]

    def pct40(d: pd.DataFrame, r: float) -> float:
        return 100 * np.average(prob_supera(d, sigma, r, 0.40), weights=d["inquilinos"])

    uc_modelo = np.average(sec["uc"], weights=w)
    uc_ecv = np.average(inq["HX240"], weights=inq["DB090"])
    mediana_a = np.exp(
        _mediana_mezcla(sec["mu_a"].to_numpy(), sec["sigma_a"].to_numpy(), w)
    )
    mediana_a_ecv = _mediana_ponderada(alquiler_ecv["HH060"], alquiler_ecv["DB090"])
    mediana_r = np.exp(
        _mediana_mezcla(np.log(sec["m_media"].to_numpy()) - sigma**2 / 2, sigma, w)
    )
    LOG.info(
        "diagnóstico del 40 %% (σ del Gini): base %.2f; ρ=0 %.2f; UC escalada a la de la ECV (%.3f frente a %.3f) %.2f; "
        "alquiler escalado a la mediana de la ECV (%.0f frente a %.0f) %.2f",
        pct40(sec, rho),
        pct40(sec, 0.0),
        uc_ecv,
        uc_modelo,
        pct40(sec.assign(uc=sec["uc"] * uc_ecv / uc_modelo), rho),
        mediana_a_ecv,
        mediana_a,
        pct40(sec.assign(mu_a=sec["mu_a"] + np.log(mediana_a_ecv / mediana_a)), rho),
    )
    LOG.info(
        "mediana de la renta por UC de los inquilinos: modelo %.0f; ECV (DB090) %.0f",
        mediana_r,
        _mediana_ponderada(renta_ecv, inq["DB090"]),
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    h = sobrecarga_ecv.hogares()
    par = parametros_ecv(h)
    LOG.info("ECV: %s", par)
    f = tenencia_2025_2021()
    LOG.info("factor de inquilinos 2025/2021: %.4f", f)
    paso = pd.read_parquet(PROCESSED / "paso_secciones_2021_2025.parquet")
    sec = secciones(paso, f, par)
    LOG.info(
        "cuantiles 5, 25, 50, 75, 95 de dif_sigma: %s",
        sec["dif_sigma"].quantile([0.05, 0.25, 0.5, 0.75, 0.95]).round(4).tolist(),
    )
    LOG.info(
        "mediana de (renta_hogar/renta_uc)/uc: %.4f",
        ((sec["renta_hogar"] / sec["renta_uc"]) / sec["uc"]).median(),
    )
    agregado = comunidad(sec, par["rho"])
    for nombre, v in agregado.items():
        LOG.info("Comunidad %s: %s", nombre, v)
    sens = comunidad(sec, 0.0)
    LOG.info(
        "sensibilidad ρ=0: 40 %% %s, pasa %s", sens["40"]["medio"], sens["40"]["pasa"]
    )
    LOG.info(
        "cota inferior del catálogo (0,84 × 40 %%): %.2f",
        0.84 * agregado["40"]["medio"],
    )
    _diagnostico(sec, h, par["rho"])
    tabla = sobrecarga(sec, par["rho"])
    PROCESSED.mkdir(parents=True, exist_ok=True)
    tabla.to_parquet(PROCESSED / "sobrecarga.parquet")


if __name__ == "__main__":
    main()
