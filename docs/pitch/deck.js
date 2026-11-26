// Presentación de Kuanto: navegación, pasos, animaciones por diapositiva y modo orador.
// Sin dependencias ni red. Lienzo y exportación según AgentBuff Presentation (MIT);
// el modo orador sigue el método de guizang-ppt-skill (notas, tiempo por bloque), escrito de cero.

// === GUION: lo que dice cada orador, tiempo previsto (s) y avisos ===
const NOTAS = {
  'corto': { s: 35, texto: '', cue: 'El corto se reproduce solo y al acabar pasa a la siguiente. Yeray sale al escenario durante el fundido a negro. Si no hay vídeo, la pantalla queda en negro: avanza con la flecha.' },
  'ciudad': { s: 5, texto: '«Una ciudad es muchas cosas.» [PAUSA]' },
  'luz': { s: 12, texto: '«Es una luz que se enciende en una ventana.» [→] «Es el trayecto de cada mañana.» [→] «Es el sitio al que vuelves cuando todo lo demás ha terminado.» [PAUSA]' },
  'cuenta': { s: 7, texto: '«Y durante años, vivir en ella se ha convertido en una cuenta que no sale.» [→ aparece la fórmula] [PAUSA LARGA]' },
  'cifra': { s: 14, texto: '«En la ciudad de Madrid, el alquiler mediano pesa un 19,6 % de la renta neta de los hogares.» [→] «Y no pesa igual en todas partes: del 12,6 % de Villanueva de la Cañada al 24,0 % de Centro.» [PAUSA]', cue: 'En rojo, las zonas donde el alquiler pesa el 18,2 % o más (quintil alto).' },
  'creemos-1': { s: 4, texto: '«Creemos que nadie debería descubrir demasiado tarde que su casa cuesta más de lo que parecía.»' },
  'creemos-2': { s: 4, texto: '«Creemos que el tiempo que pasas en un tren también es un precio.»' },
  'creemos-3': { s: 4, texto: '«Y creemos que una decisión así merece algo más que un presentimiento.» [PAUSA]' },
  'respuesta': { s: 6, texto: '«Merece una respuesta.» [→ el mapa y el logo] «Esto es Kuanto. Alex.»' },
  'lucia': { s: 25, texto: '«Os presento a Lucía. Treinta años, vive sola, gana 24.000 euros brutos y trabaja en Getafe. Busca piso, y todos los portales le dicen lo mismo: cuánto cuesta el alquiler.» [→] «Pero lo que Lucía necesita saber es otra cosa: dónde le sobra más dinero a final de mes.»' },
  'directo': { s: 150, texto: '«Vamos a verlo.» Recorrido: tarjetas (sola, 24.000 € brutos en 12 pagas, 30 años; trabajo en Getafe, 5 días, transporte público) → «Ver el mapa» con «Lo que sobra» → pinchar Parla: unos 467 € y 25,9 h al mes → cambiar a «Horas de viaje» y a «Precio de la hora» → «Otros escenarios»: fin del descuento del abono. Volver a la presentación con la flecha.', cue: 'Ten abierta antes la pestaña con el enlace del túnel y el estado de Lucía. Si la red falla: tecla B (capturas reales de hoy).' },
  'planb-tarjetas': { s: 30, texto: 'Plan B. «Seis tarjetas: hogar, sueldo, trabajo, zona de referencia, qué pinta el mapa y otros escenarios.»' },
  'planb-mapa': { s: 40, texto: 'Plan B. «Este es el mapa de lo que le sobra a Lucía. En verde, donde le sobra más; en rojo, donde no le llega.»' },
  'planb-parla': { s: 40, texto: 'Plan B. «Parla: unos 467 € al mes, pero 25,9 horas de viaje. Y la horquilla según el piso: de 338 a 575 €.»' },
  'planb-hora': { s: 40, texto: 'Plan B. «Y el precio de cada hora extra de tren: cuánto ahorras por cada hora que pierdes.» Tecla B para volver.' },
  'tres-zonas': { s: 35, texto: '«Getafe: le sobran 291 euros, con doce horas de viaje al mes. Parla: 467. Parece mejor… pero son veintiséis horas. Y en Centro, directamente, no le llega: le faltan 378.» [→] «176 euros más al mes a cambio de catorce horas más de tren. ¿Le compensa? Eso lo decide Lucía. Pero ahora lo decide sabiendo. Izan.»' },
  'capas': { s: 20, texto: '«Hay muchos proyectos que miran el alquiler. Algunos añaden el tiempo de viaje. Nosotros hacemos la cuenta entera: el neto con el IRPF de 2026 del BOE, el abono más barato para cada persona, la cesta según ingresos, el hogar y, sobre todo, desde dónde trabajas tú. Siete capas. Una sola cifra.»' },
  'engana': { s: 17, texto: '«¿Por qué hace falta? Porque mirar solo el alquiler engaña. En Chamartín el alquiler mediano es de 1.126 euros, más que en Centro. Y aun así pesa menos: un 16 % frente a un 24 %.» [→] «No es más barato. Es que allí se gana un 78 % más.»' },
  'horas': { s: 13, texto: '«Y el tiempo. Con el sueldo mínimo, irse lejos para pagar menos solo compensa las horas de tren, valoradas a lo que ganas por hora, en una de cada siete combinaciones. En las otras seis, lo pagas con tu tiempo.»' },
  'bono': { s: 22, texto: '«Y no es solo un problema de cada persona. En 2022 hubo 51.735 solicitudes del Bono Alquiler Joven. Se aceptó el 22 %. Y la proporción aceptada no cambia con lo que pesa el alquiler en cada municipio.» [→] «Con el sueldo mínimo, 16 municipios quedan fuera del tope del Bono. Catorce, por menos de 80 euros.»' },
  'abono': { s: 13, texto: '«Y lo que viene. Si todo el descuento del abono termina con 2026, cada adulto puede pagar hasta 33 euros más al mes. A 21 de noviembre no se había publicado ninguna prórroga. Kuanto ya lo calcula, zona a zona.»' },
  'ia': { s: 20, texto: '«¿Por qué no preguntárselo a una IA? Lo hicimos. ChatGPT y Gemini miraron entre cuatro y seis zonas, erraron el neto y cada uno puso un municipio en la zona de abono equivocada. Kuanto da cifra en 99 zonas, con la ley en la mano. Yeray os cuenta cómo.»', cue: 'Son cuatro respuestas: ilustra, no mide. Dilo si preguntan.' },
  'fuentes': { s: 17, texto: '«Detrás de cada cifra hay una fuente oficial. 89 descargas: INE, Consorcio de Transportes, BOE, BOCM, el catálogo de la Comunidad, Hacienda, el Ministerio de Vivienda. Cada una con su huella digital: si cambia un solo byte, lo sabemos.»' },
  'traza': { s: 20, texto: '«Y cada cifra se puede seguir hasta su origen. Los 467 euros de Lucía salen de un cálculo en su navegador, de un fichero de alquileres y de una descarga del Ministerio con esta huella.» [→] «Si alguien intenta publicar una cifra sin fuente, el sistema la rechaza.»' },
  'maquinas': { s: 22, texto: '«Somos tres personas. Pero hemos construido un equipo: agentes de IA que escriben el código y otros que lo auditan. Doce especialistas, ocho revisores, un abogado del diablo incluido, y dieciséis guardias automáticos. Ningún cambio de un área con revisor entra sin su veredicto.»' },
  'ritmo': { s: 10, texto: '«En quince días: 259 cambios fusionados, 993 tests y 131 decisiones fechadas y justificadas. Rápido. Y revisado.»' },
  'privacidad': { s: 15, texto: '«Y en un momento en que nuestros datos valen más que nunca, una promesa sencilla: tu sueldo nunca sale de tu móvil. Sin servidor, sin cuentas, sin rastreo.»' },
  'conectar': { s: 20, texto: '«Kuanto está hecho para conectarse: el estándar europeo DCAT-AP, 1.670 entidades de Smart Data Models y un servidor MCP para que cualquier IA responda con nuestras cifras. Y para durar: cero euros de servidor y un comando que lo regenera todo.»' },
  'datamad': { s: 10, texto: '«Datos de la Comunidad dentro del cálculo. Viable. Abierto. Y útil para quien busca piso y para quien hace política de vivienda.»' },
  'cierre': { s: 21, texto: '«Empezamos diciendo que una ciudad es muchas cosas. Para demasiada gente, también es una cuenta que no sale.» [PAUSA] «Nadie debería descubrir demasiado tarde cuánto le cuesta su casa.» [→] «Esto es Kuanto. Gracias.»', cue: 'Tecla A: anexo para las preguntas.' },
  'anexo-fuentes': { s: 0, texto: 'Anexo: fuentes por publicador. Esc para volver al cierre.' },
  'anexo-metodo': { s: 0, texto: 'Anexo: método y validación.' },
  'anexo-harness': { s: 0, texto: 'Anexo: cómo trabajan los agentes.' },
};

// === ESTADO ===
const todas = [...document.querySelectorAll('.slide')];
const idDe = (s) => s.dataset.id;
let modo = 'normal'; // normal | planb | anexo
const recorrido = () => todas.filter((s) => (modo === 'normal' ? !s.classList.contains('oculta')
  : modo === 'planb' ? idDe(s).startsWith('planb') : idDe(s).startsWith('anexo')));
let lista = recorrido();
let i = 0, paso = 0, generacion = 0;
const canal = 'BroadcastChannel' in window ? new BroadcastChannel('kuanto-pitch') : null;
const ES_ORADOR = new URLSearchParams(location.search).has('orador');

// === LIENZO: escala 1920×1080 entero a la ventana ===
function encajar() {
  const s = Math.min(innerWidth / 1920, innerHeight / 1080);
  document.getElementById('escenario').style.transform =
    `translate(${(innerWidth - 1920 * s) / 2}px,${(innerHeight - 1080 * s) / 2}px) scale(${s})`;
}

// === NAVEGACIÓN ===
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
  canal?.postMessage({ tipo: 'estado', id: idDe(s), paso, i, total: lista.length });
}
const pasosDe = (s) => Number(s.dataset.pasos || 0);
function siguiente() {
  const s = lista[i];
  if (paso < pasosDe(s)) { paso++; aplicarPasos(s); alPaso(s); pintarNotas(); canal?.postMessage({ tipo: 'estado', id: idDe(s), paso, i, total: lista.length }); return; }
  if (i < lista.length - 1) mostrar(i + 1);
  else if (modo === 'planb') cambiarModo('normal', 'tres-zonas');
}
function anterior() {
  if (paso > 0) { paso--; aplicarPasos(lista[i]); pintarNotas(); return; }
  if (i > 0) mostrar(i - 1, pasosDe(lista[i - 1]));
}
function aplicarPasos(s) {
  s.querySelectorAll('[data-paso]').forEach((el) => el.classList.toggle('ya', Number(el.dataset.paso) <= paso));
}
function cambiarModo(nuevo, volverA) {
  modo = nuevo;
  lista = recorrido();
  const destino = volverA ? lista.findIndex((s) => idDe(s) === volverA) : 0;
  i = 0;
  mostrar(Math.max(0, destino));
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
  else if (k === 'b' || k === 'B') modo === 'planb' ? cambiarModo('normal', 'tres-zonas') : cambiarModo('planb');
  else if (k === 'a' || k === 'A') modo === 'anexo' ? cambiarModo('normal', 'cierre') : cambiarModo('anexo');
  else if (k === 'Escape' && modo !== 'normal') cambiarModo('normal', modo === 'planb' ? 'tres-zonas' : 'cierre');
  else if (k === 'l' || k === 'L') document.body.classList.toggle('ligero');
});
addEventListener('click', (e) => { if (!ES_ORADOR && !e.target.closest('a,button,video')) (e.clientX > innerWidth / 3 ? siguiente : anterior)(); });
let toqueX = null;
addEventListener('touchstart', (e) => { toqueX = e.touches[0].clientX; }, { passive: true });
addEventListener('touchend', (e) => { if (toqueX === null) return; const d = e.changedTouches[0].clientX - toqueX; if (Math.abs(d) > 50) (d < 0 ? siguiente : anterior)(); toqueX = null; });
canal && (canal.onmessage = (m) => {
  if (ES_ORADOR) return pintarOrador(m.data);
  if (m.data.tipo === 'orden') ({ siguiente, anterior })[m.data.orden]?.();
  if (m.data.tipo === 'hola') mostrar(i, paso);
});

// === NOTAS EN PANTALLA (tecla N) ===
function pintarNotas() {
  const n = NOTAS[idDe(lista[i])] || {};
  document.getElementById('notas').innerHTML = `<b>${lista[i].dataset.quien} · ${idDe(lista[i])}</b> (${i + 1}/${lista.length}, paso ${paso}/${pasosDe(lista[i])})<br>${n.texto || '—'}${n.cue ? `<br><b>Aviso:</b> ${n.cue}` : ''}`;
}

// === ANIMACIONES POR DIAPOSITIVA ===
const entradas = {
  corto(s) { const v = s.querySelector('video'); v.currentTime = 0; v.play().catch(() => {}); v.onended = () => { if (lista[i] === s) siguiente(); }; },
  cifra() { contar(document.getElementById('contador196'), 19.6, 1, ' %', 2200); construirMapa(); },
  respuesta(s) { s.querySelector('#mereceFrase').style.opacity = 1; limpiarCanvas('particulas'); },
  fuentes() { construirNodos(); lluvia(); },
  maquinas() { construirBucle(); },
  ritmo() { construirRitmo(); },
};
const pasos = {
  cifra() { document.querySelectorAll('#mapaSube path').forEach((p, k) => { if (p.dataset.alto === 'true') { p.style.setProperty('--d', `${(k % 60) * 25}ms`); p.classList.add('sube'); } }); },
  respuesta(s) { s.querySelector('#mereceFrase').style.opacity = 0.0; particulas(); },
};
function entrar(s) { generacion++; entradas[idDe(s)]?.(s); if (paso) alPaso(s); }
function alPaso(s) { pasos[idDe(s)]?.(s); }
function salir(s) {
  if (idDe(s) === 'corto') s.querySelector('video').pause();
  s.querySelectorAll('#mapaSube path').forEach((p) => p.classList.remove('sube'));
}

function contar(el, fin, dec, sufijo, ms) {
  const g = generacion, t0 = performance.now();
  (function f(t) {
    if (g !== generacion) return;
    const k = Math.min(1, (t - t0) / ms), v = fin * (1 - Math.pow(1 - k, 4));
    el.textContent = v.toLocaleString('es-ES', { minimumFractionDigits: dec, maximumFractionDigits: dec }) + sufijo;
    if (k < 1) requestAnimationFrame(f);
  })(t0);
}

function construirMapa() {
  const svg = document.getElementById('mapaSube');
  if (svg.childElementCount) return;
  for (const z of window.MAPA.zonas) {
    const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    p.setAttribute('d', z.d);
    p.dataset.sube = String(z.sube);
    if (z.e === null) p.classList.add('sin');
    p.dataset.alto = String(z.e !== null && z.e >= 0.182); // corte del quintil alto (cifras.md)
    svg.appendChild(p);
  }
}

function limpiarCanvas(id) { const c = document.getElementById(id); c.getContext('2d').clearRect(0, 0, c.width, c.height); }
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
      ctx.globalAlpha = (0.15 + 0.6 * e) * (fin > 2.2 ? Math.max(0.22, 1 - (fin - 2.2) * 0.8) : 1);
      ctx.beginPath(); ctx.arc(p.x + (p.tx - p.x) * e, p.y + (p.ty - p.y) * e, 2.4, 0, 7); ctx.fill();
    }
    if (fin < 4) requestAnimationFrame(f);
  })(t0);
}

// Publicadores de data/README.md (89 filas con SHA-256, recuento por URL): radio ∝ √descargas.
const PUBLICADORES = [['INE', 23, 1250, 430], ['CRTM', 13, 1600, 400], ['BOE', 9, 1790, 610], ['BOCM', 13, 1530, 700], ['Comunidad de Madrid', 12, 1180, 760], ['AEAT', 7, 1400, 920], ['MIVAU', 5, 1700, 930], ['Otros', 7, 970, 560]];
function construirNodos() {
  const caja = document.getElementById('nodos');
  if (caja.childElementCount) return;
  PUBLICADORES.forEach(([n, v, x, y], k) => {
    const r = Math.round(40 * Math.sqrt(v));
    const d = document.createElement('div');
    d.className = 'nodo';
    Object.assign(d.style, { left: `${x - r}px`, top: `${y - r}px`, width: `${2 * r}px`, height: `${2 * r}px` });
    d.style.setProperty('--d', `${0.4 + k * 0.18}s`);
    d.style.setProperty('--fs', `${Math.max(40, r * 0.62)}px`);
    d.innerHTML = `<b>${v}</b><span>${n}</span>`;
    caja.appendChild(d);
  });
}
// Huellas reales (primeros 16 caracteres del SHA-256 de data/README.md).
const HUELLAS = '55c9da7e34d3bb3c 4168f4e1a0d4a4a9 d87cfaa552978e37 11dff8cab49afb68 c8e8bc79433e65be 2bcbc1ef138c17f0 32d4c0e446569237 fd266e11edf124ca 56409f54cad90e43 b67de15e52a96db5 35a0e51fee696ad8 d1a8bf517e542611 375963579a24131b 950ba6dfa6ff44c3 33a62c8121e11da4 ee9eb4e04bb7353e 196af39ab59a1cc2 16e8e53ce16ab6d7 e23e0ba93b91e640 c6e6683ddc0e3f81 ab1a0f07aed4a7ab 1a18668179adf9ed 9cbd0b5af3b8b9c1 83dd8f2878cfe236 f00ca4d7f27d23f8 ba79b5be3aaef86f 6fbaa5b50070a5d8 8ea9a933c732c634 9757658e33286872 badf74ee4e8a04bc d9d4569edb9e3051 848d8e60eabcac48 99a5099a02b6e706 af30b424617af40a aa1dafb7a9dab291 88fdae5f080f54c1 29fd48476b663e36 0cd4f1c8a7d0f4e6 debbfbd9b80d6073 1fae5699b8b365b8'.split(' ');
function lluvia() {
  const c = document.getElementById('lluvia'), ctx = c.getContext('2d'), g = generacion;
  const col = Array.from({ length: 22 }, (_, k) => ({ x: 40 + k * 88, y: Math.random() * -1080, v: 0.6 + Math.random() * 1.4, h: HUELLAS[k % HUELLAS.length] }));
  ctx.font = '16px ui-monospace, Menlo, monospace';
  (function f() {
    if (g !== generacion || document.body.classList.contains('ligero')) return;
    ctx.clearRect(0, 0, 1920, 1080);
    for (const k of col) {
      for (let j = 0; j < k.h.length; j++) {
        ctx.fillStyle = `rgba(156,194,245,${0.05 + 0.25 * (j / k.h.length)})`;
        ctx.fillText(k.h[j], k.x, k.y + j * 20);
      }
      k.y += k.v; if (k.y > 1100) { k.y = -340; k.h = HUELLAS[Math.floor(Math.random() * HUELLAS.length)]; }
    }
    requestAnimationFrame(f);
  })();
}

const BUCLE = ['Issue', 'Worktree', 'Skill del área', 'Hooks y tests', 'Commit', 'Revisor', 'Pull request', 'CI y merge'];
function construirBucle() {
  const svg = document.getElementById('bucle');
  if (svg.childElementCount) return;
  const cx = 410, cy = 370, r = 255, ns = 'http://www.w3.org/2000/svg';
  svg.innerHTML = `<circle class="arco" cx="${cx}" cy="${cy}" r="${r}"/><circle class="vivo" cx="${cx}" cy="${cy}" r="${r}" pathLength="2000"/>`;
  BUCLE.forEach((t, k) => {
    const a = -Math.PI / 2 + (k / BUCLE.length) * 2 * Math.PI, x = cx + r * Math.cos(a), y = cy + r * Math.sin(a);
    const gr = document.createElementNS(ns, 'g');
    gr.setAttribute('class', 'paso');
    const c = Math.cos(a), ancla = c > 0.3 ? 'start' : c < -0.3 ? 'end' : 'middle';
    gr.innerHTML = `<circle cx="${x}" cy="${y}" r="16"/><text x="${x + c * 30}" y="${y + Math.sin(a) * 34 + 8}" style="text-anchor:${ancla}">${t}</text>`;
    svg.appendChild(gr);
  });
  svg.insertAdjacentHTML('beforeend', `<text x="${cx}" y="${cy - 10}" text-anchor="middle" style="fill:var(--texto);font:400 52px var(--serif)">Un cambio</text><text x="${cx}" y="${cy + 40}" text-anchor="middle" style="fill:var(--texto-2);font:400 26px var(--fuente)">de la idea al merge</text>`);
}

// PR fusionados por día, del 11 al 25-11-2026 (gh pr list --state merged).
const PR_DIA = [5, 7, 20, 24, 23, 28, 10, 19, 20, 31, 9, 10, 18, 19, 16];
function construirRitmo() {
  const caja = document.getElementById('ritmo');
  if (caja.childElementCount) return;
  PR_DIA.forEach((n, k) => {
    const b = document.createElement('i');
    b.dataset.n = n;
    b.style.setProperty('--h', `${(n / 31) * 100}%`);
    b.style.setProperty('--d', `${0.2 + k * 0.06}s`);
    caja.appendChild(b);
  });
}

// === MODO ORADOR (tecla P): ventana aparte con guion, siguiente y relojes por bloque ===
function iniciarOrador() {
  document.querySelector('.deck-viewport').style.display = 'none';
  document.getElementById('progreso').style.display = 'none';
  const plan = {};
  todas.filter((s) => !s.classList.contains('oculta')).forEach((s) => { const q = s.dataset.quien; plan[q] = (plan[q] || 0) + (NOTAS[idDe(s)]?.s || 0); });
  document.body.style.cssText = 'overflow:auto;background:#020409;color:#eef2f7;font:400 22px/1.5 "Instrument Sans",sans-serif;padding:28px 40px';
  document.body.insertAdjacentHTML('beforeend', `
    <div style="display:flex;gap:40px;align-items:baseline;border-bottom:1px solid #1f2c40;padding-bottom:14px">
      <div style="font:400 64px 'Instrument Serif'" id="oTotal">0:00</div>
      <div>Total · previsto 9:00</div>
      <div style="margin-left:auto;font-size:20px;color:#8592a6">Flechas: avanzar y retroceder en la presentación · R: reiniciar relojes</div>
    </div>
    <div id="oBloque" style="font:500 26px 'Instrument Sans';margin:18px 0 4px"></div>
    <div id="oTit" style="font:400 44px 'Instrument Serif';margin:6px 0"></div>
    <div id="oTexto" style="font:400 34px/1.45 'Instrument Sans';max-width:1500px;margin:12px 0"></div>
    <div id="oCue" style="color:#f2d38a;font-size:24px;margin:10px 0"></div>
    <div id="oSig" style="color:#8592a6;font-size:24px;margin-top:22px;border-top:1px solid #1f2c40;padding-top:14px"></div>`);
  let t0 = Date.now(), quien = null, tb = Date.now();
  const mmss = (s) => `${s < 0 ? '−' : ''}${Math.floor(Math.abs(s) / 60)}:${String(Math.floor(Math.abs(s)) % 60).padStart(2, '0')}`;
  window.pintarOrador = (d) => {
    if (d.tipo !== 'estado') return;
    const s = todas.find((x) => idDe(x) === d.id), q = s.dataset.quien, n = NOTAS[d.id] || {};
    if (q !== quien) { quien = q; tb = Date.now(); }
    const idx = todas.indexOf(s), sig = todas.slice(idx + 1).find((x) => !x.classList.contains('oculta') || x.dataset.id.startsWith(d.id.slice(0, 5)));
    document.getElementById('oTit').textContent = `${d.i + 1}/${d.total} · ${d.id}${pasosDe(s) ? ` · paso ${d.paso}/${pasosDe(s)}` : ''}`;
    document.getElementById('oTexto').textContent = n.texto || '—';
    document.getElementById('oCue').textContent = n.cue || '';
    document.getElementById('oSig').textContent = sig ? `Siguiente: ${sig.dataset.id} (${sig.dataset.quien})` : 'Fin';
    window.oPlan = plan[q] || 0;
  };
  setInterval(() => {
    document.getElementById('oTotal').textContent = mmss((Date.now() - t0) / 1000);
    if (quien) {
      const pasado = (Date.now() - tb) / 1000, resta = (window.oPlan || 0) - pasado;
      const el = document.getElementById('oBloque');
      el.textContent = `${quien}: ${mmss(pasado)} de ${mmss(window.oPlan || 0)} · ${resta >= 0 ? `quedan ${mmss(resta)}` : `te pasas ${mmss(-resta)}`}`;
      el.style.color = resta < 0 ? '#f2777f' : resta < 15 ? '#f2d38a' : '#5cc8b8';
    }
  }, 250);
  addEventListener('keydown', (e) => {
    if (['ArrowRight', 'PageDown', ' '].includes(e.key)) canal?.postMessage({ tipo: 'orden', orden: 'siguiente' });
    if (['ArrowLeft', 'PageUp'].includes(e.key)) canal?.postMessage({ tipo: 'orden', orden: 'anterior' });
    if (e.key === 'r' || e.key === 'R') { t0 = Date.now(); tb = Date.now(); }
  });
  canal?.postMessage({ tipo: 'hola' });
}
function pintarOrador(d) { window.pintarOrador?.(d); }

// === ARRANQUE ===
// Un navegador automatizado (la exportación) recibe el estado final; ?animado lo evita para probar.
if (navigator.webdriver && !new URLSearchParams(location.search).has('animado')) {
  document.body.classList.add('estatico');
  construirMapa(); construirNodos(); construirBucle(); construirRitmo();
}
if (matchMedia('(prefers-reduced-motion: reduce)').matches) document.body.classList.add('ligero');
if (ES_ORADOR) iniciarOrador();
else {
  addEventListener('resize', encajar);
  encajar();
  const desdeUrl = location.hash.slice(1);
  if (desdeUrl.startsWith('planb')) { modo = 'planb'; lista = recorrido(); }
  if (desdeUrl.startsWith('anexo')) { modo = 'anexo'; lista = recorrido(); }
  const k = lista.findIndex((s) => idDe(s) === desdeUrl);
  document.fonts.ready.then(() => mostrar(k >= 0 ? k : 0));
}
