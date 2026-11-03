import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Text, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from backend.app.database import Base

def utcnow_iso():
    return datetime.now(timezone.utc).isoformat()

def gen_uuid():
    return str(uuid.uuid4())

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(String, primary_key=True)
    legal_name = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    currency = Column(String, nullable=False, default="INR")
    is_active = Column(Integer, nullable=False, default=1)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(String, nullable=False, default=utcnow_iso)
    updated_at = Column(String, nullable=False, default=utcnow_iso)

    purchase_orders = relationship("PurchaseOrder", back_populates="vendor")
    invoices = relationship("Invoice", back_populates="vendor")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(String, primary_key=True)
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=False)
    currency = Column(String, nullable=False)
    status = Column(String, nullable=False, default="open")
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(String, nullable=False, default=utcnow_iso)
    updated_at = Column(String, nullable=False, default=utcnow_iso)

    vendor = relationship("Vendor", back_populates="purchase_orders")
    lines = relationship("PurchaseOrderLine", back_populates="purchase_order", cascade="all, delete-orphan")
    goods_receipts = relationship("GoodsReceipt", back_populates="purchase_order")
    invoices = relationship("Invoice", back_populates="purchase_order")


class PurchaseOrderLine(Base):
    __tablename__ = "purchase_order_lines"

    id = Column(String, primary_key=True)
    purchase_order_id = Column(String, ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False)
    line_number = Column(Integer, nullable=False)
    sku = Column(String, nullable=True)
    description = Column(String, nullable=False)
    ordered_qty = Column(String, nullable=False)
    unit_price = Column(String, nullable=False)
    uom = Column(String, nullable=False, default="each")

    __table_args__ = (
        UniqueConstraint("purchase_order_id", "line_number", name="uq_po_line_number"),
    )

    purchase_order = relationship("PurchaseOrder", back_populates="lines")
    grn_lines = relationship("GoodsReceiptLine", back_populates="po_line")


class GoodsReceipt(Base):
    __tablename__ = "goods_receipts"

    id = Column(String, primary_key=True)
    purchase_order_id = Column(String, ForeignKey("purchase_orders.id"), nullable=False)
    status = Column(String, nullable=False, default="accepted")
    received_at = Column(String, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(String, nullable=False, default=utcnow_iso)

    purchase_order = relationship("PurchaseOrder", back_populates="goods_receipts")
    lines = relationship("GoodsReceiptLine", back_populates="goods_receipt", cascade="all, delete-orphan")


class GoodsReceiptLine(Base):
    __tablename__ = "goods_receipt_lines"

    id = Column(String, primary_key=True)
    goods_receipt_id = Column(String, ForeignKey("goods_receipts.id", ondelete="CASCADE"), nullable=False)
    po_line_id = Column(String, ForeignKey("purchase_order_lines.id"), nullable=False)
    accepted_qty = Column(String, nullable=False)
    rejected_qty = Column(String, nullable=False, default="0")

    goods_receipt = relationship("GoodsReceipt", back_populates="lines")
    po_line = relationship("PurchaseOrderLine", back_populates="grn_lines")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String, primary_key=True)
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=False)
    invoice_number = Column(String, nullable=False)
    normalized_invoice_number = Column(String, nullable=False)
    invoice_date = Column(String, nullable=False)
    purchase_order_id = Column(String, ForeignKey("purchase_orders.id"), nullable=True)
    currency = Column(String, nullable=False, default="INR")
    subtotal = Column(String, nullable=True)
    tax_total = Column(String, nullable=True)
    invoice_total = Column(String, nullable=False)
    status = Column(String, nullable=False, default="draft")
    version = Column(Integer, nullable=False, default=1)
    created_by = Column(String, nullable=False)
    created_at = Column(String, nullable=False, default=utcnow_iso)
    updated_at = Column(String, nullable=False, default=utcnow_iso)

    __table_args__ = (
        Index("idx_invoices_status", "status"),
        Index("idx_invoices_duplicate_key", "vendor_id", "normalized_invoice_number"),
        Index("idx_invoices_vendor", "vendor_id"),
    )

    vendor = relationship("Vendor", back_populates="invoices")
    purchase_order = relationship("PurchaseOrder", back_populates="invoices")
    documents = relationship("Document", back_populates="invoice", cascade="all, delete-orphan")
    lines = relationship("InvoiceLine", back_populates="invoice", cascade="all, delete-orphan")
    extractions = relationship("Extraction", back_populates="invoice", cascade="all, delete-orphan")
    match_runs = relationship("MatchRun", back_populates="invoice", cascade="all, delete-orphan")
    exceptions = relationship("ExceptionRecord", back_populates="invoice", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="invoice")
    payment_ready_record = relationship("PaymentReadyRecord", back_populates="invoice", uselist=False)


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=gen_uuid)
    invoice_id = Column(String, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    original_filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    sha256 = Column(String, nullable=False)
    document_type = Column(String, nullable=False)
    created_by = Column(String, nullable=False)
    created_at = Column(String, nullable=False, default=utcnow_iso)

    __table_args__ = (
        Index("idx_documents_sha256", "sha256"),
    )

    invoice = relationship("Invoice", back_populates="documents")


class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    id = Column(String, primary_key=True, default=gen_uuid)
    invoice_id = Column(String, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    line_number = Column(Integer, nullable=False)
    sku = Column(String, nullable=True)
    description = Column(String, nullable=False)
    quantity = Column(String, nullable=False)
    unit_price = Column(String, nullable=False)
    net_amount = Column(String, nullable=False)
    tax_rate = Column(String, nullable=True)
    tax_amount = Column(String, nullable=True)
    gross_amount = Column(String, nullable=True)
    source_page = Column(Integer, nullable=True)
    source_excerpt = Column(Text, nullable=True)
    confidence = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint("invoice_id", "line_number", name="uq_invoice_line_number"),
    )

    invoice = relationship("Invoice", back_populates="lines")


class Extraction(Base):
    __tablename__ = "extractions"

    id = Column(String, primary_key=True, default=gen_uuid)
    invoice_id = Column(String, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), nullable=True)
    extractor_actor_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    payload_json = Column(Text, nullable=False)
    confidence_summary = Column(Text, nullable=True)
    confirmed_by = Column(String, nullable=True)
    confirmed_at = Column(String, nullable=True)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(String, nullable=False, default=utcnow_iso)

    invoice = relationship("Invoice", back_populates="extractions")


class MatchRun(Base):
    __tablename__ = "match_runs"

    id = Column(String, primary_key=True, default=gen_uuid)
    invoice_id = Column(String, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    invoice_version = Column(Integer, nullable=False)
    po_version = Column(Integer, nullable=True)
    grn_version_fingerprint = Column(String, nullable=True)
    policy_version = Column(String, nullable=False)
    overall_status = Column(String, nullable=False) # PASS, BLOCKED, NEEDS_HUMAN
    checks_json = Column(Text, nullable=False)
    executed_by = Column(String, nullable=False)
    created_at = Column(String, nullable=False, default=utcnow_iso)

    invoice = relationship("Invoice", back_populates="match_runs")
    exceptions = relationship("ExceptionRecord", back_populates="match_run")


class ExceptionRecord(Base):
    __tablename__ = "exceptions"

    id = Column(String, primary_key=True, default=gen_uuid)
    invoice_id = Column(String, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    match_run_id = Column(String, ForeignKey("match_runs.id"), nullable=True)
    code = Column(String, nullable=False)
    severity = Column(String, nullable=False) # info, warning, blocking
    status = Column(String, nullable=False, default="open") # open, resolved, overridden
    owner_role = Column(String, nullable=False)
    description = Column(String, nullable=False)
    expected_value = Column(String, nullable=True)
    actual_value = Column(String, nullable=True)
    source_refs_json = Column(Text, nullable=False, default="[]")
    created_at = Column(String, nullable=False, default=utcnow_iso)
    resolved_at = Column(String, nullable=True)
    resolved_by = Column(String, nullable=True)

    __table_args__ = (
        Index("idx_exceptions_invoice_status", "invoice_id", "status"),
    )

    invoice = relationship("Invoice", back_populates="exceptions")
    match_run = relationship("MatchRun", back_populates="exceptions")
    resolution_proposals = relationship("ResolutionProposal", back_populates="exception", cascade="all, delete-orphan")


class ResolutionProposal(Base):
    __tablename__ = "resolution_proposals"

    id = Column(String, primary_key=True, default=gen_uuid)
    exception_id = Column(String, ForeignKey("exceptions.id", ondelete="CASCADE"), nullable=False)
    proposer_id = Column(String, nullable=False)
    proposal_type = Column(String, nullable=False)
    rationale = Column(String, nullable=False)
    evidence_refs_json = Column(Text, nullable=False, default="[]")
    proposed_payload_json = Column(Text, nullable=False, default="{}")
    status = Column(String, nullable=False, default="pending_human_review")
    created_at = Column(String, nullable=False, default=utcnow_iso)

    exception = relationship("ExceptionRecord", back_populates="resolution_proposals")


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String, primary_key=True, default=gen_uuid)
    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=False)
    match_run_id = Column(String, ForeignKey("match_runs.id"), nullable=False)
    decision = Column(String, nullable=False) # approved, rejected
    comment = Column(String, nullable=False)
    approver_id = Column(String, nullable=False)
    approver_role = Column(String, nullable=False)
    idempotency_key_hash = Column(String, nullable=False, unique=True)
    created_at = Column(String, nullable=False, default=utcnow_iso)

    invoice = relationship("Invoice", back_populates="approvals")


class PaymentReadyRecord(Base):
    __tablename__ = "payment_ready_records"

    id = Column(String, primary_key=True, default=gen_uuid)
    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=False, unique=True)
    approval_id = Column(String, ForeignKey("approvals.id"), nullable=False, unique=True)
    approved_amount = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    status = Column(String, nullable=False, default="ready_for_downstream_payment")
    created_at = Column(String, nullable=False, default=utcnow_iso)
    created_by = Column(String, nullable=False)

    invoice = relationship("Invoice", back_populates="payment_ready_record")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String, primary_key=True, default=gen_uuid)
    occurred_at = Column(String, nullable=False, default=utcnow_iso)
    actor_id = Column(String, nullable=False)
    actor_type = Column(String, nullable=False) # human, agent, system
    action = Column(String, nullable=False)
    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=True)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    before_state = Column(String, nullable=True)
    after_state = Column(String, nullable=True)
    reason = Column(String, nullable=True)
    source_refs_json = Column(Text, nullable=False, default="[]")
    request_id = Column(String, nullable=True)
    idempotency_key_hash = Column(String, nullable=True)

    __table_args__ = (
        Index("idx_audit_invoice_time", "invoice_id", "occurred_at"),
    )


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"

    id = Column(String, primary_key=True, default=gen_uuid)
    key_hash = Column(String, nullable=False, unique=True)
    actor_id = Column(String, nullable=False)
    operation = Column(String, nullable=False)
    request_hash = Column(String, nullable=False)
    response_json = Column(Text, nullable=False)
    created_at = Column(String, nullable=False, default=utcnow_iso)


class SwitchMessage(Base):
    __tablename__ = "switch_messages"

    id = Column(String, primary_key=True, default=gen_uuid)
    room_id = Column(String, nullable=False, default="room_invoiceops_ap", index=True)
    thread_id = Column(String, nullable=False, default="thread_main", index=True)
    sender_id = Column(String, nullable=False)
    sender_name = Column(String, nullable=False)
    sender_role = Column(String, nullable=False) # agent, human, system
    avatar = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    mentions_json = Column(Text, nullable=False, default="[]")
    evidence_refs_json = Column(Text, nullable=False, default="[]")
    action_type = Column(String, nullable=True) # intake_report, match_exception, procurement_override, finance_approval, chat
    action_payload_json = Column(Text, nullable=False, default="{}")
    created_at = Column(String, nullable=False, default=utcnow_iso)

    __table_args__ = (
        Index("idx_switch_room_thread_time", "room_id", "thread_id", "created_at"),
    )


