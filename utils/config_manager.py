"""
utils/config_manager.py
Gestiona la configuración persistente de PDF Master en config.json.
"""
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

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
