# this is the final , the image does not work properly
import fitz
import pytesseract
from PIL import Image
import re
import shutil
import os

# -------------------------------------------------
# CONFIG
# -------------------------------------------------

OCR_DPI = 300

# Explicit path (Windows-safe)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

OCR_AVAILABLE = shutil.which("tesseract") is not None


# -------------------------------------------------
# BASIC CLEAN (LOSSLESS)
# -------------------------------------------------
def clean_line(text):
    # Minimal cleanup only
    return re.sub(r"[ \t]+", " ", text).strip()


# -------------------------------------------------
# OCR PAGE (RAW)
# -------------------------------------------------
def ocr_page(page):
    if not OCR_AVAILABLE:
        return []

    pix = page.get_pixmap(dpi=OCR_DPI)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    text = pytesseract.image_to_string(img)

    return [clean_line(l) for l in text.split("\n") if clean_line(l)]


# -------------------------------------------------
# RAW EXTRACTION (TEXT + OCR)
# -------------------------------------------------
def extract_raw_content(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []

    for page_no, page in enumerate(doc, start=1):
        page_lines = []

        # Normal text extraction
        text = page.get_text("text")
        for line in text.split("\n"):
            line = clean_line(line)
            if line:
                page_lines.append(line)

        # OCR fallback (ONLY if needed)
        if OCR_AVAILABLE and (len(page_lines) < 10 or page.get_images()):
            ocr_lines = ocr_page(page)

            # Append OCR lines without deduping aggressively
            for l in ocr_lines:
                if l not in page_lines:
                    page_lines.append(l)

        pages.append({"page": page_no, "lines": page_lines})

    return pages


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main():
    print("\n📄 Extracting RAW PDF content (LLM-ready)...")
    print(f"🔍 OCR enabled: {OCR_AVAILABLE}\n")
    PDF_PATH = r"C:\Users\techt\Downloads\ilovepdf_merged.pdf"
    pages = extract_raw_content(PDF_PATH)

    for page in pages:
        print(f"\n================ PAGE {page['page']} =================\n")
        for line in page["lines"]:
            print(line)

    print("\n✅ RAW extraction completed (no stitching, no interpretation).")


if __name__ == "__main__":
    main()
