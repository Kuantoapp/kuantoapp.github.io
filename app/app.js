// Conecta la página: carga los datos, crea el mapa y lo repinta al cambiar el formulario.
// La validación, el color y los textos están en vista.js y el cálculo en calculo.js; aquí solo hay DOM.
// El sueldo no sale del navegador: lo único que se pide por red son los ficheros de `datos/`, del mismo sitio.
import { calcular } from "./calculo.js";
import {
  ESCENARIO_NEUTRO, METRICAS, avisoPrueba, baseEscala, avisos, avisosEntrada, contextoFicha, contorno, entradaEscenario, estadoAEnlace, estadoDeEnlace, hayEscenario, imprecisas, leyenda, licencias, lineaDiferencia,
  lineaTooltip, lineasFicha, mejores, modosDisponibles, nombresFuente, pintar, tituloEscenario, validar, valorDeEjemplo,
} from "./vista.js";

const $ = (id) => document.getElementById(id);
const formulario = () => $("formulario");
const NOMBRES = ["alquiler", "hogares", "netos", "tarifas", "tiempos"];
const EDAD_POR_DEFECTO = 30; // supuesto: hogares.json no trae edad; decide el Abono Joven (hasta 25 años)
const reducido = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

// Siempre `datos/` junto a la página: sin parámetro, porque en github.io el origen lo comparten otros repos (#255).
const CARPETA_DATOS = new URL("datos/", location.href);

async function cargarJSON(base, nombre) {
  const res = await fetch(new URL(nombre, base));
  if (!res.ok) throw new Error(`No se pudo cargar ${nombre} (${res.status})`);
  return res.json();
}

async function cargarApi(base) {
  const [zonas, ...resto] = await Promise.all([cargarJSON(base, "zonas.geojson"), ...NOMBRES.map((n) => cargarJSON(base, `${n}.json`))]);
  return { ...Object.fromEntries(NOMBRES.map((n, i) => [n, resto[i]])), zonas };
}

function elemento(etiqueta, texto, clase) {
  const el = document.createElement(etiqueta);
  el.textContent = texto;
  if (clase) el.className = clase;
  return el;
}

// --- Formulario ----------------------------------------------------------------------------------

const formularios = () => [formulario(), $("escenario")];
const valoresFormulario = () => Object.fromEntries(formularios().flatMap((f) => [...new FormData(f)]));

/** Escribe en los controles los valores ya validados (claves de `valoresFormulario`). */
function aplicarValores(valores) {
  for (const f of formularios()) for (const [clave, valor] of Object.entries(valores)) if (f.elements[clave]) f.elements[clave].value = valor;
}

// La segunda persona solo existe con el perfil de pareja.
const mostrarSegunda = () => {
  $("persona2").hidden = formulario().elements.perfil.value !== "pareja";
};

// Un campo de edad por hijo, solo los que hay.
const mostrarHijos = () => {
  const n = Number(formulario().elements.hijos.value);
  $("edades-hijos").hidden = !(n > 0);
  for (const etiqueta of $("edades-hijos").querySelectorAll("label")) etiqueta.hidden = Number(etiqueta.dataset.hijo) > n;
};

function rellenarPerfil(api) {
  const f = formulario().elements;
  const p = api.hogares.perfiles[f.perfil.value];
  f.adultos.value = String(p.adultos);
  f.hijos.value = String(p.hijos);
  f.m2.value = String(p.m2);
  f.personas.value = String(p.personas_comparten);
}

function prepararFormulario(api) {
  const destinos = $("destinos");
  for (const d of api.tiempos.destinos.filter((x) => ["zona", "polo"].includes(x.tipo))) {
    const opcion = document.createElement("option");
    opcion.value = d.nombre;
    destinos.append(opcion);
  }
  // El coche solo se ofrece si los datos traen su matriz (`modosDisponibles`); el transporte público ya está en el HTML.
  if (modosDisponibles(api.tiempos).includes("coche")) {
    for (const modo of [formulario().elements.modo, formulario().elements.modo2]) modo.append(new Option("Coche", "coche"));
  }
  const metricas = $("metricas");
  for (const [clave, m] of Object.entries(METRICAS)) {
    const etiqueta = document.createElement("label");
    const radio = Object.assign(document.createElement("input"), { type: "radio", name: "metrica", value: clave, checked: clave === "precio_hora" });
    etiqueta.append(radio, m.titulo);
    metricas.append(etiqueta);
  }
  const refs = formulario().elements.ref;
  const porNombre = [...api.zonas.features].sort((a, b) => a.properties.nombre.localeCompare(b.properties.nombre, "es"));
  for (const f of porNombre) refs.append(new Option(f.properties.nombre, f.properties.zona_id));
  rellenarPerfil(api);
  formulario().elements.edad.value = String(EDAD_POR_DEFECTO);
}

/** El control de un campo (el primero de un grupo de radios), o el formulario si no existe. */
function controlDe(campo) {
  const control = formulario().elements[campo];
  return control?.nodeType === 1 ? control : (control?.[0] ?? formulario());
}

function mostrarErrores(errores) {
  for (const el of formulario().querySelectorAll(".error, .usar-ejemplo")) el.remove();
  for (const el of formulario().querySelectorAll("[aria-invalid]")) el.removeAttribute("aria-invalid");
  for (const { campo, mensaje } of errores) {
    const destino = controlDe(campo);
    const aviso = elemento("span", mensaje, "error");
    aviso.id = `error-${campo}`;
    aviso.setAttribute("role", "alert");
    if (destino !== formulario()) {
      destino.setAttribute("aria-invalid", "true");
      destino.setAttribute("aria-describedby", aviso.id);
      destino.after(aviso);
    } else formulario().prepend(aviso);
  }
}

// --- Leyenda, ficha y mapa -----------------------------------------------------------------------

function pintarLeyenda(api, resultadoPintado, metrica) {
  const m = METRICAS[metrica];
  const cont = $("leyenda");
  const { alquiler, hogares, netos, tarifas, tiempos, zonas } = api;
  const metas = [zonas.meta, alquiler.meta, tiempos.meta, hogares.meta, netos.meta, tarifas.meta];
  const hayEstimadas = Object.values(alquiler.zonas).some((z) => z.origen === "estimado");
  const hayImprecisas = imprecisas(alquiler).size > 0 && m.datos.includes("alquiler");
  const usaAlquiler = m.datos.includes("alquiler");
  const pct = new Intl.NumberFormat("es-ES", { style: "percent", signDisplay: "exceptZero" });
  const metodo = m.cortes ? `Cortes fijos en el ${m.cortes.map((c) => pct.format(c)).join(", ")} ${m.base}` : "Cuantiles";
  // A la vista, lo justo para leer el mapa; lo largo (unidad, fuentes, notas, licencias) va al <details>.
  cont.replaceChildren(elemento("p", `${m.titulo}, en ${m.corta} (estimado)${usaAlquiler ? `, con el alquiler de ${alquiler.meta.anio_dato}` : ""}`, "titulo"));
  for (const { color, texto } of leyenda(resultadoPintado.clases, resultadoPintado.categorias, metrica)) {
    const fila = elemento("div", "", "fila");
    const muestra = elemento("span", "", "muestra");
    muestra.style.backgroundColor = color;
    fila.append(muestra, elemento("span", texto));
    cont.append(fila);
  }
  cont.append(elemento("p", `${hayImprecisas ? "Borde punteado: pocos alquileres declarados (impreciso). " : ""}${hayEstimadas ? "Borde discontinuo: alquiler estimado. " : ""}Borde grueso: zona de referencia.`));
  // Lo largo va plegado: a la vista del desplegable, qué mide; dentro, fuentes, licencias y notas.
  const detalle = document.createElement("details");
  const ejemplo = avisoPrueba(metas) !== null; // datos inventados: no se atribuyen a ninguna fuente
  detalle.append(elemento("summary", "Fuentes, método y licencias"), elemento("p", `${m.unidad}. ${metodo}. ${m.nota} Parte de los tiempos de viaje son estimados.`));
  // Segundo nivel: las fuentes, las licencias y las notas de cada fichero, que llevan las fechas de actualización y los avisos
  // de supuestos que piden las licencias (MIVAU, Comunidad de Madrid) y el propio cálculo.
  const todas = document.createElement("details");
  const notas = [
    `Alquiler: ${alquiler.meta.nota}`,
    `Tiempos: ${tiempos.meta.nota ?? "ver fuentes"}`,
    `Hogar y cesta: ${hogares.meta.nota}`,
    `Neto y tarifas (estimado): ${netos.meta.nota ?? "con la normativa de 2026"} ${tarifas.meta.nota ?? ""} ${tarifas.meta.nota_ruta ?? ""}`,
  ];
  if (ejemplo) todas.append(elemento("summary", "Notas"));
  else {
    const nombres = nombresFuente(...metas);
    const lista = document.createElement("ul");
    lista.append(...nombres.map((n) => elemento("li", n)));
    todas.append(elemento("summary", `Fuentes (${nombres.length}), licencias y notas`), lista, elemento("p", `Licencias: ${licencias(...metas)}.`));
  }
  todas.append(...notas.map((n) => elemento("p", n)));
  detalle.append(todas);
  cont.append(detalle);
}

/** Caja que envuelve las zonas dadas (Polygon y MultiPolygon). */
function limitesDe(features) {
  const limites = new maplibregl.LngLatBounds();
  for (const f of features) {
    const c = f.geometry.coordinates.flat(Infinity);
    for (let i = 0; i < c.length; i += 2) limites.extend([c[i], c[i + 1]]);
  }
  return limites;
}

// Mapa base propio, del mismo sitio: provincias y países vecinos (`mesobra.fondo`) y glifos para los nombres de zona.
// Nada sale a la red, así que funciona sin conexión. `{fontstack}` y `{range}` los rellena MapLibre: no van por `new URL`.
const CARPETA_MAPA = new URL("mapa/", location.href);
const GLIFOS = `${new URL("glifos/", CARPETA_MAPA).href}{fontstack}/{range}.pbf`;
const FUENTE_ETIQUETAS = ["Noto Sans Regular"]; // solo el rango 0-255 (test_fondo comprueba los nombres)
// España entera (Península, Baleares, Canarias, Ceuta y Melilla): al alejar, el mapa no sale de aquí.
const ESPANA = [[-19.5, 26.8], [5.5, 44.6]];
const VELO = { type: "Feature", properties: {}, geometry: { type: "Polygon", coordinates: [[[-180, -85], [180, -85], [180, 85], [-180, 85], [-180, -85]]] } };
// Colores del mapa (no de la web) en cada tema. Los de las clases no cambian: son los datos. `marca` y `bajoMarca` son las
// líneas de zona imprecisa, estimada, de referencia y elegida, y el halo que las separa de la clase de debajo.
const TEMAS = {
  claro: { mar: "#dfe6ec", vecino: "#ecece8", provincia: "#f7f7f5", lineaProvincia: "#c9ccd1", lineaPais: "#a9adb4", velo: "#f5f5f7", interior: "#d9e6f6", contorno: "#0b4f9c", bordeZona: "#ffffff", texto: "#1d1d1f", textoProvincia: "#5c6069", halo: "#ffffff", marca: "#111111", bajoMarca: "#ffffff" },
  oscuro: { mar: "#11161c", vecino: "#181d24", provincia: "#232a33", lineaProvincia: "#3a4350", lineaPais: "#56606e", velo: "#0d1117", interior: "#1d3352", contorno: "#7fb2ff", bordeZona: "#0d1117", texto: "#e6e8eb", textoProvincia: "#a9b0ba", halo: "#0d1117", marca: "#f5f5f7", bajoMarca: "#0d1117" },
};
// [capa, propiedad de pintura, color de TEMAS]
const PINTURA_TEMA = [
  ["mar", "background-color", "mar"], ["vecinos", "fill-color", "vecino"], ["provincias", "fill-color", "provincia"],
  ["provincias-borde", "line-color", "lineaProvincia"], ["vecinos-borde", "line-color", "lineaPais"], ["velo", "fill-color", "velo"], ["comunidad-interior", "fill-color", "interior"],
  ["comunidad", "line-color", "contorno"], ["zonas-borde", "line-color", "bordeZona"], ["zonas-nombre", "text-color", "texto"],
  ["zonas-nombre", "text-halo-color", "halo"], ["provincias-nombre", "text-color", "textoProvincia"], ["provincias-nombre", "text-halo-color", "halo"], ["zonas-encima", "line-color", "marca"], ["zonas-elegida-halo", "line-color", "bajoMarca"],
  ["zonas-elegida", "line-color", "marca"], ["zonas-imprecisas-fondo", "line-color", "bajoMarca"], ["zonas-imprecisas", "line-color", "marca"],
  ["zonas-estimadas", "line-color", "marca"], ["zonas-referencia", "line-color", "marca"], ["zonas-encima-halo", "line-color", "bajoMarca"],
  ["zonas-estimadas-fondo", "line-color", "bajoMarca"], ["zonas-referencia-fondo", "line-color", "bajoMarca"],
];

const CLAVE_TEMA = "kuanto.temaMapa";

/** El tema que eligió quien mira (si el navegador deja guardarlo) o, si no, el de su sistema. */
function temaActual() {
  try {
    const guardado = localStorage.getItem(CLAVE_TEMA);
    if (Object.hasOwn(TEMAS, guardado ?? "")) return guardado;
  } catch {
    // sin almacenamiento (ventana privada, bloqueado): se decide por el sistema
  }
  return matchMedia("(prefers-color-scheme: dark)").matches ? "oscuro" : "claro";
}

function aplicarTema(mapa, tema) {
  for (const [capa, propiedad, clave] of PINTURA_TEMA) if (mapa.getLayer(capa)) mapa.setPaintProperty(capa, propiedad, TEMAS[tema][clave]);
}

function crearMapa(zonas, fondo) {
  const t = TEMAS.claro;
  const deTipo = (tipo) => ["==", ["get", "tipo"], tipo];
  const mapa = new maplibregl.Map({
    container: "mapa",
    // Solo el mar al crear: las capas con GeoJSON se añaden en `load`, así ese evento no espera a procesarlas.
    style: { version: 8, glyphs: GLIFOS, sources: {}, layers: [{ id: "mar", type: "background", paint: { "background-color": t.mar } }] },
    attributionControl: false, // el fondo es de dominio público (Natural Earth) y se cita en data/README.md
    maxBounds: ESPANA,
    maxZoom: 13, // los polígonos están simplificados: a nivel de calle no casan
  });
  mapa.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
  const limites = limitesDe(zonas.features);
  // En pantalla estrecha la leyenda ocupa parte del contenedor cuando se pinta, después de crear el mapa:
  // hay que recalcular su tamaño y encuadrarlo de nuevo, o se corta por abajo.
  const encuadrar = (opciones = { animate: false }) => {
    mapa.resize();
    mapa.fitBounds(limites, { padding: 24, ...opciones });
  };
  encuadrar();
  let pendiente = null;
  mapa.on("load", () => {
    mapa.addSource("fondo", { type: "geojson", data: fondo });
    mapa.addLayer({ id: "vecinos", type: "fill", source: "fondo", filter: deTipo("pais"), paint: { "fill-color": t.vecino } });
    mapa.addLayer({ id: "provincias", type: "fill", source: "fondo", filter: deTipo("provincia"), paint: { "fill-color": t.provincia } });
    mapa.addLayer({ id: "vecinos-borde", type: "line", source: "fondo", filter: deTipo("pais"), paint: { "line-color": t.lineaPais, "line-width": 0.8 } });
    // Solo de lejos: de cerca se vería, junto al contorno de las zonas, el borde de Madrid de Natural Earth (hasta 3,7 km de desfase)
    mapa.addLayer({ id: "provincias-borde", type: "line", source: "fondo", maxzoom: 8.5, filter: deTipo("provincia"), paint: { "line-color": t.lineaProvincia, "line-width": 1 } });
    // Fuera de la Comunidad, un velo claro: es el único sitio donde la herramienta tiene datos.
    mapa.addSource("velo", { type: "geojson", data: VELO });
    mapa.addLayer({ id: "velo", type: "fill", source: "velo", paint: { "fill-color": "#f5f5f7", "fill-opacity": 0.55 } });
    mapa.addSource("zonas", { type: "geojson", data: pendiente ?? zonas, promoteId: "zona_id" });
    mapa.addSource("comunidad", { type: "geojson", data: { type: "Feature", properties: {}, geometry: contorno(zonas.features) } });
    // Interior de la Comunidad (las zonas la cubren entera), un azul claro del acento: solo en la vista previa del recorrido (#389).
    mapa.addLayer({ id: "comunidad-interior", type: "fill", source: "zonas", paint: { "fill-color": t.interior, "fill-opacity": 0 } });
    mapa.addLayer({ id: "zonas-relleno", type: "fill", source: "zonas", paint: { "fill-color": ["get", "color"], "fill-opacity": 0.85 } });
    mapa.addLayer({ id: "zonas-borde", type: "line", source: "zonas", paint: { "line-color": "#ffffff", "line-width": 1.4 } });
    mapa.addLayer({ id: "comunidad", type: "line", source: "comunidad", paint: { "line-color": "#0b4f9c", "line-width": 2.5 } });
    // Al pasar por encima, la zona se recorta con la línea de marca; la elegida (ficha abierta), además con halo.
    const siEncima = (ancho) => ["case", ["boolean", ["feature-state", "encima"], false], ancho, 0];
    mapa.addLayer({ id: "zonas-encima-halo", type: "line", source: "zonas", paint: { "line-color": "#ffffff", "line-width": siEncima(4) } });
    mapa.addLayer({ id: "zonas-encima", type: "line", source: "zonas", paint: { "line-color": "#1d1d1f", "line-width": siEncima(2) } });
    // Halo blanco bajo una línea casi negra: se ve sobre cualquier clase, clara u oscura.
    mapa.addLayer({ id: "zonas-elegida-halo", type: "line", source: "zonas", filter: ["==", ["get", "zona_id"], ""], paint: { "line-color": "#ffffff", "line-width": 6 } });
    mapa.addLayer({ id: "zonas-elegida", type: "line", source: "zonas", filter: ["==", ["get", "zona_id"], ""], paint: { "line-color": "#1d1d1f", "line-width": 3 } });
    // Fondo blanco bajo el punteado: sin él no se ve sobre la clase más oscura.
    mapa.addLayer({ id: "zonas-imprecisas-fondo", type: "line", source: "zonas", filter: ["==", ["get", "impreciso"], true], paint: { "line-color": "#fff", "line-width": 3 } });
    mapa.addLayer({ id: "zonas-imprecisas", type: "line", source: "zonas", filter: ["==", ["get", "impreciso"], true], paint: { "line-color": "#111", "line-width": 1.5, "line-dasharray": [1, 1.5] } });
    // Cada marca lleva su halo (`bajoMarca`) para verse sobre clases claras y oscuras en los dos temas.
    // Una marca nueva se suma también a `MARCAS` (en `main`), o se vería en el mapa de vista previa del recorrido.
    const estimada = ["==", ["get", "estimado"], true];
    const referencia = ["==", ["get", "referencia"], true];
    mapa.addLayer({ id: "zonas-estimadas-fondo", type: "line", source: "zonas", filter: estimada, paint: { "line-color": "#fff", "line-width": 4 } });
    mapa.addLayer({ id: "zonas-estimadas", type: "line", source: "zonas", filter: estimada, paint: { "line-color": "#111", "line-width": 2, "line-dasharray": [2, 2] } });
    mapa.addLayer({ id: "zonas-referencia-fondo", type: "line", source: "zonas", filter: referencia, paint: { "line-color": "#fff", "line-width": 5 } });
    mapa.addLayer({ id: "zonas-referencia", type: "line", source: "zonas", filter: referencia, paint: { "line-color": "#000", "line-width": 3 } });
    // Nombres oficiales de provincia de lejos; al acercarse los sustituyen los de las zonas.
    mapa.addLayer({
      id: "provincias-nombre",
      type: "symbol",
      source: "fondo",
      maxzoom: 8.5,
      filter: deTipo("etiqueta"),
      layout: { "text-field": ["get", "nombre"], "text-font": FUENTE_ETIQUETAS, "text-size": 11, "text-max-width": 7 },
      paint: { "text-color": t.textoProvincia, "text-halo-color": t.halo, "text-halo-width": 1.5 },
    });
    // Nombres de zona al acercarse, encima de todo.
    mapa.addLayer({
      id: "zonas-nombre",
      type: "symbol",
      source: "zonas",
      minzoom: 9.5,
      layout: { "text-field": ["get", "nombre"], "text-font": FUENTE_ETIQUETAS, "text-size": 12, "text-max-width": 8 },
      paint: { "text-color": t.texto, "text-halo-color": t.halo, "text-halo-width": 1.5 },
    });
    pendiente = null;
    // El botón manda: si se pulsó antes de cargar y no hay almacenamiento, `temaActual` ya no diría lo mismo.
    aplicarTema(mapa, $("tema-mapa").getAttribute("aria-pressed") === "true" ? "oscuro" : "claro");
  });
  return {
    mapa,
    encuadrar,
    actualizar(datos) {
      const fuente = mapa.getSource("zonas");
      if (fuente) fuente.setData(datos);
      else pendiente = datos;
    },
  };
}

// --- Principal -----------------------------------------------------------------------------------

async function main() {
  const [api, fondo] = await Promise.all([cargarApi(CARPETA_DATOS), cargarJSON(CARPETA_MAPA, "fondo.geojson")]);
  $("fecha-datos").textContent = api.tiempos.meta.generado;
  const maxHijos = Math.max(...api.netos.configuraciones.map((c) => c.hijos));
  $("max-hijos").textContent = `(hasta ${maxHijos} hijos)`;
  prepararFormulario(api);
  for (let i = 1; i <= maxHijos; i++) {
    const etiqueta = elemento("label", `Edad del hijo ${i} `);
    etiqueta.dataset.hijo = String(i);
    etiqueta.append(Object.assign(document.createElement("input"), { name: `hijo${i}`, type: "number", inputMode: "numeric" }));
    $("edades-hijos").append(etiqueta);
  }
  const deEjemplo = valoresFormulario(); // los de la página al abrirse, antes del enlace: «Usar el valor de ejemplo»
  // El estado de los formularios viaja en el fragmento de la URL, que no se envía a ningún servidor.
  const enlace = estadoDeEnlace(location.hash.slice(1), valoresFormulario(), api);
  aplicarValores(enlace.valores);
  mostrarSegunda();
  mostrarHijos();
  const { mapa, actualizar, encuadrar } = crearMapa(api.zonas, fondo);
  prepararVista(mapa);
  // Va con los avisos del dato y no en la leyenda: con otros ficheros el formulario por defecto puede no validar y la leyenda no se pinta.
  const prueba = avisoPrueba([api.zonas, ...NOMBRES.map((n) => api[n])].map((x) => x.meta));
  $("pie").hidden = prueba !== null; // el pie atribuye los tiempos al CRTM: con datos de ejemplo no
  const lineasAviso = [...(prueba ? [prueba] : []), ...enlace.avisos, ...avisos(api.alquiler)];
  $("avisos").replaceChildren(...lineasAviso.map((t) => elemento("li", t)));
  const nombres = Object.fromEntries(api.zonas.features.map((f) => [f.properties.zona_id, f.properties.nombre]));
  // `resultado` es lo que se pinta (el escenario si lo hay); `actual`, la situación de hoy, solo para la diferencia.
  const estado = { entrada: null, resultado: null, actual: null, simulando: false, metrica: "precio_hora", zona: null };
  const lineas = (id) => lineasFicha(nombres[id], estado.resultado.zonas[id], estado.metrica, contextoFicha(api, estado.entrada, estado.resultado, id));
  // La ficha de la zona pinchada se mantiene, actualizada, al cambiar de métrica o de entradas. Con un escenario, la tercera línea
  // es la diferencia frente a hoy (las dos primeras son las del tooltip).
  const fichaDe = (id) => {
    const base = lineas(id);
    return estado.simulando ? [...base.slice(0, 2), lineaDiferencia(estado.actual.zonas[id], estado.resultado.zonas[id]), ...base.slice(2)] : base;
  };
  const pintarFicha = () =>
    $("ficha").replaceChildren(...(estado.zona ? fichaDe(estado.zona).map((t, i) => elemento("p", t, estado.simulando && i === 2 ? "diferencia" : "")) : []));
  const elegir = (id) => {
    estado.zona = id;
    pintarFicha();
    for (const capa of ["zonas-elegida-halo", "zonas-elegida"]) if (mapa.getLayer(capa)) mapa.setFilter(capa, ["==", ["get", "zona_id"], id]);
  };
  function pintarMejores() {
    $("mejores-titulo").textContent = `Las diez mejores zonas: ${METRICAS[estado.metrica].titulo.toLowerCase()} (estimado)`;
    const items = mejores(estado.resultado, estado.metrica, nombres, imprecisas(api.alquiler)).map(({ zona_id, texto }) => {
      const boton = elemento("button", texto);
      boton.type = "button";
      boton.addEventListener("click", () => {
        mapa.fitBounds(limitesDe(api.zonas.features.filter((f) => f.properties.zona_id === zona_id)), { padding: 48, maxZoom: 11, duration: reducido() ? 0 : 900 });
        elegir(zona_id);
      });
      // La zona se marca en el mapa al pasar por la lista, con el ratón o con el teclado.
      for (const evento of ["mouseenter", "focus"]) boton.addEventListener(evento, () => marcarEncima(zona_id));
      for (const evento of ["mouseleave", "blur"]) boton.addEventListener(evento, () => marcarEncima(null));
      const li = document.createElement("li");
      li.append(boton);
      return li;
    });
    $("mejores-lista").replaceChildren(...(items.length ? items : [elemento("li", "Ninguna zona tiene cifra con estas entradas.")]));
  }

  function recalcular() {
    const v = valoresFormulario();
    const { entrada, errores } = validar(v, api);
    mostrarErrores(errores ?? []);
    if (!errores) $("avisos-hogar").replaceChildren(...avisosEntrada(entrada).map((t) => elemento("li", t)));
    if (errores) {
      $("estado").textContent = "Corrige los campos marcados para recalcular el mapa.";
      return;
    }
    const entradaSim = entradaEscenario(entrada, v, api.tarifas.edad_max_joven + 1);
    let actual;
    let pintada;
    try {
      actual = calcular(api, entrada);
      pintada = entradaSim === null ? actual : calcular(api, entradaSim);
    } catch (error) {
      const porRef = entrada.ref && error.message.startsWith("zona de referencia");
      $("estado").textContent = porRef
        ? "La zona de referencia que elegiste no tiene alquiler o ruta con estas entradas: elige otra o deja «la de menos horas»."
        : `No se pudo calcular: ${error.message}`;
      return;
    }
    Object.assign(estado, { entrada: entradaSim ?? entrada, resultado: pintada, actual, simulando: entradaSim !== null });
    $("estado").textContent = "";
    $("subida-valor").textContent = `${v.subida} %`;
    history.replaceState(history.state, "", `#${estadoAEnlace(v)}`);
    estado.metrica = v.metrica;
    const algunaZona = Object.values(actual.zonas)[0];
    // Con dos sueldos `zona.neto` es el del hogar: no es el de la primera persona.
    if (v.fuente === "bruto") formulario().elements.neto.value = entrada.sueldos.length === 1 ? String(Math.round(algunaZona.neto)) : "";
    const base = baseEscala(estado.metrica, api, estado.entrada, estado.resultado);
    const pintado = pintar(api.zonas, estado.resultado, estado.metrica, { pocas: imprecisas(api.alquiler), base });
    actualizar(pintado.zonas);
    pintarLeyenda(api, pintado, estado.metrica);
    const simulacion = tituloEscenario(v, api.tarifas.edad_max_joven + 1);
    if (simulacion) $("leyenda").querySelector(".titulo").after(elemento("p", simulacion, "titulo"));
    pintarFicha();
    pintarMejores();
  }

  formulario().addEventListener("input", (e) => {
    const { name } = e.target;
    if (name === "perfil") {
      rellenarPerfil(api);
      mostrarSegunda();
    }
    if (["perfil", "hijos"].includes(name)) {
      mostrarHijos();
    }
    if (["bruto", "neto", "bruto2", "neto2"].includes(name)) formulario().elements[`fuente${name.endsWith("2") ? "2" : ""}`].value = name.replace("2", "");
    recalcular();
  });
  formulario().addEventListener("submit", (e) => e.preventDefault());
  $("escenario").addEventListener("input", recalcular);
  $("escenario").addEventListener("submit", (e) => e.preventDefault());

  // Deshacer y rehacer: cada cambio confirmado (evento `change`: al soltar el deslizador o salir de un campo) es un paso del
  // historial, así que también valen «atrás» y «adelante» del navegador. `confirmado` es el estado del paso actual;
  // `inicial`, el de la página al abrirse (lo que recupera «Cancelar cambios»); `pasoMax`, el último paso al que se puede rehacer.
  let confirmado = null;
  let inicial = null;
  let pasoMax = 0;
  const pasoActual = () => history.state?.paso ?? 0;
  const actualizarBotones = () => {
    $("deshacer").disabled = pasoActual() === 0;
    $("rehacer").disabled = pasoActual() >= pasoMax;
    $("cancelar").disabled = confirmado === inicial;
    $("quitar-escenario").disabled = !hayEscenario(valoresFormulario());
  };
  const guardarPaso = () => {
    actualizarBotones(); // también si el paso no se guarda (errores o sin cambios): «Quitar el escenario» sigue al formulario
    const valores = valoresFormulario();
    // Un paso con errores no se guarda: al volver a él, el enlace lo descartaría y «Deshacer» parecería no hacer nada.
    if (validar(valores, api).errores) return;
    const ahora = estadoAEnlace(valores);
    if (ahora === confirmado) return;
    const paso = pasoActual() + 1;
    history.replaceState(history.state, "", `#${confirmado}`); // `recalcular` ya había escrito el nuevo en este paso
    history.pushState({ paso }, "", `#${ahora}`);
    confirmado = ahora;
    pasoMax = paso; // un cambio nuevo descarta lo que se podía rehacer, como en el navegador
    actualizarBotones();
  };
  // Aplica un estado del enlace a los formularios y repinta.
  const ir = (valores) => {
    aplicarValores(valores);
    mostrarSegunda();
    mostrarHijos(); // las casillas de edad de los hijos siguen al número de hijos del estado al que se vuelve
    recalcular();
  };
  formulario().addEventListener("change", guardarPaso);
  $("escenario").addEventListener("change", guardarPaso);
  $("deshacer").addEventListener("click", () => history.back());
  $("rehacer").addEventListener("click", () => history.forward());
  // Ir a la portada apila una entrada (#388) y descarta lo que se podía rehacer, como un cambio nuevo.
  $("ir-portada").addEventListener("click", () => {
    pasoMax = pasoActual();
    actualizarBotones();
  });
  $("cancelar").addEventListener("click", () => {
    ir(estadoDeEnlace(inicial, valoresFormulario(), api).valores);
    guardarPaso(); // también se puede deshacer
  });
  $("quitar-escenario").addEventListener("click", () => {
    aplicarValores(ESCENARIO_NEUTRO);
    recalcular();
    guardarPaso();
  });
  window.addEventListener("popstate", () => {
    ir(estadoDeEnlace(location.hash.slice(1), valoresFormulario(), api).valores);
    confirmado = estadoAEnlace(valoresFormulario());
    actualizarBotones();
  });

  const tooltip = $("tooltip");
  let encima = null; // zona bajo el puntero, para su borde (feature-state)
  const marcarEncima = (id) => {
    if (!mapa.getSource("zonas")) return; // antes de que cargue el mapa
    if (encima !== null) mapa.setFeatureState({ source: "zonas", id: encima }, { encima: false });
    encima = id;
    if (id !== null) mapa.setFeatureState({ source: "zonas", id }, { encima: true });
  };
  mapa.on("mousemove", "zonas-relleno", (e) => {
    if (!estado.resultado || guiado()) return; // en el recorrido el mapa solo se mira
    const id = e.features[0].properties.zona_id;
    if (id !== encima) marcarEncima(id);
    tooltip.textContent = lineaTooltip(lineas(id), METRICAS[estado.metrica].datos.includes("alquiler") ? api.alquiler.zonas[id] : undefined, api.alquiler.meta);
    tooltip.style.left = `${e.point.x + 12}px`;
    tooltip.style.top = `${e.point.y + 12}px`;
    tooltip.hidden = false;
    mapa.getCanvas().style.cursor = "pointer";
  });
  mapa.on("mouseleave", "zonas-relleno", () => {
    marcarEncima(null);
    tooltip.hidden = true;
    mapa.getCanvas().style.cursor = "";
  });
  mapa.on("click", "zonas-relleno", (e) => {
    if (estado.resultado && !guiado()) elegir(e.features[0].properties.zona_id);
  });

  // Recorrido guiado (#389): el mismo mapa, solo para mirar (fondo, contorno, bordes y nombres), hasta «Ver el mapa».
  const MARCAS = ["zonas-encima-halo", "zonas-encima", "zonas-elegida-halo", "zonas-elegida", "zonas-imprecisas-fondo", "zonas-imprecisas", "zonas-estimadas-fondo", "zonas-estimadas", "zonas-referencia-fondo", "zonas-referencia"];
  const pintarModo = (vista) => {
    $("mapa").setAttribute("aria-label", vista ? "Mapa de la Comunidad de Madrid, solo para mirar" : "Mapa de las zonas coloreadas por la métrica elegida");
    if (!mapa.getLayer("zonas-relleno")) return; // antes de cargar: lo aplica el `load` de abajo
    // Al llegar al mapa final, el color y las marcas se funden juntos mientras entran la barra y la leyenda.
    const fundido = vista || reducido() ? 0 : 700;
    const transicion = { duration: fundido, delay: fundido && 200 };
    for (const [capa, propiedad, opaca] of [["zonas-relleno", "fill-opacity", 0.85], ...MARCAS.map((c) => [c, "line-opacity", 1])]) {
      mapa.setPaintProperty(capa, `${propiedad}-transition`, transicion);
      mapa.setPaintProperty(capa, propiedad, vista ? 0 : opaca);
    }
    // El interior claro, al revés: se ve en la vista previa y se va en el mapa final para no teñir las clases.
    mapa.setPaintProperty("comunidad-interior", "fill-opacity-transition", transicion);
    mapa.setPaintProperty("comunidad-interior", "fill-opacity", vista ? 1 : 0);
  };
  mapa.on("load", () => pintarModo(guiado()));
  alCambiarModo = (vista) => {
    pintarModo(vista);
    marcarEncima(null);
    tooltip.hidden = true;
    // Tras el cambio de disposición: la Comunidad entera en el hueco nuevo; al llegar al mapa final, con vuelo.
    requestAnimationFrame(() => encuadrar(vista || reducido() ? { animate: false } : { duration: 800 }));
  };
  // «Siguiente»: si falla un campo de la tarjeta, se señala el primero y se ofrece su valor de ejemplo.
  tarjetaValida = (menu) => {
    let errores = (validar(valoresFormulario(), api).errores ?? []).filter(({ campo }) => menu.contains(controlDe(campo)));
    recalcular(); // pinta los errores junto a sus campos
    // Una zona de referencia sin alquiler o sin ruta no la rechaza `validar` sino `calcular`, que lo dice en `#estado`.
    if (errores.length === 0 && menu.contains(controlDe("ref")) && $("estado").textContent.startsWith("La zona de referencia")) {
      errores = [{ campo: "ref", mensaje: $("estado").textContent }];
      mostrarErrores(errores);
    }
    if (errores.length === 0) return true;
    for (const { campo } of errores) {
      // El neto vuelve al bruto y una edad de hijo vacía todas (valorDeEjemplo): el botón dice lo que hace.
      const texto = /^neto2?$/.test(campo) ? "Volver al bruto de ejemplo" : /^hijo\d+$/.test(campo) ? "Dejar vacías las edades" : "Usar el valor de ejemplo";
      const boton = elemento("button", texto, "usar-ejemplo");
      boton.type = "button";
      boton.addEventListener("click", () => {
        ir(valorDeEjemplo(campo, valoresFormulario(), api, deEjemplo));
        guardarPaso();
        controlDe(campo).focus();
      });
      $(`error-${campo}`).after(boton);
    }
    const primero = controlDe(errores[0].campo);
    primero.focus({ preventScroll: true });
    primero.scrollIntoView({ block: "center", behavior: reducido() ? "instant" : "smooth" });
    return false;
  };
  recalcular(); // pinta la leyenda por primera vez: el mapa ya tiene su tamaño final
  confirmado = estadoAEnlace(valoresFormulario());
  inicial = confirmado;
  pasoMax = pasoActual(); // al recargar a mitad del historial, lo que hubiera por delante no se conoce
  actualizarBotones();
  encuadrar();
}

/**
 * Menús de la barra de filtros, pestaña del panel lateral, «Mapa completo» y tema del mapa. No tocan el cálculo.
 * Los menús se abren al pasar el ratón o con el foco (CSS) y también al pulsar (`aria-expanded`), para el móvil y el teclado.
 */
function prepararVista(mapa) {
  const botonesMenu = [...document.querySelectorAll(".menu-boton")];
  const cerrarMenus = (salvo) => {
    for (const b of botonesMenu) if (b !== salvo) b.setAttribute("aria-expanded", "false");
  };
  for (const b of botonesMenu) {
    b.addEventListener("click", () => {
      const abrir = b.getAttribute("aria-expanded") !== "true";
      cerrarMenus(b);
      b.setAttribute("aria-expanded", String(abrir));
    });
  }
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".menu")) cerrarMenus(null); // pulsar fuera cierra el desplegable
  });
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    const abierto = botonesMenu.find((b) => b.closest(".menu").contains(document.activeElement));
    cerrarMenus(null);
    // El abierto al pasar el ratón también se cierra: `.sin-hover` lo anula hasta que el ratón sale (WCAG 1.4.13).
    for (const menu of document.querySelectorAll(".menu:hover")) menu.classList.add("sin-hover");
    abierto?.focus(); // el foco vuelve al botón de su menú
  });
  for (const menu of document.querySelectorAll(".menu")) {
    menu.addEventListener("mouseleave", () => menu.classList.remove("sin-hover"));
    // Al salir con Tab, el menú abierto al pulsar se cierra.
    menu.addEventListener("focusout", (e) => {
      // sin `relatedTarget` (pulsar texto o un hueco del panel) no se cierra: pulsar fuera ya lo cierra el `click`
      if (e.relatedTarget && !menu.contains(e.relatedTarget)) menu.querySelector(".menu-boton").setAttribute("aria-expanded", "false");
    });
  }
  // MapLibre ajusta el lienzo con su ResizeObserver; estas llamadas lo hacen también al pulsar y al acabar una transición
  // de la barra. El panel ya no anima su ancho (#434): le basta `ajustar`.
  const ajustar = () => requestAnimationFrame(() => mapa.resize());
  $("barra-filtros").addEventListener("transitionend", (e) => e.target === e.currentTarget && mapa.resize());
  const pestana = $("plegar-panel");
  pestana.addEventListener("click", () => {
    const abierto = pestana.getAttribute("aria-expanded") === "true";
    pestana.setAttribute("aria-expanded", String(!abierto));
    document.body.classList.toggle("panel-plegado", abierto);
    ajustar();
  });
  const completo = $("mapa-completo");
  completo.addEventListener("click", () => {
    const activo = completo.getAttribute("aria-pressed") !== "true";
    completo.setAttribute("aria-pressed", String(activo));
    document.body.classList.toggle("mapa-completo", activo);
    cerrarMenus(null);
    ajustar();
  });
  const boton = $("tema-mapa");
  const ponerTema = (tema) => {
    aplicarTema(mapa, tema);
    boton.setAttribute("aria-pressed", String(tema === "oscuro")); // etiqueta fija: el estado lo dice `aria-pressed`
  };
  ponerTema(temaActual());
  boton.addEventListener("click", () => {
    const tema = boton.getAttribute("aria-pressed") === "true" ? "claro" : "oscuro";
    ponerTema(tema);
    try {
      localStorage.setItem(CLAVE_TEMA, tema);
    } catch {
      // sin almacenamiento: el tema vale hasta recargar
    }
  });
}

// Portada y herramienta, dos vistas de la misma página (#388). La vista no va en el fragmento, que guarda el
// estado del formulario: la herramienta siempre está maquetada (oculta e `inert`), así el mapa nace con su tamaño.
const herramienta = $("herramienta");
const verHerramienta = (visible) => {
  document.body.classList.toggle("en-herramienta", visible);
  herramienta.inert = !visible;
  $("portada").hidden = visible;
  scrollTo({ top: 0, behavior: "instant" });
};
// La vista va en la búsqueda (`?herramienta`), así una recarga o «atrás» respetan la vista en la que estabas.
// Cada cambio de vista es una entrada del historial, y la portada a la que se llega desde el mapa va marcada
// (`portada`): al volver al mapa se retrocede a su entrada, para que no quede una portada entre los pasos de
// «Deshacer» (que también usa el historial).
const vistaDeUrl = () => new URLSearchParams(location.search).has("herramienta");

// --- Recorrido guiado (#389) ---------------------------------------------------------------------
// «Calcular» abre seis tarjetas, una por menú de la barra (`data-tarjeta`), con el mapa a la derecha solo para mirar. Al acabar
// llega el mapa final con lo elegido, porque las tarjetas son los mismos paneles del formulario. No usan el historial: así no
// se cruzan con «Deshacer» (`guardarPaso`, `pasoMax`).
const TARJETAS = 6;
let tarjeta = 0;
let alCambiarModo = () => {}; // `main` los sustituye al crear el mapa y cargar los datos
let tarjetaValida = () => true;
const guiado = () => herramienta.classList.contains("guiado");
const menuDe = (n) => document.querySelector(`.menu[data-tarjeta="${n}"]`);

function verTarjeta(n) {
  tarjeta = n;
  const menu = menuDe(n);
  for (const m of document.querySelectorAll(".menu")) m.classList.toggle("tarjeta-actual", m === menu);
  $("guia-paso").textContent = `Tarjeta ${n} de ${TARJETAS}: `;
  $("guia-nombre").textContent = menu.dataset.titulo;
  $("guia-entradilla").textContent = menu.dataset.entradilla;
  $("guia-contador").textContent = `${n}/${TARJETAS}`;
  $("guia-atras").hidden = n === 1;
  $("guia-siguiente").textContent = n === TARJETAS ? "Ver el mapa" : "Siguiente";
  $("barra-filtros").scrollTop = 0;
  $("guia-titulo").focus();
}

function empezarGuia() {
  herramienta.classList.remove("entrando", "saliendo");
  herramienta.classList.add("guiado");
  alCambiarModo(true);
  verTarjeta(1);
}

function cerrarGuia() {
  herramienta.classList.remove("guiado", "saliendo");
  for (const m of document.querySelectorAll(".tarjeta-actual")) m.classList.remove("tarjeta-actual");
  tarjeta = 0;
  alCambiarModo(false);
}

// Transición al mapa final: sale la tarjeta, cambia la disposición y entran la barra, el panel y la leyenda mientras las zonas se colorean.
function terminarGuia() {
  const llegar = () => {
    cerrarGuia();
    herramienta.classList.add("entrando");
    const animaciones = herramienta.getAnimations({ subtree: true }).map((a) => a.finished);
    Promise.allSettled(animaciones).then(() => herramienta.classList.remove("entrando"));
    $("mejores-titulo").focus();
  };
  if (reducido()) return llegar();
  if (herramienta.classList.contains("saliendo")) return; // doble pulsación
  herramienta.classList.add("saliendo");
  // La animación de salida de la propia tarjeta (no las de dentro): si se cancela porque se cierra el recorrido, no llega.
  const sale = $("guia-tarjeta").getAnimations()[0];
  if (sale) sale.finished.then(llegar, () => {});
  else llegar();
}

$("guia-atras").addEventListener("click", () => verTarjeta(tarjeta - 1));
$("guia-siguiente").addEventListener("click", () => {
  if (!guiado() || !tarjetaValida(menuDe(tarjeta))) return; // fuera del recorrido (doble pulsación al llegar al mapa)
  if (tarjeta < TARJETAS) verTarjeta(tarjeta + 1);
  else terminarGuia();
});
for (const boton of document.querySelectorAll("[data-ir-herramienta]")) {
  boton.addEventListener("click", () => {
    if (history.state?.portada) history.back();
    else if (!vistaDeUrl()) history.pushState(history.state, "", `?herramienta${location.hash}`);
    verHerramienta(true);
    empezarGuia(); // «Calcular» pasa por las tarjetas; el mapa directo es `index.html?herramienta`
  });
}
$("ir-portada").addEventListener("click", (e) => {
  e.preventDefault(); // sin recargar: se conservan el mapa y lo que hayas elegido
  if (guiado()) cerrarGuia(); // como «atrás»: volver a la herramienta por el historial abre el mapa final
  if (vistaDeUrl()) history.pushState({ ...history.state, portada: true }, "", location.pathname + location.hash);
  verHerramienta(false);
  $("titulo-portada").focus(); // Safari no da el foco al enlace pulsado
});
window.addEventListener("popstate", () => {
  const antes = document.body.classList.contains("en-herramienta");
  if (!vistaDeUrl() && guiado()) cerrarGuia(); // «atrás» en mitad del recorrido lleva a la portada; volver por URL abre el mapa
  verHerramienta(vistaDeUrl());
  // Solo al cambiar de vista: el foco no puede quedarse en la que se oculta (y «Deshacer» no debe moverlo).
  if (vistaDeUrl() !== antes) (vistaDeUrl() ? herramienta.querySelector(".menu-boton") : $("titulo-portada")).focus();
});
verHerramienta(vistaDeUrl());

main().catch((error) => {
  $("estado").textContent = `Error: ${error.message}`;
  console.error(error);
});
