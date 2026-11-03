import React from 'react';
import { 
  Search, 
  Filter, 
  ArrowRight, 
  AlertTriangle, 
  Clock, 
  CheckCircle2, 
  FileCheck, 
  RotateCw,
  ExternalLink,
  ChevronRight,
  Sparkles,
  ShieldCheck,
  Terminal,
  Plus
} from 'lucide-react';
import { InvoiceItem } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { IngestInvoiceModal } from '../components/IngestInvoiceModal';
import { api } from '../services/api';

interface InboxPageProps {
  onSelectInvoice: (invoiceId: string) => void;
  onOpenSwitchRoom: () => void;
}

export const InboxPage: React.FC<InboxPageProps> = ({ 
  onSelectInvoice,
  onOpenSwitchRoom,
}) => {
  const [invoices, setInvoices] = React.useState<InvoiceItem[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [searchQuery, setSearchQuery] = React.useState('');
  const [statusFilter, setStatusFilter] = React.useState<string>('all');
  const [runningMatches, setRunningMatches] = React.useState<Record<string, boolean>>({});
  const [showIngestModal, setShowIngestModal] = React.useState<boolean>(false);

  const loadInvoices = async () => {
    setLoading(true);
    try {
      const data = await api.getInvoices();
      const list = Array.isArray(data) ? data : (Array.isArray(data?.items) ? data.items : []);
      setInvoices(list);
    } catch (err) {
      console.error("Failed to load invoices", err);
      setInvoices([]);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    loadInvoices();
  }, []);

  const handleRunMatch = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    setRunningMatches(prev => ({ ...prev, [id]: true }));
    try {
      await api.runMatch(id);
      await loadInvoices();
    } catch (err: any) {
      alert(`Match failed: ${err.message}`);
    } finally {
      setRunningMatches(prev => ({ ...prev, [id]: false }));
    }
  };

  // KPI Calculations
  const needsReviewCount = invoices.filter(i => i.status === 'needs_review' || i.status === 'extracting').length;
  const openExceptionsCount = invoices.filter(i => i.status === 'exception_open' || i.status === 'duplicate_blocked').length;
  const awaitingHumanCount = invoices.filter(i => i.status === 'awaiting_human').length;
  const readyForApprovalCount = invoices.filter(i => i.status === 'ready_for_approval').length;
  const paymentReadyCount = invoices.filter(i => i.status === 'payment_ready' || i.status === 'approved').length;

  const filteredInvoices = invoices.filter(i => {
    if (statusFilter === 'exceptions') {
      if (i.status !== 'exception_open' && i.status !== 'duplicate_blocked') return false;
    } else if (statusFilter === 'ready') {
      if (i.status !== 'ready_for_approval') return false;
    } else if (statusFilter === 'payment_ready') {
      if (i.status !== 'payment_ready' && i.status !== 'approved') return false;
    }

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchNum = (i.invoice_number || '').toLowerCase().includes(q);
      const matchVen = (i.vendor_id || '').toLowerCase().includes(q);
      const matchPO = (i.po_id || '').toLowerCase().includes(q);
      const matchId = (i.invoice_id || '').toLowerCase().includes(q);
      return matchNum || matchVen || matchPO || matchId;
    }
    return true;
  });

  return (
    <div className="space-y-6">
      
      {/* Top Banner & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-text-primary tracking-tight font-sans">Accounts Payable Exceptions</h1>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-dark-panel border border-dark-border text-supabase-400">
              {filteredInvoices.length} records
            </span>
          </div>
          <p className="text-xs text-text-secondary mt-1">
            Real-time AP exception resolution coordinated with Switch agents in <code className="font-mono text-supabase-400">#invoiceops-ap</code>
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowIngestModal(true)}
            className="px-3 py-1.5 text-xs font-semibold rounded-md bg-supabase-500 hover:bg-supabase-400 text-black shadow-supabase-glow transition flex items-center space-x-1.5 font-mono"
            title="Ingest new invoice document"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Ingest Invoice</span>
          </button>

          <button
            onClick={onOpenSwitchRoom}
            className="px-3 py-1.5 text-xs font-medium rounded-md bg-dark-panel border border-dark-borderLight text-text-primary hover:border-supabase-500/50 transition flex items-center space-x-1.5 shadow-sm"
          >
            <Sparkles className="w-3.5 h-3.5 text-supabase-400" />
            <span>Switch Thread</span>
          </button>
        </div>
      </div>

      {/* 5 Supabase Studio KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
        
        {/* Needs Review */}
        <div 
          onClick={() => setStatusFilter('all')}
          className="bg-dark-panel p-4 rounded-lg border border-dark-border hover:border-dark-borderLight transition cursor-pointer group"
        >
          <div className="flex items-center justify-between text-text-muted mb-1 text-[11px] font-mono uppercase tracking-wider">
            <span>Needs Review</span>
            <Clock className="w-3.5 h-3.5 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-text-primary num-tabular">{needsReviewCount}</div>
          <span className="text-[10px] text-text-dim">Extraction confidence</span>
        </div>

        {/* Open Exceptions */}
        <div 
          onClick={() => setStatusFilter(statusFilter === 'exceptions' ? 'all' : 'exceptions')}
          className={`bg-dark-panel p-4 rounded-lg border transition cursor-pointer group ${
            statusFilter === 'exceptions' 
              ? 'border-red-500/80 bg-red-950/10' 
              : 'border-dark-border hover:border-red-500/40'
          }`}
        >
          <div className="flex items-center justify-between text-text-muted mb-1 text-[11px] font-mono uppercase tracking-wider">
            <span>Exceptions</span>
            <AlertTriangle className="w-3.5 h-3.5 text-red-400" />
          </div>
          <div className="text-2xl font-bold text-red-400 num-tabular">{openExceptionsCount}</div>
          <span className="text-[10px] text-text-dim">Qty, price & duplicates</span>
        </div>

        {/* Awaiting Human */}
        <div className="bg-dark-panel p-4 rounded-lg border border-dark-border hover:border-dark-borderLight transition">
          <div className="flex items-center justify-between text-text-muted mb-1 text-[11px] font-mono uppercase tracking-wider">
            <span>Awaiting Human</span>
            <Clock className="w-3.5 h-3.5 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-text-primary num-tabular">{awaitingHumanCount}</div>
          <span className="text-[10px] text-text-dim">Procurement / AP action</span>
        </div>

        {/* Ready for Approval */}
        <div 
          onClick={() => setStatusFilter(statusFilter === 'ready' ? 'all' : 'ready')}
          className={`bg-dark-panel p-4 rounded-lg border transition cursor-pointer group ${
            statusFilter === 'ready' 
              ? 'border-supabase-500/80 bg-supabase-950/10' 
              : 'border-dark-border hover:border-supabase-500/40'
          }`}
        >
          <div className="flex items-center justify-between text-text-muted mb-1 text-[11px] font-mono uppercase tracking-wider">
            <span>Ready for Approval</span>
            <CheckCircle2 className="w-3.5 h-3.5 text-supabase-400" />
          </div>
          <div className="text-2xl font-bold text-supabase-400 num-tabular">{readyForApprovalCount}</div>
          <span className="text-[10px] text-text-dim">3-way match PASS</span>
        </div>

        {/* Payment-Ready */}
        <div 
          onClick={() => setStatusFilter(statusFilter === 'payment_ready' ? 'all' : 'payment_ready')}
          className={`bg-dark-panel p-4 rounded-lg border transition cursor-pointer group ${
            statusFilter === 'payment_ready' 
              ? 'border-cyan-500/80 bg-cyan-950/10' 
              : 'border-dark-border hover:border-cyan-500/40'
          }`}
        >
          <div className="flex items-center justify-between text-text-muted mb-1 text-[11px] font-mono uppercase tracking-wider">
            <span>Payment-Ready</span>
            <FileCheck className="w-3.5 h-3.5 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-cyan-300 num-tabular">{paymentReadyCount}</div>
          <span className="text-[10px] text-text-dim">Non-payment downstream</span>
        </div>

      </div>

      {/* Supabase Studio Filter & Search Bar */}
      <div className="bg-dark-surface p-3 rounded-lg border border-dark-border flex flex-col sm:flex-row items-center justify-between gap-3">
        {/* Search Input */}
        <div className="relative w-full sm:w-80">
          <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-text-muted" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Filter by invoice #, vendor, PO..."
            className="w-full pl-9 pr-14 py-1.5 text-xs bg-dark-bg border border-dark-border rounded-md text-text-primary placeholder:text-text-muted focus:outline-none focus:border-supabase-500/70 font-mono transition"
          />
          <div className="absolute right-2.5 top-2 text-[10px] text-text-dim font-mono border border-dark-borderLight rounded px-1">
            ⌘K
          </div>
        </div>

        {/* Segmented Filter Pills */}
        <div className="flex items-center space-x-1.5 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
          <button
            onClick={() => setStatusFilter('all')}
            className={`px-2.5 py-1 text-xs rounded font-medium transition ${
              statusFilter === 'all' 
                ? 'bg-supabase-500/15 text-supabase-400 border border-supabase-500/30' 
                : 'text-text-secondary hover:text-text-primary hover:bg-dark-panel border border-transparent'
            }`}
          >
            All ({invoices.length})
          </button>
          <button
            onClick={() => setStatusFilter('exceptions')}
            className={`px-2.5 py-1 text-xs rounded font-medium transition ${
              statusFilter === 'exceptions' 
                ? 'bg-red-500/15 text-red-400 border border-red-500/30' 
                : 'text-text-secondary hover:text-text-primary hover:bg-dark-panel border border-transparent'
            }`}
          >
            Exceptions ({openExceptionsCount})
          </button>
          <button
            onClick={() => setStatusFilter('ready')}
            className={`px-2.5 py-1 text-xs rounded font-medium transition ${
              statusFilter === 'ready' 
                ? 'bg-supabase-500/15 text-supabase-400 border border-supabase-500/30' 
                : 'text-text-secondary hover:text-text-primary hover:bg-dark-panel border border-transparent'
            }`}
          >
            Ready for Approval ({readyForApprovalCount})
          </button>
          <button
            onClick={() => setStatusFilter('payment_ready')}
            className={`px-2.5 py-1 text-xs rounded font-medium transition ${
              statusFilter === 'payment_ready' 
                ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30' 
                : 'text-text-secondary hover:text-text-primary hover:bg-dark-panel border border-transparent'
            }`}
          >
            Payment-Ready ({paymentReadyCount})
          </button>
        </div>
      </div>

      {/* Supabase Studio Dark Data Grid */}
      <div className="bg-dark-panel rounded-lg border border-dark-border overflow-hidden shadow-supabase">
        {loading ? (
          <div className="p-16 text-center text-xs text-text-muted font-mono flex items-center justify-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-supabase-500 animate-ping"></span>
            <span>Querying cases from SQLite...</span>
          </div>
        ) : filteredInvoices.length === 0 ? (
          <div className="p-16 text-center">
            <Terminal className="w-8 h-8 text-text-muted mx-auto mb-2 opacity-50" />
            <h4 className="text-sm font-semibold text-text-primary">No records match filter</h4>
            <p className="text-xs text-text-muted mt-1 font-mono">SELECT * FROM invoices WHERE status = '{statusFilter}'</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-dark-surface border-b border-dark-border text-text-muted font-mono uppercase tracking-wider text-[11px]">
                  <th className="py-2.5 px-4 font-semibold">Invoice Number</th>
                  <th className="py-2.5 px-4 font-semibold">Vendor</th>
                  <th className="py-2.5 px-4 font-semibold">PO Reference</th>
                  <th className="py-2.5 px-4 font-semibold">Date</th>
                  <th className="py-2.5 px-4 text-right font-semibold">Total (INR)</th>
                  <th className="py-2.5 px-4 text-center font-semibold">Match State</th>
                  <th className="py-2.5 px-4 font-semibold">Version</th>
                  <th className="py-2.5 px-4 text-right font-semibold">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-dark-border/60">
                {filteredInvoices.map((inv) => {
                  const isMatching = runningMatches[inv.invoice_id];
                  return (
                    <tr 
                      key={inv.invoice_id}
                      onClick={() => onSelectInvoice(inv.invoice_id)}
                      className="hover:bg-dark-hover/70 cursor-pointer transition group"
                    >
                      <td className="py-3 px-4 font-mono font-medium text-text-primary">
                        <div className="flex items-center space-x-2">
                          <span className="text-supabase-400 group-hover:underline font-semibold">
                            {inv.invoice_number || inv.invoice_id}
                          </span>
                          <span className="text-[10px] text-text-dim">({inv.invoice_id})</span>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-text-secondary font-medium">
                        {inv.vendor_id === 'VND-001' ? 'Northstar Components' : inv.vendor_id}
                      </td>
                      <td className="py-3 px-4 text-text-muted font-mono">
                        {inv.po_id || '—'}
                      </td>
                      <td className="py-3 px-4 text-text-dim font-mono">
                        {inv.invoice_date || '—'}
                      </td>
                      <td className="py-3 px-4 text-right font-mono font-bold text-text-primary text-xs">
                        ₹{inv.invoice_total || '0.00'}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <StatusBadge status={inv.status} size="sm" />
                      </td>
                      <td className="py-3 px-4 text-text-dim font-mono text-[11px]">
                        v{inv.version}
                      </td>
                      <td className="py-3 px-4 text-right space-x-2">
                        <button
                          onClick={(e) => handleRunMatch(e, inv.invoice_id)}
                          disabled={isMatching}
                          className="px-2 py-0.5 text-[11px] font-mono bg-dark-bg hover:bg-dark-surface border border-dark-border text-text-secondary hover:text-text-primary rounded transition disabled:opacity-40"
                          title="Trigger 3-way match run"
                        >
                          {isMatching ? 'Matching...' : 'Match'}
                        </button>
                        <span className="text-supabase-400 group-hover:translate-x-0.5 inline-block transition text-xs font-mono font-semibold">
                          View &rarr;
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal for Ingesting New Invoices */}
      <IngestInvoiceModal
        isOpen={showIngestModal}
        onClose={() => setShowIngestModal(false)}
        onSuccess={(newId) => {
          loadInvoices();
          onSelectInvoice(newId);
        }}
      />
    </div>
  );
};
