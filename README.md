# DocYork

**Enterprise-grade, zero-hallucination Natural Language Query & Analytics Engine.**

DocYork lets engineers, plant managers, and business operators query complex databases and uploaded spreadsheets (Excel, CSV, JSON) using plain English/Hindi — and get 100% mathematically accurate, ground-truth-verified answers along with interactive visual analytics.

---

## 🎯 Problem it Solves

Traditional LLM chat applications hallucinate — they invent facts and miscalculate sums. DocYork fixes this by **separating reasoning from computation**:

- **Reasoning** → handled by the LLM (translates natural language into SQL)
- **Computation** → handled deterministically by an in-memory DuckDB engine

Every answer is validated against the database engine before being shown to the user, so numbers are never "made up" — they always come from a real query result.

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** — high-speed async ASGI framework
- **DuckDB** — in-memory columnar database for analytical SQL queries
- **Groq Cloud** (`llama-3.3-70b-versatile`) & **Gemini API** (`gemini-1.5-flash`) — swappable LLM providers
- **pandas / openpyxl** — Excel & CSV parsing
- **pypdf / PyMuPDF (fitz)** — PDF text & table extraction
- **pytesseract / Pillow** — OCR for scanned/image-based PDFs
- **pydantic** — request/response validation
- **Uvicorn** — ASGI server

### Frontend
- **React 18 + TypeScript** — SPA core
- **Vite** — ultra-fast bundler
- **Tailwind CSS + Vanilla CSS** — dark/light theme support
- **Recharts** — interactive, responsive data visualizations
- **Lucide React** — icon library

---

## 🏗️ System Architecture

```
User Query
    │
    ▼
Multi-Table Entity Router  → routes to correct table based on ID pattern
    │                         (e.g. MAC-XXXX, EMP-XXXX, FLT-XXXX, INV-XXXX)
    │                         or falls back to the active uploaded table
    ▼
Text-to-SQL Engine (LLM)   → translates natural language into DuckDB SQL
    │
    ▼
DuckDB Execution           → SQL runs against the in-memory table
    │
    ├── Rows matched > 0  → Answer Synthesizer
    └── Error / 0 rows    → Semantic Keyword Fallback → Answer Synthesizer
                                                            │
                                                            ▼
                                        Grounded Factual Response + Chart
```

**Key design principle:** the LLM never performs computation. It only (1) generates SQL and (2) converts a verified SQL result into a natural-sounding sentence. All actual math happens inside DuckDB — this is what guarantees zero hallucination.

### Pipeline Steps
1. **Dynamic Data Ingestion** — uploaded sheets are loaded into an in-memory DuckDB table
2. **Auto-Profiling** — descriptive stats (count, averages, min/max, category distributions) feed the LLM to generate summary insights and suggested prompts
3. **Multi-Table Entity Router** — queries containing known ID formats are redirected to their correct source table
4. **SQL Generator** — converts the query into a DuckDB SQL statement
5. **Execution & Validation** — runs the SQL; falls back to semantic keyword search on failure/empty result
6. **Answer Synthesizer** — formulates a conversational response strictly grounded in the SQL result

---

## 🚀 Deployment

### Frontend (Vercel)
```bash
# Root Directory: frontend
# Framework Preset: Vite
# Build Command: npm run build
# Output Directory: dist
```

Add `frontend/vercel.json` to handle API proxying and SPA routing:
```json
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://<your-backend-url>/api/:path*" },
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

### Backend (Render / Fly.io / AWS)
```bash
# Build Command: pip install -r backend/requirements.txt
# Start Command: python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Environment variables required:
```
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 📦 Getting Started (Local Development)

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

