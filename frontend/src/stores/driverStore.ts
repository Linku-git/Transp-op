import { create } from 'zustand';
import type {
  DriverTrip,
  DriverVehicle,
  DriverRiskProfile,
  ScheduleDay,
} from '../api/driver';

interface DriverState {
  trips: DriverTrip[];
  vehicle: DriverVehicle | null;
  riskProfile: DriverRiskProfile | null;
  schedule: ScheduleDay[];
  activeTrip: DriverTrip | null;
  unreadNotifications: number;

  setTrips: (trips: DriverTrip[]) => void;
  setVehicle: (vehicle: DriverVehicle) => void;
  setRiskProfile: (profile: DriverRiskProfile) => void;
  setSchedule: (schedule: ScheduleDay[]) => void;
  setActiveTrip: (trip: DriverTrip | null) => void;
  setUnreadNotifications: (count: number) => void;
}

export const useDriverStore = create<DriverState>((set) => ({
  trips: [],
  vehicle: null,
  riskProfile: null,
  schedule: [],
  activeTrip: null,
  unreadNotifications: 3,

  setTrips: (trips) => set({ trips }),
  setVehicle: (vehicle) => set({ vehicle }),
  setRiskProfile: (profile) => set({ riskProfile: profile }),
  setSchedule: (schedule) => set({ schedule }),
  setActiveTrip: (trip) => set({ activeTrip: trip }),
  setUnreadNotifications: (count) => set({ unreadNotifications: count }),
}));
