"""
utils/single_instance.py
Garantiza una sola ventana de PDF Master.

Cuando se seleccionan varios archivos en el Explorador y se usa el menú
contextual, Windows lanza UN proceso por archivo. Este módulo hace que:
  - El primer proceso (dueño del mutex) abra un QLocalServer y la ventana.
  - Los demás envíen su (tool, archivo) al primero y terminen sin mostrar nada.
"""
from __future__ import annotations

import json
import sys
import time

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

SERVER_NAME = "PDFMaster_SingleInstance_v1"
_MUTEX_NAME = "Local\\PDFMaster_SingleInstance_Mutex_v1"
_ERROR_ALREADY_EXISTS = 183

_mutex_handle = None  # se mantiene vivo mientras dure el proceso


def acquire_primary() -> bool:
    """True si este proceso es la instancia principal."""
    global _mutex_handle
    if sys.platform != "win32":
        return True
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.CreateMutexW.restype = ctypes.c_void_p
    _mutex_handle = kernel32.CreateMutexW(None, False, _MUTEX_NAME)
    return kernel32.GetLastError() != _ERROR_ALREADY_EXISTS


def send_to_primary(tool_id: str | None, filepath: str | None,
                    timeout_s: float = 8.0) -> bool:
    """Envía los argumentos a la instancia principal (reintenta mientras arranca)."""
    payload = json.dumps({"tool": tool_id, "file": filepath}).encode("utf-8")
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        sock = QLocalSocket()
        sock.connectToServer(SERVER_NAME)
        if sock.waitForConnected(300):
            sock.write(payload + b"\n")
            sock.flush()
            sock.waitForBytesWritten(1000)
            sock.disconnectFromServer()
            return True
        time.sleep(0.1)
    return False


class InstanceServer(QObject):
    """Servidor local que recibe archivos de instancias secundarias."""

    message_received = pyqtSignal(object, object)  # (tool_id, filepath)

    def __init__(self, parent=None):
        super().__init__(parent)
        QLocalServer.removeServer(SERVER_NAME)
        self._server = QLocalServer(self)
        self._server.newConnection.connect(self._on_new_connection)
        self._server.listen(SERVER_NAME)

    def _on_new_connection(self) -> None:
        while self._server.hasPendingConnections():
            sock = self._server.nextPendingConnection()
            if sock is None:
                continue
            sock.setParent(self)
            buf = bytearray()

            def _read(s=sock, b=buf):
                b.extend(bytes(s.readAll()))
                while b"\n" in b:
                    line, _, rest = bytes(b).partition(b"\n")
                    b[:] = rest
                    try:
                        data = json.loads(line.decode("utf-8"))
                        self.message_received.emit(data.get("tool"), data.get("file"))
                    except Exception:
                        pass

            sock.readyRead.connect(_read)
            sock.disconnected.connect(sock.deleteLater)
            if sock.bytesAvailable() > 0:
                _read()
