import { useEffect, useState, useCallback, useMemo, useRef } from 'react';
import {
  listConfigurationPlans,
  createConfigurationPlan,
  updateConfigurationPlan,
  listConfigurationTransport,
} from '@/api/vehicles';
import type { ConfigurationPlan, ConfigurationTransport } from '@/types/vehicle';

/* ══════════════════════════════════════════════════════════════════════════════
   CONSTANTS
══════════════════════════════════════════════════════════════════════════════ */
const PRESTATAIRE_COLOR: Record<string, string> = {
  STCR:         'bg-blue-100 text-blue-700',
  'S.TOURISME': 'bg-purple-100 text-purple-700',
  MANAVETTE:    'bg-amber-100 text-amber-700',
  CTM:          'bg-orange-100 text-orange-700',
  SOTREG:       'bg-green-100 text-green-700',
};
const VEHICULE_COLOR: Record<string, string> = {
  AUTOCAR: 'bg-sky-100 text-sky-700',
  MINIBUS: 'bg-indigo-100 text-indigo-700',
  MINICAR: 'bg-pink-100 text-pink-700',
};
const AR_COLOR: Record<string, string> = {
  ALLER:  'bg-emerald-50 text-emerald-700',
  RETOUR: 'bg-rose-50 text-rose-700',
};

/* ── Gantt color palettes ─────────────────────────────────────────────────── */
const SHIFT_BAR: Record<string, { fill: string; text: string }> = {
  P1: { fill: '#3b82f6', text: '#fff' },
  P2: { fill: '#f59e0b', text: '#fff' },
  P3: { fill: '#10b981', text: '#fff' },
  N:  { fill: '#64748b', text: '#fff' },
  S:  { fill: '#8b5cf6', text: '#fff' },
};
const PRESTATAIRE_BAR: Record<string, { fill: string; text: string }> = {
  STCR:         { fill: '#3b82f6', text: '#fff' },
  'S.TOURISME': { fill: '#8b5cf6', text: '#fff' },
  MANAVETTE:    { fill: '#f59e0b', text: '#fff' },
  CTM:          { fill: '#f97316', text: '#fff' },
  SOTREG:       { fill: '#10b981', text: '#fff' },
};
const AR_BAR: Record<string, { fill: string; text: string }> = {
  ALLER:  { fill: '#059669', text: '#fff' },
  RETOUR: { fill: '#e11d48', text: '#fff' },
};
const DEFAULT_BAR = { fill: '#94a3b8', text: '#fff' };

/* ── Gantt timeline ───────────────────────────────────────────────────────── */
const G_START = 5 * 60;    // 05:00 in minutes from midnight
const G_END   = 25 * 60;   // 01:00 next day  (25h)
const G_RANGE = G_END - G_START;  // 1200 min
const LANE_H  = 32;               // px per row
const LABEL_W = 200;              // px for label column

const HOUR_TICKS = Array.from({ length: G_RANGE / 60 + 1 }, (_, i) => G_START + i * 60);
const HALF_TICKS = Array.from({ length: G_RANGE / 30 + 1 }, (_, i) => G_START + i * 30);

function fmtTick(min: number): string {
  return `${String(Math.floor(min / 60) % 24).padStart(2, '0')}:00`;
}

function parseMin(t: string | null): number | null {
  if (!t) return null;
  const m = t.match(/(\d{1,2}):(\d{2})/);
  if (!m) return null;
  const total = parseInt(m[1]) * 60 + parseInt(m[2]);
  return total < G_START ? total + 1440 : total;
}

function gPct(min: number): number {
  return ((min - G_START) / G_RANGE) * 100;
}

/* ══════════════════════════════════════════════════════════════════════════════
   SMALL REUSABLE COMPONENTS
══════════════════════════════════════════════════════════════════════════════ */
const selectCls =
  'bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 outline-none focus:ring-2 focus:ring-blue-100 appearance-none min-w-[130px]';

function Badge({ text, cls }: { text: string; cls?: string }) {
  return (
    <span className={['inline-block rounded-full px-2 py-0.5 text-[11px] font-semibold whitespace-nowrap', cls ?? 'bg-slate-100 text-slate-600'].join(' ')}>
      {text}
    </span>
  );
}
function fmtDuree(min: number | null): string {
  if (min == null) return '—';
  return `${Math.floor(min / 60)}h${String(min % 60).padStart(2, '0')}`;
}

/* ── PlanCard ─────────────────────────────────────────────────────────────── */
function PlanCard({ plan, selected, onClick }: { plan: ConfigurationPlan; selected: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={[
        'flex flex-col gap-1 rounded-xl border px-4 py-3 text-left transition-all min-w-[180px] shrink-0',
        selected ? 'border-blue-500 bg-blue-50 shadow-sm' : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50',
      ].join(' ')}
    >
      <div className="flex items-center justify-between gap-2">
        <span className={['text-sm font-semibold truncate max-w-[140px]', selected ? 'text-blue-700' : 'text-slate-800'].join(' ')}>
          {plan.name}
        </span>
        {plan.is_current && (
          <span className="shrink-0 rounded-full bg-green-100 text-green-700 text-[10px] font-bold px-2 py-0.5">actuelle</span>
        )}
      </div>
      <span className="text-[11px] text-slate-400 font-mono">{plan.row_count} lignes</span>
      {plan.source && <span className="text-[10px] text-slate-400 capitalize">{plan.source}</span>}
    </button>
  );
}

/* ── NewPlanModal ─────────────────────────────────────────────────────────── */
function NewPlanModal({ onClose, onCreated }: { onClose: () => void; onCreated: (p: ConfigurationPlan) => void }) {
  const [name, setName] = useState('');
  const [desc, setDesc] = useState('');
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSaving(true); setErr(null);
    try { onCreated(await createConfigurationPlan({ name: name.trim(), description: desc || null })); }
    catch { setErr('Erreur lors de la création'); }
    finally { setSaving(false); }
  };
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-xl p-6 w-full max-w-md flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-800">Nouveau plan</h2>
          <button type="button" onClick={onClose} className="text-slate-400 hover:text-slate-700"><span className="material-symbols-outlined">close</span></button>
        </div>
        {err && <div className="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{err}</div>}
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-slate-500">Nom *</label>
          <input required autoFocus value={name} onChange={(e) => setName(e.target.value)}
            className="border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-200" placeholder="Ex: Configuration Q2-2025" />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-slate-500">Description</label>
          <textarea rows={2} value={desc} onChange={(e) => setDesc(e.target.value)}
            className="border border-slate-200 rounded-lg px-3 py-2 text-sm resize-none outline-none focus:ring-2 focus:ring-blue-200" placeholder="Description optionnelle…" />
        </div>
        <div className="flex gap-3 pt-1">
          <button type="submit" disabled={saving} className="flex-1 bg-blue-600 text-white rounded-lg py-2 text-sm font-semibold hover:bg-blue-700 disabled:opacity-60">{saving ? 'Création…' : 'Créer'}</button>
          <button type="button" onClick={onClose} className="flex-1 bg-slate-100 text-slate-700 rounded-lg py-2 text-sm font-semibold hover:bg-slate-200">Annuler</button>
        </div>
      </form>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════════════════
   GANTT VIEW
══════════════════════════════════════════════════════════════════════════════ */
type ColorBy = 'shift' | 'prestataire' | 'aller_retour';
type GroupBy = 'conducteur' | 'poste' | 'mle_vehicule';

interface GanttLane {
  key: string;
  label: string;
  sublabel: string;
  trips: ConfigurationTransport[];
}

function barColor(row: ConfigurationTransport, colorBy: ColorBy): { fill: string; text: string } {
  if (colorBy === 'shift')       return SHIFT_BAR[row.shift ?? '']       ?? DEFAULT_BAR;
  if (colorBy === 'prestataire') return PRESTATAIRE_BAR[row.prestataire ?? ''] ?? DEFAULT_BAR;
  if (colorBy === 'aller_retour') return AR_BAR[row.aller_retour ?? '']  ?? DEFAULT_BAR;
  return DEFAULT_BAR;
}

interface TooltipState { row: ConfigurationTransport; x: number; y: number }

function GanttTooltip({ state }: { state: TooltipState }) {
  const { row, x, y } = state;
  const viewW = window.innerWidth;
  const left = x + 16 + 280 > viewW ? x - 16 - 280 : x + 16;
  return (
    <div
      className="fixed z-50 bg-slate-900 text-white rounded-xl shadow-2xl px-4 py-3 text-xs pointer-events-none min-w-[240px] max-w-[280px]"
      style={{ top: y - 10, left }}
    >
      <p className="font-bold text-sm mb-2 text-white">{row.conducteur ?? '—'}</p>
      <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-slate-300">
        <span className="text-slate-400">Poste</span><span className="text-white font-mono">{row.poste}</span>
        <span className="text-slate-400">Préstataire</span><span className="text-white">{row.prestataire}</span>
        <span className="text-slate-400">Véhicule</span><span className="text-white font-mono">{row.mle_vehicule}</span>
        <span className="text-slate-400">Type</span><span className="text-white">{row.type_vehicule} · {row.type_moteur}</span>
        <span className="text-slate-400">Shift</span><span className="text-white font-bold">{row.shift}</span>
        <span className="text-slate-400">A/R</span><span className={row.aller_retour === 'ALLER' ? 'text-emerald-400' : 'text-rose-400'}>{row.aller_retour}</span>
        <span className="text-slate-400">Départ</span><span className="text-white font-mono">{row.heure_depart}</span>
        <span className="text-slate-400">Arrivée</span><span className="text-white font-mono">{row.heure_arrivee}</span>
        <span className="text-slate-400">De</span><span className="text-white truncate">{row.point_depart}</span>
        <span className="text-slate-400">À</span><span className="text-white truncate">{row.point_arrivee}</span>
        <span className="text-slate-400">Circuit</span><span className="text-white font-mono text-[10px] truncate">{row.arrets_circuit}</span>
        <span className="text-slate-400">Durée</span><span className="text-white">{fmtDuree(row.duree_trajet_min)}</span>
        <span className="text-slate-400">KM</span><span className="text-white">{row.km} km</span>
        <span className="text-slate-400">T. KM</span><span className="text-white font-bold">{row.t_km} km</span>
      </div>
    </div>
  );
}

function GanttView({
  rows, colorBy, groupBy, loading,
}: {
  rows: ConfigurationTransport[];
  colorBy: ColorBy;
  groupBy: GroupBy;
  loading: boolean;
}) {
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  /* ── Build lanes ────────────────────────────────────────────────────────── */
  const lanes = useMemo((): GanttLane[] => {
    const map = new Map<string, GanttLane>();
    for (const row of rows) {
      let key = '';
      let label = '';
      let sublabel = '';
      if (groupBy === 'conducteur') {
        key = `${row.conducteur ?? '?'}__${row.mle_vehicule ?? '?'}`;
        label = row.conducteur ?? '—';
        sublabel = `${row.poste ?? ''} · ${row.mle_vehicule ?? ''}`;
      } else if (groupBy === 'poste') {
        key = row.poste ?? '?';
        label = row.poste ?? '—';
        sublabel = `${row.conducteur ?? ''} · ${row.mle_vehicule ?? ''}`;
      } else {
        key = row.mle_vehicule ?? '?';
        label = row.mle_vehicule ?? '—';
        sublabel = `${row.conducteur ?? ''} · ${row.poste ?? ''}`;
      }
      if (!map.has(key)) map.set(key, { key, label, sublabel, trips: [] });
      map.get(key)!.trips.push(row);
    }
    return Array.from(map.values()).sort((a, b) => a.label.localeCompare(b.label));
  }, [rows, groupBy]);

  const totalH = lanes.length * LANE_H + 40; // 40 = header

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48 text-slate-400">
        <span className="material-symbols-outlined text-4xl animate-spin mr-3">progress_activity</span>
        Chargement du Gantt…
      </div>
    );
  }

  if (lanes.length === 0) {
    return <div className="flex items-center justify-center h-40 text-slate-400 text-sm">Aucune donnée pour ces filtres</div>;
  }

  return (
    <div className="overflow-auto rounded-xl border border-slate-200 bg-white shadow-sm" ref={containerRef}
      style={{ maxHeight: 'calc(100vh - 18rem)' }}>
      <div style={{ minWidth: LABEL_W + 900, width: '100%' }}>

        {/* ── Time header ─────────────────────────────────────────────────── */}
        <div className="sticky top-0 z-20 flex" style={{ height: 40 }}>
          {/* Label column header */}
          <div
            className="sticky left-0 z-30 bg-slate-700 text-white flex items-end px-3 pb-1 text-xs font-bold border-r border-slate-600 shrink-0"
            style={{ width: LABEL_W }}
          >
            {groupBy === 'conducteur' ? 'Conducteur' : groupBy === 'poste' ? 'Poste' : 'Véhicule'}
          </div>
          {/* Time axis */}
          <div className="relative flex-1 bg-slate-700 border-b border-slate-600 overflow-hidden">
            {/* half-hour gridlines labels */}
            {HOUR_TICKS.map((min) => (
              <div
                key={min}
                className="absolute top-0 bottom-0 border-l border-slate-500"
                style={{ left: `${gPct(min)}%` }}
              >
                <span className="absolute bottom-1 left-1 text-[10px] font-mono text-slate-300 whitespace-nowrap">
                  {fmtTick(min)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* ── Lanes ─────────────────────────────────────────────────────────── */}
        {lanes.map((lane, li) => (
          <div
            key={lane.key}
            className="flex border-b border-slate-100 group"
            style={{ height: LANE_H }}
          >
            {/* Label cell */}
            <div
              className={[
                'sticky left-0 z-10 flex flex-col justify-center px-3 border-r border-slate-200 shrink-0',
                li % 2 === 0 ? 'bg-white group-hover:bg-blue-50/60' : 'bg-slate-50/70 group-hover:bg-blue-50/60',
              ].join(' ')}
              style={{ width: LABEL_W }}
            >
              <span className="text-xs font-semibold text-slate-700 truncate leading-tight">{lane.label}</span>
              <span className="text-[10px] text-slate-400 truncate leading-tight">{lane.sublabel}</span>
            </div>

            {/* Timeline cell */}
            <div
              className={['relative flex-1 overflow-hidden', li % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'].join(' ')}
            >
              {/* Half-hour gridlines */}
              {HALF_TICKS.map((min) => (
                <div
                  key={min}
                  className={['absolute inset-y-0 border-l', min % 60 === 0 ? 'border-slate-200' : 'border-slate-100'].join(' ')}
                  style={{ left: `${gPct(min)}%` }}
                />
              ))}

              {/* Trip bars */}
              {lane.trips.map((trip) => {
                const start = parseMin(trip.heure_depart);
                const end = parseMin(trip.heure_arrivee);
                if (start == null || end == null || end <= start) return null;
                const leftPct = gPct(start);
                const widthPct = gPct(end) - leftPct;
                if (leftPct < 0 || leftPct > 100) return null;
                const { fill, text } = barColor(trip, colorBy);
                const isRetour = trip.aller_retour === 'RETOUR';
                return (
                  <div
                    key={trip.id}
                    className="absolute inset-y-[4px] rounded-sm cursor-pointer transition-opacity hover:opacity-80 flex items-center overflow-hidden"
                    style={{
                      left: `${Math.max(0, leftPct)}%`,
                      width: `${Math.min(widthPct, 100 - leftPct)}%`,
                      backgroundColor: fill,
                      backgroundImage: isRetour
                        ? `repeating-linear-gradient(45deg, transparent, transparent 3px, rgba(255,255,255,0.2) 3px, rgba(255,255,255,0.2) 6px)`
                        : 'none',
                      minWidth: 4,
                    }}
                    onMouseEnter={(e) => setTooltip({ row: trip, x: e.clientX, y: e.clientY })}
                    onMouseMove={(e) => setTooltip({ row: trip, x: e.clientX, y: e.clientY })}
                    onMouseLeave={() => setTooltip(null)}
                  >
                    <span
                      className="px-1 text-[9px] font-bold truncate leading-none"
                      style={{ color: text }}
                    >
                      {trip.shift}{trip.aller_retour === 'RETOUR' ? '↩' : '→'}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        ))}

        {/* bottom padding */}
        <div style={{ height: 8 }} />
      </div>

      {/* Tooltip portal */}
      {tooltip && <GanttTooltip state={tooltip} />}
    </div>
  );
}

/* ── Legend ─────────────────────────────────────────────────────────────── */
function GanttLegend({ colorBy }: { colorBy: ColorBy }) {
  const entries = colorBy === 'shift'
    ? Object.entries(SHIFT_BAR).map(([k, v]) => ({ label: `Shift ${k}`, fill: v.fill }))
    : colorBy === 'prestataire'
    ? Object.entries(PRESTATAIRE_BAR).map(([k, v]) => ({ label: k, fill: v.fill }))
    : Object.entries(AR_BAR).map(([k, v]) => ({ label: k, fill: v.fill }));

  return (
    <div className="flex items-center flex-wrap gap-3 text-xs text-slate-600">
      {entries.map((e) => (
        <div key={e.label} className="flex items-center gap-1.5">
          <span className="inline-block w-3 h-3 rounded-sm" style={{ backgroundColor: e.fill }} />
          {e.label}
        </div>
      ))}
      <div className="flex items-center gap-1.5 ml-2">
        <span className="inline-block w-3 h-3 rounded-sm" style={{
          backgroundColor: '#3b82f6',
          backgroundImage: 'repeating-linear-gradient(45deg, transparent, transparent 2px, rgba(255,255,255,0.4) 2px, rgba(255,255,255,0.4) 4px)'
        }} />
        Retour (strié)
      </div>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════════════════
   MAIN PAGE
══════════════════════════════════════════════════════════════════════════════ */
const PAGE_SIZE = 100;

export function ConfigurationTransportPage() {
  const [plans, setPlans] = useState<ConfigurationPlan[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<ConfigurationPlan | null>(null);
  const [plansLoading, setPlansLoading] = useState(true);

  /* ── view mode ────────────────────────────────────────────────────────── */
  const [viewMode, setViewMode] = useState<'table' | 'gantt'>('table');
  const [colorBy, setColorBy] = useState<ColorBy>('shift');
  const [groupBy, setGroupBy] = useState<GroupBy>('conducteur');

  /* ── table state ──────────────────────────────────────────────────────── */
  const [rows, setRows] = useState<ConfigurationTransport[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [rowsLoading, setRowsLoading] = useState(false);

  /* ── gantt state ──────────────────────────────────────────────────────── */
  const [ganttRows, setGanttRows] = useState<ConfigurationTransport[]>([]);
  const [ganttLoading, setGanttLoading] = useState(false);

  /* ── shared filters ───────────────────────────────────────────────────── */
  const [filterPrestataire, setFilterPrestataire] = useState('');
  const [filterSecteur, setFilterSecteur] = useState('');
  const [filterShift, setFilterShift] = useState('');
  const [filterAR, setFilterAR] = useState('');
  const [filterVehicule, setFilterVehicule] = useState('');

  const [showNewPlan, setShowNewPlan] = useState(false);

  /* ── load plans ───────────────────────────────────────────────────────── */
  const loadPlans = useCallback(async () => {
    setPlansLoading(true);
    try {
      const res = await listConfigurationPlans({ page_size: 50 });
      const items = res.items ?? [];
      setPlans(items);
      const current = items.find((p) => p.is_current) ?? items[0] ?? null;
      setSelectedPlan((prev) => prev ?? current);
    } finally {
      setPlansLoading(false);
    }
  }, []);
  useEffect(() => { loadPlans(); }, [loadPlans]);

  /* ── build filter params ──────────────────────────────────────────────── */
  const filterParams = useCallback((extra: Record<string, unknown> = {}): Record<string, unknown> => {
    const p: Record<string, unknown> = {};
    if (filterPrestataire) p.prestataire = filterPrestataire;
    if (filterSecteur)     p.secteur = filterSecteur;
    if (filterShift)       p.shift = filterShift;
    if (filterAR)          p.aller_retour = filterAR;
    return { ...p, ...extra };
  }, [filterPrestataire, filterSecteur, filterShift, filterAR]);

  /* ── load table rows ──────────────────────────────────────────────────── */
  const loadRows = useCallback(async () => {
    if (!selectedPlan || viewMode !== 'table') return;
    setRowsLoading(true);
    try {
      const res = await listConfigurationTransport({
        plan_id: selectedPlan.id, page, page_size: PAGE_SIZE,
        ...filterParams(),
      });
      setRows(res.items ?? []);
      setTotal(res.total ?? 0);
    } finally {
      setRowsLoading(false);
    }
  }, [selectedPlan, page, filterParams, viewMode]);
  useEffect(() => { loadRows(); }, [loadRows]);

  /* ── load gantt rows (all at once) ────────────────────────────────────── */
  const loadGantt = useCallback(async () => {
    if (!selectedPlan || viewMode !== 'gantt') return;
    setGanttLoading(true);
    try {
      const res = await listConfigurationTransport({
        plan_id: selectedPlan.id, page: 1, page_size: 600,
        ...filterParams(),
      });
      setGanttRows(res.items ?? []);
    } finally {
      setGanttLoading(false);
    }
  }, [selectedPlan, filterParams, viewMode]);
  useEffect(() => { loadGantt(); }, [loadGantt]);

  const resetPage = () => setPage(1);
  const clearFilters = () => { setFilterPrestataire(''); setFilterSecteur(''); setFilterShift(''); setFilterAR(''); setFilterVehicule(''); resetPage(); };

  /* ── client-side vehicule filter (table only) ─────────────────────────── */
  const displayed = useMemo(
    () => filterVehicule ? rows.filter((r) => r.type_vehicule === filterVehicule) : rows,
    [rows, filterVehicule],
  );
  const ganttDisplayed = useMemo(
    () => filterVehicule ? ganttRows.filter((r) => r.type_vehicule === filterVehicule) : ganttRows,
    [ganttRows, filterVehicule],
  );

  /* ── stats ────────────────────────────────────────────────────────────── */
  const statsRows = viewMode === 'gantt' ? ganttDisplayed : rows;
  const totalKm   = useMemo(() => statsRows.reduce((s, r) => s + (r.t_km ?? 0), 0), [statsRows]);
  const uniquePostes = useMemo(() => new Set(statsRows.map((r) => r.poste)).size, [statsRows]);
  const uniqueVehs   = useMemo(() => new Set(statsRows.map((r) => r.mle_vehicule).filter(Boolean)).size, [statsRows]);

  const markCurrent = async (plan: ConfigurationPlan) => {
    await updateConfigurationPlan(plan.id, { is_current: true });
    await loadPlans();
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="flex flex-col gap-5">
      {/* ── PAGE HEADER ────────────────────────────────────────────────── */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <span className="material-symbols-outlined text-blue-600 text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>
              settings_applications
            </span>
            Configuration Transport-Véhicule
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            {selectedPlan ? `${total > 0 ? total : ganttRows.length} lignes — Plan : ${selectedPlan.name}` : 'Sélectionnez un plan'}
          </p>
        </div>
        <button onClick={() => setShowNewPlan(true)}
          className="flex items-center gap-2 bg-blue-600 text-white rounded-xl px-4 py-2.5 text-sm font-semibold hover:bg-blue-700 transition-colors shrink-0">
          <span className="material-symbols-outlined text-base">add</span>
          Nouveau plan
        </button>
      </div>

      {/* ── PLANS CAROUSEL ─────────────────────────────────────────────── */}
      {plansLoading ? (
        <div className="h-20 bg-slate-100 animate-pulse rounded-xl" />
      ) : (
        <div className="flex items-center gap-3 overflow-x-auto pb-1">
          {plans.map((plan) => (
            <PlanCard
              key={plan.id} plan={plan}
              selected={selectedPlan?.id === plan.id}
              onClick={() => { setSelectedPlan(plan); resetPage(); }}
            />
          ))}
          {plans.length === 0 && <p className="text-sm text-slate-400 italic">Aucun plan — créez-en un ci-dessus</p>}
        </div>
      )}

      {selectedPlan && (
        <>
          {/* ── PLAN META BAR ──────────────────────────────────────────── */}
          <div className="flex items-center gap-4 bg-blue-50 border border-blue-100 rounded-xl px-4 py-3">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-blue-800 truncate">{selectedPlan.name}</p>
              {selectedPlan.description && <p className="text-xs text-blue-600 truncate">{selectedPlan.description}</p>}
            </div>
            <div className="flex items-center gap-4 shrink-0 text-xs text-blue-700 flex-wrap">
              <span className="flex items-center gap-1"><span className="material-symbols-outlined text-sm">route</span><strong>{uniquePostes}</strong> postes</span>
              <span className="flex items-center gap-1"><span className="material-symbols-outlined text-sm">directions_car</span><strong>{uniqueVehs}</strong> véhicules</span>
              <span className="flex items-center gap-1"><span className="material-symbols-outlined text-sm">straighten</span><strong>{totalKm.toLocaleString('fr-MA', { maximumFractionDigits: 0 })}</strong> km</span>
              {!selectedPlan.is_current && (
                <button onClick={() => markCurrent(selectedPlan)} className="ml-2 bg-blue-600 text-white rounded-lg px-3 py-1 text-xs font-semibold hover:bg-blue-700">
                  Marquer comme actuelle
                </button>
              )}
            </div>
          </div>

          {/* ── TOOLBAR: filters + view toggle ─────────────────────────── */}
          <div className="flex flex-wrap items-center gap-3 bg-white border border-slate-100 rounded-xl px-4 py-3">
            {/* View toggle */}
            <div className="flex rounded-lg overflow-hidden border border-slate-200 shrink-0 mr-2">
              <button
                onClick={() => setViewMode('table')}
                className={['flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold transition-colors',
                  viewMode === 'table' ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'].join(' ')}
              >
                <span className="material-symbols-outlined text-sm leading-none">table_rows</span>
                Tableau
              </button>
              <button
                onClick={() => setViewMode('gantt')}
                className={['flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold transition-colors border-l border-slate-200',
                  viewMode === 'gantt' ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'].join(' ')}
              >
                <span className="material-symbols-outlined text-sm leading-none">view_timeline</span>
                Gantt
              </button>
            </div>

            {/* Filters */}
            <select value={filterPrestataire} onChange={(e) => { setFilterPrestataire(e.target.value); resetPage(); }} className={selectCls}>
              <option value="">Tous les prestataires</option>
              {['STCR', 'S.TOURISME', 'MANAVETTE', 'CTM', 'SOTREG'].map((p) => <option key={p}>{p}</option>)}
            </select>
            <select value={filterSecteur} onChange={(e) => { setFilterSecteur(e.target.value); resetPage(); }} className={selectCls}>
              <option value="">Tous les secteurs</option>
              {['KHOURIBGA', 'OUEDZEM', 'BOULANOIR', 'BOUJNIBA', 'HATTANE', 'FQUIH BEN SALEH'].map((s) => <option key={s}>{s}</option>)}
            </select>
            <select value={filterShift} onChange={(e) => { setFilterShift(e.target.value); resetPage(); }} className={selectCls}>
              <option value="">Tous les shifts</option>
              {['P1', 'P2', 'P3', 'N', 'S'].map((s) => <option key={s} value={s}>Shift {s}</option>)}
            </select>
            <select value={filterAR} onChange={(e) => { setFilterAR(e.target.value); resetPage(); }} className={selectCls}>
              <option value="">Aller & Retour</option>
              <option value="ALLER">Aller</option>
              <option value="RETOUR">Retour</option>
            </select>
            <select value={filterVehicule} onChange={(e) => setFilterVehicule(e.target.value)} className={selectCls}>
              <option value="">Tous types</option>
              {['AUTOCAR', 'MINIBUS', 'MINICAR'].map((v) => <option key={v}>{v}</option>)}
            </select>

            {/* Gantt-specific controls */}
            {viewMode === 'gantt' && (
              <>
                <div className="w-px h-5 bg-slate-200" />
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400 font-medium">Grouper</span>
                  <select value={groupBy} onChange={(e) => setGroupBy(e.target.value as GroupBy)} className={selectCls}>
                    <option value="conducteur">Conducteur</option>
                    <option value="poste">Poste</option>
                    <option value="mle_vehicule">Véhicule</option>
                  </select>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400 font-medium">Couleur</span>
                  <select value={colorBy} onChange={(e) => setColorBy(e.target.value as ColorBy)} className={selectCls}>
                    <option value="shift">Par shift</option>
                    <option value="prestataire">Par prestataire</option>
                    <option value="aller_retour">Aller / Retour</option>
                  </select>
                </div>
              </>
            )}

            {(filterPrestataire || filterSecteur || filterShift || filterAR || filterVehicule) && (
              <button onClick={clearFilters} className="text-xs text-slate-500 hover:text-slate-800 flex items-center gap-1">
                <span className="material-symbols-outlined text-sm">close</span>Effacer
              </button>
            )}
            <span className="ml-auto text-xs text-slate-400">
              {viewMode === 'table'
                ? (rowsLoading ? 'Chargement…' : `${displayed.length} / ${total} lignes`)
                : (ganttLoading ? 'Chargement…' : `${ganttDisplayed.length} lignes`)}
            </span>
          </div>

          {/* ══ TABLE VIEW ══════════════════════════════════════════════════ */}
          {viewMode === 'table' && (
            <>
              <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
                <table className="w-full text-xs min-w-[1200px]">
                  <thead>
                    <tr className="border-b border-slate-200 bg-slate-50">
                      {['Conducteur', 'Poste', 'Prestataire', 'Mle Veh.', 'Type', 'Moteur',
                        'Secteur', 'Entité', 'A/R', 'Shift', 'Départ', 'De', 'À', 'Arrivée',
                        'Circuit', 'Durée', 'KM', 'ROT', 'T KM'].map((h) => (
                        <th key={h} className="px-3 py-2.5 text-left font-bold text-slate-500 whitespace-nowrap">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {rowsLoading && (
                      <tr><td colSpan={19} className="text-center py-12 text-slate-400">
                        <span className="material-symbols-outlined text-3xl animate-spin">progress_activity</span>
                      </td></tr>
                    )}
                    {!rowsLoading && displayed.length === 0 && (
                      <tr><td colSpan={19} className="text-center py-12 text-slate-400 text-sm">Aucune ligne pour ces filtres</td></tr>
                    )}
                    {displayed.map((row, i) => (
                      <tr key={row.id} className={['border-b border-slate-100 hover:bg-blue-50/30 transition-colors', i % 2 ? 'bg-slate-50/40' : ''].join(' ')}>
                        <td className="px-3 py-2 font-medium text-slate-700 whitespace-nowrap">{row.conducteur ?? '—'}</td>
                        <td className="px-3 py-2 font-mono text-slate-600">{row.poste ?? '—'}</td>
                        <td className="px-3 py-2">{row.prestataire ? <Badge text={row.prestataire} cls={PRESTATAIRE_COLOR[row.prestataire]} /> : '—'}</td>
                        <td className="px-3 py-2 font-mono text-slate-500 text-[11px]">{row.mle_vehicule ?? '—'}</td>
                        <td className="px-3 py-2">{row.type_vehicule ? <Badge text={row.type_vehicule} cls={VEHICULE_COLOR[row.type_vehicule]} /> : '—'}</td>
                        <td className="px-3 py-2 text-slate-500">{row.type_moteur ?? '—'}</td>
                        <td className="px-3 py-2 text-slate-600">{row.secteur ?? '—'}</td>
                        <td className="px-3 py-2 text-slate-600 max-w-[120px] truncate" title={row.entite ?? ''}>{row.entite ?? '—'}</td>
                        <td className="px-3 py-2">{row.aller_retour ? <Badge text={row.aller_retour} cls={AR_COLOR[row.aller_retour]} /> : '—'}</td>
                        <td className="px-3 py-2 font-mono text-slate-600">{row.shift ?? '—'}</td>
                        <td className="px-3 py-2 font-mono text-slate-600 whitespace-nowrap">{row.heure_depart ?? '—'}</td>
                        <td className="px-3 py-2 text-slate-600 max-w-[100px] truncate" title={row.point_depart ?? ''}>{row.point_depart ?? '—'}</td>
                        <td className="px-3 py-2 text-slate-600 max-w-[100px] truncate" title={row.point_arrivee ?? ''}>{row.point_arrivee ?? '—'}</td>
                        <td className="px-3 py-2 font-mono text-slate-600 whitespace-nowrap">{row.heure_arrivee ?? '—'}</td>
                        <td className="px-3 py-2 text-slate-500 max-w-[120px] truncate font-mono text-[10px]" title={row.arrets_circuit ?? ''}>{row.arrets_circuit ?? '—'}</td>
                        <td className="px-3 py-2 font-mono text-slate-600">{fmtDuree(row.duree_trajet_min)}</td>
                        <td className="px-3 py-2 text-right font-mono text-slate-700">{row.km != null ? Number(row.km).toLocaleString('fr-MA') : '—'}</td>
                        <td className="px-3 py-2 text-right font-mono text-slate-600">{row.rot != null ? Number(row.rot) : '—'}</td>
                        <td className="px-3 py-2 text-right font-semibold font-mono text-slate-800">{row.t_km != null ? Number(row.t_km).toLocaleString('fr-MA') : '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {totalPages > 1 && (
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span>Page {page} / {totalPages} — {total} lignes</span>
                  <div className="flex items-center gap-2">
                    <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}
                      className="px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-40">← Préc.</button>
                    <button onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages}
                      className="px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-40">Suiv. →</button>
                  </div>
                </div>
              )}
            </>
          )}

          {/* ══ GANTT VIEW ══════════════════════════════════════════════════ */}
          {viewMode === 'gantt' && (
            <div className="flex flex-col gap-3">
              {/* Legend */}
              <div className="flex items-center justify-between flex-wrap gap-2">
                <GanttLegend colorBy={colorBy} />
                <span className="text-xs text-slate-400">
                  {ganttDisplayed.length} trajets · {new Set(ganttDisplayed.map((r) =>
                    groupBy === 'conducteur' ? `${r.conducteur}__${r.mle_vehicule}` :
                    groupBy === 'poste' ? r.poste : r.mle_vehicule
                  )).size} lignes Gantt
                </span>
              </div>

              <GanttView
                rows={ganttDisplayed}
                colorBy={colorBy}
                groupBy={groupBy}
                loading={ganttLoading}
              />
            </div>
          )}
        </>
      )}

      {/* ── NEW PLAN MODAL ─────────────────────────────────────────────── */}
      {showNewPlan && (
        <NewPlanModal
          onClose={() => setShowNewPlan(false)}
          onCreated={(plan) => { setPlans((prev) => [plan, ...prev]); setSelectedPlan(plan); setShowNewPlan(false); }}
        />
      )}
    </div>
  );
}
