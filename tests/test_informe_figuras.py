"""Gráficos del informe técnico (#468): globos accesibles, cortes de quintil y lectura de lo publicado."""

import matplotlib

matplotlib.use("svg")

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from mesobra import informe_figuras as f


def test_guardar_pone_globo_accesible_y_escapa(tmp_path):
    f.estilo()
    fig, ax = plt.subplots()
    (p,) = ax.plot([1], [1], "o")
    globos: dict = {}
    f._globo(p, "m1", 'Móstoles: 15,3 % <"x">', globos)
    ruta = tmp_path / "a.svg"
    f.guardar(fig, ruta, globos)
    svg = ruta.read_text(encoding="utf-8")
    assert 'class="marca" role="img"' in svg
    assert (
        "style=" not in svg and "<style" not in svg
    )  # la CSP del informe los bloquearía
    assert "<title>Móstoles: 15,3 % &lt;&quot;x&quot;&gt;</title>" in svg
    assert "font-family" in svg and "Instrument Sans" in svg  # texto vivo, no trazos


def test_guardar_falla_si_la_marca_no_esta(tmp_path):
    fig, _ = plt.subplots()
    with pytest.raises(ValueError, match="no está"):
        f.guardar(fig, tmp_path / "a.svg", {"nada": "x"})


def test_cruza_corte():
    t = pd.DataFrame(
        {"esfuerzo": [0.10, 0.15, 0.20], "error": [0.01, 0.06, 0.001]},
        index=["a", "b", "c"],
    )
    cortes = [0.0, 0.12, 0.30]  # un solo corte interior, en 0,12
    assert f.cruza_corte(t, cortes).tolist() == [False, True, False]


def test_rinde_por_perfil_lee_los_titulares():
    texto = (
        "Persona sola con el SMI: neto estimado de 8,80 € por hora trabajada. En 8.620 pares, vivir lejos "
        "rinde una mediana estimada de −0,34 € por hora extra de viaje (cuartiles −5,65 a 4,99); iguala…"
    )
    titulares = [{"texto": texto}] + [
        {"texto": texto.replace("Persona sola con el SMI", p)}
        for _, p in f.PERFILES[1:]
    ]
    d = f.rinde_por_perfil(titulares)
    assert d.loc[0, ["neto_hora", "mediana", "q1", "q3"]].tolist() == [
        8.80,
        -0.34,
        -5.65,
        4.99,
    ]


def test_rinde_por_perfil_falla_si_cambia_el_texto():
    titulares = [{"texto": f"{p}: neto distinto por hora extra"} for _, p in f.PERFILES]
    with pytest.raises(ValueError, match="No se reconoce"):
        f.rinde_por_perfil(titulares)


def test_especificaciones_en_rechazadas_por_punto():
    m = {"beta": 100.0, "se": 10.0, "p": 0.01}
    espacial = {
        k: m
        for k in (
            "sem_het",
            "sem_het_dos_pasos",
            "sem",
            "sar",
            "sdem",
            "slx",
            "ols",
            "ols_hac",
        )
    }
    bi = {
        "espacial": {"k5": espacial, "k8": espacial},
        "robustez_vivienda_alquilada": {"control_alquiler": {"k5": m, "k8": m}},
    }
    d = f.especificaciones(bi)
    assert len(d) == 11
    assert d.loc[0, ["b", "lo", "hi"]].round(3).tolist() == [1.0, 0.804, 1.196]
