import React from 'react';
import { X, FileCheck, CheckCircle2, AlertCircle } from 'lucide-react';
import { ExceptionItem } from '../types';
import { api, getGlobalRole } from '../services/api';

interface EvidenceModalProps {
  isOpen: boolean;
  onClose: () => void;
  invoiceId: string;
  exception: ExceptionItem | null;
  onSuccess: () => void;
}

export const EvidenceModal: React.FC<EvidenceModalProps> = ({
  isOpen,
  onClose,
  invoiceId,
  exception,
  onSuccess,
}) => {
  const [sourceType, setSourceType] = React.useState('grn');
  const [sourceRef, setSourceRef] = React.useState('');
  const [comment, setComment] = React.useState('');
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  if (!isOpen || !exception) return null;

  const role = getGlobalRole();
  const canAttach = role === 'procurement_owner' || role === 'ap_clerk' || role === 'ap_admin';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sourceRef.trim() || !comment.trim() || comment.trim().length < 3) {
      setError("Please provide a source reference and a comment (min 3 chars).");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await api.attachEvidence(invoiceId, exception.exception_id, {
        source_type: sourceType,
        source_ref: sourceRef,
        comment: comment,
      });
      alert("Verified evidence attached! Please rerun match to recompute pass/fail status.");
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to attach evidence.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-dark-panel rounded-xl shadow-2xl max-w-lg w-full overflow-hidden border border-dark-border text-text-primary">
        
        <div className="px-6 py-4 border-b border-dark-border bg-dark-surface flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <FileCheck className="w-5 h-5 text-supabase-400" />
            <h3 className="font-bold text-sm font-mono uppercase tracking-wide text-text-primary">Attach Verified Evidence</h3>
          </div>
          <button onClick={onClose} className="text-text-muted hover:text-text-primary p-1 rounded-md hover:bg-dark-hover transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-4">
          <div className="bg-dark-bg p-3.5 rounded-lg border border-dark-border text-xs font-mono space-y-1">
            <div className="font-semibold text-red-400">{exception.code}</div>
            <div className="text-text-secondary text-[11px]">{exception.description}</div>
            <div className="text-text-dim text-[10px] pt-1">
              Expected: {exception.expected_value || 'N/A'} | Actual: {exception.actual_value || 'N/A'}
            </div>
          </div>

          {!canAttach && (
            <div className="p-3 bg-red-950/30 border border-red-500/40 rounded-lg text-xs text-red-300 flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
              <span>Only Procurement Owner, AP Clerk or Admin can attach operational evidence.</span>
            </div>
          )}

          {error && (
            <div className="p-2.5 bg-red-950/40 text-red-300 text-xs rounded-md border border-red-500/50 font-mono">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3.5">
            <div>
              <label className="block text-xs font-mono font-semibold text-text-muted mb-1.5">Evidence Source Type</label>
              <select
                value={sourceType}
                onChange={(e) => setSourceType(e.target.value)}
                disabled={!canAttach}
                className="w-full text-xs p-2 bg-dark-bg border border-dark-border rounded-md text-text-primary focus:outline-none focus:border-supabase-500 font-mono"
              >
                <option value="grn">Goods Receipt Note (GRN)</option>
                <option value="po_amendment">PO Amendment</option>
                <option value="human_confirmation">Warehouse / Procurement Confirmation</option>
                <option value="credit_note">Supplier Credit Note</option>
                <option value="other">Other Supporting Record</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-mono font-semibold text-text-muted mb-1.5">Source Reference ID</label>
              <input
                type="text"
                value={sourceRef}
                onChange={(e) => setSourceRef(e.target.value)}
                placeholder="e.g. GRN-2026-0042 or Dock Slip #881"
                disabled={!canAttach}
                className="w-full text-xs p-2 bg-dark-bg border border-dark-border rounded-md text-text-primary focus:outline-none focus:border-supabase-500 font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-mono font-semibold text-text-muted mb-1.5">Operational Explanation</label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="e.g. Warehouse accepted remaining 2 units on dock slip #881; total accepted 10 units."
                rows={3}
                disabled={!canAttach}
                className="w-full text-xs p-2 bg-dark-bg border border-dark-border rounded-md text-text-primary focus:outline-none focus:border-supabase-500 font-mono"
              />
            </div>

            <div className="flex items-center justify-end space-x-2.5 pt-3 border-t border-dark-border">
              <button
                type="button"
                onClick={onClose}
                className="px-3.5 py-1.5 text-xs text-text-secondary hover:text-text-primary hover:bg-dark-hover rounded-md transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting || !canAttach}
                className="px-4 py-1.5 text-xs font-bold text-black bg-supabase-500 hover:bg-supabase-400 disabled:opacity-40 rounded-md shadow-supabase-glow transition font-mono"
              >
                {isSubmitting ? 'Attaching...' : 'Attach Evidence'}
              </button>
            </div>
          </form>
        </div>

      </div>
    </div>
  );
};
