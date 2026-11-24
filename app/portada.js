// Plano de la portada: las 199 zonas de datos/zonas.geojson en línea fina. Entran por coronas tarifarias, de Madrid
// hacia fuera, y al pasar el ratón la zona se marca con su nombre y su corona. Solo es una vista: el cálculo está en la
// herramienta. La animación de las cifras de la portada también vive aquí.
const NS = "http://www.w3.org/2000/svg";
const CORONAS = ["A", "B1", "B2", "B3", "C1", "C2"];
const reducido = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

/** Anillos exteriores de cada polígono (los huecos no se ven a esta escala). */
const anillos = (geometria) => (geometria.type === "Polygon" ? [geometria.coordinates[0]] : geometria.coordinates.map((p) => p[0]));

/** Proyección equirectangular con el coseno de la latitud media, en un lienzo de `ancho` unidades. */
function proyeccion(features, ancho) {
  let [x0, y0, x1, y1] = [Infinity, Infinity, -Infinity, -Infinity];
  for (const f of features) for (const anillo of anillos(f.geometry)) for (const [x, y] of anillo) {
    x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y);
  }
  const k = Math.cos((((y0 + y1) / 2) * Math.PI) / 180);
  const escala = ancho / ((x1 - x0) * k);
  return { alto: (y1 - y0) * escala, punto: ([x, y]) => [((x - x0) * k * escala).toFixed(1), ((y1 - y) * escala).toFixed(1)] };
}

/** Las zonas como caminos SVG dentro de `contenedor`. */
function caminos(contenedor, zonas) {
  const { alto, punto } = proyeccion(zonas.features, 1000);
  const svg = document.createElementNS(NS, "svg");
  svg.setAttribute("viewBox", `0 0 1000 ${Math.ceil(alto)}`);
  svg.setAttribute("aria-hidden", "true");
  for (const f of zonas.features) {
    const camino = document.createElementNS(NS, "path");
    camino.setAttribute("d", anillos(f.geometry).map((a) => `M${a.map(punto).join("L")}Z`).join(""));
    camino.classList.add("zona");
    svg.append(camino);
  }
  contenedor.append(svg);
}

/** El plano de la portada: cada zona con su nombre y su corona, y una mira que sigue al ratón. */
function dibujar(figura, zonas) {
  const lienzo = figura.querySelector(".plano-lienzo");
  caminos(lienzo, zonas);
  const svg = lienzo.lastElementChild;
  const grupo = document.createElementNS(NS, "g"); // las zonas en un grupo, para que la mira quede siempre encima
  const zonasSvg = [...svg.querySelectorAll(".zona")]; // en el orden de zonas.features
  grupo.append(...zonasSvg);
  svg.append(grupo);
  zonasSvg.forEach((camino, i) => {
    const { nombre, corona } = zonas.features[i].properties;
    Object.assign(camino.dataset, { nombre, corona });
    // CSSOM (permitido por la CSP): el retraso de entrada crece con la corona
    camino.style.setProperty("--retraso", `${Math.max(0, CORONAS.indexOf(corona)) * 140}ms`);
  });
  const mira = document.createElementNS(NS, "g");
  mira.classList.add("mira");
  for (const [x1, y1, x2, y2] of [[-2000, 0, 2000, 0], [0, -2000, 0, 2000]]) {
    const linea = document.createElementNS(NS, "line");
    Object.entries({ x1, y1, x2, y2 }).forEach(([k, v]) => linea.setAttribute(k, v));
    mira.append(linea);
  }
  svg.append(mira);
  return { svg, mira };
}

function interactuar(figura, { svg, mira }) {
  const rotulo = figura.querySelector(".plano-rotulo");
  const reposo = rotulo.textContent;
  let activa = null;
  const marcar = (e) => {
    const p = new DOMPoint(e.clientX, e.clientY).matrixTransform(svg.getScreenCTM().inverse());
    mira.setAttribute("transform", `translate(${p.x.toFixed(1)} ${p.y.toFixed(1)})`);
    const zona = e.target.closest?.(".zona");
    if (zona === activa) return;
    activa?.classList.remove("activa");
    activa = zona;
    if (!zona) return void (rotulo.textContent = reposo);
    zona.classList.add("activa");
    zona.parentNode.append(zona); // encima de sus vecinas, para que su borde se vea entero
    rotulo.textContent = `${zona.dataset.nombre}, corona ${zona.dataset.corona}`;
  };
  svg.addEventListener("pointermove", marcar);
  svg.addEventListener("pointerdown", marcar); // en una pantalla táctil, tocar una zona la marca
  svg.addEventListener("pointerleave", () => {
    activa?.classList.remove("activa");
    activa = null;
    rotulo.textContent = reposo;
  });
}

/** Las cifras de la portada cuentan desde cero al cargar; el texto del HTML ya trae el valor real. */
function contar() {
  if (reducido()) return;
  for (const cifra of document.querySelectorAll(".cifras-heroe .cifra")) {
    const final = Number(cifra.textContent);
    if (!Number.isInteger(final)) continue;
    const inicio = performance.now();
    const paso = (t) => {
      const avance = Math.min(1, (t - inicio) / 1100);
      cifra.textContent = String(Math.round(final * (1 - (1 - avance) ** 3)));
      if (avance < 1) requestAnimationFrame(paso);
    };
    requestAnimationFrame(paso);
  }
}

const figura = document.getElementById("plano");
if (figura) {
  fetch("datos/zonas.geojson")
    .then((r) => {
      if (!r.ok) throw new Error(`datos/zonas.geojson: ${r.status}`);
      return r.json();
    })
    .then((zonas) => {
      interactuar(figura, dibujar(figura, zonas));
      figura.classList.add("listo");
      const fondo = document.querySelector(".cierre-plano");
      if (fondo) caminos(fondo, zonas); // el mismo plano, de fondo en el cierre
    })
    .catch((error) => {
      figura.hidden = true; // sin plano la portada se lee igual; el error queda en la consola
      console.error(error);
    });
}
contar();
