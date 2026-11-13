"""Valida subagentes, skills y CLAUDE.md según la doc de Claude Code y las reglas de .claude/README.md.

Claude Code ignora en silencio los agentes mal formados y los campos desconocidos,
así que estos errores solo se ven aquí.
Uso: python .github/scripts/validar_claude.py [raíz]
     python .github/scripts/validar_claude.py --hook   (PostToolUse: valida si se tocó .claude/, AGENTS.md o CLAUDE.md)
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except (
    ImportError
):  # el hook no debe romper la sesión de quien no tenga pyyaml; la CI sí lo exige
    yaml = None

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
# Guía de autoría de skills: la description va en tercera persona
SEGUNDA_PERSONA = re.compile(
    r"\b(úsala|úsame|usa esta|puedes|te ayud\w*|ayudarte)\b", re.IGNORECASE
)
# Quien revisa no corrige: sin herramientas de edición
SOLO_LECTURA = re.compile(r"revisor|auditor|verificador|trazador|abogado")
EDICION = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
ENLACE = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")


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
        herramientas = fm.get("tools") or []
        if isinstance(herramientas, str):
            herramientas = [h.strip() for h in herramientas.split(",")]
        if SOLO_LECTURA.search(name) and EDICION & set(herramientas):
            errores.append(
                f"{rel}: un {SOLO_LECTURA.search(name).group(0)} solo lee: quita {sorted(EDICION & set(herramientas))} de tools"
            )
        if SOLO_LECTURA.search(name) and fm.get("memory"):
            errores.append(
                f"{rel}: un {SOLO_LECTURA.search(name).group(0)} no lleva memory (reactiva la escritura y su juicio debe salir de la evidencia)"
            )
        for s in fm.get("skills") or []:
            skill_md = claude / "skills" / str(s) / "SKILL.md"
            if not skill_md.exists():
                errores.append(f"{rel}: precarga la skill '{s}', que no existe")
            elif (frontmatter(skill_md)[0] or {}).get("disable-model-invocation"):
                errores.append(
                    f"{rel}: '{s}' tiene disable-model-invocation y no se puede precargar"
                )
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
        if not str(fm.get("when_to_use", "")).strip():
            errores.append(
                f"{rel}/SKILL.md: falta when_to_use (frases o preguntas que la disparan)"
            )
        if SEGUNDA_PERSONA.search(desc):
            errores.append(
                f"{rel}/SKILL.md: description en tercera persona («Prepara…», no «Úsala…» ni «puedes…»)"
            )
        cuerpo = skill.read_text(encoding="utf-8")
        enlazados = set()
        for destino in ENLACE.findall(cuerpo):
            if "://" in destino:
                continue
            if not (carpeta / destino).exists():
                errores.append(f"{rel}/SKILL.md: enlace roto a {destino}")
            enlazados.add((carpeta / destino).resolve())
        for apoyo in sorted(carpeta.rglob("*.md")):
            if apoyo == skill:
                continue
            rel_apoyo = apoyo.relative_to(raiz)
            if apoyo.resolve() not in enlazados:
                errores.append(
                    f"{rel_apoyo}: no se enlaza desde SKILL.md (Claude no lo encontraría)"
                )
            lineas = apoyo.read_text(encoding="utf-8").splitlines()
            if len(lineas) > 100 and not any(
                "contenido" in x.lower() for x in lineas[:15]
            ):
                errores.append(
                    f"{rel_apoyo}: más de 100 líneas sin índice «Contenido» al principio"
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


VIGILADOS = (
    ".claude/agents/",
    ".claude/skills/",
    ".claude/README.md",
    "AGENTS.md",
    "CLAUDE.md",
)


def desde_hook() -> int:
    """PostToolUse: si se editó algo vigilado, valida todo y devuelve los errores al agente (exit 2)."""
    raiz = Path(os.environ.get("CLAUDE_PROJECT_DIR") or ".").resolve()
    try:
        ruta = Path(json.load(sys.stdin).get("tool_input", {}).get("file_path") or "")
        rel = ruta.resolve().relative_to(raiz).as_posix()
    except Exception:  # noqa: BLE001 — un hook no debe romper la sesión
        return 0
    if not rel.startswith(VIGILADOS):
        return 0
    if yaml is None:
        print(
            "validar_claude: falta pyyaml; no se valida aquí (la CI sí lo hará)",
            file=sys.stderr,
        )
        return 0
    errores = validar(raiz)
    if errores:
        print(
            "Incumple las reglas de .claude/README.md:\n" + "\n".join(errores),
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--hook"]:
        sys.exit(desde_hook())
    if yaml is None:
        sys.exit("validar_claude: instala pyyaml")
    errores = validar(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    print("\n".join(errores) or "Agentes, skills y CLAUDE.md correctos")
    sys.exit(1 if errores else 0)
