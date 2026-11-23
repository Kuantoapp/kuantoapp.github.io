import assert from "node:assert/strict";
import { test } from "node:test";
import { seccionActiva } from "./indice.js";

// Bordes superiores de tres secciones respecto a la ventana; el índice acaba en la línea 118.
test("antes de la primera sección no hay ninguna activa", () => {
  assert.equal(seccionActiva([400, 1200, 2000], 118, false), -1);
});

test("la activa es la última que ya pasó bajo el índice", () => {
  assert.equal(seccionActiva([118, 900, 1700], 118, false), 0);
  assert.equal(seccionActiva([-900, 50, 800], 118, false), 1);
});

test("al final de la página se marca la última aunque no llegue a la línea", () => {
  assert.equal(seccionActiva([-2000, -600, 400], 118, true), 2);
});
