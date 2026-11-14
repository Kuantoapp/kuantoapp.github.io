# Código mínimo

Claude Code carga esta regla en todas las sesiones, como `AGENTS.md`, y se aplica a cada línea de código que escribas, no solo al refactorizar. ruff (`ruff.toml`) rechaza al editar y en la CI lo que una máquina puede detectar, y `dm-revisor-codigo` comprueba el resto en cada PR.

El mejor código es el que no se escribe: cada línea hay que leerla, probarla y arreglarla después, y con varios agentes escribiendo a la vez el código de más se multiplica. Se resuelve **la tarea entera** con **el menor código nuevo**: perezoso con la solución, nunca con el cambio.

**Limpio y escalable aquí significa simple:** se escala borrando y reutilizando, no preparando capas. Una abstracción se gana con la tercera repetición real; antes, es código que alguien tendrá que leer sin que aporte nada.

## Antes de escribir

1. **Qué se pide:** la issue y su criterio de aceptación. Si no hay uno comprobable, escríbelo antes de tocar nada; lo que queda fuera no se implementa.
2. **Qué está decidido:** `docs/decisiones.md` (stack, librerías, formatos). No metas otra librería para lo mismo.
3. **Alcance:** lee el código que tocas y lista **todo** lo que el cambio debe alcanzar: quién llama a la función (`grep -rn "nombre" src app tests notebooks`), tests, fixtures, configuración y documentación. Comprueba qué puede romper para quien lo usa: datos que se pierden o exponen, llamadas que dejan de funcionar. Eso es el alcance; funcionalidades extra, no.

## La primera opción que funcione del todo

1. **¿Hace falta?** Nada de opciones, parámetros ni flexibilidad que nadie pidió; nómbralas en una línea y sigue. Una petición vaga recibe la versión más pequeña que cumple lo esencial.
2. **¿Ya está en el repo?** Una función de `src/`, un patrón, un componente: úsalo como lo usa el código de alrededor.
3. **¿Lo hace la librería estándar o una que ya usa el proyecto?** pandas, geopandas, numpy y la stdlib antes que código propio.
4. **¿Hay una dependencia ya instalada?** Úsala. Nunca una dependencia nueva por unas pocas líneas; si hace falta una, se fija en `requirements.txt` y se justifica en el PR.
5. **¿Cabe en una línea que se entiende de un vistazo?** Una línea. Una que hay que descifrar no es corta.
6. **Si no:** el código mínimo que funciona.

## Reglas

- **Sin abstracciones de un solo uso:** ni clases, envoltorios, conversiones de tipo, configuración ni código «para luego». Se abstrae a la tercera repetición real, no antes. Los valores se quedan en la forma que ya da la librería (un `DataFrame` no se convierte en lista de diccionarios para volver a convertirlo).
- **Borrar gana a añadir.** Respeta la estructura que ya tiene el repo: sus capas, carpetas y convenciones.
- **Corrige la causa una vez:** antes de arreglar un fallo, busca a todos los que llaman a la función y arréglalo en el código compartido, no en cada llamada.
- **Lo que se mueve conserva** su manejo de errores y sus validaciones.
- **Falla alto y claro:** nunca silencies una excepción ni conviertas un error en un valor vacío.
- **Entre dos opciones del mismo tamaño,** la que es correcta en los casos límite (vacío, nulos, un solo elemento).
- **Sin cambios ajenos:** ni formato, ni renombres, ni «ya que estaba».
- **Comentarios solo para el porqué** que el código no muestra, en una línea.
- **Un atajo con límite conocido** lleva un comentario con esta forma: `# shortcut: <el límite>, <cuándo mejorarlo>`.
- **La lógica nueva no trivial** (una rama, un bucle, un parser, un join, un cálculo) lleva un test pequeño en `tests/` que fallaría si se rompe.

## Python

| En vez de… | Usa |
|---|---|
| Bucles por fila (`iterrows`, `apply(axis=1)`) | Operaciones vectorizadas de pandas o numpy |
| Una clase con un solo método o sin estado | Una función |
| Leer y convertir a mano un CSV | `pd.read_csv(..., dtype={"codigo": str}, encoding=...)` |
| Rutas con `os.path` o cadenas | `pathlib.Path`, relativas a la raíz del repo |
| Contadores, agrupaciones o cachés hechos a mano | `collections.Counter`, `groupby`, `functools.cache` |
| Un parámetro o una opción «por si acaso» | Nada, hasta que alguien lo necesite |
| Un parámetro booleano que cambia lo que hace la función | Dos funciones, o ninguna si solo se usa un camino |

## Antes de darlo por hecho

| Pregunta | Si la respuesta es sí |
|---|---|
| ¿Se puede borrar una línea, un fichero o un parámetro sin perder funcionalidad? | Bórralo |
| ¿Duplica algo que ya existe en el repo? | Reutiliza lo existente |
| ¿Alguna abstracción tiene un solo uso? | Quítala |
| ¿El diff tiene cambios ajenos al objetivo? | Sácalos a otro PR |
| ¿Falta un test que demuestre el criterio de aceptación? | Escríbelo |

En el PR, una o dos líneas con **lo que no hiciste o no comprobaste** y el riesgo que deba conocer quien lo revise.

## Lo que nunca se recorta

Ahorrar código nunca justifica quitar esto:

- La validación de lo que entra de fuera (descargas, APIs, usuarios de la demo).
- El manejo de errores que evita perder datos o dar un resultado falso sin avisar.
- La seguridad y la accesibilidad de la demo.
- Cualquier parte que pida la issue: un cambio más corto que no la cumple entera no está hecho.

Adaptado de `ponytail` (licencia MIT).
