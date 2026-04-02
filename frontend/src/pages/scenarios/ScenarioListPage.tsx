import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

import { listScenarios, deleteScenario } from '@/api/scenarios';
import { Button } from '@/components/ui/Button';
import { useSiteStore } from '@/stores/siteStore';
import type { Scenario } from '@/types/scenario';

const CONDITION_LABELS: Record<string, string> = {
  normal: 'Normal',
  rain: 'Pluie',
  strike: 'Greve',
  peak: 'Pic activite',
  night: 'Nuit',
  transit_failure: 'Defaillance TC',
};

function ConditionChip({ condition }: { condition: string }) {
  const label = CONDITION_LABELS[condition] ?? condition;

  let bg: string;
  let text: string;

  switch (condition) {
    case 'rain':
    case 'strike':
    case 'transit_failure':
      bg = 'bg-error-container';
      text = 'text-error';
      break;
    case 'peak':
    case 'night':
      bg = 'bg-amber-50';
      text = 'text-amber-700';
      break;
    default:
      bg = 'bg-surface-container-high';
      text = 'text-on-surface-variant';
      break;
  }

  return (
    <span
      className={`inline-block rounded-md px-2.5 py-0.5 text-xs font-sans font-medium ${bg} ${text}`}
    >
      {label}
    </span>
  );
}

export function ScenarioListPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { sites, fetchSites } = useSiteStore();

  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [siteFilter, setSiteFilter] = useState<string>('');
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const loadScenarios = useCallback(async (siteId?: string) => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await listScenarios(siteId || undefined);
      setScenarios(data);
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setError(axiosError.response?.data?.detail ?? 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSites();
  }, [fetchSites]);

  useEffect(() => {
    loadScenarios(siteFilter || undefined);
  }, [loadScenarios, siteFilter]);

  const handleDelete = useCallback(
    async (scenario: Scenario) => {
      const name = scenario.name ?? scenario.id.slice(0, 8);
      const confirmed = window.confirm(
        t('scenarios.delete_confirm', 'Supprimer le scenario "{{name}}" ?', {
          name,
        }),
      );
      if (!confirmed) return;

      try {
        setDeletingId(scenario.id);
        await deleteScenario(scenario.id);
        setScenarios((prev) => prev.filter((s) => s.id !== scenario.id));
        setSelected((prev) => {
          const next = new Set(prev);
          next.delete(scenario.id);
          return next;
        });
      } catch (err: unknown) {
        const axiosError = err as {
          response?: { data?: { detail?: string } };
        };
        setError(
          axiosError.response?.data?.detail ?? 'Failed to delete scenario',
        );
      } finally {
        setDeletingId(null);
      }
    },
    [t],
  );

  const handleToggleSelect = useCallback((id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else if (next.size < 3) {
        next.add(id);
      }
      return next;
    });
  }, []);

  const handleCompare = useCallback(() => {
    if (selected.size < 2) return;
    const ids = Array.from(selected).join(',');
    navigate(`/scenarios/compare?ids=${ids}`);
  }, [selected, navigate]);

  const siteNameMap = useMemo(() => {
    const map: Record<string, string> = {};
    for (const site of sites) {
      map[site.id] = site.name;
    }
    return map;
  }, [sites]);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const formatNumber = (value: number, decimals = 0) => {
    return value.toLocaleString('fr-FR', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  };

  // Loading state
  if (isLoading && scenarios.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <svg
            className="animate-spin h-8 w-8 text-primary"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
          <span className="text-sm font-sans text-on-surface-variant">
            {t('common.loading', 'Chargement...')}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="font-sans text-3xl font-black tracking-tight text-on-surface">
          {t('scenarios.title', 'Scenarios')}
        </h1>
        <div className="flex items-center gap-3">
          <Button
            variant="secondary"
            size="md"
            disabled={selected.size < 2}
            onClick={handleCompare}
          >
            {t('scenarios.compare_selected', 'Comparer ({{count}})', {
              count: selected.size,
            })}
          </Button>
          <Button
            variant="primary"
            size="md"
            onClick={() => navigate('/optimization')}
          >
            {t('scenarios.new_scenario', 'Nouveau scenario')}
          </Button>
        </div>
      </div>

      {/* Site filter */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 mb-6">
        <div className="flex flex-wrap items-end gap-4">
          <div className="w-64">
            <label className="block text-[10px] font-bold uppercase tracking-widest text-outline mb-1.5">
              {t('scenarios.filter_site', 'Filtrer par site')}
            </label>
            <select
              value={siteFilter}
              onChange={(e) => setSiteFilter(e.target.value)}
              className="w-full bg-surface-container-high/50 border-none rounded-lg p-3 text-on-surface font-sans text-sm outline-none focus:ring-2 focus:ring-primary/20 appearance-none cursor-pointer"
            >
              <option value="">
                {t('scenarios.all_sites', 'Tous les sites')}
              </option>
              {sites.map((site) => (
                <option key={site.id} value={site.id}>
                  {site.name}
                </option>
              ))}
            </select>
          </div>
          {selected.size > 0 && (
            <p className="text-xs font-sans text-on-surface-variant py-3">
              {t(
                'scenarios.selection_hint',
                '{{count}} scenario(s) selectionne(s) - max 3',
                { count: selected.size },
              )}
            </p>
          )}
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="bg-error-container rounded-xl p-4 mb-4 flex items-center justify-between">
          <p className="text-error text-sm font-sans">{error}</p>
          <button
            onClick={() => setError(null)}
            className="text-error text-sm font-sans font-medium hover:underline ml-4 cursor-pointer"
          >
            {t('common.dismiss', 'Fermer')}
          </button>
        </div>
      )}

      {/* Empty state */}
      {!isLoading && scenarios.length === 0 && (
        <div className="flex-1 flex flex-col items-center justify-center">
          <svg
            className="mx-auto mb-3 w-12 h-12 text-primary/30"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5"
            />
          </svg>
          <p className="font-sans text-base font-semibold text-on-surface mb-1">
            {t('scenarios.empty_title', 'Aucun scenario')}
          </p>
          <p className="text-sm font-sans text-on-surface-variant mb-4">
            {t(
              'scenarios.empty_desc',
              'Lancez une optimisation pour creer votre premier scenario.',
            )}
          </p>
          <Button
            variant="primary"
            size="md"
            onClick={() => navigate('/optimization')}
          >
            {t('scenarios.go_to_optimization', 'Aller a l\'optimisation')}
          </Button>
        </div>
      )}

      {/* Table */}
      {scenarios.length > 0 && (
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-auto">
            <table className="w-full text-sm font-sans">
              <thead>
                <tr className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant bg-surface-container-low/50">
                  <th className="text-left py-3 px-4 w-10">
                    <span className="sr-only">
                      {t('scenarios.col_select', 'Selectionner')}
                    </span>
                  </th>
                  <th className="text-left py-3 px-4">
                    {t('scenarios.col_name', 'Nom')}
                  </th>
                  <th className="text-left py-3 px-4">
                    {t('scenarios.col_site', 'Site')}
                  </th>
                  <th className="text-left py-3 px-4">
                    {t('scenarios.col_condition', 'Condition')}
                  </th>
                  <th className="text-right py-3 px-4">
                    {t('scenarios.col_multiplier', 'Multiplicateur')}
                  </th>
                  <th className="text-right py-3 px-4">
                    {t('scenarios.col_vehicles', 'Vehicules')}
                  </th>
                  <th className="text-right py-3 px-4">
                    {t('scenarios.col_cost', 'Cout (MAD)')}
                  </th>
                  <th className="text-right py-3 px-4">
                    {t('scenarios.col_co2', 'CO2 (kg)')}
                  </th>
                  <th className="text-left py-3 px-4">
                    {t('scenarios.col_date', 'Date')}
                  </th>
                  <th className="text-right py-3 px-4">
                    {t('scenarios.col_actions', 'Actions')}
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/10">
                {scenarios.map((scenario) => {
                  const isSelected = selected.has(scenario.id);
                  const isDeleting = deletingId === scenario.id;
                  const metrics = scenario.estimated_metrics;
                  const siteName =
                    siteNameMap[scenario.site_id] ?? scenario.site_id.slice(0, 8);

                  return (
                    <tr
                      key={scenario.id}
                      className={[
                        'transition-colors',
                        isSelected
                          ? 'bg-primary/5'
                          : 'hover:bg-surface-bright',
                      ].join(' ')}
                    >
                      {/* Checkbox */}
                      <td className="py-3 px-4">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          disabled={!isSelected && selected.size >= 3}
                          onChange={() => handleToggleSelect(scenario.id)}
                          className="w-4 h-4 rounded accent-primary cursor-pointer disabled:cursor-not-allowed disabled:opacity-40"
                          aria-label={t('scenarios.select_scenario', 'Selectionner {{name}}', {
                            name: scenario.name ?? scenario.id.slice(0, 8),
                          })}
                        />
                      </td>

                      {/* Name */}
                      <td className="py-3 px-4 text-on-surface font-medium">
                        {scenario.name ?? scenario.id.slice(0, 8)}
                      </td>

                      {/* Site */}
                      <td className="py-3 px-4 text-on-surface-variant">
                        {siteName}
                      </td>

                      {/* Condition */}
                      <td className="py-3 px-4">
                        <ConditionChip condition={scenario.condition_type} />
                      </td>

                      {/* Multiplier */}
                      <td className="py-3 px-4 text-right text-on-surface tabular-nums">
                        {formatNumber(scenario.demand_multiplier, 2)}x
                      </td>

                      {/* Vehicles */}
                      <td className="py-3 px-4 text-right text-on-surface tabular-nums">
                        {metrics.total_vehicles_used}
                      </td>

                      {/* Cost */}
                      <td className="py-3 px-4 text-right text-on-surface tabular-nums">
                        {formatNumber(metrics.estimated_fuel_cost_mad, 2)}
                      </td>

                      {/* CO2 */}
                      <td className="py-3 px-4 text-right text-on-surface tabular-nums">
                        {formatNumber(metrics.co2_estimate_kg, 1)}
                      </td>

                      {/* Date */}
                      <td className="py-3 px-4 text-on-surface-variant">
                        {formatDate(scenario.created_at)}
                      </td>

                      {/* Actions */}
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center gap-2 justify-end">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() =>
                              navigate(
                                `/scenarios/compare?ids=${scenario.id}`,
                              )
                            }
                          >
                            {t('common.view', 'Voir')}
                          </Button>
                          <Button
                            variant="danger"
                            size="sm"
                            isLoading={isDeleting}
                            disabled={isDeleting}
                            onClick={() => handleDelete(scenario)}
                          >
                            {t('common.delete', 'Supprimer')}
                          </Button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
