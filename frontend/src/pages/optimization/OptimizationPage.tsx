import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

import { useOptimizationStore } from '@/stores/optimizationStore';
import { useSiteStore } from '@/stores/siteStore';
import { Button } from '@/components/ui/Button';
import { ClusterRegion } from '@/components/maps/ClusterRegion';
import { RoutePolyline } from '@/components/maps/RoutePolyline';
import { MeetingZoneMarker } from '@/components/maps/MeetingZoneMarker';
import { AccessLeg } from '@/components/maps/AccessLeg';
import { MapLegend } from '@/components/maps/MapLegend';
import type { OptimizationRunParams, OptimizationMetrics, MeetingZone } from '@/types/optimization';
import type { Site } from '@/types/site';

const CASABLANCA: [number, number] = [33.57, -7.59];

const CONDITION_OPTIONS = [
  { value: 'normal', label: 'Normal' },
  { value: 'rain', label: 'Rain' },
  { value: 'strike', label: 'Strike' },
  { value: 'peak', label: 'Peak' },
  { value: 'night', label: 'Night' },
];

const ALGORITHM_OPTIONS = [
  { value: 'dbscan', label: 'DBSCAN' },
  { value: 'kmeans', label: 'K-Means' },
  { value: 'hierarchical', label: 'Hierarchical' },
];

function MetricCard({ label, value, unit }: { label: string; value: string | number; unit?: string }) {
  return (
    <div className="bg-surface-container-lowest rounded-lg p-4 flex-1 min-w-[140px]">
      <p className="text-xs font-sans text-on-surface-variant mb-1">{label}</p>
      <p className="font-display text-xl font-bold text-on-surface tabular-nums">
        {value}
        {unit && <span className="text-sm font-normal text-on-surface-variant ml-1">{unit}</span>}
      </p>
    </div>
  );
}

function ProgressBar({ progress, step }: { progress: number; step: string }) {
  return (
    <div className="mt-4">
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-xs font-sans text-on-surface-variant">{step}</span>
        <span className="text-xs font-sans font-medium text-on-surface tabular-nums">
          {Math.round(progress)}%
        </span>
      </div>
      <div className="h-2 bg-surface-container-high rounded-full overflow-hidden">
        <div
          className="h-full bg-secondary rounded-full transition-all duration-300"
          style={{ width: `${Math.min(progress, 100)}%` }}
        />
      </div>
    </div>
  );
}

export function OptimizationPage() {
  const { t } = useTranslation();

  const {
    current,
    status,
    isLoading,
    isRunning,
    error,
    layers,
    selectedRouteId,
    launch,
    fetchLatest,
    toggleLayer,
    selectRoute,
    clearError,
  } = useOptimizationStore();

  const { sites, fetchSites } = useSiteStore();

  // Form state
  const [siteId, setSiteId] = useState('');
  const [targetDate, setTargetDate] = useState(() => {
    const today = new Date();
    return today.toISOString().slice(0, 10);
  });
  const [conditionType, setConditionType] = useState('normal');
  const [algorithm, setAlgorithm] = useState('dbscan');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [epsMeter, setEpsMeter] = useState(500);
  const [minSamples, setMinSamples] = useState(2);
  const [maxWalkingDistance, setMaxWalkingDistance] = useState(800);
  const [includeVolunteers, setIncludeVolunteers] = useState(false);

  // Load sites for dropdown and fetch latest optimization on mount
  useEffect(() => {
    fetchSites({ page: 1, page_size: 100 });
  }, [fetchSites]);

  useEffect(() => {
    fetchLatest();
  }, [fetchLatest]);

  // Determine map center from current optimization site or fallback
  const mapCenter = useMemo((): [number, number] => {
    if (current && current.clusters.length > 0) {
      const firstCluster = current.clusters[0];
      return [firstCluster.centroid_lat, firstCluster.centroid_lng];
    }
    // Try selected site
    const selectedSite = sites.find((s) => s.id === siteId);
    if (selectedSite) {
      return [selectedSite.lat, selectedSite.lng];
    }
    return CASABLANCA;
  }, [current, sites, siteId]);

  // Extract metrics from current optimization
  const metrics = useMemo((): OptimizationMetrics | null => {
    if (!current || !current.metrics) return null;
    const m = current.metrics as OptimizationMetrics;
    if (typeof m.total_employees !== 'number') return null;
    return m;
  }, [current]);

  // Build meeting zones from cluster data if available in params
  const meetingZones = useMemo((): MeetingZone[] => {
    if (!current) return [];
    // Meeting zones may be embedded in params or as a separate field
    const params = current.params as Record<string, unknown>;
    if (Array.isArray(params?.meeting_zones)) {
      return params.meeting_zones as MeetingZone[];
    }
    return [];
  }, [current]);

  // Build employee lookup from clusters for access legs
  const clusterEmployees = useMemo(() => {
    if (!current) return [];
    return current.clusters.flatMap((cluster) =>
      (cluster.employees ?? []).map((emp) => ({
        ...emp,
        cluster_centroid_lat: cluster.centroid_lat,
        cluster_centroid_lng: cluster.centroid_lng,
      })),
    );
  }, [current]);

  // Filtered routes based on selectedRouteId
  const visibleRoutes = useMemo(() => {
    if (!current) return [];
    if (selectedRouteId === null) return current.routes;
    return current.routes.filter((r) => r.id === selectedRouteId);
  }, [current, selectedRouteId]);

  // Find the site being viewed for the site marker
  const activeSite = useMemo((): Site | null => {
    if (!current?.site_id) return null;
    return sites.find((s) => s.id === current.site_id) ?? null;
  }, [current, sites]);

  const handleLaunch = useCallback(() => {
    if (!siteId) return;

    const params: OptimizationRunParams = {
      site_id: siteId,
      condition_type: conditionType,
      target_date: targetDate,
      algorithm,
      eps_meters: epsMeter,
      min_samples: minSamples,
      max_walking_distance_meters: maxWalkingDistance,
      include_volunteers: includeVolunteers,
    };

    launch(params);
  }, [
    siteId,
    conditionType,
    targetDate,
    algorithm,
    epsMeter,
    minSamples,
    maxWalkingDistance,
    includeVolunteers,
    launch,
  ]);

  return (
    <div className="flex flex-col h-full">
      {/* Page header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="font-display text-2xl font-bold text-on-surface">
          {t('optimization.title', 'Optimization')}
        </h1>
        {current && (
          <span className="text-xs font-sans text-on-surface-variant">
            {t('optimization.last_run', 'Last run')}: {new Date(current.created_at).toLocaleString()}
          </span>
        )}
      </div>

      {/* Error banner */}
      {error && (
        <div className="bg-error-container rounded-lg p-4 mb-4 flex items-center justify-between">
          <p className="text-error text-sm font-sans">{error}</p>
          <button
            onClick={clearError}
            className="text-error text-sm font-sans font-medium hover:underline ml-4"
          >
            {t('common.dismiss', 'Dismiss')}
          </button>
        </div>
      )}

      {/* Metrics bar */}
      {metrics && (
        <div className="flex gap-3 mb-4 overflow-x-auto">
          <MetricCard
            label={t('optimization.metrics.vehicles', 'Vehicles used')}
            value={metrics.total_vehicles_used}
          />
          <MetricCard
            label={t('optimization.metrics.assigned', 'Employees assigned')}
            value={metrics.employees_assigned}
          />
          <MetricCard
            label={t('optimization.metrics.occupancy', 'Avg occupancy')}
            value={`${(metrics.avg_occupancy_rate * 100).toFixed(0)}`}
            unit="%"
          />
          <MetricCard
            label={t('optimization.metrics.distance', 'Total distance')}
            value={metrics.total_distance_km.toFixed(1)}
            unit="km"
          />
          <MetricCard
            label={t('optimization.metrics.co2', 'CO2 estimate')}
            value={metrics.co2_estimate_kg.toFixed(1)}
            unit="kg"
          />
        </div>
      )}

      {/* Main split layout */}
      <div className="flex flex-1 gap-4 min-h-0">
        {/* Left panel - Controls */}
        <div
          className="w-80 flex-shrink-0 bg-surface-container-lowest rounded-lg p-5 overflow-y-auto"
        >
          <h2 className="font-display text-base font-semibold text-on-surface mb-5">
            {t('optimization.controls', 'Run Parameters')}
          </h2>

          {/* Site selector */}
          <div className="mb-4">
            <label className="block text-sm font-sans font-medium text-on-surface-variant mb-1.5">
              {t('optimization.site', 'Site')}
            </label>
            <select
              value={siteId}
              onChange={(e) => setSiteId(e.target.value)}
              className="w-full bg-surface-container-high rounded-md p-3 text-on-surface font-sans text-sm outline-none transition-shadow duration-150 focus:ring-1 focus:ring-secondary/40 appearance-none"
            >
              <option value="">{t('optimization.select_site', '-- Select a site --')}</option>
              {sites.map((site) => (
                <option key={site.id} value={site.id}>
                  {site.name} ({site.code})
                </option>
              ))}
            </select>
          </div>

          {/* Target date */}
          <div className="mb-4">
            <label className="block text-sm font-sans font-medium text-on-surface-variant mb-1.5">
              {t('optimization.target_date', 'Target date')}
            </label>
            <input
              type="date"
              value={targetDate}
              onChange={(e) => setTargetDate(e.target.value)}
              className="w-full bg-surface-container-high rounded-md p-3 text-on-surface font-sans text-sm outline-none transition-shadow duration-150 focus:ring-1 focus:ring-secondary/40"
            />
          </div>

          {/* Condition type */}
          <div className="mb-4">
            <label className="block text-sm font-sans font-medium text-on-surface-variant mb-1.5">
              {t('optimization.condition', 'Condition')}
            </label>
            <select
              value={conditionType}
              onChange={(e) => setConditionType(e.target.value)}
              className="w-full bg-surface-container-high rounded-md p-3 text-on-surface font-sans text-sm outline-none transition-shadow duration-150 focus:ring-1 focus:ring-secondary/40 appearance-none"
            >
              {CONDITION_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Algorithm */}
          <div className="mb-4">
            <label className="block text-sm font-sans font-medium text-on-surface-variant mb-1.5">
              {t('optimization.algorithm', 'Algorithm')}
            </label>
            <select
              value={algorithm}
              onChange={(e) => setAlgorithm(e.target.value)}
              className="w-full bg-surface-container-high rounded-md p-3 text-on-surface font-sans text-sm outline-none transition-shadow duration-150 focus:ring-1 focus:ring-secondary/40 appearance-none"
            >
              {ALGORITHM_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Advanced settings toggle */}
          <button
            onClick={() => setShowAdvanced((v) => !v)}
            className="flex items-center gap-2 text-sm font-sans text-secondary font-medium mb-3 cursor-pointer"
          >
            <svg
              className={`w-4 h-4 transition-transform ${showAdvanced ? 'rotate-90' : ''}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
            </svg>
            {t('optimization.advanced', 'Advanced settings')}
          </button>

          {showAdvanced && (
            <div className="bg-surface-container rounded-lg p-4 mb-4 space-y-3">
              {/* eps_meters */}
              <div>
                <label className="block text-xs font-sans text-on-surface-variant mb-1">
                  eps_meters
                </label>
                <input
                  type="number"
                  value={epsMeter}
                  onChange={(e) => setEpsMeter(Number(e.target.value))}
                  min={100}
                  max={5000}
                  step={50}
                  className="w-full bg-surface-container-high rounded-md p-2.5 text-on-surface font-sans text-sm outline-none focus:ring-1 focus:ring-secondary/40 tabular-nums"
                />
              </div>

              {/* min_samples */}
              <div>
                <label className="block text-xs font-sans text-on-surface-variant mb-1">
                  min_samples
                </label>
                <input
                  type="number"
                  value={minSamples}
                  onChange={(e) => setMinSamples(Number(e.target.value))}
                  min={1}
                  max={20}
                  step={1}
                  className="w-full bg-surface-container-high rounded-md p-2.5 text-on-surface font-sans text-sm outline-none focus:ring-1 focus:ring-secondary/40 tabular-nums"
                />
              </div>

              {/* max_walking_distance */}
              <div>
                <label className="block text-xs font-sans text-on-surface-variant mb-1">
                  max_walking_distance (m)
                </label>
                <input
                  type="number"
                  value={maxWalkingDistance}
                  onChange={(e) => setMaxWalkingDistance(Number(e.target.value))}
                  min={100}
                  max={3000}
                  step={50}
                  className="w-full bg-surface-container-high rounded-md p-2.5 text-on-surface font-sans text-sm outline-none focus:ring-1 focus:ring-secondary/40 tabular-nums"
                />
              </div>

              {/* include_volunteers */}
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={includeVolunteers}
                  onChange={(e) => setIncludeVolunteers(e.target.checked)}
                  className="w-4 h-4 rounded accent-secondary"
                />
                <span className="text-sm font-sans text-on-surface-variant">
                  {t('optimization.include_volunteers', 'Include volunteers')}
                </span>
              </label>
            </div>
          )}

          {/* Launch button */}
          <Button
            onClick={handleLaunch}
            disabled={!siteId || isRunning}
            isLoading={isRunning}
            className="w-full"
          >
            {isRunning
              ? t('optimization.running', 'Running...')
              : t('optimization.launch', 'Run Optimization')}
          </Button>

          {/* Progress indicator when running */}
          {isRunning && status && (
            <ProgressBar
              progress={status.progress}
              step={status.step}
            />
          )}

          {/* Quick summary when loaded */}
          {!isRunning && current && (
            <div className="mt-5 bg-surface-container rounded-lg p-4">
              <p className="text-xs font-sans text-on-surface-variant mb-2">
                {t('optimization.summary', 'Summary')}
              </p>
              <p className="text-sm font-sans text-on-surface">
                <span className="font-medium">{current.clusters.length}</span>{' '}
                {t('optimization.clusters', 'clusters')},{' '}
                <span className="font-medium">{current.routes.length}</span>{' '}
                {t('optimization.routes', 'routes')}
              </p>
              <p className="text-xs font-sans text-on-surface-variant mt-1">
                {t('optimization.condition_label', 'Condition')}:{' '}
                <span className="text-on-surface">{current.condition_type}</span>
              </p>
              {current.target_date && (
                <p className="text-xs font-sans text-on-surface-variant mt-0.5">
                  {t('optimization.date_label', 'Date')}:{' '}
                  <span className="text-on-surface">{current.target_date}</span>
                </p>
              )}
            </div>
          )}
        </div>

        {/* Right panel - Map */}
        <div className="flex-1 relative rounded-lg overflow-hidden min-h-[400px]">
          {/* Loading overlay */}
          {isLoading && (
            <div className="absolute inset-0 z-[1001] flex items-center justify-center bg-surface/60 backdrop-blur-sm rounded-lg">
              <div className="flex flex-col items-center gap-3">
                <svg
                  className="animate-spin h-8 w-8 text-secondary"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                <span className="text-sm font-sans text-on-surface-variant">
                  {t('common.loading', 'Loading...')}
                </span>
              </div>
            </div>
          )}

          {/* Empty state */}
          {!isLoading && !current && !isRunning && (
            <div className="absolute inset-0 z-[1001] flex items-center justify-center bg-surface-container-low/80 backdrop-blur-sm rounded-lg">
              <div className="text-center max-w-xs">
                <svg
                  className="mx-auto mb-3 w-12 h-12 text-on-surface-variant/40"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={1.5}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M9 6.75V15m6-6v8.25m.503 3.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 00-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c.317-.159.69-.159 1.006 0l4.994 2.497c.317.158.69.158 1.006 0z"
                  />
                </svg>
                <p className="font-display text-base font-semibold text-on-surface mb-1">
                  {t('optimization.empty_title', 'No optimization loaded')}
                </p>
                <p className="text-sm font-sans text-on-surface-variant">
                  {t(
                    'optimization.empty_desc',
                    'Select a site and run an optimization to see clusters, routes, and meeting zones on the map.',
                  )}
                </p>
              </div>
            </div>
          )}

          <MapContainer
            center={mapCenter}
            zoom={12}
            style={{ height: '100%', width: '100%' }}
            scrollWheelZoom
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {/* Site marker */}
            {layers.siteMarker && activeSite && (
              <CircleMarker
                center={[activeSite.lat, activeSite.lng]}
                radius={10}
                pathOptions={{
                  fillColor: '#041627',
                  fillOpacity: 0.9,
                  color: '#041627',
                  weight: 2,
                  opacity: 0.7,
                }}
              >
                <Popup>
                  <div className="font-sans text-sm text-on-surface min-w-[140px]">
                    <p className="font-medium text-on-surface">{activeSite.name}</p>
                    <p className="text-xs text-on-surface-variant mt-0.5">{activeSite.code}</p>
                    <p className="text-xs text-on-surface-variant mt-1">{activeSite.city}</p>
                  </div>
                </Popup>
              </CircleMarker>
            )}

            {/* Cluster regions */}
            {layers.clusters &&
              current?.clusters.map((cluster) => (
                <ClusterRegion key={cluster.id} cluster={cluster} />
              ))}

            {/* Employee markers from cluster data */}
            {layers.employees &&
              clusterEmployees
                .filter((emp) => emp.lat !== null && emp.lng !== null)
                .map((emp) => (
                  <CircleMarker
                    key={emp.employee_id}
                    center={[emp.lat as number, emp.lng as number]}
                    radius={5}
                    pathOptions={{
                      fillColor: emp.is_pmr ? '#68fadd' : '#2563eb',
                      fillOpacity: 0.85,
                      color: emp.is_pmr ? '#006b5c' : '#2563eb',
                      weight: 1.5,
                      opacity: 0.6,
                    }}
                  >
                    <Popup>
                      <div className="font-sans text-sm">
                        <p className="font-medium text-on-surface">
                          {emp.first_name} {emp.last_name}
                        </p>
                        {emp.is_pmr && (
                          <span className="inline-block mt-1 rounded-md bg-secondary-container text-on-secondary-container px-2 py-0.5 text-xs font-medium">
                            PMR
                          </span>
                        )}
                      </div>
                    </Popup>
                  </CircleMarker>
                ))}

            {/* Route polylines */}
            {layers.routes &&
              visibleRoutes.map((route, idx) => (
                <RoutePolyline
                  key={route.id}
                  route={route}
                  index={idx}
                  isSelected={route.id === selectedRouteId}
                />
              ))}

            {/* Meeting zone markers */}
            {layers.meetingZones &&
              meetingZones.map((zone, idx) => (
                <MeetingZoneMarker key={`mz-${idx}`} zone={zone} />
              ))}

            {/* Access legs */}
            {layers.accessLegs &&
              clusterEmployees
                .filter((emp) => emp.lat !== null && emp.lng !== null)
                .map((emp) => (
                  <AccessLeg
                    key={`leg-${emp.employee_id}`}
                    employeeLat={emp.lat as number}
                    employeeLng={emp.lng as number}
                    zoneLat={emp.cluster_centroid_lat}
                    zoneLng={emp.cluster_centroid_lng}
                  />
                ))}

            {/* Floating map legend */}
            <MapLegend
              layers={layers}
              onToggle={toggleLayer}
              routeCount={current?.routes.length ?? 0}
              selectedRouteId={selectedRouteId}
              routeIds={current?.routes.map((r) => r.id) ?? []}
              onSelectRoute={selectRoute}
            />
          </MapContainer>
        </div>
      </div>
    </div>
  );
}
