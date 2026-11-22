"""Servidor MCP local (stdio) de Kuanto sobre los ficheros de la API estática.

Tres herramientas, todas sobre `mesobra.calculo` y los ficheros de `app/datos/` (los del paquete
instalado, o los del repositorio): sin red, sin credenciales y sin que el sueldo salga del equipo.
Ninguna cifra sale de otro sitio que las herramientas. Cada respuesta lleva unidades, año del dato,
marca de estimado, fuentes y supuestos, y explica cada cifra nula (sin alquiler, sin ruta) y sobre
cuántas zonas se ha calculado.

    uvx --from <repositorio> mesobra-mcp
"""

import json
from collections import Counter
from collections.abc import Callable
from functools import cache, wraps
from pathlib import Path
from typing import Annotated, Any, Literal, NotRequired, TypedDict

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import ConfigDict, Field, with_config

from mesobra.calculo import RAIZ, calcular, leer_api

# El wheel trae app/datos como mesobra/datos (force-include); en el checkout, la carpeta del repo. En el checkout,
# src/mesobra/datos existe (guarda polos.csv) pero sin la API: se elige la carpeta que tiene zonas.geojson.
DATOS = next(
    (
        c
        for c in (Path(__file__).parent / "datos", RAIZ / "app/datos")
        if (c / "zonas.geojson").is_file()
    ),
    None,
)
if DATOS is None:
    raise FileNotFoundError(
        "sin mesobra/datos ni app/datos: instala el paquete completo"
    )
# Una clave mal escrita no se descarta en silencio.
ESTRICTO = ConfigDict(extra="forbid", strict=True)
UNIDADES = {
    "neto": "€/mes del hogar; desde el bruto, estimado: neto anual ÷ 12 con cotización y cuota de IRPF 2026 de la declaración (retención si no hay obligación de declarar), tributación individual, sin deducciones reembolsables (ver fuentes.netos.json.supuestos)",
    "alquiler": "€/mes de un contrato nuevo, estimado: mediana P50 de los contratos en vigor × factor_ipc × factor_brecha (AEAT, IRPF 2024); P25 y P75 en alquiler_p25/p75. Sigue siendo un suelo",
    "alquiler_contrato": "€/mes con lo que pagan los inquilinos actuales (P50 × factor_ipc, sin factor_brecha)",
    "transporte": "€/mes, estimado: media anual del título más barato con precios de 2026 (BOCM de 31-12-2025) y el calendario laboral de 2026 (ver fuentes.tarifas.json.supuestos)",
    "cesta": "€/mes (cesta básica del hogar)",
    "sobra": "€/mes del hogar = neto − alquiler − transporte − cesta",
    "sobra_contrato": "€/mes del hogar con el alquiler de alquiler_contrato (inquilinos actuales)",
    "sobra_banda": "[bajo, alto] €/mes",
    "horas": "horas/mes de viaje al trabajo (ida y vuelta)",
    "viajes": "por sueldo y en su orden: {horas, coste, titulo} del viaje (título de la misma celda de tarifas que el coste; coche en coche)",
    "esfuerzo": "proporción alquiler ÷ neto",
    "precio_hora": "€/mes ganados por cada hora extra de viaje al mes frente a la referencia",
}


@with_config(ESTRICTO)
class Hogar(TypedDict):
    perfil: Literal["solo", "comparte", "pareja", "monoparental"]
    edad: int  # 16 a 64
    adultos: NotRequired[int]
    hijos: NotRequired[int]
    personas_comparten: NotRequired[int]
    m2: NotRequired[float]


@with_config(ESTRICTO)
class Sueldo(TypedDict):
    destino: str  # código INE de la zona donde trabaja, no el nombre (Getafe: 28065)
    dias: int  # días presenciales a la semana, 1 a 5
    modo: Literal["tp", "coche"]  # tp = transporte público
    bruto: NotRequired[float]  # €/año; o neto_mes, uno de los dos
    neto_mes: NotRequired[float]  # €/mes
    viajes_dia: NotRequired[int]  # 2 (ida y vuelta) o 4


@with_config(ESTRICTO)
class Escenario(TypedDict, total=False):
    tarifas: Literal["vigente_2026", "sin_descuento"]
    subida_alquiler: float  # %
    edad: int


@cache
def _api() -> dict[str, Any]:
    analisis = json.loads((DATOS / "analisis.json").read_text("utf-8"))
    return leer_api(DATOS) | {"analisis": analisis}


def _fuentes(*nombres: str) -> dict[str, Any]:
    """Año del dato, fuentes con licencia y supuestos de cada fichero usado."""
    api = _api()
    salida = {}
    for n in nombres:
        m = api[n]["meta"]
        salida[f"{n}.json"] = {
            "anio_dato": m["anio_dato"],
            "fuentes": [
                {k: f.get(k) for k in ("nombre", "url", "licencia")}
                for f in [*m["fuentes"], *m.get("fuentes_ruta", [])]
            ],
            "supuestos": " ".join(filter(None, [m.get("nota"), m.get("nota_ruta")]))
            or None,
        }
    return salida


@cache
def _nombres() -> dict[str, dict[str, Any]]:
    return {
        f["properties"]["zona_id"]: f["properties"] for f in _api()["zonas"]["features"]
    }


def _zona_existente(zona_id: str) -> None:
    if zona_id not in _api()["alquiler"]["zonas"]:
        raise ValueError(
            f"zona_id {zona_id!r} inexistente: es el código INE de 5 dígitos del municipio "
            "(28065) o 28079 + distrito de Madrid (2807913); consúltalo con indicadores_zona"
        )


def _motivos(z: dict) -> list[str]:
    """Por qué una zona no tiene sobrante; vacío si lo tiene."""
    if z["sobra"] is not None:
        return []
    motivos = []
    if z["alquiler"] is None:
        motivos.append("sin dato de alquiler")
    if z["horas"] is None:
        motivos.append("sin ruta en 120 min")
    return motivos or ["sin coste de transporte"]


def _calcular(
    hogar: Hogar, sueldos: list[Sueldo], escenario: Escenario | None
) -> dict[str, Any]:
    """`calcular` sobre todas las zonas (misma referencia que la web), con los destinos validados."""
    api = _api()
    destinos = {d["destino_id"] for d in api["tiempos"]["destinos"]}
    for s in sueldos:
        if s.get("destino") not in destinos:
            raise ValueError(
                f"destino {s.get('destino')!r} inexistente: usa el código de una zona (Getafe: 28065)"
            )
    entrada = {"hogar": hogar, "sueldos": sueldos, "escenario": escenario or {}}
    return calcular(api, entrada)


def _zona(zona_id: str, z: dict) -> dict[str, Any]:
    alq = _api()["alquiler"]["zonas"][zona_id]
    return {
        "zona_id": zona_id,
        "nombre": _nombres()[zona_id]["nombre"],
        **z,
        "anio_alquiler": alq["anio"],
        "estimado": z["origen"] == "estimado",
        "motivos_sin_cifra": _motivos(z),
    }


def _envoltura(res: dict) -> dict[str, Any]:
    zonas = res["zonas"]
    calculadas = sum(z["sobra"] is not None for z in zonas.values())
    salida = {
        "unidades": UNIDADES,
        "referencia": res["ref"],
        "escenario": res["escenario"],
        "zonas_calculadas": calculadas,
        "zonas_total": len(zonas),
        "fuentes": _fuentes("alquiler", "hogares", "netos", "tarifas", "tiempos"),
    }
    if res["escenario"]["tarifas"] != "vigente_2026":
        salida["simulacion"] = (
            "precios oficiales del BOCM-20251231-3 sin la bonificación de 2026 (RDL 17/2025, "
            "BOE-A-2025-26459); el precio vigente es vigente_2026"
        )
    return salida


def _claro(f: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
    """Un `ValueError` de validación llega al modelo con su mensaje, no como «error inesperado»."""

    @wraps(f)
    def envuelta(*args: Any, **kwargs: Any) -> dict[str, Any]:
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            raise ToolError(str(e)) from e

    return envuelta


servidor = MCPServer(
    "mesobra",
    instructions=(
        "Cifras de Kuanto (Comunidad de Madrid, 199 zonas). Todas las cifras salen de estas "
        "herramientas: no estimes ni completes ninguna. Da siempre las horas de viaje junto al "
        "sobrante, di la fuente y el año, y marca como estimado lo estimado. Un valor nulo no es cero: "
        "explica su motivo y sobre cuántas zonas se ha calculado. Los destinos y zonas van por código INE "
        "(Getafe = 28065), no por nombre. Con escenario `sin_descuento` es una simulación: presenta "
        "junto a ella la cifra `vigente_2026` y etiquétala como tal. La tarifa joven se aplica a todos "
        "los sueldos según una sola edad."
    ),
)


@servidor.tool()
@_claro
def calcular_sobrante(
    hogar: Hogar,
    sueldos: list[Sueldo],
    zona_id: str,
    escenario: Escenario | None = None,
) -> dict[str, Any]:
    """Cuánto sobra al mes (neto − alquiler − transporte − cesta) viviendo en `zona_id`, con las horas
    de viaje, la banda, el esfuerzo de alquiler y el precio de la hora frente a la zona de referencia."""
    _zona_existente(zona_id)
    if zona_id not in _api()["tiempos"]["origenes"]:
        raise ValueError(f"zona_id {zona_id!r} sin tiempos de viaje en tiempos.json")
    res = _calcular(hogar, sueldos, escenario)
    return _envoltura(res) | {"zona": _zona(zona_id, res["zonas"][zona_id])}


@servidor.tool()
@_claro
def ranking_zonas(
    hogar: Hogar,
    sueldos: list[Sueldo],
    escenario: Escenario | None = None,
    n: Annotated[int, Field(strict=True, ge=1, le=199)] = 10,
) -> dict[str, Any]:
    """Las `n` zonas donde más sobra al mes, cada una con sus horas de viaje; y las zonas sin cifra
    con su motivo. Las que más sobran pueden estar muy lejos del trabajo: mira las horas."""
    res = _calcular(hogar, sueldos, escenario)
    zonas = {z: _zona(z, v) for z, v in res["zonas"].items()}
    con_cifra = sorted(
        (z for z in zonas.values() if z["sobra"] is not None),
        key=lambda z: z["sobra"],
        reverse=True,
    )
    sin = [z for z in zonas.values() if z["sobra"] is None]
    return _envoltura(res) | {
        "ranking": con_cifra[:n],
        "sin_cifra_por_motivo": dict(
            Counter(" y ".join(z["motivos_sin_cifra"]) for z in sin)
        ),
        "sin_cifra": [
            {
                "zona_id": z["zona_id"],
                "nombre": z["nombre"],
                "motivos": z["motivos_sin_cifra"],
            }
            for z in sin
        ],
    }


@servidor.tool()
@_claro
def indicadores_zona(
    zona_id: str, anio: Annotated[int | None, Field(strict=True)] = None
) -> dict[str, Any]:
    """Alquiler (€/m²), esfuerzo de alquiler sobre la renta y ayuda del Bono Alquiler Joven de una zona;
    `anio` es el del esfuerzo (por defecto, el último)."""
    _zona_existente(zona_id)
    api = _api()
    esfuerzo = {
        e["anio"]: e for e in api["analisis"]["esfuerzo"] if e["zona_id"] == zona_id
    }
    if anio is None and esfuerzo:
        anio = max(esfuerzo)
    if anio is not None and anio not in esfuerzo:
        raise ValueError(f"anio = {anio!r}: hay esfuerzo de {sorted(esfuerzo)}")
    props = _nombres()[zona_id]
    bono = next(
        (
            b
            for b in api["analisis"]["bono"]
            if b["municipio_id"] == props["municipio_id"]
        ),
        None,
    )
    alq = api["alquiler"]["zonas"][zona_id]
    return {
        "unidades": {
            "alquiler": "€/m² al mes, vivienda colectiva (p25, p50, p75); m2 = superficie del piso tipo",
            "alquiler_mes_p50": "€/mes",
            "renta_hogar_mes": "€/mes, renta neta media por hogar",
            "esfuerzo": "proporción alquiler ÷ renta del hogar",
            "bono": "por municipio (en los distritos de Madrid, el de todo el municipio); solicitudes, aceptadas y rechazadas: hogares; necesidad: índice relativo",
        },
        "zona": props,
        "alquiler": alq | {"estimado": alq["origen"] == "estimado"},
        "esfuerzo": esfuerzo.get(anio),
        "esfuerzo_motivo": None
        if (esfuerzo.get(anio) or {}).get("esfuerzo") is not None
        else "sin alquiler o renta de la zona",
        "bono": bono,
        "bono_motivo": None
        if bono
        else "sin datos del Bono Alquiler Joven del municipio",
        "fuentes": _fuentes("alquiler", "analisis"),
    }


# shortcut: API privada de mcp 2.3.0 (fijada), revisar al subir de versión. El SDK deja pasar
# los argumentos de primer nivel mal escritos (`escenarios`) y daría una cifra sin el escenario pedido.
for _herramienta in servidor._tool_manager.list_tools():
    _herramienta.fn_metadata.arg_model.model_config["extra"] = "forbid"
    _herramienta.fn_metadata.arg_model.model_rebuild(force=True)


def main() -> None:
    servidor.run("stdio")
