"""Imputación del €/m² mediano de 2024 en las zonas sin dato del SERPAVI (F3-05, #99); todo lo que sale es estimado.

Ejecutar con `python -m mesobra.imputacion`: escribe la validación en `data/processed/imputacion_validacion.json`.
`pipeline_euros` llama a `imputar`. Método de la skill `dm-modelado-espacial`, escenario B (completar zonas sin
publicar), revisado como diseño por `dm-revisor-espacial` antes de escribir código.

Reglas preregistradas: se fijan antes de ejecutar con los datos reales y no se cambian después de ver el resultado.
- Objetivo: log(eur_m2_p50) de 2024 de las zonas sin p50 en ningún año (41 en 2024). Una zona con dato de un año
  anterior no se imputa: `alquiler.json` ya lleva su último año.
- Variables: log población, log renta media por hogar (ADRH 2024; nula en los municipios de menos de 100
  residentes, que tienen el valor común de su comarca, #166), minutos en TP a Centro (2807901) y a la zona de
  50.000 habitantes o más más cercana, con techo de 120 e indicador «sin ruta en 120 min» (`tiempos.json` da null por
  encima). Sin testigos (son la causa de que falte el dato), sin coordenadas y sin identificadores.
- Validación: leave-one-out sobre las zonas con dato con exclusión espacial al estilo NNDM (Milà et al., 2022). Para
  cada zona de test se quitan del train las que están a menos de `b`. `b` minimiza la distancia KS entre la distancia
  de cada test a su train más cercano y la de las zonas objetivo a su dato más cercano (solo coordenadas). Si la KS
  mínima pasa de `KS_MAX`, la validación no imita la tarea y no se imputa.
- La validación que cuenta: zonas con dato y población no mayor que la máxima de las objetivo («pequeños»).
- Modelos, de más simple a más complejo: Wy (media de log p50 de los `K` train más cercanos a más de `b`), MCO en log
  con Wy y las variables, y LightGBM con las mismas más la distancia media a esos vecinos. El Wy de cada fila de train
  sale con la misma exclusión, así que tiene la misma distribución que en test.
- Elección: MAE en log sobre los pequeños. Se queda el más simple salvo que otro lo baje al menos un `MARGEN` en todas
  las variantes de robustez (`K` en {5, 8} y `b` × {0,5; 1; 2}).
- Intervalo: conformal normalizado tipo jackknife (predicción del modelo completo ± q·σ̂, scores LOO; sin la garantía
  ≥ 1 − 2α de CV+, que usaría la predicción de cada pliegue), score |r| / σ̂, con σ̂ = desviación
  típica de log p50 de los vecinos más la mediana de esa desviación en train. El cuantil que se aplica a las objetivo
  sale de los pequeños, con nivel `NIVEL`. La cobertura se mide como transferencia: cuantil de las zonas con dato
  mayores que las objetivo, comprobado en los pequeños, con su IC de Wilson; no se promete.
  Corrección posterior al preregistro (3d8aaf7): este punto medía la cobertura con LOO sobre los propios pequeños, y eso
  da ⌈NIVEL·n⌉/n por construcción (salió 60/66 en todos los modelos y variantes). La regla de corte no cambia; quita
  también la variante de semilla, que estaba vacía (el LOO no tiene azar).
- Corte (plan B de la issue): si la cobertura sobre los pequeños queda más de `CORTE` por debajo de `NIVEL`, no se imputa.
- Zona a zona: «estimado» si el ancho del intervalo no pasa de `UMBRAL_ANCHO` · p50 (supuesto de la issue) y la zona
  está en el área de aplicabilidad (distancia al dato no mayor que la máxima validada y, si el modelo usa variables,
  todas dentro del rango de train, sin nulos). Si no, sigue «sin_dato».
- Resultado esperado según la teoría: Moran alto (0,78 con k=5) y objetivos a 2,7-11 km del dato, así que Wy debería
  explicar la mayor parte. Signos esperados en el MCO: renta +, población +, minutos al centro −.
- p25 y p75 de las filas estimadas = p50 × la mediana de p25/p50 y p75/p50 observada en 2024. La cuantía queda nula:
  esas zonas no tienen esfuerzo (#202).
"""

import json
import logging
from math import ceil, sqrt
from pathlib import Path

import geopandas as gpd
import lightgbm
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

from mesobra import alquiler, bono, contratos, renta

LOG = logging.getLogger(__name__)
# la misma fuente que `pipeline_analisis.FUENTES`; no se importa porque pipeline_analisis importa pipeline_euros
FUENTE_ADRH = {
    "nombre": "INE, Atlas de Distribución de Renta de los Hogares, tabla 31097 (renta neta media por hogar)",
    "url": "https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/31097.csv",
    "licencia": "CC BY 4.0",
}
RAIZ = Path(__file__).resolve().parents[2]
APP_DATOS = RAIZ / "app/datos"
SALIDA = RAIZ / "data/processed/imputacion_validacion.json"
ANIO = 2024
MADRID = "28079"
CENTRO = "2807901"
POLO_HAB = 50_000  # supuesto: «zona más poblada cercana» = la de 50.000 hab o más más cercana en TP
TECHO_TP = 120  # tiempos.json da null por encima de 120 min
SEMILLA = 99
K = 5
NIVEL = 0.90  # supuesto
CORTE = 0.10  # issue: cobertura más de 10 puntos bajo la nominal → no se imputa
MARGEN = 0.10  # supuesto: mejora mínima del MAE para elegir un modelo más complejo
UMBRAL_ANCHO = 0.5  # issue (supuesto declarado): ancho del intervalo ≤ 0,5 · p50
MIN_PEQUENOS = 20  # supuesto: con menos, la cobertura medida tiene ±13 puntos y no sirve para el corte
# supuesto: por encima, la validación no imita la distancia de las objetivo
KS_MAX = 0.3
REJILLA_B = np.arange(0, 15_001, 500)  # metros
VARIABLES = [
    "log_pob",
    "log_renta",
    "tp_centro",
    "sin_ruta_centro",
    "tp_polo",
    "sin_ruta_polo",
]
COLS_MCO = ["wy", *VARIABLES]
MODELOS = ("wy", "mco", "lgbm")  # de más simple a más complejo
LGBM = {
    "n_estimators": 200,
    "learning_rate": 0.05,
    "num_leaves": 7,
    "min_child_samples": 10,
    "deterministic": True,
    "force_row_wise": True,
    "num_threads": 1,
    "verbose": -1,
}


def coordenadas(zonas: gpd.GeoDataFrame) -> pd.DataFrame:
    """Centroide (EPSG:25830, metros) de cada zona, por `zona_id`."""
    c = zonas.set_index("zona_id").to_crs(25830).geometry.centroid
    return pd.DataFrame({"x": c.x, "y": c.y})


def variables(
    zonas: gpd.GeoDataFrame, rentas: pd.DataFrame, tiempos: dict
) -> pd.DataFrame:
    """Variables por `zona_id` (ver docstring); la renta de comarca de los municipios de <100 residentes, nula."""
    pob = zonas.set_index("zona_id")["poblacion"]
    r = rentas[(rentas["nivel"] == "zona") & (rentas["anio"] == ANIO)].set_index(
        "unidad_id"
    )
    renta_propia = r["renta_hogar"].where(r["poblacion"] >= 100)
    destinos = [d["destino_id"] for d in tiempos["destinos"]]
    tp = pd.DataFrame(
        tiempos["tp"], index=tiempos["origenes"], columns=destinos, dtype=float
    )
    polos = pob.index[pob >= POLO_HAB]
    centro, polo = tp[CENTRO], tp[polos].min(axis=1)
    return pd.DataFrame(
        {
            "log_pob": np.log(pob),
            "log_renta": np.log(renta_propia.reindex(pob.index)),
            "tp_centro": centro.reindex(pob.index).fillna(TECHO_TP),
            "sin_ruta_centro": centro.reindex(pob.index).isna().astype(float),
            "tp_polo": polo.reindex(pob.index).fillna(TECHO_TP),
            "sin_ruta_polo": polo.reindex(pob.index).isna().astype(float),
        }
    )


def distancias(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Distancias euclídeas (m) entre las filas de `a` y las de `b`."""
    return np.sqrt(((a[:, None, :] - b[None, :, :]) ** 2).sum(-1))


def vecinos(d: np.ndarray, k: int, b: float) -> np.ndarray:
    """Índices de los `k` más cercanos a más de `b` por fila (`d` filas × candidatos); la propia zona, a 0 m, queda fuera."""
    lejos = np.where(d > b, d, np.inf)
    idx = np.argsort(lejos, axis=1, kind="stable")[:, :k]
    if np.isinf(np.take_along_axis(lejos, idx, axis=1)).any():
        raise ValueError(f"Menos de {k} vecinos a más de {b} m")
    return idx


def elegir_buffer(d_obs: np.ndarray, d_obj: np.ndarray) -> tuple[float, float]:
    """`b` de la rejilla que minimiza la KS entre la distancia test-train más cercano (LOO) y la de las objetivo."""
    objetivo = d_obj.min(axis=1)
    ks = [
        ks_2samp(np.where(d_obs > b, d_obs, np.inf).min(axis=1), objetivo).statistic
        for b in REJILLA_B
    ]
    i = int(np.argmin(ks))
    return float(REJILLA_B[i]), float(ks[i])


def particiones(d_obs: np.ndarray, test: np.ndarray, b: float):
    """Por cada zona de `test` (índices), (zona, train): todas las demás menos las que están a `b` metros o menos."""
    for i in test:
        yield i, np.flatnonzero(d_obs[i] > b)


def _locales(y_vec: np.ndarray, d_vec: np.ndarray) -> pd.DataFrame:
    return pd.DataFrame(
        {"wy": y_vec.mean(axis=1), "sd": y_vec.std(axis=1), "dist": d_vec.mean(axis=1)}
    )


def _beta(train: pd.DataFrame) -> np.ndarray:
    """Coeficientes del MCO (constante y `COLS_MCO`) de `y` en `train`."""
    a = np.c_[np.ones(len(train)), train[COLS_MCO].to_numpy()]
    return np.linalg.lstsq(a, train["y"].to_numpy(), rcond=None)[0]


def coeficientes_mco(obs: dict, b: float) -> dict[str, float]:
    """Coeficientes del MCO con todas las zonas con dato (Wy con la exclusión `b`), para contrastar los signos."""
    train = _con_vecinos(obs["x"], obs["y"], obs["d"], vecinos(obs["d"], K, b))
    train["y"] = obs["y"]
    return dict(zip(["constante", *COLS_MCO], _beta(train).tolist(), strict=True))


def _ajustar_predecir(
    modelo: str, train: pd.DataFrame, test: pd.DataFrame, semilla: int
) -> np.ndarray:
    """Predicción en log de `test` con `modelo` ajustado en `train` (columna `y`)."""
    if modelo == "wy":
        return test["wy"].to_numpy()
    if modelo == "mco":
        beta = _beta(train)
        return np.c_[np.ones(len(test)), test[COLS_MCO].to_numpy()] @ beta
    cols = ["wy", "dist", *VARIABLES]
    m = lightgbm.LGBMRegressor(**LGBM, random_state=semilla).fit(
        train[cols], train["y"]
    )
    return m.predict(test[cols])


def _con_vecinos(
    x: pd.DataFrame, y: np.ndarray, d: np.ndarray, v: np.ndarray
) -> pd.DataFrame:
    """Variables + `wy`, `sd` y `dist` de cada fila con sus vecinos `v` (índices en `y`; `d`: fila × candidatos)."""
    locales = _locales(y[v], np.take_along_axis(d, v, 1))
    return pd.concat([x.reset_index(drop=True), locales], axis=1)


def predecir(
    datos: dict, test_x: pd.DataFrame, d_test: np.ndarray, conf: dict
) -> pd.DataFrame:
    """Predice log p50 de `test_x` entrenando con `datos` (`x`, `y`, `d` entre ellos); `d_test`: test × train.

    `conf`: `modelo`, `k`, `b` (exclusión del Wy de train), `b_test` (la del test) y `semilla`.
    """
    k, y = conf["k"], datos["y"]
    v_train = vecinos(datos["d"], k, conf["b"])
    v_test = vecinos(d_test, k, conf["b_test"])
    train = _con_vecinos(datos["x"], y, datos["d"], v_train)
    test = _con_vecinos(test_x, y, d_test, v_test)
    train["y"] = y
    c = float(np.median(train["sd"]))
    test["pred"] = _ajustar_predecir(conf["modelo"], train, test, conf["semilla"])
    test["sigma"] = test["sd"] + c
    test["dist_dato"] = d_test.min(axis=1)
    return test


def validar_loo(obs: dict, pequenos: np.ndarray, conf: dict) -> pd.DataFrame:
    """Predicción fuera de muestra de cada pequeño con la partición de `particiones` (`conf["b"]`)."""
    filas = []
    for i, tr in particiones(obs["d"], pequenos, conf["b"]):
        datos = {
            "x": obs["x"].iloc[tr],
            "y": obs["y"][tr],
            "d": obs["d"][np.ix_(tr, tr)],
        }
        p = predecir(
            datos, obs["x"].iloc[[i]], obs["d"][[i]][:, tr], conf | {"b_test": 0.0}
        )
        filas.append(p.assign(i=i, y=obs["y"][i]))
    return pd.concat(filas, ignore_index=True)


def cuantil_conformal(scores: np.ndarray, nivel: float) -> float:
    """⌈nivel·(n+1)⌉-ésimo menor score; infinito si n es demasiado pequeño."""
    r = ceil(nivel * (len(scores) + 1))
    return float(np.sort(scores)[r - 1]) if r <= len(scores) else float("inf")


def scores(oof: pd.DataFrame) -> np.ndarray:
    """Score conformal normalizado |y − ŷ| / σ̂."""
    return (np.abs(oof["y"] - oof["pred"]) / oof["sigma"]).to_numpy()


def cobertura(evaluadas: pd.DataFrame, calibracion: np.ndarray, nivel: float) -> dict:
    """Cobertura de `evaluadas` con el cuantil de los scores de `calibracion` (otras zonas); IC de Wilson al 95 %.

    Calibrar y evaluar con LOO sobre el mismo conjunto da siempre ⌈nivel·n⌉/n por construcción (rango de cada
    score entre los demás), sea cual sea el modelo: por eso se calibra con otras zonas y se mide la transferencia.
    """
    cubre = scores(evaluadas) <= cuantil_conformal(calibracion, nivel)
    n, p, z = len(cubre), float(np.mean(cubre)), 1.96
    centro, radio = (
        (p + z * z / (2 * n)) / (1 + z * z / n),
        z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n),
    )
    return {
        "n": n,
        "nominal": nivel,
        "real": p,
        "wilson95": [centro - radio, centro + radio],
    }


def clasificar(p50: np.ndarray, inf: np.ndarray, sup: np.ndarray) -> np.ndarray:
    """«estimado» si el ancho del intervalo no pasa de `UMBRAL_ANCHO` · p50; si no, «sin_dato»."""
    return np.where(sup - inf <= UMBRAL_ANCHO * p50, "estimado", "sin_dato")


def elegir(mae: pd.DataFrame) -> str:
    """El modelo más simple, salvo que otro baje el MAE al menos un `MARGEN` en todas las variantes (filas)."""
    elegido = MODELOS[0]
    for m in MODELOS[1:]:
        if (mae[m] <= (1 - MARGEN) * mae[elegido]).all():
            elegido = m
    return elegido


def _mae(oof: pd.DataFrame) -> float:
    return float(np.mean(np.abs(oof["y"] - oof["pred"])))


def evaluar(obs: dict, pequeno: np.ndarray, b: float) -> dict:
    """Por modelo y variante de robustez: MAE en log de los pequeños (máscara `pequeno`) y su cobertura calibrada
    con los demás; y las predicciones LOO de todas las zonas en la variante principal.

    Sin variante de semilla: el LOO no tiene azar y LightGBM sin submuestreo es determinista.
    """
    filas, principal = [], {}
    for k in (K, 8):
        for f in (0.5, 1.0, 2.0):
            conf = {"k": k, "b": b * f, "semilla": SEMILLA}
            todas = np.arange(len(obs["y"]))
            oofs = {m: validar_loo(obs, todas, conf | {"modelo": m}) for m in MODELOS}
            fila = conf.copy()
            for m, o in oofs.items():
                fila[m] = _mae(o[pequeno])
                cal = scores(o[~pequeno])
                fila[f"cob_{m}"] = cobertura(o[pequeno], cal, NIVEL)["real"]
            filas.append(fila)
            if (k, f) == (K, 1.0):
                principal = oofs
    return {"mae": pd.DataFrame(filas), "oof": principal}


def _por_tramo(oof: pd.DataFrame, pob: np.ndarray, cal: np.ndarray) -> dict:
    """MAE, media del residuo y cobertura por tramo de población (las objetivo son mucho más pequeñas)."""
    tramo = np.where(pob < 1000, "<1000", ">=1000")
    return {
        t: {
            "mae": _mae(g),
            "media_residuo": float((g["y"] - g["pred"]).mean()),
            "cobertura": cobertura(g, cal, NIVEL),
        }
        for t, g in oof.groupby(tramo)
    }


def _aplicable(
    pred: pd.DataFrame, train_x: pd.DataFrame, modelo: str, dist_max: float
) -> np.ndarray:
    """Área de aplicabilidad: distancia al dato ≤ la máxima validada y, si el modelo usa variables, todas en rango."""
    ok = pred["dist_dato"].to_numpy() <= dist_max
    if modelo != "wy":
        x = pred[VARIABLES]
        en_rango = x.notna() & x.ge(train_x.min()) & x.le(train_x.max())
        ok &= en_rango.all(axis=1).to_numpy()
    return ok


def _preparar(
    zona: pd.DataFrame, zonas: gpd.GeoDataFrame, x: pd.DataFrame
) -> tuple[dict, list[str], np.ndarray]:
    """Observadas de `ANIO` (`ids`, `x`, `y` en log, `d`, `xy`), ids objetivo y distancias objetivo × observadas."""
    z = zona[zona["zona_id"] != MADRID]
    nunca = z.groupby("zona_id")["eur_m2_p50"].apply(lambda s: s.isna().all())
    con = z[(z["anio"] == ANIO) & z["eur_m2_p50"].notna()]
    y = con.set_index("zona_id")["eur_m2_p50"]
    xy = coordenadas(zonas)
    objetivo = sorted(nunca.index[nunca])
    xy_obs = xy.loc[y.index].to_numpy()
    obs = {
        "ids": list(y.index),
        "x": x.loc[y.index],
        "y": np.log(y.to_numpy(float)),
        "d": distancias(xy_obs, xy_obs),
        "xy": xy_obs,
    }
    return obs, objetivo, distancias(xy.loc[objetivo].to_numpy(), xy_obs)


def _validacion(obs: dict, pob: pd.Series, pob_max: float, d_obj: np.ndarray) -> dict:
    """Buffer, validación, elección y cobertura: todo lo que va al informe."""
    b, ks = elegir_buffer(obs["d"], d_obj)
    inf = {"b_m": b, "ks": ks, "semilla": SEMILLA, "k": K, "nivel": NIVEL}
    if ks > KS_MAX:
        motivo = f"KS {ks:.3f} > {KS_MAX}: la validación no imita la tarea"
        return inf | {"imputar": False, "motivo": motivo}
    pob_obs = pob.loc[obs["ids"]].to_numpy()
    pequeno = pob_obs <= pob_max
    if min(pequeno.sum(), (~pequeno).sum()) < MIN_PEQUENOS:
        motivo = f"solo {pequeno.sum()} zonas con dato tan pequeñas como las objetivo y {(~pequeno).sum()} mayores"
        return inf | {"imputar": False, "motivo": motivo}
    ev = evaluar(obs, pequeno, b)
    modelo = elegir(ev["mae"])
    oof = ev["oof"][modelo][pequeno]
    cal = scores(ev["oof"][modelo][~pequeno])
    conf = {"k": K, "b": 0.0, "semilla": SEMILLA, "modelo": modelo}
    aleatorio = validar_loo(obs, np.flatnonzero(pequeno), conf)
    cob = cobertura(oof, cal, NIVEL)
    residuo = (oof["y"] - oof["pred"]).to_numpy()
    inf |= {
        "n_pequenos": int(pequeno.sum()),
        "n_calibracion_cobertura": len(cal),
        "pob_max_objetivo": pob_max,
        "modelo": modelo,
        "mae_variantes": ev["mae"].to_dict("records"),
        "mae_aleatorio": _mae(aleatorio),
        "mae_bloques": _mae(oof),
        "cobertura": cob,
        "por_tramo": _por_tramo(oof, pob_obs[oof["i"]], cal),
        "moran_residuos_k5": bono.moran(residuo, obs["xy"][oof["i"]], K),
        "coeficientes_mco": coeficientes_mco(obs, b),
        "dist_max_validada_m": float(oof["dist_dato"].max()),
        "scores": scores(oof).tolist(),
    }
    if cob["real"] < NIVEL - CORTE:
        motivo = f"cobertura {cob['real']:.3f} < {NIVEL - CORTE:.2f}"
        return inf | {"imputar": False, "motivo": motivo}
    return inf | {"imputar": True}


def imputar(
    zona: pd.DataFrame, rentas: pd.DataFrame, zonas: gpd.GeoDataFrame, tiempos: dict
) -> pd.DataFrame:
    """`alquiler_zona` con las filas de `ANIO` de las zonas sin dato estimadas cuando cumplen las reglas del módulo.

    El informe de la validación y de cada zona objetivo queda en `attrs["imputacion"]`.
    """
    x = variables(zonas, rentas, tiempos)
    obs, objetivo, d_obj = _preparar(zona, zonas, x)
    out = zona.copy()
    if not objetivo:
        out.attrs["imputacion"] = {"imputar": False, "motivo": "sin zonas objetivo"}
        return out
    pob = zonas.set_index("zona_id")["poblacion"]
    inf = _validacion(obs, pob, float(pob.loc[objetivo].max()), d_obj)
    out.attrs["imputacion"] = inf
    if not inf["imputar"]:
        LOG.warning("No se imputa: %s", inf["motivo"])
        return out
    conf = {"modelo": inf["modelo"], "k": K, "b": inf["b_m"], "b_test": 0.0}
    p = predecir(obs, x.loc[objetivo], d_obj, conf | {"semilla": SEMILLA})
    q = cuantil_conformal(np.array(inf["scores"]), NIVEL)
    est = pd.DataFrame(
        {
            "zona_id": objetivo,
            "p50": np.exp(p["pred"]),
            "inf": np.exp(p["pred"] - q * p["sigma"]),
            "sup": np.exp(p["pred"] + q * p["sigma"]),
            "aplicable": _aplicable(
                p, obs["x"], inf["modelo"], inf["dist_max_validada_m"]
            ),
        }
    )
    est["origen"] = np.where(
        est["aplicable"], clasificar(est["p50"], est["inf"], est["sup"]), "sin_dato"
    )
    inf["objetivo"] = est.to_dict("records")
    return _escribir(out, est[est["origen"] == "estimado"].set_index("zona_id"))


def _escribir(zona: pd.DataFrame, est: pd.DataFrame) -> pd.DataFrame:
    """Rellena las filas de `ANIO` de `est`; p25 y p75 con la mediana de los cocientes observados de `ANIO`."""
    obs = zona[
        (zona["anio"] == ANIO)
        & zona["eur_m2_p50"].notna()
        & (zona["zona_id"] != MADRID)
    ]
    r25 = float((obs["eur_m2_p25"] / obs["eur_m2_p50"]).median())
    r75 = float((obs["eur_m2_p75"] / obs["eur_m2_p50"]).median())
    filas = (zona["anio"] == ANIO) & zona["zona_id"].isin(est.index)
    ids = zona.loc[filas, "zona_id"]
    p50 = ids.map(est["p50"]).to_numpy(float)
    zona.loc[filas, "eur_m2_p50"] = p50
    zona.loc[filas, "eur_m2_p25"] = p50 * r25
    zona.loc[filas, "eur_m2_p75"] = p50 * r75
    zona.loc[filas, "ic_inf"] = ids.map(est["inf"]).to_numpy(float)
    zona.loc[filas, "ic_sup"] = ids.map(est["sup"]).to_numpy(float)
    zona.loc[filas, "origen"] = "estimado"
    contratos.validar(zona, "alquiler_zona")
    return zona


def leer_entradas() -> tuple[pd.DataFrame, gpd.GeoDataFrame, dict]:
    """Renta del ADRH, `zonas.geojson` y `tiempos.json` de `app/datos/`."""
    tiempos = json.loads((APP_DATOS / "tiempos.json").read_text(encoding="utf-8"))
    return renta.renta(), gpd.read_file(APP_DATOS / "zonas.geojson"), tiempos


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    zona = imputar(alquiler.alquiler_zona(alquiler.leer_serpavi()), *leer_entradas())
    inf = zona.attrs["imputacion"]
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(inf, indent=1, ensure_ascii=False, default=float)
    SALIDA.write_text(texto, encoding="utf-8")
    LOG.info(
        "Validación de la imputación en %s: %s", SALIDA, inf.get("motivo", "imputa")
    )


if __name__ == "__main__":
    main()
