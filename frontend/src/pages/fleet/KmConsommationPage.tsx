import { useEffect, useState, useCallback } from 'react';

import {
  listKmConsommation,
  createKmConsommation,
  updateKmConsommation,
  deleteKmConsommation,
} from '@/api/vehicles';
import type { KmConsommation, KmConsommationCreate } from '@/types/vehicle';
import { VEHICLE_TYPES } from '@/types/vehicle';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useSiteStore } from '@/stores/siteStore';

const EMPTY: KmConsommationCreate = {
  prestataire: '',
  vehicle_type: 'Minibus',
  site_id: null,
  vehicle_count_peak: null,
  km_avg: null,
  km_min: null,
  km_max: null,
  seat_count: null,
  fuel_consumption_l100km: null,
  monthly_cost_per_vehicle_mad: null,
  observations: '',
};

function fmt(n: number | null | undefined): string {
  if (n == null) return '—';
  return Number(n).toLocaleString('fr-FR', { maximumFractionDigits: 2 });
}

export function KmConsommationPage() {
  const { sites, fetchSites } = useSiteStore();
  const [items, setItems] = useState<KmConsommation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editItem, setEditItem] = useState<KmConsommation | null>(null);
  const [form, setForm] = useState<KmConsommationCreate>(EMPTY);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listKmConsommation({ page_size: 200 });
      setItems(res.items ?? []);
    } catch {
      setError('Impossible de charger les données');
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

  const openEdit = (item: KmConsommation) => {
    setEditItem(item);
    setForm({
      prestataire: item.prestataire,
      vehicle_type: item.vehicle_type,
      site_id: item.site_id,
      vehicle_count_peak: item.vehicle_count_peak,
      km_avg: item.km_avg,
      km_min: item.km_min,
      km_max: item.km_max,
      seat_count: item.seat_count,
      fuel_consumption_l100km: item.fuel_consumption_l100km,
      monthly_cost_per_vehicle_mad: item.monthly_cost_per_vehicle_mad,
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
      const payload = {
        ...form,
        site_id: form.site_id || null,
        observations: form.observations || null,
      };
      if (editItem) {
        await updateKmConsommation(editItem.id, payload);
      } else {
        await createKmConsommation(payload);
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
    if (!confirm('Supprimer cette ligne ?')) return;
    try {
      await deleteKmConsommation(id);
      await fetchData();
    } catch {
      alert('Erreur lors de la suppression');
    }
  };

  const set = (k: keyof KmConsommationCreate, v: unknown) =>
    setForm((f) => ({ ...f, [k]: v }));

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">Type Véhicules & Consommation Gasoil</h1>
          <p className="text-sm text-on-surface-variant mt-0.5">Statistiques par prestataire et type de véhicule</p>
        </div>
        <Button onClick={openCreate}>
          <span className="material-symbols-outlined text-base">add</span>
          Ajouter une ligne
        </Button>
      </div>


      {error && (
        <div className="rounded-lg bg-error-container/20 text-error px-4 py-3 text-sm">{error}</div>
      )}

      {/* Modal form */}
      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <form
            onSubmit={handleSave}
            className="bg-surface rounded-2xl shadow-xl p-6 w-full max-w-2xl flex flex-col gap-4 max-h-[90vh] overflow-y-auto"
          >
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-on-surface">
                {editItem ? 'Modifier la ligne' : 'Nouvelle ligne de consommation'}
              </h2>
              <button type="button" onClick={() => setShowForm(false)} className="text-on-surface-variant hover:text-on-surface">
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            {formError && (
              <div className="rounded-lg bg-error-container/20 text-error px-3 py-2 text-sm">{formError}</div>
            )}

            <div className="grid grid-cols-2 gap-3">
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Prestataire *</label>
                <Input required placeholder="Ex: SOTREG" value={form.prestataire} onChange={(e) => set('prestataire', e.target.value)} />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Type de véhicule *</label>
                <select required value={form.vehicle_type} onChange={(e) => set('vehicle_type', e.target.value)}
                  className="h-10 rounded-lg border border-outline-variant bg-surface px-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary">
                  {VEHICLE_TYPES.map((t) => <option key={t}>{t}</option>)}
                </select>
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Site</label>
                <select value={form.site_id ?? ''} onChange={(e) => set('site_id', e.target.value || null)}
                  className="h-10 rounded-lg border border-outline-variant bg-surface px-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary">
                  <option value="">— Tous les sites —</option>
                  {sites.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
                </select>
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Nb véhicules au PIC</label>
                <Input type="number" min={0} value={form.vehicle_count_peak ?? ''} onChange={(e) => set('vehicle_count_peak', e.target.value ? parseInt(e.target.value) : null)} />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Km Moyen</label>
                <Input type="number" min={0} step={0.1} value={form.km_avg ?? ''} onChange={(e) => set('km_avg', e.target.value ? parseFloat(e.target.value) : null)} />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Km Min</label>
                <Input type="number" min={0} step={0.1} value={form.km_min ?? ''} onChange={(e) => set('km_min', e.target.value ? parseFloat(e.target.value) : null)} />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Km Max</label>
                <Input type="number" min={0} step={0.1} value={form.km_max ?? ''} onChange={(e) => set('km_max', e.target.value ? parseFloat(e.target.value) : null)} />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Nb sièges</label>
                <Input type="number" min={0} value={form.seat_count ?? ''} onChange={(e) => set('seat_count', e.target.value ? parseInt(e.target.value) : null)} />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Consommation (L/100 km)</label>
                <Input type="number" min={0} step={0.1} value={form.fuel_consumption_l100km ?? ''} onChange={(e) => set('fuel_consumption_l100km', e.target.value ? parseFloat(e.target.value) : null)} />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Coût mensuel/véhicule (MAD)</label>
                <Input type="number" min={0} step={0.01} value={form.monthly_cost_per_vehicle_mad ?? ''} onChange={(e) => set('monthly_cost_per_vehicle_mad', e.target.value ? parseFloat(e.target.value) : null)} />
              </div>
              <div className="col-span-2 flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Observations</label>
                <textarea rows={2} className="rounded-lg border border-outline-variant bg-surface px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary"
                  value={form.observations ?? ''} onChange={(e) => set('observations', e.target.value)} />
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
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Prestataire</th>
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Type</th>
              <th className="px-4 py-3 text-right font-semibold text-on-surface-variant">Nb PIC</th>
              <th className="px-4 py-3 text-right font-semibold text-on-surface-variant">Km Moy</th>
              <th className="px-4 py-3 text-right font-semibold text-on-surface-variant">Km Min</th>
              <th className="px-4 py-3 text-right font-semibold text-on-surface-variant">Km Max</th>
              <th className="px-4 py-3 text-right font-semibold text-on-surface-variant">Sièges</th>
              <th className="px-4 py-3 text-right font-semibold text-on-surface-variant">L/100 km</th>
              <th className="px-4 py-3 text-right font-semibold text-on-surface-variant">Coût/véh (MAD)</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr><td colSpan={10} className="text-center py-10 text-on-surface-variant text-sm">Chargement…</td></tr>
            )}
            {!loading && items.length === 0 && (
              <tr><td colSpan={10} className="text-center py-10 text-on-surface-variant text-sm">Aucune donnée — cliquez sur « Ajouter » pour commencer</td></tr>
            )}
            {items.map((item) => (
              <tr key={item.id} className="border-b border-surface-container-high hover:bg-surface-container-low/50">
                <td className="px-4 py-3 font-medium text-on-surface">{item.prestataire}</td>
                <td className="px-4 py-3 text-on-surface-variant">{item.vehicle_type}</td>
                <td className="px-4 py-3 text-right text-on-surface">{item.vehicle_count_peak ?? '—'}</td>
                <td className="px-4 py-3 text-right text-on-surface">{fmt(item.km_avg)}</td>
                <td className="px-4 py-3 text-right text-on-surface">{fmt(item.km_min)}</td>
                <td className="px-4 py-3 text-right text-on-surface">{fmt(item.km_max)}</td>
                <td className="px-4 py-3 text-right text-on-surface">{item.seat_count ?? '—'}</td>
                <td className="px-4 py-3 text-right text-on-surface">{fmt(item.fuel_consumption_l100km)}</td>
                <td className="px-4 py-3 text-right text-on-surface font-medium">{fmt(item.monthly_cost_per_vehicle_mad)}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1 justify-end">
                    <button onClick={() => openEdit(item)} className="p-1 rounded hover:bg-surface-container text-on-surface-variant hover:text-on-surface" title="Modifier">
                      <span className="material-symbols-outlined text-base">edit</span>
                    </button>
                    <button onClick={() => handleDelete(item.id)} className="p-1 rounded hover:bg-error-container/20 text-on-surface-variant hover:text-error" title="Supprimer">
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
