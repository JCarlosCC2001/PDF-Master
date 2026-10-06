"""
ui/components/drop_zone.py
Zona de arrastre y suelta de archivos reutilizable para todos los paneles.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent, QDragLeaveEvent


CLR_BORDER_NORMAL  = "#CCCCCC"
CLR_BORDER_HOVER   = "#D62828"
CLR_BG_NORMAL      = "#F8F8F8"
CLR_BG_HOVER       = "#FFF0F0"
CLR_TEXT           = "#6B6B6B"
CLR_ICON           = "#D62828"


class DropZone(QWidget):
    """
    Widget de zona drag & drop.
    Emite `files_dropped` con la lista de rutas absolutas al soltar archivos.
    """
    files_dropped = pyqtSignal(list)   # list[str]

    def __init__(
        self,
        accepted_extensions: list[str] | None = None,
        message: str = "Arrastra archivos aquí",
        sub_message: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self._accepted = [ext.lower() for ext in (accepted_extensions or [])]
        self.setAcceptDrops(True)
        self.setMinimumHeight(180)
        self._build_ui(message, sub_message)
        self._set_style(hovered=False)

    def _build_ui(self, message: str, sub_message: str) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)

        # Ícono
        self._icon = QLabel("📂")
        self._icon.setFont(QFont("Segoe UI Emoji", 36))
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self._icon)

        # Mensaje principal
        self._msg = QLabel(message)
        self._msg.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self._msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._msg.setStyleSheet(f"color: {CLR_TEXT}; background: transparent; border: none;")
        layout.addWidget(self._msg)

        # Sub-mensaje
        if sub_message:
            sub = QLabel(sub_message)
            sub.setFont(QFont("Segoe UI", 9))
            sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sub.setStyleSheet(f"color: {CLR_TEXT}; background: transparent; border: none;")
            layout.addWidget(sub)

    def _set_style(self, hovered: bool) -> None:
        border_clr = CLR_BORDER_HOVER if hovered else CLR_BORDER_NORMAL
        bg_clr     = CLR_BG_HOVER     if hovered else CLR_BG_NORMAL
        dash       = "dashed"
        self.setStyleSheet(f"""
            DropZone {{
                border: 2px {dash} {border_clr};
                border-radius: 10px;
                background-color: {bg_clr};
            }}
        """)

    # ── Drag & Drop ────────────────────────────────────────────────────────────
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._set_style(hovered=True)
        else:
            event.ignore()

    def dragMoveEvent(self, event) -> None:
        """Necesario en PyQt6/Windows: sin esto el drop se cancela antes de llegar a dropEvent."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:
        self._set_style(hovered=False)

    def dropEvent(self, event: QDropEvent) -> None:
        self._set_style(hovered=False)
        paths = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if self._accepted:
                ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
                if ext not in self._accepted:
                    continue
            paths.append(path)
        if paths:
            self.files_dropped.emit(paths)
        event.acceptProposedAction()

