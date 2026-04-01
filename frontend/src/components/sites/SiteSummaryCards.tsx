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

function StatCard({ value, label }: { value: number; label: string }) {
  return (
    <div className="bg-surface-container-lowest rounded-lg p-5">
      <span className="font-display text-3xl font-bold text-secondary tabular-nums block">
        {value}
      </span>
      <span className="text-sm text-on-surface-variant font-sans mt-1 block">
        {label}
      </span>
    </div>
  );
}

function StatCardSkeleton() {
  return (
    <div className="bg-surface-container-lowest rounded-lg p-5">
      <Skeleton variant="text" className="w-16 h-9 mb-1" />
      <Skeleton variant="text" className="w-24 h-4" />
    </div>
  );
}

export function SiteSummaryCards({ summary, isLoading = false }: SiteSummaryCardsProps) {
  const { t } = useTranslation();

  if (isLoading) {
    return (
      <div className="grid grid-cols-3 gap-4">
        <StatCardSkeleton />
        <StatCardSkeleton />
        <StatCardSkeleton />
      </div>
    );
  }

  return (
    <div className="grid grid-cols-3 gap-4">
      <StatCard
        value={summary.employee_count}
        label={t('sites.detail.employee_count', 'Employes')}
      />
      <StatCard
        value={summary.vehicle_count}
        label={t('sites.detail.vehicle_count', 'Vehicules')}
      />
      <StatCard
        value={summary.pmr_count}
        label={t('sites.detail.pmr_count', 'PMR')}
      />
    </div>
  );
}
