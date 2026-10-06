# PDF Master

Herramienta de escritorio todo-en-uno para trabajar con archivos PDF e imagenes en Windows.

---

## Caracteristicas

| Herramienta | Descripcion |
|---|---|
| **Imagenes a PDF** | Convierte JPG, PNG, BMP, TIFF, WEBP a un PDF de una o varias paginas |
| **PDF a Imagenes** | Extrae paginas de un PDF como imagenes (PNG, JPG, TIFF) a la resolucion elegida |
| **Unir PDFs** | Combina multiples archivos PDF en uno solo con orden personalizable |
| **Reordenar PDF** | Reordena, rota y elimina paginas con vista en miniatura |
| **Reparar PDF** | Intenta recuperar PDFs corruptos o protegidos por contrasena |
| **Editar PDF** | Aniade marcas de agua, texto superpuesto o paginas en blanco |

---

## Requisitos

- Windows 10 / 11 (64-bit)
- Python 3.10 o superior *(solo si ejecutas desde el codigo fuente)*

---

## Instalacion rapida (ejecutable)

1. Descarga la carpeta `PDF Master/` desde la seccion de releases.
2. Ejecuta `PDF Master.exe`.
3. *(Opcional)* Ejecuta `install_context_menu.py` como Administrador para habilitar el menu contextual.

---

## Instalacion desde el codigo fuente

```powershell
# 1. Clonar o descomprimir el proyecto
cd "PDF-Master"

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno
venv\Scripts\Activate.ps1

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar la aplicacion
python main.py
```

---

## Compilar el ejecutable

```bat
build.bat
```

El ejecutable se generara en `dist\PDF Master\PDF Master.exe`.

---

## Menu contextual de Windows

Para agregar PDF Master al menu contextual del Explorador de Windows:

```powershell
# Ejecutar como Administrador
python install_context_menu.py
```

Para eliminarlo:

```powershell
python uninstall_context_menu.py
```

### Formatos soportados en el menu contextual

| Extension | Opciones disponibles |
|---|---|
| `.pdf` | Abrir · Convertir a Imagenes · Unir con... · Reordenar paginas · Reparar PDF |
| `.jpg .png .bmp .tiff .webp` | Abrir · Convertir a PDF |

---

## Configuracion

Las preferencias se guardan en `config.json`:

| Clave | Descripcion | Valores |
|---|---|---|
| `color_mode` | Modo de color | `original`, `grayscale`, `bw` |
| `page_size` | Tamano de pagina | `A4`, `Letter`, `Legal`, `A3`, `A5`, `custom` |
| `orientation` | Orientacion | `portrait`, `landscape` |
| `image_quality` | Calidad JPEG (1-100) | `80` por defecto |
| `output_folder` | Carpeta de salida | ruta absoluta o `""` (misma carpeta) |
| `dpi` | Resolucion al exportar | `72`, `150`, `300`, `600` |
| `image_format` | Formato al exportar imagenes | `PNG`, `JPG`, `TIFF` |

---

## Stack tecnologico

| Componente | Tecnologia |
|---|---|
| Interfaz grafica | PyQt6 |
| Motor PDF | PyMuPDF (pymupdf) |
| Reparacion PDF | pikepdf |
| Imagenes | Pillow |
| Empaquetado | PyInstaller |

---

## Version

**0.4.0** — Fases 1-4 completadas
