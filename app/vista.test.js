import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { calcular } from "./calculo.js";
import {
  CATEGORIAS, PALETA, SIN_DATO, categoria, colorPara, cortesCuantiles, escalaDivergente, escalaSecuencial, fuentes,
  leyenda, licencias, lineasFicha, pintar, resolverDestino, validar,
} from "./vista.js";

const leer = (ruta) => JSON.parse(readFileSync(new URL(`../${ruta}`, import.meta.url), "utf8"));
const NOMBRES = ["alquiler", "hogares", "netos", "tarifas", "tiempos"];
const cargar = (carpeta) => ({ ...Object.fromEntries(NOMBRES.map((n) => [n, leer(`${carpeta}/${n}.json`)])), zonas: leer(`${carpeta}/zonas.geojson`) });
const ejemplo = cargar("tests/fixtures/api");
const real = cargar("app/datos");

const BASE = {
  fuente: "bruto", bruto: "24000", neto: "", pagas: "12", perfil: "solo", adultos: "1", hijos: "0", edad: "30",
  m2: "69", personas: "1", destino: "Getafe", dias: "5", viajes: "2", modo: "tp",
};
const campos = (cambios) => validar({ ...BASE, ...cambios }, real).errores?.map((e) => e.campo);

// --- Escalas y color ---------------------------------------------------------------------------

test("los cortes salen ordenados, sin repetir y sin clases vacías por empates", () => {
  const cortes = cortesCuantiles([3, 1, 2, 4, 5, 6, 7, 8]);
  assert.deepEqual(cortes, [...cortes].sort((a, b) => a - b));
  assert.equal(new Set(cortes).size, cortes.length);
  assert.deepEqual(cortesCuantiles([5, 5, 5, 5]), [5]);
  assert.deepEqual(cortesCuantiles([1, 1, 2, 2, 2, 2]), [1, 2]);
});

test("ninguna clase queda vacía, tampoco cuando el cuantil interpolado caería entre dos valores", () => {
  for (const valores of [[0, 2, 3, 3, 4, 5, 5, 5], [1, 2, 3, 4, 5, 6, 7, 8], [1, 1, 1, 2, 9, 9, 9, 10, 10]]) {
    const clases = escalaSecuencial(valores);
    const cuenta = clases.map((c, i) => valores.filter((v) => v >= c.desde && (i === clases.length - 1 ? v <= c.hasta : v < c.hasta)).length);
    assert.ok(cuenta.every((n) => n > 0), `${valores} -> ${JSON.stringify(clases)} -> ${cuenta}`);
  }
});

test("sin valores, con nulos o con un solo valor no falla", () => {
  assert.deepEqual(cortesCuantiles([]), []);
  assert.deepEqual(cortesCuantiles([null, undefined, NaN]), []);
  assert.deepEqual(escalaSecuencial([null]), []);
  assert.deepEqual(escalaDivergente([null, NaN]), []);
  assert.equal(colorPara(10, []), SIN_DATO);
  assert.equal(colorPara(null, escalaSecuencial([1, 2])), SIN_DATO);
  assert.equal(colorPara(5, escalaSecuencial([5])), PALETA[0]);
  assert.equal(escalaDivergente([-3]).length, 1);
  assert.equal(escalaDivergente([4]).length, 1);
});

test("la escala divergente tiene el 0 como borde: lo negativo a un lado de la paleta y lo demás al otro", () => {
  const valores = [-40, -20, -10, -1, 0, 2, 5, 9, 30];
  const clases = escalaDivergente(valores);
  assert.equal(clases.length, 4);
  assert.deepEqual(clases.map((c) => c.desde), [-40, -10, 0, 5]);
  assert.equal(clases[1].hasta, 0);
  assert.equal(new Set(clases.map((c) => c.color)).size, 4);
  assert.equal(colorPara(-0.5, clases), clases[1].color);
  assert.equal(colorPara(0, clases), clases[2].color);
  assert.equal(colorPara(30, clases), clases[3].color);
});

// --- pintar: categorías, nulos y leyenda --------------------------------------------------------

const SOLO = { hogar: { perfil: "solo", edad: 30 }, sueldos: [{ bruto: 24000, destino: "28065", dias: 5, modo: "tp" }] };

test("una zona sin cifra no se pinta con color de clase ni se escribe como cero, y dice por qué falta", () => {
  // Con la API de ejemplo: solo las tres zonas que tienen tarifa (A y B1); una de ellas, sin ruta, queda sin cifra.
  const ids = ["2807901", "2807913", "28065"];
  const zonas3 = { ...ejemplo.zonas, features: ejemplo.zonas.features.filter((f) => ids.includes(f.properties.zona_id)) };
  const entrada = { hogar: { perfil: "solo", edad: 30 }, sueldos: [{ bruto: 22000, destino: "2807901", dias: 3, modo: "tp" }], zonas: ids };
  const pintadas = pintar(zonas3, calcular(ejemplo, entrada), "sobra").zonas.features.map((f) => f.properties);
  assert.ok(pintadas.every((p) => (p.valor === null) === (p.categoria !== null)));
  assert.ok(pintadas.every((p) => p.valor === null || p.color !== SIN_DATO));
  // Con los datos reales: sin cifra no es cero, y el color es el del motivo.
  const props = pintar(real.zonas, calcular(real, SOLO), "sobra").zonas.features.map((f) => f.properties);
  const sinCifra = props.filter((p) => p.valor === null);
  assert.equal(sinCifra.length, 97);
  assert.ok(sinCifra.every((p) => Object.values(CATEGORIAS).some((c) => c.texto === p.categoria && c.color === p.color)));
  assert.equal(props.filter((p) => p.valor === 0).length, 0);
});

test("Getafe con datos reales: 102 zonas con cifra, 56 solo sin ruta y 41 sin alquiler y sin ruta", () => {
  const resultado = calcular(real, SOLO);
  const { zonas, categorias } = pintar(real.zonas, resultado, "sobra");
  const props = zonas.features.map((f) => f.properties);
  const cuenta = (texto) => props.filter((p) => p.categoria === texto).length;
  assert.equal(props.length, 199);
  assert.equal(props.filter((p) => p.valor !== null).length, 102);
  assert.equal(cuenta(CATEGORIAS.ruta.texto), 56);
  assert.equal(cuenta(CATEGORIAS.alquiler.texto), 0);
  assert.equal(cuenta(CATEGORIAS.ambos.texto), 41);
  assert.deepEqual(categorias.map((c) => c.texto).sort(), [CATEGORIAS.ambos.texto, CATEGORIAS.ruta.texto].sort());
  assert.ok(props.filter((p) => p.valor === null).every((p) => p.color !== SIN_DATO || p.categoria !== null));
  assert.notEqual(CATEGORIAS.alquiler.texto, CATEGORIAS.ruta.texto);
});

test("el precio de la hora distingue la referencia y «mismo tiempo» de la falta de dato", () => {
  const resultado = calcular(real, SOLO);
  const { zonas } = pintar(real.zonas, resultado, "precio_hora");
  const ref = zonas.features.find((f) => f.properties.zona_id === resultado.ref).properties;
  assert.equal(ref.referencia, true);
  assert.equal(ref.categoria, CATEGORIAS.referencia.texto);
  const mismo = zonas.features.filter((f) => f.properties.categoria === CATEGORIAS["mismo tiempo"].texto);
  assert.ok(mismo.length >= 1 || resultado.zonas[resultado.ref].horas !== null);
  assert.ok(zonas.features.some((f) => typeof f.properties.valor === "number"));
});

test("las horas se pintan aunque falte el alquiler, y sin ruta es solo «sin ruta»", () => {
  assert.equal(categoria({ horas: 10, alquiler: null }, "horas"), null);
  assert.equal(categoria({ horas: null, alquiler: null }, "horas"), "ruta");
  assert.equal(categoria({ sobra: null, horas: null, alquiler: null }, "sobra"), "ambos");
  assert.equal(categoria({ sobra: null, horas: null, alquiler: 5 }, "sobra"), "ruta");
  assert.equal(categoria({ sobra: null, horas: 4, alquiler: null }, "sobra"), "alquiler");
});

test("pintar rechaza formatos y métricas inesperados", () => {
  assert.throws(() => pintar({}, { zonas: {} }, "sobra"), /Formato inesperado/);
  assert.throws(() => pintar(real.zonas, {}, "sobra"), /Formato inesperado/);
  assert.throws(() => pintar(real.zonas, { zonas: {} }, "nada"), /Métrica desconocida/);
  assert.throws(() => pintar(real.zonas, { zonas: {} }, "sobra"), /no tiene resultado/);
});

test("la leyenda tiene una entrada por clase más una por cada motivo de «sin cifra»", () => {
  const resultado = calcular(real, SOLO);
  const { clases, categorias } = pintar(real.zonas, resultado, "sobra");
  const entradas = leyenda(clases, categorias, "sobra");
  assert.equal(entradas.length, clases.length + categorias.length);
  assert.match(entradas[0].texto, /^-?[\d.]+ – -?[\d.]+$/);
  assert.equal(entradas.at(-1).texto, categorias.at(-1).texto);
});

test("la ficha dice el valor con su unidad, el año del alquiler y que la cesta es estimada", () => {
  const lineas = lineasFicha("Getafe", { sobra: 123.4, cesta: 356.4, origen: "observado" }, 2024, "sobra");
  assert.deepEqual(lineas, ["Getafe", "123 €/mes (estimado)", "Alquiler de 2024", "Cesta básica: 356 €/mes (estimado, gasto medio de 2025)"]);
  assert.equal(lineasFicha("X", { horas: null, alquiler: 1 }, null, "horas")[1], CATEGORIAS.ruta.texto);
  assert.match(lineasFicha("X", { sobra: 1, origen: "estimado" }, 2023, "sobra")[2], /\(estimado\)/);
});

// --- Validación de entradas ---------------------------------------------------------------------

test("una entrada correcta devuelve la entrada del cálculo y ningún error", () => {
  const res = validar(BASE, real);
  assert.equal(res.errores, undefined);
  assert.deepEqual(res.entrada.sueldos, [{ bruto: 24000, destino: "28065", dias: 5, modo: "tp", viajes_dia: 2 }]);
  assert.deepEqual(res.entrada.hogar, { perfil: "solo", adultos: 1, hijos: 0, edad: 30, personas_comparten: 1, m2: 69 });
  assert.doesNotThrow(() => calcular(real, res.entrada));
});

test("sueldo negativo, texto, vacío o fuera de la tabla de netos devuelven un aviso y no un cálculo", () => {
  for (const bruto of ["-5000", "abc", "", "1e5", "Infinity", "11999", "120001", "NaN"]) {
    const res = validar({ ...BASE, bruto }, real);
    assert.equal(res.entrada, undefined, bruto);
    assert.deepEqual(res.errores.map((e) => e.campo), ["bruto"], bruto);
  }
  assert.match(validar({ ...BASE, bruto: "5000" }, real).errores[0].mensaje, /fuera de 12\.000–120\.000 € brutos al año, introduce tu neto mensual/);
});

test("0 o 6 días, o días que no son un entero, devuelven un aviso", () => {
  for (const dias of ["0", "6", "2,5", "", "tres", "-1"]) assert.deepEqual(campos({ dias }), ["dias"], dias);
  for (const dias of ["1", "5"]) assert.equal(campos({ dias }), undefined);
});

test("el neto es el mensual medio tal cual: las pagas no lo cambian (con 14 la paga extra ya cotiza prorrateada)", () => {
  for (const pagas of ["12", "14"]) {
    const res = validar({ ...BASE, fuente: "neto", neto: "1800", pagas }, real);
    assert.equal(res.errores, undefined);
    assert.equal(res.entrada.sueldos[0].neto_mes, 1800);
    assert.equal(res.entrada.sueldos[0].bruto, undefined);
  }
  for (const neto of ["0", "-3", "x", "", "10001"]) assert.deepEqual(campos({ fuente: "neto", neto }), ["neto"], neto);
  assert.deepEqual(campos({ pagas: "13" }), ["pagas"]);
});

test("el punto de miles a la española no se lee como decimal: «1.800» son 1800 y «1.800,50», 1800,5", () => {
  const neto = (t) => validar({ ...BASE, fuente: "neto", neto: t }, real).entrada?.sueldos[0].neto_mes;
  assert.equal(neto("1.800"), 1800);
  assert.equal(neto("1.800,50"), 1800.5);
  assert.equal(neto("1800,5"), 1800.5);
  assert.equal(neto("1.5"), 1.5); // no es un grupo de tres cifras: es un decimal
  assert.equal(validar({ ...BASE, bruto: "24.000" }, real).entrada.sueldos[0].bruto, 24000);
  for (const malo of ["1.2.3", "1.800.", ".800", "1.800,", "1,800.50"]) assert.deepEqual(campos({ bruto: malo }), ["bruto"], malo);
  for (const malo of ["1.800.", ".800", "10.000,01"]) assert.deepEqual(campos({ fuente: "neto", neto: malo }), ["neto"], malo);
  assert.equal(neto("10.000"), 10000);
});

test("los límites exactos se aceptan y un paso fuera se rechaza", () => {
  const ok = (cambios) => assert.equal(campos(cambios), undefined, JSON.stringify(cambios));
  const mal = (cambios, campo) => assert.deepEqual(campos(cambios), [campo], JSON.stringify(cambios));
  for (const edad of ["16", "64"]) ok({ edad });
  for (const bruto of ["12000", "120000"]) ok({ bruto });
  mal({ bruto: "11999,99" }, "bruto");
  mal({ bruto: "120000,01" }, "bruto");
  ok({ fuente: "neto", neto: "10000" });
  mal({ fuente: "neto", neto: "10000,01" }, "neto");
  for (const m2 of ["10", "300"]) ok({ m2 });
  mal({ m2: "9,99" }, "m2");
  mal({ m2: "300,01" }, "m2");
  for (const personas of ["1", "20"]) ok({ personas });
  mal({ personas: "21" }, "personas");
});

test("hijos solo de 0 a 2, edad de 16 a 64, y el resto de campos con su rango", () => {
  assert.equal(validar({ ...BASE, hijos: "3" }, real).errores[0].mensaje, "Hasta 2 hijos");
  assert.deepEqual(campos({ edad: "15" }), ["edad"]);
  assert.deepEqual(campos({ edad: "65" }), ["edad"]);
  assert.deepEqual(campos({ adultos: "3" }), ["adultos"]);
  assert.deepEqual(campos({ m2: "0" }), ["m2"]);
  assert.deepEqual(campos({ m2: "301" }), ["m2"]);
  assert.deepEqual(campos({ personas: "0" }), ["personas"]);
  assert.deepEqual(campos({ perfil: "castillo" }), ["perfil"]);
  assert.deepEqual(campos({ perfil: "__proto__" }), ["perfil"]);
  assert.deepEqual(campos({ viajes: "3" }), ["viajes"]);
  assert.deepEqual(campos({ modo: "coche" }), ["modo"]);
  assert.equal(campos({ viajes: "4" }), undefined);
});

test("el destino se resuelve por nombre o id y se rechaza lo que no está en la lista", () => {
  const { destinos } = real.tiempos;
  assert.equal(resolverDestino(" getafe ", destinos), "28065");
  assert.equal(resolverDestino("28065", destinos), "28065");
  assert.equal(resolverDestino("Getafe; DROP TABLE", destinos), null);
  assert.equal(resolverDestino("<img src=x onerror=alert(1)>", destinos), null);
  assert.equal(resolverDestino("", destinos), null);
  assert.equal(resolverDestino(undefined, destinos), null);
  assert.deepEqual(campos({ destino: "Mordor" }), ["destino"]);
});

test("varios errores se devuelven juntos, cada uno con su campo", () => {
  assert.deepEqual(campos({ bruto: "x", dias: "9", hijos: "7" }), ["bruto", "hijos", "dias"]);
});

// --- Textos de fuentes ---------------------------------------------------------------------------

test("la fuente sale de meta.fuentes sin repetir nombres", () => {
  const meta = { fuentes: [{ nombre: "INE" }, { nombre: "INE" }, { nombre: "CRTM" }] };
  assert.equal(fuentes(meta, meta), "fuente: INE, CRTM");
});

test("las licencias salen de meta.fuentes sin repetir", () => {
  const meta = { fuentes: [{ licencia: "CC BY 4.0" }, { licencia: "ODbL 1.0" }] };
  assert.equal(licencias(meta, meta), "CC BY 4.0; ODbL 1.0");
});
