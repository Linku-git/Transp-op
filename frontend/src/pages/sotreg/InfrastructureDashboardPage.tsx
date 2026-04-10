import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { StopGeneratorPanel } from '@/components/sotreg/StopGeneratorPanel';
import { StopCapacityTable } from '@/components/sotreg/StopCapacityTable';
import { DepotLayoutViewer } from '@/components/sotreg/DepotLayoutViewer';
import { IRVECostBreakdown } from '@/components/sotreg/IRVECostBreakdown';

/* ------------------------------------------------------------------ */
/*  Tab definitions                                                    */
/* ------------------------------------------------------------------ */

interface TabDef {
  label: string;
  icon: string;
}

const TABS: TabDef[] = [
  { label: 'Arrets', icon: 'location_on' },
  { label: 'Depot', icon: 'warehouse' },
  { label: 'Couts IRVE', icon: 'payments' },
];

/* ------------------------------------------------------------------ */
/*  Main page component                                                */
/* ------------------------------------------------------------------ */

export function InfrastructureDashboardPage() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<number>(0);

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* -- Page header ------------------------------------------------ */}
      <div>
        <h1 className="font-sans text-xl font-bold text-on-surface">
          {t(
            'sotreg.infrastructure.title',
            'Infrastructure & Arrets',
          )}
        </h1>
        <p className="font-sans text-sm text-on-surface-variant mt-1">
          {t(
            'sotreg.infrastructure.subtitle',
            'Module M3 — Infrastructure de Transport',
          )}
        </p>
      </div>

      {/* -- Tab bar ---------------------------------------------------- */}
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

      {/* -- Tab content ------------------------------------------------ */}
      {activeTab === 0 && (
        <div className="space-y-6">
          <StopGeneratorPanel />
          <StopCapacityTable />
        </div>
      )}

      {activeTab === 1 && <DepotLayoutViewer />}

      {activeTab === 2 && <IRVECostBreakdown />}
    </div>
  );
}
