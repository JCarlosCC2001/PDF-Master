# 📁 PDF Master — Contexto y Seguimiento del Proyecto

**Última actualización:** 2026-10-01  
**Versión actual:** 0.5.0 (Fases 1–5 completadas)

> **⚠️ REGLA ESTRICTA PARA EL AGENTE:**  
> Siempre que se aplique un cambio significativo en el proyecto, o se discuta un nuevo plan/fase, **DEBES guardar y actualizar** este archivo (`PROJECT_CONTEXT.md`) y el archivo `PLAN_DE_ACCION.md` sin que el usuario te lo tenga que pedir explícitamente. Esto asegura que el proyecto se pueda continuar en otra PC.

---

## 🧱 Stack Tecnológico

| Componente | Tecnología | Versión mínima |
|---|---|---|
| Lenguaje | Python | 3.10+ |
| Interfaz gráfica | PyQt6 | 6.6+ |
| Motor PDF | PyMuPDF (pymupdf) | 1.23+ |
| Reparación PDF | pikepdf | 8.0+ |
| Imágenes | Pillow | 10.0+ |
| Empaquetado | PyInstaller | 6.0+ |

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
├── main.py
├── requirements.txt
├── README.md                    ✅ Fase 5
├── PROJECT_CONTEXT.md
├── PLAN_DE_ACCION.md
├── install_context_menu.py      ✅ Fase 4
├── uninstall_context_menu.py    ✅ Fase 4
├── build.bat                    ✅ Fase 5
├── PDF Master.spec              ✅ Fase 5
├── config.json
├── assets/
│   ├── icon.ico                 ✅ Fase 5
│   └── icon.png                 ✅ Fase 5
├── tools/
│   ├── img_to_pdf.py        ✅ Fase 2
│   ├── pdf_to_img.py        ✅ Fase 2
│   ├── merge_pdf.py         ✅ Fase 2
│   ├── reorder_pdf.py       ✅ Fase 3
│   ├── repair_pdf.py        ✅ Fase 3
│   └── edit_pdf.py          ✅ Fase 3
├── ui/
│   ├── main_window.py       ✅ Fase 1+4
│   ├── components/
│   │   ├── sidebar.py       ✅ Fase 1
│   │   ├── card_button.py   ✅ Fase 1
│   │   ├── drop_zone.py     ✅ Fase 1
│   │   └── file_list.py     ✅ Fase 2
│   └── panels/
│       ├── home_panel.py        ✅ Fase 1
│       ├── settings_panel.py    ✅ Fase 1
│       ├── placeholder_panel.py ✅ Fase 1
│       ├── img_to_pdf_panel.py  ✅ Fase 2
│       ├── pdf_to_img_panel.py  ✅ Fase 2
│       ├── merge_panel.py       ✅ Fase 2
│       ├── reorder_panel.py     ✅ Fase 3
│       ├── repair_panel.py      ✅ Fase 3
│       └── edit_panel.py        ✅ Fase 3
├── utils/
│   └── config_manager.py    ✅ Fase 1
└── dist/
    └── PDF Master/          ✅ Fase 5 (build output)
        └── PDF Master.exe
```

---

## 🗂️ Fases del Proyecto

### ✅ FASE 1 — Fundamentos y estructura (COMPLETADA)
- [x] Estructura de carpetas creada
- [x] requirements.txt generado
- [x] Entorno virtual configurado (venv)
- [x] utils/config_manager.py — gestión de config.json
- [x] ui/components/sidebar.py — navegación lateral
- [x] ui/components/card_button.py — tarjetas del dashboard
- [x] ui/components/drop_zone.py — zona de arrastre de archivos
- [x] ui/panels/home_panel.py — grid responsive de herramientas
- [x] ui/panels/settings_panel.py — panel de configuración global
- [x] ui/panels/placeholder_panel.py — placeholder para fases futuras
- [x] ui/main_window.py — ventana principal con QStackedWidget
- [x] main.py — punto de entrada

**Estado:** ✅ Completada — 2026-09-30  
**Correcciones aplicadas:** QPalette para fondos (bug transparent PyQt6), fuentes Segoe UI explícitas, grid 1-2 columnas responsive.

---

### ✅ FASE 2 — Herramientas core Parte I (COMPLETADA)
- [x] tools/img_to_pdf.py — conversión imágenes→PDF (PIL + PyMuPDF, tamaño, orientación, color, calidad)
- [x] tools/pdf_to_img.py — extracción PDF→imágenes (DPI, PNG/JPG/TIFF, grayscale)
- [x] tools/merge_pdf.py — fusión de PDFs (orden configurable)
- [x] ui/components/file_list.py — lista de archivos con subir/bajar/quitar
- [x] ui/panels/img_to_pdf_panel.py — drop zone + opciones + progreso + QThread
- [x] ui/panels/pdf_to_img_panel.py — drop zone + DPI + formato + QThread
- [x] ui/panels/merge_panel.py — drop zone múltiple + reordenamiento + resumen páginas

**Estado:** ✅ Completada — 2026-09-30  
**Patrón implementado:** Conversión siempre en QThread separado. Barra de progreso en tiempo real. Notificación al terminar.

---

### ✅ FASE 3 — Herramientas core Parte II (COMPLETADA)
- [x] tools/reorder_pdf.py — miniaturas por página, reordenar, rotar, eliminar
- [x] tools/repair_pdf.py — reparación doble (pikepdf primero, PyMuPDF fallback, soporte contraseña)
- [x] tools/edit_pdf.py — marca de agua diagonal, texto superpuesto XY, insertar páginas en blanco
- [x] ui/panels/reorder_panel.py — miniaturas cargadas en QThread, controles ↑↓ rotar eliminar por tarjeta
- [x] ui/panels/repair_panel.py — informe con código de color (verde=éxito, rojo=error)
- [x] ui/panels/edit_panel.py — 3 modos con QStackedWidget (marca de agua / texto / página en blanco)

**Estado:** ✅ Completada — 2026-09-30

---

### ✅ FASE 4 — Menú contextual Windows (COMPLETADA)
- [x] install_context_menu.py — agrega opción al clic derecho en archivos PDF/imagen
- [x] uninstall_context_menu.py — elimina las entradas del registro
- [x] Soporte extensiones: .pdf .jpg .jpeg .png .bmp .tiff .webp
- [x] Pasa la ruta del archivo y `--tool <id>` como argumento a main.py
- [x] main.py detecta argumentos `--tool` y `<filepath>` y los pasa a MainWindow
- [x] MainWindow._handle_file_argument() navega al panel correcto y llama `panel.load_file()` si existe
- [x] Auto-elevación UAC (ShellExecuteW runas) en ambos scripts

**Estado:** ✅ Completada — 2026-10-01  
**Submenú PDF:** Abrir · Convertir a Imágenes · Unir con... · Reordenar páginas · Reparar PDF  
**Submenú Imágenes:** Abrir · Convertir a PDF  
**Dependencias:** Fase 3 completada ✅

---

### ✅ FASE 5 — Empaquetado y distribución (COMPLETADA)
- [x] `PDF Master.spec` — configuración de PyInstaller (modo carpeta, sin consola, con ícono)
- [x] `build.bat` — compila con un doble clic, limpia builds anteriores, abre el resultado
- [x] `assets/icon.ico` — icono de la aplicación (16×16 a 256×256, multi-tamaño)
- [x] `assets/icon.png` — icono PNG 256×256
- [x] `README.md` — documentación completa: instalación, uso, compilación, menú contextual, config
- [x] `dist/PDF Master/PDF Master.exe` — ejecutable generado

**Estado:** ✅ Completada — 2026-10-01  
**Modo de build:** carpeta distribuible (`--onedir`) con UPX activado  
**Sin instalador NSIS** (opcional, se puede agregar como extensión futura)  
**Dependencias:** Fases 1-4 completadas ✅

---

## 📝 Decisiones de Diseño

| Decisión | Razón |
|---|---|
| PyQt6 sobre Tkinter | Widgets nativos, drag & drop, mejor rendimiento |
| PyMuPDF sobre pypdf | Más rápido en renderizado y thumbnails |
| QStackedWidget para paneles | Sin parpadeo al cambiar herramienta |
| QPalette en vez de stylesheet para BG | Bug: transparent en PyQt6 renderea blanco |
| QThread para todas las conversiones | Evita que la UI se congele durante procesos largos |
| pikepdf como primer intento de reparación | Más tolerante con PDFs corruptos que PyMuPDF |
| config.json local | Fácil de editar manualmente |

---

## 🐛 Problemas Conocidos / Notas

- **Bug resuelto:** `background: transparent` en `QPushButton`/`QWidget` dentro de PyQt6 en Windows puede renderizarse blanco en vez del color del padre. Solución: `setAutoFillBackground(True)` + `QPalette`.
- **Warning resuelto:** `import fitz` → deprecado, reemplazado por `import pymupdf as fitz` en todos los tools.
