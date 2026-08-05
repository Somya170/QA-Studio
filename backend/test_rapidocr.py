import fitz
import numpy as np
from PIL import Image
import io
from rapidocr_onnxruntime import RapidOCR

print("Initializing RapidOCR...")
ocr = RapidOCR()
print("RapidOCR ready!")

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
    
    result, elapse = ocr(img_np)
    if result:
        lines = [line[1] for line in result]
        text = "\n".join(lines)
        print(f"Extracted {len(text)} chars in {elapse:.1f}s:")
        print(text[:600])
    else:
        print("No text extracted")

doc.close()
print("\nDone!")
