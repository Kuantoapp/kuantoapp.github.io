// Conecta la página: carga los datos, crea el mapa y lo repinta al cambiar el formulario.
// La validación, el color y los textos están en vista.js y el cálculo en calculo.js; aquí solo hay DOM.
// El sueldo no sale del navegador: lo único que se pide por red son los ficheros de `datos/`, del mismo sitio.
import { calcular } from "./calculo.js";
import { METRICAS, fuentes, leyenda, licencias, lineasFicha, pintar, validar } from "./vista.js";

const $ = (id) => document.getElementById(id);
const formulario = () => $("formulario");
const NOMBRES = ["alquiler", "hogares", "netos", "tarifas", "tiempos"];
const EDAD_POR_DEFECTO = 30; // supuesto: hogares.json no trae edad; decide el Abono Joven (hasta 25 años)

/** Carpeta de datos: `?datos=<ruta>` o `datos/`. Se rechaza otro origen: la página no pide nada a terceros. */
function carpetaDatos() {
  const ruta = new URLSearchParams(location.search).get("datos") ?? "datos/";
  const base = new URL(ruta.endsWith("/") ? ruta : `${ruta}/`, location.href);
  if (base.origin !== location.origin) throw new Error("El parámetro «datos» debe apuntar al mismo sitio");
  return base;
}

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

const valoresFormulario = () => Object.fromEntries(new FormData(formulario()));

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
  for (const d of api.tiempos.destinos.filter((x) => x.tipo === "zona")) {
    const opcion = document.createElement("option");
    opcion.value = d.nombre;
    destinos.append(opcion);
  }
  const metricas = $("metricas");
  for (const [clave, m] of Object.entries(METRICAS)) {
    const etiqueta = document.createElement("label");
    const radio = Object.assign(document.createElement("input"), { type: "radio", name: "metrica", value: clave, checked: clave === "precio_hora" });
    etiqueta.append(radio, m.titulo);
    metricas.append(etiqueta);
  }
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
  const anterior = Object.values(alquiler.zonas).some((z) => z.anio != null && z.anio < alquiler.meta.anio_dato);
  const metodo = m.divergente ? "Cuantiles por separado a cada lado del 0" : "Cuantiles";
  // A la vista, lo justo para leer el mapa; lo largo (unidad, fuentes, notas, licencias) va al <details>.
  cont.replaceChildren(elemento("p", `${m.titulo} · ${m.corta} (estimado)`, "titulo"));
  for (const { color, texto } of leyenda(resultadoPintado.clases, resultadoPintado.categorias, metrica)) {
    const fila = elemento("div", "", "fila");
    const muestra = elemento("span", "", "muestra");
    muestra.style.backgroundColor = color;
    fila.append(muestra, elemento("span", texto));
    cont.append(fila);
  }
  if (hayEstimadas) cont.append(elemento("p", "Borde discontinuo: alquiler estimado."));
  const bordes = `${hayEstimadas ? "Borde discontinuo: alquiler estimado. " : ""}Borde grueso: zona de referencia.`;
  const detalle = document.createElement("details");
  const notas = [
    `${m.titulo}: ${m.unidad}. ${metodo}. ${m.nota}`,
    `${fuentes(...metas)}. ${bordes}`,
    `Alquiler: dato de ${alquiler.meta.anio_dato}${anterior ? " (alguna zona, de un año anterior)" : ""}. ${alquiler.meta.nota}`,
    `Tiempos: ${tiempos.meta.nota ?? "ver fuentes"} Parte de los tiempos son estimados y el fichero no marca cuáles.`,
    `Hogar y cesta: ${hogares.meta.nota}`,
    `Neto y tarifas: ${netos.meta.nota ?? "estimados con la normativa de 2026"} ${tarifas.meta.nota ?? ""}`,
    `Licencias: ${licencias(...metas)}.`,
  ];
  detalle.append(elemento("summary", "Qué mide, fuentes, notas y licencias"), ...notas.map((n) => elemento("p", n)));
  cont.append(detalle);
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
  const limites = new maplibregl.LngLatBounds();
  for (const f of zonas.features) {
    const c = f.geometry.coordinates.flat(Infinity); // Polygon y MultiPolygon
    for (let i = 0; i < c.length; i += 2) limites.extend([c[i], c[i + 1]]);
  }
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
  const api = await cargarApi(carpetaDatos());
  $("fecha-datos").textContent = api.tiempos.meta.generado;
  const maxHijos = Math.max(...api.netos.configuraciones.map((c) => c.hijos));
  $("max-hijos").textContent = `(hasta ${maxHijos} hijos)`;
  prepararFormulario(api);
  const { mapa, actualizar, encuadrar } = crearMapa(api.zonas);
  const estado = { resultado: null, metrica: "precio_hora", zona: null };
  const lineas = (id) => {
    const z = estado.resultado.zonas[id];
    return lineasFicha(api.zonas.features.find((f) => f.properties.zona_id === id).properties.nombre, z, api.alquiler.zonas[id].anio, estado.metrica);
  };
  // La ficha de la zona pinchada se mantiene, actualizada, al cambiar de métrica o de entradas.
  const pintarFicha = () => $("ficha").replaceChildren(...(estado.zona ? lineas(estado.zona).map((t) => elemento("p", t)) : []));

  function recalcular() {
    const v = valoresFormulario();
    const { entrada, errores } = validar(v, api);
    mostrarErrores(errores ?? []);
    if (errores) {
      $("estado").textContent = "Corrige los campos marcados para recalcular el mapa.";
      return;
    }
    try {
      estado.resultado = calcular(api, entrada);
    } catch (error) {
      $("estado").textContent = `No se pudo calcular: ${error.message}`;
      return;
    }
    $("estado").textContent = "";
    estado.metrica = v.metrica;
    const algunaZona = Object.values(estado.resultado.zonas)[0];
    if (v.fuente === "bruto") formulario().elements.neto.value = String(Math.round(algunaZona.neto));
    const pintado = pintar(api.zonas, estado.resultado, estado.metrica);
    actualizar(pintado.zonas);
    pintarLeyenda(api, pintado, estado.metrica);
    pintarFicha();
  }

  formulario().addEventListener("input", (e) => {
    const { name } = e.target;
    if (name === "perfil") rellenarPerfil(api);
    if (name === "bruto" || name === "neto") formulario().elements.fuente.value = name;
    recalcular();
  });
  formulario().addEventListener("submit", (e) => e.preventDefault());

  const tooltip = $("tooltip");
  mapa.on("mousemove", "zonas-relleno", (e) => {
    if (!estado.resultado) return;
    tooltip.textContent = lineas(e.features[0].properties.zona_id).slice(0, 2).join(" · ");
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
    if (!estado.resultado) return;
    estado.zona = e.features[0].properties.zona_id;
    pintarFicha();
  });
  recalcular(); // pinta la leyenda por primera vez: el mapa ya tiene su tamaño final
  encuadrar();
}

main().catch((error) => {
  $("estado").textContent = `Error: ${error.message}`;
  console.error(error);
});
