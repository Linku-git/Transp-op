import { useEffect, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { getVehicle, deleteVehicle } from '@/api/vehicles';
import type { Vehicle } from '@/types/vehicle';
import { Button } from '@/components/ui/Button';

function InfoRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs text-on-surface-variant font-medium uppercase tracking-wide">{label}</span>
      <span className="text-sm text-on-surface">{value ?? '—'}</span>
    </div>
  );
}

export function VehicleDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [vehicle, setVehicle] = useState<Vehicle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    getVehicle(id)
      .then(setVehicle)
      .catch(() => setError('Véhicule introuvable'))
      .finally(() => setLoading(false));
  }, [id]);

  const handleDelete = async () => {
    if (!vehicle) return;
    if (!confirm('Supprimer définitivement ce véhicule ?')) return;
    try {
      await deleteVehicle(vehicle.id);
      navigate('/vehicles');
    } catch {
      alert('Erreur lors de la suppression');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-40 text-on-surface-variant text-sm">
        Chargement…
      </div>
    );
  }

  if (error || !vehicle) {
    return (
      <div className="p-6 text-error text-sm">{error ?? 'Véhicule introuvable'}</div>
    );
  }

  return (
    <div className="flex flex-col gap-6 p-6 max-w-3xl">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/vehicles')}
            className="p-2 rounded-lg hover:bg-surface-container text-on-surface-variant"
          >
            <span className="material-symbols-outlined">arrow_back</span>
          </button>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">
              {vehicle.matricule ?? vehicle.type}
            </h1>
            <p className="text-sm text-on-surface-variant">{vehicle.type} · {vehicle.brand_model ?? '—'}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Link to={`/vehicles/${vehicle.id}/edit`}>
            <Button variant="secondary">
              <span className="material-symbols-outlined text-base">edit</span>
              Modifier
            </Button>
          </Link>
          <button
            onClick={handleDelete}
            className="px-3 py-2 rounded-lg text-sm font-medium text-error border border-error/30 hover:bg-error-container/20 transition-colors"
          >
            Supprimer
          </button>
        </div>
      </div>

      {/* Identification */}
      <div className="grid grid-cols-3 gap-4 bg-surface rounded-xl border border-surface-container-high p-5">
        <h2 className="col-span-3 text-sm font-semibold text-on-surface-variant uppercase tracking-wide mb-2">
          Identification
        </h2>
        <InfoRow label="Matricule" value={<span className="font-mono">{vehicle.matricule}</span>} />
        <InfoRow label="Type" value={vehicle.type} />
        <InfoRow label="Marque / Modèle" value={vehicle.brand_model} />
        <InfoRow label="Capacité" value={`${vehicle.capacity} places`} />
        <InfoRow
          label="Mise en circulation"
          value={
            vehicle.circulation_date
              ? new Date(vehicle.circulation_date).toLocaleDateString('fr-FR')
              : vehicle.year
              ? `${vehicle.year}`
              : null
          }
        />
        <InfoRow label="État" value={vehicle.condition} />
      </div>

      {/* Prestataire */}
      <div className="grid grid-cols-3 gap-4 bg-surface rounded-xl border border-surface-container-high p-5">
        <h2 className="col-span-3 text-sm font-semibold text-on-surface-variant uppercase tracking-wide mb-2">
          Prestataire & Propriété
        </h2>
        <InfoRow label="Prestataire" value={vehicle.prestataire} />
        <InfoRow label="Type de propriété" value={vehicle.owner_type} />
        <InfoRow label="Site d'affectation" value={vehicle.site_name} />
        <InfoRow label="PMR accessible" value={vehicle.is_pmr_accessible ? 'Oui' : 'Non'} />
        <InfoRow label="ZFE conforme" value={vehicle.zfe_compliant ? 'Oui' : 'Non'} />
      </div>

      {/* Coûts */}
      <div className="grid grid-cols-3 gap-4 bg-surface rounded-xl border border-surface-container-high p-5">
        <h2 className="col-span-3 text-sm font-semibold text-on-surface-variant uppercase tracking-wide mb-2">
          Coûts & Consommation
        </h2>
        <InfoRow
          label="Coût mensuel"
          value={vehicle.monthly_cost_mad != null ? `${Number(vehicle.monthly_cost_mad).toLocaleString('fr-FR')} MAD` : null}
        />
        <InfoRow
          label="Km mensuels"
          value={vehicle.monthly_km != null ? `${Number(vehicle.monthly_km).toLocaleString('fr-FR')} km` : null}
        />
        <InfoRow
          label="Consommation gasoil"
          value={vehicle.fuel_consumption != null ? `${vehicle.fuel_consumption} L/100 km` : null}
        />
        <InfoRow
          label="Coût par km"
          value={vehicle.cost_per_km != null ? `${vehicle.cost_per_km} MAD/km` : null}
        />
        <InfoRow label="Motorisation" value={vehicle.motorization} />
      </div>

      {vehicle.observations && (
        <div className="bg-surface rounded-xl border border-surface-container-high p-5">
          <h2 className="text-sm font-semibold text-on-surface-variant uppercase tracking-wide mb-2">Observations</h2>
          <p className="text-sm text-on-surface whitespace-pre-wrap">{vehicle.observations}</p>
        </div>
      )}
    </div>
  );
}
