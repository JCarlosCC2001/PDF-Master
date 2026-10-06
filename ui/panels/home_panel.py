"""
ui/panels/home_panel.py
Panel de inicio con grid responsive de tarjetas horizontales.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame,
    QScrollArea, QSizePolicy, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ui.components.card_button import ToolCard


TOOLS = [
    {
        "icon":  "I",
        "title": "Imagenes a PDF",
        "desc":  "Convierte JPG, PNG, BMP, TIFF y WEBP a un PDF.",
        "page":  "img2pdf",
    },
    {
        "icon":  "P",
        "title": "PDF a Imagenes",
        "desc":  "Extrae paginas de un PDF como imagenes.",
        "page":  "pdf2img",
    },
    {
        "icon":  "+",
        "title": "Unir PDF",
        "desc":  "Combina multiples PDFs en uno solo.",
        "page":  "merge",
    },
    {
        "icon":  "R",
        "title": "Reordenar PDF",
        "desc":  "Mueve, elimina o rota paginas de un PDF.",
        "page":  "reorder",
    },
    {
        "icon":  "F",
        "title": "Reparar PDF",
        "desc":  "Recupera PDFs danados o con proteccion.",
        "page":  "repair",
    },
    {
        "icon":  "E",
        "title": "Editar PDF",
        "desc":  "Agrega texto y marcas de agua al PDF.",
        "page":  "edit",
    },
]


class ResponsiveGrid(QWidget):
    """
    Grid de tarjetas que ajusta columnas segun el ancho:
    >= 760px -> 2 col   |   < 760px -> 1 col
    Las tarjetas son horizontales y se ven bien en 1 o 2 columnas.
    """
    navigate = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self._cards: list[ToolCard] = []
        self._cols = -1   # fuerza recalculo en el primer resizeEvent
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(20, 16, 20, 20)
        self._layout.setHorizontalSpacing(14)
        self._layout.setVerticalSpacing(12)
        self._build_cards()

    def _build_cards(self) -> None:
        for tool in TOOLS:
            card = ToolCard(
                icon=tool["icon"],
                title=tool["title"],
                description=tool["desc"],
                page_id=tool["page"],
            )
            card.clicked.connect(self.navigate.emit)
            self._cards.append(card)
        self._place_cards(cols=2)

    def _place_cards(self, cols: int) -> None:
        while self._layout.count():
            self._layout.takeAt(0)
        for i, card in enumerate(self._cards):
            row, col = divmod(i, cols)
            self._layout.addWidget(card, row, col)
        for c in range(cols):
            self._layout.setColumnStretch(c, 1)
        self._cols = cols

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        new_cols = 2 if self.width() >= 600 else 1
        if new_cols != self._cols:
            self._place_cards(new_cols)


class HomePanel(QWidget):
    navigate = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        from PyQt6.QtGui import QPalette, QColor
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor("#F0F0F0"))
        self.setPalette(pal)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_header())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("background-color: #F0F0F0; border: none;")

        self._grid = ResponsiveGrid()
        self._grid.navigate.connect(self.navigate.emit)
        self._grid.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        scroll.setWidget(self._grid)
        root.addWidget(scroll)

    def _make_header(self) -> QWidget:
        header = QWidget()
        header.setFixedHeight(66)
        header.setAutoFillBackground(True)
        from PyQt6.QtGui import QPalette, QColor
        pal = header.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor("#FFFFFF"))
        header.setPalette(pal)
        header.setStyleSheet("border-bottom: 2px solid #E0E0E0;")

        layout = QVBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.setSpacing(2)

        title = QLabel("Inicio")
        title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #1A1A1A; background: transparent;")
        layout.addWidget(title)

        subtitle = QLabel("Selecciona una herramienta para comenzar")
        subtitle.setFont(QFont("Segoe UI", 9))
        subtitle.setStyleSheet("color: #666666; background: transparent;")
        layout.addWidget(subtitle)

        return header
