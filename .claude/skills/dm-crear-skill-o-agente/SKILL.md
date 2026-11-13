---
description: "Diseña, escribe y prueba una skill o un subagente nuevo del repo, o cambia uno existente, con la estructura común de .claude/ y las buenas prácticas oficiales de Claude Code: decidir si hace falta y qué pieza es (regla, skill, agente o hook), evitar solapes, description y when_to_use precisas, plantilla de secciones, herramientas y modelo, validación, prueba real e índice. No ejecuta la tarea de la pieza que crea."
when_to_use: "Crea una skill para X; necesito un agente que revise Y; convierte este procedimiento en skill; adapta esta skill personal al repo; ¿esto debería ser una skill, un agente o un hook?; esta skill no se activa o se activa de más; mejora la descripción de este agente"
---

# Crear o cambiar una skill o un agente

Claude ya sabe escribir skills y agentes en general; esta skill aporta **lo propio del repo**: prefijo `dm-`, secciones comunes, índice, validador, cableado de revisores obligatorios y las lecciones de las piezas que ya hay. Cada pieza cuesta contexto en todas las sesiones (su descripción está siempre a la vista) y compite con las demás por activarse: solo se justifica si hace algo que no hace ninguna otra.

## Regla de oro

**Primero, ¿hace falta?** Si cabe en una pieza que ya existe, se amplía esa. Si es una regla que debe cumplirse siempre, va en `AGENTS.md`; si no puede fallar nunca, es un hook, una regla `deny` o un paso de CI, no texto. Una pieza, una responsabilidad.

## Antes de empezar: conectar con el desarrollo del proyecto

1. **Lee [.claude/README.md](../../README.md):** índice, «Principios de diseño», «Dónde va cada cosa» y las reglas de agentes y skills. Es la norma (sus límites los comprueba `validar_claude.py`); esta skill es el procedimiento.
2. **Trabaja como cualquier cambio:** con su issue y en la rama `<usuario>/claude-<nombre>`.
3. **Elige la pieza:**

   | Necesito… | Pieza |
   |---|---|
   | Una regla que se aplica siempre, en cualquier tarea | Una línea en `AGENTS.md` |
   | Una regla solo para parte del repo | `.claude/rules/<tema>.md` con `paths` (aún no hay ninguna y la CI no las valida) |
   | Un procedimiento de varios pasos que Claude aplica en la conversación | Skill |
   | Una tarea delegable con contexto propio y herramientas limitadas (revisar, auditar, verificar) | Subagente |
   | Algo que no debe pasar nunca | Hook, `deny` o CI: sigue la fila «Algo que **nunca** debe pasar» de «Dónde va cada cosa» (lanzador `py`, Python 3.9, tests y versión de Windows) |
   | **Un procedimiento con una parte que no puede fallar** (lo más habitual) | Las dos piezas: la skill con el procedimiento y el hook o paso de CI con la parte dura, que la skill nombra. Si son pequeñas, en el mismo PR; si no, la skill primero y el hook en otra issue que la skill cita como pendiente |

4. **Busca solapes:** compara con las descripciones del índice y con `grep -rn "description:\|when_to_use:" .claude/agents .claude/skills`. Si dos piezas se activarían con las mismas frases, se unen o se delimitan con un «no es para… (pieza)» **en las dos**.
5. **Evaluaciones primero:** antes de escribir, apunta 3 peticiones reales que deben activarla, con el resultado esperado, y 2 que no (son de otra pieza). Ejecuta una de las 3 **sin** la pieza: si el resultado ya es bueno, no hace falta.

## Flujo

1. **Nombre:** `dm-<verbo-o-tema>`, en minúsculas y con guiones; la carpeta o el fichero se llaman igual. **Un agente que revisa lleva en el nombre** `revisor`, `auditor`, `verificador`, `trazador` o `abogado`: la CI solo le exige ser de solo lectura si su nombre lo dice.
2. **Descripción** (es lo que decide si se usa; detalle en [buenas-practicas.md](referencia/buenas-practicas.md)):
   - Tercera persona, empezando por el caso de uso clave con verbo («Revisa…», «Prepara…»).
   - Después, los términos concretos que diría el equipo y, al final, para qué **no** es y qué pieza usar.
   - Skill: `description` + `when_to_use` con frases o preguntas de ejemplo. Agente: si debe usarse sin pedirlo, «Úsalo de forma proactiva…». Longitudes, las de `.claude/README.md`.
   - Que no case con cualquier tarea: si una regla aplica a todo el código, va en `AGENTS.md` y la skill queda para los casos concretos.
3. **Cuerpo, con la plantilla:** [plantilla-skill.md](referencia/plantilla-skill.md) o [plantilla-agente.md](referencia/plantilla-agente.md). El agente de referencia es `dm-trazador-cifras`; la skill, `dm-nueva-fuente`. Solo lo que Claude no sabe ya; el detalle va a `referencia/` (un nivel, enlazado desde el fichero principal; los de más de 100 líneas empiezan con una línea «Contenido»).
4. **Grado de libertad según lo frágil que sea la tarea:** texto con criterios si hay varios caminos válidos; plantilla si hay un patrón preferido; script exacto si un error es caro.
5. **Scripts:** en `scripts/` de la skill, solo stdlib, compatibles con Python 3.9 si los ejecuta un hook, con un test en `tests/` que los carga por ruta con `importlib` (como `tests/test_nueva_fuente.py`). Si necesitas código de otra skill, impórtalo por ruta igual, no lo copies. En el `SKILL.md`, di si se ejecutan o se leen. Un límite conocido lleva `# shortcut: <límite>, <cuándo mejorarlo>`.
6. **Agente:** `tools` mínimas; quien revisa no edita (`disallowedTools: Edit, Write, NotebookEdit, Agent`) y no lleva `memory` (reactiva la escritura); `model` según la tarea (`opus` para revisar o razonar, `sonnet` para ejecutar algo definido, `haiku` solo para tareas mecánicas). Precarga skills (`skills:`) solo si las usa siempre: se inyectan enteras en cada ejecución. El cuerpo es su prompt completo, porque no ve la conversación (sí recibe `AGENTS.md`).
7. **Revisor obligatorio** (si la CI debe exigir su veredicto): área en `.github/scripts/revisiones.py` (`REVISORES` y `area()`), su nombre en el matcher `SubagentStop` de `.claude/settings.json` y en `tests/test_settings.py`, un test de su área en `tests/test_revisiones.py` y una fila en la tabla de `AGENTS.md`.
8. **Cambiar una pieza existente:** se cambia lo que pide la issue. Si diverge de la plantilla, no se migra entera de paso; eso es otra issue.

## Contrastar cada resultado con lo que debe salir

| Comprobación | Lo correcto | Si no se cumple |
|---|---|---|
| `python .github/scripts/validar_claude.py` (también salta solo al guardar) | Sin errores | Corrige lo que diga: campos, longitudes, enlaces, índice, solo lectura |
| **Activación, con ojos limpios:** lanza un subagente general (no ve esta conversación) con solo las descripciones del índice y las 5 peticiones, y pregúntale qué pieza usaría para cada una | Elige esta para las 3 y otra para las 2 | Ajusta la descripción con los términos de la petición o añade el «no es para…» |
| **Prueba real:** una de las 3 peticiones, con el modelo que la usará (`sonnet` si la lanza un agente `sonnet`) | Da el resultado esperado y mejor que sin la pieza | Corrige el paso que falla. Las piezas nuevas se detectan en segundos; si no aparecen, `/reload-skills` o prueba el prompt con un agente general que lea su fichero |
| Coste | Dentro de los límites; nada precargado sin uso; `SKILL.md` de menos de 500 líneas | Recorta o mueve a `referencia/` |
| `ruff check . && pytest -q` y `python .github/scripts/docs_al_dia.py` | En verde | Arregla scripts, tests o documentación |

## Al terminar: dejar el trabajo conectado

En este orden:

1. Fila en el índice de `.claude/README.md` (tipo, origen y para qué) y, si delimitaste un solape, el «no es para…» de la otra pieza.
2. Si cambia cómo trabaja el equipo, una línea en `docs/decisiones.md`.
3. Validador, ruff, tests y `docs_al_dia.py` en verde; commit.
4. `dm-abogado-del-diablo` sobre el diseño (solapes, activación, coste, contradicciones internas); corrige y commit.
5. PR con la issue. Los cambios en `.claude/` los aprueba `@yeraybc`. Si se adapta de una pieza externa o personal, una línea con su origen y licencia.

## Errores que invalidan una pieza

- Repite algo que ya hace otra, o una regla de `AGENTS.md`.
- Descripción vaga («ayuda con datos»), en segunda persona o que encaja con cualquier tarea.
- Revisor con herramientas de edición, con `memory` o con un nombre que no dice que revisa.
- Skills precargadas que no usa siempre: pagan contexto en cada ejecución.
- Ejemplos que enseñan a inventar: un «después» con datos que no estaban en el «antes», o cifras y hechos sobre fuentes sin fuente o sin «(verificar)».
- Reglas que se contradicen dentro de la misma pieza.
- Información con fecha que caduca sin decirlo: va en `referencia/` con «comprobado el AAAA-MM-DD» y su fuente.
- Referencias anidadas o ficheros sin enlazar: Claude no los encuentra.
- Atada a una idea o a unos datos concretos: lo específico se lee del proyecto (`docs/decisiones.md`, `data/README.md`).

## Referencia

- [plantilla-skill.md](referencia/plantilla-skill.md): esqueleto de `SKILL.md` con las secciones comunes.
- [plantilla-agente.md](referencia/plantilla-agente.md): esqueletos de agente revisor y ejecutor, con formato de veredicto.
- [buenas-practicas.md](referencia/buenas-practicas.md): las prácticas oficiales de Claude Code que aplican estas plantillas, con sus fuentes.
