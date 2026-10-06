"""
ui/panels/repair_panel.py
Panel para reparar PDFs danados o protegidos.
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QFrame, QProgressBar,
    QMessageBox, QTextEdit, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

from ui.components.drop_zone import DropZone
from tools.repair_pdf import repair_pdf, suggest_output_name


RED    = "#D62828"
WHITE  = "#FFFFFF"
BG     = "#F0F0F0"
BORDER = "#E0E0E0"
DARK   = "#1A1A1A"
MUTED  = "#666666"
GREEN  = "#16A34A"


class RepairWorker(QThread):
    finished = pyqtSignal(dict)
    error    = pyqtSignal(str)

    def __init__(self, pdf_path, output_path, password):
        super().__init__()
        self.pdf_path    = pdf_path
        self.output_path = output_path
        self.password    = password

    def run(self):
        try:
            result = repair_pdf(self.pdf_path, self.output_path, self.password)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class RepairPanel(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(BG))
        self.setPalette(pal)
        self._pdf_path = ""
        self._worker: RepairWorker | None = None
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
        t = QLabel("Reparar PDF")
        t.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {DARK}; background: transparent;")
        lay.addWidget(t)
        s = QLabel("Intenta recuperar PDFs danados, corruptos o con problemas de apertura")
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
            message="Arrastra el PDF a reparar aqui",
            sub_message="Solo archivos .pdf",
        )
        drop.files_dropped.connect(self._on_pdf_dropped)
        lay.addWidget(drop, stretch=1)

        # Info del archivo cargado
        self._info_card = QWidget()
        self._info_card.setAutoFillBackground(True)
        ip = self._info_card.palette()
        ip.setColor(QPalette.ColorRole.Window, QColor(WHITE))
        self._info_card.setPalette(ip)
        self._info_card.setStyleSheet(f"border: 1px solid {BORDER}; border-radius: 8px;")
        info_lay = QVBoxLayout(self._info_card)
        info_lay.setContentsMargins(14, 10, 14, 10)
        info_lay.setSpacing(4)

        self._info_name = QLabel("Ningun archivo cargado")
        self._info_name.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._info_name.setStyleSheet(f"color: {DARK}; background: transparent; border: none;")
        info_lay.addWidget(self._info_name)

        self._info_size = QLabel("")
        self._info_size.setFont(QFont("Segoe UI", 8))
        self._info_size.setStyleSheet(f"color: {MUTED}; background: transparent; border: none;")
        info_lay.addWidget(self._info_size)

        lay.addWidget(self._info_card)

        # Informe de resultado
        report_lbl = QLabel("Informe de reparacion:")
        report_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        report_lbl.setStyleSheet(f"color: {DARK}; background: transparent;")
        lay.addWidget(report_lbl)

        self._report_box = QTextEdit()
        self._report_box.setReadOnly(True)
        self._report_box.setFont(QFont("Segoe UI", 9))
        self._report_box.setPlaceholderText(
            "El informe de reparacion aparecera aqui despues de procesar el PDF..."
        )
        self._report_box.setStyleSheet(f"""
            QTextEdit {{
                background-color: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 8px;
                color: {DARK};
            }}
        """)
        lay.addWidget(self._report_box, stretch=2)

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

        t = QLabel("Opciones de reparacion")
        t.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {DARK}; background: transparent; border: none;")
        lay.addWidget(t)
        lay.addWidget(self._divider())

        # Contrasena (para PDFs protegidos)
        lay.addWidget(self._sec_label("Contrasena (si esta protegido)"))
        self._pwd_edit = QLineEdit()
        self._pwd_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._pwd_edit.setPlaceholderText("Dejar en blanco si no tiene contrasena")
        self._pwd_edit.setFont(QFont("Segoe UI", 9))
        self._pwd_edit.setFixedHeight(30)
        self._pwd_edit.setStyleSheet(self._input_style())
        lay.addWidget(self._pwd_edit)

        # Archivo de salida
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

        # Nota informativa
        info_note = QLabel(
            "PDF Master intenta reparar el archivo\n"
            "usando dos metodos:\n\n"
            "1. pikepdf (muy tolerante con errores)\n"
            "2. PyMuPDF (recuperacion alternativa)\n\n"
            "El resultado no esta garantizado para\n"
            "archivos muy danados."
        )
        info_note.setFont(QFont("Segoe UI", 8))
        info_note.setWordWrap(True)
        info_note.setStyleSheet(f"""
            QLabel {{
                color: {MUTED};
                background-color: #F8F8F8;
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 10px;
            }}
        """)
        lay.addWidget(info_note)

        lay.addStretch()
        lay.addWidget(self._divider())

        self._repair_btn = QPushButton("  Reparar PDF")
        self._repair_btn.setFixedHeight(42)
        self._repair_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self._repair_btn.setEnabled(False)
        self._repair_btn.setStyleSheet(self._action_btn_style())
        self._repair_btn.clicked.connect(self._start_repair)
        lay.addWidget(self._repair_btn)

        scroll.setWidget(card)
        return scroll

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

        self._status_lbl = QLabel("Carga un PDF para reparar.")
        self._status_lbl.setFont(QFont("Segoe UI", 9))
        self._status_lbl.setStyleSheet(f"color: {MUTED}; background: transparent;")
        lay.addWidget(self._status_lbl)
        lay.addStretch()

        self._progress = QProgressBar()
        self._progress.setFixedWidth(200)
        self._progress.setFixedHeight(10)
        self._progress.setRange(0, 0)
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
        size_mb = os.path.getsize(path) / (1024 * 1024)
        self._info_name.setText(os.path.basename(path))
        self._info_size.setText(f"{size_mb:.2f} MB")
        self._output_edit.setText(suggest_output_name(path))
        self._repair_btn.setEnabled(True)
        self._report_box.clear()
        self._status_lbl.setText(f"Archivo cargado: {os.path.basename(path)}")

    def _browse_output(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF reparado como",
            self._output_edit.text(), "Archivos PDF (*.pdf)"
        )
        if path:
            if not path.lower().endswith(".pdf"):
                path += ".pdf"
            self._output_edit.setText(path)

    def _start_repair(self) -> None:
        if not self._pdf_path:
            return
        output = self._output_edit.text().strip() or suggest_output_name(self._pdf_path)
        self._output_edit.setText(output)

        self._repair_btn.setEnabled(False)
        self._progress.show()
        self._report_box.clear()
        self._status_lbl.setText("Reparando PDF...")

        self._worker = RepairWorker(
            pdf_path=self._pdf_path,
            output_path=output,
            password=self._pwd_edit.text(),
        )
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_finished(self, result: dict) -> None:
        self._progress.hide()
        self._repair_btn.setEnabled(True)

        color = GREEN if result["success"] else RED
        status = "Exito" if result["success"] else "Error"
        self._status_lbl.setText(
            f"{status}: {result['pages']} paginas | {result['file_size_repaired_mb']:.2f} MB"
            if result["success"] else f"Error: {result['message'][:60]}"
        )

        report = f"=== RESULTADO: {'EXITO' if result['success'] else 'ERROR'} ===\n\n"
        report += f"{result['message']}\n\n"
        report += "=== DETALLES ===\n"
        for issue in result.get("issues", []):
            report += f"• {issue}\n"

        self._report_box.setPlainText(report)

        if result["success"]:
            self._report_box.setStyleSheet(f"""
                QTextEdit {{ background: white; border: 2px solid {GREEN};
                    border-radius: 6px; padding: 8px; color: {DARK}; }}
            """)
        else:
            self._report_box.setStyleSheet(f"""
                QTextEdit {{ background: white; border: 2px solid {RED};
                    border-radius: 6px; padding: 8px; color: {DARK}; }}
            """)

    def _on_error(self, msg: str) -> None:
        self._progress.hide()
        self._repair_btn.setEnabled(True)
        self._status_lbl.setText("Error inesperado.")
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
        return f"QLineEdit {{ border: 1px solid {BORDER}; border-radius: 5px; padding: 4px 8px; background: white; color: {DARK}; }}"

    def _small_btn_style(self) -> str:
        return f"QPushButton {{ background: #F0F0F0; border: 1px solid {BORDER}; border-radius: 5px; color: {DARK}; }} QPushButton:hover {{ background: #E0E0E0; }}"

    def _action_btn_style(self) -> str:
        return f"""
            QPushButton {{ background-color: {RED}; color: white; border: none; border-radius: 8px; font-size: 11pt; font-weight: bold; }}
            QPushButton:hover {{ background-color: #B82020; }}
            QPushButton:disabled {{ background-color: #CCCCCC; color: #999999; }}
        """
