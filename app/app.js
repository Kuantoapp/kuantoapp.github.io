// Conecta la página: carga los datos, crea el mapa y lo repinta al cambiar el formulario.
// La validación, el color y los textos están en vista.js y el cálculo en calculo.js; aquí solo hay DOM.
// El sueldo no sale del navegador: lo único que se pide por red son los ficheros de `datos/`, del mismo sitio.
import { calcular } from "./calculo.js";
import {
  METRICAS, avisoPrueba, avisos, avisosEntrada, contextoFicha, entradaEscenario, estadoAEnlace, estadoDeEnlace, fuentes, imprecisas, leyenda, licencias, lineaDiferencia,
  lineaTooltip, lineasFicha, mejores, modosDisponibles, pintar, tituloEscenario, validar,
} from "./vista.js";

const $ = (id) => document.getElementById(id);
const formulario = () => $("formulario");
const NOMBRES = ["alquiler", "hogares", "netos", "tarifas", "tiempos"];
const EDAD_POR_DEFECTO = 30; // supuesto: hogares.json no trae edad; decide el Abono Joven (hasta 25 años)

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

function mostrarErrores(errores) {
  for (const el of formulario().querySelectorAll(".error")) el.remove();
  for (const el of formulario().querySelectorAll("[aria-invalid]")) el.removeAttribute("aria-invalid");
  for (const { campo, mensaje } of errores) {
    const control = formulario().elements[campo];
    const destino = control?.nodeType === 1 ? control : (control?.[0] ?? formulario());
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
  const metodo = m.divergente ? "Cuantiles por separado a cada lado del 0" : "Cuantiles";
  // A la vista, lo justo para leer el mapa; lo largo (unidad, fuentes, notas, licencias) va al <details>.
  cont.replaceChildren(elemento("p", `${m.titulo} · ${m.corta} (estimado)${usaAlquiler ? ` · alquiler de ${alquiler.meta.anio_dato}` : ""}`, "titulo"));
  for (const { color, texto } of leyenda(resultadoPintado.clases, resultadoPintado.categorias, metrica)) {
    const fila = elemento("div", "", "fila");
    const muestra = elemento("span", "", "muestra");
    muestra.style.backgroundColor = color;
    fila.append(muestra, elemento("span", texto));
    cont.append(fila);
  }
  cont.append(elemento("p", `${hayImprecisas ? "Borde punteado: pocos alquileres declarados (impreciso). " : ""}${hayEstimadas ? "Borde discontinuo: alquiler estimado. " : ""}Borde grueso: zona de referencia.`));
  const detalle = document.createElement("details");
  const ejemplo = avisoPrueba(metas) !== null; // datos inventados: no se atribuyen a ninguna fuente
  const notas = [
    `${m.titulo}: ${m.unidad}. ${metodo}. ${m.nota}`,
    ...(ejemplo ? [] : [`Color: ${fuentes(...m.datos.map((n) => api[n].meta))}.`, `Zonas y coronas (las coronas fijan la tarifa del transporte): ${fuentes(zonas.meta)}.`]),
    `Alquiler (año y avisos, arriba en el panel): ${alquiler.meta.nota}`,
    `Tiempos: ${tiempos.meta.nota ?? "ver fuentes"} Parte de los tiempos son estimados y el fichero no marca cuáles.`,
    `Hogar y cesta: ${hogares.meta.nota}`,
    `Neto y tarifas (estimado): ${netos.meta.nota ?? "con la normativa de 2026"} ${tarifas.meta.nota ?? ""} ${tarifas.meta.nota_ruta ?? ""}`,
    ...(ejemplo ? [] : [`Licencias: ${licencias(...metas)}.`]),
  ];
  detalle.append(elemento("summary", "Qué mide, fuentes, notas y licencias"), ...notas.map((n) => elemento("p", n)));
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

function crearMapa(zonas) {
  const mapa = new maplibregl.Map({
    container: "mapa",
    // Sin base: ni teselas ni glifos, así que no hay peticiones a terceros. Fondo blanco: el hueco entre zonas
    // (enclave de Torrejón del Rey, fuera de la Comunidad) no se confunde con «sin dato».
    style: { version: 8, sources: {}, layers: [{ id: "fondo", type: "background", paint: { "background-color": "#ffffff" } }] },
    attributionControl: false,
    maxZoom: 13, // los polígonos están simplificados y no casan con un mapa base a nivel de calle
  });
  const limites = limitesDe(zonas.features);
  // En pantalla estrecha la leyenda ocupa parte del contenedor cuando se pinta, después de crear el mapa:
  // hay que recalcular su tamaño y encuadrarlo de nuevo, o se corta por abajo.
  const encuadrar = () => {
    mapa.resize();
    mapa.fitBounds(limites, { padding: 24, animate: false });
  };
  encuadrar();
  let pendiente = null;
  mapa.on("load", () => {
    mapa.addSource("zonas", { type: "geojson", data: pendiente ?? zonas, promoteId: "zona_id" });
    mapa.addLayer({ id: "zonas-relleno", type: "fill", source: "zonas", paint: { "fill-color": ["get", "color"] } });
    mapa.addLayer({ id: "zonas-borde", type: "line", source: "zonas", paint: { "line-color": "#444", "line-width": 0.6 } });
    // Fondo blanco bajo el punteado: sin él no se ve sobre la clase más oscura.
    mapa.addLayer({ id: "zonas-imprecisas-fondo", type: "line", source: "zonas", filter: ["==", ["get", "impreciso"], true], paint: { "line-color": "#fff", "line-width": 3 } });
    mapa.addLayer({ id: "zonas-imprecisas", type: "line", source: "zonas", filter: ["==", ["get", "impreciso"], true], paint: { "line-color": "#111", "line-width": 1.5, "line-dasharray": [1, 1.5] } });
    mapa.addLayer({ id: "zonas-estimadas", type: "line", source: "zonas", filter: ["==", ["get", "estimado"], true], paint: { "line-color": "#111", "line-width": 2, "line-dasharray": [2, 2] } });
    mapa.addLayer({ id: "zonas-referencia", type: "line", source: "zonas", filter: ["==", ["get", "referencia"], true], paint: { "line-color": "#000", "line-width": 3 } });
    pendiente = null;
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
  const api = await cargarApi(CARPETA_DATOS);
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
  // El estado de los formularios viaja en el fragmento de la URL, que no se envía a ningún servidor.
  const enlace = estadoDeEnlace(location.hash.slice(1), valoresFormulario(), api);
  aplicarValores(enlace.valores);
  mostrarSegunda();
  mostrarHijos();
  const { mapa, actualizar, encuadrar } = crearMapa(api.zonas);
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
  };
  function pintarMejores() {
    $("mejores-titulo").textContent = `Las diez mejores zonas: ${METRICAS[estado.metrica].titulo.toLowerCase()} (estimado)`;
    const items = mejores(estado.resultado, estado.metrica, nombres, imprecisas(api.alquiler)).map(({ zona_id, texto }) => {
      const boton = elemento("button", texto);
      boton.type = "button";
      boton.addEventListener("click", () => {
        mapa.fitBounds(limitesDe(api.zonas.features.filter((f) => f.properties.zona_id === zona_id)), { padding: 48, maxZoom: 10 });
        elegir(zona_id);
      });
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
    history.replaceState(null, "", `#${estadoAEnlace(v)}`);
    estado.metrica = v.metrica;
    const algunaZona = Object.values(actual.zonas)[0];
    // Con dos sueldos `zona.neto` es el del hogar: no es el de la primera persona.
    if (v.fuente === "bruto") formulario().elements.neto.value = entrada.sueldos.length === 1 ? String(Math.round(algunaZona.neto)) : "";
    const pintado = pintar(api.zonas, estado.resultado, estado.metrica, imprecisas(api.alquiler));
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

  const tooltip = $("tooltip");
  mapa.on("mousemove", "zonas-relleno", (e) => {
    if (!estado.resultado) return;
    const id = e.features[0].properties.zona_id;
    tooltip.textContent = lineaTooltip(lineas(id), METRICAS[estado.metrica].datos.includes("alquiler") ? api.alquiler.zonas[id] : undefined, api.alquiler.meta);
    tooltip.style.left = `${e.point.x + 12}px`;
    tooltip.style.top = `${e.point.y + 12}px`;
    tooltip.hidden = false;
    mapa.getCanvas().style.cursor = "pointer";
  });
  mapa.on("mouseleave", "zonas-relleno", () => {
    tooltip.hidden = true;
    mapa.getCanvas().style.cursor = "";
  });
  mapa.on("click", "zonas-relleno", (e) => {
    if (estado.resultado) elegir(e.features[0].properties.zona_id);
  });
  recalcular(); // pinta la leyenda por primera vez: el mapa ya tiene su tamaño final
  encuadrar();
}

main().catch((error) => {
  $("estado").textContent = `Error: ${error.message}`;
  console.error(error);
});
