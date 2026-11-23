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
FUENTE_SIMULACION = (
    "Tope de 600 € (900 € en los municipios del Anexo II), Acuerdo de 26-12-2024 (BOCM-20250110-20). Alquiler: SERPAVI "
    "(MIVAU) con el IPC de alquiler (INE).\nSimulación propia: es elegible el municipio, no se cobra la ayuda."
)
FUENTE_DESCUENTO = (
    "Fuente: tarifas del CRTM de 2026 (BOCM-20251231-3) y del 30-11-2025 (BOCM-20130130-9 y BOCM-20211217-35); "
    "RDL 17/2025, art. 8.\nCaso: 5 días a la semana, ida y vuelta; ruta por la zona A. Sin prórroga publicada a "
    "21-11-2026. Elaboración propia."
)
FUENTE_TITULARES = (
    "Fuente: elaboración propia con mesobra.calculo: SERPAVI (MIVAU) e IPC (INE), tiempos con los GTFS del CRTM, "
    "tarifas del CRTM, neto con la LIRPF de 2026.\nSueldos: SMI (RD 126/2026), EAES y EES (INE) llevados a 2026 "
    "con la ETCL (estimado), nómina del SERMAS de 2026 (BOCM-20260209-6). Todo estimado."
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

    `textos`: título de la leyenda, rótulo de cada clase y pie con la fuente. Las zonas con
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
        nota,
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
    _mapa(g, cortes, "YlOrRd", (titulo, _rangos(cortes), FUENTE_MAPAS), ruta)
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
    pie = f"Extremos: mínimo {con_signo(g['valor'].min())} y máximo {con_signo(g['valor'].max())} p. p.\n"
    _mapa(g, cortes, "RdBu_r", (titulo, etiquetas, pie + FUENTE_MAPAS), ruta)
    return int(g["valor"].isna().sum()), int(g["pocos"].sum())


def con_signo(x: float) -> str:
    """Fracción en puntos porcentuales con un decimal y «+» delante si es positiva."""
    return ("+" if x > 0 else "") + es(100 * x)


def mapa_bono_tope(
    elegible: pd.Series, testigos: pd.Series, zonas: gpd.GeoDataFrame, ruta: Path
) -> tuple[int, int]:
    """Municipios donde el perfil cumple el Bono vigente (`elegible` por `municipio_id`); los distritos de Madrid
    toman el valor del municipio. `testigos` por `zona_id` (de `alquiler.json`) marca el alquiler impreciso."""
    por_zona = zonas.set_index("zona_id")["municipio_id"].map(elegible.astype(float))
    g = _unir(zonas, por_zona)
    g = _marcar(g, testigos < MIN_TESTIGOS)
    etiquetas = ["fuera: el alquiler pasa del tope", "dentro"]
    titulo = "Persona sola con el SMI y el\nBono Alquiler Joven vigente\n(vivienda de 69 m²; estimado)"
    _mapa(g, [-0.5, 0.5, 1.5], "BrBG", (titulo, etiquetas, FUENTE_SIMULACION), ruta)
    return int(g["valor"].isna().sum()), int(g["pocos"].sum())


def fin_por_corona(fin: pd.DataFrame, coronas: pd.Series) -> pd.DataFrame:
    """€/mes por corona (filas) y (criterio, perfil) (columnas); falla si dentro de una corona no es constante."""
    t = fin.assign(corona=fin["municipio_id"].map(coronas))
    if t["corona"].isna().any():
        raise ValueError("Municipios del fin del descuento sin corona")
    g = t.groupby(["corona", "criterio", "perfil"])["eur_mes"]
    if (g.nunique() > 1).any():
        raise ValueError("El fin del descuento cambia dentro de una corona")
    return g.first().unstack(["criterio", "perfil"])


def fin_descuento_coronas(fin: pd.DataFrame, coronas: pd.Series, ruta: Path) -> None:
    """Por corona: rango del adulto entre `fin_descuento_rdl` y `fin_descuento`, y el joven."""
    t = fin_por_corona(fin, coronas).sort_index(ascending=False)
    y = np.arange(len(t))
    alto, bajo = t[("fin_descuento", "adulto")], t[("fin_descuento_rdl", "adulto")]
    joven = t[("fin_descuento", "joven")]
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.hlines(y, bajo, alto, color="#0b4f9c", lw=6, alpha=0.35)
    ax.scatter(
        bajo,
        y,
        color="#0b4f9c",
        zorder=3,
        label="Adulto: solo se retira la parte del RDL 17/2025",
    )
    ax.scatter(
        alto,
        y,
        color="#0b4f9c",
        marker="D",
        zorder=3,
        label="Adulto: se acaba todo el descuento",
    )
    ax.scatter(
        joven,
        y - 0.3,
        color="#8c510a",
        marker="s",
        zorder=3,
        label="Joven (Abono Joven): las dos cotas coinciden",
    )
    for yi, b, a, j in zip(y, bajo, alto, joven, strict=True):
        ax.annotate(
            f"{es(b, 2)} a {es(a, 2)} €",
            (a, yi),
            xytext=(8, -3),
            textcoords="offset points",
            fontsize=9,
        )
        ax.annotate(
            f"{es(j, 2)} €",
            (j, yi - 0.3),
            xytext=(8, -3),
            textcoords="offset points",
            fontsize=8,
            ha="left",
        )
    ax.set_yticks(y, [f"Corona {c}" for c in t.index])
    ax.set_xlim(0, 1.25 * alto.max())
    ax.set_xlabel(
        "€ más al mes si no se prorroga el descuento (media del año; estimado)"
    )
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.2),
        frameon=False,
        fontsize=8,
        ncols=1,
    )
    fig.text(0.01, -0.2, FUENTE_DESCUENTO, fontsize=8, color="#444444", va="top")
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)  # fmt: skip


# etiquetas cortas, en el orden de `titulares.PERFILES` (zip estricto: falla si cambia el número de perfiles)
PERFILES_CORTOS = (
    "Sola, SMI",
    "Teleoperador, 23, SMI",
    "Pareja, 29, mediano",
    "Madre sola, 34, oficina",
    "Sola, 29, mediano de su edad",
    "Enfermera, 26, SERMAS",
)


def titulares_perfiles(res: list[tuple[dict, dict]], ruta: Path) -> None:
    """Dos paneles por perfil: % de pares en que vivir lejos rinde al menos el neto por hora, y zonas con sobrante
    mediano negativo con la banda del alquiler (P25 a P75)."""
    r = [x for _, x in res]
    etiquetas = [e for e, _ in zip(PERFILES_CORTOS, res, strict=True)]
    y = np.arange(len(r))[::-1]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 4.2), sharey=True)
    a1.scatter([x["pct_encima"] for x in r], y, color="#0b4f9c", zorder=3)
    a1.set_xlim(0, 20)
    a1.set_xlabel(
        "% de pares origen-destino en que\nvivir lejos rinde ≥ el neto por hora"
    )
    neg = np.array([x["n_zonas_negativas"] for x in r])
    lo, hi = np.array([x["banda_zonas_negativas"] for x in r]).T
    a2.hlines(
        y,
        lo,
        hi,
        color="#0b4f9c",
        lw=5,
        alpha=0.3,
        label="banda: alquiler del P25 al P75",
    )
    a2.scatter(neg, y, color="#0b4f9c", zorder=3, label="alquiler mediano")
    a2.set_xlim(0, max(hi.max(), 1) * 1.15)
    a2.set_xlabel(
        f"zonas (de {r[0]['n_zonas']}) con sobrante\nmensual mediano negativo"
    )
    a2.legend(loc="lower right", frameon=False, fontsize=8)
    a1.set_yticks(y, etiquetas)
    for a in (a1, a2):
        a.spines[["top", "right"]].set_visible(False)
        a.grid(axis="x", color="#dddddd", lw=0.5)
    fig.text(0.01, -0.04, FUENTE_TITULARES, fontsize=8, color="#444444", va="top")
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)  # fmt: skip


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
