import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { extractApiError } from '@/lib/apiError';
import type { Vehicle, VehicleCreate } from '@/types/vehicle';
import { VEHICLE_TYPES, CONDITIONS, OWNER_TYPES } from '@/types/vehicle';
import { createVehicle, updateVehicle } from '@/api/vehicles';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useSiteStore } from '@/stores/siteStore';

interface Props {
  vehicle?: Vehicle;
}

export function VehicleForm({ vehicle }: Props) {
  const navigate = useNavigate();
  const { sites, fetchSites } = useSiteStore();
  const isEdit = !!vehicle;
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState<VehicleCreate>({
    matricule: vehicle?.matricule ?? '',
    type: vehicle?.type ?? 'Minibus',
    brand_model: vehicle?.brand_model ?? '',
    capacity: vehicle?.capacity ?? 20,
    year: vehicle?.year ?? null,
    circulation_date: vehicle?.circulation_date ?? '',
    owner_type: vehicle?.owner_type ?? '',
    prestataire: vehicle?.prestataire ?? '',
    monthly_cost_mad: vehicle?.monthly_cost_mad ?? null,
    monthly_km: vehicle?.monthly_km ?? null,
    condition: vehicle?.condition ?? 'Bon',
    site_id: vehicle?.site_id ?? '',
    is_pmr_accessible: vehicle?.is_pmr_accessible ?? false,
    fuel_consumption: vehicle?.fuel_consumption ?? null,
    observations: vehicle?.observations ?? '',
  });

  useEffect(() => {
    fetchSites();
  }, [fetchSites]);

  const set = (k: keyof VehicleCreate, v: unknown) =>
    setForm((f) => ({ ...f, [k]: v }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const payload: VehicleCreate = {
        ...form,
        matricule: form.matricule || null,
        brand_model: form.brand_model || null,
        circulation_date: form.circulation_date || null,
        owner_type: form.owner_type || null,
        prestataire: form.prestataire || null,
        site_id: form.site_id || null,
        observations: form.observations || null,
        year: form.year || null,
      };
      if (isEdit && vehicle) {
        await updateVehicle(vehicle.id, payload);
      } else {
        await createVehicle(payload);
      }
      navigate('/vehicles');
    } catch (err: unknown) {
      setError(extractApiError(err, 'Erreur lors de la sauvegarde'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6 p-6 max-w-3xl">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={() => navigate('/vehicles')}
          className="p-2 rounded-lg hover:bg-surface-container text-on-surface-variant"
        >
          <span className="material-symbols-outlined">arrow_back</span>
        </button>
        <h1 className="text-2xl font-bold text-on-surface">
          {isEdit ? 'Modifier le véhicule' : 'Nouveau véhicule'}
        </h1>
      </div>

      {error && (
        <div className="rounded-lg bg-error-container/20 text-error px-4 py-3 text-sm">
          {error}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 bg-surface rounded-xl border border-surface-container-high p-5">
        <h2 className="col-span-2 text-sm font-semibold text-on-surface-variant uppercase tracking-wide">
          Identification
        </h2>

        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-on-surface-variant">Matricule</label>
          <Input
            placeholder="Ex: 12345-A-7"
            value={form.matricule ?? ''}
            onChange={(e) => set('matricule', e.target.value)}
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-on-surface-variant">Type *</label>
          <select
            required
            value={form.type}
            onChange={(e) => set('type', e.target.value)}
            className="h-10 rounded-lg border border-outline-variant bg-surface px-3 text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary"
          >
            {VEHICLE_TYPES.map((t) => <option key={t}>{t}</option>)}
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-on-surface-variant">Marque / Modèle</label>
          <Input
            placeholder="Ex: Mercedes Sprinter"
            value={form.brand_model ?? ''}
            onChange={(e) => set('brand_model', e.target.value)}
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-on-surface-variant">Capacité (places) *</label>
          <Input
            type="number"
            min={1}
            max={200}
            required
            value={form.capacity}
            onChange={(e) => set('capacity', parseInt(e.target.value) || 1)}
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-on-surface-variant">Date mise en circulation</label>
          <Input
            type="date"
            value={form.circulation_date ?? ''}
            onChange={(e) => set('circulation_date', e.target.value)}
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-on-surface-variant">Année (si date inconnue)</label>
          <Input
            type="number"
            min={1980}
            max={2035}
            placeholder="Ex: 2022"
            value={form.year ?? ''}
            onChange={(e) => set('year', e.target.value ? parseInt(e.target.value) : null)}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 bg-surface rounded-xl border border-surface-container-high p-5">
        <h2 className="col-span-2 text-sm font-semibold text-on-surface-variant uppercase tracking-wide">
          Prestataire & Propriété
        </h2>

        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-on-surface-variant">Prestataire (SOTREG, STCR, CTM…)</label>
          <Input
            placeholder="Ex: SOTREG"
            value={form.prestataire ?? ''}
            onChange={(e) => set('prestataire', e.target.value)}
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-on-surface-variant">Type de propriété</label>
          <select
            value={form.owner_type ?? ''}
            onChange={(e) => set('owner_type', e.target.value)}
            className="h-10 rounded-lg border border-outline-variant bg-surface px-3 text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">— Sélectionner —</option>
            {OWNER_TYPES.map((t) => <option key={t}>{t}</option>)}
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-on-surface-variant">Site d'affectation</label>
          <select
            value={form.site_id ?? ''}
            onChange={(e) => set('site_id', e.target.value)}
            className="h-10 rounded-lg border border-outline-variant bg-surface px-3 text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">— Aucun site —</option>
            {sites.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-on-surface-variant">État</label>
          <select
            value={form.condition}
            onChange={(e) => set('condition', e.target.value)}
            className="h-10 rounded-lg border border-outline-variant bg-surface px-3 text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary"
          >
            {CONDITIONS.map((c) => <option key={c}>{c}</option>)}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 bg-surface rounded-xl border border-surface-container-high p-5">
        <h2 className="col-span-2 text-sm font-semibold text-on-surface-variant uppercase tracking-wide">
          Coûts & Consommation
        </h2>

        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-on-surface-variant">Coût mensuel (MAD)</label>
          <Input
            type="number"
            min={0}
            step={0.01}
            placeholder="Ex: 12500"
            value={form.monthly_cost_mad ?? ''}
            onChange={(e) => set('monthly_cost_mad', e.target.value ? parseFloat(e.target.value) : null)}
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-on-surface-variant">Km mensuels</label>
          <Input
            type="number"
            min={0}
            step={0.01}
            placeholder="Ex: 3200"
            value={form.monthly_km ?? ''}
            onChange={(e) => set('monthly_km', e.target.value ? parseFloat(e.target.value) : null)}
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-on-surface-variant">Consommation gasoil (L/100 km)</label>
          <Input
            type="number"
            min={0}
            step={0.1}
            placeholder="Ex: 12.5"
            value={form.fuel_consumption ?? ''}
            onChange={(e) => set('fuel_consumption', e.target.value ? parseFloat(e.target.value) : null)}
          />
        </div>

        <div className="flex items-center gap-2 pt-5">
          <input
            type="checkbox"
            id="pmr"
            checked={form.is_pmr_accessible ?? false}
            onChange={(e) => set('is_pmr_accessible', e.target.checked)}
            className="w-4 h-4 accent-primary"
          />
          <label htmlFor="pmr" className="text-sm text-on-surface">Accessible PMR</label>
        </div>
      </div>

      <div className="flex flex-col gap-1 bg-surface rounded-xl border border-surface-container-high p-5">
        <label className="text-xs font-medium text-on-surface-variant">Observations</label>
        <textarea
          rows={3}
          className="rounded-lg border border-outline-variant bg-surface px-3 py-2 text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary resize-none"
          value={form.observations ?? ''}
          onChange={(e) => set('observations', e.target.value)}
        />
      </div>

      <div className="flex gap-3">
        <Button type="submit" disabled={saving}>
          {saving ? 'Enregistrement…' : isEdit ? 'Mettre à jour' : 'Créer le véhicule'}
        </Button>
        <Button variant="secondary" type="button" onClick={() => navigate('/vehicles')}>
          Annuler
        </Button>
      </div>
    </form>
  );
}
