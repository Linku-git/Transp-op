/**
 * Zustand store for real-time operations dashboard state.
 *
 * Manages vehicle positions, alerts, forecast data, driver risk data,
 * and optimization controls.
 *
 * Session 122 — M8 Real-Time Operations.
 */
import { create } from 'zustand';

export interface VehicleMarker {
  id: string;
  lat: number;
  lng: number;
  speed: number;
  heading: number;
  ligneId: string;
  ligneName: string;
  passengers: number;
  lastUpdate: number;
}

export interface ForecastPoint {
  timestamp: string;
  demand: number;
  lower: number;
  upper: number;
}

export interface DriverRisk {
  driverId: string;
  name: string;
  riskScore: number;
  riskCategory: 'low' | 'medium' | 'high' | 'critical';
  ligneId: string;
  infractions: {
    speed: number;
    acceleration: number;
    braking: number;
    geofence: number;
    drivingTime: number;
  };
}

export interface OperationAlert {
  id: string;
  type: 'geofence_alert' | 'route_deviation' | 'maintenance' | 'speed';
  severity: 'info' | 'warning' | 'critical';
  vehicleId: string;
  message: string;
  lat: number;
  lng: number;
  timestamp: number;
}

export type SolverStrategy = 'ortools' | 'cw' | 'ga';

interface OperationsState {
  // Vehicles
  vehicles: Map<string, VehicleMarker>;
  selectedVehicleId: string | null;

  // Forecast
  forecastData: ForecastPoint[];
  selectedLigneId: string | null;

  // Driver Risk
  driverRisks: DriverRisk[];
  riskFilter: string | null;

  // Alerts
  alerts: OperationAlert[];

  // Optimization
  solverStrategy: SolverStrategy;
  isOptimizing: boolean;

  // Actions
  updateVehicle: (vehicle: VehicleMarker) => void;
  selectVehicle: (id: string | null) => void;
  setForecastData: (data: ForecastPoint[]) => void;
  selectLigne: (id: string | null) => void;
  setDriverRisks: (risks: DriverRisk[]) => void;
  setRiskFilter: (filter: string | null) => void;
  addAlert: (alert: OperationAlert) => void;
  clearAlerts: () => void;
  setSolverStrategy: (strategy: SolverStrategy) => void;
  setOptimizing: (val: boolean) => void;
}

export const useOperationsStore = create<OperationsState>((set) => ({
  vehicles: new Map(),
  selectedVehicleId: null,
  forecastData: [],
  selectedLigneId: null,
  driverRisks: [],
  riskFilter: null,
  alerts: [],
  solverStrategy: 'ortools',
  isOptimizing: false,

  updateVehicle: (vehicle) =>
    set((state) => {
      const updated = new Map(state.vehicles);
      updated.set(vehicle.id, vehicle);
      return { vehicles: updated };
    }),

  selectVehicle: (id) => set({ selectedVehicleId: id }),

  setForecastData: (data) => set({ forecastData: data }),

  selectLigne: (id) => set({ selectedLigneId: id }),

  setDriverRisks: (risks) => set({ driverRisks: risks }),

  setRiskFilter: (filter) => set({ riskFilter: filter }),

  addAlert: (alert) =>
    set((state) => ({
      alerts: [alert, ...state.alerts].slice(0, 100), // keep last 100
    })),

  clearAlerts: () => set({ alerts: [] }),

  setSolverStrategy: (strategy) => set({ solverStrategy: strategy }),

  setOptimizing: (val) => set({ isOptimizing: val }),
}));
