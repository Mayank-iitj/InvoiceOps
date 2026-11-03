export type UserRole = 
  | 'ap_clerk'
  | 'procurement_owner'
  | 'finance_approver'
  | 'invoice_intake_agent'
  | 'invoice_match_agent'
  | 'ap_admin';

export interface InvoiceItem {
  invoice_id: string;
  vendor_id?: string;
  invoice_number?: string;
  invoice_date?: string;
  currency?: string;
  invoice_total?: string;
  po_id?: string;
  status: string;
  version: number;
}

export interface InvoiceLine {
  line_number: number;
  sku?: string;
  description: string;
  quantity: string;
  unit_price: string;
  net_amount: string;
  tax_rate?: string;
  tax_amount?: string;
  gross_amount?: string;
  source_page?: number;
  source_excerpt?: string;
  confidence?: string;
}

export interface DocumentItem {
  document_id: string;
  invoice_id: string;
  filename: string;
  mime_type: string;
  size_bytes: number;
  sha256: string;
  document_type: string;
  extraction_status?: string;
  created_at?: string;
}

export interface MatchCheck {
  code: string;
  status: 'pass' | 'fail' | 'unknown';
  severity: 'info' | 'warning' | 'blocking';
  message: string;
  expected?: string;
  actual?: string;
  source_refs: string[];
}

export interface MatchRun {
  match_run_id: string;
  invoice_id: string;
  overall_status: 'PASS' | 'BLOCKED' | 'NEEDS_HUMAN';
  invoice_version: number;
  po_version?: number;
  grn_version_fingerprint?: string;
  policy_version: string;
  checks: MatchCheck[];
  executed_by?: string;
  created_at?: string;
}

export interface ExceptionItem {
  exception_id: string;
  invoice_id?: string;
  match_run_id?: string;
  code: string;
  severity: string;
  status: 'open' | 'resolved' | 'overridden';
  owner_role: string;
  description: string;
  expected_value?: string;
  actual_value?: string;
  source_refs?: string[];
  created_at?: string;
  resolved_at?: string;
  resolved_by?: string;
}

export interface ApprovalItem {
  approval_id: string;
  invoice_id: string;
  decision: string;
  approver_id: string;
  created_at: string;
}

export interface PaymentReadyRecord {
  payment_ready_record_id: string;
  invoice_id: string;
  approval_id: string;
  approved_amount: string;
  currency: string;
  status: string;
  created_at: string;
  payment_executed: boolean;
  invoice_number?: string;
  vendor_id?: string;
}

export interface AuditEventItem {
  event_id: string;
  occurred_at: string;
  actor_id: string;
  actor_type: string;
  action: string;
  entity_type: string;
  entity_id: string;
  reason?: string;
  before_state?: string;
  after_state?: string;
  source_refs?: string[];
  request_id?: string;
}

export interface InvoiceDetail {
  invoice_id: string;
  vendor_id: string;
  vendor_name?: string;
  invoice_number: string;
  normalized_invoice_number?: string;
  invoice_date: string;
  po_id?: string;
  currency: string;
  subtotal?: string;
  tax_total?: string;
  invoice_total: string;
  status: string;
  version: number;
  created_by?: string;
  created_at: string;
  updated_at: string;
  lines: InvoiceLine[];
  documents: DocumentItem[];
  latest_match_run?: MatchRun;
  open_exceptions: ExceptionItem[];
  approvals: ApprovalItem[];
  payment_ready_record?: PaymentReadyRecord;
}

export interface PolicySettings {
  policy_version: string;
  default_currency: string;
  quantity_tolerance: string;
  price_variance_percent: string;
  price_variance_absolute_inr: string;
  price_variance_absolute_paise: string;
  extraction_confidence_threshold: number;
  audit_retention_days: number;
  max_upload_mb: number;
}

