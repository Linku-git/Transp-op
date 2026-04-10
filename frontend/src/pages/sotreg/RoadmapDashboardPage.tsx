import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { TransitionPlanWizard } from '@/components/sotreg/TransitionPlanWizard';
import { GanttChart } from '@/components/sotreg/GanttChart';
import { BudgetAllocationChart } from '@/components/sotreg/BudgetAllocationChart';
import { MilestoneTracker } from '@/components/sotreg/MilestoneTracker';
import type { TransitionPlanResponse } from '@/types/sotreg';

/* ------------------------------------------------------------------ */
/*  Tab definitions                                                    */
/* ------------------------------------------------------------------ */

interface TabDef {
  label: string;
  icon: string;
}

const TABS: TabDef[] = [
  { label: 'Planification', icon: 'timeline' },
  { label: 'Budget', icon: 'account_balance_wallet' },
  { label: 'Jalons', icon: 'flag' },
];

/* ------------------------------------------------------------------ */
/*  Main page component                                                */
/* ------------------------------------------------------------------ */

export function RoadmapDashboardPage() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<number>(0);
  const [plan, setPlan] = useState<TransitionPlanResponse | null>(null);

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* -- Page header -------------------------------------------------- */}
      <div>
        <h1 className="font-sans text-xl font-bold text-on-surface">
          {t('sotreg.roadmap.title', 'Feuille de Route')}
        </h1>
        <p className="font-sans text-sm text-on-surface-variant mt-1">
          {t(
            'sotreg.roadmap.subtitle',
            'Module M6 \u2014 Transition Electrique',
          )}
        </p>
      </div>

      {/* -- Tab bar ------------------------------------------------------ */}
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

      {/* -- Tab content -------------------------------------------------- */}
      {activeTab === 0 && (
        <div className="space-y-6">
          <TransitionPlanWizard onPlanGenerated={setPlan} />
          {plan && plan.phases.length > 0 && (
            <GanttChart phases={plan.phases} />
          )}
        </div>
      )}

      {activeTab === 1 && (
        <div className="space-y-6">
          {plan && plan.phases.length > 0 ? (
            <BudgetAllocationChart phases={plan.phases} />
          ) : (
            <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
              <div className="flex flex-col items-center justify-center py-12 text-on-surface-variant">
                <span className="material-symbols-outlined text-4xl mb-2 opacity-40">
                  account_balance_wallet
                </span>
                <p className="text-sm">
                  {t(
                    'sotreg.roadmap.budgetEmpty',
                    'Generez un plan de transition dans l\'onglet Planification pour visualiser le budget.',
                  )}
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 2 && (
        <div className="space-y-6">
          {plan && plan.milestones.length > 0 ? (
            <MilestoneTracker milestones={plan.milestones} />
          ) : (
            <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
              <div className="flex flex-col items-center justify-center py-12 text-on-surface-variant">
                <span className="material-symbols-outlined text-4xl mb-2 opacity-40">
                  flag
                </span>
                <p className="text-sm">
                  {t(
                    'sotreg.roadmap.milestonesEmpty',
                    'Generez un plan de transition dans l\'onglet Planification pour afficher les jalons.',
                  )}
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
