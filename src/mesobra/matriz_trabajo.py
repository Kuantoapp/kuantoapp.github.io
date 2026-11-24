"""Dónde trabajan los residentes de cada municipio de la Comunidad de Madrid (#301).

Fuente: INE, Censo anual de población (ocupación y actividad) 2021-2023, «Matriz de municipio de residencia por
municipio de trabajo» (`matriz_ocu_anonim.xlsb`, publicada el 02-12-2025, CC BY 4.0). Elaboración propia con datos
extraídos del sitio web del INE: www.ine.es. Se usa la hoja `C23` (ocupados de 2023), la más reciente.

Formato: una hoja por año (`C21`, `C22`, `C23`), en largo. La fila 0 agrupa «Lugar de residencia» y «Lugar de
trabajo»; la 1 trae las columnas de `COLUMNAS`; después, una fila por par (residencia, trabajo) con los «Ocupados de
16 y más años». El mínimo publicado es 5: probable supresión de las celdas menores (el fichero se llama «anonim»;
el INE no lo dice en lo leído), así que un par que falta no es un cero. «No consta» como municipio, o como provincia,
de trabajo es lugar desconocido, no un destino.

En la Comunidad de Madrid, 2023, leído del fichero original el 19-11-2026: 179 municipios de residencia, 3.067.380
ocupados, el 94,19 % trabaja en la provincia y el 9,47 % tiene municipio de trabajo «No consta». El INE obtiene los
ocupados sobre todo de la afiliación a la Seguridad Social (el 94,2 % de los del censo, metodología del Censo anual,
abril de 2026): el lugar de trabajo puede ser la sede de la empresa y no el centro real (sin comprobar).
"""

import json
import logging
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

from mesobra import calculo

LOG = logging.getLogger(__name__)
RAW = (
    calculo.RAIZ / "data/raw/ine_censo_anual_matriz_residencia_trabajo_2026-11-19.xlsb"
)
PROCESSED = calculo.RAIZ / "data/processed/matriz_trabajo_2023.csv"
DISTRITOS = calculo.RAIZ / "data/raw/cm_colectivo_empresarial_distrito_2026-11-19.csv"
ZONAS = calculo.RAIZ / "app/datos/zonas.geojson"
AFILIACION = (
    calculo.RAIZ / "data/raw/cm_afiliados_centro_trabajo_regimen_2026-11-24.csv"
)
AFILIACION_CUENTA = (
    calculo.RAIZ / "data/raw/cm_afiliados_cuenta_cotizacion_municipio_2026-11-24.csv"
)
EDM_INDIVIDUOS = calculo.RAIZ / "data/raw/crtm_edm2018_individuos_2026-11-24.xlsx"
EDM_HOGARES = calculo.RAIZ / "data/raw/crtm_edm2018_hogares_2026-11-24.xlsx"
DISTRITOS_MADRID = 21
# errata del fichero de cuentas de cotización (leído el 2026-11-24) frente al nombre oficial, ya pasada por `_clave`
ERRATAS_CUENTA = {"readuena": "reduena"}
MUNICIPIO_MADRID = "28079"
HOJA = "C23"
MADRID = "28"
MUNICIPIOS = 179  # municipios de la Comunidad de Madrid
COLUMNAS = [
    "Provincia de residencia",
    "Nombre",
    "Municipio de residencia",
    "Nombre.1",
    "Provincia de trabajo",
    "Nombre.2",
    "Municipio de trabajo",
    "Nombre.3",
    "Ocupados de 16 y más años",
]


def ordenar(hoja: pd.DataFrame) -> pd.DataFrame:
    """Pares con origen en la Comunidad: `origen` y `destino` (código INE de 5 cifras, nulo si no consta),
    `prov_destino` (2 cifras, nula si no consta) y `ocupados`. Falla si cambia el formato."""
    if faltan := [c for c in COLUMNAS if c not in hoja.columns]:
        raise ValueError(f"la matriz del INE no trae las columnas {faltan}")
    m = hoja[hoja["Provincia de residencia"] == MADRID]
    ocupados = pd.to_numeric(m["Ocupados de 16 y más años"], errors="coerce")
    if ocupados.isna().any() or (ocupados < 0).any() or (ocupados % 1 != 0).any():
        raise ValueError(
            "ocupados no enteros, no numéricos o negativos en la matriz del INE"
        )
    prov = m["Provincia de trabajo"].where(
        m["Provincia de trabajo"].str.fullmatch(r"\d{2}", na=False)
    )
    mun = m["Municipio de trabajo"].where(
        m["Municipio de trabajo"].str.fullmatch(r"\d{3}", na=False)
    )
    return pd.DataFrame(
        {
            "origen": m["Provincia de residencia"] + m["Municipio de residencia"],
            "prov_destino": prov,
            "destino": prov + mun,  # nulo si no consta la provincia o el municipio
            "ocupados": ocupados.astype(int),
        }
    ).reset_index(drop=True)


def _hoja(ruta: Path = RAW, hoja: str = HOJA) -> pd.DataFrame:
    return pd.read_excel(ruta, hoja, header=1, engine="calamine", dtype=str)


def leer_matriz(ruta: Path = RAW) -> pd.DataFrame:
    """Matriz de la Comunidad de `ruta`, validada: un origen por municipio de la Comunidad."""
    df = ordenar(_hoja(ruta))
    if (n := df["origen"].nunique()) != MUNICIPIOS:
        raise ValueError(
            f"la matriz trae {n} municipios de residencia de la Comunidad, no {MUNICIPIOS}"
        )
    return df


def _clave(nombre: str) -> str:
    """Nombre sin tildes, en minúsculas y sin guiones: «Fuencarral - El Pardo» = «Fuencarral-El Pardo»."""
    sin = unicodedata.normalize("NFD", nombre.lower().replace("-", " "))
    return " ".join("".join(c for c in sin if not unicodedata.combining(c)).split())


def leer_cuotas_distritos(
    ruta: Path = DISTRITOS, zonas: Path = ZONAS, año: int = 2023
) -> pd.Series:
    """Cuota de los ocupados de `año` (2023 en los pesos) de cada distrito de Madrid (`zona_id` 2807901…) en el
    Colectivo Empresarial (Total, sin «no consta distrito»). Falla si no salen los 21 distritos de `zonas`."""
    props = [f["properties"] for f in json.loads(zonas.read_text("utf-8"))["features"]]
    # shortcut: une por nombre porque el CSV no trae código de distrito; si lo trae, unir por código
    ids = {
        _clave(p["nombre"]): p["zona_id"]
        for p in props
        if p["municipio_id"] == MUNICIPIO_MADRID and p["tipo"] == "distrito"
    }
    df = pd.read_csv(ruta, sep=";", encoding="utf-8-sig", dtype=str)
    df = df[
        (df["Medida"] == "Ocupados")
        & (df["Estrato Empleo"] == "Total")
        & (df["Año"] == str(año))
    ]
    nombre = df["Concepto"].str.extract(
        r"en el distrito de (.+) del municipio de Madrid$"
    )[0]
    if nombre.isna().any():
        raise ValueError(
            "el Colectivo Empresarial trae conceptos sin distrito de Madrid"
        )
    ocupados = pd.to_numeric(df["Valor"].set_axis(nombre.map(_clave)), errors="raise")
    ocupados = ocupados.drop(_clave("las que no consta distrito"), errors="ignore")
    if sorted(ocupados.index) != sorted(ids) or ocupados.index.duplicated().any():
        raise ValueError(
            f"no salen los {len(ids)} distritos de Madrid: {sorted(ocupados.index)}"
        )
    cuotas = ocupados.rename(index=ids)
    return (cuotas / cuotas.sum()).sort_index()


def _dentro(m: pd.DataFrame) -> pd.DataFrame:
    """Filas con destino en la Comunidad y municipio conocido: la base común de `pesos` y `ocupados_observados`."""
    return m[(m["prov_destino"] == MADRID) & m["destino"].notna()]


def ocupados_observados(m: pd.DataFrame) -> pd.Series:
    """Por origen, ocupados que trabajan en la Comunidad con municipio conocido: la base de los pesos (0 si no hay)."""
    observados = _dentro(m).groupby("origen")["ocupados"].sum()
    return observados.reindex(m["origen"].unique(), fill_value=0)


def pesos(m: pd.DataFrame, cuotas: pd.Series) -> tuple[pd.DataFrame, pd.Series]:
    """(w, excluida): `w` con columnas `origen`, `destino` (código de municipio, o `zona_id` de distrito si es Madrid)
    y `w` = ocupados ÷ total de los que trabajan en la Comunidad con municipio conocido, que suma 1 por origen;
    `excluida`, por origen, la fracción de sus ocupados que queda fuera (otras provincias o «No consta»).
    Las celdas suprimidas no se imputan: no se distinguen de los ceros."""
    dentro = _dentro(m).groupby(["origen", "destino"], as_index=False)["ocupados"].sum()
    por_origen = ocupados_observados(m)
    excluida = 1 - por_origen / m.groupby("origen")["ocupados"].sum()
    dentro["w"] = dentro["ocupados"] / dentro["origen"].map(por_origen)
    madrid = dentro["destino"] == MUNICIPIO_MADRID
    reparto = dentro[madrid].merge(
        cuotas.rename("cuota").rename_axis("zona").reset_index(), how="cross"
    )
    reparto = reparto.assign(destino=reparto["zona"], w=reparto["w"] * reparto["cuota"])
    w = pd.concat([dentro[~madrid], reparto], ignore_index=True)
    return w[["origen", "destino", "w"]], excluida.rename("excluida")


def entradas(hoja: pd.DataFrame) -> pd.Series:
    """Ocupados que trabajan en cada municipio de la Comunidad (código de 5 cifras) desde todos los orígenes, también
    de otras provincias, sin «No consta»: lo comparable con la afiliación por centro de trabajo (#357)."""
    m = hoja[
        (hoja["Provincia de trabajo"] == MADRID)
        & hoja["Municipio de trabajo"].str.fullmatch(r"\d{3}", na=False)
    ]
    ocupados = pd.to_numeric(m["Ocupados de 16 y más años"], errors="raise")
    return ocupados.groupby(MADRID + m["Municipio de trabajo"]).sum().rename("ocupados")


def leer_afiliacion_centro(ruta: Path = AFILIACION, año: int = 2022) -> pd.Series:
    """Afiliados en alta a 31-12-`año` por municipio del centro de trabajo (código de 5 cifras), suma de los
    regímenes, sin «Sin municipio asignado» (9999). Falla si no salen los 179 municipios o si los municipios no
    cuadran con la fila de la Comunidad más allá del redondeo a 5 de cada celda (desde 2021)."""
    df = pd.read_csv(ruta, sep=";", encoding="utf-8-sig", dtype=str)
    df = df[df["Año"] == str(año)]
    valor = pd.to_numeric(df["Valor"], errors="raise")
    mun = df["Tipo territorio"] == "Municipios"
    por_codigo = valor[mun].groupby(df.loc[mun, "Código territorio"]).sum()
    total = valor[df["Tipo territorio"] == "Comunidad de Madrid"].sum()
    if abs(por_codigo.sum() - total) > 2.5 * mun.sum():
        raise ValueError(
            f"la afiliación de los municipios ({por_codigo.sum()}) no cuadra con la Comunidad ({total})"
        )
    afil = por_codigo.drop("9999")
    afil.index = (
        MADRID + afil.index.str[:3]
    )  # 4 cifras: municipio del INE + dígito de control
    if len(afil) != MUNICIPIOS or afil.index.duplicated().any():
        raise ValueError(f"la afiliación trae {len(afil)} municipios, no {MUNICIPIOS}")
    return afil.rename("afiliados")


def leer_afiliacion_cuenta(
    ruta: Path = AFILIACION_CUENTA, centro: Path = AFILIACION, año: int = 2022
) -> pd.Series:
    """Afiliados en alta a 31-12-`año` por municipio de la **cuenta de cotización** (código de 5 cifras), sin «No
    distribuidos». El fichero no trae código: se une por el nombre, con los códigos de la afiliación por centro de
    trabajo (`centro`, mismo publicador y misma forma de los nombres). Falla si un nombre no casa o no salen 179."""
    c = pd.read_csv(centro, sep=";", encoding="utf-8-sig", dtype=str)
    c = c[(c["Tipo territorio"] == "Municipios") & (c["Código territorio"] != "9999")]
    codigos = dict(
        zip(c["Territorio"].map(_clave), MADRID + c["Código territorio"].str[:3])
    )
    df = pd.read_csv(ruta, sep=";", encoding="utf-8-sig", dtype=str)
    df = df[
        (df["Año"] == str(año))
        & (df["Periodo"] == "M12")
        & (df["Territorio"] != "No distribuidos")
    ]
    claves = df["Territorio"].map(_clave).replace(ERRATAS_CUENTA)
    if faltan := sorted(set(claves) - set(codigos)):
        raise ValueError(f"municipios de la cuenta de cotización sin código: {faltan}")
    afil = pd.to_numeric(df["Valor"], errors="raise").set_axis(claves.map(codigos))
    if len(afil) != MUNICIPIOS or afil.index.duplicated().any():
        raise ValueError(
            f"la cuenta de cotización trae {len(afil)} municipios, no {MUNICIPIOS}"
        )
    return afil.rename("afiliados")


def leer_edm_trabajo(
    individuos: Path = EDM_INDIVIDUOS, hogares: Path = EDM_HOGARES
) -> pd.DataFrame:
    """Personas del EDM2018 (CRTM) que trabajan (`C8ACTIV` 1 o 2) con centro de trabajo (`C11ZT1259`) en Madrid:
    `hogar`, `residencia` (zona ZT1259 del hogar), `municipio` (de residencia, 5 cifras), `distrito` de trabajo
    (`zona_id` 28079DD, del código de zona `079-DD-…`), `peso` («Elevador de individuos»), `cuenta_propia` (`C9PROF`
    3 o 4) y `en_casa` (centro de trabajo en la zona del hogar). Falla si una zona de Madrid no trae distrito, falta
    alguno de los 21 o una persona no tiene hogar."""
    ind = pd.read_excel(individuos, "INDIVIDUOS", engine="calamine", dtype=str)
    hog = pd.read_excel(hogares, "HOGARES", engine="calamine", dtype=str)
    ind = ind[ind["C8ACTIV"].isin(["1", "2"])]
    ind = ind[ind["C11ZT1259"].str.startswith("079", na=False)]
    dd = ind["C11ZT1259"].str.extract(r"^079-(\d{2})-")[0]
    if dd.isna().any():
        raise ValueError(
            "zonas de trabajo de Madrid del EDM2018 sin distrito en el código"
        )
    df = ind.merge(hog[["ID_HOGAR", "CODMUNI", "ZT1259"]], on="ID_HOGAR", how="left")
    if df["ZT1259"].isna().any():
        raise ValueError("personas del EDM2018 sin hogar en la tabla HOGARES")
    out = pd.DataFrame(
        {
            "hogar": df["ID_HOGAR"],
            "residencia": df["ZT1259"],
            "municipio": MADRID + df["CODMUNI"],
            "distrito": MUNICIPIO_MADRID + dd.to_numpy(),
            "peso": pd.to_numeric(df["ELE_G_POND"], errors="raise"),
            "cuenta_propia": df["C9PROF"].isin(["3", "4"]),
            "en_casa": df["C11ZT1259"] == df["ZT1259"],
        }
    )
    if (n := out["distrito"].nunique()) != DISTRITOS_MADRID:
        raise ValueError(
            f"el EDM2018 trae {n} distritos de trabajo, no {DISTRITOS_MADRID}"
        )
    return out


def cuotas_edm(edm: pd.DataFrame) -> pd.Series:
    """Cuota de cada distrito en las personas ponderadas de `edm`."""
    por_distrito = edm.groupby("distrito")["peso"].sum()
    return por_distrito / por_distrito.sum()


def disimilitud(a: pd.Series, b: pd.Series) -> float:
    """Índice de disimilitud ½ Σ |a − b| entre dos repartos que suman 1: la parte que habría que mover."""
    if set(a.index) != set(b.index):
        raise ValueError("los dos repartos no tienen las mismas unidades")
    return float((a - b).abs().sum() / 2)


def _cuotas(s: pd.Series) -> pd.Series:
    return s / s.sum()


def no_consta_provincia(hoja: pd.DataFrame) -> int:
    """Ocupados que trabajan en la provincia de Madrid con municipio «No consta», desde todos los orígenes."""
    m = hoja[
        (hoja["Provincia de trabajo"] == MADRID)
        & ~hoja["Municipio de trabajo"].str.fullmatch(r"\d{3}", na=False)
    ]
    return int(pd.to_numeric(m["Ocupados de 16 y más años"], errors="raise").sum())


def entradas_w(m: pd.DataFrame, w: pd.DataFrame) -> pd.Series:
    """Ocupados que entran en cada municipio según los pesos: Σ_o ocupados_o · w(o, d), con los distritos de Madrid
    sumados en el municipio. Es lo que usa el modelo: el «No consta» queda repartido dentro de cada origen."""
    ocupados = m.groupby("origen")["ocupados"].sum()
    return (w["w"] * w["origen"].map(ocupados)).groupby(w["destino"].str[:5]).sum()


def comparar(a: pd.Series, b: pd.Series) -> dict:
    """D, Δ de Madrid capital (puntos) y municipios con |Δ| ≥ 0,5 puntos entre las cuotas de `a` y `b`."""
    ca, cb = _cuotas(a), _cuotas(b.reindex(a.index, fill_value=0))
    delta = 100 * (ca - cb)
    return {
        "D": round(disimilitud(ca, cb), 4),
        "delta_madrid": round(float(delta[MUNICIPIO_MADRID]), 2),
        "grandes": delta[delta.abs() >= 0.5].round(2).sort_values().to_dict(),
    }


def control_municipios() -> None:
    """Bloque A del registro previo de #357: hoja C23 frente a la afiliación a 31-12-2022."""
    hoja = _hoja()
    centro, cuenta = leer_afiliacion_centro(), leer_afiliacion_cuenta()
    ine = entradas(hoja).reindex(centro.index, fill_value=0)
    LOG.info("municipios sin entradas en la C23: %s", list(ine[ine == 0].index))
    m = leer_matriz()
    w_mun = entradas_w(m, pesos(m, leer_cuotas_distritos())[0])
    nc = ine.copy()
    nc[MUNICIPIO_MADRID] += no_consta_provincia(hoja)
    c22 = entradas(_hoja(hoja="C22")).reindex(centro.index, fill_value=0)
    filas = {
        "INE frente a centro": comparar(ine, centro),
        "INE frente a cuenta": comparar(ine, cuenta),
        "cuenta frente a centro": comparar(cuenta, centro),
        "INE (No consta a Madrid) frente a centro": comparar(nc, centro),
        "INE (No consta a Madrid) frente a cuenta": comparar(nc, cuenta),
        "w frente a centro": comparar(
            w_mun.reindex(centro.index, fill_value=0), centro
        ),
        "ruido: C22 frente a C23": comparar(c22, ine),
        "ruido: centro 2021 frente a 2022": comparar(
            leer_afiliacion_centro(año=2021), centro
        ),
    }
    for nombre, r in filas.items():
        LOG.info("%s: %s", nombre, r)
    cociente = _cuotas(ine) / _cuotas(centro)
    con = ine > 0
    LOG.info(
        "cociente total INE ÷ centro %.4f, ÷ cuenta %.4f; Spearman de niveles %.4f; "
        "Spearman log(cociente de cuotas) con log(afiliados) %.4f (n = %d)",
        ine.sum() / centro.sum(),
        ine.sum() / cuenta.sum(),
        ine.corr(centro, method="spearman"),
        np.log(cociente[con]).corr(np.log(centro[con]), method="spearman"),
        con.sum(),
    )


def _estrato(edm: pd.DataFrame) -> pd.Series:
    """Municipio de residencia; en Madrid, distrito de residencia (de la zona `079-DD-…`)."""
    madrid = edm["municipio"] == MUNICIPIO_MADRID
    return edm["municipio"].where(
        ~madrid, MUNICIPIO_MADRID + edm["residencia"].str[4:6]
    )


def _por_hogar(edm: pd.DataFrame) -> pd.DataFrame:
    """Peso de cada hogar en cada distrito de trabajo (filas: hogar; columnas: distrito)."""
    return edm.pivot_table(
        index="hogar", columns="distrito", values="peso", aggfunc="sum", fill_value=0
    )


def bootstrap_cuotas(edm: pd.DataFrame, reps: int, semilla: int = 357) -> pd.DataFrame:
    """Cuotas por distrito en `reps` réplicas, remuestreando hogares con reemplazo dentro de cada estrato
    (`_estrato`). El elevador es el de la encuesta, sin su diseño completo: el IC es aproximado."""
    h = _por_hogar(edm)
    estrato = _estrato(edm).groupby(edm["hogar"]).first().reindex(h.index)
    grupos = [np.flatnonzero(estrato.to_numpy() == e) for e in estrato.unique()]
    rng = np.random.default_rng(semilla)
    filas = []
    for _ in range(reps):
        idx = np.concatenate([rng.choice(g, len(g)) for g in grupos])
        peso = np.bincount(idx, minlength=len(h)) @ h.to_numpy()
        filas.append(peso / peso.sum())
    return pd.DataFrame(filas, columns=h.columns)


def tabla_distritos(edm: pd.DataFrame, reps: int = 1000) -> pd.DataFrame:
    """Bloque B: por distrito, cuotas del Colectivo 2023 y 2018 y del EDM2018, IC 95 % bootstrap, Δ en puntos con
    su descomposición (definición = Colectivo 2018 − EDM; deriva = Colectivo 2023 − 2018) y la marca de
    discrepancia del registro previo."""
    boot = bootstrap_cuotas(edm, reps)
    t = pd.DataFrame(
        {
            "colectivo_2023": leer_cuotas_distritos(),
            "colectivo_2018": leer_cuotas_distritos(año=2018),
            "edm": cuotas_edm(edm),
            "ic_inf": boot.quantile(0.025),
            "ic_sup": boot.quantile(0.975),
        }
    )
    t["delta"] = 100 * (t["colectivo_2023"] - t["edm"])
    t["definicion"] = 100 * (t["colectivo_2018"] - t["edm"])
    t["deriva"] = 100 * (t["colectivo_2023"] - t["colectivo_2018"])
    fuera = (t["colectivo_2023"] < t["ic_inf"]) | (t["colectivo_2023"] > t["ic_sup"])
    grande = (t["delta"].abs() > 1) | (t["delta"].abs() / (100 * t["edm"]) > 0.2)
    t["discrepa"] = fuera & grande
    return t


def control_distritos(edm: pd.DataFrame) -> None:
    """Bloque B del registro previo de #357: cuotas del Colectivo frente al EDM2018."""
    t = tabla_distritos(edm)
    LOG.info("distritos (cuotas y Δ en puntos):\n%s", t.round(4).to_string())
    LOG.info(
        "D(Colectivo 2023, EDM) %.4f; D(Colectivo 2018, EDM) %.4f; D(Colectivo 2023, 2018) %.4f; "
        "discrepan %d de 21",
        disimilitud(t["colectivo_2023"], t["edm"]),
        disimilitud(t["colectivo_2018"], t["edm"]),
        disimilitud(t["colectivo_2023"], t["colectivo_2018"]),
        t["discrepa"].sum(),
    )
    for nombre, sub in {
        "sin cuenta propia": edm[~edm["cuenta_propia"]],
        "sin centro de trabajo en la zona del hogar": edm[~edm["en_casa"]],
    }.items():
        LOG.info(
            "sensibilidad %s: D(Colectivo 2023, EDM) %.4f",
            nombre,
            disimilitud(t["colectivo_2023"], cuotas_edm(sub)),
        )


def grupos_origen(edm: pd.DataFrame) -> pd.Series:
    """Grupo de origen del registro previo: distrito de residencia en Madrid; fuera, el municipio si tiene al menos
    300 trabajadores en Madrid en la muestra y «resto» si no."""
    n = edm.groupby("municipio")["hogar"].transform("size")
    fuera = edm["municipio"].where(n >= 300, "resto")
    return _estrato(edm).where(edm["municipio"] == MUNICIPIO_MADRID, fuera)


def _d_grupos(h: np.ndarray, grupo: np.ndarray, etiquetas: np.ndarray) -> np.ndarray:
    """D de cada grupo frente al reparto global, con `h` el peso de cada hogar en cada distrito."""
    total = h.sum(axis=0) / h.sum()
    d = []
    for g in etiquetas:
        s = h[grupo == g].sum(axis=0)
        d.append(np.abs(s / s.sum() - total).sum() / 2)
    return np.array(d)


def control_origenes(
    edm: pd.DataFrame, reps: int = 1000, semilla: int = 357
) -> pd.DataFrame:
    """Bloque C del registro previo de #357 (supuesto 17): D de cada grupo de origen frente a la cuota global del
    EDM, con su referencia nula permutando el grupo entre hogares (pesos fijos): D nulo medio y p."""
    h = _por_hogar(edm)
    por_hogar = grupos_origen(edm).groupby(edm["hogar"]).first().reindex(h.index)
    grupo, etiquetas = por_hogar.to_numpy(), np.unique(por_hogar)
    obs = _d_grupos(h.to_numpy(), grupo, etiquetas)
    rng = np.random.default_rng(semilla)
    nulos = np.array(
        [
            _d_grupos(h.to_numpy(), rng.permutation(grupo), etiquetas)
            for _ in range(reps)
        ]
    )
    peso = h.sum(axis=1).groupby(grupo).sum().reindex(etiquetas).to_numpy()
    t = pd.DataFrame(
        {
            "personas": grupos_origen(edm).value_counts().reindex(etiquetas).to_numpy(),
            "peso": peso,
            "D": obs,
            "D_nulo": nulos.mean(axis=0),
            "p": (nulos >= obs).mean(axis=0),
        },
        index=etiquetas,
    )
    LOG.info("grupos de origen (supuesto 17):\n%s", t.round(4).to_string())
    LOG.info(
        "D medio ponderado %.4f; D nulo medio ponderado %.4f",
        np.average(obs, weights=peso),
        np.average(nulos.mean(axis=0), weights=peso),
    )
    return t


def _cambio(base: pd.DataFrame, alt: pd.DataFrame) -> dict:
    """Municipios que entran y salen de `elegible` y cambio medio absoluto de `pct_ocupados_elegibles` (puntos),
    por perfil y criterio, frente a `base`."""
    claves = ["perfil", "criterio", "municipio_id"]
    j = base.merge(alt, on=claves, suffixes=("", "_alt"), validate="one_to_one")
    j["entra"] = ~j["elegible"].astype(bool) & j["elegible_alt"].astype(bool)
    j["sale"] = j["elegible"].astype(bool) & ~j["elegible_alt"].astype(bool)
    # `pct_ocupados_elegibles` ya viene en porcentaje (simulacion._pct_municipios)
    j["dpct"] = (j["pct_ocupados_elegibles_alt"] - j["pct_ocupados_elegibles"]).abs()
    return (
        j.groupby(["perfil", "criterio"])[["entra", "sale", "dpct"]]
        .agg({"entra": "sum", "sale": "sum", "dpct": "mean"})
        .round(2)
        .to_dict("index")
    )


def efecto(edm: pd.DataFrame, reps: int = 20) -> None:
    """Efecto del registro previo de #357 (escala, no alternativa): municipios que cambian de `elegible` con (1) la
    cuota global del EDM2018 en vez del Colectivo, y su ruido con `reps` réplicas bootstrap; (2) la cuota de cada
    grupo de origen (`grupos_origen`) para los orígenes de fuera de Madrid, frente a (1)."""
    # import local: `simulacion` importa este módulo
    from mesobra import simulacion

    api = calculo.leer_api(calculo.RAIZ / "app/datos")
    m = leer_matriz()

    def correr(w: pd.DataFrame) -> pd.DataFrame:
        return simulacion.simulacion(simulacion.pares_con_imputacion(api, w))

    base = correr(pesos(m, leer_cuotas_distritos())[0])
    global_edm = correr(pesos(m, cuotas_edm(edm))[0])
    LOG.info("efecto (1) EDM global frente a Colectivo: %s", _cambio(base, global_edm))
    for i, fila in bootstrap_cuotas(edm, reps).iterrows():
        alt = correr(pesos(m, fila.rename_axis(None))[0])
        LOG.info("efecto (1) réplica %d frente a Colectivo: %s", i, _cambio(base, alt))
    grupo = grupos_origen(edm)
    propios = set(grupo[edm["municipio"] != MUNICIPIO_MADRID]) - {"resto"}
    clave = m["origen"].where(m["origen"].isin(propios), "resto")
    clave = clave.where(m["origen"] != MUNICIPIO_MADRID, MUNICIPIO_MADRID)
    partes = [pesos(m[clave == MUNICIPIO_MADRID], cuotas_edm(edm))[0]]
    for g in sorted(propios | {"resto"}):
        de_fuera = edm[(grupo == g) & (edm["municipio"] != MUNICIPIO_MADRID)]
        partes.append(pesos(m[clave == g], cuotas_edm(de_fuera))[0])
    por_grupo = correr(pd.concat(partes, ignore_index=True))
    LOG.info(
        "efecto (2) EDM por grupo frente a EDM global: %s",
        _cambio(global_edm, por_grupo),
    )
    LOG.info(
        "efecto (2) EDM por grupo frente a Colectivo: %s", _cambio(base, por_grupo)
    )


def control() -> None:
    """Control externo de los pesos de destino (#357), con el método del registro previo de `docs/decisiones.md`."""
    logging.basicConfig(level=logging.INFO)
    control_municipios()
    edm = leer_edm_trabajo()
    control_distritos(edm)
    control_origenes(edm)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    df = leer_matriz()
    total = df["ocupados"].sum()
    LOG.info(
        "ocupados %d; trabajan en la provincia %.1f %%; municipio de trabajo no consta %.2f %%",
        total,
        100 * df.loc[df["prov_destino"] == MADRID, "ocupados"].sum() / total,
        100 * df.loc[df["destino"].isna(), "ocupados"].sum() / total,
    )
    PROCESSED.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED, index=False)
    LOG.info("%s: %d pares", PROCESSED, len(df))


if __name__ == "__main__":
    if sys.argv[1:] == ["efecto"]:
        logging.basicConfig(level=logging.INFO)
        efecto(leer_edm_trabajo())
    else:
        control() if sys.argv[1:] == ["control"] else main()
