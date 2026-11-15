"""Contratos de las tablas de `data/processed/` (sección 2 del plan de desarrollo).

Cada contrato fija la clave y las columnas con su tipo; la unidad y el dominio van en el comentario de cada línea.
Los fixtures de `tests/fixtures/processed/` son valores inventados y plausibles, no datos.
"""

import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_float_dtype,
    is_integer_dtype,
    is_string_dtype,
)

CONTRATOS: dict[str, dict] = {
    "zonas": {
        "clave": ("zona_id",),
        "columnas": {
            "zona_id": "texto",  # INE 5 dígitos (municipio) o 28079 + distrito de 2 dígitos
            "nombre": "texto",
            "tipo": "texto",  # {municipio, distrito}
            "municipio_id": "texto",  # INE 5 dígitos
            "corona": "texto",  # {A, B1, B2, B3, C1, C2}
            "poblacion": "entero",  # personas
            "lon_centro": "decimal",  # grados, EPSG:4326
            "lat_centro": "decimal",  # grados, EPSG:4326
            "geometry": "geometria",  # polígono en EPSG:25830
        },
    },
    "tiempos": {
        "clave": ("zona_id", "destino_id", "modo"),
        "columnas": {
            "zona_id": "texto",  # origen
            "destino_id": "texto",  # un zona_id o polo:<slug>
            "modo": "texto",  # {tp, coche}
            "minutos": "decimal",  # mediana puerta a puerta, 7:30-8:30 de un martes; nulo sin ruta en 120 min
            "km": "decimal",  # km, solo coche
            "estimado": "booleano",  # verdadero si sale de la línea base por distancia
        },
    },
    "alquiler_zona": {
        "clave": ("zona_id", "anio"),
        "columnas": {
            "zona_id": "texto",
            "anio": "entero",
            "eur_m2_p25": "decimal",  # €/m² al mes, vivienda colectiva
            "eur_m2_p50": "decimal",  # €/m² al mes
            "eur_m2_p75": "decimal",  # €/m² al mes
            "m2_p50": "decimal",  # m²
            "testigos": "entero",  # anuncios o contratos
            "origen": "texto",  # {observado, estimado, sin_dato}
            "ic_inf": "decimal",  # €/m² al mes, solo estimado
            "ic_sup": "decimal",  # €/m² al mes, solo estimado
            "factor_ipc": "decimal",  # 1,0 sin actualizar
        },
    },
    "alquiler_seccion": {
        "clave": ("seccion_id", "anio"),
        "columnas": {
            "seccion_id": "texto",  # 10 dígitos
            "anio": "entero",
            "eur_m2_p25": "decimal",  # €/m² al mes
            "eur_m2_p50": "decimal",  # €/m² al mes
            "eur_m2_p75": "decimal",  # €/m² al mes
            "cuantia_p25": "decimal",  # €/mes
            "cuantia_p50": "decimal",  # €/mes
            "cuantia_p75": "decimal",  # €/mes
            "testigos": "entero",
        },
    },
    "renta": {
        "clave": ("unidad_id", "nivel", "anio"),
        "columnas": {
            "unidad_id": "texto",  # zona_id o seccion_id según nivel
            "nivel": "texto",  # {zona, seccion}
            "anio": "entero",
            "renta_hogar": "decimal",  # €/año, media por hogar
            "renta_uc": "decimal",  # €/año por unidad de consumo
            "gini": "decimal",  # 0–100
            "p80p20": "decimal",  # cociente
            "poblacion": "entero",  # personas
            "tam_hogar": "decimal",  # personas
        },
    },
    "netos": {
        "clave": ("bruto_anual", "hijos", "monoparental"),
        "columnas": {
            "bruto_anual": "entero",  # €, cada 250 y cada 50 entre 16.500 y 21.500
            "hijos": "entero",  # {0, 1, 2}
            "monoparental": "booleano",
            "cotizacion": "decimal",  # €/año
            "cuota_irpf": "decimal",  # €/año
            "neto_anual": "decimal",  # €/año
        },
    },
    "tarifas": {
        "clave": ("escenario", "joven", "corona", "dias"),
        "columnas": {
            "escenario": "texto",  # {vigente_2026, sin_descuento}
            "joven": "booleano",
            "corona": "texto",
            "dias": "entero",  # 1–5 días de trabajo por semana
            "titulo": "texto",
            "coste_mes": "decimal",  # €/mes
        },
    },
    "hogares": {
        "clave": ("perfil",),
        "columnas": {
            "perfil": "texto",  # {solo, comparte, pareja, monoparental}
            "adultos": "entero",
            "hijos": "entero",
            "personas_comparten": "entero",  # personas que reparten el alquiler
            "alimentacion": "decimal",  # €/mes
            "suministros": "decimal",  # €/mes
            "anio": "entero",
        },
    },
    "esfuerzo": {
        "clave": ("zona_id", "anio"),
        "columnas": {
            "zona_id": "texto",
            "anio": "entero",
            "alquiler_mes_p50": "decimal",  # €/mes
            "renta_hogar_mes": "decimal",  # €/mes
            "esfuerzo": "decimal",  # proporción (0,30 = 30 %)
        },
    },
    "bono": {
        "clave": ("municipio_id",),
        "columnas": {
            "municipio_id": "texto",
            "solicitudes": "entero",
            "aceptadas": "entero",
            "rechazadas": "entero",
            "poblacion_joven": "entero",  # personas
            "necesidad": "decimal",
            "indicador_necesidad": "texto",  # {esfuerzo, sobrecarga}
            "grupo": "texto",
        },
    },
    "sobrecarga": {
        "clave": ("zona_id", "anio"),
        "columnas": {
            "zona_id": "texto",
            "anio": "entero",
            "pct_40_inf": "decimal",  # % de hogares inquilinos
            "pct_40_sup": "decimal",  # % de hogares inquilinos
            "pct_30_inf": "decimal",  # % de hogares inquilinos
            "pct_30_sup": "decimal",  # % de hogares inquilinos
            "dif_sigma": "decimal",
        },
    },
    "simulacion": {
        "clave": ("perfil", "municipio_id", "criterio"),
        "columnas": {
            "perfil": "texto",
            "municipio_id": "texto",
            "criterio": "texto",
            "elegible": "booleano",
            "eur_mes": "decimal",  # €/mes
            "estimado": "booleano",
        },
    },
}

COMPRUEBA = {
    "texto": is_string_dtype,
    "entero": is_integer_dtype,
    "decimal": is_float_dtype,
    "booleano": is_bool_dtype,
    "geometria": lambda serie: serie.dtype.name == "geometry",
}
DTYPES = {
    "texto": "string",
    "entero": "Int64",
    "decimal": "float64",
    "booleano": "boolean",
    "geometria": "string",
}


def dtypes(nombre: str) -> dict[str, str]:
    """Columna → dtype para `pd.read_csv` (la geometría llega como WKT)."""
    return {col: DTYPES[tipo] for col, tipo in CONTRATOS[nombre]["columnas"].items()}


def _problemas_clave(df: pd.DataFrame, clave: tuple[str, ...]) -> list[str]:
    if not set(clave) <= set(df.columns):
        return []  # ya consta como columna que falta
    columnas = list(clave)
    problemas = []
    if nulas := int(df[columnas].isna().any(axis=1).sum()):
        problemas.append(f"clave {clave} con {nulas} filas nulas")
    repetidas = df.loc[df.duplicated(columnas, keep=False), columnas]
    if not repetidas.empty:
        problemas.append(
            f"clave {clave} repetida, p. ej. {repetidas.head(3).values.tolist()}"
        )
    return problemas


def validar(df: pd.DataFrame, nombre: str) -> None:
    """Lanza un único `ValueError` con todos los incumplimientos del contrato de `nombre`."""
    clave, columnas = CONTRATOS[nombre]["clave"], CONTRATOS[nombre]["columnas"]
    if repetidas := df.columns[df.columns.duplicated()].tolist():
        raise ValueError(f"{nombre}: columnas repetidas: {repetidas}")
    problemas = []
    if faltan := [c for c in columnas if c not in df.columns]:
        problemas.append(f"faltan columnas: {faltan}")
    if sobran := [c for c in df.columns if c not in columnas]:
        problemas.append(f"sobran columnas: {sobran}")
    for col, tipo in columnas.items():
        if col not in df.columns:
            continue
        if not COMPRUEBA[tipo](df[col]):
            problemas.append(f"{col}: se esperaba {tipo} y hay {df[col].dtype}")
        crs = getattr(df, "crs", None)
        if tipo == "geometria" and (crs is None or crs.to_epsg() != 25830):
            problemas.append(f"{col}: se esperaba EPSG:25830 y hay {crs}")
    problemas += _problemas_clave(df, clave)
    if problemas:
        raise ValueError(f"{nombre}: " + "; ".join(problemas))
