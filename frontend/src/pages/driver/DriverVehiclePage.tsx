import { useState, useEffect } from 'react';
import { useDriverStore } from '@/stores/driverStore';
import type { DriverVehicle, MaintenanceAlert } from '@/api/driver';

/* ── Demo data ─────────────────────────────────────────────────────────── */

const DEMO_VEHICLE: DriverVehicle = {
  id: 'v-001',
  plate: '12345-A-78',
  type: 'Bus Standard',
  capacity: 50,
  motorization: 'Diesel Euro VI',
  fuel_level_pct: 68,
  odometer_km: 142350,
  maintenance_alerts: [
    {
      id: 'ma-1',
      type: 'Vidange moteur',
      severity: 'medium',
      message: 'Vidange moteur prevue dans 1 200 km',
      due_date: '2026-04-20',
    },
    {
      id: 'ma-2',
      type: 'Pression pneus',
      severity: 'low',
      message: 'Verification de la pression des pneus recommandee',
      due_date: '2026-04-15',
    },
    {
      id: 'ma-3',
      type: 'Freins AV',
      severity: 'high',
      message: 'Plaquettes de freins avant a remplacer prochainement',
      due_date: '2026-04-18',
    },
  ],
  telemetry: {
    speed_avg_kmh: 34.5,
    distance_today_km: 87.2,
    fuel_consumed_l: 28.4,
    engine_hours: 4.5,
  },
};

/* ── Severity helpers ──────────────────────────────────────────────────── */

const SEVERITY_CONFIG: Record<
  MaintenanceAlert['severity'],
  { label: string; className: string; icon: string }
> = {
  low: {
    label: 'Faible',
    className: 'bg-green-50 text-green-700',
    icon: 'info',
  },
  medium: {
    label: 'Moyen',
    className: 'bg-amber-50 text-amber-700',
    icon: 'warning',
  },
  high: {
    label: 'Eleve',
    className: 'bg-orange-50 text-orange-700',
    icon: 'error',
  },
  critical: {
    label: 'Critique',
    className: 'bg-error-container/30 text-error',
    icon: 'dangerous',
  },
};

/* ── Issue report types ────────────────────────────────────────────────── */

const ISSUE_TYPES = [
  'Moteur',
  'Freins',
  'Pneus',
  'Eclairage',
  'Climatisation',
  'Carrosserie',
  'Tableau de bord',
  'Autre',
];

/* ── Component ─────────────────────────────────────────────────────────── */

export function DriverVehiclePage() {
  const { setVehicle } = useDriverStore();
  const [vehicle, setLocalVehicle] = useState<DriverVehicle | null>(null);
  const [loading, setLoading] = useState(true);
  const [showReportModal, setShowReportModal] = useState(false);
  const [issueType, setIssueType] = useState(ISSUE_TYPES[0]);
  const [issueDescription, setIssueDescription] = useState('');
  const [reportSubmitted, setReportSubmitted] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setLocalVehicle(DEMO_VEHICLE);
      setVehicle(DEMO_VEHICLE);
      setLoading(false);
    }, 300);
    return () => clearTimeout(timer);
  }, [setVehicle]);

  const handleReportSubmit = () => {
    // Simulate submission
    setReportSubmitted(true);
    setTimeout(() => {
      setShowReportModal(false);
      setReportSubmitted(false);
      setIssueType(ISSUE_TYPES[0]);
      setIssueDescription('');
    }, 1500);
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center text-on-surface-variant text-sm">
        <span className="material-symbols-outlined animate-spin mr-2">
          progress_activity
        </span>
        Chargement du vehicule...
      </div>
    );
  }

  if (!vehicle) {
    return (
      <div
        className="flex-1 flex flex-col items-center justify-center gap-3"
        data-testid="vehicle-empty"
      >
        <span className="material-symbols-outlined text-5xl text-on-surface-variant/40">
          no_crash
        </span>
        <p className="text-sm text-on-surface-variant">
          Aucun vehicule assigne pour le moment
        </p>
      </div>
    );
  }

  const fuelColor =
    vehicle.fuel_level_pct > 50
      ? 'bg-green-500'
      : vehicle.fuel_level_pct > 25
        ? 'bg-amber-500'
        : 'bg-error';

  return (
    <div className="space-y-6" data-testid="driver-vehicle-page">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">Mon Vehicule</h1>
          <p className="text-sm text-on-surface-variant mt-1">
            Etat et informations du vehicule assigne
          </p>
        </div>
        <button
          onClick={() => setShowReportModal(true)}
          className="flex items-center gap-2 bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-lg shadow-lg shadow-primary/20 px-4 py-2.5 text-sm font-semibold transition-transform hover:scale-[1.02] active:scale-[0.98]"
          data-testid="report-issue-btn"
        >
          <span className="material-symbols-outlined text-lg">report</span>
          Signaler un probleme
        </button>
      </div>

      {/* Vehicle info card */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
        <div className="flex items-start gap-6">
          {/* Vehicle icon */}
          <div className="w-16 h-16 rounded-xl bg-primary/10 flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined text-primary text-3xl">
              directions_bus
            </span>
          </div>

          {/* Vehicle details */}
          <div className="flex-1 grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                Immatriculation
              </p>
              <p className="text-base font-semibold text-on-surface mt-0.5">
                {vehicle.plate}
              </p>
            </div>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                Type
              </p>
              <p className="text-base font-semibold text-on-surface mt-0.5">
                {vehicle.type}
              </p>
            </div>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                Capacite
              </p>
              <p className="text-base font-semibold text-on-surface mt-0.5">
                {vehicle.capacity} places
              </p>
            </div>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                Motorisation
              </p>
              <p className="text-base font-semibold text-on-surface mt-0.5">
                {vehicle.motorization}
              </p>
            </div>
          </div>
        </div>

        {/* Fuel gauge */}
        <div className="mt-6 pt-6 border-t border-outline-variant/10">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-on-surface-variant text-lg">
                local_gas_station
              </span>
              <span className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                Niveau carburant
              </span>
            </div>
            <span className="text-sm font-bold text-on-surface">
              {vehicle.fuel_level_pct}%
            </span>
          </div>
          <div className="h-3 rounded-full bg-surface-container-high overflow-hidden">
            <div
              className={`h-full rounded-full ${fuelColor} transition-all duration-500`}
              style={{ width: `${vehicle.fuel_level_pct}%` }}
              data-testid="fuel-gauge"
            />
          </div>
          <p className="text-xs text-on-surface-variant mt-1">
            Compteur: {vehicle.odometer_km.toLocaleString('fr-FR')} km
          </p>
        </div>
      </div>

      {/* Telemetry card */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
        <h2 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
          Telemetrie du jour
        </h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-surface-container-low rounded-lg p-4 text-center">
            <span className="material-symbols-outlined text-primary text-2xl">
              speed
            </span>
            <p className="text-2xl font-bold text-on-surface mt-1">
              {vehicle.telemetry.speed_avg_kmh}
            </p>
            <p className="text-xs text-on-surface-variant">km/h moyenne</p>
          </div>
          <div className="bg-surface-container-low rounded-lg p-4 text-center">
            <span className="material-symbols-outlined text-primary text-2xl">
              straighten
            </span>
            <p className="text-2xl font-bold text-on-surface mt-1">
              {vehicle.telemetry.distance_today_km}
            </p>
            <p className="text-xs text-on-surface-variant">km parcourus</p>
          </div>
          <div className="bg-surface-container-low rounded-lg p-4 text-center">
            <span className="material-symbols-outlined text-primary text-2xl">
              local_gas_station
            </span>
            <p className="text-2xl font-bold text-on-surface mt-1">
              {vehicle.telemetry.fuel_consumed_l}
            </p>
            <p className="text-xs text-on-surface-variant">litres consommes</p>
          </div>
          <div className="bg-surface-container-low rounded-lg p-4 text-center">
            <span className="material-symbols-outlined text-primary text-2xl">
              schedule
            </span>
            <p className="text-2xl font-bold text-on-surface mt-1">
              {vehicle.telemetry.engine_hours}
            </p>
            <p className="text-xs text-on-surface-variant">heures moteur</p>
          </div>
        </div>
      </div>

      {/* Maintenance alerts */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
        <h2 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
          Alertes de maintenance ({vehicle.maintenance_alerts.length})
        </h2>
        {vehicle.maintenance_alerts.length === 0 ? (
          <p className="text-sm text-on-surface-variant">
            Aucune alerte de maintenance
          </p>
        ) : (
          <div className="space-y-3">
            {vehicle.maintenance_alerts
              .sort((a, b) => {
                const order = { critical: 0, high: 1, medium: 2, low: 3 };
                return order[a.severity] - order[b.severity];
              })
              .map((alert) => {
                const cfg = SEVERITY_CONFIG[alert.severity];
                return (
                  <div
                    key={alert.id}
                    className="flex items-center gap-4 bg-surface-container-low rounded-lg p-4"
                    data-testid={`alert-${alert.id}`}
                  >
                    <span
                      className={[
                        'material-symbols-outlined text-xl',
                        cfg.className.split(' ')[1],
                      ].join(' ')}
                    >
                      {cfg.icon}
                    </span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-semibold text-on-surface">
                          {alert.type}
                        </p>
                        <span
                          className={[
                            'inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold',
                            cfg.className,
                          ].join(' ')}
                        >
                          {cfg.label}
                        </span>
                      </div>
                      <p className="text-xs text-on-surface-variant mt-0.5">
                        {alert.message}
                      </p>
                    </div>
                    <div className="text-right shrink-0">
                      <p className="text-xs text-on-surface-variant">Echeance</p>
                      <p className="text-sm font-medium text-on-surface">
                        {new Date(alert.due_date).toLocaleDateString('fr-FR')}
                      </p>
                    </div>
                  </div>
                );
              })}
          </div>
        )}
      </div>

      {/* Report issue modal */}
      {showReportModal && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="bg-surface-container-lowest rounded-xl shadow-2xl border border-outline-variant/10 p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-on-surface">
                Signaler un probleme
              </h3>
              <button
                onClick={() => setShowReportModal(false)}
                className="w-8 h-8 rounded-lg flex items-center justify-center text-on-surface-variant hover:bg-surface-container-high transition-colors"
              >
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            {reportSubmitted ? (
              <div className="flex flex-col items-center gap-3 py-8">
                <span className="material-symbols-outlined text-green-600 text-4xl">
                  check_circle
                </span>
                <p className="text-sm font-medium text-on-surface">
                  Signalement envoye avec succes
                </p>
              </div>
            ) : (
              <>
                <div className="space-y-4">
                  <div>
                    <label className="block text-[10px] font-bold uppercase tracking-widest text-outline mb-1.5">
                      Type de probleme
                    </label>
                    <select
                      value={issueType}
                      onChange={(e) => setIssueType(e.target.value)}
                      className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2.5 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
                      data-testid="issue-type-select"
                    >
                      {ISSUE_TYPES.map((type) => (
                        <option key={type} value={type}>
                          {type}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold uppercase tracking-widest text-outline mb-1.5">
                      Description
                    </label>
                    <textarea
                      value={issueDescription}
                      onChange={(e) => setIssueDescription(e.target.value)}
                      rows={4}
                      placeholder="Decrivez le probleme rencontre..."
                      className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2.5 text-sm text-on-surface placeholder:text-on-surface-variant/60 focus:ring-2 focus:ring-primary/20 outline-none resize-none"
                      data-testid="issue-description"
                    />
                  </div>
                </div>

                <div className="flex items-center gap-3 mt-6">
                  <button
                    onClick={() => setShowReportModal(false)}
                    className="flex-1 bg-surface-container-lowest text-primary border border-outline-variant/15 rounded-lg shadow-sm px-4 py-2.5 text-sm font-semibold transition-colors hover:bg-surface-container-low"
                  >
                    Annuler
                  </button>
                  <button
                    onClick={handleReportSubmit}
                    disabled={!issueDescription.trim()}
                    className="flex-1 bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-lg shadow-lg shadow-primary/20 px-4 py-2.5 text-sm font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-transform hover:scale-[1.02] active:scale-[0.98]"
                    data-testid="submit-issue-btn"
                  >
                    Envoyer
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
