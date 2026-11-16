"""Indicadores por zona y año como entidades `KeyPerformanceIndicator` de Smart Data Models (NGSI-LD, forma simplificada).

Uso: python -m mesobra.sdm   (lee `app/datos/analisis.json` y `alquiler.json`, escribe `app/datos/sdm/`)
Modelo fijado en `docs/verificaciones/movilidad-interoperabilidad.md` (fila 3).
"""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from mesobra import api_estatica

RAIZ = Path(__file__).resolve().parents[2]
APP_DATOS = RAIZ / "app/datos"
# El esquema vive en los tests porque la validación es de la CI, pero `main` también lo usa.
ESQUEMA = RAIZ / "tests/fixtures/sdm_esquema.json"
TIPO = "KeyPerformanceIndicator"
CONTEXTO = [
    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
    "https://raw.githubusercontent.com/smart-data-models/dataModel.KeyPerformanceIndicator/master/context.jsonld",
]
# indicador: (bloque, campos, descripción con la unidad, sale de un modelo).
# Dos campos = intervalo {inf, sup} en `kpiValue`. El modelo SDM no tiene campo de unidad: va en `description`.
# «estimado»: siempre si sale de un modelo; si no, solo si la propia fila trae `origen` = estimado.
INDICADORES = {
    "alquiler_eur_m2_p50": (
        "alquiler",
        ("p50",),
        "Alquiler mediano de vivienda colectiva en contratos declarados (SERPAVI), €/m² al mes",
        False,
    ),
    "esfuerzo": (
        "esfuerzo",
        ("esfuerzo",),
        (
            "Cuantía mediana mensual del alquiler (SERPAVI) entre la renta neta media mensual "
            "por hogar (ADRH del INE), fracción; el año es el ejercicio del IRPF"
        ),
        False,
    ),
    "sobrecarga_40": (
        "sobrecarga",
        ("pct_40_inf", "pct_40_sup"),
        "Hogares inquilinos con alquiler sobre el 40 % de su renta, % (intervalo de un modelo log-normal)",
        True,
    ),
    "sobrecarga_30": (
        "sobrecarga",
        ("pct_30_inf", "pct_30_sup"),
        "Hogares inquilinos con alquiler sobre el 30 % de su renta, % (intervalo de un modelo log-normal)",
        True,
    ),
}
LICENCIA_MODELO = "CC BY 4.0"


def _filas(analisis: dict, alquiler: dict, bloque: str) -> list[dict]:
    if bloque == "alquiler":
        return [{"zona_id": z, **v} for z, v in alquiler["zonas"].items()]
    return analisis.get(bloque, [])


def entidades(analisis: dict, alquiler: dict) -> dict[str, list[dict]]:
    """Una entidad por indicador, zona y año con valor; sin dato no se publica."""
    salida = {}
    for nombre, (bloque, campos, texto, modelo) in INDICADORES.items():
        lista = []
        for f in _filas(analisis, alquiler, bloque):
            valores = [f[c] for c in campos]
            if None in valores:
                continue
            estimado = modelo or f.get("origen") == "estimado"
            lista.append(
                {
                    "id": f"urn:ngsi-ld:{TIPO}:{nombre}-{f['zona_id']}-{f['anio']}",
                    "type": TIPO,
                    "kpiValue": valores[0]
                    if len(valores) == 1
                    else dict(zip(("inf", "sup"), valores, strict=True)),
                    "calculationPeriod": {
                        "from": f"{f['anio']}-01-01",
                        "to": f"{f['anio']}-12-31",
                    },
                    "calculationFrequency": "yearly",
                    "area": f["zona_id"],
                    "process": nombre,
                    "description": texto + (", estimado" if estimado else ""),
                    "@context": CONTEXTO,
                }
            )
        salida[nombre] = lista
    return salida


def validar(por_indicador: dict[str, list[dict]], esquema: dict) -> None:
    """Falla en la primera entidad que incumple el esquema o repite `id`."""
    validador = Draft202012Validator(esquema, format_checker=FormatChecker())
    ids = set()
    for e in (e for lista in por_indicador.values() for e in lista):
        validador.validate(e)
        if e["id"] in ids:
            raise ValueError(f"id repetido: {e['id']}")
        ids.add(e["id"])


def _procedencia(nombre: str, meta: dict) -> str:
    """Fuentes, fecha y nota de un fichero de entrada: la nota lleva el origen, la fecha y el «no avala» de cada fuente."""
    fuentes = "\n".join(
        f"- fuente: {f['nombre']}, {f['url']}. Licencia: {f['licencia']}."
        for f in meta["fuentes"]
    )
    nota = " ".join(meta["nota"].split())
    return (
        f"### `{nombre}`, generado el {meta['generado']}\n\n{fuentes}\n"
        f"- Nota del fichero (fuente: `{nombre}`, `meta.nota`): {nota}\n"
    )


def leeme(
    esquema: dict, analisis: dict, alquiler: dict, por_indicador: dict[str, list]
) -> str:
    origen = esquema["x-origen"]
    filas = [
        f"| `{n}` | {t} | `{b}.{'` y `'.join(c)}` | <!-- sin-fuente: umbral o unidad del indicador, no un dato -->"
        for n, (b, c, t, _) in INDICADORES.items()
        if por_indicador[n]
    ]
    metas = (("analisis.json", analisis["meta"]), ("alquiler.json", alquiler["meta"]))
    ine = any(f["nombre"].startswith("INE") for _, m in metas for f in m["fuentes"])
    cita = (
        "Elaboración propia con datos extraídos del sitio web del INE: www.ine.es; la fecha de "
        "actualización de cada tabla del INE va en la nota de su fichero. El INE no participa, "
        "patrocina ni apoya este proyecto, y estos valores son derivados, no cifras del INE.\n\n"
        if ine
        else ""
    )
    return f"""# Indicadores en Smart Data Models

Cada fichero de esta carpeta es una lista de entidades NGSI-LD del modelo **{TIPO}** (Smart Data Models), en forma simplificada. Una entidad por indicador, zona y año; si no hay dato, no hay entidad.

- Modelo y esquema: versión {origen["version"]} del esquema, {origen["esquema"]}. El modelo y su esquema tienen licencia {LICENCIA_MODELO}. <!-- sin-fuente: versión y licencia del esquema -->
- Datos: no llevan la licencia del modelo, sino la de cada fuente (ver «Procedencia y licencia»).
- Copia de validación (resuelve sus referencias sin red): `tests/fixtures/sdm_esquema.json`, con el SHA-256 del original en `x-origen`.

## Campos

- `id`: `urn:ngsi-ld:{TIPO}:<indicador>-<zona_id>-<anio>`, estable.
- `kpiValue`: el valor; en los intervalos, un objeto `{{inf, sup}}`.
- `calculationPeriod`: del primer al último día del año; `calculationFrequency`: `yearly`.
- `area`: código de la zona (o del municipio) del INE.
- `process`: nombre del indicador.
- `description`: qué mide y su unidad, y «estimado» si sale de un modelo o de una imputación. El modelo no tiene campo de unidad.
- `@context`: el núcleo de NGSI-LD y el `context.jsonld` del modelo.

## Indicadores

| Indicador | Qué mide | Sale de |
|---|---|---|
{chr(10).join(filas)}

## Procedencia y licencia

Los valores son los de los ficheros de `app/datos/` que indica «Sale de», reordenados como entidades: no se recalculan ni se redondean. {cita}Procedencia, fecha y licencia de cada fichero:

{chr(10).join(_procedencia(n, m) for n, m in metas)}"""


def escribir(analisis: dict, alquiler: dict, carpeta: Path, esquema: dict) -> None:
    """Valida entradas y salida, y reescribe `carpeta` (borra sus `.json` anteriores)."""
    api_estatica.validar("analisis.json", analisis)
    api_estatica.validar("alquiler.json", alquiler)
    por_indicador = entidades(analisis, alquiler)
    validar(por_indicador, esquema)
    carpeta.mkdir(parents=True, exist_ok=True)
    for viejo in carpeta.glob("*.json"):
        viejo.unlink()
    for nombre, lista in por_indicador.items():
        # Bloque opcional ausente (p. ej. sobrecarga): no se publica un fichero vacío.
        if not lista:
            continue
        compacto = json.dumps(lista, ensure_ascii=False, separators=(",", ":"))
        (carpeta / f"{nombre}.json").write_text(compacto, "utf-8")
    (carpeta / "LEEME.md").write_text(
        leeme(esquema, analisis, alquiler, por_indicador), "utf-8"
    )


def main() -> None:
    leer = lambda p: json.loads(p.read_text("utf-8"))
    escribir(
        leer(APP_DATOS / "analisis.json"),
        leer(APP_DATOS / "alquiler.json"),
        APP_DATOS / "sdm",
        leer(ESQUEMA),
    )


if __name__ == "__main__":
    main()
