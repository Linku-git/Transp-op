import { useEffect, useState, useCallback, useMemo } from 'react';
import {
  listConfigurationPlans,
  createConfigurationPlan,
  updateConfigurationPlan,
  listConfigurationTransport,
} from '@/api/vehicles';
import type { ConfigurationPlan, ConfigurationTransport } from '@/types/vehicle';

/* ── constants ────────────────────────────────────────────────────────────── */
const PRESTATAIRE_COLOR: Record<string, string> = {
  STCR:       'bg-blue-100 text-blue-700',
  'S.TOURISME': 'bg-purple-100 text-purple-700',
  MANAVETTE:  'bg-amber-100 text-amber-700',
  CTM:        'bg-orange-100 text-orange-700',
  SOTREG:     'bg-green-100 text-green-700',
};

const VEHICULE_COLOR: Record<string, string> = {
  AUTOCAR:  'bg-sky-100 text-sky-700',
  MINIBUS:  'bg-indigo-100 text-indigo-700',
  MINICAR:  'bg-pink-100 text-pink-700',
};

const AR_COLOR: Record<string, string> = {
  ALLER:  'bg-emerald-50 text-emerald-700',
  RETOUR: 'bg-rose-50 text-rose-700',
};

const selectCls =
  'bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 outline-none focus:ring-2 focus:ring-primary/20 appearance-none min-w-[130px]';

/* ── helpers ──────────────────────────────────────────────────────────────── */
function Badge({ text, cls }: { text: string; cls?: string }) {
  return (
    <span
      className={[
        'inline-block rounded-full px-2 py-0.5 text-[11px] font-semibold whitespace-nowrap',
        cls ?? 'bg-slate-100 text-slate-600',
      ].join(' ')}
    >
      {text}
    </span>
  );
}

function fmtDuree(min: number | null): string {
  if (min == null) return '—';
  return `${Math.floor(min / 60)}h${String(min % 60).padStart(2, '0')}`;
}

/* ── PlanCard ─────────────────────────────────────────────────────────────── */
function PlanCard({
  plan, selected, onClick,
}: {
  plan: ConfigurationPlan;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={[
        'flex flex-col gap-1 rounded-xl border px-4 py-3 text-left transition-all min-w-[180px]',
        selected
          ? 'border-blue-500 bg-blue-50 shadow-sm'
          : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50',
      ].join(' ')}
    >
      <div className="flex items-center justify-between gap-2">
        <span className={['text-sm font-semibold truncate max-w-[140px]', selected ? 'text-blue-700' : 'text-slate-800'].join(' ')}>
          {plan.name}
        </span>
        {plan.is_current && (
          <span className="shrink-0 rounded-full bg-green-100 text-green-700 text-[10px] font-bold px-2 py-0.5">
            actuelle
          </span>
        )}
      </div>
      <span className="text-[11px] text-slate-400 font-mono">{plan.row_count} lignes</span>
      {plan.source && (
        <span className="text-[10px] text-slate-400 capitalize">{plan.source}</span>
      )}
    </button>
  );
}

/* ── NewPlanModal ─────────────────────────────────────────────────────────── */
function NewPlanModal({
  onClose, onCreated,
}: {
  onClose: () => void;
  onCreated: (plan: ConfigurationPlan) => void;
}) {
  const [name, setName] = useState('');
  const [desc, setDesc] = useState('');
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSaving(true);
    setErr(null);
    try {
      const p = await createConfigurationPlan({ name: name.trim(), description: desc || null });
      onCreated(p);
    } catch {
      setErr('Erreur lors de la création');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-xl p-6 w-full max-w-md flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-800">Nouveau plan de configuration</h2>
          <button type="button" onClick={onClose} className="text-slate-400 hover:text-slate-700">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>
        {err && <div className="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{err}</div>}
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-slate-500">Nom *</label>
          <input
            required autoFocus value={name} onChange={(e) => setName(e.target.value)}
            className="border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-200"
            placeholder="Ex: Configuration Q2-2025"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-slate-500">Description</label>
          <textarea rows={2} value={desc} onChange={(e) => setDesc(e.target.value)}
            className="border border-slate-200 rounded-lg px-3 py-2 text-sm resize-none outline-none focus:ring-2 focus:ring-blue-200"
            placeholder="Description optionnelle…"
          />
        </div>
        <div className="flex gap-3 pt-1">
          <button type="submit" disabled={saving}
            className="flex-1 bg-blue-600 text-white rounded-lg py-2 text-sm font-semibold hover:bg-blue-700 disabled:opacity-60">
            {saving ? 'Création…' : 'Créer le plan'}
          </button>
          <button type="button" onClick={onClose}
            className="flex-1 bg-slate-100 text-slate-700 rounded-lg py-2 text-sm font-semibold hover:bg-slate-200">
            Annuler
          </button>
        </div>
      </form>
    </div>
  );
}

/* ── Main page ────────────────────────────────────────────────────────────── */
const PAGE_SIZE = 100;

export function ConfigurationTransportPage() {
  const [plans, setPlans] = useState<ConfigurationPlan[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<ConfigurationPlan | null>(null);
  const [plansLoading, setPlansLoading] = useState(true);

  const [rows, setRows] = useState<ConfigurationTransport[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [rowsLoading, setRowsLoading] = useState(false);

  const [filterPrestataire, setFilterPrestataire] = useState('');
  const [filterSecteur, setFilterSecteur] = useState('');
  const [filterShift, setFilterShift] = useState('');
  const [filterAR, setFilterAR] = useState('');
  const [filterVehicule, setFilterVehicule] = useState('');

  const [showNewPlan, setShowNewPlan] = useState(false);

  /* ── load plans ─────────────────────────────────────────────────────── */
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

  /* ── load rows ──────────────────────────────────────────────────────── */
  const loadRows = useCallback(async () => {
    if (!selectedPlan) return;
    setRowsLoading(true);
    try {
      const params: Record<string, unknown> = {
        plan_id: selectedPlan.id,
        page,
        page_size: PAGE_SIZE,
      };
      if (filterPrestataire) params.prestataire = filterPrestataire;
      if (filterSecteur) params.secteur = filterSecteur;
      if (filterShift) params.shift = filterShift;
      if (filterAR) params.aller_retour = filterAR;
      const res = await listConfigurationTransport(params);
      setRows(res.items ?? []);
      setTotal(res.total ?? 0);
    } finally {
      setRowsLoading(false);
    }
  }, [selectedPlan, page, filterPrestataire, filterSecteur, filterShift, filterAR]);

  useEffect(() => { loadRows(); }, [loadRows]);

  const resetPage = () => setPage(1);

  /* ── filtered rows (client-side vehicule filter) ─────────────────────── */
  const displayed = useMemo(
    () => filterVehicule ? rows.filter((r) => r.type_vehicule === filterVehicule) : rows,
    [rows, filterVehicule],
  );

  /* ── stats ─────────────────────────────────────────────────────────────── */
  const totalKm = useMemo(() => rows.reduce((s, r) => s + (r.t_km ?? 0), 0), [rows]);
  const uniquePostes = useMemo(() => new Set(rows.map((r) => r.poste)).size, [rows]);
  const uniqueVehicules = useMemo(() => new Set(rows.map((r) => r.mle_vehicule).filter(Boolean)).size, [rows]);

  /* ── mark plan as current ───────────────────────────────────────────────── */
  const markCurrent = async (plan: ConfigurationPlan) => {
    await updateConfigurationPlan(plan.id, { is_current: true });
    await loadPlans();
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="flex flex-col gap-5">
      {/* ── Header ─────────────────────────────────────────────────────── */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <span className="material-symbols-outlined text-blue-600 text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>
              settings_applications
            </span>
            Configuration Transport-Véhicule
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Données réelles — {selectedPlan ? `${total} lignes dans le plan sélectionné` : 'Sélectionnez un plan'}
          </p>
        </div>
        <button
          onClick={() => setShowNewPlan(true)}
          className="flex items-center gap-2 bg-blue-600 text-white rounded-xl px-4 py-2.5 text-sm font-semibold hover:bg-blue-700 transition-colors shrink-0"
        >
          <span className="material-symbols-outlined text-base">add</span>
          Nouveau plan
        </button>
      </div>

      {/* ── Plans carousel ───────────────────────────────────────────────── */}
      {plansLoading ? (
        <div className="h-20 bg-slate-100 animate-pulse rounded-xl" />
      ) : (
        <div className="flex items-center gap-3 overflow-x-auto pb-1">
          {plans.map((plan) => (
            <PlanCard
              key={plan.id}
              plan={plan}
              selected={selectedPlan?.id === plan.id}
              onClick={() => { setSelectedPlan(plan); resetPage(); }}
            />
          ))}
          {plans.length === 0 && (
            <p className="text-sm text-slate-400 italic">Aucun plan — créez-en un ci-dessus</p>
          )}
        </div>
      )}

      {selectedPlan && (
        <>
          {/* ── Plan meta bar ─────────────────────────────────────────── */}
          <div className="flex items-center gap-4 bg-blue-50 border border-blue-100 rounded-xl px-4 py-3">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-blue-800 truncate">{selectedPlan.name}</p>
              {selectedPlan.description && (
                <p className="text-xs text-blue-600 truncate">{selectedPlan.description}</p>
              )}
            </div>
            <div className="flex items-center gap-3 shrink-0 text-xs text-blue-700">
              <span className="flex items-center gap-1">
                <span className="material-symbols-outlined text-sm">route</span>
                <strong>{uniquePostes}</strong> postes
              </span>
              <span className="flex items-center gap-1">
                <span className="material-symbols-outlined text-sm">directions_car</span>
                <strong>{uniqueVehicules}</strong> véhicules
              </span>
              <span className="flex items-center gap-1">
                <span className="material-symbols-outlined text-sm">straighten</span>
                <strong>{totalKm.toLocaleString('fr-MA', { maximumFractionDigits: 0 })}</strong> km total
              </span>
              {!selectedPlan.is_current && (
                <button
                  onClick={() => markCurrent(selectedPlan)}
                  className="ml-2 bg-blue-600 text-white rounded-lg px-3 py-1 text-xs font-semibold hover:bg-blue-700"
                >
                  Marquer comme actuelle
                </button>
              )}
            </div>
          </div>

          {/* ── Filters ───────────────────────────────────────────────── */}
          <div className="flex flex-wrap items-center gap-3 bg-white border border-slate-100 rounded-xl px-4 py-3">
            <span className="text-xs font-bold uppercase tracking-widest text-slate-400 mr-1">Filtres</span>
            <select value={filterPrestataire} onChange={(e) => { setFilterPrestataire(e.target.value); resetPage(); }} className={selectCls}>
              <option value="">Tous les prestataires</option>
              {['STCR', 'S.TOURISME', 'MANAVETTE', 'CTM', 'SOTREG'].map((p) => (
                <option key={p}>{p}</option>
              ))}
            </select>
            <select value={filterSecteur} onChange={(e) => { setFilterSecteur(e.target.value); resetPage(); }} className={selectCls}>
              <option value="">Tous les secteurs</option>
              {['KHOURIBGA', 'OUEDZEM', 'BOULANOIR', 'BOUJNIBA', 'HATTANE', 'FQUIH BEN SALEH'].map((s) => (
                <option key={s}>{s}</option>
              ))}
            </select>
            <select value={filterShift} onChange={(e) => { setFilterShift(e.target.value); resetPage(); }} className={selectCls}>
              <option value="">Tous les shifts</option>
              {['P1', 'P2', 'P3', 'N', 'S'].map((s) => (
                <option key={s} value={s}>Shift {s}</option>
              ))}
            </select>
            <select value={filterAR} onChange={(e) => { setFilterAR(e.target.value); resetPage(); }} className={selectCls}>
              <option value="">Aller & Retour</option>
              <option value="ALLER">Aller</option>
              <option value="RETOUR">Retour</option>
            </select>
            <select value={filterVehicule} onChange={(e) => setFilterVehicule(e.target.value)} className={selectCls}>
              <option value="">Tous les véhicules</option>
              {['AUTOCAR', 'MINIBUS', 'MINICAR'].map((v) => (
                <option key={v}>{v}</option>
              ))}
            </select>
            {(filterPrestataire || filterSecteur || filterShift || filterAR || filterVehicule) && (
              <button
                onClick={() => { setFilterPrestataire(''); setFilterSecteur(''); setFilterShift(''); setFilterAR(''); setFilterVehicule(''); resetPage(); }}
                className="text-xs text-slate-500 hover:text-slate-800 flex items-center gap-1"
              >
                <span className="material-symbols-outlined text-sm">close</span>
                Effacer
              </button>
            )}
            <span className="ml-auto text-xs text-slate-400">
              {rowsLoading ? 'Chargement…' : `${displayed.length} / ${total} lignes`}
            </span>
          </div>

          {/* ── Table ─────────────────────────────────────────────────── */}
          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="w-full text-xs min-w-[1200px]">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50">
                  {[
                    'Conducteur', 'Poste', 'Prestataire', 'Mle Veh.', 'Type', 'Moteur',
                    'Secteur', 'Entité', 'A/R', 'Shift', 'Départ', 'De', 'À', 'Arrivée',
                    'Circuit', 'Durée', 'KM', 'ROT', 'T KM',
                  ].map((h) => (
                    <th key={h} className="px-3 py-2.5 text-left font-bold text-slate-500 whitespace-nowrap">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rowsLoading && (
                  <tr>
                    <td colSpan={19} className="text-center py-12 text-slate-400">
                      <span className="material-symbols-outlined text-3xl animate-spin">progress_activity</span>
                    </td>
                  </tr>
                )}
                {!rowsLoading && displayed.length === 0 && (
                  <tr>
                    <td colSpan={19} className="text-center py-12 text-slate-400 text-sm">
                      Aucune ligne pour ces filtres
                    </td>
                  </tr>
                )}
                {displayed.map((row, i) => (
                  <tr
                    key={row.id}
                    className={[
                      'border-b border-slate-100 hover:bg-slate-50 transition-colors',
                      i % 2 === 0 ? '' : 'bg-slate-50/50',
                    ].join(' ')}
                  >
                    <td className="px-3 py-2 font-medium text-slate-700 whitespace-nowrap">{row.conducteur ?? '—'}</td>
                    <td className="px-3 py-2 font-mono text-slate-600">{row.poste ?? '—'}</td>
                    <td className="px-3 py-2">
                      {row.prestataire ? (
                        <Badge text={row.prestataire} cls={PRESTATAIRE_COLOR[row.prestataire] ?? 'bg-slate-100 text-slate-600'} />
                      ) : '—'}
                    </td>
                    <td className="px-3 py-2 font-mono text-slate-500 text-[11px]">{row.mle_vehicule ?? '—'}</td>
                    <td className="px-3 py-2">
                      {row.type_vehicule ? (
                        <Badge text={row.type_vehicule} cls={VEHICULE_COLOR[row.type_vehicule] ?? 'bg-slate-100 text-slate-600'} />
                      ) : '—'}
                    </td>
                    <td className="px-3 py-2 text-slate-500">{row.type_moteur ?? '—'}</td>
                    <td className="px-3 py-2 text-slate-600">{row.secteur ?? '—'}</td>
                    <td className="px-3 py-2 text-slate-600 max-w-[120px] truncate" title={row.entite ?? ''}>{row.entite ?? '—'}</td>
                    <td className="px-3 py-2">
                      {row.aller_retour ? (
                        <Badge text={row.aller_retour} cls={AR_COLOR[row.aller_retour] ?? ''} />
                      ) : '—'}
                    </td>
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

          {/* ── Pagination ────────────────────────────────────────────── */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between text-xs text-slate-500">
              <span>Page {page} / {totalPages} — {total} lignes au total</span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-40"
                >
                  ← Préc.
                </button>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-40"
                >
                  Suiv. →
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {/* ── New plan modal ─────────────────────────────────────────────── */}
      {showNewPlan && (
        <NewPlanModal
          onClose={() => setShowNewPlan(false)}
          onCreated={(plan) => {
            setPlans((prev) => [plan, ...prev]);
            setSelectedPlan(plan);
            setShowNewPlan(false);
          }}
        />
      )}
    </div>
  );
}
