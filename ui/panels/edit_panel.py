"""
ui/panels/edit_panel.py
Panel de edicion basica de PDF: texto superpuesto, marca de agua, paginas en blanco.
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QFrame, QProgressBar, QMessageBox,
    QScrollArea, QButtonGroup, QRadioButton, QSlider,
    QSpinBox, QComboBox, QStackedWidget, QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

from ui.components.drop_zone import DropZone
from tools.edit_pdf import (
    add_watermark_text, add_text_overlay,
    insert_blank_pages, suggest_output_name
)
from tools.pdf_to_img import get_pdf_info


RED    = "#D62828"
WHITE  = "#FFFFFF"
BG     = "#F0F0F0"
BORDER = "#E0E0E0"
DARK   = "#1A1A1A"
MUTED  = "#666666"


class EditWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error    = pyqtSignal(str)

    def __init__(self, mode, kwargs):
        super().__init__()
        self.mode   = mode
        self.kwargs = kwargs

    def run(self):
        try:
            if self.mode == "watermark":
                result = add_watermark_text(**self.kwargs,
                                            progress_cb=self.progress.emit)
            elif self.mode == "text":
                result = add_text_overlay(**self.kwargs,
                                          progress_cb=self.progress.emit)
            elif self.mode == "blank":
                result = insert_blank_pages(**self.kwargs,
                                            progress_cb=self.progress.emit)
            else:
                raise ValueError(f"Modo desconocido: {self.mode}")
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class EditPanel(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(BG))
        self.setPalette(pal)
        self._pdf_path = ""
        self._page_count = 0
        self._worker: EditWorker | None = None
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
        body_lay.addWidget(self._make_left_col(), stretch=5)
        body_lay.addWidget(self._make_right_col(), stretch=5)
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
        t = QLabel("Editar PDF")
        t.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {DARK}; background: transparent;")
        lay.addWidget(t)
        s = QLabel("Agrega texto, marcas de agua o paginas en blanco a tu PDF")
        s.setFont(QFont("Segoe UI", 9))
        s.setStyleSheet(f"color: {MUTED}; background: transparent;")
        lay.addWidget(s)
        return h

    # ── Columna izquierda: carga del archivo ──────────────────────────────────
    def _make_left_col(self) -> QWidget:
        col = QWidget()
        col.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(col)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        drop = DropZone(
            accepted_extensions=["pdf"],
            message="Arrastra el PDF a editar aqui",
            sub_message="Solo archivos .pdf",
        )
        drop.files_dropped.connect(self._on_pdf_dropped)
        lay.addWidget(drop, stretch=1)

        self._info_card = self._make_info_card()
        lay.addWidget(self._info_card)

        # Selector de tipo de edicion
        mode_lbl = QLabel("Tipo de edicion:")
        mode_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        mode_lbl.setStyleSheet(f"color: {DARK}; background: transparent;")
        lay.addWidget(mode_lbl)

        self._mode_grp = QButtonGroup(self)
        mode_row = QHBoxLayout()
        mode_row.setSpacing(8)
        for val, lbl in [("watermark", "Marca de agua"),
                         ("text",      "Agregar texto"),
                         ("blank",     "Pag. en blanco")]:
            rb = QRadioButton(lbl)
            rb.setFont(QFont("Segoe UI", 9))
            rb.setChecked(val == "watermark")
            rb.setStyleSheet(f"""
                QRadioButton {{ color: {DARK}; background: transparent; }}
                QRadioButton::indicator:checked {{ background: {RED}; border: 2px solid {RED}; border-radius: 6px; }}
            """)
            rb.toggled.connect(lambda checked, v=val: checked and self._switch_mode(v))
            self._mode_grp.addButton(rb)
            mode_row.addWidget(rb)
        lay.addLayout(mode_row)

        # Archivo de salida
        out_lbl = QLabel("Archivo de salida:")
        out_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        out_lbl.setStyleSheet(f"color: {DARK}; background: transparent;")
        lay.addWidget(out_lbl)

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

        return col

    def _make_info_card(self) -> QWidget:
        card = QWidget()
        card.setAutoFillBackground(True)
        cp = card.palette()
        cp.setColor(QPalette.ColorRole.Window, QColor(WHITE))
        card.setPalette(cp)
        card.setStyleSheet(f"border: 1px solid {BORDER}; border-radius: 8px;")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(3)

        self._info_name = QLabel("Ningun archivo cargado")
        self._info_name.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._info_name.setStyleSheet(f"color: {DARK}; background: transparent; border: none;")
        lay.addWidget(self._info_name)

        self._info_detail = QLabel("")
        self._info_detail.setFont(QFont("Segoe UI", 8))
        self._info_detail.setStyleSheet(f"color: {MUTED}; background: transparent; border: none;")
        lay.addWidget(self._info_detail)

        return card

    # ── Columna derecha: opciones por modo ────────────────────────────────────
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
        lay.setSpacing(12)

        t = QLabel("Opciones de edicion")
        t.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {DARK}; background: transparent; border: none;")
        lay.addWidget(t)
        lay.addWidget(self._divider())

        # Stack de opciones por modo
        self._opt_stack = QStackedWidget()
        self._opt_stack.addWidget(self._make_watermark_opts())  # idx 0
        self._opt_stack.addWidget(self._make_text_opts())        # idx 1
        self._opt_stack.addWidget(self._make_blank_opts())       # idx 2
        lay.addWidget(self._opt_stack)

        lay.addStretch()
        lay.addWidget(self._divider())

        self._apply_btn = QPushButton("  Aplicar edicion")
        self._apply_btn.setFixedHeight(42)
        self._apply_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self._apply_btn.setEnabled(False)
        self._apply_btn.setStyleSheet(self._action_btn_style())
        self._apply_btn.clicked.connect(self._start_edit)
        lay.addWidget(self._apply_btn)

        scroll.setWidget(card)
        return scroll

    def _make_watermark_opts(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        lay.addWidget(self._sec_label("Texto de la marca de agua"))
        self._wm_text = QLineEdit("CONFIDENCIAL")
        self._wm_text.setFont(QFont("Segoe UI", 9))
        self._wm_text.setFixedHeight(30)
        self._wm_text.setStyleSheet(self._input_style())
        lay.addWidget(self._wm_text)

        lay.addWidget(self._sec_label("Tamanio de fuente"))
        self._wm_size = QSpinBox()
        self._wm_size.setRange(12, 120)
        self._wm_size.setValue(48)
        self._wm_size.setFixedHeight(30)
        self._wm_size.setFont(QFont("Segoe UI", 9))
        self._wm_size.setStyleSheet(self._input_style())
        lay.addWidget(self._wm_size)

        lay.addWidget(self._sec_label("Opacidad"))
        op_row = QHBoxLayout()
        self._wm_opacity_lbl = QLabel("25%")
        self._wm_opacity_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self._wm_opacity_lbl.setStyleSheet(f"color: {RED}; background: transparent; border: none;")
        self._wm_opacity = QSlider(Qt.Orientation.Horizontal)
        self._wm_opacity.setRange(5, 80)
        self._wm_opacity.setValue(25)
        self._wm_opacity.setStyleSheet(self._slider_style())
        self._wm_opacity.valueChanged.connect(lambda v: self._wm_opacity_lbl.setText(f"{v}%"))
        op_row.addWidget(self._wm_opacity)
        op_row.addWidget(self._wm_opacity_lbl)
        lay.addLayout(op_row)

        lay.addWidget(self._sec_label("Angulo"))
        self._wm_angle = QSpinBox()
        self._wm_angle.setRange(0, 90)
        self._wm_angle.setValue(45)
        self._wm_angle.setSuffix("°")
        self._wm_angle.setFixedHeight(30)
        self._wm_angle.setFont(QFont("Segoe UI", 9))
        self._wm_angle.setStyleSheet(self._input_style())
        lay.addWidget(self._wm_angle)

        lay.addStretch()
        return w

    def _make_text_opts(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        lay.addWidget(self._sec_label("Texto a agregar"))
        self._txt_text = QTextEdit()
        self._txt_text.setPlaceholderText("Escribe el texto aqui...")
        self._txt_text.setFont(QFont("Segoe UI", 9))
        self._txt_text.setFixedHeight(70)
        self._txt_text.setStyleSheet(f"QTextEdit {{ border: 1px solid {BORDER}; border-radius: 5px; padding: 4px; background: white; color: {DARK}; }}")
        lay.addWidget(self._txt_text)

        lay.addWidget(self._sec_label("Tamanio de fuente"))
        self._txt_size = QSpinBox()
        self._txt_size.setRange(6, 72)
        self._txt_size.setValue(12)
        self._txt_size.setFixedHeight(30)
        self._txt_size.setStyleSheet(self._input_style())
        lay.addWidget(self._txt_size)

        pos_row = QHBoxLayout()
        pos_row.setSpacing(8)
        x_col = QVBoxLayout()
        x_col.addWidget(self._sec_label("X (pt)"))
        self._txt_x = QSpinBox()
        self._txt_x.setRange(0, 800)
        self._txt_x.setValue(50)
        self._txt_x.setFixedHeight(28)
        self._txt_x.setStyleSheet(self._input_style())
        x_col.addWidget(self._txt_x)
        pos_row.addLayout(x_col)

        y_col = QVBoxLayout()
        y_col.addWidget(self._sec_label("Y (pt)"))
        self._txt_y = QSpinBox()
        self._txt_y.setRange(0, 1200)
        self._txt_y.setValue(50)
        self._txt_y.setFixedHeight(28)
        self._txt_y.setStyleSheet(self._input_style())
        y_col.addWidget(self._txt_y)
        pos_row.addLayout(y_col)
        lay.addLayout(pos_row)

        lay.addStretch()
        return w

    def _make_blank_opts(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        lay.addWidget(self._sec_label("Insertar en la posicion (0 = inicio)"))
        self._blank_pos = QSpinBox()
        self._blank_pos.setRange(0, 9999)
        self._blank_pos.setValue(0)
        self._blank_pos.setFixedHeight(30)
        self._blank_pos.setFont(QFont("Segoe UI", 9))
        self._blank_pos.setStyleSheet(self._input_style())
        lay.addWidget(self._blank_pos)

        lay.addWidget(self._sec_label("Tamanio de la pagina"))
        self._blank_size = QComboBox()
        self._blank_size.addItems(["A4", "Letter", "Legal", "A3", "A5"])
        self._blank_size.setFixedHeight(30)
        self._blank_size.setFont(QFont("Segoe UI", 9))
        self._blank_size.setStyleSheet(f"""
            QComboBox {{ border: 1px solid {BORDER}; border-radius: 5px;
                padding: 3px 8px; background: white; color: {DARK}; }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
        """)
        lay.addWidget(self._blank_size)

        note = QLabel("Se insertara 1 pagina en blanco en la\nposicion indicada (antes de esa pagina).")
        note.setFont(QFont("Segoe UI", 8))
        note.setWordWrap(True)
        note.setStyleSheet(f"color: {MUTED}; background: transparent; border: none;")
        lay.addWidget(note)

        lay.addStretch()
        return w

    # ── Barra de estado ───────────────────────────────────────────────────────
    def _make_status_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(42)
        bar.setAutoFillBackground(True)
        p = bar.palette()
        p.setColor(QPalette.ColorRole.Window, QColor(WHITE))
        bar.setPalette(p)
        bar.setStyleSheet(f"border-top: 1px solid {BORDER};")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(16, 6, 16, 6)

        self._status_lbl = QLabel("Carga un PDF para comenzar.")
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

    # ── Slots ──────────────────────────────────────────────────────────────────
    def _on_pdf_dropped(self, paths: list[str]) -> None:
        pdf = next((p for p in paths if p.lower().endswith(".pdf")), None)
        if pdf:
            self.load_file(pdf)

    def load_file(self, path: str) -> None:
        self._pdf_path = path
        try:
            info = get_pdf_info(path)
            self._page_count = info["pages"]
            self._info_name.setText(os.path.basename(path))
            self._info_detail.setText(f"{info['pages']} paginas  |  {info['file_size_mb']} MB")
            self._blank_pos.setMaximum(self._page_count)
            self._blank_pos.setValue(self._page_count)
        except Exception:
            self._info_name.setText(os.path.basename(path))
        self._output_edit.setText(suggest_output_name(path))
        self._apply_btn.setEnabled(True)
        self._status_lbl.setText(f"PDF cargado: {os.path.basename(path)}")

    def _switch_mode(self, mode: str) -> None:
        idx = {"watermark": 0, "text": 1, "blank": 2}.get(mode, 0)
        self._opt_stack.setCurrentIndex(idx)
        suffix = {"watermark": "con_marca", "text": "con_texto", "blank": "con_pag"}.get(mode, "editado")
        if self._pdf_path:
            self._output_edit.setText(suggest_output_name(self._pdf_path, suffix))

    def _browse_output(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF editado como",
            self._output_edit.text(), "Archivos PDF (*.pdf)"
        )
        if path:
            if not path.lower().endswith(".pdf"):
                path += ".pdf"
            self._output_edit.setText(path)

    def _get_current_mode(self) -> str:
        for btn in self._mode_grp.buttons():
            if btn.isChecked():
                text = btn.text()
                if "agua" in text:   return "watermark"
                if "texto" in text:  return "text"
                if "blanco" in text: return "blank"
        return "watermark"

    def _start_edit(self) -> None:
        if not self._pdf_path:
            return
        output = self._output_edit.text().strip()
        if not output:
            return
        mode = self._get_current_mode()

        if mode == "watermark":
            kwargs = {
                "pdf_path":   self._pdf_path,
                "output_path": output,
                "text":       self._wm_text.text() or "MARCA DE AGUA",
                "font_size":  self._wm_size.value(),
                "opacity":    self._wm_opacity.value() / 100.0,
                "angle":      float(self._wm_angle.value()),
            }
        elif mode == "text":
            kwargs = {
                "pdf_path":   self._pdf_path,
                "output_path": output,
                "text":       self._txt_text.toPlainText() or "Texto",
                "x_pt":       float(self._txt_x.value()),
                "y_pt":       float(self._txt_y.value()),
                "font_size":  self._txt_size.value(),
            }
        elif mode == "blank":
            kwargs = {
                "pdf_path":   self._pdf_path,
                "output_path": output,
                "positions":  [self._blank_pos.value()],
                "page_size":  self._blank_size.currentText(),
            }
        else:
            return

        self._apply_btn.setEnabled(False)
        self._progress.show()
        self._progress.setValue(0)
        self._status_lbl.setText("Aplicando edicion...")

        self._worker = EditWorker(mode=mode, kwargs=kwargs)
        self._worker.progress.connect(self._progress.setValue)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_finished(self, path: str) -> None:
        self._progress.setValue(100)
        self._apply_btn.setEnabled(True)
        self._status_lbl.setText(f"Listo: {os.path.basename(path)}")
        QMessageBox.information(self, "Edicion completada",
                                f"PDF guardado correctamente:\n{path}")

    def _on_error(self, msg: str) -> None:
        self._progress.hide()
        self._apply_btn.setEnabled(True)
        self._status_lbl.setText("Error en la edicion.")
        QMessageBox.critical(self, "Error", msg)

    # ── Helpers ────────────────────────────────────────────────────────────────
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

    def _input_style(self) -> str:
        return f"QLineEdit, QSpinBox {{ border: 1px solid {BORDER}; border-radius: 5px; padding: 4px 8px; background: white; color: {DARK}; }}"

    def _small_btn_style(self) -> str:
        return f"QPushButton {{ background: #F0F0F0; border: 1px solid {BORDER}; border-radius: 5px; color: {DARK}; }} QPushButton:hover {{ background: #E0E0E0; }}"

    def _slider_style(self) -> str:
        return f"""
            QSlider::groove:horizontal {{ height: 4px; background: #E0E0E0; border-radius: 2px; }}
            QSlider::handle:horizontal {{ background: {RED}; border-radius: 7px; width: 14px; height: 14px; margin: -5px 0; }}
            QSlider::sub-page:horizontal {{ background: {RED}; border-radius: 2px; }}
        """

    def _action_btn_style(self) -> str:
        return f"""
            QPushButton {{ background-color: {RED}; color: white; border: none; border-radius: 8px; font-size: 11pt; font-weight: bold; }}
            QPushButton:hover {{ background-color: #B82020; }}
            QPushButton:disabled {{ background-color: #CCCCCC; color: #999999; }}
        """
