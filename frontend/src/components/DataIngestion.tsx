import React, { useState } from 'react';
import { Upload, CheckCircle2, RefreshCw, AlertCircle } from 'lucide-react';
import { uploadFile, fetchIngestStatus } from '../services/api';

interface DataIngestionProps {
  onIngestSuccess: () => void;
}

export const DataIngestion: React.FC<DataIngestionProps> = ({ onIngestSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string; details?: any } | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileUpload = async (file: File) => {
    setLoading(true);
    setMessage(null);
    setProgress(5);
    setStatusMessage('Uploading file to server...');
    
    let intervalId: any = null;
    
    try {
      const uploadRes = await uploadFile(file);
      const taskId = uploadRes.task_id;
      
      // Start polling status every 1 second
      intervalId = setInterval(async () => {
        try {
          const statusRes = await fetchIngestStatus(taskId);
          setProgress(statusRes.progress);
          setStatusMessage(statusRes.message);
          
          if (statusRes.status === 'SUCCESS') {
            clearInterval(intervalId);
            setLoading(false);
            setMessage({
              type: 'success',
              text: `Successfully parsed and loaded '${file.name}' into DuckDB table '${statusRes.result.table_name}'!`,
              details: statusRes.result
            });
            onIngestSuccess();
          } else if (statusRes.status === 'FAILED') {
            clearInterval(intervalId);
            setLoading(false);
            setMessage({
              type: 'error',
              text: statusRes.message || 'File ingestion failed.'
            });
          }
        } catch (pollErr: any) {
          console.error("Polling error:", pollErr);
        }
      }, 1000);
      
    } catch (err: any) {
      setLoading(false);
      setMessage({
        type: 'error',
        text: err.message || 'Failed to start file upload.'
      });
    }
  };



  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Real-time Ingestion Progress Bar */}
      {loading && (
        <div className="glass-panel p-6 rounded-2xl border border-cyan-500/20 space-y-4">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-350">
            <span className="flex items-center gap-2">
              <RefreshCw className="w-3.5 h-3.5 text-cyan-400 animate-spin" />
              {statusMessage}
            </span>
            <span className="text-cyan-400 font-bold">{progress}%</span>
          </div>
          <div className="w-full bg-slate-950/60 rounded-full h-3 overflow-hidden border border-slate-900">
            <div 
              className="bg-gradient-to-r from-cyan-500 to-blue-600 h-full rounded-full transition-all duration-300 shadow-lg shadow-cyan-500/20"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <div className="text-[10px] text-slate-500 text-center animate-pulse">
            Processing runs in the background. You can switch tabs safely without losing state.
          </div>
        </div>
      )}

      {/* Drag and Drop File Upload Area */}
      {!loading && (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setIsDragging(false);
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
              handleFileUpload(e.dataTransfer.files[0]);
            }
          }}
          className={`glass-panel p-10 rounded-2xl border-2 border-dashed text-center transition space-y-4 cursor-pointer ${
            isDragging ? 'border-cyan-400 bg-cyan-950/20' : 'border-slate-800 hover:border-slate-700'
          }`}
        >
          <div className="w-12 h-12 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center mx-auto text-cyan-400">
            <Upload className="w-6 h-6" />
          </div>

          <div>
            <h4 className="text-sm font-bold text-white">Upload Custom Industrial Logs (CSV, JSON, Excel, PDF)</h4>
            <p className="text-xs text-slate-400 mt-1">
              Drag and drop your historical CSV, JSON, XLSX, or PDF file here, or browse from computer
            </p>
          </div>

          <label className="inline-block px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 text-xs font-semibold rounded-xl cursor-pointer transition">
            <span>Browse File</span>
            <input
              type="file"
              accept=".csv, .json, .xlsx, .xls, .txt, .pdf"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleFileUpload(e.target.files[0]);
                }
              }}
            />
          </label>
        </div>
      )}

      {/* Ingestion Result Banner */}
      {message && (
        <div
          className={`p-5 rounded-2xl border text-xs space-y-2 ${
            message.type === 'success'
              ? 'border-emerald-500/30'
              : 'border-rose-500/30'
          }`}
          style={{background: '#ffffff'}}
        >
          <div className="flex items-center gap-2 font-bold text-sm">
            {message.type === 'success' ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-500" />
            ) : (
              <AlertCircle className="w-5 h-5 text-rose-500" />
            )}
            <span style={{color: message.type === 'success' ? '#059669' : '#dc2626'}}>{message.text}</span>
          </div>

          {message.details && (
            <div className="p-3 rounded-xl border font-mono text-[11px] space-y-1" style={{background: 'rgba(0,0,0,0.05)', borderColor: 'rgba(0,0,0,0.1)'}}>
              <div style={{color: '#334155'}}>Rows Inserted: <span className="font-bold" style={{color: '#0284c7'}}>{message.details.rows_inserted || message.details.machines_count}</span></div>
              {message.details.columns_detected && (
                <div style={{color: '#334155'}}>Columns Detected: {message.details.columns_detected.join(', ')}</div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
