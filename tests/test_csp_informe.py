"""La CSP de app/informe.html solo admite estilos propios: usa estilo.css, sin estilos en línea (#255, #417)."""

import re
from pathlib import Path

INFORME = Path(__file__).resolve().parents[1] / "app" / "informe.html"


def test_estilos_solo_de_estilo_css():
    html = INFORME.read_text(encoding="utf-8")
    assert "<style" not in html and not re.search(r"\sstyle=", html), (
        "Con style-src 'self', un estilo en línea no se aplica: llévalo a estilo.css"
    )
    assert "style-src 'self'" in html, "La CSP de informe.html debe admitir estilo.css"
    assert '<link rel="stylesheet" href="estilo.css">' in html
