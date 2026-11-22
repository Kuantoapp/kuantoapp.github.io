import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { calcular, precioHora, tarifa, tramoCesta } from "./calculo.js";

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

// Copia de `api` con la clave de tarifa del par origen-destino; `null` la quita (como _con_clave de test_calculo.py).
function conClave(origen, destino, clave) {
  const a = structuredClone(api);
  const t = a.tarifas;
  t.clave_tarifa[t.origenes.indexOf(origen)][t.destinos.indexOf(destino)] = clave === null ? null : t.claves.indexOf(clave);
  return a;
}

test("la clave de un polo sale de su columna de tarifas.json", () => {
  const polo = { ...CENTRO, destino: "polo:ifema" };
  assert.equal(zona("2807901", entrada({ sueldos: [polo] })).transporte, 16.57);
  const a = conClave("2807901", "polo:ifema", "A-C2|interurbano");
  assert.equal(zona("2807901", entrada({ sueldos: [polo] }), a).transporte, 45.78);
});

test("4 viajes al día en un par sin zona A (B1 a B2) cuentan la A: abono A-B2, 40,20 €", () => {
  const sueldo = { dias: 5, viajes_dia: 4, edad: 30, colectivo: "ordinario", no_laborables: 0 };
  assert.equal(tarifa(api, "28065", "28092", sueldo, "vigente_2026").coste_mes, 40.2);
  assert.ok(tarifa(api, "28065", "28092", { ...sueldo, viajes_dia: 2 }, "vigente_2026").coste_mes < 40.2);
});

test("4 viajes al día dentro de una zona (C2) pagan el interurbano de una zona más el Metro de A: 18,77 €", () => {
  const sueldo = { dias: 2, viajes_dia: 4, edad: 30, colectivo: "ordinario", no_laborables: 0 };
  assert.equal(tarifa(api, "28001", "28001", sueldo, "vigente_2026").coste_mes, 18.77);
});

test("el Abono Joven del hijo no lleva viajes no laborables, también desde una zona lejana", () => {
  const h = { perfil: "solo", edad: 33, hijos: 1, no_laborables: 16 };
  const t = (hogar) => zona("28001", entrada({ hogar, zonas: ["28001"] })).transporte;
  igual(t({ ...h, edades_hijos: [18] }), t(h) + 9.31, "hijo de 18 años");
});

test("un par sin clave falla con error claro", () => {
  assert.throws(() => calcular(conClave("2807901", "2807901", null), entrada()), /sin clave de tarifa/);
});

test("edad y colectivo por sueldo, y Abono Joven de los hijos de 15 a 25 años", () => {
  const cinco = { ...CENTRO, dias: 5 };
  const pareja = { perfil: "pareja", edad: 30 };
  const t = (hogar, sueldos, escenario = {}) => zona("2807901", entrada({ hogar, sueldos, escenario })).transporte;
  igual(t(pareja, [{ ...cinco, edad: 24 }, cinco]), 9.31 + 27.62, "joven y general");
  igual(t(pareja, [{ ...cinco, edad: 24, discapacidad: true }, cinco]), 7.44 + 27.62, "discapacidad");
  igual(t(pareja, [{ ...cinco, edad: 24 }, cinco], { edad: 26 }), 9.31 + 27.62, "el escenario es el valor por defecto");
  const dos = { perfil: "solo", edad: 33, hijos: 2 };
  assert.equal(t(dos, [cinco]), 27.62, "sin edades_hijos no se cuentan");
  igual(t({ ...dos, edades_hijos: [3, 14] }, [cinco]), 27.62, "menores de 15 gratis");
  igual(t({ ...dos, edades_hijos: [14, 15] }, [cinco]), 27.62 + 9.31, "15 años ya paga");
  igual(t({ ...dos, edades_hijos: [15, 25] }, [cinco]), 27.62 + 2 * 9.31, "hasta edad_max_joven");
  igual(t({ ...dos, perfil: "pareja", familia: "fn_general" }, [cinco]), 21.94, "familia numerosa general");
});

test("las entradas de transporte inválidas fallan con error", () => {
  const malas = [
    [{ edades_hijos: [7] }, {}, /edades_hijos/],
    [{ hijos: 1, edades_hijos: [26] }, {}, /edades_hijos/],
    [{ familia: "fn_general" }, {}, /familia numerosa con 0 hijos/],
    [{ familia: "grande" }, {}, /familia = "grande"/],
    [{ no_laborables: 4 }, {}, /no_laborables/],
    [{ no_laborables: false }, {}, /no_laborables/],
    [{}, { discapacidad: 1 }, /discapacidad/],
    [{}, { edad: 15 }, /edad = 15/],
  ];
  for (const [hogar, sueldo, mensaje] of malas) {
    const e = entrada({ hogar: { perfil: "solo", edad: 30, ...hogar }, sueldos: [{ ...CENTRO, ...sueldo }] });
    assert.throws(() => calcular(api, e), (err) => err.constructor === Error && mensaje.test(err.message));
  }
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
  assert.deepEqual(z.viajes, [{ horas: null, coste: null, titulo: null }]);
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
  assert.deepEqual([z.alquiler, z.alquiler_contrato, z.sobra, z.sobra_contrato, z.sobra_banda, z.esfuerzo, z.precio_hora], Array(7).fill(null));
  assert.ok(z.horas > 0);
  assert.equal(r.ref, "2807901");
});

test("el alquiler es el de contrato nuevo y la referencia, el de los contratos en vigor", () => {
  const z = zona("28065");
  igual(z.alquiler, 12.6 * 1.035 * 1.19 * 45, "alquiler");
  igual(z.alquiler / z.alquiler_contrato, 1.19, "factor_brecha");
  igual(z.sobra_contrato - z.sobra, z.alquiler - z.alquiler_contrato, "sobrante");
  assert.ok(z.sobra_contrato > z.sobra);
});

test("sin factor_brecha válido falla, no vale 1", () => {
  for (const brecha of [undefined, null, 0, -1.2, "1.2"]) {
    const a = structuredClone(api);
    a.alquiler.zonas["28065"].factor_brecha = brecha;
    assert.throws(() => calcular(a, entrada()), /factor_brecha/);
  }
});

test("la banda se ensancha con el intervalo de una zona estimada", () => {
  const a = structuredClone(api);
  Object.assign(a.alquiler.zonas["28065"], { origen: "estimado", ic: [9, 15] });
  const [obs, est] = [zona("28065"), zona("28065", entrada(), a)];
  const k = 1.035 * 1.19 * 45;
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

test("el tramo de la cesta cambia justo en cada corte de la EPF, ni un céntimo antes", () => {
  const cortes = [
    [0.01, 0.7], [499.99, 0.7], [500, 0.8], [999.99, 0.8], [1000, 0.85], [1499.99, 0.85], [1500, 0.95],
    [1999.99, 0.95], [2000, 0.9], [2499.99, 0.9], [2500, 0.97], [2999.99, 0.97], [3000, 1.02],
    [4999.99, 1.02], [5000, 1.15], [90000, 1.15],
  ];
  for (const [neto, factor] of cortes) assert.equal(tramoCesta(api.hogares.cesta_tramos, neto).factor, factor, `neto ${neto}`);
});
