import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useEmployeeStore } from '@/stores/employeeStore';
import { useSiteStore } from '@/stores/siteStore';
import { MapView } from '@/components/maps/MapView';
import { EmployeeMarker } from '@/components/maps/EmployeeMarker';
import { SiteMarker } from '@/components/maps/SiteMarker';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import type { Employee } from '@/types/employee';
import type { Site } from '@/types/site';

/**
 * 10 visually distinct colors for site-based employee coloring.
 * Ordered to maximize contrast between adjacent indices.
 */
const SITE_COLOR_PALETTE: string[] = [
  '#006b5c', // teal (secondary)
  '#b45309', // amber
  '#7c3aed', // violet
  '#0369a1', // sky
  '#be185d', // pink
  '#4d7c0f', // lime
  '#9333ea', // purple
  '#c2410c', // orange
  '#0891b2', // cyan
  '#a16207', // yellow
];

function getSiteColor(siteId: string, siteIds: string[]): string {
  const idx = siteIds.indexOf(siteId);
  if (idx === -1) return SITE_COLOR_PALETTE[0];
  return SITE_COLOR_PALETTE[idx % SITE_COLOR_PALETTE.length];
}

function FloatingFilterPanel({
  sites,
  siteFilter,
  onSiteChange,
  shiftFilter,
  onShiftChange,
  pmrOnly,
  onPmrChange,
  activeOnly,
  onActiveChange,
}: {
  sites: Site[];
  siteFilter: string;
  onSiteChange: (v: string) => void;
  shiftFilter: string;
  onShiftChange: (v: string) => void;
  pmrOnly: boolean;
  onPmrChange: (v: boolean) => void;
  activeOnly: boolean;
  onActiveChange: (v: boolean) => void;
}) {
  const { t } = useTranslation();

  return (
    <div className="absolute top-4 left-4 z-[1000] bg-white/80 backdrop-blur-xl rounded-lg shadow-[0_8px_32px_rgba(4,22,39,0.06)] p-4 w-64 flex flex-col gap-3">
      <p className="font-display text-sm font-semibold text-on-surface">
        {t('employees.map.filters', 'Filtres')}
      </p>

      {/* Site filter */}
      <select
        value={siteFilter}
        onChange={(e) => onSiteChange(e.target.value)}
        className="w-full bg-surface-container-high rounded-md p-2 text-on-surface font-sans text-sm outline-none transition-shadow duration-150 appearance-none focus:ring-1 focus:ring-secondary/40"
      >
        <option value="">
          {t('employees.filter_site', 'Tous les sites')}
        </option>
        {sites.map((s) => (
          <option key={s.id} value={s.id}>
            {s.code} — {s.name}
          </option>
        ))}
      </select>

      {/* Shift filter */}
      <select
        value={shiftFilter}
        onChange={(e) => onShiftChange(e.target.value)}
        className="w-full bg-surface-container-high rounded-md p-2 text-on-surface font-sans text-sm outline-none transition-shadow duration-150 appearance-none focus:ring-1 focus:ring-secondary/40"
      >
        <option value="">
          {t('employees.filter_shift', 'Toutes les equipes')}
        </option>
        <option value="Matin">Matin</option>
        <option value="Apres-midi">Apres-midi</option>
        <option value="Nuit">Nuit</option>
      </select>

      {/* PMR toggle */}
      <label className="flex items-center gap-2 cursor-pointer select-none">
        <input
          type="checkbox"
          checked={pmrOnly}
          onChange={(e) => onPmrChange(e.target.checked)}
          className="w-4 h-4 rounded accent-secondary"
        />
        <span className="text-sm font-sans text-on-surface-variant">
          {t('employees.filter_pmr', 'PMR')}
        </span>
      </label>

      {/* Active-only toggle */}
      <label className="flex items-center gap-2 cursor-pointer select-none">
        <input
          type="checkbox"
          checked={activeOnly}
          onChange={(e) => onActiveChange(e.target.checked)}
          className="w-4 h-4 rounded accent-secondary"
        />
        <span className="text-sm font-sans text-on-surface-variant">
          {t('employees.filter_active', 'Actifs uniquement')}
        </span>
      </label>
    </div>
  );
}

function FloatingLegend({
  siteColorMap,
}: {
  siteColorMap: { name: string; color: string }[];
}) {
  const { t } = useTranslation();

  if (siteColorMap.length === 0) return null;

  return (
    <div className="absolute bottom-4 left-4 z-[1000] bg-white/80 backdrop-blur-xl rounded-lg shadow-[0_8px_32px_rgba(4,22,39,0.06)] p-4 max-w-[240px]">
      <p className="font-display text-xs font-semibold text-on-surface mb-2">
        {t('employees.map.legend', 'Legende')}
      </p>
      <div className="flex flex-col gap-1.5">
        {siteColorMap.map((entry) => (
          <div key={entry.name} className="flex items-center gap-2">
            <span
              className="inline-block w-3 h-3 rounded-full shrink-0"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-xs text-on-surface-variant font-sans truncate">
              {entry.name}
            </span>
          </div>
        ))}
        {/* Site marker legend entry */}
        <div className="flex items-center gap-2 mt-1">
          <span
            className="inline-block w-3.5 h-3.5 rounded-full shrink-0"
            style={{ backgroundColor: '#041627' }}
          />
          <span className="text-xs text-on-surface-variant font-sans">
            {t('employees.map.site_marker', 'Site')}
          </span>
        </div>
      </div>
    </div>
  );
}

export function EmployeeMapPage() {
  const { t } = useTranslation();
  const { employees, isLoading: empLoading, fetchEmployees } = useEmployeeStore();
  const { sites, isLoading: sitesLoading, fetchSites } = useSiteStore();

  const [siteFilter, setSiteFilter] = useState('');
  const [shiftFilter, setShiftFilter] = useState('');
  const [pmrOnly, setPmrOnly] = useState(false);
  const [activeOnly, setActiveOnly] = useState(true);

  /* Fetch all employees (large page to get as many as possible) and all sites */
  useEffect(() => {
    fetchEmployees({ page: 1, page_size: 100, active: true });
  }, [fetchEmployees]);

  useEffect(() => {
    fetchSites({ page: 1, page_size: 100 });
  }, [fetchSites]);

  /* Unique site IDs in order for stable color assignment */
  const siteIds = useMemo(() => {
    const ids: string[] = [];
    for (const s of sites) {
      if (!ids.includes(s.id)) {
        ids.push(s.id);
      }
    }
    return ids;
  }, [sites]);

  /* Client-side filter logic */
  const filteredEmployees = useMemo(() => {
    let filtered: Employee[] = employees;

    // Only employees with valid coordinates
    filtered = filtered.filter((e) => e.lat !== null && e.lng !== null);

    if (siteFilter) {
      filtered = filtered.filter((e) => e.site_id === siteFilter);
    }

    if (shiftFilter) {
      filtered = filtered.filter((e) => e.shift_time === shiftFilter);
    }

    if (pmrOnly) {
      filtered = filtered.filter((e) => e.is_pmr);
    }

    if (activeOnly) {
      filtered = filtered.filter((e) => e.active);
    }

    return filtered;
  }, [employees, siteFilter, shiftFilter, pmrOnly, activeOnly]);

  /* Build legend data: only sites that have visible employees */
  const siteColorMap = useMemo(() => {
    const visibleSiteIds = new Set(filteredEmployees.map((e) => e.site_id));
    return sites
      .filter((s) => visibleSiteIds.has(s.id))
      .map((s) => ({
        name: `${s.code} — ${s.name}`,
        color: getSiteColor(s.id, siteIds),
      }));
  }, [filteredEmployees, sites, siteIds]);

  const handleSiteChange = useCallback((v: string) => setSiteFilter(v), []);
  const handleShiftChange = useCallback((v: string) => setShiftFilter(v), []);
  const handlePmrChange = useCallback((v: boolean) => setPmrOnly(v), []);
  const handleActiveChange = useCallback((v: boolean) => setActiveOnly(v), []);

  const isLoading = empLoading || sitesLoading;

  /* Loading state */
  if (isLoading && employees.length === 0) {
    return (
      <div className="flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <Skeleton variant="text" className="w-64 h-8" />
          <Skeleton variant="text" className="w-32 h-10" />
        </div>
        <Skeleton
          variant="rectangular"
          className="w-full"
          height="calc(100vh - 8rem)"
        />
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h1 className="font-display text-2xl font-bold text-on-surface">
          {t('employees.map.title', 'Carte des employes')}
        </h1>
        <div className="flex items-center gap-2">
          <span className="text-sm text-on-surface-variant font-sans">
            {t('employees.map.count', '{{count}} employe(s) affiches', {
              count: filteredEmployees.length,
            })}
          </span>
          <Link to="/employees">
            <Button variant="ghost">
              {t('employees.back_to_list', 'Retour a la liste')}
            </Button>
          </Link>
        </div>
      </div>

      {/* Map container */}
      <div className="relative">
        {filteredEmployees.length === 0 && !isLoading ? (
          <div
            className="flex items-center justify-center bg-surface-container rounded-lg"
            style={{ height: 'calc(100vh - 8rem)' }}
          >
            <p className="text-sm text-on-surface-variant font-sans">
              {t(
                'employees.map.empty',
                'Aucun employe avec coordonnees a afficher',
              )}
            </p>
          </div>
        ) : (
          <MapView height="calc(100vh - 8rem)">
            {/* Employee markers color-coded by site */}
            {filteredEmployees.map((emp) => (
              <EmployeeMarker
                key={emp.id}
                employee={emp}
                color={getSiteColor(emp.site_id, siteIds)}
              />
            ))}

            {/* Site markers */}
            {sites.map((site) => (
              <SiteMarker key={site.id} site={site} />
            ))}
          </MapView>
        )}

        {/* Floating filter panel */}
        <FloatingFilterPanel
          sites={sites}
          siteFilter={siteFilter}
          onSiteChange={handleSiteChange}
          shiftFilter={shiftFilter}
          onShiftChange={handleShiftChange}
          pmrOnly={pmrOnly}
          onPmrChange={handlePmrChange}
          activeOnly={activeOnly}
          onActiveChange={handleActiveChange}
        />

        {/* Floating legend */}
        <FloatingLegend siteColorMap={siteColorMap} />
      </div>
    </div>
  );
}
