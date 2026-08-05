"""Analyze the Siemens Sinumerik PDF to understand its structure and text extraction quality."""
import pypdf
import sys

pdf_path = r"c:\Users\Somya\Downloads\DocYork\backend\data\raw\siemens_sinumerk_manual_260723_125157.pdf"

print(f"Opening: {pdf_path}")
reader = pypdf.PdfReader(pdf_path)
total_pages = len(reader.pages)
print(f"Total Pages: {total_pages}\n")

# Sample first 5 pages, middle page, and last page
sample_indices = list(range(min(5, total_pages)))
if total_pages > 10:
    sample_indices.append(total_pages // 2)
    sample_indices.append(total_pages - 1)

empty_count = 0
short_count = 0
good_count = 0

for i in range(total_pages):
    text = reader.pages[i].extract_text() or ""
    text_len = len(text.strip())
    if text_len == 0:
        empty_count += 1
    elif text_len < 50:
        short_count += 1
    else:
        good_count += 1
    
    if i in sample_indices:
        preview = text.strip()[:500] if text.strip() else "[EMPTY - No text extracted]"
        print(f"{'='*80}")
        print(f"PAGE {i+1}/{total_pages}  |  Characters: {text_len}")
        print(f"{'='*80}")
        print(preview)
        print()

print(f"\n{'='*80}")
print(f"EXTRACTION SUMMARY")
print(f"{'='*80}")
print(f"Total Pages:           {total_pages}")
print(f"Pages with good text:  {good_count}  ({good_count*100//total_pages}%)")
print(f"Pages with short text: {short_count}  ({short_count*100//total_pages}%)")
print(f"Empty pages (no text): {empty_count}  ({empty_count*100//total_pages}%)")
print()

# Check what the DuckDB table looks like
print(f"{'='*80}")
print(f"CHECKING DUCKDB TABLE SCHEMA")
print(f"{'='*80}")
try:
    sys.path.insert(0, r"c:\Users\Somya\Downloads\DocYork\backend")
    from app.db.duckdb_client import db_client
    tables = db_client.list_tables()
    print(f"Available tables: {tables}")
    
    sinumerik_tables = [t for t in tables if 'sinumer' in t.lower()]
    for t in sinumerik_tables:
        schema = db_client.get_table_schema(t)
        print(f"\nTable: {t}")
        print(f"Schema: {schema}")
        
        row_count = db_client.execute_query(f"SELECT COUNT(*) as cnt FROM {t}")
        print(f"Row count: {row_count}")
        
        sample = db_client.execute_query(f"SELECT * FROM {t} LIMIT 2")
        for row in sample:
            for key, val in row.items():
                val_str = str(val)
                print(f"  {key}: {val_str[:200]}{'...' if len(val_str) > 200 else ''}")
            print("  ---")
except Exception as e:
    print(f"DuckDB Error: {e}")
