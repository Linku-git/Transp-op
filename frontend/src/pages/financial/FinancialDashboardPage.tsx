import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Tabs } from '@/components/ui/Tabs';
import { TCOCalculatorPage } from './TCOCalculatorPage';

const TAB_KEYS = {
  TCO: 'tco',
  ROI: 'roi',
  COMPARATOR: 'comparator',
} as const;

export function FinancialDashboardPage() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<string>(TAB_KEYS.TCO);

  const tabs = [
    {
      key: TAB_KEYS.TCO,
      label: t('financial.tab_tco', 'TCO'),
    },
    {
      key: TAB_KEYS.ROI,
      label: t('financial.tab_roi', 'ROI'),
    },
    {
      key: TAB_KEYS.COMPARATOR,
      label: t('financial.tab_comparator', 'Comparateur'),
    },
  ];

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="px-6 pt-6 pb-0">
        <h1 className="text-xl font-bold text-on-surface font-sans mb-1">
          {t('financial.title', 'Finance')}
        </h1>
        <p className="text-sm text-on-surface-variant mb-4">
          {t(
            'financial.subtitle',
            'Analyse financiere et cout total de possession.',
          )}
        </p>

        <div className="border-b border-outline-variant/10">
          <Tabs tabs={tabs} activeKey={activeTab} onChange={setActiveTab} />
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === TAB_KEYS.TCO && <TCOCalculatorPage />}

        {activeTab === TAB_KEYS.ROI && (
          <div className="flex-1 flex flex-col items-center justify-center p-12 text-center">
            <span className="material-symbols-outlined text-5xl text-on-surface-variant/40 mb-4">
              trending_up
            </span>
            <h2 className="text-lg font-bold text-on-surface mb-2">
              {t('financial.roi_title', 'Calculateur ROI')}
            </h2>
            <p className="text-sm text-on-surface-variant">
              {t('financial.coming_soon', 'Bientot disponible')}
            </p>
          </div>
        )}

        {activeTab === TAB_KEYS.COMPARATOR && (
          <div className="flex-1 flex flex-col items-center justify-center p-12 text-center">
            <span className="material-symbols-outlined text-5xl text-on-surface-variant/40 mb-4">
              compare_arrows
            </span>
            <h2 className="text-lg font-bold text-on-surface mb-2">
              {t('financial.comparator_title', 'Comparateur de modeles')}
            </h2>
            <p className="text-sm text-on-surface-variant">
              {t('financial.coming_soon', 'Bientot disponible')}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
