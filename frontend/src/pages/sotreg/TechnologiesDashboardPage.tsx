import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { RangeCorrectionPanel } from '@/components/sotreg/RangeCorrectionPanel';
import { TCO15YearChart } from '@/components/sotreg/TCO15YearChart';
import { BreakevenChart } from '@/components/sotreg/BreakevenChart';
import { IRVESizingWizard } from '@/components/sotreg/IRVESizingWizard';
import { ChargingScheduleTimeline } from '@/components/sotreg/ChargingScheduleTimeline';

/* ------------------------------------------------------------------ */
/*  Tab definitions                                                    */
/* ------------------------------------------------------------------ */

interface TabDef {
  label: string;
  icon: string;
}

const TABS: TabDef[] = [
  { label: 'Autonomie', icon: 'battery_charging_full' },
  { label: 'TCO 15 ans', icon: 'trending_up' },
  { label: 'Seuil de Rentabilite', icon: 'balance' },
  { label: 'IRVE', icon: 'ev_station' },
];

/* ------------------------------------------------------------------ */
/*  Main page component                                                */
/* ------------------------------------------------------------------ */

export function TechnologiesDashboardPage() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState(0);

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* ── Page header ─────────────────────────────────────────────── */}
      <div>
        <h1 className="font-sans text-xl font-bold text-on-surface">
          {t('sotreg.technologies.title', 'Technologies & Electrification')}
        </h1>
        <p className="font-sans text-sm text-on-surface-variant mt-1">
          {t(
            'sotreg.technologies.subtitle',
            'Module M2 — Analyse Technologique',
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
      {activeTab === 0 && <RangeCorrectionPanel />}

      {activeTab === 1 && <TCO15YearChart />}

      {activeTab === 2 && <BreakevenChart />}

      {activeTab === 3 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <IRVESizingWizard />
          <ChargingScheduleTimeline />
        </div>
      )}
    </div>
  );
}
