"""Cálculo de referencia de «¿Me sobra?»: sobrante, horas de viaje y precio de la hora por zona.

Funciones puras, solo stdlib, sobre los ficheros de la API estática ya leídos, para que el servidor
MCP se instale ligero. `api` es un dict con el contenido de `alquiler`, `hogares`, `netos`, `tarifas`
y `tiempos` (`.json`) y `zonas` (`zonas.geojson`). Es la cuenta que reproduce el JS (F1-07, #75) con
`tests/fixtures/casos_referencia.json`. Tras cambiar la cuenta, las salidas de ese fichero se
regeneran (las entradas no se tocan) con:

    python -m mesobra.calculo

Entrada de `calcular` (un dict):
- `hogar`: `perfil` y `edad`; opcionales `adultos`, `hijos`, `personas_comparten` y `m2` (por
  defecto, los del perfil de `hogares.json`).
- `sueldos`: 1 o 2, cada uno con `destino` (`destino_id`), `dias` (1 a 5), `modo` (`tp` o `coche`),
  `bruto` (€/año) o `neto_mes` (€/mes), y opcional `viajes_dia` (2 o 4; por defecto 2).
- Opcionales: `escenario` (`tarifas`: `vigente_2026` o `sin_descuento`; `subida_alquiler` en %;
  `edad`, que sustituye a la del hogar), `zonas` (por defecto, los orígenes de `tiempos.json`) y
  `ref` (zona de referencia).

Supuestos:
1. sobra = neto − alquiler − transporte − cesta, en €/mes del hogar; esfuerzo = alquiler ÷ neto.
2. Alquiler = €/m² × factor_ipc × (1 + subida/100) × m² del hogar ÷ personas_comparten (unidades que
   pagan el alquiler, #82). Se da con P25, P50 y P75; el sobrante central usa P50.
3. Banda del sobrante: €/m² mínimo entre P25 y el límite inferior del intervalo (zona estimada) da el
   sobrante alto; el máximo entre P75 y el superior, el bajo. El margen del neto no entra: la rejilla
   da un solo valor.
4. Neto: interpolación lineal en `brutos` de `netos.json`; fuera de la tabla, `ValueError` (no se
   extrapola). Monoparental = 1 adulto con hijos; cada sueldo usa los hijos del hogar (#183).
5. Transporte público: tabla de `tarifas.json` con la corona más exterior entre origen y destino; tarifa
   joven si edad ≤ `edad_max_joven`. Un destino sin corona conocida (los polos, hasta F3-01) da error.
6. Coche: 2 × km × días × semanas_mes × `eur_km`, sin aparcamiento ni congestión (F3-02, #96).
7. Horas al mes = Σ sueldos de minutos de ida × 2 × días × `semanas_mes` ÷ 60, con `semanas_mes` del
   calendario laboral de `tarifas.json` (3,7833 en 2026, #197), no 4,33.
8. Referencia por defecto: la zona con menos horas entre las que tienen sobrante y horas. Si la
   diferencia de horas con ella es menor de 5 al mes, `precio_hora` es nulo y `etiqueta` es «mismo tiempo».
9. Cesta por unidades de consumo OCDE modificada con el hogar del visitante (#180, `hogares.py`).
"""

import json
from bisect import bisect_right
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[2]
API_EJEMPLO = RAIZ / "tests/fixtures/api"
CASOS = RAIZ / "tests/fixtures/casos_referencia.json"

UMBRAL_HORAS = 5.0
MISMO_TIEMPO = "mismo tiempo"
EDAD_MIN, EDAD_MAX = (
    16,
    64,
)  # edad legal para trabajar; el neto supone menos de 65 años (#183)
MODOS = ("tp", "coche")

Api = dict[str, Any]


def precio_hora(
    sobra: float | None,
    horas: float | None,
    sobra_ref: float | None,
    horas_ref: float | None,
) -> tuple[float | None, str | None]:
    """(€ ganados por hora extra de viaje al mes frente a la referencia, etiqueta)."""
    if None in (sobra, horas, sobra_ref, horas_ref):
        return None, None
    dif = horas - horas_ref
    if abs(dif) < UMBRAL_HORAS:
        return None, MISMO_TIEMPO
    return (sobra - sobra_ref) / dif, None


def neto_mes(netos: dict, bruto: float, hogar: dict) -> float:
    """Neto €/mes de un sueldo bruto anual, interpolado en la rejilla de `netos.json`."""
    brutos, maximo = netos["brutos"], max(c["hijos"] for c in netos["configuraciones"])
    if not 0 <= hogar["hijos"] <= maximo:
        raise ValueError(
            f"hijos = {hogar['hijos']}: la tabla de netos llega a {maximo}"
        )
    if not brutos[0] <= bruto <= brutos[-1]:
        raise ValueError(
            f"bruto {bruto} €/año fuera de la tabla de netos "
            f"({brutos[0]}–{brutos[-1]}): pide el neto mensual"
        )
    conf = {
        "hijos": hogar["hijos"],
        "monoparental": hogar["adultos"] == 1 and hogar["hijos"] >= 1,
    }
    j = netos["configuraciones"].index(conf)
    i = max(min(bisect_right(brutos, bruto), len(brutos) - 1), 1)
    y0, y1 = netos["neto_anual"][i - 1][j], netos["neto_anual"][i][j]
    t = (bruto - brutos[i - 1]) / (brutos[i] - brutos[i - 1])
    return (y0 + t * (y1 - y0)) / 12


def cesta(cesta_uc: dict, hogar: dict) -> float:
    """Alimentación propia más la parte de suministros del piso, €/mes."""
    uc = 1 + 0.5 * (hogar["adultos"] - 1) + 0.3 * hogar["hijos"]
    p = hogar["personas_comparten"]
    return (
        cesta_uc["alimentacion"] * uc
        + cesta_uc["suministros"] * (uc + 0.5 * (p - 1)) / p
    )


def alquiler(zona: dict, hogar: dict, subida: float) -> dict[str, float] | None:
    """Alquiler €/mes del hogar con P25, P50, P75 y los extremos de la banda; None sin dato."""
    if zona["origen"] == "sin_dato":
        return None
    k = (
        zona["factor_ipc"]
        * (1 + subida / 100)
        * hogar["m2"]
        / hogar["personas_comparten"]
    )
    bajo, alto = zona["p25"], zona["p75"]
    if zona["ic"]:
        bajo, alto = min(bajo, zona["ic"][0]), max(alto, zona["ic"][1])
    eur_m2 = {
        "p25": zona["p25"],
        "p50": zona["p50"],
        "p75": zona["p75"],
        "min": bajo,
        "max": alto,
    }
    return {c: v * k for c, v in eur_m2.items()}


def _celda(tiempos: dict, matriz: str, origen: str, destino: str) -> float | None:
    destinos = [d["destino_id"] for d in tiempos["destinos"]]
    if (
        matriz not in tiempos
        or origen not in tiempos["origenes"]
        or destino not in destinos
    ):
        raise ValueError(f"tiempos.json no tiene {matriz} de {origen} a {destino}")
    return tiempos[matriz][tiempos["origenes"].index(origen)][destinos.index(destino)]


def _corona(api: Api, origen: str, destino: str) -> str:
    """La corona más exterior entre origen y destino."""
    orden = api["tarifas"]["orden_coronas"]
    coronas = {
        f["properties"]["zona_id"]: f["properties"]["corona"]
        for f in api["zonas"]["features"]
    }
    par = [coronas.get(origen), coronas.get(destino)]
    if any(c not in orden for c in par):
        raise ValueError(
            f"{origen} → {destino}: coronas {par} sin tarifa (orden_coronas {orden})"
        )
    return max(par, key=orden.index)


def viaje(
    api: Api, sueldo: dict, origen: str, escenario: dict
) -> tuple[float | None, float | None]:
    """(horas al mes, coste €/mes) del viaje al trabajo de un sueldo; None si no hay ruta."""
    tarifas, tiempos, dias = api["tarifas"], api["tiempos"], sueldo["dias"]
    semanas, destino = tarifas["semanas_mes"], sueldo["destino"]
    minutos = _celda(tiempos, sueldo["modo"], origen, destino)
    if sueldo["modo"] == "coche":
        km = _celda(tiempos, "km_coche", origen, destino)
        coste = (
            None
            if km is None
            else 2 * km * dias * semanas * tiempos["coste_coche"]["eur_km"]
        )
    else:
        edad = "joven" if escenario["edad"] <= tarifas["edad_max_joven"] else "general"
        tabla = tarifas["escenarios"][escenario["tarifas"]][edad][
            str(sueldo["viajes_dia"])
        ]
        coste = tabla[_corona(api, origen, destino)][dias - 1]["coste_mes"]
    horas = None if minutos is None else minutos * 2 * dias * semanas / 60
    return horas, coste


def _suma(valores: list[float | None]) -> float | None:
    return None if None in valores else sum(valores)


def calcular_zona(
    api: Api, hogar: dict, sueldos: list[dict], zona: str, escenario: dict
) -> dict:
    """Sobrante, banda, horas y esfuerzo de vivir en `zona` (sin `precio_hora`, que pide la referencia)."""
    neto = sum(s["neto_mes"] for s in sueldos)
    alq = alquiler(api["alquiler"]["zonas"][zona], hogar, escenario["subida_alquiler"])
    horas, costes = zip(*(viaje(api, s, zona, escenario) for s in sueldos), strict=True)
    resto = _suma([*costes]), cesta(api["hogares"]["cesta_uc"], hogar)
    fijo = None if alq is None or resto[0] is None else neto - resto[0] - resto[1]
    return {
        "origen": api["alquiler"]["zonas"][zona]["origen"],
        "neto": neto,
        "alquiler": None if alq is None else alq["p50"],
        "alquiler_p25": None if alq is None else alq["p25"],
        "alquiler_p75": None if alq is None else alq["p75"],
        "transporte": resto[0],
        "cesta": resto[1],
        "sobra": None if fijo is None else fijo - alq["p50"],
        "sobra_banda": None if fijo is None else [fijo - alq["max"], fijo - alq["min"]],
        "horas": _suma([*horas]),
        "esfuerzo": None if alq is None else alq["p50"] / neto,
    }


def _entero(nombre: str, valor: Any, rango: range) -> None:
    if type(valor) is not int or valor not in rango:
        raise ValueError(
            f"{nombre} = {valor!r}: debe ser un entero de {rango.start} a {rango.stop - 1}"
        )


def _hogar(api: Api, entrada: dict) -> tuple[dict, dict]:
    """Hogar con los valores del perfil por defecto y escenario completo, validados."""
    h = entrada["hogar"]
    if h.get("perfil") not in api["hogares"]["perfiles"]:
        raise ValueError(f"perfil desconocido: {h.get('perfil')!r}")
    hogar = {**api["hogares"]["perfiles"][h["perfil"]], **h}
    esc = {"tarifas": "vigente_2026", "subida_alquiler": 0.0, "edad": hogar["edad"]}
    esc |= {k: v for k, v in entrada.get("escenario", {}).items() if v is not None}
    _entero("edad", esc["edad"], range(EDAD_MIN, EDAD_MAX + 1))
    _entero("adultos", hogar["adultos"], range(1, 3))
    _entero("hijos", hogar["hijos"], range(10))
    _entero("personas_comparten", hogar["personas_comparten"], range(1, 21))
    if not hogar["m2"] > 0 or esc["tarifas"] not in api["tarifas"]["escenarios"]:
        raise ValueError(
            f"m2 = {hogar['m2']!r} o escenario {esc['tarifas']!r} inválido"
        )
    return hogar, esc


def _sueldos(api: Api, entrada: dict, hogar: dict) -> list[dict]:
    """Sueldos validados, con `viajes_dia` y `neto_mes`."""
    sueldos = entrada["sueldos"]
    if not 1 <= len(sueldos) <= hogar["adultos"]:
        raise ValueError(f"{len(sueldos)} sueldos para {hogar['adultos']} adultos")
    salida = []
    for s in sueldos:
        s = {"viajes_dia": 2, **s}
        _entero("dias", s["dias"], range(1, 6))
        if (
            s["modo"] not in MODOS
            or s["viajes_dia"] not in api["tarifas"]["viajes_dia"]
        ):
            raise ValueError(
                f"modo {s['modo']!r} o viajes_dia {s['viajes_dia']!r} inválido"
            )
        if "neto_mes" not in s:
            s["neto_mes"] = neto_mes(api["netos"], s["bruto"], hogar)
        elif not s["neto_mes"] > 0:
            raise ValueError(f"neto_mes = {s['neto_mes']!r}: debe ser positivo")
        salida.append(s)
    return salida


def calcular(api: Api, entrada: dict) -> dict:
    """Resultado por zona con `precio_hora` frente a la referencia (ver el docstring del módulo)."""
    hogar, escenario = _hogar(api, entrada)
    sueldos = _sueldos(api, entrada, hogar)
    ref = entrada.get("ref")
    zonas = list(
        dict.fromkeys(
            [*entrada.get("zonas", api["tiempos"]["origenes"]), *([ref] if ref else [])]
        )
    )
    res = {z: calcular_zona(api, hogar, sueldos, z, escenario) for z in zonas}
    if ref is None:
        validas = [
            z
            for z in zonas
            if res[z]["sobra"] is not None and res[z]["horas"] is not None
        ]
        ref = min(validas, key=lambda z: res[z]["horas"], default=None)
    r = res.get(ref, {"sobra": None, "horas": None})
    for z in res.values():
        z["precio_hora"], z["etiqueta"] = precio_hora(
            z["sobra"], z["horas"], r["sobra"], r["horas"]
        )
    return {"ref": ref, "zonas": res}


def leer_api(carpeta: Path) -> Api:
    """Los ficheros de la API estática de `carpeta`, ya leídos."""
    nombres = ["alquiler", "hogares", "netos", "tarifas", "tiempos"]
    api = {n: json.loads((carpeta / f"{n}.json").read_text("utf-8")) for n in nombres}
    return api | {"zonas": json.loads((carpeta / "zonas.geojson").read_text("utf-8"))}


def resolver(api: Api, entrada: dict) -> dict:
    """Salida de un caso de referencia: el resultado o el error que da."""
    try:
        return {"salida": calcular(api, entrada)}
    except ValueError as e:
        return {"error": str(e)}


def main() -> None:
    """Regenera las salidas de `casos_referencia.json` con los ficheros de ejemplo de la API."""
    api, doc = leer_api(API_EJEMPLO), json.loads(CASOS.read_text("utf-8"))
    doc["casos"] = [
        {"nombre": c["nombre"], "entrada": c["entrada"], **resolver(api, c["entrada"])}
        for c in doc["casos"]
    ]
    CASOS.write_text(
        json.dumps(doc, ensure_ascii=False, indent=1) + "\n", "utf-8", newline="\n"
    )


if __name__ == "__main__":
    main()
