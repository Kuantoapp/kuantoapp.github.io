"""Indicadores por zona y año como entidades `KeyPerformanceIndicator` de Smart Data Models (NGSI-LD, forma simplificada).

Uso: python -m mesobra.sdm   (lee `app/datos/analisis.json` y `alquiler.json`, escribe `app/datos/sdm/`)
Modelo fijado en `docs/verificaciones/movilidad-interoperabilidad.md` (fila 3).
"""

import json
import re
from pathlib import Path
from urllib.parse import urlparse

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
            "Cuantía mediana mensual del alquiler de vivienda colectiva (SERPAVI) entre la renta "
            "neta media mensual por hogar (ADRH del INE), fracción; el año es el ejercicio fiscal"
        ),
        False,
    ),
    # Definiciones de F3-06 (#100): todos los cortes cuentan alquiler y suministros.
    "sobrecarga_40": (
        "sobrecarga",
        ("pct_40_inf", "pct_40_sup"),
        (
            "% de hogares inquilinos con alquiler y suministros por encima del 40 % de su renta "
            "(rango de un modelo log-normal: σ del Gini y del P80/P20)"
        ),
        True,
    ),
    "sobrecarga_30": (
        "sobrecarga",
        ("pct_30_inf", "pct_30_sup"),
        (
            "% de hogares inquilinos con alquiler y suministros por encima del 30 % de su renta "
            "(rango de un modelo log-normal: σ del Gini y del P80/P20)"
        ),
        True,
    ),
    "sobrecarga_50": (
        "sobrecarga",
        ("pct_50_inf", "pct_50_sup"),
        (
            "% de hogares inquilinos con alquiler y suministros por encima del 50 % de su renta "
            "(rango de un modelo log-normal: σ del Gini y del P80/P20)"
        ),
        True,
    ),
}
# Mención que exige cada publicador (nota del 16-11 de #110), buscada en el nombre de la fuente y en
# `meta.nota`; además, cada fuente necesita su «actualizado el AAAA-MM-DD».
MENCIONES = {
    # Datos tratados: la cita de «sitio web del INE» a secas es para datos sin tratar (licencia-ine.md).
    "ine.es": "Elaboración propia con datos extraídos del sitio web del INE: www.ine.es",
    "mivau.gob.es": "Origen de los datos: Ministerio de Vivienda y Agenda Urbana",
    "comunidad.madrid": "Fuente de los datos: Comunidad de Madrid",
}
ACTUALIZADO = re.compile(r"actualizad[oa] el \d{4}-\d{2}-\d{2}")
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


def _citas_que_faltan(meta: dict) -> list[str]:
    """Lo que falta de lo que exige cada fuente: su mención (en su nombre o en `meta.nota`) y su fecha (en `meta.nota`)."""
    texto = " ".join(f["nombre"] for f in meta["fuentes"]) + " " + meta["nota"]
    falta = []
    for f in meta["fuentes"]:
        host = urlparse(f["url"]).hostname or ""
        dominio = next(
            (d for d in MENCIONES if host == d or host.endswith("." + d)), None
        )
        if (
            dominio is None
        ):  # una fuente nueva falla hasta que alguien escriba su regla de cita
            falta.append(f"una regla de cita para {host or f['url']} en sdm.MENCIONES")
        elif MENCIONES[dominio] not in texto:
            falta.append(f"«{MENCIONES[dominio]}»")
    # shortcut: cuenta fechas, no las asocia a cada fuente; asociarlas si una nota llega a citar varias de la misma
    if len(ACTUALIZADO.findall(meta["nota"])) < len(meta["fuentes"]):
        falta.append("«actualizado el AAAA-MM-DD» de cada fuente")
    return list(dict.fromkeys(falta))


def _procedencia(nombre: str, meta: dict) -> str:
    """Fuentes, fecha y nota de un fichero de entrada; falla si la nota no trae lo que exigen sus fuentes."""
    if falta := _citas_que_faltan(meta):
        raise ValueError(
            f"{nombre}: falta en meta.nota {', '.join(falta)} (condiciones de las fuentes, nota del 16-11 de #110)"
        )
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
    procedencia = "\n".join(_procedencia(n, m) for n, m in metas)
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

Los valores son los de los ficheros de `app/datos/` que indica «Sale de», reordenados como entidades: no se recalculan ni se redondean. Son derivados, no cifras de los publicadores, y ninguno de ellos participa, patrocina ni apoya este proyecto. La cita, la fecha de actualización y las condiciones que pide cada fuente van en la nota de su fichero (`sdm.py` no escribe nada si falta alguna). Procedencia, fecha y licencia de cada fichero:

{procedencia}"""


def escribir(analisis: dict, alquiler: dict, carpeta: Path, esquema: dict) -> None:
    """Valida entradas y salida, y reescribe `carpeta` (borra sus `.json` anteriores)."""
    api_estatica.validar("analisis.json", analisis)
    api_estatica.validar("alquiler.json", alquiler)
    por_indicador = entidades(analisis, alquiler)
    validar(por_indicador, esquema)
    # El LEEME falla si faltan citas: se genera antes de tocar la carpeta.
    texto = leeme(esquema, analisis, alquiler, por_indicador)
    carpeta.mkdir(parents=True, exist_ok=True)
    for viejo in carpeta.glob("*.json"):
        viejo.unlink()
    for nombre, lista in por_indicador.items():
        # Bloque opcional ausente (p. ej. sobrecarga): no se publica un fichero vacío.
        if not lista:
            continue
        compacto = json.dumps(lista, ensure_ascii=False, separators=(",", ":"))
        (carpeta / f"{nombre}.json").write_text(compacto, "utf-8")
    (carpeta / "LEEME.md").write_text(texto, "utf-8")


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
