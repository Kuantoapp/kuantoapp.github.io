// Lógica de la interfaz sin DOM ni MapLibre: validación del formulario, escalas de color, leyenda y textos.
// app.js solo la conecta. Todo son funciones puras con pruebas en vista.test.js.
import { MISMO_TIEMPO, REFERENCIA, UMBRAL_HORAS, corona, tramoCesta } from "./calculo.js";

// Viridis (secuencial, apta para daltónicos) para las horas. El rojo se reserva para alertas.
export const PALETA = ["#440154", "#3b528b", "#21918c", "#5ec962", "#fde725"];
// Divergente PuOr (apta para daltónicos) con el 0 como punto medio: naranja = pierdes, púrpura = ganas.
const NEGATIVOS = ["#b35806", "#f1a340"]; // del más negativo al más cercano a 0
const POSITIVOS = ["#998ec3", "#542788"]; // del más cercano a 0 al más alto
export const SIN_DATO = "#bdbdbd";
// Tope de tiempos.json (contrato de api_estatica): más minutos, o sin ruta, es null (ver tiempos.meta.nota).
const TOPE_RUTA_MIN = 120;

// Una categoría por motivo de que falte la cifra: nunca se pinta como cero ni con un color de clase.
export const CATEGORIAS = {
  alquiler: { texto: "Sin dato de alquiler", color: SIN_DATO },
  ruta: { texto: `Sin ruta en ${TOPE_RUTA_MIN} min`, color: "#8a8a8a" },
  ambos: { texto: `Sin dato de alquiler y sin ruta en ${TOPE_RUTA_MIN} min`, color: "#5c5c5c" },
  [MISMO_TIEMPO]: { texto: `Mismo tiempo de viaje que la referencia (menos de ${UMBRAL_HORAS} h/mes de diferencia)`, color: "#e0e0e0" },
  [REFERENCIA]: { texto: "Zona de referencia: con ella se compara el resto", color: "#ffffff" },
};

// Ficheros de la API cuyos números llegan al color de cada métrica (la geometría, `zonas`, se cita aparte).
const TODOS = ["alquiler", "hogares", "netos", "tarifas", "tiempos"];

export const METRICAS = {
  precio_hora: {
    titulo: "Precio de la hora de viaje",
    unidad: "€ al mes por cada hora de viaje extra al mes frente a la zona de referencia",
    corta: "€ por hora extra",
    datos: TODOS,
    decimales: 1,
    divergente: true,
    nota: "Estimado. En una zona con más horas que la de referencia, positivo es lo que ganas por cada hora de más y negativo, que pierdes dinero y tiempo a la vez. Con menos horas, el signo se invierte.",
  },
  sobra: {
    titulo: "Lo que sobra al mes",
    unidad: "€/mes del hogar tras alquiler, transporte y cesta básica",
    corta: "€/mes",
    datos: TODOS,
    decimales: 0,
    divergente: true,
    nota: "Negativo: no llega a fin de mes. Estimado con el alquiler mediano (P50).",
  },
  horas: {
    titulo: "Horas de viaje al mes",
    unidad: "h/mes de ida y vuelta al trabajo",
    corta: "h/mes",
    datos: ["tiempos", "tarifas"], // horas = minutos de ruta × días × semanas_mes: no entran ni el alquiler ni los netos
    decimales: 1,
    divergente: false,
    nota: `Estimado. Solo transporte público; más de ${TOPE_RUTA_MIN} min por trayecto cuenta como sin ruta.`,
  },
};

const esNumero = (v) => typeof v === "number" && Number.isFinite(v);
const formateador = (decimales) => new Intl.NumberFormat("es-ES", { minimumFractionDigits: decimales, maximumFractionDigits: decimales });

/**
 * Bordes de las clases [mínimo, …, máximo]. Sin valores devuelve [].
 * Cada borde es un valor observado (cuantil «por arriba»): así cada clase [a, b) contiene al menos a `a`
 * y ninguna queda vacía, ni con empates.
 */
export function cortesCuantiles(valores, k = 5) {
  const ordenados = valores.filter(esNumero).sort((a, b) => a - b);
  if (ordenados.length === 0) return [];
  const clases = Math.min(k, new Set(ordenados).size);
  const bordes = Array.from({ length: clases + 1 }, (_, i) => ordenados[Math.ceil((i / clases) * (ordenados.length - 1))]);
  return [...new Set(bordes)];
}

/** Clases secuenciales `{desde, hasta, color}` por cuantiles; la última es cerrada. */
export function escalaSecuencial(valores) {
  const cortes = cortesCuantiles(valores);
  if (cortes.length === 0) return [];
  if (cortes.length === 1) return [{ desde: cortes[0], hasta: cortes[0], color: PALETA[0] }];
  const total = cortes.length - 1;
  return Array.from({ length: total }, (_, i) => ({
    desde: cortes[i],
    hasta: cortes[i + 1],
    color: PALETA[total === 1 ? 0 : Math.round((i * (PALETA.length - 1)) / (total - 1))],
  }));
}

/** Clases divergentes con el 0 como borde: cuantiles por separado entre los negativos y los demás. */
export function escalaDivergente(valores) {
  const finitos = valores.filter(esNumero);
  const neg = cortesCuantiles(finitos.filter((v) => v < 0), 2);
  const pos = cortesCuantiles(finitos.filter((v) => v >= 0), 2);
  const inicios = neg.length > 1 ? neg.slice(0, -1) : neg;
  const clasesNeg = inicios.map((desde, i) => ({ desde, hasta: inicios[i + 1] ?? 0, color: NEGATIVOS[NEGATIVOS.length - inicios.length + i] }));
  const medios = pos.slice(1, -1);
  const ini = pos.length === 0 ? [] : [0, ...medios];
  const clasesPos = ini.map((desde, i) => ({ desde, hasta: ini[i + 1] ?? pos.at(-1), color: POSITIVOS[i] }));
  return [...clasesNeg, ...clasesPos];
}

/** Gris si no hay dato; si no, el color de la última clase que empieza en o antes de `valor`. */
export function colorPara(valor, clases) {
  if (!esNumero(valor)) return SIN_DATO;
  return clases.findLast((c) => c.desde <= valor)?.color ?? SIN_DATO;
}

/** Por qué falta la cifra de `metrica` en una zona del resultado del cálculo; `null` si no falta. */
export function categoria(zona, metrica) {
  if (esNumero(zona[metrica])) return null;
  if (metrica === "precio_hora" && zona.etiqueta) return zona.etiqueta;
  if (metrica === "horas") return "ruta";
  const sinAlquiler = zona.alquiler === null;
  const sinRuta = zona.horas === null;
  return sinAlquiler && sinRuta ? "ambos" : sinAlquiler ? "alquiler" : "ruta";
}

/** Pone `color`, `valor`, `categoria` (texto de por qué falta), `referencia` y `estimado` en cada zona. */
export function pintar(zonas, resultado, metrica) {
  if (!Array.isArray(zonas?.features) || typeof resultado?.zonas !== "object" || resultado.zonas === null) {
    throw new Error("Formato inesperado: faltan zonas.features o resultado.zonas");
  }
  if (!Object.hasOwn(METRICAS, metrica)) throw new Error(`Métrica desconocida: ${JSON.stringify(metrica)}`);
  const de = (f) => {
    const zona = resultado.zonas[f.properties.zona_id];
    if (!zona) throw new Error(`La zona ${f.properties.zona_id} no tiene resultado`);
    return zona;
  };
  const escala = METRICAS[metrica].divergente ? escalaDivergente : escalaSecuencial;
  const clases = escala(zonas.features.map((f) => de(f)[metrica]));
  const usadas = new Set();
  const features = zonas.features.map((f) => {
    const zona = de(f);
    const clave = categoria(zona, metrica);
    if (clave !== null) usadas.add(clave);
    const valor = esNumero(zona[metrica]) ? zona[metrica] : null;
    return {
      ...f,
      properties: {
        ...f.properties,
        valor,
        categoria: clave === null ? null : CATEGORIAS[clave].texto,
        color: clave === null ? colorPara(valor, clases) : CATEGORIAS[clave].color,
        referencia: zona.etiqueta === REFERENCIA,
        estimado: zona.origen === "estimado",
      },
    };
  });
  return { zonas: { ...zonas, features }, clases, categorias: [...usadas].map((k) => CATEGORIAS[k]) };
}

/** Entradas de la leyenda: una por clase `a – b` y una por cada motivo de «sin cifra» que aparece. */
export function leyenda(clases, categorias, metrica) {
  const f = formateador(METRICAS[metrica].decimales);
  const entradas = clases.map((c) => ({ color: c.color, texto: c.desde === c.hasta ? f.format(c.desde) : `${f.format(c.desde)} – ${f.format(c.hasta)}` }));
  return [...entradas, ...categorias];
}

// Supuesto: jornada completa de 40 h a la semana (máximo de la ordinaria, ET art. 34.1, BOE-A-2015-11430) durante las
// semanas que de verdad se trabajan (`tarifas.semanas_mes`, sin vacaciones ni fiestas), las mismas que cuentan los viajes.
const JORNADA_SEMANA = 40;
const ESFUERZO_RECOMENDADO = 0.3; // 30 % del neto en alquiler: recomendación de la herramienta (ficha §6.6)
const MEJORES = 10;
const euros = formateador(0);
const unDecimal = formateador(1);
const conCentimos = formateador(2);

/** Lo que la ficha necesita además de la zona: año del alquiler, zona de referencia, hogar, títulos y salario por hora. */
export function contextoFicha(api, entrada, resultado, id) {
  const hogar = { ...api.hogares.perfiles[entrada.hogar.perfil], ...entrada.hogar };
  const { escenario } = resultado;
  const edad = escenario.edad <= api.tarifas.edad_max_joven ? "joven" : "general";
  const titulo = (s) => {
    if (s.modo === "coche") return "coche";
    // shortcut: el 2 repite el `viajes_dia` por defecto de calculo.js; el formulario siempre lo da.
    const tabla = api.tarifas.escenarios[escenario.tarifas][edad][String(s.viajes_dia ?? 2)];
    return tabla[corona(api, id, s.destino)][s.dias - 1].titulo;
  };
  const zona = resultado.zonas[id];
  const dato = api.alquiler.zonas[id];
  const n = entrada.sueldos.length;
  return {
    anio: dato.anio,
    ipc: dato.factor_ipc === 1 ? null : mesIpc(api.alquiler.meta.ipc_hasta),
    ipcHasta: api.hogares.meta.ipc_hasta,
    tramo: escenario.cesta === "tramo" ? tramoDe(api.hogares.cesta_tramos, zona.neto) : null,
    subida: entrada.escenario?.subida_alquiler ?? 0,
    // Intervalo de la estimación (€/m²) en € al mes, con la misma escala que llevó el P50 a `zona.alquiler`.
    ic: dato.ic?.length && zona.alquiler !== null ? dato.ic.map((v) => (v * zona.alquiler) / dato.p50) : null,
    ref: resultado.ref === null ? null : resultado.zonas[resultado.ref],
    m2: hogar.m2,
    personas: hogar.personas_comparten,
    titulos: zona.transporte === null ? [] : entrada.sueldos.map(titulo),
    sueldos: n,
    netoEstimado: entrada.sueldos.some((s) => "bruto" in s),
    salarioHora: zona.neto / (JORNADA_SEMANA * api.tarifas.semanas_mes * n),
  };
}

// Tramo de ingresos del escenario de la cesta, con el corte siguiente para nombrarlo (#312).
function tramoDe(tramos, neto) {
  const t = tramoCesta(tramos, neto);
  return { ...t, hasta: tramos[tramos.indexOf(t) + 1]?.desde ?? null };
}

function fraseCesta(zona, ctx) {
  if (ctx.tramo === null) {
    return `Cesta básica: ${euros.format(zona.cesta)} €/mes (estimado: gasto medio de 2025 con el IPC hasta ${mesIpc(ctx.ipcHasta)}; incluye internet y móvil)`;
  }
  const { desde, hasta, factor } = ctx.tramo;
  const rango = desde === 0 ? `de menos de ${euros.format(hasta)} € al mes` : hasta === null ? `de ${euros.format(desde)} € al mes o más` : `de ${euros.format(desde)} a ${euros.format(hasta - 1)} € al mes`;
  const pct = Math.round(Math.abs(factor - 1) * 100);
  const frente = pct === 0 ? "lo mismo que la media" : `un ${pct} % ${factor < 1 ? "menos" : "más"} que la media`;
  return `Cesta básica: ${euros.format(zona.cesta)} €/mes (simulación, estimado: la comida, con lo que gastan los hogares de tu tramo de ingresos, ${rango}: ${frente}; fuente: INE, EPF de España 2025. La de referencia es la media: quien gana poco puede gastar menos en comida porque no le llega; incluye internet y móvil)`;
}

function frasePrecio(zona, ref) {
  const p = unDecimal.format(Math.abs(zona.precio_hora));
  const masHoras = zona.horas > ref.horas;
  if (masHoras && zona.precio_hora >= 0) return `Vivir aquí te paga ${p} € por cada hora de viaje de más (estimado)`;
  if (masHoras) return `Aquí viajas más y te sobra menos: pierdes ${p} € por cada hora de viaje de más (estimado)`;
  if (zona.precio_hora < 0) return "Aquí te sobra más y viajas menos que en la zona de referencia (estimado)";
  return `Vivir aquí te cuesta ${p} € por cada hora de viaje que te ahorras (estimado)`;
}

function fraseBanda([bajo, alto]) {
  const e = (v) => `${euros.format(Math.abs(v))} €`;
  // Se decide con lo redondeado que se muestra: −0,3 € no es «te falten 0 €».
  if (Math.round(bajo) >= 0) return `Te sobran entre ${e(bajo)} y ${e(alto)} al mes (estimado)`;
  if (Math.round(alto) <= 0) return `Te faltan entre ${e(alto)} y ${e(bajo)} al mes (estimado)`;
  return `Entre que te falten ${e(bajo)} y te sobren ${e(alto)} al mes (estimado)`;
}

const MES = new Intl.DateTimeFormat("es-ES", { month: "long", year: "numeric", timeZone: "UTC" });

/** «2026-10» (`meta.ipc_hasta`) como «octubre de 2026». */
function mesIpc(aaaamm) {
  return MES.format(new Date(`${aaaamm}-01T00:00:00Z`));
}

function fraseAlquiler(zona, { anio, ic, subida, ipc }) {
  const rango = `entre ${euros.format(zona.alquiler_p25)} y ${euros.format(zona.alquiler_p75)} € al mes`;
  // La subida simulada no es un dato observado: se dice aparte y se marca como simulación.
  if (subida > 0) {
    const dato = zona.origen === "estimado" ? `dato estimado de ${anio}` : `contratos de ${anio}`; // una zona imputada no tiene contratos
    const hasta = ipc === null ? "" : ` actualizad${zona.origen === "estimado" ? "o" : "os"} con el IPC de alquiler hasta ${ipc}`;
    return `Alquiler con la subida del ${subida} %: ${rango} (${dato}${hasta} más la subida; simulación, estimado)`;
  }
  if (zona.origen !== "estimado") {
    if (ipc === null) return `Alquiler: ${rango} (contratos de ${anio}, tómalo como un suelo)`;
    return `Alquiler: ${rango} (contratos de ${anio} actualizados con el IPC de alquiler hasta ${ipc}, tómalo como un suelo; estimado)`;
  }
  const intervalo = ic === null ? "sin intervalo publicado" : `intervalo de la estimación, de ${euros.format(ic[0])} a ${euros.format(ic[1])} €`;
  return `Alquiler estimado: ${rango} (año ${anio}${ipc === null ? "" : `, actualizado con el IPC de alquiler hasta ${ipc}`}; ${intervalo})`;
}

/**
 * Texto de la ficha de una zona: nombre, valor de la métrica activa (o por qué falta) y, si hay sobrante, el desglose.
 * Sin sobrante solo dice el motivo («sin dato de alquiler», «sin ruta…» o los dos), sin ninguna cifra calculada.
 * `ctx` sale de `contextoFicha`. Las dos primeras líneas son las del tooltip.
 */
export function lineasFicha(nombre, zona, metrica, ctx) {
  const f = formateador(METRICAS[metrica].decimales);
  const clave = categoria(zona, metrica);
  const lineas = [nombre, clave === null ? `${f.format(zona[metrica])} ${METRICAS[metrica].corta} (estimado)` : CATEGORIAS[clave].texto];
  const sinSobra = categoria(zona, "sobra");
  if (sinSobra !== null) return [...new Set([...lineas, CATEGORIAS[sinSobra].texto])];
  const quien = ctx.sueldos > 1 ? "Cada sueldo del hogar cobra de media" : "Tu trabajo te paga";
  const piso = (ESFUERZO_RECOMENDADO * zona.neto * ctx.m2) / zona.alquiler;
  lineas.push(
    fraseBanda(zona.sobra_banda),
    `Neto del hogar: ${euros.format(zona.neto)} € al mes${ctx.netoEstimado ? " (estimado)" : ""}`,
    fraseAlquiler(zona, ctx),
    `Transporte: ${conCentimos.format(zona.transporte)} € al mes (${[...new Set(ctx.titulos)].join(" y ")}) (estimado)`,
    fraseCesta(zona, ctx),
    `Viaje al trabajo: ${unDecimal.format(zona.horas)} h al mes, ida y vuelta (estimado)`,
    zona.etiqueta === null ? frasePrecio(zona, ctx.ref) : CATEGORIAS[zona.etiqueta].texto,
    `${quien} ${unDecimal.format(ctx.salarioHora)} € netos la hora (estimado, jornada de ${JORNADA_SEMANA} h a la semana)`,
    `El alquiler se lleva el ${euros.format(zona.esfuerzo * 100)} % del neto${Math.round(zona.esfuerzo * 100) > ESFUERZO_RECOMENDADO * 100 ? `, más del ${ESFUERZO_RECOMENDADO * 100} % que esta herramienta toma como referencia` : ""}${ctx.subida > 0 ? " (simulación, estimado)" : ctx.ipc !== null ? " (estimado)" : ""}`,
    `Con el ${ESFUERZO_RECOMENDADO * 100} % del neto alcanza para un piso de ${euros.format(piso)} m²${ctx.personas > 1 ? ` compartido entre ${ctx.personas}` : ""} (estimado)`,
  );
  return [...new Set(lineas)];
}

/**
 * Las diez mejores zonas según la métrica: más € por hora, más sobrante o menos horas. En el precio de la hora solo
 * entran las zonas con más horas que la referencia: con menos, el signo se invierte y no se pueden ordenar juntas.
 */
export function mejores(resultado, metrica, nombres) {
  const ref = resultado.ref === null ? null : resultado.zonas[resultado.ref];
  const f = formateador(METRICAS[metrica].decimales);
  const signo = metrica === "horas" ? 1 : -1;
  return Object.entries(resultado.zonas)
    .filter(([, z]) => esNumero(z[metrica]) && (metrica !== "precio_hora" || z.horas > ref.horas))
    .sort(([, a], [, b]) => signo * (a[metrica] - b[metrica]))
    .slice(0, MEJORES)
    .map(([id, z]) => ({ zona_id: id, texto: `${nombres[id]}: ${f.format(z[metrica])} ${METRICAS[metrica].corta}` }));
}

/** Aviso de que los ficheros cargados son de ejemplo, según `meta.ejemplo` (`null` si son datos reales). */
export function avisoPrueba(metas) {
  const prueba = metas.find((m) => m?.ejemplo === true);
  return prueba ? `Datos de prueba, no son datos reales: ${prueba.nota}` : null;
}

/** Avisos del dato de alquiler: es un suelo, año, zonas estimadas y zonas sin dato. La última línea es la fuente. */
export function avisos(alquiler) {
  const zonas = Object.values(alquiler.zonas);
  const cuantas = (origen) => zonas.filter((z) => z.origen === origen).length;
  const anterior = zonas.some((z) => z.anio != null && z.anio < alquiler.meta.anio_dato);
  // shortcut: aviso global; si conviven zonas con y sin IPC no lo dice por zona, mejorar entonces.
  const conIpc = zonas.some((z) => z.factor_ipc !== 1);
  const lineas = [
    `El alquiler sale de contratos ya firmados y declarados, no de anuncios${conIpc ? `, y la cifra está actualizada con el IPC de alquiler hasta ${mesIpc(alquiler.meta.ipc_hasta)} (estimado)` : ""}. Va por debajo de lo que piden hoy: tómalo como un suelo. Lo más probable es que te sobre menos de lo que ves aquí.`,
    `El dato de alquiler es de ${alquiler.meta.anio_dato}${anterior ? "; en alguna zona, de un año anterior, y lo dice su ficha" : ""}.`,
  ];
  const estimadas = cuantas("estimado");
  const zonasN = (n) => `${n} ${n === 1 ? "zona" : "zonas"}`;
  if (estimadas > 0) lineas.push(`${zonasN(estimadas)} con el alquiler estimado (borde discontinuo): su ficha da el intervalo de la estimación.`);
  const sinDato = cuantas("sin_dato");
  if (sinDato > 0) lineas.push(`${zonasN(sinDato)} sin dato publicado de alquiler: en gris y sin cifra.`);
  // Datos de ejemplo: sin fuente, para no atribuir datos inventados a quien publica los reales.
  return alquiler.meta.ejemplo === true ? lineas : [...lineas, `${fuentes(alquiler.meta)}.`];
}

// --- Validación del formulario -----------------------------------------------------------------
// shortcut: 16 y 64 repiten EDAD_MIN y EDAD_MAX de calculo.js (no se exportan); cuando se exporten, importarlos.
const EDAD = [16, 64];
const M2 = [10, 300]; // rango que acepta el contrato de hogares.json
const PERSONAS = [1, 20];
const sinEspacios = (t) => String(t ?? "").trim();
const numero = (t) => (/^-?\d+([.,]\d+)?$/.test(sinEspacios(t)) ? Number(sinEspacios(t).replace(",", ".")) : null);
// Un importe en euros admite el punto de miles a la española: «24.000» y «1.800,50» son 24000 y 1800,5, no 24 y 1,8.
const importe = (t) => numero(/^\d{1,3}(\.\d{3})+(,\d+)?$/.test(sinEspacios(t)) ? sinEspacios(t).replaceAll(".", "") : t);
const entero = (t) => (/^-?\d+$/.test(sinEspacios(t)) ? Number(sinEspacios(t)) : null);
const miles = formateador(0);

/** Destino por nombre (sin mayúsculas ni tildes) o por id; `null` si no existe o hay dos con ese nombre. */
export function resolverDestino(texto, destinos) {
  const limpio = (s) => s.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase().trim();
  const t = limpio(String(texto ?? ""));
  if (t === "") return null;
  const encontrados = destinos.filter((d) => d.tipo === "zona" && (d.destino_id === t || limpio(d.nombre) === t));
  return encontrados.length === 1 ? encontrados[0].destino_id : null;
}

/**
 * Valida los textos del formulario. Devuelve `{entrada}` para `calcular` o `{errores: [{campo, mensaje}]}`;
 * nunca lanza por lo que escriba la persona y nunca devuelve entrada si hay un error.
 * `v`: fuente ("bruto"|"neto"), bruto, neto (mensual medio), pagas (se valida, no entra en la cuenta), perfil, adultos, hijos, edad, m2, personas,
 * destino, dias, viajes, modo y ref (zona de referencia; vacía, la de menos horas). `api`: {alquiler, hogares, netos, tarifas, tiempos}.
 */
export function validar(v, api) {
  const errores = [];
  const falla = (campo, mensaje) => errores.push({ campo, mensaje });
  const enRango = (campo, texto, [min, max], mensaje) => {
    const n = entero(texto);
    if (n === null || n < min || n > max) falla(campo, mensaje ?? `Introduce un número entero de ${min} a ${max}`);
    return n;
  };
  const { brutos, configuraciones } = api.netos;
  const [brutoMin, brutoMax] = [brutos[0], brutos.at(-1)];
  const maxHijos = Math.max(...configuraciones.map((c) => c.hijos));

  const pagas = entero(v.pagas);
  if (![12, 14].includes(pagas)) falla("pagas", "Las pagas son 12 o 14");
  const sueldo = {};
  if (v.fuente === "bruto") {
    const bruto = importe(v.bruto);
    if (bruto === null) falla("bruto", "El sueldo bruto anual debe ser un número, sin letras ni signos");
    else if (bruto < brutoMin || bruto > brutoMax) {
      falla("bruto", `Para sueldos fuera de ${miles.format(brutoMin)}–${miles.format(brutoMax)} € brutos al año, introduce tu neto mensual medio`);
    } else sueldo.bruto = bruto;
  } else if (v.fuente === "neto") {
    // Neto mensual medio = neto anual ÷ 12 (`neto_mes` en la entrada de `calcular`). No se convierte desde la nómina: con 14 pagas
    // la paga extra ya cotiza prorrateada, así que nómina × 14 ÷ 12 no da el neto anual.
    const neto = importe(v.neto);
    const tope = brutoMax / 12; // el neto medio mensual no puede pasar del bruto mensual máximo
    if (neto === null || neto <= 0 || neto > tope) {
      falla("neto", `El neto mensual medio debe ser un número mayor que 0 y de como máximo ${miles.format(tope)} €`);
    } else sueldo.neto_mes = neto;
  } else falla("fuente", "Elige si das el bruto anual o el neto");

  if (typeof v.perfil !== "string" || !Object.hasOwn(api.hogares.perfiles, v.perfil)) falla("perfil", "Elige uno de los perfiles de hogar");
  const adultos = enRango("adultos", v.adultos, [1, 2]);
  const hijos = enRango("hijos", v.hijos, [0, maxHijos], `Hasta ${maxHijos} hijos`);
  const edad = enRango("edad", v.edad, EDAD, `La edad va de ${EDAD[0]} a ${EDAD[1]} años`);
  const personas = enRango("personas", v.personas, PERSONAS, `Cuenta los hogares del piso, el tuyo incluido: de ${PERSONAS[0]} (no compartes piso) a ${PERSONAS[1]}`);
  const m2 = numero(v.m2);
  if (m2 === null || m2 < M2[0] || m2 > M2[1]) falla("m2", `La vivienda va de ${M2[0]} a ${M2[1]} m²`);

  const destino = resolverDestino(v.destino, api.tiempos.destinos);
  if (destino === null) falla("destino", "Elige un lugar de trabajo de la lista");
  const dias = enRango("dias", v.dias, [1, 5], "Los días presenciales van de 1 a 5");
  const viajes = entero(v.viajes);
  if (!api.tarifas.viajes_dia.includes(viajes)) falla("viajes", `Los viajes al día son ${api.tarifas.viajes_dia.join(" o ")}`);
  if (v.modo !== "tp") falla("modo", "Por ahora solo hay transporte público");
  const ref = sinEspacios(v.ref);
  if (ref !== "" && !Object.hasOwn(api.alquiler.zonas, ref)) falla("ref", "Elige una zona de referencia de la lista");

  if (errores.length > 0) return { errores };
  const hogar = { perfil: v.perfil, adultos, hijos, edad, personas_comparten: personas, m2 };
  const sueldos = [{ ...sueldo, destino, dias, modo: "tp", viajes_dia: viajes }];
  return { entrada: { hogar, sueldos, ...(ref === "" ? {} : { ref }) } };
}

// --- Escenarios «¿y si…?» y estado en el enlace ------------------------------------------------
// Campos del formulario de escenarios (todos son select o deslizador: siempre traen valor) y su valor «sin escenario».
export const ESCENARIO_NEUTRO = { tarifas: "vigente_2026", subida: "0", cumple26: "no", dias_esc: "", cesta: "media" };
const SUBIDA = [0, 30];

/** Errores `{campo, mensaje}` de los valores del formulario de escenarios; `[]` si todos valen. */
export function erroresEscenario(v, api) {
  const errores = [];
  const falla = (campo, mensaje) => errores.push({ campo, mensaje });
  if (typeof v.tarifas !== "string" || !Object.hasOwn(api.tarifas.escenarios, v.tarifas)) falla("tarifas", "Elige una de las tarifas de la lista");
  const subida = entero(v.subida);
  if (subida === null || subida < SUBIDA[0] || subida > SUBIDA[1]) falla("subida", `La subida del alquiler va de ${SUBIDA[0]} a ${SUBIDA[1]} %`);
  if (!["no", "si"].includes(v.cumple26)) falla("cumple26", "Elige sí o no");
  if (v.dias_esc !== "" && ![1, 2, 3, 4, 5].includes(entero(v.dias_esc))) falla("dias_esc", "Los días presenciales van de 1 a 5");
  if (!["media", "tramo"].includes(v.cesta)) falla("cesta", "Elige una de las cestas de la lista");
  return errores;
}

/**
 * Entrada del cálculo con el escenario aplicado, o `null` si ningún campo se aparta de `ESCENARIO_NEUTRO`.
 * Los valores ya están validados. Cambiar los días no toca los viajes al día de cada sueldo.
 */
export function entradaEscenario(entrada, v, edadCumple) {
  if (Object.entries(ESCENARIO_NEUTRO).every(([k, neutro]) => v[k] === neutro)) return null;
  const escenario = { tarifas: v.tarifas, subida_alquiler: Number(v.subida), ...(v.cumple26 === "si" ? { edad: edadCumple } : {}), ...(v.cesta === "tramo" ? { cesta: "tramo" } : {}) };
  const dias = v.dias_esc === "" ? {} : { dias: Number(v.dias_esc) };
  return { ...entrada, escenario, sueldos: entrada.sueldos.map((s) => ({ ...s, ...dias })) };
}

/** Qué simula el mapa, en una línea; `null` si no hay escenario. */
export function tituloEscenario(v, edadCumple) {
  const partes = [
    ...(v.tarifas !== ESCENARIO_NEUTRO.tarifas ? ["se acaba el descuento del transporte (abonos y 10 viajes)"] : []),
    ...(v.subida !== ESCENARIO_NEUTRO.subida ? [`el alquiler sube un ${v.subida} %`] : []),
    ...(v.cumple26 === "si" ? [`cumples ${edadCumple} años`] : []),
    ...(v.dias_esc !== "" ? [`${v.dias_esc} ${v.dias_esc === "1" ? "día presencial" : "días presenciales"} a la semana`] : []),
    ...(v.cesta === "tramo" ? ["la cesta básica es la de tu tramo de ingresos (estimado)"] : []),
  ];
  return partes.length === 0 ? null : `Simulación: ${partes.join("; ")}`;
}

/** Línea de la ficha con lo que cambia el sobrante al mes frente a la situación actual, decidida con lo redondeado que se muestra. */
export function lineaDiferencia(actual, simulada) {
  if (!esNumero(actual.sobra) || !esNumero(simulada.sobra)) return "Sin cifra para comparar con la situación actual";
  const dif = Math.round(simulada.sobra - actual.sobra);
  const cifra = `${euros.format(Math.abs(dif))} €`;
  if (dif === 0) return "Con este escenario te sobra lo mismo que hoy (simulación, estimado)";
  return `Con este escenario ${dif < 0 ? "pierdes" : "ganas"} ${cifra} al mes frente a hoy (simulación, estimado)`;
}

/** Fragmento de la URL (sin «#») con los valores de los formularios. */
export const estadoAEnlace = (valores) => new URLSearchParams(valores).toString();

/**
 * Lee el fragmento de la URL. `porDefecto` son los valores de los formularios sin tocar (define qué claves existen).
 * Descarta, con aviso, las claves desconocidas y los valores no válidos (el campo vuelve a su valor por defecto);
 * si aun así el conjunto no es válido, descarta el enlace entero. Nunca lanza por lo que traiga la URL.
 */
export function estadoDeEnlace(texto, porDefecto, api) {
  const pedido = new URLSearchParams(texto);
  const avisos = [];
  const valores = { ...porDefecto };
  let desconocidos = 0; // no se repite su nombre: viene de fuera y puede ser un texto largo o engañoso
  for (const [clave, valor] of pedido) {
    if (Object.hasOwn(porDefecto, clave)) valores[clave] = valor;
    else desconocidos += 1;
  }
  if (desconocidos > 0) avisos.push(`El enlace trae ${desconocidos} ${desconocidos === 1 ? "dato desconocido" : "datos desconocidos"}: se ignoran.`);
  // El importe que no corresponde a `fuente` no se valida ni se usa: vuelve a su valor por defecto en vez de colarse en el formulario.
  const inactivo = valores.fuente === "bruto" ? "neto" : valores.fuente === "neto" ? "bruto" : null;
  if (inactivo !== null) valores[inactivo] = porDefecto[inactivo];
  const malos = (v) => [
    ...(validar(v, api).errores ?? []),
    ...erroresEscenario(v, api),
    ...(Object.hasOwn(METRICAS, v.metrica) ? [] : [{ campo: "metrica" }]),
  ];
  for (const { campo } of malos(valores)) {
    if (!pedido.has(campo) || !Object.hasOwn(porDefecto, campo)) continue;
    valores[campo] = porDefecto[campo];
    avisos.push(`El enlace trae un valor no válido en «${campo}»: se usa el de ejemplo.`);
  }
  if (malos(valores).length > 0) return { valores: porDefecto, avisos: [...avisos, "El enlace no da un estado válido: se usan los valores de ejemplo."] };
  return { valores, avisos };
}

/** Licencias de los `meta.fuentes` sin repetir, separadas por «; ». */
export function licencias(...metas) {
  const textos = new Set(metas.flatMap((m) => (m?.fuentes ?? []).map((f) => f.licencia)));
  return [...textos].join("; ");
}

/** «fuente: A, B» sin repetir, a partir de los `meta.fuentes` de los ficheros cargados. */
export function fuentes(...metas) {
  const nombres = new Set(metas.flatMap((m) => (m?.fuentes ?? []).map((f) => f.nombre)));
  return `fuente: ${[...nombres].join(", ")}`;
}

/** Tooltip de una zona: sus dos primeras líneas y, si su alquiler es de un año anterior al del fichero, el año. */
export function lineaTooltip(lineas, dato, meta) {
  const anterior = dato?.anio != null && dato.anio < meta.anio_dato;
  return `${lineas.slice(0, 2).join(" · ")}${anterior ? ` · alquiler de ${dato.anio}` : ""}`;
}
