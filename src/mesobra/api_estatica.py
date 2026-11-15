"""Contrato de los ficheros de la API estática de `app/datos/` (sección 2 del plan de desarrollo).

Solo librería estándar (el MCP lo importa sin pandas). Cada fichero lleva un bloque `meta`:
fecha, año del dato y fuentes con nombre, URL y licencia. Los ejemplos son inventados.
"""

import json
import math
import re
from collections import Counter
from datetime import date
from pathlib import Path

CORONAS = ["A", "B1", "B2", "B3", "C1", "C2"]
VIAJES_DIA = [2, 4]
MAX_PROBLEMAS = 20
# Caja de la Comunidad de Madrid en EPSG:4326: un 25830 sin reproyectar o lon/lat al revés caen fuera.
LON, LAT = (-4.7, -2.9), (39.8, 41.3)


# Municipio INE o Madrid (28079) + distrito 01-21
MUN = r"28\d{3}"
ZONA = MUN + r"|28079(0[1-9]|1\d|2[01])"


def _regex(patron):
    return lambda v: isinstance(v, str) and re.fullmatch(patron, v) is not None


def _es_fecha(v):
    try:
        return isinstance(v, str) and bool(date.fromisoformat(v))
    except ValueError:
        return False


_TIPOS = {
    "texto": lambda v: isinstance(v, str) and v.strip() != "",
    "entero": lambda v: type(v) is int,  # excluye bool y numpy
    "decimal": lambda v: type(v) in (int, float) and math.isfinite(v),
    "booleano": lambda v: type(v) is bool,
    "fecha": _es_fecha,
    "url": _regex(r"https?://\S+"),
    "zona": _regex(ZONA),
    "municipio": _regex(MUN),
    "destino": _regex(ZONA + "|polo:[a-z0-9_-]+"),
}


def _campo(ruta, v, spec):
    """Problemas de un valor. `spec`: tipo (con `?` si admite null), lista de valores o `(tipo, lo, hi)`."""
    if isinstance(v, float) and math.isnan(v):
        return [f"{ruta}: NaN, usa null"]
    if isinstance(spec, list):
        return [] if v in spec else [f"{ruta}: {v!r} no está en {spec}"]
    tipo, lo, hi = spec if isinstance(spec, tuple) else (spec, None, None)
    if v is None:
        return [] if tipo.endswith("?") else [f"{ruta}: no admite null"]
    if not _TIPOS[tipo.rstrip("?")](v):
        return [f"{ruta}: se esperaba {tipo.rstrip('?')} y hay {v!r}"]
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        return [f"{ruta}: {v} fuera del rango [{lo}, {hi}]"]
    return []


def _registro(ruta, obj, campos, opcionales=()):
    """Claves exactas de un objeto; un spec `None` se valida aparte."""
    if not isinstance(obj, dict):
        return [f"{ruta}: se esperaba un objeto"]
    p = []
    if faltan := [k for k in campos if k not in obj and k not in opcionales]:
        p.append(f"{ruta}: faltan claves {faltan}")
    if sobran := [k for k in obj if k not in campos]:
        p.append(f"{ruta}: sobran claves {sobran}")
    for k, spec in campos.items():
        if spec is not None and k in obj:
            p += _campo(f"{ruta}.{k}", obj[k], spec)
    return p


def _repetidos(ruta, valores):
    repetidos = sorted(v for v, n in Counter(valores).items() if n > 1)
    return [f"{ruta}: repetidos {repetidos}"] if repetidos else []


def _tabla(ruta, filas, campos, clave, opcionales=()):
    """Lista no vacía de registros con `clave` única."""
    if not isinstance(filas, list) or not filas:
        return [f"{ruta}: se esperaba una lista no vacía"]
    p = []
    for i, fila in enumerate(filas):
        p += _registro(f"{ruta}[{i}]", fila, campos, opcionales)
    if not p and clave:
        p += _repetidos(ruta, [tuple(f[c] for c in clave) for f in filas])
    return p


def _lista(ruta, valores, spec):
    if not isinstance(valores, list) or not valores:
        return [f"{ruta}: se esperaba una lista no vacía"]
    p = [m for i, v in enumerate(valores) for m in _campo(f"{ruta}[{i}]", v, spec)]
    return p or _repetidos(ruta, valores)


def _matriz(ruta, m, filas, cols, spec):
    if not isinstance(m, list) or len(m) != filas:
        return [f"{ruta}: se esperaban {filas} filas"]
    p = []
    for i, fila in enumerate(m):
        if not isinstance(fila, list) or len(fila) != cols:
            p.append(f"{ruta}[{i}]: se esperaban {cols} columnas")
        else:
            for j, v in enumerate(fila):
                p += _campo(f"{ruta}[{i}][{j}]", v, spec)
    return p


def _items(obj, clave):
    v = obj.get(clave)
    return v if isinstance(v, list) else []


def _mapa(ruta, obj, claves, validar_valor):
    """Objeto con exactamente `claves`, cada valor validado por `validar_valor(ruta, valor)`."""
    p = _registro(ruta, obj, dict.fromkeys(claves))
    for k in obj if isinstance(obj, dict) else ():
        p += validar_valor(f"{ruta}.{k}", obj[k]) if k in claves else []
    return p


ENT, POS = ("entero", 0, None), ("decimal", 0, None)
POS_N, PCT = ("decimal?", 0, None), ("decimal?", 0, 100)
ANIO = ("entero", 2000, 2100)
META = {"generado": "fecha", "anio_dato": ANIO, "fuentes": None, "nota": "texto"}
FUENTE = {"nombre": "texto", "url": "url", "licencia": "texto"}


def _raiz(o, campos, opcionales=()):
    p = _registro("$", o, {"meta": None, **campos}, opcionales)
    if "meta" not in o:
        return p
    meta = o["meta"]
    fuentes = meta.get("fuentes") if isinstance(meta, dict) else None
    p += _registro("meta", meta, META, ("nota",))
    return p + _tabla("meta.fuentes", fuentes, FUENTE, ("nombre",))


# fmt: off
PROPIEDADES = {
    "zona_id": "zona", "nombre": "texto", "tipo": ["municipio", "distrito"],
    "municipio_id": "municipio", "corona": CORONAS, "poblacion": ENT,
}
# fmt: on
GEOMETRIA = {"type": ["Polygon", "MultiPolygon"], "coordinates": None}


def _posicion(x):
    return isinstance(x, list) and len(x) == 2 and all(_TIPOS["decimal"](c) for c in x)


def _anillo(ruta, a):
    if not isinstance(a, list) or len(a) < 4 or not all(_posicion(x) for x in a):
        return [f"{ruta}: se esperaba un anillo de al menos 4 posiciones [lon, lat]"]
    p = (
        []
        if a[0] == a[-1]
        else [f"{ruta}: anillo abierto (primera y última distintas)"]
    )
    if fuera := [
        v for v in a if not (LON[0] <= v[0] <= LON[1] and LAT[0] <= v[1] <= LAT[1])
    ]:
        msg = f"{len(fuera)} vértices fuera de la Comunidad de Madrid en EPSG:4326"
        p.append(f"{ruta}: {msg} (p. ej. {fuera[0]}); ¿EPSG:25830 o lat/lon al revés?")
    return p


def _poligono(ruta, anillos):
    if not isinstance(anillos, list) or not anillos:
        return [f"{ruta}: se esperaba una lista no vacía de anillos"]
    return [m for i, a in enumerate(anillos) for m in _anillo(f"{ruta}[{i}]", a)]


def _geometria(ruta, g):
    # shortcut: sin orden de anillos (RFC 7946) ni validez topológica; usar shapely cuando F1-08 tenga geometrías reales
    p = _registro(ruta, g, GEOMETRIA)
    if p:
        return p
    ruta, c = f"{ruta}.coordinates", g["coordinates"]
    if g["type"] == "Polygon":
        return _poligono(ruta, c)
    if not isinstance(c, list) or not c:
        return [f"{ruta}: se esperaba una lista no vacía de polígonos"]
    return [m for i, x in enumerate(c) for m in _poligono(f"{ruta}[{i}]", x)]


def _coherencia_zonas(props):
    p = []
    for i, x in enumerate(props):
        if x["tipo"] == "distrito":
            bien = x["municipio_id"] == "28079" and len(x["zona_id"]) == 7
        else:
            # 28079 es Madrid entero: sus zonas son los 21 distritos
            bien = x["zona_id"] == x["municipio_id"] != "28079"
        if not bien:
            p.append(
                f"properties[{i}]: zona_id y municipio_id no casan con tipo {x['tipo']}"
            )
    return p


def _zonas(o):
    p = _raiz(o, {"type": ["FeatureCollection"], "features": None})
    features = _items(o, "features")
    if not features:
        return p + ["features: se esperaba una lista no vacía"]
    shell = {"type": ["Feature"], "geometry": None, "properties": None}
    for i, f in enumerate(features):
        p += _registro(f"features[{i}]", f, shell)
        if isinstance(f, dict):
            p += _geometria(f"features[{i}].geometry", f.get("geometry"))
    props = [f.get("properties") for f in features if isinstance(f, dict)]
    q = _tabla("properties", props, PROPIEDADES, ("zona_id",))
    return p + (q or _coherencia_zonas(props))


DESTINO = {"destino_id": "destino", "nombre": "texto", "tipo": ["zona", "polo"]}


def _destinos(destinos):
    p = _tabla("destinos", destinos, DESTINO, ("destino_id",))
    return p or [
        f"destinos[{i}]: tipo {d['tipo']!r} no casa con {d['destino_id']!r}"
        for i, d in enumerate(destinos)
        if (d["tipo"] == "polo") != d["destino_id"].startswith("polo:")
    ]


OPCIONALES = ("coche", "km_coche", "coste_coche")


def _tiempos(o):
    p = _raiz(o, dict.fromkeys(["origenes", "destinos", "tp", *OPCIONALES]), OPCIONALES)
    p += _lista("origenes", o.get("origenes"), "zona") + _destinos(o.get("destinos"))
    filas, cols = len(_items(o, "origenes")), len(_items(o, "destinos"))
    minutos, km = ("entero?", 0, 120), POS_N
    p += _matriz("tp", o.get("tp"), filas, cols, minutos)
    p += _matriz("coche", o["coche"], filas, cols, minutos) if "coche" in o else []
    p += _matriz("km_coche", o["km_coche"], filas, cols, km) if "km_coche" in o else []
    if "coste_coche" in o:
        p += _registro("coste_coche", o["coste_coche"], {"eur_km": POS})
    return p


# fmt: off
ALQUILER = {
    "anio": ("entero?", 2000, 2100), "p25": PCT, "p50": PCT, "p75": PCT, "m2": POS_N,
    "factor_ipc": ("decimal", 0.5, 2), "ic": None,
    "origen": ["observado", "estimado", "sin_dato"],
}
# fmt: on


def _ic(ruta, z):
    ic = z["ic"]
    if z["origen"] != "estimado":
        return [] if ic is None else [f"{ruta}.ic: solo si origen es estimado"]
    if not (isinstance(ic, list) and len(ic) == 2):
        return [f"{ruta}.ic: se esperaba [inf, sup]"]
    p = [
        m
        for i, v in enumerate(ic)
        for m in _campo(f"{ruta}.ic[{i}]", v, ("decimal", 0, 100))
    ]
    return p or ([f"{ruta}.ic: inf mayor que sup"] if ic[0] > ic[1] else [])


def _reglas_alquiler(ruta, z):
    pct = [z["p25"], z["p50"], z["p75"]]
    p = []
    if (z["origen"] == "sin_dato") != all(x is None for x in pct):
        p.append(f"{ruta}.origen: sin_dato si y solo si los tres percentiles son null")
    dados = [x for x in pct if x is not None]
    if dados != sorted(dados):
        p.append(f"{ruta}: se exige p25 <= p50 <= p75")
    return p + _ic(ruta, z)


def _alquiler(o):
    p = _raiz(o, {"zonas": None})
    zonas = o.get("zonas")
    if not isinstance(zonas, dict) or not zonas:
        return p + ["zonas: se esperaba un objeto no vacío"]
    for zid, z in zonas.items():
        ruta = f"zonas.{zid}"
        q = _campo(ruta, zid, "zona") + _registro(ruta, z, ALQUILER)
        p += q or _reglas_alquiler(ruta, z)
    return p


CONFIGURACION = {"hijos": ("entero", 0, 2), "monoparental": "booleano"}


def _netos(o):
    p = _raiz(o, dict.fromkeys(["brutos", "configuraciones", "neto_anual"]))
    brutos = _lista("brutos", o.get("brutos"), ENT)
    filas, cols = len(_items(o, "brutos")), len(_items(o, "configuraciones"))
    matriz = _matriz("neto_anual", o.get("neto_anual"), filas, cols, POS)
    p += brutos + matriz
    configuraciones = o.get("configuraciones")
    p += _tabla("configuraciones", configuraciones, CONFIGURACION, tuple(CONFIGURACION))
    if brutos or matriz:
        return p
    if o["brutos"] != sorted(o["brutos"]):
        p.append("brutos: se esperaban crecientes")
    return p + [
        f"neto_anual[{i}][{j}]: {v} mayor que el bruto {b}"
        for i, (b, fila) in enumerate(zip(o["brutos"], o["neto_anual"]))
        for j, v in enumerate(fila)
        if v > b
    ]


TARIFA = {"titulo": "texto", "coste_mes": POS}


def _dias(ruta, filas):
    p = _tabla(ruta, filas, TARIFA, ())
    if not p and len(filas) != 5:
        p.append(f"{ruta}: se esperaban 5 filas (días 1 a 5)")
    return p


def _tarifas(o):
    campos = {"orden_coronas": None, "edad_max_joven": ("entero", 0, 100)}
    p = _raiz(o, {**campos, "viajes_dia": None, "escenarios": None})
    p += _campo("viajes_dia", o.get("viajes_dia"), [VIAJES_DIA])
    ordenadas = _lista("orden_coronas", o.get("orden_coronas"), CORONAS)
    if ordenadas:
        return p + ordenadas
    if o["orden_coronas"] != [c for c in CORONAS if c in o["orden_coronas"]]:
        return p + ["orden_coronas: debe seguir el orden de CORONAS"]
    edades = ["joven", "general"]
    viajes = [str(v) for v in VIAJES_DIA]

    def coronas(ruta, t):
        return _mapa(ruta, t, o["orden_coronas"], _dias)

    return p + _mapa(
        "escenarios",
        o.get("escenarios"),
        ["vigente_2026", "sin_descuento"],
        lambda r, e: _mapa(r, e, edades, lambda r2, t: _mapa(r2, t, viajes, coronas)),
    )


# fmt: off
PERFIL = {
    "adultos": ("entero", 1, 10), "hijos": ("entero", 0, 10), "m2": ("decimal", 10, 300),
    "personas_comparten": ("entero", 1, 10), "alimentacion": POS, "suministros": POS,
}
# fmt: on
PERFILES = ["solo", "comparte", "pareja", "monoparental"]
CESTA_UC = {"alimentacion": POS, "suministros": POS}


def _hogares(o):
    p = _raiz(o, {"perfiles": None, "cesta_uc": None})
    p += _registro("cesta_uc", o.get("cesta_uc"), CESTA_UC)
    return p + _mapa(
        "perfiles", o.get("perfiles"), PERFILES, lambda r, v: _registro(r, v, PERFIL)
    )


# fmt: off
ESFUERZO = {"zona_id": "zona", "anio": ANIO, "alquiler_mes_p50": POS_N, "renta_hogar_mes": POS, "esfuerzo": POS_N}
BONO = {
    "municipio_id": "municipio", "solicitudes": ENT, "aceptadas": ENT, "rechazadas": ENT,
    "poblacion_joven": ENT, "necesidad": POS_N, "grupo": "texto",
    "indicador_necesidad": ["esfuerzo", "sobrecarga"],
}
SOBRECARGA = {"zona_id": "zona", "anio": ANIO, "dif_sigma": "decimal?"}
SOBRECARGA |= {f"pct_{n}_{lado}": PCT for n in (40, 30) for lado in ("inf", "sup")}
SIMULACION = {
    "perfil": PERFILES, "municipio_id": "municipio", "criterio": "texto",
    "elegible": "booleano", "eur_mes": POS, "estimado": "booleano",
}
# bloque -> (columnas, clave); sobrecarga y simulacion son opcionales
BLOQUES = {
    "esfuerzo": (ESFUERZO, ("zona_id", "anio")), "bono": (BONO, ("municipio_id",)),
    "titulares": ({"texto": "texto", "fuente": "texto"}, ()),
    "sobrecarga": (SOBRECARGA, ("zona_id", "anio")),
    "simulacion": (SIMULACION, ("perfil", "municipio_id", "criterio")),
}
REFERENCIAS_ANALISIS = {"esfuerzo": "zona_id", "sobrecarga": "zona_id", "bono": "municipio_id", "simulacion": "municipio_id"}
# fmt: on


def _analisis(o):
    p = _raiz(o, dict.fromkeys(BLOQUES), ("sobrecarga", "simulacion"))
    for bloque, (campos, clave) in BLOQUES.items():
        p += _tabla(bloque, o[bloque], campos, clave) if bloque in o else []
    return p


# fmt: off
VALIDADORES = {
    "zonas.geojson": _zonas, "tiempos.json": _tiempos, "alquiler.json": _alquiler,
    "netos.json": _netos, "tarifas.json": _tarifas, "hogares.json": _hogares,
    "analisis.json": _analisis,
}
# fmt: on
FICHEROS = tuple(VALIDADORES)


def _referencias(nombre, o):
    """Ids que el fichero toma de las zonas."""
    if nombre == "tiempos.json":
        return o["origenes"] + [
            d["destino_id"] for d in o["destinos"] if d["tipo"] == "zona"
        ]
    if nombre == "alquiler.json":
        return list(o["zonas"])
    return [f[c] for b, c in REFERENCIAS_ANALISIS.items() for f in o.get(b, [])]


def _desconocidas(nombre, o, zonas):
    propiedades = [f["properties"] for f in zonas["features"]]
    conocidas = {x["zona_id"] for x in propiedades}
    if nombre == "analisis.json":  # incluye Madrid entero (28079), un municipio_id
        conocidas |= {x["municipio_id"] for x in propiedades}
    if falta := sorted(set(_referencias(nombre, o)) - conocidas):
        return [f"ids desconocidos, no están en zonas.geojson: {falta}"]
    return []


def validar(nombre: str, objeto: dict, zonas: dict | None = None) -> None:
    """Lanza un único `ValueError` con todos los problemas de `objeto` según el contrato de `nombre`.

    `zonas` es el `zonas.geojson` ya leído: con él se comprueba además que cada id exista.
    """
    if nombre not in VALIDADORES or not isinstance(objeto, dict):
        raise ValueError(
            f"{nombre}: fuera del contrato {list(FICHEROS)} o raíz inválida"
        )
    p = VALIDADORES[nombre](objeto)
    if not p and zonas is not None and nombre != "zonas.geojson":
        validar("zonas.geojson", zonas)
        p = _desconocidas(nombre, objeto, zonas)
    if p:
        resto = f"; y {len(p) - MAX_PROBLEMAS} más" if len(p) > MAX_PROBLEMAS else ""
        raise ValueError(f"{nombre}: " + "; ".join(p[:MAX_PROBLEMAS]) + resto)


def _sin_nan(x):
    if isinstance(x, float) and math.isnan(x):
        return None
    if isinstance(x, (list, tuple)):
        return [_sin_nan(i) for i in x]
    if isinstance(x, dict):
        return {k: _sin_nan(v) for k, v in x.items()}
    return x


def escribir(nombre: str, objeto: dict, carpeta: str | Path) -> Path:
    """Valida (NaN pasa a null; los ids, contra el `zonas.geojson` de la carpeta si está) y escribe JSON compacto en UTF-8."""
    objeto = _sin_nan(objeto)
    zonas_json = Path(carpeta) / "zonas.geojson"
    zonas = json.loads(zonas_json.read_text("utf-8")) if zonas_json.exists() else None
    validar(nombre, objeto, zonas)
    destino = Path(carpeta) / nombre
    destino.parent.mkdir(parents=True, exist_ok=True)
    compacto = json.dumps(
        objeto, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    )
    destino.write_text(compacto, "utf-8")
    return destino
