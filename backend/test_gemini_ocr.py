"""Quick test: Extract text from page 3 of Siemens PDF using Gemini Vision OCR."""
import fitz
import io
import PIL.Image
import google.generativeai as genai
import sys
sys.path.insert(0, r"c:\Users\Somya\Downloads\DocYork\backend")
from app.config import GEMINI_API_KEY

print(f"Gemini API Key present: {bool(GEMINI_API_KEY)}")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

pdf_path = r"c:\Users\Somya\Downloads\DocYork\backend\data\raw\siemens_sinumerk_manual_260723_125157.pdf"
doc = fitz.open(pdf_path)
print(f"Total pages: {len(doc)}")

# Test pages 3, 5, 10 (likely content pages)
for page_idx in [2, 4, 9]:
    print(f"\n{'='*60}")
    print(f"PAGE {page_idx + 1}")
    print(f"{'='*60}")
    
    page = doc[page_idx]
    pix = page.get_pixmap(dpi=150)
    img_bytes = pix.tobytes("png")
    img = PIL.Image.open(io.BytesIO(img_bytes))
    
    try:
        response = model.generate_content([
            "Extract ALL text from this document page exactly as written. "
            "Preserve paragraphs and line breaks. Output ONLY the extracted text, nothing else. "
            "If the page has tables, format them with | separators.",
            img
        ])
        text = response.text.strip()
        print(f"Extracted {len(text)} chars:")
        print(text[:500])
    except Exception as e:
        print(f"Error: {e}")

doc.close()
print("\nDone!")
