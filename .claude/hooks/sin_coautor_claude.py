"""PreToolUse (Bash y PowerShell): bloquea los commits que nombran a Claude como coautor.

La política del repo es que Claude no figura como coautor en los commits. Mira la orden antes de ejecutarla: si es
un `git commit` (o `merge`, `revert`) cuyo mensaje lleva `Co-Authored-By: Claude` o la dirección de Anthropic, sale
con 2 y dice cómo corregirlo. Sirve igual en macOS, Linux y Windows: no hay versión `_windows`.
# shortcut: solo ve el mensaje escrito en la propia orden; un mensaje leído de fichero (`-F`) no se comprueba, y
# `git commit --amend` no limpia commits anteriores. Mejorar con un check de CI sobre los mensajes del PR si hace falta.
"""

import json
import re
import sys

COMMIT = re.compile(r"\bgit\b[^\n|;&]*\b(?:commit|merge|revert)\b", re.IGNORECASE)
COAUTOR = re.compile(
    r"co-authored-by:[^\n]*(?:claude|anthropic)|noreply@anthropic\.com", re.IGNORECASE
)


def bloquea(orden: str) -> bool:
    return bool(COMMIT.search(orden) and COAUTOR.search(orden))


def main() -> int:
    try:
        evento = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    orden = (evento.get("tool_input") or {}).get("command") or ""
    if not bloquea(orden):
        return 0
    sys.stderr.write(
        "Bloqueado: en este repo Claude no figura como coautor de los commits. "
        "Quita la línea «Co-Authored-By: Claude …» del mensaje y vuelve a lanzar el commit.\n"
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
