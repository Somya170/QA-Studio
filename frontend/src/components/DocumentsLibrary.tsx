import React, { useEffect, useState, useRef } from 'react';
import { FileText, Trash2, RefreshCw, Upload, AlertCircle, Search, Pencil, Check, X } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000/api';

interface DocInfo {
  filename: string;
  pages: number;
}

export const DocumentsLibrary: React.FC = () => {
  const [documents, setDocuments] = useState<DocInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [editingDoc, setEditingDoc] = useState<string | null>(null);
  const [newName, setNewName] = useState('');
  const renameInputRef = useRef<HTMLInputElement>(null);

  const fetchDocuments = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/documents`);
      const data = await res.json();
      setDocuments(data.documents || []);
    } catch (e: any) {
      setError('Failed to connect to backend');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (filename: string) => {
    if (!confirm(`Delete "${filename}" and all its pages?`)) return;
    setDeleting(filename);
    try {
      const res = await fetch(`${API_BASE}/documents/${encodeURIComponent(filename)}`, {
        method: 'DELETE',
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Delete failed');
      }
      await fetchDocuments();
    } catch (e: any) {
      setError(`Failed to delete: ${e.message}`);
    } finally {
      setDeleting(null);
    }
  };

  const handleRename = async (oldName: string) => {
    if (!newName.trim() || newName === oldName) {
      setEditingDoc(null);
      return;
    }
    try {
      const res = await fetch(
        `${API_BASE}/documents/${encodeURIComponent(oldName)}/rename?new_name=${encodeURIComponent(newName.trim())}`,
        { method: 'PUT' }
      );
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Rename failed');
      }
      setEditingDoc(null);
      await fetchDocuments();
    } catch (e: any) {
      setError(`Rename failed: ${e.message}`);
    }
  };

  const startEditing = (filename: string) => {
    setEditingDoc(filename);
    setNewName(filename);
    setTimeout(() => renameInputRef.current?.focus(), 50);
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const filtered = documents.filter(d =>
    d.filename.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-3">
            <FileText className="w-7 h-7 text-cyan-400" />
            Documents Library
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Manage uploaded PDFs. Query all or filter by document.
          </p>
        </div>
        <button
          onClick={fetchDocuments}
          disabled={loading}
          className="px-4 py-2 rounded-lg bg-slate-800/70 hover:bg-slate-700/70 text-slate-300 transition flex items-center gap-2 text-sm"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Search Bar */}
      {documents.length > 0 && (
        <div className="glass-panel rounded-xl border border-slate-800 p-1 flex items-center gap-2">
          <Search className="w-4 h-4 text-slate-400 ml-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search documents by name..."
            className="w-full bg-transparent py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
          />
          {searchQuery && (
            <button onClick={() => setSearchQuery('')} className="p-1.5 mr-2 text-slate-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-center gap-2 px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0" />
          {error}
          <button onClick={() => setError(null)} className="ml-auto text-red-400 hover:text-red-300">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Documents Grid */}
      {documents.length === 0 ? (
        <div className="glass-panel rounded-2xl p-12 text-center border border-slate-800">
          <Upload className="w-16 h-16 mx-auto text-slate-600 mb-4" />
          <h3 className="text-lg font-semibold text-slate-400 mb-2">No Documents Uploaded</h3>
          <p className="text-sm text-slate-500">
            Go to <span className="text-cyan-400 font-medium">Data Ingestion</span> tab to upload PDFs.
          </p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-10 text-slate-500 text-sm">
          No documents matching "{searchQuery}"
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((doc) => (
            <div
              key={doc.filename}
              className="doc-card relative rounded-xl p-5 border border-slate-200 dark:border-slate-700/50 hover:border-cyan-500/40 hover:shadow-lg hover:shadow-cyan-500/5 transition-all duration-200 group"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3 min-w-0 flex-1">
                  <div className="w-11 h-11 rounded-xl flex items-center justify-center shrink-0"
                    style={{background: 'rgba(6, 182, 212, 0.08)', border: '1px solid rgba(6, 182, 212, 0.2)'}}
                  >
                    <FileText className="w-5 h-5 text-cyan-400" />
                  </div>
                  <div className="min-w-0 flex-1">
                    {editingDoc === doc.filename ? (
                      <div className="flex items-center gap-1">
                        <input
                          ref={renameInputRef}
                          value={newName}
                          onChange={(e) => setNewName(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleRename(doc.filename);
                            if (e.key === 'Escape') setEditingDoc(null);
                          }}
                          className="bg-slate-800 text-white text-sm px-2 py-1 rounded border border-cyan-500/40 focus:outline-none w-full"
                        />
                        <button onClick={() => handleRename(doc.filename)} className="p-1 text-emerald-400 hover:text-emerald-300">
                          <Check className="w-4 h-4" />
                        </button>
                        <button onClick={() => setEditingDoc(null)} className="p-1 text-slate-400 hover:text-slate-300">
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ) : (
                      <p className="font-semibold text-white text-sm truncate cursor-pointer hover:text-cyan-300 transition" 
                         title={`Click to rename: ${doc.filename}`}
                         onClick={() => startEditing(doc.filename)}
                      >
                        {doc.filename}
                      </p>
                    )}
                    <p className="text-xs text-slate-400 mt-0.5">
                      {doc.pages} pages indexed
                    </p>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition">
                  <button
                    onClick={() => startEditing(doc.filename)}
                    title="Rename"
                    className="p-1.5 rounded-lg text-slate-400 hover:text-cyan-400 hover:bg-cyan-500/10 transition"
                  >
                    <Pencil className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => handleDelete(doc.filename)}
                    disabled={deleting === doc.filename}
                    title="Delete"
                    className="p-1.5 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition"
                  >
                    {deleting === doc.filename ? (
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Trash2 className="w-3.5 h-3.5" />
                    )}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Summary */}
      {documents.length > 0 && (
        <div className="text-sm text-slate-500 text-center">
          {documents.length} document{documents.length > 1 ? 's' : ''} • {documents.reduce((sum, d) => sum + d.pages, 0)} total pages indexed
        </div>
      )}
    </div>
  );
};
