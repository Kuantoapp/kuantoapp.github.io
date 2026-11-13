# Registro de decisiones

Una línea por decisión, la más reciente arriba. Los agentes leen esto antes de trabajar.
Formato: `AAAA-MM-DD · decisión · por qué · PR/issue`

- 2026-11-13 · `dm-revisor-codigo` pasa a revisor obligatorio para cualquier `.py` de `src/` o `app/` · ruff no ve duplicados, abstracciones de un solo uso ni fallos silenciosos; cuesta unos 35.000 tokens por PR de código · revisor de código obligatorio
- 2026-11-13 · El código mínimo es el estándar de todo el código: reglas núcleo en `AGENTS.md`, procedimiento en `dm-codigo-minimo` y ruff con `ARG`, `ERA001`, `C901`, `PLR0913` y `T201` (exentas las herramientas de `.claude/` y `.github/`, los dobles de prueba de `tests/` y los `print` de `notebooks/`) · lo que una máquina puede comprobar no debe depender de que el agente se acuerde · código mínimo
- 2026-11-13 · Cada fuente de `data/README.md` lleva el SHA-256 de su fichero, descargado con fecha en el nombre (skill `dm-nueva-fuente`); las tablas de paso entre unidades tienen su propia skill (`dm-tablas-de-paso`) y las fechas clave del equipo van en la sección «Fechas clave» de este fichero · cada persona descarga su copia y sin huella nadie sabe si trabaja con los mismos datos; las tablas de paso cambian cifras sin que nada falle; y un hook de inicio de sesión recuerda a cada agente lo pendiente · contexto, tablas de paso y fuentes
- 2026-11-13 · Los diccionarios de datos (`<nombre>.DATA.md`, skill `dm-diccionario-datos`) se versionan en `docs/datos/` · las descargas originales son inmutables y `data/` no se versiona; así el equipo comparte el perfil sin descargar · revisores de ECC y diccionario
- 2026-11-13 · Hooks también en Windows: `py` delega en `py-windows` cuando detecta Git Bash y cada hook puede tener su `<script>_windows.py`; entradas `PowerShell` en `settings.json` para `data/raw` · un miembro del equipo trabaja en Windows y la herramienta PowerShell de Claude Code no la cubre el matcher `Bash`; los hooks de macOS no cambian · hooks Windows
- 2026-11-13 · Los hooks se lanzan con el Python del proyecto (`.venv`, si no `uv`, y como último recurso el del sistema) mediante `.claude/hooks/py`; el de `data/raw` bloquea si no puede ejecutarse · el Python de Apple no se puede actualizar y una protección que no arranca no debe dejar pasar en silencio · lanzador de hooks
- 2026-11-13 · `data/raw` única para todos los worktrees (enlace al checkout principal); `data/processed` propia de cada rama · no descargar dos veces y mantener una sola copia original, sin mezclar derivados de ramas distintas · revisores y datos
- 2026-11-13 · Revisores obligatorios por área: la CI exige en el PR el veredicto vigente de `dm-revisor-espacial`, `dm-auditor-calculos-normativos`, `dm-trazador-cifras` o `dm-verificador-fuentes` según lo que cambie · la calidad no puede depender de que el agente se acuerde de pedir la revisión · revisores y datos
- 2026-11-13 · La documentación relacionada se actualiza en el mismo PR (CI con `docs_al_dia.py` y hook `Stop`); excepción explícita «Docs: sin cambios — motivo» · que la documentación no se quede atrás con tantos cambios hechos por agentes · entorno y documentación
- 2026-11-13 · Python 3.14 (`.python-version`) instalado con uv; herramientas de desarrollo fijadas en `requirements-dev.txt` · la más reciente con ruedas para todo el stack en macOS, Linux y Windows (la 3.15 aún no tiene kriging); local y CI con las mismas versiones · entorno y documentación
- 2026-11-12 · Sin aprobación obligatoria de GitHub; check `revision`: Yeray e Izan mergean con CI verde, el resto necesita su aprobación · quitar al humano como cuello de botella sin abrir la puerta a código no revisado · estructura del repo
- 2026-11-12 · Flujo GitHub Flow: ramas `<usuario>/<tema>`, PR con squash a `main`, 1 revisión · tres personas con agentes, historial lineal y revisable · estructura del repo
- _Pendiente_ · Idea elegida (plan1 / plan2 / plan3)
- _Pendiente_ · Stack de `src/` y `app/`
- _Pendiente_ · Bases del concurso: criterios y pesos del jurado, formato de entrega y duración de la presentación

## Fechas clave

Fechas fijas que el equipo tiene que tener presentes (no son tareas: las tareas van en issues). El hook de inicio de sesión (`.claude/hooks/contexto.py`) muestra a cada agente las tres siguientes con los días que faltan. Formato: `| AAAA-MM-DD | hito |`.

| Fecha | Qué pasa |
|---|---|
| 2026-11-22 | Datos y cálculos congelados (propuesta de la ficha de plan1, por confirmar) |
| 2026-11-26 | Presentación ante el jurado (fecha de la organización) |
