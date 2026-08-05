import fitz
import pytesseract
from PIL import Image
import io

# Set Tesseract path (default winget install location)
tesseract_paths = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\Somya\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
]

for p in tesseract_paths:
    import os
    if os.path.exists(p):
        pytesseract.pytesseract.tesseract_cmd = p
        print(f"Found Tesseract at: {p}")
        break
else:
    # Try system PATH
    print("Trying Tesseract from system PATH...")

# Verify tesseract works
try:
    version = pytesseract.get_tesseract_version()
    print(f"Tesseract version: {version}")
except Exception as e:
    print(f"Tesseract not found: {e}")
    exit(1)

pdf_path = r"c:\Users\Somya\Downloads\DocYork\backend\data\raw\siemens_sinumerk_manual_260723_125157.pdf"
doc = fitz.open(pdf_path)
print(f"Total pages: {len(doc)}")

for page_idx in [2, 4, 9]:
    print(f"\n{'='*60}")
    print(f"PAGE {page_idx + 1}")
    print(f"{'='*60}")
    page = doc[page_idx]
    pix = page.get_pixmap(dpi=200)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    
    text = pytesseract.image_to_string(img, lang="eng")
    print(f"Extracted {len(text)} chars:")
    print(text[:600])

doc.close()
print("\nDone!")
