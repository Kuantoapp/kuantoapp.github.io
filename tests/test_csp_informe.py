"""La CSP de app/informe.html permite su bloque <style> por hash (#255)."""

import base64
import hashlib
import re
from pathlib import Path

INFORME = Path(__file__).resolve().parents[1] / "app" / "informe.html"


def test_hash_del_estilo_coincide_con_la_csp():
    html = INFORME.read_text(encoding="utf-8")
    assert html.count("<style") == 1, "La CSP solo autoriza un bloque de estilos"
    estilo = re.search(r"<style>(.*?)</style>", html, re.DOTALL).group(1)
    huella = base64.b64encode(hashlib.sha256(estilo.encode()).digest()).decode()
    assert f"style-src 'sha256-{huella}'" in html, (
        f"Pon 'sha256-{huella}' en la CSP de informe.html"
    )
