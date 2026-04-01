import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useSiteStore } from '@/stores/siteStore';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { DataTable, type Column } from '@/components/ui/DataTable';
import type { Site, SecurityProfile } from '@/types/site';

const PAGE_SIZE = 20;

function SecurityChip({ profile }: { profile: SecurityProfile }) {
  const { t } = useTranslation();

  const labelMap: Record<SecurityProfile, string> = {
    normal: t('sites.security.normal', 'Normal'),
    elevated: t('sites.security.elevated', 'Eleve'),
    critical: t('sites.security.critical', 'Critique'),
  };

  const classMap: Record<SecurityProfile, string> = {
    normal: 'bg-surface-container text-on-surface-variant',
    elevated: 'bg-secondary-container text-on-secondary-container',
    critical: 'bg-error-container text-error',
  };

  return (
    <span
      className={[
        'inline-block rounded-md px-2 py-0.5 text-xs font-sans font-medium',
        classMap[profile],
      ].join(' ')}
    >
      {labelMap[profile]}
    </span>
  );
}

function ZfeChip() {
  return (
    <span className="inline-block rounded-md bg-secondary-container text-on-secondary-container px-2 py-0.5 text-xs font-sans font-medium">
      ZFE
    </span>
  );
}

export function SiteListPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { sites, meta, isLoading, error, fetchSites, deleteSite } =
    useSiteStore();

  const [search, setSearch] = useState('');
  const [cityFilter, setCityFilter] = useState('');
  const [zfeFilter, setZfeFilter] = useState(false);
  const [page, setPage] = useState(1);

  useEffect(() => {
    fetchSites({ page, page_size: PAGE_SIZE });
  }, [fetchSites, page]);

  const filteredSites = useMemo(() => {
    let result = sites;

    if (search.trim()) {
      const term = search.trim().toLowerCase();
      result = result.filter(
        (s) =>
          s.code.toLowerCase().includes(term) ||
          s.name.toLowerCase().includes(term),
      );
    }

    if (cityFilter.trim()) {
      const city = cityFilter.trim().toLowerCase();
      result = result.filter((s) => s.city.toLowerCase().includes(city));
    }

    if (zfeFilter) {
      result = result.filter((s) => s.zfe_zone);
    }

    return result;
  }, [sites, search, cityFilter, zfeFilter]);

  const handleDelete = useCallback(
    async (id: string, name: string) => {
      const confirmed = window.confirm(
        t('sites.delete_confirm', 'Supprimer le site "{{name}}" ?', { name }),
      );
      if (confirmed) {
        await deleteSite(id);
      }
    },
    [deleteSite, t],
  );

  const columns: Column<Site>[] = useMemo(
    () => [
      {
        key: 'code',
        label: t('sites.columns.code', 'Code'),
        render: (row) => (
          <Link
            to={`/sites/${row.id}`}
            className="text-secondary font-medium hover:underline"
          >
            {row.code}
          </Link>
        ),
      },
      {
        key: 'name',
        label: t('sites.columns.name', 'Nom'),
      },
      {
        key: 'city',
        label: t('sites.columns.city', 'Ville'),
      },
      {
        key: 'num_shifts',
        label: t('sites.columns.shifts', 'Equipes'),
        align: 'right' as const,
        render: (row) => <span className="tabular-nums">{row.num_shifts}</span>,
      },
      {
        key: 'zfe_zone',
        label: t('sites.columns.zfe', 'ZFE'),
        render: (row) => (row.zfe_zone ? <ZfeChip /> : null),
      },
      {
        key: 'security_profile',
        label: t('sites.columns.security', 'Securite'),
        render: (row) => <SecurityChip profile={row.security_profile} />,
      },
      {
        key: 'actions',
        label: '',
        render: (row) => (
          <div className="flex items-center gap-2 justify-end">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate(`/sites/${row.id}`)}
            >
              {t('common.view', 'Voir')}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate(`/sites/${row.id}/edit`)}
            >
              {t('common.edit')}
            </Button>
            <Button
              variant="danger"
              size="sm"
              onClick={() => handleDelete(row.id, row.name)}
            >
              {t('common.delete')}
            </Button>
          </div>
        ),
      },
    ],
    [t, navigate, handleDelete],
  );

  const totalPages = meta?.pages ?? 1;

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="font-display text-2xl font-bold text-on-surface">
          {t('nav.sites')}
        </h1>
        <Link to="/sites/new">
          <Button>{t('sites.add', 'Ajouter un site')}</Button>
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-surface-container-lowest rounded-lg p-4 mb-6">
        <div className="flex flex-wrap items-end gap-4">
          <div className="flex-1 min-w-[200px]">
            <Input
              placeholder={t('sites.search_placeholder', 'Rechercher par code ou nom...')}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="w-48">
            <Input
              placeholder={t('sites.filter_city', 'Filtrer par ville...')}
              value={cityFilter}
              onChange={(e) => setCityFilter(e.target.value)}
            />
          </div>
          <label className="flex items-center gap-2 cursor-pointer select-none py-2">
            <input
              type="checkbox"
              checked={zfeFilter}
              onChange={(e) => setZfeFilter(e.target.checked)}
              className="w-4 h-4 rounded accent-secondary"
            />
            <span className="text-sm font-sans text-on-surface-variant">
              {t('sites.filter_zfe', 'ZFE uniquement')}
            </span>
          </label>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="bg-error-container rounded-lg p-4 mb-6">
          <p className="text-error text-sm font-sans">{error}</p>
        </div>
      )}

      {/* Table */}
      <div className="bg-surface-container-lowest rounded-lg overflow-hidden">
        <DataTable<Site>
          columns={columns}
          data={filteredSites}
          isLoading={isLoading}
          emptyMessage={t('sites.empty', 'Aucun site')}
          rowKey={(row) => row.id}
        />
      </div>

      {/* Pagination */}
      {!isLoading && totalPages > 1 && (
        <div className="flex items-center justify-between mt-6">
          <p className="text-sm text-on-surface-variant font-sans">
            {t('sites.pagination_info', 'Page {{page}} sur {{pages}} ({{total}} sites)', {
              page,
              pages: totalPages,
              total: meta?.total ?? 0,
            })}
          </p>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              {t('common.previous', 'Precedent')}
            </Button>
            {Array.from({ length: totalPages }, (_, i) => i + 1)
              .filter((p) => {
                /* Show first, last, and pages around current */
                return p === 1 || p === totalPages || Math.abs(p - page) <= 1;
              })
              .map((p, idx, arr) => {
                const prev = arr[idx - 1];
                const showEllipsis = prev !== undefined && p - prev > 1;
                return (
                  <span key={p} className="flex items-center gap-1">
                    {showEllipsis && (
                      <span className="text-on-surface-variant text-sm px-1">...</span>
                    )}
                    <button
                      onClick={() => setPage(p)}
                      className={[
                        'w-8 h-8 rounded-md text-sm font-sans transition-colors',
                        p === page
                          ? 'bg-secondary text-on-secondary font-medium'
                          : 'text-on-surface-variant hover:bg-surface-container',
                      ].join(' ')}
                    >
                      {p}
                    </button>
                  </span>
                );
              })}
            <Button
              variant="ghost"
              size="sm"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            >
              {t('common.next', 'Suivant')}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
