"""Revisores obligatorios: si un cambio toca su área, su veredicto tiene que estar en el PR y ser del código actual.

Qué área exige qué revisor (DISPARADORES):
- código espacial (geopandas, pysal, kriging, to_crs…)      → dm-revisor-espacial
- cálculos normativos (IRPF, cotizaciones, SMI, IPREM, ayudas…) → dm-auditor-calculos-normativos
- textos que ve el público (app/, docs/pitch/)              → dm-trazador-cifras
- fuentes de datos (data/README.md)                          → dm-verificador-fuentes

Modos:
  python revisiones.py              CI: el PR debe traer, por revisor exigido, «- dm-x: APTO (sha)» de un commit
                                    tras el que no cambió nada de su área. NO APTO falla; «NO APLICA — motivo» se acepta.
  python revisiones.py --registrar  hook (PreToolUse de SubagentHandback y SubagentStop): guarda cada veredicto y
                                    rechaza el informe de un revisor que no traiga uno válido
  python revisiones.py --resumen    imprime el bloque para pegar en el PR con los veredictos válidos
  python revisiones.py --stop       hook Stop: si el trabajo está confirmado y falta una revisión, lo recuerda una vez
"""

from __future__ import annotations  # puede ejecutarse con el Python 3.9 de macOS

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CODIGO = {".py", ".ipynb", ".sql", ".r", ".js", ".jsx", ".ts", ".tsx"}
CARPETAS_CODIGO = ("src/", "app/", "notebooks/")
ESPACIAL = re.compile(
    r"\b(geopandas|libpysal|esda|spreg|mgwr|pointpats|mapclassify|pykrige|gstools|shapely|pyproj|rasterio|osmnx)\b"
    r"|\.to_crs\(|\bsjoin(_nearest)?\b|\bGroupKFold\b"
)
NORMATIVO = re.compile(
    r"\b(irpf|retenci[oó]n\w*|cotizaci[oó]n\w*|seguridad_social|smi|iprem|imv|ingreso_minimo\w*"
    r"|tarifa\w*|subvenci[oó]n\w*|bono_\w+|ayudas?_\w+|bruto|neto)\b",
    re.IGNORECASE,
)
REVISORES = {
    "dm-revisor-espacial": "código espacial",
    "dm-auditor-calculos-normativos": "cálculos normativos",
    "dm-trazador-cifras": "cifras que ve el público",
    "dm-verificador-fuentes": "fuentes de datos",
}
LINEA = re.compile(
    r"^\s*[-*]?\s*`?(dm-[a-z0-9-]+)`?\s*:\s*(APTO CON RESERVAS|NO APTO|NO APLICA|APTO)\b(.*)$",
    re.MULTILINE,
)
VEREDICTO = re.compile(r"Veredicto:\s*\**\s*(APTO CON RESERVAS|NO APTO|APTO)\b")
SHA = re.compile(r"\b([0-9a-f]{7,40})\b")


def git(*args: str, cwd: Path | None = None) -> str:
    r = subprocess.run(
        ["git", *args], capture_output=True, check=False, text=True, cwd=cwd
    )
    return r.stdout.strip()


def ok(*args: str, cwd: Path | None = None) -> bool:
    return (
        subprocess.run(
            ["git", *args], capture_output=True, check=False, cwd=cwd
        ).returncode
        == 0
    )


def area(ruta: str, raiz: Path) -> set[str]:
    """Revisores que exige un fichero cambiado, según su ruta y su contenido actual."""
    exigidos = set()
    if ruta.startswith(("app/", "docs/pitch/")):
        exigidos.add("dm-trazador-cifras")
    if ruta == "data/README.md":
        exigidos.add("dm-verificador-fuentes")
    f = raiz / ruta
    if ruta.startswith(CARPETAS_CODIGO) and f.suffix.lower() in CODIGO and f.is_file():
        texto = f.read_text(encoding="utf-8", errors="ignore")
        if ESPACIAL.search(texto):
            exigidos.add("dm-revisor-espacial")
        if NORMATIVO.search(texto) or re.search(r"normativ|parametros_\d{4}", ruta):
            exigidos.add("dm-auditor-calculos-normativos")
    return exigidos


def exigidos(nombres: set[str], raiz: Path) -> dict[str, set[str]]:
    """Revisor → ficheros de su área que cambiaron."""
    por_revisor: dict[str, set[str]] = {}
    for n in nombres:
        for r in area(n, raiz):
            por_revisor.setdefault(r, set()).add(n)
    return por_revisor


def cambiados(base: str, raiz: Path, con_trabajo: bool = False) -> set[str]:
    desde = git("merge-base", base, "HEAD", cwd=raiz) or base
    nombres = set(
        git(
            "diff", "--name-only", desde if con_trabajo else f"{desde}...HEAD", cwd=raiz
        ).split()
    )
    if con_trabajo:
        nombres |= set(
            git("ls-files", "--others", "--exclude-standard", cwd=raiz).split()
        )
    return nombres


def vigente(sha: str, ficheros: set[str], raiz: Path) -> str | None:
    """None si el veredicto sobre `sha` sigue valiendo para HEAD; si no, el motivo."""
    if not ok("cat-file", "-e", f"{sha}^{{commit}}", cwd=raiz):
        return f"el commit {sha} no existe en esta rama"
    if not ok("merge-base", "--is-ancestor", sha, "HEAD", cwd=raiz):
        return f"el commit {sha} no es un antecesor de HEAD"
    despues = set(git("diff", "--name-only", sha, "HEAD", cwd=raiz).split()) & ficheros
    if despues:
        return f"caducado: después de {sha} cambiaron {', '.join(sorted(despues)[:3])}"
    return None


def comprobar_pr(
    cuerpo: str, por_revisor: dict[str, set[str]], raiz: Path
) -> list[str]:
    declarados = {m.group(1): (m.group(2), m.group(3)) for m in LINEA.finditer(cuerpo)}
    errores = []
    for revisor, ficheros in sorted(por_revisor.items()):
        cita = f"{revisor} ({REVISORES[revisor]}: {', '.join(sorted(ficheros)[:3])})"
        if revisor not in declarados:
            errores.append(f"Falta el veredicto de {cita}")
            continue
        estado, resto = declarados[revisor]
        if estado == "NO APTO":
            errores.append(
                f"{revisor} dio NO APTO: corrige los bloqueantes y vuelve a pedir la revisión"
            )
        elif estado == "NO APLICA":
            if len(re.sub(r"^[\s—–:-]+", "", resto).strip()) < 15:
                errores.append(
                    f"{revisor}: NO APLICA necesita el motivo («NO APLICA — por qué no toca su área»)"
                )
        elif not (m := SHA.search(resto)):
            errores.append(
                f"{revisor}: indica el commit revisado («{estado} (abc1234)»)"
            )
        elif motivo := vigente(m.group(1), ficheros, raiz):
            errores.append(f"{revisor}: veredicto {motivo}; vuelve a pedir la revisión")
    return errores


def registro(raiz: Path) -> Path:
    comun = Path(git("rev-parse", "--git-common-dir", cwd=raiz) or ".git")
    comun = (
        comun if comun.is_absolute() else raiz / comun
    )  # sin --path-format: vale con git antiguo
    return (
        comun / "dm-revisiones.jsonl"
    )  # dentro de .git: compartido por los worktrees y nunca versionado


FORMATO = (
    "Tu informe debe empezar con «## Veredicto: APTO», «## Veredicto: APTO CON RESERVAS» o "
    "«## Veredicto: NO APTO» (solo esos tres; los estados de cada comprobación van en sus tablas). Corrígelo y entrégalo de nuevo."
)


def registrar(evento: dict) -> int:
    """Guarda el veredicto de un revisor y rechaza un informe sin veredicto válido, para que no se pierda.

    PreToolUse de SubagentHandback: el informe es tool_input.message; si no es válido, se deniega la entrega
    y Claude Code pide al agente que la repita. SubagentStop: el informe es last_assistant_message (si no hubo
    SubagentHandback); si el agente acaba sin veredicto registrado, se le pide una vez.
    """
    agente = evento.get("agent_type") or ""
    if agente not in REVISORES:
        return 0
    raiz = Path(evento.get("cwd") or os.getcwd())
    parada = evento.get("hook_event_name") == "SubagentStop"
    informe = (
        evento.get("last_assistant_message")
        if parada
        else (evento.get("tool_input") or {}).get("message")
    ) or ""
    m = VEREDICTO.search(informe)
    if not m:
        if not parada:
            salida = {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": FORMATO,
            }
            print(json.dumps({"hookSpecificOutput": salida}, ensure_ascii=False))
        elif not evento.get("stop_hook_active") and not ya_registrado(
            raiz, evento.get("agent_id")
        ):
            print(
                json.dumps({"decision": "block", "reason": FORMATO}, ensure_ascii=False)
            )
        return 0
    motivo = informe[m.end() :].strip().splitlines()
    fila = {
        "agente": agente,
        "agent_id": evento.get("agent_id") or "",
        "veredicto": m.group(1),
        "sha": git("rev-parse", "HEAD", cwd=raiz),
        "sucio": bool(git("status", "--porcelain", "--untracked-files=no", cwd=raiz)),
        "rama": git("branch", "--show-current", cwd=raiz),
        "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "motivo": (motivo[0] if motivo else "")[:200],
    }
    with registro(raiz).open("a", encoding="utf-8") as f:
        f.write(json.dumps(fila, ensure_ascii=False) + "\n")
    return 0


def filas(raiz: Path) -> list[dict]:
    ruta = registro(raiz)
    if not ruta.exists():
        return []
    return [
        json.loads(x)
        for x in ruta.read_text(encoding="utf-8").splitlines()
        if x.strip()
    ]


def ya_registrado(raiz: Path, agent_id: str | None) -> bool:
    return bool(agent_id) and any(f.get("agent_id") == agent_id for f in filas(raiz))


def validos(raiz: Path, por_revisor: dict[str, set[str]]) -> dict[str, dict]:
    """Último veredicto registrado de cada revisor que aún vale para HEAD."""
    vistos: dict[str, dict] = {}
    for fila in reversed(filas(raiz)):
        r = fila.get("agente")
        if (
            r in por_revisor
            and r not in vistos
            and not fila.get("sucio")
            and vigente(fila["sha"], por_revisor[r], raiz) is None
        ):
            vistos[r] = fila
    return vistos


def resumen(raiz: Path, base: str) -> int:
    por_revisor = exigidos(cambiados(base, raiz), raiz)
    hechos = validos(raiz, por_revisor)
    print("## Revisión por agentes")
    if not por_revisor:
        print("- Ningún área con revisor obligatorio en este cambio.")
    for r in sorted(por_revisor):
        if r in hechos:
            f = hechos[r]
            print(f"- {r}: {f['veredicto']} ({f['sha'][:7]}) — {f['motivo']}")
    faltan = sorted(set(por_revisor) - set(hechos))
    for r in faltan:
        print(
            f"Falta: {r} ({REVISORES[r]}). Haz commit y pide la revisión.",
            file=sys.stderr,
        )
    return 1 if faltan else 0


def stop(evento: dict, raiz: Path, base: str) -> int:
    if evento.get("stop_hook_active"):
        return 0
    por_revisor = exigidos(cambiados(base, raiz, con_trabajo=True), raiz)
    pendiente = {f for fs in por_revisor.values() for f in fs}
    if not por_revisor or git("status", "--porcelain", "--", *pendiente, cwd=raiz):
        return 0  # sin área revisable, o aún trabajando (sin confirmar): no interrumpir
    en_marcha = {
        t.get("agent_type")
        for t in evento.get("background_tasks") or []
        if t.get("type") == "subagent"
    }
    faltan = sorted(set(por_revisor) - set(validos(raiz, por_revisor)) - en_marcha)
    if faltan:
        lista = "\n- ".join(f"{r} ({REVISORES[r]})" for r in faltan)
        razon = (
            f"El trabajo confirmado toca áreas con revisor obligatorio y falta su veredicto:\n- {lista}\n"
            "Lanza esos agentes ahora, corrige lo que digan y añade al PR la salida de "
            "`python .github/scripts/revisiones.py --resumen`."
        )
        print(json.dumps({"decision": "block", "reason": razon}, ensure_ascii=False))
    return 0


def main(argv: list[str]) -> int:
    raiz = Path(os.environ.get("CLAUDE_PROJECT_DIR") or ".").resolve()
    base = "origin/" + (os.environ.get("GITHUB_BASE_REF") or "main")
    if argv in (["--registrar"], ["--stop"]):
        try:
            evento = json.load(sys.stdin)
        except ValueError:
            return 0
        if argv == ["--registrar"]:
            return registrar(evento)
        return stop(evento, Path(evento.get("cwd") or raiz), base)
    if argv == ["--resumen"]:
        return resumen(raiz, base)
    por_revisor = exigidos(cambiados(base, raiz), raiz)
    try:
        cuerpo = (
            json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())[
                "pull_request"
            ].get("body")
            or ""
        )
    except (KeyError, OSError, ValueError, TypeError):
        cuerpo = ""
    errores = comprobar_pr(cuerpo, por_revisor, raiz)
    if errores:
        print("\n".join(errores), file=sys.stderr)
        print(
            "Añade al PR la salida de `python .github/scripts/revisiones.py --resumen` (ver AGENTS.md, «Revisores obligatorios»).",
            file=sys.stderr,
        )
        return 1
    print(
        "Revisores obligatorios: "
        + (", ".join(sorted(por_revisor)) or "ninguno")
        + " — al día"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
