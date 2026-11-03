import React from 'react';
import { CreditCard, ShieldCheck, Download, CheckCircle2, Terminal } from 'lucide-react';
import { PaymentReadyRecord } from '../types';
import { api } from '../services/api';

export const PaymentReadyPage: React.FC = () => {
  const [records, setRecords] = React.useState<PaymentReadyRecord[]>([]);
  const [loading, setLoading] = React.useState(true);

  const loadRecords = async () => {
    try {
      const data = await api.getPaymentReadyRecords();
      setRecords(data.items || []);
    } catch (err) {
      console.error("Failed to load payment-ready records", err);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    loadRecords();
  }, []);

  const handleExportCSV = () => {
    if (records.length === 0) return;
    const headers = ["Record_ID", "Invoice_ID", "Invoice_Number", "Vendor", "Approved_Amount", "Currency", "Status", "Approved_At", "Payment_Executed"];
    const rows = records.map(r => [
      r.payment_ready_record_id,
      r.invoice_id,
      r.invoice_number || 'N/A',
      r.vendor_id || 'N/A',
      r.approved_amount,
      r.currency,
      r.status,
      r.created_at,
      r.payment_executed ? "TRUE" : "FALSE"
    ]);

    const csvContent = [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `invoiceops_payment_ready_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-text-primary tracking-tight font-sans">Payment-Ready Records</h1>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-dark-panel border border-dark-border text-cyan-400">
              {records.length} records
            </span>
          </div>
          <p className="text-xs text-text-secondary mt-1">
            Finance-approved invoices structured for downstream accounting & ERP batch disbursement
          </p>
        </div>
        <button
          onClick={handleExportCSV}
          disabled={records.length === 0}
          className="px-3.5 py-1.5 text-xs font-bold bg-supabase-500 hover:bg-supabase-400 text-black rounded-md shadow-supabase-glow transition disabled:opacity-40 flex items-center space-x-1.5 font-mono"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Export ERP Batch (CSV)</span>
        </button>
      </div>

      {/* Mandatory Non-Payment Boundary Banner */}
      <div className="p-4 bg-dark-panel border border-supabase-500/30 rounded-lg text-xs space-y-1.5">
        <div className="font-bold flex items-center text-supabase-300 font-mono">
          <ShieldCheck className="w-4 h-4 mr-2 text-supabase-400 shrink-0" />
          Strict Financial Safety & Non-Payment Boundary
        </div>
        <p className="text-text-secondary text-[11px] leading-relaxed">
          <strong>No payment has been initiated by InvoiceOps.</strong> These records verify that three-way reconciliation succeeded, all exceptions were resolved, and a human finance authority signed off. Final money movement happens outside InvoiceOps in external corporate banking or ERP systems.
        </p>
      </div>

      {/* Records Table */}
      <div className="bg-dark-panel rounded-lg border border-dark-border shadow-supabase overflow-hidden">
        {loading ? (
          <div className="p-16 text-center text-xs text-text-muted font-mono flex items-center justify-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-supabase-500 animate-ping"></span>
            <span>Querying payment-ready records...</span>
          </div>
        ) : records.length === 0 ? (
          <div className="p-16 text-center">
            <CreditCard className="w-8 h-8 text-text-muted mx-auto mb-2 opacity-40" />
            <h4 className="text-sm font-semibold text-text-primary">No payment-ready records generated</h4>
            <p className="text-xs text-text-muted mt-1 font-mono">Approve a clean case (e.g. INV-2026-1041) under the Finance Approver role to generate one.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-dark-surface border-b border-dark-border text-text-muted font-mono uppercase tracking-wider text-[11px]">
                  <th className="py-2.5 px-4 font-semibold">Record ID</th>
                  <th className="py-2.5 px-4 font-semibold">Invoice #</th>
                  <th className="py-2.5 px-4 font-semibold">Vendor</th>
                  <th className="py-2.5 px-4 text-right font-semibold">Approved Total</th>
                  <th className="py-2.5 px-4 text-center font-semibold">Status</th>
                  <th className="py-2.5 px-4 font-semibold">Approved At</th>
                  <th className="py-2.5 px-4 text-center font-semibold">Bank Executed</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-dark-border/60">
                {records.map((r) => (
                  <tr key={r.payment_ready_record_id} className="hover:bg-dark-hover/70 transition">
                    <td className="py-3 px-4 font-mono font-medium text-text-primary">
                      {r.payment_ready_record_id}
                    </td>
                    <td className="py-3 px-4 font-mono font-semibold text-supabase-400">
                      {r.invoice_number}
                    </td>
                    <td className="py-3 px-4 text-text-secondary font-medium">
                      {r.vendor_id === 'VND-001' ? 'Northstar Components' : r.vendor_id}
                    </td>
                    <td className="py-3 px-4 text-right font-mono font-bold text-text-primary text-xs">
                      ₹{r.approved_amount} {r.currency}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="px-2 py-0.5 text-[10px] font-mono font-semibold rounded-md bg-cyan-950/50 text-cyan-300 border border-cyan-500/30">
                        Ready for Downstream
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-text-dim text-[11px]">
                      {new Date(r.created_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="px-2 py-0.5 text-[10px] font-mono font-bold rounded uppercase tracking-wider bg-dark-bg text-text-muted border border-dark-border">
                        FALSE (Protected)
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
};
