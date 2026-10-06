"""
ui/panels/reorder_panel.py
Panel para reordenar, rotar y eliminar paginas de un PDF.
Muestra miniaturas de cada pagina con controles individuales.
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QLineEdit, QFileDialog,
    QProgressBar, QMessageBox, QSizePolicy, QGridLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QByteArray
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap

from ui.components.drop_zone import DropZone
from tools.reorder_pdf import (
    get_page_thumbnails, reorder_and_save,
    get_page_count, suggest_output_name
)


RED    = "#D62828"
WHITE  = "#FFFFFF"
BG     = "#F0F0F0"
BORDER = "#E0E0E0"
DARK   = "#1A1A1A"
MUTED  = "#666666"
CARD   = "#FAFAFA"


# ── Worker: carga miniaturas en background ─────────────────────────────────────
class ThumbnailWorker(QThread):
    done    = pyqtSignal(list)   # list[bytes] PNG
    error   = pyqtSignal(str)

    def __init__(self, pdf_path: str):
        super().__init__()
        self.pdf_path = pdf_path

    def run(self):
        try:
            thumbs = get_page_thumbnails(self.pdf_path, thumb_width=100)
            self.done.emit(thumbs)
        except Exception as e:
            self.error.emit(str(e))


class SaveWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error    = pyqtSignal(str)

    def __init__(self, pdf_path, output_path, page_order, rotations):
        super().__init__()
        self.pdf_path    = pdf_path
        self.output_path = output_path
        self.page_order  = page_order
        self.rotations   = rotations

    def run(self):
        try:
            result = reorder_and_save(
                self.pdf_path, self.output_path,
                self.page_order, self.rotations,
                progress_cb=self.progress.emit,
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


# ── Tarjeta de miniatura por pagina ──────────────────────────────────────────
class PageCard(QWidget):
    """Miniatura de pagina con controles: subir, bajar, rotar, eliminar."""
    move_up_requested   = pyqtSignal(int)   # posicion actual
    move_down_requested = pyqtSignal(int)
    rotate_requested    = pyqtSignal(int, int)   # posicion, grados (+90 o -90)
    delete_requested    = pyqtSignal(int)

    def __init__(self, position: int, orig_page: int, png_bytes: bytes,
                 rotation: int = 0, parent=None):
        super().__init__(parent)
        self.position  = position
        self.orig_page = orig_page
        self.rotation  = rotation
        self.setFixedWidth(130)
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(WHITE))
        self.setPalette(pal)
        self.setStyleSheet(f"""
            PageCard {{
                background-color: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
        """)
        self._png_bytes = png_bytes
        self._build_ui()

    def _build_ui(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(4)

        # Miniatura
        self._img_lbl = QLabel()
        self._img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._img_lbl.setFixedHeight(130)
        self._img_lbl.setStyleSheet("background: #F5F5F5; border-radius: 4px; border: none;")
        self._refresh_pixmap()
        lay.addWidget(self._img_lbl)

        # Numero de pagina
        num = QLabel(f"Pag. {self.orig_page + 1}")
        num.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        num.setStyleSheet(f"color: {DARK}; background: transparent; border: none;")
        lay.addWidget(num)

        # Rotacion actual
        self._rot_lbl = QLabel(f"{self.rotation}°")
        self._rot_lbl.setFont(QFont("Segoe UI", 7))
        self._rot_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._rot_lbl.setStyleSheet(f"color: {MUTED}; background: transparent; border: none;")
        lay.addWidget(self._rot_lbl)

        # Botones fila 1: subir / bajar
        row1 = QHBoxLayout()
        row1.setSpacing(3)
        row1.addWidget(self._icon_btn("↑", self._on_up))
        row1.addWidget(self._icon_btn("↓", self._on_down))
        lay.addLayout(row1)

        # Botones fila 2: rotar izq / rotar der / eliminar
        row2 = QHBoxLayout()
        row2.setSpacing(3)
        row2.addWidget(self._icon_btn("↺", self._on_rot_left))
        row2.addWidget(self._icon_btn("↻", self._on_rot_right))
        row2.addWidget(self._icon_btn("✕", self._on_delete, danger=True))
        lay.addLayout(row2)

    def _icon_btn(self, label: str, slot, danger: bool = False) -> QPushButton:
        btn = QPushButton(label)
        btn.setFixedHeight(22)
        btn.setFont(QFont("Segoe UI", 9))
        if danger:
            btn.setStyleSheet(f"""
                QPushButton {{ background: transparent; color: {RED};
                    border: 1px solid {RED}; border-radius: 4px; }}
                QPushButton:hover {{ background: #FEF2F2; }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{ background: #F0F0F0; color: {DARK};
                    border: 1px solid {BORDER}; border-radius: 4px; }}
                QPushButton:hover {{ background: #E0E0E0; }}
            """)
        btn.clicked.connect(slot)
        return btn

    def _refresh_pixmap(self) -> None:
        ba = QByteArray(self._png_bytes)
        pix = QPixmap()
        pix.loadFromData(ba, "PNG")
        # Aplicar rotacion visual
        if self.rotation:
            from PyQt6.QtGui import QTransform
            t = QTransform().rotate(self.rotation)
            pix = pix.transformed(t, Qt.TransformationMode.SmoothTransformation)
        pix = pix.scaled(100, 126,
                         Qt.AspectRatioMode.KeepAspectRatio,
                         Qt.TransformationMode.SmoothTransformation)
        self._img_lbl.setPixmap(pix)

    def update_rotation(self, rotation: int) -> None:
        self.rotation = rotation % 360
        self._rot_lbl.setText(f"{self.rotation}°")
        self._refresh_pixmap()

    # ── Slots ──────────────────────────────────────────────────────────────────
    def _on_up(self):         self.move_up_requested.emit(self.position)
    def _on_down(self):       self.move_down_requested.emit(self.position)
    def _on_rot_left(self):   self.rotate_requested.emit(self.position, -90)
    def _on_rot_right(self):  self.rotate_requested.emit(self.position, 90)
    def _on_delete(self):     self.delete_requested.emit(self.position)


# ── Panel principal ───────────────────────────────────────────────────────────
class ReorderPanel(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(BG))
        self.setPalette(pal)
        self._pdf_path  = ""
        self._png_data: list[bytes] = []
        self._order:    list[int]   = []    # indices originales en orden actual
        self._rotations: dict[int, int] = {}  # {orig_idx: grados}
        self._cards: list[PageCard] = []
        self._thumb_worker: ThumbnailWorker | None = None
        self._save_worker:  SaveWorker | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_header())

        # ── Zona drop + miniaturas ─────────────────────────────────────────────
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(16, 12, 16, 8)
        body_lay.setSpacing(10)

        # Drop zone (compacta, solo cuando no hay PDF)
        self._drop = DropZone(
            accepted_extensions=["pdf"],
            message="Arrastra un PDF aqui para ver sus paginas",
            sub_message="Solo archivos .pdf",
        )
        self._drop.setFixedHeight(120)
        self._drop.files_dropped.connect(self._on_pdf_dropped)
        body_lay.addWidget(self._drop)

        # Barra de herramientas (visible tras cargar PDF)
        self._toolbar = self._make_toolbar()
        self._toolbar.hide()
        body_lay.addWidget(self._toolbar)

        # Area de miniaturas scrolleable
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setStyleSheet("background: transparent; border: none;")

        self._thumb_area = QWidget()
        self._thumb_area.setStyleSheet("background: transparent;")
        self._thumb_lay = QHBoxLayout(self._thumb_area)
        self._thumb_lay.setContentsMargins(0, 0, 0, 0)
        self._thumb_lay.setSpacing(10)
        self._thumb_lay.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self._scroll.setWidget(self._thumb_area)
        body_lay.addWidget(self._scroll)

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
        t = QLabel("Reordenar PDF")
        t.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {DARK}; background: transparent;")
        lay.addWidget(t)
        s = QLabel("Mueve, rota o elimina paginas. Usa las flechas en cada miniatura.")
        s.setFont(QFont("Segoe UI", 9))
        s.setStyleSheet(f"color: {MUTED}; background: transparent;")
        lay.addWidget(s)
        return h

    def _make_toolbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(46)
        bar.setAutoFillBackground(True)
        p = bar.palette()
        p.setColor(QPalette.ColorRole.Window, QColor(WHITE))
        bar.setPalette(p)
        bar.setStyleSheet(f"border: 1px solid {BORDER}; border-radius: 8px;")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(12, 6, 12, 6)
        lay.setSpacing(10)

        self._file_lbl = QLabel("Ningun archivo cargado")
        self._file_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self._file_lbl.setStyleSheet(f"color: {DARK}; background: transparent;")
        lay.addWidget(self._file_lbl)

        self._pages_lbl = QLabel("")
        self._pages_lbl.setFont(QFont("Segoe UI", 9))
        self._pages_lbl.setStyleSheet(f"color: {MUTED}; background: transparent;")
        lay.addWidget(self._pages_lbl)

        lay.addStretch()

        out_lbl = QLabel("Guardar como:")
        out_lbl.setFont(QFont("Segoe UI", 9))
        out_lbl.setStyleSheet(f"color: {MUTED}; background: transparent;")
        lay.addWidget(out_lbl)

        self._output_edit = QLineEdit()
        self._output_edit.setFixedWidth(220)
        self._output_edit.setFixedHeight(28)
        self._output_edit.setFont(QFont("Segoe UI", 9))
        self._output_edit.setStyleSheet(f"""
            QLineEdit {{ border: 1px solid {BORDER}; border-radius: 5px;
                padding: 2px 6px; background: white; color: {DARK}; }}
        """)
        lay.addWidget(self._output_edit)

        browse = QPushButton("...")
        browse.setFixedSize(28, 28)
        browse.setStyleSheet(f"""
            QPushButton {{ background: #F0F0F0; border: 1px solid {BORDER};
                border-radius: 5px; color: {DARK}; }}
            QPushButton:hover {{ background: #E0E0E0; }}
        """)
        browse.clicked.connect(self._browse_output)
        lay.addWidget(browse)

        self._save_btn = QPushButton("  Guardar PDF")
        self._save_btn.setFixedHeight(32)
        self._save_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._save_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {RED}; color: white; border: none;
                border-radius: 6px; padding: 0 16px; }}
            QPushButton:hover {{ background-color: #B82020; }}
            QPushButton:disabled {{ background-color: #CCCCCC; color: #999; }}
        """)
        self._save_btn.clicked.connect(self._start_save)
        lay.addWidget(self._save_btn)

        return bar

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

        self._status_lbl = QLabel("Carga un PDF para ver sus paginas.")
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

    # ── Logica ─────────────────────────────────────────────────────────────────
    def _on_pdf_dropped(self, paths: list[str]) -> None:
        pdf = next((p for p in paths if p.lower().endswith(".pdf")), None)
        if pdf:
            self.load_file(pdf)

    def load_file(self, path: str) -> None:
        self._pdf_path = path
        self._order = []
        self._rotations = {}
        self._cards = []
        self._png_data = []
        self._clear_thumbnails()
        self._status_lbl.setText("Cargando miniaturas...")
        self._progress.show()
        self._progress.setRange(0, 0)   # modo indeterminado

        self._thumb_worker = ThumbnailWorker(path)
        self._thumb_worker.done.connect(self._on_thumbs_loaded)
        self._thumb_worker.error.connect(self._on_error)
        self._thumb_worker.start()

    def _on_thumbs_loaded(self, thumbs: list[bytes]) -> None:
        self._progress.hide()
        self._progress.setRange(0, 100)
        self._png_data = thumbs
        self._order = list(range(len(thumbs)))
        self._rotations = {i: 0 for i in self._order}
        self._rebuild_ui()

        self._file_lbl.setText(os.path.basename(self._pdf_path))
        self._pages_lbl.setText(f"({len(thumbs)} paginas)")
        self._output_edit.setText(suggest_output_name(self._pdf_path))
        self._toolbar.show()
        self._status_lbl.setText(
            f"{len(thumbs)} paginas cargadas. Usa los controles para reordenar."
        )

    def _rebuild_ui(self) -> None:
        """Reconstruye las tarjetas de miniatura segun el orden actual."""
        self._clear_thumbnails()
        self._cards = []
        for pos, orig_idx in enumerate(self._order):
            card = PageCard(
                position=pos,
                orig_page=orig_idx,
                png_bytes=self._png_data[orig_idx],
                rotation=self._rotations.get(orig_idx, 0),
            )
            card.move_up_requested.connect(self._move_up)
            card.move_down_requested.connect(self._move_down)
            card.rotate_requested.connect(self._rotate_page)
            card.delete_requested.connect(self._delete_page)
            self._thumb_lay.addWidget(card)
            self._cards.append(card)

    def _clear_thumbnails(self) -> None:
        while self._thumb_lay.count():
            item = self._thumb_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _move_up(self, pos: int) -> None:
        if pos > 0:
            self._order[pos], self._order[pos - 1] = self._order[pos - 1], self._order[pos]
            self._rebuild_ui()

    def _move_down(self, pos: int) -> None:
        if pos < len(self._order) - 1:
            self._order[pos], self._order[pos + 1] = self._order[pos + 1], self._order[pos]
            self._rebuild_ui()

    def _rotate_page(self, pos: int, degrees: int) -> None:
        orig_idx = self._order[pos]
        self._rotations[orig_idx] = (self._rotations.get(orig_idx, 0) + degrees) % 360
        self._cards[pos].update_rotation(self._rotations[orig_idx])

    def _delete_page(self, pos: int) -> None:
        if len(self._order) <= 1:
            QMessageBox.warning(self, "Aviso", "No puedes eliminar la unica pagina.")
            return
        self._order.pop(pos)
        self._rebuild_ui()
        self._pages_lbl.setText(f"({len(self._order)} paginas)")
        self._status_lbl.setText(f"Pagina eliminada. Quedan {len(self._order)} paginas.")

    def _browse_output(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF reordenado como",
            self._output_edit.text(), "Archivos PDF (*.pdf)"
        )
        if path:
            if not path.lower().endswith(".pdf"):
                path += ".pdf"
            self._output_edit.setText(path)

    def _start_save(self) -> None:
        if not self._pdf_path or not self._order:
            return
        output = self._output_edit.text().strip()
        if not output:
            return

        self._save_btn.setEnabled(False)
        self._progress.show()
        self._progress.setValue(0)
        self._status_lbl.setText("Guardando PDF reordenado...")

        self._save_worker = SaveWorker(
            self._pdf_path, output, list(self._order), dict(self._rotations)
        )
        self._save_worker.progress.connect(self._progress.setValue)
        self._save_worker.finished.connect(self._on_saved)
        self._save_worker.error.connect(self._on_error)
        self._save_worker.start()

    def _on_saved(self, path: str) -> None:
        self._progress.setValue(100)
        self._save_btn.setEnabled(True)
        self._status_lbl.setText(f"Guardado: {os.path.basename(path)}")
        QMessageBox.information(self, "Listo", f"PDF guardado:\n{path}")

    def _on_error(self, msg: str) -> None:
        self._progress.hide()
        self._progress.setRange(0, 100)
        self._save_btn.setEnabled(True)
        self._status_lbl.setText("Error.")
        QMessageBox.critical(self, "Error", msg)
