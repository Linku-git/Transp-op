import { useCallback, useState } from 'react';
import type {
  ModalChoiceAlternative,
  ModalChoiceResponse,
} from '../../types/sotreg';
import { computeModalChoice } from '../../api/sotreg';
import { extractApiError } from '../../lib/apiError';

const DEFAULT_MODES: ModalChoiceAlternative[] = [
  { name: 'Bus Diesel', cost: 5000, time_minutes: 45, comfort: 4 },
  { name: 'Bus Electrique', cost: 4000, time_minutes: 50, comfort: 6 },
  { name: 'Navette Hybride', cost: 6000, time_minutes: 35, comfort: 7 },
  { name: 'Covoiturage', cost: 2000, time_minutes: 40, comfort: 5 },
];

export function ModalChoicePanel() {
  const [modes, setModes] = useState<ModalChoiceAlternative[]>(DEFAULT_MODES);
  const [betaCost, setBetaCost] = useState(-0.001);
  const [betaTime, setBetaTime] = useState(-0.05);
  const [betaComfort, setBetaComfort] = useState(0.5);
  const [results, setResults] = useState<ModalChoiceResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateMode = useCallback(
    (idx: number, field: keyof ModalChoiceAlternative, value: string | number) => {
      setModes((prev) =>
        prev.map((m, i) =>
          i === idx ? { ...m, [field]: field === 'name' ? value : Number(value) } : m,
        ),
      );
    },
    [],
  );

  const addMode = useCallback(() => {
    setModes((prev) => [
      ...prev,
      { name: `Mode ${prev.length + 1}`, cost: 3000, time_minutes: 40, comfort: 5 },
    ]);
  }, []);

  const removeMode = useCallback((idx: number) => {
    setModes((prev) => prev.filter((_, i) => i !== idx));
  }, []);

  const handleCompute = useCallback(async () => {
    const valid = modes.filter((m) => m.name.trim());
    if (valid.length < 2) return;
    setLoading(true);
    setError(null);
    try {
      const res = await computeModalChoice({
        alternatives: valid,
        beta_cost: betaCost,
        beta_time: betaTime,
        beta_comfort: betaComfort,
      });
      setResults(res);
    } catch (err) {
      setError(extractApiError(err, 'Erreur de calcul'));
    } finally {
      setLoading(false);
    }
  }, [modes, betaCost, betaTime, betaComfort]);

  return (
    <div className="space-y-6">
      {/* Beta coefficients */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-5">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
          Coefficients Beta (McFadden Logit)
        </h3>
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'Beta Coût', value: betaCost, set: setBetaCost, step: 0.0001 },
            { label: 'Beta Temps', value: betaTime, set: setBetaTime, step: 0.01 },
            { label: 'Beta Confort', value: betaComfort, set: setBetaComfort, step: 0.1 },
          ].map(({ label, value, set, step }) => (
            <div key={label}>
              <label className="text-xs font-medium text-on-surface-variant block mb-1">
                {label}
              </label>
              <input
                type="number"
                value={value}
                step={step}
                onChange={(e) => set(Number(e.target.value))}
                className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
              />
            </div>
          ))}
        </div>
      </div>

      {/* Mode inputs */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
        <div className="flex items-center justify-between px-5 py-3 bg-surface-container-low/50">
          <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
            Modes de transport ({modes.length})
          </h3>
          <button
            type="button"
            onClick={addMode}
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
                <th className="text-center px-2 py-2 text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                  Coût (MAD)
                </th>
                <th className="text-center px-2 py-2 text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                  Temps (min)
                </th>
                <th className="text-center px-2 py-2 text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                  Confort (0-10)
                </th>
                <th className="px-2 py-2" />
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {modes.map((mode, idx) => (
                <tr key={idx} className="hover:bg-surface-bright">
                  <td className="px-3 py-2">
                    <input
                      type="text"
                      value={mode.name}
                      onChange={(e) => updateMode(idx, 'name', e.target.value)}
                      className="w-32 bg-transparent border-b border-outline-variant/20 text-sm text-on-surface focus:border-primary outline-none"
                    />
                  </td>
                  <td className="px-2 py-2 text-center">
                    <input
                      type="number"
                      value={mode.cost}
                      onChange={(e) => updateMode(idx, 'cost', e.target.value)}
                      min={0}
                      step={500}
                      className="w-20 text-center bg-surface-container-high/50 rounded px-1 py-1 text-sm focus:ring-1 focus:ring-primary/20 outline-none"
                    />
                  </td>
                  <td className="px-2 py-2 text-center">
                    <input
                      type="number"
                      value={mode.time_minutes}
                      onChange={(e) => updateMode(idx, 'time_minutes', e.target.value)}
                      min={0}
                      className="w-16 text-center bg-surface-container-high/50 rounded px-1 py-1 text-sm focus:ring-1 focus:ring-primary/20 outline-none"
                    />
                  </td>
                  <td className="px-2 py-2 text-center">
                    <input
                      type="number"
                      value={mode.comfort}
                      onChange={(e) => updateMode(idx, 'comfort', e.target.value)}
                      min={0}
                      max={10}
                      step={0.5}
                      className="w-16 text-center bg-surface-container-high/50 rounded px-1 py-1 text-sm focus:ring-1 focus:ring-primary/20 outline-none"
                    />
                  </td>
                  <td className="px-2 py-2 text-center">
                    <button
                      type="button"
                      onClick={() => removeMode(idx)}
                      disabled={modes.length <= 2}
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

      {/* Compute button */}
      <button
        type="button"
        onClick={handleCompute}
        disabled={loading || modes.filter((m) => m.name.trim()).length < 2}
        className="w-full bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-lg py-2.5 text-sm font-semibold shadow-lg shadow-primary/20 hover:shadow-xl disabled:opacity-50 flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <span className="material-symbols-outlined animate-spin text-lg">progress_activity</span>
            Calcul...
          </>
        ) : (
          <>
            <span className="material-symbols-outlined text-lg">psychology</span>
            Calculer les probabilités
          </>
        )}
      </button>

      {error && (
        <div className="bg-error-container/30 text-error rounded-lg px-4 py-2 text-sm">{error}</div>
      )}

      {/* Results */}
      {results && (
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
              Probabilités de choix
            </h3>
            <span className="text-xs text-on-surface-variant">
              Somme : {(results.probabilities_sum * 100).toFixed(1)}%
            </span>
          </div>

          <div className="space-y-3">
            {results.probabilities.map((p) => {
              const pct = p.probability * 100;
              const isDominant = p.name === results.dominant_mode;
              return (
                <div key={p.name} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <span className={`font-medium ${isDominant ? 'text-primary' : 'text-on-surface'}`}>
                      {p.name}
                      {isDominant && (
                        <span className="ml-2 bg-primary/10 text-primary text-[10px] font-bold px-1.5 py-0.5 rounded">
                          Dominant
                        </span>
                      )}
                    </span>
                    <span className="font-bold text-on-surface">{pct.toFixed(1)}%</span>
                  </div>
                  <div className="h-5 bg-surface-container-high rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        isDominant
                          ? 'bg-gradient-to-r from-primary to-primary-container'
                          : 'bg-outline-variant/40'
                      }`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
