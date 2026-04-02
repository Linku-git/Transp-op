import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

import { listSites } from '@/api/sites';
import { getEmployeeSummary } from '@/api/employees';
import { getOptimizationHistory, getLatestOptimization } from '@/api/optimization';
import { getModalStats } from '@/api/modal';
import type { Site } from '@/types/site';
import type { EmployeeSummary } from '@/types/employee';
import type { OptimizationHistoryItem, Optimization, OptimizationMetrics } from '@/types/optimization';
import type { ModalStats } from '@/types/modal';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface KpiCardProps {
  icon: string;
  iconBg: string;
  label: string;
  value: string;
  change: string | null;
  changePositive: boolean;
  isLoading: boolean;
}

interface ModalSlice {
  mode: string;
  percentage: number;
  color: string;
}

/* ------------------------------------------------------------------ */
/*  Constants                                                          */
/* ------------------------------------------------------------------ */

const MODE_COLORS: Record<string, string> = {
  'Voiture personnelle': '#0058be',
  'Transport en commun': '#495e8a',
  Covoiturage: '#924700',
  'Deux-roues': '#006d32',
  Marche: '#7c5800',
  Taxi: '#6e4c9e',
  default: '#727785',
};

const STATUS_CHIP_STYLES: Record<string, string> = {
  completed: 'bg-green-50 text-green-700',
  running: 'bg-blue-50 text-blue-700',
  pending: 'bg-surface-container-high text-on-surface-variant',
  failed: 'bg-error-container text-error',
};

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`;
  return n.toLocaleString();
}

function formatDistance(km: number): string {
  if (km >= 1_000) return `${(km / 1_000).toFixed(1)}k km`;
  return `${km.toFixed(0)} km`;
}

function formatCurrency(v: number): string {
  return `${v.toLocaleString(undefined, { maximumFractionDigits: 0 })} MAD`;
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

/* ------------------------------------------------------------------ */
/*  Sub-components                                                     */
/* ------------------------------------------------------------------ */

function KpiCardSkeleton() {
  return (
    <div className="bg-surface-container-lowest p-6 rounded-xl shadow-sm animate-pulse">
      <div className="flex items-start justify-between">
        <div className="w-10 h-10 rounded-full bg-surface-container-high" />
        <div className="w-12 h-5 rounded-full bg-surface-container-high" />
      </div>
      <div className="mt-4 space-y-2">
        <div className="h-3 w-24 rounded bg-surface-container-high" />
        <div className="h-8 w-16 rounded bg-surface-container-high" />
      </div>
    </div>
  );
}

function KpiCard({ icon, iconBg, label, value, change, changePositive, isLoading }: KpiCardProps) {
  if (isLoading) return <KpiCardSkeleton />;

  return (
    <div className="bg-surface-container-lowest p-6 rounded-xl shadow-sm border border-outline-variant/10">
      <div className="flex items-start justify-between">
        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${iconBg}`}>
          <span className="material-symbols-outlined text-xl">{icon}</span>
        </div>
        {change !== null && (
          <span
            className={`inline-flex items-center px-2.5 py-0.5 text-xs font-semibold rounded-full ${
              changePositive
                ? 'bg-green-50 text-green-600'
                : 'bg-red-50 text-red-600'
            }`}
          >
            {changePositive ? '+' : ''}{change}
          </span>
        )}
      </div>
      <div className="mt-4">
        <p className="text-xs font-bold text-on-surface-variant uppercase tracking-widest">
          {label}
        </p>
        <p className="text-3xl font-black text-on-surface mt-1 tabular-nums">
          {value}
        </p>
      </div>
    </div>
  );
}

function PieChartSvg({ slices }: { slices: ModalSlice[] }) {
  const total = slices.reduce((sum, s) => sum + s.percentage, 0);
  if (total === 0) return null;

  let cumulativePercent = 0;
  const radius = 50;
  const cx = 60;
  const cy = 60;

  function getCoordinatesForPercent(percent: number) {
    const angle = percent * 2 * Math.PI - Math.PI / 2;
    return {
      x: cx + radius * Math.cos(angle),
      y: cy + radius * Math.sin(angle),
    };
  }

  return (
    <svg viewBox="0 0 120 120" className="w-full h-full">
      {slices.map((slice) => {
        if (slice.percentage <= 0) return null;
        const normalizedPct = slice.percentage / total;
        const startPercent = cumulativePercent;
        cumulativePercent += normalizedPct;

        const start = getCoordinatesForPercent(startPercent);
        const end = getCoordinatesForPercent(cumulativePercent);
        const largeArc = normalizedPct > 0.5 ? 1 : 0;

        if (normalizedPct >= 0.999) {
          return (
            <circle
              key={slice.mode}
              cx={cx}
              cy={cy}
              r={radius}
              fill={slice.color}
            />
          );
        }

        return (
          <path
            key={slice.mode}
            d={`M ${cx} ${cy} L ${start.x} ${start.y} A ${radius} ${radius} 0 ${largeArc} 1 ${end.x} ${end.y} Z`}
            fill={slice.color}
          />
        );
      })}
      <circle cx={cx} cy={cy} r={30} fill="white" />
    </svg>
  );
}

function ModalDistributionCard({
  stats,
  isLoading,
}: {
  stats: ModalStats | null;
  isLoading: boolean;
}) {
  const slices = useMemo<ModalSlice[]>(() => {
    if (!stats) return [];
    return stats.distribution.map((d) => ({
      mode: d.mode,
      percentage: d.percentage,
      color: MODE_COLORS[d.mode] ?? MODE_COLORS.default,
    }));
  }, [stats]);

  if (isLoading) {
    return (
      <div className="bg-surface-container-lowest rounded-2xl p-6 shadow-sm border border-outline-variant/10 animate-pulse">
        <div className="h-4 w-40 rounded bg-surface-container-high mb-4" />
        <div className="flex items-center gap-6">
          <div className="w-28 h-28 rounded-full bg-surface-container-high" />
          <div className="flex-1 space-y-2">
            <div className="h-3 w-full rounded bg-surface-container-high" />
            <div className="h-3 w-3/4 rounded bg-surface-container-high" />
            <div className="h-3 w-1/2 rounded bg-surface-container-high" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface-container-lowest rounded-2xl p-6 shadow-sm border border-outline-variant/10">
      <h3 className="text-sm font-semibold text-on-surface mb-4">
        Modal Distribution
      </h3>
      {slices.length === 0 ? (
        <p className="text-xs text-on-surface-variant text-center py-4">No data</p>
      ) : (
        <div className="flex items-center gap-5">
          <div className="w-28 h-28 flex-shrink-0">
            <PieChartSvg slices={slices} />
          </div>
          <div className="flex-1 space-y-2.5 min-w-0">
            {slices.slice(0, 5).map((s) => (
              <div key={s.mode} className="flex items-center gap-2">
                <span
                  className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                  style={{ backgroundColor: s.color }}
                />
                <span className="text-xs text-on-surface truncate flex-1">
                  {s.mode}
                </span>
                <span className="text-xs font-semibold text-on-surface tabular-nums">
                  {s.percentage.toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function OccupancyPerSiteCard({
  sites,
  metrics,
  isLoading,
}: {
  sites: Site[];
  metrics: OptimizationMetrics | null;
  isLoading: boolean;
}) {
  const siteOccupancyData = useMemo(() => {
    if (!sites.length) return [];
    const avgOcc = metrics?.avg_occupancy_rate ?? 0;
    return sites.slice(0, 5).map((site, i) => {
      const variance = ((i % 3) - 1) * 5;
      const occupancy = Math.min(100, Math.max(0, avgOcc + variance));
      return {
        name: site.name,
        occupancy: Math.round(occupancy),
      };
    });
  }, [sites, metrics]);

  if (isLoading) {
    return (
      <div className="bg-surface-container-lowest rounded-2xl p-6 shadow-sm border border-outline-variant/10 animate-pulse">
        <div className="h-4 w-36 rounded bg-surface-container-high mb-4" />
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i}>
              <div className="h-3 w-20 rounded bg-surface-container-high mb-1.5" />
              <div className="h-2 w-full rounded-full bg-surface-container-high" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface-container-lowest rounded-2xl p-6 shadow-sm border border-outline-variant/10">
      <h3 className="text-sm font-semibold text-on-surface mb-4">
        Occupancy per Site
      </h3>
      {siteOccupancyData.length === 0 ? (
        <p className="text-xs text-on-surface-variant text-center py-4">No sites</p>
      ) : (
        <div className="space-y-3">
          {siteOccupancyData.map((entry) => (
            <div key={entry.name}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-on-surface-variant truncate max-w-[70%]">
                  {entry.name}
                </span>
                <span className="text-xs font-semibold text-on-surface tabular-nums">
                  {entry.occupancy}%
                </span>
              </div>
              <div className="h-2 rounded-full bg-surface-container-high overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${entry.occupancy}%`,
                    backgroundColor:
                      entry.occupancy >= 80
                        ? '#0058be'
                        : entry.occupancy >= 50
                          ? '#495e8a'
                          : '#924700',
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function OrchestrationStreamTable({
  history,
  isLoading,
}: {
  history: OptimizationHistoryItem[];
  isLoading: boolean;
}) {
  const navigate = useNavigate();

  if (isLoading) {
    return (
      <div className="bg-surface-container-lowest rounded-2xl p-6 shadow-sm border border-outline-variant/10 animate-pulse">
        <div className="h-4 w-48 rounded bg-surface-container-high mb-5" />
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex items-center gap-4">
              <div className="h-3 w-24 rounded bg-surface-container-high" />
              <div className="h-3 w-20 rounded bg-surface-container-high" />
              <div className="h-3 w-16 rounded bg-surface-container-high flex-1" />
              <div className="h-5 w-20 rounded-full bg-surface-container-high" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface-container-lowest rounded-2xl p-6 shadow-sm border border-outline-variant/10">
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-sm font-semibold text-on-surface">
          Live Orchestration Stream
        </h3>
        <button
          onClick={() => navigate('/optimization/history')}
          className="text-xs font-medium text-primary hover:text-primary-container transition-colors"
        >
          View all
        </button>
      </div>
      {history.length === 0 ? (
        <div className="text-center py-8">
          <span className="material-symbols-outlined text-3xl text-on-surface-variant/40 mb-2 block">
            route
          </span>
          <p className="text-xs text-on-surface-variant">No optimization runs yet</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr>
                <th className="text-left text-xs font-medium text-on-surface-variant pb-3 pr-4">
                  Site
                </th>
                <th className="text-left text-xs font-medium text-on-surface-variant pb-3 pr-4">
                  Condition
                </th>
                <th className="text-left text-xs font-medium text-on-surface-variant pb-3 pr-4">
                  Date
                </th>
                <th className="text-right text-xs font-medium text-on-surface-variant pb-3 pr-4">
                  Vehicles
                </th>
                <th className="text-right text-xs font-medium text-on-surface-variant pb-3">
                  Status
                </th>
              </tr>
            </thead>
            <tbody>
              {history.slice(0, 7).map((item) => {
                const metrics = item.metrics as Partial<OptimizationMetrics>;
                return (
                  <tr
                    key={item.id}
                    className="group cursor-pointer hover:bg-surface-container-low/50 transition-colors"
                    onClick={() => navigate(`/optimization/${item.id}`)}
                  >
                    <td className="py-2.5 pr-4">
                      <span className="text-sm text-on-surface font-medium">
                        {item.site_name ?? '--'}
                      </span>
                    </td>
                    <td className="py-2.5 pr-4">
                      <span className="text-xs text-on-surface-variant capitalize">
                        {item.condition_type}
                      </span>
                    </td>
                    <td className="py-2.5 pr-4">
                      <span className="text-xs text-on-surface-variant tabular-nums">
                        {timeAgo(item.created_at)}
                      </span>
                    </td>
                    <td className="py-2.5 pr-4 text-right">
                      <span className="text-sm font-semibold text-on-surface tabular-nums">
                        {metrics.total_vehicles_used ?? '--'}
                      </span>
                    </td>
                    <td className="py-2.5 text-right">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 text-xs font-medium rounded-full capitalize ${
                          STATUS_CHIP_STYLES[item.status] ?? STATUS_CHIP_STYLES.pending
                        }`}
                      >
                        {item.status}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function WeatherCard({ isLoading }: { isLoading: boolean }) {
  if (isLoading) {
    return (
      <div className="rounded-2xl p-6 bg-gradient-to-br from-blue-500 to-blue-700 animate-pulse">
        <div className="h-4 w-20 rounded bg-white/20 mb-3" />
        <div className="h-10 w-16 rounded bg-white/20 mb-2" />
        <div className="h-3 w-28 rounded bg-white/20" />
      </div>
    );
  }

  const today = new Date();
  const dayName = today.toLocaleDateString('en-US', { weekday: 'long' });
  const dateStr = today.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className="rounded-2xl p-6 bg-gradient-to-br from-blue-500 to-blue-700 text-white shadow-sm">
      <div className="flex items-center gap-2 mb-4">
        <span className="material-symbols-outlined text-lg text-white/90">
          wb_sunny
        </span>
        <span className="text-xs font-semibold text-white/80 uppercase tracking-widest">
          Weather
        </span>
      </div>
      <p className="text-4xl font-black tabular-nums">24&#176;C</p>
      <p className="text-sm text-white/80 mt-1">Mostly Clear</p>
      <div className="mt-4 pt-4 border-t border-white/20">
        <p className="text-xs text-white/70">{dayName}</p>
        <p className="text-sm font-semibold text-white/90">{dateStr}</p>
      </div>
      <div className="flex items-center gap-4 mt-4">
        <div className="flex items-center gap-1">
          <span className="material-symbols-outlined text-sm text-white/70">
            water_drop
          </span>
          <span className="text-xs text-white/80">12%</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="material-symbols-outlined text-sm text-white/70">
            air
          </span>
          <span className="text-xs text-white/80">8 km/h</span>
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Main Component                                                     */
/* ------------------------------------------------------------------ */

export function DashboardPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  /* State */
  const [sites, setSites] = useState<Site[]>([]);
  const [employeeSummary, setEmployeeSummary] = useState<EmployeeSummary | null>(null);
  const [optimizationHistory, setOptimizationHistory] = useState<OptimizationHistoryItem[]>([]);
  const [latestOptimization, setLatestOptimization] = useState<Optimization | null>(null);
  const [modalStats, setModalStats] = useState<ModalStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /* Derived metrics from latest optimization */
  const metrics = useMemo<OptimizationMetrics | null>(() => {
    if (!latestOptimization) return null;
    const m = latestOptimization.metrics;
    if ('total_employees' in m) return m as OptimizationMetrics;
    return null;
  }, [latestOptimization]);

  /* Fetch all dashboard data */
  const fetchDashboardData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    const results = await Promise.allSettled([
      listSites({ page: 1, page_size: 20 }),
      getEmployeeSummary(),
      getOptimizationHistory(undefined, 1, 10),
      getLatestOptimization(),
      getModalStats(),
    ]);

    const [sitesResult, empResult, histResult, latestResult, modalResult] = results;

    if (sitesResult.status === 'fulfilled') {
      setSites(sitesResult.value.data);
    }
    if (empResult.status === 'fulfilled') {
      setEmployeeSummary(empResult.value);
    }
    if (histResult.status === 'fulfilled') {
      setOptimizationHistory(histResult.value);
    }
    if (latestResult.status === 'fulfilled') {
      setLatestOptimization(latestResult.value);
    }
    if (modalResult.status === 'fulfilled') {
      setModalStats(modalResult.value);
    }

    const allFailed = results.every((r) => r.status === 'rejected');
    if (allFailed) {
      setError(t('common.error'));
    }

    setIsLoading(false);
  }, [t]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  /* KPI values */
  const totalVehicles = metrics?.total_vehicles_used ?? 0;
  const avgOccupancy = metrics?.avg_occupancy_rate ?? 0;
  const totalDistance = metrics?.total_distance_km ?? 0;
  const fuelCost = metrics?.estimated_fuel_cost_mad ?? 0;
  const co2Saved = metrics?.co2_estimate_kg ?? 0;

  /* Error state */
  if (error && !isLoading && sites.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-4">
        <span className="material-symbols-outlined text-5xl text-on-surface-variant/40">
          error_outline
        </span>
        <p className="text-sm text-on-surface-variant">{error}</p>
        <button
          onClick={fetchDashboardData}
          className="text-sm font-medium text-primary hover:text-primary-container transition-colors"
        >
          {t('common.retry', 'Retry')}
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ---- Page Header ---- */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-extrabold tracking-tight text-on-surface">
          Operations Dashboard
        </h2>
        <button
          onClick={() => navigate('/optimization')}
          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-on-primary bg-primary rounded-md hover:bg-primary-container transition-colors"
        >
          <span className="material-symbols-outlined text-base">bolt</span>
          New Optimization
        </button>
      </div>

      {/* ---- KPI Row (5 cards) ---- */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <KpiCard
          icon="directions_bus"
          iconBg="bg-primary/10 text-primary"
          label="Total Vehicles"
          value={formatNumber(totalVehicles)}
          change={totalVehicles > 0 ? '4%' : null}
          changePositive={true}
          isLoading={isLoading}
        />
        <KpiCard
          icon="groups"
          iconBg="bg-secondary/10 text-secondary"
          label="Avg Occupancy"
          value={`${avgOccupancy.toFixed(0)}%`}
          change={avgOccupancy > 0 ? '2.3%' : null}
          changePositive={true}
          isLoading={isLoading}
        />
        <KpiCard
          icon="route"
          iconBg="bg-tertiary/10 text-tertiary"
          label="Total Distance"
          value={formatDistance(totalDistance)}
          change={totalDistance > 0 ? '-1.2%' : null}
          changePositive={true}
          isLoading={isLoading}
        />
        <KpiCard
          icon="local_gas_station"
          iconBg="bg-error/10 text-error"
          label="Fuel Cost"
          value={fuelCost > 0 ? formatCurrency(fuelCost) : '--'}
          change={fuelCost > 0 ? '-3%' : null}
          changePositive={true}
          isLoading={isLoading}
        />
        <KpiCard
          icon="eco"
          iconBg="bg-green-600/10 text-green-600"
          label="CO2 Saved"
          value={co2Saved > 0 ? `${co2Saved.toFixed(0)} kg` : '--'}
          change={co2Saved > 0 ? '+8%' : null}
          changePositive={true}
          isLoading={isLoading}
        />
      </div>

      {/* ---- Main Interactive Section (map + side cards) ---- */}
      <div className="grid grid-cols-12 gap-4">
        {/* Left: Large Map Container */}
        <div className="col-span-12 lg:col-span-8">
          <div className="bg-surface-container-lowest rounded-2xl shadow-sm border border-outline-variant/10 overflow-hidden relative"
               style={{ minHeight: '420px' }}>
            {/* Map placeholder with gradient background */}
            <div className="absolute inset-0 bg-gradient-to-br from-surface-container-low to-surface-container">
              {/* Grid pattern overlay */}
              <div
                className="absolute inset-0 opacity-[0.03]"
                style={{
                  backgroundImage:
                    'linear-gradient(var(--color-on-surface) 1px, transparent 1px), linear-gradient(90deg, var(--color-on-surface) 1px, transparent 1px)',
                  backgroundSize: '40px 40px',
                }}
              />

              {/* Map center marker */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="flex flex-col items-center gap-2 opacity-30">
                  <span className="material-symbols-outlined text-6xl text-on-surface-variant">
                    map
                  </span>
                  <span className="text-xs text-on-surface-variant font-medium">
                    Map view
                  </span>
                </div>
              </div>
            </div>

            {/* Glassmorphism overlay: Hub label */}
            <div className="absolute bottom-4 left-4 glass-effect bg-white/80 rounded-xl px-5 py-4 shadow-sm">
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined text-primary text-2xl">
                  location_city
                </span>
                <div>
                  <p className="text-sm font-bold text-on-surface">
                    {sites.length > 0 ? sites[0].city : 'Casablanca'} Hub
                  </p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-xs text-on-surface-variant">
                      {sites.length} site{sites.length !== 1 ? 's' : ''} active
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Stats overlay: top-right */}
            <div className="absolute top-4 right-4 glass-effect bg-white/80 rounded-xl px-4 py-3 shadow-sm">
              <div className="flex items-center gap-4">
                <div className="text-center">
                  <p className="text-lg font-black text-on-surface tabular-nums">
                    {employeeSummary?.total_count ?? '--'}
                  </p>
                  <p className="text-[10px] font-medium text-on-surface-variant uppercase tracking-wider">
                    Employees
                  </p>
                </div>
                <div className="w-px h-8 bg-outline-variant" />
                <div className="text-center">
                  <p className="text-lg font-black text-on-surface tabular-nums">
                    {employeeSummary?.pmr_count ?? '--'}
                  </p>
                  <p className="text-[10px] font-medium text-on-surface-variant uppercase tracking-wider">
                    PMR
                  </p>
                </div>
                <div className="w-px h-8 bg-outline-variant" />
                <div className="text-center">
                  <p className="text-lg font-black text-on-surface tabular-nums">
                    {optimizationHistory.length}
                  </p>
                  <p className="text-[10px] font-medium text-on-surface-variant uppercase tracking-wider">
                    Runs
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Two stacked cards */}
        <div className="col-span-12 lg:col-span-4 flex flex-col gap-4">
          <ModalDistributionCard stats={modalStats} isLoading={isLoading} />
          <OccupancyPerSiteCard
            sites={sites}
            metrics={metrics}
            isLoading={isLoading}
          />
        </div>
      </div>

      {/* ---- Bottom Section (table + weather) ---- */}
      <div className="grid grid-cols-12 gap-4">
        {/* Left: Orchestration Stream Table */}
        <div className="col-span-12 lg:col-span-9">
          <OrchestrationStreamTable
            history={optimizationHistory}
            isLoading={isLoading}
          />
        </div>

        {/* Right: Weather Widget */}
        <div className="col-span-12 lg:col-span-3">
          <WeatherCard isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}
