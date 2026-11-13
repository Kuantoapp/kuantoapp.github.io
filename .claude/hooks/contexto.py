"""Hook SessionStart: da a Claude el estado del proyecto en pocas líneas, para que no tenga que buscarlo.

Lee lo versionado y el disco: decisiones pendientes y próximos hitos (docs/decisiones.md), marcas
«(verificar)» abiertas y descargas de data/README.md que faltan en este equipo. Nunca bloquea.
"""

from __future__ import annotations  # puede ejecutarse con el Python 3.9 de macOS

import os
import re
from datetime import date
from pathlib import Path

# Solo texto que escriben personas y agentes; nunca datos (pesados y a veces en latin-1)
CARPETAS = ("docs", "ideas", "src", "app", "notebooks")
EXTENSIONES = {".md", ".py", ".txt", ".html"}
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
    seccion = decisiones.split("## Hitos", 1)[1] if "## Hitos" in decisiones else ""
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


def verificar(base: Path) -> tuple[int, list[str]]:
    rutas = [base / "data/README.md"]
    for carpeta in CARPETAS:
        rutas += [r for r in (base / carpeta).rglob("*") if r.suffix in EXTENSIONES]
    por_fichero = {}
    for ruta in rutas:
        n = leer(ruta).lower().count("(verificar") if ruta.is_file() else 0
        if n:
            por_fichero[ruta.relative_to(base).as_posix()] = n
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
        return "Próximos hitos: " + "; ".join(proximos) if proximos else ""

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

    seccion("Hitos", _hitos)
    seccion("Decisiones pendientes", _pendientes)
    seccion("Marcas «(verificar)»", _verificar)
    seccion("Descargas", _faltan)
    if not lineas:
        return ""
    return (
        "Estado del proyecto al abrir sesión (docs/decisiones.md y data/README.md):\n- "
        + "\n- ".join(lineas)
    )


def main() -> int:
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
