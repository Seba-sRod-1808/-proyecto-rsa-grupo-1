"""Proyecto de criptografía RSA — MM2015 Matemática Discreta 1.

Punto de entrada de la aplicación: ``python main.py``.
"""

import os
import sys

RAIZ_PROYECTO = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ_PROYECTO)


def main():
    try:
        from ui.app import AplicacionRSA
    except ModuleNotFoundError as error:
        ruta_requisitos = os.path.join(RAIZ_PROYECTO, "requirements-desktop.txt")
        sys.exit(f"Falta la dependencia «{error.name}». Instálela con:\n"
                 f"    pip install -r {ruta_requisitos}")
    AplicacionRSA().mainloop()


if __name__ == "__main__":
    main()
