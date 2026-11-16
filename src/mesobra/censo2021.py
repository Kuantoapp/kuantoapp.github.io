"""Censo 2021 del INE a medida: personas en viviendas familiares por municipio, edad quinquenal y tenencia.

`python -m mesobra.censo2021` descarga la consulta (Comunidad de Madrid, 179 municipios) a
`data/raw/ine_censo2021_tenencia_edad_municipios_<fecha>.xml`, sin sobrescribir, y muestra su SHA-256.
`pct_alquiler_joven()` da el porcentaje de personas de 20 a 34 años que viven de alquiler por municipio.

Formato (SpreadsheetML en ISO-8859-1, sin etiquetas de columna): 5 filas de metadatos, la fila «Total» y una
fila por municipio con 107 valores: por cada edad (Total, 0-4, ..., 100+) cinco columnas (Total, En propiedad,
En alquiler, Otro régimen, No consta); las tres últimas edades traen cuatro (sin «No consta»). Una celda sin
texto es secreto estadístico (nulo, no cero); «0,00» es un cero publicado. Se valida el formato en `_leer`.

Cada consulta vuelve a sortear el redondeo al azar a múltiplos de 3 del INE: una descarga nueva cambia el
SHA-256 y hasta ±3 por celda con la misma supresión. Vale el fichero con fecha de `data/raw/`.

Supuestos de la robustez del Bono (`bono_inferencia.robustez_vivienda_alquilada`), con su magnitud:
- El porcentaje en alquiler se correlaciona con el esfuerzo (+0,27) y con la renta (-0,35) en los 112 municipios de
  la robustez (`correlacion_porcentaje` del JSON): es el mecanismo que atenúa r al usarlo de denominador.
- Aplicar el de 2021 a 2023 solo sesga si el cambio entre 2021 y 2023 difiere entre municipios.
- 20-34 representa a 18-35: faltan 3 de las 18 edades (18, 19 y 35), ≈17 % del grupo si la población se reparte por
  igual; sesga r solo si el alquiler de esas edades difiere entre municipios.
- El denominador es «jóvenes en vivienda alquilada», no «inquilinos»: incluye a quien vive en el piso alquilado de sus padres.
Fuente: Elaboración propia con datos extraídos del sitio web del INE: www.ine.es
"""

import hashlib
import html
import http.cookiejar
import io
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from http.client import HTTPException
from pathlib import Path
from typing import BinaryIO

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data/raw"
CENSO = RAW / "ine_censo2021_tenencia_edad_municipios_2026-11-16.xml"
BASE = "https://www.ine.es/Censo2021/"
NOMBRE = "ine_censo2021_tenencia_edad_municipios"
NS = {"s": "urn:schemas-microsoft-com:office:spreadsheet"}
VALORES = 107
GRUPOS_20_34 = (5, 6, 7)  # 20-24, 25-29 y 30-34 (el grupo 0 es «Total» y el 1, «0-4»)
MUNICIPIOS = 179
# cada celda redondeada se desvía hasta 2: el Total frente a la suma de cuatro (2 + 4 × 2)
TOLERANCIA = 10
# 21 totales de edad frente al Total de la fila (21 × 2 + 2)
TOLERANCIA_TOTAL = 44
# cada celda se desvía hasta ±2: con 6 celdas y 300 personas el porcentaje se mueve hasta ~3 puntos en el peor
# caso ((150 + 6) / (300 - 6) = 0,531 frente a 0,5), mucho menos en el típico
MIN_JOVENES_20_34 = 300
METADATOS = (
    "[Municipio de residencia]",
    "[Edad (grupos quinquenales), Régimen de tenencia de la vivienda]",
    "(Periodo=[[2021]])",
    "[Personas]",
)


def _abrir(
    opener: urllib.request.OpenerDirector,
    url: str,
    datos: list[tuple[str, str]] | None = None,
) -> bytes:
    if not url.startswith(BASE):
        raise ValueError(f"Solo {BASE}: {url}")
    cuerpo = urllib.parse.urlencode(datos).encode() if datos is not None else None
    for intento in range(3):
        try:
            with opener.open(url, cuerpo, timeout=300) as r:
                if not r.url.startswith("https://www.ine.es/"):
                    raise ValueError(f"{url} redirige a {r.url}")
                return r.read()
        except OSError, HTTPException:
            if intento == 2:
                raise
            time.sleep(3)
    raise AssertionError("inalcanzable")


def _consulta() -> bytes:
    """Recorre el asistente del Censo 2021 con una sesión HTTP nueva y devuelve el XML de la tabla."""
    sesion = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
    )
    sesion.addheaders = [("User-Agent", "dm-nueva-fuente/1.0")]
    _abrir(sesion, BASE + "Inicio.do")
    _abrir(sesion, BASE + "Wizard.do?WIZARD=1&reqCode=pasoSeleccionAccion")
    pagina = _abrir(
        sesion, BASE + "Wizard.do?WIZARD=4&reqCode=pasoSeleccionGeografia"
    ).decode("utf-8")
    madrid = r"\[RESIDENCIA\]\.\[Todo RESIDENCIA\]\.\[Madrid, Comunidad de\]\.\[28 Madrid\]\.\[28\d{3} [^\"]*\]"
    municipios = [
        html.unescape(m) for m in re.findall(f'<option value="({madrid})"', pagina)
    ]
    if len(municipios) != 179:
        raise ValueError(
            f"Se esperaban 179 municipios de Madrid y hay {len(municipios)}"
        )
    _abrir(
        sesion,
        BASE + "Wizard.do",
        [
            ("reqCode", "pasoSeleccionElementosGeografia"),
            ("WIZARD", "4"),
            ("areaOrigen", "municipios"),
            ("desglose", ""),
            *[("elementosGeograficosOrigenSeleccionados", m) for m in municipios],
        ],
    )
    _abrir(
        sesion, BASE + "Wizard.do?WIZARD=2&reqCode=pasoSeleccionColectivo"
    )  # viviendas familiares
    _abrir(
        sesion,
        BASE + "Informe.do",
        [
            ("reqCode", "iniciar"),
            ("jerarquiasSeleccionada", ""),
            ("WIZARD", "2"),
            ("pagina4", "4"),
            ("tipoInforme", "LIBRE"),
            ("idFila", "L_[RESIDENCIA].[DESC_RESIDENCIA_N3]"),
            ("idColumna", "L_[GRUPO_Q_EDAD].[DESC_GRUPO_Q_EDAD]"),
            ("idColumna", "L_[TENEN_VIV].[DESC_TENEN_VIV]"),
            ("medidas", "[Measures].[SPERSONASSUM]"),
        ],
    )
    return _abrir(sesion, BASE + "Informe.do?reqCode=xml")


def descargar(raw: Path = RAW, hoy: date | None = None) -> Path:
    """Guarda la consulta en `raw` con la fecha en el nombre; nunca sobrescribe (modo `xb`)."""
    final = raw / f"{NOMBRE}_{(hoy or date.today()).isoformat()}.xml"
    if final.exists():
        raise FileExistsError(f"Ya existe {final}: data/raw no se sobrescribe")
    datos = _consulta()
    _leer(io.BytesIO(datos))  # un HTML o un XML de otro formato no llega a data/raw
    with final.open("xb") as f:
        f.write(datos)
    return final


def _celdas(fila: ET.Element) -> list[str | None]:
    return [
        getattr(c.find("s:Data", NS), "text", None) for c in fila.findall("s:Cell", NS)
    ]


def _leer(ruta: Path | BinaryIO = CENSO) -> pd.DataFrame:
    """Total y alquiler de cada grupo de 20-34 por municipio (nulo si el INE lo suprime), con el formato validado."""
    filas = ET.parse(ruta).getroot().findall(".//s:Row", NS)
    meta = tuple(_celdas(f)[1] for f in filas[1:5])
    if meta != METADATOS:
        raise ValueError(f"Metadatos distintos de los esperados: {meta}")
    celdas = [_celdas(f) for f in filas[5:]]
    if celdas[0][0] != "Total" or any(len(c) != VALORES + 1 for c in celdas):
        raise ValueError(f"Filas sin {VALORES} valores o sin fila «Total» al principio")
    m = pd.DataFrame(celdas).set_index(0)
    etiquetas = m.index[1:]
    if (
        len(etiquetas) != MUNICIPIOS
        or not etiquetas.str[:5].is_unique
        or not etiquetas.str.fullmatch(r"28\d{3} .+").all()
    ):
        raise ValueError(
            f"Se esperaban {MUNICIPIOS} municipios únicos con código 28xxx y hay {len(etiquetas)}"
        )
    m = m.apply(lambda c: pd.to_numeric(c.str.replace(",", "."), errors="raise"))
    m.columns = range(VALORES)
    # el orden de las edades se comprueba con el Total: sus 21 totales de edad suman el total de la fila
    posiciones = [5 * g for g in range(1, 19)] + [95 + 4 * g for g in range(3)]
    if abs(m.iloc[0, posiciones].sum() - m.iloc[0, 0]) > TOLERANCIA_TOTAL:
        raise ValueError("Los grupos de edad de la fila «Total» no suman el total")
    for g in GRUPOS_20_34:
        t, partes = m[5 * g], m[[5 * g + i for i in (1, 2, 3, 4)]]
        completo = partes.notna().all(axis=1) & t.notna()
        if ((t - partes.sum(axis=1)).abs()[completo] > TOLERANCIA).any():
            raise ValueError(
                f"Total distinto de propiedad + alquiler + otro + no consta en el grupo {g}"
            )
    salida = pd.DataFrame(
        {
            "total": sum(m[5 * g] for g in GRUPOS_20_34),
            "alquiler": sum(m[5 * g + 2] for g in GRUPOS_20_34),
        }
    )  # la suma de Series con NaN deja NaN: falta una pieza, falta el municipio
    salida.index = salida.index.str[:5]
    return salida.drop(index="Total")


def recuento(ruta: Path = CENSO) -> dict:
    """Municipios con porcentaje, con alguna pieza suprimida y bajo el umbral (con las piezas completas): suman el total."""
    d = _leer(ruta)
    suprimidos = d["total"].isna() | d["alquiler"].isna()
    bajo = ~suprimidos & (d["total"] < MIN_JOVENES_20_34)
    return {
        "suprimidos": int(suprimidos.sum()),
        "bajo_umbral": int(bajo.sum()),
        "con_porcentaje": int((~suprimidos & ~bajo).sum()),
    }


def pct_alquiler_joven(ruta: Path = CENSO) -> pd.Series:
    """Fracción de personas de 20 a 34 años en alquiler por `municipio_id` (código INE de 5 cifras).

    (alquiler 20-24 + 25-29 + 30-34) / (total de esos grupos, con «No consta»). Nulo si el INE suprime
    alguna celda o si el total es menor que `MIN_JOVENES_20_34`.
    """
    d = _leer(ruta)
    return (
        (d["alquiler"] / d["total"])
        .where(d["total"] >= MIN_JOVENES_20_34)
        .rename("alquiler_joven")
    )


if __name__ == "__main__":
    final = descargar()
    sys.stdout.write(
        f"{final}\nSHA-256 {hashlib.sha256(final.read_bytes()).hexdigest()}\n"
    )
