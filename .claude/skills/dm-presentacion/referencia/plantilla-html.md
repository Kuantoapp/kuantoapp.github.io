# Plantilla de presentación en HTML

Contenido: cuándo usarla · esqueleto · cómo se usa · exportar a PDF.

Un solo fichero, sin dependencias ni red: lienzo de 1920 × 1080 escalado a la pantalla, flechas o espacio para avanzar, `N` para ver las notas al ensayar (no hay vista de presentador: con el proyector en espejo el jurado las vería, así que el día del pitch el guion va en papel o en el móvil), `F` para pantalla completa e impresión a PDF con una diapositiva por página. Se guarda en `docs/pitch/`. No enlaza `app/estilo.css`, que trae reglas de la app: copia en el bloque `:root` los valores de color y familia de la app (sus variables de `:root` si las tiene; si no, los literales que usa) para que las dos se vean igual.

## Cuándo usarla

Cuando quien presenta elige HTML o no tiene preferencia. Si elige otra herramienta, las reglas de la skill valen igual y esta plantilla no se usa.

## Esqueleto

```html
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nombre del proyecto en DataMad 2026</title>
<style>
  /* Colores y familia: los de la app, copiados aquí. */
  :root { /* sin-fuente: estilos */
    --fondo: #ffffff; --texto: #222222; --texto-2: #555555; --acento: #0b4f9c;
    --familia: system-ui, sans-serif;
    --lienzo-w: 1920px; --lienzo-h: 1080px; --margen: 120px;
  }
  html, body { /* sin-fuente: estilos */ margin: 0; height: 100%; overflow: clip; background: var(--fondo); color: var(--texto); font-family: var(--familia); }
  .diapo {
    position: absolute; left: 50%; top: 50%; /* sin-fuente: estilos */
    width: var(--lienzo-w); height: var(--lienzo-h);
    box-sizing: border-box; padding: var(--margen);
    display: none; grid-template-rows: auto minmax(0, 1fr) auto; gap: 48px; /* sin-fuente: estilos */
    font-size: 32px; line-height: 1.35;
  }
  .diapo.actual { display: grid; }
  .diapo h2 { margin: 0; font-size: 64px; line-height: 1.1; font-weight: 500; text-wrap: balance; max-width: 22ch; } /* sin-fuente: estilos */
  .diapo .cifra { font-size: 160px; line-height: 1; font-weight: 500; font-variant-numeric: tabular-nums; color: var(--acento); } /* sin-fuente: estilos */
  .diapo img { max-width: 100%; max-height: 100%; object-fit: contain; min-height: 0; } /* sin-fuente: estilos */
  .diapo .pie { font-size: 22px; color: var(--texto-2); }
  .notas { display: none; }
  body.ver-notas .diapo.actual .notas { display: block; position: absolute; inset: auto 0 0 0; font-size: 24px; padding: 24px; background: var(--fondo); border-top: 1px solid var(--texto-2); }
  @media print {
    @page { size: 1920px 1080px; margin: 0; }
    html, body { height: auto; overflow: visible; display: block; }
    .diapo { display: grid; position: relative; left: auto; top: auto; transform: none !important; break-after: page; }
    .notas { display: none !important; }
  }
</style>
</head>
<body>

<section class="diapo">
  <h2>Titular que es la conclusión de la diapositiva</h2>
  <div class="cifra">00 %</div> <!-- sin-fuente: hueco de la plantilla -->
  <p class="pie">Fuente: publicador, conjunto y fecha (estimado, si lo es)</p>
  <aside class="notas">Lo que dice quien presenta.</aside>
</section>

<section class="diapo">
  <h2>La herramienta responde en segundos</h2>
  <img src="capturas/app-390.png" alt="Captura de la app con el resultado para una zona">
  <p class="pie">Captura de la app el AAAA-MM-DD</p>
</section>

<script>
  const diapos = [...document.querySelectorAll('.diapo')];
  let i = Math.max(0, Math.min(diapos.length - 1, Number(location.hash.slice(1)) - 1 || 0));
  const escalar = () => {
    const e = Math.min(innerWidth / 1920, innerHeight / 1080);
    diapos.forEach(d => { d.style.transform = `translate(-50%, -50%) scale(${e})`; });
  };
  const ir = n => {
    i = Math.max(0, Math.min(diapos.length - 1, n));
    diapos.forEach((d, k) => d.classList.toggle('actual', k === i));
    history.replaceState(null, '', `#${i + 1}`);
  };
  addEventListener('keydown', ev => {
    if (['ArrowRight', 'PageDown', ' '].includes(ev.key)) ir(i + 1);
    else if (['ArrowLeft', 'PageUp'].includes(ev.key)) ir(i - 1);
    else if (ev.key === 'Home') ir(0);
    else if (ev.key === 'End') ir(diapos.length - 1);
    else if (ev.key.toLowerCase() === 'n') document.body.classList.toggle('ver-notas');
    else if (ev.key.toLowerCase() === 'f') document.documentElement.requestFullscreen?.();
  });
  addEventListener('click', ev => ir(ev.clientX > innerWidth / 2 ? i + 1 : i - 1));
  addEventListener('resize', escalar);
  escalar();
  ir(i);
</script>
</body>
</html>
```

## Cómo se usa

- Una `section.diapo` por diapositiva, con un `h2` que es la conclusión, una sola visual y su `p.pie` con la fuente. Las cifras reales llevan su fuente en la misma diapositiva, como exige `cifras_con_fuente.py`. El `00 %` del ejemplo es un hueco: su `sin-fuente` se quita al poner la cifra. Las líneas de CSS con números llevan `/* sin-fuente: estilos */`, como `app/informe.html`.
- Las capturas van en `docs/pitch/capturas/`, hechas con la app servida en local, con su fecha en el pie.
- Los colores y la familia son los de la app: si la app cambia, se copian otra vez. Ningún color literal fuera del bloque `:root`.
- `#3` en la URL abre la tercera diapositiva: útil para retomar tras un fallo.

## Exportar a PDF

Abre el fichero en Chrome o Edge, Imprimir → Guardar como PDF, márgenes «Ninguno» y gráficos de fondo activados. Comprueba que hay una página por diapositiva y que las fuentes no se sustituyeron. El PDF es el plan B si el proyector no abre el HTML.
