import React from 'react';
import { ShieldCheck, Database, RefreshCw, Sparkles, Sun, Moon, FileText } from 'lucide-react';

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onRefreshData: () => void;
  theme: string;
  toggleTheme: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  onRefreshData,
  theme,
  toggleTheme
}) => {
  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800 px-6 py-4 mb-6">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Brand Logo & Badge */}
        <div className="flex items-center space-x-3">
          <img 
            src="/yash_logo.png" 
            className="h-9 object-contain rounded-md bg-white p-1" 
            alt="Yash Technologies Logo" 
          />
          <span className="px-2 py-0.5 text-[9px] font-bold tracking-wider rounded-full flex items-center gap-1 data-qa-badge">
            <ShieldCheck className="w-2.5 h-2.5" /> DATA QA STUDIO
          </span>
        </div>

        {/* Tab Navigation */}
        <nav className="flex items-center space-x-1 bg-slate-900/90 p-1.5 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('qa')}
            className={`px-4 py-2 text-xs font-semibold rounded-lg transition-all flex items-center gap-2 ${
              activeTab === 'qa'
                ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" /> QA Studio
          </button>
          
          <button
            onClick={() => setActiveTab('documents')}
            className={`px-4 py-2 text-xs font-semibold rounded-lg transition-all flex items-center gap-2 ${
              activeTab === 'documents'
                ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <FileText className="w-3.5 h-3.5" /> Documents
          </button>

          <button
            onClick={() => setActiveTab('ingest')}
            className={`px-4 py-2 text-xs font-semibold rounded-lg transition-all flex items-center gap-2 ${
              activeTab === 'ingest'
                ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Database className="w-3.5 h-3.5" /> Data Ingestion
          </button>
        </nav>

        {/* Refresh, Theme Switcher */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onRefreshData}
            title="Refresh Database State"
            className="p-2 rounded-lg bg-slate-800/70 hover:bg-slate-700/70 text-slate-300 transition"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          <button
            onClick={toggleTheme}
            title={theme === 'dark' ? 'Switch to Light Theme' : 'Switch to Dark Theme'}
            className="p-2 rounded-lg bg-slate-800/70 hover:bg-slate-700/70 text-cyan-400 transition flex items-center justify-center"
          >
            {theme === 'dark' ? (
              <Sun className="w-4 h-4 text-amber-400" />
            ) : (
              <Moon className="w-4 h-4 text-blue-500" />
            )}
          </button>
        </div>

      </div>
    </header>
  );
};
