import React from 'react';
import { 
  X, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  CreditCard,
  Lock,
  ArrowRight
} from 'lucide-react';
import { InvoiceDetail } from '../types';
import { api, getGlobalRole } from '../services/api';

interface FinanceApprovalModalProps {
  isOpen: boolean;
  onClose: () => void;
  invoice: InvoiceDetail;
  onSuccess: () => void;
}

export const FinanceApprovalModal: React.FC<FinanceApprovalModalProps> = ({
  isOpen,
  onClose,
  invoice,
  onSuccess,
}) => {
  const [decision, setDecision] = React.useState<'approved' | 'rejected'>('approved');
  const [comment, setComment] = React.useState('');
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [step, setStep] = React.useState<'decision' | 'create_payment_ready'>('decision');
  const [createdApprovalId, setCreatedApprovalId] = React.useState<string | null>(null);

  if (!isOpen) return null;

  const role = getGlobalRole();
  const isFinance = role === 'finance_approver' || role === 'ap_admin';
  const matchPassed = invoice.latest_match_run?.overall_status === 'PASS';
  const hasExceptions = invoice.open_exceptions.length > 0;

  const handleSubmitDecision = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!comment.trim() || comment.trim().length < 3) {
      setError("Please provide a written comment (at least 3 characters).");
      return;
    }

    if (!invoice.latest_match_run?.match_run_id) {
      setError("Cannot approve: no valid match run exists.");
      return;
    }

    setIsSubmitting(true);
    const idempKey = `approval-${invoice.invoice_id}-${Date.now()}`;

    try {
      const resp = await api.submitApproval(
        invoice.invoice_id,
        decision,
        comment,
        invoice.latest_match_run.match_run_id,
        idempKey
      );

      if (decision === 'approved') {
        setCreatedApprovalId(resp.approval_id);
        setStep('create_payment_ready');
      } else {
        alert("Invoice rejection recorded.");
        onSuccess();
        onClose();
      }
    } catch (err: any) {
      setError(err.message || "Failed to submit approval.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCreatePaymentReady = async () => {
    if (!createdApprovalId) return;
    setIsSubmitting(true);
    setError(null);
    const idempKey = `payment-ready-${invoice.invoice_id}-${Date.now()}`;

    try {
      await api.createPaymentReady(invoice.invoice_id, createdApprovalId, idempKey);
      alert("Payment-ready record successfully generated! Downstream ERP export ready.");
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to create payment-ready record.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-dark-panel rounded-xl shadow-2xl max-w-xl w-full overflow-hidden border border-dark-border text-text-primary">
        
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-dark-border bg-dark-surface flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <ShieldCheck className="w-5 h-5 text-supabase-400" />
            <h3 className="font-bold text-sm text-text-primary font-mono uppercase tracking-wide">
              Finance Consequential Decision
            </h3>
          </div>
          <button onClick={onClose} className="text-text-muted hover:text-text-primary p-1 rounded-md hover:bg-dark-hover transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-6 space-y-5">

          {/* Hard Non-Payment Boundary Notice */}
          <div className="p-3.5 bg-amber-950/20 border border-amber-500/30 rounded-lg text-xs text-amber-300 space-y-1">
            <div className="font-bold flex items-center text-amber-200">
              <Lock className="w-3.5 h-3.5 mr-1.5 text-amber-400" />
              Non-Payment Safety Boundary
            </div>
            <p className="text-[11px] text-amber-200/80">
              <strong>This creates a payment-ready record. It does not send money.</strong> InvoiceOps connects no banking rails and initiates zero financial disbursements.
            </p>
          </div>

          {/* Case Summary Strip */}
          <div className="bg-dark-bg p-3.5 rounded-lg border border-dark-border grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
            <div>
              <span className="text-text-muted block text-[10px] uppercase">Invoice</span>
              <span className="font-semibold text-supabase-400">{invoice.invoice_number}</span>
            </div>
            <div>
              <span className="text-text-muted block text-[10px] uppercase">Vendor</span>
              <span className="font-semibold text-text-primary truncate block">{invoice.vendor_name || invoice.vendor_id}</span>
            </div>
            <div>
              <span className="text-text-muted block text-[10px] uppercase">Amount</span>
              <span className="font-bold text-text-primary">₹{invoice.invoice_total}</span>
            </div>
            <div>
              <span className="text-text-muted block text-[10px] uppercase">Match Run</span>
              <span className={`font-semibold ${matchPassed ? 'text-supabase-400' : 'text-red-400'}`}>
                {invoice.latest_match_run?.overall_status || 'UNKNOWN'}
              </span>
            </div>
          </div>

          {/* Role Check Warning */}
          {!isFinance && (
            <div className="p-3 bg-red-950/30 border border-red-500/40 rounded-lg text-xs text-red-300 flex items-start space-x-2">
              <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              <div>
                <strong>Action Blocked:</strong> Your active role is <code className="font-bold text-text-primary">{role}</code>. Only human Finance Approver identities can submit financial approval decisions.
              </div>
            </div>
          )}

          {isFinance && (!matchPassed || hasExceptions) && (
            <div className="p-3 bg-red-950/30 border border-red-500/40 rounded-lg text-xs text-red-300 flex items-start space-x-2">
              <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              <div>
                <strong>Approval Blocked:</strong> Cannot approve invoice with open exceptions or non-passing three-way match. Resolve discrepancies first.
              </div>
            </div>
          )}

          {error && (
            <div className="p-3 bg-red-950/40 border border-red-500/50 rounded-lg text-xs text-red-300 font-mono">
              {error}
            </div>
          )}

          {step === 'decision' ? (
            <form onSubmit={handleSubmitDecision} className="space-y-4">
              {/* Decision Radio */}
              <div>
                <label className="block text-xs font-mono font-bold uppercase text-text-muted mb-2">Decision</label>
                <div className="grid grid-cols-2 gap-3">
                  <label className={`flex items-center p-3 rounded-lg border cursor-pointer transition ${
                    decision === 'approved' 
                      ? 'border-supabase-500/60 bg-supabase-950/20 text-supabase-300 font-semibold' 
                      : 'border-dark-border hover:bg-dark-hover text-text-secondary'
                  }`}>
                    <input
                      type="radio"
                      name="decision"
                      value="approved"
                      checked={decision === 'approved'}
                      onChange={() => setDecision('approved')}
                      disabled={!matchPassed || hasExceptions || !isFinance}
                      className="mr-2 text-supabase-500 focus:ring-supabase-500 bg-dark-bg"
                    />
                    <CheckCircle2 className="w-4 h-4 mr-1.5 text-supabase-400" />
                    <span className="text-xs">Approve for Payment-Ready</span>
                  </label>

                  <label className={`flex items-center p-3 rounded-lg border cursor-pointer transition ${
                    decision === 'rejected' 
                      ? 'border-red-500/60 bg-red-950/20 text-red-300 font-semibold' 
                      : 'border-dark-border hover:bg-dark-hover text-text-secondary'
                  }`}>
                    <input
                      type="radio"
                      name="decision"
                      value="rejected"
                      checked={decision === 'rejected'}
                      onChange={() => setDecision('rejected')}
                      disabled={!isFinance}
                      className="mr-2 text-red-500 focus:ring-red-500 bg-dark-bg"
                    />
                    <XCircle className="w-4 h-4 mr-1.5 text-red-400" />
                    <span className="text-xs">Reject Invoice</span>
                  </label>
                </div>
              </div>

              {/* Written Reason */}
              <div>
                <label className="block text-xs font-mono font-semibold text-text-muted mb-1.5">
                  Written Mandatory Reason <span className="text-red-400">*</span>
                </label>
                <textarea
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  placeholder="e.g. Verified 3-way match, accepted receipt evidence, and PO lines. Approved for downstream processing."
                  rows={3}
                  disabled={!isFinance}
                  className="w-full text-xs p-2.5 bg-dark-bg border border-dark-border rounded-lg text-text-primary focus:outline-none focus:border-supabase-500 font-mono transition"
                />
              </div>

              {/* Buttons */}
              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-dark-border">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 text-xs font-medium text-text-secondary hover:text-text-primary hover:bg-dark-hover rounded-md transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting || !isFinance || (decision === 'approved' && (!matchPassed || hasExceptions))}
                  className="px-5 py-2 text-xs font-bold text-black bg-supabase-500 hover:bg-supabase-400 disabled:opacity-30 disabled:cursor-not-allowed rounded-md shadow-supabase-glow transition flex items-center space-x-1.5 font-mono"
                >
                  <span>{isSubmitting ? 'Recording...' : decision === 'approved' ? 'Record Approval' : 'Record Rejection'}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </form>
          ) : (
            <div className="space-y-4">
              <div className="p-4 bg-supabase-950/30 border border-supabase-500/40 rounded-lg text-supabase-300 text-xs space-y-1.5">
                <div className="font-bold flex items-center text-supabase-200">
                  <CheckCircle2 className="w-4 h-4 mr-1.5 text-supabase-400" />
                  Approval Decision Persisted
                </div>
                <p className="font-mono text-[11px] text-text-secondary">
                  Approval ID: <span className="text-text-primary">{createdApprovalId}</span>
                </p>
                <p className="text-[11px] text-text-muted">
                  Generate the downstream payment-ready record now for ERP export.
                </p>
              </div>

              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-dark-border">
                <button
                  type="button"
                  onClick={() => { onSuccess(); onClose(); }}
                  className="px-4 py-2 text-xs font-medium text-text-secondary hover:text-text-primary hover:bg-dark-hover rounded-md transition"
                >
                  Skip for Now
                </button>
                <button
                  type="button"
                  onClick={handleCreatePaymentReady}
                  disabled={isSubmitting}
                  className="px-5 py-2 text-xs font-bold text-black bg-supabase-500 hover:bg-supabase-400 disabled:opacity-40 rounded-md shadow-supabase-glow transition flex items-center space-x-1.5 font-mono"
                >
                  <CreditCard className="w-3.5 h-3.5 mr-1" />
                  <span>{isSubmitting ? 'Generating...' : 'Create Payment-Ready Record'}</span>
                </button>
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
};
