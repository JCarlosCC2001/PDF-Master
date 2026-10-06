"""
main.py
Punto de entrada de PDF Master.

Uso:
    python main.py                          → abre en el dashboard
    python main.py <ruta_archivo>           → detecta extensión y abre panel
    python main.py --tool <id> <archivo>    → abre en herramienta específica
                                              (usado por el menú contextual)
IDs de herramienta válidos:
    open, img2pdf, pdf2img, merge, reorder, repair, edit
"""
import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

from ui.main_window import MainWindow


def _parse_args() -> tuple[str | None, str | None]:
    """
    Devuelve (tool_id, filepath).
    Soporta:
        main.py                         → (None, None)
        main.py <archivo>               → (None, archivo)
        main.py --tool <id> <archivo>   → (id, archivo)
    """
    args = sys.argv[1:]

    if not args:
        return None, None

    if "--tool" in args:
        idx = args.index("--tool")
        tool_id = args[idx + 1] if idx + 1 < len(args) else None
        filepath = args[idx + 2] if idx + 2 < len(args) else None
        return tool_id, filepath

    # Argumento posicional simple (sin --tool)
    return None, args[0]


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("PDF Master")
    app.setApplicationVersion("0.3.0")
    app.setOrganizationName("PDF Master")

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    tool_id, filepath = _parse_args()

    window = MainWindow(initial_file=filepath, initial_tool=tool_id)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
