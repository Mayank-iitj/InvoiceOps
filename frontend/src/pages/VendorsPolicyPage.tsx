import React from 'react';
import { Building2, Sliders, ShieldCheck, CheckCircle2, Terminal } from 'lucide-react';
import { PolicySettings } from '../types';
import { api } from '../services/api';

export const VendorsPolicyPage: React.FC<{ initialTab?: 'vendors' | 'policy' }> = ({ initialTab = 'vendors' }) => {
  const [vendors, setVendors] = React.useState<any[]>([]);
  const [policy, setPolicy] = React.useState<PolicySettings | null>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    async function loadData() {
      try {
        const vData = await api.getVendors();
        const list = Array.isArray(vData) ? vData : (Array.isArray(vData?.items) ? vData.items : []);
        setVendors(list);
        const pData = await api.getPolicy();
        setPolicy(pData);
      } catch (err) {
        console.error("Failed to load policy data", err);
        setVendors([]);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="p-16 text-center text-xs text-text-muted font-mono flex items-center justify-center space-x-2">
        <span className="w-2 h-2 rounded-full bg-supabase-500 animate-ping"></span>
        <span>Loading master data & policies...</span>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      
      {/* Vendors Master Data Section */}
      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-bold text-text-primary tracking-tight flex items-center">
            <Building2 className="w-4 h-4 mr-2 text-supabase-400" />
            Supplier Master Data (Demo Vendors)
          </h2>
          <p className="text-xs text-text-secondary mt-0.5">
            Synthetic supplier registry. Banking and disbursement details are strictly excluded per financial safety guardrails.
          </p>
        </div>

        <div className="bg-dark-panel rounded-lg border border-dark-border shadow-supabase overflow-hidden">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-dark-surface border-b border-dark-border text-text-muted font-mono uppercase tracking-wider text-[11px]">
                <th className="py-2.5 px-4 font-semibold">Vendor ID</th>
                <th className="py-2.5 px-4 font-semibold">Legal Name</th>
                <th className="py-2.5 px-4 font-semibold">Display Name</th>
                <th className="py-2.5 px-4 font-semibold">Currency</th>
                <th className="py-2.5 px-4 text-center font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-border/60">
              {vendors.map((v) => (
                <tr key={v.id} className="hover:bg-dark-hover/70 transition">
                  <td className="py-3 px-4 font-mono font-medium text-supabase-400">{v.id}</td>
                  <td className="py-3 px-4 font-semibold text-text-primary">{v.legal_name}</td>
                  <td className="py-3 px-4 text-text-secondary">{v.display_name}</td>
                  <td className="py-3 px-4 font-mono text-text-muted">{v.currency}</td>
                  <td className="py-3 px-4 text-center">
                    <span className="px-2 py-0.5 text-[10px] font-mono font-semibold bg-supabase-950/50 text-supabase-400 rounded-md border border-supabase-500/30">
                      Active
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Matching Policy Section */}
      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-bold text-text-primary tracking-tight flex items-center">
            <Sliders className="w-4 h-4 mr-2 text-supabase-400" />
            Deterministic Reconciliation Policy & Tolerances
          </h2>
          <p className="text-xs text-text-secondary mt-0.5">
            Configured rules applied by the Python matching engine. Evaluated strictly with Decimal arithmetic.
          </p>
        </div>

        <div className="bg-dark-panel rounded-lg border border-dark-border shadow-supabase p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          
          <div className="p-4 bg-dark-bg rounded-lg border border-dark-border space-y-1 font-mono">
            <span className="text-[10px] font-bold uppercase tracking-wider text-text-muted">Policy Version</span>
            <div className="text-base font-bold text-supabase-400">{policy?.policy_version || 'demo-policy-1.0'}</div>
            <p className="text-[11px] text-text-dim font-sans">Immutable policy identifier attached to every match run</p>
          </div>

          <div className="p-4 bg-dark-bg rounded-lg border border-dark-border space-y-1 font-mono">
            <span className="text-[10px] font-bold uppercase tracking-wider text-text-muted">Quantity Tolerance</span>
            <div className="text-base font-bold text-text-primary">{policy?.quantity_tolerance || '0'} units</div>
            <p className="text-[11px] text-text-dim font-sans">Zero overbilling tolerance (invoice qty ≤ accepted receipt qty)</p>
          </div>

          <div className="p-4 bg-dark-bg rounded-lg border border-dark-border space-y-1 font-mono">
            <span className="text-[10px] font-bold uppercase tracking-wider text-text-muted">Unit Price Relative Variance</span>
            <div className="text-base font-bold text-text-primary">{policy?.price_variance_percent || '0.50'}%</div>
            <p className="text-[11px] text-text-dim font-sans">Allowable relative delta against PO unit price</p>
          </div>

          <div className="p-4 bg-dark-bg rounded-lg border border-dark-border space-y-1 font-mono">
            <span className="text-[10px] font-bold uppercase tracking-wider text-text-muted">Absolute Price Variance Cap</span>
            <div className="text-base font-bold text-text-primary">₹{policy?.price_variance_absolute_inr || '1.00'} ({policy?.price_variance_absolute_paise || '100'} paise)</div>
            <p className="text-[11px] text-text-dim font-sans">Strict absolute unit price variance cap</p>
          </div>

          <div className="p-4 bg-dark-bg rounded-lg border border-dark-border space-y-1 font-mono">
            <span className="text-[10px] font-bold uppercase tracking-wider text-text-muted">Extraction Confidence Floor</span>
            <div className="text-base font-bold text-text-primary">{policy?.extraction_confidence_threshold || 0.90}</div>
            <p className="text-[11px] text-text-dim font-sans">Proposals below 90% confidence trigger mandatory human review</p>
          </div>

          <div className="p-4 bg-dark-bg rounded-lg border border-dark-border space-y-1 font-mono">
            <span className="text-[10px] font-bold uppercase tracking-wider text-text-muted">Audit Log Retention</span>
            <div className="text-base font-bold text-text-primary">{policy?.audit_retention_days || 365} days</div>
            <p className="text-[11px] text-text-dim font-sans">Append-only audit timeline records persisted in database</p>
          </div>

        </div>
      </section>

    </div>
  );
};
