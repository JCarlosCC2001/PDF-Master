"""
tools/edit_pdf.py
Edicion basica de PDFs: texto superpuesto, marcas de agua, paginas en blanco.
"""
import os
import math
import pymupdf as fitz


# ── Marcas de agua de texto ───────────────────────────────────────────────────
def add_watermark_text(
    pdf_path: str,
    output_path: str,
    text: str,
    font_size: int = 48,
    opacity: float = 0.25,
    color: tuple[float, float, float] = (0.8, 0.0, 0.0),
    pages: list[int] | None = None,
    angle: float = 45.0,
    progress_cb=None,
) -> str:
    """
    Agrega una marca de agua de texto diagonal en las paginas indicadas.

    Args:
        text:    Texto de la marca de agua.
        opacity: 0.0 (invisible) a 1.0 (opaco). Default 0.25.
        color:   Tupla RGB normalizada (r, g, b) cada valor 0.0-1.0.
        pages:   Indices 0-based. None = todas las paginas.
        angle:   Angulo de rotacion del texto en grados.
    """
    doc = fitz.open(pdf_path)
    target_pages = pages if pages is not None else list(range(doc.page_count))
    total = len(target_pages)

    for i, p_idx in enumerate(target_pages):
        if 0 <= p_idx < doc.page_count:
            page = doc[p_idx]
            _draw_watermark_text(page, text, font_size, opacity, color, angle)
        if progress_cb:
            progress_cb(int((i + 1) / total * 100))

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    return output_path


def _draw_watermark_text(
    page,
    text: str,
    font_size: int,
    opacity: float,
    color: tuple,
    angle: float,
) -> None:
    """Dibuja el texto de marca de agua centrado y rotado en la pagina."""
    rect = page.rect
    cx, cy = rect.width / 2, rect.height / 2

    # Insertar como anotacion de sello para que sea transparente
    page.insert_text(
        fitz.Point(cx - len(text) * font_size * 0.3, cy),
        text,
        fontsize=font_size,
        color=color,
        rotate=int(angle),
        fill_opacity=opacity,
        overlay=True,
    )


# ── Texto superpuesto ─────────────────────────────────────────────────────────
def add_text_overlay(
    pdf_path: str,
    output_path: str,
    text: str,
    pages: list[int] | None = None,
    x_pt: float = 50,
    y_pt: float = 50,
    font_size: int = 12,
    color: tuple[float, float, float] = (0.0, 0.0, 0.0),
    progress_cb=None,
) -> str:
    """
    Agrega texto en una posicion fija de las paginas indicadas.

    Args:
        x_pt, y_pt: Posicion en puntos desde la esquina superior izquierda.
    """
    doc = fitz.open(pdf_path)
    target_pages = pages if pages is not None else list(range(doc.page_count))
    total = len(target_pages)

    for i, p_idx in enumerate(target_pages):
        if 0 <= p_idx < doc.page_count:
            page = doc[p_idx]
            page.insert_text(
                fitz.Point(x_pt, y_pt),
                text,
                fontsize=font_size,
                color=color,
                overlay=True,
            )
        if progress_cb:
            progress_cb(int((i + 1) / total * 100))

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    return output_path


# ── Insertar pagina en blanco ─────────────────────────────────────────────────
def insert_blank_pages(
    pdf_path: str,
    output_path: str,
    positions: list[int],
    page_size: str = "A4",
    progress_cb=None,
) -> str:
    """
    Inserta paginas en blanco en las posiciones indicadas (0-based, antes de esa pagina).
    Ej: position=0 inserta al inicio, position=N inserta al final.
    """
    PAGE_SIZES = {
        "A4":     (595, 842),
        "Letter": (612, 792),
        "Legal":  (612, 1008),
        "A3":     (842, 1190),
        "A5":     (420, 595),
    }
    w, h = PAGE_SIZES.get(page_size, PAGE_SIZES["A4"])

    doc = fitz.open(pdf_path)
    # Insertar en orden inverso para no desplazar indices
    for pos in sorted(set(positions), reverse=True):
        doc.new_page(pno=pos, width=w, height=h)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    if progress_cb:
        progress_cb(100)
    return output_path


def suggest_output_name(pdf_path: str, suffix: str = "editado") -> str:
    base = os.path.splitext(pdf_path)[0]
    return f"{base}_{suffix}.pdf"
