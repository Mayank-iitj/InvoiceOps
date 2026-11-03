import React from 'react';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const norm = (status || '').toLowerCase().replace(/_/g, ' ');

  let bg = 'bg-neutral-800/80 text-neutral-300 border-neutral-700';
  let dotColor = 'bg-neutral-400';
  let label = status;

  switch (norm) {
    case 'pass':
    case 'ready for approval':
      bg = 'bg-emerald-950/40 text-supabase-400 border-supabase-500/30';
      dotColor = 'bg-supabase-500 shadow-[0_0_8px_rgba(62,207,142,0.8)]';
      label = status === 'pass' ? 'Pass' : 'Ready for Approval';
      break;

    case 'approved':
      bg = 'bg-teal-950/40 text-teal-300 border-teal-500/30';
      dotColor = 'bg-teal-400 shadow-[0_0_8px_rgba(45,212,191,0.8)]';
      label = 'Approved';
      break;

    case 'payment ready':
    case 'ready for downstream payment':
      bg = 'bg-cyan-950/40 text-cyan-300 border-cyan-500/30';
      dotColor = 'bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.8)]';
      label = 'Payment Ready';
      break;

    case 'blocked':
    case 'fail':
    case 'exception open':
      bg = 'bg-red-950/40 text-red-400 border-red-500/30';
      dotColor = 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]';
      label = status === 'fail' ? 'Fail' : 'Blocked (Exception Open)';
      break;

    case 'duplicate blocked':
      bg = 'bg-purple-950/40 text-purple-400 border-purple-500/30';
      dotColor = 'bg-purple-500 shadow-[0_0_8px_rgba(168,85,247,0.8)]';
      label = 'Duplicate Blocked';
      break;

    case 'needs human':
    case 'needs review':
    case 'awaiting human':
      bg = 'bg-amber-950/40 text-amber-400 border-amber-500/30';
      dotColor = 'bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.8)]';
      label = 'Awaiting Human Input';
      break;

    case 'received':
    case 'draft':
    case 'extracting':
    case 'reconciling':
      bg = 'bg-blue-950/40 text-blue-400 border-blue-500/30';
      dotColor = 'bg-blue-400 shadow-[0_0_8px_rgba(96,165,250,0.8)]';
      label = status.charAt(0).toUpperCase() + status.slice(1);
      break;

    case 'rejected':
      bg = 'bg-rose-950/40 text-rose-400 border-rose-500/30';
      dotColor = 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.8)]';
      label = 'Rejected';
      break;
  }

  const px = size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-xs';

  return (
    <span className={`inline-flex items-center font-medium border rounded-md ${bg} ${px} font-mono tracking-wide`}>
      <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${dotColor} shrink-0`}></span>
      <span>{label}</span>
    </span>
  );
};
