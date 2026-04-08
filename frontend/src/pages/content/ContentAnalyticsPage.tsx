import { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  getContentAnalytics,
  type AnalyticsResponse,
  type ContentRankingItem,
} from '@/api/analytics';
import { CONTENT_TYPE_LABELS, CONTENT_TYPE_ICONS, type ContentType } from '@/types/content';

const TYPE_COLORS: Record<string, string> = {
  news: '#0058be',
  training: '#7c3aed',
  safety: '#ea580c',
  survey: '#0d9488',
};

export function ContentAnalyticsPage() {
  const [data, setData] = useState<AnalyticsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setIsLoading(true);
    getContentAnalytics()
      .then(setData)
      .catch(() => setError('Impossible de charger les analytics'))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16 text-on-surface-variant text-sm">
        Chargement des analytics...
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg bg-error-container/30 px-4 py-3 text-sm text-error">
        {error}
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <nav className="flex items-center gap-2 text-sm text-on-surface-variant mb-2">
            <Link to="/content" className="hover:text-primary transition-colors">
              Contenu
            </Link>
            <span className="material-symbols-outlined text-[14px]">chevron_right</span>
            <span className="text-on-surface font-medium">Analytics</span>
          </nav>
          <h1 className="font-display text-2xl font-bold text-on-surface">
            Engagement Analytics
          </h1>
        </div>
      </div>

      {/* Overview KPIs */}
      <EngagementOverview overview={data.overview} />

      {/* Training hours recovered */}
      <TrainingHoursCard hours={data.overview.training_hours_recovered} />

      {/* Charts row */}
      <div className="grid grid-cols-2 gap-4">
        <EngagementByTypeChart byType={data.by_type} />
        <EngagementRatesCard overview={data.overview} />
      </div>

      {/* Content ranking */}
      <ContentRankingTable items={data.content_ranking} />
    </div>
  );
}

function EngagementOverview({
  overview,
}: {
  overview: AnalyticsResponse['overview'];
}) {
  const kpis = [
    {
      label: 'Vues totales',
      value: overview.total_views.toLocaleString('fr-FR'),
      icon: 'visibility',
    },
    {
      label: 'Compléments',
      value: overview.total_completions.toLocaleString('fr-FR'),
      icon: 'check_circle',
    },
    {
      label: 'Score moyen',
      value: overview.avg_quiz_score != null ? `${overview.avg_quiz_score}%` : '—',
      icon: 'school',
    },
    {
      label: 'Temps moyen',
      value:
        overview.avg_time_spent_seconds != null
          ? `${Math.round(overview.avg_time_spent_seconds / 60)} min`
          : '—',
      icon: 'timer',
    },
  ];

  return (
    <div className="grid grid-cols-4 gap-4">
      {kpis.map((kpi) => (
        <div
          key={kpi.label}
          className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 px-5 py-4 flex items-center gap-4"
        >
          <span className="material-symbols-outlined text-2xl text-primary/60">
            {kpi.icon}
          </span>
          <div>
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
              {kpi.label}
            </p>
            <p className="text-xl font-bold text-on-surface">{kpi.value}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

function TrainingHoursCard({ hours }: { hours: number }) {
  return (
    <div className="bg-gradient-to-br from-primary to-primary-container rounded-xl p-6 text-on-primary flex items-center gap-6">
      <span className="material-symbols-outlined text-4xl opacity-80">
        hourglass_top
      </span>
      <div>
        <p className="text-[10px] font-bold uppercase tracking-widest opacity-70">
          Heures de formation récupérées
        </p>
        <p className="text-3xl font-bold">{hours}h</p>
        <p className="text-sm opacity-70 mt-1">
          Temps total de formation valorisé pendant les trajets
        </p>
      </div>
    </div>
  );
}

function EngagementByTypeChart({
  byType,
}: {
  byType: Record<string, { deliveries: number; views: number; completions: number }>;
}) {
  const types = Object.entries(byType);
  const maxViews = Math.max(...types.map(([, s]) => s.views), 1);

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
      <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
        Engagement par type
      </h3>
      <div className="space-y-3">
        {types.map(([type, stats]) => (
          <div key={type} className="flex items-center gap-3">
            <span className="material-symbols-outlined text-[16px] text-on-surface-variant">
              {CONTENT_TYPE_ICONS[type as ContentType] ?? 'article'}
            </span>
            <span className="w-20 text-xs font-medium text-on-surface">
              {CONTENT_TYPE_LABELS[type as ContentType] ?? type}
            </span>
            <div className="flex-1 h-6 bg-surface-container-high/50 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all"
                style={{
                  width: `${(stats.views / maxViews) * 100}%`,
                  backgroundColor: TYPE_COLORS[type] ?? '#6b7280',
                }}
              />
            </div>
            <span className="text-xs font-medium text-on-surface-variant w-12 text-right">
              {stats.views}
            </span>
          </div>
        ))}
      </div>
      {types.length === 0 && (
        <p className="text-sm text-on-surface-variant text-center py-4">
          Aucune donnée disponible
        </p>
      )}
    </div>
  );
}

function EngagementRatesCard({
  overview,
}: {
  overview: AnalyticsResponse['overview'];
}) {
  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
      <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
        Taux d&apos;engagement
      </h3>
      <div className="space-y-4">
        <RateBar label="Taux de vue" value={overview.view_rate} color="#0058be" />
        <RateBar
          label="Taux de complétion"
          value={overview.completion_rate}
          color="#16a34a"
        />
      </div>
      <div className="mt-4 pt-4 border-t border-outline-variant/10 grid grid-cols-2 gap-4 text-center">
        <div>
          <p className="text-2xl font-bold text-on-surface">
            {overview.total_deliveries.toLocaleString('fr-FR')}
          </p>
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
            Diffusés
          </p>
        </div>
        <div>
          <p className="text-2xl font-bold text-on-surface">
            {overview.total_completions.toLocaleString('fr-FR')}
          </p>
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
            Complétés
          </p>
        </div>
      </div>
    </div>
  );
}

function RateBar({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  return (
    <div>
      <div className="flex justify-between mb-1">
        <span className="text-xs text-on-surface-variant">{label}</span>
        <span className="text-xs font-bold text-on-surface">{value}%</span>
      </div>
      <div className="h-2.5 bg-surface-container-high/50 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${Math.min(value, 100)}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}

function ContentRankingTable({ items }: { items: ContentRankingItem[] }) {
  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
      <div className="px-5 py-4">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Classement par engagement
        </h3>
      </div>
      {items.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 gap-2">
          <span className="material-symbols-outlined text-3xl text-on-surface-variant/40">
            analytics
          </span>
          <p className="text-sm text-on-surface-variant">
            Aucune donnée d&apos;engagement
          </p>
        </div>
      ) : (
        <table className="w-full">
          <thead>
            <tr className="bg-surface-container-low/50">
              <th className="text-left text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-3">
                Contenu
              </th>
              <th className="text-left text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-3">
                Type
              </th>
              <th className="text-right text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-3">
                Vues
              </th>
              <th className="text-right text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-3">
                Complétés
              </th>
              <th className="text-right text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-3">
                Score
              </th>
              <th className="text-right text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-3">
                Temps moy.
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/10">
            {items.map((item, idx) => (
              <tr
                key={item.content_id}
                className="hover:bg-surface-bright transition-colors"
              >
                <td className="px-5 py-3 text-sm text-on-surface">
                  <span className="text-on-surface-variant text-xs mr-2">
                    #{idx + 1}
                  </span>
                  {item.title}
                </td>
                <td className="px-5 py-3">
                  <span className="inline-flex items-center gap-1.5 text-xs text-on-surface-variant">
                    <span className="material-symbols-outlined text-[14px]">
                      {CONTENT_TYPE_ICONS[item.content_type as ContentType] ?? 'article'}
                    </span>
                    {CONTENT_TYPE_LABELS[item.content_type as ContentType] ?? item.content_type}
                  </span>
                </td>
                <td className="px-5 py-3 text-sm text-on-surface text-right tabular-nums">
                  {item.views}
                </td>
                <td className="px-5 py-3 text-sm text-on-surface text-right tabular-nums">
                  {item.completions}
                </td>
                <td className="px-5 py-3 text-sm text-on-surface text-right tabular-nums">
                  {item.avg_quiz_score != null ? `${item.avg_quiz_score}%` : '—'}
                </td>
                <td className="px-5 py-3 text-sm text-on-surface-variant text-right tabular-nums">
                  {item.avg_time_seconds != null
                    ? `${Math.round(item.avg_time_seconds / 60)}m`
                    : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
