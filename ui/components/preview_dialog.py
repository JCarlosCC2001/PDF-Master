"""
ui/components/preview_dialog.py
Vista previa de imágenes y PDF dentro de la app — Fase 7.

- Imágenes: se muestran con QPixmap.
- PDF: cada página se renderiza con PyMuPDF bajo demanda.
- Navegación ◀ ▶ (también con flechas/RePág/AvPág), zoom +/− y "Ajustar".
"""
from __future__ import annotations

import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QImage, QPixmap, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QWidget
)

RED = "#D62828"
DARK = "#1A1A1A"

_IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp", ".gif"}


class PreviewDialog(QDialog):
    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self._path = path
        self._is_pdf = path.lower().endswith(".pdf")
        self._doc = None
        self._page = 0
        self._zoom = 1.0          # 1.0 = ajustado a la ventana
        self._fit = True
        self._source: QPixmap | None = None

        self.setWindowTitle(f"Vista previa — {os.path.basename(path)}")
        self.resize(820, 760)
        self.setStyleSheet(f"QDialog {{ background: #2A2A2A; }}")
        self._build_ui()

        if self._is_pdf:
            try:
                import pymupdf as fitz
                self._doc = fitz.open(path)
                if self._doc.needs_pass:
                    raise RuntimeError("El PDF está protegido con contraseña.")
            except Exception as exc:
                self._show_error(str(exc))
                return
        self._load_page()

    # ── UI ──────────────────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(False)
        self._scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scroll.setStyleSheet("QScrollArea { background: #2A2A2A; border: none; }")
        self._canvas = QLabel()
        self._canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._canvas.setStyleSheet("background: white;")
        self._scroll.setWidget(self._canvas)
        root.addWidget(self._scroll, 1)

        bar = QWidget()
        bar.setFixedHeight(54)
        bar.setStyleSheet("background: #1C1C1C;")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(14, 0, 14, 0)
        lay.setSpacing(8)

        self._btn_prev = self._btn("◀", self._prev)
        self._btn_next = self._btn("▶", self._next)
        self._page_lbl = QLabel("")
        self._page_lbl.setFont(QFont("Segoe UI", 10))
        self._page_lbl.setStyleSheet("color: #E8E8E8; background: transparent;")
        self._page_lbl.setMinimumWidth(110)
        self._page_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay.addWidget(self._btn_prev)
        lay.addWidget(self._page_lbl)
        lay.addWidget(self._btn_next)
        lay.addStretch()

        self._zoom_lbl = QLabel("Ajustar")
        self._zoom_lbl.setStyleSheet("color: #9A9A9A; background: transparent;")
        self._zoom_lbl.setFont(QFont("Segoe UI", 9))
        lay.addWidget(self._btn("−", lambda: self._set_zoom(self._zoom / 1.25)))
        lay.addWidget(self._zoom_lbl)
        lay.addWidget(self._btn("+", lambda: self._set_zoom(self._zoom * 1.25)))
        fit = self._btn("Ajustar", self._fit_window)
        fit.setFixedWidth(72)
        lay.addWidget(fit)
        close = self._btn("Cerrar", self.accept, primary=True)
        close.setFixedWidth(80)
        lay.addWidget(close)
        root.addWidget(bar)

        for keys, slot in (("Left", self._prev), ("PgUp", self._prev),
                           ("Right", self._next), ("PgDown", self._next),
                           ("Ctrl++", lambda: self._set_zoom(self._zoom * 1.25)),
                           ("Ctrl+-", lambda: self._set_zoom(self._zoom / 1.25)),
                           ("Ctrl+0", self._fit_window)):
            QShortcut(QKeySequence(keys), self, activated=slot)

    def _btn(self, text: str, slot, primary: bool = False) -> QPushButton:
        b = QPushButton(text)
        b.setFixedHeight(32)
        if len(text) <= 1:
            b.setFixedWidth(36)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold if primary else QFont.Weight.Normal))
        bg, hover = (RED, "#B82020") if primary else ("#2D2D2D", "#3A3A3A")
        b.setStyleSheet(f"""
            QPushButton {{ background: {bg}; color: white; border: none; border-radius: 6px; }}
            QPushButton:hover {{ background: {hover}; }}
            QPushButton:disabled {{ color: #555555; background: #262626; }}
        """)
        b.clicked.connect(slot)
        return b

    # ── Lógica ──────────────────────────────────────────────────────────────
    def _page_count(self) -> int:
        return len(self._doc) if self._doc is not None else 1

    def _load_page(self) -> None:
        try:
            if self._is_pdf:
                page = self._doc[self._page]
                pix = page.get_pixmap(matrix=__import__("pymupdf").Matrix(2, 2), alpha=False)
                img = QImage(pix.samples, pix.width, pix.height, pix.stride,
                             QImage.Format.Format_RGB888).copy()
                self._source = QPixmap.fromImage(img)
            else:
                self._source = QPixmap(self._path)
                if self._source.isNull():
                    raise RuntimeError("Formato de imagen no soportado para vista previa.")
        except Exception as exc:
            self._show_error(str(exc))
            return
        n = self._page_count()
        self._page_lbl.setText(f"Página {self._page + 1} de {n}" if self._is_pdf else "Imagen")
        self._btn_prev.setEnabled(self._page > 0)
        self._btn_next.setEnabled(self._page < n - 1)
        self._render()

    def _render(self) -> None:
        if not self._source:
            return
        if self._fit:
            area = self._scroll.viewport().size()
            scaled = self._source.scaled(
                max(50, area.width() - 24), max(50, area.height() - 24),
                Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self._zoom_lbl.setText("Ajustar")
        else:
            w = int(self._source.width() * self._zoom / 2)  # render base a 2x
            scaled = self._source.scaledToWidth(max(50, w), Qt.TransformationMode.SmoothTransformation)
            self._zoom_lbl.setText(f"{int(self._zoom * 100)}%")
        self._canvas.setPixmap(scaled)
        self._canvas.resize(scaled.size())

    def _set_zoom(self, z: float) -> None:
        if self._fit and self._source:
            # partir del zoom equivalente al ajuste actual
            z = (self._canvas.width() * 2 / self._source.width()) * (z / self._zoom)
        self._fit = False
        self._zoom = max(0.1, min(z, 6.0))
        self._render()

    def _fit_window(self) -> None:
        self._fit = True
        self._zoom = 1.0
        self._render()

    def _prev(self) -> None:
        if self._page > 0:
            self._page -= 1
            self._load_page()

    def _next(self) -> None:
        if self._page < self._page_count() - 1:
            self._page += 1
            self._load_page()

    def _show_error(self, msg: str) -> None:
        self._canvas.setStyleSheet("background: transparent; color: #E8E8E8;")
        self._canvas.setText(f"No se puede mostrar la vista previa:\n{msg}")
        self._canvas.resize(500, 120)
        self._btn_prev.setEnabled(False)
        self._btn_next.setEnabled(False)

    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        if self._fit:
            self._render()

    def closeEvent(self, e) -> None:
        if self._doc is not None:
            self._doc.close()
        super().closeEvent(e)

    def done(self, r) -> None:
        if self._doc is not None:
            self._doc.close()
            self._doc = None
        super().done(r)


def can_preview(path: str) -> bool:
    ext = os.path.splitext(path)[1].lower()
    return ext == ".pdf" or ext in _IMG_EXT


def open_preview(path: str, parent=None) -> None:
    if path and os.path.isfile(path) and can_preview(path):
        PreviewDialog(path, parent).exec()
