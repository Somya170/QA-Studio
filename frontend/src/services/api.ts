import type { QueryResponse, AnalyticsOverview } from '../types/dataTypes';

const API_BASE = '/api';

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Backend offline');
    return await res.json();
  } catch (err) {
    console.warn('API connection failed, falling back or retrying:', err);
    return { status: 'OFFLINE', mode: 'Fallback' };
  }
}

export async function executeQuery(query: string, filter_document?: string, filter_machine_id?: string, filter_category?: string): Promise<QueryResponse> {
  const res = await fetch(`${API_BASE}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, filter_document, filter_machine_id, filter_category })
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({ detail: 'API Error' }));
    throw new Error(errData.detail || 'Query execution failed');
  }
  return await res.json();
}

export async function uploadFile(file: File): Promise<{ task_id: string }> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/ingest`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) throw new Error('File upload failed');
  return await res.json();
}

export async function fetchIngestStatus(taskId: string): Promise<{ status: string; progress: number; message: string; result?: any; error?: string }> {
  const res = await fetch(`${API_BASE}/ingest/status/${taskId}`);
  if (!res.ok) throw new Error('Failed to fetch ingestion status');
  return await res.json();
}

export async function loadDemoData() {
  const res = await fetch(`${API_BASE}/demo-data`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Demo data generation failed');
  return await res.json();
}

export async function fetchMachines(category?: string, status?: string, search?: string, limit = 50, offset = 0) {
  const params = new URLSearchParams();
  if (category) params.append('category', category);
  if (status) params.append('status', status);
  if (search) params.append('search', search);
  params.append('limit', limit.toString());
  params.append('offset', offset.toString());

  const res = await fetch(`${API_BASE}/machines?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch machines');
  return await res.json();
}

export async function fetchFleetAnalytics(): Promise<AnalyticsOverview> {
  const res = await fetch(`${API_BASE}/analytics`);
  if (!res.ok) throw new Error('Failed to fetch fleet analytics');
  return await res.json();
}

export async function fetchTableProfile() {
  try {
    const res = await fetch(`${API_BASE}/table-profile`);
    if (!res.ok) throw new Error('Failed to fetch table profile');
    return await res.json();
  } catch (err) {
    console.error('Failed to load table profile:', err);
    return null;
  }
}
