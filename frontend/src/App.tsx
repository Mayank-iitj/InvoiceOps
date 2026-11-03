import React from 'react';
import { Navbar } from './components/Navbar';
import { LandingPage } from './pages/LandingPage';
import { InboxPage } from './pages/InboxPage';
import { InvoiceDetailPage } from './pages/InvoiceDetailPage';
import { PaymentReadyPage } from './pages/PaymentReadyPage';
import { VendorsPolicyPage } from './pages/VendorsPolicyPage';
import { AuditTrailPage } from './pages/AuditTrailPage';
import { SwitchRoomModal } from './components/SwitchRoomModal';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = React.useState<string>('overview');
  const [selectedInvoiceId, setSelectedInvoiceId] = React.useState<string | null>(null);
  const [isSwitchModalOpen, setIsSwitchModalOpen] = React.useState<boolean>(false);
  const [refreshKey, setRefreshKey] = React.useState<number>(0);

  const handleSelectInvoice = (id: string) => {
    setSelectedInvoiceId(id);
    setCurrentTab('invoice-detail');
  };

  const handleBackToInbox = () => {
    setSelectedInvoiceId(null);
    setCurrentTab('inbox');
  };

  const handleRefresh = () => {
    setRefreshKey((k) => k + 1);
  };

  return (
    <div className="min-h-screen bg-[#121212] text-text-primary flex flex-col font-sans selection:bg-blue-500/30 selection:text-blue-300">
      {/* Dynamic Island Attached Notch Top Navigation */}
      <Navbar
        currentTab={currentTab}
        setCurrentTab={(tab) => {
          setSelectedInvoiceId(null);
          setCurrentTab(tab);
        }}
        onOpenSwitchRoom={() => setIsSwitchModalOpen(true)}
        onRefresh={handleRefresh}
      />

      {/* Main Viewport */}
      {currentTab === 'overview' ? (
        <div className="flex-1 w-full">
          <LandingPage
            onEnterStudio={(tab) => setCurrentTab(tab || 'inbox')}
            onOpenSwitchRoom={() => setIsSwitchModalOpen(true)}
            onSelectInvoice={handleSelectInvoice}
          />
        </div>
      ) : (
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {currentTab === 'inbox' && (
            <InboxPage
              key={refreshKey}
              onSelectInvoice={handleSelectInvoice}
              onOpenSwitchRoom={() => setIsSwitchModalOpen(true)}
            />
          )}

          {currentTab === 'invoice-detail' && selectedInvoiceId && (
            <InvoiceDetailPage
              key={`${selectedInvoiceId}-${refreshKey}`}
              invoiceId={selectedInvoiceId}
              onBack={handleBackToInbox}
              onOpenSwitchRoom={() => setIsSwitchModalOpen(true)}
            />
          )}

          {currentTab === 'payment-ready' && (
            <PaymentReadyPage key={refreshKey} />
          )}

          {currentTab === 'vendors' && (
            <VendorsPolicyPage key={`vendors-${refreshKey}`} initialTab="vendors" />
          )}

          {currentTab === 'policy' && (
            <VendorsPolicyPage key={`policy-${refreshKey}`} initialTab="policy" />
          )}

          {currentTab === 'audit' && (
            <AuditTrailPage
              key={`audit-${refreshKey}`}
              onSelectInvoice={handleSelectInvoice}
            />
          )}
        </main>
      )}

      {/* Switch Collaboration Room Modal */}
      <SwitchRoomModal
        isOpen={isSwitchModalOpen}
        onClose={() => setIsSwitchModalOpen(false)}
        selectedInvoiceId={selectedInvoiceId || 'INV-2026-1042'}
      />

      {/* Dark Footer */}
      <footer className="border-t border-dark-border bg-dark-surface py-4 text-center text-xs text-text-muted font-mono">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>InvoiceOps Studio</span>
          <span className="text-[11px] text-blue-400">Deterministic Matching Engine • Pure Decimal • Zero Payment Rails</span>
        </div>
      </footer>
    </div>
  );
};
