// Presentación de Kuanto: navegación, pasos, renders animados y modo orador.
// Sin dependencias ni red. Lienzo y exportación según AgentBuff Presentation (MIT);
// el modo orador sigue el método de guizang-ppt-skill (notas, tiempo por bloque), escrito de cero.

// === GUION: lo que dice cada orador, tiempo previsto (s) y avisos ===
const NOTAS = {
  'corto': { s: 35, texto: '', cue: 'El corto se reproduce solo y al acabar pasa a la siguiente. Yeray sale al escenario durante el fundido. Sin vídeo, la pantalla queda en negro: avanza con la flecha.' },
  'ciudad': { s: 5, texto: '«Una ciudad es muchas cosas.» [PAUSA]' },
  'luz': { s: 12, texto: '«Es una luz que se enciende en una ventana.» [→] «Es el trayecto de cada mañana.» [→] «Es el sitio al que vuelves cuando todo lo demás ha terminado.» [PAUSA]' },
  'cuenta': { s: 7, texto: '«Y durante años, vivir en ella se ha convertido en una cuenta que no sale.» [→ fórmula] [PAUSA LARGA]' },
  'cifra': { s: 14, texto: '«En la ciudad de Madrid, el alquiler mediano pesa un 19,6 % de la renta neta de los hogares.» [→] «Y no pesa igual en todas partes: del 12,6 % de Villanueva de la Cañada al 24,0 % de Centro.» [PAUSA]', cue: 'El render: cada columna es una zona; altura y color, lo que pesa el alquiler.' },
  'creemos-1': { s: 4, texto: '«Creemos que nadie debería descubrir demasiado tarde que su casa cuesta más de lo que parecía.»' },
  'creemos-2': { s: 4, texto: '«Creemos que el tiempo que pasas en un tren también es un precio.»' },
  'creemos-3': { s: 4, texto: '«Y creemos que una decisión así merece algo más que un presentimiento.» [PAUSA]' },
  'respuesta': { s: 6, texto: '«Merece una respuesta.» [→ el mapa y el logo] «Esto es Kuanto. Alex.»' },
  'directo': { s: 210, texto: '«Os presento a Lucía. Treinta años, vive sola, gana 24.000 euros brutos y trabaja en Getafe. Todos los portales le dicen cuánto cuesta el alquiler. Kuanto le dice cuánto le sobra.» Demo en directo. Cierre: «176 euros más al mes en Parla, a cambio de catorce horas más de tren. ¿Le compensa? Ahora lo decide sabiendo. Izan.»', cue: 'Pestaña del túnel ya abierta con el estado de Lucía. Recorrido: tarjetas → «Ver el mapa» con «Lo que sobra» → Parla (467 €, 25,9 h) → «Horas de viaje» y «Precio de la hora» → «Otros escenarios»: fin del descuento. Vuelve aquí y avanza.' },
  'capas': { s: 18, texto: '«Hay muchos proyectos que miran el alquiler. Algunos añaden el tiempo. Nosotros hacemos la cuenta entera: siete capas. El neto con el IRPF de 2026, el abono más barato para cada persona, la cesta según ingresos, el hogar y, sobre todo, desde dónde trabajas tú.»' },
  'lucia-mapa': { s: 20, texto: '«Y esto es lo que cambia. La misma Lucía, con el mismo sueldo: en Salamanca le faltan 482 euros al mes. En Villarejo de Salvanés le sobran 703, pero con casi 70 horas de tren al mes. En diez zonas, directamente, no le llega.»', cue: 'Verde hacia arriba: le sobra. Rojo hacia abajo: no le llega. Etiquetas en Getafe, Parla y Centro.' },
  'engana': { s: 14, texto: '«Mirar solo el alquiler engaña. En Chamartín el alquiler es más caro que en Centro, y aun así pesa menos: 16 % frente a 24 %.» [→] «Allí se gana un 78 % más.»' },
  'horas': { s: 12, texto: '«Y el tiempo. Con el sueldo mínimo, irse lejos para pagar menos solo compensa las horas de tren, valoradas a lo que ganas por hora, en una de cada siete combinaciones.»' },
  'bono': { s: 18, texto: '«No es solo un problema de cada persona. 51.735 solicitudes del Bono Alquiler Joven. Se aceptó el 22 %. Y la proporción aceptada no cambia con lo que pesa el alquiler en cada municipio.» [→] «Con el sueldo mínimo, 16 municipios quedan fuera del tope; catorce, por menos de 80 euros.»' },
  'abono': { s: 11, texto: '«Y lo que viene: si todo el descuento del abono termina con 2026, hasta 33 euros más al mes por adulto. A 21 de noviembre no se había publicado ninguna prórroga. Kuanto ya lo calcula, corona a corona.»' },
  'ia': { s: 12, texto: '«¿Y una IA? Lo probamos. ChatGPT y Gemini miraron entre cuatro y seis zonas, erraron el neto y cada uno puso un municipio en la zona de abono equivocada. Kuanto da cifra en 99. Yeray os cuenta cómo.»', cue: 'Cuatro respuestas: ilustra, no mide.' },
  'timeline': { s: 20, texto: '«Lo construimos en quince días. Y empezamos por donde nadie empieza: por las reglas. Antes de analizar un solo dato, ya teníamos las skills de normativa, cartografía y fuentes, siete revisores y una CI que no perdona. Luego los datos, los modelos, el producto, y el 21 y el 23 congelamos los datos. 259 cambios, todos con la CI en verde.»' },
  'tuberia': { s: 16, texto: '«Así funciona por dentro. 89 fuentes oficiales, cada una con su huella. Un motor de trece mil quinientas líneas que aplica la ley y los horarios. Una API estática y congelada. Y de ahí, cinco salidas: la web, un MCP para asistentes de IA, Smart Data Models, DCAT-AP y el informe técnico. Sin servidor.»' },
  'muro': { s: 14, texto: '«Detrás de cada cifra que habéis visto hay todo esto: casi medio millón de alquileres declarados, cuarenta y dos mil trayectos calculados, microdatos de la ECV, 993 tests. Y cero cifras públicas sin fuente.»' },
  'metodos': { s: 16, texto: '«Cada cifra tiene su método y su prueba. El neto, contra ocho casos calculados aparte sobre el BOE. Los tiempos, contra 494 viajes. El alquiler, de contratos, no de anuncios. Horquillas en vez de puntos. Y en el Bono, registro previo y nueve especificaciones publicadas, también las que no salen.»' },
  'maquinas': { s: 14, texto: '«Somos tres personas. Pero hemos construido un equipo: agentes que escriben el código y otros que lo auditan. Doce especialistas, ocho revisores, dieciséis guardias automáticos. Ningún cambio de un área con revisor entra sin su veredicto.»' },
  'privacidad': { s: 11, texto: '«Y en un momento en que nuestros datos valen más que nunca, una promesa sencilla: tu sueldo nunca sale de tu móvil.»' },
  'negocio': { s: 18, texto: '«Un motor, tres mercados. Las personas, gratis, para decidir dónde vivir. La Administración, para medir dónde no llega su política de vivienda. Y empresas e IA, que pueden usar nuestra cifra dentro de sus productos. Coste de servir: cero euros de servidor. Replicable en otra región, con sus propias fuentes.»' },
  'datamad': { s: 6, texto: '«Datos de la Comunidad dentro del cálculo. Viable. Abierto. Con valor social.»' },
  'cierre': { s: 12, texto: '«Empezamos diciendo que una ciudad es muchas cosas. Para demasiada gente, también es una cuenta que no sale.» [PAUSA] «Nadie debería descubrir demasiado tarde cuánto le cuesta su casa.» [→] «Esto es Kuanto. Gracias.»', cue: 'Tecla A: anexo para las preguntas.' },
  'anexo-fuentes': { s: 0, texto: 'Anexo: fuentes por publicador. Esc para volver al cierre.' },
  'anexo-metodo': { s: 0, texto: 'Anexo: método y validación.' },
  'anexo-harness': { s: 0, texto: 'Anexo: cómo trabajan los agentes.' },
};

// === ESTADO ===
const todas = [...document.querySelectorAll('.slide')];
const idDe = (s) => s.dataset.id;
let modo = 'normal'; // normal | anexo
const recorrido = () => todas.filter((s) => (modo === 'normal' ? !s.classList.contains('oculta') : idDe(s).startsWith('anexo')));
let lista = recorrido();
let i = 0, paso = 0, generacion = 0;
const canal = 'BroadcastChannel' in window ? new BroadcastChannel('kuanto-pitch') : null;
const ES_ORADOR = new URLSearchParams(location.search).has('orador');
const ESTATICO = navigator.webdriver && !new URLSearchParams(location.search).has('animado');

// === LIENZO: escala 1920×1080 entero a la ventana ===
function encajar() {
  const s = Math.min(innerWidth / 1920, innerHeight / 1080);
  document.getElementById('escenario').style.transform = `translate(${(innerWidth - 1920 * s) / 2}px,${(innerHeight - 1080 * s) / 2}px) scale(${s})`;
}

// === NAVEGACIÓN ===
const pasosDe = (s) => Number(s.dataset.pasos || 0);
const avisar = () => canal?.postMessage({ tipo: 'estado', id: idDe(lista[i]), paso, i, total: lista.length });
function mostrar(n, p = 0) {
  const antes = lista[i];
  i = Math.max(0, Math.min(lista.length - 1, n));
  paso = p;
  const s = lista[i];
  if (antes && antes !== s) salir(antes);
  todas.forEach((x) => x.classList.toggle('active', x === s));
  aplicarPasos(s);
  if (antes !== s || p === 0) entrar(s);
  history.replaceState(null, '', `#${idDe(s)}`);
  document.getElementById('progreso').style.width = `${((i + 1) / lista.length) * 100}%`;
  pintarNotas();
  avisar();
}
function siguiente() {
  const s = lista[i];
  if (paso < pasosDe(s)) { paso++; aplicarPasos(s); alPaso(s); pintarNotas(); avisar(); return; }
  if (i < lista.length - 1) mostrar(i + 1);
}
function anterior() {
  if (paso > 0) { paso--; aplicarPasos(lista[i]); pintarNotas(); avisar(); return; }
  if (i > 0) mostrar(i - 1, pasosDe(lista[i - 1]));
}
function aplicarPasos(s) { s.querySelectorAll('[data-paso]').forEach((el) => el.classList.toggle('ya', Number(el.dataset.paso) <= paso)); }
function cambiarModo(nuevo, volverA) {
  modo = nuevo;
  lista = recorrido();
  i = 0;
  mostrar(Math.max(0, volverA ? lista.findIndex((s) => idDe(s) === volverA) : 0));
}

// === TECLADO, CLIC Y TÁCTIL ===
addEventListener('keydown', (e) => {
  if (ES_ORADOR) return;
  const k = e.key;
  if (['ArrowRight', 'PageDown', ' ', 'Enter'].includes(k)) { e.preventDefault(); siguiente(); }
  else if (['ArrowLeft', 'PageUp'].includes(k)) { e.preventDefault(); anterior(); }
  else if (k === 'Home') mostrar(0);
  else if (k === 'End') mostrar(lista.length - 1);
  else if (k === 'f' || k === 'F') document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen();
  else if (k === 'n' || k === 'N') document.getElementById('notas').classList.toggle('on');
  else if (k === 'p' || k === 'P') window.open(`${location.pathname}?orador#${idDe(lista[i])}`, 'kuanto-orador', 'width=1200,height=800');
  else if (k === 'a' || k === 'A') modo === 'anexo' ? cambiarModo('normal', 'cierre') : cambiarModo('anexo');
  else if (k === 'Escape' && modo !== 'normal') cambiarModo('normal', 'cierre');
  else if (k === 'l' || k === 'L') document.body.classList.toggle('ligero');
});
addEventListener('click', (e) => { if (!ES_ORADOR && !e.target.closest('a,button,video')) (e.clientX > innerWidth / 3 ? siguiente : anterior)(); });
let toqueX = null;
addEventListener('touchstart', (e) => { toqueX = e.touches[0].clientX; }, { passive: true });
addEventListener('touchend', (e) => { if (toqueX === null) return; const d = e.changedTouches[0].clientX - toqueX; if (Math.abs(d) > 50) (d < 0 ? siguiente : anterior)(); toqueX = null; });
if (canal) canal.onmessage = (m) => {
  if (ES_ORADOR) return window.pintarOrador?.(m.data);
  if (m.data.tipo === 'orden') ({ siguiente, anterior })[m.data.orden]?.();
  if (m.data.tipo === 'hola') avisar();
};

// === NOTAS EN PANTALLA (tecla N) ===
function pintarNotas() {
  const n = NOTAS[idDe(lista[i])] || {};
  document.getElementById('notas').textContent = `${lista[i].dataset.quien} · ${idDe(lista[i])} (${i + 1}/${lista.length}, paso ${paso}/${pasosDe(lista[i])}) — ${n.texto || '—'}${n.cue ? ` · Aviso: ${n.cue}` : ''}`;
}

// === ANIMACIONES POR DIAPOSITIVA ===
const entradas = {
  corto(s) { const v = s.querySelector('video'); v.currentTime = 0; v.play().catch(() => {}); v.onended = () => { if (lista[i] === s) siguiente(); }; },
  cifra() { contar(document.getElementById('contador196'), 19.6, 1, ' %', 2200); iso(document.getElementById('isoEsfuerzo'), RENDER_ESFUERZO); },
  respuesta(s) { s.querySelector('#mereceFrase').style.opacity = 1; limpiar('particulas'); },
  'lucia-mapa'() { iso(document.getElementById('isoLucia'), RENDER_LUCIA); },
};
const pasos = {
  respuesta(s) { s.querySelector('#mereceFrase').style.opacity = 0; particulas(); },
};
function entrar(s) {
  generacion++;
  entradas[idDe(s)]?.(s);
  s.querySelectorAll('[data-cuenta]').forEach((el) => contar(el, Number(el.dataset.cuenta), 0, '', 1800));
  if (paso) alPaso(s);
}
function alPaso(s) { pasos[idDe(s)]?.(s); }
function salir(s) { if (idDe(s) === 'corto') s.querySelector('video').pause(); }

function contar(el, fin, dec, sufijo, ms) {
  const g = generacion, t0 = performance.now();
  (function f(t) {
    if (g !== generacion) return;
    const k = Math.min(1, (t - t0) / ms), v = fin * (1 - Math.pow(1 - k, 4));
    el.textContent = v.toLocaleString('es-ES', { minimumFractionDigits: dec, maximumFractionDigits: dec }) + sufijo;
    if (k < 1) requestAnimationFrame(f);
  })(t0);
}

// === RENDER ISOMÉTRICO: el mapa de zonas con una columna por zona y una órbita lenta de cámara ===
const POLIGONOS = window.MAPA.zonas.map((z) => z.d.split('Z').filter(Boolean).map((p) => p.replace('M', '').split('L').map((q) => q.split(',').map(Number))));
const mezcla = (a, b, k) => a.map((v, j) => Math.round(v + (b[j] - v) * k));
const RENDER_ESFUERZO = {
  valor: (z) => z.e,
  altura: (v) => v * 1100, // proporcional desde cero
  color: (v) => { const k = Math.min(1, Math.max(0, (v - 0.12) / 0.12)); return k < 0.5 ? mezcla([47, 124, 246], [156, 194, 245], k * 2) : mezcla([156, 194, 245], [255, 107, 107], (k - 0.5) * 2); },
  etiquetas: { '2807901': ['Centro', 120, 120], '28176': ['Villanueva de la Cañada', 140, -190] },
};
const RENDER_LUCIA = {
  valor: (z) => z.s,
  altura: (v) => v * 0.22,
  color: (v) => (v >= 0 ? [61, 220, 151] : [255, 107, 107]),
  etiquetas: { '28065': ['Getafe', 120, 190], '28106': ['Parla', 70, -170], '2807901': ['Centro', 230, -60] },
};
function iso(canvas, cfg) {
  const ctx = canvas.getContext('2d'), W = canvas.width, H = canvas.height, g = generacion;
  const zonas = window.MAPA.zonas, t0 = performance.now();
  const barras = zonas.map((z) => ({ z, v: cfg.valor(z) })).filter((b) => b.v !== null);
  const proy = (x, y, h, th) => {
    const dx = x - 450, dy = y - 450, c = Math.cos(th), s = Math.sin(th);
    return [W / 2 + (dx * c - dy * s) * 1.2, H * 0.52 + (dx * s + dy * c) * 0.62 - h];
  };
  const pintar = (crece, th) => {
    ctx.clearRect(0, 0, W, H);
    POLIGONOS.forEach((polys, k) => {
      ctx.beginPath();
      for (const p of polys) p.forEach(([x, y], j) => { const [X, Y] = proy(x, y, 0, th); if (j) ctx.lineTo(X, Y); else ctx.moveTo(X, Y); });
      ctx.fillStyle = cfg.valor(zonas[k]) === null ? 'rgba(255,255,255,0.025)' : 'rgba(47,124,246,0.08)';
      ctx.strokeStyle = 'rgba(156,194,245,0.22)';
      ctx.lineWidth = 0.8;
      ctx.fill(); ctx.stroke();
    });
    const rotulos = [];
    // Las que no llegan (negativas) se pintan al final para que no las tapen las demás.
    const orden = barras.map((b) => ({ ...b, p: proy(b.z.c[0], b.z.c[1], 0, th) })).sort((a, b) => (a.v < 0) - (b.v < 0) || a.p[1] - b.p[1]);
    for (const b of orden) {
      const k = Math.min(1, Math.max(0, crece * 1.6 - Math.hypot(b.z.c[0] - 450, b.z.c[1] - 450) / 900));
      const h = cfg.altura(b.v) * (1 - Math.pow(1 - k, 3));
      const [r, gg, bl] = cfg.color(b.v), w = b.v < 0 ? 7 : 5;
      const esq = [[-w, -w], [w, -w], [w, w], [-w, w]].map(([a, c]) => [b.z.c[0] + a, b.z.c[1] + c]);
      const base = esq.map(([x, y]) => proy(x, y, 0, th)), techo = esq.map(([x, y]) => proy(x, y, h, th));
      const caras = [0, 1, 2, 3].map((j) => ({ j, y: (base[j][1] + base[(j + 1) % 4][1]) / 2 })).sort((a, c) => a.y - c.y);
      for (const { j } of caras) {
        const n = (j + 1) % 4, luz = j % 2 ? 0.55 : 0.75;
        ctx.beginPath(); ctx.moveTo(...base[j]); ctx.lineTo(...base[n]); ctx.lineTo(...techo[n]); ctx.lineTo(...techo[j]); ctx.closePath();
        ctx.fillStyle = `rgba(${Math.round(r * luz)},${Math.round(gg * luz)},${Math.round(bl * luz)},0.95)`; ctx.fill();
      }
      ctx.beginPath(); techo.forEach((q, j) => (j ? ctx.lineTo(...q) : ctx.moveTo(...q))); ctx.closePath();
      ctx.fillStyle = `rgb(${r},${gg},${bl})`; ctx.shadowColor = `rgba(${r},${gg},${bl},0.8)`; ctx.shadowBlur = 12; ctx.fill(); ctx.shadowBlur = 0;
      if (cfg.etiquetas[b.z.id] && k > 0.9) rotulos.push([cfg.etiquetas[b.z.id], proy(b.z.c[0], b.z.c[1], Math.max(h, 0), th)]);
    }
    for (const [[texto, alto, dx], [X, Y]] of rotulos) {
      ctx.strokeStyle = 'rgba(245,245,247,0.7)'; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.moveTo(X, Y - 6); ctx.lineTo(X + dx, Y - alto); ctx.stroke();
      ctx.font = '600 28px "Instrument Sans", sans-serif'; ctx.textAlign = 'center';
      const ancho = ctx.measureText(texto).width + 28;
      ctx.fillStyle = 'rgba(0,0,0,0.85)'; ctx.fillRect(X + dx - ancho / 2, Y - alto - 44, ancho, 42);
      ctx.fillStyle = '#f5f5f7'; ctx.fillText(texto, X + dx, Y - alto - 13);
    }
  };
  if (ESTATICO) { pintar(1, -0.35); return; }
  (function f(t) {
    if (g !== generacion) return;
    const seg = (t - t0) / 1000;
    pintar(Math.min(1, seg / 2.4), -0.35 + 0.22 * Math.sin(seg * 0.22));
    if (!document.body.classList.contains('ligero') || seg < 3) requestAnimationFrame(f);
  })(t0);
}

// === PARTÍCULAS QUE FORMAN LA COMUNIDAD ===
function limpiar(id) { const c = document.getElementById(id); c.getContext('2d').clearRect(0, 0, c.width, c.height); }
function particulas() {
  const c = document.getElementById('particulas'), ctx = c.getContext('2d'), g = generacion;
  const P = window.MAPA.puntos.map(([x, y]) => ({ x: 960 + (Math.random() - 0.5) * 2400, y: 540 + (Math.random() - 0.5) * 1400, tx: 510 + x, ty: 90 + y, d: Math.random() * 700 }));
  const t0 = performance.now();
  (function f(t) {
    if (g !== generacion) return;
    ctx.clearRect(0, 0, 1920, 1080);
    ctx.fillStyle = '#9cc2f5';
    const fin = (t - t0) / 1000;
    for (const p of P) {
      const k = Math.min(1, Math.max(0, (t - t0 - p.d) / 1600)), e = 1 - Math.pow(1 - k, 4);
      ctx.globalAlpha = (0.15 + 0.6 * e) * (fin > 2.2 ? Math.max(0.2, 1 - (fin - 2.2) * 0.8) : 1);
      ctx.beginPath(); ctx.arc(p.x + (p.tx - p.x) * e, p.y + (p.ty - p.y) * e, 2.4, 0, 7); ctx.fill();
    }
    if (fin < 4) requestAnimationFrame(f);
  })(t0);
}

// === TIMELINE: días, PR fusionados por día (gh pr list) y fases según los PR y docs/decisiones.md ===
const PR_DIA = [5, 7, 20, 24, 23, 28, 10, 19, 20, 31, 9, 10, 18, 19, 16];
const FASES = [
  { ini: 11, fin: 13, fila: 0, t: 'Las reglas', s: 'skills, revisores, hooks y CI antes que los datos', c: '#9cc2f5' },
  { ini: 14, fin: 15, fila: 1, t: 'Los datos', s: 'fuentes con huella; neto, tarifas y tiempos', c: '#2f7cf6' },
  { ini: 16, fin: 19, fila: 0, t: 'Los modelos', s: 'esfuerzo, Bono (GLM y SEM), imputación espacial, MCP', c: '#3ddc97' },
  { ini: 17, fin: 23, fila: 1, t: 'El producto', s: 'cálculo en el navegador, escenarios y seis tarjetas', c: '#ffd27a' },
  { ini: 21, fin: 23, fila: 0, t: 'Datos congelados', s: 'zonas y tiempos el 21; euros y análisis el 23', c: '#bfad95' },
  { ini: 24, fin: 25, fila: 1, t: 'El informe', s: 'técnico, estilo consultora, en web y PDF', c: '#ff9b6b' },
  { ini: 26, fin: 26, fila: 0, t: 'Jurado', s: 'hoy', c: '#f5f5f7' },
];
const HITOS = [13, 15, 17, 19, 21, 23, 25, 26];
function construirTimeline() {
  const caja = document.getElementById('lineaTiempo');
  if (caja.querySelector('.fase')) return;
  const x = (d) => ((d - 11) / 15) * 1600, retardo = (d) => `${0.4 + ((d - 11) / 15) * 3.2}s`;
  const dias = document.getElementById('dias'), prs = document.getElementById('prs');
  for (let d = 11; d <= 26; d++) {
    const s = document.createElement('span');
    s.style.left = `${x(d)}px`;
    s.textContent = d === 11 ? '11 nov' : d === 26 ? '26 nov' : String(d);
    dias.appendChild(s);
  }
  PR_DIA.forEach((n, k) => {
    const b = document.createElement('i');
    b.dataset.n = n;
    b.style.left = `${x(11 + k)}px`;
    b.style.setProperty('--h', `${(n / 31) * 150}px`);
    b.style.setProperty('--d', retardo(11 + k));
    prs.appendChild(b);
  });
  for (const f of FASES) {
    const final = f.ini === 26, el = document.createElement('div');
    el.className = 'fase';
    Object.assign(el.style, { left: `${final ? x(26) - 160 : x(f.ini)}px`, top: `${f.fila ? 250 : 40}px`, width: `${final ? 160 : 300}px`, textAlign: final ? 'right' : 'left' });
    el.style.setProperty('--d', retardo(f.ini));
    el.style.setProperty('--c', f.c);
    const banda = document.createElement('div');
    banda.className = 'banda';
    banda.style.width = `${Math.max(18, x(f.fin) - x(f.ini))}px`;
    if (final) banda.style.marginLeft = 'auto';
    const t = document.createElement('b'); t.textContent = f.t;
    const s = document.createElement('span'); s.textContent = f.s;
    el.append(banda, t, s);
    caja.appendChild(el);
  }
  for (const d of HITOS) {
    const h = document.createElement('div');
    h.className = 'hito';
    h.style.left = `${x(d)}px`;
    h.style.setProperty('--d', retardo(d));
    caja.appendChild(h);
  }
}

// === ARQUITECTURA: conectores con datos que fluyen ===
function construirTuberia() {
  const svg = document.getElementById('tuberiaSvg');
  if (svg.childElementCount) return;
  const ns = 'http://www.w3.org/2000/svg';
  const rutas = [[280, 320, 340, 320], [620, 320, 680, 320], [960, 320, 1020, 320], ...[0, 132, 264, 396, 528].map((y) => [1300, 320, 1360, y + 50])];
  rutas.forEach(([x1, y1, x2, y2], k) => {
    const d = `M${x1},${y1} C${(x1 + x2) / 2},${y1} ${(x1 + x2) / 2},${y2} ${x2},${y2}`;
    const p = document.createElementNS(ns, 'path');
    p.setAttribute('d', d); p.setAttribute('class', 'conector');
    svg.appendChild(p);
    for (let j = 0; j < 3; j++) {
      const c = document.createElementNS(ns, 'circle');
      c.setAttribute('r', '5'); c.setAttribute('class', 'gota');
      const m = document.createElementNS(ns, 'animateMotion');
      m.setAttribute('dur', '1.8s'); m.setAttribute('repeatCount', 'indefinite'); m.setAttribute('path', d);
      m.setAttribute('begin', `${(k * 0.25 + j * 0.6).toFixed(2)}s`);
      c.appendChild(m);
      svg.appendChild(c);
    }
  });
}

// === SALA DE MÁQUINAS: el bucle de cada cambio ===
const BUCLE = ['Issue', 'Worktree', 'Skill del área', 'Hooks y tests', 'Commit', 'Revisor', 'Pull request', 'CI y merge'];
function construirBucle() {
  const svg = document.getElementById('bucle');
  if (svg.childElementCount) return;
  const cx = 410, cy = 360, r = 250, ns = 'http://www.w3.org/2000/svg';
  for (const [cls, largo] of [['arco', ''], ['vivo', '2000']]) {
    const c = document.createElementNS(ns, 'circle');
    c.setAttribute('class', cls); c.setAttribute('cx', cx); c.setAttribute('cy', cy); c.setAttribute('r', r);
    if (largo) c.setAttribute('pathLength', largo);
    svg.appendChild(c);
  }
  BUCLE.forEach((t, k) => {
    const a = -Math.PI / 2 + (k / BUCLE.length) * 2 * Math.PI, x = cx + r * Math.cos(a), y = cy + r * Math.sin(a), c = Math.cos(a);
    const gr = document.createElementNS(ns, 'g'); gr.setAttribute('class', 'paso');
    const p = document.createElementNS(ns, 'circle'); p.setAttribute('cx', x); p.setAttribute('cy', y); p.setAttribute('r', 16);
    const tx = document.createElementNS(ns, 'text');
    tx.setAttribute('x', x + c * 30); tx.setAttribute('y', y + Math.sin(a) * 34 + 8);
    tx.style.textAnchor = c > 0.3 ? 'start' : c < -0.3 ? 'end' : 'middle';
    tx.textContent = t;
    gr.append(p, tx);
    svg.appendChild(gr);
  });
  const t1 = document.createElementNS(ns, 'text');
  t1.setAttribute('x', cx); t1.setAttribute('y', cy); t1.style.cssText = 'fill:#f5f5f7;font:600 44px "Instrument Sans";text-anchor:middle';
  t1.textContent = 'Un cambio';
  const t2 = document.createElementNS(ns, 'text');
  t2.setAttribute('x', cx); t2.setAttribute('y', cy + 44); t2.style.cssText = 'fill:#a3aab6;font:400 24px "Instrument Sans";text-anchor:middle';
  t2.textContent = 'de la idea al merge';
  svg.append(t1, t2);
}

// === MODO ORADOR (tecla P): ventana aparte con guion, siguiente y relojes por bloque ===
function iniciarOrador() {
  document.querySelector('.deck-viewport').style.display = 'none';
  document.getElementById('progreso').style.display = 'none';
  const plan = {};
  todas.filter((s) => !s.classList.contains('oculta')).forEach((s) => { const q = s.dataset.quien; plan[q] = (plan[q] || 0) + (NOTAS[idDe(s)]?.s || 0); });
  document.body.style.cssText = 'overflow:auto;background:#000;color:#f5f5f7;font:400 22px/1.5 "Instrument Sans",sans-serif;padding:28px 40px';
  const crear = (css) => { const d = document.createElement('div'); d.style.cssText = css; document.body.appendChild(d); return d; };
  const total = crear('font:600 64px "Instrument Sans"');
  const bloque = crear('font:600 28px "Instrument Sans";margin:14px 0 4px');
  const tit = crear('font:600 36px "Instrument Sans";margin:6px 0;color:#9cc2f5');
  const texto = crear('font:400 34px/1.45 "Instrument Sans";max-width:1500px;margin:12px 0');
  const cue = crear('color:#ffd27a;font-size:24px;margin:10px 0');
  const sig = crear('color:#a3aab6;font-size:24px;margin-top:22px;border-top:1px solid #23272f;padding-top:14px');
  crear('color:#6e7480;font-size:18px;margin-top:20px').textContent = 'Flechas: avanzar y retroceder en la presentación · R: reiniciar relojes';
  let t0 = Date.now(), quien = null, tb = Date.now(), previsto = 0;
  const mmss = (s) => `${s < 0 ? '−' : ''}${Math.floor(Math.abs(s) / 60)}:${String(Math.floor(Math.abs(s)) % 60).padStart(2, '0')}`;
  window.pintarOrador = (d) => {
    if (d.tipo !== 'estado') return;
    const s = todas.find((x) => idDe(x) === d.id), q = s.dataset.quien, n = NOTAS[d.id] || {};
    if (q !== quien) { quien = q; tb = Date.now(); }
    previsto = plan[q] || 0;
    const siguienteS = todas.slice(todas.indexOf(s) + 1).find((x) => !x.classList.contains('oculta'));
    tit.textContent = `${d.i + 1}/${d.total} · ${d.id}${pasosDe(s) ? ` · paso ${d.paso}/${pasosDe(s)}` : ''}`;
    texto.textContent = n.texto || '—';
    cue.textContent = n.cue || '';
    sig.textContent = siguienteS ? `Siguiente: ${siguienteS.dataset.id} (${siguienteS.dataset.quien})` : 'Fin';
  };
  setInterval(() => {
    total.textContent = `${mmss((Date.now() - t0) / 1000)} de 9:00`;
    if (!quien) return;
    const pasado = (Date.now() - tb) / 1000, resta = previsto - pasado;
    bloque.textContent = `${quien}: ${mmss(pasado)} de ${mmss(previsto)} · ${resta >= 0 ? `quedan ${mmss(resta)}` : `te pasas ${mmss(-resta)}`}`;
    bloque.style.color = resta < 0 ? '#ff6b6b' : resta < 15 ? '#ffd27a' : '#3ddc97';
  }, 250);
  addEventListener('keydown', (e) => {
    if (['ArrowRight', 'PageDown', ' '].includes(e.key)) canal?.postMessage({ tipo: 'orden', orden: 'siguiente' });
    if (['ArrowLeft', 'PageUp'].includes(e.key)) canal?.postMessage({ tipo: 'orden', orden: 'anterior' });
    if (e.key === 'r' || e.key === 'R') { t0 = Date.now(); tb = Date.now(); }
  });
  canal?.postMessage({ tipo: 'hola' });
}

// === ARRANQUE ===
// Se construyen antes de mostrarse para que sus transiciones se vean al entrar.
construirTimeline(); construirTuberia(); construirBucle();
if (ESTATICO) {
  // La exportación (navegador automatizado) recibe el estado final de cada diapositiva; ?animado lo evita.
  document.body.classList.add('estatico');
  iso(document.getElementById('isoEsfuerzo'), RENDER_ESFUERZO);
  iso(document.getElementById('isoLucia'), RENDER_LUCIA);
}
if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
  document.body.classList.add('ligero');
  document.querySelectorAll('svg').forEach((s) => s.pauseAnimations());
}
if (ES_ORADOR) iniciarOrador();
else {
  addEventListener('resize', encajar);
  encajar();
  const desdeUrl = location.hash.slice(1);
  if (desdeUrl.startsWith('anexo')) { modo = 'anexo'; lista = recorrido(); }
  const k = lista.findIndex((s) => idDe(s) === desdeUrl);
  document.fonts.ready.then(() => mostrar(k >= 0 ? k : 0));
}
