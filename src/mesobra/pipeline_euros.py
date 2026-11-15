"""Encadena alquiler, neto, transporte y hogares y escribe los cuatro JSON de `app/datos/`.

No calcula nada nuevo: solo da forma al contrato de `api_estatica`. Ejecutar con
`python -m mesobra.pipeline_euros`. Todos los valores salen en tipos nativos de Python.
"""

from datetime import date
from pathlib import Path

import pandas as pd

from mesobra import alquiler, api_estatica, hogares, neto, transporte

APP_DATOS = Path(__file__).resolve().parents[2] / "app/datos"
MADRID = "28079"
SERPAVI = {
    "nombre": "SERPAVI, Ministerio de Vivienda y Agenda Urbana. Origen de los datos: Ministerio de Vivienda y Agenda Urbana",
    "url": "https://cdn.mivau.gob.es/portal-web-mivau/vivienda/serpavi/2026-03_09_bd_SERPAVI_2011-2024%20-%20DEFINITIVO%20WEB_v2.xlsx",
    "licencia": "Condiciones generales para la reutilización de información del MIVAU (RD 1495/2011)",
}
LICENCIA_BOE = "Reutilización con cita de la fuente (aviso legal del BOE)"
LICENCIA_BOCM = "Reutilización con cita de la fuente (aviso legal del BOCM)"
CATALOGO = "https://datos.comunidad.madrid/dataset/"
EPF = (
    CATALOGO
    + "{}/download/gasto-medio-de-los-hogares-por-subgrupo-de-gasto-{}-digitos-coicopepf-base-2006.csv"
)
BOCM = "https://www.bocm.es/boletin/CM_Orden_BOCM/2025/12/31/BOCM-20251231-{}.PDF"


def _boe(nombre, url):
    return {"nombre": nombre, "url": url, "licencia": LICENCIA_BOE}


FUENTES_NETOS = [
    _boe(
        "LIRPF (BOE-A-2006-20764)",
        "https://www.boe.es/buscar/act.php?id=BOE-A-2006-20764",
    ),
    _boe(
        "Orden PJC/297/2026 (BOE-A-2026-7296)",
        "https://www.boe.es/buscar/doc.php?id=BOE-A-2026-7296",
    ),
    _boe(
        "RDL 5/2026 (BOE-A-2026-3810)",
        "https://www.boe.es/buscar/doc.php?id=BOE-A-2026-3810",
    ),
    {
        # shortcut: URL genérica del BOCM, sin verificar el enlace directo de BOCM-m-2010-90068; fijarlo al verificar fuentes
        "nombre": "Decreto Legislativo 1/2010 de la Comunidad de Madrid, tributos cedidos (BOCM-m-2010-90068)",
        "url": "https://www.bocm.es/",
        "licencia": LICENCIA_BOCM,
    },
]
FUENTES_TARIFAS = [
    {
        "nombre": f"BOCM de 31-12-2025 (BOCM-20251231-{n})",
        "url": BOCM.format(n),
        "licencia": LICENCIA_BOCM,
    }
    for n in (2, 3)
] + [
    {
        "nombre": "Ficha del Abono Joven, Consorcio Regional de Transportes de Madrid",
        "url": "https://www.crtm.es/billetes-y-tarifas/buscador/abono-joven/",
        "licencia": "Licencia de datos abiertos del CRTM (https://www.crtm.es/licencia-de-uso/)",
    }
]
EPF_IDS = {
    3: "39d6f25b-e043-428f-b8f6-4a46214bf34e/resource/83b08257-b457-4fe4-a11b-0fd37a2c33f7",
    4: "87b3102d-79f3-44ab-8b33-3f347bbe048b/resource/88ed4858-b94e-40e5-aae5-8a2d786546b4",
}
FUENTES_HOGARES = [
    {
        "nombre": f"INE, Encuesta de Presupuestos Familiares, {d} dígitos. Fuente de los datos: Comunidad de Madrid",
        "url": EPF.format(i, d),
        "licencia": "CC BY 4.0",
    }
    for d, i in EPF_IDS.items()
] + [SERPAVI]


def _meta(anio_dato, fuentes, nota):
    return {
        "generado": date.today().isoformat(),
        "anio_dato": anio_dato,
        "fuentes": fuentes,
        "nota": nota,
    }


def _ultimo_anio(zona: pd.DataFrame) -> pd.DataFrame:
    """Fila del último año con `eur_m2_p50` por zona, sin Madrid entero (28079)."""
    con_dato = zona[(zona["zona_id"] != MADRID) & zona["eur_m2_p50"].notna()]
    return con_dato.sort_values("anio").groupby("zona_id").tail(1)


def alquiler_json(zona: pd.DataFrame) -> dict:
    ultimo = _ultimo_anio(zona).set_index("zona_id")
    zonas = {}
    for zid in sorted(set(zona["zona_id"]) - {MADRID}):
        if zid not in ultimo.index:
            zonas[zid] = dict.fromkeys(["anio", "p25", "p50", "p75", "m2", "ic"])
            zonas[zid] |= {"factor_ipc": 1.0, "origen": "sin_dato"}
            continue
        f = ultimo.loc[zid]
        zonas[zid] = {
            "anio": int(f["anio"]),
            "p25": float(f["eur_m2_p25"]),
            "p50": float(f["eur_m2_p50"]),
            "p75": float(f["eur_m2_p75"]),
            "m2": float(f["m2_p50"]),
            "factor_ipc": float(f["factor_ipc"]),
            "origen": f["origen"],
            "ic": [float(f["ic_inf"]), float(f["ic_sup"])]
            if f["origen"] == "estimado"
            else None,
        }
    anio = int(zona["anio"].max())
    nota = (
        "€/m² al mes de vivienda colectiva (sin unifamiliar), de contratos declarados a la Agencia "
        "Tributaria (Modelo 100 cruzado con el Catastro), no de anuncios: es un suelo del precio actual. "
        "Cada zona lleva el último año con dato en euros de ese año, sin actualizar con el IPC "
        "(factor_ipc 1,0) hasta #94; las zonas cuyo último dato es anterior a "
        f"{anio} llevan su año en anio. Las zonas sin dato publicado van como sin_dato. "
        "Origen de los datos: Ministerio de Vivienda y Agenda Urbana, actualizado el 2026-07-09; "
        "el Ministerio no participa ni patrocina este proyecto."
    )
    return {"meta": _meta(anio, [SERPAVI], nota), "zonas": zonas}


def m2_por_defecto(zona: pd.DataFrame) -> int:
    """Mediana ponderada por `testigos` de `m2_p50` en el último año con dato de cada zona.

    Se ordena por `m2_p50`, se acumulan los testigos y se toma el primer valor cuya suma
    acumulada llega a la mitad del total. Madrid entero (28079) no entra.
    """
    f = _ultimo_anio(zona).sort_values("m2_p50")
    acumulado = f["testigos"].cumsum()
    return round(float(f.loc[acumulado >= f["testigos"].sum() / 2, "m2_p50"].iloc[0]))


def netos_json(rejilla: pd.DataFrame) -> dict:
    pivot = rejilla.pivot(
        index="bruto_anual", columns=["hijos", "monoparental"], values="neto_anual"
    )
    if pivot.isna().any(axis=None):
        raise ValueError("La rejilla de netos no cubre todas las combinaciones")
    nota = (
        "Neto anual en € de 2026 desde el bruto anual: cotización del trabajador e IRPF estatal y de "
        "Madrid (cuota de la declaración). Tributación individual, sin deducciones reembolsables ni "
        "autonómicas (un monoparental con dos hijos queda hasta 1.200 €/año por debajo), contrato "
        "indefinido, menor de 65 años. Rejilla de 12.000 a 120.000 €: fuera de ella no se extrapola."
    )
    return {
        "meta": _meta(2026, FUENTES_NETOS, nota),
        "brutos": [int(b) for b in pivot.index],
        "configuraciones": [
            {"hijos": int(h), "monoparental": bool(m)} for h, m in pivot.columns
        ],
        "neto_anual": pivot.values.tolist(),
    }


def tarifas_json(tabla: pd.DataFrame) -> dict:
    escenarios = {}
    claves = ["escenario", "joven", "viajes_dia", "corona"]
    for (esc, joven, viajes, corona), g in tabla.groupby(claves):
        edad = "joven" if joven else "general"
        por_viajes = escenarios.setdefault(esc, {}).setdefault(edad, {})
        por_viajes.setdefault(str(viajes), {})[corona] = [
            {"titulo": t, "coste_mes": float(c)}
            for t, c in g.sort_values("dias")[["titulo", "coste_mes"]].itertuples(
                index=False
            )
        ]
    nota = (
        "Título más barato al mes (€/mes) con los precios de 2026 del BOCM de 31-12-2025. vigente_2026 "
        "lleva el descuento del RDL 17/2025, que solo vale para 2026; sin_descuento, los precios "
        "oficiales. 4,33 semanas al mes; el viaje pasa por la zona A; sin abono anual (venta a "
        "particulares suspendida desde 2023); el 10 viajes se compra en paquetes enteros. viajes_dia 2: "
        "ida y vuelta directa; 4: cambio de operador en cada sentido (interurbano↔Metro, Metro↔EMT), "
        "con los 2 viajes extra a precio de la zona A. Abono Joven de 15 a 25 años."
    )
    return {
        "meta": _meta(2026, FUENTES_TARIFAS, nota),
        "orden_coronas": [c for c in api_estatica.CORONAS if c in set(tabla["corona"])],
        "edad_max_joven": transporte.EDAD_MAX_JOVEN,
        "viajes_dia": list(transporte.VIAJES_DIA),
        "escenarios": escenarios,
    }


def hogares_json(tabla: pd.DataFrame, cesta: pd.Series, m2: int) -> dict:
    columnas = ["adultos", "hijos", "personas_comparten", "alimentacion", "suministros"]
    perfiles = {
        f["perfil"]: {"m2": m2, **{c: f[c] for c in columnas}}
        for f in tabla.to_dict("records")
    }
    nota = (
        f"{tabla.attrs['nota']}. m² por defecto: {m2} para todos los perfiles, la mediana de la "
        "superficie mediana (m2_p50) de cada zona en su último año con dato del SERPAVI, ponderada por "
        "testigos; el formulario permite cambiarlo. Un mismo m² para todos sobreestima el alquiler de "
        "quien vive solo."
    )
    return {
        "meta": _meta(int(tabla["anio"].iloc[0]), FUENTES_HOGARES, nota),
        "perfiles": perfiles,
        "cesta_uc": {k: float(v) for k, v in cesta.items()},
    }


def main() -> None:
    zona = alquiler.alquiler_zona(alquiler.leer_serpavi())
    salidas = {
        "alquiler.json": alquiler_json(zona),
        "netos.json": netos_json(neto.rejilla()),
        "tarifas.json": tarifas_json(transporte.tabla()),
        "hogares.json": hogares_json(
            hogares.hogares(), hogares.cesta_uc(), m2_por_defecto(zona)
        ),
    }
    for nombre, objeto in salidas.items():
        api_estatica.escribir(nombre, objeto, APP_DATOS)


if __name__ == "__main__":
    main()
