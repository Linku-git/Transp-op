import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Card } from '../ui/Card';
import { BreakevenChart } from './BreakevenChart';
import { calculateCostAnalysis } from '../../api/financial';
import type { CostAnalysisRequest, CostAnalysisResponse } from '../../types/financial';

const DEFAULT_FORM: CostAnalysisRequest = {
  annual_route_cost: 0,
  vehicle_capacity: 30,
  fill_rate: 0.75,
  transported_employees: 50,
  average_distance_km: 15,
  kilometric_allowance_per_km: 0.25,
};

function formatEUR(value: number): string {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  }).format(value);
}

export function CostAnalysisPanel() {
  const { t } = useTranslation();
  const [form, setForm] = useState<CostAnalysisRequest>({ ...DEFAULT_FORM });
  const [result, setResult] = useState<CostAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (field: keyof CostAnalysisRequest, value: number) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await calculateCostAnalysis(form);
      setResult(response);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : t('common.error', 'Une erreur est survenue');
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div data-testid="cost-analysis-panel" className="space-y-6">
      <Card>
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-6">
          {t('financial.cost_analysis_form', 'Parametres analyse des couts')}
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          <Input
            label={t('financial.annual_route_cost', 'Cout annuel des lignes (EUR)')}
            type="number"
            min={0}
            value={form.annual_route_cost}
            onChange={(e) => handleChange('annual_route_cost', Number(e.target.value))}
          />

          <Input
            label={t('financial.vehicle_capacity', 'Capacite vehicule (places)')}
            type="number"
            min={1}
            value={form.vehicle_capacity}
            onChange={(e) => handleChange('vehicle_capacity', Number(e.target.value))}
          />

          <div className="flex flex-col gap-1.5">
            <label className="text-[10px] font-bold uppercase tracking-widest text-outline font-sans">
              {t('financial.fill_rate', 'Taux de remplissage')} ({Math.round(form.fill_rate * 100)}%)
            </label>
            <input
              type="range"
              min={0}
              max={100}
              step={1}
              value={Math.round(form.fill_rate * 100)}
              onChange={(e) => handleChange('fill_rate', Number(e.target.value) / 100)}
              className="w-full h-2 bg-surface-container-high/50 rounded-lg appearance-none cursor-pointer accent-primary"
            />
            <div className="flex justify-between text-[10px] text-on-surface-variant">
              <span>0%</span>
              <span>100%</span>
            </div>
          </div>

          <Input
            label={t('financial.transported_employees', 'Employes transportes')}
            type="number"
            min={1}
            value={form.transported_employees}
            onChange={(e) => handleChange('transported_employees', Number(e.target.value))}
          />

          <Input
            label={t('financial.average_distance_km', 'Distance moyenne (km)')}
            type="number"
            min={0}
            step={0.1}
            value={form.average_distance_km}
            onChange={(e) => handleChange('average_distance_km', Number(e.target.value))}
          />

          <Input
            label={t('financial.kilometric_allowance', 'Indemnite kilometrique (EUR/km)')}
            type="number"
            min={0}
            step={0.01}
            value={form.kilometric_allowance_per_km}
            onChange={(e) => handleChange('kilometric_allowance_per_km', Number(e.target.value))}
          />
        </div>

        <div className="mt-6 flex items-center gap-4">
          <Button onClick={handleSubmit} isLoading={loading}>
            <span className="material-symbols-outlined mr-2 text-[18px]">calculate</span>
            {t('financial.analyze', 'Analyser')}
          </Button>
        </div>

        {error && (
          <div className="mt-4 rounded-lg bg-error-container/30 text-error px-4 py-3 text-sm font-sans" role="alert">
            <span className="material-symbols-outlined align-middle mr-1 text-[18px]">error</span>
            {error}
          </div>
        )}
      </Card>

      {result && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              label={t('financial.cost_per_available_seat', 'Cout / place disponible')}
              value={formatEUR(result.cost_per_available_seat)}
              icon="airline_seat_recline_normal"
            />
            <MetricCard
              label={t('financial.cost_per_occupied_seat', 'Cout / place occupee')}
              value={formatEUR(result.cost_per_occupied_seat)}
              icon="event_seat"
            />
            <MetricCard
              label={t('financial.annual_cost_per_employee', 'Cout annuel / employe')}
              value={formatEUR(result.annual_cost_per_employee)}
              icon="person"
            />
            <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 flex flex-col items-center justify-center text-center">
              <span className="material-symbols-outlined text-primary text-[28px] mb-2">balance</span>
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
                {t('financial.breakeven', 'Seuil de rentabilite')}
              </p>
              <p className="text-2xl font-black text-on-surface font-sans">{result.breakeven_employees}</p>
              <span className="mt-1 inline-block bg-primary/10 text-primary text-xs font-bold px-3 py-1 rounded-full">
                {t('financial.breakeven_employees', 'employes')}
              </span>
            </div>
          </div>

          {result.breakeven_chart.length > 0 && (
            <Card>
              <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
                {t('financial.breakeven_chart', 'Courbe de seuil de rentabilite')}
              </h3>
              <BreakevenChart
                data={result.breakeven_chart}
                breakevenEmployees={result.breakeven_employees}
              />
            </Card>
          )}
        </>
      )}
    </div>
  );
}

interface MetricCardProps {
  label: string;
  value: string;
  icon: string;
}

function MetricCard({ label, value, icon }: MetricCardProps) {
  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 flex flex-col items-center justify-center text-center">
      <span className="material-symbols-outlined text-primary text-[28px] mb-2">{icon}</span>
      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
        {label}
      </p>
      <p className="text-2xl font-black text-on-surface font-sans">{value}</p>
    </div>
  );
}
