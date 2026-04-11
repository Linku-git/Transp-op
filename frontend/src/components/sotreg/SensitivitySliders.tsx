import { useCallback, useEffect, useState } from 'react';
import type {
  MCDAAlternative,
  MCDAResponse,
  MCDAWeights,
} from '../../types/sotreg';
import {
  MCDA_CRITERIA,
  MCDA_CRITERIA_LABELS,
  MCDA_DEFAULT_WEIGHTS,
} from '../../types/sotreg';
import { computeMCDA } from '../../api/sotreg';
import { extractApiError } from '../../lib/apiError';

interface SensitivitySlidersProps {
  alternatives: MCDAAlternative[];
  baseResults: MCDAResponse;
  onResultsChange?: (results: MCDAResponse) => void;
}

export function SensitivitySliders({
  alternatives,
  baseResults,
  onResultsChange,
}: SensitivitySlidersProps) {
  const [weights, setWeights] = useState<MCDAWeights>(
    () => baseResults.weights_used as MCDAWeights,
  );
  const [liveResults, setLiveResults] = useState<MCDAResponse>(baseResults);
  const [computing, setComputing] = useState(false);
  const [rankingChanged, setRankingChanged] = useState(false);

  const baseRanking = baseResults.ranked_alternatives.map((a) => a.name).join(',');

  useEffect(() => {
    const newRanking = liveResults.ranked_alternatives.map((a) => a.name).join(',');
    setRankingChanged(newRanking !== baseRanking);
  }, [liveResults, baseRanking]);

  const recompute = useCallback(
    async (newWeights: MCDAWeights) => {
      setComputing(true);
      try {
        const res = await computeMCDA({
          alternatives,
          weights: newWeights,
          scenario_name: 'Sensitivity Analysis',
        });
        setLiveResults(res);
        onResultsChange?.(res);
      } catch (err) {
        // Silently ignore — keep previous results
        console.warn('Sensitivity recompute failed:', extractApiError(err, 'Erreur'));
      } finally {
        setComputing(false);
      }
    },
    [alternatives, onResultsChange],
  );

  const updateWeight = useCallback(
    (criterion: string, rawValue: number) => {
      const clamped = Math.max(0, Math.min(1, rawValue));
      const otherKeys = MCDA_CRITERIA.filter((c) => c !== criterion);
      const delta = clamped - weights[criterion as keyof MCDAWeights];
      const otherSum = otherKeys.reduce(
        (s, k) => s + weights[k as keyof MCDAWeights],
        0,
      );

      const next = { ...weights, [criterion]: clamped };
      if (otherSum > 0) {
        for (const k of otherKeys) {
          const old = weights[k as keyof MCDAWeights];
          next[k as keyof MCDAWeights] = Math.max(0, old - delta * (old / otherSum));
        }
      } else {
        const share = (1 - clamped) / otherKeys.length;
        for (const k of otherKeys) {
          next[k as keyof MCDAWeights] = share;
        }
      }

      // Re-normalize
      const total = Object.values(next).reduce((s, v) => s + v, 0);
      if (total > 0) {
        for (const k of MCDA_CRITERIA) {
          next[k as keyof MCDAWeights] = next[k as keyof MCDAWeights] / total;
        }
      }

      setWeights(next);
      void recompute(next);
    },
    [weights, recompute],
  );

  const resetWeights = useCallback(() => {
    const defaults = { ...MCDA_DEFAULT_WEIGHTS };
    setWeights(defaults);
    void recompute(defaults);
  }, [recompute]);

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Sensibilité en temps réel
        </h3>
        <div className="flex items-center gap-3">
          {computing && (
            <span className="material-symbols-outlined animate-spin text-primary text-lg">
              progress_activity
            </span>
          )}
          {rankingChanged && (
            <span className="bg-amber-50 text-amber-700 text-[10px] font-bold px-2 py-0.5 rounded flex items-center gap-1">
              <span className="material-symbols-outlined text-xs">warning</span>
              Classement modifié
            </span>
          )}
          <button
            type="button"
            onClick={resetWeights}
            className="text-xs text-primary hover:underline flex items-center gap-1"
          >
            <span className="material-symbols-outlined text-sm">restart_alt</span>
            Réinitialiser
          </button>
        </div>
      </div>

      {/* Sliders */}
      <div className="space-y-3">
        {MCDA_CRITERIA.map((c) => {
          const val = weights[c as keyof MCDAWeights];
          const base = baseResults.weights_used[c] ?? 0;
          const delta = val - base;
          return (
            <div key={c} className="flex items-center gap-3">
              <span className="w-20 text-xs font-medium text-on-surface-variant">
                {MCDA_CRITERIA_LABELS[c]}
              </span>
              <input
                type="range"
                min={0}
                max={100}
                step={1}
                value={Math.round(val * 100)}
                onChange={(e) => updateWeight(c, Number(e.target.value) / 100)}
                className="flex-1 accent-primary"
              />
              <span className="w-12 text-right text-xs font-bold text-on-surface">
                {(val * 100).toFixed(0)}%
              </span>
              {Math.abs(delta) > 0.005 && (
                <span
                  className={`w-12 text-right text-[10px] font-bold ${
                    delta > 0 ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {delta > 0 ? '+' : ''}
                  {(delta * 100).toFixed(0)}%
                </span>
              )}
            </div>
          );
        })}
      </div>

      {/* Live ranking preview */}
      <div className="border-t border-outline-variant/10 pt-3">
        <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">
          Classement actuel
        </p>
        <div className="flex flex-wrap gap-2">
          {liveResults.ranked_alternatives.map((alt) => {
            const isTop = alt.rank === 1;
            return (
              <span
                key={alt.name}
                className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${
                  isTop ? 'bg-green-50 text-green-700' : 'bg-surface-container-high/50 text-on-surface-variant'
                }`}
              >
                <span className="font-bold">#{alt.rank}</span> {alt.name}
                <span className="text-[10px] opacity-60">({alt.score.toFixed(2)})</span>
              </span>
            );
          })}
        </div>
      </div>
    </div>
  );
}
