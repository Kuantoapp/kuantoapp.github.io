"""El servidor MCP devuelve lo mismo que `mesobra.calculo` sobre `app/datos/`, con sus motivos y fuentes."""

import asyncio
import json
from typing import Any

import pytest
from mcp.server.mcpserver.exceptions import ToolError

from mesobra import mcp_servidor
from mesobra.calculo import RAIZ, calcular, leer_api

API = leer_api(RAIZ / "app/datos")
GETAFE = "28065"
HOGAR = {"perfil": "solo", "edad": 30}
SUELDO = {"destino": GETAFE, "dias": 5, "modo": "tp", "bruto": 24000}
ENTRADA = {"hogar": HOGAR, "sueldos": [SUELDO]}


def llamar(herramienta: str, argumentos: dict[str, Any]) -> dict[str, Any]:
    r = asyncio.run(mcp_servidor.servidor.call_tool(herramienta, argumentos))
    return json.loads(r.content[0].text)


def test_datos_es_la_carpeta_con_la_api_aunque_exista_src_mesobra_datos() -> None:
    # src/mesobra/datos guarda polos.csv (F3-01) y no tiene la API: el MCP no debe elegirla en un checkout
    assert (RAIZ / "src/mesobra/datos").is_dir()
    assert mcp_servidor.DATOS == RAIZ / "app/datos"


def test_expone_las_tres_herramientas() -> None:
    nombres = {t.name for t in asyncio.run(mcp_servidor.servidor.list_tools())}
    assert nombres == {"calcular_sobrante", "ranking_zonas", "indicadores_zona"}


def test_calcular_sobrante_igual_que_calculo() -> None:
    esperado = calcular(API, ENTRADA)["zonas"]["28092"]
    r = llamar("calcular_sobrante", {**ENTRADA, "zona_id": "28092"})
    for clave, valor in esperado.items():
        assert r["zona"][clave] == valor
    assert r["zona"]["anio_alquiler"] == API["alquiler"]["zonas"]["28092"]["anio"]
    assert r["zona"]["estimado"] is False
    assert r["unidades"]["sobra"].startswith("€/mes")
    assert r["fuentes"]["alquiler.json"]["fuentes"]
    # las cifras de transporte (v2) llevan su fuente y su nota (#306)
    tarifas = r["fuentes"]["tarifas.json"]
    assert "tarifas_ruta" in tarifas["supuestos"]
    assert any("Renfe" in f["nombre"] for f in tarifas["fuentes"])


def test_escenario_y_dos_sueldos_igual_que_calculo() -> None:
    entrada = {
        "hogar": {"perfil": "pareja", "edad": 28},
        "sueldos": [SUELDO, {**SUELDO, "bruto": 30000, "dias": 3}],
        "escenario": {"tarifas": "sin_descuento", "subida_alquiler": 5},
    }
    esperado = calcular(API, entrada)["zonas"]["2807913"]["sobra"]
    r = llamar("calcular_sobrante", {**entrada, "zona_id": "2807913"})
    assert r["zona"]["sobra"] == esperado
    assert r["escenario"]["tarifas"] == "sin_descuento"
    assert "simulacion" in r


def test_simulacion_solo_con_escenario_sin_descuento() -> None:
    r = llamar("calcular_sobrante", {**ENTRADA, "zona_id": "28092"})
    assert "simulacion" not in r
    r = llamar(
        "calcular_sobrante",
        {**ENTRADA, "zona_id": "28092", "escenario": {"tarifas": "sin_descuento"}},
    )
    assert "BOCM-20251231-3" in r["simulacion"]


def test_ranking_getafe_dice_cuantas_zonas_y_por_que_faltan() -> None:
    r = llamar("ranking_zonas", {**ENTRADA, "n": 5})
    res = calcular(API, ENTRADA)["zonas"]
    ordenadas = sorted(
        (z for z, v in res.items() if v["sobra"] is not None),
        key=lambda z: res[z]["sobra"],
        reverse=True,
    )
    assert [z["zona_id"] for z in r["ranking"]] == ordenadas[:5]
    assert all(z["horas"] is not None for z in r["ranking"])
    assert (r["zonas_calculadas"], r["zonas_total"]) == (102, 199)
    assert r["sin_cifra_por_motivo"] == {
        "sin dato de alquiler y sin ruta en 120 min": 41,
        "sin ruta en 120 min": 56,
    }
    assert len(r["sin_cifra"]) == 97
    assert all(z["motivos"] for z in r["sin_cifra"])


def test_zona_sin_alquiler_explica_el_nulo() -> None:
    sin_dato = next(
        z for z, a in API["alquiler"]["zonas"].items() if a["origen"] == "sin_dato"
    )
    z = llamar("calcular_sobrante", {**ENTRADA, "zona_id": sin_dato})["zona"]
    assert z["sobra"] is None
    assert "sin dato de alquiler" in z["motivos_sin_cifra"]


def test_indicadores_zona_igual_que_analisis() -> None:
    analisis = json.loads((RAIZ / "app/datos/analisis.json").read_text("utf-8"))
    ultimo = max(e["anio"] for e in analisis["esfuerzo"] if e["zona_id"] == GETAFE)
    r = llamar("indicadores_zona", {"zona_id": GETAFE})
    assert r["esfuerzo"] == next(
        e
        for e in analisis["esfuerzo"]
        if e["zona_id"] == GETAFE and e["anio"] == ultimo
    )
    assert r["alquiler"]["p50"] == API["alquiler"]["zonas"][GETAFE]["p50"]
    assert r["zona"]["zona_id"] == GETAFE
    assert "analisis.json" in r["fuentes"]


@pytest.mark.parametrize(
    ("herramienta", "argumentos", "mensaje"),
    [
        ("calcular_sobrante", {**ENTRADA, "zona_id": "99999"}, "inexistente"),
        ("calcular_sobrante", {**ENTRADA, "zona_id": 28065}, "zona_id"),
        (
            "calcular_sobrante",
            {"hogar": {**HOGAR, "edad": 15}, "sueldos": [SUELDO], "zona_id": GETAFE},
            "edad",
        ),
        (
            "calcular_sobrante",
            {"hogar": HOGAR, "sueldos": [{**SUELDO, "dias": 6}], "zona_id": GETAFE},
            "dias",
        ),
        (
            "calcular_sobrante",
            {
                "hogar": HOGAR,
                "sueldos": [{**SUELDO, "bruto": "mucho"}],
                "zona_id": GETAFE,
            },
            "bruto",
        ),
        (
            "calcular_sobrante",
            {
                "hogar": HOGAR,
                "sueldos": [{**SUELDO, "destino": "00000"}],
                "zona_id": GETAFE,
            },
            "destino",
        ),
        (
            "calcular_sobrante",
            {
                "hogar": {"perfil": "otro", "edad": 30},
                "sueldos": [SUELDO],
                "zona_id": GETAFE,
            },
            "perfil",
        ),
        ("ranking_zonas", {**ENTRADA, "n": 0}, "greater than or equal"),
        ("indicadores_zona", {"zona_id": GETAFE, "anio": 1999}, "anio"),
        ("indicadores_zona", {"zona_id": "1"}, "inexistente"),
        ("indicadores_zona", {"zona_id": GETAFE, "anio": "2023"}, "anio"),
        (
            "calcular_sobrante",
            {**ENTRADA, "zona_id": GETAFE, "escenarios": {"subida_alquiler": 50}},
            "escenarios",
        ),
        ("ranking_zonas", {**ENTRADA, "n": True}, "n"),
        (
            "calcular_sobrante",
            {**ENTRADA, "zona_id": GETAFE, "escenario": {"subida": 50}},
            "subida",
        ),
        (
            "calcular_sobrante",
            {"hogar": {**HOGAR, "hijoss": 2}, "sueldos": [SUELDO], "zona_id": GETAFE},
            "hijoss",
        ),
        (
            "calcular_sobrante",
            {
                "hogar": HOGAR,
                "sueldos": [{**SUELDO, "viajesdia": 4}],
                "zona_id": GETAFE,
            },
            "viajesdia",
        ),
        (
            "calcular_sobrante",
            {"hogar": {**HOGAR, "edad": "30"}, "sueldos": [SUELDO], "zona_id": GETAFE},
            "edad",
        ),
    ],
)
def test_rechaza_argumentos_invalidos_con_mensaje(
    herramienta: str, argumentos: dict[str, Any], mensaje: str
) -> None:
    with pytest.raises(ToolError, match=mensaje):
        llamar(herramienta, argumentos)


def test_indicadores_sin_bono_dice_el_motivo() -> None:
    analisis = json.loads((RAIZ / "app/datos/analisis.json").read_text("utf-8"))
    con_bono = {b["municipio_id"] for b in analisis["bono"]}
    props = {
        f["properties"]["zona_id"]: f["properties"] for f in API["zonas"]["features"]
    }
    zona = next(z for z, p in props.items() if p["municipio_id"] not in con_bono)
    r = llamar("indicadores_zona", {"zona_id": zona})
    assert r["bono"] is None
    assert "Bono" in r["bono_motivo"]


def test_esfuerzo_nulo_dice_el_motivo() -> None:
    sin_dato = next(
        z for z, a in API["alquiler"]["zonas"].items() if a["origen"] == "sin_dato"
    )
    r = llamar("indicadores_zona", {"zona_id": sin_dato})
    assert r["esfuerzo"]["esfuerzo"] is None
    assert r["esfuerzo_motivo"]
