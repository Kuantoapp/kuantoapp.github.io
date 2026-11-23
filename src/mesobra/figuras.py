"""Figuras del informe de análisis (#90): dos mapas por zona y la dispersión del Bono.

Las dibuja `pipeline_analisis` a partir de las tablas `esfuerzo` y `bono`; no calculan nada nuevo salvo
los cortes de las clases. Geometría de `app/datos/zonas.geojson` (municipios y los 21 distritos de Madrid).
"""

from itertools import pairwise
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch

from mesobra import esfuerzo as esf
from mesobra.alquiler import MIN_TESTIGOS
from mesobra.zonas import MADRID

ZONAS = Path(__file__).resolve().parents[2] / "app/datos/zonas.geojson"
CRS = 25830  # UTM 30N: se dibuja en metros, sin deformar la Comunidad
FUENTE_MAPAS = "Fuente: SERPAVI (MIVAU) y ADRH (INE), elaboración propia."
FUENTE_BONO = (
    "Fuente: Bono Alquiler Joven 2022 (Comunidad de Madrid), Censo anual (INE), SERPAVI (MIVAU) y ADRH (INE), "
    "elaboración propia."
)
GRIS = "#e3e3e3"
TRAMA = "#9a9a9a"


def leer_zonas(ruta: Path = ZONAS) -> gpd.GeoDataFrame:
    return gpd.read_file(ruta).to_crs(CRS)


def es(x: float, decimales: int = 1) -> str:
    """Número en formato español: punto de miles, coma decimal y signo menos tipográfico."""
    return f"{x:,.{decimales}f}".translate(str.maketrans(",.-", ".,−"))


def cortes_simetricos(valores: pd.Series) -> list[float]:
    """`[-m, -q2, -q1, 0, q1, q2, m]`: terciles y máximo de |valor|, para colorear en torno a 0."""
    q1, q2 = np.nanquantile(np.abs(valores), [1 / 3, 2 / 3])
    m = np.nanmax(np.abs(valores))
    return [-m, -q2, -q1, 0.0, q1, q2, m]


def _unir(zonas: gpd.GeoDataFrame, serie: pd.Series) -> gpd.GeoDataFrame:
    """Valor por `zona_id` sobre la geometría; falla si el dato trae ids que no tienen geometría."""
    if sobran := sorted(set(serie.index) - set(zonas["zona_id"])):
        raise ValueError(f"Zonas con dato y sin geometría: {sobran}")
    return zonas.assign(valor=zonas["zona_id"].map(serie))


def _pocos(tabla: pd.DataFrame, anios: list[int]) -> pd.Series:
    """Por zona: True si en alguno de los `anios` tiene menos de `MIN_TESTIGOS` testigos del SERPAVI."""
    t = tabla[tabla["anio"].isin(anios)]
    return (t["testigos"] < MIN_TESTIGOS).groupby(t["zona_id"]).any()


def _marcar(g: gpd.GeoDataFrame, pocos: pd.Series) -> gpd.GeoDataFrame:
    """Columna `pocos` (solo en las zonas con valor: las sin dato ya van en gris)."""
    marca = g["zona_id"].isin(pocos.index[pocos])
    return g.assign(pocos=marca & g["valor"].notna())


def _contorno(ax: plt.Axes, g: gpd.GeoDataFrame) -> None:
    """Borde negro grueso, sin relleno, en las zonas con `pocos`."""
    if g["pocos"].any():
        g[g["pocos"]].plot(ax=ax, facecolor="none", edgecolor="black", linewidth=1.3)


def _rangos(cortes: list[float]) -> list[str]:
    return [f"{es(100 * a)} a {es(100 * b)}" for a, b in pairwise(cortes)]


def _mapa(
    zonas: gpd.GeoDataFrame,
    cortes: list[float],
    paleta: str,
    textos: tuple[str, list[str], str],
    ruta: Path,
) -> None:
    """Coropleta por clases (`cortes` en fracción) con recuadro ampliado de Madrid.

    `textos`: título de la leyenda, rótulo de cada clase y línea extra del pie. Las zonas con
    `pocos` van con borde negro grueso encima del color.
    """
    titulo, etiquetas, nota = textos
    n = len(cortes) - 1
    colores = plt.get_cmap(paleta)(np.linspace(0.1, 0.9, n))
    estilo = {
        "column": "valor",
        "cmap": ListedColormap(colores),
        "norm": BoundaryNorm(cortes, n),
        "edgecolor": "white",
        "linewidth": 0.25,
        "missing_kwds": {"color": GRIS, "hatch": "////", "edgecolor": TRAMA},
    }
    madrid = zonas[(zonas["municipio_id"] == MADRID) & (zonas["tipo"] == "distrito")]
    if madrid.empty:
        raise ValueError("La geometría no trae los distritos de Madrid (28079)")
    fig, ax = plt.subplots(figsize=(8, 7.4))
    zonas.plot(ax=ax, **estilo)
    _contorno(ax, zonas)
    ax.set_axis_off()
    # los distritos son diminutos frente a los municipios rurales: recuadro ampliado
    zoom = ax.inset_axes([0.0, 0.64, 0.36, 0.36])
    madrid.plot(ax=zoom, **estilo)
    _contorno(zoom, madrid)
    x0, y0, x1, y1 = madrid.total_bounds
    zoom.set(
        xlim=(x0, x1),
        ylim=(y0, y1),
        xticks=[],
        yticks=[],
        xlabel="",
        ylabel="",
        aspect="equal",
    )
    zoom.set_title("Madrid, 21 distritos", fontsize=9)
    marca = ax.indicate_inset_zoom(zoom, edgecolor="#444444")
    for c in marca.connectors:  # sin líneas de unión: cruzan el mapa
        c.set_visible(False)
    leyenda = [
        Patch(facecolor=c, label=e) for c, e in zip(colores, etiquetas, strict=True)
    ]
    if (sin := int(zonas["valor"].isna().sum())) > 0:
        leyenda.append(
            Patch(
                facecolor=GRIS,
                edgecolor=TRAMA,
                hatch="////",
                label=f"sin dato (n = {sin})",
            )
        )
    leyenda.append(
        Patch(
            facecolor="none",
            edgecolor="black",
            linewidth=1.3,
            label=f"pocos alquileres declarados (< {MIN_TESTIGOS}): impreciso (n = {int(zonas['pocos'].sum())})",
        )
    )
    ax.legend(
        handles=leyenda, title=titulo, loc="lower left", bbox_to_anchor=(0.0, -0.17), frameon=False,
        fontsize=9, title_fontsize=9, alignment="left",
    )  # fmt: skip
    ax.text(
        0.0,
        -0.2,
        f"{nota}{FUENTE_MAPAS}",
        transform=ax.transAxes,
        va="top",
        fontsize=8,
        color="#444444",
    )
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)


def mapa_esfuerzo(
    tabla: pd.DataFrame, zonas: gpd.GeoDataFrame, ruta: Path
) -> tuple[int, int]:
    """Esfuerzo del último año en quintiles (`tabla` con `testigos`); devuelve zonas sin dato y con pocos contratos."""
    anio = int(tabla["anio"].max())
    ultimo = tabla[(tabla["anio"] == anio) & (tabla["zona_id"] != MADRID)]
    g = _marcar(
        _unir(zonas, ultimo.set_index("zona_id")["esfuerzo"]), _pocos(ultimo, [anio])
    )
    cortes = np.nanquantile(g["valor"], np.linspace(0, 1, 6)).tolist()
    titulo = f"Esfuerzo del alquiler en {anio}\n(% de la renta neta media\nmensual del hogar; quintiles)"
    _mapa(g, cortes, "YlOrRd", (titulo, _rangos(cortes), ""), ruta)
    return int(g["valor"].isna().sum()), int(g["pocos"].sum())


def mapa_cambio(
    tabla: pd.DataFrame, zonas: gpd.GeoDataFrame, ruta: Path
) -> tuple[int, int]:
    """Cambio del esfuerzo entre el primer y el último año (`tabla` con `testigos`) en 6 clases simétricas en torno a 0."""
    desde, hasta = int(tabla["anio"].min()), int(tabla["anio"].max())
    g = _unir(zonas, esf.cambio(tabla).drop(MADRID, errors="ignore"))
    g = _marcar(g, _pocos(tabla, [desde, hasta]))
    cortes = cortes_simetricos(g["valor"])
    etiquetas = _rangos(cortes)
    # las clases de los extremos llegan hasta el mínimo y el máximo reales: se rotulan abiertas
    etiquetas[0], etiquetas[-1] = (
        f"< {es(100 * cortes[1])}",
        f"> {es(100 * cortes[-2])}",
    )
    titulo = (
        f"Cambio del esfuerzo {desde}-{hasta} (p. p.)\n"
        "cortes simétricos en torno a 0:\nterciles de |cambio|"
    )
    pie = f"Extremos: mínimo {es(100 * g['valor'].min())} y máximo +{es(100 * g['valor'].max())} p. p.\n"
    _mapa(g, cortes, "RdBu_r", (titulo, etiquetas, pie), ruta)
    return int(g["valor"].isna().sum()), int(g["pocos"].sum())


def dispersion_bono(bono: pd.DataFrame, zonas: gpd.GeoDataFrame, ruta: Path) -> None:
    """Esfuerzo de 2023 frente a aceptadas por 1.000 jóvenes, por municipio con esfuerzo."""
    nombres = zonas[zonas["tipo"] == "municipio"].set_index("zona_id")["nombre"]
    nombres[MADRID] = "Madrid"
    d = bono[bono["grupo"] != "sin_dato"].copy()
    d["x"] = 100 * d["necesidad"] / d["poblacion_joven"]
    d["y"] = 1000 * d["aceptadas"] / d["poblacion_joven"]
    foco = d["grupo"] == "necesidad_alta_ayuda_baja"
    fig, ax = plt.subplots(figsize=(8, 6.2))
    tamano = np.sqrt(d["poblacion_joven"]) / 2.5
    ax.scatter(
        d["x"][~foco],
        d["y"][~foco],
        s=tamano[~foco],
        color="#7a8ea6",
        alpha=0.6,
        linewidth=0,
    )
    ax.scatter(d["x"][foco], d["y"][foco], s=tamano[foco], color="#c0392b", alpha=0.85, linewidth=0.5,
               edgecolor="white", label=f"Necesidad alta y ayuda baja (n = {int(foco.sum())})")  # fmt: skip
    for v in d["x"].quantile([1 / 3, 2 / 3]):
        ax.axvline(v, color="#999999", ls="--", lw=0.7)
    for v in d["y"].quantile([1 / 3, 2 / 3]):
        ax.axhline(v, color="#999999", ls="--", lw=0.7)
    rotulados = d[foco | (d["municipio_id"] == MADRID)].sort_values("x")
    # shortcut: desplazamientos a mano para estos 8 rótulos; si cambian los datos, zip(strict) falla y hay que recolocarlos
    separados = (
        (-95, 14),
        (-100, 0),
        (-10, -28),
        (15, -42),
        (45, -20),
        (10, 20),
        (6, 16),
        (-20, -25),
    )
    for (_, f), desplazamiento in zip(rotulados.iterrows(), separados, strict=True):
        ax.annotate(
            nombres[f["municipio_id"]], (f["x"], f["y"]), fontsize=8,
            xytext=desplazamiento, textcoords="offset points",
            arrowprops={"arrowstyle": "-", "lw": 0.4, "color": "#555555"},
        )  # fmt: skip
    ax.set(
        xlabel="Esfuerzo del alquiler en 2023 (% de la renta neta del hogar)",
        ylabel="Aceptadas por 1.000 jóvenes de 18 a 35 años",
    )
    ax.set_ylim(bottom=-4)  # sitio para los rótulos de los puntos en 0
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    sin = int((bono["grupo"] == "sin_dato").sum())
    pie = (
        f"{FUENTE_BONO}\nLíneas discontinuas: terciles. Tamaño del punto: raíz de la población joven. "
        f"{len(d)} municipios con esfuerzo; {sin} sin dato no aparecen."
    )
    fig.text(0.01, -0.02, pie, fontsize=8, color="#444444", va="top")
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)
