"""Hook SessionStart: da a Claude el estado del proyecto en pocas líneas, para que no tenga que buscarlo.

Lee lo versionado y el disco: decisiones pendientes y próximos hitos (docs/decisiones.md), marcas
«(verificar)» abiertas y descargas de data/README.md que faltan en este equipo. Nunca bloquea.
"""

from __future__ import annotations  # puede ejecutarse con el Python 3.9 de macOS

import os
import re
from datetime import date
from pathlib import Path

CARPETAS = ("docs", "data", "ideas", "src", "app", "notebooks")
EXTENSIONES = {".md", ".py", ".txt", ".html", ".csv", ".yml", ".yaml", ".json"}
HITO = re.compile(r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(.+?)\s*\|")


def leer(ruta: Path) -> str:
    return ruta.read_text(encoding="utf-8") if ruta.exists() else ""


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
    por_fichero = {}
    for carpeta in CARPETAS:
        for ruta in (base / carpeta).rglob("*"):
            if (
                ruta.suffix in EXTENSIONES
                and "raw" not in ruta.parts
                and ruta.is_file()
            ):
                n = leer(ruta).lower().count("(verificar")
                if n:
                    por_fichero[ruta.relative_to(base).as_posix()] = n
    top = sorted(por_fichero.items(), key=lambda x: -x[1])[:3]
    return sum(por_fichero.values()), [f"{f} ({n})" for f, n in top]


def descargas_que_faltan(base: Path) -> list[str]:
    """Filas de la tabla de fuentes de data/README.md cuyo fichero no está en data/raw de este equipo."""
    filas = [
        [c.strip() for c in linea.strip().strip("|").split("|")]
        for linea in leer(base / "data/README.md").splitlines()
        if linea.startswith("|") and not linea.startswith("|---")
    ]
    if not filas:
        return []
    cabecera, filas = filas[0], filas[1:]
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
    proximos = hitos(decisiones, hoy)
    if proximos:
        lineas.append("Próximos hitos: " + "; ".join(proximos))
    sin_decidir = pendientes(decisiones)
    if sin_decidir:
        lineas.append(
            "Sin decidir aún (no lo supongas; pregunta o deja el supuesto escrito): "
            + "; ".join(sin_decidir)
        )
    total, top = verificar(base)
    if total:
        lineas.append(
            f"Marcas «(verificar)» abiertas: {total}, sobre todo en " + ", ".join(top)
        )
    faltan = descargas_que_faltan(base)
    if faltan:
        lineas.append(
            f"Faltan {len(faltan)} descargas de data/README.md en este equipo (ver «Cómo obtenerla»): "
            + ", ".join(faltan[:5])
        )
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
