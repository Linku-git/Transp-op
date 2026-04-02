import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Tabs } from '@/components/ui/Tabs';
import { TCOCalculatorPage } from './TCOCalculatorPage';
import { ROICalculatorTab } from './ROICalculatorTab';
import { InvestmentComparatorTab } from './InvestmentComparatorTab';

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

        {activeTab === TAB_KEYS.ROI && <ROICalculatorTab />}

        {activeTab === TAB_KEYS.COMPARATOR && <InvestmentComparatorTab />}
      </div>
    </div>
  );
}
