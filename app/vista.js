// Lógica del mapa sin DOM ni MapLibre: escala de color, cortes y leyenda. app.js solo la conecta.

// Viridis (secuencial, apta para daltónicos). El rojo se reserva para alertas.
export const PALETA = ["#440154", "#3b528b", "#21918c", "#5ec962", "#fde725"];
export const SIN_DATO = "#bdbdbd";
export const METODO = "Cuantiles · mediana (p50) en €/m² al mes";

const formato = new Intl.NumberFormat("es-ES", { minimumFractionDigits: 1, maximumFractionDigits: 1 });

const esNumero = (v) => typeof v === "number" && Number.isFinite(v);

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

function colorDeClase(clase, total) {
  return PALETA[total <= 1 ? 0 : Math.round((clase * (PALETA.length - 1)) / (total - 1))];
}

/** Gris si no hay dato; si no, el color de su clase (borde inferior incluido, superior excluido salvo el último). */
export function colorPara(valor, cortes) {
  if (!esNumero(valor) || cortes.length === 0) return SIN_DATO;
  const total = Math.max(cortes.length - 1, 1);
  const clase = cortes.slice(1, -1).filter((borde) => borde <= valor).length;
  return colorDeClase(clase, total);
}

/** Pone `color`, `p50` y `estimado` en cada zona. Una zona ausente de alquiler cuenta como sin dato. */
export function colorear(zonas, alquiler) {
  if (!Array.isArray(zonas?.features) || typeof alquiler?.zonas !== "object" || alquiler.zonas === null) {
    throw new Error("Formato inesperado: faltan zonas.features o alquiler.zonas");
  }
  const p50 = (f) => {
    const valor = alquiler.zonas[f.properties.zona_id]?.p50;
    return esNumero(valor) ? valor : null;
  };
  const cortes = cortesCuantiles(zonas.features.map(p50));
  const features = zonas.features.map((f) => {
    const valor = p50(f);
    const origen = alquiler.zonas[f.properties.zona_id]?.origen;
    return {
      ...f,
      properties: { ...f.properties, p50: valor, estimado: origen === "estimado", color: colorPara(valor, cortes) },
    };
  });
  return { zonas: { ...zonas, features }, cortes };
}

/** Entradas de la leyenda: una por clase [a, b) (la última cerrada) y «Sin dato». */
export function leyenda(cortes) {
  if (cortes.length === 1) return [{ color: PALETA[0], texto: formato.format(cortes[0]) }, { color: SIN_DATO, texto: "Sin dato" }];
  const total = cortes.length - 1;
  const clases = Array.from({ length: Math.max(total, 0) }, (_, i) => ({
    color: colorDeClase(i, total),
    texto: `${formato.format(cortes[i])} – ${formato.format(cortes[i + 1])}`,
  }));
  return [...clases, { color: SIN_DATO, texto: "Sin dato" }];
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
