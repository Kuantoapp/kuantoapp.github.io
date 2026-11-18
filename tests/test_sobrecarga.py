import numpy as np
import pandas as pd
import pytest
from scipy.stats import norm

from mesobra import sobrecarga as s


def _sec(n=1, sigma_a=0.0, sum_uc=0.0, **extra):
    d = {
        "m_media": 20000.0,
        "mu_a": np.log(900),
        "sigma_a": sigma_a,
        "uc": 1.5,
        "sum_uc": sum_uc,
        "inquilinos": 100.0,
    } | extra
    return pd.DataFrame([d] * n)


@pytest.mark.parametrize("k", s.CORTES)
def test_alquiler_fijo_coincide_con_la_formula_cerrada(k):
    sigma, m_t = 0.6, np.log(20000) - 0.6**2 / 2
    p = s.prob_supera(_sec(), [sigma], 0.3, k)
    esperado = norm.cdf((np.log(12 * 900 / 1.5 / k) - m_t) / sigma)
    assert p[0] == pytest.approx(esperado, rel=1e-9)


def test_alquiler_variable_coincide_con_la_formula_cerrada():
    sigma, sa, rho, uc = 0.6, 0.4, 0.3, 1.5
    m_t = np.log(20000) - sigma**2 / 2
    for k in s.CORTES:
        p = s.prob_supera(_sec(sigma_a=sa), [sigma], rho, k)
        dt = np.sqrt(sa**2 + sigma**2 - 2 * rho * sigma * sa)
        esperado = norm.cdf((np.log(900) + np.log(12 / (uc * k)) - m_t) / dt)
        assert p[0] == pytest.approx(esperado, rel=1e-6)
    # con la tasa por debajo del 50 %, la correlación positiva la reduce
    sec = _sec(sigma_a=sa)
    assert s.prob_supera(sec, [sigma], 0.3, 0.5) < s.prob_supera(sec, [sigma], 0.0, 0.5)


def test_esfuerzo_mediano_con_alquiler_fijo():
    sigma, m_t = 0.6, np.log(20000) - 0.6**2 / 2
    m = s.esfuerzo_mediano(_sec(sum_uc=30.0), [sigma], 0.3, [1])
    assert m == pytest.approx(100 * 12 * (900 / 1.5 + 30) / np.exp(m_t), rel=1e-6)


def test_gini_sin_recorte_es_el_de_la_log_normal():
    assert s.gini_recortado(0.6, recorte=0) == pytest.approx(
        2 * norm.cdf(0.6 / np.sqrt(2)) - 1, abs=1e-4
    )


def test_sigma_gini_ida_y_vuelta():
    assert s.sigma_gini(100 * s.gini_recortado(0.55)) == pytest.approx(0.55, abs=1e-3)
    with pytest.raises(ValueError):
        s.sigma_gini(99.9)


def test_gini_recortado_coincide_con_una_muestra():
    x = np.sort(np.random.default_rng(0).lognormal(0, 0.6, 200_000))
    x = x[int(0.015 * len(x)) : int(0.985 * len(x))]
    n = len(x)
    gini = 2 * (np.arange(1, n + 1) * x).sum() / (n * x.sum()) - (n + 1) / n
    assert s.gini_recortado(0.6) == pytest.approx(gini, abs=2e-3)


def test_sigma_p80p20():
    r = np.exp(0.7 * (norm.ppf(0.8) - norm.ppf(0.2)))
    assert s.sigma_p80p20(r) == pytest.approx(0.7)


def test_media_inquilinos():
    assert s.media_inquilinos(25000, 1, 0.65) == pytest.approx(25000)
    assert s.media_inquilinos(25000, 0.3, 1) == pytest.approx(25000)
    # mezcla de vuelta: p·m_inq + (1 − p)·m_prop = media
    m = s.media_inquilinos(25000, 0.3, 0.65)
    assert 0.3 * m + 0.7 * m / 0.65 == pytest.approx(25000)


def test_unidades_consumo():
    assert s.unidades_consumo(1, 0) == pytest.approx(1)
    assert s.unidades_consumo(3, 100 / 3) == pytest.approx(1 + 0.5 + 0.3)


def test_tenencia_2025_2021(tmp_path):
    ruta = tmp_path / "t.csv"
    filas = [
        (2021, s.MERCADO, "20.3"),
        (2021, s.REDUCIDO, "3.7"),
        (2025, s.MERCADO, "22.6"),
        (2025, s.REDUCIDO, "4.3"),
        (2025, "Hogares con la vivienda en regimen de propiedad", "69.1"),
    ]
    cabecera = "Año;Concepto;Tipo territorio;Código territorio;Territorio;Valor;Unidad;Estado dato"
    ruta.write_text(
        "\n".join(
            [cabecera] + [f"{a};{c};Otros;;;{v};Porcentaje;" for a, c, v in filas]
        ),
        encoding="utf-8-sig",
    )
    assert s.tenencia_2025_2021(ruta) == pytest.approx(26.9 / 24.0)
    ruta.write_text("\n".join([cabecera] + [f"2021;{s.MERCADO};Otros;;;1;Porcentaje;"]))
    with pytest.raises(ValueError):
        s.tenencia_2025_2021(ruta)


def test_sobrecarga_sobre_secciones_sinteticas(tmp_path, monkeypatch):
    renta = pd.DataFrame(
        {
            "unidad_id": ["28001", "28002", "28003"],
            "nivel": "zona",
            "anio": 2024,
        }
    )
    renta.to_parquet(tmp_path / "renta.parquet")
    monkeypatch.setattr(s, "PROCESSED", tmp_path)
    sec = pd.concat(
        [
            _sec(2, sigma_a=0.3, sum_uc=30.0, inquilinos=50.0),
            _sec(1, sigma_a=0.2, sum_uc=30.0, m_media=30000.0),
        ],
        ignore_index=True,
    ).assign(
        zona_id=["28001", "28001", "28002"],
        sigma_gini=[0.5, 0.55, 0.6],
        sigma_p80=[0.6, 0.6, 0.55],
    )
    sec["dif_sigma"] = sec["sigma_p80"] - sec["sigma_gini"]
    t = s.sobrecarga(sec, 0.28).set_index("zona_id")
    ok = t.loc[["28001", "28002"]]
    assert (ok.filter(like="_inf").values <= ok.filter(like="_sup").values).all()
    assert (ok.pct_50_inf <= ok.pct_40_inf).all() and (
        ok.pct_40_inf <= ok.pct_30_inf
    ).all()
    assert t.loc["28003"].drop("anio").isna().all()
    # con una sola σ los tramos de la Comunidad suman 100
    c = s.comunidad(sec.assign(sigma_p80=sec["sigma_gini"]), 0.28)
    assert sum(
        c[t]["medio"] for t in ("<=30", "30-40", "40-50", ">50")
    ) == pytest.approx(100)
