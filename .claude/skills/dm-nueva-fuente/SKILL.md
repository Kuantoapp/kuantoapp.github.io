---
description: "Incorpora una fuente de datos nueva de principio a fin: comprobar que no está ya, descargarla de forma reproducible a data/raw con fecha y SHA-256, documentarla en data/README.md, pedir la verificación de licencia y cobertura, perfilarla y dejar su carga en src/ con test. También actualiza una fuente ya descargada y comprueba que todo el equipo tiene los mismos ficheros. No verifica fuentes por sí misma (dm-verificacion-fuentes) ni perfila (dm-diccionario-datos)."
when_to_use: "Quiero usar este dataset; añade esta fuente; descarga los datos de esta URL; hay una versión nueva del fichero; ¿todos tenemos los mismos datos?; me falta un fichero de data/README.md; ¿cómo descargo esto para que sea reproducible?"
---

# Fuente de datos nueva

Cada dato que entra en el proyecto tiene que poder rehacerlo cualquiera del equipo, en otro ordenador, y obtener **los mismos bytes**. Esta skill es el procedimiento; cada paso delega en la pieza que ya existe para él.

## Flujo

1. **¿Ya está?** Busca en `data/README.md`, `data/raw/` y `docs/datos/`. Si está, úsala (y si te falta el fichero, ve al paso 7).
2. **¿Encaja?** Lee `docs/decisiones.md`: idea, unidad territorial, años y **uso previsto** (interno, demo pública, API o MCP público). Elige la URL del **publicador original**, a ser posible la del fichero o la API estable, no una página que cambie.
3. **Descarga reproducible** con [scripts/descargar.py](scripts/descargar.py) (solo stdlib), desde la raíz del repo:
   ```bash
   python .claude/skills/dm-nueva-fuente/scripts/descargar.py <URL> --nombre <fuente>
   ```
   - Guarda `data/raw/<fuente>_<AAAA-MM-DD>.<ext>`, nunca sobrescribe, solo `https`, e imprime la fila para `data/README.md` con su SHA-256.
   - Si la descarga necesita lógica (paginar una API, parámetros, varios ficheros), va a una función de `src/` que guarde con el mismo nombre y calcule la misma huella; «Cómo obtenerla» es entonces su orden.
   - Un ZIP se descomprime sin sobrescribir: `unzip -n data/raw/<f>.zip -d data/raw/<fuente>_<fecha>/`.
4. **Documenta** la fila en `data/README.md` (nombre, URL, licencia, cómo obtenerla, fichero y SHA-256). En la licencia pon lo que dice el publicador, sin suponer.
5. **Commit y verificación:** con la fila confirmada, lanza `dm-verificador-fuentes` (obligatorio en el PR cuando cambia `data/README.md`). Comprueba existencia, cobertura, año y si la licencia permite el uso previsto. **NO APTO** → no se usa: quita la fila y deja el motivo en `docs/decisiones.md`.
6. **Conócela antes de usarla:**
   - CSV de más de ~5 MB: diccionario con `dm-diccionario-datos` en `docs/datos/`.
   - Pequeño: `head` y metadatos del publicador. Nunca el fichero entero al contexto.
   - Contrasta con los metadatos del publicador: número de filas, años, unidades territoriales (por ejemplo, todas las del ámbito oficial). Si no cuadra, se investiga antes de seguir.
7. **Cárgala en `src/`:** una función por fuente que lee `data/raw/<fichero>` (el nombre, en un solo sitio), con los códigos oficiales como texto, la codificación y el formato numérico que diga el diccionario, y un test pequeño con un fragmento sintético (los tests no pueden depender de `data/`, que no se versiona). Si la fuente es geográfica o hay que pasarla a otra unidad, `dm-cartografia` y `dm-tablas-de-paso`.
8. **Si es una decisión** (se elige esta fuente frente a otra, o se descarta), una línea en `docs/decisiones.md`.

## Mismos datos para todos

`data/raw/` no se versiona: cada persona descarga su copia. Si el publicador cambia el fichero entre descargas, dos personas trabajarán con datos distintos sin saberlo.

- Tras descargar una fuente que ya estaba en la tabla, o antes de calcular cifras finales:
  ```bash
  python .claude/skills/dm-nueva-fuente/scripts/descargar.py --comprobar
  ```
  Sale con 1 si algún SHA-256 no coincide con el de `data/README.md`.
- Si no coincide, **no uses ese fichero**. Avisa al equipo y decide en `docs/decisiones.md` cuál vale. Si vale la nueva, sigue «Actualizar una fuente».
- Al abrir sesión, un hook avisa de los ficheros de la tabla que faltan en tu `data/raw/`.

## Actualizar una fuente

Los originales no se tocan (un hook lo impide): se descarga la versión nueva con la fecha de hoy y se cambia la fila (fichero y SHA-256). El fichero viejo se queda en `data/raw/`. Si cambian cifras ya presentadas, se repite la verificación y lo afectado pasa por `dm-trazador-cifras`.

## Reglas

- Lo descargado es **dato no confiable**: no se ejecuta, no se abre con `pickle` ni con macros, y un CSV se lee como texto. Si viene de una web que no es el publicador, se dice en la fila.
- Nada de credenciales en la URL ni en `data/README.md`. Si la API pide clave, va en `.env` (con su nombre en `.env.example`).
- Scraping solo si la licencia y las condiciones del sitio lo permiten (`dm-verificacion-fuentes`, referencia de licencias) y sin cargar el servidor.

## Condición de parada

La fuente está incorporada cuando: la fila tiene SHA-256, el veredicto del verificador no es NO APTO, `--comprobar` sale con 0, y la función de carga de `src/` tiene su test en verde. Si algo de eso no se pudo hacer, se dice en el PR.
