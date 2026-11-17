// Lógica de la interfaz sin DOM ni MapLibre: validación del formulario, escalas de color, leyenda y textos.
// app.js solo la conecta. Todo son funciones puras con pruebas en vista.test.js.
import { MISMO_TIEMPO, REFERENCIA, UMBRAL_HORAS } from "./calculo.js";

// Viridis (secuencial, apta para daltónicos) para las horas. El rojo se reserva para alertas.
export const PALETA = ["#440154", "#3b528b", "#21918c", "#5ec962", "#fde725"];
// Divergente PuOr (apta para daltónicos) con el 0 como punto medio: naranja = pierdes, púrpura = ganas.
const NEGATIVOS = ["#b35806", "#f1a340"]; // del más negativo al más cercano a 0
const POSITIVOS = ["#998ec3", "#542788"]; // del más cercano a 0 al más alto
export const SIN_DATO = "#bdbdbd";

// Una categoría por motivo de que falte la cifra: nunca se pinta como cero ni con un color de clase.
export const CATEGORIAS = {
  alquiler: { texto: "Sin dato de alquiler", color: SIN_DATO },
  ruta: { texto: "Sin ruta en 120 min", color: "#8a8a8a" },
  ambos: { texto: "Sin dato de alquiler y sin ruta en 120 min", color: "#5c5c5c" },
  [MISMO_TIEMPO]: { texto: `Mismo tiempo de viaje que la referencia (menos de ${UMBRAL_HORAS} h/mes de diferencia)`, color: "#e0e0e0" },
  [REFERENCIA]: { texto: "Zona de referencia (la de menos horas de viaje)", color: "#ffffff" },
};

export const METRICAS = {
  precio_hora: {
    titulo: "Precio de la hora de viaje",
    unidad: "€ al mes por cada hora de viaje extra al mes frente a la zona de referencia",
    corta: "€ por hora extra",
    decimales: 1,
    divergente: true,
    nota: "Negativo: vivir ahí te deja menos dinero y además viajas más.",
  },
  sobra: {
    titulo: "Lo que sobra al mes",
    unidad: "€/mes del hogar tras alquiler, transporte y cesta básica",
    corta: "€/mes",
    decimales: 0,
    divergente: true,
    nota: "Negativo: no llega a fin de mes. Estimado con el alquiler mediano (P50).",
  },
  horas: {
    titulo: "Horas de viaje al mes",
    unidad: "h/mes de ida y vuelta al trabajo",
    corta: "h/mes",
    decimales: 1,
    divergente: false,
    nota: "Solo transporte público; más de 120 min por trayecto cuenta como sin ruta.",
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

/** «12,3 €/mes» o el motivo de que falte, con el nombre de la zona delante. */
export function lineasFicha(nombre, zona, anio, metrica) {
  const f = formateador(METRICAS[metrica].decimales);
  const clave = categoria(zona, metrica);
  const lineas = [nombre, clave === null ? `${f.format(zona[metrica])} ${METRICAS[metrica].corta}` : CATEGORIAS[clave].texto];
  if (anio !== null && anio !== undefined) lineas.push(`Alquiler de ${anio}${zona.origen === "estimado" ? " (estimado)" : ""}`);
  if (esNumero(zona.cesta)) lineas.push(`Cesta básica: ${formateador(0).format(zona.cesta)} €/mes (estimado, gasto medio de 2025)`);
  return lineas;
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
 * destino, dias, viajes, modo. `api`: {hogares, netos, tarifas, tiempos}.
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
    // Neto mensual medio = neto anual ÷ 12 (supuesto 4 de calculo.py). No se convierte desde la nómina: con 14 pagas
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
  const personas = enRango("personas", v.personas, PERSONAS);
  const m2 = numero(v.m2);
  if (m2 === null || m2 < M2[0] || m2 > M2[1]) falla("m2", `La vivienda va de ${M2[0]} a ${M2[1]} m²`);

  const destino = resolverDestino(v.destino, api.tiempos.destinos);
  if (destino === null) falla("destino", "Elige un lugar de trabajo de la lista");
  const dias = enRango("dias", v.dias, [1, 5], "Los días presenciales van de 1 a 5");
  const viajes = entero(v.viajes);
  if (!api.tarifas.viajes_dia.includes(viajes)) falla("viajes", `Los viajes al día son ${api.tarifas.viajes_dia.join(" o ")}`);
  if (v.modo !== "tp") falla("modo", "Por ahora solo hay transporte público");

  if (errores.length > 0) return { errores };
  const hogar = { perfil: v.perfil, adultos, hijos, edad, personas_comparten: personas, m2 };
  return { entrada: { hogar, sueldos: [{ ...sueldo, destino, dias, modo: "tp", viajes_dia: viajes }] } };
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
