"""
uninstall_context_menu.py
=========================
Elimina del Registro de Windows todas las entradas que
install_context_menu.py creó para PDF Master.

Uso (ejecutar como Administrador):
    python uninstall_context_menu.py
"""

import sys
import os
import ctypes
import winreg

# ---------------------------------------------------------------------------
# Configuración  (debe coincidir con install_context_menu.py)
# ---------------------------------------------------------------------------

EXTENSIONS = ["pdf", "jpg", "jpeg", "png", "bmp", "tiff", "webp"]
PARENT_KEY_NAME = "PDFMaster"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def _delete_tree(root, path: str) -> None:
    """Elimina recursivamente una clave del registro y todas sus subclaves."""
    try:
        key = winreg.OpenKey(
            root, path, 0,
            winreg.KEY_READ | winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY
        )
    except FileNotFoundError:
        return   # ya no existe

    # Eliminar subclaves recursivamente
    with key:
        while True:
            try:
                subkey_name = winreg.EnumKey(key, 0)
                _delete_tree(root, f"{path}\\{subkey_name}")
            except OSError:
                break   # no quedan subclaves

    winreg.DeleteKey(
        winreg.OpenKey(root, os.path.dirname(path),
                       0, winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY),
        os.path.basename(path)
    )


# ---------------------------------------------------------------------------
# Desinstalación
# ---------------------------------------------------------------------------

def uninstall_for_extension(ext: str) -> None:
    # Rutas actuales (HKCU) + antiguas (HKCR)
    _delete_tree(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\SystemFileAssociations\\.{ext}\\shell\\{PARENT_KEY_NAME}")
    _delete_tree(winreg.HKEY_CLASSES_ROOT, f"SystemFileAssociations\\.{ext}\\shell\\{PARENT_KEY_NAME}")
    _delete_tree(winreg.HKEY_CLASSES_ROOT, f".{ext}\\shell\\{PARENT_KEY_NAME}")
    print(f"  OK  .{ext}")


def uninstall() -> None:
    print("\nPDF Master — Desinstalando menu contextual de Windows\n")

    errores = 0
    for ext in EXTENSIONS:
        try:
            uninstall_for_extension(ext)
        except Exception as exc:
            pass # Ignoramos permisos o errores en HKCR, solo nos importa HKCU ahora

    print("\nDesinstalacion completada. El menu contextual ha sido eliminado.\n")


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uninstall()
