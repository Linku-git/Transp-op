import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useSiteStore } from '@/stores/siteStore';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { DataTable, type Column } from '@/components/ui/DataTable';
import type { Site, SecurityProfile } from '@/types/site';
import { exportSitesCSV, importSitesCSV, type ImportCSVResult } from '@/api/sites';

const PAGE_SIZE = 20;

function SecurityChip({ profile }: { profile: SecurityProfile }) {
  const { t } = useTranslation();

  const labelMap: Record<SecurityProfile, string> = {
    normal: t('sites.security.normal', 'Normal'),
    elevated: t('sites.security.elevated', 'Eleve'),
    critical: t('sites.security.critical', 'Critique'),
  };

  const levelMap: Record<SecurityProfile, string> = {
    normal: 'Level 1',
    elevated: 'Level 2',
    critical: 'Level 3',
  };

  const iconColorMap: Record<SecurityProfile, string> = {
    normal: 'text-green-600',
    elevated: 'text-amber-600',
    critical: 'text-error',
  };

  return (
    <div className="flex items-center gap-1.5">
      <span className={`material-symbols-outlined text-sm ${iconColorMap[profile]}`}>verified_user</span>
      <span className="text-xs font-sans font-medium text-on-surface-variant" title={labelMap[profile]}>
        {levelMap[profile]}
      </span>
    </div>
  );
}

function ZfeDot({ compliant }: { compliant: boolean }) {
  return (
    <div className="flex items-center gap-1.5">
      <span className={`w-2 h-2 rounded-full ${compliant ? 'bg-green-500' : 'bg-amber-500'}`} />
      <span className={`inline-block rounded-full px-2 py-0.5 text-[10px] font-bold font-sans uppercase tracking-wider ${compliant ? 'bg-green-50 text-green-700' : 'bg-amber-50 text-amber-700'}`}>
        {compliant ? 'ZFE' : 'Non-ZFE'}
      </span>
    </div>
  );
}

function ShiftCircles({ count }: { count: number }) {
  const labels = ['M', 'A', 'N'];
  const colors = [
    'bg-blue-100 text-blue-700',
    'bg-amber-100 text-amber-700',
    'bg-indigo-100 text-indigo-700',
  ];
  return (
    <div className="flex items-center gap-1">
      {Array.from({ length: count }, (_, i) => (
        <span
          key={i}
          className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-black ${colors[i % colors.length]}`}
        >
          {labels[i % labels.length]}
        </span>
      ))}
    </div>
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

  const [isExporting, setIsExporting] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [importResult, setImportResult] = useState<ImportCSVResult | null>(null);
  const [importError, setImportError] = useState<string | null>(null);
  const importFileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchSites({ page, page_size: PAGE_SIZE });
  }, [fetchSites, page]);

  const handleExportCSV = useCallback(async () => {
    setIsExporting(true);
    try {
      await exportSitesCSV();
    } catch {
      // silent — browser will show nothing downloaded
    } finally {
      setIsExporting(false);
    }
  }, []);

  const handleImportFile = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      e.target.value = '';
      setImportResult(null);
      setImportError(null);
      setIsImporting(true);
      try {
        const result = await importSitesCSV(file);
        setImportResult(result);
        fetchSites({ page: 1, page_size: PAGE_SIZE });
        setPage(1);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Import failed';
        setImportError(msg);
      } finally {
        setIsImporting(false);
      }
    },
    [fetchSites],
  );

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
            className="font-mono font-bold text-primary hover:underline"
          >
            {row.code}
          </Link>
        ),
      },
      {
        key: 'name',
        label: t('sites.columns.name', 'Nom'),
        render: (row) => (
          <span className="font-sans font-medium text-on-surface">{row.name}</span>
        ),
      },
      {
        key: 'city',
        label: t('sites.columns.city', 'Ville'),
      },
      {
        key: 'num_shifts',
        label: t('sites.columns.shifts', 'Equipes'),
        render: (row) => <ShiftCircles count={row.num_shifts} />,
      },
      {
        key: 'zfe_zone',
        label: t('sites.columns.zfe', 'ZFE'),
        render: (row) => <ZfeDot compliant={row.zfe_zone} />,
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
          <div className="flex items-center gap-1 justify-end opacity-0 group-hover:opacity-100 transition-opacity">
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
            <button
              className="p-1.5 rounded-md hover:bg-surface-container transition-colors"
              onClick={() => handleDelete(row.id, row.name)}
              title={t('common.delete')}
            >
              <span className="material-symbols-outlined text-base text-on-surface-variant">more_vert</span>
            </button>
          </div>
        ),
      },
    ],
    [t, navigate, handleDelete],
  );

  const totalPages = meta?.pages ?? 1;

  return (
    <div className="flex flex-col gap-8">
      {/* Page header */}
      <div className="flex items-end justify-between">
        <div>
          <h1 className="font-sans text-3xl font-black text-on-surface tracking-tight">
            {t('nav.sites')}
          </h1>
          <p className="text-sm text-on-surface-variant font-sans mt-1">
            {t('sites.description', 'Gestion et configuration des sites industriels')}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Hidden file input for CSV import */}
          <input
            ref={importFileRef}
            type="file"
            accept=".csv"
            className="hidden"
            onChange={handleImportFile}
          />

          <Button
            variant="secondary"
            size="md"
            onClick={() => importFileRef.current?.click()}
            disabled={isImporting}
          >
            <span className="material-symbols-outlined text-base mr-1.5">
              {isImporting ? 'sync' : 'upload'}
            </span>
            {isImporting ? t('common.importing', 'Import...') : t('common.import_csv', 'Import CSV')}
          </Button>

          <Button
            variant="secondary"
            size="md"
            onClick={handleExportCSV}
            disabled={isExporting}
          >
            <span className="material-symbols-outlined text-base mr-1.5">
              {isExporting ? 'sync' : 'download'}
            </span>
            {isExporting ? t('common.exporting', 'Export...') : t('common.export_csv', 'Export CSV')}
          </Button>

          <Link to="/sites/new">
            <Button>
              <span className="material-symbols-outlined text-base mr-1.5">add_location</span>
              {t('sites.add', 'Ajouter un site')}
            </Button>
          </Link>
        </div>
      </div>

      {/* Import result banner */}
      {importResult && (
        <div className="flex items-start gap-3 bg-green-50 border border-green-200 rounded-xl px-4 py-3">
          <span className="material-symbols-outlined text-green-600 text-lg mt-0.5">check_circle</span>
          <div className="flex-1">
            <p className="text-sm font-sans font-semibold text-green-800">
              {t('sites.import_success', 'Import terminé')}
            </p>
            <p className="text-xs text-green-700 font-sans mt-0.5">
              {importResult.created} {t('sites.import_created', 'créé(s)')},&nbsp;
              {importResult.updated} {t('sites.import_updated', 'mis à jour')},&nbsp;
              {importResult.skipped} {t('sites.import_skipped', 'ignoré(s)')}
            </p>
            {importResult.errors.length > 0 && (
              <ul className="mt-1 list-disc list-inside text-xs text-amber-700 font-sans">
                {importResult.errors.slice(0, 5).map((e, i) => (
                  <li key={i}>{e}</li>
                ))}
                {importResult.errors.length > 5 && (
                  <li>…et {importResult.errors.length - 5} autre(s)</li>
                )}
              </ul>
            )}
          </div>
          <button
            onClick={() => setImportResult(null)}
            className="text-green-600 hover:text-green-800 transition-colors"
          >
            <span className="material-symbols-outlined text-base">close</span>
          </button>
        </div>
      )}

      {/* Import error banner */}
      {importError && (
        <div className="flex items-start gap-3 bg-error-container border border-error/20 rounded-xl px-4 py-3">
          <span className="material-symbols-outlined text-error text-lg mt-0.5">error</span>
          <p className="flex-1 text-sm font-sans text-error">{importError}</p>
          <button
            onClick={() => setImportError(null)}
            className="text-error hover:opacity-70 transition-opacity"
          >
            <span className="material-symbols-outlined text-base">close</span>
          </button>
        </div>
      )}

      {/* Bento grid: mini stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="md:col-span-2 bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-4 overflow-hidden relative" style={{ minHeight: '120px' }}>
          <div className="absolute inset-0 bg-surface-container-low opacity-40 rounded-xl" />
          <div className="relative z-10">
            <span className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant font-sans">
              {t('sites.map_preview', 'Apercu carte')}
            </span>
            <p className="text-sm text-on-surface-variant font-sans mt-2">
              {t('sites.total_count', '{{count}} sites actifs', { count: meta?.total ?? filteredSites.length })}
            </p>
          </div>
        </div>
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-5 hover:bg-surface-bright transition-colors">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-full bg-green-50 flex items-center justify-center">
              <span className="material-symbols-outlined text-lg text-green-600">verified</span>
            </div>
            <div>
              <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest font-sans block">
                {t('sites.compliance_rate', 'Taux conformite')}
              </span>
              <span className="text-2xl font-black text-on-surface font-sans tabular-nums">
                {filteredSites.length > 0 ? `${Math.round((filteredSites.filter(s => s.zfe_zone).length / filteredSites.length) * 100)}%` : '--'}
              </span>
            </div>
          </div>
        </div>
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-5 hover:bg-surface-bright transition-colors">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
              <span className="material-symbols-outlined text-lg text-primary">schedule</span>
            </div>
            <div>
              <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest font-sans block">
                {t('sites.active_shifts', 'Equipes actives')}
              </span>
              <span className="text-2xl font-black text-on-surface font-sans tabular-nums">
                {filteredSites.reduce((sum, s) => sum + s.num_shifts, 0)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Filter bar */}
      <div className="bg-surface-container-low rounded-xl p-4">
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
          <label className="flex items-center gap-2 cursor-pointer select-none py-2 px-3 rounded-lg hover:bg-surface-container transition-colors">
            <input
              type="checkbox"
              checked={zfeFilter}
              onChange={(e) => setZfeFilter(e.target.checked)}
              className="w-4 h-4 rounded accent-primary"
            />
            <span className="text-sm font-sans font-medium text-on-surface-variant">
              {t('sites.filter_zfe', 'ZFE uniquement')}
            </span>
          </label>
          <button className="flex items-center gap-1.5 px-4 py-2.5 rounded-lg bg-surface-container hover:bg-surface-container-high transition-colors text-sm font-sans font-medium text-on-surface-variant">
            <span className="material-symbols-outlined text-base">tune</span>
            {t('common.filters', 'Filtres')}
          </button>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="bg-error-container rounded-xl p-4">
          <p className="text-error text-sm font-sans">{error}</p>
        </div>
      )}

      {/* Table */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
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
        <div className="flex items-center justify-between">
          <p className="text-xs text-on-surface-variant font-sans">
            {t('sites.pagination_showing', 'Showing {{from}}-{{to}} of {{total}}', {
              from: (page - 1) * PAGE_SIZE + 1,
              to: Math.min(page * PAGE_SIZE, meta?.total ?? 0),
              total: meta?.total ?? 0,
            })}
          </p>
          <div className="flex items-center gap-1">
            <button
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="w-8 h-8 rounded-lg flex items-center justify-center text-on-surface-variant hover:bg-surface-container disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <span className="material-symbols-outlined text-lg">chevron_left</span>
            </button>
            {Array.from({ length: totalPages }, (_, i) => i + 1)
              .filter((p) => {
                return p === 1 || p === totalPages || Math.abs(p - page) <= 1;
              })
              .map((p, idx, arr) => {
                const prev = arr[idx - 1];
                const showEllipsis = prev !== undefined && p - prev > 1;
                return (
                  <span key={p} className="flex items-center">
                    {showEllipsis && (
                      <span className="text-on-surface-variant text-xs px-1">...</span>
                    )}
                    <button
                      onClick={() => setPage(p)}
                      className={[
                        'w-8 h-8 rounded-lg text-xs font-sans font-bold transition-colors',
                        p === page
                          ? 'bg-primary text-on-primary'
                          : 'text-on-surface-variant hover:bg-surface-container',
                      ].join(' ')}
                    >
                      {p}
                    </button>
                  </span>
                );
              })}
            <button
              disabled={page >= totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              className="w-8 h-8 rounded-lg flex items-center justify-center text-on-surface-variant hover:bg-surface-container disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <span className="material-symbols-outlined text-lg">chevron_right</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
