// Gráficos del informe (#468): cada <figure class="grafico"> lleva un <img> con su SVG. Aquí se inserta el SVG
// en línea (hereda Instrument Sans), sus marcas abren un globo con el ratón, el toque y el teclado (Tab entra en el
// gráfico y las flechas recorren las marcas) y la lista de valores se construye con los mismos textos.
// Sin JS queda la imagen y su texto alternativo.

const globo = document.createElement("div");
globo.className = "globo";
globo.setAttribute("role", "status");
globo.hidden = true;
document.body.append(globo);

function mostrar(marca) {
  const caja = marca.getBoundingClientRect();
  globo.textContent = marca.getAttribute("aria-label");
  globo.hidden = false;
  const ancho = globo.offsetWidth;
  const x = Math.min(Math.max(8, caja.left + caja.width / 2 - ancho / 2), window.innerWidth - ancho - 8);
  globo.style.left = `${x + window.scrollX}px`;
  globo.style.top = `${caja.top + window.scrollY - globo.offsetHeight - 10}px`;
}

function ocultar() {
  globo.hidden = true;
}

function lista(figura, marcas) {
  const detalles = figura.querySelector("details.valores");
  if (!detalles || !marcas.length) return;
  const ul = document.createElement("ul");
  for (const m of marcas) {
    const li = document.createElement("li");
    li.textContent = m.getAttribute("aria-label");
    ul.append(li);
  }
  detalles.append(ul);
}

async function insertar(figura) {
  const img = figura.querySelector("img");
  const respuesta = await fetch(img.getAttribute("src"));
  if (!respuesta.ok) return; // se queda la imagen
  const svg = new DOMParser().parseFromString(await respuesta.text(), "image/svg+xml").documentElement;
  if (svg.nodeName !== "svg") return;
  svg.removeAttribute("width");
  svg.removeAttribute("height");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", img.alt);
  img.replaceWith(svg);
  const marcas = [...svg.querySelectorAll(".marca")];
  lista(figura, marcas);
  if (!marcas.length) return;
  let actual = 0;
  marcas.forEach((m, i) => m.setAttribute("tabindex", i ? "-1" : "0"));
  const ir = (i) => {
    marcas[actual].setAttribute("tabindex", "-1");
    actual = (i + marcas.length) % marcas.length;
    marcas[actual].setAttribute("tabindex", "0");
    marcas[actual].focus();
  };
  svg.addEventListener("keydown", (e) => {
    const paso = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
    if (paso) {
      e.preventDefault();
      ir(actual + paso);
    } else if (e.key === "Escape") ocultar();
  });
  svg.addEventListener("focusin", (e) => {
    const m = e.target.closest(".marca");
    if (m) mostrar(m);
  });
  svg.addEventListener("focusout", ocultar);
  svg.addEventListener("pointerover", (e) => {
    const m = e.target.closest(".marca");
    if (m) mostrar(m);
  });
  svg.addEventListener("pointerleave", ocultar);
  svg.addEventListener("click", (e) => {
    const m = e.target.closest(".marca");
    if (m) ir(marcas.indexOf(m));
  });
}

for (const f of document.querySelectorAll("figure.grafico")) insertar(f);

// En papel no hay clic: el detalle técnico se imprime abierto (?imprimir lo abre para generar el PDF sin diálogo).
const detalles = () => document.querySelectorAll("main details:not(.valores):not([open])");
let abiertos = [];
addEventListener("beforeprint", () => {
  abiertos = [...detalles()];
  abiertos.forEach((d) => (d.open = true));
});
addEventListener("afterprint", () => abiertos.forEach((d) => (d.open = false)));
if (new URLSearchParams(location.search).has("imprimir")) detalles().forEach((d) => (d.open = true));
