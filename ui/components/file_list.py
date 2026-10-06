"""
ui/components/file_list.py
Lista de archivos con reordenamiento (subir/bajar) y eliminacion.
Reutilizable en todos los paneles de la Fase 2 y 3.
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QListWidgetItem, QPushButton, QLabel, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor


CLR_RED    = "#D62828"
CLR_BG     = "#FFFFFF"
CLR_BORDER = "#E0E0E0"
CLR_MUTED  = "#888888"
CLR_ITEM   = "#1A1A1A"
CLR_ITEM_H = "#FEF2F2"


class FileListWidget(QWidget):
    """
    Widget de lista de archivos con controles de reordenamiento.
    Emite `files_changed` cada vez que cambia la lista.
    """
    files_changed = pyqtSignal(list)   # list[str]

    def __init__(
        self,
        file_type_label: str = "archivo",
        parent=None,
    ):
        super().__init__(parent)
        self._file_type = file_type_label
        self._paths: list[str] = []
        self.setStyleSheet(f"background-color: {CLR_BG};")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # ── Lista ─────────────────────────────────────────────────────────────
        self._list = QListWidget()
        self._list.setFont(QFont("Segoe UI", 9))
        self._list.setAlternatingRowColors(True)
        self._list.setStyleSheet(f"""
            QListWidget {{
                background-color: {CLR_BG};
                border: 1px solid {CLR_BORDER};
                border-radius: 6px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 6px 10px;
                color: {CLR_ITEM};
                border-bottom: 1px solid #F5F5F5;
            }}
            QListWidget::item:selected {{
                background-color: {CLR_ITEM_H};
                color: {CLR_RED};
            }}
            QListWidget::item:alternate {{
                background-color: #FAFAFA;
            }}
        """)
        layout.addWidget(self._list)

        # ── Contador ──────────────────────────────────────────────────────────
        self._count_lbl = QLabel("0 archivos")
        self._count_lbl.setFont(QFont("Segoe UI", 8))
        self._count_lbl.setStyleSheet(f"color: {CLR_MUTED}; background: transparent;")
        layout.addWidget(self._count_lbl)

        # ── Botones de control ────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        self._btn_up     = self._make_btn("Subir",     self._move_up)
        self._btn_down   = self._make_btn("Bajar",     self._move_down)
        self._btn_remove = self._make_btn("Quitar",    self._remove_selected, danger=True)
        self._btn_clear  = self._make_btn("Limpiar",   self._clear_all, danger=True)

        for btn in (self._btn_up, self._btn_down, self._btn_remove, self._btn_clear):
            btn_row.addWidget(btn)

        layout.addLayout(btn_row)

    def _make_btn(self, label: str, slot, danger: bool = False) -> QPushButton:
        btn = QPushButton(label)
        btn.setFixedHeight(28)
        btn.setFont(QFont("Segoe UI", 8))
        if danger:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {CLR_RED};
                    border: 1px solid {CLR_RED};
                    border-radius: 4px;
                    padding: 0 8px;
                }}
                QPushButton:hover {{ background-color: #FEF2F2; }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #F5F5F5;
                    color: {CLR_ITEM};
                    border: 1px solid {CLR_BORDER};
                    border-radius: 4px;
                    padding: 0 8px;
                }}
                QPushButton:hover {{ background-color: #EBEBEB; }}
            """)
        btn.clicked.connect(slot)
        return btn

    # ── API publica ───────────────────────────────────────────────────────────
    def add_files(self, paths: list[str]) -> None:
        """Agrega archivos a la lista (evita duplicados)."""
        added = False
        for path in paths:
            if path not in self._paths:
                self._paths.append(path)
                self._list.addItem(self._make_item(path))
                added = True
        if added:
            self._update_count()
            self.files_changed.emit(list(self._paths))

    def get_files(self) -> list[str]:
        return list(self._paths)

    def clear(self) -> None:
        self._paths.clear()
        self._list.clear()
        self._update_count()
        self.files_changed.emit([])

    # ── Slots privados ────────────────────────────────────────────────────────
    def _make_item(self, path: str) -> QListWidgetItem:
        name = os.path.basename(path)
        size_mb = os.path.getsize(path) / (1024 * 1024)
        label = f"  {name}   ({size_mb:.1f} MB)"
        item = QListWidgetItem(label)
        item.setData(Qt.ItemDataRole.UserRole, path)
        return item

    def _move_up(self) -> None:
        row = self._list.currentRow()
        if row > 0:
            self._paths[row], self._paths[row - 1] = self._paths[row - 1], self._paths[row]
            item = self._list.takeItem(row)
            self._list.insertItem(row - 1, item)
            self._list.setCurrentRow(row - 1)
            self.files_changed.emit(list(self._paths))

    def _move_down(self) -> None:
        row = self._list.currentRow()
        if 0 <= row < self._list.count() - 1:
            self._paths[row], self._paths[row + 1] = self._paths[row + 1], self._paths[row]
            item = self._list.takeItem(row)
            self._list.insertItem(row + 1, item)
            self._list.setCurrentRow(row + 1)
            self.files_changed.emit(list(self._paths))

    def _remove_selected(self) -> None:
        row = self._list.currentRow()
        if row >= 0:
            self._list.takeItem(row)
            self._paths.pop(row)
            self._update_count()
            self.files_changed.emit(list(self._paths))

    def _clear_all(self) -> None:
        self.clear()

    def _update_count(self) -> None:
        n = len(self._paths)
        self._count_lbl.setText(f"{n} {self._file_type}{'s' if n != 1 else ''}")
