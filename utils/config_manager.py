"""
utils/config_manager.py
Gestiona la configuración persistente de PDF Master en config.json.
"""
import json
import os
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEGACY_CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

APP_DATA_DIR = os.path.join(os.getenv("APPDATA", os.path.expanduser("~")), "PDF Master")
CONFIG_PATH = os.path.join(APP_DATA_DIR, "config.json")

# Migrar configuración anterior si existe
if os.path.exists(LEGACY_CONFIG_PATH) and not os.path.exists(CONFIG_PATH):
    os.makedirs(APP_DATA_DIR, exist_ok=True)
    try:
        shutil.copy(LEGACY_CONFIG_PATH, CONFIG_PATH)
            except OSError:
        pass

DEFAULTS = {
    "color_mode": "original",          # original | grayscale | blackwhite
    "page_size": "A4",                 # A4 | Letter | Legal | A3 | A5 | Custom
    "orientation": "portrait",         # portrait | landscape
    "image_quality": 80,               # 1-100
    "output_folder": "",               # carpeta de salida predeterminada
    "language": "es",                  # es | en
    "custom_width_mm": 210,
    "custom_height_mm": 297,
    "dpi": 150,                        # DPI para PDF→Imágenes
    "image_format": "PNG",             # PNG | JPG | TIFF
    "check_updates": True,             # buscar actualizaciones al iniciar
    "last_update_check": 0,            # timestamp de la última comprobación
    "skipped_version": "",             # versión que el usuario decidió omitir
}


class ConfigManager:
    """Gestiona lectura/escritura de la configuración de la aplicación."""

    def __init__(self):
        self._config: dict = {}
        self.load()

    def load(self) -> None:
        """Carga la configuración desde disco. Si no existe, usa los valores por defecto."""
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                # Mezcla: valores guardados tienen prioridad, defaults rellenan los que faltan
                self._config = {**DEFAULTS, **saved}
            except (json.JSONDecodeError, OSError):
                self._config = dict(DEFAULTS)
        else:
            self._config = dict(DEFAULTS)
        self.save()

    def save(self) -> None:
        """Persiste la configuración actual en disco."""
        try:
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def get(self, key: str, fallback=None):
        """Obtiene un valor de configuración."""
        return self._config.get(key, fallback if fallback is not None else DEFAULTS.get(key))

    def set(self, key: str, value) -> None:
        """Establece un valor y lo persiste."""
        self._config[key] = value
        self.save()

    def reset_to_defaults(self) -> None:
        """Restaura todos los valores a los predeterminados."""
        self._config = dict(DEFAULTS)
        self.save()

    @property
    def all(self) -> dict:
        """Devuelve una copia de la configuración completa."""
        return dict(self._config)


# Instancia global accesible desde toda la app
config = ConfigManager()
