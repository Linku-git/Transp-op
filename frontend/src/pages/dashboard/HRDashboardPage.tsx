import { useEffect, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { getHRKPIs } from '@/api/hr';
import type { HRKPIsResponse, AbsenteeismCorrelation } from '@/types/hr';
import { Card } from '@/components/ui/Card';
import { HeatmapTable } from '@/components/charts/HeatmapTable';
import { ScatterPlot } from '@/components/charts/ScatterPlot';
import type { ScatterPoint } from '@/components/charts/ScatterPlot';
import { RetentionImpactCard } from '@/components/dashboard/RetentionImpactCard';
import { ShadowZonesList } from '@/components/dashboard/ShadowZonesList';
import { MobilityAlerts } from '@/components/dashboard/MobilityAlerts';

function buildAbsenteeismScatterData(corr: AbsenteeismCorrelation): ScatterPoint[] {
  return [
    {
      x: corr.with_transport.avg_absence_days,
      y: corr.with_transport.absence_rate_pct,
      label: 'Avec transport',
    },
    {
      x: corr.without_transport.avg_absence_days,
      y: corr.without_transport.absence_rate_pct,
      label: 'Sans transport',
    },
    {
      x: corr.maybe_transport.avg_absence_days,
      y: corr.maybe_transport.absence_rate_pct,
      label: 'Peut-etre',
    },
  ];
}

function getCoverageColor(pct: number): string {
  if (pct >= 75) return 'text-green-600';
  if (pct >= 50) return 'text-amber-600';
  return 'text-error';
}

interface ScoreTooltipPayload {
  value: number;
  name: string;
}

interface ScoreTooltipProps {
  active?: boolean;
  label?: string;
  payload?: ScoreTooltipPayload[];
}

function ScoreTooltip({ active, label, payload }: ScoreTooltipProps) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-surface-container-lowest text-on-surface rounded-lg px-3 py-2 shadow-sm border border-outline-variant/10">
      <p className="font-sans text-xs text-on-surface-variant">{label}</p>
      {payload.map((entry) => (
        <p key={entry.name} className="font-sans text-sm font-medium">
          {entry.name}: {entry.value}
        </p>
      ))}
    </div>
  );
}

export function HRDashboardPage() {
  const { t } = useTranslation();
  const [data, setData] = useState<HRKPIsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getHRKPIs();
      setData(result);
    } catch {
      setError(t('common.error'));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    void fetchData();
  }, [fetchData]);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center" data-testid="hr-loading">
        <div className="flex items-center gap-3">
          <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <span className="font-sans text-sm text-on-surface-variant">
            {t('common.loading')}
          </span>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-4">
        <span className="material-symbols-outlined text-4xl text-error">error</span>
        <p className="font-sans text-sm text-on-surface-variant">
          {error ?? t('common.error')}
        </p>
        <button
          type="button"
          onClick={() => void fetchData()}
          className="bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-lg shadow-lg shadow-primary/20 px-4 py-2 font-sans text-sm font-medium"
        >
          {t('hr.retry', 'Reessayer')}
        </button>
      </div>
    );
  }

  const scoreEvolution = data.mobility_score_evolution.map((pt) => ({
    date: new Date(pt.date).toLocaleDateString('fr-FR', {
      month: 'short',
      day: 'numeric',
    }),
    score: pt.score,
    co2_kg: pt.co2_kg,
    occupancy_pct: pt.occupancy_pct,
  }));

  const absenteeismData = buildAbsenteeismScatterData(data.absenteeism_correlation);

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* Page header */}
      <div>
        <h1 className="font-sans text-xl font-bold text-on-surface">
          {t('hr.title', 'Tableau de bord RH')}
        </h1>
        <p className="font-sans text-sm text-on-surface-variant mt-1">
          {t('hr.subtitle', 'Couverture mobilite, absenteisme et retention.')}
        </p>
      </div>

      {/* Alerts */}
      <MobilityAlerts
        coverage={data.mobility_coverage}
        shadowZones={data.shadow_zones}
      />

      {/* Row 1: Coverage summary + by site heatmap */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <div className="flex flex-col items-center justify-center h-full">
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">
              {t('hr.coverage_label', 'Couverture mobilite')}
            </p>
            <p
              className={`font-sans text-5xl font-bold ${getCoverageColor(data.mobility_coverage.coverage_pct)}`}
              data-testid="coverage-pct"
            >
              {data.mobility_coverage.coverage_pct.toFixed(1)}%
            </p>
            <p className="font-sans text-sm text-on-surface-variant mt-2">
              {data.mobility_coverage.covered_employees} / {data.mobility_coverage.total_employees}{' '}
              {t('hr.employees_covered', 'employes couverts')}
            </p>
          </div>
        </Card>
        <div className="lg:col-span-2">
          <HeatmapTable
            data={data.mobility_coverage.by_site}
            title={t('hr.coverage_by_site', 'Couverture par site')}
          />
        </div>
      </div>

      {/* Row 2: Heatmaps by shift and department */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <HeatmapTable
          data={data.mobility_coverage.by_shift}
          title={t('hr.coverage_by_shift', 'Couverture par equipe')}
        />
        <HeatmapTable
          data={data.mobility_coverage.by_department}
          title={t('hr.coverage_by_department', 'Couverture par departement')}
        />
      </div>

      {/* Row 3: Score evolution line chart */}
      <Card title={t('hr.score_evolution', 'Evolution du score mobilite')}>
        {scoreEvolution.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={scoreEvolution} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#c2c6d6" opacity={0.3} />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#424754' }} />
              <YAxis
                domain={[0, 100]}
                tick={{ fontSize: 11, fill: '#424754' }}
                label={{
                  value: 'Score',
                  angle: -90,
                  position: 'insideLeft',
                  style: { fontSize: 11, fill: '#424754' },
                }}
              />
              <Tooltip content={<ScoreTooltip />} />
              <Line
                type="monotone"
                dataKey="score"
                name="Score"
                stroke="#0058be"
                strokeWidth={2}
                dot={{ r: 3, fill: '#0058be' }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="font-sans text-sm text-on-surface-variant">
            {t('common.no_data')}
          </p>
        )}
      </Card>

      {/* Row 4: Absenteeism correlation + Retention impact */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title={t('hr.absenteeism_title', 'Correlation absenteisme')}>
          <ScatterPlot
            data={absenteeismData}
            xLabel={t('hr.avg_absence_days', 'Jours d\'absence moy.')}
            yLabel={t('hr.absence_rate', 'Taux d\'absence (%)')}
            height={280}
          />
          <div className="mt-3 px-2 py-2 bg-surface-container-low rounded-lg">
            <p className="font-sans text-xs text-on-surface-variant">
              <span className="font-semibold">{t('hr.delta', 'Delta')}: </span>
              {data.absenteeism_correlation.correlation.delta_pct.toFixed(2)}% &mdash;{' '}
              {data.absenteeism_correlation.correlation.interpretation}
            </p>
          </div>
        </Card>
        <RetentionImpactCard data={data.retention_impact} />
      </div>

      {/* Row 5: Shadow zones */}
      <ShadowZonesList data={data.shadow_zones} />
    </div>
  );
}
