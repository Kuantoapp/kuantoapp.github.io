import numpy as np
import pandas as pd
import pytest
from scipy.stats import norm

from mesobra import hogares as cesta_mod
from mesobra import sobrecarga as s
from mesobra.sobrecarga_ecv import (
    EFECTO_DISENO,
    INQUILINOS,
    MADRID,
    RAW,
    _supera,
    alquiler_30,
    control_f306,
    hogares,
    sobrecarga_control,
    sobrecarga_eurostat,
    tasa,
    tramos_control,
)

B = "          "  # «no aplicable» del INE: varios espacios

# id, región, peso hogar, HH021, HH060, HH070, HY020, HY070N, HX240
H = [
    (1, "ES30", 100, 3, 500, 600, 18000, 0, 1.0),
    (2, "ES30", 200, 4, 300, 500, 12000, 1200, 1.0),
    (3, "ES30", 300, 5, B, 100, -1000, 0, 1.0),
    (4, "ES10", 400, 3, 400, B, 24000, 0, 1.0),
    (5, "ES30", 100, 3, 800, 900, 20000, 0, 1.0),
]
# RB030 = id de hogar · 100 + orden; el hogar 1 tiene dos personas
R = [(101, 50), (102, 60), (201, 10), (301, 20), (401, 30), (501, 40)]


def _csv(ruta, columnas, filas):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    cuerpo = "\n".join(",".join(str(v) for v in f) for f in filas)
    ruta.write_text(",".join(columnas) + "\n" + cuerpo + "\n", encoding="utf-8")


@pytest.fixture
def carpeta(tmp_path):
    _csv(
        tmp_path / "ECV_Td_2025/CSV/esudb25d.csv",
        ["DB030", "DB040", "DB090"],
        [(f[0], f[1], f[2]) for f in H],
    )
    _csv(
        tmp_path / "ECV_Th_2025/CSV/esudb25h.csv",
        ["HB030", "HH021", "HH060", "HH070", "HY020", "HY070N", "HX240"],
        [(f[0], *f[3:]) for f in H],
    )
    _csv(tmp_path / "ECV_Tr_2025/CSV/esudb25r.csv", ["RB030", "RB050"], R)
    return tmp_path


def test_hogares_une_y_pesa_personas(carpeta):
    h = hogares(carpeta).set_index("DB030")
    assert len(h) == 5
    assert h.peso_personas.to_dict() == {1: 110, 2: 10, 3: 20, 4: 30, 5: 40}
    assert h.loc[1, "HH021"] == 3
    assert np.isnan(h.loc[3, "HH060"]) and np.isnan(h.loc[4, "HH070"])


def test_hogares_falta_en_h(carpeta):
    ruta = carpeta / "ECV_Th_2025/CSV/esudb25h.csv"
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    ruta.write_text("\n".join(lineas[:-1]) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no están a la vez"):
        hogares(carpeta)


def test_hogares_sin_personas(carpeta):
    ruta = carpeta / "ECV_Tr_2025/CSV/esudb25r.csv"
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    ruta.write_text("\n".join(lineas[:-1]) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="sin personas"):
        hogares(carpeta)


def test_reglas_a_mano(carpeta):
    h = hogares(carpeta).set_index("DB030")
    # 1: 7200/18000 = 0,40 (no supera); 2: (6000−1200)/10800 = 0,44; 3: renta < 0 → 1; 4: blanco; 5: 0,54
    assert sobrecarga_eurostat(h).fillna(-1).tolist() == [0, 1, 1, -1, 1]
    # sin descontar ayudas: 2 pasa a 6000/12000 = 0,5
    assert sobrecarga_control(h).fillna(-1).tolist() == [0, 1, 1, -1, 1]
    # alquiler: 0,33 → 1; 0,30 exacto → 0; blanco; 0,20 → 0; 0,48 → 1
    assert alquiler_30(h).fillna(-1).tolist() == [1, 0, -1, 0, 1]


def test_tramos_sintetico(carpeta):
    # inquilinos de ES30: 1 (0,40 → 30-40, peso 100), 2 (0,50 exacto → 40-50, 200), 5 (0,54 → >50, 100)
    t = tramos_control(hogares(carpeta))["tasa"].to_dict()
    assert t == pytest.approx({"<=30": 0, "30-40": 25, "40-50": 50, ">50": 25})


def test_tramos_renta_negativa_y_corte_exacto():
    # renta ≤ 0 → «>50» (Eurostat); 0,30 exacto no supera → «<=30»
    h = pd.DataFrame(
        {
            "DB040": [MADRID] * 2,
            "HH021": [3, 3],
            "DB090": [1.0, 1.0],
            "HH070": [100, 300],
            "HY020": [-500, 12000],
        }
    )
    t = tramos_control(h)["tasa"].to_dict()
    assert t == pytest.approx({"<=30": 50, "30-40": 0, "40-50": 0, ">50": 50})


def test_reglas_casos_limite():
    # Eurostat §5: denominador 0 → sobrecargado; numerador ≤ 0 → no; 0,40 exacto no supera
    h = pd.DataFrame(
        {
            "HH070": [100, 100, 600, 600.01],
            "HY020": [1200, 20000, 18000, 18000],
            "HY070N": [1200, 1500, 0, 0],
        }
    )
    assert sobrecarga_eurostat(h).tolist() == [1, 0, 0, 1]


def test_tasa_a_mano():
    # p = 0,5; w·(y−p) = 0,5, −1, 0,5; ee = sqrt(3/2 · 1,5) / 4 = 0,375
    t, ee, n = tasa(pd.Series([1.0, 0.0, 1.0, np.nan]), pd.Series([1, 2, 1, 9]))
    assert (t, ee, n) == (pytest.approx(50), pytest.approx(37.5), 3)


def test_tasa_pocas_observaciones():
    with pytest.raises(ValueError):
        tasa(pd.Series([1.0, np.nan]), pd.Series([1, 1]))


def test_control_sintetico(carpeta):
    # inquilinos de ES30: hogares 1, 2 y 5, pesos 100, 200, 100
    c = control_f306(hogares(carpeta))
    # gasto_40: y = 0, 1, 1 → 75 %; ee = sqrt(1,5 · 8750) / 400
    g = c.loc["gasto_40"]
    assert (g.tasa, g.ee, g.n) == (
        pytest.approx(75),
        pytest.approx(100 * 13125**0.5 / 400),
        3,
    )
    amplitud = 1.96 * g.ee * EFECTO_DISENO**0.5
    assert g.ic_inf == pytest.approx(g.tasa - amplitud)
    assert g.ic_sup == pytest.approx(g.tasa + amplitud)
    # alquiler_30: y = 1, 0, 1 → 50 %; ee = sqrt(1,5 · 15000) / 400 = 0,375
    a = c.loc["alquiler_30"]
    assert (a.tasa, a.ee, a.n) == (pytest.approx(50), pytest.approx(37.5), 3)


# --- cifras reales de la ECV 2025 -------------------------------------------------------------
# Tolerancia ±0,05 puntos: Eurostat publica con un decimal.
real = pytest.mark.skipif(
    not RAW.exists(), reason="faltan los microdatos de la ECV en data/raw"
)


@pytest.fixture(scope="module")
def h():
    return hogares()


def _eurostat(h, tenencias=None):
    if tenencias is not None:
        h = h[h.HH021.isin(tenencias)]
    return tasa(sobrecarga_eurostat(h), h.peso_personas)[0]


@real
@pytest.mark.parametrize(
    ("tenencias", "esperado"),
    [((3,), 26.8), ((4, 5), 8.4), ((2,), 3.4), ((1,), 1.9), (None, 7.2)],
)
def test_eurostat_espana(h, tenencias, esperado):
    # Eurostat ilc_lvho07c, España 2025, por tenencia (HH021)
    assert _eurostat(h, tenencias) == pytest.approx(esperado, abs=0.05)


@real
def test_eurostat_madrid(h):
    # Eurostat ilc_lvho07_r, ES30 2025
    assert _eurostat(h[h.DB040 == MADRID]) == pytest.approx(9.9, abs=0.05)


@real
@pytest.mark.parametrize("fila", ["gasto_40", "alquiler_30"])
def test_control_f306(h, fila):
    # Cifra de control de F3-06 (#100), cálculo propio sobre ES30 y HH021 3 o 4 (estimado)
    esperado = {"gasto_40": 36.0, "alquiler_30": 41.4}[fila]
    c = control_f306(h).loc[fila]
    assert c.tasa == pytest.approx(esperado, abs=0.05)
    assert c.ee == pytest.approx(2.7, abs=0.05)
    assert c.n == 562


@real
@pytest.mark.parametrize(
    ("tenencias", "esperado"),
    [((1, 2), 69.1), ((3,), 22.6), ((4,), 4.3), ((5,), 4.0)],
)
def test_reparto_tenencia_madrid(h, tenencias, esperado):
    # Catálogo 1912645 / INE t=9997, 2025: hogares de ES30 por tenencia, ponderados con DB090
    m = h[h.DB040 == MADRID]
    parte = m.DB090[m.HH021.isin(tenencias)].sum() / m.DB090.sum()
    assert 100 * parte == pytest.approx(esperado, abs=0.05)


@real
@pytest.mark.parametrize(
    ("tenencias", "esperado"),
    [
        ((3, 4), 19781.17),
        (None, 27136.20),
        ((2,), 31108.81),
        ((1,), 29941.95),
        ((5,), 21833.65),
    ],
)
def test_renta_por_uc_madrid(h, tenencias, esperado):
    # IECM 175_000004, 2025: media de HY020/HX240 ponderada con el peso de las personas
    m = h[h.DB040 == MADRID]
    if tenencias is not None:
        m = m[m.HH021.isin(tenencias)]
    media = np.average(m.HY020 / m.HX240, weights=m.peso_personas)
    assert media == pytest.approx(esperado, abs=0.01)


@real
def test_tramos_control(h):
    # Tramos de F3-06 (#100, nota del 18-11), ES30 y HH021 3 o 4 (estimado). Las constantes de
    # sobrecarga.CONTROL se fijaron a mano con EE redondeados antes de ejecutar: difieren ≤ 0,25.
    from mesobra.sobrecarga import CONTROL

    t = tramos_control(h)
    esperado = {"<=30": 46.0, "30-40": 18.0, "40-50": 10.4, ">50": 25.6}
    assert t["tasa"].to_dict() == pytest.approx(esperado, abs=0.05)
    assert t["tasa"].sum() == pytest.approx(100)
    assert (t["n"] == 562).all()
    for tramo, (inf, sup) in t[["ic_inf", "ic_sup"]].iterrows():
        assert (inf, sup) == pytest.approx(CONTROL[tramo], abs=0.25)


# --- #194: el método de F3-06 con entradas de la ECV --------------------------------------------
# Regla y diseño en docs/verificaciones/renta-vivienda.md (#194), fijados antes de ejecutar. ESTIMADO.
UMBRAL_METODO = 3.7


def _cuantil(x, w, q):
    """Cuantil ponderado: interpolación sobre el peso acumulado en el punto medio (como `wq` de #193)."""
    o = np.argsort(x)
    x, w = np.asarray(x, dtype=float)[o], np.asarray(w, dtype=float)[o]
    return np.interp(q, (np.cumsum(w) - w / 2) / w.sum(), x)


def _gini_winsorizado(x, w, recorte=s.RECORTE):
    """Gini ponderado con las colas winsorizadas, con la fórmula de `sobrecarga.gini_recortado`."""
    x = np.clip(np.asarray(x, dtype=float), *_cuantil(x, w, [recorte, 1 - recorte]))
    o = np.argsort(x)
    x, w = x[o], np.asarray(w, dtype=float)[o]
    u = (np.cumsum(w) - w / 2) / w.sum()
    return 2 * np.average(u * x, weights=w) / np.average(x, weights=w) - 1


def _inquilinos(h):
    """Inquilinos de ES30 con alquiler y renta declarados: la misma población en los dos lados."""
    q = h[(h.DB040 == MADRID) & h.HH021.isin(INQUILINOS)]
    return q.dropna(subset=["HH060", "HY020"])


def _entradas(q, cesta):
    """Toda la Comunidad como una sección, y las dos σ (Gini, P80/P20) de la renta por UC; pesos DB090."""
    w = q.DB090
    r = q.HY020 / q.HX240
    p20, p80 = _cuantil(r, w, [0.2, 0.8])
    a25, a75 = np.log(_cuantil(q.HH060, w, [0.25, 0.75]))
    sec = pd.DataFrame(
        {
            "m_media": [np.average(r, weights=w)],
            # como sobrecarga.alquiler_2025
            "mu_a": [(a25 + a75) / 2],
            "sigma_a": [(a75 - a25) / (2 * norm.ppf(0.75))],
            "uc": [np.average(q.HX240, weights=w)],
            "sum_uc": [cesta],
        }
    )
    sigmas = np.array(
        [s.sigma_gini(100 * _gini_winsorizado(r, w)), s.sigma_p80p20(p80 / p20)]
    )
    return sec, sigmas


def _directa(q, cesta, k):
    return tasa(_supera(12 * (q.HH060 + cesta * q.HX240), q.HY020, k), q.DB090)[0]


def _metodo(q, cesta, k, rho):
    """Tasa (%) del método con cada σ: `prob_supera` difunde las dos σ sobre la única sección."""
    sec, sigmas = _entradas(q, cesta)
    return 100 * s.prob_supera(sec, sigmas, rho, k)


@pytest.fixture
def cesta_2025(monkeypatch):
    """Suministros €/UC·mes de la EPF 2025 sin IPC: la renta y el alquiler de la ECV 2025 son de 2024."""
    subgrupos = {g for c in cesta_mod.CONCEPTOS.values() for _, g in c.values()}
    f = pd.Series(1.0, index=sorted(subgrupos))
    f.attrs["ipc_hasta"] = "2025-12"
    monkeypatch.setattr(cesta_mod, "factores_ipc", lambda _carpeta: f)
    return cesta_mod.cesta_uc()["suministros"]


def test_cuantil_y_gini_ponderados():
    x = np.array([3.0, 1.0, 7.0, 2.0, 5.0])
    assert _cuantil(x, np.ones(5), 0.5) == 3.0
    # pesos enteros = muestra repetida (sin recorte: el cuantil interpolado no es invariante a repetir)
    w = np.array([2, 1, 3, 1, 2])
    n, rep = w.sum(), np.sort(np.repeat(x, w))
    gini = 2 * (np.arange(1, n + 1) * rep).sum() / (n * rep.sum()) - (n + 1) / n
    assert _gini_winsorizado(x, w, recorte=0) == pytest.approx(gini)
    # misma fórmula que gini_recortado: una muestra grande de la log-normal da su Gini winsorizado
    m = np.random.default_rng(0).lognormal(0, 0.6, 200_000)
    assert _gini_winsorizado(m, np.ones(len(m))) == pytest.approx(
        s.gini_recortado(0.6), abs=2e-3
    )


def test_metodo_igual_a_directa_si_los_datos_son_log_normales():
    # de punta a punta: con hogares log-normales, misma UC y ρ conocido, entradas → método ≈ recuento
    g = np.random.default_rng(2)
    z, e = g.standard_normal((2, 200_000))
    rho, sigma = 0.28, 0.6
    q = pd.DataFrame(
        {
            "DB090": g.uniform(0.5, 2, len(z)),
            "HH060": np.exp(np.log(800) + 0.35 * z),
            "HY020": 1.7
            * np.exp(
                np.log(20000)
                - sigma**2 / 2
                + sigma * (rho * z + np.sqrt(1 - rho**2) * e)
            ),
            "HX240": 1.7,
        }
    )
    _, sigmas = _entradas(q, 81.0)
    assert sigmas == pytest.approx([sigma, sigma], abs=0.01)
    for k in (0.30, 0.40):
        assert _metodo(q, 81.0, k, rho) == pytest.approx(
            [_directa(q, 81.0, k)] * 2, abs=0.3
        )


@real
def test_metodo_con_entradas_de_la_ecv(h, cesta_2025):
    # #194, estimado: cifras y veredicto de docs/verificaciones/renta-vivienda.md (regla fijada antes)
    assert cesta_2025 == pytest.approx(
        (806.38 + 166.63) / 12
    )  # EPF 2025, 04.5 + 04.4.1
    q = _inquilinos(h)
    assert len(q) == 562
    rho = s.parametros_ecv(h)["rho"]
    # el lado directo reproduce las cifras de control (criterio 3: 36,0 tras #260; 35,9 antes)
    assert control_f306(h).loc["gasto_40", "tasa"] == pytest.approx(36.0, abs=0.05)
    assert _directa(q, 0.0, 0.30) == pytest.approx(tasa(alquiler_30(q), q.DB090)[0])
    esperado = {  # medida: directa, método con σ del Gini y con σ del P80/P20
        "40": (cesta_2025, 0.40, 34.441, (37.312, 37.538)),
        "30": (0.0, 0.30, 41.447, (44.310, 44.493)),
    }
    for c, k, directa, metodo in esperado.values():
        assert _directa(q, c, k) == pytest.approx(directa, abs=1e-3)
        assert _metodo(q, c, k, rho) == pytest.approx(metodo, abs=1e-3)
    c, k, directa, _ = esperado["40"]
    assert np.abs(_metodo(q, c, k, rho) - directa).max() <= UMBRAL_METODO  # pasa: 3,10


def test_prob_supera_coincide_con_monte_carlo():
    # segunda vía de la integración de Gauss-Hermite: muestreo de las mismas log-normales correlacionadas
    sec = pd.DataFrame(
        {
            "m_media": [20000.0],
            "mu_a": [np.log(800)],
            "sigma_a": [0.35],
            "uc": [1.7],
            "sum_uc": [81.0],
        }
    )
    sigma, rho, k = 0.6, 0.28, 0.40
    z, e = np.random.default_rng(1).standard_normal((2, 1_000_000))
    renta = np.exp(
        np.log(20000) - sigma**2 / 2 + sigma * (rho * z + np.sqrt(1 - rho**2) * e)
    )
    coste = 12 * (np.exp(np.log(800) + 0.35 * z) / 1.7 + 81.0)
    assert 100 * s.prob_supera(sec, np.array([sigma]), rho, k)[0] == pytest.approx(
        100 * (coste > k * renta).mean(), abs=0.1
    )
