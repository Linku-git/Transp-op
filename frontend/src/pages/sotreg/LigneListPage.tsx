import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { listLignes, deleteLigne } from '@/api/sotreg';
import { extractApiError } from '@/lib/apiError';
import type { Ligne, LigneListParams, LigneListMeta } from '@/types/sotreg';
import { SERVICE_TYPE_LABELS } from '@/types/sotreg';

const PAGE_SIZE = 20;

const SERVICE_TYPE_BADGE_STYLES: Record<string, string> = {
  navette: 'bg-primary/10 text-primary',
  liaison: 'bg-green-50 text-green-700',
  vip: 'bg-amber-50 text-amber-700',
  mixte: 'bg-slate-100 text-slate-700',
};

function formatNumber(n: number | null | undefined): string {
  if (n == null) return '--';
  return n.toLocaleString('fr-FR');
}

function formatKm(n: number | null | undefined): string {
  if (n == null) return '--';
  return `${n.toLocaleString('fr-FR', { maximumFractionDigits: 1 })} km`;
}

export function LigneListPage() {
  const [lignes, setLignes] = useState<Ligne[]>([]);
  const [meta, setMeta] = useState<LigneListMeta | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [page, setPage] = useState(1);
  const [serviceTypeFilter, setServiceTypeFilter] = useState<string>('');
  const [isActiveFilter, setIsActiveFilter] = useState<string>('');
  const [search, setSearch] = useState('');

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params: LigneListParams = { page, page_size: PAGE_SIZE };
      if (serviceTypeFilter) {
        params.service_type = serviceTypeFilter;
      }
      if (isActiveFilter === 'true') {
        params.is_active = true;
      } else if (isActiveFilter === 'false') {
        params.is_active = false;
      }
      const response = await listLignes(params);
      setLignes(response.data);
      setMeta(response.meta);
    } catch (err) {
      setError(extractApiError(err, 'Erreur lors du chargement des lignes'));
    } finally {
      setIsLoading(false);
    }
  }, [page, serviceTypeFilter, isActiveFilter]);

  useEffect(() => {
    void fetchData();
  }, [fetchData]);

  const handleDelete = useCallback(
    async (id: string, code: string) => {
      if (!confirm(`Supprimer la ligne "${code}" ?`)) return;
      try {
        await deleteLigne(id);
        void fetchData();
      } catch (err) {
        setError(extractApiError(err, 'Erreur lors de la suppression'));
      }
    },
    [fetchData],
  );

  const filtered = search.trim()
    ? lignes.filter((l) => {
        const q = search.toLowerCase();
        return (
          l.code.toLowerCase().includes(q) ||
          l.name.toLowerCase().includes(q)
        );
      })
    : lignes;

  return (
    <div className="flex flex-col gap-6">
      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-sans text-2xl font-bold text-on-surface">
            Lignes de Transport
          </h1>
          <p className="text-sm text-on-surface-variant mt-1">
            Gestion des lignes de transport SOTREG
          </p>
        </div>
        <Link
          to="/sotreg/lignes/new"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-gradient-to-br from-primary to-primary-container text-on-primary text-sm font-medium shadow-lg shadow-primary/20 hover:shadow-xl transition-all"
        >
          <span className="material-symbols-outlined text-[18px]">add</span>
          Nouvelle Ligne
        </Link>
      </div>

      {/* ── Filter bar ──────────────────────────────────────────────────── */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant/50 text-[18px]">
            search
          </span>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Rechercher par code ou nom..."
            className="w-full pl-10 pr-4 py-2.5 bg-surface-container-high/50 border-none rounded-lg text-sm text-on-surface outline-none focus:ring-2 focus:ring-primary/20"
          />
        </div>
        <select
          value={serviceTypeFilter}
          onChange={(e) => {
            setServiceTypeFilter(e.target.value);
            setPage(1);
          }}
          className="bg-surface-container-high/50 border-none rounded-lg px-3 py-2.5 text-sm text-on-surface outline-none focus:ring-2 focus:ring-primary/20 appearance-none min-w-[160px]"
        >
          <option value="">Tous les types</option>
          {Object.entries(SERVICE_TYPE_LABELS).map(([val, label]) => (
            <option key={val} value={val}>
              {label}
            </option>
          ))}
        </select>
        <select
          value={isActiveFilter}
          onChange={(e) => {
            setIsActiveFilter(e.target.value);
            setPage(1);
          }}
          className="bg-surface-container-high/50 border-none rounded-lg px-3 py-2.5 text-sm text-on-surface outline-none focus:ring-2 focus:ring-primary/20 appearance-none min-w-[140px]"
        >
          <option value="">Tous les statuts</option>
          <option value="true">Actif</option>
          <option value="false">Inactif</option>
        </select>
      </div>

      {/* ── Error ───────────────────────────────────────────────────────── */}
      {error && (
        <div className="rounded-lg bg-error-container/30 px-4 py-3 text-sm text-error flex items-center gap-2">
          <span className="material-symbols-outlined text-[18px]">error</span>
          {error}
        </div>
      )}

      {/* ── Table ───────────────────────────────────────────────────────── */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center py-16 text-on-surface-variant text-sm gap-2">
            <span className="material-symbols-outlined animate-spin text-primary">
              progress_activity
            </span>
            Chargement des lignes...
          </div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 gap-2">
            <span className="material-symbols-outlined text-4xl text-on-surface-variant/40">
              route
            </span>
            <p className="text-sm text-on-surface-variant">
              Aucune ligne de transport trouvee
            </p>
            {(search || serviceTypeFilter || isActiveFilter) && (
              <button
                type="button"
                onClick={() => {
                  setSearch('');
                  setServiceTypeFilter('');
                  setIsActiveFilter('');
                  setPage(1);
                }}
                className="mt-2 text-xs text-primary hover:underline"
              >
                Reinitialiser les filtres
              </button>
            )}
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="bg-surface-container-low/50">
                <th className="text-left text-[10px] font-black uppercase tracking-widest text-on-surface-variant px-5 py-3">
                  Code
                </th>
                <th className="text-left text-[10px] font-black uppercase tracking-widest text-on-surface-variant px-5 py-3">
                  Nom
                </th>
                <th className="text-left text-[10px] font-black uppercase tracking-widest text-on-surface-variant px-5 py-3">
                  Type de service
                </th>
                <th className="text-right text-[10px] font-black uppercase tracking-widest text-on-surface-variant px-5 py-3">
                  Distance
                </th>
                <th className="text-right text-[10px] font-black uppercase tracking-widest text-on-surface-variant px-5 py-3">
                  Rotations/jour
                </th>
                <th className="text-right text-[10px] font-black uppercase tracking-widest text-on-surface-variant px-5 py-3">
                  Km annuels
                </th>
                <th className="text-left text-[10px] font-black uppercase tracking-widest text-on-surface-variant px-5 py-3">
                  Motorisation
                </th>
                <th className="text-left text-[10px] font-black uppercase tracking-widest text-on-surface-variant px-5 py-3">
                  Statut
                </th>
                <th className="text-right text-[10px] font-black uppercase tracking-widest text-on-surface-variant px-5 py-3">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {filtered.map((ligne) => (
                <tr
                  key={ligne.id}
                  className="hover:bg-surface-bright transition-colors group"
                >
                  {/* Code */}
                  <td className="px-5 py-3.5">
                    <span className="text-sm font-semibold text-on-surface">
                      {ligne.code}
                    </span>
                  </td>

                  {/* Nom */}
                  <td className="px-5 py-3.5">
                    <span className="text-sm text-on-surface">
                      {ligne.name}
                    </span>
                  </td>

                  {/* Type de service */}
                  <td className="px-5 py-3.5">
                    <span
                      className={[
                        'inline-block px-2.5 py-0.5 rounded-full text-xs font-medium',
                        SERVICE_TYPE_BADGE_STYLES[ligne.service_type] ??
                          'bg-slate-100 text-slate-700',
                      ].join(' ')}
                    >
                      {SERVICE_TYPE_LABELS[ligne.service_type] ??
                        ligne.service_type}
                    </span>
                  </td>

                  {/* Distance */}
                  <td className="px-5 py-3.5 text-right">
                    <span className="text-sm text-on-surface tabular-nums">
                      {formatKm(ligne.distance_km)}
                    </span>
                  </td>

                  {/* Rotations/jour */}
                  <td className="px-5 py-3.5 text-right">
                    <span className="text-sm text-on-surface tabular-nums">
                      {ligne.rotations_per_day}
                    </span>
                  </td>

                  {/* Km annuels */}
                  <td className="px-5 py-3.5 text-right">
                    <span className="text-sm text-on-surface-variant tabular-nums">
                      {formatNumber(ligne.km_annual)}
                    </span>
                  </td>

                  {/* Motorisation */}
                  <td className="px-5 py-3.5">
                    <span className="text-sm text-on-surface-variant capitalize">
                      {ligne.motorization ?? '--'}
                    </span>
                  </td>

                  {/* Statut */}
                  <td className="px-5 py-3.5">
                    {ligne.is_active ? (
                      <span className="inline-block px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-50 text-green-700">
                        Actif
                      </span>
                    ) : (
                      <span className="inline-block px-2.5 py-0.5 rounded-full text-xs font-medium bg-error-container/30 text-error">
                        Inactif
                      </span>
                    )}
                  </td>

                  {/* Actions */}
                  <td className="px-5 py-3.5">
                    <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Link
                        to={`/sotreg/lignes/${ligne.id}/edit`}
                        title="Modifier"
                        className="inline-flex items-center justify-center w-8 h-8 rounded-md text-on-surface-variant hover:bg-surface-container-high/50 transition-colors"
                      >
                        <span className="material-symbols-outlined text-[18px]">
                          edit
                        </span>
                      </Link>
                      <button
                        type="button"
                        onClick={() => handleDelete(ligne.id, ligne.code)}
                        title="Supprimer"
                        className="inline-flex items-center justify-center w-8 h-8 rounded-md text-error hover:bg-error-container/20 transition-colors"
                      >
                        <span className="material-symbols-outlined text-[18px]">
                          delete
                        </span>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* ── Pagination ──────────────────────────────────────────────────── */}
      {meta && meta.pages > 1 && (
        <div className="flex items-center justify-between text-sm text-on-surface-variant">
          <span>
            Page {meta.page} / {meta.pages} ({meta.total} lignes)
          </span>
          <div className="flex gap-2">
            <button
              type="button"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-container-lowest border border-outline-variant/15 text-sm hover:bg-surface-container-low transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <span className="material-symbols-outlined text-[16px]">
                chevron_left
              </span>
              Precedent
            </button>
            <button
              type="button"
              disabled={page >= meta.pages}
              onClick={() => setPage((p) => p + 1)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-container-lowest border border-outline-variant/15 text-sm hover:bg-surface-container-low transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Suivant
              <span className="material-symbols-outlined text-[16px]">
                chevron_right
              </span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
