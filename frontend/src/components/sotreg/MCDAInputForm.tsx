import { useCallback, useState } from 'react';
import type {
  MCDAAlternative,
  MCDAWeights,
} from '../../types/sotreg';
import {
  MCDA_CRITERIA,
  MCDA_CRITERIA_LABELS,
  MCDA_DEFAULT_WEIGHTS,
} from '../../types/sotreg';

interface MCDAInputFormProps {
  onSubmit: (alternatives: MCDAAlternative[], weights: MCDAWeights, scenarioName: string) => void;
  loading?: boolean;
}

const EMPTY_ALT: MCDAAlternative = {
  name: '',
  capex: 200000,
  opex: 80000,
  co2: 50,
  risk: 3,
  comfort: 5,
  maturity: 5,
};

const PRESET_ALTERNATIVES: MCDAAlternative[] = [
  { name: 'Diesel', capex: 180000, opex: 120000, co2: 90, risk: 3, comfort: 3, maturity: 5 },
  { name: 'Electrique', capex: 300000, opex: 60000, co2: 10, risk: 2, comfort: 4.5, maturity: 3 },
  { name: 'Hybride', capex: 250000, opex: 80000, co2: 45, risk: 2.5, comfort: 4, maturity: 4 },
  { name: 'GNV', capex: 220000, opex: 95000, co2: 60, risk: 3.5, comfort: 3.5, maturity: 3.5 },
];

export function MCDAInputForm({ onSubmit, loading }: MCDAInputFormProps) {
  const [scenarioName, setScenarioName] = useState('Analyse MCDA');
  const [alternatives, setAlternatives] = useState<MCDAAlternative[]>(PRESET_ALTERNATIVES);
  const [weights, setWeights] = useState<MCDAWeights>({ ...MCDA_DEFAULT_WEIGHTS });

  const addAlternative = useCallback(() => {
    setAlternatives((prev) => [
      ...prev,
      { ...EMPTY_ALT, name: `Alternative ${prev.length + 1}` },
    ]);
  }, []);

  const removeAlternative = useCallback((index: number) => {
    setAlternatives((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const updateAlternative = useCallback(
    (index: number, field: keyof MCDAAlternative, value: string | number) => {
      setAlternatives((prev) =>
        prev.map((alt, i) =>
          i === index ? { ...alt, [field]: field === 'name' ? value : Number(value) } : alt,
        ),
      );
    },
    [],
  );

  const updateWeight = useCallback((criterion: string, newValue: number) => {
    setWeights((prev) => {
      const clamped = Math.max(0, Math.min(1, newValue));
      const delta = clamped - prev[criterion as keyof MCDAWeights];
      const otherKeys = MCDA_CRITERIA.filter((c) => c !== criterion);
      const otherSum = otherKeys.reduce((s, k) => s + prev[k as keyof MCDAWeights], 0);

      const next = { ...prev, [criterion]: clamped };
      if (otherSum > 0) {
        for (const k of otherKeys) {
          const old = prev[k as keyof MCDAWeights];
          next[k as keyof MCDAWeights] = Math.max(0, old - delta * (old / otherSum));
        }
      } else {
        const share = (1 - clamped) / otherKeys.length;
        for (const k of otherKeys) {
          next[k as keyof MCDAWeights] = share;
        }
      }

      // Re-normalize to handle floating point drift
      const total = Object.values(next).reduce((s, v) => s + v, 0);
      if (total > 0) {
        for (const k of MCDA_CRITERIA) {
          next[k as keyof MCDAWeights] = next[k as keyof MCDAWeights] / total;
        }
      }

      return next;
    });
  }, []);

  const resetWeights = useCallback(() => {
    setWeights({ ...MCDA_DEFAULT_WEIGHTS });
  }, []);

  const handleSubmit = useCallback(() => {
    const valid = alternatives.filter((a) => a.name.trim() !== '');
    if (valid.length < 1) return;
    onSubmit(valid, weights, scenarioName);
  }, [alternatives, weights, scenarioName, onSubmit]);

  const weightSum = Object.values(weights).reduce((s, v) => s + v, 0);

  return (
    <div className="space-y-6">
      {/* Scenario name */}
      <div>
        <label className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant block mb-1">
          Nom du scénario
        </label>
        <input
          type="text"
          value={scenarioName}
          onChange={(e) => setScenarioName(e.target.value)}
          className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
        />
      </div>

      {/* Weight sliders */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
            Pondérations (somme = {(weightSum * 100).toFixed(0)}%)
          </h3>
          <button
            type="button"
            onClick={resetWeights}
            className="text-xs text-primary hover:underline flex items-center gap-1"
          >
            <span className="material-symbols-outlined text-sm">restart_alt</span>
            Défaut CDC
          </button>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {MCDA_CRITERIA.map((c) => (
            <div key={c}>
              <label className="text-xs font-medium text-on-surface-variant block mb-1">
                {MCDA_CRITERIA_LABELS[c]}{' '}
                <span className="text-primary font-bold">
                  {(weights[c as keyof MCDAWeights] * 100).toFixed(0)}%
                </span>
              </label>
              <input
                type="range"
                min={0}
                max={100}
                step={1}
                value={Math.round(weights[c as keyof MCDAWeights] * 100)}
                onChange={(e) => updateWeight(c, Number(e.target.value) / 100)}
                className="w-full accent-primary"
              />
            </div>
          ))}
        </div>
      </div>

      {/* Alternatives table */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
        <div className="flex items-center justify-between px-5 py-3 bg-surface-container-low/50">
          <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
            Alternatives ({alternatives.length})
          </h3>
          <button
            type="button"
            onClick={addAlternative}
            className="text-xs bg-primary/10 text-primary px-3 py-1 rounded-lg hover:bg-primary/20 flex items-center gap-1"
          >
            <span className="material-symbols-outlined text-sm">add</span>
            Ajouter
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-surface-container-low/30">
                <th className="text-left px-3 py-2 text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                  Nom
                </th>
                {MCDA_CRITERIA.map((c) => (
                  <th
                    key={c}
                    className="text-center px-2 py-2 text-[10px] font-bold uppercase tracking-widest text-on-surface-variant"
                  >
                    {MCDA_CRITERIA_LABELS[c]}
                  </th>
                ))}
                <th className="px-2 py-2" />
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {alternatives.map((alt, idx) => (
                <tr key={idx} className="hover:bg-surface-bright">
                  <td className="px-3 py-2">
                    <input
                      type="text"
                      value={alt.name}
                      onChange={(e) => updateAlternative(idx, 'name', e.target.value)}
                      className="w-28 bg-transparent border-b border-outline-variant/20 text-sm text-on-surface focus:border-primary outline-none"
                      placeholder="Nom..."
                    />
                  </td>
                  {MCDA_CRITERIA.map((c) => (
                    <td key={c} className="px-2 py-2 text-center">
                      <input
                        type="number"
                        value={alt[c as keyof MCDAAlternative] as number}
                        onChange={(e) => updateAlternative(idx, c as keyof MCDAAlternative, e.target.value)}
                        step={c === 'capex' || c === 'opex' ? 10000 : 0.5}
                        min={0}
                        max={c === 'risk' || c === 'comfort' || c === 'maturity' ? 10 : undefined}
                        className="w-20 text-center bg-surface-container-high/50 rounded px-1 py-1 text-sm text-on-surface focus:ring-1 focus:ring-primary/20 outline-none"
                      />
                    </td>
                  ))}
                  <td className="px-2 py-2 text-center">
                    <button
                      type="button"
                      onClick={() => removeAlternative(idx)}
                      disabled={alternatives.length <= 1}
                      className="text-on-surface-variant hover:text-error disabled:opacity-30"
                    >
                      <span className="material-symbols-outlined text-lg">delete</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Submit */}
      <button
        type="button"
        onClick={handleSubmit}
        disabled={loading || alternatives.filter((a) => a.name.trim()).length < 1}
        className="w-full bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-lg py-2.5 text-sm font-semibold shadow-lg shadow-primary/20 hover:shadow-xl disabled:opacity-50 flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <span className="material-symbols-outlined animate-spin text-lg">progress_activity</span>
            Calcul en cours...
          </>
        ) : (
          <>
            <span className="material-symbols-outlined text-lg">calculate</span>
            Lancer l'analyse MCDA
          </>
        )}
      </button>
    </div>
  );
}
