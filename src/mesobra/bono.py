"""Bono Alquiler Joven 2022 (Comunidad de Madrid) frente a la necesidad joven por municipio.

Cruza solicitudes, aceptadas y rechazadas del Bono con la población de 18 a 35 años (INE, 1-1-2023) y
con la necesidad (esfuerzo de alquiler del municipio). Produce la tabla `bono` (contrato en `contratos.py`)
y una validación estadística. Fuentes: Bono (portal de datos abiertos de la Comunidad de Madrid, ficha del
2026-02-03), INE (población por edad simple), SERPAVI y ADRH (esfuerzo, `esfuerzo.py`).

Especificación principal, fijada antes de ver el resultado real: Pearson parcial, y = rechazadas por 1.000
jóvenes, x = esfuerzo de 2023, controles = renta neta media por hogar del ADRH 2023 + tope de alquiler
(600/900 €), sin ponderar. Todo lo demás es robustez y se informa entero, coincida o no: Spearman parcial,
renta del catálogo regional, esfuerzo y renta de 2022, solicitudes por 1.000 y tasa de aceptación como y,
I de Moran de los residuos (k = 5 y k = 8) y la exclusión de Madrid. La conclusión se apoya solo en la principal.

Supuestos:
- Año 2023 (ejercicio IRPF 2023): unos 10,5 de los 14 meses del plazo y 24 de los 31,8 M€ caen en 2023,
  igual que la población a 1-1-2023. El 2022 queda como robustez.
- `necesidad` = esfuerzo × población joven (volumen), pero los terciles y la correlación usan el esfuerzo
  (necesidad por joven) frente a aceptadas o rechazadas por 1.000 jóvenes; si no, «necesidad alta» sería
  casi «municipio grande».
- Municipio sin esfuerzo: `necesidad` nula y `grupo = "sin_dato"`, fuera de terciles y correlación; nunca cero.
  Terciles de necesidad y de ayuda sobre el mismo conjunto (los municipios con esfuerzo). Umbrales de cuantil
  (`<= q1/3` baja, `> q2/3` alta): los empates caen en el grupo inferior.
- `aceptadas` son las del dataset en su fecha (2026-02-03), sin las bajas de la fase de pago.
- Los rechazos mezclan no cumplir requisitos y crédito agotado (Orden de 6-11-2023), sin recuento por motivo
  (`docs/verificaciones/renta-vivienda.md`, 1c y 1d): no se leen como una sola causa. La métrica principal de
  ayuda es aceptadas por 1.000 jóvenes.
- La fila «Otro» (3.352 solicitudes sin contrato de un inmueble concreto, ninguna aceptada) se informa aparte
  y no se reparte; sin ella la tasa de aceptación es del 23,7 %.
- Tope de alquiler: 600 € o 900 € en los 29 municipios de `TOPE_900` (BOCM-20220920-16; el Anexo II no está
  leído). Es un parámetro normativo que sirve de control, no prueba que el rechazo se deba a él. El de
  habitación (300/450 €) no se distingue porque el dataset no separa.
- Autocorrelación: I de Moran de los residuos con W de k vecinos más cercanos entre centroides (la W reina
  deja islas al quitar municipios sin esfuerzo), normalizada por filas, p por permutaciones. Si sale
  significativo, el n efectivo es menor que n y el IC es optimista.
Sin modelar, se declaran: la solicitud cuenta en el municipio del piso, no en el de residencia; cuenta
solicitudes, no personas; el denominador son todos los jóvenes, no los inquilinos ni quienes cumplen requisitos
(tenencia, renta ≤ 3 × IPREM); «fuente regular de ingresos»; concesión por orden de llegada hasta agotar el
crédito (influye el momento de solicitar); el SERPAVI recoge el parque de contratos y va por detrás del
mercado; falacia ecológica; Madrid entra como un solo municipio; el SERPAVI es solo vivienda colectiva, así
que los municipios sin esfuerzo son pequeños o rurales y el resultado habla de los urbanos; la renta de los
municipios de menos de 100 residentes es la común de su comarca (ADRH); las tasas de municipios pequeños son
ruidosas (cubre en parte el Spearman); correlación, no causalidad; varias pruebas de robustez.
"""

import io
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from mesobra import contratos, zonas

LOG = logging.getLogger(__name__)
RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data/raw"
PROCESSED = RAIZ / "data/processed"
BONO = RAW / "cm_bono_alquiler_joven_2022_2026-11-15.csv"
CENSO = RAW / "ine_censo_poblacion_edad_municipios_2026-11-15.csv"
POBLACION_CM = RAW / "cm_poblacion_edad_nacionalidad_sexo_2026-11-15.csv"
IRPF_CM = RAW / "cm_irpf_indicador_renta_2026-11-15.csv"
ANIO = 2023
EDADES = (18, 35)
TOTALES = (51735, 11477, 3352)  # solicitudes, aceptadas y solicitudes «Otro»
INDICADORES = ("esfuerzo", "sobrecarga")
Y = ("rechazadas_por_mil", "solicitudes_por_mil", "tasa_aceptacion")
PERMUTACIONES = 999
SEMILLA = 2026
MADRID = "28079"
# Municipios con tope de 900 € (vivienda) en el Bono 2022: extracto BOCM-20220920-16, apartado primero, y
# sede A235 (https://sede.comunidad.madrid/ayudas-becas-subvenciones/bono-alquiler-joven). Código INE: nombre del CSV.
TOPE_900 = {
    "28005": "Alcalá de Henares",
    "28006": "Alcobendas",
    "28007": "Alcorcón",
    "28009": "Algete",
    "28015": "Arroyomolinos",
    "28022": "Boadilla del Monte",
    "28047": "Collado Villalba",
    "28049": "Coslada",
    "28058": "Fuenlabrada",
    "28061": "Galapagar",
    "28065": "Getafe",
    "28074": "Leganés",
    "28079": "Madrid",
    "28080": "Majadahonda",
    "28092": "Móstoles",
    "28106": "Parla",
    "28113": "Pinto",
    "28115": "Pozuelo de Alarcón",
    "28123": "Rivas-Vaciamadrid",
    "28127": "Rozas de Madrid, Las",
    "28130": "San Fernando de Henares",
    "28134": "San Sebastián de los Reyes",
    "28148": "Torrejón de Ardoz",
    "28152": "Torrelodones",
    "28161": "Valdemoro",
    "28176": "Villanueva de la Cañada",
    "28177": "Villanueva del Pardillo",
    "28181": "Villaviciosa de Odón",
    "28903": "Tres Cantos",
}


def leer_bono(ruta: Path = BONO) -> pd.DataFrame:
    """Solicitudes del Bono por municipio; `municipio_id` es nulo en la fila «Otro»."""
    df = pd.read_csv(ruta, sep=";", encoding="latin-1", dtype={"municipio": str})
    df["municipio_id"] = ("28" + df["municipio"]).where(df["municipio"] != "-")
    cuadra = df["aceptadas"] + df["rechazadas"] == df["solicitudes"]
    if not cuadra.all():
        raise ValueError(f"aceptadas + rechazadas != solicitudes:\n{df[~cuadra]}")
    return df.drop(columns="municipio")


def _edades(ruta: Path = CENSO, anio: int = ANIO) -> pd.DataFrame:
    """Personas por municipio de Madrid y edad simple (Total sexos) en el año `anio`."""
    # el CSV pesa 854 MB: solo se parsean las líneas de la provincia de Madrid
    with open(ruta, encoding="utf-8-sig") as f:
        madrid = "".join(
            linea for linea in f if linea.startswith("Total Nacional;28 Madrid;28")
        )
    columnas = ["pais", "provincia", "municipio", "sexo", "edad", "periodo", "personas"]
    df = pd.read_csv(io.StringIO(madrid), sep=";", names=columnas, dtype=str)
    df = df[(df["sexo"] == "Total") & (df["periodo"] == str(anio))]
    df = df[df["edad"].str.fullmatch(r"\d+ años?")]
    return pd.DataFrame(
        {
            "municipio_id": df["municipio"].str[:5],
            "nombre": df["municipio"].str[6:],
            "edad": df["edad"].str.extract(r"(\d+)", expand=False).astype(int),
            "personas": df["personas"].str.replace(".", "", regex=False).astype(int),
        }
    )


def poblacion_joven(edades: pd.DataFrame) -> pd.Series:
    """Personas de 18 a 35 años (ambos incluidos) por municipio."""
    joven = edades[edades["edad"].between(*EDADES)]
    return joven.groupby("municipio_id")["personas"].sum().rename("poblacion_joven")


def _catalogo_20_34(ruta: Path, anio: int) -> pd.Series:
    cm = pd.read_csv(ruta, sep=";", encoding="utf-8-sig", dtype=str)
    rangos = ["De 20-24 años", "De 25-29 años", "De 30-34 años"]
    cm = cm[
        (cm["Tipo territorio"] == "Municipios")
        & (cm["Año"] == str(anio))
        & (cm["Nacionalidad"] == "Total")
        & (cm["Sexo"] == "Total")
        & cm["Edad"].isin(rangos)
    ]
    return (
        cm.assign(
            municipio_id="28" + cm["Código territorio"].str[:3],
            Valor=cm["Valor"].astype(int),
        )
        .groupby("municipio_id")["Valor"]
        .sum()
    )


def _comparar_catalogo(
    edades: pd.DataFrame, ruta: Path = POBLACION_CM, anio: int = ANIO
) -> None:
    """La suma INE de 20 a 34 años debe ser igual a la del catálogo regional, municipio a municipio."""
    ine = (
        edades[edades["edad"].between(20, 34)].groupby("municipio_id")["personas"].sum()
    )
    cm = _catalogo_20_34(ruta, anio)
    distintos = pd.concat([ine, cm], axis=1, keys=["ine", "cm"]).query(
        "ine != cm or ine.isna() or cm.isna()"
    )
    if not distintos.empty:
        raise ValueError(
            f"{len(distintos)} municipios con 20-34 años distintos del catálogo:\n{distintos.head()}"
        )


def por_mil(tabla: pd.DataFrame) -> pd.DataFrame:
    """Solicitudes, aceptadas y rechazadas por 1.000 jóvenes y tasa de aceptación."""
    jovenes = tabla["poblacion_joven"]
    salida = {
        f"{c}_por_mil": tabla[c] / jovenes * 1000
        for c in ("solicitudes", "aceptadas", "rechazadas")
    }
    salida["tasa_aceptacion"] = tabla["aceptadas"] / tabla["solicitudes"]
    return pd.DataFrame(salida, index=tabla.index)


def terciles(serie: pd.Series) -> pd.Series:
    """«baja» (<= q1/3), «alta» (> q2/3) o «media»; el nulo sigue nulo y los empates caen abajo."""
    q1, q2 = serie.quantile([1 / 3, 2 / 3])
    grupo = pd.Series(
        np.select([serie <= q1, serie > q2], ["baja", "alta"], "media"),
        index=serie.index,
    )
    return grupo.where(serie.notna())


def tope_eur(ids: pd.Index) -> pd.Series:
    """Alquiler máximo de vivienda del Bono 2022: 900 € en los municipios de `TOPE_900`, 600 € en el resto."""
    return pd.Series(
        np.where(ids.isin(list(TOPE_900)), 900.0, 600.0), index=ids, name="tope"
    )


def bono(
    solicitudes: pd.DataFrame, poblacion: pd.Series, indicador: pd.Series
) -> pd.DataFrame:
    """Tabla `bono`. `indicador` es una Series por municipio cuyo `name` es `esfuerzo` o `sobrecarga`."""
    if indicador.name not in INDICADORES:
        raise ValueError(
            f"El indicador debe llamarse {INDICADORES}, no {indicador.name!r}"
        )
    df = solicitudes.dropna(subset=["municipio_id"]).reset_index(drop=True)
    if faltan := sorted(set(df["municipio_id"]) - set(poblacion.index)):
        raise ValueError(f"Municipios del Bono sin población: {faltan}")
    df["poblacion_joven"] = df["municipio_id"].map(poblacion)
    if (df["poblacion_joven"] <= 0).any():
        raise ValueError("Municipio con población joven nula")
    por_joven = df["municipio_id"].map(indicador).astype(float)
    df["necesidad"] = por_joven * df["poblacion_joven"]
    df["indicador_necesidad"] = indicador.name
    aceptadas = por_mil(df)["aceptadas_por_mil"].where(por_joven.notna())
    grupo = "necesidad_" + terciles(por_joven) + "_ayuda_" + terciles(aceptadas)
    df["grupo"] = grupo.fillna("sin_dato")
    columnas = list(contratos.CONTRATOS["bono"]["columnas"])
    df = df[columnas].astype(contratos.dtypes("bono"))
    contratos.validar(df, "bono")
    return df


def _residuos(y: pd.Series, x: pd.DataFrame) -> np.ndarray:
    z = np.column_stack([np.ones(len(x)), x.to_numpy(float)])
    return y.to_numpy(float) - z @ np.linalg.lstsq(z, y.to_numpy(float), rcond=None)[0]


def correlacion_parcial(x: pd.Series, y: pd.Series, controles: pd.DataFrame) -> dict:
    """Pearson parcial de x e y controlando por `controles`: r, n, k, ic95 (Fisher) y p (t de n-2-k gl)."""
    d = pd.concat([x.rename("x"), y.rename("y"), controles], axis=1).dropna()
    n, k = len(d), controles.shape[1]
    if n - 3 - k < 2:
        raise ValueError(f"Faltan datos: n = {n} con {k} controles")
    c = d[list(controles.columns)]
    r = float(np.corrcoef(_residuos(d["x"], c), _residuos(d["y"], c))[0, 1])
    r = min(max(r, -1.0), 1.0)
    with np.errstate(divide="ignore"):
        z, se = np.arctanh(r), 1 / np.sqrt(n - 3 - k)
        t = r * np.sqrt((n - 2 - k) / (1 - r**2))
    return {
        "r": r,
        "n": n,
        "k": k,
        "ic95": (float(np.tanh(z - 1.96 * se)), float(np.tanh(z + 1.96 * se))),
        "p": float(2 * stats.t.sf(abs(t), n - 2 - k)),
    }


def _vecinos(xy: np.ndarray, k: int) -> np.ndarray:
    """Índices de los k vecinos más cercanos de cada punto (euclídea, sin él mismo)."""
    if len(xy) <= k:
        raise ValueError(f"Con {len(xy)} puntos no hay {k} vecinos")
    dist = np.linalg.norm(xy[:, None, :] - xy[None, :, :], axis=2)
    np.fill_diagonal(dist, np.inf)
    return np.argsort(dist, axis=1, kind="stable")[:, :k]


def moran(valores: np.ndarray, xy: np.ndarray, k: int) -> dict:
    """I de Moran con W de k vecinos normalizada por filas; p pseudo-bilateral por permutaciones."""
    vecinos = _vecinos(xy, k)
    z = np.asarray(valores, float) - np.mean(valores)

    # W normalizada por filas: S0 = n, así que I = z'Wz / z'z (permutar no cambia z'z)
    def indice(zz: np.ndarray) -> np.ndarray:
        return (zz * zz[..., vecinos].mean(axis=-1)).sum(axis=-1) / (z @ z)

    n = len(z)
    esperado = -1 / (n - 1)
    perm = z[
        np.argsort(np.random.default_rng(SEMILLA).random((PERMUTACIONES, n)), axis=1)
    ]
    obs = float(indice(z))
    mayor = (np.abs(indice(perm) - esperado) >= abs(obs - esperado)).sum()
    return {
        "I": obs,
        "esperado": esperado,
        "p": float((1 + mayor) / (PERMUTACIONES + 1)),
    }


def validacion(tabla: pd.DataFrame, renta: pd.Series, xy: pd.DataFrame) -> dict:
    """Por cada y de `Y`: Pearson y Spearman parcial (controles renta y tope) y Moran k = 5 y 8 de los residuos.

    `tabla` es la tabla `bono`; `renta` y `xy` (columnas x, y; EPSG:25830) van por `municipio_id`.
    """
    t = tabla.set_index("municipio_id")
    controles = pd.DataFrame(
        {"renta": renta.reindex(t.index), "tope": tope_eur(t.index)}
    )
    base = pd.concat(
        [(t["necesidad"] / t["poblacion_joven"]).rename("x"), por_mil(t), controles],
        axis=1,
    )
    salida = {}
    for y in Y:
        d = base[["x", y, "renta", "tope"]].dropna()
        res = {
            nombre: correlacion_parcial(datos["x"], datos[y], datos[["renta", "tope"]])
            for nombre, datos in (("pearson", d), ("spearman", d.rank()))
        }
        residuos = _residuos(d[y], d[["x", "renta", "tope"]])
        for k in (5, 8):
            res[f"moran_k{k}"] = moran(residuos, xy.loc[d.index].to_numpy(float), k)
        salida[y] = res
    return salida


def _municipios_xy() -> pd.DataFrame:
    """Centroide (EPSG:25830) de cada municipio, disolviendo las secciones por `CUMUN`."""
    centro = zonas.leer_secciones().dissolve("CUMUN").centroid
    return pd.DataFrame({"x": centro.x, "y": centro.y})


def _renta_catalogo(ruta: Path = IRPF_CM, anio: int = ANIO) -> pd.Series:
    """Renta bruta per cápita del catálogo regional por municipio (control alternativo)."""
    cm = pd.read_csv(ruta, sep=";", encoding="utf-8-sig", dtype=str)
    cm = cm[
        (cm["Tipo territorio"] == "Municipios")
        & (cm["Medida"] == "Per cápita")
        & (cm["Año"] == str(anio))
    ]
    cm = cm[cm["Valor"] != "-"]
    return pd.Series(
        cm["Valor"].astype(float).to_numpy(),
        index="28" + cm["Código territorio"].str[:3],
    )


def _norma(nombre: pd.Series) -> pd.Series:
    return nombre.str.strip().str.casefold()


def _comprobar_nombres(solicitudes: pd.DataFrame, edades: pd.DataFrame) -> None:
    """El código del Bono debe llevar al mismo nombre en el INE: detecta códigos mal puestos."""
    ine = edades.drop_duplicates("municipio_id").set_index("municipio_id")["nombre"]
    df = solicitudes.dropna(subset=["municipio_id"])
    distintos = df[
        _norma(df["municipio_id"].map(ine)) != _norma(df["municipio_nombre"])
    ]
    if not distintos.empty:
        raise ValueError(
            f"Código y nombre no coinciden entre el Bono y el INE:\n{distintos}"
        )


def _informe(etiqueta: str, res: dict) -> None:
    for y, r in res.items():
        p, s = r["pearson"], r["spearman"]
        LOG.info(
            "%s | %s | Pearson r=%.3f n=%d k=%d IC95=[%.3f, %.3f] p=%.4f | Spearman r=%.3f p=%.4f | Moran k5 I=%.3f p=%.3f, k8 I=%.3f p=%.3f",
            etiqueta, y, p["r"], p["n"], p["k"], *p["ic95"], p["p"], s["r"], s["p"],
            r["moran_k5"]["I"], r["moran_k5"]["p"], r["moran_k8"]["I"], r["moran_k8"]["p"],
        )  # fmt: skip


def _por_anio(
    solicitudes: pd.DataFrame, poblacion: pd.Series, esfuerzo: pd.DataFrame, anio: int
) -> pd.DataFrame:
    por_zona = esfuerzo[esfuerzo["anio"] == anio].set_index("zona_id")["esfuerzo"]
    return bono(solicitudes, poblacion, por_zona)


def _renta_adrh(renta: pd.DataFrame, anio: int) -> pd.Series:
    r = renta[
        (renta["nivel"] == "zona")
        & (renta["anio"] == anio)
        & (renta["unidad_id"].str.len() == 5)
    ]
    return r.set_index("unidad_id")["renta_hogar"]


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    solicitudes = leer_bono()
    otro = solicitudes[solicitudes["municipio_id"].isna()]
    sumas = (solicitudes["solicitudes"], solicitudes["aceptadas"], otro["solicitudes"])
    totales = tuple(int(c.sum()) for c in sumas)
    if totales != TOTALES or otro["aceptadas"].sum() != 0:
        raise ValueError(
            f"Totales {totales} distintos de {TOTALES} (solicitudes, aceptadas, «Otro»)"
        )
    edades = _edades()
    _comparar_catalogo(edades)
    _comprobar_nombres(solicitudes, edades)
    poblacion = poblacion_joven(edades)
    esfuerzo = pd.read_parquet(PROCESSED / "esfuerzo.parquet")
    renta = pd.read_parquet(PROCESSED / "renta.parquet")
    tabla = _por_anio(solicitudes, poblacion, esfuerzo, ANIO)
    if len(tabla) != 159:
        raise ValueError(f"Se esperaban 159 municipios y hay {len(tabla)}")
    tasa = tabla["aceptadas"].sum() / (tabla["solicitudes"].sum())
    mil = por_mil(tabla)
    con = tabla["grupo"] != "sin_dato"
    LOG.info(
        "Municipios cruzados: %d; con necesidad: %d; sin dato: %d",
        len(tabla),
        con.sum(),
        (~con).sum(),
    )
    LOG.info(
        "Totales (solicitudes, aceptadas, Otro): %s; tasa de aceptación sin «Otro»: %.1f %%",
        totales,
        100 * tasa,
    )
    madrid = tabla[tabla["municipio_id"] == MADRID].iloc[0]
    LOG.info("Madrid: población joven %d, esfuerzo %d: %.4f", madrid["poblacion_joven"], ANIO,
             madrid["necesidad"] / madrid["poblacion_joven"])  # fmt: skip
    mayor = mil["solicitudes_por_mil"].idxmax()
    LOG.info("Máximo de solicitudes por 1.000 jóvenes: %.1f en %s", mil.loc[mayor, "solicitudes_por_mil"],
             solicitudes.dropna(subset=["municipio_id"]).set_index("municipio_id").loc[tabla.loc[mayor, "municipio_id"], "municipio_nombre"])  # fmt: skip
    LOG.info(
        "Medianas con esfuerzo / sin esfuerzo:\n%s",
        mil.groupby(con.to_numpy()).median().to_string(),
    )
    LOG.info("Municipios por grupo:\n%s", tabla["grupo"].value_counts().to_string())
    t22 = _por_anio(solicitudes, poblacion, esfuerzo, 2022)
    ambos = (tabla["grupo"] != "sin_dato") & (t22["grupo"] != "sin_dato")
    LOG.info(
        "Cambian de grupo 2022 -> 2023: %d de %d",
        (tabla["grupo"] != t22["grupo"])[ambos].sum(),
        ambos.sum(),
    )
    xy = _municipios_xy()
    renta23, cat = _renta_adrh(renta, ANIO), _renta_catalogo()
    sin_madrid = tabla["municipio_id"] != MADRID
    _informe(
        "PRINCIPAL (esfuerzo 2023, renta ADRH 2023)", validacion(tabla, renta23, xy)
    )
    _informe("Renta del catálogo 2023", validacion(tabla, cat, xy))
    _informe("Esfuerzo y renta 2022", validacion(t22, _renta_adrh(renta, 2022), xy))
    _informe("Sin Madrid", validacion(tabla[sin_madrid], renta23, xy))
    PROCESSED.mkdir(parents=True, exist_ok=True)
    tabla.to_parquet(PROCESSED / "bono.parquet")


if __name__ == "__main__":
    main()
