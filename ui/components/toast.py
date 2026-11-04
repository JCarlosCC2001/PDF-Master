"""
ui/components/toast.py
Notificaciones emergentes (toast) no bloqueantes — Fase 7.

Uso:
    from ui.components.toast import show_toast
    show_toast(self, "PDF generado", "success",
               action_text="Abrir carpeta", action=lambda: ...)
"""
from __future__ import annotations

from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QParallelAnimationGroup
)
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtWidgets import (
    QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QGraphicsOpacityEffect, QGraphicsDropShadowEffect, QApplication
)
from PyQt6.QtGui import QColor

_KINDS = {
    #            acento     icono
    "success": ("#2E9E5B", "✓"),
    "error":   ("#D62828", "✕"),
    "info":    ("#2F6FDB", "i"),
    "warning": ("#E09B12", "!"),
}

_MARGIN = 20
_SPACING = 10


class Toast(QFrame):
    def __init__(self, host: QWidget, text: str, kind: str = "success",
                 title: str | None = None, action_text: str | None = None,
                 action=None, duration_ms: int = 4500):
        super().__init__(host)
        self._host = host
        accent, icon = _KINDS.get(kind, _KINDS["info"])
        self.setObjectName("toast")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            QFrame#toast {{
                background-color: #1F1F1F;
                border-radius: 10px;
                border-left: 4px solid {accent};
            }}
            QLabel {{ background: transparent; color: #F2F2F2; }}
        """)
        self.setFixedWidth(340)

        # Fundido de todo el toast (fondo incluido)
        self._opacity = QGraphicsOpacityEffect(self)
        self._opacity.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        inner = QWidget(self)
        inner.setStyleSheet("background: transparent;")
        outer.addWidget(inner)

        lay = QHBoxLayout(inner)
        lay.setContentsMargins(14, 12, 10, 12)
        lay.setSpacing(12)

        badge = QLabel(icon)
        badge.setFixedSize(26, 26)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        badge.setStyleSheet(f"background: {accent}; color: white; border-radius: 13px;")
        lay.addWidget(badge, 0, Qt.AlignmentFlag.AlignTop)

        col = QVBoxLayout()
        col.setSpacing(2)
        if title:
            t = QLabel(title)
            t.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            col.addWidget(t)
        msg = QLabel(text)
        msg.setWordWrap(True)
        msg.setFont(QFont("Segoe UI", 9))
        msg.setStyleSheet("color: #CFCFCF;" if title else "color: #F2F2F2;")
        col.addWidget(msg)

        if action_text and action:
            btn = QPushButton(action_text)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            btn.setStyleSheet(f"""
                QPushButton {{ background: transparent; color: {accent};
                               border: none; text-align: left; padding: 4px 0 0 0; }}
                QPushButton:hover {{ text-decoration: underline; }}
            """)
            btn.clicked.connect(lambda: (action(), self.dismiss()))
            col.addWidget(btn, 0, Qt.AlignmentFlag.AlignLeft)
        lay.addLayout(col, 1)

        close = QPushButton("×")
        close.setFixedSize(22, 22)
        close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close.setStyleSheet("""
            QPushButton { background: transparent; color: #8A8A8A; border: none; font-size: 14pt; }
            QPushButton:hover { color: #FFFFFF; }
        """)
        close.clicked.connect(self.dismiss)
        lay.addWidget(close, 0, Qt.AlignmentFlag.AlignTop)

        self.adjustSize()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.dismiss)
        self._duration = duration_ms
        self._closing = False
        self._anim = None

    # Pausar el cierre automático mientras el ratón está encima
    def enterEvent(self, e):
        self._timer.stop()
        super().enterEvent(e)

    def leaveEvent(self, e):
        if not self._closing:
            self._timer.start(1800)
        super().leaveEvent(e)

    def popup(self, target: QPoint) -> None:
        self.move(target + QPoint(0, 24))
        self.show()
        self.raise_()
        self._animate(target, 1.0, QEasingCurve.Type.OutCubic, 260)
        self._timer.start(self._duration)

    def slide_to(self, target: QPoint) -> None:
        anim = QPropertyAnimation(self, b"pos", self)
        anim.setDuration(200)
        anim.setEndValue(target)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def dismiss(self) -> None:
        if self._closing:
            return
        self._closing = True
        self._timer.stop()
        self._animate(self.pos() + QPoint(0, 16), 0.0, QEasingCurve.Type.InCubic, 200,
                      on_done=self._finish)

    def _finish(self) -> None:
        _ToastManager.remove(self)
        self.deleteLater()

    def _animate(self, pos: QPoint, opacity: float, curve, ms: int, on_done=None) -> None:
        group = QParallelAnimationGroup(self)
        a_pos = QPropertyAnimation(self, b"pos")
        a_pos.setDuration(ms)
        a_pos.setEndValue(pos)
        a_pos.setEasingCurve(curve)
        a_op = QPropertyAnimation(self._opacity, b"opacity")
        a_op.setDuration(ms)
        a_op.setEndValue(opacity)
        group.addAnimation(a_pos)
        group.addAnimation(a_op)
        if on_done:
            group.finished.connect(on_done)
        self._anim = group
        group.start()


class _ToastManager:
    """Apila los toasts en la esquina inferior derecha de la ventana."""
    _stacks: dict[int, list[Toast]] = {}

    @classmethod
    def add(cls, host: QWidget, toast: Toast) -> None:
        stack = cls._stacks.setdefault(id(host), [])
        stack.append(toast)
        if len(stack) > 4:              # no saturar la pantalla
            stack[0].dismiss()
        toast.popup(cls._target(host, stack, toast))
        cls._relayout(host, animate=True, skip=toast)

    @classmethod
    def remove(cls, toast: Toast) -> None:
        host = toast._host
        stack = cls._stacks.get(id(host), [])
        if toast in stack:
            stack.remove(toast)
        cls._relayout(host, animate=True)

    @classmethod
    def relayout(cls, host: QWidget) -> None:
        cls._relayout(host, animate=False)

    @classmethod
    def _target(cls, host, stack, toast) -> QPoint:
        y = host.height() - _MARGIN
        for t in reversed(stack):
            y -= t.height()
            if t is toast:
                break
            y -= _SPACING
        return QPoint(host.width() - toast.width() - _MARGIN, y)

    @classmethod
    def _relayout(cls, host, animate: bool, skip=None) -> None:
        stack = cls._stacks.get(id(host), [])
        for t in stack:
            if t is skip or t._closing:
                continue
            target = cls._target(host, stack, t)
            if animate:
                t.slide_to(target)
            else:
                t.move(target)


def show_toast(widget: QWidget, text: str, kind: str = "success",
               title: str | None = None, action_text: str | None = None,
               action=None, duration_ms: int = 4500) -> Toast:
    """Muestra un toast sobre la ventana principal que contiene a `widget`."""
    host = widget.window() if widget else QApplication.activeWindow()
    toast = Toast(host, text, kind, title, action_text, action, duration_ms)
    _ToastManager.add(host, toast)
    # Si la ventana no está en primer plano, hacer parpadear la barra de tareas
    if not host.isActiveWindow():
        QApplication.alert(host, 0)
    return toast


def relayout_toasts(host: QWidget) -> None:
    _ToastManager.relayout(host)


def open_in_explorer(path: str) -> None:
    """Abre el Explorador con el archivo seleccionado (o la carpeta)."""
    import os
    import subprocess
    if os.path.isfile(path):
        subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
    elif os.path.isdir(path):
        os.startfile(path)
