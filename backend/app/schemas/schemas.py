from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"

class InvoiceLineBase(BaseModel):
    line_number: Optional[int] = None
    sku: Optional[str] = None
    description: str
    quantity: str
    unit_price: str
    net_amount: Optional[str] = None
    tax_rate: Optional[str] = None
    tax_amount: Optional[str] = None
    gross_amount: Optional[str] = None
    source_page: Optional[int] = None
    source_excerpt: Optional[str] = None
    confidence: Optional[str] = None

class InvoiceCreate(BaseModel):
    vendor_id: str
    invoice_number: str
    invoice_date: str
    po_id: Optional[str] = None
    currency: str = Field("INR", pattern="^[A-Z]{3}$")
    subtotal: Optional[str] = Field(None, pattern=r"^-?[0-9]+(\.[0-9]{1,2})?$")
    tax_total: Optional[str] = Field(None, pattern=r"^-?[0-9]+(\.[0-9]{1,2})?$")
    invoice_total: str = Field(..., pattern=r"^-?[0-9]+(\.[0-9]{1,2})?$")
    lines: Optional[List[InvoiceLineBase]] = None

class InvoiceResponse(BaseModel):
    invoice_id: str
    status: str
    version: int
    invoice_number: Optional[str] = None
    vendor_id: Optional[str] = None
    invoice_date: Optional[str] = None
    currency: Optional[str] = "INR"
    invoice_total: Optional[str] = None
    po_id: Optional[str] = None

class InvoiceListResponse(BaseModel):
    items: List[InvoiceResponse]
    next_cursor: Optional[str] = None

class DocumentResponse(BaseModel):
    document_id: str
    invoice_id: str
    filename: str
    mime_type: str
    size_bytes: int
    sha256: str
    document_type: str
    extraction_status: Optional[str] = "unprocessed"
    created_at: Optional[str] = None

class Evidence(BaseModel):
    field: str
    value: Optional[str] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    document_id: Optional[str] = None
    page: Optional[int] = None
    excerpt: Optional[str] = None

class ExtractionLineProposal(BaseModel):
    sku: Optional[str] = None
    description: str
    quantity: str
    unit_price: str
    net_amount: Optional[str] = None
    tax_amount: Optional[str] = None
    source_page: Optional[int] = None
    confidence: float = Field(1.0, ge=0.0, le=1.0)

class ExtractionProposal(BaseModel):
    document_id: str
    fields: List[Evidence]
    lines: List[ExtractionLineProposal]

class ExtractionConfirmation(BaseModel):
    confirmed: bool
    comment: str = Field(..., min_length=3)
    corrected_fields: Optional[Dict[str, Any]] = None

class ExtractionResponse(BaseModel):
    extraction_id: str
    invoice_id: str
    status: str
    requires_human_review: bool

class MatchCheck(BaseModel):
    code: str
    status: str # pass, fail, unknown
    severity: str = "blocking" # info, warning, blocking
    message: str
    expected: Optional[str] = None
    actual: Optional[str] = None
    source_refs: List[str] = []

class MatchRunResponse(BaseModel):
    match_run_id: str
    invoice_id: str
    overall_status: str # PASS, BLOCKED, NEEDS_HUMAN
    invoice_version: int
    po_version: Optional[int] = None
    grn_version_fingerprint: Optional[str] = None
    policy_version: str
    checks: List[MatchCheck]
    executed_by: Optional[str] = None
    created_at: Optional[str] = None

class ExceptionResponse(BaseModel):
    exception_id: str
    invoice_id: Optional[str] = None
    match_run_id: Optional[str] = None
    code: str
    severity: str = "blocking"
    status: str = "open"
    owner_role: str
    description: str
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    source_refs: Optional[List[str]] = []
    created_at: Optional[str] = None
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None

class EvidenceCreate(BaseModel):
    source_type: str # grn, po_amendment, human_confirmation, credit_note, other
    source_ref: str
    comment: str = Field(..., min_length=3)

class EvidenceResponse(BaseModel):
    evidence_id: str
    exception_id: str
    status: str

class ResolutionProposalCreate(BaseModel):
    proposal_type: str
    rationale: str
    evidence_refs: List[str]
    proposed_payload: Optional[Dict[str, Any]] = None

class ResolutionProposalResponse(BaseModel):
    proposal_id: str
    status: str = "pending_human_review"

class ApprovalDecision(BaseModel):
    decision: str = Field(..., pattern="^(approved|rejected)$")
    comment: str = Field(..., min_length=3)
    match_run_id: str
    expected_invoice_version: Optional[int] = None

class ApprovalResponse(BaseModel):
    approval_id: str
    invoice_id: str
    decision: str
    approver_id: str
    created_at: str

class PaymentReadyCreate(BaseModel):
    approval_id: str

class PaymentReadyRecordResponse(BaseModel):
    payment_ready_record_id: str
    invoice_id: str
    approval_id: str
    approved_amount: str
    currency: str
    status: str = "ready_for_downstream_payment"
    created_at: str
    payment_executed: bool = False

class AuditEventResponse(BaseModel):
    event_id: str
    occurred_at: str
    actor_id: str
    actor_type: str
    action: str
    entity_type: str
    entity_id: str
    reason: Optional[str] = None
    before_state: Optional[str] = None
    after_state: Optional[str] = None
    source_refs: Optional[List[str]] = []

class InvoiceDetailResponse(BaseModel):
    invoice_id: str
    vendor_id: str
    vendor_name: Optional[str] = None
    invoice_number: str
    normalized_invoice_number: Optional[str] = None
    invoice_date: str
    po_id: Optional[str] = None
    currency: str
    subtotal: Optional[str] = None
    tax_total: Optional[str] = None
    invoice_total: str
    status: str
    version: int
    created_by: Optional[str] = None
    created_at: str
    updated_at: str
    lines: List[Dict[str, Any]] = []
    documents: List[DocumentResponse] = []
    latest_match_run: Optional[MatchRunResponse] = None
    open_exceptions: List[ExceptionResponse] = []
    approvals: List[ApprovalResponse] = []
    payment_ready_record: Optional[PaymentReadyRecordResponse] = None
