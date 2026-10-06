"""
tools/reorder_pdf.py
Reordena, rota y elimina paginas de un PDF.
"""
import os
import pymupdf as fitz


def get_page_thumbnails(pdf_path: str, thumb_width: int = 110) -> list[bytes]:
    """
    Renderiza una miniatura PNG por pagina del PDF.
    Returns: lista de bytes PNG en orden de paginas.
    """
    doc = fitz.open(pdf_path)
    thumbs: list[bytes] = []
    for page in doc:
        # Escala para que el ancho sea thumb_width px
        scale = thumb_width / page.rect.width
        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        thumbs.append(pix.tobytes("png"))
    doc.close()
    return thumbs


def reorder_and_save(
    pdf_path: str,
    output_path: str,
    page_order: list[int],
    rotations: dict[int, int] | None = None,
    progress_cb=None,
) -> str:
    """
    Guarda un nuevo PDF con el orden y rotaciones indicados.

    Args:
        pdf_path:    PDF original.
        output_path: PDF de salida.
        page_order:  Lista de indices originales en el nuevo orden deseado.
                     Ej: [2, 0, 1] -> pagina 3, luego 1, luego 2.
        rotations:   Diccionario {indice_original: grados} para rotar.
                     Grados validos: 0, 90, 180, 270.
        progress_cb: Funcion opcional progress_cb(porcentaje: int).
    """
    if not page_order:
        raise ValueError("El orden de paginas esta vacio.")

    rotations = rotations or {}
    doc = fitz.open(pdf_path)
    total = len(page_order)

    # Crear nuevo PDF con el orden indicado
    new_doc = fitz.open()
    for i, orig_idx in enumerate(page_order):
        new_doc.insert_pdf(doc, from_page=orig_idx, to_page=orig_idx)
        # Aplicar rotacion si corresponde
        rot = rotations.get(orig_idx, 0)
        if rot:
            new_doc[-1].set_rotation(rot % 360)
        if progress_cb:
            progress_cb(int((i + 1) / total * 100))

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    new_doc.save(output_path, garbage=4, deflate=True)
    new_doc.close()
    doc.close()
    return output_path


def get_page_count(pdf_path: str) -> int:
    try:
        doc = fitz.open(pdf_path)
        n = doc.page_count
        doc.close()
        return n
    except Exception:
        return 0


def suggest_output_name(pdf_path: str) -> str:
    base = os.path.splitext(pdf_path)[0]
    return f"{base}_reordenado.pdf"
