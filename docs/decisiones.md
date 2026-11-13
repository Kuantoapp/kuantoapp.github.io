# Registro de decisiones

Una línea por decisión, la más reciente arriba. Los agentes leen esto antes de trabajar.
Formato: `AAAA-MM-DD · decisión · por qué · PR/issue`

- 2026-11-13 · Los hooks se lanzan con el Python del proyecto (`.venv`, si no `uv`, y como último recurso el del sistema) mediante `.claude/hooks/py`; el de `data/raw` bloquea si no puede ejecutarse · el Python de Apple no se puede actualizar y una protección que no arranca no debe dejar pasar en silencio · lanzador de hooks
- 2026-11-13 · `data/raw` única para todos los worktrees (enlace al checkout principal); `data/processed` propia de cada rama · no descargar dos veces y mantener una sola copia original, sin mezclar derivados de ramas distintas · revisores y datos
- 2026-11-13 · Revisores obligatorios por área: la CI exige en el PR el veredicto vigente de `dm-revisor-espacial`, `dm-auditor-calculos-normativos`, `dm-trazador-cifras` o `dm-verificador-fuentes` según lo que cambie · la calidad no puede depender de que el agente se acuerde de pedir la revisión · revisores y datos
- 2026-11-13 · La documentación relacionada se actualiza en el mismo PR (CI con `docs_al_dia.py` y hook `Stop`); excepción explícita «Docs: sin cambios — motivo» · que la documentación no se quede atrás con tantos cambios hechos por agentes · entorno y documentación
- 2026-11-13 · Python 3.14 (`.python-version`) instalado con uv; herramientas de desarrollo fijadas en `requirements-dev.txt` · la más reciente con ruedas para todo el stack en macOS, Linux y Windows (la 3.15 aún no tiene kriging); local y CI con las mismas versiones · entorno y documentación
- 2026-11-12 · Sin aprobación obligatoria de GitHub; check `revision`: Yeray e Izan mergean con CI verde, el resto necesita su aprobación · quitar al humano como cuello de botella sin abrir la puerta a código no revisado · estructura del repo
- 2026-11-12 · Flujo GitHub Flow: ramas `<usuario>/<tema>`, PR con squash a `main`, 1 revisión · tres personas con agentes, historial lineal y revisable · estructura del repo
- _Pendiente_ · Idea elegida (plan1 / plan2 / plan3)
- _Pendiente_ · Stack de `src/` y `app/`
