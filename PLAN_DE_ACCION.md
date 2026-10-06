# 📋 Plan de Acción — PDF Master

> **Stack tecnológico:** Python + PyQt6 (interfaz), PyMuPDF / Pillow / img2pdf / pikepdf (procesamiento PDF)
> **Plataforma:** Windows
> **Paleta:** Rojo `#D62828` · Blanco `#FAFAFA` · Negro `#1A1A1A`
> **Última actualización:** 2026-10-01 — v0.5.0 (todas las fases completadas)

---

## 🗂️ Resumen de Fases

| Fase | Nombre | Estado |
|------|--------|--------|
| 1 | Fundamentos y estructura | ✅ Completada |
| 2 | Herramientas core (I) — Img→PDF, PDF→Img, Unir | ✅ Completada |
| 3 | Herramientas core (II) — Reordenar, Reparar, Editar | ✅ Completada |
| 4 | Menú contextual de Windows (clic derecho) | ✅ Completada |
| 5 | Empaquetado y distribución (.exe, ícono, README) | ✅ Completada |

---

## 🔵 FASE 1 — Fundamentos y estructura del proyecto
**Duración estimada:** 1 sesión

### Objetivos
- Crear la estructura de carpetas del proyecto
- Configurar el entorno virtual con todas las dependencias
- Construir la ventana principal con la paleta rojo/blanco/negro
- Diseñar la navegación entre herramientas (sidebar o tarjetas)

### Entregables
- `main.py` — punto de entrada
- `ui/main_window.py` — ventana principal con diseño visual
- `ui/components/` — componentes reutilizables (botones, tarjetas, header)
- `requirements.txt` — dependencias del proyecto
- `assets/` — íconos SVG para cada herramienta

---

## 🟡 FASE 2 — Herramientas core (Parte I)
**Duración estimada:** 1-2 sesiones

### 2A · Imágenes → PDF
- Arrastrar y soltar imágenes (JPG, PNG, BMP, TIFF, WEBP)
- Ordenar imágenes antes de convertir
- Selección de tamaño de hoja (A4, Carta, Legal, personalizado)
- Opción: color original vs. blanco y negro

### 2B · PDF → Imágenes
- Seleccionar PDF de entrada
- Elegir páginas específicas o todas
- Formato de salida: JPG, PNG, TIFF
- DPI ajustable (72, 150, 300, 600)
- Opción: color original vs. blanco y negro

### 2C · Unir PDF
- Arrastrar múltiples PDFs
- Reordenar antes de unir
- Vista previa de la primera página de cada archivo

---

## 🟠 FASE 3 — Herramientas core (Parte II)
**Duración estimada:** 1-2 sesiones

### 3A · Reordenar PDF
- Miniaturas de todas las páginas
- Drag & drop para reordenar páginas
- Eliminar páginas individuales
- Rotar páginas (90°, 180°, 270°)

### 3B · Reparar PDF
- Detectar PDFs corruptos o protegidos
- Intentar recuperar contenido con pikepdf
- Eliminar contraseñas (si son conocidas)
- Informe del resultado de la reparación

### 3C · Editar PDF (básico)
- Añadir texto sobre páginas existentes
- Insertar marcas de agua (texto o imagen)
- Recortar páginas (crop)
- Añadir/eliminar páginas en blanco

---

## 🟢 FASE 4 — Opciones globales y configuración
**Duración estimada:** 1 sesión

### Configuración global (persiste entre sesiones)
- **Modo de color:** Original · Escala de grises · Blanco y negro puro
- **Tamaño de hoja:** A4, Carta (Letter), Legal, A3, A5, Personalizado
- **Orientación:** Portrait / Landscape
- **Calidad de imagen:** Baja / Media / Alta / Máxima
- **Carpeta de salida predeterminada**
- **Idioma:** Español / Inglés

### Implementación
- Panel de `Configuración` accesible desde la barra lateral
- Guardar preferencias en `config.json`
- `utils/config_manager.py` — clase de gestión de configuración
- Aplicar opciones globales a todas las herramientas automáticamente

---

## 🔴 FASE 5 — Integración con menú contextual de Windows
**Duración estimada:** 1 sesión

### Funcionalidad de anticlick (clic derecho)
Al hacer clic derecho sobre un archivo (PDF, imagen, Word, etc.) en el Explorador de Windows, aparecerá un submenú:

```
📄 PDF Master
  ├─ Convertir a PDF
  ├─ Convertir a Imágenes
  ├─ Unir con...
  ├─ Reparar PDF
  └─ Abrir en PDF Master
```

### Implementación técnica
- Script `install_context_menu.py` que escribe en el Registro de Windows (`winreg`)
- Soporte para extensiones: `.pdf`, `.jpg`, `.png`, `.bmp`, `.tiff`, `.webp`
- La aplicación recibe el archivo como argumento (`sys.argv[1]`)
- La ventana se abre directamente en la herramienta correcta según el tipo de archivo

---

## 🟣 FASE 6 — Pulido, empaquetado y distribución
**Duración estimada:** 1-2 sesiones

### Pulido visual
- Animaciones de transición entre paneles
- Barra de progreso con porcentaje durante conversiones
- Notificaciones emergentes (toast) al finalizar una tarea
- Vista previa de archivos dentro de la app

### Empaquetado
- Usar **PyInstaller** para generar un `.exe` portable
- Incluir todos los assets e íconos en el ejecutable
- Generar un instalador con **Inno Setup** (opcional)

### Distribución
- `build.bat` — script de compilación con un clic
- `README.md` completo
- Versión portable (carpeta) + versión instalable (`.exe`)
