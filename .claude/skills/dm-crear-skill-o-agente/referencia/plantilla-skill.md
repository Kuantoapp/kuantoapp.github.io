# Plantilla de skill

Copia el bloque en `.claude/skills/dm-<nombre>/SKILL.md` y sustituye lo que va entre `<…>`. Las secciones son las comunes del repo: quita las que no apliquen, no inventes otras si una común sirve.

````markdown
---
description: "<Verbo en tercera persona> <qué hace, caso de uso clave primero>: <términos concretos que diría el equipo>. No <lo que no hace> (<pieza que sí>)."
when_to_use: "<frase de ejemplo>; <otra>; ¿<pregunta típica>?; ¿<otra>?"
---

# <Título en minúscula salvo la primera palabra>

<Una o dos frases: qué resuelve y por qué importa en este repo.>

## Regla de oro

<Opcional: la única regla que, si se rompe, invalida todo lo demás.>

## Antes de empezar: conectar con el desarrollo del proyecto

1. **<Qué está decidido>:** lee `docs/decisiones.md` (<qué buscar>). Si no está decidido, pregunta; si supones, escríbelo.
2. **<Qué hay hecho>:** busca y reutiliza: `grep -rn "<patrón>" src tests`.
3. **<De dónde salen los datos o el contexto>:** `data/README.md` u otra pieza.

## Flujo

1. **<Paso>:** <qué hacer y con qué; criterio para decidir>.
2. **<Paso>:** <…>.

## Contrastar cada resultado con lo que debe salir

| Comprobación | Lo correcto | Si no se cumple |
|---|---|---|
| <qué se mira> | <valor de control, teoría o segunda vía> | <diagnóstico y arreglo> |

## Al terminar: dejar el trabajo conectado

- <Dónde va el código (`src/`) y su test (`tests/`)>.
- <Qué se documenta (`data/README.md`, `docs/decisiones.md`)>.
- <Qué revisor pasa antes del PR>.

## Errores que invalidan un resultado

- <Error concreto y por qué invalida>.

## Python

| Tarea | Función |
|---|---|
| <tarea> | `<función o patrón>` |

## Referencia

- [<fichero>.md](referencia/<fichero>.md): <qué contiene>.
````

## Notas

- **Frontmatter:** solo `description` y `when_to_use` salvo motivo. `disable-model-invocation: true` si tiene efectos (push, PR, borrar, desplegar): solo se lanza a mano y su descripción deja de ocupar contexto. `paths` si solo aplica a ciertos ficheros. `allowed-tools` preaprueba herramientas en el turno en que se invoca, no restringe.
- **Scripts:** en `scripts/`, solo stdlib, compatibles con Python 3.9 si un hook los ejecuta (`ruff.toml` lo fija), con errores claros y un test en `tests/`. En el `SKILL.md`, di si se ejecutan o se leen.
- **Ejemplos:** usa solo información que esté en el propio ejemplo o un hueco `<…>`; nunca cifras o hechos de fuentes sin su fuente.
