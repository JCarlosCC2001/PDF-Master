"""
ui/components/sidebar.py
Barra lateral de navegacion principal de PDF Master.
NOTA: Los botones NO usan 'transparent' porque en PyQt6 puede
      renderizarse como blanco en vez del fondo del padre.
      Se usa el color de fondo explicito en cada estado.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor, QPalette, QColor


BG      = "#1C1C1C"   # fondo sidebar
ACTIVE  = "#D62828"   # rojo activo
A_HOVER = "#B82020"   # rojo hover
HOVER   = "#2D2D2D"   # gris hover inactivo
TEXT    = "#E8E8E8"   # texto normal
DIVIDER = "#303030"   # separador


MENU_ITEMS = [
    ("home",    "Inicio"),
    ("img2pdf", "Img a PDF"),
    ("pdf2img", "PDF a Img"),
    ("merge",   "Unir PDF"),
    ("reorder", "Reordenar"),
    ("repair",  "Reparar PDF"),
    ("edit",    "Editar PDF"),
]


class SidebarButton(QPushButton):

    def __init__(self, page_id: str, label: str, parent=None):
        super().__init__(parent)
        self.page_id = page_id
        self.setText(label)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedHeight(42)
        self.setFont(QFont("Segoe UI", 10))
        self._apply_style(active=False)

    def set_active(self, active: bool) -> None:
        self._apply_style(active)

    def _apply_style(self, active: bool) -> None:
        if active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ACTIVE};
                    color: #FFFFFF;
                    border: none;
                    border-radius: 6px;
                    padding-left: 14px;
                    text-align: left;
                    font-size: 10pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {A_HOVER};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {BG};
                    color: {TEXT};
                    border: none;
                    border-radius: 6px;
                    padding-left: 14px;
                    text-align: left;
                    font-size: 10pt;
                }}
                QPushButton:hover {{
                    background-color: {HOVER};
                    color: #FFFFFF;
                }}
            """)


class Sidebar(QWidget):
    page_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        # Fondo explicito via QPalette para garantizar el color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(BG))
        self.setPalette(palette)
        # Stylesheet adicional para cubrir bordes/margenes
        self.setStyleSheet(f"QWidget {{ background-color: {BG}; border: none; }}")
        self._buttons: dict[str, SidebarButton] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 8)
        layout.setSpacing(3)

        # ── Logo ──────────────────────────────────────────────────────────────
        logo_w = QWidget()
        logo_w.setFixedHeight(74)
        logo_w.setStyleSheet(f"background-color: {BG};")
        logo_lay = QVBoxLayout(logo_w)
        logo_lay.setContentsMargins(10, 20, 10, 6)
        logo_lay.setSpacing(2)

        title_lbl = QLabel("PDF Master")
        title_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title_lbl.setStyleSheet(f"color: #FFFFFF; background: {BG};")
        logo_lay.addWidget(title_lbl)

        sub_lbl = QLabel("Herramientas PDF")
        sub_lbl.setFont(QFont("Segoe UI", 8))
        sub_lbl.setStyleSheet(f"color: #888888; background: {BG};")
        logo_lay.addWidget(sub_lbl)
        layout.addWidget(logo_w)

        # Separador
        layout.addWidget(self._sep())
        layout.addSpacing(6)

        # ── Botones de menu ───────────────────────────────────────────────────
        for page_id, label in MENU_ITEMS:
            btn = SidebarButton(page_id, label)
            btn.clicked.connect(lambda _, pid=page_id: self._on_click(pid))
            self._buttons[page_id] = btn
            layout.addWidget(btn)

        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum,
                                        QSizePolicy.Policy.Expanding))

        layout.addWidget(self._sep())
        layout.addSpacing(4)

        # Boton configuracion
        cfg = SidebarButton("settings", "Configuracion")
        cfg.clicked.connect(lambda: self._on_click("settings"))
        self._buttons["settings"] = cfg
        layout.addWidget(cfg)

        self.set_active_page("home")

    def _sep(self) -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setFixedHeight(1)
        f.setStyleSheet(f"background-color: {DIVIDER}; border: none; max-height: 1px;")
        return f

    def _on_click(self, page_id: str) -> None:
        self.set_active_page(page_id)
        self.page_changed.emit(page_id)

    def set_active_page(self, page_id: str) -> None:
        for pid, btn in self._buttons.items():
            btn.set_active(pid == page_id)
