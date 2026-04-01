import { useTranslation } from 'react-i18next';

interface StatCardProps {
  title: string;
}

function StatCard({ title }: StatCardProps) {
  return (
    <div className="bg-surface-container-lowest rounded-lg p-6">
      <h3 className="font-sans text-sm font-medium text-on-surface-variant mb-2">
        {title}
      </h3>
      <span className="font-display text-4xl font-bold text-secondary">
        &mdash;
      </span>
    </div>
  );
}

export function DashboardPage() {
  const { t } = useTranslation();

  const cards = [
    { key: 'sites', title: t('nav.sites') },
    { key: 'employees', title: t('nav.employees') },
    { key: 'vehicles', title: t('nav.vehicles') },
    { key: 'optimizations', title: t('nav.optimization') },
  ];

  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-on-surface mb-8">
        {t('nav.dashboard')}
      </h1>

      <div className="grid grid-cols-2 gap-6">
        {cards.map((card) => (
          <StatCard key={card.key} title={card.title} />
        ))}
      </div>
    </div>
  );
}
