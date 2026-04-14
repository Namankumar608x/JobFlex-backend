import fitz  # PyMuPDF


def extract_text_from_pdf(file) -> str:
    """
    Extracts all text from a PDF file using PyMuPDF (fitz).

    PyMuPDF is more reliable than pdfplumber for:
    - Multi-column resumes
    - Resumes with tables
    - PDFs with embedded fonts

    file: Django InMemoryUploadedFile (from request.FILES)
    Returns: plain text string of the entire resume
    """
    # Read file bytes into memory — fitz works with bytes directly
    file_bytes = file.read()

    # Open PDF from bytes buffer
    pdf = fitz.open(stream=file_bytes, filetype="pdf")

    full_text = ""
    for page in pdf:
        # get_text("text") returns plain text preserving reading order
        full_text += page.get_text("text") + "\n"

    pdf.close()
    return full_text.strip()
