import { useTranslation } from 'react-i18next';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
} from 'recharts';
import type { BreakevenPoint } from '../../types/financial';

interface BreakevenChartProps {
  data: BreakevenPoint[];
  breakevenEmployees: number;
}

function formatEUR(value: number): string {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  }).format(value);
}

export function BreakevenChart({ data, breakevenEmployees }: BreakevenChartProps) {
  const { t } = useTranslation();

  if (data.length === 0) {
    return (
      <div
        data-testid="breakeven-chart-empty"
        className="flex items-center justify-center h-64 text-on-surface-variant text-sm"
      >
        <span className="material-symbols-outlined mr-2">info</span>
        {t('common.no_data', 'Aucune donnee disponible')}
      </div>
    );
  }

  return (
    <div data-testid="breakeven-chart" className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 30, left: 20, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#c2c6d6" opacity={0.3} />

          <XAxis
            dataKey="employees"
            label={{
              value: t('financial.employees_axis', 'Nombre d\'employes'),
              position: 'insideBottom',
              offset: -5,
              style: { fontSize: 11, fill: '#424754' },
            }}
            tick={{ fontSize: 11, fill: '#424754' }}
            stroke="#c2c6d6"
          />

          <YAxis
            tickFormatter={(v: number) => formatEUR(v)}
            tick={{ fontSize: 11, fill: '#424754' }}
            stroke="#c2c6d6"
            label={{
              value: t('financial.annual_cost_axis', 'Cout annuel / employe (EUR)'),
              angle: -90,
              position: 'insideLeft',
              offset: -5,
              style: { fontSize: 11, fill: '#424754', textAnchor: 'middle' },
            }}
          />

          <Tooltip
            contentStyle={{
              backgroundColor: '#ffffff',
              border: '1px solid rgba(194,198,214,0.15)',
              borderRadius: '12px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
              fontFamily: 'Inter, sans-serif',
              fontSize: '12px',
            }}
            formatter={(value) => [formatEUR(value as number), String(value)]}
            labelFormatter={(label) =>
              `${label ?? 0} ${t('financial.employees_label', 'employes')}`
            }
          />

          <Legend
            verticalAlign="top"
            height={36}
            wrapperStyle={{ fontSize: '12px', fontFamily: 'Inter, sans-serif' }}
          />

          <ReferenceLine
            x={breakevenEmployees}
            stroke="#424754"
            strokeDasharray="6 4"
            strokeWidth={1.5}
            label={{
              value: `${t('financial.breakeven_label', 'Seuil')}: ${breakevenEmployees}`,
              position: 'top',
              fill: '#424754',
              fontSize: 11,
              fontWeight: 700,
            }}
          />

          <Line
            type="monotone"
            dataKey="transport_cost_per_employee"
            name={t('financial.transport_cost', 'Cout transport')}
            stroke="#0058be"
            strokeWidth={2.5}
            dot={{ r: 3, fill: '#0058be' }}
            activeDot={{ r: 5, fill: '#0058be', stroke: '#fff', strokeWidth: 2 }}
          />

          <Line
            type="monotone"
            dataKey="allowance_cost_per_employee"
            name={t('financial.kilometric_allowance_line', 'Indemnite km')}
            stroke="#924700"
            strokeWidth={2.5}
            strokeDasharray="8 4"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
