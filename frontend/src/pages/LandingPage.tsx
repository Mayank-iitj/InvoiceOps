import React, { useState } from 'react';
import { 
  FileText, 
  ArrowRight, 
  ShieldCheck, 
  CheckCircle2, 
  AlertTriangle, 
  Copy, 
  RotateCcw, 
  MessageSquare, 
  Scale, 
  Lock, 
  Zap, 
  Bot, 
  UserCheck, 
  ExternalLink,
  ChevronRight,
  TrendingUp,
  Award,
  Check,
  ShoppingBag,
  Calculator,
  Building2,
  BarChart3,
  FileCheck,
  Sliders,
  SlidersHorizontal,
  Mail,
  Globe,
  Cpu,
  Layers,
  Filter,
  DollarSign
} from 'lucide-react';

interface LandingPageProps {
  onEnterStudio: (tab?: string) => void;
  onOpenSwitchRoom: () => void;
  onSelectInvoice: (id: string) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onEnterStudio,
  onOpenSwitchRoom,
  onSelectInvoice
}) => {
  const [activePreviewTab, setActivePreviewTab] = useState<'all' | '1041' | '1042' | '1043' | '1044'>('all');
  const [activeRuleTab, setActiveRuleTab] = useState<'price' | 'qty' | 'conf' | 'dup'>('price');

  const demoInvoices = [
    {
      id: 'INV-2026-1041',
      vendor: 'Acme Supplies Co.',
      po: 'PO-2026-0082',
      amount: '₹3,750.00',
      status: 'MATCH_OK',
      badgeClass: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      detail: 'Perfect 3-way match. PO & GRN quantities and unit rates match within 0.00% delta.',
      type: '1041'
    },
    {
      id: 'INV-2026-1042',
      vendor: 'Acme Supplies Co.',
      po: 'PO-2026-0082',
      amount: '₹4,150.00',
      status: 'PRICE_MISMATCH',
      badgeClass: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      detail: 'Industrial Widget unit price is ₹250.00 instead of PO rate ₹200.00 (+10.7% total delta).',
      type: '1042'
    },
    {
      id: 'INV-2026-1043',
      vendor: 'Acme Supplies Co.',
      po: 'PO-2026-0082',
      amount: '₹3,750.00',
      status: 'DUPLICATE_SUBMISSION',
      badgeClass: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
      detail: 'Identical normalized invoice number and vendor ID as processed invoice INV-2026-1041.',
      type: '1043'
    },
    {
      id: 'INV-2026-1044',
      vendor: 'Acme Supplies Co.',
      po: 'PO-2026-0082',
      amount: '₹3,750.00',
      status: 'QTY_MISMATCH',
      badgeClass: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
      detail: 'Billed 10 units of Heavy Duty Bracket, but Goods Receipt Note GRN-2026-0041 shows 0 received.',
      type: '1044'
    }
  ];

  const filteredInvoices = activePreviewTab === 'all' 
    ? demoInvoices 
    : demoInvoices.filter(i => i.type === activePreviewTab);

  return (
    <div className="min-h-screen text-white -mt-14">
      
      {/* =========================================================================
          1. HERO SECTION: Vibrant Royal Sky + Bold Typography + CTAs
          ========================================================================= */}
      <section className="relative pt-20 pb-24 md:pb-32 px-4 sm:px-6 lg:px-8 overflow-hidden bg-gradient-to-b from-[#1447F0] via-[#1E5BF8] to-[#3B82F6]">
        {/* Subtle radial glow spotlight */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-white/10 blur-[120px] rounded-full pointer-events-none" />

        <div className="relative max-w-5xl mx-auto text-center flex flex-col items-center">
          
          {/* Top Pill Badge */}
          <div className="inline-flex items-center space-x-2 bg-white/15 hover:bg-white/20 backdrop-blur-md border border-white/25 rounded-full px-4 py-1.5 text-xs sm:text-sm font-medium text-white shadow-sm mb-6 transition-all">
            <span className="w-2 h-2 rounded-full bg-emerald-300 animate-pulse" />
            <span className="font-semibold tracking-wide">Autonomous Accounts Payable</span>
            <span className="text-white/60">·</span>
            <span>Deterministic 3-Way Matching Engine</span>
          </div>

          {/* Hero Headline: Bold Modern Sans + High-Contrast Italic Serif */}
          <h1 className="text-5xl sm:text-7xl lg:text-8xl font-black tracking-tight text-white mb-6 leading-[1.05]">
            Match once. <br />
            <span className="font-serif italic font-normal text-blue-100 tracking-normal drop-shadow-sm">
              Reconcile anytime.
            </span>
          </h1>

          {/* Hero Subhead */}
          <p className="max-w-2xl text-base sm:text-lg text-white/90 leading-relaxed font-normal mb-8">
            InvoiceOps autonomously ingests vendor invoices, executes deterministic 3-way line-item matching against POs and GRNs with Decimal arithmetic, and resolves exceptions in real-time Switch collaboration rooms.
          </p>

          {/* CTA Buttons (Black Pill + White Pill matching Supaste) */}
          <div className="flex flex-col sm:flex-row items-center gap-3.5 mb-5 w-full sm:w-auto">
            <button
              onClick={() => onEnterStudio('inbox')}
              className="w-full sm:w-auto bg-black hover:bg-neutral-900 text-white font-semibold text-sm sm:text-base px-7 py-3.5 rounded-full shadow-[0_4px_20px_rgba(0,0,0,0.4)] hover:shadow-[0_6px_25px_rgba(0,0,0,0.6)] transition-all flex items-center justify-center space-x-2.5 active:scale-95 group"
            >
              <Zap className="w-4 h-4 fill-white text-white group-hover:scale-110 transition-transform" />
              <span>Launch Studio Workbench</span>
              <ChevronRight className="w-4 h-4 text-white/70 group-hover:translate-x-0.5 transition-transform" />
            </button>

            <button
              onClick={onOpenSwitchRoom}
              className="w-full sm:w-auto bg-white hover:bg-neutral-100 text-black font-semibold text-sm sm:text-base px-7 py-3.5 rounded-full shadow-[0_4px_20px_rgba(255,255,255,0.3)] hover:shadow-[0_6px_25px_rgba(255,255,255,0.5)] transition-all flex items-center justify-center space-x-2.5 active:scale-95"
            >
              <MessageSquare className="w-4 h-4 fill-black text-black" />
              <span>Open #invoiceops-ap Room</span>
            </button>
          </div>

          {/* Micro-copy specs */}
          <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-1 text-xs text-blue-100/80 font-medium">
            <span>Deterministic Python Engine</span>
            <span>•</span>
            <span>Pure Decimal Precision</span>
            <span>•</span>
            <span>Zero Payment Rails</span>
            <span>•</span>
            <span>16/16 P0 Tests Passed</span>
          </div>

        </div>

        {/* =========================================================================
            2. HERO FLOATING NOTCH SHELF / INTERACTIVE WORKBENCH
            ========================================================================= */}
        <div className="relative mt-12 sm:mt-16 max-w-5xl mx-auto">
          {/* Floating Dark Dock Shelf */}
          <div className="bg-black/95 backdrop-blur-xl border border-white/15 rounded-3xl p-4 sm:p-6 shadow-[0_25px_60px_rgba(0,0,0,0.6)]">
            
            {/* Shelf Top Bar with Category Tabs */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 border-b border-white/10 gap-3">
              <div className="flex items-center space-x-2">
                <span className="w-3 h-3 rounded-full bg-red-500/80 inline-block" />
                <span className="w-3 h-3 rounded-full bg-yellow-500/80 inline-block" />
                <span className="w-3 h-3 rounded-full bg-green-500/80 inline-block" />
                <span className="text-xs text-neutral-400 font-mono ml-2">InvoiceOps Studio Inspector — Live Preview</span>
              </div>

              {/* Filter Tabs */}
              <div className="flex items-center overflow-x-auto max-w-full space-x-1.5 p-1 bg-white/5 rounded-full border border-white/10 text-xs">
                <button
                  onClick={() => setActivePreviewTab('all')}
                  className={`px-3 py-1 rounded-full transition whitespace-nowrap ${
                    activePreviewTab === 'all' 
                      ? 'bg-white text-black font-semibold' 
                      : 'text-neutral-300 hover:text-white'
                  }`}
                >
                  All Cases (4)
                </button>
                <button
                  onClick={() => setActivePreviewTab('1041')}
                  className={`px-3 py-1 rounded-full transition whitespace-nowrap ${
                    activePreviewTab === '1041' 
                      ? 'bg-emerald-500 text-white font-semibold' 
                      : 'text-neutral-300 hover:text-white'
                  }`}
                >
                  Clean Match
                </button>
                <button
                  onClick={() => setActivePreviewTab('1042')}
                  className={`px-3 py-1 rounded-full transition whitespace-nowrap ${
                    activePreviewTab === '1042' 
                      ? 'bg-amber-500 text-black font-semibold' 
                      : 'text-neutral-300 hover:text-white'
                  }`}
                >
                  Price Mismatch
                </button>
                <button
                  onClick={() => setActivePreviewTab('1043')}
                  className={`px-3 py-1 rounded-full transition whitespace-nowrap ${
                    activePreviewTab === '1043' 
                      ? 'bg-purple-500 text-white font-semibold' 
                      : 'text-neutral-300 hover:text-white'
                  }`}
                >
                  Duplicate
                </button>
                <button
                  onClick={() => setActivePreviewTab('1044')}
                  className={`px-3 py-1 rounded-full transition whitespace-nowrap ${
                    activePreviewTab === '1044' 
                      ? 'bg-rose-500 text-white font-semibold' 
                      : 'text-neutral-300 hover:text-white'
                  }`}
                >
                  Qty Mismatch
                </button>
              </div>
            </div>

            {/* Interactive Cards Grid + Sidecar Preview */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 pt-5">
              
              {/* Invoices List (Left 2 Columns) */}
              <div className="lg:col-span-2 space-y-3">
                {filteredInvoices.map((inv) => (
                  <div
                    key={inv.id}
                    onClick={() => onSelectInvoice(inv.id)}
                    className="group bg-neutral-900/90 hover:bg-neutral-800/90 border border-white/10 hover:border-blue-500/50 rounded-2xl p-4 transition-all cursor-pointer shadow-lg hover:shadow-blue-500/10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3"
                  >
                    <div className="flex items-start space-x-3.5">
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-b from-blue-600 to-indigo-800 flex items-center justify-center shrink-0 border border-white/15">
                        <FileText className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="font-mono font-bold text-sm text-white group-hover:text-blue-300 transition">
                            {inv.id}
                          </span>
                          <span className="text-xs text-neutral-400 font-mono">
                            {inv.po}
                          </span>
                        </div>
                        <p className="text-xs text-neutral-300 mt-0.5 font-sans">
                          {inv.detail}
                        </p>
                      </div>
                    </div>

                    <div className="flex sm:flex-col items-center sm:items-end justify-between w-full sm:w-auto shrink-0 gap-1.5 border-t sm:border-t-0 border-white/10 pt-2 sm:pt-0">
                      <span className="font-mono font-bold text-sm text-white">
                        {inv.amount}
                      </span>
                      <span className={`text-[11px] font-mono px-2.5 py-0.5 rounded-full border ${inv.badgeClass}`}>
                        {inv.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Right Sidecar Card: Live #invoiceops-ap Switch Thread */}
              <div className="bg-gradient-to-b from-neutral-900 to-neutral-950 border border-white/15 rounded-2xl p-4 flex flex-col justify-between shadow-xl">
                <div>
                  <div className="flex items-center justify-between pb-3 border-b border-white/10">
                    <div className="flex items-center space-x-2">
                      <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
                      <span className="font-mono text-xs font-bold text-white">#invoiceops-ap</span>
                    </div>
                    <span className="text-[10px] font-mono text-neutral-400">Thread #T-1042</span>
                  </div>

                  {/* Chat messages */}
                  <div className="space-y-3 mt-3 text-xs">
                    <div className="bg-white/5 rounded-xl p-2.5 border border-white/5">
                      <div className="flex items-center justify-between text-[11px] text-blue-400 font-semibold mb-1">
                        <span>Reconcile Agent (AI)</span>
                        <span className="text-neutral-500 font-mono">10:42 AM</span>
                      </div>
                      <p className="text-neutral-300 text-[11px]">
                        Discrepancy detected on INV-2026-1042: Industrial Widget rate is ₹250 (+₹50 vs PO). Total discrepancy ₹400.00.
                      </p>
                    </div>

                    <div className="bg-white/5 rounded-xl p-2.5 border border-white/5">
                      <div className="flex items-center justify-between text-[11px] text-emerald-400 font-semibold mb-1">
                        <span>Procurement Owner</span>
                        <span className="text-neutral-500 font-mono">10:45 AM</span>
                      </div>
                      <p className="text-neutral-300 text-[11px]">
                        Vendor approved expedited shipping surcharge of ₹50/unit per Addendum #A-42. Verified PO amendment attached.
                      </p>
                    </div>

                    <div className="bg-white/5 rounded-xl p-2.5 border border-white/5">
                      <div className="flex items-center justify-between text-[11px] text-amber-400 font-semibold mb-1">
                        <span>Finance Approver</span>
                        <span className="text-neutral-500 font-mono">10:50 AM</span>
                      </div>
                      <p className="text-neutral-300 text-[11px]">
                        Exception verified against procurement override. Ready for Human Sign-off.
                      </p>
                    </div>
                  </div>
                </div>

                <button
                  onClick={onOpenSwitchRoom}
                  className="mt-4 w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs py-2 rounded-xl transition flex items-center justify-center space-x-1.5"
                >
                  <MessageSquare className="w-3.5 h-3.5" />
                  <span>Join Live Switch Room</span>
                </button>
              </div>

            </div>

          </div>

          {/* Lush Green Hills Background Landscape Layer */}
          <div className="relative -mt-10 h-32 sm:h-44 w-full overflow-hidden pointer-events-none rounded-b-3xl">
            <svg viewBox="0 0 1200 240" className="w-full h-full preserve-3d" preserveAspectRatio="none">
              <defs>
                <linearGradient id="hillGrad1" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#48BB78" stopOpacity="0.85" />
                  <stop offset="100%" stopColor="#22543D" stopOpacity="0.95" />
                </linearGradient>
                <linearGradient id="hillGrad2" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#38A169" stopOpacity="0.9" />
                  <stop offset="100%" stopColor="#1C4532" stopOpacity="1" />
                </linearGradient>
              </defs>
              <path d="M0,140 Q300,50 600,120 T1200,80 L1200,240 L0,240 Z" fill="url(#hillGrad1)" />
              <path d="M0,170 Q400,100 800,150 T1200,130 L1200,240 L0,240 Z" fill="url(#hillGrad2)" opacity="0.9" />
            </svg>
            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-[#121212]" />
          </div>

        </div>

      </section>

      {/* =========================================================================
          3. HONORS & ARCHITECTURE TRUST BADGES
          ========================================================================= */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-[#121212] border-t border-white/10">
        <div className="max-w-6xl mx-auto text-center">
          
          {/* Circular Stamp / Honors Badges Row */}
          <div className="flex flex-wrap items-center justify-center gap-4 sm:gap-6 mb-12">
            
            {/* Badge 1: 3-Way Match */}
            <div className="w-24 h-24 rounded-full border border-dashed border-white/20 bg-neutral-900/60 flex flex-col items-center justify-center p-2 text-center shadow-lg group hover:border-blue-400 transition">
              <Award className="w-5 h-5 text-blue-400 mb-0.5" />
              <span className="text-[10px] uppercase font-bold tracking-tight text-white">3-Way Match</span>
              <span className="text-[8px] text-neutral-400">Deterministic</span>
            </div>

            {/* Badge 2: 0% Rail */}
            <div className="w-24 h-24 rounded-full border border-dashed border-white/20 bg-neutral-900/60 flex flex-col items-center justify-center p-2 text-center shadow-lg group hover:border-emerald-400 transition">
              <Lock className="w-5 h-5 text-emerald-400 mb-0.5" />
              <span className="text-[10px] uppercase font-bold tracking-tight text-white">0% Rail</span>
              <span className="text-[8px] text-neutral-400">Zero Payment</span>
            </div>

            {/* Badge 3: 100% Deterministic */}
            <div className="w-24 h-24 rounded-full border border-dashed border-white/20 bg-neutral-900/60 flex flex-col items-center justify-center p-2 text-center shadow-lg group hover:border-cyan-400 transition">
              <Scale className="w-5 h-5 text-cyan-400 mb-0.5" />
              <span className="text-[10px] uppercase font-bold tracking-tight text-white">100% Det.</span>
              <span className="text-[8px] text-neutral-400">Pure Decimal</span>
            </div>

            {/* Badge 4: 16/16 P0 Passed */}
            <div className="w-24 h-24 rounded-full border border-dashed border-white/20 bg-neutral-900/60 flex flex-col items-center justify-center p-2 text-center shadow-lg group hover:border-green-400 transition">
              <CheckCircle2 className="w-5 h-5 text-green-400 mb-0.5" />
              <span className="text-[10px] uppercase font-bold tracking-tight text-white">16/16 P0</span>
              <span className="text-[8px] text-neutral-400">E2E Passed</span>
            </div>

            {/* Badge 5: Append-Only Audit */}
            <div className="w-24 h-24 rounded-full border border-dashed border-white/20 bg-neutral-900/60 flex flex-col items-center justify-center p-2 text-center shadow-lg group hover:border-amber-400 transition">
              <ShieldCheck className="w-5 h-5 text-amber-400 mb-0.5" />
              <span className="text-[10px] uppercase font-bold tracking-tight text-white">Audit Log</span>
              <span className="text-[8px] text-neutral-400">Append-Only</span>
            </div>

            {/* Badge 6: OpenAPI Conformance */}
            <div className="w-24 h-24 rounded-full border border-dashed border-white/20 bg-neutral-900/60 flex flex-col items-center justify-center p-2 text-center shadow-lg group hover:border-purple-400 transition">
              <Zap className="w-5 h-5 text-purple-400 mb-0.5" />
              <span className="text-[10px] uppercase font-bold tracking-tight text-white">OpenAPI</span>
              <span className="text-[8px] text-neutral-400">REST v1 Spec</span>
            </div>

          </div>

          {/* Section Headline & Description */}
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white mb-4">
            Your invoices, guarded wherever they go
          </h2>
          <p className="max-w-2xl mx-auto text-neutral-400 text-sm sm:text-base leading-relaxed mb-8">
            Use deterministic 3-way line item matching, automated tolerance engines, duplicate hash suppression, and multi-turn Switch rooms to eliminate manual accounts payable toil.
          </p>

          {/* Pills / Tag Cloud */}
          <div className="flex flex-wrap items-center justify-center gap-2 max-w-4xl mx-auto">
            {[
              'Deterministic 3-Way Matching',
              'Zero Payment Rails',
              'Tolerance Engine (₹1.00 / 0.5%)',
              'OCR Confidence Scoring',
              'Duplicate Hash Shield',
              'Procurement Handoffs',
              'Append-Only Audit Ledger',
              'FastAPI & React Studio',
              'Strict Role-Based Auth',
              'Idempotent Approvals',
              'Clean Mock Extraction',
              'Automated Dispute Resolution'
            ].map((tag, idx) => (
              <span
                key={idx}
                className="bg-neutral-800/80 hover:bg-neutral-700/80 border border-white/10 rounded-full px-3.5 py-1.5 text-xs text-neutral-300 font-medium transition cursor-default shadow-sm"
              >
                {tag}
              </span>
            ))}
          </div>

        </div>
      </section>

      {/* =========================================================================
          4. REUSE ANYTHING WITHOUT SWITCHING APPS (Image 1 from user upload)
             Tailored: "Reconcile Everything Without Switching Apps"
          ========================================================================= */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-[#181818] border-t border-white/10">
        <div className="max-w-5xl mx-auto">
          
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white mb-4">
              Reconcile Everything Without Switching Apps
            </h2>
            <p className="max-w-2xl mx-auto text-neutral-400 text-sm sm:text-base leading-relaxed">
              Keep your active POs, delivery receipts, line-item rates, tolerances, and exception threads right at the top of your workspace. Inspect variances, attach override evidence, and approve payment-ready records without opening another window or switching context.
            </p>
          </div>

          {/* Large macOS Floating Window / Split Canvas */}
          <div className="bg-black rounded-3xl border border-white/15 overflow-hidden shadow-[0_25px_70px_rgba(0,0,0,0.85)] grid grid-cols-1 md:grid-cols-12">
            
            {/* Left Canvas: Ingested Invoice Document with Vendor Badge */}
            <div className="md:col-span-7 p-6 sm:p-8 flex flex-col justify-between bg-gradient-to-br from-neutral-900/90 via-black to-neutral-950 border-b md:border-b-0 md:border-r border-white/10">
              <div>
                <div className="flex items-center justify-between pb-4 border-b border-white/10">
                  <div className="flex items-center space-x-2.5">
                    <div className="w-8 h-8 rounded-lg bg-blue-600/30 border border-blue-500/40 flex items-center justify-center text-blue-400 font-bold text-xs">
                      IO
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-white">Acme Supplies Co.</h4>
                      <p className="text-[10px] text-neutral-400 font-mono">VND-001 · Tax ID: 27AABCA1234F1Z5</p>
                    </div>
                  </div>
                  <span className="bg-blue-500/10 text-blue-400 border border-blue-500/20 text-[10px] font-mono px-2 py-0.5 rounded-full">
                    OCR 98% Conf
                  </span>
                </div>

                <div className="mt-6 space-y-3 font-mono text-xs">
                  <div className="bg-white/5 rounded-xl p-3 border border-white/5 flex items-center justify-between">
                    <div>
                      <span className="text-neutral-400 text-[11px]">Invoice Reference:</span>
                      <p className="text-white font-bold text-sm">INV-2026-1042</p>
                    </div>
                    <div className="text-right">
                      <span className="text-neutral-400 text-[11px]">Purchase Order:</span>
                      <p className="text-blue-400 font-bold text-sm">PO-2026-0082</p>
                    </div>
                  </div>

                  <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-3 text-amber-300">
                    <div className="flex items-center justify-between font-bold text-xs mb-1">
                      <span>Line 1: Industrial Widget (Item-A)</span>
                      <span>₹250.00 / unit</span>
                    </div>
                    <p className="text-[11px] text-amber-200/80 font-sans">
                      PO agreed rate was ₹200.00. Variance delta of +₹50.00/unit (+25.0%) exceeds ₹1.00 tolerance cap.
                    </p>
                  </div>

                  <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-3 text-emerald-300">
                    <div className="flex items-center justify-between font-bold text-xs mb-1">
                      <span>Line 2: Fastening Bolt Set (Item-B)</span>
                      <span>₹143.33 / unit</span>
                    </div>
                    <p className="text-[11px] text-emerald-200/80 font-sans">
                      15 units billed matches 15 delivered on GRN-2026-0041 within 0.00% precision.
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-white/10 flex items-center justify-between text-xs text-neutral-400">
                <span>Normalized Hash: <span className="text-neutral-200 font-mono">c9a4...8f12</span></span>
                <span className="text-emerald-400 font-semibold flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Ready for Review
                </span>
              </div>
            </div>

            {/* Right Canvas: macOS Inspector Palette (like appearance / layout in image 1) */}
            <div className="md:col-span-5 p-6 bg-neutral-950 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between pb-3 border-b border-white/10 text-xs text-neutral-400 font-mono">
                  <span className="uppercase tracking-wider font-semibold text-neutral-300">Inspector Palette</span>
                  <Sliders className="w-3.5 h-3.5 text-neutral-400" />
                </div>

                <div className="mt-4 space-y-4 text-xs">
                  <div>
                    <label className="text-[11px] text-neutral-400 font-semibold uppercase tracking-wider block mb-1.5">
                      Reconciliation Mode
                    </label>
                    <div className="bg-neutral-900 border border-white/10 rounded-xl p-2 flex items-center justify-between">
                      <span className="text-white font-medium">3-Way PO + GRN + INV</span>
                      <span className="w-2 h-2 rounded-full bg-emerald-400" />
                    </div>
                  </div>

                  <div>
                    <label className="text-[11px] text-neutral-400 font-semibold uppercase tracking-wider block mb-1.5">
                      Price Variance Cap
                    </label>
                    <div className="space-y-2 bg-neutral-900 border border-white/10 rounded-xl p-3">
                      <div className="flex justify-between text-neutral-300 font-mono text-[11px]">
                        <span>Absolute Limit:</span>
                        <span className="text-white font-bold">₹1.00</span>
                      </div>
                      <div className="w-full bg-neutral-800 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-blue-500 h-full w-[25%]" />
                      </div>
                      <div className="flex justify-between text-neutral-300 font-mono text-[11px]">
                        <span>Relative Limit:</span>
                        <span className="text-white font-bold">0.50%</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="text-[11px] text-neutral-400 font-semibold uppercase tracking-wider block mb-1.5">
                      Active Role Context
                    </label>
                    <div className="bg-neutral-900 border border-white/10 rounded-xl p-2.5 flex items-center justify-between text-neutral-300">
                      <span className="font-semibold text-white">Finance Approver</span>
                      <span className="text-[10px] bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded font-mono">
                        HITL AUTH
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-white/10">
                <button
                  onClick={() => onSelectInvoice('INV-2026-1042')}
                  className="w-full bg-white hover:bg-neutral-200 text-black font-semibold text-xs py-2.5 rounded-xl transition flex items-center justify-center space-x-1.5 shadow-md"
                >
                  <span>Open Full Inspector</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* =========================================================================
          5. TWO SIDE-BY-SIDE CARDS (Image 2 from user upload)
             Card A: Custom Categories -> Custom Matching Rules & Tolerances
             Card B: Find by App or Type -> Filter by ERP Source or Format
          ========================================================================= */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-[#121212] border-t border-white/10">
        <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Card A: Custom Matching Rules & Tolerances */}
          <div className="bg-neutral-900/90 border border-white/10 rounded-3xl p-6 sm:p-8 flex flex-col justify-between shadow-xl">
            <div>
              <h3 className="text-2xl font-bold text-white mb-3">
                Custom Matching Rules & Tolerances
              </h3>
              <p className="text-neutral-400 text-xs sm:text-sm leading-relaxed mb-6">
                Create organization-wide or vendor-specific tolerance thresholds. Set absolute rupee limits, percentage variances, quantity caps, and auto-approval policies for trusted recurring suppliers.
              </p>

              {/* Interactive Category Pills from Image 2 */}
              <div className="flex flex-wrap gap-2 mb-6">
                <button
                  onClick={() => setActiveRuleTab('price')}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition ${
                    activeRuleTab === 'price'
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-neutral-800 text-neutral-300 hover:text-white'
                  }`}
                >
                  Price Buffer 24
                </button>

                <button
                  onClick={() => setActiveRuleTab('qty')}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition ${
                    activeRuleTab === 'qty'
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-neutral-800 text-neutral-300 hover:text-white'
                  }`}
                >
                  Zero Quantity Delta 0
                </button>

                <button
                  onClick={() => setActiveRuleTab('conf')}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition ${
                    activeRuleTab === 'conf'
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-neutral-800 text-neutral-300 hover:text-white'
                  }`}
                >
                  Confidence 90%
                </button>

                <button
                  onClick={() => setActiveRuleTab('dup')}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition ${
                    activeRuleTab === 'dup'
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-neutral-800 text-neutral-300 hover:text-white'
                  }`}
                >
                  Hash Shield 24
                </button>

                <button
                  onClick={() => onEnterStudio('policy')}
                  className="px-3 py-1.5 rounded-full text-xs font-semibold bg-neutral-800 hover:bg-neutral-700 text-neutral-400 hover:text-white transition flex items-center gap-1"
                >
                  <span>+</span>
                </button>
              </div>
            </div>

            <div className="bg-black/50 border border-white/5 rounded-2xl p-4 text-xs font-mono text-neutral-300">
              <span className="text-blue-400 font-semibold">Active Policy:</span>
              <p className="mt-1 text-neutral-400">
                {activeRuleTab === 'price' && 'Absolute ₹1.00 tolerance + 0.50% relative price variance. Invoices within buffer match autonomously.'}
                {activeRuleTab === 'qty' && 'Strict 0 quantity tolerance. Even 1 unit discrepancy triggers exception review in Switch rooms.'}
                {activeRuleTab === 'conf' && 'OCR confidence threshold set to 0.90. Low-confidence extractions routed to manual clerk review.'}
                {activeRuleTab === 'dup' && 'Normalized (vendor_id, invoice_number) hash blocks subsequent duplicate submissions instantly.'}
              </p>
            </div>
          </div>

          {/* Card B: Filter by ERP Source or Format */}
          <div className="bg-neutral-900/90 border border-white/10 rounded-3xl p-6 sm:p-8 flex flex-col justify-between shadow-xl">
            <div>
              <h3 className="text-2xl font-bold text-white mb-3">
                Filter by Source or Vendor
              </h3>
              <p className="text-neutral-400 text-xs sm:text-sm leading-relaxed mb-6">
                Filter your reconciliation streams by ERP source, vendor identity, intake format, or exception status. Instantly surface invoices from SAP, NetSuite, QuickBooks, Email intake, EDI, or manual upload.
              </p>

              {/* Grid of App / Format Squircle Badges from Image 2 */}
              <div className="grid grid-cols-5 gap-3 mb-6">
                {[
                  { name: 'SAP S/4', icon: 'S', color: 'from-blue-600 to-blue-800' },
                  { name: 'NetSuite', icon: 'N', color: 'from-cyan-600 to-cyan-800' },
                  { name: 'QuickBooks', icon: 'QB', color: 'from-green-600 to-green-800' },
                  { name: 'Workday', icon: 'W', color: 'from-orange-600 to-orange-800' },
                  { name: 'Slack', icon: '#', color: 'from-purple-600 to-purple-800' },
                  { name: 'Email', icon: '@', color: 'from-neutral-800 to-neutral-700' },
                  { name: 'EDI 810', icon: '⚡', color: 'from-neutral-800 to-neutral-700' },
                  { name: 'PDF OCR', icon: 'PDF', color: 'from-neutral-800 to-neutral-700' },
                  { name: 'XML / JSON', icon: '</>', color: 'from-neutral-800 to-neutral-700' },
                  { name: 'CSV', icon: '≡', color: 'from-neutral-800 to-neutral-700' },
                ].map((app, idx) => (
                  <div
                    key={idx}
                    className="flex flex-col items-center group cursor-pointer"
                    title={app.name}
                  >
                    <div className={`w-11 h-11 rounded-2xl bg-gradient-to-b ${app.color} border border-white/15 flex items-center justify-center text-white font-bold text-xs shadow-md group-hover:scale-105 transition-transform`}>
                      {app.icon}
                    </div>
                    <span className="text-[10px] text-neutral-400 mt-1 truncate max-w-full font-medium">
                      {app.name}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-black/50 border border-white/5 rounded-2xl p-4 text-xs font-mono text-neutral-300 flex items-center justify-between">
              <span className="text-emerald-400 font-semibold flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" /> 10+ Ingestion Integrations
              </span>
              <button
                onClick={() => onEnterStudio('vendors')}
                className="text-blue-400 hover:text-blue-300 font-medium text-xs flex items-center gap-1"
              >
                <span>View Vendors</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

        </div>
      </section>

      {/* =========================================================================
          6. BUILT FOR EVERYTHING YOU RECONCILE (Image 3 from user upload)
             6 Clean Persona Cards for Accounts Payable Stakeholders
          ========================================================================= */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-neutral-950 border-t border-white/10">
        <div className="max-w-6xl mx-auto">
          
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white mb-4">
              Built for everything you reconcile
            </h2>
            <p className="max-w-2xl mx-auto text-neutral-400 text-sm sm:text-base leading-relaxed">
              From line-item rate discrepancies and missing GRNs to high-volume recurring vendor bills, InvoiceOps keeps every piece of your accounts payable organized, verified, and audit-ready.
            </p>
          </div>

          {/* 6 Clean Cards in 3x2 Grid from Image 3 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            
            {/* Card 1: Procurement Teams */}
            <div className="bg-neutral-900/90 border border-white/10 rounded-3xl p-7 flex flex-col justify-between shadow-xl hover:border-blue-500/40 transition-all group">
              <div>
                <div className="w-11 h-11 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-5 group-hover:scale-105 transition-transform">
                  <ShoppingBag className="w-5 h-5 text-blue-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Procurement Teams</h3>
                <p className="text-xs sm:text-sm text-neutral-400 leading-relaxed">
                  Match issued purchase orders against vendor quotes, track line-item fulfillment, and verify expedited surcharge addendums before payment release.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-white/5 text-[11px] font-mono text-neutral-500">
                PO & Goods Receipt Verification
              </div>
            </div>

            {/* Card 2: Accounts Payable Clerks */}
            <div className="bg-neutral-900/90 border border-white/10 rounded-3xl p-7 flex flex-col justify-between shadow-xl hover:border-cyan-500/40 transition-all group">
              <div>
                <div className="w-11 h-11 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-5 group-hover:scale-105 transition-transform">
                  <Calculator className="w-5 h-5 text-cyan-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">AP Clerks</h3>
                <p className="text-xs sm:text-sm text-neutral-400 leading-relaxed">
                  Eliminate manual spreadsheet checks, automate OCR extraction, and collaborate with procurement owners in Switch rooms when rates diverge.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-white/5 text-[11px] font-mono text-neutral-500">
                Automated Exception Inbox
              </div>
            </div>

            {/* Card 3: Finance & Controllers */}
            <div className="bg-neutral-900/90 border border-white/10 rounded-3xl p-7 flex flex-col justify-between shadow-xl hover:border-emerald-500/40 transition-all group">
              <div>
                <div className="w-11 h-11 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-5 group-hover:scale-105 transition-transform">
                  <Lock className="w-5 h-5 text-emerald-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Finance Controllers</h3>
                <p className="text-xs sm:text-sm text-neutral-400 leading-relaxed">
                  Maintain absolute approval authority with strict human-in-the-loop signoffs, zero payment rail access, and tamper-evident audit ledgers.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-white/5 text-[11px] font-mono text-neutral-500">
                Strict Non-Payment Boundary
              </div>
            </div>

            {/* Card 4: Vendor Managers */}
            <div className="bg-neutral-900/90 border border-white/10 rounded-3xl p-7 flex flex-col justify-between shadow-xl hover:border-purple-500/40 transition-all group">
              <div>
                <div className="w-11 h-11 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-5 group-hover:scale-105 transition-transform">
                  <Building2 className="w-5 h-5 text-purple-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Vendor Managers</h3>
                <p className="text-xs sm:text-sm text-neutral-400 leading-relaxed">
                  Manage supplier catalogs, track historical invoice disputes, enforce contract tolerances, and cut invoice processing cycles from days to minutes.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-white/5 text-[11px] font-mono text-neutral-500">
                Supplier Profile & Catalog Governance
              </div>
            </div>

            {/* Card 5: CFOs & Executives */}
            <div className="bg-neutral-900/90 border border-white/10 rounded-3xl p-7 flex flex-col justify-between shadow-xl hover:border-amber-500/40 transition-all group">
              <div>
                <div className="w-11 h-11 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-5 group-hover:scale-105 transition-transform">
                  <BarChart3 className="w-5 h-5 text-amber-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">CFOs & Executives</h3>
                <p className="text-xs sm:text-sm text-neutral-400 leading-relaxed">
                  Real-time visibility into working capital commitments, pending exceptions, vendor payment readiness, and zero fraud or duplicate leakage.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-white/5 text-[11px] font-mono text-neutral-500">
                Working Capital & Risk Visibility
              </div>
            </div>

            {/* Card 6: Audit & Compliance */}
            <div className="bg-neutral-900/90 border border-white/10 rounded-3xl p-7 flex flex-col justify-between shadow-xl hover:border-rose-500/40 transition-all group">
              <div>
                <div className="w-11 h-11 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-5 group-hover:scale-105 transition-transform">
                  <FileCheck className="w-5 h-5 text-rose-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Audit & Compliance</h3>
                <p className="text-xs sm:text-sm text-neutral-400 leading-relaxed">
                  Immutable append-only state transition records for every invoice lifecycle event. Exportable audit packs ready for SOC 2 and statutory reviews.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-white/5 text-[11px] font-mono text-neutral-500">
                SOC 2 & Statutory Audit Readiness
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* =========================================================================
          7. DEEP DIVE FEATURE CARD: Smarter, Faster, Connected Across Enterprise
          ========================================================================= */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-[#121212]">
        <div className="max-w-5xl mx-auto">
          
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white mb-4">
              Smarter, Faster, and Guardrailed Across Your Enterprise
            </h2>
            <p className="max-w-2xl mx-auto text-neutral-400 text-sm sm:text-base leading-relaxed">
              Keep finance operations audit-ready with strict human-in-the-loop approvals, auto-detect duplicate invoices across vendor IDs, and collaborate in real time with AI agents in Switch rooms.
            </p>
          </div>

          {/* Dual Panel macOS Style Window Preview */}
          <div className="bg-black rounded-3xl border border-white/15 overflow-hidden shadow-[0_20px_60px_rgba(0,0,0,0.8)]">
            
            {/* Window Chrome Header */}
            <div className="bg-neutral-900 px-4 py-3 border-b border-white/10 flex items-center justify-between text-xs text-neutral-400 font-mono">
              <div className="flex items-center space-x-2">
                <span className="w-3 h-3 rounded-full bg-red-500" />
                <span className="w-3 h-3 rounded-full bg-yellow-500" />
                <span className="w-3 h-3 rounded-full bg-green-500" />
                <span className="ml-3 text-white font-semibold">reconciliation-matrix-inv-1042.log</span>
              </div>
              <span>Status: EXCEPTION_REVIEW</span>
            </div>

            {/* Panel 1: 3-Way Line Item Matrix */}
            <div className="p-6 border-b border-white/10 bg-neutral-950">
              <h3 className="text-sm font-bold text-white mb-3 flex items-center space-x-2">
                <Scale className="w-4 h-4 text-amber-400" />
                <span>3-Way Verification Breakdown (Decimal Math Engine)</span>
              </h3>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead>
                    <tr className="border-b border-white/10 text-neutral-400">
                      <th className="py-2">Line Description</th>
                      <th className="py-2 text-right">PO Qty / Rate</th>
                      <th className="py-2 text-right">GRN Delivered</th>
                      <th className="py-2 text-right">Invoice Billed</th>
                      <th className="py-2 text-right">Variance</th>
                      <th className="py-2 text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5 text-neutral-300">
                    <tr>
                      <td className="py-2.5 font-sans font-medium text-white">Line 1: Industrial Widget (Item-A)</td>
                      <td className="py-2.5 text-right">8 @ ₹200.00</td>
                      <td className="py-2.5 text-right text-emerald-400">8 rec'd</td>
                      <td className="py-2.5 text-right font-bold text-amber-400">8 @ ₹250.00</td>
                      <td className="py-2.5 text-right text-amber-400 font-bold">+₹400.00 (+25.0%)</td>
                      <td className="py-2.5 text-center">
                        <span className="bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded text-[10px]">PRICE_MISMATCH</span>
                      </td>
                    </tr>
                    <tr>
                      <td className="py-2.5 font-sans font-medium text-white">Line 2: Fastening Bolt Set (Item-B)</td>
                      <td className="py-2.5 text-right">15 @ ₹143.33</td>
                      <td className="py-2.5 text-right text-emerald-400">15 rec'd</td>
                      <td className="py-2.5 text-right text-emerald-400">15 @ ₹143.33</td>
                      <td className="py-2.5 text-right text-neutral-400">₹0.00 (0.0%)</td>
                      <td className="py-2.5 text-center">
                        <span className="bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded text-[10px]">LINE_OK</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Panel 2: Multi-turn Switch Room Resolution */}
            <div className="p-6 bg-neutral-900/60">
              <h3 className="text-sm font-bold text-white mb-3 flex items-center space-x-2">
                <MessageSquare className="w-4 h-4 text-blue-400" />
                <span>Multi-Turn Switch Collaboration Room (#invoiceops-ap)</span>
              </h3>

              <div className="space-y-3 font-mono text-xs">
                <div className="p-3 rounded-xl bg-black/60 border border-white/10 flex items-start space-x-3">
                  <Bot className="w-4 h-4 text-blue-400 mt-0.5 shrink-0" />
                  <div>
                    <span className="text-blue-400 font-bold">intake_agent:</span>
                    <span className="text-neutral-300 ml-2">Invoice INV-2026-1042 ingested. OCR confidence 0.98. Currency verified INR. Triggering 3-way matcher.</span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-black/60 border border-white/10 flex items-start space-x-3">
                  <Scale className="w-4 h-4 text-amber-400 mt-0.5 shrink-0" />
                  <div>
                    <span className="text-amber-400 font-bold">matching_engine:</span>
                    <span className="text-neutral-300 ml-2">FLAG: Line 1 unit price delta ₹50.00 exceeds tolerance limit (₹1.00 abs / 0.5% rel). Exception case created.</span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-black/60 border border-white/10 flex items-start space-x-3">
                  <UserCheck className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                  <div>
                    <span className="text-emerald-400 font-bold">procurement_owner:</span>
                    <span className="text-neutral-300 ml-2">Overnight rate surcharge authorized per Addendum #A-42. Verified PDF attachment provided.</span>
                  </div>
                </div>
              </div>

              <div className="mt-4 flex items-center justify-end">
                <button
                  onClick={() => onSelectInvoice('INV-2026-1042')}
                  className="bg-white hover:bg-neutral-100 text-black font-semibold text-xs px-4 py-2 rounded-xl transition flex items-center space-x-1.5"
                >
                  <span>Inspect Case in Studio Workbench</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* =========================================================================
          8. THE 4 FINANCE STACK ROLES
          ========================================================================= */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-neutral-950 border-t border-white/10">
        <div className="max-w-6xl mx-auto">
          
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white mb-4">
              InvoiceOps, built for every role in your finance stack
            </h2>
            <p className="max-w-2xl mx-auto text-neutral-400 text-sm sm:text-base leading-relaxed">
              Your accounts payable workflow is guardrailed at every layer. AI intake agents parse invoices, deterministic algorithms match line items, and human approvers hold ultimate authority.
            </p>
          </div>

          {/* 4 Vertical Device Style Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            
            {/* Role Card 1 */}
            <div className="bg-neutral-900 border border-white/10 rounded-3xl p-6 flex flex-col justify-between shadow-xl hover:border-blue-500/40 transition-all group">
              <div>
                <div className="w-12 h-12 rounded-2xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center mb-5 group-hover:scale-105 transition-transform">
                  <Bot className="w-6 h-6 text-blue-400" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">AI Intake Agent</h3>
                <p className="text-xs text-neutral-400 leading-relaxed mb-4">
                  Extracts structured line items, calculates normalized invoice hashes, and tags OCR confidence scores before ingestion.
                </p>
                <ul className="space-y-2 text-xs text-neutral-300">
                  <li className="flex items-center space-x-2">
                    <Check className="w-3.5 h-3.5 text-blue-400" />
                    <span>PDF & XML Extraction</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <Check className="w-3.5 h-3.5 text-blue-400" />
                    <span>Vendor ID resolution</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <Check className="w-3.5 h-3.5 text-blue-400" />
                    <span>Duplicate submission flag</span>
                  </li>
                </ul>
              </div>
              <div className="mt-6 pt-4 border-t border-white/10 font-mono text-[11px] text-blue-400">
                ROLE: intake_agent
              </div>
            </div>

            {/* Role Card 2 */}
            <div className="bg-neutral-900 border border-white/10 rounded-3xl p-6 flex flex-col justify-between shadow-xl hover:border-cyan-500/40 transition-all group">
              <div>
                <div className="w-12 h-12 rounded-2xl bg-cyan-600/20 border border-cyan-500/30 flex items-center justify-center mb-5 group-hover:scale-105 transition-transform">
                  <Scale className="w-6 h-6 text-cyan-400" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">Matching Engine</h3>
                <p className="text-xs text-neutral-400 leading-relaxed mb-4">
                  Deterministic Python Decimal engine reconciles PO, GRN, and Invoice quantities and prices with 0 floating-point drift.
                </p>
                <ul className="space-y-2 text-xs text-neutral-300">
                  <li className="flex items-center space-x-2">
                    <Check className="w-3.5 h-3.5 text-cyan-400" />
                    <span>0 tolerance on quantity</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <Check className="w-3.5 h-3.5 text-cyan-400" />
                    <span>₹1.00 abs / 0.5% rel price</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <Check className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Line-item variance tags</span>
                  </li>
                </ul>
              </div>
              <div className="mt-6 pt-4 border-t border-white/10 font-mono text-[11px] text-cyan-400">
                ROLE: matching_engine
              </div>
            </div>

            {/* Role Card 3 */}
            <div className="bg-neutral-900 border border-white/10 rounded-3xl p-6 flex flex-col justify-between shadow-xl hover:border-emerald-500/40 transition-all group">
              <div>
                <div className="w-12 h-12 rounded-2xl bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center mb-5 group-hover:scale-105 transition-transform">
                  <MessageSquare className="w-6 h-6 text-emerald-400" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">AP Clerk & Owner</h3>
                <p className="text-xs text-neutral-400 leading-relaxed mb-4">
                  Collaborative Switch rooms bring procurement owners and AP clerks together to resolve price and quantity discrepancies.
                </p>
                <ul className="space-y-2 text-xs text-neutral-300">
                  <li className="flex items-center space-x-2">
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Evidence attachment</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Threaded dispute audit</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Vendor communications</span>
                  </li>
                </ul>
              </div>
              <div className="mt-6 pt-4 border-t border-white/10 font-mono text-[11px] text-emerald-400">
                ROLE: ap_clerk / procurement
              </div>
            </div>

            {/* Role Card 4 */}
            <div className="bg-neutral-900 border border-white/10 rounded-3xl p-6 flex flex-col justify-between shadow-xl hover:border-purple-500/40 transition-all group">
              <div>
                <div className="w-12 h-12 rounded-2xl bg-purple-600/20 border border-purple-500/30 flex items-center justify-center mb-5 group-hover:scale-105 transition-transform">
                  <Lock className="w-6 h-6 text-purple-400" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">Finance Approver</h3>
                <p className="text-xs text-neutral-400 leading-relaxed mb-4">
                  Human-in-the-loop sign-off authority. Produces downstream payment-ready records with zero payment execution capability.
                </p>
                <ul className="space-y-2 text-xs text-neutral-300">
                  <li className="flex items-center space-x-2">
                    <Check className="w-3.5 h-3.5 text-purple-400" />
                    <span>Exclusive approval auth</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <Check className="w-3.5 h-3.5 text-purple-400" />
                    <span>403 Forbidden on agents</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <Check className="w-3.5 h-3.5 text-purple-400" />
                    <span>Idempotent SHA-256 keys</span>
                  </li>
                </ul>
              </div>
              <div className="mt-6 pt-4 border-t border-white/10 font-mono text-[11px] text-purple-400">
                ROLE: finance_approver
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* =========================================================================
          9. SIGNATURE FOOTER WITH INVERTED NOTCH & GIANT WATERMARK (Image 4 from user upload)
          ========================================================================= */}
      <footer className="relative bg-black pt-16 pb-12 px-4 sm:px-6 lg:px-8 border-t border-white/10 overflow-hidden">
        
        {/* Top Inverted Notch / Ear Cutout Feature from Image 4 */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-64 h-4 bg-[#121212] rounded-b-2xl border-b border-x border-white/10 pointer-events-none" />

        <div className="relative max-w-6xl mx-auto z-10">
          
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 pb-12 border-b border-white/10">
            
            {/* Brand Column (Left 5 Cols) */}
            <div className="md:col-span-5 space-y-4">
              <div className="flex items-center space-x-3">
                {/* 3D Glossy Blue Icon */}
                <div className="relative w-8 h-8 rounded-xl bg-gradient-to-b from-[#3884FF] via-[#1A6DFF] to-[#0051E8] shadow-[0_2px_10px_rgba(0,102,255,0.6)] flex items-center justify-center p-0.5 border border-white/20 shrink-0">
                  <div className="absolute top-0.5 left-1 right-1 h-3 rounded-full bg-gradient-to-b from-white/90 to-transparent opacity-85" />
                  <FileText className="w-4 h-4 text-white" />
                </div>
                <span className="font-bold text-lg text-white tracking-tight">InvoiceOps</span>
                <span className="text-xs text-neutral-400 font-mono">macOS / Web</span>
              </div>

              <h4 className="text-lg font-bold text-white leading-snug">
                Match once. <br />
                <span className="font-serif italic font-normal text-blue-400">Reconcile anytime.</span>
              </h4>

              <p className="text-xs text-neutral-400 leading-relaxed max-w-sm">
                InvoiceOps saves finance teams hundreds of hours by autonomously ingesting vendor invoices, verifying line items against POs and GRNs, and resolving exceptions in real-time Switch collaboration rooms.
              </p>

              <div>
                <button
                  onClick={() => onEnterStudio('inbox')}
                  className="bg-white hover:bg-neutral-100 text-black font-semibold text-xs px-5 py-2.5 rounded-full shadow-md transition flex items-center space-x-2 active:scale-95"
                >
                  <Zap className="w-3.5 h-3.5 fill-black text-black" />
                  <span>Launch Studio Workbench</span>
                </button>
              </div>

              <div className="pt-2 text-[11px] text-neutral-500 font-mono space-y-1">
                <p>© 2026 InvoiceOps. All rights reserved.</p>
                <p>Built with 💙 for Autonomous Business Workflows</p>
              </div>
            </div>

            {/* Links Columns (Right 7 Cols) */}
            <div className="md:col-span-7 grid grid-cols-2 sm:grid-cols-3 gap-6 text-xs">
              
              {/* Column 1: Navigation */}
              <div>
                <h5 className="font-bold text-white uppercase tracking-wider text-[11px] mb-3">Platform</h5>
                <ul className="space-y-2 text-neutral-400 font-medium">
                  <li>
                    <button onClick={() => onEnterStudio('overview')} className="hover:text-white transition">Overview</button>
                  </li>
                  <li>
                    <button onClick={() => onEnterStudio('inbox')} className="hover:text-white transition">AP Invoices Inbox</button>
                  </li>
                  <li>
                    <button onClick={() => onEnterStudio('payment-ready')} className="hover:text-white transition">Payment-Ready Feed</button>
                  </li>
                  <li>
                    <button onClick={() => onEnterStudio('vendors')} className="hover:text-white transition">Vendor Registry</button>
                  </li>
                  <li>
                    <button onClick={() => onEnterStudio('policy')} className="hover:text-white transition">Matching Policies</button>
                  </li>
                  <li>
                    <button onClick={onOpenSwitchRoom} className="hover:text-white transition text-blue-400 font-semibold">Switch Room</button>
                  </li>
                </ul>
              </div>

              {/* Column 2: Architecture */}
              <div>
                <h5 className="font-bold text-white uppercase tracking-wider text-[11px] mb-3">Architecture</h5>
                <ul className="space-y-2 text-neutral-400 font-medium">
                  <li><span className="text-neutral-300">Deterministic Engine</span></li>
                  <li><span className="text-neutral-300">Pure Decimal Precision</span></li>
                  <li><span className="text-neutral-300">Zero Payment Rails</span></li>
                  <li><span className="text-neutral-300">Tolerance Limits</span></li>
                  <li><span className="text-neutral-300">Duplicate Hash Shield</span></li>
                  <li><span className="text-neutral-300">Append-Only Audit</span></li>
                </ul>
              </div>

              {/* Column 3: Enterprise Specs */}
              <div>
                <h5 className="font-bold text-white uppercase tracking-wider text-[11px] mb-3">Enterprise Specs</h5>
                <ul className="space-y-2 text-neutral-400 font-medium">
                  <li><span className="text-white font-semibold">Production Ready</span></li>
                  <li><span className="text-blue-400 font-semibold">Autonomous AP Engine</span></li>
                  <li><span className="text-emerald-400 font-semibold">16/16 P0 Tests Passed</span></li>
                  <li>
                    <a href="/docs" target="_blank" rel="noreferrer" className="hover:text-white transition flex items-center gap-1">
                      <span>OpenAPI 3.1 Spec</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </li>
                  <li><span className="text-neutral-300">FastAPI + SQLite</span></li>
                  <li><span className="text-neutral-300">React 18 + Vite</span></li>
                </ul>
              </div>

            </div>

          </div>

          {/* GIANT WATERMARK TEXT (Image 4 from user upload) */}
          <div className="pt-8 select-none pointer-events-none text-center">
            <h1 className="text-[12vw] font-black tracking-tighter text-white/[0.04] leading-none uppercase">
              InvoiceOps
            </h1>
          </div>

        </div>

      </footer>

    </div>
  );
};
