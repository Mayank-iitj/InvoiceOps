import React from 'react';
import { 
  FileText, 
  RotateCcw, 
  MessageSquare 
} from 'lucide-react';
import { UserRole } from '../types';
import { getGlobalRole, setGlobalRole, api } from '../services/api';

interface NavbarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  onOpenSwitchRoom: () => void;
  onRefresh: () => void;
}

const ROLES: { id: UserRole; label: string }[] = [
  { id: 'ap_clerk', label: 'AP Clerk (Human)' },
  { id: 'procurement_owner', label: 'Procurement Owner' },
  { id: 'finance_approver', label: 'Finance Approver' },
  { id: 'invoice_intake_agent', label: 'Intake Agent (AI)' },
  { id: 'invoice_match_agent', label: 'Reconcile Agent (AI)' },
  { id: 'ap_admin', label: 'AP Admin' },
];

export const Navbar: React.FC<NavbarProps> = ({ 
  currentTab, 
  setCurrentTab, 
  onOpenSwitchRoom,
  onRefresh 
}) => {
  const [role, setRole] = React.useState<UserRole>(getGlobalRole());
  const [isResetting, setIsResetting] = React.useState(false);

  const handleRoleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newRole = e.target.value as UserRole;
    setRole(newRole);
    setGlobalRole(newRole);
    onRefresh();
  };

  const handleReset = async () => {
    if (!window.confirm("Reset database and reload clean demo fixtures?")) return;
    setIsResetting(true);
    try {
      await api.demoReset();
      alert("Database reset and re-seeded successfully.");
      onRefresh();
    } catch (err: any) {
      alert(`Reset failed: ${err.message}`);
    } finally {
      setIsResetting(false);
    }
  };

  return (
    <div className="sticky top-0 z-50 w-full flex flex-col items-center">
      {/* Ambient Royal Blue Glow Behind the Notch - only shown on studio workbench pages */}
      {currentTab !== 'overview' && (
        <div className="absolute top-0 left-0 right-0 h-28 bg-gradient-to-b from-[#1846E8] via-[#0E2C9E]/50 to-transparent pointer-events-none" />
      )}

      {/* Dynamic Island Notch Attached to the Top Edge - Generously sized to enclose all tiles & controls */}
      <div className="relative z-10 flex items-center justify-between bg-black text-white h-14 px-6 sm:px-8 rounded-b-[24px] shadow-[0_14px_45px_rgba(0,0,0,0.85)] w-fit max-w-[98vw] border-b border-x border-white/5">
        
        {/* Left Inverted Ear (Concave Fillet into Top Ceiling) */}
        <div className="absolute -left-5 top-0 w-5 h-5 pointer-events-none overflow-hidden">
          <svg viewBox="0 0 20 20" className="w-5 h-5 fill-black">
            <path d="M20 0 V20 A20 20 0 0 0 0 0 Z" />
          </svg>
        </div>

        {/* Right Inverted Ear (Concave Fillet into Top Ceiling) */}
        <div className="absolute -right-5 top-0 w-5 h-5 pointer-events-none overflow-hidden">
          <svg viewBox="0 0 20 20" className="w-5 h-5 fill-black">
            <path d="M0 0 V20 A20 20 0 0 1 20 0 Z" />
          </svg>
        </div>

        {/* Left: 3D Glossy App Icon + Brand Name */}
        <div className="flex items-center space-x-3 shrink-0 mr-6 sm:mr-8">
          <button 
            onClick={() => setCurrentTab('overview')}
            className="flex items-center space-x-2.5 focus:outline-none group"
            title="InvoiceOps Landing Page"
          >
            {/* Glossy 3D Blue App Icon matching screenshot */}
            <div className="relative w-8 h-8 rounded-xl bg-gradient-to-b from-[#3884FF] via-[#1A6DFF] to-[#0051E8] shadow-[0_2px_10px_rgba(0,102,255,0.5),inset_0_1px_1px_rgba(255,255,255,0.7)] flex items-center justify-center p-0.5 border border-white/20 shrink-0 overflow-hidden group-hover:scale-105 transition-transform">
              {/* Specular highlight glass sheen */}
              <div className="absolute top-0.5 left-1 right-1 h-3 rounded-full bg-gradient-to-b from-white/90 to-transparent opacity-85 pointer-events-none" />
              <FileText className="w-4 h-4 text-white drop-shadow-[0_1px_2px_rgba(0,0,0,0.5)]" />
            </div>
            
            <span className="font-bold text-[15px] tracking-tight text-white group-hover:text-neutral-200 transition whitespace-nowrap">
              InvoiceOps
            </span>
          </button>
        </div>

        {/* Center: Clean Nav Links (Features / FAQ / Pricing style from screenshot) */}
        <nav className="flex items-center space-x-5 sm:space-x-7 shrink-0">
          <button
            onClick={() => setCurrentTab('overview')}
            className={`text-sm transition-colors whitespace-nowrap ${
              currentTab === 'overview' 
                ? 'text-white font-semibold' 
                : 'text-neutral-400 hover:text-white font-medium'
            }`}
          >
            Overview
          </button>

          <button
            onClick={() => setCurrentTab('inbox')}
            className={`text-sm transition-colors whitespace-nowrap ${
              currentTab === 'inbox' 
                ? 'text-white font-semibold' 
                : 'text-neutral-400 hover:text-white font-medium'
            }`}
          >
            AP Invoices
          </button>

          <button
            onClick={() => setCurrentTab('payment-ready')}
            className={`text-sm transition-colors whitespace-nowrap ${
              currentTab === 'payment-ready' 
                ? 'text-white font-semibold' 
                : 'text-neutral-400 hover:text-white font-medium'
            }`}
          >
            Payment-Ready
          </button>

          <button
            onClick={() => setCurrentTab('vendors')}
            className={`text-sm transition-colors whitespace-nowrap ${
              currentTab === 'vendors' 
                ? 'text-white font-semibold' 
                : 'text-neutral-400 hover:text-white font-medium'
            }`}
          >
            Vendors
          </button>

          <button
            onClick={() => setCurrentTab('policy')}
            className={`text-sm transition-colors whitespace-nowrap ${
              currentTab === 'policy' 
                ? 'text-white font-semibold' 
                : 'text-neutral-400 hover:text-white font-medium'
            }`}
          >
            Policies
          </button>

          <button
            onClick={() => setCurrentTab('audit')}
            className={`text-sm transition-colors whitespace-nowrap ${
              currentTab === 'audit' 
                ? 'text-white font-semibold' 
                : 'text-neutral-400 hover:text-white font-medium'
            }`}
          >
            Audit Log
          </button>
        </nav>

        {/* Right: White Pill Button (Apple / Download style) + Role + Reset fully covered inside notch */}
        <div className="flex items-center space-x-3 shrink-0 ml-6 sm:ml-8 pl-1">
          {/* White Pill Action Button */}
          <button
            onClick={onOpenSwitchRoom}
            className="bg-white hover:bg-neutral-100 text-black font-semibold text-xs sm:text-[13px] rounded-full px-4 py-1.5 shadow-[0_2px_12px_rgba(255,255,255,0.25)] hover:shadow-[0_2px_16px_rgba(255,255,255,0.4)] transition-all flex items-center space-x-1.5 whitespace-nowrap shrink-0 active:scale-95"
            title="Open Switch Collaboration Console"
          >
            <MessageSquare className="w-3.5 h-3.5 fill-black text-black shrink-0" />
            <span>Switch Room</span>
          </button>

          {/* Acting Role Dropdown (Discreet Glass Pill) */}
          <div className="hidden sm:flex items-center bg-white/10 hover:bg-white/15 border border-white/10 rounded-full px-3 py-1 text-xs whitespace-nowrap shrink-0 transition">
            <span className="text-[10px] text-neutral-400 uppercase font-semibold mr-1.5">Role:</span>
            <select
              value={role}
              onChange={handleRoleChange}
              className="bg-transparent text-white font-medium focus:outline-none cursor-pointer pr-1 text-xs"
            >
              {ROLES.map((r) => (
                <option key={r.id} value={r.id} className="bg-[#181818] text-white">
                  {r.label}
                </option>
              ))}
            </select>
          </div>

          {/* Reset Database Button */}
          <button
            onClick={handleReset}
            disabled={isResetting}
            className="p-1.5 text-neutral-400 hover:text-white hover:bg-white/10 rounded-full transition shrink-0 ml-0.5"
            title="Reset Demo Data"
          >
            <RotateCcw className={`w-3.5 h-3.5 ${isResetting ? 'animate-spin text-blue-400' : ''}`} />
          </button>
        </div>

      </div>
    </div>
  );
};
