"""
ui/components/card_button.py
Tarjeta de herramienta para el dashboard principal.
Diseno limpio: linea de color rojo lateral + icono de texto grande + titulo + descripcion.
"""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QGraphicsDropShadowEffect, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QCursor, QEnterEvent


# Paleta
CLR_BG     = "#FFFFFF"
CLR_HOVER  = "#FEF2F2"
CLR_ACCENT = "#D62828"
CLR_TITLE  = "#1A1A1A"
CLR_DESC   = "#5A5A5A"
CLR_BORDER = "#EBEBEB"

# Icono y datos por herramienta
TOOL_DATA = {
    "img2pdf": {"letter": "I",  "color": "#D62828"},
    "pdf2img": {"letter": "P",  "color": "#C0392B"},
    "merge":   {"letter": "+",  "color": "#D62828"},
    "reorder": {"letter": "R",  "color": "#C0392B"},
    "repair":  {"letter": "F",  "color": "#D62828"},
    "edit":    {"letter": "E",  "color": "#C0392B"},
}


class ToolCard(QWidget):
    """
    Tarjeta clickable con diseno de barra lateral roja.
    Layout: [barra roja 5px] | [icono circulo] | [titulo + descripcion]
    """
    clicked = pyqtSignal(str)

    def __init__(self, icon: str, title: str, description: str,
                 page_id: str, color: str = CLR_ACCENT, parent=None):
        super().__init__(parent)
        self.page_id = page_id
        self._accent = color
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumSize(180, 100)
        self.setMaximumHeight(120)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._build_ui(icon, title, description, page_id)
        self._add_shadow()
        self._apply_style(hovered=False)

    def _build_ui(self, icon: str, title: str, description: str, page_id: str) -> None:
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Barra lateral de color ────────────────────────────────────────────
        bar = QFrame()
        bar.setFixedWidth(6)
        bar.setStyleSheet(f"background-color: {self._accent}; border-radius: 10px 0 0 10px;")
        outer.addWidget(bar)

        # ── Contenido principal ───────────────────────────────────────────────
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_lay = QHBoxLayout(content)
        content_lay.setContentsMargins(14, 12, 16, 12)
        content_lay.setSpacing(14)

        # Circulo con letra
        letter_data = TOOL_DATA.get(page_id, {"letter": "?", "color": self._accent})
        circle = QLabel(letter_data["letter"])
        circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        circle.setFixedSize(46, 46)
        font_c = QFont("Segoe UI", 18, QFont.Weight.Bold)
        circle.setFont(font_c)
        circle.setStyleSheet(f"""
            QLabel {{
                background-color: {letter_data['color']};
                color: #FFFFFF;
                border-radius: 23px;
            }}
        """)
        content_lay.addWidget(circle, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Texto: titulo + descripcion
        text_col = QVBoxLayout()
        text_col.setSpacing(4)

        title_lbl = QLabel(title)
        title_font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        title_lbl.setFont(title_font)
        title_lbl.setStyleSheet(f"color: {CLR_TITLE}; background: transparent;")
        title_lbl.setWordWrap(True)
        text_col.addWidget(title_lbl)

        desc_lbl = QLabel(description)
        desc_font = QFont("Segoe UI", 8)
        desc_lbl.setFont(desc_font)
        desc_lbl.setStyleSheet(f"color: {CLR_DESC}; background: transparent;")
        desc_lbl.setWordWrap(True)
        text_col.addWidget(desc_lbl)

        content_lay.addLayout(text_col)
        outer.addWidget(content)

    def _add_shadow(self) -> None:
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 25))
        self.setGraphicsEffect(shadow)

    def _apply_style(self, hovered: bool) -> None:
        bg = CLR_HOVER if hovered else CLR_BG
        self.setStyleSheet(f"""
            ToolCard {{
                background-color: {bg};
                border-radius: 10px;
                border: 1px solid {CLR_BORDER};
            }}
        """)

    def enterEvent(self, event: QEnterEvent) -> None:
        self._apply_style(hovered=True)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._apply_style(hovered=False)
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.page_id)
        super().mousePressEvent(event)
