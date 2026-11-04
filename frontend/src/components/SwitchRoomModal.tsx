import React, { useState, useEffect, useRef } from 'react';
import { 
  X, 
  Bot, 
  User, 
  Send, 
  RotateCcw, 
  Sparkles,
  ShieldCheck, 
  Terminal, 
  Paperclip, 
  ChevronRight, 
  CheckCircle2, 
  AlertTriangle,
  Play,
  Cpu,
  Layers,
  ExternalLink,
  MessageSquare
} from 'lucide-react';
import { api } from '../services/api';

interface SwitchRoomModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedInvoiceId?: string;
}

export const SwitchRoomModal: React.FC<SwitchRoomModalProps> = ({ 
  isOpen, 
  onClose,
  selectedInvoiceId = 'INV-2026-1042'
}) => {
  const [activeInvoice, setActiveInvoice] = useState<string>(selectedInvoiceId);
  const [messages, setMessages] = useState<any[]>([]);
  const [inputText, setInputText] = useState<string>('');
  const [selectedRole, setSelectedRole] = useState<'ap_clerk' | 'procurement' | 'finance'>('procurement');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [showMcpDrawer, setShowMcpDrawer] = useState<boolean>(false);
  const [statusData, setStatusData] = useState<any>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const threadId = `thread_${activeInvoice}`;
  const currentOrigin = typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8000';
  const mcpEndpointUrl = `${currentOrigin}/api/v1/switch/mcp`;

  const loadMessages = async () => {
    try {
      const res = await api.getSwitchMessages('room_invoiceops_ap', threadId);
      const list = Array.isArray(res) 
        ? res 
        : (Array.isArray(res?.items) ? res.items : (Array.isArray(res?.messages) ? res.messages : []));
      setMessages(list);
    } catch (err) {
      console.error('Failed to load Switch messages:', err);
      setMessages([]);
    }
  };

  const loadStatus = async () => {
    try {
      const status = await api.getSwitchStatus();
      setStatusData(status);
    } catch (err) {
      console.error('Failed to load Switch status:', err);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadMessages();
      loadStatus();
    }
  }, [isOpen, activeInvoice]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (!isOpen) return null;

  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputText.trim() || isLoading) return;

    const roleMap = {
      ap_clerk: { id: 'ap_clerk_1', name: 'Sarah Chen (AP Clerk)', role: 'human', avatar: 'user-green' },
      procurement: { id: 'procurement_owner_1', name: 'Rajesh Kumar (Procurement)', role: 'human', avatar: 'user-amber' },
      finance: { id: 'finance_approver_1', name: 'Elena Rostova (Finance Approver)', role: 'human', avatar: 'user-purple' }
    };

    const sender = roleMap[selectedRole];
    const textToSend = inputText;
    setInputText('');
    setIsLoading(true);

    try {
      await api.postSwitchMessage('room_invoiceops_ap', {
        thread_id: threadId,
        sender_id: sender.id,
        sender_name: sender.name,
        sender_role: sender.role,
        avatar: sender.avatar,
        content: textToSend,
        mentions: textToSend.match(/@[a-zA-Z0-9_-]+/g) || []
      });
      await loadMessages();
    } catch (err: any) {
      alert(`Message dispatch failed: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunSimulation = async () => {
    setIsSimulating(true);
    try {
      const res = await api.simulateSwitchWorkflow('room_invoiceops_ap', activeInvoice);
      setMessages(res.messages);
    } catch (err: any) {
      alert(`Simulation failed: ${err.message}`);
    } finally {
      setIsSimulating(false);
    }
  };

  const handleResetThread = async () => {
    if (!window.confirm("Reset this Switch thread back to clean initial demo state?")) return;
    try {
      await api.resetSwitchRoom('room_invoiceops_ap');
      await loadMessages();
    } catch (err: any) {
      alert(`Reset failed: ${err.message}`);
    }
  };

  const addMention = (mention: string) => {
    setInputText((prev) => (prev ? `${prev} ${mention} ` : `${mention} `));
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/85 backdrop-blur-md flex items-center justify-center p-3 sm:p-5">
      <div className="bg-[#121212] rounded-2xl shadow-[0_20px_70px_rgba(0,0,0,0.9)] max-w-5xl w-full h-[90vh] flex flex-col overflow-hidden border border-white/15 text-white">
        
        {/* Header Bar */}
        <div className="px-5 py-3.5 border-b border-white/10 bg-neutral-900 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-b from-blue-600 to-indigo-800 border border-white/20 flex items-center justify-center font-bold text-white shadow-md">
              #
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="font-bold text-white text-sm font-mono tracking-tight">#invoiceops-ap</h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span>Switch Core Connected</span>
                </span>
              </div>
              <p className="text-xs text-neutral-400 font-sans mt-0.5">
                Multi-Agent Coordination: 2 AI Teammates + AP Clerk + Procurement + Finance
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* Run Judge Walkthrough Button */}
            <button
              onClick={handleRunSimulation}
              disabled={isSimulating}
              className="bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs px-3 py-1.5 rounded-lg transition flex items-center space-x-1.5 shadow-md active:scale-95 disabled:opacity-50"
              title="Execute the full multi-agent collaborative resolution scenario for judges"
            >
              <Play className={`w-3.5 h-3.5 fill-current ${isSimulating ? 'animate-spin' : ''}`} />
              <span className="hidden sm:inline">Run Judge Demo</span>
            </button>

            {/* Toggle MCP & Connectors drawer */}
            <button
              onClick={() => setShowMcpDrawer(!showMcpDrawer)}
              className={`p-1.5 rounded-lg border text-xs transition flex items-center gap-1 ${
                showMcpDrawer 
                  ? 'bg-purple-600/20 text-purple-300 border-purple-500/40' 
                  : 'bg-white/5 text-neutral-400 hover:text-white border-white/10'
              }`}
              title="View Switch MCP Tools & Chat Connectors"
            >
              <Cpu className="w-4 h-4" />
              <span className="text-[11px] font-mono hidden md:inline">MCP / Connectors</span>
            </button>

            {/* Reset Thread */}
            <button
              onClick={handleResetThread}
              className="p-1.5 text-neutral-400 hover:text-white hover:bg-white/10 rounded-lg transition"
              title="Reset Switch Thread"
            >
              <RotateCcw className="w-4 h-4" />
            </button>

            {/* Close */}
            <button 
              onClick={onClose} 
              className="text-neutral-400 hover:text-white p-1.5 rounded-lg hover:bg-white/10 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Invoice Thread Tabs */}
        <div className="px-5 py-2 bg-neutral-950 border-b border-white/10 flex items-center justify-between overflow-x-auto gap-2 shrink-0">
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-neutral-500 font-mono text-[11px]">Active Thread:</span>
            {['INV-2026-1042', 'INV-2026-1041', 'INV-2026-1043', 'INV-2026-1044'].map((id) => (
              <button
                key={id}
                onClick={() => setActiveInvoice(id)}
                className={`px-2.5 py-1 rounded-md font-mono text-xs transition whitespace-nowrap ${
                  activeInvoice === id
                    ? 'bg-blue-600 text-white font-bold'
                    : 'bg-neutral-900 text-neutral-400 hover:text-white border border-white/5'
                }`}
              >
                {id} {id === 'INV-2026-1042' && '(Exception)'}
              </button>
            ))}
          </div>

          <div className="text-[11px] text-neutral-400 font-mono hidden sm:flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span>Slack / Mattermost Gateway Ready</span>
          </div>
        </div>

        {/* Main Body (Chat Area + Optional MCP Drawer) */}
        <div className="flex-1 flex overflow-hidden">
          
          {/* Chat Messages Stream */}
          <div className="flex-1 flex flex-col justify-between overflow-hidden bg-neutral-950">
            
            {/* Scrollable messages container */}
            <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
              {messages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center text-neutral-500 text-sm">
                  <MessageSquare className="w-8 h-8 mb-2 opacity-40" />
                  <p>No messages in this thread yet.</p>
                  <button
                    onClick={handleRunSimulation}
                    className="mt-3 text-xs text-blue-400 hover:underline"
                  >
                    Click to load demo exception walkthrough
                  </button>
                </div>
              ) : (
                (Array.isArray(messages) ? messages : []).map((m) => {
                  const isAgent = m.sender_role === 'agent';
                  const isFinanceApproval = m.action_type === 'payment_voucher_generated' || m.action_type === 'finance_approval';
                  
                  return (
                    <div 
                      key={m.id}
                      className={`flex items-start space-x-3.5 p-3.5 rounded-xl transition border ${
                        isFinanceApproval
                          ? 'bg-emerald-950/20 border-emerald-500/30'
                          : isAgent
                            ? 'bg-neutral-900/80 border-white/10'
                            : 'bg-neutral-900/40 border-white/5'
                      }`}
                    >
                      {/* Avatar */}
                      <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 border ${
                        m.avatar === 'bot-cyan'
                          ? 'bg-cyan-600/20 border-cyan-500/40 text-cyan-400'
                          : m.avatar === 'bot-blue'
                            ? 'bg-blue-600/20 border-blue-500/40 text-blue-400'
                            : m.avatar === 'user-purple'
                              ? 'bg-purple-600/20 border-purple-500/40 text-purple-400'
                              : 'bg-amber-600/20 border-amber-500/40 text-amber-400'
                      }`}>
                        {isAgent ? <Bot className="w-5 h-5" /> : <User className="w-5 h-5" />}
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <div className="flex items-center space-x-2">
                            <span className="font-bold text-xs sm:text-sm text-white">
                              {m.sender_name}
                            </span>
                            <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded border ${
                              isAgent 
                                ? 'bg-blue-500/10 text-blue-400 border-blue-500/30' 
                                : 'bg-neutral-800 text-neutral-300 border-white/10'
                            }`}>
                              {isAgent ? 'AI Teammate' : 'Human Operator'}
                            </span>
                          </div>
                          <span className="text-[11px] text-neutral-500 font-mono">
                            {new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>

                        {/* Body */}
                        <div className="text-xs sm:text-sm text-neutral-300 leading-relaxed whitespace-pre-wrap font-sans">
                          {m.content}
                        </div>

                        {/* Attached Evidence Chips */}
                        {Array.isArray(m?.evidence_refs) && m.evidence_refs.length > 0 && (
                          <div className="mt-2.5 flex flex-wrap gap-1.5">
                            {m.evidence_refs.map((ref: string, idx: number) => (
                              <span 
                                key={idx}
                                className="inline-flex items-center space-x-1 bg-white/5 border border-white/15 px-2 py-0.5 rounded text-[11px] font-mono text-neutral-300"
                              >
                                <Paperclip className="w-3 h-3 text-neutral-400" />
                                <span>{ref}</span>
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Message Composer Footer */}
            <div className="p-3.5 bg-neutral-900 border-t border-white/10 shrink-0">
              
              {/* Role selector + Quick Mention Bar */}
              <div className="flex flex-wrap items-center justify-between gap-2 mb-2.5 text-xs">
                <div className="flex items-center space-x-1.5">
                  <span className="text-neutral-400 text-[11px]">Speaking As:</span>
                  <select
                    value={selectedRole}
                    onChange={(e: any) => setSelectedRole(e.target.value)}
                    className="bg-black border border-white/15 rounded-md px-2 py-1 text-xs text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="procurement">Procurement Owner (Human)</option>
                    <option value="finance">Finance Approver (Human)</option>
                    <option value="ap_clerk">AP Clerk (Human)</option>
                  </select>
                </div>

                {/* Quick Mention Pills */}
                <div className="flex items-center space-x-1 overflow-x-auto text-[11px]">
                  <span className="text-neutral-500 hidden sm:inline">Mention:</span>
                  <button
                    type="button"
                    onClick={() => addMention('@invoiceops-reconcile')}
                    className="bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 px-2 py-0.5 rounded border border-cyan-500/30 transition"
                  >
                    @reconcile
                  </button>
                  <button
                    type="button"
                    onClick={() => addMention('@invoiceops-intake')}
                    className="bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded border border-blue-500/30 transition"
                  >
                    @intake
                  </button>
                  <button
                    type="button"
                    onClick={() => addMention('@finance_approver')}
                    className="bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 px-2 py-0.5 rounded border border-purple-500/30 transition"
                  >
                    @finance
                  </button>
                </div>
              </div>

              {/* Input Form */}
              <form onSubmit={handleSendMessage} className="flex items-center space-x-2">
                <input
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder={`Reply in #${threadId} as ${selectedRole}...`}
                  className="flex-1 bg-black border border-white/15 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-white focus:outline-none focus:border-blue-500 transition placeholder-neutral-500 font-sans"
                />
                <button
                  type="submit"
                  disabled={!inputText.trim() || isLoading}
                  className="bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white font-semibold px-4 py-2.5 rounded-xl transition flex items-center justify-center shrink-0 shadow-md"
                >
                  <Send className="w-4 h-4" />
                </button>
              </form>

            </div>

          </div>

          {/* MCP Tools & Connectors Drawer (Collapsible) */}
          {showMcpDrawer && (
            <div className="w-80 border-l border-white/10 bg-neutral-900 p-4 overflow-y-auto flex flex-col justify-between text-xs shrink-0">
              <div>
                <div className="flex items-center justify-between pb-3 border-b border-white/10 mb-4">
                  <div className="flex items-center space-x-2">
                    <Cpu className="w-4 h-4 text-purple-400" />
                    <span className="font-bold text-white uppercase tracking-wider text-[11px]">
                      Switch MCP Server
                    </span>
                  </div>
                  <span className="text-[10px] bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded font-mono">
                    ONLINE
                  </span>
                </div>

                <div className="space-y-4 font-mono text-[11px]">
                  <div>
                    <span className="text-neutral-400 block mb-1">MCP Endpoint:</span>
                    <div className="bg-black p-2 rounded border border-white/10 text-neutral-300 break-all select-all font-mono">
                      {mcpEndpointUrl}
                    </div>
                  </div>

                  <div>
                    <span className="text-neutral-400 block mb-1">Connect Claude Code:</span>
                    <div className="bg-black p-2 rounded border border-white/10 text-blue-300 break-all text-[10px] select-all font-mono">
                      claude mcp add invoiceops {mcpEndpointUrl}
                    </div>
                  </div>

                  <div>
                    <span className="text-neutral-400 block mb-1.5 font-bold text-white font-sans text-xs">
                      5 Exported MCP Tools:
                    </span>
                    <ul className="space-y-1.5 text-neutral-300">
                      <li className="bg-white/5 p-1.5 rounded border border-white/5">
                        <span className="text-cyan-400 font-bold block">invoiceops_match</span>
                        <span className="text-[10px] text-neutral-400 font-sans">Deterministic Decimal 3-way line check</span>
                      </li>
                      <li className="bg-white/5 p-1.5 rounded border border-white/5">
                        <span className="text-blue-400 font-bold block">invoiceops_inspect</span>
                        <span className="text-[10px] text-neutral-400 font-sans">OCR confidence & line variance deltas</span>
                      </li>
                      <li className="bg-white/5 p-1.5 rounded border border-white/5">
                        <span className="text-amber-400 font-bold block">invoiceops_attach_evidence</span>
                        <span className="text-[10px] text-neutral-400 font-sans">Attach procurement addendums</span>
                      </li>
                      <li className="bg-white/5 p-1.5 rounded border border-white/5">
                        <span className="text-purple-400 font-bold block">invoiceops_approve_payment</span>
                        <span className="text-[10px] text-neutral-400 font-sans">HITL payment voucher sign-off</span>
                      </li>
                      <li className="bg-white/5 p-1.5 rounded border border-white/5">
                        <span className="text-emerald-400 font-bold block">invoiceops_get_audit</span>
                        <span className="text-[10px] text-neutral-400 font-sans">Append-only audit ledger pack</span>
                      </li>
                    </ul>
                  </div>

                  <div className="pt-2 border-t border-white/10">
                    <span className="text-neutral-400 block mb-1">Chat Surfaces:</span>
                    <div className="grid grid-cols-2 gap-1.5 text-[10px]">
                      <span className="bg-black p-1 rounded text-center text-emerald-400 border border-white/10">Mattermost</span>
                      <span className="bg-black p-1 rounded text-center text-blue-400 border border-white/10">Slack</span>
                      <span className="bg-black p-1 rounded text-center text-purple-400 border border-white/10">Teams</span>
                      <span className="bg-black p-1 rounded text-center text-indigo-400 border border-white/10">Discord</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-white/10 text-center">
                <a
                  href="/docs"
                  target="_blank"
                  rel="noreferrer"
                  className="text-neutral-400 hover:text-white transition flex items-center justify-center gap-1 font-mono text-[11px]"
                >
                  <span>OpenAPI 3.1 Spec</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
};
