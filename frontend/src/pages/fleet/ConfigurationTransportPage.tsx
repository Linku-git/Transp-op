import { useEffect, useState, useCallback } from 'react';

import {
  listConfigurationTransport,
  createConfigurationTransport,
  updateConfigurationTransport,
  deleteConfigurationTransport,
  listPointsArret,
} from '@/api/vehicles';
import type { ConfigurationTransport, ConfigurationTransportCreate, PointArret } from '@/types/vehicle';
import { VEHICLE_TYPES } from '@/types/vehicle';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useSiteStore } from '@/stores/siteStore';

const EMPTY: ConfigurationTransportCreate = {
  ligne: '',
  prestataire: '',
  site_id: null,
  vehicle_type: null,
  vehicle_count: null,
  shift: null,
  point_depart_id: null,
  point_arrivee_id: null,
  circuit: '',
  is_active: true,
  observations: '',
};

export function ConfigurationTransportPage() {
  const { sites, fetchSites } = useSiteStore();
  const [items, setItems] = useState<ConfigurationTransport[]>([]);
  const [stops, setStops] = useState<PointArret[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editItem, setEditItem] = useState<ConfigurationTransport | null>(null);
  const [form, setForm] = useState<ConfigurationTransportCreate>(EMPTY);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [confRes, stopsRes] = await Promise.all([
        listConfigurationTransport({ page_size: 200 }),
        listPointsArret({ page_size: 200, is_active: true }),
      ]);
      setItems(confRes.items ?? []);
      setStops(stopsRes.items ?? []);
    } catch {
      setError('Impossible de charger la configuration');
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

  const openEdit = (item: ConfigurationTransport) => {
    setEditItem(item);
    setForm({
      ligne: item.ligne,
      prestataire: item.prestataire,
      site_id: item.site_id,
      vehicle_type: item.vehicle_type,
      vehicle_count: item.vehicle_count,
      shift: item.shift,
      point_depart_id: item.point_depart_id,
      point_arrivee_id: item.point_arrivee_id,
      circuit: item.circuit ?? '',
      is_active: item.is_active,
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
        vehicle_type: form.vehicle_type || null,
        shift: form.shift || null,
        point_depart_id: form.point_depart_id || null,
        point_arrivee_id: form.point_arrivee_id || null,
        circuit: form.circuit || null,
        observations: form.observations || null,
      };
      if (editItem) {
        await updateConfigurationTransport(editItem.id, payload);
      } else {
        await createConfigurationTransport(payload);
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
    if (!confirm('Supprimer cette configuration ?')) return;
    try {
      await deleteConfigurationTransport(id);
      await fetchData();
    } catch {
      alert('Erreur lors de la suppression');
    }
  };

  const set = (k: keyof ConfigurationTransportCreate, v: unknown) =>
    setForm((f) => ({ ...f, [k]: v }));

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">Configuration Transport-Véhicule</h1>
          <p className="text-sm text-on-surface-variant mt-0.5">
            {items.length} ligne{items.length !== 1 ? 's' : ''} configurée{items.length !== 1 ? 's' : ''}
          </p>
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
                {editItem ? 'Modifier la configuration' : 'Nouvelle configuration'}
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
                <label className="text-xs font-medium text-on-surface-variant">Ligne *</label>
                <Input required placeholder="Ex: L1 - Casablanca Centre" value={form.ligne} onChange={(e) => set('ligne', e.target.value)} />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Prestataire *</label>
                <Input required placeholder="Ex: SOTREG" value={form.prestataire} onChange={(e) => set('prestataire', e.target.value)} />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Type de véhicule</label>
                <select value={form.vehicle_type ?? ''} onChange={(e) => set('vehicle_type', e.target.value || null)}
                  className="h-10 rounded-lg border border-outline-variant bg-surface px-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary">
                  <option value="">— Sélectionner —</option>
                  {VEHICLE_TYPES.map((t) => <option key={t}>{t}</option>)}
                </select>
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Nb véhicules</label>
                <Input type="number" min={0} value={form.vehicle_count ?? ''} onChange={(e) => set('vehicle_count', e.target.value ? parseInt(e.target.value) : null)} />
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
                <label className="text-xs font-medium text-on-surface-variant">Shift</label>
                <select value={form.shift ?? ''} onChange={(e) => set('shift', e.target.value || null)}
                  className="h-10 rounded-lg border border-outline-variant bg-surface px-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary">
                  <option value="">— Tous les shifts —</option>
                  <option value="Shift 1">Shift 1</option>
                  <option value="Shift 2">Shift 2</option>
                  <option value="Shift 3">Shift 3</option>
                </select>
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Point de départ</label>
                <select value={form.point_depart_id ?? ''} onChange={(e) => set('point_depart_id', e.target.value || null)}
                  className="h-10 rounded-lg border border-outline-variant bg-surface px-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary">
                  <option value="">— Aucun —</option>
                  {stops.map((s) => <option key={s.id} value={s.id}>{s.code} – {s.nom}</option>)}
                </select>
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Point d'arrivée</label>
                <select value={form.point_arrivee_id ?? ''} onChange={(e) => set('point_arrivee_id', e.target.value || null)}
                  className="h-10 rounded-lg border border-outline-variant bg-surface px-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary">
                  <option value="">— Aucun —</option>
                  {stops.map((s) => <option key={s.id} value={s.id}>{s.code} – {s.nom}</option>)}
                </select>
              </div>
              <div className="col-span-2 flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Circuit</label>
                <Input placeholder="Description du circuit" value={form.circuit ?? ''} onChange={(e) => set('circuit', e.target.value)} />
              </div>
              <div className="col-span-2 flex items-center gap-2">
                <input type="checkbox" id="cfg-active" checked={form.is_active ?? true} onChange={(e) => set('is_active', e.target.checked)} className="w-4 h-4 accent-primary" />
                <label htmlFor="cfg-active" className="text-sm text-on-surface">Configuration active</label>
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
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Ligne</th>
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Prestataire</th>
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Type véhicule</th>
              <th className="px-4 py-3 text-right font-semibold text-on-surface-variant">Nb veh.</th>
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Shift</th>
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Départ</th>
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Arrivée</th>
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Statut</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr><td colSpan={9} className="text-center py-10 text-on-surface-variant text-sm">Chargement…</td></tr>
            )}
            {!loading && items.length === 0 && (
              <tr><td colSpan={9} className="text-center py-10 text-on-surface-variant text-sm">Aucune configuration — cliquez sur « Ajouter » pour commencer</td></tr>
            )}
            {items.map((item) => (
              <tr key={item.id} className="border-b border-surface-container-high hover:bg-surface-container-low/50">
                <td className="px-4 py-3 font-medium text-on-surface">{item.ligne}</td>
                <td className="px-4 py-3 text-on-surface-variant">{item.prestataire}</td>
                <td className="px-4 py-3 text-on-surface-variant">{item.vehicle_type ?? '—'}</td>
                <td className="px-4 py-3 text-right text-on-surface">{item.vehicle_count ?? '—'}</td>
                <td className="px-4 py-3 text-on-surface-variant">{item.shift ?? '—'}</td>
                <td className="px-4 py-3 text-xs text-on-surface-variant">{item.point_depart_nom ?? '—'}</td>
                <td className="px-4 py-3 text-xs text-on-surface-variant">{item.point_arrivee_nom ?? '—'}</td>
                <td className="px-4 py-3">
                  <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${item.is_active ? 'bg-green-100 text-green-700' : 'bg-surface-container text-on-surface-variant'}`}>
                    {item.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
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
