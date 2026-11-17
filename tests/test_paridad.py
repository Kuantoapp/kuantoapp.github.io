"""Paridad entre `app/calculo.js` (Node) y `mesobra.calculo` (Python) sobre los datos reales de `app/datos/`.

`node --test` (#75) contrasta el JS con `tests/fixtures/casos_referencia.json` sobre los ejemplos; este test
usa los ficheros reales y exige las mismas cifras para las 199 zonas, con los nulos comparados (nulo en un
lado y cero en el otro es un fallo). Se salta si no hay Node o aún no hay datos reales.

Casos fijos (hogar y sueldo bruto anual; el resto, por defecto):
- GETAFE: perfil `solo`, 30 años, 24.000 €, trabaja en Getafe (28065), 5 días, 2 viajes al día, transporte público.
  Es el caso de la nota del 16-11 de #77: deja zonas sin alquiler y sin ruta, así que prueba los nulos.
- CUATRO_VIAJES: perfil `comparte`, 30 años (tarifa general: el Abono Joven es plano), 30.000 €, trabaja en el distrito Centro (2807901),
  3 días, 4 viajes al día (cambio de operador en cada sentido): usa la fila `"4"` de `tarifas.json`.
"""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest

from mesobra import calculo

RAIZ = Path(__file__).resolve().parents[1]
DATOS = RAIZ / "app/datos"
TOLERANCIA = 1e-9  # ≪ 1 céntimo

# Lee la entrada por stdin y escribe el resultado de `calcular` (JSON) por stdout.
GUION_JS = """
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
const [calculo, datos] = process.argv.slice(1);
const { calcular } = await import(pathToFileURL(calculo).href);
const leer = (n) => JSON.parse(readFileSync(`${datos}/${n}`, "utf8"));
const api = Object.fromEntries(["alquiler", "hogares", "netos", "tarifas", "tiempos"].map((n) => [n, leer(`${n}.json`)]));
api.zonas = leer("zonas.geojson");
process.stdout.write(JSON.stringify(calcular(api, JSON.parse(readFileSync(0, "utf8")))));
"""

GETAFE = {
    "hogar": {"perfil": "solo", "edad": 30},
    "sueldos": [{"bruto": 24000, "destino": "28065", "dias": 5, "modo": "tp"}],
}
CUATRO_VIAJES = {
    "hogar": {"perfil": "comparte", "edad": 30},
    "sueldos": [
        {"bruto": 30000, "destino": "2807901", "dias": 3, "modo": "tp", "viajes_dia": 4}
    ],
}

pytestmark = pytest.mark.skipif(
    shutil.which("node") is None or not (DATOS / "tiempos.json").exists(),
    reason="hace falta Node y los datos reales de app/datos/",
)


def _en_js(entrada: dict) -> dict:
    """Resultado de `calcular` de `app/calculo.js` sobre los datos reales."""
    proceso = subprocess.run(
        [
            "node",
            "--input-type=module",
            "-e",
            GUION_JS,
            str(RAIZ / "app/calculo.js"),
            str(DATOS),
        ],
        input=json.dumps(entrada),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        timeout=60,
    )
    assert proceso.returncode == 0, proceso.stderr
    return json.loads(proceso.stdout)


def _en_python(entrada: dict) -> dict:
    """Lo mismo con `mesobra.calculo`, pasado por JSON para compararlo con la salida de Node."""
    return json.loads(json.dumps(calculo.calcular(calculo.leer_api(DATOS), entrada)))


def _igual(js: Any, py: Any, ruta: str) -> None:
    """Mismas claves y valores; los números con tolerancia; nulo solo contra nulo."""
    if isinstance(py, bool) or py is None or isinstance(py, str):
        assert js == py, f"{ruta}: JS {js!r} ≠ Python {py!r}"
    elif isinstance(py, (int, float)):
        assert isinstance(js, (int, float)), f"{ruta}: JS {js!r} ≠ Python {py!r}"
        assert abs(js - py) <= TOLERANCIA, f"{ruta}: JS {js} ≠ Python {py}"
    elif isinstance(py, list):
        assert isinstance(js, list) and len(js) == len(py), f"{ruta}: longitud"
        for i, (a, b) in enumerate(zip(js, py, strict=True)):
            _igual(a, b, f"{ruta}[{i}]")
    else:
        assert isinstance(js, dict) and sorted(js) == sorted(py), f"{ruta}: claves"
        for clave in py:
            _igual(js[clave], py[clave], f"{ruta}.{clave}")


@pytest.mark.parametrize(
    "entrada", [GETAFE, CUATRO_VIAJES], ids=["getafe", "cuatro_viajes"]
)
def test_js_da_las_mismas_cifras_que_python_en_las_199_zonas(entrada: dict) -> None:
    js, py = _en_js(entrada), _en_python(entrada)
    assert len(py["zonas"]) == 199
    _igual(js, py, "salida")


def test_los_casos_fijos_ejercitan_los_nulos_y_los_cuatro_viajes() -> None:
    zonas = _en_python(GETAFE)["zonas"].values()
    assert (
        sum(z["sobra"] is None for z in zonas) == 97
    )  # 41 sin alquiler y sin ruta, 56 solo sin ruta
    assert any(z["sobra"] is not None for z in zonas)
    dos = _en_python(CUATRO_VIAJES)["zonas"]
    cuatro = _en_python(
        CUATRO_VIAJES | {"sueldos": [CUATRO_VIAJES["sueldos"][0] | {"viajes_dia": 2}]}
    )["zonas"]
    assert any(
        dos[z]["transporte"] is not None
        and dos[z]["transporte"] != cuatro[z]["transporte"]
        for z in dos
    ), "el caso de 4 viajes debe cambiar el coste de transporte"


def test_un_nulo_en_un_lado_y_un_cero_en_el_otro_es_un_fallo() -> None:
    with pytest.raises(AssertionError):
        _igual({"sobra": 0}, {"sobra": None}, "x")
    with pytest.raises(AssertionError):
        _igual({"sobra": None}, {"sobra": 0}, "x")
