import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { NPVWaterfallChart } from '@/components/sotreg/NPVWaterfallChart';
import { PaybackTimelineChart } from '@/components/sotreg/PaybackTimelineChart';
import { EfficientFrontierChart } from '@/components/sotreg/EfficientFrontierChart';
import { CO2ValorizationPanel } from '@/components/sotreg/CO2ValorizationPanel';
import { SupernetworkFlowDiagram } from '@/components/sotreg/SupernetworkFlowDiagram';

/* ------------------------------------------------------------------ */
/*  Tab definitions                                                    */
/* ------------------------------------------------------------------ */

interface TabDef {
  label: string;
  icon: string;
}

const TABS: TabDef[] = [
  { label: 'VAN & Payback', icon: 'account_balance' },
  { label: 'Portefeuille', icon: 'pie_chart' },
  { label: 'CO\u2082', icon: 'eco' },
  { label: 'Supernetwork', icon: 'hub' },
];

/* ------------------------------------------------------------------ */
/*  Main page component                                                */
/* ------------------------------------------------------------------ */

export function AdvancedFinanceDashboardPage() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<number>(0);

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* ── Page header ─────────────────────────────────────────────── */}
      <div>
        <h1 className="font-sans text-xl font-bold text-on-surface">
          {t('sotreg.advancedFinance.title', 'Finance Avancee')}
        </h1>
        <p className="font-sans text-sm text-on-surface-variant mt-1">
          {t(
            'sotreg.advancedFinance.subtitle',
            'Module M5 — Analyse Financiere',
          )}
        </p>
      </div>

      {/* ── Tab bar ─────────────────────────────────────────────────── */}
      <div className="flex gap-1 bg-surface-container-low/50 rounded-xl p-1">
        {TABS.map((tab, index) => (
          <button
            key={tab.label}
            type="button"
            onClick={() => setActiveTab(index)}
            className={
              index === activeTab
                ? 'bg-surface-container-lowest text-primary font-medium shadow-sm rounded-lg px-4 py-2 inline-flex items-center gap-2 transition-colors'
                : 'text-on-surface-variant hover:text-on-surface rounded-lg px-4 py-2 inline-flex items-center gap-2 transition-colors'
            }
          >
            <span className="material-symbols-outlined text-lg">
              {tab.icon}
            </span>
            <span className="text-sm">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* ── Tab content ─────────────────────────────────────────────── */}
      {activeTab === 0 && (
        <div className="space-y-6">
          <NPVWaterfallChart />
          <PaybackTimelineChart />
        </div>
      )}

      {activeTab === 1 && <EfficientFrontierChart />}

      {activeTab === 2 && <CO2ValorizationPanel />}

      {activeTab === 3 && <SupernetworkFlowDiagram />}
    </div>
  );
}
