import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useTranslation } from 'react-i18next';
import type { TCOVehicleResult } from '@/types/financial';

interface VehicleTCOBreakdownProps {
  vehicles: TCOVehicleResult[];
}

const VEHICLE_TYPE_SHORT: Record<string, string> = {
  minibus: 'Mini',
  midibus: 'Midi',
  bus_standard: 'Std',
  grand_bus: 'Grand',
  vehicule_leger: 'VL',
};

const MOTORIZATION_SHORT: Record<string, string> = {
  diesel: 'Dies',
  hybrid: 'Hyb',
  electric: 'Elec',
  hydrogen: 'H2',
  gnv: 'GNV',
};

function formatCompact(value: number): string {
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)}M`;
  }
  if (value >= 1_000) {
    return `${(value / 1_000).toFixed(0)}k`;
  }
  return String(value);
}

function formatMAD(value: number): string {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'MAD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

interface ChartDataItem {
  name: string;
  purchase: number;
  maintenance: number;
  energy: number;
  residual: number;
}

interface TooltipPayloadItem {
  name: string;
  value: number;
  color: string;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: TooltipPayloadItem[];
  label?: string;
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload || payload.length === 0) return null;

  return (
    <div className="bg-surface-container-lowest rounded-lg shadow-lg border border-outline-variant/10 px-3 py-2 text-xs">
      <p className="font-bold text-on-surface mb-1">{label}</p>
      {payload.map((entry) => (
        <div
          key={entry.name}
          className="flex justify-between gap-4"
          style={{ color: entry.color }}
        >
          <span>{entry.name}</span>
          <span className="font-medium">{formatMAD(entry.value)}</span>
        </div>
      ))}
    </div>
  );
}

export function VehicleTCOBreakdown({ vehicles }: VehicleTCOBreakdownProps) {
  const { t } = useTranslation();

  if (vehicles.length === 0) {
    return (
      <p className="text-sm text-on-surface-variant">
        {t('common.no_data', 'Aucune donnee')}
      </p>
    );
  }

  const chartData: ChartDataItem[] = vehicles.map((v) => ({
    name: `${VEHICLE_TYPE_SHORT[v.vehicle_type] ?? v.vehicle_type} ${MOTORIZATION_SHORT[v.motorization] ?? v.motorization}`,
    purchase: v.purchase_price * v.quantity,
    maintenance: v.maintenance_total,
    energy: v.energy_total,
    residual: v.residual_value * v.quantity,
  }));

  return (
    <div data-testid="vehicle-tco-breakdown" className="w-full h-72">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          margin={{ top: 8, right: 16, left: 8, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#c2c6d633" />
          <XAxis
            dataKey="name"
            tick={{ fontSize: 11, fill: '#424754' }}
            tickLine={false}
            axisLine={{ stroke: '#c2c6d633' }}
          />
          <YAxis
            tickFormatter={formatCompact}
            tick={{ fontSize: 11, fill: '#424754' }}
            tickLine={false}
            axisLine={false}
            width={60}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: 11 }}
            iconType="square"
            iconSize={10}
          />
          <Bar
            dataKey="purchase"
            name={t('financial.purchase', 'Achat')}
            stackId="cost"
            fill="#0058be"
            radius={[0, 0, 0, 0]}
          />
          <Bar
            dataKey="maintenance"
            name={t('financial.maintenance', 'Maintenance')}
            stackId="cost"
            fill="#924700"
            radius={[0, 0, 0, 0]}
          />
          <Bar
            dataKey="energy"
            name={t('financial.energy', 'Energie')}
            stackId="cost"
            fill="#16a34a"
            radius={[4, 4, 0, 0]}
          />
          <Bar
            dataKey="residual"
            name={t('financial.residual', 'Residuel')}
            fill="#ba1a1a"
            radius={[4, 4, 0, 0]}
            opacity={0.6}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
