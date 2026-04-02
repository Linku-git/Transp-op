import { useEffect, useState, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  listVehicles,
  deleteVehicle,
} from '@/api/vehicles';
import type { Vehicle } from '@/types/vehicle';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

const PAGE_SIZE = 20;

function conditionBadge(c: string) {
  const map: Record<string, string> = {
    Bon: 'bg-green-100 text-green-700',
    Moyen: 'bg-yellow-100 text-yellow-700',
    Mauvais: 'bg-red-100 text-red-700',
  };
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${map[c] ?? 'bg-surface-container text-on-surface-variant'}`}>
      {c}
    </span>
  );
}

export function VehicleListPage() {
  const navigate = useNavigate();
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchVehicles = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listVehicles({ page, page_size: PAGE_SIZE });
      setVehicles(res.items ?? []);
      setTotal(res.total ?? 0);
    } catch {
      setError('Impossible de charger les véhicules');
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => {
    fetchVehicles();
  }, [fetchVehicles]);

  const filtered = search.trim()
    ? vehicles.filter((v) => {
        const q = search.toLowerCase();
        return (
          v.matricule?.toLowerCase().includes(q) ||
          v.type.toLowerCase().includes(q) ||
          v.brand_model?.toLowerCase().includes(q) ||
          v.prestataire?.toLowerCase().includes(q)
        );
      })
    : vehicles;

  const handleDelete = async (id: string) => {
    if (!confirm('Supprimer ce véhicule ?')) return;
    setDeletingId(id);
    try {
      await deleteVehicle(id);
      await fetchVehicles();
    } catch {
      alert('Erreur lors de la suppression');
    } finally {
      setDeletingId(null);
    }
  };

  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">Parc Véhicule</h1>
          <p className="text-sm text-on-surface-variant mt-0.5">
            {total} véhicule{total !== 1 ? 's' : ''} enregistré{total !== 1 ? 's' : ''}
          </p>
        </div>
        <Button onClick={() => navigate('/vehicles/new')}>
          <span className="material-symbols-outlined text-base">add</span>
          Ajouter un véhicule
        </Button>
      </div>

      {/* Sub-nav: fleet section tabs */}
      <div className="flex gap-2 border-b border-surface-container-high pb-3">
        <Link to="/vehicles" className="text-sm font-medium text-primary border-b-2 border-primary pb-1 px-1">
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
      </div>

      {/* Search */}
      <div className="max-w-sm">
        <Input
          placeholder="Rechercher par matricule, type, prestataire…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-lg bg-error-container/20 text-error px-4 py-3 text-sm">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-surface-container-high bg-surface">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-surface-container-high bg-surface-container-low">
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Matricule</th>
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Type</th>
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Marque / Modèle</th>
              <th className="px-4 py-3 text-right font-semibold text-on-surface-variant">Capacité</th>
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Mise en circ.</th>
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Prestataire</th>
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">État</th>
              <th className="px-4 py-3 text-left font-semibold text-on-surface-variant">Site</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={9} className="text-center py-10 text-on-surface-variant text-sm">
                  Chargement…
                </td>
              </tr>
            )}
            {!loading && filtered.length === 0 && (
              <tr>
                <td colSpan={9} className="text-center py-10 text-on-surface-variant text-sm">
                  Aucun véhicule trouvé
                </td>
              </tr>
            )}
            {filtered.map((v) => (
              <tr
                key={v.id}
                className="border-b border-surface-container-high hover:bg-surface-container-low/50 transition-colors"
              >
                <td className="px-4 py-3 font-mono font-medium text-on-surface">
                  {v.matricule ?? <span className="text-on-surface-variant italic">—</span>}
                </td>
                <td className="px-4 py-3 text-on-surface">{v.type}</td>
                <td className="px-4 py-3 text-on-surface-variant">{v.brand_model ?? '—'}</td>
                <td className="px-4 py-3 text-right text-on-surface font-medium">{v.capacity}</td>
                <td className="px-4 py-3 text-on-surface-variant">
                  {v.circulation_date
                    ? new Date(v.circulation_date).toLocaleDateString('fr-FR')
                    : v.year ?? '—'}
                </td>
                <td className="px-4 py-3 text-on-surface-variant">{v.prestataire ?? '—'}</td>
                <td className="px-4 py-3">{conditionBadge(v.condition)}</td>
                <td className="px-4 py-3 text-on-surface-variant text-xs">{v.site_name ?? '—'}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1 justify-end">
                    <button
                      onClick={() => navigate(`/vehicles/${v.id}`)}
                      className="p-1 rounded hover:bg-surface-container text-on-surface-variant hover:text-on-surface"
                      title="Voir détail"
                    >
                      <span className="material-symbols-outlined text-base">visibility</span>
                    </button>
                    <button
                      onClick={() => navigate(`/vehicles/${v.id}/edit`)}
                      className="p-1 rounded hover:bg-surface-container text-on-surface-variant hover:text-on-surface"
                      title="Modifier"
                    >
                      <span className="material-symbols-outlined text-base">edit</span>
                    </button>
                    <button
                      onClick={() => handleDelete(v.id)}
                      disabled={deletingId === v.id}
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

      {/* Pagination */}
      {pages > 1 && (
        <div className="flex items-center gap-2 justify-end">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1.5 rounded border text-sm disabled:opacity-40 hover:bg-surface-container"
          >
            Précédent
          </button>
          <span className="text-sm text-on-surface-variant">
            Page {page} / {pages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(pages, p + 1))}
            disabled={page === pages}
            className="px-3 py-1.5 rounded border text-sm disabled:opacity-40 hover:bg-surface-container"
          >
            Suivant
          </button>
        </div>
      )}
    </div>
  );
}
