"""
install_context_menu.py
=======================
Registra PDF Master en el menú contextual (clic derecho) del Explorador de
Windows para archivos PDF e imágenes.

Uso (ejecutar como Administrador):
    python install_context_menu.py

Qué hace:
    Escribe entradas en HKEY_CLASSES_ROOT\\SystemFileAssociations\\.<ext>\\shell\\PDFMaster
    (esta ruta funciona aunque otro programa —Acrobat, Nitro— sea el predeterminado;
    la ruta antigua HKCR\\.<ext>\\shell era ignorada por Windows en ese caso)
    Al hacer clic derecho aparecerá el submenú:

        PDF Master >
            Abrir en PDF Master
            Convertir a PDF         (solo imágenes)
            Convertir a Imágenes    (solo PDF)
            Unir con...             (solo PDF)
            Reordenar páginas       (solo PDF)
            Reparar PDF             (solo PDF)
"""

import sys
import os
import ctypes
import winreg

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXE = sys.executable
MAIN_PY = os.path.join(ROOT_DIR, "main.py")

# pythonw.exe = mismo Python pero sin ventana de consola
_PYTHONW = os.path.join(os.path.dirname(PYTHON_EXE), "pythonw.exe")
LAUNCH_EXE = _PYTHONW if os.path.isfile(_PYTHONW) else PYTHON_EXE

CMD_BASE = f'"{LAUNCH_EXE}" "{MAIN_PY}"'

# extensión → lista de (etiqueta visible, argumento --tool)
EXT_MENUS: dict[str, list[tuple[str, str]]] = {
    "pdf": [
        ("Abrir en PDF Master",  "open"),
        ("Convertir a Imágenes", "pdf2img"),
        ("Unir con...",          "merge"),
        ("Reordenar páginas",    "reorder"),
        ("Reparar PDF",          "repair"),
    ],
    "jpg":  [("Abrir en PDF Master", "open"), ("Convertir a PDF", "img2pdf")],
    "jpeg": [("Abrir en PDF Master", "open"), ("Convertir a PDF", "img2pdf")],
    "png":  [("Abrir en PDF Master", "open"), ("Convertir a PDF", "img2pdf")],
    "bmp":  [("Abrir en PDF Master", "open"), ("Convertir a PDF", "img2pdf")],
    "tiff": [("Abrir en PDF Master", "open"), ("Convertir a PDF", "img2pdf")],
    "webp": [("Abrir en PDF Master", "open"), ("Convertir a PDF", "img2pdf")],
}

PARENT_LABEL = "PDF Master"
PARENT_KEY_NAME = "PDFMaster"

# Ruta base donde se registra el menú (relativa a HKEY_CLASSES_ROOT)
ASSOC_ROOT = "SystemFileAssociations"

# Ícono: usa el de la app si existe, si no el de Python
_ICON_FILE = os.path.join(ROOT_DIR, "assets", "icon.ico")
ICON = _ICON_FILE if os.path.isfile(_ICON_FILE) else PYTHON_EXE


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def _create_key(root, path: str):
    return winreg.CreateKeyEx(
        root, path, 0,
        winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY
    )


def _set_str(key, name: str, value: str) -> None:
    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)


def _delete_tree(root, path: str) -> None:
    """Elimina recursivamente una clave del registro (si existe)."""
    try:
        key = winreg.OpenKey(
            root, path, 0,
            winreg.KEY_READ | winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY
        )
    except FileNotFoundError:
        return
    with key:
        while True:
            try:
                sub = winreg.EnumKey(key, 0)
            except OSError:
                break
            _delete_tree(root, f"{path}\\{sub}")
    parent_path, name = path.rsplit("\\", 1)
    with winreg.OpenKey(root, parent_path, 0,
                        winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY) as parent:
        winreg.DeleteKey(parent, name)


# ---------------------------------------------------------------------------
# Instalación
# ---------------------------------------------------------------------------

def install_for_extension(ext: str, items: list[tuple[str, str]]) -> None:
    # Limpiar la ruta antigua (versiones previas del instalador)
    _delete_tree(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\.{ext}\\shell\\{PARENT_KEY_NAME}")

    base_path = f"Software\\Classes\\{ASSOC_ROOT}\\.{ext}\\shell\\{PARENT_KEY_NAME}"

    # Nodo padre — etiqueta e ícono.
    # Los submenús en cascada requieren MUIVerb (el valor por defecto se ignora).
    with _create_key(winreg.HKEY_CURRENT_USER, base_path) as parent:
        _set_str(parent, "MUIVerb", PARENT_LABEL)
        _set_str(parent, "Icon", ICON)
        _set_str(parent, "SubCommands", "")

    # Ítems hijos bajo <base>\shell
    shell_path = f"{base_path}\\shell"
    for label, tool in items:
        item_id = tool.replace("2", "to")   # img2pdf → imgtopdf (nombre seguro)
        item_path = f"{shell_path}\\{item_id}"

        with _create_key(winreg.HKEY_CURRENT_USER, item_path) as item:
            _set_str(item, "", label)
            # Sin esto Windows oculta la opción al seleccionar más de 15 archivos
            _set_str(item, "MultiSelectModel", "Player")

        with _create_key(winreg.HKEY_CURRENT_USER, f"{item_path}\\command") as cmd:
            _set_str(cmd, "", f'{CMD_BASE} --tool {tool} "%1"')

    print(f"  OK  .{ext}  ({len(items)} opciones)")


def install() -> None:
    print("\nPDF Master — Instalando menu contextual de Windows\n")
    print(f"  Interprete : {PYTHON_EXE}")
    print(f"  Script     : {MAIN_PY}\n")

    if not os.path.isfile(MAIN_PY):
        print(f"ERROR: No se encontro main.py en: {MAIN_PY}")
        sys.exit(1)

    errores = 0
    for ext, items in EXT_MENUS.items():
        try:
            install_for_extension(ext, items)
        except PermissionError:
            print(f"  ERROR  .{ext}  — Sin permisos (ejecuta como Administrador)")
            errores += 1
        except Exception as exc:
            print(f"  ERROR  .{ext}  — {exc}")
            errores += 1

    if errores == 0:
        print("\nInstalacion completada correctamente.")
        print("Haz clic derecho sobre un PDF o imagen para verificar.\n")
    else:
        print(f"\nInstalacion finalizada con {errores} error(es).\n")


# ---------------------------------------------------------------------------
# Punto de entrada con auto-elevacion
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    install()
