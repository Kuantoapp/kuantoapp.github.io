import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { calcular, precioHora } from "./calculo.js";

const leer = (ruta) => JSON.parse(readFileSync(new URL(`../tests/${ruta}`, import.meta.url), "utf8"));
const api = Object.fromEntries(
  ["alquiler", "hogares", "netos", "tarifas", "tiempos"].map((n) => [n, leer(`fixtures/api/${n}.json`)]),
);
api.zonas = leer("fixtures/api/zonas.geojson");
const { casos } = leer("fixtures/casos_referencia.json");

// Mismas claves y valores; los números, con tolerancia (1e-9 ≪ 1 céntimo); null solo contra null.
function igual(real, esperado, ruta) {
  if (typeof esperado === "number") {
    assert.equal(typeof real, "number", `${ruta}: esperaba número, salió ${real}`);
    assert.ok(Math.abs(real - esperado) <= 1e-9, `${ruta}: ${real} ≠ ${esperado}`);
  } else if (esperado !== null && typeof esperado === "object") {
    assert.ok(real !== null && typeof real === "object", `${ruta}: esperaba objeto, salió ${real}`);
    assert.deepEqual(Object.keys(real).sort(), Object.keys(esperado).sort(), `${ruta}: claves`);
    for (const k of Object.keys(esperado)) igual(real[k], esperado[k], `${ruta}.${k}`);
  } else assert.strictEqual(real, esperado, ruta);
}

for (const caso of casos) {
  test(caso.nombre, () => {
    if ("error" in caso) assert.throws(() => calcular(api, caso.entrada));
    else igual(calcular(api, structuredClone(caso.entrada)), caso.salida, "salida");
  });
}

test("hay 12 o más casos y los de error fallan, no devuelven vacío", () => {
  assert.ok(casos.length >= 12);
  assert.equal(casos.filter((c) => "error" in c).length, 3);
});

test("sin dato o sin ruta sale null, nunca cero", () => {
  assert.deepEqual(precioHora(null, 10, 5, 2), [null, null]);
  assert.deepEqual(precioHora(1, undefined, 5, 2), [null, null]);
  assert.deepEqual(precioHora(0, 10, 0, 2), [0, null]);
  const salida = casos.flatMap((c) => Object.values(c.salida?.zonas ?? {}));
  assert.ok(salida.some((z) => z.sobra === null), "el fixture debe cubrir una zona sin sobrante");
});

test("una entrada rota falla con error, no con un resultado", () => {
  const base = casos[0].entrada;
  for (const mala of [null, {}, { ...base, sueldos: [] }, { ...base, hogar: { perfil: "constructor" } }]) {
    assert.throws(() => calcular(api, mala));
  }
});

test("calculo.js es puro: ni imports ni DOM", () => {
  const fuente = readFileSync(new URL("./calculo.js", import.meta.url), "utf8");
  assert.doesNotMatch(fuente, /^\s*import\b|\bdocument\b|\bwindow\b/m);
});
