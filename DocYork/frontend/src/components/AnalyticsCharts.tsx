import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { Activity, DollarSign, Clock, Cpu, HeartPulse, RefreshCw } from 'lucide-react';
import type { AnalyticsOverview } from '../types/dataTypes';
import { fetchFleetAnalytics, fetchTableProfile } from '../services/api';

export const AnalyticsCharts: React.FC = () => {
  const [data, setData] = useState<AnalyticsOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTable, setActiveTable] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    setRefreshing(true);
    try {
      const profile = await fetchTableProfile();
      if (profile && profile.table_name) {
        setActiveTable(profile.table_name);
      }
      
      const res = await fetchFleetAnalytics();
      setData(res);
    } catch (err) {
      console.error('Failed to load fleet analytics:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading || !data) {
    return (
      <div className="glass-panel p-12 rounded-2xl border border-slate-800 text-center text-slate-400 text-xs flex items-center justify-center gap-2">
        <div className="animate-spin rounded-full h-5 w-5 border-2 border-cyan-500 border-t-transparent"></div>
        <span>Calculating DuckDB Aggregate Analytics...</span>
      </div>
    );
  }

  const { fleet_summary, downtime_by_category, cost_by_category, recent_maintenance_logs } = data;

  const isCustomTable = activeTable && activeTable !== "machines";
  
  // Dynamic labels based on dataset type
  let labelTotal = "Total Machines";
  let labelDowntime = "Total Downtime";
  let labelCost = "Total Maintenance Cost";
  let labelHealth = "Average Health Score";
  
  let valDowntimeSuffix = " hrs";
  let valCostPrefix = "$";
  let valHealthSuffix = "%";
  
  let chartTitle1 = "Total Downtime Hours by Machine Category";
  let chartTitle2 = "Total Maintenance Spend by Category ($)";
  
  let tableColId = "Log ID";
  let tableColName = "Machine";
  let tableColDate = "Date";
  let tableColCat = "Issue Type";
  let tableColVal1 = "Cost ($)";
  let tableColVal2 = "Downtime";
  let tableColDesc = "Parts Replaced";

  if (isCustomTable) {
    const tableLower = activeTable.toLowerCase();
    if (tableLower.includes("sales") || tableLower.includes("inventory")) {
      labelTotal = "Total Products";
      labelDowntime = "Total Quantity Sold";
      labelCost = "Total Revenue";
      labelHealth = "Avg Unit Price";
      valDowntimeSuffix = " units";
      valCostPrefix = "$";
      valHealthSuffix = "";
      chartTitle1 = "Quantity Sold by Category";
      chartTitle2 = "Average Unit Price by Category ($)";
      tableColId = "Item ID";
      tableColName = "Product Name";
      tableColDate = "Sales Date";
      tableColCat = "Category";
      tableColVal1 = "Unit Price ($)";
      tableColVal2 = "Qty Sold";
      tableColDesc = "Location";
    } else if (tableLower.includes("attendance") || tableLower.includes("employee")) {
      labelTotal = "Total Employees";
      labelDowntime = "Total Hours Worked";
      labelCost = "Present Logs Count";
      labelHealth = "Avg Daily Hours";
      valDowntimeSuffix = " hrs";
      valCostPrefix = "";
      valHealthSuffix = " hrs/day";
      chartTitle1 = "Total Hours Worked by Department";
      chartTitle2 = "Average Hours by Department";
      tableColId = "Employee ID";
      tableColName = "Employee Name";
      tableColDate = "Date";
      tableColCat = "Department";
      tableColVal1 = "Hours Worked";
      tableColVal2 = "Log Index";
      tableColDesc = "Status";
    } else if (tableLower.includes("fleet") || tableLower.includes("vehicle")) {
      labelTotal = "Total Fleet Vehicles";
      labelDowntime = "Total Mileage";
      labelCost = "Average Mileage";
      labelHealth = "Avg Fuel Economy";
      valDowntimeSuffix = " mi";
      valCostPrefix = "";
      valHealthSuffix = " MPG";
      chartTitle1 = "Total Mileage by Vehicle Type";
      chartTitle2 = "Avg Fuel Efficiency by Type (MPG)";
      tableColId = "Vehicle ID";
      tableColName = "Model";
      tableColDate = "Service Date";
      tableColCat = "Type";
      tableColVal1 = "Mileage";
      tableColVal2 = "Fuel Econ (MPG)";
      tableColDesc = "Assigned Driver";
    } else {
      labelTotal = "Total Records";
      labelDowntime = "Total Volume";
      labelCost = "Total Aggregate Value";
      labelHealth = "Average Value";
      valDowntimeSuffix = "";
      valCostPrefix = "";
      valHealthSuffix = "";
      chartTitle1 = "Volume distribution by Category";
      chartTitle2 = "Average value distribution by Category";
    }
  }

  return (
    <div className="space-y-6">
      {/* Title Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <Activity className="w-5 h-5 text-cyan-400" />
            <span>Interactive Analytics Dashboard</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            {isCustomTable ? `Displaying real-time analytical metrics for custom dataset: ${activeTable}` : 'Displaying fleet health indicators for 1,000 synthetic machines'}
          </p>
        </div>

        <button
          onClick={loadData}
          disabled={refreshing}
          className="px-3.5 py-1.5 bg-slate-900 border border-slate-800 hover:border-cyan-500/40 rounded-xl text-xs text-slate-300 flex items-center gap-1.5 transition disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-cyan-400 ${refreshing ? 'animate-spin' : ''}`} />
          <span>Refresh Analytics</span>
        </button>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Cards */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/5 rounded-full blur-2xl"></div>
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>{labelTotal}</span>
            <Cpu className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-white">{fleet_summary.total_machines}</div>
          <div className="text-[10px] text-slate-400">
            {isCustomTable ? 'Profiled via DuckDB' : `${fleet_summary.operational_count} Active Machines`}
          </div>
        </div>

        {/* Volume / Downtime Cards */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-amber-500/5 rounded-full blur-2xl"></div>
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>{labelDowntime}</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-400">
            {fleet_summary.total_downtime_hours.toLocaleString()}{valDowntimeSuffix}
          </div>
          <div className="text-[10px] text-slate-400">
            {isCustomTable ? 'Aggregated sum' : `${fleet_summary.maintenance_due_count} Maintenance Due`}
          </div>
        </div>

        {/* Cost / Revenue Cards */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-full blur-2xl"></div>
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>{labelCost}</span>
            <DollarSign className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400">
            {valCostPrefix}{fleet_summary.total_maintenance_cost.toLocaleString()}
          </div>
          <div className="text-[10px] text-slate-400">
            {isCustomTable ? 'Summed columns' : 'Aggregated maintenance cost'}
          </div>
        </div>

        {/* Health / Efficiency Cards */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-rose-500/5 rounded-full blur-2xl"></div>
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>{labelHealth}</span>
            <HeartPulse className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {fleet_summary.average_health_score}{valHealthSuffix}
          </div>
          <div className="text-[10px] text-slate-400">
            {isCustomTable ? 'Average value distribution' : `${fleet_summary.breakdown_count} Breakdowns`}
          </div>
        </div>
      </div>

      {/* Interactive Recharts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Chart 1: Category Bar Chart */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-850 pb-2">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Clock className="w-3.5 h-3.5 text-cyan-400" /> 
              {chartTitle1}
            </h3>
          </div>
          <div className="h-72">
            {downtime_by_category && downtime_by_category.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={downtime_by_category} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
                  <defs>
                    <linearGradient id="cyanGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#00f2fe" stopOpacity={0.9} />
                      <stop offset="100%" stopColor="#00c6ff" stopOpacity={0.3} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="category" stroke="#64748b" tick={{ fontSize: 9 }} angle={-25} textAnchor="end" />
                  <YAxis stroke="#64748b" tick={{ fontSize: 9 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.95)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px', fontSize: '11px', color: '#f1f5f9' }}
                    cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                  />
                  <Bar dataKey="downtime_hours" fill="url(#cyanGradient)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-500">
                No category metrics available for this dataset.
              </div>
            )}
          </div>
        </div>

        {/* Chart 2: Category Cost Chart */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-850 pb-2">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
              {chartTitle2}
            </h3>
          </div>
          <div className="h-72">
            {cost_by_category && cost_by_category.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={cost_by_category} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
                  <defs>
                    <linearGradient id="emeraldGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#10b981" stopOpacity={0.9} />
                      <stop offset="100%" stopColor="#059669" stopOpacity={0.3} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="category" stroke="#64748b" tick={{ fontSize: 9 }} angle={-25} textAnchor="end" />
                  <YAxis stroke="#64748b" tick={{ fontSize: 9 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.95)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px', fontSize: '11px', color: '#f1f5f9' }}
                    cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                  />
                  <Bar dataKey="cost" fill="url(#emeraldGradient)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-500">
                No cost metrics available for this dataset.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Dynamic Data Table Logs */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyan-400" /> 
          {isCustomTable ? 'Loaded Dataset Table (Recent 10 Records)' : 'Recent Incident Maintenance Logs'}
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase bg-slate-900/60">
                <th className="p-3">{tableColId}</th>
                <th className="p-3">{tableColName}</th>
                <th className="p-3">{tableColDate}</th>
                <th className="p-3">{tableColCat}</th>
                <th className="p-3">{tableColVal1}</th>
                <th className="p-3">{tableColVal2}</th>
                <th className="p-3">{tableColDesc}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {recent_maintenance_logs.map((log, idx) => (
                <tr key={idx} className="hover:bg-slate-900/40 transition font-mono">
                  <td className="p-3 text-cyan-400 font-bold">{log.log_id}</td>
                  <td className="p-3 text-slate-200 font-sans">{log.machine_id}</td>
                  <td className="p-3 text-slate-400">{log.date}</td>
                  <td className="p-3 text-slate-200 font-sans font-medium">{log.issue_type}</td>
                  <td className="p-3 text-emerald-400 font-bold">
                    {valCostPrefix}{log.cost.toLocaleString()}
                  </td>
                  <td className="p-3 text-amber-400">
                    {log.downtime_hours.toLocaleString()}{isCustomTable ? '' : ' hrs'}
                  </td>
                  <td className="p-3 text-slate-400 font-sans">{log.parts_replaced}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
