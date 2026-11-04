"""
ui/main_window.py
Ventana principal de PDF Master con sidebar de navegacion y area de contenido.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QProgressBar,
    QGraphicsOpacityEffect, QMessageBox, QProgressDialog, QApplication
)
from PyQt6.QtCore import (
    QSize, QTimer, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QPoint
)
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
        self._transition = None
        self._pending_external = 0
        self._external_timer = QTimer(self)
        self._external_timer.setSingleShot(True)
        self._external_timer.timeout.connect(self._announce_external_files)
        self._build_ui()
        self._polish_progress_bars()
        self._navigate(initial_page, animate=False)

        if initial_file or initial_tool:
            self._handle_file_argument(initial_file, initial_tool, animate=False)

        # Buscar actualizaciones (Fase 6) — como máximo 1 vez al día
        from utils.updater import updater
        self.updater = updater
        self.updater.update_available.connect(self._on_update_available)
        QTimer.singleShot(2500, self.updater.check_for_updates)

    # ── Actualizaciones ───────────────────────────────────────────────────────
    def _on_update_available(self, version: str, notes: str, asset_url: str, html_url: str) -> None:
        """Aviso no intrusivo: toast con acceso a los detalles."""
        from ui.components.toast import show_toast
        show_toast(
            self, f"La versión {version} de PDF Master está disponible.", "info",
            title="Actualización disponible", action_text="Ver detalles",
            action=lambda: self._show_update_dialog(version, notes, asset_url, html_url),
            duration_ms=12000,
        )

    def _show_update_dialog(self, version: str, notes: str, asset_url: str, html_url: str) -> None:
        from utils.config_manager import config
        msg = QMessageBox(self)
        msg.setWindowTitle("Actualización disponible")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(f"<b>PDF Master {version}</b> está disponible.")
        msg.setInformativeText("¿Deseas descargarla e instalarla ahora?")
        if notes:
            msg.setDetailedText(notes)
        b_install = msg.addButton("Descargar e instalar", QMessageBox.ButtonRole.AcceptRole)
        msg.addButton("Ahora no", QMessageBox.ButtonRole.RejectRole)
        b_skip = msg.addButton("Omitir esta versión", QMessageBox.ButtonRole.DestructiveRole)
        msg.exec()
        clicked = msg.clickedButton()
        if clicked is b_skip:
            config.set("skipped_version", version)
        elif clicked is b_install:
            if asset_url:
                self._download_update(version, asset_url)
            else:
                import webbrowser
                webbrowser.open(html_url)

    def _download_update(self, version: str, url: str) -> None:
        from utils.updater import DownloadWorker
        dlg = QProgressDialog(f"Descargando PDF Master {version}...", "Cancelar", 0, 100, self)
        dlg.setWindowTitle("Actualización")
        dlg.setMinimumDuration(0)
        dlg.setAutoClose(False)
        dlg.setValue(0)
        worker = DownloadWorker(url, f"PDF-Master-Setup-{version}.exe", self)
        worker.progress.connect(dlg.setValue)
        dlg.canceled.connect(worker.cancel)

        def _ok(path: str) -> None:
            dlg.close()
            import subprocess
            try:
                subprocess.Popen([path, "/CLOSEAPPLICATIONS"], close_fds=True)
            except OSError as exc:
                QMessageBox.critical(self, "Error", f"No se pudo ejecutar el instalador:\n{exc}")
                return
            QApplication.quit()

        def _fail(err: str) -> None:
            dlg.close()
            if "cancelada" not in err:
                from ui.components.toast import show_toast
                show_toast(self, err, "error", title="No se pudo descargar", duration_ms=7000)

        worker.finished_ok.connect(_ok)
        worker.failed.connect(_fail)
        worker.start()
        self._download_worker = worker

    # ── Pulido visual (Fase 7) ────────────────────────────────────────────────
    def _polish_progress_bars(self) -> None:
        """Muestra el porcentaje en todas las barras de progreso de los paneles."""
        for bar in self.findChildren(QProgressBar):
            bar.setTextVisible(True)
            bar.setFormat("%p%")
            bar.setFixedHeight(18)
            bar.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            bar.setStyleSheet("""
                QProgressBar {
                    border: none; border-radius: 9px; background: #E4E4E4;
                    color: #1A1A1A; text-align: center;
                }
                QProgressBar::chunk {
                    border-radius: 9px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                stop:0 #E84545, stop:1 #D62828);
                }
            """)

    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        from ui.components.toast import relayout_toasts
        relayout_toasts(self)

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

    def _navigate(self, page_id: str, animate: bool = True) -> None:
        """Cambia al panel indicado y actualiza la selección del sidebar."""
        if page_id not in self._pages:
            return
        widget = self._pages[page_id]
        changed = self._stack.currentWidget() is not widget
        self._stack.setCurrentWidget(widget)
        self._sidebar.set_active_page(page_id)
        if animate and changed:
            self._animate_in(widget)

    def _animate_in(self, widget: QWidget) -> None:
        """Transición: fundido + desplazamiento lateral corto (Fase 7)."""
        if self._transition is not None:
            group_old, cleanup_old = self._transition
            group_old.stop()
            cleanup_old()
            self._transition = None
        effect = QGraphicsOpacityEffect(widget)
        effect.setOpacity(0.0)
        widget.setGraphicsEffect(effect)

        end = QPoint(0, 0)
        widget.move(18, 0)

        fade = QPropertyAnimation(effect, b"opacity")
        fade.setDuration(220)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.Type.OutCubic)

        slide = QPropertyAnimation(widget, b"pos")
        slide.setDuration(240)
        slide.setStartValue(QPoint(18, 0))
        slide.setEndValue(end)
        slide.setEasingCurve(QEasingCurve.Type.OutCubic)

        group = QParallelAnimationGroup(self)
        group.addAnimation(fade)
        group.addAnimation(slide)

        def _cleanup():
            # Quitar el efecto evita costo de render y conflictos con otros efectos
            widget.setGraphicsEffect(None)
            widget.move(end)

        group.finished.connect(_cleanup)
        self._transition = (group, _cleanup)
        group.start()

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

    def open_external(self, tool_id, filepath) -> None:
        """Recibe un archivo enviado por otra instancia (multiselección en el Explorador)."""
        self._handle_file_argument(filepath, tool_id, animate=False)
        if filepath:
            self._pending_external += 1
            # Agrupa los archivos que llegan seguidos en un solo aviso
            self._external_timer.start(700)
        from PyQt6.QtCore import Qt
        if self.isMinimized():
            self.showNormal()
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized
                            | Qt.WindowState.WindowActive)
        self.raise_()
        self.activateWindow()

    def _announce_external_files(self) -> None:
        n = self._pending_external
        self._pending_external = 0
        if n > 0:
            from ui.components.toast import show_toast
            show_toast(self, f"Se agregaron {n} archivo{'s' if n != 1 else ''} desde el Explorador.",
                       "info", duration_ms=3000)

    def _handle_file_argument(
        self,
        filepath: str | None,
        tool_id: str | None = None,
        animate: bool = True,
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

        # 1. tool_id explícito ("open" con archivo → se decide por extensión)
        if tool_id and tool_id in TOOL_TO_PAGE and not (tool_id == "open" and filepath):
            page = TOOL_TO_PAGE[tool_id]
        # 2. Inferir por extensión
        elif filepath:
            ext = filepath.rsplit(".", 1)[-1].lower() if "." in filepath else ""
            page = EXT_TO_PAGE.get(ext, "home")
        else:
            page = "home"

        self._navigate(page, animate=animate)

        # Cargar el archivo en el panel activo (si el panel lo soporta)
        if filepath and page in self._pages:
            panel = self._pages[page]
            if hasattr(panel, "load_file"):
                panel.load_file(filepath)
