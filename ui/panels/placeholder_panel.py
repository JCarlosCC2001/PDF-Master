"""
ui/panels/placeholder_panel.py
Panel temporal para herramientas aun no implementadas.
Se reemplazara en fases posteriores.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor


PANEL_META = {
    "img2pdf": ("Imagenes a PDF",  "Convierte JPG, PNG, BMP, TIFF y WEBP a PDF", "Fase 2"),
    "pdf2img": ("PDF a Imagenes",  "Extrae paginas del PDF como imagenes",        "Fase 2"),
    "merge":   ("Unir PDF",        "Combina multiples PDFs en uno",               "Fase 2"),
    "reorder": ("Reordenar PDF",   "Reorganiza las paginas del PDF",              "Fase 3"),
    "repair":  ("Reparar PDF",     "Recupera PDFs danados o con proteccion",      "Fase 3"),
    "edit":    ("Editar PDF",      "Agrega texto y marcas de agua",               "Fase 3"),
}

LETTER = {
    "img2pdf": "I", "pdf2img": "P", "merge": "+",
    "reorder": "R", "repair": "F",  "edit": "E",
}


class PlaceholderPanel(QWidget):
    """Panel de marcador de posicion mientras se implementa cada herramienta."""

    def __init__(self, page_id: str, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor("#F0F0F0"))
        self.setPalette(pal)
        title, desc, fase = PANEL_META.get(page_id, (page_id, "", "proximamente"))
        letter = LETTER.get(page_id, "?")
        self._build_ui(letter, title, desc, fase)

    def _build_ui(self, letter: str, title: str, desc: str, fase: str) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(66)
        header.setAutoFillBackground(True)
        hp = header.palette()
        hp.setColor(QPalette.ColorRole.Window, QColor("#FFFFFF"))
        header.setPalette(hp)
        header.setStyleSheet("border-bottom: 2px solid #E0E0E0;")
        h_lay = QVBoxLayout(header)
        h_lay.setContentsMargins(24, 0, 24, 0)
        h_lay.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        t = QLabel(title)
        t.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        t.setStyleSheet("color: #1A1A1A; background: transparent;")
        h_lay.addWidget(t)
        root.addWidget(header)

        # ── Centro ────────────────────────────────────────────────────────────
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        b = QVBoxLayout(body)
        b.setAlignment(Qt.AlignmentFlag.AlignCenter)
        b.setSpacing(14)

        circle = QLabel(letter)
        circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        circle.setFixedSize(90, 90)
        circle.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        circle.setStyleSheet("""
            QLabel {
                background-color: #D62828;
                color: #FFFFFF;
                border-radius: 45px;
            }
        """)
        b.addWidget(circle, alignment=Qt.AlignmentFlag.AlignHCenter)

        coming = QLabel(f"Disponible en {fase}")
        coming.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        coming.setAlignment(Qt.AlignmentFlag.AlignCenter)
        coming.setStyleSheet("color: #D62828; background: transparent;")
        b.addWidget(coming)

        desc_lbl = QLabel(desc)
        desc_lbl.setFont(QFont("Segoe UI", 10))
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_lbl.setStyleSheet("color: #555555; background: transparent;")
        b.addWidget(desc_lbl)

        root.addWidget(body)
