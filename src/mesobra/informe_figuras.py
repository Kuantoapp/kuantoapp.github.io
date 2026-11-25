"""Gráficos del informe técnico (#468), en SVG con el texto vivo y un globo por marca.

`python -m mesobra.informe_figuras` lee solo lo ya publicado (`app/datos/*.json`), `bono_inferencia.json` y,
para el error de la mediana y los testigos, `data/processed/alquiler_zona.parquet`; escribe `app/img/gNN.svg`.
No recalcula ninguna cifra del texto: los asserts comprueban que lo que dibuja coincide con lo publicado.
El titular, la fuente y la nota de cada gráfico van en `app/informe.html`, no en el SVG.
"""

import html
import json
import logging
import re
from pathlib import Path

import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap

from mesobra import esfuerzo as esf
from mesobra.alquiler import MIN_TESTIGOS, semiancho_lognormal
from mesobra.bono_inferencia import SALIDA as BONO_INFERENCIA
from mesobra.figuras import _clases, errores_cambio, es, leer_zonas
from mesobra.zonas import MADRID

LOG = logging.getLogger(__name__)
RAIZ = Path(__file__).resolve().parents[2]
APP = RAIZ / "app"
ALQUILER_ZONA = RAIZ / "data/processed/alquiler_zona.parquet"

# tokens de app/estilo.css
ACENTO = "#0b4f9c"
TINTA = "#0d1b2e"
TEXTO = "#1d1d1f"
TEXTO_2 = "#474a52"
APAGADO = "#5c6069"
LINEA = "#d9dbe0"
NEUTRO = "#a9adb6"
SUBE = "#b2182b"  # --pierdes
BAJA = "#01665e"  # --ganas
SIN_DATO = "#eceef1"
# rampa secuencial del acento, de clara a tinta (5 clases)
RAMPA = ["#dbe6f3", "#a9c3e3", "#6b98cc", "#2f6aae", "#0d3a73"]
ANCHO = 7.2  # pulgadas: el SVG se escala con la columna; el texto, en pt, sale a tamaño de lectura


def estilo() -> None:
    """rcParams comunes: texto SVG vivo en Instrument Sans, sin marcos ni rejillas por defecto."""
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    mpl.rcParams.update(
        {
            "svg.fonttype": "none",
            "svg.hashsalt": "kuanto",  # ids estables: el SVG no cambia si no cambian los datos
            "font.family": "sans-serif",
            "font.sans-serif": ["Instrument Sans", "DejaVu Sans"],
            "font.size": 9,
            "text.color": TEXTO,
            "axes.edgecolor": LINEA,
            "axes.labelcolor": TEXTO_2,
            "axes.labelsize": 8.5,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.spines.left": False,
            "axes.grid": False,
            "xtick.color": APAGADO,
            "ytick.color": APAGADO,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "xtick.major.size": 0,
            "ytick.major.size": 0,
            "axes.formatter.use_locale": False,
            "lines.solid_capstyle": "round",
        }
    )


def _rejilla(ax: plt.Axes, eje: str) -> None:
    ax.grid(axis=eje, color=LINEA, lw=0.6)
    ax.set_axisbelow(True)


def _formato(ax: plt.Axes, eje: str, sufijo: str = "", decimales: int = 0) -> None:
    f = mpl.ticker.FuncFormatter(lambda v, _: es(v, decimales) + sufijo)
    (ax.xaxis if eje == "x" else ax.yaxis).set_major_formatter(f)


def _globo(artista: mpl.artist.Artist, gid: str, texto: str, globos: dict) -> None:
    """Marca con `gid`; `guardar` le pone `<title>`, foco y `aria-label` con `texto`."""
    artista.set_gid(gid)
    globos[gid] = texto


def guardar(fig: plt.Figure, ruta: Path, globos: dict) -> None:
    """SVG transparente y sin fecha, con un globo accesible en cada marca de `globos`."""
    fig.savefig(
        ruta,
        format="svg",
        transparent=True,
        bbox_inches="tight",
        metadata={"Date": None},
    )
    plt.close(fig)
    svg = sin_estilos(ruta.read_text(encoding="utf-8"))
    for gid, texto in globos.items():
        t = html.escape(texto, quote=True)
        svg, n = re.subn(
            f'<g id="{re.escape(gid)}">',
            f'<g id="{gid}" class="marca" role="img" aria-label="{t}"><title>{t}</title>',
            svg,
            count=1,
        )
        if n != 1:
            raise ValueError(f"{ruta.name}: la marca {gid} no está en el SVG")
    ruta.write_text(svg, encoding="utf-8")


def sin_estilos(svg: str) -> str:
    """`style="a: b; …"` → atributos de presentación `a="b"`, sin `<style>`: la CSP del informe
    (`style-src 'self'`) bloquea los estilos en línea del SVG insertado en la página."""

    def atributos(m: re.Match) -> str:
        pares = (p.split(":", 1) for p in m.group(1).split(";") if p.strip())
        return " ".join(f'{k.strip()}="{v.strip()}"' for k, v in pares)

    svg = re.sub(r"<style[^>]*>.*?</style>", "", svg, flags=re.DOTALL)
    svg = re.sub(
        r"\s*<metadata>.*?</metadata>", "", svg, flags=re.DOTALL
    )  # RDF de matplotlib, sin uso
    svg = re.sub(r'style="([^"]*)"', atributos, svg)
    if "style=" in svg:
        raise ValueError("Queda un estilo en línea en el SVG")
    return svg.replace(
        "<svg ", '<svg stroke-linejoin="round" ', 1
    )  # sustituye al <style> de matplotlib


def leer_publicado() -> dict:
    return json.loads((APP / "datos/analisis.json").read_text(encoding="utf-8"))


def tabla_esfuerzo(aj: dict) -> pd.DataFrame:
    """Esfuerzo publicado por zona y año, con nulos fuera (secreto del INE o sin SERPAVI)."""
    return pd.DataFrame(aj["esfuerzo"]).dropna(subset=["esfuerzo"])


def nombres(zonas: gpd.GeoDataFrame) -> pd.Series:
    n = zonas.set_index("zona_id")["nombre"]
    # «Acebeda, La» → «La Acebeda»
    return n.str.replace(r"^(.*), (La|El|Los|Las)$", r"\2 \1", regex=True)


# ---------- capítulo 4: esfuerzo de 2024 ----------


def ic_esfuerzo(tabla: pd.DataFrame, zona: pd.DataFrame, anio: int) -> pd.DataFrame:
    """Esfuerzo de `anio` por zona con el semiancho de su IC 95 % (fracción) y sus testigos (#354)."""
    antes = tabla[(tabla["anio"] == anio) & (tabla["zona_id"] != MADRID)]
    t = antes.merge(
        zona[zona["anio"] == anio][
            ["zona_id", "testigos", "cuantia_p25", "cuantia_p75"]
        ],
        on="zona_id",
        validate="one_to_one",
    )
    semi = semiancho_lognormal(t["cuantia_p25"], t["cuantia_p75"], t["testigos"])
    t = t.assign(error=t["esfuerzo"] * semi)
    if len(t) != len(antes) or t["error"].isna().any():
        raise ValueError(
            f"{len(antes) - len(t)} zonas sin alquiler_zona o con error nulo en {anio}"
        )
    return t.set_index("zona_id")


def cortes_quintil(valores: pd.Series) -> list[float]:
    return np.quantile(valores, np.linspace(0, 1, 6)).tolist()


def cruza_corte(t: pd.DataFrame, cortes: list[float]) -> pd.Series:
    """True si el IC de la zona contiene alguno de los cortes interiores."""
    interiores = np.array(cortes[1:-1])
    lo = (t["esfuerzo"] - t["error"]).to_numpy()[:, None]
    hi = (t["esfuerzo"] + t["error"]).to_numpy()[:, None]
    return pd.Series(
        ((lo <= interiores) & (interiores <= hi)).any(axis=1), index=t.index
    )


def _leyenda_clases(fig: plt.Figure, cortes: list[float], caja: list[float]) -> None:
    """Leyenda en escalera, horizontal: una caja por clase con sus cortes debajo."""
    ax = fig.add_axes(caja)
    for i, c in enumerate(RAMPA):
        ax.add_patch(mpl.patches.Rectangle((i, 0), 0.94, 1, color=c, lw=0))
    for i, v in enumerate(cortes):
        ax.text(i - 0.03 if i else 0, -0.5, es(100 * v), ha="center" if i else "left", va="top", fontsize=7.5,
                color=APAGADO)  # fmt: skip
    ax.add_patch(
        mpl.patches.Rectangle(
            (5.4, 0), 0.6, 1, facecolor=SIN_DATO, edgecolor=NEUTRO, lw=0.5, hatch="////"
        )
    )
    ax.text(6.15, 0.5, "sin dato", va="center", fontsize=7.5, color=APAGADO)
    ax.add_patch(
        mpl.patches.Rectangle(
            (7.4, 0), 0.6, 1, facecolor="none", edgecolor=TINTA, lw=1.1
        )
    )
    ax.text(
        8.15,
        0.5,
        f"< {MIN_TESTIGOS} alquileres declarados",
        va="center",
        fontsize=7.5,
        color=APAGADO,
    )
    ax.text(0, 1.5, "% de la renta del hogar, quintiles", fontsize=7.5, color=TEXTO_2)
    ax.set(xlim=(0, 12), ylim=(-1.5, 2.2))
    ax.set_axis_off()


def _dibujar_zonas(
    ax: plt.Axes, g: gpd.GeoDataFrame, norm: BoundaryNorm, globos: dict
) -> None:
    """Una marca por zona (para su globo); las imprecisas con borde de tinta encima."""
    cmap = ListedColormap(RAMPA)
    for _, z in g.iterrows():  # una marca por zona: el globo necesita su propio <g>
        sin = pd.isna(z["valor"])
        color = SIN_DATO if sin else cmap(norm(z["valor"]))
        p = gpd.GeoSeries([z.geometry]).plot(
            ax=ax, color=color, edgecolor="white", lw=0.3, hatch="////" if sin else None
        )
        texto = f"{z['nombre_es']}: " + (
            "sin dato" if sin else f"{es(100 * z['valor'])} % de la renta del hogar"
        )
        if z["pocos"]:
            texto += f" (impreciso: {int(z['testigos'])} alquileres declarados)"
        _globo(p.collections[-1], f"z{z['zona_id']}{ax.get_label()}", texto, globos)
    if g["pocos"].any():
        g[g["pocos"]].plot(ax=ax, facecolor="none", edgecolor=TINTA, lw=1.0)


def g01_mapa_esfuerzo(t: pd.DataFrame, zonas: gpd.GeoDataFrame, ruta: Path) -> None:
    cortes = cortes_quintil(t["esfuerzo"])
    g = zonas.assign(
        valor=zonas["zona_id"].map(t["esfuerzo"]),
        testigos=zonas["zona_id"].map(t["testigos"]),
        nombre_es=zonas["zona_id"].map(nombres(zonas)),
    )
    g["pocos"] = g["valor"].notna() & (g["testigos"] < MIN_TESTIGOS)
    g["geometry"] = g.geometry.simplify(
        40
    )  # 40 m: invisible a esta escala y el SVG pesa una fracción
    norm = BoundaryNorm(cortes, len(RAMPA))
    globos: dict = {}
    fig = plt.figure(figsize=(ANCHO, 6.0))
    ax = fig.add_axes([0, 0, 0.56, 0.88], label="")
    madrid = g[g["tipo"] == "distrito"]
    _dibujar_zonas(ax, g[g["tipo"] == "municipio"], norm, globos)
    # la capital, sin globos en el mapa grande: los distritos se leen en el recuadro
    madrid.plot(
        ax=ax,
        color=[ListedColormap(RAMPA)(norm(v)) for v in madrid["valor"]],
        edgecolor="white",
        lw=0.2,
    )
    x0, y0, x1, y1 = madrid.total_bounds
    ax.add_patch(
        mpl.patches.Rectangle(
            (x0, y0), x1 - x0, y1 - y0, fill=False, ec=TEXTO_2, lw=0.6
        )
    )
    ax.set_axis_off()
    zoom = fig.add_axes([0.58, 0.12, 0.3, 0.66], label="d")
    _dibujar_zonas(zoom, madrid, norm, globos)
    zoom.set_axis_off()
    zoom.set_title("Madrid, 21 distritos", fontsize=8.5, color=TEXTO_2, loc="left")
    # rótulos de los distritos que nombra el texto, con línea guía hacia el margen derecho
    for zid, y in (
        ("2807905", 0.86),
        ("2807904", 0.72),
        ("2807901", 0.58),
        ("2807912", 0.38),
        ("2807913", 0.24),
    ):
        p = madrid.set_index("zona_id").geometry[zid].representative_point()
        zoom.annotate(f"{nombres(zonas)[zid]} {es(100 * t.at[zid, 'esfuerzo'])} %", (p.x, p.y),
                      xytext=(1.04, y), textcoords="axes fraction", fontsize=7.4, va="center", color=TEXTO,
                      arrowprops={"arrowstyle": "-", "lw": 0.5, "color": TEXTO_2, "shrinkA": 0, "shrinkB": 0})  # fmt: skip
    _leyenda_clases(fig, cortes, [0.02, 0.92, 0.6, 0.06])
    guardar(fig, ruta, globos)


def g02_franja_error(t: pd.DataFrame, nombre: pd.Series, ruta: Path) -> None:
    """Las 157 zonas ordenadas con su IC 95 %: en acento las que cruzan un corte de quintil."""
    cortes = cortes_quintil(t["esfuerzo"])
    cruza = cruza_corte(t, cortes)
    if (n := int(cruza.sum())) != 89:
        raise ValueError(
            f"El IC cruza un corte en {n} zonas; el informe publica 89 (#354)"
        )
    d = t.assign(cruza=cruza).sort_values("esfuerzo")
    x = np.arange(len(d))
    globos: dict = {}
    fig, ax = plt.subplots(figsize=(ANCHO, 3.4))
    for v in cortes[1:-1]:
        ax.axhline(100 * v, color=NEUTRO, lw=0.7, ls=(0, (2, 2)), zorder=1)
        ax.text(
            len(d) + 1.5, 100 * v, es(100 * v), va="center", fontsize=7.5, color=APAGADO
        )
    for xi, (zid, f) in zip(x, d.iterrows(), strict=True):
        color = ACENTO if f["cruza"] else NEUTRO
        (linea,) = ax.plot([xi, xi], [100 * (f["esfuerzo"] - f["error"]), 100 * (f["esfuerzo"] + f["error"])],
                           color=color, lw=1.1, alpha=0.75)  # fmt: skip
        ax.plot(xi, 100 * f["esfuerzo"], "o", ms=2.6, color=color, mec="white", mew=0.3)
        texto = f"{nombre[zid]}: {es(100 * f['esfuerzo'])} %, {int(f['testigos'])} alquileres declarados"
        _globo(
            linea,
            f"e{zid}",
            texto + (", su intervalo cruza un corte" if f["cruza"] else ""),
            globos,
        )
    ax.text(
        len(d) + 1.5,
        100 * cortes[-2] + 2.2,
        "cortes de\nquintil",
        fontsize=7,
        color=APAGADO,
        va="bottom",
    )
    techo = 32  # dos zonas con 10 y 11 alquileres declarados no caben: se corta; el pie del informe lo dice
    ax.text(2, techo - 1, f"{n} de {len(d)} zonas (en azul): su intervalo del 95 %\ncruza al menos un corte de quintil",
            fontsize=7.8, color=ACENTO, fontweight="semibold", va="top")  # fmt: skip
    ax.text(2, techo - 5.2, f"{len(d) - n} zonas (en gris): el intervalo queda dentro de su clase", fontsize=7.8,
            color=APAGADO, va="top")  # fmt: skip
    ax.set_ylim(4, techo)
    ax.set_xlim(-2, len(d) + 8)
    ax.set_xticks([])
    ax.set_xlabel(f"{len(d)} zonas, de menor a mayor esfuerzo")
    _formato(ax, "y", " %")
    _rejilla(ax, "y")
    guardar(fig, ruta, globos)


def g03_renta_alquiler(
    t: pd.DataFrame, nombre: pd.Series, zonas: gpd.GeoDataFrame, ruta: Path
) -> None:
    """Alquiler mediano frente a renta del hogar, con isolíneas de esfuerzo; los distritos en acento."""
    distritos = set(zonas.loc[zonas["tipo"] == "distrito", "zona_id"])
    globos: dict = {}
    fig, ax = plt.subplots(figsize=(ANCHO, 4.6))
    xmax = t["renta_hogar_mes"].max() * 1.06
    ymax = t["alquiler_mes_p50"].max() * 1.08
    for e in (0.15, 0.20, 0.25):
        ax.plot([0, xmax], [0, e * xmax], color=LINEA, lw=0.9, zorder=1)
        xe = min(xmax, ymax / e)  # donde la isolínea sale del gráfico
        ax.text(xe - 60, e * xe - 10, f"{es(100 * e, 0)} % de la renta", fontsize=7.2, color=APAGADO, ha="right",
                va="top")  # fmt: skip
    for zid, f in t.iterrows():
        dist = zid in distritos
        (p,) = ax.plot(f["renta_hogar_mes"], f["alquiler_mes_p50"], "o", ms=4.2 if dist else 3,
                       color=ACENTO if dist else NEUTRO, alpha=0.95 if dist else 0.6, mec="white", mew=0.4)  # fmt: skip
        texto = (f"{nombre[zid]}: alquiler {es(f['alquiler_mes_p50'], 0)} €, renta {es(f['renta_hogar_mes'], 0)} € "
                 f"al mes; esfuerzo {es(100 * f['esfuerzo'])} %")  # fmt: skip
        _globo(p, f"r{zid}", texto, globos)
    # shortcut: desplazamientos a mano de seis rótulos; si cambian los datos, revisar el render
    for z, dx, dy in (("2807901", -7, 4), ("2807913", -7, -9), ("2807905", -7, 6), ("2807904", -7, 5),
                      ("2807912", 7, 5), ("2807909", 7, -8)):  # fmt: skip
        ax.annotate(nombre[z], (t.at[z, "renta_hogar_mes"], t.at[z, "alquiler_mes_p50"]),
                    xytext=(dx, dy), textcoords="offset points", fontsize=7.6, color=TEXTO,
                    ha="left" if dx > 0 else "right")  # fmt: skip
    ax.set(xlim=(t["renta_hogar_mes"].min() * 0.9, xmax), ylim=(0, ymax))
    ax.set_xlabel("Renta neta media del hogar (€ al mes, 2024)")
    ax.set_ylabel("Alquiler mediano (€ al mes, 2024)")
    _formato(ax, "x")
    _formato(ax, "y")
    _rejilla(ax, "y")
    guardar(fig, ruta, globos)


# ---------- capítulo 5: cambio 2015-2024 ----------


def g04_madrid_serie(tabla: pd.DataFrame, zonas: gpd.GeoDataFrame, ruta: Path) -> None:
    """Madrid entero por año, sobre la banda entre el distrito más bajo y el más alto."""
    distritos = set(zonas.loc[zonas["tipo"] == "distrito", "zona_id"])
    m = tabla[tabla["zona_id"] == MADRID].set_index("anio")["esfuerzo"] * 100
    banda = (
        tabla[tabla["zona_id"].isin(distritos)]
        .groupby("anio")["esfuerzo"]
        .agg(["min", "max"])
        * 100
    )
    esperado = {2015: 19.1, 2020: 21.0, 2024: 19.6}
    if any(round(m[a], 1) != v for a, v in esperado.items()):
        raise ValueError(
            f"Madrid entero no coincide con lo publicado: {m.round(1).to_dict()}"
        )
    globos: dict = {}
    fig, ax = plt.subplots(figsize=(ANCHO, 3.0))
    ax.fill_between(
        banda.index, banda["min"], banda["max"], color=ACENTO, alpha=0.08, lw=0
    )
    ax.text(banda.index.min() + 0.1, banda.loc[banda.index.min(), "max"] + 0.4, "del distrito más bajo al más alto",
            fontsize=7.4, color=APAGADO)  # fmt: skip
    ax.plot(m.index, m.values, color=ACENTO, lw=2)
    for a, v in m.items():
        (p,) = ax.plot(
            a, v, "o", ms=7 if a in esperado else 0.1, color=ACENTO, mec="white", mew=1
        )
        _globo(p, f"m{a}", f"Madrid, {a}: {es(v)} %", globos)
        if a in esperado:
            ax.annotate(f"{es(v)} %", (a, v), xytext=(0, 8), textcoords="offset points", ha="center",
                        fontsize=8.5, fontweight="semibold", color=TEXTO)  # fmt: skip
    ax.set_xticks(m.index, [str(a) for a in m.index])
    _formato(ax, "y", " %")
    _rejilla(ax, "y")
    ax.set_ylim(banda["min"].min() - 1, banda["max"].max() + 1.5)
    guardar(fig, ruta, globos)


def g05_distritos(tabla: pd.DataFrame, zona: pd.DataFrame, nombre: pd.Series, zonas: gpd.GeoDataFrame,
                  ruta: Path) -> None:  # fmt: skip
    """Dumbbell 2015 → 2024 de los 21 distritos; color por clase frente a su propio error (#354)."""
    distritos = zonas.loc[zonas["tipo"] == "distrito", "zona_id"]
    clase = _clases(
        esf.cambio(tabla).drop(MADRID, errors="ignore"), errores_cambio(tabla, zona)
    )
    ancho = (
        tabla.pivot(index="zona_id", columns="anio", values="esfuerzo").loc[distritos]
        * 100
    )
    a0, a1 = ancho.columns.min(), ancho.columns.max()
    d = ancho[[a0, a1]].assign(clase=clase.reindex(ancho.index)).sort_values(a1)
    n = d["clase"].value_counts().reindex([0, 1, 2], fill_value=0)
    if n.tolist() != [3, 6, 12]:
        raise ValueError(
            f"Distritos baja / sin cambio / sube: {n.tolist()}; el informe publica 3 / 6 / 12"
        )
    colores = {0: BAJA, 1: NEUTRO, 2: SUBE}
    globos: dict = {}
    fig, ax = plt.subplots(figsize=(ANCHO, 5.6))
    for y, (zid, f) in enumerate(d.iterrows()):
        c = colores[f["clase"]]
        ax.plot(
            [f[a0], f[a1]],
            [y, y],
            color=LINEA if f["clase"] == 1 else c,
            lw=1.6,
            alpha=0.9,
            zorder=1,
        )
        ax.plot(f[a0], y, "o", ms=5, mfc="white", mec=NEUTRO, mew=1.2, zorder=2)
        (p,) = ax.plot(f[a1], y, "o", ms=6.5, color=c, mec="white", mew=0.8, zorder=3)
        dif = f[a1] - f[a0]
        texto = f"{nombre[zid]}: {es(f[a0])} % en {a0}, {es(f[a1])} % en {a1} ({'+' if dif > 0 else ''}{es(dif)} p. p.)"
        _globo(p, f"d{zid}", texto, globos)
        ax.text(27.2, y, ("+" if dif > 0 else "") + es(dif), va="center", ha="right", fontsize=7.8,
                color=TEXTO if f["clase"] != 1 else APAGADO)  # fmt: skip
    ax.set_yticks(range(len(d)), [nombre[z] for z in d.index], fontsize=8)
    ax.text(
        27.2, len(d) + 0.1, "cambio, p. p.", ha="right", fontsize=7.4, color=APAGADO
    )
    for i, (k, txt) in enumerate(
        (
            (2, "sube más que su error"),
            (1, "sin cambio claro"),
            (0, "baja más que su error"),
        )
    ):
        ax.plot(
            12.5 + 4.6 * i, len(d) + 0.3, "o", ms=6, color=colores[k], clip_on=False
        )
        ax.text(
            12.9 + 4.6 * i, len(d) + 0.3, txt, va="center", fontsize=7.4, color=TEXTO_2
        )
    ax.plot(
        12.5, len(d) + 1.3, "o", ms=5, mfc="white", mec=NEUTRO, mew=1.2, clip_on=False
    )
    ax.text(12.9, len(d) + 1.3, str(a0), va="center", fontsize=7.4, color=TEXTO_2)
    ax.set_xlim(12, 27.5)
    ax.set_ylim(-0.8, len(d) + 1.8)
    _formato(ax, "x", " %")
    _rejilla(ax, "x")
    guardar(fig, ruta, globos)


# ---------- capítulo 8: Bono Alquiler Joven ----------


def g06_aceptadas_esfuerzo(bono: pd.DataFrame, nombre: pd.Series, ruta: Path) -> None:
    """Proporción aceptada frente al esfuerzo de 2023, por municipio con esfuerzo; punto según solicitudes."""
    d = bono[(bono["solicitudes"] > 0) & bono["necesidad"].notna()].copy()
    total = bono["aceptadas"].sum() / bono["solicitudes"].sum()
    if (len(d), round(100 * total, 1)) != (134, 23.7):
        raise ValueError(
            f"{len(d)} municipios y {100 * total:.1f} %; se publican 134 y 23,7 %"
        )
    d["x"] = 100 * d["necesidad"] / d["poblacion_joven"]
    d["prop"] = 100 * d["aceptadas"] / d["solicitudes"]
    globos: dict = {}
    fig, ax = plt.subplots(figsize=(ANCHO, 3.9))
    ax.axhline(100 * total, color=ACENTO, lw=1.2, zorder=1)
    ax.text(d["x"].min(), 100 * total + 1.6, f"{es(100 * total)} %, toda la convocatoria", fontsize=7.4,
            color=ACENTO, va="bottom")  # fmt: skip
    for _, f in d.sort_values("solicitudes", ascending=False).iterrows():
        (m,) = ax.plot(f["x"], f["prop"], "o", ms=2.2 + 1.1 * f["solicitudes"] ** 0.25, color=TEXTO_2,
                       alpha=0.45, mec="white", mew=0.5)  # fmt: skip
        texto = (f"{nombre[f['municipio_id']]}: esfuerzo {es(f['x'])} %; {int(f['aceptadas'])} aceptadas de "
                 f"{int(f['solicitudes'])} solicitudes ({es(f['prop'])} %)")  # fmt: skip
        _globo(m, f"b{f['municipio_id']}", texto, globos)
    md = d[d["municipio_id"] == MADRID].iloc[0]
    ax.annotate("Madrid", (md["x"], md["prop"]), xytext=(-4, 22), textcoords="offset points", fontsize=7.8, ha="right",
                arrowprops={"arrowstyle": "-", "lw": 0.5, "color": APAGADO})  # fmt: skip
    ax.text(
        d["x"].min(),
        73,
        "Tamaño del punto: solicitudes del municipio",
        fontsize=7.2,
        color=APAGADO,
        va="top",
    )
    ax.set_ylim(-4, 75)
    ax.set_xlabel("Esfuerzo del alquiler en 2023 (% de la renta neta media del hogar)")
    ax.set_ylabel("Aceptadas sobre solicitudes")
    _formato(ax, "x", " %")
    _formato(ax, "y", " %")
    _rejilla(ax, "y")
    guardar(fig, ruta, globos)


def especificaciones(bi: dict) -> pd.DataFrame:
    """β del esfuerzo sobre las rechazadas por 1.000 jóvenes en las especificaciones de `bono_inferencia` cuyo β es
    el efecto del esfuerzo. Fuera, SAR, SLX y SDEM: su β es solo una parte (efectos directo e indirecto)."""
    e = bi["espacial"]
    r = bi["robustez_vivienda_alquilada"]
    filas = [
        ("Error espacial heterocedástico, 5 vecinos (principal)", e["k5"]["sem_het"], "principal"),
        ("Error espacial heterocedástico, 8 vecinos", e["k8"]["sem_het"], "espacial"),
        ("Error espacial heterocedástico, dos pasos, 5 vecinos", e["k5"]["sem_het_dos_pasos"], "espacial"),
        ("Error espacial, máxima verosimilitud, 5 vecinos", e["k5"]["sem"], "espacial"),
        ("Mínimos cuadrados", e["k5"]["ols"], "mco"),
        ("Mínimos cuadrados, errores robustos HAC", e["k5"]["ols_hac"], "mco"),
        ("Principal en los 112 municipios con % de alquiler", r["principal_misma_submuestra"]["espacial"]["k5"]["sem_het"], "control"),
        ("Con % de jóvenes en alquiler, 5 vecinos (112)", r["control_alquiler"]["k5"], "control"),
        ("Con % de jóvenes en alquiler, 8 vecinos (112)", r["control_alquiler"]["k8"], "control"),
    ]  # fmt: skip
    d = pd.DataFrame([(n, m["beta"], m["se"], m["p"], g) for n, m, g in filas],
                     columns=["modelo", "beta", "se", "p", "grupo"])  # fmt: skip
    # por punto de esfuerzo (el modelo lo mide en fracción); IC z asintótico, como da spreg
    return d.assign(
        b=d["beta"] / 100,
        lo=(d["beta"] - 1.96 * d["se"]) / 100,
        hi=(d["beta"] + 1.96 * d["se"]) / 100,
    )


def _fila_forest(ax: plt.Axes, yi: float, f: pd.Series, globos: dict) -> None:
    principal = f["grupo"] == "principal"
    c = ACENTO if principal else TEXTO_2
    ax.plot(
        [f["lo"], f["hi"]], [yi, yi], color=c, lw=1.6, alpha=0.9 if principal else 0.5
    )
    (p,) = ax.plot(
        f["b"], yi, "D" if principal else "o", ms=6, color=c, mec="white", mew=0.8
    )
    texto = (f"{f['modelo']}: {es(f['b'], 2)} rechazadas por 1.000 jóvenes por punto de esfuerzo "
             f"(IC 95 % {es(f['lo'], 2)} a {es(f['hi'], 2)}; p = {es(f['p'], 3)}; estimado)")  # fmt: skip
    _globo(p, f"f{int(yi)}", texto, globos)
    ax.text(2.75, yi, f"p = {es(f['p'], 3)}", va="center", ha="right", fontsize=7.4,
            color=ACENTO if f["p"] < 0.05 else APAGADO)  # fmt: skip


def g07_forest(bi: dict, ruta: Path) -> None:
    d = especificaciones(bi)
    if (
        round(d.at[0, "p"], 3) != 0.043
        or round(d.at[7, "p"], 2) != 0.22
        or round(d.at[5, "p"], 2) != 0.17
    ):
        raise ValueError(
            "Las p de bono_inferencia.json no son las publicadas (0,043, 0,17 y 0,22)"
        )
    globos: dict = {}
    fig, (ax, ar) = plt.subplots(
        2,
        1,
        figsize=(ANCHO, 5.2),
        height_ratios=[len(d), 2.4],
        gridspec_kw={"hspace": 0.55},
    )
    y = np.arange(len(d))[::-1]
    ax.axvline(0, color=TEXTO_2, lw=0.8)
    for yi, (_, f) in zip(y, d.iterrows(), strict=True):
        _fila_forest(ax, yi, f, globos)
    ax.axhspan(2.5, 4.5, color=LINEA, alpha=0.35, lw=0)
    ax.text(-0.95, 3.5, "sin W", ha="center", va="center", fontsize=6.8, color=APAGADO)
    ax.axhline(2.5, color=NEUTRO, lw=0.6, ls=(0, (2, 2)))
    ax.text(-0.95, 1, "n = 112", ha="center", va="center", fontsize=6.8, color=APAGADO)
    if (n0 := int((d["lo"] <= 0).sum())) != 5:
        raise ValueError(
            f"{n0} intervalos tocan el cero; el titular de G07 dice 5 de 9"
        )
    ax.set_yticks(y, d["modelo"], fontsize=7.8)
    ax.set_xlim(-1.1, 2.8)
    ax.set_xlabel(
        "Rechazadas por 1.000 jóvenes por cada punto de esfuerzo de más (IC 95 %; estimado)"
    )
    _formato(ax, "x", decimales=1)
    _rejilla(ax, "x")
    r = [("Correlación parcial, fijada antes de ver los datos", bi["pearson_parcial"]),
         ("Ídem, tasas suavizadas (Bayes empírico)", bi["pearson_parcial_eb"])]  # fmt: skip
    ar.axvline(0, color=TEXTO_2, lw=0.8)
    for yi, (n, m) in zip((1, 0), r, strict=True):
        ar.plot(m["ic95"], [yi, yi], color=TEXTO_2, lw=1.6, alpha=0.5)
        (p,) = ar.plot(m["r"], yi, "s", ms=6, color=TEXTO_2, mec="white", mew=0.8)
        _globo(p, f"r{yi}", f"{n}: r = {es(m['r'], 3)} (IC 95 % {es(m['ic95'][0], 2)} a {es(m['ic95'][1], 2)}; "
               f"p = {es(m['p'], 3)}; estimado)", globos)  # fmt: skip
        ar.text(
            0.48,
            yi,
            f"p = {es(m['p'], 3)}",
            va="center",
            ha="right",
            fontsize=7.4,
            color=APAGADO,
        )
    ar.set_yticks([1, 0], [n for n, _ in r], fontsize=7.8)
    ar.set_ylim(-0.6, 1.6)
    ar.set_xlim(-0.2, 0.5)
    ar.set_xlabel(
        "Correlación parcial del esfuerzo con las rechazadas por 1.000 jóvenes (otra escala)"
    )
    _formato(ar, "x", decimales=1)
    _rejilla(ar, "x")
    guardar(fig, ruta, globos)


# ---------- capítulo 6: seis sueldos ----------

PERFILES = (
    ("Persona sola con el SMI", "Persona sola con el SMI"),
    ("Teleoperador, 23 años, SMI", "Teleoperador de 23"),
    ("Pareja, 29 años, sueldo mediano", "Pareja de 29"),
    ("Madre sola, 34 años, administrativa", "Madre sola de 34"),
    ("Persona sola, 29 años, mediano de su edad", "Persona sola de 29"),
    ("Enfermera, 26 años, SERMAS", "Enfermera de 26"),
)
_NUM = r"(−?[\d.]+,\d+)"


def _num(s: str) -> float:
    return float(s.replace(".", "").replace(",", ".").replace("−", "-"))


def rinde_por_perfil(titulares: list[dict]) -> pd.DataFrame:
    """Neto por hora, mediana y cuartiles de lo que rinde la hora extra, leídos de los titulares publicados."""
    filas = []
    for etiqueta, prefijo in PERFILES:
        textos = [
            x["texto"]
            for x in titulares
            if x["texto"].startswith(prefijo) and "por hora extra" in x["texto"]
        ]
        t = textos[0] if textos else ""  # sin titular: falla abajo con su nombre
        m = re.search(
            rf"neto estimado de {_NUM} €.*mediana estimada de {_NUM} €.*cuartiles {_NUM} a {_NUM}\)",
            t,
        )
        if not m:
            raise ValueError(f"No se reconoce el titular de {prefijo}: {t[:120]}")
        filas.append((etiqueta, *map(_num, m.groups())))
    return pd.DataFrame(filas, columns=["perfil", "neto_hora", "mediana", "q1", "q3"])


def g08_sueldos(titulares: list[dict], ruta: Path) -> None:
    d = rinde_por_perfil(titulares)
    if d.at[0, "neto_hora"] != 8.80:
        raise ValueError("El neto por hora del SMI no es el publicado (8,80 €)")
    y = np.arange(len(d))[::-1]
    globos: dict = {}
    fig, ax = plt.subplots(figsize=(ANCHO, 3.4))
    ax.axvline(0, color=TEXTO_2, lw=0.8)
    for yi, (_, f) in zip(y, d.iterrows(), strict=True):
        (b,) = ax.plot(
            [f["q1"], f["q3"]],
            [yi, yi],
            color=NEUTRO,
            lw=7,
            alpha=0.7,
            solid_capstyle="butt",
        )
        ax.plot(f["mediana"], yi, "|", ms=11, mew=2, color=TEXTO)
        (n,) = ax.plot(
            f["neto_hora"], yi, "D", ms=6.5, color=ACENTO, mec="white", mew=0.8
        )
        ax.annotate("", (f["neto_hora"] - 0.25, yi), (f["q3"] + 0.2, yi),
                    arrowprops={"arrowstyle": "-", "color": ACENTO, "lw": 0.8, "ls": (0, (1.5, 2))})  # fmt: skip
        ax.text(
            f["neto_hora"] + 0.45,
            yi,
            f"{es(f['neto_hora'], 2)} €",
            va="center",
            fontsize=7.8,
            color=ACENTO,
        )
        _globo(b, f"q{yi}", f"{f['perfil']}: la mitad central de los pares rinde de {es(f['q1'], 2)} a "
               f"{es(f['q3'], 2)} € por hora extra de viaje (mediana {es(f['mediana'], 2)} €; estimado)", globos)  # fmt: skip
        _globo(
            n,
            f"n{yi}",
            f"{f['perfil']}: neto de {es(f['neto_hora'], 2)} € por hora trabajada (estimado)",
            globos,
        )
    ax.set_yticks(y, d["perfil"], fontsize=8)
    top = len(d) - 0.35
    ax.plot(
        [-6.6, -5.8],
        [top, top],
        color=NEUTRO,
        lw=7,
        alpha=0.7,
        solid_capstyle="butt",
        clip_on=False,
    )
    ax.text(
        -5.6,
        top,
        "mitad central de los pares (cuartiles)",
        va="center",
        fontsize=7.4,
        color=TEXTO_2,
    )
    ax.plot(2.6, top, "|", ms=9, mew=2, color=TEXTO, clip_on=False)
    ax.text(2.9, top, "mediana", va="center", fontsize=7.4, color=TEXTO_2)
    ax.plot(6.0, top, "D", ms=5.5, color=ACENTO, clip_on=False)
    ax.text(
        6.4, top, "neto por hora trabajada", va="center", fontsize=7.4, color=TEXTO_2
    )
    ax.set_xlim(-7, 16.5)
    ax.set_ylim(-0.6, len(d) - 0.1)
    ax.set_xlabel(
        "€ que rinde cada hora extra de viaje al trabajo frente a vivir más cerca (estimado)"
    )
    _formato(ax, "x", " €")
    _rejilla(ax, "x")
    guardar(fig, ruta, globos)


# ---------- capítulo 7: sobrecarga ----------

# Publicado en el informe y en docs/decisiones.md (2026-11-18): ECV 2025, intervalo con efecto de diseño 2;
# el modelo por zona (F3-06) da 47,0 a 47,3 % y no se publica por no pasar este control.
SOBRECARGA_ECV = (36.0, 28.6, 43.4)
SOBRECARGA_MODELO = (47.2, 47.0, 47.3)


def g10_sobrecarga(ruta: Path) -> None:
    globos: dict = {}
    fig, ax = plt.subplots(figsize=(ANCHO, 1.9))
    v, lo, hi = SOBRECARGA_ECV
    ax.axvspan(lo, hi, color=ACENTO, alpha=0.10, lw=0)
    (b,) = ax.plot([lo, hi], [1, 1], color=ACENTO, lw=2)
    (p,) = ax.plot(v, 1, "o", ms=9, color=ACENTO, mec="white", mew=1)
    _globo(
        p,
        "s-ecv",
        f"ECV 2025: {es(v)} % (intervalo del 95 %, {es(lo)} a {es(hi)}; estimado)",
        globos,
    )
    ax.text(
        v,
        1.32,
        f"{es(v)} %",
        ha="center",
        fontsize=10,
        fontweight="semibold",
        color=ACENTO,
    )
    ax.text(lo, 0.55, f"{es(lo)}", ha="center", fontsize=7.6, color=APAGADO)
    ax.text(hi, 0.55, f"{es(hi)}", ha="center", fontsize=7.6, color=APAGADO)
    m, mlo, mhi = SOBRECARGA_MODELO
    (q,) = ax.plot(m, 0, "o", ms=8, mfc="white", mec=SUBE, mew=1.6)
    ax.plot([mlo, mhi], [0, 0], color=SUBE, lw=2)
    _globo(q, "s-modelo", f"Modelo por zona: {es(m)} % ({es(mlo)} a {es(mhi)}), fuera del intervalo; no se publica",
           globos)  # fmt: skip
    ax.text(m + 1.2, 0, "modelo por zona: fuera del intervalo,\nno se publica", va="center", fontsize=7.6,
            color=SUBE)  # fmt: skip
    _globo(b, "s-ic", f"Intervalo del 95 % de la ECV: {es(lo)} a {es(hi)} %", globos)
    ax.set_yticks([1, 0], ["Encuesta de Condiciones\nde Vida 2025 (INE)", "Estimación por zona\n(ADRH y SERPAVI)"],
                  fontsize=8)  # fmt: skip
    ax.set_xlim(20, 62)
    ax.set_ylim(-0.6, 1.7)
    ax.set_xlabel(
        "% de hogares inquilinos que dedican más del 40 % de su renta a la vivienda (Comunidad de Madrid)"
    )
    _formato(ax, "x", " %")
    _rejilla(ax, "x")
    guardar(fig, ruta, globos)


# ---------- capítulo 9: simulación del Bono ----------

# € al mes en que el alquiler de 69 m² pasa del tope, persona sola con el SMI: publicados en el informe de #435
# (salen de pipeline_analisis.exceso_tope, que necesita los pares de tiempos; aquí solo se dibujan).
EXCESO_TOPE = {
    600: {"El Molar": 6.81, "Collado Mediano": 24.44, "Pedrezuela": 25.88, "Navacerrada": 26.19, "El Álamo": 32.15,
          "Villalbilla": 32.67, "Sevilla la Nueva": 51.31, "Manzanares el Real": 52.82, "Hoyo de Manzanares": 71.10,
          "Valdemorillo": 75.69},
    900: {"Boadilla del Monte": 31.98, "Villaviciosa de Odón": 51.93, "Majadahonda": 74.31, "Madrid": 79.51,
          "Las Rozas de Madrid": 88.60, "Pozuelo de Alarcón": 108.24},
}  # fmt: skip


def g11_tope(ruta: Path) -> None:
    filas = [
        (t, n, v)
        for t, m in EXCESO_TOPE.items()
        for n, v in sorted(m.items(), key=lambda x: -x[1])
    ]
    if len(filas) != 16 or sum(v < 80 for _, _, v in filas) != 14:
        raise ValueError(
            "El exceso sobre el tope no son los 16 municipios publicados (14 por menos de 80 €)"
        )
    globos: dict = {}
    fig, ax = plt.subplots(figsize=(ANCHO, 4.6))
    y, ys, grupos = 0, [], {}
    for t in (900, 600):
        grupo = [f for f in filas if f[0] == t]
        grupos[t] = (y, y + len(grupo) - 1)
        for _, n, v in grupo:
            c = ACENTO if v < 80 else TEXTO_2
            ax.plot([0, v], [y, y], color=c, lw=1.4, alpha=0.8)
            (p,) = ax.plot(v, y, "o", ms=6, color=c, mec="white", mew=0.8)
            _globo(
                p,
                f"t{len(ys)}",
                f"{n}: {es(v, 2)} € al mes por encima del tope de {t} € (estimado)",
                globos,
            )
            ax.text(
                v + 2.5, y, f"{es(v, 2)} €", va="center", fontsize=7.6, color=TEXTO_2
            )
            ys.append((y, n))
            y += 1
        y += 1.2
    ax.axvline(80, color=TEXTO_2, lw=0.8, ls=(0, (2, 2)))
    ax.text(80.8, -0.9, "80 € al mes", fontsize=7.4, color=TEXTO_2)
    for t, (a, b) in grupos.items():
        ax.text(-34, (a + b) / 2, f"Tope de\n{t} €", ha="center", va="center", fontsize=8, color=TEXTO_2,
                fontweight="semibold")  # fmt: skip
        ax.plot([-20.5, -20.5], [a - 0.3, b + 0.3], color=LINEA, lw=1.2, clip_on=False)
    ax.set_yticks([a for a, _ in ys], [n for _, n in ys], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, 125)
    ax.set_xlabel(
        "€ al mes en que el alquiler mediano de 69 m² pasa del tope del Bono (estimado)"
    )
    _formato(ax, "x", " €")
    _rejilla(ax, "x")
    guardar(fig, ruta, globos)


CRITERIOS = (
    ("bono_vigente", "Bono vigente\n(tope 600 / 900 €)"),
    ("alquiler_transporte", "Sin tope: alquiler y\ntransporte > 45 % del neto"),
    ("horas_viaje_sin_imputar", "Con horas de viaje,\nsin trayectos sin ruta"),
    ("horas_viaje", "Con horas de viaje,\nsin ruta = 120 min"),
)
PERFILES_SIM = (
    ("smi_30", "Persona sola con el SMI"),
    ("teleoperador_23", "Teleoperador, 23 años"),
    ("madre_oficina", "Madre sola, 34 años"),
    ("joven_mediano", "Persona sola, 29 años"),
    ("pareja_mediana", "Pareja, 29 años"),
    ("enfermera_26", "Enfermera, 26 años"),
)


def matriz_criterios(sim: pd.DataFrame) -> pd.DataFrame:
    """Municipios en que cada perfil cumple cada criterio; con la variante «_bruto» donde la hay."""
    s = sim[sim["perfil"].isin([p for p, _ in PERFILES_SIM])]
    n = s.groupby(["perfil", "criterio"])["elegible"].sum().unstack()
    total = s.groupby(["perfil", "criterio"])["municipio_id"].nunique().unstack()
    if (total[[c for c, _ in CRITERIOS]] != 138).any().any():
        raise ValueError(
            "La simulación no cubre los 138 municipios en todos los criterios"
        )
    return n


def g12_matriz(sim: pd.DataFrame, ruta: Path) -> None:
    n = matriz_criterios(sim)
    publicado = {("smi_30", "bono_vigente"): 122, ("smi_30", "alquiler_transporte"): 72,
                 ("teleoperador_23", "alquiler_transporte"): 65, ("madre_oficina", "alquiler_transporte"): 14,
                 ("joven_mediano", "bono_vigente"): 122, ("joven_mediano", "bono_vigente_bruto"): 0}  # fmt: skip
    if dif := {k: int(n.loc[k]) for k, v in publicado.items() if int(n.loc[k]) != v}:
        raise ValueError(f"Recuentos distintos de los publicados: {dif}")
    globos: dict = {}
    fig, ax = plt.subplots(figsize=(ANCHO, 3.5))
    cmap = mpl.colors.LinearSegmentedColormap.from_list(
        "k", ["#ffffff", RAMPA[1], RAMPA[3]]
    )
    for i, (p, etiqueta) in enumerate(PERFILES_SIM):
        for j, (c, _) in enumerate(CRITERIOS):
            v = int(n.at[p, c])
            bruto = f"{c}_bruto" if c != "horas_viaje_sin_imputar" else None
            vb = (
                int(n.at[p, bruto])
                if bruto in n.columns and pd.notna(n.at[p, bruto])
                else None
            )
            r = mpl.patches.Rectangle(
                (j, i), 0.96, 0.92, color=cmap(v / 138) if v else SIN_DATO, lw=0
            )
            ax.add_patch(r)
            oscuro = v / 138 > 0.6
            ax.text(j + 0.48, i + 0.42 if vb is None else i + 0.34, str(v), ha="center", va="center", fontsize=11,
                    fontweight="semibold", color="white" if oscuro else TEXTO)  # fmt: skip
            texto = f"{etiqueta}, {CRITERIOS[j][1].replace(chr(10), ' ')}: cumple en {v} de 138 municipios"
            if vb is not None:
                ax.text(j + 0.48, i + 0.68, f"con el bruto: {vb}", ha="center", va="center", fontsize=6.8,
                        color="white" if oscuro else TEXTO_2)  # fmt: skip
                texto += f" ({vb} si los ingresos se miden con el sueldo bruto)"
            _globo(r, f"c{i}{j}", texto + " (estimado)", globos)
    ax.set_xlim(0, len(CRITERIOS))
    ax.set_ylim(len(PERFILES_SIM), 0)
    ax.set_xticks(
        np.arange(len(CRITERIOS)) + 0.48, [e for _, e in CRITERIOS], fontsize=7.6
    )
    ax.xaxis.tick_top()
    ax.set_yticks(
        np.arange(len(PERFILES_SIM)) + 0.46, [e for _, e in PERFILES_SIM], fontsize=8
    )
    ax.spines["bottom"].set_visible(False)
    guardar(fig, ruta, globos)


# ---------- capítulo 10: fin del descuento ----------


def g13_descuento(sim: pd.DataFrame, zonas: gpd.GeoDataFrame, ruta: Path) -> None:
    # Madrid solo está por distritos, todos en la corona A: un municipio por fila, como en pipeline_analisis
    coronas = zonas.drop_duplicates("municipio_id").set_index("municipio_id")["corona"]
    f = sim[sim["criterio"].str.startswith("fin_")].assign(
        corona=lambda x: x["municipio_id"].map(coronas)
    )
    if f["corona"].isna().any():
        raise ValueError("Municipios del fin del descuento sin corona")
    t = f.groupby(["corona", "criterio", "perfil"])["eur_mes"].agg(["min", "max"])
    if (t["min"] != t["max"]).any():
        raise ValueError("El fin del descuento cambia dentro de una corona")
    t = t["min"].unstack(["criterio", "perfil"]).sort_index(ascending=False)
    bajo, alto, joven = (
        t[("fin_descuento_rdl", "adulto")],
        t[("fin_descuento", "adulto")],
        t[("fin_descuento", "joven")],
    )
    if (bajo.min(), alto.max(), joven.max()) != (9.23, 32.76, 9.30):
        raise ValueError(
            "El fin del descuento no da las cifras publicadas (9,23, 32,76 y 9,30 €)"
        )
    y = np.arange(len(t))
    globos: dict = {}
    fig, ax = plt.subplots(figsize=(ANCHO, 3.2))
    for yi, c in zip(y, t.index, strict=True):
        (r,) = ax.plot(
            [bajo[c], alto[c]],
            [yi, yi],
            color=ACENTO,
            lw=8,
            alpha=0.28,
            solid_capstyle="butt",
        )
        ax.plot(bajo[c], yi, "|", ms=12, mew=2, color=ACENTO)
        ax.plot(alto[c], yi, "|", ms=12, mew=2, color=ACENTO)
        ax.plot(joven[c], yi - 0.32, "s", ms=4.5, color=TEXTO_2)
        ax.text(
            alto[c] + 0.8,
            yi,
            f"{es(bajo[c], 2)} a {es(alto[c], 2)} €",
            va="center",
            fontsize=7.8,
        )
        _globo(r, f"k{c}", f"Corona {c}: de {es(bajo[c], 2)} a {es(alto[c], 2)} € más al mes para un adulto; "
               f"{es(joven[c], 2)} € con el Abono Joven (estimado)", globos)  # fmt: skip
    ax.text(
        joven.iloc[-1] + 0.8,
        y[-1] - 0.32,
        "Abono Joven",
        va="center",
        fontsize=7.2,
        color=TEXTO_2,
    )
    ax.set_yticks(y, [f"Corona {c}" for c in t.index], fontsize=8)
    ax.set_xlim(0, 42)
    ax.set_ylim(-0.7, len(t) - 0.4)
    ax.set_xlabel(
        "€ más al mes si en 2027 no se prorroga el descuento: solo la parte del RDL 17/2025 → todo (estimado)"
    )
    _formato(ax, "x", " €")
    _rejilla(ax, "x")
    guardar(fig, ruta, globos)


# ---------- capítulo 12: calidad del dato ----------


def g14_testigos(testigos: pd.Series, ruta: Path) -> None:
    """Histograma en escala logarítmica de los alquileres declarados por zona, con el umbral."""
    pocos = int((testigos < MIN_TESTIGOS).sum())
    if (len(testigos), pocos) != (158, 39):
        raise ValueError(
            f"Zonas {len(testigos)} y por debajo del umbral {pocos}; se publican 158 y 39"
        )
    bordes = np.r_[
        np.geomspace(testigos.min() * 0.95, MIN_TESTIGOS, 8)[:-1],
        np.geomspace(MIN_TESTIGOS, testigos.max() * 1.05, 20),
    ]  # el umbral es un borde
    fig, ax = plt.subplots(figsize=(ANCHO, 2.8))
    alto, _, barras = ax.hist(testigos, bins=bordes, color=NEUTRO, rwidth=0.88)
    for b, a in zip(barras, bordes[:-1], strict=True):
        if a < MIN_TESTIGOS:
            b.set_color(ACENTO)
    ax.axvline(MIN_TESTIGOS, color=TEXTO, lw=0.9, ls=(0, (2, 2)))
    ax.text(MIN_TESTIGOS * 0.92, alto.max() * 0.95, f"{pocos} zonas por debajo de {MIN_TESTIGOS}:\nvalor impreciso",
            ha="right", va="top", fontsize=7.8, color=ACENTO)  # fmt: skip
    ax.text(MIN_TESTIGOS * 1.1, alto.max() * 0.95, f"{len(testigos) - pocos} zonas", va="top", fontsize=7.8,
            color=TEXTO_2)  # fmt: skip
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: es(v, 0)))
    ax.set_xlabel(
        "Alquileres declarados de vivienda colectiva en el último año con dato (escala logarítmica)"
    )
    ax.set_ylabel("Zonas")
    _rejilla(ax, "y")
    guardar(fig, ruta, {})


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    estilo()
    aj = leer_publicado()
    tabla = tabla_esfuerzo(aj)
    zona = pd.read_parquet(ALQUILER_ZONA)
    zonas = leer_zonas()
    nombre = nombres(zonas)
    nombre[MADRID] = "Madrid"
    bi = json.loads(BONO_INFERENCIA.read_text(encoding="utf-8"))
    sim = pd.DataFrame(aj["simulacion"])
    alquiler = json.loads((APP / "datos/alquiler.json").read_text(encoding="utf-8"))[
        "zonas"
    ]
    testigos = pd.Series({k: v["testigos"] for k, v in alquiler.items()}).dropna()
    img = APP / "img"
    t24 = ic_esfuerzo(tabla, zona, 2024)
    g01_mapa_esfuerzo(t24, zonas, img / "g01.svg")
    g02_franja_error(t24, nombre, img / "g02.svg")
    g03_renta_alquiler(t24, nombre, zonas, img / "g03.svg")
    g04_madrid_serie(tabla, zonas, img / "g04.svg")
    g05_distritos(tabla, zona, nombre, zonas, img / "g05.svg")
    g06_aceptadas_esfuerzo(pd.DataFrame(aj["bono"]), nombre, img / "g06.svg")
    g07_forest(bi, img / "g07.svg")
    g08_sueldos(aj["titulares"], img / "g08.svg")
    g10_sobrecarga(img / "g10.svg")
    g11_tope(img / "g11.svg")
    g12_matriz(sim, img / "g12.svg")
    g13_descuento(sim, zonas, img / "g13.svg")
    g14_testigos(testigos, img / "g14.svg")


if __name__ == "__main__":
    main()
