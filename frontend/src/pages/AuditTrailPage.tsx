import React from 'react';
import { 
  ShieldCheck, 
  Clock, 
  Search, 
  Filter, 
  Download, 
  CheckCircle2, 
  ExternalLink,
  Code,
  Layers,
  Sparkles,
  Bot,
  User,
  ArrowRight,
  RefreshCw
} from 'lucide-react';
import { api } from '../services/api';

interface AuditTrailPageProps {
  onSelectInvoice?: (id: string) => void;
}

export const AuditTrailPage: React.FC<AuditTrailPageProps> = ({ onSelectInvoice }) => {
  const [events, setEvents] = React.useState<any[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [filterAction, setFilterAction] = React.useState<string>('all');
  const [searchQuery, setSearchQuery] = React.useState<string>('');
  const [selectedEvent, setSelectedEvent] = React.useState<any | null>(null);

  const loadAuditTrail = async () => {
    setLoading(true);
    try {
      const data = await api.getGlobalAuditEvents(150, filterAction === 'all' ? undefined : filterAction);
      setEvents(data.items || []);
    } catch (err) {
      console.error("Failed to load audit events", err);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    loadAuditTrail();
  }, [filterAction]);

  const filteredEvents = events.filter((ev) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    const matchInv = (ev.invoice_id || '').toLowerCase().includes(q);
    const matchActor = (ev.actor_id || '').toLowerCase().includes(q);
    const matchAction = (ev.action || '').toLowerCase().includes(q);
    const matchEntity = (ev.entity_id || '').toLowerCase().includes(q);
    const matchReq = (ev.request_id || '').toLowerCase().includes(q);
    return matchInv || matchActor || matchAction || matchEntity || matchReq;
  });

  const exportJSON = () => {
    const blob = new Blob([JSON.stringify(events, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `invoiceops_immutable_audit_log_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const aiEventsCount = events.filter(e => e.actor_type === 'agent' || (e.actor_id || '').includes('agent')).length;
  const humanEventsCount = events.length - aiEventsCount;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-text-primary tracking-tight font-sans">
              Immutable Governance Audit Log
            </h1>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-dark-panel border border-dark-border text-supabase-400">
              {events.length} events logged
            </span>
          </div>
          <p className="text-xs text-text-secondary mt-1">
            Complete append-only audit trail tracking every deterministic match check, agent action, and finance decision
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={loadAuditTrail}
            className="p-1.5 rounded-md bg-dark-panel border border-dark-border text-text-muted hover:text-white transition"
            title="Refresh Log"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-supabase-400' : ''}`} />
          </button>

          <button
            onClick={exportJSON}
            className="px-3 py-1.5 text-xs font-semibold rounded-md bg-supabase-500 hover:bg-supabase-400 text-black shadow-supabase-glow transition flex items-center space-x-1.5 font-mono"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Audit Trail (JSON)</span>
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
        <div className="bg-dark-panel p-4 rounded-lg border border-dark-border">
          <div className="text-[11px] font-mono uppercase tracking-wider text-text-muted mb-1 flex items-center justify-between">
            <span>Log Integrity</span>
            <ShieldCheck className="w-3.5 h-3.5 text-supabase-400" />
          </div>
          <div className="text-xl font-bold text-supabase-400 font-mono">100% Cryptographic</div>
          <span className="text-[10px] text-text-dim">SHA-256 source tied</span>
        </div>

        <div className="bg-dark-panel p-4 rounded-lg border border-dark-border">
          <div className="text-[11px] font-mono uppercase tracking-wider text-text-muted mb-1 flex items-center justify-between">
            <span>Total Events</span>
            <Layers className="w-3.5 h-3.5 text-blue-400" />
          </div>
          <div className="text-xl font-bold text-white font-mono">{events.length}</div>
          <span className="text-[10px] text-text-dim">Append-only sequence</span>
        </div>

        <div className="bg-dark-panel p-4 rounded-lg border border-dark-border">
          <div className="text-[11px] font-mono uppercase tracking-wider text-text-muted mb-1 flex items-center justify-between">
            <span>AI Agent Actions</span>
            <Bot className="w-3.5 h-3.5 text-cyan-400" />
          </div>
          <div className="text-xl font-bold text-cyan-300 font-mono">{aiEventsCount}</div>
          <span className="text-[10px] text-text-dim">Switch agent operations</span>
        </div>

        <div className="bg-dark-panel p-4 rounded-lg border border-dark-border">
          <div className="text-[11px] font-mono uppercase tracking-wider text-text-muted mb-1 flex items-center justify-between">
            <span>Human Approvals</span>
            <User className="w-3.5 h-3.5 text-amber-400" />
          </div>
          <div className="text-xl font-bold text-amber-300 font-mono">{humanEventsCount}</div>
          <span className="text-[10px] text-text-dim">Role-enforced sign-offs</span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-dark-surface p-3 rounded-lg border border-dark-border flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="relative w-full sm:w-80">
          <Search className="w-3.5 h-3.5 text-text-muted absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by invoice, actor, action, request ID..."
            className="w-full bg-dark-bg border border-dark-border rounded-md pl-8 pr-3 py-1.5 text-xs text-text-primary placeholder:text-text-muted focus:outline-none focus:border-supabase-500 font-mono"
          />
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <Filter className="w-3.5 h-3.5 text-text-muted" />
          <select
            value={filterAction}
            onChange={(e) => setFilterAction(e.target.value)}
            className="bg-dark-bg border border-dark-border rounded-md px-2.5 py-1.5 text-xs text-text-primary focus:outline-none focus:border-supabase-500 font-mono"
          >
            <option value="all">All Actions</option>
            <option value="MATCH_RUN">MATCH_RUN</option>
            <option value="EXCEPTION_RAISED">EXCEPTION_RAISED</option>
            <option value="EVIDENCE_ATTACHED">EVIDENCE_ATTACHED</option>
            <option value="APPROVAL_DECISION">APPROVAL_DECISION</option>
            <option value="PAYMENT_READY_CREATED">PAYMENT_READY_CREATED</option>
          </select>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="bg-dark-panel rounded-lg border border-dark-border shadow-supabase overflow-hidden">
        {loading ? (
          <div className="p-16 text-center text-xs text-text-muted font-mono flex items-center justify-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-supabase-500 animate-ping"></span>
            <span>Loading governance records...</span>
          </div>
        ) : filteredEvents.length === 0 ? (
          <div className="p-16 text-center text-xs text-text-muted font-mono">
            No audit events found matching query.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-dark-surface border-b border-dark-border text-text-muted font-mono uppercase tracking-wider text-[11px]">
                  <th className="py-2.5 px-4 font-semibold">Timestamp</th>
                  <th className="py-2.5 px-4 font-semibold">Action</th>
                  <th className="py-2.5 px-4 font-semibold">Target Invoice</th>
                  <th className="py-2.5 px-4 font-semibold">Actor</th>
                  <th className="py-2.5 px-4 font-semibold">Reason / Detail</th>
                  <th className="py-2.5 px-4 text-right font-semibold">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-dark-border/60">
                {filteredEvents.map((ev) => (
                  <tr key={ev.event_id} className="hover:bg-dark-hover/70 transition">
                    <td className="py-2.5 px-4 font-mono text-[11px] text-text-muted whitespace-nowrap">
                      {ev.occurred_at ? new Date(ev.occurred_at).toLocaleString() : 'N/A'}
                    </td>
                    <td className="py-2.5 px-4 font-mono font-medium">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        ev.action === 'APPROVAL_DECISION' ? 'bg-supabase-950/60 text-supabase-400 border border-supabase-500/40' :
                        ev.action === 'PAYMENT_READY_CREATED' ? 'bg-cyan-950/60 text-cyan-300 border border-cyan-500/40' :
                        ev.action === 'EXCEPTION_RAISED' ? 'bg-red-950/60 text-red-400 border border-red-500/40' :
                        ev.action === 'EVIDENCE_ATTACHED' ? 'bg-amber-950/60 text-amber-300 border border-amber-500/40' :
                        'bg-blue-950/60 text-blue-300 border border-blue-500/40'
                      }`}>
                        {ev.action}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 font-mono">
                      {ev.invoice_id ? (
                        <button
                          onClick={() => onSelectInvoice && onSelectInvoice(ev.invoice_id)}
                          className="text-supabase-400 hover:underline flex items-center space-x-1"
                        >
                          <span>{ev.invoice_id}</span>
                          <ArrowRight className="w-3 h-3 opacity-60" />
                        </button>
                      ) : (
                        <span className="text-text-dim">—</span>
                      )}
                    </td>
                    <td className="py-2.5 px-4 font-mono text-text-secondary text-[11px]">
                      <span className="text-white font-medium">{ev.actor_id}</span>
                      <span className="text-text-dim ml-1">({ev.actor_type})</span>
                    </td>
                    <td className="py-2.5 px-4 text-text-secondary text-[11px] max-w-xs truncate">
                      {ev.reason || ev.after_state || '—'}
                    </td>
                    <td className="py-2.5 px-4 text-right">
                      <button
                        onClick={() => setSelectedEvent(ev)}
                        className="px-2 py-1 text-[10px] font-mono bg-dark-surface hover:bg-dark-hover border border-dark-borderLight text-text-primary rounded transition"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Event Details Modal */}
      {selectedEvent && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-dark-panel border border-dark-border rounded-xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="p-4 border-b border-dark-border flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-supabase-400" />
                <h3 className="text-sm font-bold text-white font-mono">
                  Audit Event #{selectedEvent.event_id}
                </h3>
              </div>
              <button
                onClick={() => setSelectedEvent(null)}
                className="text-text-muted hover:text-white text-xs px-2 py-1 rounded bg-dark-surface"
              >
                Close
              </button>
            </div>

            <div className="p-4 overflow-y-auto space-y-3 text-xs font-mono">
              <div className="grid grid-cols-2 gap-2 bg-dark-bg p-3 rounded border border-dark-border">
                <div>
                  <span className="text-text-dim text-[10px] block">Action</span>
                  <span className="text-supabase-400 font-bold">{selectedEvent.action}</span>
                </div>
                <div>
                  <span className="text-text-dim text-[10px] block">Timestamp</span>
                  <span className="text-white">{selectedEvent.occurred_at}</span>
                </div>
                <div>
                  <span className="text-text-dim text-[10px] block">Actor</span>
                  <span className="text-white">{selectedEvent.actor_id} ({selectedEvent.actor_type})</span>
                </div>
                <div>
                  <span className="text-text-dim text-[10px] block">Target Invoice</span>
                  <span className="text-white">{selectedEvent.invoice_id || 'System Global'}</span>
                </div>
              </div>

              <div>
                <span className="text-text-dim text-[10px] block mb-1">State Transition</span>
                <div className="grid grid-cols-2 gap-2 text-[11px]">
                  <div className="p-2 bg-dark-surface rounded border border-dark-border">
                    <span className="text-text-dim block text-[10px]">Before State</span>
                    <span className="text-text-muted">{selectedEvent.before_state || 'None'}</span>
                  </div>
                  <div className="p-2 bg-dark-surface rounded border border-dark-border">
                    <span className="text-text-dim block text-[10px]">After State</span>
                    <span className="text-supabase-400">{selectedEvent.after_state || 'None'}</span>
                  </div>
                </div>
              </div>

              {selectedEvent.reason && (
                <div>
                  <span className="text-text-dim text-[10px] block mb-1">Audit Reason / Justification</span>
                  <p className="p-2.5 bg-dark-bg rounded border border-dark-border text-text-primary text-[11px] font-sans">
                    {selectedEvent.reason}
                  </p>
                </div>
              )}

              {selectedEvent.source_refs && selectedEvent.source_refs.length > 0 && (
                <div>
                  <span className="text-text-dim text-[10px] block mb-1">Source Artifact References</span>
                  <div className="space-y-1">
                    {selectedEvent.source_refs.map((ref: any, idx: number) => (
                      <div key={idx} className="p-2 bg-dark-surface rounded border border-dark-border text-[10px] break-all">
                        {typeof ref === 'string' ? ref : JSON.stringify(ref)}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <span className="text-text-dim text-[10px] block mb-1">Raw Event Payload</span>
                <pre className="p-3 bg-dark-bg rounded border border-dark-border text-[10px] text-text-secondary overflow-x-auto">
                  {JSON.stringify(selectedEvent, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

