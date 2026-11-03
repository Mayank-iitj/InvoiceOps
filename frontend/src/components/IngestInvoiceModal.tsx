import React, { useState } from 'react';
import { 
  X, 
  UploadCloud, 
  FileText, 
  Check, 
  Sparkles, 
  Plus, 
  Trash2, 
  AlertCircle,
  Zap,
  ArrowRight
} from 'lucide-react';
import { api } from '../services/api';

interface IngestInvoiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (newInvoiceId: string) => void;
}

export const IngestInvoiceModal: React.FC<IngestInvoiceModalProps> = ({
  isOpen,
  onClose,
  onSuccess
}) => {
  const [activeTab, setActiveTab] = useState<'quick' | 'custom' | 'file'>('quick');
  const [vendorId, setVendorId] = useState('VND-001');
  const [poId, setPoId] = useState('PO-2026-0082');
  const [invoiceNumber, setInvoiceNumber] = useState(`INV-2026-${Math.floor(1000 + Math.random() * 9000)}`);
  const [invoiceDate, setInvoiceDate] = useState(new Date().toISOString().slice(0, 10));
  const [currency, setCurrency] = useState('INR');
  const [lines, setLines] = useState<any[]>([
    { description: 'Industrial Widget (Item-A)', quantity: '8', unit_price: '200.00' },
    { description: 'Fastening Bolt Set (Item-B)', quantity: '15', unit_price: '143.33' }
  ]);
  const [autoMatch, setAutoMatch] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  if (!isOpen) return null;

  const quickTemplates = [
    {
      title: 'Clean 3-Way Match',
      desc: 'PO & GRN quantity (8 & 15 units) and agreed unit rates match within 0.00% delta.',
      badge: 'MATCH_OK',
      badgeClass: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
      apply: () => {
        setInvoiceNumber(`INV-2026-${Math.floor(2000 + Math.random() * 5000)}`);
        setLines([
          { description: 'Industrial Widget (Item-A)', quantity: '8', unit_price: '200.00' },
          { description: 'Fastening Bolt Set (Item-B)', quantity: '15', unit_price: '143.33' }
        ]);
      }
    },
    {
      title: 'Price Surcharge Discrepancy',
      desc: 'Line 1 billed at ₹250.00 instead of PO rate ₹200.00 (+25.0% variance over ₹1.00 tolerance).',
      badge: 'PRICE_MISMATCH',
      badgeClass: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
      apply: () => {
        setInvoiceNumber(`INV-2026-${Math.floor(2000 + Math.random() * 5000)}`);
        setLines([
          { description: 'Industrial Widget (Item-A)', quantity: '8', unit_price: '250.00' },
          { description: 'Fastening Bolt Set (Item-B)', quantity: '15', unit_price: '143.33' }
        ]);
      }
    },
    {
      title: 'Duplicate Submission Test',
      desc: 'Re-submits normalized invoice number INV-2026-1041 to verify cryptographic hash suppression.',
      badge: 'DUPLICATE_CHECK',
      badgeClass: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
      apply: () => {
        setInvoiceNumber('INV-2026-1041');
        setLines([
          { description: 'Industrial Widget (Item-A)', quantity: '8', unit_price: '200.00' }
        ]);
      }
    },
    {
      title: 'Zero-Delivered Quantity Variance',
      desc: 'Billed 10 brackets, but Goods Receipt Note GRN-2026-0041 shows 0 units received.',
      badge: 'QTY_MISMATCH',
      badgeClass: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
      apply: () => {
        setInvoiceNumber(`INV-2026-${Math.floor(2000 + Math.random() * 5000)}`);
        setLines([
          { description: 'Heavy Duty Structural Bracket', quantity: '10', unit_price: '150.00' }
        ]);
      }
    }
  ];

  const handleAddLine = () => {
    setLines([...lines, { description: 'New Material Item', quantity: '1', unit_price: '100.00' }]);
  };

  const handleRemoveLine = (idx: number) => {
    if (lines.length <= 1) return;
    setLines(lines.filter((_, i) => i !== idx));
  };

  const calculateTotal = () => {
    return lines.reduce((sum, line) => {
      const q = parseFloat(line.quantity) || 0;
      const p = parseFloat(line.unit_price) || 0;
      return sum + (q * p);
    }, 0).toFixed(2);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const total = calculateTotal();
      const payload = {
        invoice_number: invoiceNumber,
        vendor_id: vendorId,
        po_id: poId,
        invoice_date: invoiceDate,
        currency,
        invoice_total: total,
        lines: lines.map((l, i) => ({
          line_number: i + 1,
          description: l.description,
          quantity: l.quantity,
          unit_price: l.unit_price
        }))
      };

      const result = await api.createInvoice(payload);
      const newId = result.invoice_id;

      // Auto run match if requested
      if (autoMatch) {
        try {
          await api.runMatch(newId);
        } catch (mErr) {
          console.warn("Initial auto-match notice:", mErr);
        }
      }

      onSuccess(newId);
      onClose();
    } catch (err: any) {
      alert(`Invoice intake failed: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/85 backdrop-blur-sm flex items-center justify-center p-3 sm:p-5">
      <div className="bg-[#181818] rounded-2xl shadow-[0_20px_70px_rgba(0,0,0,0.85)] max-w-2xl w-full border border-white/15 text-white overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="px-6 py-4 bg-neutral-900 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <UploadCloud className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-sm sm:text-base text-white">Ingest Vendor Invoice</h3>
              <p className="text-xs text-neutral-400">Extracts line items, validates duplicate hashes, and triggers 3-way matching</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-neutral-400 hover:text-white p-1 rounded-lg hover:bg-white/10 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Selection */}
        <div className="px-6 pt-3 pb-2 bg-neutral-950 border-b border-white/10 flex items-center space-x-2 text-xs">
          <button
            type="button"
            onClick={() => setActiveTab('quick')}
            className={`px-3 py-1.5 rounded-lg font-medium transition ${
              activeTab === 'quick'
                ? 'bg-blue-600 text-white'
                : 'text-neutral-400 hover:text-white hover:bg-white/5'
            }`}
          >
            Quick Templates
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('custom')}
            className={`px-3 py-1.5 rounded-lg font-medium transition ${
              activeTab === 'custom'
                ? 'bg-blue-600 text-white'
                : 'text-neutral-400 hover:text-white hover:bg-white/5'
            }`}
          >
            Manual Line Items
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('file')}
            className={`px-3 py-1.5 rounded-lg font-medium transition ${
              activeTab === 'file'
                ? 'bg-blue-600 text-white'
                : 'text-neutral-400 hover:text-white hover:bg-white/5'
            }`}
          >
            Upload PDF / Document
          </button>
        </div>

        {/* Body Content */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-5">
          
          {/* Quick Templates View */}
          {activeTab === 'quick' && (
            <div className="space-y-3">
              <span className="text-xs font-semibold text-neutral-400 block mb-1">
                Select a verification template:
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {quickTemplates.map((t, idx) => (
                  <div
                    key={idx}
                    onClick={t.apply}
                    className="p-3.5 rounded-xl bg-neutral-900 border border-white/10 hover:border-blue-500/50 hover:bg-neutral-850 transition cursor-pointer flex flex-col justify-between group"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="font-bold text-xs text-white group-hover:text-blue-300 transition">
                          {t.title}
                        </span>
                        <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${t.badgeClass}`}>
                          {t.badge}
                        </span>
                      </div>
                      <p className="text-[11px] text-neutral-400 leading-snug font-sans">
                        {t.desc}
                      </p>
                    </div>
                    <span className="mt-3 text-[10px] font-mono text-blue-400 flex items-center gap-1">
                      <span>Click to load</span>
                      <ArrowRight className="w-3 h-3" />
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* File Upload Tab */}
          {activeTab === 'file' && (
            <div
              onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
              onDragLeave={() => setDragActive(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragActive(false);
                if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                  setUploadedFile(e.dataTransfer.files[0]);
                }
              }}
              className={`border-2 border-dashed rounded-2xl p-8 text-center transition ${
                dragActive ? 'border-blue-500 bg-blue-500/10' : 'border-white/15 bg-neutral-900/50'
              }`}
            >
              <FileText className="w-10 h-10 text-neutral-400 mx-auto mb-3" />
              <h4 className="text-sm font-semibold text-white">
                {uploadedFile ? uploadedFile.name : 'Drag & drop invoice PDF or XML'}
              </h4>
              <p className="text-xs text-neutral-400 mt-1">
                Supported formats: PDF, JSON, XML (max 15MB)
              </p>
              <input
                type="file"
                id="file-upload"
                className="hidden"
                accept=".pdf,.json,.xml"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setUploadedFile(e.target.files[0]);
                  }
                }}
              />
              <label
                htmlFor="file-upload"
                className="mt-4 inline-block bg-white hover:bg-neutral-200 text-black text-xs font-semibold px-4 py-2 rounded-xl cursor-pointer transition shadow"
              >
                Browse Files
              </label>
            </div>
          )}

          {/* Core Invoice Metadata Fields */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div>
              <label className="text-[11px] font-semibold text-neutral-400 uppercase font-mono block mb-1">
                Invoice Number
              </label>
              <input
                type="text"
                value={invoiceNumber}
                onChange={(e) => setInvoiceNumber(e.target.value)}
                required
                className="w-full bg-black border border-white/15 rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="text-[11px] font-semibold text-neutral-400 uppercase font-mono block mb-1">
                Purchase Order ID
              </label>
              <input
                type="text"
                value={poId}
                onChange={(e) => setPoId(e.target.value)}
                required
                className="w-full bg-black border border-white/15 rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="text-[11px] font-semibold text-neutral-400 uppercase font-mono block mb-1">
                Vendor ID
              </label>
              <input
                type="text"
                value={vendorId}
                onChange={(e) => setVendorId(e.target.value)}
                required
                className="w-full bg-black border border-white/15 rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="text-[11px] font-semibold text-neutral-400 uppercase font-mono block mb-1">
                Currency
              </label>
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                className="w-full bg-black border border-white/15 rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-blue-500"
              >
                <option value="INR">INR (₹)</option>
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR (€)</option>
              </select>
            </div>
          </div>

          {/* Line Items Table */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-neutral-300 uppercase font-mono tracking-wider">
                Line Items ({lines.length})
              </span>
              <button
                type="button"
                onClick={handleAddLine}
                className="text-xs text-blue-400 hover:text-blue-300 font-semibold flex items-center space-x-1"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Item</span>
              </button>
            </div>

            <div className="space-y-2">
              {lines.map((line, idx) => (
                <div key={idx} className="flex items-center space-x-2 bg-neutral-900 p-2.5 rounded-xl border border-white/10">
                  <span className="text-neutral-500 font-mono text-xs w-6">{idx + 1}.</span>
                  <input
                    type="text"
                    value={line.description}
                    onChange={(e) => {
                      const updated = [...lines];
                      updated[idx].description = e.target.value;
                      setLines(updated);
                    }}
                    placeholder="Item description"
                    className="flex-1 bg-black border border-white/10 rounded-lg px-2.5 py-1 text-xs text-white"
                  />
                  <input
                    type="number"
                    value={line.quantity}
                    onChange={(e) => {
                      const updated = [...lines];
                      updated[idx].quantity = e.target.value;
                      setLines(updated);
                    }}
                    placeholder="Qty"
                    className="w-16 bg-black border border-white/10 rounded-lg px-2 py-1 text-xs text-right text-white font-mono"
                  />
                  <input
                    type="text"
                    value={line.unit_price}
                    onChange={(e) => {
                      const updated = [...lines];
                      updated[idx].unit_price = e.target.value;
                      setLines(updated);
                    }}
                    placeholder="Rate"
                    className="w-24 bg-black border border-white/10 rounded-lg px-2 py-1 text-xs text-right text-white font-mono"
                  />
                  <button
                    type="button"
                    onClick={() => handleRemoveLine(idx)}
                    disabled={lines.length <= 1}
                    className="p-1 text-neutral-500 hover:text-red-400 disabled:opacity-30 transition"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>

            <div className="mt-3 flex items-center justify-between px-3 py-2 bg-neutral-900/60 rounded-xl border border-white/5 text-xs font-mono">
              <span className="text-neutral-400">Total Billed:</span>
              <span className="text-base font-bold text-white">₹{calculateTotal()} {currency}</span>
            </div>
          </div>

          {/* Trigger matching checkbox */}
          <div className="flex items-center space-x-2.5 bg-neutral-900 p-3 rounded-xl border border-white/10">
            <input
              type="checkbox"
              id="auto-match"
              checked={autoMatch}
              onChange={(e) => setAutoMatch(e.target.checked)}
              className="w-4 h-4 rounded text-blue-600 focus:ring-0 bg-black border-white/20 cursor-pointer"
            />
            <label htmlFor="auto-match" className="text-xs text-neutral-300 cursor-pointer select-none">
              Automatically trigger Python 3-way matching engine immediately after intake
            </label>
          </div>

          {/* Footer Submit */}
          <div className="pt-2 flex items-center justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-medium text-neutral-400 hover:text-white transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold text-xs px-5 py-2.5 rounded-xl shadow-md transition flex items-center space-x-1.5"
            >
              {isSubmitting ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Ingesting...</span>
                </>
              ) : (
                <>
                  <Zap className="w-3.5 h-3.5" />
                  <span>Ingest & Process Invoice</span>
                </>
              )}
            </button>
          </div>

        </form>

      </div>
    </div>
  );
};

