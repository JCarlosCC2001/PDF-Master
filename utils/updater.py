"""
utils/updater.py
Comprueba actualizaciones en GitHub Releases y descarga el instalador.

- Como máximo 1 comprobación automática al día (config "last_update_check").
- Respeta "Omitir esta versión" (config "skipped_version").
- Sin internet o error → silencioso en modo automático.
- Si no hay releases publicados aún (HTTP 404), informa que se tiene la versión más reciente.
- Solo biblioteca estándar (urllib, json).
"""
from __future__ import annotations

import json
import os
import tempfile
import time
import urllib.request
import urllib.error

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from version import __version__, GITHUB_REPO
from utils.config_manager import config

_DEFAULT_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
_HEADERS = {"User-Agent": "PDF-Master-App", "Accept": "application/vnd.github+json"}
_ONE_DAY = 24 * 60 * 60


def parse_version(v: str) -> tuple[int, ...]:
    """Parsea '1.0.0' o 'v1.0.0' a una tupla numérica (1, 0, 0)."""
    parts = []
    for p in v.strip().lstrip("vV").split("."):
        num = "".join(ch for ch in p if ch.isdigit())
        parts.append(int(num) if num else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


def is_newer(latest: str, current: str) -> bool:
    """True si la versión remota es estrictamente mayor que la instalada."""
    try:
        return parse_version(latest) > parse_version(current)
    except Exception:
        return False


class _CheckWorker(QThread):
    done = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def run(self) -> None:
        try:
            url = config.get("update_url", _DEFAULT_API_URL)
            req = urllib.request.Request(url, headers=_HEADERS)
            with urllib.request.urlopen(req, timeout=8) as resp:
                self.done.emit(json.loads(resp.read().decode("utf-8")))
        except urllib.error.HTTPError as exc:
            # 404 indica que el repositorio aun no tiene ningún release publicado
            if exc.code == 404:
                self.done.emit({})
            else:
                self.failed.emit(f"HTTP {exc.code}: {exc.reason}")
        except Exception as exc:
            self.failed.emit(str(exc))


class DownloadWorker(QThread):
    progress = pyqtSignal(int)          # 0-100
    finished_ok = pyqtSignal(str)       # ruta del instalador descargado
    failed = pyqtSignal(str)

    def __init__(self, url: str, filename: str, parent=None):
        super().__init__(parent)
        self._url = url
        self._dest = os.path.join(tempfile.gettempdir(), filename)
        self._cancel = False

    def cancel(self) -> None:
        self._cancel = True

    def run(self) -> None:
        try:
            req = urllib.request.Request(self._url, headers={"User-Agent": "PDF-Master-App"})
            with urllib.request.urlopen(req, timeout=30) as resp, open(self._dest, "wb") as f:
                total = int(resp.headers.get("Content-Length") or 0)
                read = 0
                while True:
                    if self._cancel:
                        raise RuntimeError("Descarga cancelada")
                    chunk = resp.read(64 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    read += len(chunk)
                    if total:
                        self.progress.emit(int(read * 100 / total))
            self.finished_ok.emit(self._dest)
        except Exception as exc:
            try:
                os.remove(self._dest)
            except OSError:
                pass
            self.failed.emit(str(exc))


class Updater(QObject):
    # Señales: (versión, notas, url_instalador, url_release)
    update_available = pyqtSignal(str, str, str, str)
    no_update = pyqtSignal()
    check_failed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker: _CheckWorker | None = None
        self._manual = False

    def check_for_updates(self, force: bool = False) -> None:
        """force=True -> comprobación manual (ignora límite diario y versión omitida)."""
        if self._worker and self._worker.isRunning():
            return
        if not force:
            if not config.get("check_updates", True):
                return
            last = float(config.get("last_update_check", 0) or 0)
            if time.time() - last < _ONE_DAY:
                return
        self._manual = force
        self._worker = _CheckWorker(self)
        self._worker.done.connect(self._on_done)
        self._worker.failed.connect(self._on_failed)
        self._worker.start()

    def _on_done(self, data: dict) -> None:
        config.set("last_update_check", time.time())
        latest = str(data.get("tag_name", "")).lstrip("vV")
        if not latest or not is_newer(latest, __version__):
            self.no_update.emit()
            return
        if not self._manual and config.get("skipped_version") == latest:
            return
        asset_url = ""
        for asset in data.get("assets", []) or []:
            name = str(asset.get("name", "")).lower()
            if name.endswith(".exe") and "setup" in name:
                asset_url = asset.get("browser_download_url", "")
                break
        self.update_available.emit(
            latest, data.get("body") or "", asset_url, data.get("html_url") or ""
        )

    def _on_failed(self, msg: str) -> None:
        if self._manual:
            self.check_failed.emit(msg)


# Instancia global (usada por MainWindow y SettingsPanel)
updater = Updater()
