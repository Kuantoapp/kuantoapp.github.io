"""Valida subagentes, skills y CLAUDE.md según la doc de Claude Code y las reglas de .claude/README.md.

Claude Code ignora en silencio los agentes mal formados y los campos desconocidos,
así que estos errores solo se ven aquí. Uso: python .github/scripts/validar_claude.py [raíz]
"""

import re
import sys
from pathlib import Path

import yaml

# Campos de https://code.claude.com/docs/en/sub-agents
CAMPOS_AGENTE = {
    "name", "description", "tools", "disallowedTools", "model", "permissionMode", "maxTurns",
    "autoCompactWindow", "skills", "mcpServers", "hooks", "memory", "background", "omitClaudeMd",
    "effort", "isolation", "color", "initialPrompt", "experimental",
}  # fmt: skip
# Campos de https://code.claude.com/docs/en/skills
CAMPOS_SKILL = {
    "name", "description", "when_to_use", "argument-hint", "arguments", "disable-model-invocation",
    "user-invocable", "allowed-tools", "disallowed-tools", "model", "effort", "context", "agent",
    "background", "hooks", "paths", "shell", "metadata", "license", "compatibility",
}  # fmt: skip
# Claude Code quita descripciones del listado si no caben en su presupuesto: cortas y con el caso clave primero
MAX_DESC_AGENTE = 400
MAX_DESC_SKILL = 800
MODELOS = {"sonnet", "opus", "haiku", "fable", "inherit"}
COLORES = {"red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"}
# Prefijo dm-: una skill personal con el mismo nombre taparía la del proyecto
KEBAB = re.compile(r"^dm(-[a-z0-9]+)+$")
FILA = re.compile(r"^\|\s*`?([^|`]+?)`?\s*\|\s*(agente|skill)\s*\|")


def frontmatter(ruta: Path) -> tuple[dict | None, str]:
    texto = ruta.read_text(encoding="utf-8")
    if not texto.startswith("---\n"):
        return None, "falta el bloque --- en la línea 1"
    fin = texto.find("\n---", 4)
    if fin == -1:
        return None, "el bloque --- no se cierra"
    try:
        datos = yaml.safe_load(texto[4:fin]) or {}
    except yaml.YAMLError as e:
        return None, f"YAML inválido: {e}"
    if not isinstance(datos, dict):
        return None, "el frontmatter no es un mapa clave: valor"
    return datos, ""


def validar(raiz: Path) -> list[str]:
    errores: list[str] = []
    claude = raiz / ".claude"
    vistos: dict[str, str] = {}

    if (claude / "commands").exists():
        errores.append(".claude/commands/: usa .claude/skills/<nombre>/SKILL.md")

    for ruta in sorted((claude / "agents").rglob("*.md")):
        rel = ruta.relative_to(raiz)
        fm, err = frontmatter(ruta)
        if fm is None:
            errores.append(f"{rel}: {err}")
            continue
        name = str(fm.get("name", ""))
        for campo in sorted(set(fm) - CAMPOS_AGENTE):
            errores.append(
                f"{rel}: campo desconocido '{campo}' (Claude Code lo ignoraría)"
            )
        if not KEBAB.fullmatch(name):
            errores.append(
                f"{rel}: name '{name}' debe empezar por dm- y ir en minúsculas con guiones"
            )
        elif ruta.stem != name:
            errores.append(f"{rel}: el fichero debe llamarse {name}.md")
        desc = str(fm.get("description", "")).strip()
        if not desc:
            errores.append(f"{rel}: falta description")
        elif len(desc) > MAX_DESC_AGENTE:
            errores.append(
                f"{rel}: description de {len(desc)} caracteres (máx. {MAX_DESC_AGENTE}); el detalle va en el cuerpo"
            )
        if not fm.get("tools"):
            errores.append(f"{rel}: falta tools (lista mínima de herramientas)")
        modelo = fm.get("model")
        if modelo and modelo not in MODELOS and not str(modelo).startswith("claude-"):
            errores.append(f"{rel}: model '{modelo}' no válido")
        if fm.get("permissionMode") == "bypassPermissions":
            errores.append(f"{rel}: permissionMode bypassPermissions prohibido")
        if fm.get("color") and fm["color"] not in COLORES:
            errores.append(f"{rel}: color '{fm['color']}' no válido")
        if name in vistos:
            errores.append(f"{rel}: name '{name}' repetido")
        vistos[name] = "agente"

    for carpeta in (
        sorted(p for p in (claude / "skills").iterdir() if p.is_dir())
        if (claude / "skills").exists()
        else []
    ):
        rel = carpeta.relative_to(raiz)
        skill = carpeta / "SKILL.md"
        if not KEBAB.fullmatch(carpeta.name) or carpeta.name.lower() == "synced":
            errores.append(
                f"{rel}: nombre de carpeta no válido (dm-, minúsculas con guiones)"
            )
        if not skill.exists():
            errores.append(f"{rel}: falta SKILL.md")
            continue
        fm, err = frontmatter(skill)
        if fm is None:
            errores.append(f"{rel}/SKILL.md: {err}")
            continue
        for campo in sorted(set(fm) - CAMPOS_SKILL):
            errores.append(f"{rel}/SKILL.md: campo desconocido '{campo}'")
        if fm.get("name") and fm["name"] != carpeta.name:
            errores.append(
                f"{rel}/SKILL.md: name '{fm['name']}' no coincide con la carpeta"
            )
        desc = str(fm.get("description", "")).strip()
        if not desc:
            errores.append(f"{rel}/SKILL.md: falta description")
        elif len(desc) + len(str(fm.get("when_to_use", ""))) > MAX_DESC_SKILL:
            errores.append(
                f"{rel}/SKILL.md: description + when_to_use > {MAX_DESC_SKILL} caracteres"
            )
        if len(skill.read_text(encoding="utf-8").splitlines()) > 500:
            errores.append(
                f"{rel}/SKILL.md: más de 500 líneas; mueve detalle a ficheros de apoyo"
            )
        if carpeta.name in vistos:
            errores.append(f"{rel}: '{carpeta.name}' ya existe como agente")
        vistos[carpeta.name] = "skill"

    indice_md = claude / "README.md"
    indice = {}
    if indice_md.exists():
        # Solo la sección "## Índice": otras tablas del README también nombran "skill"
        texto = indice_md.read_text(encoding="utf-8")
        seccion = texto.split("## Índice", 1)[-1].split("\n## ", 1)[0]
        for linea in seccion.splitlines():
            if m := FILA.match(linea):
                indice[m.group(1).strip()] = m.group(2)
    for nombre, tipo in vistos.items():
        if indice.get(nombre) != tipo:
            errores.append(
                f".claude/README.md: falta la fila de '{nombre}' ({tipo}) en el índice"
            )
    for nombre in sorted(set(indice) - set(vistos)):
        errores.append(
            f".claude/README.md: la fila '{nombre}' no corresponde a ningún fichero"
        )

    for md in ("CLAUDE.md", "AGENTS.md"):
        if (raiz / md).exists() and len(
            (raiz / md).read_text(encoding="utf-8").splitlines()
        ) > 200:
            errores.append(f"{md}: más de 200 líneas (la doc recomienda menos)")
    return errores


if __name__ == "__main__":
    errores = validar(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    print("\n".join(errores) or "Agentes, skills y CLAUDE.md correctos")
    sys.exit(1 if errores else 0)
