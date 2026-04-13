import { useState, useEffect, useMemo } from 'react';
import { useDriverStore } from '@/stores/driverStore';
import type { DriverTrip, TripStop } from '@/api/driver';

/* ── Demo data ─────────────────────────────────────────────────────────── */

const DEMO_TRIPS: DriverTrip[] = [
  {
    id: 'trip-001',
    ligne_id: 'ligne-a1',
    ligne_name: 'Ligne A1 - Ain Sebaa / Usine OCP',
    vehicle_id: 'v-001',
    vehicle_plate: '12345-A-78',
    shift: 'Matin',
    status: 'completed',
    scheduled_departure: '2026-04-13T06:00:00',
    scheduled_arrival: '2026-04-13T07:15:00',
    actual_departure: '2026-04-13T06:02:00',
    actual_arrival: '2026-04-13T07:18:00',
    passenger_count_total: 38,
    stops: [
      { id: 's1', stop_name: 'Depot Ain Sebaa', scheduled_time: '06:00', actual_time: '06:02', passenger_count: 0, lat: 33.605, lng: -7.535, status: 'departed' },
      { id: 's2', stop_name: 'Bd Mohamed V', scheduled_time: '06:12', actual_time: '06:14', passenger_count: 12, lat: 33.595, lng: -7.545, status: 'departed' },
      { id: 's3', stop_name: 'Place Maarif', scheduled_time: '06:28', actual_time: '06:30', passenger_count: 15, lat: 33.585, lng: -7.625, status: 'departed' },
      { id: 's4', stop_name: 'Rond Point OCP', scheduled_time: '06:45', actual_time: '06:48', passenger_count: 11, lat: 33.575, lng: -7.650, status: 'departed' },
      { id: 's5', stop_name: 'Usine OCP', scheduled_time: '07:15', actual_time: '07:18', passenger_count: 0, lat: 33.570, lng: -7.660, status: 'arrived' },
    ],
  },
  {
    id: 'trip-002',
    ligne_id: 'ligne-b2',
    ligne_name: 'Ligne B2 - Sidi Bernoussi / Zone Industrielle',
    vehicle_id: 'v-001',
    vehicle_plate: '12345-A-78',
    shift: 'Apres-midi',
    status: 'in_progress',
    scheduled_departure: '2026-04-13T13:30:00',
    scheduled_arrival: '2026-04-13T14:45:00',
    actual_departure: '2026-04-13T13:32:00',
    actual_arrival: null,
    passenger_count_total: 42,
    stops: [
      { id: 's6', stop_name: 'Depot Bernoussi', scheduled_time: '13:30', actual_time: '13:32', passenger_count: 0, lat: 33.610, lng: -7.510, status: 'departed' },
      { id: 's7', stop_name: 'Hay Mohammadi', scheduled_time: '13:45', actual_time: '13:46', passenger_count: 18, lat: 33.600, lng: -7.530, status: 'departed' },
      { id: 's8', stop_name: 'Bd Hassan II', scheduled_time: '14:00', actual_time: null, passenger_count: 14, lat: 33.590, lng: -7.560, status: 'pending' },
      { id: 's9', stop_name: 'Zone Industrielle', scheduled_time: '14:20', actual_time: null, passenger_count: 10, lat: 33.580, lng: -7.590, status: 'pending' },
      { id: 's10', stop_name: 'Usine Principale', scheduled_time: '14:45', actual_time: null, passenger_count: 0, lat: 33.575, lng: -7.610, status: 'pending' },
    ],
  },
  {
    id: 'trip-003',
    ligne_id: 'ligne-c3',
    ligne_name: 'Ligne C3 - Hay Hassani / Site Jorf',
    vehicle_id: 'v-001',
    vehicle_plate: '12345-A-78',
    shift: 'Soir',
    status: 'upcoming',
    scheduled_departure: '2026-04-13T18:00:00',
    scheduled_arrival: '2026-04-13T19:30:00',
    actual_departure: null,
    actual_arrival: null,
    passenger_count_total: 35,
    stops: [
      { id: 's11', stop_name: 'Depot Hay Hassani', scheduled_time: '18:00', actual_time: null, passenger_count: 0, lat: 33.555, lng: -7.680, status: 'pending' },
      { id: 's12', stop_name: 'Av. des FAR', scheduled_time: '18:15', actual_time: null, passenger_count: 20, lat: 33.560, lng: -7.650, status: 'pending' },
      { id: 's13', stop_name: 'Centre Ville', scheduled_time: '18:35', actual_time: null, passenger_count: 15, lat: 33.575, lng: -7.620, status: 'pending' },
      { id: 's14', stop_name: 'Site Jorf', scheduled_time: '19:30', actual_time: null, passenger_count: 0, lat: 33.580, lng: -7.590, status: 'pending' },
    ],
  },
];

/* ── Status helpers ────────────────────────────────────────────────────── */

const STATUS_CONFIG: Record<
  DriverTrip['status'],
  { label: string; className: string }
> = {
  upcoming: { label: 'A venir', className: 'bg-primary/10 text-primary' },
  in_progress: {
    label: 'En cours',
    className: 'bg-green-50 text-green-700 animate-pulse',
  },
  completed: { label: 'Termine', className: 'bg-slate-100 text-slate-500' },
  cancelled: {
    label: 'Annule',
    className: 'bg-error-container/30 text-error',
  },
};

const STOP_STATUS_CONFIG: Record<
  TripStop['status'],
  { icon: string; className: string }
> = {
  pending: { icon: 'radio_button_unchecked', className: 'text-slate-400' },
  arrived: { icon: 'location_on', className: 'text-primary' },
  departed: { icon: 'check_circle', className: 'text-green-600' },
  skipped: { icon: 'cancel', className: 'text-error' },
};

/* ── Component ─────────────────────────────────────────────────────────── */

export function DriverTripsPage() {
  const { setTrips, setActiveTrip } = useDriverStore();
  const [trips, setLocalTrips] = useState<DriverTrip[]>([]);
  const [expandedTrip, setExpandedTrip] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load demo data
    const timer = setTimeout(() => {
      setLocalTrips(DEMO_TRIPS);
      setTrips(DEMO_TRIPS);
      const active = DEMO_TRIPS.find((t) => t.status === 'in_progress') ?? null;
      setActiveTrip(active);
      setLoading(false);
    }, 300);
    return () => clearTimeout(timer);
  }, [setTrips, setActiveTrip]);

  const activeTrip = useMemo(
    () => trips.find((t) => t.status === 'in_progress') ?? null,
    [trips],
  );

  const nextStop = useMemo(() => {
    if (!activeTrip) return null;
    return activeTrip.stops.find((s) => s.status === 'pending') ?? null;
  }, [activeTrip]);

  const progressPct = useMemo(() => {
    if (!activeTrip) return 0;
    const total = activeTrip.stops.length;
    const done = activeTrip.stops.filter(
      (s) => s.status === 'departed' || s.status === 'arrived',
    ).length;
    return Math.round((done / total) * 100);
  }, [activeTrip]);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center text-on-surface-variant text-sm">
        <span className="material-symbols-outlined animate-spin mr-2">
          progress_activity
        </span>
        Chargement des trajets...
      </div>
    );
  }

  if (trips.length === 0) {
    return (
      <div
        className="flex-1 flex flex-col items-center justify-center gap-3"
        data-testid="trips-empty"
      >
        <span className="material-symbols-outlined text-5xl text-on-surface-variant/40">
          no_transfer
        </span>
        <p className="text-sm text-on-surface-variant">
          Aucun trajet prevu pour aujourd&apos;hui
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="driver-trips-page">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-on-surface">Mes Trajets</h1>
        <p className="text-sm text-on-surface-variant mt-1">
          {trips.length} trajet{trips.length > 1 ? 's' : ''} aujourd&apos;hui
        </p>
      </div>

      {/* Active trip highlight */}
      {activeTrip && (
        <div
          className="bg-surface-container-lowest rounded-xl shadow-sm border-2 border-primary/30 p-6"
          data-testid="active-trip-card"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-green-50 flex items-center justify-center">
                <span className="material-symbols-outlined text-green-600 text-xl">
                  directions_bus
                </span>
              </div>
              <div>
                <h2 className="text-base font-semibold text-on-surface">
                  {activeTrip.ligne_name}
                </h2>
                <p className="text-xs text-on-surface-variant">
                  {activeTrip.vehicle_plate} - Shift {activeTrip.shift}
                </p>
              </div>
            </div>
            <span className="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold bg-green-50 text-green-700 animate-pulse">
              En cours
            </span>
          </div>

          {/* Progress bar */}
          <div className="mb-3">
            <div className="flex items-center justify-between text-xs text-on-surface-variant mb-1">
              <span>Progression</span>
              <span className="font-semibold text-on-surface">
                {progressPct}%
              </span>
            </div>
            <div className="h-2 rounded-full bg-surface-container-high overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-primary to-primary-container transition-all duration-500"
                style={{ width: `${progressPct}%` }}
              />
            </div>
          </div>

          {/* Next stop countdown */}
          {nextStop && (
            <div className="flex items-center gap-2 bg-primary/5 rounded-lg p-3">
              <span className="material-symbols-outlined text-primary text-lg">
                next_plan
              </span>
              <div className="flex-1">
                <span className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                  Prochain arret
                </span>
                <p className="text-sm font-semibold text-on-surface">
                  {nextStop.stop_name}
                </p>
              </div>
              <div className="text-right">
                <span className="text-xs text-on-surface-variant">Prevu</span>
                <p className="text-sm font-bold text-primary">
                  {nextStop.scheduled_time}
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* All trips list */}
      <div className="space-y-3">
        {trips.map((trip) => {
          const config = STATUS_CONFIG[trip.status];
          const isExpanded = expandedTrip === trip.id;
          const isActive = trip.status === 'in_progress';

          return (
            <div
              key={trip.id}
              className={[
                'bg-surface-container-lowest rounded-xl shadow-sm border p-5 transition-all',
                isActive
                  ? 'border-primary/20'
                  : 'border-outline-variant/10',
              ].join(' ')}
              data-testid={`trip-card-${trip.id}`}
            >
              {/* Trip header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div
                    className={[
                      'w-10 h-10 rounded-lg flex items-center justify-center shrink-0',
                      trip.status === 'completed'
                        ? 'bg-slate-100'
                        : trip.status === 'in_progress'
                          ? 'bg-green-50'
                          : 'bg-primary/10',
                    ].join(' ')}
                  >
                    <span
                      className={[
                        'material-symbols-outlined text-xl',
                        trip.status === 'completed'
                          ? 'text-slate-400'
                          : trip.status === 'in_progress'
                            ? 'text-green-600'
                            : 'text-primary',
                      ].join(' ')}
                    >
                      directions_bus
                    </span>
                  </div>
                  <div className="min-w-0">
                    <h3 className="text-sm font-semibold text-on-surface truncate">
                      {trip.ligne_name}
                    </h3>
                    <div className="flex items-center gap-2 text-xs text-on-surface-variant mt-0.5">
                      <span>{trip.vehicle_plate}</span>
                      <span className="w-1 h-1 rounded-full bg-outline-variant" />
                      <span>Shift {trip.shift}</span>
                      <span className="w-1 h-1 rounded-full bg-outline-variant" />
                      <span>{trip.passenger_count_total} passagers</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  {/* Times */}
                  <div className="text-right">
                    <p className="text-xs text-on-surface-variant">
                      {trip.scheduled_departure.split('T')[1]?.slice(0, 5)} -{' '}
                      {trip.scheduled_arrival.split('T')[1]?.slice(0, 5)}
                    </p>
                  </div>

                  {/* Status badge */}
                  <span
                    className={[
                      'inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold',
                      config.className,
                    ].join(' ')}
                  >
                    {config.label}
                  </span>

                  {/* Expand button */}
                  <button
                    onClick={() =>
                      setExpandedTrip(isExpanded ? null : trip.id)
                    }
                    className="w-8 h-8 rounded-lg flex items-center justify-center text-on-surface-variant hover:bg-surface-container-high transition-colors"
                  >
                    <span
                      className={[
                        'material-symbols-outlined text-lg transition-transform duration-200',
                        isExpanded ? 'rotate-180' : '',
                      ].join(' ')}
                    >
                      expand_more
                    </span>
                  </button>
                </div>
              </div>

              {/* Expanded stop list */}
              {isExpanded && (
                <div className="mt-4 pt-4 border-t border-outline-variant/10">
                  <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">
                    Arrets ({trip.stops.length})
                  </p>
                  <div className="space-y-2">
                    {trip.stops.map((stop, idx) => {
                      const stopCfg = STOP_STATUS_CONFIG[stop.status];
                      const isLast = idx === trip.stops.length - 1;
                      return (
                        <div
                          key={stop.id}
                          className="flex items-center gap-3"
                          data-testid={`stop-${stop.id}`}
                        >
                          {/* Timeline dot */}
                          <div className="flex flex-col items-center">
                            <span
                              className={[
                                'material-symbols-outlined text-base',
                                stopCfg.className,
                              ].join(' ')}
                            >
                              {stopCfg.icon}
                            </span>
                            {!isLast && (
                              <div className="w-0.5 h-4 bg-outline-variant/20" />
                            )}
                          </div>

                          {/* Stop details */}
                          <div className="flex-1 flex items-center justify-between min-w-0">
                            <div className="min-w-0">
                              <p className="text-sm text-on-surface truncate">
                                {stop.stop_name}
                              </p>
                              {stop.passenger_count > 0 && (
                                <p className="text-xs text-on-surface-variant">
                                  {stop.passenger_count} passagers
                                </p>
                              )}
                            </div>
                            <div className="text-right shrink-0 ml-3">
                              <p className="text-xs text-on-surface-variant">
                                {stop.scheduled_time}
                              </p>
                              {stop.actual_time && (
                                <p className="text-xs font-medium text-on-surface">
                                  {stop.actual_time}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
