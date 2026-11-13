Closes #

## Qué cambia
<!-- Resumen corto. Título del PR: tipo(área): qué cambia -->

## Cómo probarlo
<!-- Comando o pasos -->

## Revisión por agentes
<!-- Pega aquí la salida de `python .github/scripts/revisiones.py --resumen` (ver AGENTS.md, «Revisores obligatorios») -->

## Agente
- [ ] Lo ha generado un agente y **he leído el diff entero**
- [ ] Toca solo lo que pide la issue (nada "ya que estaba")

## Checklist
- [ ] `ruff check . && pytest -q` en verde
- [ ] Sin dependencias nuevas (o justificadas aquí)
- [ ] Sin secretos, datos ni ficheros pesados
- [ ] Si decidí algo que afecta al equipo, está en `docs/decisiones.md`
- [ ] Documentación relacionada al día (si no hace falta, escribe abajo «Docs: sin cambios — motivo»)
