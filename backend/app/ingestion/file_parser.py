import pandas as pd
import json
from pathlib import Path
from typing import Tuple, List, Dict, Any

def parse_uploaded_file(file_path: Path) -> Tuple[pd.DataFrame, str]:
    """Parses uploaded CSV, JSON, Excel, or PDF file into a pandas DataFrame."""
    ext = file_path.suffix.lower()
    table_name = file_path.stem.lower().replace("-", "_").replace(" ", "_")

    if ext in [".csv", ".txt"]:
        df = pd.read_csv(file_path)
    elif ext in [".json"]:
        df = pd.read_json(file_path)
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
    elif ext in [".pdf"]:
        try:
            import pypdf
        except ImportError:
            raise ImportError("Python package 'pypdf' is required for PDF parsing. Please run 'pip install pypdf'.")
            
        reader = pypdf.PdfReader(str(file_path))
        pages_data = []
        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages_data.append({
                "page_number": int(idx + 1),
                "text_content": text,
                "filename": file_path.name
            })
        df = pd.DataFrame(pages_data)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    # Standardize column names (lowercase, no spaces)
    df.columns = [str(col).strip().lower().replace(" ", "_").replace("-", "_") for col in df.columns]
    return df, table_name
