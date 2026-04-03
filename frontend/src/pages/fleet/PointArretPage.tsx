import { useEffect, useState, useCallback } from 'react';

import {
  listPointsArret,
  createPointArret,
  updatePointArret,
  deletePointArret,
} from '@/api/vehicles';
import type { PointArret, PointArretCreate } from '@/types/vehicle';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useSiteStore } from '@/stores/siteStore';

const EMPTY: PointArretCreate = {
  code: '',
  nom: '',
  lat: 33.573,
  lng: -7.589,
  adresse: '',
  ville: 'Casablanca',
  prestataire: '',
  site_id: null,
  is_active: true,
  correspondance_tb: '',
  observations: '',
};

export function PointArretPage() {
  const { sites, fetchSites } = useSiteStore();
  const [items, setItems] = useState<PointArret[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editItem, setEditItem] = useState<PointArret | null>(null);
  const [form, setForm] = useState<PointArretCreate>(EMPTY);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listPointsArret({ page_size: 200 });
      setItems(res.items ?? []);
    } catch {
      setError('Impossible de charger les points d\'arrêt');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    fetchSites();
  }, [fetchData, fetchSites]);

  const filtered = search.trim()
    ? items.filter((i) => {
        const q = search.toLowerCase();
        return (
          i.code.toLowerCase().includes(q) ||
          i.nom.toLowerCase().includes(q) ||
          i.prestataire?.toLowerCase().includes(q) ||
          i.ville?.toLowerCase().includes(q)
        );
      })
    : items;

  const openCreate = () => {
    setEditItem(null);
    setForm(EMPTY);
    setFormError(null);
    setShowForm(true);
  };

  const openEdit = (item: PointArret) => {
    setEditItem(item);
    setForm({
      code: item.code,
      nom: item.nom,
      lat: item.lat,
      lng: item.lng,
      adresse: item.adresse ?? '',
      ville: item.ville ?? '',
      prestataire: item.prestataire ?? '',
      site_id: item.site_id,
      is_active: item.is_active,
      correspondance_tb: item.correspondance_tb ?? '',
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
        adresse: form.adresse || null,
        ville: form.ville || null,
        prestataire: form.prestataire || null,
        site_id: form.site_id || null,
        correspondance_tb: form.correspondance_tb || null,
        observations: form.observations || null,
      };
      if (editItem) {
        await updatePointArret(editItem.id, payload);
      } else {
        await createPointArret(payload);
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
    if (!confirm('Supprimer ce point d\'arrêt ?')) return;
    try {
      await deletePointArret(id);
      await fetchData();
    } catch {
      alert('Erreur lors de la suppression');
    }
  };

  const set = (k: keyof PointArretCreate, v: unknown) =>
    setForm((f) => ({ ...f, [k]: v }));

  const activeCount = items.filter((i) => i.is_active).length;

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">Points d'Arrêt SOTREG</h1>
          <p className="text-sm text-on-surface-variant mt-0.5">
            {items.length} arrêt{items.length !== 1 ? 's' : ''} · {activeCount} actif{activeCount !== 1 ? 's' : ''}
          </p>
        </div>
        <Button onClick={openCreate}>
          <span className="material-symbols-outlined text-base">add</span>
          Ajouter un arrêt
        </Button>
      </div>


      {/* Search */}
      <div className="max-w-sm">
        <Input
          placeholder="Rechercher par code, nom, prestataire…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
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
                {editItem ? 'Modifier l\'arrêt' : 'Nouveau point d\'arrêt'}
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
                <label className="text-xs font-medium text-on-surface-variant">Code *</label>
                <Input required placeholder="Ex: AR-001" value={form.code} onChange={(e) => set('code', e.target.value)} />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Nom *</label>
                <Input required placeholder="Ex: Arrêt Place Mohammed V" value={form.nom} onChange={(e) => set('nom', e.target.value)} />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Adresse</label>
                <Input placeholder="Adresse complète" value={form.adresse ?? ''} onChange={(e) => set('adresse', e.target.value)} />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Ville</label>
                <Input placeholder="Ex: Casablanca" value={form.ville ?? ''} onChange={(e) => set('ville', e.target.value)} />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Latitude *</label>
                <Input required type="number" step="0.000001" min={-90} max={90} value={form.lat} onChange={(e) => set('lat', parseFloat(e.target.value) || 0)} />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Longitude *</label>
                <Input required type="number" step="0.000001" min={-180} max={180} value={form.lng} onChange={(e) => set('lng', parseFloat(e.target.value) || 0)} />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Prestataire</label>
                <Input placeholder="Ex: SOTREG" value={form.prestataire ?? ''} onChange={(e) => set('prestataire', e.target.value)} />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Site</label>
                <select value={form.site_id ?? ''} onChange={(e) => set('site_id', e.target.value || null)}
                  className="h-10 rounded-lg border border-outline-variant bg-surface px-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary">
                  <option value="">— Aucun site —</option>
                  {sites.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
                </select>
              </div>
              <div className="col-span-2 flex items-center gap-2">
                <input type="checkbox" id="active" checked={form.is_active ?? true} onChange={(e) => set('is_active', e.target.checked)} className="w-4 h-4 accent-primary" />
                <label htmlFor="active" className="text-sm text-on-surface">Arrêt actif</label>
              </div>
              <div className="col-span-2 flex flex-col gap-1">
                <label className="text-xs font-medium text-on-surface-variant">Correspondance Arrêts avec TB</label>
                <Input
                  value={form.correspondance_tb ?? ''}
                  onChange={(e) => set('correspondance_tb', e.target.value)}
                  placeholder="ex: Arrêt A, Arrêt B"
                />
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
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Code</th>
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Nom</th>
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Ville</th>
              <th className="px-4 py-3 text-right font-semibold text-on-surface-variant">Lat</th>
              <th className="px-4 py-3 text-right font-semibold text-on-surface-variant">Lng</th>
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Prestataire</th>
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Corresp. TB</th>
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Site</th>
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Statut</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr><td colSpan={10} className="text-center py-10 text-on-surface-variant text-sm">Chargement…</td></tr>
            )}
            {!loading && filtered.length === 0 && (
              <tr><td colSpan={10} className="text-center py-10 text-on-surface-variant text-sm">Aucun point d'arrêt enregistré</td></tr>
            )}
            {filtered.map((item) => (
              <tr key={item.id} className="border-b border-surface-container-high hover:bg-surface-container-low/50">
                <td className="px-4 py-3 font-mono text-on-surface font-medium">{item.code}</td>
                <td className="px-4 py-3 text-on-surface">{item.nom}</td>
                <td className="px-4 py-3 text-on-surface-variant">{item.ville ?? '—'}</td>
                <td className="px-4 py-3 text-right font-mono text-xs text-on-surface-variant">{item.lat.toFixed(5)}</td>
                <td className="px-4 py-3 text-right font-mono text-xs text-on-surface-variant">{item.lng.toFixed(5)}</td>
                <td className="px-4 py-3 text-on-surface-variant">{item.prestataire ?? '—'}</td>
                <td className="px-4 py-3 text-xs text-on-surface-variant max-w-[150px] truncate" title={item.correspondance_tb ?? ''}>{item.correspondance_tb ?? '—'}</td>
                <td className="px-4 py-3 text-xs text-on-surface-variant">{item.site_name ?? '—'}</td>
                <td className="px-4 py-3">
                  <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${item.is_active ? 'bg-green-100 text-green-700' : 'bg-surface-container text-on-surface-variant'}`}>
                    {item.is_active ? 'Actif' : 'Inactif'}
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
