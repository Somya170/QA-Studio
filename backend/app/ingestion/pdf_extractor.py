"""
Advanced PDF text extractor with multi-strategy fallback:
  1. PyMuPDF (fitz) text extraction - fast, for text-based PDFs
  2. Tesseract OCR via pytesseract - for scanned/image-based PDFs
  
Automatically detects if PDF is scanned and switches to OCR.
"""
import os
import io
from pathlib import Path
from typing import List, Dict, Callable, Optional

# Tesseract paths for Windows
TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\Somya\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
]

def _find_tesseract() -> Optional[str]:
    """Locate Tesseract binary on Windows."""
    for p in TESSERACT_PATHS:
        if os.path.exists(p):
            return p
    return None

def extract_with_pymupdf_text(pdf_path: str, progress_callback: Optional[Callable] = None) -> List[Dict]:
    """Strategy 1: PyMuPDF native text extraction (fast, no OCR)."""
    import fitz
    doc = fitz.open(pdf_path)
    total = len(doc)
    pages_data = []
    
    for idx in range(total):
        if progress_callback:
            progress_callback(idx, total, "Text Extraction")
        page = doc[idx]
        text = page.get_text("text") or ""
        pages_data.append({
            "page_number": idx + 1,
            "text_content": text.strip(),
            "filename": Path(pdf_path).name
        })
    doc.close()
    return pages_data

def extract_with_tesseract(pdf_path: str, progress_callback: Optional[Callable] = None) -> List[Dict]:
    """Strategy 2: Tesseract OCR — renders each page as image and runs OCR."""
    import fitz
    import pytesseract
    from PIL import Image
    
    tess_path = _find_tesseract()
    if tess_path:
        pytesseract.pytesseract.tesseract_cmd = tess_path
    
    doc = fitz.open(pdf_path)
    total = len(doc)
    pages_data = []
    
    for idx in range(total):
        if progress_callback:
            progress_callback(idx, total, "Tesseract OCR")
        
        page = doc[idx]
        # Render page at 200 DPI for good OCR quality
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        
        try:
            text = pytesseract.image_to_string(img, lang="eng")
        except Exception as e:
            print(f"  Tesseract failed on page {idx+1}: {e}")
            text = ""
        
        pages_data.append({
            "page_number": idx + 1,
            "text_content": text.strip(),
            "filename": Path(pdf_path).name
        })
    
    doc.close()
    return pages_data

def smart_extract_pdf(pdf_path: str, progress_callback: Optional[Callable] = None) -> List[Dict]:
    """
    Master extractor: tries PyMuPDF text first, auto-falls back to Tesseract OCR
    if the PDF is scanned/image-based.
    
    Detection: If <30% of pages have meaningful text (>30 chars), it's likely scanned.
    """
    pdf_path = str(pdf_path)
    
    # Strategy 1: Try PyMuPDF native text extraction (fastest)
    try:
        import fitz
        pages = extract_with_pymupdf_text(pdf_path, progress_callback)
        text_pages = sum(1 for p in pages if len(p["text_content"]) > 30)
        total = len(pages)
        quality = text_pages / total if total > 0 else 0
        
        print(f"[PDF Extractor] PyMuPDF text: {text_pages}/{total} pages with text ({quality*100:.0f}%)")
        
        if quality >= 0.3:
            return pages
        else:
            print(f"[PDF Extractor] Low text quality ({quality*100:.0f}%) — PDF appears scanned. Switching to OCR...")
    except Exception as e:
        print(f"[PDF Extractor] PyMuPDF error: {e}")
    
    # Strategy 2: Tesseract OCR for scanned PDFs
    tess_path = _find_tesseract()
    if tess_path:
        try:
            print(f"[PDF Extractor] Using Tesseract OCR at: {tess_path}")
            pages = extract_with_tesseract(pdf_path, progress_callback)
            text_pages = sum(1 for p in pages if len(p["text_content"]) > 30)
            print(f"[PDF Extractor] Tesseract OCR: {text_pages}/{len(pages)} pages with text")
            return pages
        except Exception as e:
            print(f"[PDF Extractor] Tesseract OCR failed: {e}")
    else:
        print("[PDF Extractor] Tesseract OCR not found. Install via: winget install UB-Mannheim.TesseractOCR")
    
    # Final fallback: return whatever PyMuPDF gave us (possibly empty)
    print("[PDF Extractor] All OCR strategies exhausted, returning best available extraction")
    try:
        return extract_with_pymupdf_text(pdf_path, progress_callback)
    except:
        return [{"page_number": 1, "text_content": "", "filename": Path(pdf_path).name}]
