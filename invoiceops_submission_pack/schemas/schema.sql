PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS vendors (
  id TEXT PRIMARY KEY,
  legal_name TEXT NOT NULL,
  display_name TEXT NOT NULL,
  currency TEXT NOT NULL DEFAULT 'INR',
  is_active INTEGER NOT NULL DEFAULT 1,
  version INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS purchase_orders (
  id TEXT PRIMARY KEY,
  vendor_id TEXT NOT NULL REFERENCES vendors(id),
  currency TEXT NOT NULL,
  status TEXT NOT NULL,
  version INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS purchase_order_lines (
  id TEXT PRIMARY KEY,
  purchase_order_id TEXT NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
  line_number INTEGER NOT NULL,
  sku TEXT,
  description TEXT NOT NULL,
  ordered_qty TEXT NOT NULL,
  unit_price TEXT NOT NULL,
  uom TEXT NOT NULL,
  UNIQUE(purchase_order_id, line_number)
);

CREATE TABLE IF NOT EXISTS goods_receipts (
  id TEXT PRIMARY KEY,
  purchase_order_id TEXT NOT NULL REFERENCES purchase_orders(id),
  status TEXT NOT NULL,
  received_at TEXT NOT NULL,
  version INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS goods_receipt_lines (
  id TEXT PRIMARY KEY,
  goods_receipt_id TEXT NOT NULL REFERENCES goods_receipts(id) ON DELETE CASCADE,
  po_line_id TEXT NOT NULL REFERENCES purchase_order_lines(id),
  accepted_qty TEXT NOT NULL,
  rejected_qty TEXT NOT NULL DEFAULT '0'
);

CREATE TABLE IF NOT EXISTS invoices (
  id TEXT PRIMARY KEY,
  vendor_id TEXT NOT NULL REFERENCES vendors(id),
  invoice_number TEXT NOT NULL,
  normalized_invoice_number TEXT NOT NULL,
  invoice_date TEXT NOT NULL,
  purchase_order_id TEXT REFERENCES purchase_orders(id),
  currency TEXT NOT NULL,
  subtotal TEXT,
  tax_total TEXT,
  invoice_total TEXT NOT NULL,
  status TEXT NOT NULL,
  version INTEGER NOT NULL DEFAULT 1,
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_duplicate_key ON invoices(vendor_id, normalized_invoice_number);
CREATE INDEX IF NOT EXISTS idx_invoices_vendor ON invoices(vendor_id);

CREATE TABLE IF NOT EXISTS documents (
  id TEXT PRIMARY KEY,
  invoice_id TEXT NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
  original_filename TEXT NOT NULL,
  storage_path TEXT NOT NULL,
  mime_type TEXT NOT NULL,
  size_bytes INTEGER NOT NULL,
  sha256 TEXT NOT NULL,
  document_type TEXT NOT NULL,
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_documents_sha256 ON documents(sha256);

CREATE TABLE IF NOT EXISTS invoice_lines (
  id TEXT PRIMARY KEY,
  invoice_id TEXT NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
  line_number INTEGER NOT NULL,
  sku TEXT,
  description TEXT NOT NULL,
  quantity TEXT NOT NULL,
  unit_price TEXT NOT NULL,
  net_amount TEXT NOT NULL,
  tax_rate TEXT,
  tax_amount TEXT,
  gross_amount TEXT,
  source_page INTEGER,
  source_excerpt TEXT,
  confidence TEXT,
  UNIQUE(invoice_id, line_number)
);

CREATE TABLE IF NOT EXISTS extractions (
  id TEXT PRIMARY KEY,
  invoice_id TEXT NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
  document_id TEXT REFERENCES documents(id),
  extractor_actor_id TEXT NOT NULL,
  status TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  confidence_summary TEXT,
  confirmed_by TEXT,
  confirmed_at TEXT,
  version INTEGER NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS match_runs (
  id TEXT PRIMARY KEY,
  invoice_id TEXT NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
  invoice_version INTEGER NOT NULL,
  po_version INTEGER,
  grn_version_fingerprint TEXT,
  policy_version TEXT NOT NULL,
  overall_status TEXT NOT NULL,
  checks_json TEXT NOT NULL,
  executed_by TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS exceptions (
  id TEXT PRIMARY KEY,
  invoice_id TEXT NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
  match_run_id TEXT REFERENCES match_runs(id),
  code TEXT NOT NULL,
  severity TEXT NOT NULL,
  status TEXT NOT NULL,
  owner_role TEXT NOT NULL,
  description TEXT NOT NULL,
  expected_value TEXT,
  actual_value TEXT,
  source_refs_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  resolved_at TEXT,
  resolved_by TEXT
);
CREATE INDEX IF NOT EXISTS idx_exceptions_invoice_status ON exceptions(invoice_id, status);

CREATE TABLE IF NOT EXISTS resolution_proposals (
  id TEXT PRIMARY KEY,
  exception_id TEXT NOT NULL REFERENCES exceptions(id) ON DELETE CASCADE,
  proposer_id TEXT NOT NULL,
  proposal_type TEXT NOT NULL,
  rationale TEXT NOT NULL,
  evidence_refs_json TEXT NOT NULL,
  proposed_payload_json TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending_human_review',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS approvals (
  id TEXT PRIMARY KEY,
  invoice_id TEXT NOT NULL REFERENCES invoices(id),
  match_run_id TEXT NOT NULL REFERENCES match_runs(id),
  decision TEXT NOT NULL CHECK(decision IN ('approved','rejected')),
  comment TEXT NOT NULL,
  approver_id TEXT NOT NULL,
  approver_role TEXT NOT NULL,
  idempotency_key_hash TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS payment_ready_records (
  id TEXT PRIMARY KEY,
  invoice_id TEXT NOT NULL UNIQUE REFERENCES invoices(id),
  approval_id TEXT NOT NULL UNIQUE REFERENCES approvals(id),
  approved_amount TEXT NOT NULL,
  currency TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'ready_for_downstream_payment',
  created_at TEXT NOT NULL,
  created_by TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_events (
  id TEXT PRIMARY KEY,
  occurred_at TEXT NOT NULL,
  actor_id TEXT NOT NULL,
  actor_type TEXT NOT NULL,
  action TEXT NOT NULL,
  invoice_id TEXT REFERENCES invoices(id),
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  before_state TEXT,
  after_state TEXT,
  reason TEXT,
  source_refs_json TEXT NOT NULL DEFAULT '[]',
  request_id TEXT
);
CREATE INDEX IF NOT EXISTS idx_audit_invoice_time ON audit_events(invoice_id, occurred_at);

CREATE TABLE IF NOT EXISTS idempotency_records (
  id TEXT PRIMARY KEY,
  key_hash TEXT NOT NULL UNIQUE,
  actor_id TEXT NOT NULL,
  operation TEXT NOT NULL,
  request_hash TEXT NOT NULL,
  response_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);
