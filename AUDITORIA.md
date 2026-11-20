# Auditoría del proyecto «¿Me sobra?» y viabilidad de integrar la Idea 2

Fecha: 2026-11-19. Referencia auditada: `origin/main` en `0656270` (#315). Solo lectura: no se ha tocado código, ramas, issues ni PRs. Este fichero está sin versionar.

Cómo leer las etiquetas: **[HECHO]** es algo comprobado con un comando sobre `origin/main` o GitHub; **[INFERENCIA]** es una conclusión que saco de esos hechos y que puede discutirse. Los hallazgos de severidad alta los he comprobado yo; el resto viene de tres análisis delegados y lleva su evidencia.

## 1. Resumen ejecutivo

El producto va por delante del plan y la entrega va por detrás. Todas las tareas de las fases 0, 1 y 2 del plan están cerradas y el hito del 20-11 (herramienta y análisis básicos en `main`) se cumplió un día antes. En cambio, el bloque de entrega está entero sin empezar: no existe el comando único que regenera los datos, no hay congelación, ni nota metodológica, ni guion, ni diapositivas, y la web nunca se ha publicado. Quedan 45 issues abiertas a siete días de la presentación, y 27 de ellas nacieron fuera del plan, varias en los dos últimos días.

Las tres acciones más urgentes:

1. **Empezar ya el comando único (#104) y ensayar una regeneración completa antes del 22-11.** De él cuelgan en cadena la congelación, la web final, el README, la nota metodológica y el pitch, y los datos publicados hoy son del 16-11.
2. **Probar la publicación de la web antes del 23-11.** El despliegue ha fallado las 12 veces que se ha ejecutado, porque el repositorio sigue privado; tal como está decidido, la primera prueba real sería el mismo día del plazo.
3. **Cerrar el alcance y repartir el pitch hoy.** El guion (#111) y las diapositivas (#112) no tienen dueño, y hay que decidir qué trabajo nuevo (Bono, cesta, coche) entra en la congelación y cuál se queda fuera.

Sobre la Idea 2: no conviene integrarla como código ahora. Sí cabe como una diapositiva de continuidad en el pitch, sin tocar el producto (detalle en la sección 4).

## 2. Hallazgos de la Fase 1

### 2.1 Issues olvidados

| # | Sev. | Hallazgo | Evidencia | Acción propuesta |
|---|---|---|---|---|
| 1.1 | **Alta** | El guion y las diapositivas, que el plan marca como imprescindibles, no tienen dueño. La decisión sobre quién lleva ese tercer carril vencía el 16-11 y no consta tomada. | [HECHO] #111 y #112 abiertas y sin asignar; `docs/decisiones.md` no contiene ninguna línea sobre el tercer carril (D7 del plan); no existe `docs/pitch/`. | Asignarlas hoy. El plan dice que, sin responsable, pasan a Yeray e Izan. |
| 1.2 | Media | El piloto con usuarios sigue abierto aunque su señal de corte ya saltó. | [HECHO] #113 y #114 sin dueño y sin actividad desde el 14 y el 17-11; el plan (sección 1) dice «el 17 sin responsable → fuera». | Cerrarlas como no planificadas con una nota, o asignarlas con el alcance reducido que prevé el plan (prueba en local con cinco personas). |
| 1.3 | Media | Varias piezas opcionales tienen la señal de corte vencida o a horas de vencer y nadie ha registrado si siguen. | [HECHO] Coche y segundo sueldo (#96, #97): sin empezar, corte el 20-11 a las 12:00. Nóminas reales (#115): corte el 18-11, sin actividad desde el 15-11. Fin del descuento del abono (#102) e informe ampliado (#103): sin empezar, corte el 21-11. | Decidir cada una hoy y dejarlo en `docs/decisiones.md`; cerrar las que se caen. |
| 1.4 | Media | El resumen de 100 palabras que pide la organización antes del 24-11 está sin empezar. | [HECHO] #191 abierta, asignada a Yeray, sin PR. Es un requisito de participación. | Redactarlo el 22-23, en cuanto estén congeladas las cifras. |
| 1.5 | Baja | La issue que pide planificar la Idea 2 lleva abierta y sin dueño desde el 14-11. | [HECHO] #63; no existe `docs/plan-cerca/`. | Cerrarla o reformularla según la sección 4. |
| 1.6 | — | Sin hallazgo: no hay tareas del plan sin issue ni referencias a issues inexistentes. | [HECHO] Las 58 tareas de la sección 3 del plan tienen issue. Ningún commit ni documento cita un número que no exista. Las issues cerradas sin PR de cierre (#30, #257, #68, #91) tienen su resultado en `main`. | Ninguna. |

### 2.2 Problemas arrastrados

| # | Sev. | Hallazgo | Evidencia | Acción propuesta |
|---|---|---|---|---|
| 2.1 | Media | Hay soluciones provisionales que esperan a issues aún abiertas. Si esas issues se recortan, lo provisional pasa a ser lo que se presenta. | [HECHO] `src/mesobra/transporte.py:435` y `api_estatica.py:407` («hasta que #164»); `transporte.py:368` («vale hasta #161»); `app/index.html:88` y `app/vista.js:375` («por ahora solo transporte público», pendiente de #96 y #97); `simulacion.py:178` duplica un cálculo de `neto.py`. | Al decidir el alcance (1.3), revisar estas cinco marcas: o se resuelven, o se declaran como límite en la nota metodológica (#109). |
| 2.2 | Media | El único PR abierto no puede fusionarse. | [HECHO] PR #300 (`yeraybc/docs-bono`, cierra #297): conflicto en `docs/decisiones.md`, sin auto-merge, 7 commits por detrás de `main`. | Rebasar y fusionar hoy; es documentación. |
| 2.3 | Baja | Queda una rama remota huérfana. | [HECHO] `origin/yeraybc/hook-sin-coautor-claude`: su PR #283 se cerró sin fusionar y su issue #282 se descartó. | Borrarla. |
| 2.4 | Baja | En el equipo de Izan hay 28 ramas locales y 4 worktrees de PRs ya fusionados, y `main` local va 3 commits por detrás. | [HECHO] Todas las ramas locales corresponden a un PR fusionado; `paso-secciones-publicar` no tiene PR propio pero su punta es la del PR #217. El worktree `../dm-ficha-ipc` tiene sin versionar `app/datos/sdm/`, que es salida regenerable. | Limpiar tras confirmarlo (pregunta 7). |
| 2.5 | — | Sin hallazgo: no hay marcas antiguas ni trabajo duplicado entre ramas. | [HECHO] Cero `TODO`, `FIXME` o `HACK`. Hay 25 comentarios `shortcut:`, todos escritos entre el 13 y el 19-11 (el proyecto tiene ocho días). | Ninguna. |

### 2.3 Deriva respecto al plan original

| # | Sev. | Hallazgo | Evidencia | Acción propuesta |
|---|---|---|---|---|
| 3.1 | **Alta** | El alcance crece cuando tocaría cerrarlo. El plan solo permite abrir trabajo nuevo si el 20 por la noche todo lo imprescindible está fusionado, y el bloque de entrega no lo está. | [HECHO] 45 issues abiertas: 18 con identificador del plan y 27 nacidas después. Entre el 18 y el 19-11 se abrieron el rediseño del criterio del Bono (#301, #302), la cesta según renta (#312), los hogares con tres hijos o más (#183, #290) y cuatro correcciones de polos y tarifas (#307, #313, #316, #317). [INFERENCIA] #301 y #302 cambian datos que se congelan el 22. | Lista cerrada de lo que entra en la congelación; el resto se aparca con una nota. |
| 3.2 | Media | Se ha construido bastante más análisis del previsto. Está justificado en `docs/decisiones.md`, pero el plan no se actualizó. | [HECHO] Sin tarea en el plan: `bono_inferencia.py` (modelos espaciales; el plan pedía una correlación controlada por renta), `censo2021.py`, `sobrecarga_ecv.py`, `lineas_estimadas.py`, `paso_secciones.py`, `matriz_trabajo.py` y la banda de contrato nuevo de la AEAT en `alquiler.json`. Cada uno tiene su línea de decisión. | Ninguna sobre el código. Contarlo en el pitch como profundidad, y no ampliar más. |
| 3.3 | Media | La decisión de no publicar la sobrecarga dejó restos que la contradicen. | [HECHO] `docs/decisiones.md:19` (18-11) dice que no se publica; `docs/decisiones.md:33` (16-11) sigue diciendo que Smart Data Models publica `sobrecarga_40` y `sobrecarga_30`; `src/mesobra/sdm.py:45-63` conserva esas entradas; el título de #103 sigue siendo «informe con sobrecarga». | Marcar la línea 33 como sustituida y ajustar #103. |
| 3.4 | Media | Dos decisiones humanas del plan siguen sin cerrar. | [HECHO] La fecha de congelación figura «por confirmar» en `docs/decisiones.md:104`. El tercer carril, ver 1.1. La publicación se movió del 18 al 23-11 y eso sí está documentado (`docs/decisiones.md:30`). | Confirmar el 22 por escrito. |
| 3.5 | Baja | La decisión sobre hogares con tres hijos o más está abierta y bloquea dos issues. | [HECHO] #290 sin resolver; #183 y parte de #164 dependen de ella. | Decidir; con el calendario actual, la respuesta barata es «no». |

### 2.4 Otros riesgos de proyecto

| # | Sev. | Hallazgo | Evidencia | Acción propuesta |
|---|---|---|---|---|
| 4.1 | **Alta** | El camino crítico de la entrega no ha empezado y pasa casi entero por una persona. | [HECHO] Cadena de dependencias según los cuerpos de las issues: #104 (comando único) → #105 (congelar zonas y tiempos) → #106 (congelar euros y análisis) → #107, #108, #109, #111 → #112. Ninguna tiene PR. No existe `src/mesobra/__main__.py` ni ninguna etiqueta git. Izan lleva #104, #105, #107 y #108, además de #96, #97, #161, #164, #307, #311 y #316. | Empezar #104 ya y repartir: #107 o #108 pueden cambiar de manos. |
| 4.2 | **Alta** | La publicación de la web no se ha probado nunca. | [HECHO] El workflow `Pages` suma 12 ejecuciones y 12 fallos desde el 17-11; el repositorio es privado; #92 («publica app/ en GitHub Pages») se cerró el 17-11 y su sustituta #255 no tiene actividad. `README.md:33` da la URL como publicada. [INFERENCIA] Con la decisión actual, el primer despliegue real ocurre el día del plazo, sin margen si falla por otra causa (rutas relativas, tamaño de los JSON, caché). | Adelantar la apertura del repositorio y la activación de Pages, o al menos ensayar el despliegue en una copia pública. |
| 4.3 | **Alta** | Los datos que usa la web están desfasados respecto al código, y la primera regeneración completa coincidirá con la congelación. | [HECHO] `app/datos/tiempos.json` y `zonas.geojson` son del 16-11 (commit `48e64fe`). Los 16 polos de empleo, fusionados el 19-11 (#308, #314), no aparecen en ningún fichero de `app/datos/`. En `tiempos.json`, 28.207 de 39.601 pares origen × destino no tienen tiempo (71 %), y Arroyomolinos solo tiene ruta a 8 destinos (#311, abierta). | Ensayo completo el 20 o el 21 (el plan ya lo prevé para el 21) y decidir antes si #311 entra. |
| 4.4 | Media | Hay módulos fusionados que ningún pipeline ejecuta, así que su resultado no llega a la web. | [HECHO] `sdm.py`: el plan (línea 109) exige `app/datos/sdm/` y la carpeta no existe en `main`. `bono_inferencia.py`: `app/informe.html:75-81` cita `bono_inferencia.json` como fuente de varias cifras y ese fichero no está publicado ni versionado. `simulacion.py` (#296): `analisis.json` no trae su bloque. `matriz_trabajo.py` (#315): nadie lo importa todavía. [INFERENCIA] El texto de #104 nombra los tres pipelines y `sdm`, pero no `bono_inferencia`. | Añadir a #104 la lista completa de pasos y publicar `bono_inferencia.json` en `app/datos/` (o cambiar la cita). |
| 4.5 | Media | La regeneración completa quizá no pueda ejecutarse en cualquier equipo. | [HECHO] Según el aviso de inicio de sesión, en el equipo de Izan faltan 21 descargas de `data/README.md`. Una de ellas, el Censo 2021 a medida del 16-11, no se puede volver a bajar igual porque el INE redondea al azar en cada consulta (#210). [INFERENCIA] #104 comprueba los SHA-256 antes de ejecutar, así que fallaría en ese equipo. | Decidir en qué equipo se congela y copiar ahí los ficheros que faltan. |
| 4.6 | Media | La web tiene enlaces rotos entre sus piezas. | [HECHO] `app/index.html` no enlaza `informe.html` (solo existe el enlace inverso, `informe.html:31`). `app/index.html:37` remite a una nota metodológica que no existe (#109). | Incluirlo en #107. |
| 4.7 | Media | Documentación que no coincide con lo que hay. | [HECHO] `README.md:29` dice que `pyproject.toml` no declara dependencias y declara dos (`pyproject.toml:11`). El README no explica cómo reproducir ni cómo instalar el servidor MCP (#108). `docs/decisiones.md:94` da las bases por pendientes mientras la línea 49 ya recoge parte. Faltan en `data/README.md` las filas de los boletines de tarifas (#299). | Resolver dentro de #108 y #299. |
| 4.8 | Baja | `docs/decisiones.md` provoca conflictos porque todos los PR escriben en sus primeras líneas. | [HECHO] Es el conflicto del PR #300. [INFERENCIA] Se repetirá durante la congelación, cuando coincidan más PRs. | Fusionar pronto los PRs de documentación. |
| 4.9 | — | Sin hallazgo: no hay ramas que dependan unas de otras. | [HECHO] Solo hay dos ramas remotas además de `main`. Los bloqueos son entre issues (4.1). | Ninguna. |

## 3. Tabla de ramas

«Divergencia» es commits por detrás / por delante de `origin/main`. Las ramas locales se fusionaron con squash, y por eso siguen figurando «por delante» aunque su contenido ya esté en `main`.

| Rama | Propósito | Estado | Divergencia | Recomendación |
|---|---|---|---|---|
| `origin/yeraybc/docs-bono` | Decisiones de la simulación del Bono (PR #300, cierra #297) | Abierta, con conflicto en `docs/decisiones.md` | 7 / 4 | **Rebasar** y mergear |
| `origin/yeraybc/hook-sin-coautor-claude` | Hook que bloquea la coautoría de Claude (PR #283) | PR cerrado sin fusionar, issue descartada | 16 / 1 | **Cerrar** (borrar) |
| `main` (local) | Rama principal | 3 commits por detrás de `origin/main` | 3 / 0 | `git pull --rebase` |
| `izan-diaz/polos-ajuste`, `polos-empleo`, `ficha-ipc`, `mcp-servidor` | Polos de empleo, ficha con IPC, servidor MCP (PRs #314, #308, #304, #298) | Fusionadas el 19-11. `polos-ajuste` está en el worktree `../dm-ficha-ipc` | 3–8 / 2–10 | **Cerrar** |
| `izan-diaz/atribucion-leyenda`, `marca-fixtures`, `leyenda-ficha`, `formulario-mapa`, `calculo-js` | Web: leyenda, formulario, mapa y cálculo en el navegador (PRs #265, #268, #244, #241, #239) | Fusionadas el 17 y 18-11 | 25–41 / 1–5 | **Cerrar** |
| `izan-diaz/api-territorio`, `calculo`, `calculo-errores`, `paso-secciones`, `paso-secciones-publicar` | Primera API de territorio, cálculo de referencia, tabla de paso de secciones (PRs #229, #216, #228, #217) | Fusionadas el 16-11. `api-territorio` está en el worktree `../dm-territorio`. `paso-secciones-publicar` no tiene PR propio; su punta es la del PR #217 | 45–53 / 2–8 | **Cerrar** |
| `izan-diaz/lineas-estimadas`, `centro-poblacion`, `tiempos`, `zonas`, `decisiones-corona`, `decisiones-tiempos` | Zonas, tiempos con r5py y líneas reconstruidas (PRs #181, #177, #174, #171, #172, #176) | Fusionadas el 15 y 16-11. Dos están en los worktrees `../dm-lineas-estimadas` y `../dm-tiempos` | 72–78 / 1–4 | **Cerrar** |
| `izan-diaz/paquete-mesobra`, `plan-desarrollo`, `plan1-ficha-abogado`, `plan1-ficha-unificada`, `plan1-idea-definitiva` | Paquete, plan y fichas de la Idea 1 (PRs #118, #117, #54, #48, #46) | Fusionadas el 14-11 | 106–116 / 1–4 | **Cerrar** |
| `izan-diaz/hooks-windows`, `claude-revisores-ecc`, `izan` | Hooks para Windows, revisores y primeras fichas (PRs #31, #32, #8, #9) | Fusionadas entre el 11 y el 13-11. La punta local de `hooks-windows` no es la que se fusionó; `main` tiene la versión final | 128–145 / 0–2 | **Cerrar** |

Ninguna rama está en «continuar»: hoy no hay trabajo en curso con rama, salvo el PR #300. Límite: no veo las ramas locales de Yeray.

## 4. Fase 2: viabilidad de integrar la Idea 2 («Cerca»)

### Qué es la Idea 2 y qué comparte ya con la Idea 1

«Cerca» mide si las personas con más necesidad tienen cerca los servicios públicos (centros de salud, farmacias, colegios, servicios sociales) y dónde convendría abrir uno nuevo. Trabaja por sección censal y está pensada para el personal técnico que reparte inversión; la Idea 1 trabaja por zona y está pensada para un hogar joven que decide dónde vivir. [HECHO] La ficha de la Idea 2 recibió un veredicto «NO APTO» de `dm-abogado-del-diablo` el 14-11 y no se ha vuelto a revisar (`propuesta-B-unificada.md:9`); tiene nueve verificaciones pendientes, entre ellas licencias del Catastro y de CartoCiudad, y no trae estimaciones de esfuerzo.

[HECHO] Lo que podía compartirse sin coste ya se comparte: las 199 zonas son las mismas, y la renta por sección, el Censo 2021, el seccionado de 2025, OpenStreetMap y los GTFS del Consorcio ya están en `data/README.md`. Lo que distingue a la Idea 2 es todo nuevo: puntos de servicios, edificios del Catastro, modelo de elevación, perfiles de peatón, el algoritmo de ubicación y la auditoría del plan de inversiones.

Asunción de tamaños: S es hasta media jornada de una persona con su agente, incluida la revisión obligatoria; M es de uno a dos días; L es de tres días en adelante. Son estimaciones mías.

### Vías evaluadas

| Vía | Qué aporta | Qué toca del proyecto actual | Esfuerzo y asunciones | Riesgos | Choque con la Fase 1 |
|---|---|---|---|---|---|
| **Datos:** uno o dos conjuntos del catálogo regional como contexto de cada zona (paro registrado por municipio; recuento de centros sanitarios, farmacias o colegios por zona) | Más conjuntos del catálogo regional en uso, que es la regla central del concurso. Un dato de contexto en la ficha de zona («qué hay aquí además del precio»). | Una fuente nueva por conjunto (descarga, fila en `data/README.md`, función de carga y test), un fichero nuevo en `app/datos/` y unas líneas en la ficha de `app/vista.js`. | **S** por conjunto si es una tabla por municipio. **M** si son puntos que hay que asignar a zonas. Asumo que las coordenadas son utilizables, y la propia ficha lo deja sin verificar para los centros sociales. | Aporta poco al relato de «cuánto me sobra». No se sabe si el jurado cuenta el número de conjuntos (#143, sin respuesta). | Con 3.1 (más alcance) y 4.3 (añade un fichero justo antes de congelar). Solo es compatible si se hace después de la congelación, como fichero aparte que no altere los ya congelados. |
| **Análisis:** un capítulo sobre «la media de la zona oculta diferencias internas», aplicado al esfuerzo de alquiler por sección | Refuerza el informe para la Administración con un mensaje propio de la Idea 2. | `renta.py`, `alquiler.py`, `paso_secciones.py`, `pipeline_analisis.py`, `app/informe.html`. | **M**. Asumo que alquiler y renta por sección sirven tal como están. | [HECHO] La única estimación por sección que se intentó, la sobrecarga, no pasó su control y se retiró (`docs/decisiones.md:19`). [INFERENCIA] Este capítulo puede acabar igual. Exige revisión espacial. | Con 3.1 y 3.2 (el análisis ya excede el plan) y con 4.1 (lo haría Yeray, que tiene la congelación de euros, la nota metodológica y el Bono). |
| **Análisis:** auditoría del reparto del plan de inversiones regional frente a la necesidad | Un segundo caso de «ayuda frente a necesidad», junto al del Bono. | Fuentes nuevas (boletín oficial, presupuestos municipales) y un módulo nuevo. | **L**. | Fuente y cifras sin verificar; faltan los presupuestos de 2022 y 2023. | Descartada: no cabe antes del 22. |
| **Funcionalidad:** acceso a pie a servicios, simulador de ubicaciones, pestaña técnica | El núcleo de la Idea 2. | Matrices nuevas edificio × servicio, capa de secciones, pestaña nueva. | **L** cada una. | Licencias sin verificar. La ficha propone DuckDB y PMTiles, y el stack decidido los excluye (`docs/decisiones.md:74`). | Descartada: es un producto aparte. |
| **Relato:** una diapositiva de «siguiente paso» que presenta la Idea 2 como extensión de la misma infraestructura | Enseña que las zonas, los tiempos de viaje, la tabla de paso de secciones y el servidor MCP sirven para otra pregunta de política pública. | Solo `docs/pitch/` (#112). Ningún código ni dato. | **S**. Asumo que el formato del pitch admite una diapositiva de continuidad. | Ninguno técnico. No debe prometer cifras de la Idea 2. | Ninguno. Depende de que #112 tenga dueño (1.1). |

### Recomendación

**No integrar la Idea 2 como código ni como datos antes de la congelación del 22-11.** Las razones salen de la Fase 1:

- El plan ya tiene una regla para esto: los extras solo se abren si el 20 por la noche todo lo imprescindible está fusionado y hay una persona con un agente libre. No se cumple ninguna de las dos condiciones (4.1).
- El proyecto tiene un problema de alcance creciente (3.1). Cualquier vía añade trabajo a las mismas dos personas que tienen el bloque de entrega sin empezar.
- La única vía de análisis con sentido repite el tipo de estimación que ya falló una vez.

**Lo que sí recomiendo:** usar la Idea 2 en el pitch como diapositiva de continuidad (vía «Relato», S) y decidir el destino de #63.

**Qué tendría que cambiar para que convenga la vía de datos**, que es la única barata. Tendrían que darse las tres condiciones:

1. La congelación del 22-11 sale bien: #104, #105 y #106 fusionadas, y la web publicada y comprobada.
2. La organización confirma que valora el número de conjuntos del catálogo regional usados (#143).
3. Hay una persona libre el 23 o el 24 que no esté en el guion, las diapositivas ni la nota metodológica.

Entonces se podría añadir un conjunto por municipio como contexto en la ficha de zona, en un fichero aparte. Sin la segunda condición, el beneficio no compensa el riesgo de tocar la web después de congelar.

### Asunciones de esta fase

- No he verificado las fuentes ni las licencias de la Idea 2; uso lo que su ficha declara pendiente.
- No he comprobado que los conjuntos del catálogo que cito para la vía de datos tengan la cobertura y el formato esperados.
- Doy por buenas las fechas de `docs/decisiones.md` (22, 23, 24 y 26-11).

## 5. Preguntas abiertas que solo tú puedes responder

1. **¿Quién lleva el guion y las diapositivas?** El contexto del proyecto habla de un equipo de tres, pero todos los commits y todas las asignaciones son de Izan y de Yeray. ¿Hay una tercera persona disponible?
2. **¿Se confirma el 22-11 como fecha de congelación?** Y, con ella, ¿entran o no el rediseño del criterio del Bono (#301, #302), la corrección de Arroyomolinos y del tope de 120 minutos (#311) y la cesta según renta (#312)?
3. **¿El coche y el segundo sueldo (#96, #97) se caen?** Su señal de corte es el 20-11 a las 12:00 y no están empezados.
4. **¿Qué impide hacer público el repositorio antes del 23-11?** Si no hay un motivo de fondo, adelantarlo elimina el riesgo 4.2.
5. **¿En qué equipo se ejecuta la regeneración completa** y quién tiene la copia del Censo 2021 del 16-11 y las otras 20 descargas que faltan en el tuyo?
6. **¿Ha respondido la organización** sobre los criterios y sobre si cuenta el número de conjuntos del catálogo (#143)? De eso depende la única vía barata de la Idea 2.
7. **¿Puedo dar por buena la limpieza** de las 28 ramas locales, los 4 worktrees y la rama remota huérfana? No he borrado nada.
8. **¿Hogares con tres hijos o más (#290): sí o no?**
9. **¿Hay trabajo en ramas locales de Yeray** que no esté subido? Desde aquí no se ve.

## Lo que no he comprobado

- La calidad del código, de los tests, de las matemáticas y de las fuentes, por estar fuera del alcance.
- El contenido de los PRs fusionados más allá de sus referencias de cierre.
- La correspondencia entre los datos de ejemplo de `tests/fixtures/api/` y `app/datos/`.
- La ficha `propuesta-A-unificada.md` completa; he trabajado con el plan de desarrollo, que la resume.
- Si las 21 descargas que faltan siguen faltando: es lo que dijo el aviso de inicio de sesión, no lo he vuelto a contar.
