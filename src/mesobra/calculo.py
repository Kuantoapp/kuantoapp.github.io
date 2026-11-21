"""Cálculo de referencia de Kuanto: sobrante, horas de viaje y precio de la hora por zona.

Funciones puras, solo stdlib, sobre los ficheros de la API estática ya leídos, para que el servidor
MCP se instale ligero. `api` es un dict con el contenido de `alquiler`, `hogares`, `netos`, `tarifas`
y `tiempos` (`.json`) y `zonas` (`zonas.geojson`). Es la cuenta que reproduce el JS (F1-07, #75) con
`tests/fixtures/casos_referencia.json`. Tras cambiar la cuenta, las salidas de ese fichero se
regeneran (las entradas no se tocan) con:

    python -m mesobra.calculo

Entrada de `calcular` (un dict):
- `hogar`: `perfil` y `edad`; opcionales `adultos`, `hijos`, `personas_comparten` y `m2` (por
  defecto, los del perfil de `hogares.json`), `edades_hijos` (vacía, o una edad de 0 a `edad_max_joven`
  por hijo), `familia` (`ordinario`, `fn_general` o `fn_especial`; las numerosas piden 2 hijos o más) y
  `no_laborables` (viajes de ocio al mes: 0, 8 o 16; por defecto 0).
- `sueldos`: 1 o 2, cada uno con `destino` (`destino_id`), `dias` (1 a 5), `modo` (`tp` o `coche`),
  `bruto` (€/año) o `neto_mes` (€/mes, neto anual ÷ 12; con 14 pagas, suma de las nóminas del año ÷ 12), y
  opcionales `viajes_dia` (2 o 4; por defecto 2), `edad` (por defecto, la del escenario, que por defecto
  es la del hogar) y `discapacidad` (`true`: grado igual o superior al 65 %; por defecto `false`).
- Opcionales: `escenario` (`tarifas`: `vigente_2026` o `sin_descuento`; `subida_alquiler` en %;
  `edad`, que sustituye a la del hogar; `cesta`: `media` o `tramo`), `zonas` (por defecto, los orígenes de `tiempos.json`) y
  `ref` (zona de referencia).

Salida: `{"ref", "escenario" (el aplicado, con sus valores por defecto), "zonas": {zona_id: {...}}}`.

Supuestos:
1. sobra = neto − alquiler − transporte − cesta, en €/mes del hogar; esfuerzo = alquiler ÷ neto.
2. Alquiler = €/m² × factor_ipc × (1 + subida/100) × m² del hogar ÷ personas_comparten (unidades que
   pagan el alquiler, #82). Se da con P25, P50 y P75; el sobrante central usa P50.
3. Banda del sobrante: €/m² mínimo entre P25 y el límite inferior del intervalo (zona estimada) da el
   sobrante alto; el máximo entre P75 y el superior, el bajo. El margen del neto no entra: la rejilla
   da un solo valor.
4. Neto: interpolación lineal en `brutos` de `netos.json`; fuera de la tabla, `ValueError` (no se
   extrapola). Monoparental = 1 adulto con hijos; cada sueldo usa los hijos del hogar (#183).
5. Transporte público de todo el hogar (#164), con la v2 de `tarifas.json`: la clave de la ruta
   (`clave_tarifa` del par origen-destino; con 4 viajes al día, la de la misma ruta con cambio de
   operador, `transbordo`), los viajes no laborables, la edad y el colectivo de cada sueldo
   (`tarifas_ruta`). Tarifa joven si edad ≤ `edad_max_joven`. El colectivo es el de la familia más la
   discapacidad de la persona. Un par sin clave da error. Cada hijo de 15 a `edad_max_joven` años
   suma un Abono Joven (a 5 días, en la ruta del primer sueldo: es plano) con el colectivo de la
   familia; los menores de 15 años no pagan (BOCM-20251231-2, pág. 66). Sin `edades_hijos` no se cuentan.
   shortcut: la edad mayor de 64 (Abono +65) no se calcula, porque el neto supone menores de 65 años;
   cuando se admita, `tarifa` ya pide la edad `mayor_65` (verificar si basta con 65 cumplidos).
6. Coche: 2 × km × días × semanas_mes × `eur_km`, sin aparcamiento ni congestión (F3-02, #96).
7. Horas al mes = Σ sueldos de minutos de ida × 2 × días × `semanas_mes` ÷ 60, con `semanas_mes` del
   calendario laboral de `tarifas.json` (3,7833 en 2026, #197), no 4,33.
8. Referencia por defecto: la zona con menos horas entre las que tienen sobrante y horas. Si la
   diferencia de horas con ella es menor de 5 al mes, `precio_hora` es nulo y `etiqueta` es «mismo tiempo»;
   la propia referencia lleva `etiqueta` «referencia». Una `ref` pedida sin sobrante u horas da error.
   Sin ruta (minutos nulos), el viaje no tiene horas ni coste, y la zona queda sin sobrante.
9. Cesta por unidades de consumo OCDE modificada con el hogar del visitante (#180, `hogares.py`).
10. Escenario `cesta`: `media` (por defecto, la referencia) o `tramo`, que multiplica la alimentación por
   el cociente de la EPF de España del tramo de ingresos del neto del hogar (`cesta_tramos` de
   `hogares.json`, `hogares.factores_tramo`; estimado, #312). El neto ÷ 12 equivale al ingreso mensual de la
   EPF, que prorratea las pagas extra (la EPF suma además otras rentas del hogar, que aquí no entran);
   en «comparte», el neto propio (la EPF cuenta aparte a quien no
   comparte gastos).
"""

import json
import math
from bisect import bisect_right
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[2]
API_EJEMPLO = RAIZ / "tests/fixtures/api"
CASOS = RAIZ / "tests/fixtures/casos_referencia.json"

UMBRAL_HORAS = 5.0
MISMO_TIEMPO = "mismo tiempo"
REFERENCIA = "referencia"
# 16: edad mínima para trabajar (ET art. 6.1, BOE-A-2015-11430); 64: el neto supone no tener
# el mínimo por edad de más de 65 años (LIRPF art. 57.2, BOE-A-2006-20764; #183).
EDAD_MIN, EDAD_MAX = 16, 64
MODOS = ("tp", "coche")
ESCENARIO = {"tarifas", "subida_alquiler", "edad", "cesta"}
CESTAS = ("media", "tramo")
FAMILIAS = ("ordinario", "fn_general", "fn_especial")
EDAD_MIN_JOVEN = 15  # BOCM-20251231-2, pág. 66: de 7 a 14 años el abono es gratuito

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
    if type(bruto) not in (int, float):
        raise ValueError(f"bruto = {bruto!r}: debe ser un número")
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


def tramo_cesta(tramos: list[dict], neto: float) -> dict:
    """Tramo de ingresos de la EPF del neto €/mes del hogar: el último con `desde` ≤ neto (estimado, #312)."""
    return tramos[bisect_right([t["desde"] for t in tramos], neto) - 1]


def cesta(cesta_uc: dict, hogar: dict, factor: float) -> float:
    """Alimentación propia (× `factor` del tramo de ingresos) más la parte de suministros y comunicaciones del piso, €/mes."""
    uc = 1 + 0.5 * (hogar["adultos"] - 1) + 0.3 * hogar["hijos"]
    p = hogar["personas_comparten"]
    return (
        cesta_uc["alimentacion"] * factor * uc
        + (cesta_uc["suministros"] + cesta_uc["comunicaciones"])
        * (uc + 0.5 * (p - 1))
        / p
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


def tarifa(api: Api, origen: str, destino: str, sueldo: dict, escenario: str) -> dict:
    """Título y coste del mes (`{titulo, coste_mes}`) de la ruta de `origen` a `destino` en transporte
    público para un `sueldo` ya preparado (`dias`, `viajes_dia`, `edad`, `colectivo`, `no_laborables`)."""
    t = api["tarifas"]
    if origen not in t["origenes"] or destino not in t["destinos"]:
        raise ValueError(f"tarifas.json no tiene la ruta {origen} → {destino}")
    k = t["clave_tarifa"][t["origenes"].index(origen)][t["destinos"].index(destino)]
    if k is not None and sueldo["viajes_dia"] == 4:
        k = t["transbordo"][k]
    if k is None:
        raise ValueError(f"{origen} → {destino}: sin clave de tarifa")
    edad = "joven" if sueldo["edad"] <= t["edad_max_joven"] else "general"
    por_clave = t["tarifas_ruta"][escenario][sueldo["colectivo"]][edad][t["claves"][k]]
    return por_clave[str(sueldo["no_laborables"])][sueldo["dias"] - 1]


def viaje(
    api: Api, sueldo: dict, origen: str, escenario: dict
) -> tuple[float | None, float | None]:
    """(horas al mes, coste €/mes) del viaje al trabajo de un sueldo; None si no hay ruta."""
    tarifas, tiempos, dias = api["tarifas"], api["tiempos"], sueldo["dias"]
    semanas, destino = tarifas["semanas_mes"], sueldo["destino"]
    minutos = _celda(tiempos, sueldo["modo"], origen, destino)
    if minutos is None:  # sin ruta no hay viaje que pagar: ni horas ni coste
        return None, None
    if sueldo["modo"] == "coche":
        km = _celda(tiempos, "km_coche", origen, destino)
        coste = (
            None
            if km is None
            else 2 * km * dias * semanas * tiempos["coste_coche"]["eur_km"]
        )
    else:
        coste = tarifa(api, origen, destino, sueldo, escenario["tarifas"])["coste_mes"]
    return minutos * 2 * dias * semanas / 60, coste


def hijos_jovenes(api: Api, hogar: dict) -> int:
    """Hijos con Abono Joven: de `EDAD_MIN_JOVEN` a `edad_max_joven` años."""
    return sum(
        EDAD_MIN_JOVEN <= e <= api["tarifas"]["edad_max_joven"]
        for e in hogar["edades_hijos"]
    )


def coste_hijos(
    api: Api, hogar: dict, sueldos: list[dict], zona: str, escenario: dict
) -> float:
    """Abonos Jóvenes de los hijos, €/mes: a 5 días y en la ruta del primer sueldo (el precio es plano)."""
    n = hijos_jovenes(api, hogar)
    if n == 0:
        return 0.0
    hijo = {
        "dias": 5,
        "viajes_dia": 2,
        "edad": EDAD_MIN_JOVEN,
        "colectivo": hogar["familia"],
        "no_laborables": hogar["no_laborables"],
    }
    destino = sueldos[0]["destino"]
    return n * tarifa(api, zona, destino, hijo, escenario["tarifas"])["coste_mes"]


def _suma(valores: list[float | None]) -> float | None:
    return None if None in valores else sum(valores)


def calcular_zona(
    api: Api, hogar: dict, sueldos: list[dict], zona: str, escenario: dict
) -> dict:
    """Sobrante, banda, horas y esfuerzo de vivir en `zona` (sin `precio_hora`, que pide la referencia)."""
    neto = sum(s["neto_mes"] for s in sueldos)
    alq = alquiler(api["alquiler"]["zonas"][zona], hogar, escenario["subida_alquiler"])
    horas, costes = zip(*(viaje(api, s, zona, escenario) for s in sueldos), strict=True)
    transporte = _suma([*costes, coste_hijos(api, hogar, sueldos, zona, escenario)])
    factor = (
        tramo_cesta(api["hogares"]["cesta_tramos"], neto)["factor"]
        if escenario["cesta"] == "tramo"
        else 1.0
    )
    cesta_mes = cesta(api["hogares"]["cesta_uc"], hogar, factor)
    fijo = None if alq is None or transporte is None else neto - transporte - cesta_mes
    return {
        "origen": api["alquiler"]["zonas"][zona]["origen"],
        "neto": neto,
        "alquiler": None if alq is None else alq["p50"],
        "alquiler_p25": None if alq is None else alq["p25"],
        "alquiler_p75": None if alq is None else alq["p75"],
        "transporte": transporte,
        "cesta": cesta_mes,
        "sobra": None if fijo is None else fijo - alq["p50"],
        "sobra_banda": None if fijo is None else [fijo - alq["max"], fijo - alq["min"]],
        "horas": _suma(list(horas)),
        "esfuerzo": None if alq is None else alq["p50"] / neto,
    }


def _entero(nombre: str, valor: Any, rango: range) -> None:
    if type(valor) is not int or valor not in rango:
        raise ValueError(
            f"{nombre} = {valor!r}: debe ser un entero de {rango.start} a {rango.stop - 1}"
        )


def _numero(nombre: str, valor: Any, minimo: float) -> None:
    """`valor` es un número finito (no bool) mayor que `minimo`."""
    if (
        type(valor) not in (int, float)
        or not math.isfinite(valor)
        or not valor > minimo
    ):
        raise ValueError(f"{nombre} = {valor!r}: debe ser un número mayor que {minimo}")


def _estructura(entrada: Any) -> None:
    """La entrada es un objeto con `hogar` y `sueldos`, y cada parte del tipo esperado."""
    claves = entrada.keys() if isinstance(entrada, dict) else set()
    if {"hogar", "sueldos"} - claves:
        raise ValueError("entrada sin hogar o sueldos (debe ser un objeto con ambos)")
    for clave, tipo in {
        "hogar": dict,
        "sueldos": list,
        "escenario": dict,
        "zonas": list,
    }.items():
        if clave in entrada and not isinstance(entrada[clave], tipo):
            raise ValueError(f"{clave}: debe ser de tipo {tipo.__name__}")
    ids = [*entrada.get("zonas", []), entrada.get("ref")]
    if not all(isinstance(s, dict) for s in entrada["sueldos"]) or not all(
        i is None or isinstance(i, str) for i in ids
    ):
        raise ValueError("cada sueldo debe ser un objeto, y zonas y ref, textos")


def _transporte_hogar(api: Api, hogar: dict) -> None:
    """Valida `edades_hijos`, `familia` y `no_laborables` del hogar."""
    edades = hogar["edades_hijos"]
    if not isinstance(edades, list) or len(edades) not in (0, hogar["hijos"]):
        raise ValueError(
            f"edades_hijos = {edades!r}: debe estar vacía o tener una edad por hijo ({hogar['hijos']})"
        )
    for e in edades:
        _entero("edades_hijos", e, range(api["tarifas"]["edad_max_joven"] + 1))
    if hogar["familia"] not in FAMILIAS:
        raise ValueError(
            f"familia = {hogar['familia']!r}: debe ser {' o '.join(FAMILIAS)}"
        )
    if hogar["familia"] != "ordinario" and hogar["hijos"] < 2:
        raise ValueError(f"familia numerosa con {hogar['hijos']} hijos: pide 2 o más")
    if hogar["no_laborables"] not in api["tarifas"]["no_laborables"]:
        raise ValueError(
            f"no_laborables = {hogar['no_laborables']!r}: debe ser {api['tarifas']['no_laborables']}"
        )


def _hogar(api: Api, entrada: dict) -> tuple[dict, dict]:
    """Hogar con los valores del perfil por defecto y escenario completo, validados."""
    h = entrada["hogar"]
    if (
        type(h.get("perfil")) is not str
        or h["perfil"] not in api["hogares"]["perfiles"]
    ):
        raise ValueError(f"perfil desconocido: {h.get('perfil')!r}")
    hogar = {
        "edades_hijos": [],
        "familia": "ordinario",
        "no_laborables": 0,
        **api["hogares"]["perfiles"][h["perfil"]],
        **h,
    }
    pedido = entrada.get("escenario", {})
    if extra := set(pedido) - ESCENARIO:
        raise ValueError(f"escenario con claves desconocidas: {sorted(extra)}")
    _entero("edad", hogar.get("edad"), range(EDAD_MIN, EDAD_MAX + 1))
    esc = {
        "tarifas": "vigente_2026",
        "subida_alquiler": 0.0,
        "edad": hogar["edad"],
        "cesta": "media",
    }
    esc |= {k: v for k, v in pedido.items() if v is not None}
    _numero("subida_alquiler", esc["subida_alquiler"], -100)
    _entero("edad", esc["edad"], range(EDAD_MIN, EDAD_MAX + 1))
    _entero("adultos", hogar["adultos"], range(1, 3))
    maximo = max(c["hijos"] for c in api["netos"]["configuraciones"])
    _entero(
        "hijos", hogar["hijos"], range(maximo + 1)
    )  # la rejilla de netos llega a 2 (#183)
    _entero("personas_comparten", hogar["personas_comparten"], range(1, 21))
    _numero("m2", hogar["m2"], 0)
    _transporte_hogar(api, hogar)
    if (
        type(esc["tarifas"]) is not str
        or esc["tarifas"] not in api["tarifas"]["tarifas_ruta"]
    ):
        raise ValueError(f"escenario {esc['tarifas']!r} inválido")
    if esc["cesta"] not in CESTAS:
        raise ValueError(f"cesta = {esc['cesta']!r}: debe ser {' o '.join(CESTAS)}")
    return hogar, esc


def _colectivo(hogar: dict, sueldo: dict) -> str:
    """Colectivo de `tarifas.json` de una persona: su familia más su discapacidad del 65 % o más."""
    if not sueldo["discapacidad"]:
        return hogar["familia"]
    return (
        "discapacidad"
        if hogar["familia"] == "ordinario"
        else f"{hogar['familia']}_discapacidad"
    )


def _sueldos(api: Api, entrada: dict, hogar: dict, escenario: dict) -> list[dict]:
    """Sueldos validados, con `viajes_dia`, `neto_mes`, `edad`, `colectivo` y `no_laborables`."""
    sueldos = entrada["sueldos"]
    if not 1 <= len(sueldos) <= hogar["adultos"]:
        raise ValueError(f"{len(sueldos)} sueldos para {hogar['adultos']} adultos")
    salida = []
    for s in sueldos:
        if faltan := {"destino", "dias", "modo"} - s.keys():
            raise ValueError(f"sueldo sin {sorted(faltan)}")
        s = {"viajes_dia": 2, "edad": escenario["edad"], "discapacidad": False, **s}
        _entero("dias", s["dias"], range(1, 6))
        _entero("edad", s["edad"], range(EDAD_MIN, EDAD_MAX + 1))
        if type(s["discapacidad"]) is not bool:
            raise ValueError(
                f"discapacidad = {s['discapacidad']!r}: debe ser verdadero o falso"
            )
        s["colectivo"] = _colectivo(hogar, s)
        s["no_laborables"] = hogar["no_laborables"]
        if (
            s["modo"] not in MODOS
            or type(s["viajes_dia"]) is not int
            or s["viajes_dia"] not in api["tarifas"]["viajes_dia"]
        ):
            raise ValueError(
                f"modo {s['modo']!r} o viajes_dia {s['viajes_dia']!r} inválido"
            )
        if ("bruto" in s) == ("neto_mes" in s):
            raise ValueError("cada sueldo lleva bruto o neto_mes, uno de los dos")
        if "bruto" in s:
            s["neto_mes"] = neto_mes(api["netos"], s["bruto"], hogar)
        else:
            _numero("neto_mes", s["neto_mes"], 0)
        salida.append(s)
    return salida


def calcular(api: Api, entrada: dict) -> dict:
    """Resultado por zona con `precio_hora` frente a la referencia (ver el docstring del módulo)."""
    _estructura(entrada)
    hogar, escenario = _hogar(api, entrada)
    sueldos = _sueldos(api, entrada, hogar, escenario)
    ref = entrada.get("ref")
    zonas = list(
        dict.fromkeys(
            [
                *entrada.get("zonas", api["tiempos"]["origenes"]),
                *([] if ref is None else [ref]),
            ]
        )
    )
    if desconocidas := [z for z in zonas if z not in api["alquiler"]["zonas"]]:
        raise ValueError(f"zonas sin entrada en alquiler.json: {desconocidas}")
    res = {z: calcular_zona(api, hogar, sueldos, z, escenario) for z in zonas}
    if ref is None:
        validas = [
            z
            for z in zonas
            if res[z]["sobra"] is not None and res[z]["horas"] is not None
        ]
        ref = min(validas, key=lambda z: res[z]["horas"], default=None)
    elif res[ref]["sobra"] is None or res[ref]["horas"] is None:
        raise ValueError(f"zona de referencia {ref} sin sobrante u horas")
    r = res.get(ref, {"sobra": None, "horas": None})
    for z in res.values():
        z["precio_hora"], z["etiqueta"] = precio_hora(
            z["sobra"], z["horas"], r["sobra"], r["horas"]
        )
    if ref is not None:
        res[ref]["etiqueta"] = REFERENCIA
    return {"ref": ref, "escenario": escenario, "zonas": res}


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
    casos = [
        {"nombre": c["nombre"], "entrada": c["entrada"], **resolver(api, c["entrada"])}
        for c in doc["casos"]
    ]
    # Un caso por línea: el diff se lee y el PR no pasa de 800 líneas.
    lineas = ",\n".join(f"  {json.dumps(c, ensure_ascii=False)}" for c in casos)
    nota = json.dumps(doc["nota"], ensure_ascii=False)
    texto = f'{{\n "nota": {nota},\n "casos": [\n{lineas}\n ]\n}}\n'
    CASOS.write_text(texto, "utf-8", newline="\n")


if __name__ == "__main__":
    main()
