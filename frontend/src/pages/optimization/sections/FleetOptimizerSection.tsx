import { useEffect, useState, useCallback, useMemo } from 'react';
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, Cell } from 'recharts';
import { listConfigurationPlans } from '@/api/vehicles';
import {
  getFleetAnalysis, runFleetOptimizer, generateNewConfig,
  type FleetAnalysis, type OptimizationResult, type OptimizedTrip,
  type NewConfigResult, type ProposedTrip,
} from '@/api/transportOptimization';
import type { ConfigurationPlan } from '@/types/vehicle';

/* ── constants ───────────────────────────────────────────────────────────── */
const VEHICLE_COLOR: Record<string, string> = {
  AUTOCAR: 'bg-sky-100 text-sky-700',
  MINIBUS: 'bg-indigo-100 text-indigo-700',
  MINICAR: 'bg-pink-100 text-pink-700',
};
const ACTION_COLOR: Record<string, { bg: string; text: string; icon: string }> = {
  downsize: { bg: 'bg-emerald-50', text: 'text-emerald-700', icon: 'arrow_downward' },
  upsize:   { bg: 'bg-amber-50',   text: 'text-amber-700',   icon: 'arrow_upward' },
  keep:     { bg: 'bg-slate-50',   text: 'text-slate-500',   icon: 'check' },
};
const SHIFT_COLOR: Record<string, string> = {
  P1: 'bg-blue-100 text-blue-700',
  P2: 'bg-amber-100 text-amber-700',
  P3: 'bg-green-100 text-green-700',
  N:  'bg-slate-100 text-slate-600',
  S:  'bg-purple-100 text-purple-700',
};

/* ── helpers ─────────────────────────────────────────────────────────────── */
function FillBar({ pct, color }: { pct: number; color?: string }) {
  const clr = color ?? (pct >= 70 ? '#10b981' : pct >= 50 ? '#f59e0b' : '#ef4444');
  return (
    <div className="flex items-center gap-1.5 flex-1">
      <div className="flex-1 h-1.5 rounded-full bg-slate-100 overflow-hidden">
        <div className="h-full rounded-full transition-all" style={{ width: `${Math.min(100, pct)}%`, backgroundColor: clr }} />
      </div>
      <span className="text-[10px] font-mono w-7 text-right" style={{ color: clr }}>{pct}%</span>
    </div>
  );
}
function ScoreGauge({ score, label }: { score: number; label: string }) {
  const grade = score >= 85 ? 'A' : score >= 70 ? 'B' : score >= 55 ? 'C' : score >= 40 ? 'D' : 'F';
  const color = score >= 85 ? '#10b981' : score >= 70 ? '#3b82f6' : score >= 55 ? '#f59e0b' : '#ef4444';
  return (
    <div className="flex flex-col items-center gap-1 flex-1">
      <div className="w-12 h-12 rounded-full border-4 flex items-center justify-center font-black text-lg" style={{ borderColor: color, color }}>
        {grade}
      </div>
      <p className="text-[10px] text-slate-500 text-center">{label}</p>
      <p className="text-xs font-mono" style={{ color }}>{Math.round(score)}/100</p>
    </div>
  );
}
function KpiCard({ label, value, sub, icon, highlight }: { label: string; value: string | number; sub?: string; icon?: string; highlight?: boolean }) {
  return (
    <div className={['rounded-xl border p-4 flex flex-col gap-1', highlight ? 'bg-emerald-50 border-emerald-200' : 'bg-white border-slate-100'].join(' ')}>
      {icon && (
        <span className={['material-symbols-outlined text-xl', highlight ? 'text-emerald-500' : 'text-blue-400'].join(' ')} style={{ fontVariationSettings: "'FILL' 1" }}>
          {icon}
        </span>
      )}
      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{label}</p>
      <p className={['text-2xl font-black', highlight ? 'text-emerald-700' : 'text-slate-800'].join(' ')}>{value}</p>
      {sub && <p className="text-[10px] text-slate-400">{sub}</p>}
    </div>
  );
}

/* ── New config mode component ───────────────────────────────────────────── */
function NewConfigMode() {
  const [targetFill, setTargetFill] = useState(78);
  const [preferSmaller, setPreferSmaller] = useState(true);
  const [maxStops, setMaxStops] = useState(8);
  const [shifts, setShifts] = useState<string[]>(['P1', 'P2', 'N']);
  const [planName, setPlanName] = useState('Nouvelle configuration 2025');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<NewConfigResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filterShift, setFilterShift] = useState('');
  const [filterVehicle, setFilterVehicle] = useState('');
  const [showTrips, setShowTrips] = useState(false);

  const SHIFTS_ALL = ['P1', 'P2', 'P3', 'N', 'S'];

  const toggleShift = (s: string) => setShifts((prev) => prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const r = await generateNewConfig({ target_fill: targetFill / 100, prefer_smaller: preferSmaller, max_stops_per_route: maxStops, shifts, plan_name: planName });
      setResult(r);
      setShowTrips(false);
    } catch (e: unknown) {
      setError((e as Error).message || 'Erreur de génération');
    } finally {
      setLoading(false);
    }
  };

  const filteredTrips = useMemo(() => {
    if (!result) return [];
    return result.trips.filter((t) => {
      if (filterShift && t.shift !== filterShift) return false;
      if (filterVehicle && t.vehicle_type !== filterVehicle) return false;
      return true;
    });
  }, [result, filterShift, filterVehicle]);

  const vehicleChartData = result ? Object.entries(result.vehicle_summary).map(([k, v]) => ({ name: k, value: v, color: k === 'AUTOCAR' ? '#3b82f6' : k === 'MINIBUS' ? '#8b5cf6' : '#f59e0b' })) : [];

  return (
    <div className="flex flex-col gap-5">
      {/* Info banner */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl px-4 py-3 flex items-start gap-3">
        <span className="material-symbols-outlined text-blue-500 text-xl mt-0.5" style={{ fontVariationSettings: "'FILL' 1" }}>info</span>
        <div>
          <p className="text-sm font-semibold text-blue-800">Génération depuis les données maîtres</p>
          <p className="text-xs text-blue-600 mt-0.5">
            Cette configuration est générée en partant de zéro — en utilisant uniquement les arrêts, employés et véhicules du master data.
            <span className="ml-1 font-bold text-blue-700">Configuration Initiale 2024 exclue.</span>
          </p>
        </div>
      </div>

      {/* Params wizard */}
      <div className="bg-white border border-slate-100 rounded-xl p-5">
        <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4">Paramètres de génération</p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-bold text-slate-500">Nom du plan</label>
            <input value={planName} onChange={(e) => setPlanName(e.target.value)}
              className="border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 bg-slate-50" />
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-bold text-slate-500">Taux remplissage cible</label>
            <div className="flex items-center gap-2">
              <input type="range" min={50} max={95} step={5} value={targetFill}
                onChange={(e) => setTargetFill(Number(e.target.value))} className="flex-1 accent-blue-600" />
              <span className="text-sm font-bold text-blue-700 w-10">{targetFill}%</span>
            </div>
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-bold text-slate-500">Arrêts max. par circuit</label>
            <div className="flex items-center gap-2">
              <input type="range" min={3} max={15} step={1} value={maxStops}
                onChange={(e) => setMaxStops(Number(e.target.value))} className="flex-1 accent-blue-600" />
              <span className="text-sm font-bold text-slate-700 w-6">{maxStops}</span>
            </div>
          </div>
          <div className="flex flex-col gap-1.5 col-span-full md:col-span-1">
            <label className="text-xs font-bold text-slate-500">Shifts à couvrir</label>
            <div className="flex gap-2 flex-wrap">
              {SHIFTS_ALL.map((s) => (
                <button key={s} onClick={() => toggleShift(s)}
                  className={['px-3 py-1.5 rounded-lg text-xs font-bold border transition-colors', shifts.includes(s) ? 'bg-blue-600 text-white border-blue-600' : 'bg-slate-50 text-slate-500 border-slate-200 hover:border-blue-300'].join(' ')}>
                  {s}
                </button>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-3 col-span-full md:col-span-1">
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <div className={['w-10 h-5 rounded-full relative transition-colors', preferSmaller ? 'bg-blue-600' : 'bg-slate-300'].join(' ')} onClick={() => setPreferSmaller((v) => !v)}>
                <div className={['absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform', preferSmaller ? 'translate-x-5' : 'translate-x-0.5'].join(' ')} />
              </div>
              <span className="text-xs font-bold text-slate-600">Préférer véhicules plus petits</span>
            </label>
          </div>
          <div className="flex items-end col-span-full md:col-span-1">
            <button onClick={handleGenerate} disabled={loading || shifts.length === 0}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-xl px-6 py-2.5 text-sm font-semibold transition-colors shadow-sm">
              {loading ? <><span className="material-symbols-outlined text-base animate-spin">progress_activity</span>Génération…</> : <><span className="material-symbols-outlined text-base">auto_awesome</span>Générer la configuration</>}
            </button>
          </div>
        </div>
      </div>

      {error && <div className="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3 border border-red-200">{error}</div>}

      {result && (
        <>
          {/* KPIs */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <KpiCard label="Trajets proposés" value={result.total_proposed_trips} icon="route" />
            <KpiCard label="Arrêts utilisés" value={result.total_stops_used} icon="location_on" />
            <KpiCard label="KM journaliers" value={result.total_estimated_km.toLocaleString('fr-MA')} icon="straighten" />
            <KpiCard label="Coût journalier" value={`${result.total_estimated_daily_cost.toLocaleString('fr-MA')} MAD`} icon="payments" highlight />
          </div>

          {/* Charts + methodology */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            <div className="bg-white rounded-xl border border-slate-100 p-4">
              <p className="text-xs font-bold text-slate-400 mb-3 uppercase tracking-wider">Répartition véhicules</p>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={vehicleChartData} margin={{ left: -20, right: 0 }}>
                  <XAxis dataKey="name" tick={{ fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 10 }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ fontSize: 11, borderRadius: 8 }} />
                  <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                    {vehicleChartData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="bg-white rounded-xl border border-slate-100 p-4">
              <p className="text-xs font-bold text-slate-400 mb-3 uppercase tracking-wider">Répartition shifts</p>
              <div className="flex flex-col gap-2 mt-2">
                {Object.entries(result.shift_summary).map(([shift, count]) => (
                  <div key={shift} className="flex items-center gap-3">
                    <span className={['text-[10px] font-bold px-2 py-0.5 rounded-full w-10 text-center', SHIFT_COLOR[shift] ?? 'bg-slate-100 text-slate-500'].join(' ')}>{shift}</span>
                    <div className="flex-1 h-2 rounded-full bg-slate-100 overflow-hidden">
                      <div className="h-full rounded-full bg-blue-500" style={{ width: `${(count / result.total_proposed_trips) * 100}%` }} />
                    </div>
                    <span className="text-xs font-mono text-slate-500 w-8 text-right">{count}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-4 text-white flex flex-col gap-3">
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Méthodologie IA</p>
              <p className="text-xs text-slate-300 leading-relaxed">{result.methodology}</p>
              <div className="mt-auto pt-2 border-t border-slate-700">
                <p className="text-[10px] text-slate-500">Données exclues</p>
                <p className="text-xs font-semibold text-amber-400">{result.excluded_plan}</p>
              </div>
            </div>
          </div>

          {/* Trip table */}
          <div className="bg-white rounded-xl border border-slate-100 overflow-hidden">
            <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100">
              <div className="flex items-center gap-3">
                <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Trajets proposés ({filteredTrips.length})</p>
                <select value={filterShift} onChange={(e) => setFilterShift(e.target.value)}
                  className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2 py-1 text-slate-600 appearance-none">
                  <option value="">Tous shifts</option>
                  {result.shifts && Object.keys(result.shift_summary).map((s) => <option key={s}>{s}</option>)}
                </select>
                <select value={filterVehicle} onChange={(e) => setFilterVehicle(e.target.value)}
                  className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2 py-1 text-slate-600 appearance-none">
                  <option value="">Tous véhicules</option>
                  {Object.keys(result.vehicle_summary).map((v) => <option key={v}>{v}</option>)}
                </select>
              </div>
              <button onClick={() => setShowTrips((v) => !v)}
                className="text-xs text-blue-500 hover:text-blue-700 flex items-center gap-1 font-medium">
                <span className="material-symbols-outlined text-sm">{showTrips ? 'expand_less' : 'expand_more'}</span>
                {showTrips ? 'Réduire' : 'Voir les trajets'}
              </button>
            </div>

            {showTrips && (
              <div className="overflow-y-auto" style={{ maxHeight: 420 }}>
                <table className="w-full text-xs">
                  <thead className="bg-slate-50 sticky top-0">
                    <tr>
                      {['Zone', 'Shift', 'A/R', 'Arrêts', 'Passagers', 'Véhicule', 'Remplissage', 'KM', 'Coût/jour'].map((h) => (
                        <th key={h} className="px-3 py-2 text-left text-[10px] font-bold text-slate-400 uppercase tracking-wider">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {filteredTrips.slice(0, 200).map((t, i) => (
                      <tr key={i} className="hover:bg-slate-50/50">
                        <td className="px-3 py-2 font-medium text-slate-700">{t.zone}</td>
                        <td className="px-3 py-2">
                          <span className={['px-1.5 py-0.5 rounded-full font-bold text-[10px]', SHIFT_COLOR[t.shift] ?? 'bg-slate-100 text-slate-500'].join(' ')}>{t.shift}</span>
                        </td>
                        <td className="px-3 py-2">
                          <span className={['px-1.5 py-0.5 rounded-full font-bold text-[10px]', t.aller_retour === 'ALLER' ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'].join(' ')}>{t.aller_retour}</span>
                        </td>
                        <td className="px-3 py-2 text-slate-500">{t.stop_count} arrêts</td>
                        <td className="px-3 py-2 font-mono text-slate-700">{t.estimated_passengers}</td>
                        <td className="px-3 py-2">
                          <span className={['px-1.5 py-0.5 rounded font-bold text-[10px]', VEHICLE_COLOR[t.vehicle_type] ?? 'bg-slate-100 text-slate-500'].join(' ')}>{t.vehicle_type}</span>
                        </td>
                        <td className="px-3 py-2">
                          <div className="flex items-center gap-1">
                            <div className="w-12 h-1.5 rounded-full bg-slate-100 overflow-hidden">
                              <div className="h-full rounded-full" style={{ width: `${Math.min(100, t.fill_pct)}%`, backgroundColor: t.fill_pct >= 70 ? '#10b981' : t.fill_pct >= 50 ? '#f59e0b' : '#ef4444' }} />
                            </div>
                            <span className="font-mono text-[10px] text-slate-500">{t.fill_pct}%</span>
                          </div>
                        </td>
                        <td className="px-3 py-2 font-mono text-slate-500">{t.estimated_km}</td>
                        <td className="px-3 py-2 font-mono text-slate-700">{t.estimated_cost_mad.toFixed(0)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {filteredTrips.length > 200 && <p className="text-center py-3 text-xs text-slate-400">+ {filteredTrips.length - 200} trajets supplémentaires (appliquer des filtres pour réduire)</p>}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

/* ── Main component ──────────────────────────────────────────────────────── */
export function FleetOptimizerSection() {
  const [mode, setMode] = useState<'optimize' | 'new_config'>('optimize');
  const [plans, setPlans] = useState<ConfigurationPlan[]>([]);
  const [planId, setPlanId] = useState('');
  const [analysis, setAnalysis] = useState<FleetAnalysis | null>(null);
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAll, setShowAll] = useState(false);

  // Params
  const [minFill, setMinFill] = useState(70);
  const [fillAssumption, setFillAssumption] = useState(82);
  const [preferSmaller, setPreferSmaller] = useState(true);
  const [shiftFilter, setShiftFilter] = useState('');
  const [secteurFilter, setSecteurFilter] = useState('');

  useEffect(() => {
    listConfigurationPlans({ page_size: 50 }).then((r) => {
      const items = r.items ?? [];
      setPlans(items);
      const current = items.find((p) => p.is_current) ?? items[0];
      if (current) setPlanId(current.id);
    });
  }, []);

  const loadAnalysis = useCallback(async (id: string) => {
    if (!id) return;
    setAnalysisLoading(true);
    setResult(null);
    setError(null);
    try {
      setAnalysis(await getFleetAnalysis(id));
    } catch (e: unknown) {
      setError((e as Error).message || 'Erreur');
    } finally {
      setAnalysisLoading(false);
    }
  }, []);

  useEffect(() => { if (planId) loadAnalysis(planId); }, [planId, loadAnalysis]);

  const handleOptimize = async () => {
    if (!planId) return;
    setRunning(true);
    setError(null);
    try {
      const r = await runFleetOptimizer(planId, {
        min_fill_rate: minFill / 100,
        fill_assumption: fillAssumption / 100,
        prefer_smaller: preferSmaller,
        shift_filter: shiftFilter || null,
        secteur_filter: secteurFilter || null,
      });
      setResult(r);
    } catch (e: unknown) {
      setError((e as Error).message || 'Erreur d\'optimisation');
    } finally {
      setRunning(false);
    }
  };

  const radarData = analysis ? [
    { subject: 'Efficacité', before: analysis.current_score.efficiency, after: result?.new_score.efficiency ?? null },
    { subject: 'Finance',   before: analysis.current_score.finance,    after: result?.new_score.finance    ?? null },
    { subject: 'Taux remplissage', before: analysis.current_score.fill, after: result?.new_score.fill      ?? null },
    { subject: 'CO₂',       before: analysis.current_score.co2,        after: result?.new_score.co2        ?? null },
  ] : [];

  const sectors = analysis ? Object.keys(analysis.secteurs) : [];

  const displayedTrips: OptimizedTrip[] = result
    ? (showAll ? result.optimized_trips : result.optimized_trips.filter((t) => t.action !== 'keep').slice(0, 40))
    : [];

  return (
    <div className="flex flex-col gap-5">
      {/* ── Mode toggle ─────────────────────────────────────────────────── */}
      <div className="flex items-center gap-2 bg-white border border-slate-100 rounded-xl p-1.5 self-start">
        <button
          onClick={() => setMode('optimize')}
          className={['flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-colors', mode === 'optimize' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-500 hover:text-slate-700'].join(' ')}
        >
          <span className="material-symbols-outlined text-base">tune</span>
          Optimiser configuration existante
        </button>
        <button
          onClick={() => setMode('new_config')}
          className={['flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-colors', mode === 'new_config' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-500 hover:text-slate-700'].join(' ')}
        >
          <span className="material-symbols-outlined text-base">auto_awesome</span>
          Nouvelle configuration
        </button>
      </div>

      {mode === 'new_config' ? <NewConfigMode /> : (
      <>
      {/* ── Plan + params bar ──────────────────────────────────────────── */}
      <div className="bg-white border border-slate-100 rounded-xl px-4 py-4 flex flex-wrap gap-4 items-end">
        <div className="flex flex-col gap-1 min-w-[200px]">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Plan de configuration</label>
          <select value={planId} onChange={(e) => setPlanId(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 appearance-none">
            {plans.map((p) => (
              <option key={p.id} value={p.id}>{p.name}{p.is_current ? ' ✓' : ''}</option>
            ))}
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Taux remplissage min.</label>
          <div className="flex items-center gap-2">
            <input type="range" min={50} max={90} step={5} value={minFill}
              onChange={(e) => setMinFill(Number(e.target.value))}
              className="w-28 accent-blue-600" />
            <span className="text-sm font-bold text-blue-700 w-10">{minFill}%</span>
          </div>
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Occupation estimée</label>
          <div className="flex items-center gap-2">
            <input type="range" min={60} max={95} step={5} value={fillAssumption}
              onChange={(e) => setFillAssumption(Number(e.target.value))}
              className="w-28 accent-blue-600" />
            <span className="text-sm font-bold text-slate-700 w-10">{fillAssumption}%</span>
          </div>
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Shift</label>
          <select value={shiftFilter} onChange={(e) => setShiftFilter(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 appearance-none min-w-[110px]">
            <option value="">Tous</option>
            {['P1','P2','P3','N','S'].map((s) => <option key={s}>Shift {s}</option>)}
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Secteur</label>
          <select value={secteurFilter} onChange={(e) => setSecteurFilter(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 appearance-none min-w-[130px]">
            <option value="">Tous</option>
            {sectors.map((s) => <option key={s}>{s}</option>)}
          </select>
        </div>
        <div className="flex items-center gap-2 pb-0.5">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider whitespace-nowrap">
            <input type="checkbox" checked={preferSmaller} onChange={(e) => setPreferSmaller(e.target.checked)} className="mr-1.5 accent-blue-600" />
            Réduire la taille
          </label>
        </div>
        <button
          onClick={handleOptimize}
          disabled={running || !planId || analysisLoading}
          className="flex items-center gap-2 bg-blue-600 text-white rounded-xl px-5 py-2.5 text-sm font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors ml-auto"
        >
          {running
            ? <><span className="material-symbols-outlined text-base animate-spin">progress_activity</span>Optimisation…</>
            : <><span className="material-symbols-outlined text-base">bolt</span>Lancer l'optimisation</>
          }
        </button>
      </div>

      {error && <div className="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3 border border-red-200">{error}</div>}

      {analysisLoading ? (
        <div className="flex items-center justify-center h-40 text-slate-400">
          <span className="material-symbols-outlined text-3xl animate-spin mr-3">progress_activity</span>
          Chargement de l'analyse…
        </div>
      ) : analysis && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          {/* Left: current analysis */}
          <div className="flex flex-col gap-4">
            <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Configuration actuelle</p>
            <div className="grid grid-cols-2 gap-3">
              <KpiCard label="Trajets" value={analysis.total_trips} icon="route" />
              <KpiCard label="Postes" value={analysis.total_postes} icon="grid_view" />
              <KpiCard label="Total KM" value={analysis.total_km.toLocaleString('fr-MA')} icon="straighten" />
              <KpiCard label="Taux remplissage" value={`${analysis.avg_fill_pct}%`} icon="local_shipping" />
            </div>
            {/* Vehicle distribution */}
            <div className="bg-white rounded-xl border border-slate-100 p-4">
              <p className="text-xs font-bold text-slate-400 mb-3">Types de véhicules</p>
              {Object.entries(analysis.vehicle_dist).map(([type, count]) => (
                <div key={type} className="flex items-center gap-3 mb-2">
                  <span className={['text-[10px] font-bold px-2 py-0.5 rounded-full w-20 text-center shrink-0', VEHICLE_COLOR[type] ?? 'bg-slate-100 text-slate-600'].join(' ')}>{type}</span>
                  <div className="flex-1 h-2 rounded-full bg-slate-100 overflow-hidden">
                    <div className="h-full rounded-full bg-blue-500" style={{ width: `${(count / analysis.total_trips) * 100}%` }} />
                  </div>
                  <span className="text-xs font-mono text-slate-600 w-12 text-right">{count} ({Math.round((count / analysis.total_trips) * 100)}%)</span>
                </div>
              ))}
            </div>
            {/* Shift distribution */}
            <div className="bg-white rounded-xl border border-slate-100 p-4">
              <p className="text-xs font-bold text-slate-400 mb-3">Répartition shifts</p>
              {Object.entries(analysis.shifts).sort().map(([shift, count]) => (
                <div key={shift} className="flex items-center gap-3 mb-2">
                  <span className={['text-[10px] font-bold px-2 py-0.5 rounded-full w-14 text-center shrink-0', SHIFT_COLOR[shift] ?? 'bg-slate-100 text-slate-600'].join(' ')}>Shift {shift}</span>
                  <div className="flex-1 h-2 rounded-full bg-slate-100 overflow-hidden">
                    <div className="h-full rounded-full bg-amber-400" style={{ width: `${(count / analysis.total_trips) * 100}%` }} />
                  </div>
                  <span className="text-xs font-mono text-slate-600 w-10 text-right">{count}</span>
                </div>
              ))}
            </div>
            <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 text-xs text-amber-700">
              <p className="font-bold mb-1">⚠ Alertes</p>
              <p>{analysis.routes_below_70} trajet(s) sous 70% de remplissage</p>
              {analysis.routes_above_100 > 0 && <p>{analysis.routes_above_100} trajet(s) en surtaux</p>}
              <p className="mt-1 font-semibold">Coût journalier estimé: {analysis.estimated_daily_cost_mad.toLocaleString('fr-MA')} MAD</p>
            </div>
          </div>

          {/* Center: radar chart */}
          <div className="flex flex-col gap-4">
            <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">
              {result ? 'Scores : Avant vs Après' : 'Scores de performance'}
            </p>
            <div className="bg-white rounded-xl border border-slate-100 p-4">
              <div className="flex justify-center gap-6 mb-3">
                {[
                  { label: 'Actuel', color: '#3b82f6' },
                  ...(result ? [{ label: 'Optimisé', color: '#10b981' }] : []),
                ].map((e) => (
                  <div key={e.label} className="flex items-center gap-1.5 text-xs text-slate-500">
                    <span className="w-3 h-3 rounded-full" style={{ backgroundColor: e.color }} />
                    {e.label}
                  </div>
                ))}
              </div>
              <ResponsiveContainer width="100%" height={260}>
                <RadarChart data={radarData} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11 }} />
                  <Tooltip contentStyle={{ fontSize: 11, borderRadius: 8 }} formatter={(v: number) => [`${v.toFixed(0)}/100`]} />
                  <Radar name="Actuel" dataKey="before" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.2} />
                  {result && <Radar name="Optimisé" dataKey="after" stroke="#10b981" fill="#10b981" fillOpacity={0.2} />}
                </RadarChart>
              </ResponsiveContainer>
              <div className="flex justify-around mt-2">
                {['efficiency', 'finance', 'fill', 'co2'].map((k) => (
                  <ScoreGauge
                    key={k}
                    score={result ? (result.new_score[k] ?? 0) : analysis.current_score[k]}
                    label={{ efficiency: 'Efficacité', finance: 'Finance', fill: 'Remplissage', co2: 'CO₂' }[k]!}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Right: optimization results */}
          <div className="flex flex-col gap-4">
            {!result ? (
              <div className="bg-slate-50 rounded-xl border border-slate-200 border-dashed p-8 flex flex-col items-center justify-center text-center gap-3">
                <span className="material-symbols-outlined text-4xl text-slate-300">bolt</span>
                <p className="text-sm font-semibold text-slate-400">Lancez l'optimisation pour voir les recommandations</p>
                <p className="text-xs text-slate-300">L'algorithme analysera chaque trajet et suggérera la meilleure affectation véhicule</p>
              </div>
            ) : (
              <>
                <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Résultats de l'optimisation</p>
                <div className="grid grid-cols-2 gap-3">
                  <KpiCard label="Économies" value={`${result.total_saving_mad.toLocaleString('fr-MA')} MAD`} icon="savings" highlight={result.total_saving_mad > 0} />
                  <KpiCard label="Réduction" value={`${result.total_saving_pct}%`} icon="trending_down" highlight={result.total_saving_pct > 0} />
                  <KpiCard label="Trajets optimisés" value={`${result.trips_optimized}/${result.total_trips}`} icon="done_all" />
                  <KpiCard label="Amélioration remplissage" value={`+${result.fill_improvement_pct}%`} icon="local_shipping" highlight={result.fill_improvement_pct > 0} />
                </div>
                <div className="bg-blue-50 border border-blue-200 rounded-xl px-4 py-3">
                  <p className="text-xs text-blue-700 font-medium">{result.summary}</p>
                  <div className="flex gap-4 mt-2 text-xs text-blue-600">
                    <span>↓ {result.trips_downsized} réduits</span>
                    <span>↑ {result.trips_upsized} agrandis</span>
                    <span>= {result.trips_kept} inchangés</span>
                  </div>
                </div>

                {/* Trip list */}
                <div className="bg-white rounded-xl border border-slate-100 overflow-hidden">
                  <div className="px-4 py-2.5 border-b border-slate-100 flex items-center justify-between">
                    <p className="text-xs font-bold text-slate-400">Modifications recommandées</p>
                    <label className="flex items-center gap-1.5 text-xs text-slate-500 cursor-pointer">
                      <input type="checkbox" checked={showAll} onChange={(e) => setShowAll(e.target.checked)} className="accent-blue-600" />
                      Tout afficher
                    </label>
                  </div>
                  <div className="overflow-y-auto" style={{ maxHeight: 320 }}>
                    {displayedTrips.length === 0 && (
                      <p className="text-center py-6 text-xs text-slate-400">Aucune modification — tous les trajets sont inchangés</p>
                    )}
                    {displayedTrips.map((t) => {
                      const ac = ACTION_COLOR[t.action] ?? ACTION_COLOR.keep;
                      return (
                        <div key={t.trip_id} className={['border-b border-slate-50 px-4 py-2.5 flex items-center gap-3', ac.bg].join(' ')}>
                          <span className={['material-symbols-outlined text-base', ac.text].join(' ')}>{ac.icon}</span>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="text-xs font-bold text-slate-700">{t.poste}</span>
                              {t.shift && <span className={['text-[10px] px-1.5 py-0.5 rounded-full font-bold', SHIFT_COLOR[t.shift] ?? 'bg-slate-100'].join(' ')}>{t.shift}</span>}
                              {t.aller_retour && <span className={['text-[10px] px-1.5 py-0.5 rounded-full font-bold', t.aller_retour === 'ALLER' ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'].join(' ')}>{t.aller_retour}</span>}
                            </div>
                            <div className="flex items-center gap-2 mt-0.5">
                              <span className={['text-[10px] font-bold px-1.5 rounded', VEHICLE_COLOR[t.current_vehicle ?? ''] ?? 'bg-slate-100 text-slate-600'].join(' ')}>{t.current_vehicle}</span>
                              {t.action !== 'keep' && (
                                <>
                                  <span className="text-[10px] text-slate-400">→</span>
                                  <span className={['text-[10px] font-bold px-1.5 rounded', VEHICLE_COLOR[t.suggested_vehicle ?? ''] ?? 'bg-slate-100 text-slate-600'].join(' ')}>{t.suggested_vehicle}</span>
                                </>
                              )}
                            </div>
                          </div>
                          <div className="text-right shrink-0">
                            <FillBar pct={t.suggested_fill_pct} />
                            {t.saving_mad !== 0 && (
                              <span className={['text-[10px] font-mono', t.saving_mad > 0 ? 'text-emerald-600' : 'text-red-500'].join(' ')}>
                                {t.saving_mad > 0 ? '-' : '+'}{Math.abs(t.saving_mad).toFixed(0)} MAD
                              </span>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {result.can_generate_plan && (
                  <button className="flex items-center gap-2 justify-center bg-emerald-600 text-white rounded-xl py-2.5 text-sm font-semibold hover:bg-emerald-700 transition-colors">
                    <span className="material-symbols-outlined text-base">add_chart</span>
                    Générer un nouveau plan optimisé
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      )}
      </>
      )}
    </div>
  );
}
