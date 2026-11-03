import { UserRole } from '../types';

let currentRole: UserRole = 'ap_clerk';
let currentActorId: string = 'ap_clerk_user';

export const setGlobalRole = (role: UserRole, actorId?: string) => {
  currentRole = role;
  currentActorId = actorId || `${role}_user`;
  localStorage.setItem('invoiceops_role', role);
  localStorage.setItem('invoiceops_actor_id', currentActorId);
};

export const getGlobalRole = (): UserRole => {
  const saved = localStorage.getItem('invoiceops_role') as UserRole;
  if (saved) currentRole = saved;
  return currentRole;
};

export const getGlobalActorId = (): string => {
  const saved = localStorage.getItem('invoiceops_actor_id');
  if (saved) currentActorId = saved;
  return currentActorId;
};

const API_BASE = '/api/v1';

async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const headers = new Headers(options.headers || {});
  headers.set('X-Actor-Role', getGlobalRole());
  headers.set('X-Actor-ID', getGlobalActorId());
  
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const errorMsg = data?.error?.message || response.statusText || 'Request failed';
    const err = new Error(errorMsg);
    (err as any).status = response.status;
    (err as any).details = data?.error?.details;
    (err as any).code = data?.error?.code;
    throw err;
  }

  return data;
}

export const api = {
  // Invoices
  getInvoices: (status?: string, q?: string) => {
    const params = new URLSearchParams();
    if (status) params.set('status', status);
    if (q) params.set('q', q);
    return fetchWithAuth(`/invoices?${params.toString()}`);
  },

  getInvoice: (id: string) => fetchWithAuth(`/invoices/${id}`),

  createInvoice: (payload: any) =>
    fetchWithAuth('/invoices', {
      method: 'POST',
      headers: { 'Idempotency-Key': `create-${Date.now()}-${Math.random().toString(36).substring(7)}` },
      body: JSON.stringify(payload),
    }),

  // Match
  runMatch: (invoiceId: string) =>
    fetchWithAuth(`/invoices/${invoiceId}/match-runs`, {
      method: 'POST',
      body: JSON.stringify({ policy_version: 'demo-policy-1.0' }),
    }),

  // Exceptions & Evidence
  attachEvidence: (invoiceId: string, exceptionId: string, payload: { source_type: string; source_ref: string; comment: string }) =>
    fetchWithAuth(`/invoices/${invoiceId}/exceptions/${exceptionId}/evidence`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // Approvals
  submitApproval: (invoiceId: string, decision: 'approved' | 'rejected', comment: string, matchRunId: string, idempotencyKey: string) =>
    fetchWithAuth(`/invoices/${invoiceId}/approvals`, {
      method: 'POST',
      headers: { 'Idempotency-Key': idempotencyKey },
      body: JSON.stringify({
        decision,
        comment,
        match_run_id: matchRunId,
      }),
    }),

  // Payment Ready
  createPaymentReady: (invoiceId: string, approvalId: string, idempotencyKey: string) =>
    fetchWithAuth(`/invoices/${invoiceId}/payment-ready-records`, {
      method: 'POST',
      headers: { 'Idempotency-Key': idempotencyKey },
      body: JSON.stringify({ approval_id: approvalId }),
    }),

  getPaymentReadyRecords: () => fetchWithAuth('/payment-ready-records'),

  // Audit Events
  getAuditEvents: (invoiceId: string) => fetchWithAuth(`/invoices/${invoiceId}/audit-events`),
  getGlobalAuditEvents: (limit: number = 100, action?: string) => {
    const params = new URLSearchParams({ limit: String(limit) });
    if (action) params.set('action', action);
    return fetchWithAuth(`/audit-events?${params.toString()}`);
  },

  // Vendors & Policy
  getVendors: () => fetchWithAuth('/vendors'),
  getPolicy: () => fetchWithAuth('/settings/policy'),

  // Demo seed/reset
  demoReset: () => fetchWithAuth('/demo/reset', { method: 'POST' }),
  demoSeed: () => fetchWithAuth('/demo/seed', { method: 'POST' }),

  // Switch Collaboration Room API
  getSwitchStatus: () => fetchWithAuth('/switch/status'),
  getSwitchMessages: (roomId: string = 'room_invoiceops_ap', threadId?: string) => {
    const params = threadId ? `?thread_id=${encodeURIComponent(threadId)}` : '';
    return fetchWithAuth(`/switch/rooms/${roomId}/messages${params}`);
  },
  postSwitchMessage: (roomId: string = 'room_invoiceops_ap', payload: any) =>
    fetchWithAuth(`/switch/rooms/${roomId}/messages`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  simulateSwitchWorkflow: (roomId: string = 'room_invoiceops_ap', invoiceId: string = 'INV-2026-1042') =>
    fetchWithAuth(`/switch/rooms/${roomId}/simulate-workflow?invoice_id=${encodeURIComponent(invoiceId)}`, {
      method: 'POST',
    }),
  resetSwitchRoom: (roomId: string = 'room_invoiceops_ap') =>
    fetchWithAuth(`/switch/rooms/${roomId}/reset`, {
      method: 'POST',
    }),
  getSwitchMCPManifest: () => fetchWithAuth('/switch/mcp'),
};

