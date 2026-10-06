"""
ui/panels/settings_panel.py
Panel de configuración global de PDF Master.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QSlider, QFrame, QLineEdit, QFileDialog,
    QButtonGroup, QRadioButton, QScrollArea, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from utils.config_manager import config


CLR_RED    = "#D62828"
CLR_BG     = "#F0F0F0"
CLR_CARD   = "#FFFFFF"
CLR_TITLE  = "#1A1A1A"
CLR_MUTED  = "#6B6B6B"
CLR_BORDER = "#E0E0E0"


def _section_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
    lbl.setStyleSheet(f"color: {CLR_MUTED}; background: transparent; text-transform: uppercase;")
    return lbl


class SettingsPanel(QWidget):
    """Panel de configuración global de la aplicación."""

    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {CLR_BG};")
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(72)
        header.setStyleSheet(f"background-color: {CLR_CARD}; border-bottom: 1px solid {CLR_BORDER};")
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(32, 0, 32, 0)
        h_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        t = QLabel("⚙️  Configuración")
        t.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {CLR_TITLE}; background: transparent;")
        h_layout.addWidget(t)
        root.addWidget(header)

        # ── Cuerpo scrolleable ────────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"background-color: {CLR_BG};")

        body = QWidget()
        body.setStyleSheet(f"background-color: {CLR_BG};")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(32, 24, 32, 32)
        body_layout.setSpacing(20)
        body_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        body_layout.addWidget(self._card_color_mode())
        body_layout.addWidget(self._card_page_size())
        body_layout.addWidget(self._card_quality())
        body_layout.addWidget(self._card_output_folder())
        body_layout.addWidget(self._card_reset())

        scroll.setWidget(body)
        root.addWidget(scroll)

    # ── Tarjetas de configuración ─────────────────────────────────────────────
    def _card(self, title: str) -> tuple[QGroupBox, QVBoxLayout]:
        box = QGroupBox(title)
        box.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        box.setStyleSheet(f"""
            QGroupBox {{
                background-color: {CLR_CARD};
                border: 1px solid {CLR_BORDER};
                border-radius: 8px;
                margin-top: 8px;
                padding: 12px;
                color: {CLR_TITLE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
            }}
        """)
        layout = QVBoxLayout(box)
        layout.setSpacing(10)
        return box, layout

    def _card_color_mode(self) -> QWidget:
        box, layout = self._card("🎨  Modo de color")

        self._color_group = QButtonGroup(self)
        for idx, (value, label) in enumerate([
            ("original",    "Color original"),
            ("grayscale",   "Escala de grises"),
            ("blackwhite",  "Blanco y negro puro"),
        ]):
            rb = QRadioButton(label)
            rb.setFont(QFont("Segoe UI", 10))
            rb.setStyleSheet(f"color: {CLR_TITLE}; background: transparent;")
            rb.setChecked(config.get("color_mode") == value)
            rb.toggled.connect(lambda checked, v=value: checked and config.set("color_mode", v))
            self._color_group.addButton(rb, idx)
            layout.addWidget(rb)
        return box

    def _card_page_size(self) -> QWidget:
        box, layout = self._card("📄  Tamaño de hoja")

        row = QHBoxLayout()
        row.setSpacing(12)

        # Tamaño de hoja
        size_col = QVBoxLayout()
        size_col.addWidget(_section_label("Tamaño"))
        self._size_combo = QComboBox()
        self._size_combo.setFont(QFont("Segoe UI", 10))
        self._size_combo.setFixedHeight(32)
        self._size_combo.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {CLR_BORDER};
                border-radius: 6px;
                padding: 4px 8px;
                background: white;
                color: {CLR_TITLE};
            }}
            QComboBox::drop-down {{ border: none; }}
        """)
        for sz in ["A4", "Carta (Letter)", "Legal", "A3", "A5", "Personalizado"]:
            self._size_combo.addItem(sz)
        current = config.get("page_size")
        idx = self._size_combo.findText(current)
        if idx >= 0:
            self._size_combo.setCurrentIndex(idx)
        self._size_combo.currentTextChanged.connect(
            lambda t: config.set("page_size", t.split(" ")[0])
        )
        size_col.addWidget(self._size_combo)
        row.addLayout(size_col)

        # Orientación
        orient_col = QVBoxLayout()
        orient_col.addWidget(_section_label("Orientación"))
        self._orient_group = QButtonGroup(self)
        orient_row = QHBoxLayout()
        for value, label in [("portrait", "↕ Portrait"), ("landscape", "↔ Landscape")]:
            rb = QRadioButton(label)
            rb.setFont(QFont("Segoe UI", 10))
            rb.setStyleSheet(f"color: {CLR_TITLE}; background: transparent;")
            rb.setChecked(config.get("orientation") == value)
            rb.toggled.connect(lambda checked, v=value: checked and config.set("orientation", v))
            self._orient_group.addButton(rb)
            orient_row.addWidget(rb)
        orient_col.addLayout(orient_row)
        row.addLayout(orient_col)

        layout.addLayout(row)
        return box

    def _card_quality(self) -> QWidget:
        box, layout = self._card("🔍  Calidad de imagen")

        label_row = QHBoxLayout()
        lbl = QLabel("Calidad de salida:")
        lbl.setFont(QFont("Segoe UI", 10))
        lbl.setStyleSheet(f"color: {CLR_TITLE}; background: transparent;")
        self._quality_val = QLabel(f"{config.get('image_quality')}%")
        self._quality_val.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._quality_val.setStyleSheet(f"color: {CLR_RED}; background: transparent;")
        label_row.addWidget(lbl)
        label_row.addStretch()
        label_row.addWidget(self._quality_val)
        layout.addLayout(label_row)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(10, 100)
        slider.setValue(config.get("image_quality"))
        slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{ height: 4px; background: {CLR_BORDER}; border-radius: 2px; }}
            QSlider::handle:horizontal {{
                background: {CLR_RED}; border-radius: 7px;
                width: 14px; height: 14px; margin: -5px 0;
            }}
            QSlider::sub-page:horizontal {{ background: {CLR_RED}; border-radius: 2px; }}
        """)
        slider.valueChanged.connect(lambda v: (
            config.set("image_quality", v),
            self._quality_val.setText(f"{v}%")
        ))
        layout.addWidget(slider)
        return box

    def _card_output_folder(self) -> QWidget:
        box, layout = self._card("📁  Carpeta de salida predeterminada")

        row = QHBoxLayout()
        self._folder_edit = QLineEdit(config.get("output_folder") or "")
        self._folder_edit.setPlaceholderText("Misma carpeta del archivo original")
        self._folder_edit.setFont(QFont("Segoe UI", 10))
        self._folder_edit.setFixedHeight(32)
        self._folder_edit.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {CLR_BORDER};
                border-radius: 6px;
                padding: 4px 8px;
                background: white;
                color: {CLR_TITLE};
            }}
        """)
        self._folder_edit.textChanged.connect(lambda t: config.set("output_folder", t))

        browse_btn = QPushButton("Examinar")
        browse_btn.setFixedHeight(32)
        browse_btn.setFont(QFont("Segoe UI", 9))
        browse_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CLR_RED};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0 16px;
            }}
            QPushButton:hover {{ background-color: #B52020; }}
        """)
        browse_btn.clicked.connect(self._browse_folder)

        row.addWidget(self._folder_edit)
        row.addWidget(browse_btn)
        layout.addLayout(row)
        return box

    def _card_reset(self) -> QWidget:
        box, layout = self._card("⚠️  Restablecer")
        btn = QPushButton("Restablecer configuración predeterminada")
        btn.setFixedHeight(36)
        btn.setFont(QFont("Segoe UI", 10))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {CLR_RED};
                border: 2px solid {CLR_RED};
                border-radius: 6px;
                padding: 0 16px;
            }}
            QPushButton:hover {{ background-color: #FFF0F0; }}
        """)
        btn.clicked.connect(self._reset)
        layout.addWidget(btn)
        return box

    def _browse_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de salida")
        if folder:
            self._folder_edit.setText(folder)

    def _reset(self) -> None:
        config.reset_to_defaults()
        self.settings_changed.emit()
        # Recargar panel
        parent = self.parent()
        if parent:
            parent.repaint()
