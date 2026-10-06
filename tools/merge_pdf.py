"""
tools/merge_pdf.py
Une multiples archivos PDF en uno solo usando PyMuPDF.
"""
import os
import pymupdf as fitz  # PyMuPDF


def merge_pdfs(
    pdf_paths: list[str],
    output_path: str,
    progress_cb=None,
) -> str:
    """
    Une los PDFs en el orden dado y guarda el resultado.

    Args:
        pdf_paths:   Lista ordenada de rutas de PDFs a unir.
        output_path: Ruta del PDF de salida.
        progress_cb: Funcion opcional progress_cb(porcentaje: int).

    Returns:
        output_path si fue exitoso.

    Raises:
        ValueError si la lista esta vacia o tiene menos de 2 PDFs.
        FileNotFoundError si algun PDF no existe.
    """
    if len(pdf_paths) < 2:
        raise ValueError("Se necesitan al menos 2 archivos PDF para unir.")

    for path in pdf_paths:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"No se encontro: {path}")

    output_doc = fitz.open()
    total = len(pdf_paths)

    try:
        for i, pdf_path in enumerate(pdf_paths):
            src = fitz.open(pdf_path)
            output_doc.insert_pdf(src)
            src.close()
            if progress_cb:
                progress_cb(int((i + 1) / total * 100))

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        output_doc.save(output_path, garbage=4, deflate=True)

    finally:
        output_doc.close()

    return output_path


def get_pdf_page_count(pdf_path: str) -> int:
    """Retorna el numero de paginas de un PDF rapidamente."""
    try:
        doc = fitz.open(pdf_path)
        count = doc.page_count
        doc.close()
        return count
    except Exception:
        return 0


def suggest_output_name(first_pdf_path: str) -> str:
    """Sugiere un nombre de salida para el PDF unido."""
    folder = os.path.dirname(first_pdf_path)
    return os.path.join(folder, "documentos_unidos.pdf")
