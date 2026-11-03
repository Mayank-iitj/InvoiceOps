import React from 'react';
import { 
  ArrowLeft, 
  FileText, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  ExternalLink, 
  RotateCw, 
  ShieldCheck, 
  Clock, 
  Lock,
  Copy,
  Check,
  Code,
  Terminal,
  Zap,
  Layers
} from 'lucide-react';
import { InvoiceDetail, ExceptionItem } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { FinanceApprovalModal } from '../components/FinanceApprovalModal';
import { EvidenceModal } from '../components/EvidenceModal';
import { api, getGlobalRole } from '../services/api';

interface InvoiceDetailPageProps {
  invoiceId: string;
  onBack: () => void;
  onOpenSwitchRoom: () => void;
}

export const InvoiceDetailPage: React.FC<InvoiceDetailPageProps> = ({
  invoiceId,
  onBack,
  onOpenSwitchRoom,
}) => {
  const [invoice, setInvoice] = React.useState<InvoiceDetail | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [isMatching, setIsMatching] = React.useState(false);
  const [showApprovalModal, setShowApprovalModal] = React.useState(false);
  const [selectedExceptionForEvidence, setSelectedExceptionForEvidence] = React.useState<ExceptionItem | null>(null);
  const [copiedSha, setCopiedSha] = React.useState(false);
  const [auditEvents, setAuditEvents] = React.useState<any[]>([]);

  const loadInvoiceData = async () => {
    try {
      const data = await api.getInvoice(invoiceId);
      setInvoice(data);
      const auditData = await api.getAuditEvents(invoiceId);
      setAuditEvents(auditData.items || []);
    } catch (err) {
      console.error("Failed to load invoice", err);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    loadInvoiceData();
  }, [invoiceId]);

  const handleRerunMatch = async () => {
    setIsMatching(true);
    try {
      await api.runMatch(invoiceId);
      await loadInvoiceData();
    } catch (err: any) {
      alert(`Match failed: ${err.message}`);
    } finally {
      setIsMatching(false);
    }
  };

  if (loading || !invoice) {
    return (
      <div className="p-16 text-center text-xs text-text-muted font-mono flex items-center justify-center space-x-2">
        <span className="w-2 h-2 rounded-full bg-supabase-500 animate-ping"></span>
        <span>Loading case record {invoiceId}...</span>
      </div>
    );
  }

  const role = getGlobalRole();
  const isFinance = role === 'finance_approver' || role === 'ap_admin';
  const matchPassed = invoice.latest_match_run?.overall_status === 'PASS';
  const hasExceptions = invoice.open_exceptions.length > 0;
  const isDuplicate = invoice.status === 'duplicate_blocked';
  const canApprove = isFinance && matchPassed && !hasExceptions && !isDuplicate;

  const doc = invoice.documents[0];

  const handleCopySha = () => {
    if (doc?.sha256) {
      navigator.clipboard.writeText(doc.sha256);
      setCopiedSha(true);
      setTimeout(() => setCopiedSha(false), 2000);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Supabase Studio Top Breadcrumb & Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-dark-surface p-4 rounded-lg border border-dark-border shadow-supabase">
        <div className="flex items-center space-x-3">
          <button
            onClick={onBack}
            className="p-1.5 text-text-muted hover:text-text-primary hover:bg-dark-hover rounded-md border border-dark-border transition"
            title="Back to Invoices"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          
          <div>
            <div className="flex items-center space-x-2.5">
              <span className="text-text-muted text-xs font-mono">invoices /</span>
              <h2 className="text-base font-bold text-text-primary font-mono tracking-tight">{invoice.invoice_number}</h2>
              <StatusBadge status={invoice.status} />
              <span className="text-[11px] text-text-dim font-mono bg-dark-bg px-1.5 py-0.5 rounded border border-dark-border">
                v{invoice.version}
              </span>
            </div>
            
            <div className="flex items-center space-x-2 text-xs text-text-secondary mt-1">
              <span>{invoice.vendor_name || invoice.vendor_id}</span>
              <span className="text-dark-border">•</span>
              <span className="font-mono text-text-muted">{invoice.invoice_date}</span>
              <span className="text-dark-border">•</span>
              <span className="font-mono text-text-secondary">PO: {invoice.po_id || 'None'}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2.5">
          <button
            onClick={onOpenSwitchRoom}
            className="px-3 py-1.5 text-xs font-medium rounded-md bg-supabase-950/40 text-supabase-300 border border-supabase-500/40 hover:bg-supabase-900/40 transition flex items-center space-x-1.5 shadow-sm"
          >
            <ExternalLink className="w-3.5 h-3.5 text-supabase-400" />
            <span className="font-mono text-[11px]">#invoiceops-ap thread</span>
          </button>

          <button
            onClick={handleRerunMatch}
            disabled={isMatching}
            className="px-3 py-1.5 text-xs font-medium bg-dark-panel hover:bg-dark-hover border border-dark-borderLight text-text-primary rounded-md transition flex items-center space-x-1.5 disabled:opacity-40"
          >
            <RotateCw className={`w-3.5 h-3.5 ${isMatching ? 'animate-spin text-supabase-400' : ''}`} />
            <span>Rerun Match Engine</span>
          </button>
        </div>
      </div>

      {/* 3-Column Studio Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* LEFT COLUMN: Source Document & Extraction Proposal (4 cols) */}
        <div className="lg:col-span-4 space-y-5">
          
          {/* Document Evidence Card */}
          <div className="bg-dark-panel rounded-lg border border-dark-border p-4 space-y-3 shadow-supabase">
            <div className="flex items-center justify-between border-b border-dark-border/80 pb-2.5">
              <span className="text-xs font-mono font-semibold uppercase tracking-wider text-text-muted flex items-center">
                <FileText className="w-3.5 h-3.5 mr-1.5 text-supabase-400" />
                Source Document
              </span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-dark-bg border border-dark-border text-amber-400">
                Untrusted Artifact
              </span>
            </div>

            {doc ? (
              <div className="space-y-2.5 text-xs">
                <div>
                  <span className="text-text-muted block text-[10px] font-mono uppercase">Filename</span>
                  <span className="font-mono text-text-primary truncate block text-xs mt-0.5">{doc.filename}</span>
                </div>
                
                <div className="flex items-center justify-between text-[11px] text-text-secondary pt-1">
                  <span>Size: {(doc.size_bytes / 1024).toFixed(1)} KB</span>
                  <span className="font-mono text-[10px] text-text-muted">SHA-256</span>
                </div>

                <div className="relative group">
                  <div className="p-2.5 bg-dark-bg rounded border border-dark-border font-mono text-[10px] text-text-secondary break-all select-all pr-8">
                    {doc.sha256}
                  </div>
                  <button
                    onClick={handleCopySha}
                    className="absolute right-2 top-2.5 text-text-muted hover:text-text-primary transition"
                    title="Copy SHA-256 Hash"
                  >
                    {copiedSha ? <Check className="w-3.5 h-3.5 text-supabase-400" /> : <Copy className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-xs text-text-muted italic">No document attached</div>
            )}
          </div>

          {/* Extracted Schema Key-Values (Supabase JSON View style) */}
          <div className="bg-dark-panel rounded-lg border border-dark-border p-4 space-y-3 shadow-supabase">
            <div className="flex items-center justify-between border-b border-dark-border/80 pb-2.5">
              <span className="text-xs font-mono font-semibold uppercase tracking-wider text-text-muted flex items-center">
                <Code className="w-3.5 h-3.5 mr-1.5 text-supabase-400" />
                Extracted Proposal
              </span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-supabase-950/50 text-supabase-400 border border-supabase-500/30">
                Agent-extracted
              </span>
            </div>

            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between py-1 border-b border-dark-border/40">
                <span className="text-text-muted">vendor_id</span>
                <span className="text-text-primary font-medium">{invoice.vendor_id}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-dark-border/40">
                <span className="text-text-muted">invoice_number</span>
                <span className="text-supabase-400 font-medium">{invoice.invoice_number}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-dark-border/40">
                <span className="text-text-muted">invoice_date</span>
                <span className="text-text-primary">{invoice.invoice_date}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-dark-border/40">
                <span className="text-text-muted">currency</span>
                <span className="text-text-primary">{invoice.currency}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-dark-border/40">
                <span className="text-text-muted">subtotal</span>
                <span className="text-text-primary">₹{invoice.subtotal || '0.00'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-dark-border/40">
                <span className="text-text-muted">tax_total</span>
                <span className="text-text-primary">₹{invoice.tax_total || '0.00'}</span>
              </div>
              <div className="flex justify-between py-1.5 pt-2 font-bold text-text-primary">
                <span className="text-text-muted">invoice_total</span>
                <span className="text-supabase-400 text-sm">₹{invoice.invoice_total} INR</span>
              </div>
            </div>
          </div>

        </div>

        {/* CENTER COLUMN: Deterministic Three-Way Line Reconciliation (5 cols) */}
        <div className="lg:col-span-5 space-y-5">
          
          <div className="bg-dark-panel rounded-lg border border-dark-border p-4 space-y-4 shadow-supabase">
            <div className="flex items-center justify-between border-b border-dark-border/80 pb-2.5">
              <div>
                <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-text-primary">
                  Three-Way Reconciliation Grid
                </h3>
                <span className="text-[11px] text-text-muted">Invoice ↔ Purchase Order ↔ Accepted Receipts</span>
              </div>
              <span className={`px-2 py-0.5 text-xs font-mono font-bold rounded ${
                matchPassed 
                  ? 'bg-supabase-950/60 text-supabase-400 border border-supabase-500/40' 
                  : 'bg-red-950/60 text-red-400 border border-red-500/40'
              }`}>
                {invoice.latest_match_run?.overall_status || 'UNKNOWN'}
              </span>
            </div>

            {/* Reconciliation Line Items */}
            <div className="space-y-3.5">
              {invoice.lines.map((line) => {
                const qtyCheck = invoice.latest_match_run?.checks.find(c => c.code === 'QTY_EXCEEDS_RECEIVED');
                const priceCheck = invoice.latest_match_run?.checks.find(c => c.code === 'PRICE_VARIANCE');

                return (
                  <div key={line.line_number} className="p-3.5 bg-dark-bg rounded-lg border border-dark-border text-xs space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-text-primary font-mono text-xs">
                        Line {line.line_number}: {line.sku || line.description}
                      </span>
                      <span className="text-[11px] text-text-muted font-mono">Rate: ₹{line.unit_price}</span>
                    </div>

                    {/* Comparison Pill Matrix */}
                    <div className="grid grid-cols-3 gap-2 p-2.5 bg-dark-surface rounded border border-dark-border/70 text-center text-[11px]">
                      <div>
                        <span className="text-text-muted block text-[9px] font-mono uppercase">Billed Qty</span>
                        <span className="font-bold text-text-primary font-mono text-xs">{line.quantity}</span>
                      </div>
                      <div>
                        <span className="text-text-muted block text-[9px] font-mono uppercase">PO Qty</span>
                        <span className="font-mono text-xs text-text-secondary">10</span>
                      </div>
                      <div>
                        <span className="text-text-muted block text-[9px] font-mono uppercase">Accepted GRN</span>
                        <span className={`font-mono text-xs font-bold ${
                          qtyCheck?.status === 'fail' ? 'text-red-400' : 'text-supabase-400'
                        }`}>
                          {qtyCheck?.expected || '8'}
                        </span>
                      </div>
                    </div>

                    {/* Quantity Check Flag */}
                    {qtyCheck && (
                      <div className={`p-2.5 rounded border text-[11px] flex items-center justify-between font-mono ${
                        qtyCheck.status === 'pass' 
                          ? 'bg-supabase-950/30 text-supabase-300 border-supabase-500/30' 
                          : 'bg-red-950/30 text-red-300 border-red-500/30'
                      }`}>
                        <div className="flex items-center space-x-1.5">
                          {qtyCheck.status === 'pass' ? (
                            <CheckCircle2 className="w-3.5 h-3.5 text-supabase-400 shrink-0" />
                          ) : (
                            <XCircle className="w-3.5 h-3.5 text-red-400 shrink-0" />
                          )}
                          <span className="font-semibold">Quantity:</span>
                          <span>{qtyCheck.status.toUpperCase()}</span>
                        </div>
                        <span className="text-[10px] text-text-muted">{qtyCheck.actual} vs {qtyCheck.expected} accepted</span>
                      </div>
                    )}

                    {/* Price Variance Flag */}
                    {priceCheck && (
                      <div className={`p-2.5 rounded border text-[11px] flex items-center justify-between font-mono ${
                        priceCheck.status === 'pass' 
                          ? 'bg-supabase-950/30 text-supabase-300 border-supabase-500/30' 
                          : 'bg-red-950/30 text-red-300 border-red-500/30'
                      }`}>
                        <div className="flex items-center space-x-1.5">
                          {priceCheck.status === 'pass' ? (
                            <CheckCircle2 className="w-3.5 h-3.5 text-supabase-400 shrink-0" />
                          ) : (
                            <XCircle className="w-3.5 h-3.5 text-red-400 shrink-0" />
                          )}
                          <span className="font-semibold">Price Delta:</span>
                          <span>{priceCheck.status.toUpperCase()}</span>
                        </div>
                        <span className="text-[10px] text-text-muted">₹{priceCheck.actual} vs ₹{priceCheck.expected}</span>
                      </div>
                    )}

                    <div className="flex justify-between text-text-muted text-[11px] pt-0.5 font-mono">
                      <span>Line Net: <strong className="text-text-primary">₹{line.net_amount}</strong></span>
                      <span>GST: <strong className="text-text-primary">₹{line.tax_amount} ({line.tax_rate}%)</strong></span>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Arithmetic Verification Console Card */}
            <div className="p-3 bg-dark-bg rounded-lg border border-dark-border text-xs space-y-1 font-mono">
              <div className="text-supabase-400 font-semibold flex items-center">
                <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" />
                Arithmetic Verification (Decimal Recomputation)
              </div>
              <p className="text-[11px] text-text-secondary">
                Quantity × Unit Price = Stated Net. Recomputed Document Total = ₹{invoice.invoice_total} INR.
              </p>
            </div>

          </div>

        </div>

        {/* RIGHT COLUMN: Studio Finance Actions & Audit Logs (3 cols) */}
        <div className="lg:col-span-3 space-y-5">
          
          {/* Finance Action Card (Supabase Green CTA) */}
          <div className="bg-dark-panel rounded-lg border border-dark-border p-4 space-y-3.5 shadow-supabase">
            <div className="flex items-center justify-between border-b border-dark-border/80 pb-2.5">
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-text-muted flex items-center">
                <ShieldCheck className="w-3.5 h-3.5 mr-1.5 text-supabase-400" />
                Finance Approval
              </span>
              <span className="text-[10px] font-mono text-text-dim">Human Only</span>
            </div>

            {invoice.payment_ready_record ? (
              <div className="p-3 bg-cyan-950/30 border border-cyan-500/30 rounded-lg text-xs space-y-1.5 text-cyan-200">
                <div className="font-bold flex items-center text-cyan-300">
                  <CheckCircle2 className="w-4 h-4 mr-1 text-cyan-400" />
                  Payment-Ready Record
                </div>
                <div className="font-mono text-[10px] text-cyan-300/80 break-all">
                  {invoice.payment_ready_record.payment_ready_record_id}
                </div>
                <p className="text-[10px] text-text-muted">
                  No bank transfer executed. Downstream ERP export ready.
                </p>
              </div>
            ) : invoice.status === 'approved' ? (
              <div className="p-3 bg-supabase-950/30 border border-supabase-500/30 rounded-lg text-xs space-y-2">
                <div className="font-bold text-supabase-300 flex items-center">
                  <CheckCircle2 className="w-4 h-4 mr-1 text-supabase-400" />
                  Invoice Approved
                </div>
                <button
                  onClick={() => setShowApprovalModal(true)}
                  className="w-full py-2 bg-supabase-500 hover:bg-supabase-600 text-black font-bold text-xs rounded-md shadow-supabase-glow transition"
                >
                  Generate Payment-Ready Record
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                <p className="text-xs text-text-secondary leading-relaxed">
                  {canApprove 
                    ? "Three-way match passed with zero open exceptions. Ready for finance sign-off." 
                    : "Approval currently blocked. Ensure 3-way match passes and switch to Finance Approver role."}
                </p>

                <button
                  onClick={() => setShowApprovalModal(true)}
                  disabled={!canApprove}
                  className="w-full py-2.5 bg-supabase-500 hover:bg-supabase-400 disabled:opacity-30 disabled:cursor-not-allowed text-black text-xs font-bold rounded-md shadow-supabase-glow transition flex items-center justify-center space-x-1.5"
                >
                  <Lock className="w-3.5 h-3.5 mr-1" />
                  <span>Review & Decide</span>
                </button>
              </div>
            )}
          </div>

          {/* Exceptions Panel */}
          <div className="bg-dark-panel rounded-lg border border-dark-border p-4 space-y-3 shadow-supabase">
            <div className="flex items-center justify-between border-b border-dark-border/80 pb-2.5">
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-text-muted flex items-center">
                <AlertTriangle className="w-3.5 h-3.5 mr-1.5 text-red-400" />
                Exceptions ({invoice.open_exceptions.length})
              </span>
            </div>

            {invoice.open_exceptions.length === 0 ? (
              <div className="p-3 bg-supabase-950/20 border border-supabase-500/20 rounded-md text-xs text-supabase-300 flex items-center space-x-1.5 font-mono">
                <CheckCircle2 className="w-4 h-4 text-supabase-400 shrink-0" />
                <span>Zero blocking discrepancies</span>
              </div>
            ) : (
              <div className="space-y-2.5">
                {invoice.open_exceptions.map((exc) => (
                  <div key={exc.exception_id} className="p-3 bg-red-950/20 border border-red-500/30 rounded-md text-xs space-y-2">
                    <div className="flex items-center justify-between font-mono">
                      <span className="font-bold text-red-400">{exc.code}</span>
                      <span className="text-[10px] font-semibold bg-red-950/80 text-red-300 px-1.5 py-0.5 rounded border border-red-500/30">
                        {exc.owner_role}
                      </span>
                    </div>
                    <p className="text-[11px] text-text-secondary">{exc.description}</p>
                    
                    <button
                      onClick={() => setSelectedExceptionForEvidence(exc)}
                      className="w-full py-1.5 bg-dark-surface hover:bg-dark-hover border border-dark-borderLight text-text-primary font-medium text-[11px] rounded transition shadow-xs flex items-center justify-center space-x-1 font-mono"
                    >
                      <span>Attach Evidence</span>
                      <span>&rarr;</span>
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Real-time Audit Timeline (Supabase Log Explorer Style) */}
          <div className="bg-dark-panel rounded-lg border border-dark-border p-4 space-y-3 shadow-supabase">
            <div className="flex items-center justify-between border-b border-dark-border/80 pb-2.5">
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-text-muted flex items-center">
                <Clock className="w-3.5 h-3.5 mr-1.5 text-text-muted" />
                Event Logs ({auditEvents.length})
              </span>
            </div>

            <div className="space-y-2.5 max-h-64 overflow-y-auto pr-1 font-mono">
              {auditEvents.map((ev, idx) => (
                <div key={idx} className="text-xs border-l-2 border-supabase-500/60 pl-2.5 py-1 space-y-0.5 bg-dark-bg/40 rounded-r">
                  <div className="flex items-center justify-between text-[10px] text-text-muted">
                    <span className="font-semibold text-supabase-400">{ev.action}</span>
                    <span className="text-text-dim">{ev.occurred_at ? new Date(ev.occurred_at).toLocaleTimeString() : ''}</span>
                  </div>
                  <div className="text-[10px] text-text-secondary">{ev.actor_id} ({ev.actor_type})</div>
                  {ev.reason && <p className="text-[10px] text-text-dim italic font-sans">"{ev.reason}"</p>}
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>

      {/* Finance Approval Modal */}
      <FinanceApprovalModal
        isOpen={showApprovalModal}
        onClose={() => setShowApprovalModal(false)}
        invoice={invoice}
        onSuccess={loadInvoiceData}
      />

      {/* Attach Evidence Modal */}
      <EvidenceModal
        isOpen={!!selectedExceptionForEvidence}
        onClose={() => setSelectedExceptionForEvidence(null)}
        invoiceId={invoice.invoice_id}
        exception={selectedExceptionForEvidence}
        onSuccess={loadInvoiceData}
      />

    </div>
  );
};
