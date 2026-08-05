import json
from typing import Dict, Any, List
from app.db.duckdb_client import db_client
from app.llm.cloud_provider import cloud_llm

# In-memory profile cache for the active custom table
_active_profile_cache: Dict[str, Any] = {
    "table_name": None,
    "suggested_queries": [
        "What is the location of MAC-5007?",
        "Which machine had the highest repair cost in the uploaded file?",
        "Who operated CNC Lathe MAC-5002?",
        "Which machine had the highest downtime in the file?",
        "Show maintenance details for MAC-5001"
    ],
    "summary_insights": [
        "Welcome to DocYork Fleet Studio! Standard industrial templates are active.",
        "Upload a custom Excel/CSV/JSON file to automatically generate tailored questions and summary insights."
    ]
}

def get_active_profile() -> Dict[str, Any]:
    return _active_profile_cache

def profile_table(table_name: str) -> Dict[str, Any]:
    """
    Profiles a newly ingested table dynamically, querying DuckDB for metrics,
    and uses the active LLM (Llama/Gemini) to generate tailored questions and insights.
    Handles both structured tables and unstructured PDF text data.
    """
    global _active_profile_cache
    
    try:
        # 1. Fetch column metadata
        cols = db_client.get_table_schema(table_name)
        if not cols:
            return _active_profile_cache

        # 2. Fetch basic statistics
        total_rows = db_client.execute_query(f"SELECT COUNT(*) as cnt FROM {table_name}")[0]["cnt"]
        
        # Check if PDF table
        is_pdf_table = len(cols) == 3 and any(c["column"].lower() == "text_content" for c in cols) and any(c["column"].lower() == "page_number" for c in cols)
        
        column_summaries = []
        if is_pdf_table:
            # Query first 3 pages for sample context
            sample_rows = db_client.execute_query(f"SELECT page_number, text_content FROM {table_name} ORDER BY page_number ASC LIMIT 3")
            sample_text = "\n".join([f"Page {r['page_number']}:\n{r['text_content'][:600]}..." for r in sample_rows])
            column_summaries = [
                "Unstructured PDF Document",
                f"Page Count (Rows): {total_rows}",
                f"Sample text from first pages:\n{sample_text}"
            ]
        else:
            # Structured columns stats
            for c in cols:
                col_name = c["column"]
                col_type = c["type"].lower()
                
                if "int" in col_type or "double" in col_type or "float" in col_type or "decimal" in col_type:
                    stats = db_client.execute_query(f"SELECT MIN({col_name}) as val_min, MAX({col_name}) as val_max, AVG({col_name}) as val_avg FROM {table_name}")[0]
                    column_summaries.append(
                        f"Numeric Column '{col_name}': Min={stats['val_min']}, Max={stats['val_max']}, Avg={round(stats['val_avg'] or 0, 2)}"
                    )
                else:
                    freqs = db_client.execute_query(
                        f"SELECT {col_name} as val, COUNT(*) as cnt FROM {table_name} GROUP BY {col_name} ORDER BY cnt DESC LIMIT 3"
                    )
                    top_vals = [f"'{f['val']}' (x{f['cnt']})" for f in freqs if f["val"] is not None]
                    column_summaries.append(
                        f"Categorical Column '{col_name}': Top values: {', '.join(top_vals)}"
                    )

        # 3. Formulate LLM Prompt
        system_prompt = (
            "You are an expert data profiler. Given a database table description/stats or a PDF document sample, "
            "generate: \n"
            "1. 5 highly practical, business-relevant natural language questions that can be answered by querying this table or document.\n"
            "2. 3 short bullet-point summary insights summarizing key highlights or patterns in the data.\n\n"
            "Rules:\n"
            "- Output strictly a raw JSON string. Do not include markdown backticks (no ```json or ```).\n"
            "- Ensure the JSON format matches exactly: \n"
            "{\n"
            "  \"suggested_queries\": [\"Question 1\", \"Question 2\", ...],\n"
            "  \"summary_insights\": [\"Insight 1\", \"Insight 2\", ...]\n"
            "}"
        )
        
        prompt = (
            f"Table Name: {table_name}\n"
            f"Total Record Count: {total_rows}\n"
            f"Columns & Profile Statistics:\n"
            + "\n".join(column_summaries)
        )

        # 4. Request insights from LLM
        response_text = cloud_llm.generate(prompt, system_prompt=system_prompt)
        response_text = response_text.replace("```json", "").replace("```", "").strip()

        # Parse JSON
        profile_data = json.loads(response_text)
        
        # Save to active cache
        _active_profile_cache = {
            "table_name": table_name,
            "suggested_queries": profile_data.get("suggested_queries", _active_profile_cache["suggested_queries"]),
            "summary_insights": profile_data.get("summary_insights", _active_profile_cache["summary_insights"])
        }
        
    except Exception as e:
        print("Auto-Profiling Failed, keeping standard templates. Detail:", e)
        _active_profile_cache["table_name"] = table_name

    return _active_profile_cache
