"""
ui/panels/img_to_pdf_panel.py
Panel completo de conversion Imagenes -> PDF.
Layout: DropZone + FileList (izq) | Opciones + Boton (der)
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSlider, QLineEdit, QFileDialog, QFrame,
    QButtonGroup, QRadioButton, QProgressBar, QMessageBox,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QPalette, QColor

from ui.components.drop_zone import DropZone
from ui.components.file_list import FileListWidget
from tools.img_to_pdf import convert_images_to_pdf, suggest_output_name
from utils.config_manager import config


# ── Paleta ────────────────────────────────────────────────────────────────────
RED    = "#D62828"
WHITE  = "#FFFFFF"
BG     = "#F0F0F0"
BORDER = "#E0E0E0"
DARK   = "#1A1A1A"
MUTED  = "#666666"


# ── Worker thread ─────────────────────────────────────────────────────────────
class ConversionWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error    = pyqtSignal(str)

    def __init__(self, image_paths, output_path, page_size,
                 orientation, color_mode, quality):
        super().__init__()
        self.image_paths  = image_paths
        self.output_path  = output_path
        self.page_size    = page_size
        self.orientation  = orientation
        self.color_mode   = color_mode
        self.quality      = quality

    def run(self):
        try:
            result = convert_images_to_pdf(
                image_paths=self.image_paths,
                output_path=self.output_path,
                page_size=self.page_size,
                orientation=self.orientation,
                color_mode=self.color_mode,
                quality=self.quality,
                progress_cb=self.progress.emit,
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


# ── Panel principal ───────────────────────────────────────────────────────────
class ImgToPdfPanel(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(BG))
        self.setPalette(pal)
        self._worker: ConversionWorker | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        root.addWidget(self._make_header())

        # Cuerpo: izquierda + derecha
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        body_lay = QHBoxLayout(body)
        body_lay.setContentsMargins(16, 14, 16, 14)
        body_lay.setSpacing(14)

        # Columna izquierda (archivos)
        left = self._make_left_col()
        body_lay.addWidget(left, stretch=6)

        # Columna derecha (opciones)
        right = self._make_right_col()
        body_lay.addWidget(right, stretch=4)

        root.addWidget(body)

        # Barra de progreso + status
        root.addWidget(self._make_status_bar())

    # ── Header ────────────────────────────────────────────────────────────────
    def _make_header(self) -> QWidget:
        h = QWidget()
        h.setFixedHeight(66)
        h.setAutoFillBackground(True)
        pal = h.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(WHITE))
        h.setPalette(pal)
        h.setStyleSheet("border-bottom: 2px solid #E0E0E0;")
        lay = QVBoxLayout(h)
        lay.setContentsMargins(22, 0, 22, 0)
        lay.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        lay.setSpacing(2)
        t = QLabel("Imagenes a PDF")
        t.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {DARK}; background: transparent;")
        lay.addWidget(t)
        s = QLabel("Arrastra imagenes, ordenarlas y convierte a PDF")
        s.setFont(QFont("Segoe UI", 9))
        s.setStyleSheet(f"color: {MUTED}; background: transparent;")
        lay.addWidget(s)
        return h

    # ── Columna izquierda ─────────────────────────────────────────────────────
    def _make_left_col(self) -> QWidget:
        col = QWidget()
        col.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(col)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        # Drop zone
        drop = DropZone(
            accepted_extensions=["jpg", "jpeg", "png", "bmp", "tiff", "tif", "webp"],
            message="Arrastra imagenes aqui",
            sub_message="JPG  PNG  BMP  TIFF  WEBP",
        )
        drop.files_dropped.connect(self._on_files_dropped)
        lay.addWidget(drop, stretch=1)

        # Lista de archivos
        lbl = QLabel("Archivos cargados:")
        lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {DARK}; background: transparent;")
        lay.addWidget(lbl)

        self._file_list = FileListWidget(file_type_label="imagen")
        self._file_list.files_changed.connect(self._on_files_changed)
        self._file_list.setSizePolicy(QSizePolicy.Policy.Expanding,
                                      QSizePolicy.Policy.Expanding)
        lay.addWidget(self._file_list, stretch=2)

        return col

    # ── Columna derecha ───────────────────────────────────────────────────────
    def _make_right_col(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        card = QWidget()
        card.setAutoFillBackground(True)
        cp = card.palette()
        cp.setColor(QPalette.ColorRole.Window, QColor(WHITE))
        card.setPalette(cp)
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {WHITE};
                border-radius: 10px;
                border: 1px solid {BORDER};
            }}
        """)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 16, 18, 18)
        lay.setSpacing(14)

        # -- Titulo opciones --
        t = QLabel("Opciones de conversion")
        t.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {DARK}; background: transparent; border: none;")
        lay.addWidget(t)

        lay.addWidget(self._divider())

        # -- Tamanio de hoja --
        lay.addWidget(self._sec_label("Tamanio de hoja"))
        self._size_combo = self._make_combo(
            ["A4", "Letter", "Legal", "A3", "A5"],
            config.get("page_size", "A4")
        )
        lay.addWidget(self._size_combo)

        # -- Orientacion --
        lay.addWidget(self._sec_label("Orientacion"))
        orient_row = QHBoxLayout()
        self._orient_grp = QButtonGroup(self)
        for val, lbl in [("portrait", "Portrait"), ("landscape", "Landscape")]:
            rb = self._make_radio(lbl, val == config.get("orientation", "portrait"))
            self._orient_grp.addButton(rb)
            orient_row.addWidget(rb)
        lay.addLayout(orient_row)

        # -- Color --
        lay.addWidget(self._sec_label("Modo de color"))
        color_row = QHBoxLayout()
        self._color_grp = QButtonGroup(self)
        cfg_color = config.get("color_mode", "original")
        for val, lbl in [("original", "Original"), ("grayscale", "Grises"), ("blackwhite", "B y N")]:
            rb = self._make_radio(lbl, val == cfg_color)
            self._color_grp.addButton(rb)
            color_row.addWidget(rb)
        lay.addLayout(color_row)

        # -- Calidad --
        lay.addWidget(self._sec_label("Calidad de imagen"))
        q_row = QHBoxLayout()
        self._quality_lbl = QLabel(f"{config.get('image_quality', 85)}%")
        self._quality_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self._quality_lbl.setStyleSheet(f"color: {RED}; background: transparent; border: none;")
        q_row.addWidget(QLabel("10%"))
        self._quality_slider = QSlider(Qt.Orientation.Horizontal)
        self._quality_slider.setRange(10, 100)
        self._quality_slider.setValue(config.get("image_quality", 85))
        self._quality_slider.setStyleSheet(self._slider_style())
        self._quality_slider.valueChanged.connect(
            lambda v: self._quality_lbl.setText(f"{v}%")
        )
        q_row.addWidget(self._quality_slider)
        q_row.addWidget(self._quality_lbl)
        lay.addLayout(q_row)

        # -- Archivo de salida --
        lay.addWidget(self._sec_label("Archivo de salida"))
        out_row = QHBoxLayout()
        self._output_edit = QLineEdit()
        self._output_edit.setPlaceholderText("Se genera automaticamente")
        self._output_edit.setFont(QFont("Segoe UI", 9))
        self._output_edit.setFixedHeight(30)
        self._output_edit.setStyleSheet(self._input_style())
        out_row.addWidget(self._output_edit)
        browse = QPushButton("...")
        browse.setFixedSize(30, 30)
        browse.setStyleSheet(self._small_btn_style())
        browse.clicked.connect(self._browse_output)
        out_row.addWidget(browse)
        lay.addLayout(out_row)

        lay.addStretch()
        lay.addWidget(self._divider())

        # -- Boton convertir --
        self._convert_btn = QPushButton("  Convertir a PDF")
        self._convert_btn.setFixedHeight(42)
        self._convert_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self._convert_btn.setEnabled(False)
        self._convert_btn.setStyleSheet(self._action_btn_style())
        self._convert_btn.clicked.connect(self._start_conversion)
        lay.addWidget(self._convert_btn)

        scroll.setWidget(card)
        return scroll

    # ── Barra de estado/progreso ──────────────────────────────────────────────
    def _make_status_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(42)
        bar.setAutoFillBackground(True)
        bp = bar.palette()
        bp.setColor(QPalette.ColorRole.Window, QColor(WHITE))
        bar.setPalette(bp)
        bar.setStyleSheet(f"border-top: 1px solid {BORDER};")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(16, 6, 16, 6)

        self._status_lbl = QLabel("Listo. Carga imagenes para comenzar.")
        self._status_lbl.setFont(QFont("Segoe UI", 9))
        self._status_lbl.setStyleSheet(f"color: {MUTED}; background: transparent;")
        lay.addWidget(self._status_lbl)

        lay.addStretch()

        self._progress = QProgressBar()
        self._progress.setFixedWidth(200)
        self._progress.setFixedHeight(10)
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(False)
        self._progress.setStyleSheet(f"""
            QProgressBar {{ border: none; border-radius: 5px; background: #EBEBEB; }}
            QProgressBar::chunk {{ background-color: {RED}; border-radius: 5px; }}
        """)
        self._progress.hide()
        lay.addWidget(self._progress)

        return bar

    # ── Slots ─────────────────────────────────────────────────────────────────
    def _on_files_dropped(self, paths: list[str]) -> None:
        self._file_list.add_files(paths)

    def _on_files_changed(self, paths: list[str]) -> None:
        has = len(paths) > 0
        self._convert_btn.setEnabled(has)
        if has and not self._output_edit.text():
            self._output_edit.setText(suggest_output_name(paths[0]))

    def _browse_output(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF como", self._output_edit.text(),
            "Archivos PDF (*.pdf)"
        )
        if path:
            if not path.lower().endswith(".pdf"):
                path += ".pdf"
            self._output_edit.setText(path)

    def _get_selected_orientation(self) -> str:
        for btn in self._orient_grp.buttons():
            if btn.isChecked():
                return "landscape" if "Landscape" in btn.text() else "portrait"
        return "portrait"

    def _get_selected_color(self) -> str:
        for btn in self._color_grp.buttons():
            if btn.isChecked():
                t = btn.text()
                if "Grises" in t:   return "grayscale"
                if "B y N"  in t:   return "blackwhite"
        return "original"

    def _start_conversion(self) -> None:
        files = self._file_list.get_files()
        if not files:
            return

        output = self._output_edit.text().strip()
        if not output:
            output = suggest_output_name(files[0])
            self._output_edit.setText(output)

        self._convert_btn.setEnabled(False)
        self._progress.show()
        self._progress.setValue(0)
        self._status_lbl.setText("Convirtiendo...")

        self._worker = ConversionWorker(
            image_paths=files,
            output_path=output,
            page_size=self._size_combo.currentText(),
            orientation=self._get_selected_orientation(),
            color_mode=self._get_selected_color(),
            quality=self._quality_slider.value(),
        )
        self._worker.progress.connect(self._progress.setValue)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_finished(self, output_path: str) -> None:
        self._progress.setValue(100)
        self._convert_btn.setEnabled(True)
        self._status_lbl.setText(f"Listo: {os.path.basename(output_path)}")
        QMessageBox.information(
            self, "Conversion completada",
            f"PDF generado correctamente:\n{output_path}",
        )

    def _on_error(self, msg: str) -> None:
        self._convert_btn.setEnabled(True)
        self._progress.hide()
        self._status_lbl.setText("Error en la conversion.")
        QMessageBox.critical(self, "Error", f"No se pudo convertir:\n{msg}")

    # ── Helpers de estilo ─────────────────────────────────────────────────────
    def _sec_label(self, text: str) -> QLabel:
        lbl = QLabel(text.upper())
        lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {MUTED}; background: transparent; border: none;")
        return lbl

    def _divider(self) -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setFixedHeight(1)
        f.setStyleSheet(f"background: {BORDER}; border: none;")
        return f

    def _make_combo(self, items: list[str], current: str) -> QComboBox:
        cb = QComboBox()
        cb.setFont(QFont("Segoe UI", 9))
        cb.setFixedHeight(30)
        cb.addItems(items)
        idx = cb.findText(current)
        if idx >= 0:
            cb.setCurrentIndex(idx)
        cb.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {BORDER}; border-radius: 5px;
                padding: 3px 8px; background: white; color: {DARK};
            }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
            QComboBox QAbstractItemView {{ background: white; color: {DARK}; }}
        """)
        return cb

    def _make_radio(self, label: str, checked: bool) -> QRadioButton:
        rb = QRadioButton(label)
        rb.setFont(QFont("Segoe UI", 9))
        rb.setChecked(checked)
        rb.setStyleSheet(f"""
            QRadioButton {{ color: {DARK}; background: transparent; border: none; }}
            QRadioButton::indicator:checked {{ background: {RED}; border: 2px solid {RED}; border-radius: 6px; }}
        """)
        return rb

    def _slider_style(self) -> str:
        return f"""
            QSlider::groove:horizontal {{ height: 4px; background: #E0E0E0; border-radius: 2px; }}
            QSlider::handle:horizontal {{
                background: {RED}; border-radius: 7px; width: 14px; height: 14px; margin: -5px 0;
            }}
            QSlider::sub-page:horizontal {{ background: {RED}; border-radius: 2px; }}
        """

    def _input_style(self) -> str:
        return f"""
            QLineEdit {{
                border: 1px solid {BORDER}; border-radius: 5px;
                padding: 4px 8px; background: white; color: {DARK};
            }}
        """

    def _small_btn_style(self) -> str:
        return f"""
            QPushButton {{
                background: #F0F0F0; border: 1px solid {BORDER};
                border-radius: 5px; color: {DARK};
            }}
            QPushButton:hover {{ background: #E0E0E0; }}
        """

    def _action_btn_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: {RED}; color: white; border: none;
                border-radius: 8px; font-size: 11pt; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #B82020; }}
            QPushButton:disabled {{ background-color: #CCCCCC; color: #999999; }}
        """

    # ── Método público: cargar archivo externo (Fase 5) ───────────────────────
    def load_file(self, path: str) -> None:
        self._file_list.add_files([path])
