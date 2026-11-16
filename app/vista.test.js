import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { PALETA, SIN_DATO, colorPara, colorear, cortesCuantiles, fuentes, leyenda, licencias } from "./vista.js";

const leer = (nombre) => JSON.parse(readFileSync(new URL(`../tests/fixtures/api/${nombre}`, import.meta.url), "utf8"));
const zonas = leer("zonas.geojson");
const alquiler = leer("alquiler.json");

test("cada zona de ejemplo con dato recibe un color de la paleta y la que no tiene, gris", () => {
  const { zonas: pintadas } = colorear(zonas, alquiler);
  const colores = Object.fromEntries(pintadas.features.map((f) => [f.properties.zona_id, f.properties.color]));
  assert.equal(pintadas.features.length, 5);
  assert.equal(colores["28001"], SIN_DATO);
  for (const id of ["2807901", "2807913", "28065", "28092"]) assert.ok(PALETA.includes(colores[id]), id);
});

test("el valor más alto y el más bajo caen en las clases extremas", () => {
  const { zonas: pintadas } = colorear(zonas, alquiler);
  const color = (id) => pintadas.features.find((f) => f.properties.zona_id === id).properties.color;
  assert.equal(color("2807901"), PALETA.at(-1)); // 19,6 €/m²
  assert.equal(color("28092"), PALETA[0]); // 11,8 €/m²
});

test("una zona estimada se marca y una zona ausente de alquiler cuenta como sin dato", () => {
  const sinEntrada = { ...alquiler, zonas: { "28092": alquiler.zonas["28092"] } };
  const { zonas: pintadas } = colorear(zonas, sinEntrada);
  const porId = Object.fromEntries(pintadas.features.map((f) => [f.properties.zona_id, f.properties]));
  assert.equal(porId["28092"].estimado, true);
  assert.equal(porId["2807901"].color, SIN_DATO);
  assert.equal(porId["2807901"].p50, null);
});

test("los cortes salen ordenados, sin repetir y sin clases vacías por empates", () => {
  const cortes = cortesCuantiles([3, 1, 2, 4, 5, 6, 7, 8]);
  assert.deepEqual(cortes, [...cortes].sort((a, b) => a - b));
  assert.equal(new Set(cortes).size, cortes.length);
  assert.deepEqual(cortesCuantiles([5, 5, 5, 5]), [5]);
  assert.deepEqual(cortesCuantiles([1, 1, 2, 2, 2, 2]), [1, 2]);
});

test("ninguna clase queda vacía, tampoco cuando el cuantil interpolado caería entre dos valores", () => {
  for (const valores of [[0, 2, 3, 3, 4, 5, 5, 5], [1, 2, 3, 4, 5, 6, 7, 8], [1, 1, 1, 2, 9, 9, 9, 10, 10]]) {
    const cortes = cortesCuantiles(valores);
    const cuenta = Array(cortes.length - 1).fill(0);
    for (const v of valores) cuenta[Math.min(cortes.slice(1, -1).filter((b) => b <= v).length, cuenta.length - 1)]++;
    assert.ok(cuenta.every((n) => n > 0), `${valores} -> ${cortes} -> ${cuenta}`);
  }
});

test("sin valores, con nulos o con un solo valor no falla", () => {
  assert.deepEqual(cortesCuantiles([]), []);
  assert.deepEqual(cortesCuantiles([null, undefined, NaN]), []);
  assert.equal(colorPara(10, []), SIN_DATO);
  assert.equal(colorPara(null, [1, 2]), SIN_DATO);
  assert.equal(colorPara(5, [5]), PALETA[0]);
});

test("la leyenda tiene una entrada por clase más «Sin dato»", () => {
  const { cortes } = colorear(zonas, alquiler);
  const entradas = leyenda(cortes);
  assert.equal(entradas.length, cortes.length);
  assert.deepEqual(entradas.at(-1), { color: SIN_DATO, texto: "Sin dato" });
  assert.match(entradas[0].texto, /^11,8 – /);
});

test("la fuente sale de meta.fuentes sin repetir nombres", () => {
  assert.equal(fuentes(zonas.meta, alquiler.meta), "fuente: INE, Comunidad de Madrid, datos abiertos");
});

test("un formato inesperado falla en voz alta", () => {
  assert.throws(() => colorear({}, alquiler), /Formato inesperado/);
  assert.throws(() => colorear(zonas, {}), /Formato inesperado/);
});

test("las licencias salen de meta.fuentes sin repetir", () => {
  const meta = { fuentes: [{ licencia: "CC BY 4.0" }, { licencia: "ODbL 1.0" }] };
  assert.equal(licencias(meta, meta), "CC BY 4.0; ODbL 1.0");
});
