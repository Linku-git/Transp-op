import { useTranslation } from 'react-i18next';
import { Skeleton } from '@/components/ui/Skeleton';

interface SiteSummaryData {
  employee_count: number;
  vehicle_count: number;
  pmr_count: number;
}

interface SiteSummaryCardsProps {
  summary: SiteSummaryData;
  isLoading?: boolean;
}

interface StatCardProps {
  value: number;
  label: string;
  icon: string;
  iconBg: string;
  iconColor: string;
}

function StatCard({ value, label, icon, iconBg, iconColor }: StatCardProps) {
  return (
    <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm border border-outline-variant/10 flex items-center gap-4 hover:bg-surface-bright transition-colors">
      <div className={`w-12 h-12 rounded-full ${iconBg} flex items-center justify-center shrink-0`}>
        <span className={`material-symbols-outlined text-xl ${iconColor}`}>{icon}</span>
      </div>
      <div className="flex flex-col">
        <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest font-sans">
          {label}
        </span>
        <span className="text-2xl font-black text-on-surface tabular-nums font-sans mt-0.5">
          {value}
        </span>
      </div>
    </div>
  );
}

function StatCardSkeleton() {
  return (
    <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm border border-outline-variant/10">
      <div className="flex items-center gap-4">
        <Skeleton variant="circular" className="w-12 h-12" />
        <div className="flex flex-col gap-1">
          <Skeleton variant="text" className="w-20 h-3" />
          <Skeleton variant="text" className="w-16 h-8" />
        </div>
      </div>
    </div>
  );
}

export function SiteSummaryCards({ summary, isLoading = false }: SiteSummaryCardsProps) {
  const { t } = useTranslation();

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCardSkeleton />
        <StatCardSkeleton />
        <StatCardSkeleton />
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <StatCard
        value={summary.employee_count}
        label={t('sites.detail.employee_count', 'Employes')}
        icon="groups"
        iconBg="bg-primary/10"
        iconColor="text-primary"
      />
      <StatCard
        value={summary.vehicle_count}
        label={t('sites.detail.vehicle_count', 'Vehicules')}
        icon="directions_bus"
        iconBg="bg-tertiary/10"
        iconColor="text-tertiary"
      />
      <StatCard
        value={summary.pmr_count}
        label={t('sites.detail.pmr_count', 'PMR')}
        icon="accessible"
        iconBg="bg-secondary/10"
        iconColor="text-secondary"
      />
    </div>
  );
}
