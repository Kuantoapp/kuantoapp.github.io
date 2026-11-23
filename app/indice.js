// Resalta en el índice fijo la sección que estás leyendo (#417). Sin JS el índice sigue funcionando, sin resaltado.

/**
 * Posición de la sección activa: la última cuyo borde superior ya pasó bajo el índice (`linea`), o la última de
 * todas al llegar al final de la página (una sección corta al final nunca sube hasta la línea). -1 antes de la primera.
 */
export function seccionActiva(arribas, linea, alFinal) {
  if (alFinal) return arribas.length - 1;
  return arribas.findLastIndex((arriba) => arriba <= linea);
}

if (typeof document !== "undefined") {
  const indice = document.querySelector(".indice");
  const lista = indice.querySelector("ul");
  const enlaces = [...indice.querySelectorAll("a")];
  const secciones = enlaces.map((a) => document.getElementById(a.hash.slice(1)));
  const suave = matchMedia("(prefers-reduced-motion: no-preference)").matches ? "smooth" : "auto";
  let actual = null;
  let pendiente = false;
  const marcar = () => {
    pendiente = false;
    const alFinal = innerHeight + scrollY >= document.documentElement.scrollHeight - 2;
    // La línea es donde acaba el índice ya pegado (barra + índice), no donde está ahora: arriba aún no se ha pegado.
    const linea = parseFloat(getComputedStyle(indice).top) + indice.offsetHeight + 1;
    const activa = seccionActiva(secciones.map((s) => s.getBoundingClientRect().top), linea, alFinal);
    if (activa === actual) return;
    actual = activa;
    enlaces.forEach((a, i) => (i === activa ? a.setAttribute("aria-current", "true") : a.removeAttribute("aria-current")));
    // En pantalla estrecha el índice se desplaza en horizontal: la entrada activa se trae a la vista.
    if (activa >= 0) lista.scrollTo({ left: enlaces[activa].offsetLeft - lista.offsetLeft - 16, behavior: suave });
  };
  const pedir = () => {
    if (!pendiente) requestAnimationFrame(marcar);
    pendiente = true;
  };
  addEventListener("scroll", pedir, { passive: true });
  addEventListener("resize", pedir);
  marcar();
}
