---
description: "Incorpora o actualiza una fuente de datos de principio a fin: descarga reproducible a data/raw con fecha y SHA-256, fila en data/README.md, verificación, perfil y función de carga en src/ con test; comprueba que todo el equipo tiene los mismos ficheros. No verifica licencias ni cobertura por sí misma (dm-verificacion-fuentes) ni perfila (dm-diccionario-datos)."
when_to_use: "Quiero usar este dataset; añade esta fuente; descarga los datos de esta URL; hay una versión nueva del fichero; ¿todos tenemos los mismos datos?; me falta un fichero de data/README.md; ¿cómo descargo esto para que sea reproducible?"
---

# Fuente de datos nueva

Cada dato que entra en el proyecto tiene que poder rehacerlo cualquiera del equipo, en otro ordenador, y obtener **los mismos bytes**. Esta skill es el procedimiento; cada paso delega en la pieza que ya existe para él.

## Antes de empezar: conectar con el desarrollo del proyecto

1. **¿Ya está?** Busca en `data/README.md`, `data/raw/` y `docs/datos/`. Si está en la tabla pero no en tu `data/raw/`, descárgala con su «Cómo obtenerla» y pasa a «Contrastar». Si no está, sigue.
2. **¿Encaja?** Lee `docs/decisiones.md`: idea, unidad territorial, años y **uso previsto** (interno, demo pública, API o MCP público). Si no está decidido, pregunta o deja el supuesto escrito.
3. **¿De dónde?** La URL del **publicador original**, a ser posible la del fichero o la API estable, no una página que cambie ni un espejo.

## Flujo

1. **Descarga** con [scripts/descargar.py](scripts/descargar.py) (solo stdlib), desde la raíz del repo:
   ```bash
   python .claude/skills/dm-nueva-fuente/scripts/descargar.py <URL> --nombre <fuente>
   ```
   - Guarda `data/raw/<fuente>_<AAAA-MM-DD>.<ext>`, nunca sobrescribe, solo `https`, detecta descargas cortadas e imprime la fila para `data/README.md` con su SHA-256.
   - Si la descarga necesita lógica (paginar una API, parámetros, varios ficheros), va a una función de `src/` que guarde con el mismo nombre y calcule la misma huella; «Cómo obtenerla» es entonces su orden.
   - Un ZIP se descomprime sin sobrescribir: `unzip -n data/raw/<f>.zip -d data/raw/<fuente>_<fecha>/`.
2. **Documenta** la fila en `data/README.md` (nombre, URL, licencia, cómo obtenerla, fichero y SHA-256). La licencia, como la escribe el publicador.
3. **Commit y verificación:** lanza `dm-verificador-fuentes` (obligatorio en el PR cuando cambia `data/README.md`): existencia, cobertura, año y si la licencia permite el uso previsto. **NO APTO** → no se usa: quita la fila y deja el motivo en `docs/decisiones.md`.
4. **Conócela antes de usarla:** CSV de más de ~5 MB, diccionario con `dm-diccionario-datos`; si es pequeño, `head` y los metadatos del publicador. Nunca el fichero entero al contexto.
5. **Cárgala en `src/`:** una función por fuente que lee `data/raw/<fichero>` (el nombre, en un solo sitio), con los códigos oficiales como texto y la codificación y el formato numérico que diga el diccionario. Test pequeño con un fragmento sintético: los tests no pueden depender de `data/`, que no se versiona. Si es geográfica o hay que pasarla a otra unidad, `dm-cartografia` y `dm-tablas-de-paso`.

**Actualizar una fuente:** los originales no se tocan (un hook lo impide). Se descarga la versión nueva con la fecha de hoy y se cambian fichero y SHA-256 en la fila; el viejo se queda. Si cambian cifras ya presentadas, se repite la verificación y lo afectado pasa por `dm-trazador-cifras`.

## Contrastar cada resultado con lo que debe salir

| Comprobación | Lo correcto | Si no se cumple |
|---|---|---|
| `descargar.py --comprobar` | Sale con 0: tus ficheros son los de la tabla | Otro SHA-256: el publicador cambió el fichero o la descarga está corrupta. No lo uses; avisa y decide en `docs/decisiones.md` cuál vale |
| Filas, columnas y años | Los que declara el publicador en sus metadatos | Descarga parcial, filtro en la URL o versión distinta |
| Unidades territoriales | Todas las del ámbito oficial (por ejemplo, todos los municipios) | Ver `dm-cartografia` |
| Licencia frente al uso previsto | Compatible, según `dm-verificador-fuentes` | No se usa, o solo para lo que permite |
| Función de carga | Test en verde y mismo número de filas que el fichero | Separador, codificación o cabecera mal leídos |

Al abrir sesión, un hook avisa de los ficheros de la tabla que faltan en tu `data/raw/`.

## Al terminar: dejar el trabajo conectado

- Fila completa en `data/README.md`, veredicto del verificador en el PR y `--comprobar` en 0.
- Si se elige esta fuente frente a otra, o se descarta, una línea en `docs/decisiones.md`.
- Si algo no se pudo hacer (sin metadatos para contrastar, licencia dudosa), se dice en el PR.

## Errores que invalidan una fuente

- Descargar de un espejo, un agregador o una copia en GitHub en lugar del publicador.
- Trabajar con un fichero cuyo SHA-256 no coincide con la tabla: dos personas, dos resultados.
- Tratar lo descargado como confiable: no se ejecuta, no se abre con `pickle` ni con macros, y un CSV se lee como texto.
- Credenciales en la URL o en `data/README.md`: si la API pide clave, va en `.env` (con su nombre en `.env.example`).
- Scraping sin comprobar la licencia y las condiciones del sitio (`dm-verificacion-fuentes`) o cargando el servidor.
