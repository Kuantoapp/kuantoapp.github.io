"""Ajustes de pytest por plataforma."""

import sys

# test_lanzador.py prueba el lanzador de macOS y Linux con /bin/sh y enlaces simbólicos, que en Windows no hay.
# El de Windows (py-windows) lo prueba test_windows.py.
collect_ignore = ["test_lanzador.py"] if sys.platform == "win32" else []
