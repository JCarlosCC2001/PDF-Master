"""
tools/img_to_pdf.py
Convierte una lista de imagenes a un unico archivo PDF.
Soporta: color original, escala de grises, blanco y negro.
Soporta tamanios: A4, Letter, Legal, A3, A5.
"""
import os
import tempfile
from PIL import Image
import pymupdf as fitz  # PyMuPDF


# Tamanios en puntos (pt): 1pt = 1/72 pulgada
PAGE_SIZES_PT = {
    "A4":     (595, 842),
    "Letter": (612, 792),
    "Legal":  (612, 1008),
    "A3":     (842, 1190),
    "A5":     (420, 595),
}

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}


def convert_images_to_pdf(
    image_paths: list[str],
    output_path: str,
    page_size: str = "A4",
    orientation: str = "portrait",
    color_mode: str = "original",
    quality: int = 85,
    progress_cb=None,
) -> str:
    """
    Convierte una lista de imagenes a un PDF.

    Args:
        image_paths:  Rutas absolutas de las imagenes (en orden).
        output_path:  Ruta del PDF de salida.
        page_size:    A4 | Letter | Legal | A3 | A5
        orientation:  portrait | landscape
        color_mode:   original | grayscale | blackwhite
        quality:      Calidad JPEG 1-100 para la compresion interna.
        progress_cb:  Funcion opcional progress_cb(porcentaje: int).

    Returns:
        output_path si la conversion fue exitosa.

    Raises:
        ValueError si no hay imagenes validas.
        Exception en caso de error de conversion.
    """
    if not image_paths:
        raise ValueError("No se proporcionaron imagenes para convertir.")

    w, h = PAGE_SIZES_PT.get(page_size, PAGE_SIZES_PT["A4"])
    if orientation == "landscape":
        w, h = h, w

    doc = fitz.open()
    total = len(image_paths)
    tmp_files: list[str] = []

    try:
        for i, img_path in enumerate(image_paths):
            ext = os.path.splitext(img_path)[1].lower()
            if ext not in SUPPORTED_EXTENSIONS:
                continue

            pil_img = Image.open(img_path)

            # Normalizar modo
            if pil_img.mode in ("RGBA", "P", "LA"):
                pil_img = pil_img.convert("RGB")
            elif pil_img.mode == "L":
                if color_mode == "original":
                    pil_img = pil_img.convert("RGB")

            # Aplicar modo de color
            if color_mode == "grayscale":
                pil_img = pil_img.convert("L").convert("RGB")
            elif color_mode == "blackwhite":
                pil_img = pil_img.convert("1").convert("RGB")

            # Guardar imagen procesada en temporal
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                tmp_path = tmp.name
                tmp_files.append(tmp_path)
                pil_img.save(tmp_path, "JPEG", quality=quality, optimize=True)

            # Crear pagina e insertar imagen escalada al tamanio de hoja
            page = doc.new_page(width=w, height=h)
            img_rect = fitz.Rect(0, 0, w, h)
            page.insert_image(img_rect, filename=tmp_path)

            if progress_cb:
                progress_cb(int((i + 1) / total * 100))

        if doc.page_count == 0:
            raise ValueError("No se encontraron imagenes validas en la lista.")

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        doc.save(output_path, garbage=4, deflate=True)

    finally:
        doc.close()
        for tmp_path in tmp_files:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    return output_path


def suggest_output_name(first_image_path: str) -> str:
    """Sugiere un nombre de archivo PDF basado en la primera imagen."""
    base = os.path.splitext(os.path.basename(first_image_path))[0]
    folder = os.path.dirname(first_image_path)
    return os.path.join(folder, f"{base}_convertido.pdf")
