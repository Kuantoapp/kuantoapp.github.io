"""Genera `<fichero>.DATA.md` (diccionario de datos) para CSV/TSV pesados.

Solo stdlib: lee en streaming, no carga el fichero en memoria y no necesita pandas.
Perfila como mucho `--max-rows` filas repartidas con paso constante por todo el fichero
(no solo las primeras, que suelen estar sesgadas por el orden).

Uso:
    python perfilar.py RUTA [--out SALIDA] [--max-rows N] [--seed N] [--encoding COD]
    python perfilar.py RUTA --check      # 0 = al dia, 1 = desfasado, 2 = no existe
"""

from __future__ import annotations

import argparse
import csv
import math
import random
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

NA_TOKENS = frozenset({"", "NA", "N/A", "NaN", "nan", "null", "NULL", "None"})
INT_RE = re.compile(r"^[+-]?\d+$")
# Coma decimal o punto de miles («1.234,5», «0,25»): float() no los lee y quedan como texto
ES_NUM_RE = re.compile(r"^[+-]?(\d{1,3}(\.\d{3})+(,\d+)?|\d+,\d+)$")
META_RE = re.compile(r"<!-- datadict: size=(\d+) mtime=(\d+) ")
NOTES_HEADER = "## Notas"
SEPARATORS = {",": "coma", ";": "punto y coma", "\t": "tabulador", "|": "barra"}
MAX_DISTINCT = 50
MAX_CELL = 40
HEAD_ROWS = 5
SHOW_COLS = 15


@dataclass
class ColStats:
    """Estadisticos incrementales de una columna."""

    name: str
    n: int = 0
    nulls: int = 0
    n_int: int = 0
    n_float: int = 0
    n_str: int = 0
    n_es: int = 0
    lo: float = math.inf
    hi: float = -math.inf
    total: float = 0.0
    overflow: bool = False
    counts: Counter[str] = field(default_factory=Counter)

    def add(self, value: str) -> None:
        self.n += 1
        if value in NA_TOKENS:
            self.nulls += 1
            return
        if value in self.counts or len(self.counts) < MAX_DISTINCT:
            self.counts[value] += 1
        else:
            self.overflow = True
        try:
            x = float(value)
        except ValueError:
            self.n_str += 1
            self.n_es += bool(ES_NUM_RE.match(value))
            return
        if not math.isfinite(x):
            self.n_str += 1
            return
        if INT_RE.match(value):
            self.n_int += 1
        else:
            self.n_float += 1
        self.lo, self.hi, self.total = min(self.lo, x), max(self.hi, x), self.total + x

    @property
    def n_num(self) -> int:
        return self.n_int + self.n_float

    @property
    def kind(self) -> str:
        if self.n_num + self.n_str == 0:
            return "vacia"
        if self.n_str == 0:
            return "int" if self.n_float == 0 else "float"
        return "str" if self.n_num == 0 else "mixto"

    @property
    def null_pct(self) -> float:
        return 100.0 * self.nulls / self.n if self.n else 0.0

    @property
    def distinct(self) -> str:
        return f">={MAX_DISTINCT}" if self.overflow else str(len(self.counts))

    def summary(self) -> str:
        if self.kind in ("int", "float") and self.n_num:
            return f"{_fmt(self.lo)}..{_fmt(self.hi)} (media {_fmt(self.total / self.n_num)})"
        if not self.overflow and self.counts:
            nn = self.n - self.nulls
            top = ", ".join(
                f"{_cell(v)} ({100 * c / nn:.0f}%)"
                for v, c in self.counts.most_common(3)
            )
            return f"top: {top}"
        return "alta cardinalidad" if self.overflow else ""


def _fmt(x: float) -> str:
    return f"{x:.6g}"


def _cell(value: str) -> str:
    """Escapa y recorta un valor para una celda de tabla Markdown."""
    value = value.replace("\n", " ").replace("\r", " ").replace("|", r"\|")
    return value if len(value) <= MAX_CELL else value[: MAX_CELL - 1] + "…"


def count_lines(path: Path) -> int:
    with path.open("rb") as fh:
        return sum(chunk.count(b"\n") for chunk in iter(lambda: fh.read(1 << 20), b""))


def detect_separator(path: Path, encoding: str) -> str:
    with path.open("r", encoding=encoding, errors="replace", newline="") as fh:
        sample = fh.read(65536)
    try:
        return csv.Sniffer().sniff(sample, delimiters="".join(SEPARATORS)).delimiter
    except csv.Error:
        return ","


def read_previous(out: Path) -> tuple[dict[str, str], str]:
    """Descripciones y notas escritas a mano en una version anterior, para no perderlas."""
    if not out.exists():
        return {}, ""
    text = out.read_text(encoding="utf-8")
    descriptions: dict[str, str] = {}
    for line in text.splitlines():
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line)[1:-1]]
        if len(cells) == 6 and cells[0] not in ("Columna", "---") and cells[5]:
            descriptions[cells[0]] = cells[5]
    idx = text.find(NOTES_HEADER)
    return descriptions, text[idx:].rstrip() + "\n" if idx >= 0 else ""


def profile(path: Path, max_rows: int, seed: int, encoding: str = "utf-8-sig") -> dict:
    sep = detect_separator(path, encoding)
    stride = max(1, math.ceil(max(count_lines(path) - 1, 1) / max_rows))
    rng = random.Random(seed)
    head: list[list[str]] = []
    reservoir: list[list[str]] = []
    rows_total = profiled = ragged = undecodable = 0
    with path.open("r", encoding=encoding, errors="replace", newline="") as fh:
        reader = csv.reader(fh, delimiter=sep)
        header = next(reader)
        ncols = len(header)
        stats = [ColStats(h) for h in header]
        for i, row in enumerate(reader):
            rows_total += 1
            if len(row) != ncols:
                ragged += 1
                row = (row + [""] * ncols)[:ncols]
            if len(head) < HEAD_ROWS:
                head.append(row)
            if i % stride:
                continue
            # errors="replace" no corta la lectura: hay que contar los � para avisar
            undecodable += sum("�" in v for v in row)
            profiled += 1
            if len(reservoir) < HEAD_ROWS:
                reservoir.append(row)
            elif (j := rng.randint(0, profiled - 1)) < HEAD_ROWS:
                reservoir[j] = row
            for st, value in zip(stats, row):
                st.add(value)
    return {
        "sep": sep,
        "stride": stride,
        "rows_total": rows_total,
        "profiled": profiled,
        "ragged": ragged,
        "undecodable": undecodable,
        "encoding": encoding,
        "stats": stats,
        "head": head,
        "sample": reservoir,
    }


def warnings_for(res: dict) -> list[str]:
    out: list[str] = []
    if res["ragged"]:
        out.append(
            f"{res['ragged']} filas con numero de columnas distinto a la cabecera (rellenadas o recortadas)."
        )
    if res["undecodable"]:
        out.append(
            f"{res['undecodable']} celdas perfiladas con caracteres no decodificables en {res['encoding']}: "
            "prueba `--encoding latin-1` (o cp1252)."
        )
    groups: dict[str, list[str]] = {
        "vacias": [],
        "con >=40% de nulos": [],
        "con tipos mezclados": [],
        "constantes": [],
        "con numeros en formato espanol (coma decimal o punto de miles)": [],
    }
    for st in res["stats"]:
        if st.n_es and st.n_es >= 0.5 * (st.n_str + st.n_num):
            groups[
                "con numeros en formato espanol (coma decimal o punto de miles)"
            ].append(st.name)
        if st.kind == "vacia":
            groups["vacias"].append(st.name)
        elif st.null_pct >= 40:
            groups["con >=40% de nulos"].append(st.name)
        elif st.kind == "mixto":
            groups["con tipos mezclados"].append(st.name)
        elif len(st.counts) == 1 and not st.overflow and st.n - st.nulls > 1:
            groups["constantes"].append(st.name)
    for (
        label,
        names,
    ) in (
        groups.items()
    ):  # agrupado y recortado: en tablas anchas, un aviso por columna ahoga el resumen
        if names:
            more = f" y {len(names) - 8} mas" if len(names) > 8 else ""
            out.append(
                f"{len(names)} columnas {label}: "
                + ", ".join(f"`{n}`" for n in names[:8])
                + more
                + "."
            )
    return out


def _table(rows: list[list[str]], cols: list[str]) -> list[str]:
    lines = ["| " + " | ".join(_cell(c) for c in cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(_cell(v) for v in r[: len(cols)]) + " |" for r in rows]
    return lines


def render(
    path: Path, res: dict, seed: int, descriptions: dict[str, str], notes: str
) -> str:
    st_ = path.stat()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    stats: list[ColStats] = res["stats"]
    note = (
        f"perfilado sobre {res['profiled']} de {res['rows_total']} filas (1 de cada {res['stride']})"
        if res["stride"] > 1
        else f"perfilado sobre las {res['rows_total']} filas"
    )
    lines = [
        f"# {path.name} — diccionario de datos",
        (
            f"<!-- datadict: size={st_.st_size} mtime={int(st_.st_mtime)} rows={res['rows_total']} "
            f"stride={res['stride']} sep={SEPARATORS.get(res['sep'], res['sep'])!r} seed={seed} generated={now} -->"
        ),
        "",
        f"- Filas: {res['rows_total']} · Columnas: {len(stats)} · Tamano: {st_.st_size / 1048576:.1f} MB",
        f"- Separador: {SEPARATORS.get(res['sep'], res['sep'])} · {note} · semilla {seed}",
        "- Origen: POR COMPLETAR",
        "",
        "## Columnas",
        "| Columna | Tipo | Nulos % | Distintos | Rango / valores | Descripcion |",
        "|---|---|---|---|---|---|",
    ]
    for s in stats:
        desc = descriptions.get(s.name, "POR COMPLETAR")
        lines.append(
            f"| {_cell(s.name)} | {s.kind} | {s.null_pct:.1f} | {s.distinct} | {_cell(s.summary())} | {_cell(desc)} |"
        )
    shown = [s.name for s in stats[:SHOW_COLS]]
    trunc = (
        f" (primeras {SHOW_COLS} de {len(stats)} columnas)"
        if len(stats) > SHOW_COLS
        else ""
    )
    lines += [
        "",
        f"## Primeras filas{trunc}",
        *_table(res["head"], shown),
        "",
        f"## Muestra aleatoria{trunc}",
        *_table(res["sample"], shown),
    ]
    warn = warnings_for(res)
    lines += ["", "## Avisos", *(f"- {w}" for w in warn)] if warn else []
    lines += [
        "",
        notes
        if notes
        else f"{NOTES_HEADER}\n(Escribe aqui lo que no sale del script; se conserva al regenerar.)\n",
    ]
    return "\n".join(lines)


def check(path: Path, out: Path) -> int:
    if not out.exists():
        print(f"FALTA: {out}")
        return 2
    m = META_RE.search(out.read_text(encoding="utf-8"))
    st = path.stat()
    if m and int(m.group(1)) == st.st_size and int(m.group(2)) == int(st.st_mtime):
        print(f"AL DIA: {out}")
        return 0
    print(f"DESFASADO: {out} (el fichero cambio; regenerar)")
    return 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("path", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--max-rows", type=int, default=200_000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--check", action="store_true")
    ap.add_argument(
        "--encoding",
        default="utf-8-sig",
        help="p. ej. latin-1 o cp1252 si el aviso lo pide",
    )
    args = ap.parse_args(argv)
    if not args.path.is_file():
        print(f"No existe: {args.path}", file=sys.stderr)
        return 2
    out = args.out or args.path.with_suffix(".DATA.md")
    if args.check:
        return check(args.path, out)
    descriptions, notes = read_previous(out)
    res = profile(args.path, max(1, args.max_rows), args.seed, args.encoding)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        render(args.path, res, args.seed, descriptions, notes),
        encoding="utf-8",
        newline="\n",
    )
    print(f"OK: {out} ({res['rows_total']} filas, {len(res['stats'])} columnas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
