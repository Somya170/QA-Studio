import fitz
import easyocr
import numpy as np
from PIL import Image
import io

print("Initializing EasyOCR (first run downloads ~100MB model)...")
reader = easyocr.Reader(["en"], gpu=False, verbose=False)
print("EasyOCR ready!")

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
    img_np = np.array(img)
    results = reader.readtext(img_np, detail=0, paragraph=True)
    text = "\n".join(results)
    print(f"Extracted {len(text)} chars:")
    print(text[:500])

doc.close()
print("\nDone!")
