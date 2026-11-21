import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { calcular } from "./calculo.js";
import {
  CATEGORIAS, ESCENARIO_NEUTRO, METRICAS, PALETA, SIN_DATO, avisoPrueba, avisos, categoria, colorPara, contextoFicha, contorno, cortesCuantiles, entradaEscenario, hayEscenario,
  erroresEscenario, escalaDivergente, escalaSecuencial, estadoAEnlace, estadoDeEnlace, fuentes, imprecisas, leyenda, licencias, lineaDiferencia, lineaTooltip,
  lineasFicha, mejores, modosDisponibles, avisosEntrada, pintar, resolverDestino, tituloEscenario, validar,
} from "./vista.js";

const leer = (ruta) => JSON.parse(readFileSync(new URL(`../${ruta}`, import.meta.url), "utf8"));
const NOMBRES = ["alquiler", "hogares", "netos", "tarifas", "tiempos"];
const cargar = (carpeta) => ({ ...Object.fromEntries(NOMBRES.map((n) => [n, leer(`${carpeta}/${n}.json`)])), zonas: leer(`${carpeta}/zonas.geojson`) });
const ejemplo = cargar("tests/fixtures/api");
const EDAD = ejemplo.tarifas.edad_max_joven + 1;
const real = cargar("app/datos");

const BASE = {
  fuente: "bruto", bruto: "24000", neto: "", pagas: "12", perfil: "solo", adultos: "1", hijos: "0", edad: "30",
  m2: "69", personas: "1", destino: "Getafe", dias: "5", viajes: "2", modo: "tp",
  fuente2: "bruto", bruto2: "24000", neto2: "", pagas2: "12", destino2: "Getafe", dias2: "5", viajes2: "2", modo2: "tp",
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

// --- Ficha de zona, diez mejores y avisos --------------------------------------------------------

const { casos } = leer("tests/fixtures/casos_referencia.json");
const fichaDe = (caso, id, metrica = "precio_hora") => lineasFicha("Zona", caso.salida.zonas[id], metrica, contextoFicha(ejemplo, caso.entrada, caso.salida, id));
// Una cifra calculada: un número seguido de su unidad (los motivos como «120 min» o «5 h/mes de diferencia» no lo son).
const CIFRA = /\d+(,\d+)? ?(€|h al|%|m²)/;

test("con la subida del alquiler activa, la ficha lo dice como simulación y no como contratos observados", () => {
  const caso = casos.find((c) => !("error" in c));
  const z = caso.salida.zonas["28065"];
  const ctx = { ...contextoFicha(ejemplo, caso.entrada, caso.salida, "28065"), subida: 10 };
  const linea = lineasFicha("Zona", z, "sobra", ctx).find((l) => l.startsWith("Alquiler"));
  assert.match(linea, /subida del 10 %.*simulación, estimado/);
  assert.doesNotMatch(linea, /contratos de \d{4}, tómalo como un suelo/);
});

test("con la subida, una zona con alquiler estimado no dice «contratos»", () => {
  const caso = casos.find((c) => !("error" in c));
  const z = { ...caso.salida.zonas["28065"], origen: "estimado" };
  const ctx = { ...contextoFicha(ejemplo, caso.entrada, caso.salida, "28065"), subida: 10 };
  const linea = lineasFicha("Zona", z, "sobra", ctx).find((l) => l.startsWith("Alquiler"));
  assert.match(linea, /dato estimado de \d{4}.* más la subida; simulación, estimado/);
  assert.doesNotMatch(linea, /contratos/);
});

test("con factor_ipc distinto de 1 la ficha no dice «contratos de {año}» a secas y lleva estimado; con 1 sí", () => {
  const caso = casos.find((c) => !("error" in c));
  const alquiler = (id) => fichaDe(caso, id, "sobra").find((l) => l.startsWith("Alquiler"));
  assert.match(alquiler("28065"), /actualizados con el IPC de alquiler hasta octubre de 2026.*estimado\)$/);
  assert.doesNotMatch(alquiler("28065"), /contratos de \d{4}, tómalo/);
  const sin = { ...ejemplo, alquiler: { ...ejemplo.alquiler, zonas: { ...ejemplo.alquiler.zonas, 28065: { ...ejemplo.alquiler.zonas["28065"], factor_ipc: 1 } } } };
  const ctx = contextoFicha(sin, caso.entrada, caso.salida, "28065");
  assert.match(lineasFicha("Zona", caso.salida.zonas["28065"], "sobra", ctx).find((l) => l.startsWith("Alquiler")), /\(contratos de 2024, tómalo como un suelo\)$/);
});

const conTestigos = (n) => ({ ...ejemplo, alquiler: { ...ejemplo.alquiler, zonas: { ...ejemplo.alquiler.zonas, 28065: { ...ejemplo.alquiler.zonas["28065"], testigos: n } } } });

test("la ficha avisa de pocos alquileres declarados con menos de min_testigos y no con 50 ni en una zona estimada", () => {
  const lineas = (api, id, caso = casos.find((c) => !("error" in c))) => lineasFicha("Zona", caso.salida.zonas[id], "sobra", contextoFicha(api, caso.entrada, caso.salida, id));
  assert.ok(lineas(conTestigos(49), "28065").some((l) => l.startsWith("Impreciso: pocos alquileres declarados (49 en 2024, menos de 50)")));
  assert.ok(!lineas(conTestigos(50), "28065").some((l) => l.startsWith("Impreciso")));
  assert.ok(!lineas(conTestigos(49), "28092", casos.find((c) => c.nombre.startsWith("coche"))).some((l) => l.startsWith("Impreciso")), "estimada: testigos null");
});

test("imprecisas con datos reales: 33 zonas, entre ellas Titulcia", () => {
  const pocas = imprecisas(real.alquiler);
  assert.equal(pocas.size, 33);
  assert.ok(pocas.has("28147"));
});

test("pintar marca impreciso con 49 testigos y no con 50, y nunca en horas", () => {
  const resultado = { zonas: Object.fromEntries(ejemplo.zonas.features.map((f) => [f.properties.zona_id, { sobra: 1, horas: 1 }])) };
  const marca = (n, metrica = "sobra") => {
    const api = conTestigos(n);
    return pintar(api.zonas, resultado, metrica, imprecisas(api.alquiler)).zonas.features.filter((f) => f.properties.impreciso).map((f) => f.properties.zona_id);
  };
  assert.deepEqual(marca(49), ["28065"]);
  assert.deepEqual(marca(50), []);
  assert.deepEqual(marca(49, "horas"), []);
});

test("mejores marca las imprecisas en las métricas del alquiler y no en las horas", () => {
  const resultado = { ref: null, zonas: { a: { sobra: 1, horas: 2 }, b: { sobra: 0, horas: 1 } } };
  const nombres = { a: "A", b: "B" };
  const pocas = new Set(["a"]);
  assert.equal(mejores(resultado, "sobra", nombres, pocas)[0].texto, "A: 1 €/mes (impreciso: pocos alquileres declarados)");
  assert.equal(mejores(resultado, "sobra", nombres, pocas)[1].texto, "B: 0 €/mes");
  assert.equal(mejores(resultado, "horas", nombres, pocas)[1].texto, "A: 2,0 h/mes");
});

test("los avisos cuentan las zonas con pocos alquileres declarados solo si las hay", () => {
  assert.ok(avisos(conTestigos(49).alquiler).includes("1 zona con pocos alquileres declarados (menos de 50): borde punteado; su ficha lo avisa."));
  assert.ok(!avisos(ejemplo.alquiler).some((l) => l.includes("pocos alquileres declarados")));
});

test("el aviso y la ficha nombran el mismo mes del IPC", () => {
  const caso = casos.find((c) => !("error" in c));
  const mes = /hasta (\w+ de \d{4})/;
  const deAviso = avisos(ejemplo.alquiler)[0].match(mes)[1];
  const deFicha = fichaDe(caso, "28065", "sobra").find((l) => l.startsWith("Alquiler")).match(mes)[1];
  assert.equal(deAviso, deFicha);
  assert.match(avisos(ejemplo.alquiler)[0], /\(estimado\)/);
});

test("con datos reales (con IPC) el aviso y la ficha dicen lo mismo", () => {
  const caso = casos.find((c) => !("error" in c));
  const api = { ...ejemplo, alquiler: real.alquiler }; // la zona 28065 del fixture existe también en los datos reales
  const ficha = lineasFicha("Zona", caso.salida.zonas["28065"], "sobra", contextoFicha(api, caso.entrada, caso.salida, "28065")).find((l) => l.startsWith("Alquiler"));
  const mes = /hasta (\w+ de \d{4})/;
  assert.equal(ficha.match(mes)[1], avisos(real.alquiler)[0].match(mes)[1]);
});

test("con IPC, la subida y la zona estimada concuerdan en el texto", () => {
  const caso = casos.find((c) => !("error" in c));
  const z = caso.salida.zonas["28065"];
  const base = contextoFicha(ejemplo, caso.entrada, caso.salida, "28065");
  const linea = (zona, ctx) => lineasFicha("Zona", zona, "sobra", ctx).find((l) => l.startsWith("Alquiler"));
  assert.match(linea(z, { ...base, subida: 10 }), /contratos de 2024 actualizados con el IPC de alquiler hasta octubre de 2026 más la subida/);
  assert.match(linea({ ...z, origen: "estimado" }, { ...base, subida: 10 }), /dato estimado de 2024 actualizado con el IPC/);
  assert.match(linea({ ...z, origen: "estimado" }, { ...base, ic: null }), /año 2024, actualizado con el IPC de alquiler hasta octubre de 2026; sin intervalo/);
});

test("la ficha de cada caso de referencia trae exactamente sus cifras", () => {
  const f = (d) => new Intl.NumberFormat("es-ES", { minimumFractionDigits: d, maximumFractionDigits: d });
  for (const caso of casos.filter((c) => !("error" in c))) {
    for (const [id, z] of Object.entries(caso.salida.zonas)) {
      const texto = fichaDe(caso, id).join("\n");
      if (z.sobra === null) {
        assert.doesNotMatch(texto, CIFRA, `${caso.nombre} ${id}`);
        continue;
      }
      const esperadas = [
        f(0).format(z.neto), f(0).format(z.alquiler_p25), f(0).format(z.alquiler_p75), f(2).format(z.transporte),
        f(0).format(z.cesta), f(1).format(z.horas), `${f(0).format(z.esfuerzo * 100)} %`,
        ...z.sobra_banda.map((v) => `${f(0).format(Math.abs(v))} €`),
      ];
      if (z.precio_hora !== null) esperadas.push(`${f(1).format(Math.abs(z.precio_hora))} €`);
      for (const e of esperadas) assert.ok(texto.includes(e), `${caso.nombre} ${id}: falta «${e}» en\n${texto}`);
    }
  }
});

test("ficha completa de una zona: banda del sobrante, título, precio de la hora frente al salario y m²", () => {
  assert.deepEqual(fichaDe(casos[0], "28065"), [
    "Zona",
    "24,4 € por hora extra (estimado)",
    "Te sobran entre 440 € y 594 € al mes (estimado)",
    "Neto del hogar: 1523 € al mes (estimado)",
    "Alquiler: entre 512 y 666 € al mes (contratos de 2024 actualizados con el IPC de alquiler hasta octubre de 2026, tómalo como un suelo; estimado)",
    "Transporte: 16,57 € al mes (10 viajes) (estimado)",
    "Cesta básica: 400 €/mes (estimado: gasto medio de 2025 con el IPC hasta octubre de 2026; incluye internet y móvil)",
    "Viaje al trabajo: 15,5 h al mes, ida y vuelta (estimado)",
    "Vivir aquí te paga 24,4 € por cada hora de viaje de más (estimado)",
    "Tu trabajo te paga 10,1 € netos la hora (estimado, jornada de 40 h a la semana)",
    "El alquiler se lleva el 39 % del neto, más del 30 % que esta herramienta toma como referencia (estimado)",
    "Con el 30 % del neto alcanza para un piso de 35 m² (estimado)",
  ]);
  // 10,1 € la hora = 1.523,03 € ÷ (40 h × 3,7833 semanas); 35 m² = 30 % × 1.523,03 € × 45 m² (perfil solo) ÷ 586,84 €.
  assert.ok(Math.abs(contextoFicha(ejemplo, casos[0].entrada, casos[0].salida, "28065").salarioHora - 10.064) < 0.001);
  assert.ok(fichaDe(casos[1], "28065").includes("Transporte: 9,31 € al mes (Abono Joven) (estimado)"));
});

test("el título de la ficha es el de la celda que paga el cálculo: borde de 25/26 años y 4 viajes al día", () => {
  const conEdad = (edad, viajes_dia) => {
    const entrada = structuredClone(casos[0].entrada);
    entrada.hogar.edad = edad;
    if (viajes_dia) entrada.sueldos[0].viajes_dia = viajes_dia;
    const resultado = calcular(ejemplo, structuredClone(entrada));
    return lineasFicha("Zona", resultado.zonas["28065"], "sobra", contextoFicha(ejemplo, entrada, resultado, "28065"));
  };
  assert.ok(conEdad(25).includes("Transporte: 9,31 € al mes (Abono Joven) (estimado)"));
  assert.ok(conEdad(26).includes("Transporte: 16,57 € al mes (10 viajes) (estimado)"));
  const tabla = Object.entries(ejemplo.tarifas.tarifas_ruta.vigente_2026.ordinario.general).filter(([k]) => k.includes("+"));
  const celda = tabla.map(([, c]) => c["0"][2]).find((c) => conEdad(30, 4).some((l) => l === `Transporte: ${c.coste_mes.toFixed(2).replace(".", ",")} € al mes (${c.titulo}) (estimado)`));
  assert.ok(celda, "con 4 viajes al día el título y el coste salen de la misma celda");
});

test("dos sueldos con el mismo título no lo repiten", () => {
  const caso = casos.find((c) => c.nombre.startsWith("pareja con un hijo"));
  assert.ok(fichaDe(caso, "28065").includes("Transporte: 27,62 € al mes (10 viajes) (estimado)"));
});

test("el borde del 30 % y el de la banda se deciden con lo que se muestra redondeado", () => {
  const caso = casos[0];
  const ctx = contextoFicha(ejemplo, caso.entrada, caso.salida, "28065");
  const con = (cambios) => lineasFicha("Zona", { ...caso.salida.zonas["28065"], ...cambios }, "sobra", ctx);
  assert.ok(con({ esfuerzo: 0.3004 }).includes("El alquiler se lleva el 30 % del neto (estimado)"));
  assert.ok(con({ esfuerzo: 0.306 }).includes("El alquiler se lleva el 31 % del neto, más del 30 % que esta herramienta toma como referencia (estimado)"));
  assert.ok(con({ sobra_banda: [-0.3, 120] }).includes("Te sobran entre 0 € y 120 € al mes (estimado)"));
  assert.ok(con({ sobra_banda: [-80, 0.2] }).includes("Te faltan entre 0 € y 80 € al mes (estimado)"));
  assert.ok(con({ sobra_banda: [-80, 120] }).includes("Entre que te falten 80 € y te sobren 120 € al mes (estimado)"));
});

test("una referencia sin sobrante u horas falla con el mensaje que app.js reconoce", () => {
  const entrada = { ...structuredClone(casos.find((c) => c.nombre.startsWith("coche")).entrada), ref: "28001" };
  assert.throws(() => calcular(ejemplo, entrada), /^Error: zona de referencia /);
});

test("con una referencia elegida, la ficha lee bien el signo del precio de la hora", () => {
  const caso = casos.find((c) => c.entrada.ref === "28065");
  assert.ok(fichaDe(caso, "2807901").includes("Vivir aquí te cuesta 10,8 € por cada hora de viaje que te ahorras (estimado)"));
  const gana = { ...caso.salida.zonas["2807901"], precio_hora: -3, sobra: 900 };
  const ctx = contextoFicha(ejemplo, caso.entrada, caso.salida, "2807901");
  assert.ok(lineasFicha("Zona", gana, "sobra", ctx).includes("Aquí te sobra más y viajas menos que en la zona de referencia (estimado)"));
  const pierde = { ...caso.salida.zonas["2807913"], horas: 30, precio_hora: -2 };
  assert.ok(lineasFicha("Zona", pierde, "sobra", ctx).includes("Aquí viajas más y te sobra menos: pierdes 2,0 € por cada hora de viaje de más (estimado)"));
});

test("sin cifra, la ficha dice el motivo concreto y ningún número; «mismo tiempo» es otro aviso", () => {
  const caso = casos.find((c) => c.nombre.startsWith("coche"));
  assert.deepEqual(fichaDe(caso, "28001", "sobra"), ["Zona", CATEGORIAS.alquiler.texto]);
  const sinRuta = { ...caso.salida.zonas["2807901"], horas: null, sobra: null, sobra_banda: null, precio_hora: null, etiqueta: null };
  const ctx = contextoFicha(ejemplo, caso.entrada, caso.salida, "2807901");
  assert.deepEqual(lineasFicha("Zona", sinRuta, "sobra", ctx), ["Zona", CATEGORIAS.ruta.texto]);
  const ambos = { ...sinRuta, alquiler: null };
  const lineas = lineasFicha("Zona", ambos, "precio_hora", ctx);
  assert.deepEqual(lineas, ["Zona", CATEGORIAS.ambos.texto]);
  assert.doesNotMatch(lineas.join(" "), CIFRA);
  const mismo = fichaDe(casos.find((c) => c.nombre.startsWith("1 día")), "28065", "precio_hora");
  assert.equal(mismo[1], CATEGORIAS["mismo tiempo"].texto);
  assert.notEqual(CATEGORIAS["mismo tiempo"].texto, CATEGORIAS.ruta.texto);
});

test("la zona estimada da su intervalo de la estimación en euros", () => {
  const caso = casos.find((c) => c.nombre.startsWith("coche"));
  // ic de 10,3 a 13,4 €/m² (fixture) con la escala que lleva el P50 de 11,8 €/m² al alquiler de la zona.
  assert.ok(fichaDe(caso, "28092").includes("Alquiler estimado: entre 459 y 608 € al mes (año 2024; intervalo de la estimación, de 464 a 603 €)"));
});

test("las diez mejores: orden por métrica, sin las zonas sin cifra ni, en el precio, las de menos horas", () => {
  const z = (precio_hora, sobra, horas) => ({ precio_hora, sobra, horas });
  const resultado = { ref: "r", zonas: { r: z(null, 100, 2), a: z(5, 200, 30), b: z(9, 300, 20), c: z(-4, 500, 1), d: z(null, null, null) } };
  const nombres = { r: "R", a: "A", b: "B", c: "C", d: "D" };
  assert.deepEqual(mejores(resultado, "precio_hora", nombres).map((m) => m.zona_id), ["b", "a"]);
  assert.deepEqual(mejores(resultado, "sobra", nombres).map((m) => m.zona_id), ["c", "b", "a", "r"]);
  assert.deepEqual(mejores(resultado, "horas", nombres).map((m) => m.zona_id), ["c", "r", "b", "a"]);
  assert.equal(mejores(resultado, "precio_hora", nombres)[0].texto, "B: 9,0 € por hora extra");
  const muchas = { ref: "r", zonas: Object.fromEntries(Array.from({ length: 15 }, (_, i) => [`z${i}`, z(i, i, i)])) };
  assert.equal(mejores(muchas, "sobra", {}).length, 10);
});

test("los avisos dicen suelo, año, zonas estimadas y sin dato, con su fuente", () => {
  const lineas = avisos(ejemplo.alquiler);
  assert.match(lineas[0], /suelo/);
  assert.equal(lineas[1], "El dato de alquiler es de 2024.");
  assert.ok(lineas.includes("1 zona con el alquiler estimado (borde discontinuo): su ficha da el intervalo de la estimación."));
  assert.ok(lineas.includes("1 zona sin dato publicado de alquiler: en gris y sin cifra."));
  assert.ok(!lineas.some((l) => l.startsWith("fuente:")), "con datos de ejemplo no se atribuye ninguna fuente");
  const reales = avisos(real.alquiler);
  assert.match(reales.at(-1), /^fuente: /);
  assert.match(reales.at(-1), / Tabla 76137 del INE actualizada el \d{4}-\d{2}-\d{2}\.$/);
  assert.ok(reales.includes("41 zonas sin dato publicado de alquiler: en gris y sin cifra."));
  assert.ok(!reales.some((l) => /estimado \(borde/.test(l)));
});

test("el aviso de prueba sale con los fixtures y no con los datos reales", () => {
  const metasDe = (api) => [api.zonas, ...NOMBRES.map((n) => api[n])].map((x) => x.meta);
  assert.match(avisoPrueba(metasDe(ejemplo)), /^Datos de prueba, no son datos reales: Ejemplo/);
  assert.equal(avisoPrueba(metasDe(real)), null);
  assert.equal(avisoPrueba([{ nota: "Ejemplo de otra cosa" }]), null, "la nota no decide: solo la marca");
  assert.ok(Object.values(ejemplo).every((f) => f.meta.ejemplo === true) && Object.values(real).every((f) => f.meta.ejemplo === undefined));
});

test("el tooltip añade el año solo si el alquiler de la zona es anterior al del fichero", () => {
  const meta = { anio_dato: 2024 };
  assert.equal(lineaTooltip(["Titulcia", "5 €/mes", "otra"], { anio: 2023 }, meta), "Titulcia · 5 €/mes · alquiler de 2023");
  assert.equal(lineaTooltip(["Getafe", "6 €/mes"], { anio: 2024 }, meta), "Getafe · 6 €/mes");
  assert.equal(lineaTooltip(["Getafe", "6 €/mes"], undefined, meta), "Getafe · 6 €/mes");
  assert.ok(Object.values(real.alquiler.zonas).some((z) => z.anio < real.alquiler.meta.anio_dato), "Titulcia sigue siendo de un año anterior");
});

test("la fuente del color de las horas no incluye el alquiler y la de las otras métricas sí", () => {
  assert.ok(!METRICAS.horas.datos.includes("alquiler"));
  for (const k of ["precio_hora", "sobra"]) assert.ok(METRICAS[k].datos.includes("alquiler"));
  for (const m of Object.values(METRICAS)) for (const n of m.datos) assert.ok(real[n].meta.fuentes.length > 0, n);
});

test("la atribución real lleva la cita del INE, la fecha del MIVAU y que el Ministerio no patrocina", () => {
  assert.match(licencias(real.zonas.meta), /Elaboración propia con datos extraídos del sitio web del INE: www\.ine\.es/);
  assert.match(real.alquiler.meta.nota, /actualizado el \d{4}-\d{2}-\d{2}; el Ministerio no participa ni patrocina/);
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

test("la zona de referencia es opcional y solo se acepta una de la lista", () => {
  assert.equal(validar(BASE, real).entrada.ref, undefined);
  assert.equal(validar({ ...BASE, ref: "28065" }, real).entrada.ref, "28065");
  assert.deepEqual(campos({ ref: "<script>" }), ["ref"]);
  assert.deepEqual(campos({ ref: "__proto__" }), ["ref"]);
});

test("varios errores se devuelven juntos, cada uno con su campo", () => {
  assert.deepEqual(campos({ bruto: "x", dias: "9", hijos: "7" }), ["bruto", "dias", "hijos"]);
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

test("las fuentes y licencias incluyen las de la ruta (fuentes_ruta de tarifas.json)", () => {
  const meta = { fuentes: [{ nombre: "CRTM", licencia: "CC BY 4.0" }], fuentes_ruta: [{ nombre: "RDL 17/2025", licencia: "BOE" }] };
  assert.equal(fuentes(meta), "fuente: CRTM, RDL 17/2025");
  assert.equal(licencias(meta), "CC BY 4.0; BOE");
});

// --- Escenarios «¿y si…?» y estado en el enlace -------------------------------------------------

const NEUTRO = { ...BASE, ref: "", metrica: "precio_hora", ...ESCENARIO_NEUTRO };
// Zona A (2807913) a zona A (2807901), 5 días y 2 viajes al día: el abono manda. Con los fixtures, el 10 viajes de un adulto cuesta 27,62 € y el Abono Joven, 9,31 €.
const transporteA = (edad, v) => {
  const base = { hogar: { perfil: "solo", edad }, sueldos: [{ bruto: 24000, destino: "2807901", dias: 5, modo: "tp" }], zonas: ["2807913"] };
  const entrada = entradaEscenario(base, { ...NEUTRO, ...v }, EDAD) ?? base;
  return calcular(ejemplo, entrada).zonas["2807913"].transporte;
};

test("sin el descuento, el abono de un adulto pasa de 27,62 a 47,29 € y el del joven, de 9,31 a 18,61 €", () => {
  const fin = { tarifas: "sin_descuento" };
  assert.equal(transporteA(30, {}).toFixed(2), "27.62");
  assert.equal(transporteA(30, fin).toFixed(2), "47.29");
  assert.equal(transporteA(20, {}).toFixed(2), "9.31");
  assert.equal(transporteA(20, fin).toFixed(2), "18.61");
});

test("cumplir 26 años quita el Abono Joven, y cambiar los días no toca los viajes al día", () => {
  assert.equal(transporteA(25, { cumple26: "si" }).toFixed(2), "27.62");
  const entrada = { hogar: { perfil: "solo", edad: 25 }, sueldos: [{ bruto: 24000, destino: "2807901", dias: 5, modo: "tp", viajes_dia: 4 }] };
  const sim = entradaEscenario(entrada, { ...NEUTRO, dias_esc: "3", subida: "10" }, EDAD);
  assert.deepEqual(sim.sueldos[0], { ...entrada.sueldos[0], dias: 3 });
  assert.deepEqual(sim.escenario, { tarifas: "vigente_2026", subida_alquiler: 10 });
  assert.equal(entradaEscenario(entrada, NEUTRO, EDAD), null);
  assert.equal(entrada.sueldos[0].dias, 5, "no se modifica la entrada original");
});

test("la subida del alquiler del escenario reduce lo que sobra, y la ficha lo dice", () => {
  const entrada = { hogar: { perfil: "solo", edad: 30 }, sueldos: [{ bruto: 24000, destino: "2807901", dias: 5, modo: "tp" }], zonas: ["28065"] };
  const actual = calcular(ejemplo, entrada).zonas["28065"];
  const sim = calcular(ejemplo, entradaEscenario(entrada, { ...NEUTRO, subida: "10" }, EDAD)).zonas["28065"];
  assert.ok(Math.abs(actual.alquiler * 0.1 - (actual.sobra - sim.sobra)) < 1e-9);
  const euros = Math.round(actual.sobra - sim.sobra).toLocaleString("es-ES");
  assert.equal(lineaDiferencia(actual, sim), `Con este escenario pierdes ${euros} € al mes frente a hoy (simulación, estimado)`);
});

test("la diferencia decide con lo redondeado y avisa si falta una cifra", () => {
  assert.match(lineaDiferencia({ sobra: 100 }, { sobra: 122 }), /ganas 22 € al mes/);
  assert.match(lineaDiferencia({ sobra: 100 }, { sobra: 78 }), /pierdes 22 € al mes/);
  assert.match(lineaDiferencia({ sobra: 100 }, { sobra: 100.4 }), /te sobra lo mismo que hoy/);
  assert.match(lineaDiferencia({ sobra: null }, { sobra: 1 }), /^Sin cifra para comparar/);
});

test("el título del escenario nombra solo lo que cambia", () => {
  assert.equal(tituloEscenario(NEUTRO, EDAD), null);
  assert.equal(tituloEscenario({ ...NEUTRO, tarifas: "sin_descuento", subida: "10", cumple26: "si", dias_esc: "1" }, EDAD),
    "Simulación: se acaba el descuento del transporte (abonos y 10 viajes); el alquiler sube un 10 %; cumples 26 años; 1 día presencial a la semana");
});

test("la cesta del tramo solo cambia la comida y se nombra en el título", () => {
  const entrada = { hogar: { perfil: "solo", edad: 30 }, sueldos: [{ neto_mes: 1400, destino: "2807901", dias: 5, modo: "tp" }], zonas: ["28065"] };
  const sim = entradaEscenario(entrada, { ...NEUTRO, cesta: "tramo" }, EDAD);
  assert.deepEqual(sim.escenario, { tarifas: "vigente_2026", subida_alquiler: 0, cesta: "tramo" });
  const actual = calcular(ejemplo, entrada).zonas["28065"];
  const tramo = calcular(ejemplo, sim).zonas["28065"];
  assert.ok(Math.abs(ejemplo.hogares.cesta_uc.alimentacion * 0.15 - (actual.cesta - tramo.cesta)) < 1e-9);
  assert.equal(tituloEscenario({ ...NEUTRO, cesta: "tramo" }, EDAD), "Simulación: la cesta básica es la de tu tramo de ingresos (estimado)");
});

test("la ficha dice qué cesta usa, el tramo con su diferencia y por qué la media es la referencia", () => {
  const linea = (neto, cesta) => {
    const entrada = { hogar: { perfil: "solo", edad: 30 }, sueldos: [{ neto_mes: neto, destino: "2807901", dias: 5, modo: "tp" }], zonas: ["28065"] };
    const sim = entradaEscenario(entrada, { ...NEUTRO, cesta }, EDAD) ?? entrada;
    const res = calcular(ejemplo, sim);
    return lineasFicha("Zona", res.zonas["28065"], "sobra", contextoFicha(ejemplo, sim, res, "28065")).find((l) => l.startsWith("Cesta básica"));
  };
  assert.match(linea(1400, "media"), /\(estimado: gasto medio de 2025 con el IPC/);
  const baja = linea(1400, "tramo");
  assert.match(baja, /de 1000 a 1499 € al mes: un 15 % menos que la media/);
  assert.match(baja, /simulación, estimado/);
  assert.match(baja, /fuente: INE, EPF de España 2025/);
  assert.match(baja, /La de referencia es la media/);
  assert.match(baja, /sobre el gasto medio de Madrid de 2025 con el IPC/);
  // el neto que elige el tramo va con céntimos: 499,99 no se lee «500» junto a «menos de 500»
  assert.match(linea(499.99, "tramo"), /\(499,99 € netos al mes\), de menos de 500 € al mes: un 30 % menos/);
  assert.match(linea(6000, "tramo"), /de 5000 € al mes o más: un 15 % más que la media/);
});

test("los escenarios inválidos se señalan campo a campo", () => {
  assert.deepEqual(erroresEscenario(NEUTRO, real), []);
  const mal = { tarifas: "x", subida: "31", cumple26: "tal", dias_esc: "6", cesta: "baja" };
  assert.deepEqual(erroresEscenario({ ...NEUTRO, ...mal }, real).map((e) => e.campo), Object.keys(mal));
  assert.equal(erroresEscenario({ ...NEUTRO, subida: "-1" }, real).length, 1);
  assert.equal(erroresEscenario({ ...NEUTRO, subida: "1.5" }, real).length, 1);
});

test("escribir y leer el enlace devuelve el mismo estado, también con tildes, comas y espacios", () => {
  const v = { ...NEUTRO, fuente: "neto", neto: "1.800,50", destino: "Alcalá de Henares", tarifas: "sin_descuento", subida: "17", cumple26: "si", dias_esc: "3", cesta: "tramo", metrica: "sobra" };
  const { valores, avisos: avisosEnlace } = estadoDeEnlace(estadoAEnlace(v), NEUTRO, real);
  assert.deepEqual(valores, v);
  assert.deepEqual(avisosEnlace, []);
  assert.deepEqual(estadoDeEnlace("", NEUTRO, real), { valores: NEUTRO, avisos: [] });
});

test("los parámetros inválidos del enlace se descartan con aviso y el resto se conserva", () => {
  const { valores, avisos: av } = estadoDeEnlace("subida=99&foo=1&tarifas=x&ref=nadie&metrica=otra&dias=2&__proto__=1", NEUTRO, real);
  assert.deepEqual(valores, { ...NEUTRO, dias: "2" });
  assert.equal(av.length, 5);
  assert.ok(av.includes("El enlace trae 2 datos desconocidos: se ignoran."));
  assert.ok(av.some((t) => t.includes("«subida»")) && av.some((t) => t.includes("«metrica»")));
  assert.equal(Object.getPrototypeOf(valores), Object.prototype);
});

test("un enlace que no da un estado válido ni descartando campos vuelve a los valores de ejemplo", () => {
  const { valores, avisos: av } = estadoDeEnlace("fuente=neto&neto=", NEUTRO, real);
  assert.deepEqual(valores, NEUTRO);
  assert.match(av.at(-1), /no da un estado válido/);
});

test("un enlace con claves enormes o numerosas da un solo aviso y no repite su texto", () => {
  const muchas = Array.from({ length: 1000 }, (_, i) => `clave${i}=1`).join("&");
  const largo = `${"x".repeat(5000)}=1`;
  for (const texto of [muchas, largo]) {
    const { valores, avisos: av } = estadoDeEnlace(texto, NEUTRO, real);
    assert.deepEqual(valores, NEUTRO);
    assert.equal(av.length, 1);
    assert.ok(av[0].length < 100);
  }
});

test("el importe que no corresponde a la fuente no se cuela desde el enlace", () => {
  const { valores } = estadoDeEnlace("fuente=bruto&bruto=30000&neto=texto%20libre", NEUTRO, real);
  assert.equal(valores.bruto, "30000");
  assert.equal(valores.neto, NEUTRO.neto);
});

test("«cumples 26 años» es la primera edad sin Abono Joven: edad_max_joven + 1", () => {
  assert.equal(ejemplo.tarifas.edad_max_joven + 1, 26);
  assert.equal(real.tarifas.edad_max_joven + 1, 26);
});

// --- Modo coche, segundo sueldo y polos (#97) ----------------------------------------------------

// Pareja con la segunda persona en IFEMA (polo) dos días; con los datos de ejemplo, que traen coche y polo.
const PAREJA = { ...BASE, perfil: "pareja", adultos: "2", destino: "Centro", destino2: "IFEMA", dias2: "2" };
// Las zonas del ejemplo que tienen tarifa a las dos ubicaciones (en las otras el ejemplo no trae corona tarifada).
const ZONAS_EJ = ["2807913", "28065"];
const validarEj = (cambios) => validar({ ...PAREJA, ...cambios }, ejemplo);

test("el coche se ofrece solo si los datos traen su matriz, los km y el coste por km", () => {
  assert.deepEqual(modosDisponibles(real.tiempos), ["tp"]);
  assert.deepEqual(modosDisponibles(ejemplo.tiempos), ["tp", "coche"]);
  for (const falta of ["coche", "km_coche", "coste_coche"]) {
    const { [falta]: _, ...resto } = ejemplo.tiempos;
    assert.deepEqual(modosDisponibles(resto), ["tp"], falta);
  }
  assert.deepEqual(campos({ modo: "coche" }), ["modo"]);
  assert.equal(validar({ ...BASE, destino: "Centro", modo: "coche" }, ejemplo).entrada.sueldos[0].modo, "coche");
});

test("los polos con nombre son destinos válidos, por nombre o por id", () => {
  assert.equal(resolverDestino("ifema", ejemplo.tiempos.destinos), "polo:ifema");
  assert.equal(resolverDestino("polo:ifema", ejemplo.tiempos.destinos), "polo:ifema");
});

test("con el perfil de pareja hay dos sueldos, cada uno con su lugar, días, viajes y modo; sin él, el segundo se ignora", () => {
  const { sueldos } = validarEj({ viajes2: "4", modo2: "coche", bruto2: "30.000" }).entrada;
  assert.deepEqual(sueldos, [
    { bruto: 24000, destino: "2807901", dias: 5, modo: "tp", viajes_dia: 2 },
    { bruto: 30000, destino: "polo:ifema", dias: 2, modo: "coche", viajes_dia: 4 },
  ]);
  const solo = validarEj({ perfil: "solo", adultos: "1", destino2: "no existe", dias2: "9" });
  assert.equal(solo.entrada.sueldos.length, 1);
});

test("los errores del segundo sueldo apuntan a sus campos y una pareja tiene dos adultos", () => {
  const campos2 = (cambios) => validarEj(cambios).errores?.map((e) => e.campo);
  assert.deepEqual(campos2({ destino2: "Atlantis" }), ["destino2"]);
  assert.deepEqual(campos2({ dias2: "6", viajes2: "3", modo2: "avión" }), ["dias2", "viajes2", "modo2"]);
  assert.deepEqual(campos2({ fuente2: "neto", neto2: "" }), ["neto2"]);
  assert.deepEqual(campos2({ pagas2: "13", bruto2: "x" }), ["pagas2", "bruto2"]);
  assert.deepEqual(campos2({ adultos: "1" }), ["adultos"]);
});

test("la ficha de pareja desglosa a cada persona y su suma es la del hogar", () => {
  for (const cambios of [{}, { modo2: "coche" }, { modo: "coche", viajes: "4" }]) {
    const { entrada } = validarEj(cambios);
    const resultado = calcular(ejemplo, { ...structuredClone(entrada), zonas: ZONAS_EJ });
    for (const id of ["2807913", "28065"]) {
      const zona = resultado.zonas[id];
      const { porPersona, personas } = contextoFicha(ejemplo, entrada, resultado, id);
      assert.equal(personas, entrada.hogar.personas_comparten, "`personas` sigue siendo cuántos comparten el piso");
      assert.equal(porPersona.length, 2);
      assert.ok(Math.abs(porPersona[0].horas + porPersona[1].horas - zona.horas) < 1e-9);
      assert.ok(Math.abs(porPersona[0].coste + porPersona[1].coste - zona.transporte) < 1e-9);
    }
  }
});

test("las líneas de la ficha de pareja dicen horas, coste y título de cada persona; con un sueldo no hay desglose", () => {
  const { entrada } = validarEj({ modo2: "coche" });
  const resultado = calcular(ejemplo, { ...structuredClone(entrada), zonas: ZONAS_EJ });
  const ficha = lineasFicha("Zona", resultado.zonas["28065"], "sobra", contextoFicha(ejemplo, entrada, resultado, "28065"));
  const personas = ficha.filter((l) => l.startsWith("Persona "));
  assert.equal(personas.length, 2);
  assert.match(personas[0], /^Persona 1 \(.+\): [\d,]+ h al mes, [\d,]+ € al mes de transporte \(estimado\)$/);
  assert.match(personas[1], /^Persona 2 \(coche\): /);
  assert.ok(ficha.some((l) => l.startsWith("Viaje al trabajo del hogar:")));
  assert.equal(fichaDe(casos[0], "28065").filter((l) => l.startsWith("Persona ")).length, 0);
  const sinCoste = { titulo: "coche", horas: 1, coste: null };
  const lineas = lineasFicha("Zona", resultado.zonas["28065"], "sobra", { ...contextoFicha(ejemplo, entrada, resultado, "28065"), porPersona: [sinCoste, { ...sinCoste, horas: null }] });
  assert.ok(lineas.includes("Persona 1 (coche): 1,0 h al mes, sin coste calculable (estimado)"));
  assert.ok(lineas.includes("Persona 2 (coche): sin ruta, sin coste calculable (estimado)"));
  const compartido = lineasFicha("Zona", resultado.zonas["28065"], "sobra", { ...contextoFicha(ejemplo, entrada, resultado, "28065"), personas: 3 });
  assert.ok(compartido.some((l) => l.includes("compartido entre 3")), "el desglose por persona no pisa cuántos comparten el piso");
});

test("los avisos del formulario: el coche nunca sin su aviso del tráfico y la pareja, la edad única", () => {
  const de = (cambios) => avisosEntrada(validarEj(cambios).entrada);
  assert.deepEqual(de({}).length, 1);
  assert.match(de({}).join(" "), /edad es una sola para el hogar.*Abono Joven.*las dos personas o a ninguna/);
  for (const cambios of [{ modo: "coche" }, { modo2: "coche" }]) {
    const lineas = de(cambios);
    assert.equal(lineas.length, 2);
    assert.match(lineas[0], /no incluye el tráfico.*estimación.*aparcamiento ni peajes/);
  }
  assert.deepEqual(avisosEntrada(validar({ ...BASE, destino: "Centro" }, ejemplo).entrada), []);
  assert.ok(!/\d/.test(de({ modo: "coche" })[0]), "sin cifras: no necesita nota de fuente");
});

test("el enlace de una pareja con dos destinos es válido; el modo coche sin matriz se descarta con aviso", () => {
  const porDefecto = { ...NEUTRO, destino: "Centro" };
  const ok = estadoDeEnlace("perfil=pareja&adultos=2&destino=Centro&destino2=IFEMA&dias2=2", porDefecto, ejemplo);
  assert.deepEqual(ok.avisos, []);
  assert.deepEqual([ok.valores.perfil, ok.valores.destino2, ok.valores.dias2], ["pareja", "IFEMA", "2"]);
  const coche = estadoDeEnlace("modo=coche", NEUTRO, real);
  assert.equal(coche.valores.modo, "tp");
  assert.equal(coche.avisos.length, 1);
  assert.match(coche.avisos[0], /«modo»/);
  assert.equal(estadoDeEnlace("modo=coche&destino=Centro", { ...NEUTRO, destino: "Centro" }, ejemplo).avisos.length, 0);
});

test("hay escenario si un solo campo se aparta del neutro", () => {
  assert.equal(hayEscenario(ESCENARIO_NEUTRO), false);
  assert.equal(hayEscenario({ ...ESCENARIO_NEUTRO, subida: "5" }), true);
  assert.equal(hayEscenario({ ...ESCENARIO_NEUTRO, dias_esc: "3" }), true);
});

test("el contorno de dos cuadrados vecinos deja fuera el borde común", () => {
  const cuadrado = (x) => ({ geometry: { type: "Polygon", coordinates: [[[x, 0], [x + 1, 0], [x + 1, 1], [x, 1], [x, 0]]] } });
  const { type, coordinates } = contorno([cuadrado(0), cuadrado(1)]);
  assert.equal(type, "MultiLineString");
  assert.equal(coordinates.length, 6); // 8 tramos menos los 2 del borde común (x = 1), uno por cuadrado
  assert.ok(!coordinates.some(([a, b]) => a[0] === 1 && b[0] === 1));
});

test("las zonas reales comparten bordes: el contorno es una parte pequeña de sus tramos", () => {
  const { features } = leer("app/datos/zonas.geojson");
  const tramos = features.flatMap(({ geometry: g }) => (g.type === "Polygon" ? [g.coordinates] : g.coordinates).flat()).reduce((n, anillo) => n + anillo.length - 1, 0);
  const { coordinates } = contorno(features);
  assert.ok(coordinates.length > 0 && coordinates.length < tramos / 2); // si no compartieran topología, saldrían casi todos
});

test("el importe inactivo de la segunda persona tampoco se cuela desde el enlace", () => {
  const { valores } = estadoDeEnlace("perfil=pareja&adultos=2&fuente2=bruto&neto2=texto%20libre", NEUTRO, real);
  assert.equal(valores.neto2, NEUTRO.neto2);
});
