// Conecta la página: carga los datos, crea el mapa y pinta. La lógica de color y leyenda está en vista.js.
import { METODO, SIN_DATO, colorear, fuentes, leyenda, licencias } from "./vista.js";

const $ = (id) => document.getElementById(id);

/** Carpeta de datos: `?datos=<ruta>` o `datos/`. Se rechaza otro origen: la página no pide nada a terceros. */
function carpetaDatos() {
  const ruta = new URLSearchParams(location.search).get("datos") ?? "datos/";
  const base = new URL(ruta.endsWith("/") ? ruta : `${ruta}/`, location.href);
  if (base.origin !== location.origin) throw new Error("El parámetro «datos» debe apuntar al mismo sitio");
  return base;
}

async function cargarJSON(base, nombre) {
  const url = new URL(nombre, base);
  const res = await fetch(url);
  if (!res.ok) throw new Error(`No se pudo cargar ${nombre} (${res.status})`);
  return res.json();
}

function pintarLeyenda(cortes, textoFuente, zonas, alquiler) {
  const cont = $("leyenda");
  const titulo = document.createElement("p");
  titulo.className = "titulo";
  const anterior = Object.values(alquiler.zonas).some((z) => z.anio != null && z.anio < alquiler.meta.anio_dato);
  titulo.textContent = `${METODO}. Dato de ${alquiler.meta.anio_dato}${anterior ? " (alguna zona, de un año anterior)" : ""}`;
  cont.replaceChildren(titulo);
  for (const { color, texto } of leyenda(cortes)) {
    const fila = document.createElement("div");
    fila.className = "fila";
    const muestra = document.createElement("span");
    muestra.className = "muestra";
    muestra.style.backgroundColor = color;
    const etiqueta = document.createElement("span");
    etiqueta.textContent = texto;
    fila.append(muestra, etiqueta);
    cont.append(fila);
  }
  const pie = document.createElement("p");
  pie.textContent = `${textoFuente}. Borde discontinuo: valor estimado.`;
  const detalle = document.createElement("details");
  const resumen = document.createElement("summary");
  resumen.textContent = "Nota metodológica y licencias";
  const nota = document.createElement("p");
  nota.textContent = `${alquiler.meta.nota} Licencias: ${licencias(zonas.meta, alquiler.meta)}.`;
  detalle.append(resumen, nota);
  cont.append(pie, detalle);
}

function pintarMapa(zonas) {
  const mapa = new maplibregl.Map({
    container: "mapa",
    // Sin base: ni teselas ni glifos, así que no hay peticiones a terceros.
    style: { version: 8, sources: {}, layers: [{ id: "fondo", type: "background", paint: { "background-color": "#f4f4f4" } }] },
    attributionControl: false,
  });
  const limites = new maplibregl.LngLatBounds();
  for (const f of zonas.features) {
    const c = f.geometry.coordinates.flat(Infinity); // Polygon y MultiPolygon
    for (let i = 0; i < c.length; i += 2) limites.extend([c[i], c[i + 1]]);
  }
  mapa.fitBounds(limites, { padding: 24, animate: false });

  mapa.on("load", () => {
    mapa.addSource("zonas", { type: "geojson", data: zonas, promoteId: "zona_id" });
    mapa.addLayer({ id: "zonas-relleno", type: "fill", source: "zonas", paint: { "fill-color": ["get", "color"] } });
    mapa.addLayer({ id: "zonas-borde", type: "line", source: "zonas", paint: { "line-color": "#444", "line-width": 0.6 } });
    mapa.addLayer({
      id: "zonas-estimadas",
      type: "line",
      source: "zonas",
      filter: ["==", ["get", "estimado"], true],
      paint: { "line-color": "#111", "line-width": 2, "line-dasharray": [2, 2] },
    });
  });

  const tooltip = $("tooltip");
  mapa.on("mousemove", "zonas-relleno", (e) => {
    const { nombre, estimado, color } = e.features[0].properties;
    tooltip.textContent = `${nombre}${estimado ? " · estimado" : ""}${color === SIN_DATO ? " · sin dato" : ""}`;
    tooltip.style.left = `${e.point.x + 12}px`;
    tooltip.style.top = `${e.point.y + 12}px`;
    tooltip.hidden = false;
    mapa.getCanvas().style.cursor = "pointer";
  });
  mapa.on("mouseleave", "zonas-relleno", () => {
    tooltip.hidden = true;
    mapa.getCanvas().style.cursor = "";
  });
}

async function main() {
  const base = carpetaDatos();
  const [zonas, alquiler] = await Promise.all([cargarJSON(base, "zonas.geojson"), cargarJSON(base, "alquiler.json")]);
  const { zonas: pintadas, cortes } = colorear(zonas, alquiler);
  pintarLeyenda(cortes, fuentes(zonas.meta, alquiler.meta), zonas, alquiler);
  pintarMapa(pintadas);
}

main().catch((error) => {
  $("estado").textContent = `Error: ${error.message}`;
  console.error(error);
});
