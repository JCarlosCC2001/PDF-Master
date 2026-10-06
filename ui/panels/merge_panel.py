"""
ui/panels/merge_panel.py
Panel para unir multiples PDFs en uno solo.
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QFrame, QProgressBar,
    QMessageBox, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

from ui.components.drop_zone import DropZone
from ui.components.file_list import FileListWidget
from tools.merge_pdf import merge_pdfs, suggest_output_name, get_pdf_page_count


RED    = "#D62828"
WHITE  = "#FFFFFF"
BG     = "#F0F0F0"
BORDER = "#E0E0E0"
DARK   = "#1A1A1A"
MUTED  = "#666666"


class MergeWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error    = pyqtSignal(str)

    def __init__(self, pdf_paths, output_path):
        super().__init__()
        self.pdf_paths   = pdf_paths
        self.output_path = output_path

    def run(self):
        try:
            result = merge_pdfs(
                pdf_paths=self.pdf_paths,
                output_path=self.output_path,
                progress_cb=self.progress.emit,
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MergePanel(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(BG))
        self.setPalette(pal)
        self._worker: MergeWorker | None = None
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
        t = QLabel("Unir PDF")
        t.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {DARK}; background: transparent;")
        lay.addWidget(t)
        s = QLabel("Combina multiples archivos PDF en uno. Arrastra para reordenar.")
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

        drop = DropZone(
            accepted_extensions=["pdf"],
            message="Arrastra archivos PDF aqui",
            sub_message="Puedes arrastrar varios a la vez",
        )
        drop.files_dropped.connect(self._on_files_dropped)
        lay.addWidget(drop, stretch=1)

        lbl = QLabel("Archivos PDF (el orden aqui es el orden del resultado):")
        lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {DARK}; background: transparent;")
        lay.addWidget(lbl)

        self._file_list = FileListWidget(file_type_label="PDF")
        self._file_list.files_changed.connect(self._on_files_changed)
        self._file_list.setSizePolicy(QSizePolicy.Policy.Expanding,
                                      QSizePolicy.Policy.Expanding)
        lay.addWidget(self._file_list, stretch=2)

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

        t = QLabel("Opciones de fusion")
        t.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {DARK}; background: transparent; border: none;")
        lay.addWidget(t)
        lay.addWidget(self._divider())

        # Resumen
        self._summary_lbl = QLabel("Carga al menos 2 PDFs para comenzar.")
        self._summary_lbl.setFont(QFont("Segoe UI", 9))
        self._summary_lbl.setWordWrap(True)
        self._summary_lbl.setStyleSheet(f"""
            QLabel {{
                color: {MUTED};
                background-color: #F8F8F8;
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 10px;
            }}
        """)
        lay.addWidget(self._summary_lbl)

        # Nombre de salida
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

        self._merge_btn = QPushButton("  Unir PDFs")
        self._merge_btn.setFixedHeight(42)
        self._merge_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self._merge_btn.setEnabled(False)
        self._merge_btn.setStyleSheet(self._action_btn_style())
        self._merge_btn.clicked.connect(self._start_merge)
        lay.addWidget(self._merge_btn)

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

        self._status_lbl = QLabel("Listo. Carga 2 o mas PDFs para comenzar.")
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
    def _on_files_dropped(self, paths: list[str]) -> None:
        pdf_paths = [p for p in paths if p.lower().endswith(".pdf")]
        self._file_list.add_files(pdf_paths)

    def _on_files_changed(self, paths: list[str]) -> None:
        n = len(paths)
        ready = n >= 2
        self._merge_btn.setEnabled(ready)

        if ready:
            total_pages = sum(get_pdf_page_count(p) for p in paths)
            self._summary_lbl.setText(
                f"{n} archivos PDF\n"
                f"Total aprox: {total_pages} paginas\n"
                f"Orden final: segun la lista de la izquierda."
            )
            if not self._output_edit.text():
                self._output_edit.setText(suggest_output_name(paths[0]))
        else:
            self._summary_lbl.setText("Carga al menos 2 PDFs para comenzar.")

    def _browse_output(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF unido como", self._output_edit.text(),
            "Archivos PDF (*.pdf)"
        )
        if path:
            if not path.lower().endswith(".pdf"):
                path += ".pdf"
            self._output_edit.setText(path)

    def _start_merge(self) -> None:
        files = self._file_list.get_files()
        if len(files) < 2:
            return
        output = self._output_edit.text().strip()
        if not output:
            output = suggest_output_name(files[0])
            self._output_edit.setText(output)

        self._merge_btn.setEnabled(False)
        self._progress.show()
        self._progress.setValue(0)
        self._status_lbl.setText("Uniendo PDFs...")

        self._worker = MergeWorker(pdf_paths=files, output_path=output)
        self._worker.progress.connect(self._progress.setValue)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_finished(self, output_path: str) -> None:
        self._progress.setValue(100)
        self._merge_btn.setEnabled(True)
        self._status_lbl.setText(f"Listo: {os.path.basename(output_path)}")
        QMessageBox.information(
            self, "Union completada",
            f"PDF unido generado correctamente:\n{output_path}",
        )

    def _on_error(self, msg: str) -> None:
        self._merge_btn.setEnabled(True)
        self._progress.hide()
        self._status_lbl.setText("Error al unir los PDFs.")
        QMessageBox.critical(self, "Error", f"No se pudo unir:\n{msg}")

    def load_file(self, path: str) -> None:
        if path.lower().endswith(".pdf"):
            self._file_list.add_files([path])

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
