"""Quick test: Extract text from Siemens PDF using Groq Vision API."""
import fitz
import io
import base64
import requests
import sys
sys.path.insert(0, r"c:\Users\Somya\Downloads\DocYork\backend")
from app.config import GROQ_API_KEY

print(f"Groq API Key present: {bool(GROQ_API_KEY)}")

pdf_path = r"c:\Users\Somya\Downloads\DocYork\backend\data\raw\siemens_sinumerk_manual_260723_125157.pdf"
doc = fitz.open(pdf_path)
print(f"Total pages: {len(doc)}")

# Test pages 3, 5, 10
for page_idx in [2, 4, 9]:
    print(f"\n{'='*60}")
    print(f"PAGE {page_idx + 1}")
    print(f"{'='*60}")
    
    page = doc[page_idx]
    pix = page.get_pixmap(dpi=150)
    img_bytes = pix.tobytes("png")
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.2-90b-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract ALL text from this document page exactly as written. Preserve paragraphs and line breaks. Output ONLY the extracted text, nothing else. If the page has tables, format them with | separators."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.1,
        "max_tokens": 4096
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            text = response.json()["choices"][0]["message"]["content"].strip()
            print(f"Extracted {len(text)} chars:")
            print(text[:600])
        else:
            print(f"Error {response.status_code}: {response.text[:300]}")
    except Exception as e:
        print(f"Error: {e}")

doc.close()
print("\nDone!")
