// Cálculo de Kuanto en el navegador: port de src/mesobra/calculo.py (supuestos en su docstring).
// Funciones puras, sin DOM ni imports; solo interpola y consulta lo precalculado en `api`
// ({alquiler, hogares, netos, tarifas, tiempos, zonas}). Sin dato o sin ruta sale `null`, nunca 0.
// Contraste con Python: tests/fixtures/casos_referencia.json (app/calculo.test.js).

export const UMBRAL_HORAS = 5;
export const MISMO_TIEMPO = "mismo tiempo";
export const REFERENCIA = "referencia";
// 16: ET art. 6.1 (BOE-A-2015-11430); 64: el neto supone sin mínimo por edad >65 (LIRPF art. 57.2, BOE-A-2006-20764).
const EDAD_MIN = 16;
const EDAD_MAX = 64;
const MODOS = ["tp", "coche"];
const ESCENARIO = ["tarifas", "subida_alquiler", "edad", "cesta"];
const CESTAS = ["media", "tramo"];
const FAMILIAS = ["ordinario", "fn_general", "fn_especial"];
const EDAD_MIN_JOVEN = 15; // BOCM-20251231-2, pág. 66: de 7 a 14 años el abono es gratuito

const falta = (v) => v === null || v === undefined;
const tiene = (obj, clave) => obj !== null && typeof obj === "object" && Object.hasOwn(obj, clave);

function entero(nombre, valor, minimo, maximo) {
  if (!Number.isInteger(valor) || valor < minimo || valor > maximo) {
    throw new Error(`${nombre} = ${JSON.stringify(valor)}: debe ser un entero de ${minimo} a ${maximo}`);
  }
}

function numero(nombre, valor, minimo) {
  if (typeof valor !== "number" || !Number.isFinite(valor) || !(valor > minimo)) {
    throw new Error(`${nombre} = ${JSON.stringify(valor)}: debe ser un número mayor que ${minimo}`);
  }
}

export function precioHora(sobra, horas, sobraRef, horasRef) {
  if ([sobra, horas, sobraRef, horasRef].some(falta)) return [null, null];
  const dif = horas - horasRef;
  if (Math.abs(dif) < UMBRAL_HORAS) return [null, MISMO_TIEMPO];
  return [(sobra - sobraRef) / dif, null];
}

export function netoMes(netos, bruto, hogar) {
  if (typeof bruto !== "number") throw new Error(`bruto = ${JSON.stringify(bruto)}: debe ser un número`);
  const { brutos, configuraciones } = netos;
  const maximo = Math.max(...configuraciones.map((c) => c.hijos));
  if (!(hogar.hijos >= 0 && hogar.hijos <= maximo)) {
    throw new Error(`hijos = ${hogar.hijos}: la tabla de netos llega a ${maximo}`);
  }
  if (!(bruto >= brutos[0] && bruto <= brutos.at(-1))) {
    throw new Error(`bruto ${bruto} €/año fuera de la tabla de netos (${brutos[0]}–${brutos.at(-1)}): pide el neto mensual`);
  }
  const monoparental = hogar.adultos === 1 && hogar.hijos >= 1;
  const j = configuraciones.findIndex((c) => c.hijos === hogar.hijos && c.monoparental === monoparental);
  if (j < 0) throw new Error(`netos.json no tiene la configuración hijos=${hogar.hijos}, monoparental=${monoparental}`);
  const i = Math.max(Math.min(brutos.filter((b) => b <= bruto).length, brutos.length - 1), 1);
  const y0 = netos.neto_anual[i - 1][j];
  const y1 = netos.neto_anual[i][j];
  const t = (bruto - brutos[i - 1]) / (brutos[i] - brutos[i - 1]);
  return (y0 + t * (y1 - y0)) / 12;
}

// Tramo de ingresos de la EPF del neto €/mes del hogar: el último con `desde` ≤ neto (estimado, #312).
export function tramoCesta(tramos, neto) {
  return tramos[tramos.filter((t) => t.desde <= neto).length - 1];
}

export function cesta(cestaUc, hogar, factor) {
  const uc = 1 + 0.5 * (hogar.adultos - 1) + 0.3 * hogar.hijos;
  const p = hogar.personas_comparten;
  return cestaUc.alimentacion * factor * uc + ((cestaUc.suministros + cestaUc.comunicaciones) * (uc + 0.5 * (p - 1))) / p;
}

export function alquiler(zona, hogar, subida) {
  if (zona.origen === "sin_dato") return null;
  const k = (zona.factor_ipc * (1 + subida / 100) * hogar.m2) / hogar.personas_comparten;
  let [bajo, alto] = [zona.p25, zona.p75];
  if (zona.ic?.length) [bajo, alto] = [Math.min(bajo, zona.ic[0]), Math.max(alto, zona.ic[1])];
  return { p25: zona.p25 * k, p50: zona.p50 * k, p75: zona.p75 * k, min: bajo * k, max: alto * k };
}

function celda(tiempos, matriz, origen, destino) {
  const i = tiempos.origenes.indexOf(origen);
  const j = tiempos.destinos.findIndex((d) => d.destino_id === destino);
  if (!tiene(tiempos, matriz) || i < 0 || j < 0) {
    throw new Error(`tiempos.json no tiene ${matriz} de ${origen} a ${destino}`);
  }
  return tiempos[matriz][i][j] ?? null;
}

// {titulo, coste_mes} de la ruta de `origen` a `destino` en transporte público para un `sueldo` ya preparado
// (dias, viajes_dia, edad, colectivo, no_laborables): como `tarifa` de calculo.py.
export function tarifa(api, origen, destino, sueldo, escenario) {
  const t = api.tarifas;
  const i = t.origenes.indexOf(origen);
  const j = t.destinos.indexOf(destino);
  if (i < 0 || j < 0) throw new Error(`tarifas.json no tiene la ruta ${origen} → ${destino}`);
  let k = t.clave_tarifa[i][j];
  if (k !== null && sueldo.viajes_dia === 4) k = t.transbordo[k];
  if (k === null) throw new Error(`${origen} → ${destino}: sin clave de tarifa`);
  const edad = sueldo.edad <= t.edad_max_joven ? "joven" : "general";
  const porClave = t.tarifas_ruta[escenario][sueldo.colectivo][edad][t.claves[k]];
  return porClave[String(sueldo.no_laborables)][sueldo.dias - 1];
}

// [horas al mes, coste €/mes] del viaje de un sueldo; [null, null] si no hay ruta.
export function viaje(api, sueldo, origen, escenario) {
  const { tarifas, tiempos } = api;
  const { dias, destino } = sueldo;
  const minutos = celda(tiempos, sueldo.modo, origen, destino);
  if (minutos === null) return [null, null];
  let coste;
  if (sueldo.modo === "coche") {
    const km = celda(tiempos, "km_coche", origen, destino);
    coste = km === null ? null : 2 * km * dias * tarifas.semanas_mes * tiempos.coste_coche.eur_km;
  } else {
    coste = tarifa(api, origen, destino, sueldo, escenario.tarifas).coste_mes;
  }
  return [(minutos * 2 * dias * tarifas.semanas_mes) / 60, coste];
}

// Hijos con Abono Joven: de EDAD_MIN_JOVEN a edad_max_joven años.
export const hijosJovenes = (api, hogar) => hogar.edades_hijos.filter((e) => e >= EDAD_MIN_JOVEN && e <= api.tarifas.edad_max_joven).length;

// Abonos Jóvenes de los hijos de 15 a edad_max_joven años, €/mes: a 5 días y en la ruta del primer sueldo (el precio es plano).
function costeHijos(api, hogar, sueldos, zona, escenario) {
  const n = hijosJovenes(api, hogar);
  if (n === 0) return 0;
  const hijo = { dias: 5, viajes_dia: 2, edad: EDAD_MIN_JOVEN, colectivo: hogar.familia, no_laborables: hogar.no_laborables };
  return n * tarifa(api, zona, sueldos[0].destino, hijo, escenario.tarifas).coste_mes;
}

const suma = (valores) => (valores.some(falta) ? null : valores.reduce((a, b) => a + b, 0));

function calcularZona(api, hogar, sueldos, zona, escenario) {
  const neto = suma(sueldos.map((s) => s.neto_mes));
  const alq = alquiler(api.alquiler.zonas[zona], hogar, escenario.subida_alquiler);
  const viajes = sueldos.map((s) => viaje(api, s, zona, escenario));
  const transporte = suma([...viajes.map((v) => v[1]), costeHijos(api, hogar, sueldos, zona, escenario)]);
  const factor = escenario.cesta === "tramo" ? tramoCesta(api.hogares.cesta_tramos, neto).factor : 1;
  const cestaMes = cesta(api.hogares.cesta_uc, hogar, factor);
  const fijo = alq === null || transporte === null ? null : neto - transporte - cestaMes;
  return {
    origen: api.alquiler.zonas[zona].origen,
    neto,
    alquiler: alq === null ? null : alq.p50,
    alquiler_p25: alq === null ? null : alq.p25,
    alquiler_p75: alq === null ? null : alq.p75,
    transporte,
    cesta: cestaMes,
    sobra: fijo === null ? null : fijo - alq.p50,
    sobra_banda: fijo === null ? null : [fijo - alq.max, fijo - alq.min],
    horas: suma(viajes.map((v) => v[0])),
    esfuerzo: alq === null ? null : alq.p50 / neto,
  };
}

function estructura(entrada) {
  const objeto = (v) => v !== null && typeof v === "object" && !Array.isArray(v);
  if (!objeto(entrada) || !("hogar" in entrada) || !("sueldos" in entrada)) {
    throw new Error("entrada sin hogar o sueldos (debe ser un objeto con ambos)");
  }
  const tipos = { hogar: objeto, sueldos: Array.isArray, escenario: objeto, zonas: Array.isArray };
  for (const [clave, esTipo] of Object.entries(tipos)) {
    if (clave in entrada && !esTipo(entrada[clave])) throw new Error(`${clave}: tipo no válido`);
  }
  const ids = [...(entrada.zonas ?? []), entrada.ref];
  if (!entrada.sueldos.every(objeto) || !ids.every((i) => falta(i) || typeof i === "string")) {
    throw new Error("cada sueldo debe ser un objeto, y zonas y ref, textos");
  }
}

// Valida edades_hijos, familia y no_laborables del hogar.
function transporteHogar(api, hogar) {
  const edades = hogar.edades_hijos;
  if (!Array.isArray(edades) || ![0, hogar.hijos].includes(edades.length)) {
    throw new Error(`edades_hijos = ${JSON.stringify(edades)}: debe estar vacía o tener una edad por hijo (${hogar.hijos})`);
  }
  for (const e of edades) entero("edades_hijos", e, 0, api.tarifas.edad_max_joven);
  if (!FAMILIAS.includes(hogar.familia)) throw new Error(`familia = ${JSON.stringify(hogar.familia)}: debe ser ${FAMILIAS.join(" o ")}`);
  if (hogar.familia !== "ordinario" && hogar.hijos < 2) throw new Error(`familia numerosa con ${hogar.hijos} hijos: pide 2 o más`);
  if (!api.tarifas.no_laborables.includes(hogar.no_laborables)) {
    throw new Error(`no_laborables = ${JSON.stringify(hogar.no_laborables)}: debe ser ${JSON.stringify(api.tarifas.no_laborables)}`);
  }
}

function prepararHogar(api, entrada) {
  const h = entrada.hogar;
  if (typeof h.perfil !== "string" || !tiene(api.hogares.perfiles, h.perfil)) {
    throw new Error(`perfil desconocido: ${JSON.stringify(h.perfil)}`);
  }
  const hogar = { edades_hijos: [], familia: "ordinario", no_laborables: 0, ...api.hogares.perfiles[h.perfil], ...h };
  const pedido = entrada.escenario ?? {};
  const extra = Object.keys(pedido).filter((k) => !ESCENARIO.includes(k));
  if (extra.length) throw new Error(`escenario con claves desconocidas: ${JSON.stringify(extra.sort())}`);
  entero("edad", hogar.edad, EDAD_MIN, EDAD_MAX);
  const esc = { tarifas: "vigente_2026", subida_alquiler: 0, edad: hogar.edad, cesta: "media" };
  for (const [k, v] of Object.entries(pedido)) if (!falta(v)) esc[k] = v;
  numero("subida_alquiler", esc.subida_alquiler, -100);
  entero("edad", esc.edad, EDAD_MIN, EDAD_MAX);
  entero("adultos", hogar.adultos, 1, 2);
  entero("hijos", hogar.hijos, 0, Math.max(...api.netos.configuraciones.map((c) => c.hijos)));
  entero("personas_comparten", hogar.personas_comparten, 1, 20);
  numero("m2", hogar.m2, 0);
  transporteHogar(api, hogar);
  if (typeof esc.tarifas !== "string" || !tiene(api.tarifas.tarifas_ruta, esc.tarifas)) {
    throw new Error(`escenario ${JSON.stringify(esc.tarifas)} inválido`);
  }
  if (!CESTAS.includes(esc.cesta)) throw new Error(`cesta = ${JSON.stringify(esc.cesta)}: debe ser ${CESTAS.join(" o ")}`);
  return [hogar, esc];
}

// Colectivo de tarifas.json de una persona: su familia más su discapacidad del 65 % o más.
export const colectivo = (hogar, sueldo) => (!sueldo.discapacidad ? hogar.familia : hogar.familia === "ordinario" ? "discapacidad" : `${hogar.familia}_discapacidad`);

function prepararSueldos(api, entrada, hogar, escenario) {
  const { sueldos } = entrada;
  if (sueldos.length < 1 || sueldos.length > hogar.adultos) {
    throw new Error(`${sueldos.length} sueldos para ${hogar.adultos} adultos`);
  }
  return sueldos.map((original) => {
    const faltan = ["destino", "dias", "modo"].filter((k) => !(k in original));
    if (faltan.length) throw new Error(`sueldo sin ${JSON.stringify(faltan)}`);
    const s = { viajes_dia: 2, edad: escenario.edad, discapacidad: false, ...original };
    entero("dias", s.dias, 1, 5);
    entero("edad", s.edad, EDAD_MIN, EDAD_MAX);
    if (typeof s.discapacidad !== "boolean") throw new Error(`discapacidad = ${JSON.stringify(s.discapacidad)}: debe ser verdadero o falso`);
    s.colectivo = colectivo(hogar, s);
    s.no_laborables = hogar.no_laborables;
    if (!MODOS.includes(s.modo) || !api.tarifas.viajes_dia.includes(s.viajes_dia)) {
      throw new Error(`modo ${JSON.stringify(s.modo)} o viajes_dia ${JSON.stringify(s.viajes_dia)} inválido`);
    }
    if ("bruto" in s === "neto_mes" in s) throw new Error("cada sueldo lleva bruto o neto_mes, uno de los dos");
    if ("bruto" in s) s.neto_mes = netoMes(api.netos, s.bruto, hogar);
    else numero("neto_mes", s.neto_mes, 0);
    return s;
  });
}

export function calcular(api, entrada) {
  estructura(entrada);
  const [hogar, escenario] = prepararHogar(api, entrada);
  const sueldos = prepararSueldos(api, entrada, hogar, escenario);
  let ref = entrada.ref ?? null;
  // Se recorre el array, no un objeto: los ids numéricos («28079») reordenarían las claves.
  const ids = [...new Set([...(entrada.zonas ?? api.tiempos.origenes), ...(ref === null ? [] : [ref])])];
  const desconocidas = ids.filter((z) => !tiene(api.alquiler.zonas, z));
  if (desconocidas.length) throw new Error(`zonas sin entrada en alquiler.json: ${JSON.stringify(desconocidas)}`);
  const res = new Map(ids.map((z) => [z, calcularZona(api, hogar, sueldos, z, escenario)]));
  const completa = (z) => res.get(z).sobra !== null && res.get(z).horas !== null;
  if (ref === null) {
    ref = ids.filter(completa).reduce((mejor, z) => (mejor === null || res.get(z).horas < res.get(mejor).horas ? z : mejor), null);
  } else if (!completa(ref)) {
    throw new Error(`zona de referencia ${ref} sin sobrante u horas`);
  }
  const r = ref === null ? { sobra: null, horas: null } : res.get(ref);
  for (const z of res.values()) [z.precio_hora, z.etiqueta] = precioHora(z.sobra, z.horas, r.sobra, r.horas);
  if (ref !== null) res.get(ref).etiqueta = REFERENCIA;
  return { ref, escenario, zonas: Object.fromEntries(res) };
}
