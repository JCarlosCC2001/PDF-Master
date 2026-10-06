"""
tools/pdf_to_img.py
Extrae paginas de un PDF como imagenes individuales.
Soporta: JPG, PNG, TIFF. DPI ajustable. Color original o grises.
"""
import os
import pymupdf as fitz  # PyMuPDF


SUPPORTED_FORMATS = {"PNG", "JPG", "TIFF"}

DPI_OPTIONS = [72, 96, 150, 200, 300, 600]


def convert_pdf_to_images(
    pdf_path: str,
    output_dir: str,
    dpi: int = 150,
    image_format: str = "PNG",
    color_mode: str = "original",
    pages: list[int] | None = None,
    progress_cb=None,
) -> list[str]:
    """
    Extrae paginas de un PDF y las guarda como imagenes.

    Args:
        pdf_path:     Ruta al archivo PDF.
        output_dir:   Directorio donde se guardan las imagenes.
        dpi:          Resolucion de salida (72, 96, 150, 200, 300, 600).
        image_format: PNG | JPG | TIFF
        color_mode:   original | grayscale
        pages:        Lista de indices de pagina (0-based). None = todas.
        progress_cb:  Funcion opcional progress_cb(porcentaje: int).

    Returns:
        Lista de rutas absolutas de las imagenes generadas.
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"No se encontro el archivo: {pdf_path}")

    image_format = image_format.upper()
    if image_format not in SUPPORTED_FORMATS:
        image_format = "PNG"

    ext_map = {"PNG": "png", "JPG": "jpg", "TIFF": "tiff"}
    ext = ext_map[image_format]

    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    total_pages = doc.page_count

    if pages is None:
        page_indices = list(range(total_pages))
    else:
        page_indices = [p for p in pages if 0 <= p < total_pages]

    total = len(page_indices)
    output_paths: list[str] = []
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]

    # Matriz de escala segun DPI (base 72dpi)
    scale = dpi / 72.0
    matrix = fitz.Matrix(scale, scale)

    # Colorspace segun modo
    colorspace = fitz.csGRAY if color_mode == "grayscale" else fitz.csRGB

    try:
        for i, page_idx in enumerate(page_indices):
            page = doc[page_idx]
            pix = page.get_pixmap(matrix=matrix, colorspace=colorspace, alpha=False)

            page_num_str = str(page_idx + 1).zfill(len(str(total_pages)))
            out_name = f"{base_name}_pagina_{page_num_str}.{ext}"
            out_path = os.path.join(output_dir, out_name)

            if image_format == "JPG":
                pix.save(out_path, output="jpeg")
            elif image_format == "TIFF":
                pix.save(out_path, output="tiff")
            else:
                pix.save(out_path)

            output_paths.append(out_path)

            if progress_cb:
                progress_cb(int((i + 1) / total * 100))

    finally:
        doc.close()

    return output_paths


def get_pdf_info(pdf_path: str) -> dict:
    """
    Retorna informacion basica de un PDF.
    Returns: {pages, title, file_size_mb}
    """
    doc = fitz.open(pdf_path)
    info = {
        "pages": doc.page_count,
        "title": doc.metadata.get("title", "") or os.path.basename(pdf_path),
        "file_size_mb": round(os.path.getsize(pdf_path) / (1024 * 1024), 2),
    }
    doc.close()
    return info


def suggest_output_dir(pdf_path: str) -> str:
    """Sugiere carpeta de salida junto al PDF original."""
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    folder = os.path.dirname(pdf_path)
    return os.path.join(folder, f"{base}_imagenes")
