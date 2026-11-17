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
    // Error propio (no un TypeError por un fallo distinto del esperado).
    if ("error" in caso) assert.throws(() => calcular(api, caso.entrada), (e) => e.constructor === Error);
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

// Casos fuera del fixture, espejo de tests/test_calculo.py (sin ruta, banda con ic, borde del Abono Joven).
const CENTRO = { bruto: 22000, destino: "2807901", dias: 3, modo: "tp" };
const entrada = (cambios = {}) => ({ hogar: { perfil: "solo", edad: 30 }, sueldos: [CENTRO], zonas: ["2807901", "2807913", "28065"], ...cambios });
const zona = (id, e = entrada(), a = api) => calcular(a, e).zonas[id];

test("sin ruta en transporte público no hay horas, coste, sobrante ni precio, y el alquiler sigue", () => {
  const a = structuredClone(api);
  a.tiempos.tp[1][0] = null;
  const z = zona("2807913", entrada(), a);
  assert.deepEqual([z.horas, z.transporte, z.sobra, z.sobra_banda, z.precio_hora], [null, null, null, null, null]);
  assert.notEqual(z.alquiler, null);
  assert.notEqual(calcular(a, entrada()).ref, "2807913");
});

test("sin km en coche el coste es null pero las horas se mantienen", () => {
  const a = structuredClone(api);
  a.tiempos.km_coche[1][0] = null;
  const e = entrada({ sueldos: [{ ...CENTRO, modo: "coche" }] });
  const z = zona("2807913", e, a);
  assert.deepEqual([z.transporte, z.sobra], [null, null]);
  assert.ok(z.horas > 0);
});

test("una zona sin dato de alquiler da null en alquiler, sobra, banda, esfuerzo y precio, pero con horas", () => {
  const a = structuredClone(api);
  a.alquiler.zonas["2807913"] = api.alquiler.zonas["28001"];
  const r = calcular(a, entrada());
  const z = r.zonas["2807913"];
  assert.deepEqual([z.alquiler, z.sobra, z.sobra_banda, z.esfuerzo, z.precio_hora], [null, null, null, null, null]);
  assert.ok(z.horas > 0);
  assert.equal(r.ref, "2807901");
});

test("la banda se ensancha con el intervalo de una zona estimada", () => {
  const a = structuredClone(api);
  Object.assign(a.alquiler.zonas["28065"], { origen: "estimado", ic: [9, 15] });
  const [obs, est] = [zona("28065"), zona("28065", entrada(), a)];
  const k = 1.035 * 45;
  const fijo = obs.neto - obs.transporte - obs.cesta;
  igual(obs.sobra_banda, [fijo - 14.3 * k, fijo - 11.0 * k], "observada");
  igual(est.sobra_banda, [fijo - 15.0 * k, fijo - 9.0 * k], "estimada");
});

test("el Abono Joven llega hasta edad_max_joven inclusive", () => {
  const max = api.tarifas.edad_max_joven;
  const coste = (edad) => zona("2807913", entrada({ hogar: { perfil: "solo", edad } })).transporte;
  assert.ok(coste(max) < coste(max + 1), "con 25 años aún paga tarifa joven");
  assert.equal(coste(max), zona("2807913", entrada({ hogar: { perfil: "solo", edad: 30 }, escenario: { edad: max } })).transporte);
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
