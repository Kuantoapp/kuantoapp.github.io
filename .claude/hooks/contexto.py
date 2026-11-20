"""Hook SessionStart: da a Claude el estado del proyecto en pocas líneas, para que no tenga que buscarlo.

Lee lo versionado y el disco: decisiones pendientes y próximas fechas clave (docs/decisiones.md), marcas
«(verificar)» abiertas, descargas de data/README.md que faltan en este equipo y commits nuevos de origin/main
que aún no tiene tu rama (hace un `git fetch` corto; no hace pull). Nunca bloquea.

--stop (hook Stop): avisa a la persona cuando el contexto de la sesión pasa de UMBRAL tokens, para que
compacte o cambie de sesión (el agente no puede hacerlo solo). Una vez por cada tramo de 100.000.
"""

from __future__ import annotations  # puede ejecutarse con el Python 3.9 de macOS

import ast
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

# Se recorre lo que git conoce, sea cual sea la estructura de carpetas, salvo reglas, CI,
# datos (pesados y a veces en latin-1) y tests (sus marcas son de prueba)
EXCLUIR = (".claude/", ".github/", "data/", "tests/")
EXTENSIONES = {".md", ".py", ".txt", ".html", ".ipynb"}
# «(verificar)» entre comillas es texto que habla de la marca, no una marca pendiente
MARCA = re.compile(r"(?<!«)\(verificar", re.IGNORECASE)
HITO = re.compile(r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(.+?)\s*\|")


def leer(ruta: Path) -> str:
    return ruta.read_text(encoding="utf-8", errors="replace") if ruta.exists() else ""


def pendientes(decisiones: str) -> list[str]:
    return [
        linea.split("·", 1)[1].strip()
        for linea in decisiones.splitlines()
        if linea.startswith("- _Pendiente_") and "·" in linea
    ]


def hitos(decisiones: str, hoy: date) -> list[str]:
    seccion = (
        decisiones.split("## Fechas clave", 1)[1]
        if "## Fechas clave" in decisiones
        else ""
    )
    futuros = []
    for linea in seccion.splitlines():
        m = HITO.match(linea)
        if m:
            dias = (date.fromisoformat(m.group(1)) - hoy).days
            if dias >= 0:
                futuros.append((dias, m.group(1), m.group(2)))
    return [
        f"{fecha} ({'HOY' if dias == 0 else f'en {dias} días'}): {texto}"
        for dias, fecha, texto in sorted(futuros)[:3]
    ]


def ficheros(base: Path) -> list[str]:
    """Rutas relativas de lo versionado y lo nuevo sin ignorar; sin git, todo el árbol."""
    r = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=base,
        capture_output=True,
        check=False,
        text=True,
    )
    if r.returncode == 0:
        return r.stdout.splitlines()
    return [
        p.relative_to(base).as_posix() for p in base.rglob("*") if ".git" not in p.parts
    ]


def verificar(base: Path) -> tuple[int, list[str]]:
    rutas = ["data/README.md"] + [
        f
        for f in ficheros(base)
        if Path(f).suffix in EXTENSIONES and not f.startswith(EXCLUIR)
    ]
    por_fichero = {}
    for rel in rutas:
        ruta = base / rel
        n = len(MARCA.findall(leer(ruta))) if ruta.is_file() else 0
        if n:
            por_fichero[rel] = n
    top = sorted(por_fichero.items(), key=lambda x: -x[1])[:3]
    return sum(por_fichero.values()), [f"{f} ({n})" for f, n in top]


def tabla_fuentes(readme: str) -> tuple[list[str], list[list[str]]]:
    """La primera tabla de data/README.md (la de fuentes): termina en la primera línea que no es fila."""
    # Copia del parser de .claude/skills/dm-nueva-fuente/scripts/descargar.py (los dos scripts son independientes): cambia ambos a la vez
    filas = []
    for linea in readme.splitlines():
        if not linea.startswith("|"):
            if filas:
                break
            continue
        if not linea.startswith("|---"):
            filas.append([c.strip() for c in linea.strip().strip("|").split("|")])
    return (filas[0], filas[1:]) if filas else ([], [])


def descargas_que_faltan(base: Path) -> list[str]:
    """Filas de la tabla de fuentes de data/README.md cuyo fichero no está en data/raw de este equipo."""
    cabecera, filas = tabla_fuentes(leer(base / "data/README.md"))
    col = next((i for i, c in enumerate(cabecera) if c.startswith("Fichero")), None)
    if col is None:
        return []
    faltan = []
    for fila in filas:
        fichero = fila[col].strip("`") if len(fila) > col else ""
        if (
            fichero
            and not fila[0].startswith("_")
            and not (base / "data/raw" / fichero).exists()
        ):
            faltan.append(f"{fichero} ({fila[0]})")
    return faltan


def git(base: Path, *args: str, espera: int = 10) -> str | None:
    """Salida de un comando git, o None si falla, no hay git o tarda más de `espera` segundos."""
    try:
        r = subprocess.run(
            ["git", *args],
            cwd=base,
            capture_output=True,
            check=False,
            text=True,
            timeout=espera,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


# Lo que cambia las reglas del juego para todos, aunque tú no lo toques
COMUN = (
    ".claude/",
    ".github/",
    "AGENTS.md",
    "CLAUDE.md",
    "requirements",
    ".python-version",
    "docs/decisiones.md",
)


def lineas(base: Path, *args: str) -> set[str]:
    return set((git(base, *args) or "").splitlines())


def importados(base: Path, rel: str) -> set[str]:
    """Rutas posibles de los módulos que importa un .py (un nivel; en la raíz o en src/)."""
    try:
        arbol = ast.parse((base / rel).read_text(encoding="utf-8"))
    except (OSError, SyntaxError, ValueError):
        return set()  # borrado, ilegible o no es Python: no hay imports que seguir
    modulos = []  # (ruta relativa de un módulo, ¿relativa al fichero?)
    for n in ast.walk(arbol):
        if isinstance(n, ast.Import):
            modulos += [(a.name.replace(".", "/"), False) for a in n.names]
        elif isinstance(n, ast.ImportFrom):
            ruta = (n.module or "").replace(".", "/")
            if n.level:
                ruta = "/".join([".."] * (n.level - 1) + [ruta]).rstrip("/")
            modulos += [(ruta, n.level > 0)] + [
                (f"{ruta}/{a.name}", n.level > 0) for a in n.names
            ]
    candidatos = set()
    for ruta, relativa in modulos:
        if relativa:
            ruta = os.path.normpath(str(Path(rel).parent / ruta)).replace(os.sep, "/")
        for raiz in ("",) if relativa else ("", "src/"):
            candidatos |= {f"{raiz}{ruta}.py", f"{raiz}{ruta}/__init__.py"}
    return candidatos


def remoto(base: Path) -> str:
    """Aviso si origin/main cambió algo que te afecta (ficheros que tocas o reglas comunes); si no, calla."""
    if git(base, "fetch", "--quiet", "origin", "main", espera=5) is None:
        return ""  # sin repo, sin remoto o sin red: se trabaja igual
    nuevos = lineas(base, "diff", "--name-only", "HEAD...origin/main")
    if not nuevos:
        return ""
    # shortcut: solo coincidencia por fichero; no ve dependencias entre ficheros distintos, cuándo mejorarlo: si falla en la práctica
    sucios = lineas(base, "diff", "--name-only", "HEAD") | lineas(
        base, "ls-files", "--others", "--exclude-standard"
    )
    suyos = lineas(base, "diff", "--name-only", "origin/main...HEAD") | sucios
    comunes = {f for f in nuevos if f.startswith(COMUN)}
    choque = sorted(nuevos & suyos)
    # shortcut: un solo nivel de imports; los transitivos darían demasiados falsos avisos
    deps = set().union(*(importados(base, f) for f in suyos if f.endswith(".py")))
    usados = sorted(nuevos & deps - set(choque))
    if not choque and not usados and not comunes:
        return ""
    rama = git(base, "branch", "--show-current") or "HEAD"
    accion = "git pull --rebase" if rama == "main" else "git rebase origin/main"
    motivo = []
    if choque:
        motivo.append("ficheros que tú también tocas: " + ", ".join(choque[:5]))
    if usados:
        motivo.append("ficheros que importas: " + ", ".join(usados[:5]))
    if comunes:
        motivo.append(
            "reglas o dependencias comunes: " + ", ".join(sorted(comunes)[:5])
        )
    sucio = (
        " Tienes cambios sin confirmar: haz commit o `git stash` antes."
        if sucios
        else ""
    )
    return f"origin/main ha cambiado ({'; '.join(motivo)}). Tu rama «{rama}» no lo tiene: ejecuta `{accion}`.{sucio}"


def contexto(base: Path, hoy: date) -> str:
    decisiones = leer(base / "docs/decisiones.md")
    lineas = []

    def seccion(nombre, calcular):
        # Cada parte por separado: si una falla, las demás se siguen mostrando
        try:
            texto = calcular()
        except Exception as e:  # noqa: BLE001
            texto = f"{nombre}: no se pudo calcular ({e!r})"
        if texto:
            lineas.append(texto)

    def _hitos():
        proximos = hitos(decisiones, hoy)
        return (
            "Próximas fechas clave (fechas fijas, no tareas): " + "; ".join(proximos)
            if proximos
            else ""
        )

    def _pendientes():
        sin_decidir = pendientes(decisiones)
        if not sin_decidir:
            return ""
        return (
            "Sin decidir aún (no lo supongas; pregunta o deja el supuesto escrito): "
            + "; ".join(sin_decidir)
        )

    def _verificar():
        total, top = verificar(base)
        return (
            f"Marcas «(verificar)» abiertas: {total}, sobre todo en " + ", ".join(top)
            if total
            else ""
        )

    def _faltan():
        faltan = descargas_que_faltan(base)
        if not faltan:
            return ""
        return (
            f"Faltan {len(faltan)} descargas de data/README.md en este equipo (ver «Cómo obtenerla»): "
            + ", ".join(faltan[:5])
        )

    seccion("Repositorio", lambda: remoto(base))
    seccion("Fechas clave", _hitos)
    seccion("Decisiones pendientes", _pendientes)
    seccion("Marcas «(verificar)»", _verificar)
    seccion("Descargas", _faltan)
    if not lineas:
        return ""
    return (
        "Estado del proyecto al abrir sesión (docs/decisiones.md y data/README.md):\n- "
        + "\n- ".join(lineas)
    )


UMBRAL = 150_000


def tokens_contexto(transcript: Path) -> int:
    """Contexto enviado en la última respuesta del asistente, según su uso registrado en el transcript."""
    with transcript.open("rb") as f:
        f.seek(0, os.SEEK_END)
        f.seek(max(0, f.tell() - 2_000_000))  # basta el final: la última respuesta
        lineas = f.read().decode("utf-8", "replace").splitlines()
    for linea in reversed(lineas):
        try:
            d = json.loads(linea)
        except ValueError:
            continue
        uso = (
            (d.get("message") or {}).get("usage")
            if d.get("type") == "assistant"
            else None
        )
        if uso:
            return sum(
                uso.get(k) or 0
                for k in (
                    "input_tokens",
                    "cache_read_input_tokens",
                    "cache_creation_input_tokens",
                )
            )
    return 0


def aviso_contexto(evento: dict) -> str:
    ruta = evento.get("transcript_path")
    if not ruta or not Path(ruta).is_file():
        return ""
    tokens = tokens_contexto(Path(ruta))
    marca = (
        Path(tempfile.gettempdir())
        / f"dm-contexto-{evento.get('session_id') or 'sesion'}"
    )
    if tokens < UMBRAL:
        marca.unlink(missing_ok=True)  # tras compactar, se vuelve a avisar si crece
        return ""
    tramo = tokens // 100_000
    if marca.exists() and int(marca.read_text(encoding="utf-8") or 0) >= tramo:
        return ""
    marca.write_text(str(tramo), encoding="utf-8")
    return json.dumps(
        {
            "systemMessage": f"Contexto de unos {tokens // 1000} mil tokens, y cada turno lo reenvía. "
            "Si sigues con la misma tarea, /compact al cerrar esta etapa; si cambias de tarea, /clear o sesión nueva."
        },
        ensure_ascii=False,
    )


def main() -> int:
    if sys.argv[1:] == ["--stop"]:
        try:
            texto = aviso_contexto(json.load(sys.stdin))
        except Exception:  # noqa: BLE001 — un aviso que falla no debe molestar al terminar
            texto = ""
        if texto:
            print(texto)
        return 0
    base = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    try:
        texto = contexto(base, date.today())
    except Exception as e:  # noqa: BLE001 — el contexto es una ayuda; si falla, se trabaja igual
        texto = f"No se pudo resumir el estado del proyecto ({e!r}); lee docs/decisiones.md."
    if texto:
        print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
