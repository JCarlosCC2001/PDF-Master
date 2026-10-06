"""
tools/repair_pdf.py
Intenta reparar archivos PDF danados o protegidos usando pikepdf.
"""
import os
import pikepdf
import pymupdf as fitz


def repair_pdf(
    pdf_path: str,
    output_path: str,
    password: str = "",
) -> dict:
    """
    Intenta abrir, limpiar y guardar el PDF.

    Returns dict con:
        success (bool)
        pages (int)
        message (str)
        issues (list[str])
        file_size_original_mb (float)
        file_size_repaired_mb (float)
    """
    issues: list[str] = []
    original_size = os.path.getsize(pdf_path) / (1024 * 1024)

    # -- Intento 1: pikepdf (muy tolerante con PDFs corruptos) --
    try:
        open_args = {"password": password} if password else {}
        pdf = pikepdf.open(pdf_path, allow_overwriting_input=False, **open_args)

        # Verificar paginas
        page_count = len(pdf.pages)
        if page_count == 0:
            issues.append("El PDF no tiene paginas detectadas.")

        # Limpiar y guardar
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        pdf.save(
            output_path,
            compress_streams=True,
            object_stream_mode=pikepdf.ObjectStreamMode.generate,
        )
        pdf.close()

        repaired_size = os.path.getsize(output_path) / (1024 * 1024)

        if not issues:
            issues.append("No se encontraron errores criticos.")

        return {
            "success": True,
            "pages": page_count,
            "message": (
                f"PDF procesado correctamente.\n"
                f"{page_count} paginas recuperadas.\n"
                f"Tamanio original: {original_size:.2f} MB → "
                f"Reparado: {repaired_size:.2f} MB"
            ),
            "issues": issues,
            "file_size_original_mb": original_size,
            "file_size_repaired_mb": repaired_size,
        }

    except pikepdf.PasswordError:
        return {
            "success": False,
            "pages": 0,
            "message": "El PDF esta protegido con contrasena.\nIngresa la contrasena correcta e intenta de nuevo.",
            "issues": ["Protegido con contrasena"],
            "file_size_original_mb": original_size,
            "file_size_repaired_mb": 0.0,
        }

    except Exception as e1:
        issues.append(f"pikepdf: {e1}")

        # -- Intento 2: PyMuPDF con recuperacion agresiva --
        try:
            doc = fitz.open(pdf_path)
            page_count = doc.page_count

            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            doc.save(
                output_path,
                garbage=4,
                deflate=True,
                clean=True,
            )
            doc.close()

            repaired_size = os.path.getsize(output_path) / (1024 * 1024)
            issues.append("Se uso recuperacion alternativa (PyMuPDF).")

            return {
                "success": True,
                "pages": page_count,
                "message": (
                    f"PDF recuperado con metodo alternativo.\n"
                    f"{page_count} paginas.\n"
                    f"Tamanio original: {original_size:.2f} MB → "
                    f"Reparado: {repaired_size:.2f} MB"
                ),
                "issues": issues,
                "file_size_original_mb": original_size,
                "file_size_repaired_mb": repaired_size,
            }

        except Exception as e2:
            issues.append(f"PyMuPDF: {e2}")
            return {
                "success": False,
                "pages": 0,
                "message": f"No se pudo reparar el PDF.\nEl archivo puede estar demasiado danado.",
                "issues": issues,
                "file_size_original_mb": original_size,
                "file_size_repaired_mb": 0.0,
            }


def suggest_output_name(pdf_path: str) -> str:
    base = os.path.splitext(pdf_path)[0]
    return f"{base}_reparado.pdf"
