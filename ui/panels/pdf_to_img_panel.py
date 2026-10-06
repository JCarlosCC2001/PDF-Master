"""
ui/panels/pdf_to_img_panel.py
Panel de conversion PDF -> Imagenes.
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QFileDialog, QFrame, QButtonGroup,
    QRadioButton, QProgressBar, QMessageBox, QScrollArea,
    QSizePolicy, QSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

from ui.components.drop_zone import DropZone
from tools.pdf_to_img import convert_pdf_to_images, get_pdf_info, suggest_output_dir
from utils.config_manager import config


RED    = "#D62828"
WHITE  = "#FFFFFF"
BG     = "#F0F0F0"
BORDER = "#E0E0E0"
DARK   = "#1A1A1A"
MUTED  = "#666666"


class ConversionWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)
    error    = pyqtSignal(str)

    def __init__(self, pdf_path, output_dir, dpi, fmt, color_mode):
        super().__init__()
        self.pdf_path   = pdf_path
        self.output_dir = output_dir
        self.dpi        = dpi
        self.fmt        = fmt
        self.color_mode = color_mode

    def run(self):
        try:
            result = convert_pdf_to_images(
                pdf_path=self.pdf_path,
                output_dir=self.output_dir,
                dpi=self.dpi,
                image_format=self.fmt,
                color_mode=self.color_mode,
                progress_cb=self.progress.emit,
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class PdfToImgPanel(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(BG))
        self.setPalette(pal)
        self._pdf_path: str = ""
        self._worker: ConversionWorker | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_header())

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        body_lay = QHBoxLayout(body)
        body_lay.setContentsMargins(16, 14, 16, 14)
        body_lay.setSpacing(14)
        body_lay.addWidget(self._make_left_col(), stretch=6)
        body_lay.addWidget(self._make_right_col(), stretch=4)
        root.addWidget(body)

        root.addWidget(self._make_status_bar())

    def _make_header(self) -> QWidget:
        h = QWidget()
        h.setFixedHeight(66)
        h.setAutoFillBackground(True)
        p = h.palette()
        p.setColor(QPalette.ColorRole.Window, QColor(WHITE))
        h.setPalette(p)
        h.setStyleSheet("border-bottom: 2px solid #E0E0E0;")
        lay = QVBoxLayout(h)
        lay.setContentsMargins(22, 0, 22, 0)
        lay.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        lay.setSpacing(2)
        t = QLabel("PDF a Imagenes")
        t.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {DARK}; background: transparent;")
        lay.addWidget(t)
        s = QLabel("Extrae las paginas de un PDF como imagenes")
        s.setFont(QFont("Segoe UI", 9))
        s.setStyleSheet(f"color: {MUTED}; background: transparent;")
        lay.addWidget(s)
        return h

    def _make_left_col(self) -> QWidget:
        col = QWidget()
        col.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(col)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        # Drop zone solo PDF
        self._drop = DropZone(
            accepted_extensions=["pdf"],
            message="Arrastra un archivo PDF aqui",
            sub_message="Solo archivos .pdf",
        )
        self._drop.files_dropped.connect(self._on_pdf_dropped)
        lay.addWidget(self._drop, stretch=2)

        # Info del PDF cargado
        self._info_card = QWidget()
        self._info_card.setAutoFillBackground(True)
        ip = self._info_card.palette()
        ip.setColor(QPalette.ColorRole.Window, QColor(WHITE))
        self._info_card.setPalette(ip)
        self._info_card.setStyleSheet(f"""
            QWidget {{
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
        """)
        info_lay = QVBoxLayout(self._info_card)
        info_lay.setContentsMargins(14, 10, 14, 10)
        info_lay.setSpacing(4)

        self._info_name = QLabel("Ningun archivo cargado")
        self._info_name.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._info_name.setStyleSheet(f"color: {DARK}; background: transparent; border: none;")
        info_lay.addWidget(self._info_name)

        self._info_detail = QLabel("")
        self._info_detail.setFont(QFont("Segoe UI", 8))
        self._info_detail.setStyleSheet(f"color: {MUTED}; background: transparent; border: none;")
        info_lay.addWidget(self._info_detail)

        lay.addWidget(self._info_card, stretch=1)

        return col

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
        card.setStyleSheet(f"background-color: {WHITE}; border-radius: 10px; border: 1px solid {BORDER};")

        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 16, 18, 18)
        lay.setSpacing(14)

        t = QLabel("Opciones de extraccion")
        t.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {DARK}; background: transparent; border: none;")
        lay.addWidget(t)
        lay.addWidget(self._divider())

        # DPI
        lay.addWidget(self._sec_label("Resolucion (DPI)"))
        self._dpi_combo = self._make_combo(["72", "96", "150", "200", "300", "600"], "150")
        lay.addWidget(self._dpi_combo)

        # Formato
        lay.addWidget(self._sec_label("Formato de salida"))
        fmt_row = QHBoxLayout()
        self._fmt_grp = QButtonGroup(self)
        for fmt in ["PNG", "JPG", "TIFF"]:
            rb = self._make_radio(fmt, fmt == "PNG")
            self._fmt_grp.addButton(rb)
            fmt_row.addWidget(rb)
        lay.addLayout(fmt_row)

        # Color
        lay.addWidget(self._sec_label("Modo de color"))
        color_row = QHBoxLayout()
        self._color_grp = QButtonGroup(self)
        cfg_color = config.get("color_mode", "original")
        for val, lbl in [("original", "Original"), ("grayscale", "Grises")]:
            rb = self._make_radio(lbl, val == cfg_color)
            self._color_grp.addButton(rb)
            color_row.addWidget(rb)
        lay.addLayout(color_row)

        # Carpeta salida
        lay.addWidget(self._sec_label("Carpeta de salida"))
        out_row = QHBoxLayout()
        self._output_edit = QLineEdit()
        self._output_edit.setPlaceholderText("Junto al PDF original")
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

        self._convert_btn = QPushButton("  Extraer Imagenes")
        self._convert_btn.setFixedHeight(42)
        self._convert_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self._convert_btn.setEnabled(False)
        self._convert_btn.setStyleSheet(self._action_btn_style())
        self._convert_btn.clicked.connect(self._start_conversion)
        lay.addWidget(self._convert_btn)

        scroll.setWidget(card)
        return scroll

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

        self._status_lbl = QLabel("Listo. Carga un PDF para comenzar.")
        self._status_lbl.setFont(QFont("Segoe UI", 9))
        self._status_lbl.setStyleSheet(f"color: {MUTED}; background: transparent;")
        lay.addWidget(self._status_lbl)
        lay.addStretch()

        self._progress = QProgressBar()
        self._progress.setFixedWidth(200)
        self._progress.setFixedHeight(10)
        self._progress.setRange(0, 100)
        self._progress.setTextVisible(False)
        self._progress.setStyleSheet(f"""
            QProgressBar {{ border: none; border-radius: 5px; background: #EBEBEB; }}
            QProgressBar::chunk {{ background-color: {RED}; border-radius: 5px; }}
        """)
        self._progress.hide()
        lay.addWidget(self._progress)

        return bar

    # ── Slots ─────────────────────────────────────────────────────────────────
    def _on_pdf_dropped(self, paths: list[str]) -> None:
        pdf = next((p for p in paths if p.lower().endswith(".pdf")), None)
        if pdf:
            self.load_file(pdf)

    def load_file(self, path: str) -> None:
        self._pdf_path = path
        try:
            info = get_pdf_info(path)
            self._info_name.setText(os.path.basename(path))
            self._info_detail.setText(
                f"{info['pages']} paginas  |  {info['file_size_mb']} MB"
            )
        except Exception:
            self._info_name.setText(os.path.basename(path))
            self._info_detail.setText("")
        self._output_edit.setText(suggest_output_dir(path))
        self._convert_btn.setEnabled(True)
        self._status_lbl.setText(f"PDF cargado: {os.path.basename(path)}")

    def _browse_output(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Carpeta de salida",
                                                  self._output_edit.text())
        if folder:
            self._output_edit.setText(folder)

    def _get_selected_fmt(self) -> str:
        for btn in self._fmt_grp.buttons():
            if btn.isChecked():
                return btn.text()
        return "PNG"

    def _get_selected_color(self) -> str:
        for btn in self._color_grp.buttons():
            if btn.isChecked():
                return "grayscale" if "Grises" in btn.text() else "original"
        return "original"

    def _start_conversion(self) -> None:
        if not self._pdf_path:
            return
        output = self._output_edit.text().strip() or suggest_output_dir(self._pdf_path)
        dpi = int(self._dpi_combo.currentText())

        self._convert_btn.setEnabled(False)
        self._progress.show()
        self._progress.setValue(0)
        self._status_lbl.setText("Extrayendo imagenes...")

        self._worker = ConversionWorker(
            pdf_path=self._pdf_path,
            output_dir=output,
            dpi=dpi,
            fmt=self._get_selected_fmt(),
            color_mode=self._get_selected_color(),
        )
        self._worker.progress.connect(self._progress.setValue)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_finished(self, output_paths: list[str]) -> None:
        self._progress.setValue(100)
        self._convert_btn.setEnabled(True)
        n = len(output_paths)
        folder = os.path.dirname(output_paths[0]) if output_paths else ""
        self._status_lbl.setText(f"{n} imagenes generadas.")
        QMessageBox.information(
            self, "Extraccion completada",
            f"Se generaron {n} imagenes en:\n{folder}",
        )

    def _on_error(self, msg: str) -> None:
        self._convert_btn.setEnabled(True)
        self._progress.hide()
        self._status_lbl.setText("Error en la extraccion.")
        QMessageBox.critical(self, "Error", f"No se pudo extraer:\n{msg}")

    # ── Helpers estilo ────────────────────────────────────────────────────────
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

    def _make_combo(self, items, current) -> QComboBox:
        cb = QComboBox()
        cb.setFont(QFont("Segoe UI", 9))
        cb.setFixedHeight(30)
        cb.addItems(items)
        idx = cb.findText(current)
        if idx >= 0:
            cb.setCurrentIndex(idx)
        cb.setStyleSheet(f"""
            QComboBox {{ border: 1px solid {BORDER}; border-radius: 5px;
                padding: 3px 8px; background: white; color: {DARK}; }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
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

    def _input_style(self) -> str:
        return f"QLineEdit {{ border: 1px solid {BORDER}; border-radius: 5px; padding: 4px 8px; background: white; color: {DARK}; }}"

    def _small_btn_style(self) -> str:
        return f"QPushButton {{ background: #F0F0F0; border: 1px solid {BORDER}; border-radius: 5px; color: {DARK}; }} QPushButton:hover {{ background: #E0E0E0; }}"

    def _action_btn_style(self) -> str:
        return f"""
            QPushButton {{ background-color: {RED}; color: white; border: none; border-radius: 8px; font-size: 11pt; font-weight: bold; }}
            QPushButton:hover {{ background-color: #B82020; }}
            QPushButton:disabled {{ background-color: #CCCCCC; color: #999999; }}
        """
