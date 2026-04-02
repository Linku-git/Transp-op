import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useEmployeeStore } from '@/stores/employeeStore';
import { useSiteStore } from '@/stores/siteStore';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { DataTable, type Column } from '@/components/ui/DataTable';
import type { Employee, OptInChoice } from '@/types/employee';

function downloadCSV(employees: Employee[]) {
  const headers = [
    'matricule',
    'first_name',
    'last_name',
    'site_name',
    'department',
    'shift_time',
    'is_pmr',
    'active',
  ];
  const escape = (v: string | null | undefined | boolean): string => {
    const str = String(v ?? '');
    if (str.includes(',') || str.includes('"') || str.includes('\n')) {
      return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
  };
  const rows = employees.map((e) =>
    [
      e.matricule,
      e.first_name,
      e.last_name,
      e.site_name,
      e.department,
      e.shift_time,
      e.is_pmr,
      e.active,
    ]
      .map(escape)
      .join(','),
  );
  const csv = [headers.join(','), ...rows].join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = `employes_export_${new Date().toISOString().slice(0, 10)}.csv`;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}

const PAGE_SIZE = 20;

function PmrChip() {
  const { t } = useTranslation();
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-tertiary-container/30 text-tertiary px-2.5 py-0.5 text-xs font-sans font-semibold">
      <span className="material-symbols-outlined text-sm">accessible</span>
      {t('employees.badges.pmr', 'PMR')}
    </span>
  );
}

function OptInChip({ value }: { value: OptInChoice }) {
  const classMap: Record<OptInChoice, string> = {
    Oui: 'bg-secondary-container/30 text-on-secondary-container',
    Non: 'bg-surface-container-high text-on-surface-variant',
    'Sous conditions': 'bg-surface-container text-on-surface-variant',
  };

  return (
    <span
      className={[
        'inline-block rounded-full px-2.5 py-0.5 text-xs font-sans font-medium',
        classMap[value],
      ].join(' ')}
    >
      {value}
    </span>
  );
}

function SelectFilter({
  value,
  onChange,
  placeholder,
  options,
}: {
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
  options: { value: string; label: string }[];
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={[
        'w-full bg-surface-container-high/50 border-none rounded-lg p-3 text-on-surface font-sans text-sm',
        'outline-none transition-shadow duration-150 appearance-none',
        'focus:ring-2 focus:ring-primary/20',
      ].join(' ')}
    >
      <option value="">{placeholder}</option>
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  );
}

export function EmployeeListPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { employees, meta, isLoading, error, fetchEmployees, deleteEmployee } =
    useEmployeeStore();
  const { sites, fetchSites } = useSiteStore();

  const [search, setSearch] = useState('');
  const [siteFilter, setSiteFilter] = useState(
    searchParams.get('site_id') ?? '',
  );
  const [shiftFilter, setShiftFilter] = useState('');
  const [pmrFilter, setPmrFilter] = useState(false);
  const [departmentFilter, setDepartmentFilter] = useState('');
  const [activeFilter, setActiveFilter] = useState(true);
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchSites({ page: 1, page_size: 100 });
  }, [fetchSites]);

  useEffect(() => {
    fetchEmployees({
      page,
      page_size: PAGE_SIZE,
      site_id: siteFilter || undefined,
      shift_time: shiftFilter || undefined,
      is_pmr: pmrFilter || undefined,
      department: departmentFilter || undefined,
      active: activeFilter,
      q: search.trim() || undefined,
    });
  }, [fetchEmployees, page, siteFilter, shiftFilter, pmrFilter, departmentFilter, activeFilter, search]);

  /* Reset to page 1 when filters change */
  useEffect(() => {
    setPage(1);
  }, [siteFilter, shiftFilter, pmrFilter, departmentFilter, activeFilter, search]);

  const handleDelete = useCallback(
    async (id: string, name: string) => {
      const confirmed = window.confirm(
        t('employees.delete_confirm', 'Supprimer l\'employe "{{name}}" ?', {
          name,
        }),
      );
      if (confirmed) {
        await deleteEmployee(id);
        setSelected((prev) => {
          const next = new Set(prev);
          next.delete(id);
          return next;
        });
      }
    },
    [deleteEmployee, t],
  );

  const toggleSelect = useCallback((id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  const toggleSelectAll = useCallback(() => {
    setSelected((prev) => {
      if (prev.size === employees.length && employees.length > 0) {
        return new Set();
      }
      return new Set(employees.map((e) => e.id));
    });
  }, [employees]);

  const handleBulkExportCSV = useCallback(() => {
    const selectedEmployees = employees.filter((e) => selected.has(e.id));
    if (selectedEmployees.length > 0) {
      downloadCSV(selectedEmployees);
    }
  }, [employees, selected]);

  const handleBulkDelete = useCallback(async () => {
    const count = selected.size;
    const confirmed = window.confirm(
      t(
        'employees.bulk.delete_confirm',
        'Supprimer {{count}} employe(s) selectionnes ?',
        { count },
      ),
    );
    if (!confirmed) return;
    const ids = Array.from(selected);
    for (const id of ids) {
      await deleteEmployee(id);
    }
    setSelected(new Set());
  }, [selected, deleteEmployee, t]);

  const handleDeselectAll = useCallback(() => {
    setSelected(new Set());
  }, []);

  /* Clear selection when page or filters change */
  useEffect(() => {
    setSelected(new Set());
  }, [page, siteFilter, shiftFilter, pmrFilter, departmentFilter, activeFilter, search]);

  const allSelected =
    employees.length > 0 && selected.size === employees.length;

  const columns: Column<Employee>[] = useMemo(
    () => [
      {
        key: 'select',
        label: '',
        render: (row: Employee) => (
          <input
            type="checkbox"
            checked={selected.has(row.id)}
            onChange={() => toggleSelect(row.id)}
            className="w-4 h-4 rounded accent-primary cursor-pointer"
            onClick={(e) => e.stopPropagation()}
          />
        ),
      },
      {
        key: 'matricule',
        label: t('employees.columns.matricule', 'Matricule'),
        render: (row) => (
          <Link
            to={`/employees/${row.id}`}
            className="text-primary font-mono font-bold hover:underline"
          >
            {row.matricule}
          </Link>
        ),
      },
      {
        key: 'name',
        label: t('employees.columns.name', 'Nom'),
        render: (row) => (
          <span className="text-on-surface">
            {row.first_name} {row.last_name}
          </span>
        ),
      },
      {
        key: 'site_name',
        label: t('employees.columns.site', 'Site'),
        render: (row) => (
          <span className="text-on-surface-variant">
            {row.site_name ?? '\u2014'}
          </span>
        ),
      },
      {
        key: 'shift_time',
        label: t('employees.columns.shift_time', 'Equipe'),
        render: (row) => (
          <span className="text-on-surface-variant">
            {row.shift_time ?? '\u2014'}
          </span>
        ),
      },
      {
        key: 'is_pmr',
        label: t('employees.columns.pmr', 'PMR'),
        render: (row) => (row.is_pmr ? <PmrChip /> : null),
      },
      {
        key: 'current_transport_mode',
        label: t('employees.columns.transport_mode', 'Mode transport'),
        render: (row) => (
          <span className="text-on-surface-variant">
            {row.current_transport_mode ?? '\u2014'}
          </span>
        ),
      },
      {
        key: 'opt_in_company_transport',
        label: t('employees.columns.opt_in', 'Opt-in'),
        render: (row) => (
          <OptInChip value={row.opt_in_company_transport} />
        ),
      },
      {
        key: 'actions',
        label: '',
        render: (row) => (
          <div className="flex items-center gap-2 justify-end">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate(`/employees/${row.id}`)}
            >
              {t('common.view', 'Voir')}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate(`/employees/${row.id}/edit`)}
            >
              {t('common.edit')}
            </Button>
            <Button
              variant="danger"
              size="sm"
              onClick={() =>
                handleDelete(row.id, `${row.first_name} ${row.last_name}`)
              }
            >
              {t('common.delete')}
            </Button>
          </div>
        ),
      },
    ],
    [t, navigate, handleDelete, selected, toggleSelect],
  );

  const totalPages = meta?.pages ?? 1;

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-sans text-3xl font-black text-on-surface tracking-tight">
            {t('nav.employees')}
          </h1>
          <p className="text-sm text-on-surface-variant font-sans mt-1">
            {t('employees.description', 'Gestion et suivi des employes')}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/employees/map">
            <Button variant="secondary">
              <span className="material-symbols-outlined text-lg mr-1.5">map</span>
              {t('employees.view_on_map', 'Voir sur la carte')}
            </Button>
          </Link>
          <Link to="/employees/new">
            <Button>
              <span className="material-symbols-outlined text-lg mr-1.5">person_add</span>
              {t('employees.add', 'Ajouter un employe')}
            </Button>
          </Link>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm border border-outline-variant/10 mb-6">
        <div className="flex flex-wrap items-end gap-4">
          <div className="flex-1 min-w-[200px]">
            <Input
              placeholder={t(
                'employees.search_placeholder',
                'Rechercher par nom ou matricule...',
              )}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="w-48">
            <SelectFilter
              value={siteFilter}
              onChange={setSiteFilter}
              placeholder={t('employees.filter_site', 'Tous les sites')}
              options={sites.map((s) => ({
                value: s.id,
                label: `${s.code} — ${s.name}`,
              }))}
            />
          </div>
          <div className="w-40">
            <SelectFilter
              value={shiftFilter}
              onChange={setShiftFilter}
              placeholder={t('employees.filter_shift', 'Toutes les equipes')}
              options={[
                { value: 'Matin', label: 'Matin' },
                { value: 'Apres-midi', label: 'Apres-midi' },
                { value: 'Nuit', label: 'Nuit' },
              ]}
            />
          </div>
          <div className="w-48">
            <Input
              placeholder={t(
                'employees.filter_department',
                'Departement...',
              )}
              value={departmentFilter}
              onChange={(e) => setDepartmentFilter(e.target.value)}
            />
          </div>
          <label className="flex items-center gap-2 cursor-pointer select-none py-2">
            <input
              type="checkbox"
              checked={pmrFilter}
              onChange={(e) => setPmrFilter(e.target.checked)}
              className="w-4 h-4 rounded accent-primary"
            />
            <span className="text-sm font-sans text-on-surface-variant">
              {t('employees.filter_pmr', 'PMR')}
            </span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer select-none py-2">
            <input
              type="checkbox"
              checked={activeFilter}
              onChange={(e) => setActiveFilter(e.target.checked)}
              className="w-4 h-4 rounded accent-primary"
            />
            <span className="text-sm font-sans text-on-surface-variant">
              {t('employees.filter_active', 'Actifs uniquement')}
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

      {/* Bulk action bar */}
      {selected.size > 0 && (
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-3 mb-4 flex items-center gap-3 flex-wrap">
          <span className="text-sm font-sans font-medium text-on-surface">
            {t('employees.bulk.selected_count', '{{count}} selectionne(s)', {
              count: selected.size,
            })}
          </span>
          <Button variant="secondary" size="sm" onClick={handleBulkExportCSV}>
            {t('employees.bulk.export_csv', 'Exporter CSV')}
          </Button>
          <Button variant="danger" size="sm" onClick={handleBulkDelete}>
            {t('common.delete', 'Supprimer')}
          </Button>
          <Button variant="ghost" size="sm" onClick={handleDeselectAll}>
            {t('employees.bulk.deselect_all', 'Deselectionner tout')}
          </Button>
        </div>
      )}

      {/* Table with select-all header */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm overflow-hidden border border-outline-variant/10">
        {/* Select-all row above table */}
        {!isLoading && employees.length > 0 && (
          <div className="px-4 py-2 bg-surface-container-low/50 flex items-center gap-2">
            <input
              type="checkbox"
              checked={allSelected}
              onChange={toggleSelectAll}
              className="w-4 h-4 rounded accent-primary cursor-pointer"
            />
            <span className="text-xs font-sans text-on-surface-variant">
              {allSelected
                ? t('employees.bulk.deselect_all', 'Deselectionner tout')
                : t('employees.bulk.select_all', 'Tout selectionner')}
            </span>
          </div>
        )}
        <DataTable<Employee>
          columns={columns}
          data={employees}
          isLoading={isLoading}
          emptyMessage={t('employees.empty', 'Aucun employe')}
          rowKey={(row) => row.id}
        />
      </div>

      {/* Pagination */}
      {!isLoading && totalPages > 1 && (
        <div className="flex items-center justify-between mt-6">
          <p className="text-sm text-on-surface-variant font-sans">
            {t(
              'employees.pagination_info',
              'Page {{page}} sur {{pages}} ({{total}} employes)',
              {
                page,
                pages: totalPages,
                total: meta?.total ?? 0,
              },
            )}
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
                return (
                  p === 1 || p === totalPages || Math.abs(p - page) <= 1
                );
              })
              .map((p, idx, arr) => {
                const prev = arr[idx - 1];
                const showEllipsis = prev !== undefined && p - prev > 1;
                return (
                  <span key={p} className="flex items-center gap-1">
                    {showEllipsis && (
                      <span className="text-on-surface-variant text-sm px-1">
                        ...
                      </span>
                    )}
                    <button
                      onClick={() => setPage(p)}
                      className={[
                        'w-8 h-8 rounded-lg text-sm font-sans transition-colors',
                        p === page
                          ? 'bg-primary text-on-primary font-medium'
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
