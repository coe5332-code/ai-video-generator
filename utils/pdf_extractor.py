import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import re
import shutil
import os
import platform
import logging

# -------------------------------------------------
# DYNAMIC CONFIGURATION
# -------------------------------------------------

def get_tesseract_path():
    """
    Finds the Tesseract binary path dynamically based on the OS.
    """
    # 1. Check if it's already in the system PATH (Best for Linux/Cloud)
    path = shutil.which("tesseract")
    if path:
        return path

    # 2. Fallback for common Windows installation paths
    if platform.system() == "Windows":
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expanduser(r"~\AppData\Local\Tesseract-OCR\tesseract.exe")
        ]
        for p in common_paths:
            if os.path.exists(p):
                return p
    
    # 3. Fallback for Linux (Standard location)
    linux_path = "/usr/bin/tesseract"
    if os.path.exists(linux_path):
        return linux_path

    return None

# Initialize Pytesseract
TESSERACT_EXE = get_tesseract_path()
if TESSERACT_EXE:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE
    OCR_AVAILABLE = True
else:
    logging.warning("Tesseract OCR not found. OCR features will be disabled.")
    OCR_AVAILABLE = False

OCR_DPI = 200  # 200 is usually enough for text and faster than 300

# -------------------------------------------------
# HELPERS
# -------------------------------------------------

def clean_line(text):
    """Clean whitespace and junk characters."""
    if not text: return ""
    return re.sub(r"[ \t]+", " ", text).strip()

def ocr_page(page):
    """Convert PDF page to image and perform OCR."""
    if not OCR_AVAILABLE:
        return []

    try:
        # Higher DPI improves OCR accuracy for small text
        pix = page.get_pixmap(dpi=OCR_DPI)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Performance tip: Use 'eng' lang or specify others if needed
        text = pytesseract.image_to_string(img, lang='eng')
        return [clean_line(l) for l in text.split("\n") if clean_line(l)]
    except Exception as e:
        logging.error(f"OCR Error on page: {e}")
        return []

# -------------------------------------------------
# MAIN EXTRACTION
# -------------------------------------------------

def extract_raw_content(pdf_path):
    """
    Extracts text from PDF. Uses native text first, 
    falls back to OCR if the page looks like an image.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at {pdf_path}")

    doc = fitz.open(pdf_path)
    extracted_pages = []

    for page_no, page in enumerate(doc, start=1):
        page_lines = []

        # 1. Native Text Extraction (Vector text)
        text = page.get_text("text")
        for line in text.split("\n"):
            line = clean_line(line)
            if line:
                page_lines.append(line)

        # 2. OCR Fallback 
        # Trigger if: Very little text found OR page contains images/is scanned
        if OCR_AVAILABLE and (len(page_lines) < 5 or page.get_images()):
            ocr_lines = ocr_page(page)
            
            # Simple merge: add OCR lines if they aren't already captured
            for l in ocr_lines:
                if l not in page_lines:
                    page_lines.append(l)

        extracted_pages.append({"page": page_no, "lines": page_lines})

    doc.close()
    return extracted_pages

if __name__ == "__main__":
    # Test script (Update path for local testing)
    TEST_PDF = "test_sample.pdf"
    if os.path.exists(TEST_PDF):
        results = extract_raw_content(TEST_PDF)
        for p in results:
            print(f"--- Page {p['page']} ---")
            print("\n".join(p['lines'][:10])) # Print first 10 lines
