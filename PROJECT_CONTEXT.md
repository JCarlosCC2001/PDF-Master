# 📁 PDF Master — Contexto y Seguimiento del Proyecto

**Última actualización:** 2026-11-04  
**Versión actual:** 1.0.0 (Fases 1–7 completadas y operativas)

> **⚠️ REGLA ESTRICTA PARA EL AGENTE:**  
> Siempre que se aplique un cambio significativo en el proyecto, o se discuta un nuevo plan/fase, **DEBES guardar y actualizar** este archivo (`PROJECT_CONTEXT.md`) y el archivo `PLAN_DE_ACCION.md` sin que el usuario te lo tenga que pedir explícitamente. Esto asegura que el proyecto se pueda continuar en otra PC.

---

## 🧱 Stack Tecnológico

| Componente | Tecnología | Versión instalada / mínima |
|---|---|---|
| Lenguaje | Python | 3.15.0 (64-bit) / 3.10+ |
| Interfaz gráfica | PyQt6 + PyQt6-Qt6 | 6.12.0 / 6.6+ |
| Motor PDF | PyMuPDF (pymupdf) | 1.28.2 / 1.23+ |
| Reparación PDF | pikepdf | 10.17.0 / 8.0+ |
| Imágenes | Pillow | 13.0.0 / 10.0+ |
| Conversión Imágenes | img2pdf | 0.6.3 / 0.4.4+ |
| Generación de documentos | reportlab | 5.1.0 / 4.0+ |
| Empaquetado | PyInstaller | 6.22.3 / 6.0+ |
| Compilador de Instalador | Inno Setup | 6.7.3 (ISCC.exe) |

---

## 🎨 Diseño Visual

| Elemento | Valor |
|---|---|
| Color primario (rojo) | #D62828 |
| Color de fondo claro | #F0F0F0 |
| Color oscuro / texto | #1A1A1A |
| Fondo sidebar | #1C1C1C |
| Gris texto secundario | #666666 |
| Fuente principal | Segoe UI (nativa Windows) |
| Sidebar ancho | 200px (fijo) |
| Radio de bordes | 8px |

**Layout:** Sidebar izquierdo oscuro (#1C1C1C) + Área principal gris (#F0F0F0)  
**Patrón de paneles:** Header fijo 66px + 2 columnas (zona de archivos 55–60% + opciones 40–45%)  
**Fondo garantizado:** `setAutoFillBackground(True)` + `QPalette` (evita bugs de transparent en PyQt6)

---

## 🗂️ Estructura de Archivos

```
PDF-Master/
├── main.py                          ✅ Punto de entrada + single instance handler
├── version.py                       ✅ Fuente única de versión (1.0.0)
├── requirements.txt                 ✅ Dependencias del proyecto
├── README.md                        ✅ Documentación + Registro de cambios
├── PROJECT_CONTEXT.md               ✅ Memoria viva del proyecto
├── PLAN_DE_ACCION.md                ✅ Plan de fases del proyecto
├── create_version_info.py           ✅ Genera version_info.txt para Windows EXE
├── create_installer.py              ✅ Genera installer.iss para Inno Setup
├── install_context_menu.py          ✅ Menú contextual Windows (HKCU/desarrollo)
├── uninstall_context_menu.py        ✅ Desinstalador de menú contextual
├── build.bat                        ✅ Compila PyInstaller + Inno Setup a 1-clic
├── PDF Master.spec                  ✅ Configuración de PyInstaller
├── config.json                      ✅ Configuración por defecto
├── assets/
│   ├── icon.ico                     ✅ Ícono multi-resolución Windows
│   └── icon.png                     ✅ Ícono PNG 256x256
├── tools/
│   ├── img_to_pdf.py                ✅ Imágenes -> PDF
│   ├── pdf_to_img.py                ✅ PDF -> Imágenes
│   ├── merge_pdf.py                 ✅ Fusión de PDFs
│   ├── reorder_pdf.py               ✅ Reordenar, rotar y eliminar páginas
│   ├── repair_pdf.py                ✅ Reparación doble pikepdf + pymupdf
│   └── edit_pdf.py                  ✅ Marca de agua, texto, páginas blanco
├── ui/
│   ├── main_window.py               ✅ Ventana principal, navegación, transiciones, updater
│   ├── components/
│   │   ├── sidebar.py               ✅ Barra lateral de navegación
│   │   ├── card_button.py           ✅ Tarjetas del dashboard
│   │   ├── drop_zone.py             ✅ Área Drag & Drop
│   │   ├── file_list.py             ✅ Lista de archivos con reordenamiento
│   │   ├── toast.py                 ✅ Notificaciones flotantes tipo Toast
│   │   └── preview_dialog.py        ✅ Visor integrado de PDF
│   └── panels/
│       ├── home_panel.py            ✅ Dashboard principal
│       ├── settings_panel.py        ✅ Configuración global + búsqueda actualizaciones
│       ├── placeholder_panel.py     ✅ Base para prototipos
│       ├── img_to_pdf_panel.py      ✅ Panel Imágenes -> PDF
│       ├── pdf_to_img_panel.py      ✅ Panel PDF -> Imágenes
│       ├── merge_panel.py           ✅ Panel Unir PDFs
│       ├── reorder_panel.py         ✅ Panel Reordenar páginas con miniaturas
│       ├── repair_panel.py          ✅ Panel Reparación y diagnóstico
│       └── edit_panel.py            ✅ Panel Edición básica
├── utils/
│   ├── config_manager.py            ✅ Guarda en %APPDATA%\PDF Master\config.json
│   ├── single_instance.py           ✅ Mutex Windows + QLocalServer/Socket multiselección
│   └── updater.py                   ✅ Buscador/descargador con GitHub Releases
├── installer/
│   └── Output/
│       └── PDF-Master-Setup-1.0.0.exe ✅ Instalador final generado
└── dist/
    └── PDF Master/                  ✅ Build desempaquetado de PyInstaller
        └── PDF Master.exe
```

---

## 🗂️ Fases del Proyecto

### ✅ FASES 1–5 — Core, Menú Contextual y Build Base (COMPLETADAS)
* Estructura base, componentes visuales y paneles 100% operativos.
* 6 herramientas core funcionando con procesos en `QThread` y barras de progreso.
* Integración con menú contextual de Windows en `HKCU\Software\Classes\SystemFileAssociations`.
* Empaquetado base con PyInstaller.

---

### ✅ FASE 6 — Instalador, Versiones y Actualizaciones (COMPLETADA)
* **Fuente única de versión:** [`version.py`](file:///d:/Desarrollo%20Software/PDF-Master/version.py) centraliza `__version__ = "1.0.0"`.
* **Configuración del usuario:** `%APPDATA%\PDF Master\config.json` garantiza persistencia fuera de la carpeta de instalación.
* **Instalador Inno Setup (`create_installer.py` + `ISCC.exe`):**
  * Instalación por usuario en `%LOCALAPPDATA%\Programs\PDF Master` (no requiere elevación UAC).
  * Menú contextual integrado en la instalación sin requerir scripts Python externos.
  * Opciones configurables: acceso directo en escritorio, menú contextual, iniciar al finalizar.
* **Sistema de Actualizaciones (`utils/updater.py`):**
  * Consulta periódica (1 vez al día) o manual desde Configuración contra GitHub Releases.
  * Si la API responde 404 (sin releases publicados aún), responde limpiamente indicando que se tiene la versión más reciente.
  * Descargador en segundo plano con `DownloadWorker` y barra de progreso.

---

### ✅ FASE 7 — Pulido Visual y Usabilidad (COMPLETADA)
* **Animaciones de transición:** Transiciones suaves de fundido y deslizamiento entre paneles en `MainWindow._animate_in()`.
* **Barras de progreso pulidas:** Formato porcentual visible (`%p%`) con gradiente rojo distintivo.
* **Notificaciones Toast (`ui/components/toast.py`):** Avisos no invasivos para finalización de tareas con botones de acción directa ("Ver PDF", "Abrir carpeta").
* **Visor de previsualización (`ui/components/preview_dialog.py`):** Permite revisar el resultado sin abrir visores externos.
* **Instancia Única Robusta (`utils/single_instance.py`):** Al seleccionar múltiples archivos en Windows Explorer, se utiliza un Mutex local y `QLocalServer`/`QLocalSocket` para despacharlos a la ventana abierta sin duplicar procesos.

---

## 🔄 ¿Cómo se actualiza el programa si ya está instalado?

1. **Detección de instalación previa (`AppId` fijo):**  
   El instalador tiene configurado un identificador único e inmutable:  
   `AppId={{8F3C2A71-5D4E-4B9A-9C61-2E7F0A1D4B35}`.  
   Cuando se ejecuta `PDF-Master-Setup-<nueva_version>.exe` en un equipo donde la aplicación ya existe, Inno Setup detecta la entrada de registro y opera en **modo actualización** (`UsePreviousAppDir=yes`), manteniendo el mismo directorio (`%LOCALAPPDATA%\Programs\PDF Master`) sin preguntar de nuevo al usuario.

2. **Cierre limpio de procesos en ejecución:**  
   Inno Setup cuenta con `CloseApplications=force`. Además, al pulsar "Descargar e instalar" desde la aplicación, esta ejecuta el instalador con el parámetro `/CLOSEAPPLICATIONS` e inmediatamente invoca `QApplication.quit()`. Esto previene errores de archivos DLL/EXE bloqueados.

3. **Preservación total de preferencias:**  
   Los datos del usuario se almacenan en `%APPDATA%\PDF Master\config.json`, ubicación desacoplada del directorio de la aplicación. Al actualizar, el instalador no toca `%APPDATA%`, por lo que las configuraciones de formato, DPI, idioma y carpeta de salida persisten intactas.

4. **Persistencia del Menú Contextual:**  
   Las rutas del menú contextual apuntan a `{app}\PDF Master.exe`. Dado que `{app}` permanece inalterado, todas las opciones del menú contextual continúan funcionando sin interrupción.

---

## 🛠️ Entorno y Comandos de Trabajo

* **Entorno virtual recreado:** Python 3.15.0 ubicado en:  
  `C:\Users\Gestión de Calidad\AppData\Local\Programs\Python\Python315\python.exe`
* **Compilación de Ejecutable e Instalador con un solo paso:**  
  Ejecutar `.\build.bat` en PowerShell o CMD. Este script:
  1. Verifica el entorno virtual y dependencias.
  2. Genera `version_info.txt`.
  3. Ejecuta PyInstaller con `PDF Master.spec`.
  4. Copia los archivos complementarios a `dist\PDF Master\`.
  5. Ejecuta `create_installer.py` para generar `installer.iss`.
  6. Compila el instalador con `ISCC.exe` dejando el archivo final en `installer\Output\PDF-Master-Setup-1.0.0.exe`.
