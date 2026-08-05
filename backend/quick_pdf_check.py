import pypdf

pdf_path = r"c:\Users\Somya\Downloads\DocYork\backend\data\raw\siemens_sinumerk_manual_260723_125157.pdf"
reader = pypdf.PdfReader(pdf_path)
print(f"Total pages: {len(reader.pages)}")
print(f"Metadata: {reader.metadata}")
print(f"Creator: {reader.metadata.get('/Creator', 'N/A')}")
print(f"Producer: {reader.metadata.get('/Producer', 'N/A')}")
print()

# Check text extraction on sample pages
empty_pages = 0
text_pages = 0
sample_pages = [0, 1, 2, 3, 4, 9, 19, 49, 99, 199, 300, 415]

for i in sample_pages:
    if i < len(reader.pages):
        try:
            txt = reader.pages[i].extract_text() or ""
            chars = len(txt.strip())
            if chars == 0:
                print(f"Page {i+1}: EMPTY (0 chars) - likely scanned image")
            else:
                print(f"Page {i+1}: {chars} chars")
                print(f"  Preview: {txt.strip()[:200]}")
                print()
        except Exception as e:
            print(f"Page {i+1}: ERROR - {e}")

# Count all empty vs text pages (first 20 only to save time)
print("\n--- Sampling first 20 pages for text vs image ratio ---")
for i in range(min(20, len(reader.pages))):
    try:
        txt = reader.pages[i].extract_text() or ""
        if len(txt.strip()) > 0:
            text_pages += 1
        else:
            empty_pages += 1
    except:
        empty_pages += 1

print(f"Text pages (out of 20): {text_pages}")
print(f"Empty/Image pages (out of 20): {empty_pages}")

if empty_pages > text_pages:
    print("\n*** DIAGNOSIS: This PDF is SCANNED/IMAGE-BASED ***")
    print("pypdf cannot extract text from scanned images.")
    print("Solution: Need OCR (Optical Character Recognition) like pytesseract or pdfplumber with OCR.")
else:
    print("\n*** DIAGNOSIS: This PDF has extractable text ***")
