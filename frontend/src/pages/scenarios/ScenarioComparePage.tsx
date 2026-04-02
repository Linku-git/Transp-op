import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSearchParams, Link } from 'react-router-dom';

import { listScenarios, compareScenarios } from '@/api/scenarios';
import { Button } from '@/components/ui/Button';
import type { Scenario, ScenarioComparison, MetricDelta } from '@/types/scenario';

const MAX_SCENARIOS = 3;
const MIN_SCENARIOS = 2;

function formatDelta(
  value: number,
  unit: string,
  invertSign: boolean = false,
): { text: string; className: string } {
  const improved = invertSign ? value > 0 : value < 0;
  const sign = value > 0 ? '+' : '';
  return {
    text: `${sign}${value.toFixed(1)} ${unit}`,
    className:
      value === 0
        ? 'text-on-surface-variant'
        : improved
          ? 'text-green-700'
          : 'text-error',
  };
}

function scenarioLabel(scenario: Scenario): string {
  if (scenario.name) return scenario.name;
  const date = new Date(scenario.created_at).toLocaleDateString();
  return `${scenario.condition_type} - ${date}`;
}

function LoadingSpinner({ label }: { label: string }) {
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
        <span className="text-sm font-sans text-on-surface-variant">{label}</span>
      </div>
    </div>
  );
}

function ScenarioSelector({
  index,
  selectedId,
  scenarios,
  disabledIds,
  onChange,
  label,
}: {
  index: number;
  selectedId: string;
  scenarios: Scenario[];
  disabledIds: string[];
  onChange: (index: number, id: string) => void;
  label: string;
}) {
  return (
    <div className="flex-1">
      <label className="block text-[10px] font-bold uppercase tracking-widest text-outline mb-1.5">
        {label}
      </label>
      <select
        value={selectedId}
        onChange={(e) => onChange(index, e.target.value)}
        className="w-full bg-surface-container-high/50 border-none rounded-lg p-3 text-on-surface font-sans text-sm outline-none focus:ring-2 focus:ring-primary/20 appearance-none cursor-pointer"
      >
        <option value="">{''}</option>
        {scenarios.map((s) => (
          <option key={s.id} value={s.id} disabled={disabledIds.includes(s.id)}>
            {scenarioLabel(s)}
          </option>
        ))}
      </select>
    </div>
  );
}

function MetricRow({
  label,
  values,
  unit,
  format,
}: {
  label: string;
  values: number[];
  unit: string;
  format?: (v: number) => string;
}) {
  const formatter = format ?? ((v: number) => v.toFixed(1));
  return (
    <tr className="hover:bg-surface-bright transition-colors">
      <td className="py-3 px-4 text-sm font-sans text-on-surface font-medium">
        {label}
      </td>
      {values.map((val, idx) => (
        <td
          key={idx}
          className="py-3 px-4 text-right font-sans text-base font-bold text-on-surface tabular-nums"
        >
          {formatter(val)}
          <span className="text-xs font-normal font-sans text-on-surface-variant ml-1">
            {unit}
          </span>
        </td>
      ))}
    </tr>
  );
}

function DeltaRow({
  label,
  delta: deltaValue,
  unit,
  invertSign,
}: {
  label: string;
  delta: number;
  unit: string;
  invertSign?: boolean;
}) {
  const delta = formatDelta(deltaValue, unit, invertSign);
  return (
    <tr className="hover:bg-surface-bright transition-colors">
      <td className="py-3 px-4 text-sm font-sans text-on-surface font-medium">
        {label}
      </td>
      <td className={`py-3 px-4 text-right font-sans text-base font-bold tabular-nums ${delta.className}`}>
        {delta.text}
      </td>
    </tr>
  );
}

function RecommendationsPanel({
  deltas,
  scenarios,
}: {
  deltas: MetricDelta[];
  scenarios: Scenario[];
}) {
  const { t } = useTranslation();

  const recommendations = useMemo(() => {
    const lines: string[] = [];

    for (const delta of deltas) {
      const scenarioA = scenarios.find((s) => s.id === delta.scenario_a_id);
      const scenarioB = scenarios.find((s) => s.id === delta.scenario_b_id);
      if (!scenarioA || !scenarioB) continue;

      const nameA = scenarioLabel(scenarioA);
      const nameB = scenarioLabel(scenarioB);

      if (delta.cost_delta_mad < 0) {
        lines.push(
          t(
            'scenarios.rec_cost_lower',
            '"{{nameB}}" reduces fuel cost by {{amount}} MAD compared to "{{nameA}}".',
            {
              nameA,
              nameB,
              amount: Math.abs(delta.cost_delta_mad).toFixed(0),
            },
          ),
        );
      } else if (delta.cost_delta_mad > 0) {
        lines.push(
          t(
            'scenarios.rec_cost_higher',
            '"{{nameB}}" increases fuel cost by {{amount}} MAD compared to "{{nameA}}".',
            {
              nameA,
              nameB,
              amount: delta.cost_delta_mad.toFixed(0),
            },
          ),
        );
      }

      if (delta.co2_delta_kg < -1) {
        lines.push(
          t(
            'scenarios.rec_co2_lower',
            '"{{nameB}}" emits {{amount}} kg less CO2 than "{{nameA}}".',
            {
              nameA,
              nameB,
              amount: Math.abs(delta.co2_delta_kg).toFixed(1),
            },
          ),
        );
      }

      if (delta.occupancy_delta_pct > 0) {
        lines.push(
          t(
            'scenarios.rec_occupancy_better',
            '"{{nameB}}" improves occupancy by {{amount}}% over "{{nameA}}".',
            {
              nameA,
              nameB,
              amount: delta.occupancy_delta_pct.toFixed(1),
            },
          ),
        );
      }

      if (delta.vehicles_delta < 0) {
        lines.push(
          t(
            'scenarios.rec_fewer_vehicles',
            '"{{nameB}}" uses {{count}} fewer vehicles than "{{nameA}}".',
            {
              nameA,
              nameB,
              count: Math.abs(delta.vehicles_delta),
            },
          ),
        );
      }
    }

    if (lines.length === 0) {
      lines.push(
        t(
          'scenarios.rec_no_significant',
          'No significant differences detected between the selected scenarios.',
        ),
      );
    }

    return lines;
  }, [deltas, scenarios, t]);

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
      <h2 className="text-sm font-bold uppercase tracking-widest text-on-surface-variant mb-4">
        {t('scenarios.recommendations', 'Recommendations')}
      </h2>
      <ul className="space-y-2">
        {recommendations.map((rec, idx) => (
          <li key={idx} className="flex gap-2 text-sm font-sans text-on-surface">
            <span className="text-primary mt-0.5 flex-shrink-0">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </span>
            <span>{rec}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function ScenarioComparePage() {
  const { t } = useTranslation();
  const [searchParams, setSearchParams] = useSearchParams();

  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>(['', '', '']);
  const [comparison, setComparison] = useState<ScenarioComparison | null>(null);
  const [isLoadingList, setIsLoadingList] = useState(true);
  const [isComparing, setIsComparing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load available scenarios
  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setIsLoadingList(true);
      setError(null);
      try {
        const data = await listScenarios(undefined, 1, 100);
        if (!cancelled) {
          setScenarios(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : t('scenarios.load_error', 'Failed to load scenarios'),
          );
        }
      } finally {
        if (!cancelled) {
          setIsLoadingList(false);
        }
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [t]);

  // Read pre-selected IDs from URL params
  useEffect(() => {
    const idsParam = searchParams.get('ids');
    if (idsParam && scenarios.length > 0) {
      const ids = idsParam
        .split(',')
        .filter((id) => scenarios.some((s) => s.id === id))
        .slice(0, MAX_SCENARIOS);

      if (ids.length > 0) {
        const padded = [...ids];
        while (padded.length < MAX_SCENARIOS) padded.push('');
        setSelectedIds(padded);
      }
    }
  }, [searchParams, scenarios]);

  const handleSelectorChange = useCallback(
    (index: number, id: string) => {
      setSelectedIds((prev) => {
        const next = [...prev];
        next[index] = id;
        return next;
      });

      // Update URL params
      const nextIds = [...selectedIds];
      nextIds[index] = id;
      const validIds = nextIds.filter(Boolean);
      if (validIds.length > 0) {
        setSearchParams({ ids: validIds.join(',') }, { replace: true });
      } else {
        setSearchParams({}, { replace: true });
      }
    },
    [selectedIds, setSearchParams],
  );

  const validSelectedIds = useMemo(
    () => selectedIds.filter(Boolean),
    [selectedIds],
  );

  const canCompare = validSelectedIds.length >= MIN_SCENARIOS;

  const handleCompare = useCallback(async () => {
    if (!canCompare) return;
    setIsComparing(true);
    setError(null);
    setComparison(null);
    try {
      const result = await compareScenarios(validSelectedIds);
      setComparison(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : t('scenarios.compare_error', 'Failed to compare scenarios'),
      );
    } finally {
      setIsComparing(false);
    }
  }, [canCompare, validSelectedIds, t]);

  // Auto-compare if URL had pre-selected IDs and we loaded scenarios
  useEffect(() => {
    const idsParam = searchParams.get('ids');
    if (idsParam && scenarios.length > 0 && !comparison && !isComparing) {
      const ids = idsParam
        .split(',')
        .filter((id) => scenarios.some((s) => s.id === id));
      if (ids.length >= MIN_SCENARIOS) {
        const doCompare = async () => {
          setIsComparing(true);
          setError(null);
          try {
            const result = await compareScenarios(ids);
            setComparison(result);
          } catch (err) {
            setError(
              err instanceof Error
                ? err.message
                : t('scenarios.compare_error', 'Failed to compare scenarios'),
            );
          } finally {
            setIsComparing(false);
          }
        };
        doCompare();
      }
    }
    // Only run on initial load
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scenarios]);

  const comparedScenarios = useMemo(
    () => comparison?.scenarios ?? [],
    [comparison],
  );

  const clearError = useCallback(() => setError(null), []);

  // Loading state for scenario list
  if (isLoadingList) {
    return (
      <LoadingSpinner label={t('common.loading', 'Loading...')} />
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Link
            to="/scenarios"
            className="text-sm font-sans text-primary font-medium hover:underline flex items-center gap-1"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
            {t('common.back', 'Back')}
          </Link>
          <h1 className="font-sans text-3xl font-black tracking-tight text-on-surface">
            {t('scenarios.compare_title', 'Scenario Comparison')}
          </h1>
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="bg-error-container rounded-xl p-4 mb-4 flex items-center justify-between">
          <p className="text-error text-sm font-sans">{error}</p>
          <button
            onClick={clearError}
            className="text-error text-sm font-sans font-medium hover:underline ml-4 cursor-pointer"
          >
            {t('common.dismiss', 'Dismiss')}
          </button>
        </div>
      )}

      {/* Empty state: no scenarios available */}
      {scenarios.length === 0 && (
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
              d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3"
            />
          </svg>
          <p className="font-sans text-base font-semibold text-on-surface mb-1">
            {t('scenarios.empty_title', 'No scenarios available')}
          </p>
          <p className="text-sm font-sans text-on-surface-variant mb-4">
            {t(
              'scenarios.empty_desc',
              'Simulate scenarios from the optimization page first.',
            )}
          </p>
          <Link
            to="/optimization"
            className="text-sm font-sans font-medium text-primary hover:underline"
          >
            {t('scenarios.go_to_optimization', 'Go to Optimization')}
          </Link>
        </div>
      )}

      {/* Selector section */}
      {scenarios.length > 0 && (
        <>
          <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 mb-6">
            <h2 className="text-sm font-bold uppercase tracking-widest text-on-surface-variant mb-4">
              {t('scenarios.select_scenarios', 'Select scenarios to compare')}
            </h2>
            <div className="flex gap-4 items-end">
              {selectedIds.map((id, index) => (
                <ScenarioSelector
                  key={index}
                  index={index}
                  selectedId={id}
                  scenarios={scenarios}
                  disabledIds={selectedIds.filter(
                    (sid, sidx) => sid !== '' && sidx !== index,
                  )}
                  onChange={handleSelectorChange}
                  label={t('scenarios.scenario_label', 'Scenario {{n}}', {
                    n: index + 1,
                  })}
                />
              ))}
              <Button
                variant="secondary"
                size="md"
                onClick={handleCompare}
                disabled={!canCompare}
                isLoading={isComparing}
              >
                {t('scenarios.compare_btn', 'Compare')}
              </Button>
            </div>
            {!canCompare && validSelectedIds.length < MIN_SCENARIOS && (
              <p className="text-xs font-sans text-on-surface-variant mt-2">
                {t(
                  'scenarios.select_hint',
                  'Select at least {{min}} scenarios to compare.',
                  { min: MIN_SCENARIOS },
                )}
              </p>
            )}
          </div>

          {/* Comparing spinner */}
          {isComparing && (
            <LoadingSpinner
              label={t('scenarios.comparing', 'Comparing scenarios...')}
            />
          )}

          {/* Comparison results */}
          {comparison && !isComparing && (
            <div className="flex flex-col gap-6 flex-1 min-h-0 overflow-y-auto">
              {/* Side-by-side metric cards */}
              <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
                <h2 className="text-sm font-bold uppercase tracking-widest text-on-surface-variant px-6 pt-5 pb-3">
                  {t('scenarios.side_by_side', 'Side-by-Side Metrics')}
                </h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm font-sans">
                    <thead>
                      <tr className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant bg-surface-container-low/50">
                        <th className="text-left py-3 px-4">
                          {t('scenarios.metric', 'Metric')}
                        </th>
                        {comparedScenarios.map((s) => (
                          <th
                            key={s.id}
                            className="text-right py-3 px-4 max-w-[200px] truncate"
                          >
                            {scenarioLabel(s)}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-outline-variant/10">
                      <MetricRow
                        label={t('scenarios.metric_vehicles', 'Vehicles')}
                        values={comparedScenarios.map(
                          (s) => s.estimated_metrics.total_vehicles_used,
                        )}
                        unit=""
                        format={(v) => v.toFixed(0)}
                      />
                      <MetricRow
                        label={t('scenarios.metric_occupancy', 'Occupancy')}
                        values={comparedScenarios.map(
                          (s) => s.estimated_metrics.avg_occupancy_rate * 100,
                        )}
                        unit="%"
                      />
                      <MetricRow
                        label={t('scenarios.metric_distance', 'Distance')}
                        values={comparedScenarios.map(
                          (s) => s.estimated_metrics.total_distance_km,
                        )}
                        unit="km"
                      />
                      <MetricRow
                        label={t('scenarios.metric_duration', 'Duration')}
                        values={comparedScenarios.map(
                          (s) => s.estimated_metrics.total_duration_minutes,
                        )}
                        unit="min"
                        format={(v) => v.toFixed(0)}
                      />
                      <MetricRow
                        label={t('scenarios.metric_fuel_cost', 'Fuel Cost')}
                        values={comparedScenarios.map(
                          (s) => s.estimated_metrics.estimated_fuel_cost_mad,
                        )}
                        unit="MAD"
                        format={(v) => v.toFixed(0)}
                      />
                      <MetricRow
                        label={t('scenarios.metric_co2', 'CO2')}
                        values={comparedScenarios.map(
                          (s) => s.estimated_metrics.co2_estimate_kg,
                        )}
                        unit="kg"
                      />
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Delta tables -- one per pair */}
              {comparison.deltas.map((delta) => {
                const scenarioA = comparedScenarios.find(
                  (s) => s.id === delta.scenario_a_id,
                );
                const scenarioB = comparedScenarios.find(
                  (s) => s.id === delta.scenario_b_id,
                );
                if (!scenarioA || !scenarioB) return null;

                const pairLabel = `${scenarioLabel(scenarioA)} → ${scenarioLabel(scenarioB)}`;

                return (
                  <div
                    key={`${delta.scenario_a_id}-${delta.scenario_b_id}`}
                    className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden"
                  >
                    <h2 className="text-sm font-bold uppercase tracking-widest text-on-surface-variant px-6 pt-5 pb-1">
                      {t('scenarios.deltas_title', 'Deltas')}
                    </h2>
                    <p className="text-xs font-sans text-on-surface-variant px-6 pb-3">
                      {pairLabel}
                    </p>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm font-sans">
                        <thead>
                          <tr className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant bg-surface-container-low/50">
                            <th className="text-left py-3 px-4">
                              {t('scenarios.metric', 'Metric')}
                            </th>
                            <th className="text-right py-3 px-4">
                              {t('scenarios.delta', 'Delta')}
                            </th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-outline-variant/10">
                          <DeltaRow
                            label={t('scenarios.metric_vehicles', 'Vehicles')}
                            delta={delta.vehicles_delta}
                            unit=""
                          />
                          <DeltaRow
                            label={t('scenarios.metric_occupancy', 'Occupancy')}
                            delta={delta.occupancy_delta_pct}
                            unit="%"
                            invertSign
                          />
                          <DeltaRow
                            label={t('scenarios.metric_distance', 'Distance')}
                            delta={delta.distance_delta_km}
                            unit="km"
                          />
                          <DeltaRow
                            label={t('scenarios.metric_duration', 'Duration')}
                            delta={delta.duration_delta_minutes}
                            unit="min"
                          />
                          <DeltaRow
                            label={t('scenarios.metric_fuel_cost', 'Fuel Cost')}
                            delta={delta.cost_delta_mad}
                            unit="MAD"
                          />
                          <DeltaRow
                            label={t('scenarios.metric_co2', 'CO2')}
                            delta={delta.co2_delta_kg}
                            unit="kg"
                          />
                        </tbody>
                      </table>
                    </div>
                  </div>
                );
              })}

              {/* Recommendations */}
              <RecommendationsPanel
                deltas={comparison.deltas}
                scenarios={comparedScenarios}
              />
            </div>
          )}
        </>
      )}
    </div>
  );
}
