import { useCallback, useEffect, useMemo, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
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
import type { OptimizationMetrics, MeetingZone } from '@/types/optimization';
import type { Site } from '@/types/site';

const CASABLANCA: [number, number] = [33.57, -7.59];

type TabId = 'routes' | 'clusters' | 'sites';

function MetricsPanel({ metrics }: { metrics: OptimizationMetrics }) {
  const { t } = useTranslation();
  return (
    <div className="flex gap-3 overflow-x-auto">
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
        label={t('optimization.metrics.duration', 'Total duration')}
        value={metrics.total_duration_minutes.toFixed(0)}
        unit="min"
      />
      <MetricCard
        label={t('optimization.metrics.co2', 'CO2 estimate')}
        value={metrics.co2_estimate_kg.toFixed(1)}
        unit="kg"
      />
    </div>
  );
}

function MetricCard({
  label,
  value,
  unit,
}: {
  label: string;
  value: string | number;
  unit?: string;
}) {
  return (
    <div className="bg-surface-container-lowest rounded-lg p-4 flex-1 min-w-[130px]">
      <p className="text-xs font-sans text-on-surface-variant mb-1">{label}</p>
      <p className="font-display text-xl font-bold text-on-surface tabular-nums">
        {value}
        {unit && (
          <span className="text-sm font-normal text-on-surface-variant ml-1">
            {unit}
          </span>
        )}
      </p>
    </div>
  );
}

function RouteList({
  routes,
  selectedRouteId,
  onSelectRoute,
}: {
  routes: { id: string; total_distance_km: number | null; total_time_minutes: number | null; ordered_stops: unknown[]; vehicle_type: string | null; vehicle_capacity: number | null }[];
  selectedRouteId: string | null;
  onSelectRoute: (id: string | null) => void;
}) {
  const { t } = useTranslation();

  if (routes.length === 0) {
    return (
      <p className="text-sm font-sans text-on-surface-variant py-6 text-center">
        {t('optimization.no_routes', 'No routes generated')}
      </p>
    );
  }

  return (
    <div className="space-y-2">
      {routes.map((route, idx) => {
        const isSelected = route.id === selectedRouteId;
        return (
          <button
            key={route.id}
            onClick={() => onSelectRoute(isSelected ? null : route.id)}
            className={`w-full text-left rounded-lg p-3 transition-colors cursor-pointer ${
              isSelected
                ? 'bg-secondary-container'
                : 'bg-surface-container hover:bg-surface-container-high'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="font-sans text-sm font-medium text-on-surface">
                {t('optimization.route_label', 'Route')} {idx + 1}
              </span>
              {route.vehicle_type && (
                <span className="text-xs font-sans text-on-surface-variant bg-surface-container-high rounded-md px-2 py-0.5">
                  {route.vehicle_type}
                  {route.vehicle_capacity != null && ` (${route.vehicle_capacity})`}
                </span>
              )}
            </div>
            <div className="flex gap-4 text-xs font-sans text-on-surface-variant">
              <span>{route.ordered_stops.length} stops</span>
              {route.total_distance_km != null && (
                <span className="tabular-nums">{route.total_distance_km.toFixed(1)} km</span>
              )}
              {route.total_time_minutes != null && (
                <span className="tabular-nums">{route.total_time_minutes.toFixed(0)} min</span>
              )}
            </div>
          </button>
        );
      })}
    </div>
  );
}

function ClusterTable({
  clusters,
}: {
  clusters: { id: string; employee_count: number; pmr_count: number; centroid_lat: number; centroid_lng: number }[];
}) {
  const { t } = useTranslation();

  if (clusters.length === 0) {
    return (
      <p className="text-sm font-sans text-on-surface-variant py-6 text-center">
        {t('optimization.no_clusters', 'No clusters generated')}
      </p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm font-sans">
        <thead>
          <tr className="text-xs text-on-surface-variant">
            <th className="text-left py-2 px-2 font-medium">#</th>
            <th className="text-right py-2 px-2 font-medium">
              {t('optimization.employees', 'Employees')}
            </th>
            <th className="text-right py-2 px-2 font-medium">PMR</th>
            <th className="text-right py-2 px-2 font-medium">
              {t('optimization.centroid', 'Centroid')}
            </th>
          </tr>
        </thead>
        <tbody>
          {clusters.map((cluster, idx) => (
            <tr
              key={cluster.id}
              className="hover:bg-surface-container-low transition-colors"
            >
              <td className="py-2 px-2 text-on-surface">{idx + 1}</td>
              <td className="py-2 px-2 text-right text-on-surface tabular-nums">
                {cluster.employee_count}
              </td>
              <td className="py-2 px-2 text-right text-on-surface tabular-nums">
                {cluster.pmr_count}
              </td>
              <td className="py-2 px-2 text-right text-on-surface-variant tabular-nums text-xs">
                {cluster.centroid_lat.toFixed(4)}, {cluster.centroid_lng.toFixed(4)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function SiteBreakdown({
  metrics,
  conditionType,
  targetDate,
  createdAt,
}: {
  metrics: OptimizationMetrics | null;
  conditionType: string;
  targetDate: string | null;
  createdAt: string;
}) {
  const { t } = useTranslation();

  return (
    <div className="space-y-4">
      <div className="bg-surface-container rounded-lg p-4">
        <p className="text-xs font-sans text-on-surface-variant mb-2 font-medium">
          {t('optimization.run_info', 'Run Information')}
        </p>
        <div className="space-y-1.5 text-sm font-sans">
          <div className="flex justify-between">
            <span className="text-on-surface-variant">
              {t('optimization.condition_label', 'Condition')}
            </span>
            <span className="text-on-surface font-medium">{conditionType}</span>
          </div>
          {targetDate && (
            <div className="flex justify-between">
              <span className="text-on-surface-variant">
                {t('optimization.date_label', 'Date')}
              </span>
              <span className="text-on-surface font-medium">{targetDate}</span>
            </div>
          )}
          <div className="flex justify-between">
            <span className="text-on-surface-variant">
              {t('optimization.created_at', 'Created at')}
            </span>
            <span className="text-on-surface font-medium">
              {new Date(createdAt).toLocaleString()}
            </span>
          </div>
        </div>
      </div>

      {metrics && (
        <div className="bg-surface-container rounded-lg p-4">
          <p className="text-xs font-sans text-on-surface-variant mb-2 font-medium">
            {t('optimization.detailed_metrics', 'Detailed Metrics')}
          </p>
          <div className="space-y-1.5 text-sm font-sans">
            <div className="flex justify-between">
              <span className="text-on-surface-variant">
                {t('optimization.total_employees_label', 'Total employees')}
              </span>
              <span className="text-on-surface font-medium tabular-nums">
                {metrics.total_employees}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-on-surface-variant">
                {t('optimization.excluded_leave', 'Excluded (leave)')}
              </span>
              <span className="text-on-surface font-medium tabular-nums">
                {metrics.employees_excluded_leave}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-on-surface-variant">
                {t('optimization.unassigned_clusters', 'Unassigned clusters')}
              </span>
              <span className="text-on-surface font-medium tabular-nums">
                {metrics.unassigned_clusters}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-on-surface-variant">
                {t('optimization.fuel_liters', 'Fuel estimate')}
              </span>
              <span className="text-on-surface font-medium tabular-nums">
                {metrics.estimated_fuel_liters.toFixed(1)} L
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-on-surface-variant">
                {t('optimization.fuel_cost', 'Fuel cost')}
              </span>
              <span className="text-on-surface font-medium tabular-nums">
                {metrics.estimated_fuel_cost_mad.toFixed(0)} MAD
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-on-surface-variant">
                {t('optimization.time_saved', 'Time saved vs individual')}
              </span>
              <span className="text-on-surface font-medium tabular-nums">
                {metrics.time_saved_vs_individual_hours.toFixed(1)} h
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export function OptimizationResultPage() {
  const { id } = useParams<{ id: string }>();
  const { t } = useTranslation();

  const {
    current,
    isLoading,
    error,
    layers,
    selectedRouteId,
    fetchResult,
    toggleLayer,
    selectRoute,
    clearError,
  } = useOptimizationStore();

  const { sites, fetchSites } = useSiteStore();

  const [activeTab, setActiveTab] = useState<TabId>('routes');

  useEffect(() => {
    if (id) {
      fetchResult(id);
    }
  }, [id, fetchResult]);

  useEffect(() => {
    fetchSites({ page: 1, page_size: 100 });
  }, [fetchSites]);

  const mapCenter = useMemo((): [number, number] => {
    if (current && current.clusters.length > 0) {
      const firstCluster = current.clusters[0];
      return [firstCluster.centroid_lat, firstCluster.centroid_lng];
    }
    return CASABLANCA;
  }, [current]);

  const metrics = useMemo((): OptimizationMetrics | null => {
    if (!current || !current.metrics) return null;
    const m = current.metrics as OptimizationMetrics;
    if (typeof m.total_employees !== 'number') return null;
    return m;
  }, [current]);

  const meetingZones = useMemo((): MeetingZone[] => {
    if (!current) return [];
    const params = current.params as Record<string, unknown>;
    if (Array.isArray(params?.meeting_zones)) {
      return params.meeting_zones as MeetingZone[];
    }
    return [];
  }, [current]);

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

  const visibleRoutes = useMemo(() => {
    if (!current) return [];
    if (selectedRouteId === null) return current.routes;
    return current.routes.filter((r) => r.id === selectedRouteId);
  }, [current, selectedRouteId]);

  const activeSite = useMemo((): Site | null => {
    if (!current?.site_id) return null;
    return sites.find((s) => s.id === current.site_id) ?? null;
  }, [current, sites]);

  const handleExport = useCallback((format: string) => {
    // eslint-disable-next-line no-console
    console.log(`Export ${format} for optimization ${id}`);
  }, [id]);

  const tabs: { id: TabId; label: string }[] = [
    { id: 'routes', label: t('optimization.tab_routes', 'Routes') },
    { id: 'clusters', label: t('optimization.tab_clusters', 'Clusters') },
    { id: 'sites', label: t('optimization.tab_breakdown', 'Breakdown') },
  ];

  // Loading state
  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <svg
            className="animate-spin h-8 w-8 text-secondary"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
          <span className="text-sm font-sans text-on-surface-variant">
            {t('common.loading', 'Loading...')}
          </span>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !current) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-4">
        <div className="bg-error-container rounded-lg p-6 max-w-md text-center">
          <p className="text-error text-sm font-sans mb-3">{error}</p>
          <div className="flex gap-3 justify-center">
            <Link
              to="/optimization"
              className="text-sm font-sans font-medium text-secondary hover:underline"
            >
              {t('optimization.back_to_optimization', 'Back to Optimization')}
            </Link>
            <button
              onClick={clearError}
              className="text-sm font-sans font-medium text-on-surface-variant hover:underline cursor-pointer"
            >
              {t('common.dismiss', 'Dismiss')}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Empty / not found state
  if (!current) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-4">
        <p className="font-display text-base font-semibold text-on-surface">
          {t('optimization.not_found', 'Optimization result not found')}
        </p>
        <Link
          to="/optimization"
          className="text-sm font-sans font-medium text-secondary hover:underline"
        >
          {t('optimization.back_to_optimization', 'Back to Optimization')}
        </Link>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Link
            to="/optimization"
            className="text-sm font-sans text-secondary font-medium hover:underline flex items-center gap-1"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
            {t('common.back', 'Back')}
          </Link>
          <h1 className="font-display text-2xl font-bold text-on-surface">
            {t('optimization.result_title', 'Optimization Result')}
          </h1>
        </div>

        <div className="flex gap-2">
          <Button variant="ghost" size="sm" onClick={() => handleExport('pdf')}>
            {t('optimization.export_pdf', 'Export PDF')}
          </Button>
          <Button variant="ghost" size="sm" onClick={() => handleExport('excel')}>
            {t('optimization.export_excel', 'Export Excel')}
          </Button>
          <Button variant="ghost" size="sm" onClick={() => handleExport('geojson')}>
            {t('optimization.export_geojson', 'Export GeoJSON')}
          </Button>
        </div>
      </div>

      {/* Error banner (non-blocking) */}
      {error && (
        <div className="bg-error-container rounded-lg p-4 mb-4 flex items-center justify-between">
          <p className="text-error text-sm font-sans">{error}</p>
          <button
            onClick={clearError}
            className="text-error text-sm font-sans font-medium hover:underline ml-4 cursor-pointer"
          >
            {t('common.dismiss', 'Dismiss')}
          </button>
        </div>
      )}

      {/* Metrics row */}
      {metrics && (
        <div className="mb-4">
          <MetricsPanel metrics={metrics} />
        </div>
      )}

      {/* Two-column layout */}
      <div className="flex flex-1 gap-4 min-h-0">
        {/* Left: Map (60%) */}
        <div className="w-[60%] flex-shrink-0 relative rounded-lg overflow-hidden min-h-[400px]">
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
              current.clusters.map((cluster) => (
                <ClusterRegion key={cluster.id} cluster={cluster} />
              ))}

            {/* Employee markers */}
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

            {/* Map legend */}
            <MapLegend
              layers={layers}
              onToggle={toggleLayer}
              routeCount={current.routes.length}
              selectedRouteId={selectedRouteId}
              routeIds={current.routes.map((r) => r.id)}
              onSelectRoute={selectRoute}
            />
          </MapContainer>
        </div>

        {/* Right: Tabbed panel (40%) */}
        <div className="flex-1 bg-surface-container-lowest rounded-lg flex flex-col min-h-0 overflow-hidden">
          {/* Tab bar */}
          <div className="flex bg-surface-container-low">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 py-3 text-sm font-sans font-medium text-center transition-colors cursor-pointer ${
                  activeTab === tab.id
                    ? 'text-secondary bg-surface-container-lowest'
                    : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab content */}
          <div className="flex-1 overflow-y-auto p-4">
            {activeTab === 'routes' && (
              <RouteList
                routes={current.routes}
                selectedRouteId={selectedRouteId}
                onSelectRoute={selectRoute}
              />
            )}
            {activeTab === 'clusters' && (
              <ClusterTable clusters={current.clusters} />
            )}
            {activeTab === 'sites' && (
              <SiteBreakdown
                metrics={metrics}
                conditionType={current.condition_type}
                targetDate={current.target_date}
                createdAt={current.created_at}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
