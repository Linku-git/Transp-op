import { useTranslation } from 'react-i18next';
import { GaugeChart } from '@/components/charts/GaugeChart';
import type { OptimizationMetrics } from '@/types/optimization';

interface MetricsPanelProps {
  metrics: OptimizationMetrics;
}

interface MetricCardProps {
  label: string;
  children: React.ReactNode;
}

function MetricCard({ label, children }: MetricCardProps) {
  return (
    <div className="bg-surface-container-lowest rounded-lg p-4">
      {children}
      <p className="font-sans text-xs text-on-surface-variant mt-1">
        {label}
      </p>
    </div>
  );
}

function StatValue({
  value,
  unit,
}: {
  value: string | number;
  unit?: string;
}) {
  return (
    <p className="font-display text-2xl font-bold text-on-surface tabular-nums">
      {value}
      {unit && (
        <span className="text-sm font-normal text-on-surface-variant ml-1">
          {unit}
        </span>
      )}
    </p>
  );
}

/** SVG truck icon rendered inline to avoid external icon dependencies. */
function TruckIcon() {
  return (
    <svg
      className="w-5 h-5 text-secondary mb-1"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={1.5}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124a17.902 17.902 0 00-3.213-9.193 2.056 2.056 0 00-1.58-.86H14.25M16.5 18.75h-2.25m0-11.177v-.958c0-.568-.422-1.048-.987-1.106a48.554 48.554 0 00-10.026 0 1.106 1.106 0 00-.987 1.106v7.635m12-6.677v6.677m0 4.5v-4.5m0 0h-12"
      />
    </svg>
  );
}

/** SVG users icon for employees. */
function UsersIcon() {
  return (
    <svg
      className="w-5 h-5 text-secondary mb-1"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={1.5}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z"
      />
    </svg>
  );
}

/** SVG route/distance icon. */
function RouteIcon() {
  return (
    <svg
      className="w-5 h-5 text-secondary mb-1"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={1.5}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9 6.75V15m6-6v8.25m.503 3.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 00-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c.317-.159.69-.159 1.006 0l4.994 2.497c.317.158.69.158 1.006 0z"
      />
    </svg>
  );
}

/** SVG fuel/cost icon. */
function FuelIcon() {
  return (
    <svg
      className="w-5 h-5 text-secondary mb-1"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={1.5}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z"
      />
    </svg>
  );
}

/** SVG leaf icon for CO2. */
function LeafIcon() {
  return (
    <svg
      className="w-5 h-5 text-secondary mb-1"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={1.5}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z"
      />
    </svg>
  );
}

export function MetricsPanel({ metrics }: MetricsPanelProps) {
  const { t } = useTranslation();

  const occupancyPct = metrics.avg_occupancy_rate * 100;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      {/* Vehicles Used */}
      <MetricCard
        label={t('optimization.metrics.vehicles', 'Vehicules utilises')}
      >
        <TruckIcon />
        <StatValue value={metrics.total_vehicles_used} />
      </MetricCard>

      {/* Employees Assigned */}
      <MetricCard
        label={t('optimization.metrics.assigned', 'Employes affectes')}
      >
        <UsersIcon />
        <StatValue
          value={`${metrics.employees_assigned}/${metrics.total_employees}`}
        />
      </MetricCard>

      {/* Average Occupancy */}
      <MetricCard
        label={t('optimization.metrics.occupancy', 'Taux d\'occupation moyen')}
      >
        <GaugeChart value={occupancyPct} size={96} />
      </MetricCard>

      {/* Total Distance */}
      <MetricCard
        label={t('optimization.metrics.distance', 'Distance totale')}
      >
        <RouteIcon />
        <StatValue value={metrics.total_distance_km.toFixed(1)} unit="km" />
      </MetricCard>

      {/* Fuel Cost */}
      <MetricCard
        label={t('optimization.metrics.fuel_cost', 'Cout carburant')}
      >
        <FuelIcon />
        <StatValue
          value={metrics.estimated_fuel_cost_mad.toFixed(0)}
          unit="MAD"
        />
      </MetricCard>

      {/* CO2 Saved */}
      <MetricCard
        label={t('optimization.metrics.co2', 'CO2 economise')}
      >
        <LeafIcon />
        <StatValue value={metrics.co2_estimate_kg.toFixed(1)} unit="kg" />
      </MetricCard>
    </div>
  );
}
