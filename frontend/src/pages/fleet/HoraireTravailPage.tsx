import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
  listHorairesTravail,
  createHoraireTravail,
  updateHoraireTravail,
  deleteHoraireTravail,
} from '@/api/vehicles';
import type { HoraireTravail, HoraireTravailCreate } from '@/types/vehicle';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useSiteStore } from '@/stores/siteStore';

const SHIFT_TYPES = [
  'Journalier',
  '2x8',
  '3x8',
  'VSD (Vendredi-Samedi-Dimanche)',
  'Nuit',
  'Administratif',
  'Posté',
  'Quart',
];

const EMPTY: HoraireTravailCreate = {
  type_horaire: 'Journalier',
  site_id: null,
  depart_h1: '',
  retour_h1: '',
  depart_h2: '',
  retour_h2: '',
  observations: '',
};

function TimeCell({ value }: { value: string | null }) {
  if (!value) return <span className="text-on-surface-variant">—</span>;
  return (
    <span className="font-mono text-sm font-medium text-on-surface">{value}</span>
  );
}

export function HoraireTravailPage() {
  const { sites, fetchSites } = useSiteStore();
  const [items, setItems] = useState<HoraireTravail[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editItem, setEditItem] = useState<HoraireTravail | null>(null);
  const [form, setForm] = useState<HoraireTravailCreate>(EMPTY);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listHorairesTravail({ page_size: 200 });
      setItems(res.items ?? []);
    } catch {
      setError('Impossible de charger les horaires');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    fetchSites();
  }, [fetchData, fetchSites]);

  const openCreate = () => {
    setEditItem(null);
    setForm(EMPTY);
    setFormError(null);
    setShowForm(true);
  };

  const openEdit = (item: HoraireTravail) => {
    setEditItem(item);
    setForm({
      type_horaire: item.type_horaire,
      site_id: item.site_id,
      depart_h1: item.depart_h1 ?? '',
      retour_h1: item.retour_h1 ?? '',
      depart_h2: item.depart_h2 ?? '',
      retour_h2: item.retour_h2 ?? '',
      observations: item.observations ?? '',
    });
    setFormError(null);
    setShowForm(true);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setFormError(null);
    try {
      const payload: HoraireTravailCreate = {
        ...form,
        site_id: form.site_id || null,
        depart_h1: form.depart_h1 || null,
        retour_h1: form.retour_h1 || null,
        depart_h2: form.depart_h2 || null,
        retour_h2: form.retour_h2 || null,
        observations: form.observations || null,
      };
      if (editItem) {
        await updateHoraireTravail(editItem.id, payload);
      } else {
        await createHoraireTravail(payload);
      }
      setShowForm(false);
      await fetchData();
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } };
      setFormError(e?.response?.data?.detail ?? 'Erreur lors de la sauvegarde');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Supprimer cet horaire ?')) return;
    try {
      await deleteHoraireTravail(id);
      await fetchData();
    } catch {
      alert('Erreur lors de la suppression');
    }
  };

  const set = (k: keyof HoraireTravailCreate, v: unknown) =>
    setForm((f) => ({ ...f, [k]: v }));

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">Horaires de Travail</h1>
          <p className="text-sm text-on-surface-variant mt-0.5">
            {items.length} horaire{items.length !== 1 ? 's' : ''} configuré{items.length !== 1 ? 's' : ''}
          </p>
        </div>
        <Button onClick={openCreate}>
          <span className="material-symbols-outlined text-base">add</span>
          Ajouter un horaire
        </Button>
      </div>

      {/* Sub-nav */}
      <div className="flex gap-2 border-b border-surface-container-high pb-3 flex-wrap">
        <Link to="/vehicles" className="text-sm font-medium text-on-surface-variant hover:text-on-surface px-1 pb-1">
          Parc Véhicule
        </Link>
        <Link to="/fleet/consumption" className="text-sm font-medium text-on-surface-variant hover:text-on-surface px-1 pb-1">
          Km & Consommation
        </Link>
        <Link to="/fleet/stops" className="text-sm font-medium text-on-surface-variant hover:text-on-surface px-1 pb-1">
          Points d'Arrêt
        </Link>
        <Link to="/fleet/config" className="text-sm font-medium text-on-surface-variant hover:text-on-surface px-1 pb-1">
          Config. Transport
        </Link>
        <Link to="/fleet/horaires" className="text-sm font-medium text-primary border-b-2 border-primary pb-1 px-1">
          Horaires de Travail
        </Link>
      </div>

      {error && (
        <div className="rounded-lg bg-error-container/20 text-error px-4 py-3 text-sm">{error}</div>
      )}

      {/* Modal form */}
      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <form
            onSubmit={handleSave}
            className="bg-surface rounded-2xl shadow-xl p-6 w-full max-w-xl flex flex-col gap-4 max-h-[90vh] overflow-y-auto"
          >
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-on-surface">
                {editItem ? 'Modifier l\'horaire' : 'Nouvel horaire de travail'}
              </h2>
              <button type="button" onClick={() => setShowForm(false)} className="text-on-surface-variant hover:text-on-surface">
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            {formError && (
              <div className="rounded-lg bg-error-container/20 text-error px-3 py-2 text-sm">{formError}</div>
            )}

            <div className="grid grid-cols-2 gap-3">
              <div className="col-span-2 flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Type Horaire *</label>
                <select
                  required
                  value={form.type_horaire}
                  onChange={(e) => set('type_horaire', e.target.value)}
                  className="h-10 rounded-lg border border-outline-variant bg-surface px-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  {SHIFT_TYPES.map((t) => <option key={t}>{t}</option>)}
                </select>
              </div>

              <div className="col-span-2 flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Site</label>
                <select
                  value={form.site_id ?? ''}
                  onChange={(e) => set('site_id', e.target.value || null)}
                  className="h-10 rounded-lg border border-outline-variant bg-surface px-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="">— Tous les sites —</option>
                  {sites.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
                </select>
              </div>

              {/* Premier Horaire */}
              <div className="col-span-2">
                <p className="text-xs font-semibold text-on-surface-variant uppercase tracking-wide mb-2 flex items-center gap-2">
                  <span className="inline-block w-5 h-5 rounded-full bg-primary text-on-primary text-xs flex items-center justify-center font-bold">1</span>
                  Premier Horaire
                </p>
                <div className="grid grid-cols-2 gap-3">
                  <div className="flex flex-col gap-1">
                    <label className="text-xs text-on-surface-variant">Horaire Départ</label>
                    <Input
                      type="time"
                      value={form.depart_h1 ?? ''}
                      onChange={(e) => set('depart_h1', e.target.value)}
                      placeholder="06:00"
                    />
                  </div>
                  <div className="flex flex-col gap-1">
                    <label className="text-xs text-on-surface-variant">Horaire Retour</label>
                    <Input
                      type="time"
                      value={form.retour_h1 ?? ''}
                      onChange={(e) => set('retour_h1', e.target.value)}
                      placeholder="14:00"
                    />
                  </div>
                </div>
              </div>

              {/* Deuxième Horaire */}
              <div className="col-span-2">
                <p className="text-xs font-semibold text-on-surface-variant uppercase tracking-wide mb-2 flex items-center gap-2">
                  <span className="inline-block w-5 h-5 rounded-full bg-surface-container text-on-surface-variant text-xs flex items-center justify-center font-bold border">2</span>
                  Deuxième Horaire
                </p>
                <div className="grid grid-cols-2 gap-3">
                  <div className="flex flex-col gap-1">
                    <label className="text-xs text-on-surface-variant">Horaire Départ</label>
                    <Input
                      type="time"
                      value={form.depart_h2 ?? ''}
                      onChange={(e) => set('depart_h2', e.target.value)}
                      placeholder="14:00"
                    />
                  </div>
                  <div className="flex flex-col gap-1">
                    <label className="text-xs text-on-surface-variant">Horaire Retour</label>
                    <Input
                      type="time"
                      value={form.retour_h2 ?? ''}
                      onChange={(e) => set('retour_h2', e.target.value)}
                      placeholder="22:00"
                    />
                  </div>
                </div>
              </div>

              <div className="col-span-2 flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Observations</label>
                <textarea
                  rows={2}
                  className="rounded-lg border border-outline-variant bg-surface px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary"
                  value={form.observations ?? ''}
                  onChange={(e) => set('observations', e.target.value)}
                />
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <Button type="submit" disabled={saving}>{saving ? 'Enregistrement…' : 'Enregistrer'}</Button>
              <Button variant="secondary" type="button" onClick={() => setShowForm(false)}>Annuler</Button>
            </div>
          </form>
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-surface-container-high bg-surface">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-surface-container-high bg-surface-container-low">
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Type Horaire</th>
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Site</th>
              <th className="px-4 py-3 text-center font-semibold text-on-surface-variant" colSpan={2}>
                1er Horaire
              </th>
              <th className="px-4 py-3 text-center font-semibold text-on-surface-variant" colSpan={2}>
                2ème Horaire
              </th>
              <th className="px-4 py-3" />
            </tr>
            <tr className="border-b border-surface-container-high bg-surface-container-lowest text-xs text-on-surface-variant">
              <th className="px-4 py-1" />
              <th className="px-4 py-1" />
              <th className="px-4 py-1 text-center font-medium">Départ</th>
              <th className="px-4 py-1 text-center font-medium">Retour</th>
              <th className="px-4 py-1 text-center font-medium">Départ</th>
              <th className="px-4 py-1 text-center font-medium">Retour</th>
              <th className="px-4 py-1" />
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr><td colSpan={7} className="text-center py-10 text-on-surface-variant text-sm">Chargement…</td></tr>
            )}
            {!loading && items.length === 0 && (
              <tr><td colSpan={7} className="text-center py-10 text-on-surface-variant text-sm">Aucun horaire enregistré — cliquez sur « Ajouter » pour commencer</td></tr>
            )}
            {items.map((item) => (
              <tr key={item.id} className="border-b border-surface-container-high hover:bg-surface-container-low/50">
                <td className="px-4 py-3 font-medium text-on-surface">{item.type_horaire}</td>
                <td className="px-4 py-3 text-xs text-on-surface-variant">{item.site_name ?? '—'}</td>
                <td className="px-4 py-3 text-center"><TimeCell value={item.depart_h1} /></td>
                <td className="px-4 py-3 text-center"><TimeCell value={item.retour_h1} /></td>
                <td className="px-4 py-3 text-center"><TimeCell value={item.depart_h2} /></td>
                <td className="px-4 py-3 text-center"><TimeCell value={item.retour_h2} /></td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1 justify-end">
                    <button
                      onClick={() => openEdit(item)}
                      className="p-1 rounded hover:bg-surface-container text-on-surface-variant hover:text-on-surface"
                      title="Modifier"
                    >
                      <span className="material-symbols-outlined text-base">edit</span>
                    </button>
                    <button
                      onClick={() => handleDelete(item.id)}
                      className="p-1 rounded hover:bg-error-container/20 text-on-surface-variant hover:text-error"
                      title="Supprimer"
                    >
                      <span className="material-symbols-outlined text-base">delete</span>
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
