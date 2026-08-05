import React, { useState, useEffect } from 'react';
import { Search, Filter, Cpu, AlertTriangle, CheckCircle, Clock, User, ShieldAlert, ChevronRight, X } from 'lucide-react';
import type { Machine } from '../types/dataTypes';
import { fetchMachines } from '../services/api';

const CATEGORIES = [
  "All Categories", "CNC Lathe", "Robotic Arm", "Hydraulic Press", 
  "3D Metal Printer", "Laser Cutter", "Injection Molding", "Conveyor Belt System", "AGV Transport"
];

const STATUSES = ["ALL", "OPERATIONAL", "MAINTENANCE_DUE", "BREAKDOWN", "WARNING"];

export const FleetDashboard: React.FC = () => {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [selectedMachine, setSelectedMachine] = useState<Machine | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const catParam = selectedCategory === 'All Categories' ? undefined : selectedCategory;
      const statusParam = selectedStatus === 'ALL' ? undefined : selectedStatus;
      const res = await fetchMachines(catParam, statusParam, search, 60, 0);
      setMachines(res.machines || []);
      setTotalCount(res.total || 0);
    } catch (err) {
      console.error('Failed to load fleet machines:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedCategory, selectedStatus, search]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'OPERATIONAL':
        return (
          <span className="px-2.5 py-1 text-[10px] font-bold text-emerald-400 bg-emerald-950/80 border border-emerald-500/30 rounded-full flex items-center gap-1">
            <CheckCircle className="w-3 h-3 text-emerald-400" /> Operational
          </span>
        );
      case 'MAINTENANCE_DUE':
        return (
          <span className="px-2.5 py-1 text-[10px] font-bold text-amber-400 bg-amber-950/80 border border-amber-500/30 rounded-full flex items-center gap-1">
            <Clock className="w-3 h-3 text-amber-400" /> Maintenance Due
          </span>
        );
      case 'BREAKDOWN':
        return (
          <span className="px-2.5 py-1 text-[10px] font-bold text-rose-400 bg-rose-950/80 border border-rose-500/30 rounded-full flex items-center gap-1">
            <ShieldAlert className="w-3 h-3 text-rose-400" /> Breakdown
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-1 text-[10px] font-bold text-cyan-400 bg-cyan-950/80 border border-cyan-500/30 rounded-full flex items-center gap-1">
            <AlertTriangle className="w-3 h-3 text-cyan-400" /> Warning
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Search & Filters Header */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Cpu className="w-5 h-5 text-cyan-400" /> 1,000 Machine Fleet Monitor
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Showing {machines.length} of {totalCount} monitored industrial machines
            </p>
          </div>

          {/* Search Box */}
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by Machine ID (MAC-0012), Name, or Location..."
              className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50"
            />
          </div>
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center justify-between gap-4 pt-2 border-t border-slate-800/80">
          {/* Categories */}
          <div className="flex flex-wrap gap-1.5">
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                  selectedCategory === cat
                    ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                    : 'bg-slate-900 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Status Dropdown */}
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-xs text-slate-400 font-medium">Status:</span>
            <div className="flex gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800">
              {STATUSES.map((st) => (
                <button
                  key={st}
                  onClick={() => setSelectedStatus(st)}
                  className={`px-2.5 py-1 rounded text-[10px] font-bold transition ${
                    selectedStatus === st
                      ? 'bg-slate-800 text-cyan-400 border border-cyan-500/30'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {st}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Grid of Machines */}
      {loading ? (
        <div className="glass-panel p-12 rounded-2xl border border-slate-800 text-center text-slate-400 text-xs flex items-center justify-center gap-2">
          <div className="animate-spin rounded-full h-5 w-5 border-2 border-cyan-500 border-t-transparent"></div>
          <span>Loading 1,000 Industrial Machine Dataset from DuckDB...</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {machines.map((m) => (
            <div
              key={m.machine_id}
              onClick={() => setSelectedMachine(m)}
              className="glass-panel p-5 rounded-xl border border-slate-800 hover:border-cyan-500/40 hover:bg-slate-900/80 transition cursor-pointer group space-y-3"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-cyan-400 group-hover:text-cyan-300">
                  {m.machine_id}
                </span>
                {getStatusBadge(m.status)}
              </div>

              <div>
                <h4 className="text-sm font-bold text-white group-hover:text-cyan-200 truncate">{m.name}</h4>
                <p className="text-[11px] text-slate-400">{m.location}</p>
              </div>

              {/* Health Score Bar */}
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="text-slate-400 font-medium">Health Score</span>
                  <span className="text-slate-200 font-mono font-bold">{m.health_score}%</span>
                </div>
                <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      m.health_score >= 90
                        ? 'bg-emerald-400'
                        : m.health_score >= 70
                        ? 'bg-amber-400'
                        : 'bg-rose-500'
                    }`}
                    style={{ width: `${m.health_score}%` }}
                  ></div>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
                <div className="flex items-center gap-1">
                  <User className="w-3 h-3 text-slate-500" />
                  <span className="truncate max-w-[110px]">{m.current_operator}</span>
                </div>
                <span className="text-slate-500 flex items-center gap-0.5">
                  Details <ChevronRight className="w-3 h-3" />
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Machine Detail Modal */}
      {selectedMachine && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-md p-4">
          <div className="glass-panel-glow max-w-lg w-full p-6 rounded-2xl border border-cyan-500/30 text-slate-100 shadow-2xl space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold text-cyan-400">{selectedMachine.machine_id}</span>
                  {getStatusBadge(selectedMachine.status)}
                </div>
                <h3 className="text-lg font-bold text-white mt-1">{selectedMachine.name}</h3>
                <p className="text-xs text-slate-400">{selectedMachine.category} | {selectedMachine.location}</p>
              </div>
              <button
                onClick={() => setSelectedMachine(null)}
                className="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4 text-xs">
              <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
                <div className="text-slate-400 font-semibold uppercase text-[10px]">Health Score</div>
                <div className="text-lg font-bold text-cyan-400 mt-0.5">{selectedMachine.health_score}%</div>
              </div>
              <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
                <div className="text-slate-400 font-semibold uppercase text-[10px]">Total Downtime</div>
                <div className="text-lg font-bold text-rose-400 mt-0.5">{selectedMachine.total_downtime_hours} hrs</div>
              </div>
              <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
                <div className="text-slate-400 font-semibold uppercase text-[10px]">Last Maintenance</div>
                <div className="text-xs font-medium text-slate-200 mt-1">{selectedMachine.last_maintenance}</div>
              </div>
              <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
                <div className="text-slate-400 font-semibold uppercase text-[10px]">Next Scheduled</div>
                <div className="text-xs font-medium text-amber-400 mt-1">{selectedMachine.next_scheduled_maintenance}</div>
              </div>
            </div>

            <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-1">
              <div className="text-[10px] text-slate-400 font-semibold uppercase">Assigned Operator</div>
              <div className="text-sm font-bold text-white flex items-center gap-2">
                <User className="w-4 h-4 text-cyan-400" />
                {selectedMachine.current_operator}
              </div>
            </div>

            <button
              onClick={() => setSelectedMachine(null)}
              className="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold rounded-xl transition"
            >
              Close Inspector
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
