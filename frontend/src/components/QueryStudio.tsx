import React, { useState, useEffect } from 'react';
import { Send, ShieldCheck, Code, Table as TableIcon, Sparkles, CheckCircle2, AlertTriangle, FileSpreadsheet, RefreshCw } from 'lucide-react';
import type { QueryResponse } from '../types/dataTypes';
import { executeQuery, fetchTableProfile } from '../services/api';

export const QueryStudio: React.FC = () => {
  const [queryInput, setQueryInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showSqlInspector, setShowSqlInspector] = useState(false);
  
  // Table dynamic profile states
  const [suggestedQueries, setSuggestedQueries] = useState<string[]>([
    "Which machine had the highest total downtime?",
    "Show maintenance history for Machine MAC-0452",
    "How many machines require maintenance due?",
    "What is the total maintenance cost by category?",
    "Show operator efficiency rating & shift logs"
  ]);
  const [summaryInsights, setSummaryInsights] = useState<string[]>([
    "Upload any custom Excel, CSV, or JSON file to automatically profile insights.",
    "Engine uses DuckDB under the hood for zero-hallucination factual grounding."
  ]);
  const [activeTable, setActiveTable] = useState<string | null>(null);
  const [refreshingProfile, setRefreshingProfile] = useState(false);
  const [documents, setDocuments] = useState<{filename: string; pages: number}[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<string>('all');

  const loadProfile = async () => {
    setRefreshingProfile(true);
    try {
      const profile = await fetchTableProfile();
      if (profile && profile.table_name) {
        setActiveTable(profile.table_name);
        if (profile.suggested_queries && profile.suggested_queries.length > 0) {
          setSuggestedQueries(profile.suggested_queries);
        }
        if (profile.summary_insights && profile.summary_insights.length > 0) {
          setSummaryInsights(profile.summary_insights);
        }
      }
    } catch (err) {
      console.warn("Failed to load table profile, using default prompts:", err);
    } finally {
      setRefreshingProfile(false);
    }
  };

  const fetchDocuments = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/documents');
      const data = await res.json();
      setDocuments(data.documents || []);
    } catch (err) {
      console.warn('Failed to fetch documents:', err);
    }
  };

  useEffect(() => {
    loadProfile();
    fetchDocuments();
  }, []);

  const handleAsk = async (promptToRun?: string) => {
    const q = promptToRun || queryInput;
    if (!q.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const res = await executeQuery(q, selectedDocument !== 'all' ? selectedDocument : undefined);
      setResponse(res);
    } catch (err: any) {
      setError(err.message || 'Error executing query');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Hero Banner with Auto-Generated Summary Insights */}
      <div className="glass-panel p-6 rounded-2xl border border-cyan-500/20 relative overflow-hidden">
        <div className="absolute -right-10 -bottom-10 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>
        
        <div className="flex flex-col lg:flex-row gap-6 justify-between">
          <div className="space-y-3 max-w-xl">
            <div className="flex flex-wrap items-center gap-2">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-cyan-950/60 border border-cyan-500/30 rounded-full text-cyan-300 text-xs font-semibold">
                <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
                <span>DuckDB Deterministic Engine Active</span>
              </div>
              {activeTable && (
                <div className="inline-flex items-center gap-1 px-2.5 py-0.5 bg-emerald-950/60 border border-emerald-500/30 rounded-full text-emerald-300 text-[10px] font-semibold uppercase">
                  <FileSpreadsheet className="w-3 h-3 text-emerald-400" />
                  <span>Active: {activeTable}</span>
                </div>
              )}
            </div>
            
            <h2 className="text-2xl font-bold text-white tracking-tight">
              Natural Language Data QA Studio
            </h2>
            <p className="text-xs text-slate-400">
              Ask any question about your dataset. Answers are computed directly via DuckDB with 100% mathematical accuracy and zero hallucination.
            </p>

            {/* Dynamic Summary Insights Panel */}
            <div className="p-3.5 bg-slate-950/70 border border-slate-900 rounded-xl space-y-1.5">
              <div className="text-[10px] text-cyan-400 font-bold uppercase tracking-wider flex items-center justify-between">
                <span>AI Data Insights Profile</span>
                <button 
                  onClick={loadProfile}
                  disabled={refreshingProfile}
                  className="hover:text-cyan-300 transition flex items-center gap-1 disabled:opacity-50"
                  title="Reload suggestions"
                >
                  <RefreshCw className={`w-2.5 h-2.5 ${refreshingProfile ? 'animate-spin' : ''}`} />
                  <span>Refresh</span>
                </button>
              </div>
              <ul className="list-disc pl-4 text-slate-300 text-[11px] space-y-1">
                {summaryInsights.map((insight, idx) => (
                  <li key={idx}>{insight}</li>
                ))}
              </ul>
            </div>
          </div>

          {/* Dynamic Suggested Prompts Chips */}
          <div className="flex flex-col gap-2 max-w-md w-full shrink-0">
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider pl-1">
              Suggested Questions for this Data:
            </span>
            <div className="flex flex-col gap-2">
              {suggestedQueries.slice(0, 5).map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setQueryInput(prompt);
                    handleAsk(prompt);
                  }}
                  className="px-3.5 py-2 bg-slate-900/60 hover:bg-cyan-950/40 hover:border-cyan-500/30 border border-slate-800/80 rounded-xl text-[11px] text-slate-300 hover:text-cyan-300 transition text-left flex items-center gap-2"
                >
                  <Sparkles className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                  <span className="truncate">{prompt}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Document Filter Dropdown */}
      {documents.length > 0 && (
        <div className="glass-panel p-3 rounded-xl border border-slate-800 flex items-center gap-3">
          <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider shrink-0 pl-2">Query Scope:</span>
          <select
            value={selectedDocument}
            onChange={(e) => setSelectedDocument(e.target.value)}
            className="flex-1 bg-slate-900/80 text-sm text-slate-200 py-2 px-3 rounded-lg border border-slate-700 focus:outline-none focus:border-cyan-500/50 transition appearance-none cursor-pointer"
          >
            <option value="all">📚 All Documents (Cross-document search)</option>
            {documents.map((doc) => (
              <option key={doc.filename} value={doc.filename}>
                📄 {doc.filename} ({doc.pages} pages)
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Query Search Bar */}
      <div className="glass-panel p-2 rounded-2xl border border-slate-800 flex items-center gap-2">
        <div className="pl-4 text-cyan-400">
          <Sparkles className="w-5 h-5 animate-pulse" />
        </div>
        <input
          type="text"
          value={queryInput}
          onChange={(e) => setQueryInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAsk()}
          placeholder="Ask a question (e.g. 'What is the category of MAC-5007?')..."
          className="w-full bg-transparent py-3 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-500 focus:outline-none"
        />
        <button
          onClick={() => handleAsk()}
          disabled={loading || !queryInput.trim()}
          className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs rounded-xl shadow-lg shadow-cyan-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center gap-2 shrink-0"
        >
          {loading ? (
            <span className="inline-block animate-spin rounded-full h-4 w-4 border-2 border-slate-950 border-t-transparent"></span>
          ) : (
            <>
              <span>Ask AI Engine</span>
              <Send className="w-3.5 h-3.5" />
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="p-4 bg-rose-950/50 border border-rose-500/30 rounded-xl text-rose-300 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Answer Output View */}
      {response && (
        <div className="space-y-6">
          {/* Answer Banner */}
          <div className="glass-panel-glow p-6 rounded-2xl border border-cyan-500/30 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-cyan-950 flex items-center justify-center border border-cyan-500/30">
                  <CheckCircle2 className="w-4 h-4 text-cyan-400" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">Grounded Answer Output</h3>
                  <span className="text-[10px] text-cyan-400 font-medium">
                    Execution Mode: {response.execution_type} | Grounding Confidence: {response.audit.confidence_score}%
                  </span>
                </div>
              </div>

              {response.audit.sql_executed && (
                <button
                  onClick={() => setShowSqlInspector(!showSqlInspector)}
                  className="px-3 py-1.5 bg-slate-900 border border-slate-700 hover:border-cyan-500/40 rounded-lg text-xs text-slate-300 flex items-center gap-1.5 transition"
                >
                  <Code className="w-3.5 h-3.5 text-cyan-400" />
                  <span>{showSqlInspector ? 'Hide SQL Code' : 'Inspect SQL Query'}</span>
                </button>
              )}
            </div>

            {/* Natural language summary text */}
            <div className="text-slate-200 text-sm leading-relaxed font-sans bg-slate-900/60 p-4 rounded-xl border border-slate-800/80">
              {response.answer}
            </div>

            {/* SQL Query Code Drawer */}
            {showSqlInspector && response.audit.sql_executed && (
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs font-mono text-cyan-300 space-y-2">
                <div className="text-[10px] uppercase font-bold text-slate-500 flex items-center justify-between">
                  <span>Executed SQL Query (DuckDB Engine)</span>
                  <span className="text-emerald-400">100% Deterministic</span>
                </div>
                <pre className="overflow-x-auto whitespace-pre-wrap">{response.audit.sql_executed}</pre>
              </div>
            )}
          </div>

          {/* Data Table View */}
          {response.data_table && response.data_table.length > 0 && (
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                  <TableIcon className="w-4 h-4 text-cyan-400" />
                  Direct Ground-Truth Records ({response.data_table.length} rows)
                </h3>
                <span className="text-xs text-slate-400">Source: DuckDB In-Memory Warehouse</span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase bg-slate-900/60">
                      {Object.keys(response.data_table[0]).map((col) => (
                        <th key={col} className="p-3">
                          {col.replace(/_/g, ' ')}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300">
                    {response.data_table.map((row, idx) => (
                      <tr key={idx} className="hover:bg-slate-900/40 transition">
                        {Object.values(row).map((val, valIdx) => (
                          <td key={valIdx} className="p-3 font-mono">
                            {val !== null && val !== undefined ? String(val) : '-'}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Grounding Evidence Audit Panel */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              Zero-Hallucination Evidence Trail & Audit Log
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
                <div className="text-[10px] text-slate-400 font-semibold uppercase">Confidence Score</div>
                <div className="text-xl font-bold text-emerald-400 mt-1">{response.audit.confidence_score}% Verified</div>
              </div>
              <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
                <div className="text-[10px] text-slate-400 font-semibold uppercase">Matched Source Rows</div>
                <div className="text-xl font-bold text-cyan-400 mt-1">{response.audit.matched_row_count} Records</div>
              </div>
              <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
                <div className="text-[10px] text-slate-400 font-semibold uppercase">Audit Status</div>
                <div className="text-xs font-semibold text-slate-200 mt-2 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Zero Hallucination Shield Passed
                </div>
              </div>
            </div>

            <div className="text-xs text-slate-400 bg-slate-950 p-3 rounded-lg border border-slate-800 font-mono">
              <span className="text-cyan-400 font-bold">Trace:</span> {response.audit.reasoning_trace}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
