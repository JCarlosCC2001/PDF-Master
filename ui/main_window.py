"""
ui/main_window.py
Ventana principal de PDF Master con sidebar de navegacion y area de contenido.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget
)
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QFont

from ui.components.sidebar import Sidebar
from ui.panels.home_panel import HomePanel
from ui.panels.placeholder_panel import PlaceholderPanel
from ui.panels.settings_panel import SettingsPanel
# Fase 2 — paneles reales
from ui.panels.img_to_pdf_panel import ImgToPdfPanel
from ui.panels.pdf_to_img_panel import PdfToImgPanel
from ui.panels.merge_panel import MergePanel
# Fase 3 — paneles reales
from ui.panels.reorder_panel import ReorderPanel
from ui.panels.repair_panel import RepairPanel
from ui.panels.edit_panel import EditPanel


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación PDF Master."""

    def __init__(
        self,
        initial_page: str = "home",
        initial_file: str | None = None,
        initial_tool: str | None = None,
    ):
        super().__init__()
        self.setWindowTitle("PDF Master")
        self.setMinimumSize(QSize(720, 500))
        self.resize(1000, 660)
        self._build_ui()
        self._navigate(initial_page)

        if initial_file or initial_tool:
            self._handle_file_argument(initial_file, initial_tool)

    def _build_ui(self) -> None:
        # ── Widget central ────────────────────────────────────────────────────
        central = QWidget()
        central.setStyleSheet("background-color: #EFEFEF;")
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ───────────────────────────────────────────────────────────
        self._sidebar = Sidebar()
        self._sidebar.page_changed.connect(self._navigate)
        root.addWidget(self._sidebar)

        # ── Stack de paneles ──────────────────────────────────────────────────
        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background-color: #F0F0F0;")
        root.addWidget(self._stack)

        # Registrar paneles
        self._pages: dict[str, QWidget] = {}

        home = HomePanel()
        home.navigate.connect(self._navigate)
        self._register_panel("home", home)

        # ── Fase 2: paneles funcionales ───────────────────────────────────────
        self._register_panel("img2pdf", ImgToPdfPanel())
        self._register_panel("pdf2img", PdfToImgPanel())
        self._register_panel("merge",   MergePanel())

        # ── Fase 3: paneles funcionales ───────────────────────────────────────
        self._register_panel("reorder", ReorderPanel())
        self._register_panel("repair",  RepairPanel())
        self._register_panel("edit",    EditPanel())

        self._register_panel("settings", SettingsPanel())


    def _register_panel(self, page_id: str, widget: QWidget) -> None:
        self._pages[page_id] = widget
        self._stack.addWidget(widget)

    def _navigate(self, page_id: str) -> None:
        """Cambia al panel indicado y actualiza la selección del sidebar."""
        if page_id in self._pages:
            self._stack.setCurrentWidget(self._pages[page_id])
            self._sidebar.set_active_page(page_id)

    def replace_panel(self, page_id: str, widget: QWidget) -> None:
        """
        Reemplaza un panel placeholder por uno funcional.
        Llamado desde fases posteriores al implementar herramientas.
        """
        if page_id in self._pages:
            old = self._pages[page_id]
            idx = self._stack.indexOf(old)
            self._stack.removeWidget(old)
            old.deleteLater()

        self._pages[page_id] = widget
        self._stack.addWidget(widget)

    def _handle_file_argument(
        self,
        filepath: str | None,
        tool_id: str | None = None,
    ) -> None:
        """
        Navega al panel correcto según el argumento --tool y/o la extensión
        del archivo recibido desde el menú contextual de Windows.

        Prioridad:
            1. tool_id explícito (--tool <id>)  → navega directamente
            2. Extensión del archivo             → infiere herramienta
            3. Fallback                          → home
        """
        # Mapeo de tool_id del menú contextual → page_id interno
        TOOL_TO_PAGE: dict[str, str] = {
            "open":    "home",
            "img2pdf": "img2pdf",
            "pdf2img": "pdf2img",
            "merge":   "merge",
            "reorder": "reorder",
            "repair":  "repair",
            "edit":    "edit",
        }

        # Mapeo extensión → page_id cuando no hay --tool explícito
        EXT_TO_PAGE: dict[str, str] = {
            "pdf":  "repair",    # para PDFs, abrir en Reparar (opción más útil)
            "jpg":  "img2pdf",
            "jpeg": "img2pdf",
            "png":  "img2pdf",
            "bmp":  "img2pdf",
            "tiff": "img2pdf",
            "webp": "img2pdf",
        }

        # 1. tool_id explícito
        if tool_id and tool_id in TOOL_TO_PAGE:
            page = TOOL_TO_PAGE[tool_id]
        # 2. Inferir por extensión
        elif filepath:
            ext = filepath.rsplit(".", 1)[-1].lower() if "." in filepath else ""
            page = EXT_TO_PAGE.get(ext, "home")
        else:
            page = "home"

        self._navigate(page)

        # Cargar el archivo en el panel activo (si el panel lo soporta)
        if filepath and page in self._pages:
            panel = self._pages[page]
            if hasattr(panel, "load_file"):
                panel.load_file(filepath)
