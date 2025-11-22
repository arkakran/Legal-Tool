import os
from typing import Tuple
from werkzeug.datastructures import FileStorage
from loguru import logger


def validate_pdf(file: FileStorage) -> Tuple[bool, str]:
    if not file:
        return False, "No file provided"

    if file.filename == "":
        return False, "No filename provided"

    filename = file.filename.lower().strip()

    # Allow multiple dots, but must end with .pdf
    if not filename.endswith(".pdf"):
        return False, "Invalid file type. Only PDF files are allowed"

    # Block disguised executables like file.pdf.exe
    # last extension must be pdf
    if filename.split(".")[-1] != "pdf":
        return False, "Invalid PDF file type"

    # MIME type check
    if hasattr(file, "mimetype") and file.mimetype not in [
        "application/pdf",
        "application/x-pdf"
    ]:
        return False, "Invalid MIME type. File does not appear to be a PDF"

    # Magic bytes check (robust)
    try:
        file.seek(0)
        header = file.read(1024)  # read more to handle BOM/metadata
        file.seek(0)

        # "%PDF" may not be first 4 bytes
        if b"%PDF" not in header:
            return False, "Invalid PDF file format (missing PDF header)"

    except Exception as e:
        logger.error(f"Error reading file header: {e}")
        return False, "Error validating file"

    return True, ""


def validate_file_size(file: FileStorage, max_size: int) -> Tuple[bool, str]:
    try:
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)

        if size > max_size:
            max_mb = max_size / (1024 * 1024)
            return False, f"File size exceeds {max_mb:.1f}MB limit"

        if size == 0:
            return False, "File is empty"

        return True, ""

    except Exception as e:
        logger.error(f"Error checking file size: {e}")
        return False, "Error validating file size"
