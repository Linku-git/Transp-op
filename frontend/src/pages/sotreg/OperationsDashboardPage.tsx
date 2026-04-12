/**
 * OperationsDashboardPage — Real-time operations dashboard.
 *
 * Combines LiveFleetMap, DemandForecastChart, DriverRiskHeatmap,
 * RouteOptimizationPanel, and AlertFeed into a unified M8 view.
 *
 * Session 122 — M8 Real-Time Operations.
 */
import { useCallback, useEffect, useMemo } from 'react';
import { useOperationsStore } from '../../stores/operationsStore';
import type { SolverStrategy } from '../../stores/operationsStore';
import { useSocketIO } from '../../hooks/useSocketIO';
import { LiveFleetMap } from '../../components/sotreg/LiveFleetMap';
import { DemandForecastChart } from '../../components/sotreg/DemandForecastChart';
import { DriverRiskHeatmap } from '../../components/sotreg/DriverRiskHeatmap';
import { RouteOptimizationPanel } from '../../components/sotreg/RouteOptimizationPanel';
import { AlertFeed } from '../../components/sotreg/AlertFeed';

/* ── Demo data for initial render ────────────────────────────────────────── */
const DEMO_DRIVERS = [
  {
    driverId: 'd1',
    name: 'Ahmed Tazi',
    riskScore: 92,
    riskCategory: 'low' as const,
    ligneId: 'l1',
    infractions: { speed: 0, acceleration: 1, braking: 0, geofence: 0, drivingTime: 0 },
  },
  {
    driverId: 'd2',
    name: 'Karim Benali',
    riskScore: 68,
    riskCategory: 'medium' as const,
    ligneId: 'l1',
    infractions: { speed: 3, acceleration: 2, braking: 1, geofence: 0, drivingTime: 0 },
  },
  {
    driverId: 'd3',
    name: 'Youssef Amrani',
    riskScore: 42,
    riskCategory: 'high' as const,
    ligneId: 'l2',
    infractions: { speed: 5, acceleration: 3, braking: 2, geofence: 1, drivingTime: 0 },
  },
  {
    driverId: 'd4',
    name: 'Hassan Ouali',
    riskScore: 18,
    riskCategory: 'critical' as const,
    ligneId: 'l2',
    infractions: { speed: 8, acceleration: 4, braking: 3, geofence: 2, drivingTime: 1 },
  },
];

const DEMO_FORECAST = Array.from({ length: 48 }, (_, i) => ({
  timestamp: new Date(Date.now() + i * 30 * 60000).toISOString(),
  demand: 20 + Math.sin(i / 6) * 10 + Math.random() * 3,
  lower: 15 + Math.sin(i / 6) * 8,
  upper: 25 + Math.sin(i / 6) * 12 + Math.random() * 5,
}));

export default function OperationsDashboardPage() {
  const {
    vehicles,
    selectedVehicleId,
    selectVehicle,
    forecastData,
    selectedLigneId,
    selectLigne,
    setForecastData,
    driverRisks,
    riskFilter,
    setDriverRisks,
    setRiskFilter,
    alerts,
    solverStrategy,
    isOptimizing,
    setSolverStrategy,
    setOptimizing,
  } = useOperationsStore();

  const { status } = useSocketIO();

  // Load demo data on mount
  useEffect(() => {
    setForecastData(DEMO_FORECAST);
    setDriverRisks(DEMO_DRIVERS);
  }, [setForecastData, setDriverRisks]);

  const vehicleList = useMemo(() => Array.from(vehicles.values()), [vehicles]);

  const handleOptimize = useCallback(() => {
    setOptimizing(true);
    setTimeout(() => setOptimizing(false), 3000);
  }, [setOptimizing]);

  const handleLocateVehicle = useCallback(
    (vehicleId: string, _lat: number, _lng: number) => {
      selectVehicle(vehicleId);
    },
    [selectVehicle],
  );

  return (
    <div
      className="flex flex-col gap-4 p-4 max-w-[1600px] mx-auto"
      data-testid="operations-dashboard"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">Operations Temps Reel</h1>
          <p className="text-sm text-on-surface-variant">
            Module M8 -- Flotte, previsions, risques et alertes
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`w-2 h-2 rounded-full ${
              status === 'connected'
                ? 'bg-green-500'
                : status === 'connecting'
                  ? 'bg-amber-500 animate-pulse'
                  : 'bg-red-500'
            }`}
          />
          <span className="text-xs text-on-surface-variant capitalize">{status}</span>
        </div>
      </div>

      {/* Main layout: 60/40 split */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        {/* Left: Map (60%) */}
        <div className="lg:col-span-3">
          <LiveFleetMap
            vehicles={vehicleList}
            selectedVehicleId={selectedVehicleId}
            onSelectVehicle={selectVehicle}
          />
        </div>

        {/* Right: Side panels (40%) */}
        <div className="lg:col-span-2 space-y-4">
          <RouteOptimizationPanel
            strategy={solverStrategy}
            onStrategyChange={setSolverStrategy as (s: SolverStrategy) => void}
            isOptimizing={isOptimizing}
            onOptimize={handleOptimize}
          />
          <AlertFeed alerts={alerts} onLocateVehicle={handleLocateVehicle} />
        </div>
      </div>

      {/* Bottom row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <DemandForecastChart
          data={forecastData}
          selectedLigneId={selectedLigneId}
          onSelectLigne={selectLigne as (id: string) => void}
        />
        <DriverRiskHeatmap
          drivers={driverRisks}
          filterCategory={riskFilter}
          onFilterChange={setRiskFilter}
        />
      </div>
    </div>
  );
}
