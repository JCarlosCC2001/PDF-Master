# 📋 Plan de Acción — PDF Master

> **Stack tecnológico:** Python 3.15 + PyQt6 (interfaz), PyMuPDF / Pillow / img2pdf / pikepdf (procesamiento PDF), PyInstaller + Inno Setup (distribución)
> **Plataforma:** Windows 10 / 11 (64-bit)
> **Paleta:** Rojo `#D62828` · Blanco `#FAFAFA` · Negro `#1A1A1A`
> **Última actualización:** 2026-11-04 — v1.0.0 (Fases 1–7 completadas y verificadas)

---

## 🗂️ Resumen de Fases

| Fase | Nombre | Estado |
|------|--------|--------|
| 1 | Fundamentos y estructura | ✅ Completada |
| 2 | Herramientas core (I) — Img→PDF, PDF→Img, Unir | ✅ Completada |
| 3 | Herramientas core (II) — Reordenar, Reparar, Editar | ✅ Completada |
| 4 | Menú contextual de Windows (clic derecho) | ✅ Completada |
| 5 | Empaquetado y distribución (.exe, ícono, README) | ✅ Completada |
| 6 | Instalador, versiones y actualizaciones | ✅ Completada |
| 7 | Pulido visual (animaciones, toasts, vista previa) | ✅ Completada |

---

## 🔵 FASE 1 — Fundamentos y estructura del proyecto
**Estado:** ✅ Completada — 2026-09-30

### Objetivos y Entregables
- Estructura modular del proyecto en Python + PyQt6
- `main.py` y `ui/main_window.py` con navegación lateral (`Sidebar`)
- `utils/config_manager.py` para gestión de configuración
- Paleta visual con fondo reforzado vía `QPalette` (evita bugs transparent en PyQt6)

---

## 🟡 FASE 2 — Herramientas core (Parte I)
**Estado:** ✅ Completada — 2026-09-30

### Herramientas
- **Imágenes → PDF:** Soporta JPG, PNG, BMP, TIFF, WEBP, tamaño de hoja, orientación, color/B&W.
- **PDF → Imágenes:** Extracción por páginas o todo el documento, formato configurable, DPI personalizable (72-600).
- **Unir PDFs:** Drag & drop múltiple, reordenamiento antes de combinar.
- Procesamiento en `QThread` con barra de progreso en tiempo real.

---

## 🟠 FASE 3 — Herramientas core (Parte II)
**Estado:** ✅ Completada — 2026-09-30

### Herramientas
- **Reordenar PDF:** Renderizado de miniaturas por página en segundo plano, rotación y eliminación interactiva.
- **Reparar PDF:** Estrategia dual (pikepdf como primer intento, PyMuPDF como fallback), soporte de desbloqueo y diagnóstico.
- **Editar PDF:** Marcas de agua de texto, texto posicional XY e inserción de páginas en blanco.

---

## 🟢 FASE 4 — Menú contextual de Windows
**Estado:** ✅ Completada — 2026-10-01

### Integración con el Sistema Operativo
- Scripts `install_context_menu.py` y `uninstall_context_menu.py`.
- Registro en `HKCU\Software\Classes\SystemFileAssociations` (funciona con cualquier visor predeterminado).
- Submenú cascada nativo para PDFs e imágenes.
- Parámetros `--tool <id> <archivo>` con auto-enrutamiento al panel correcto.

---

## 🔴 FASE 5 — Empaquetado y distribución (.exe)
**Estado:** ✅ Completada — 2026-10-01

### Distribución Base
- `PDF Master.spec` para PyInstaller con soporte de assets, íconos y dependencias.
- `build.bat` para automatizar la compilación.
- Íconos multi-resolución en `assets/icon.ico` y `assets/icon.png`.

---

## 📦 FASE 6 — Instalador, versiones y actualizaciones
**Estado:** ✅ Completada — 2026-11-04

### Componentes Implementados
- **Fuente única de versión:** `version.py` (`__version__ = "1.0.0"`).
- **Almacenamiento desacoplado:** Configuración en `%APPDATA%\PDF Master\config.json` independiente del ejecutable.
- **Instalador Inno Setup:** Generación mediante `create_installer.py` y compilación con `ISCC.exe`.
  - Instalación de usuario en `%LOCALAPPDATA%\Programs\PDF Master` (sin privilegios administrativos).
  - Menú contextual registrado automáticamente durante la instalación.
- **Sistema de Actualización Inteligente (`utils/updater.py`):**
  - Consulta automática contra GitHub Releases (`/releases/latest`).
  - Detección de versión con comparación SemVer estricta.
  - Descargador en segundo plano con notificación flotante y diálogo de progreso.
  - **Mecanismo de actualización sobre instalación existente:**
    - `AppId` fijo para actualizar la versión existente sin duplicar rutas.
    - Argumento `/CLOSEAPPLICATIONS` y directiva `CloseApplications=force` para evitar bloqueo de archivos en uso.
    - Persistencia de configuraciones en `%APPDATA%` (nunca se sobreescriben).

---

## 🟣 FASE 7 — Pulido visual y experiencia de usuario
**Estado:** ✅ Completada — 2026-11-04

### Mejoras de UX / UI
- **Transiciones fluidas:** Efecto de fundido (fade) y desplazamiento lateral suave al cambiar de panel (`MainWindow._animate_in()`).
- **Notificaciones Toast (`ui/components/toast.py`):** Avisos tipo toast en la esquina inferior derecha con acciones directas ("Ver PDF", "Abrir carpeta").
- **Visor Integrado (`ui/components/preview_dialog.py`):** Previsualización inmediata del PDF resultante.
- **Manejo de Instancia Única (`utils/single_instance.py`):** Control por Mutex de Windows y sockets locales (`QLocalServer`/`QLocalSocket`) para recibir multiselecciones del Explorador en la misma ventana abierta.
