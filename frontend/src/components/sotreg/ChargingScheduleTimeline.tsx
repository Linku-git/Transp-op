import { useState, useCallback, useMemo } from 'react';
import { computeChargingOptimization } from '@/api/sotreg';
import { extractApiError } from '@/lib/apiError';
import type {
  ChargingOptimizationRequest,
  ChargingOptimizationResponse,
  ChargingWindowSchedule,
} from '@/types/sotreg';

/* ── Constants ────────────────────────────────────────────────────────────── */

/** ONEE tariff windows (Morocco) */
const ONEE_WINDOWS = [
  { name: 'creuse', label: 'Heures creuses', start: 22, end: 7, color: '#16a34a', bgClass: 'bg-green-500' },
  { name: 'pleine', label: 'Heures pleines', start: 7, end: 17, color: '#d97706', bgClass: 'bg-amber-500' },
  { name: 'pointe', label: 'Heures de pointe', start: 17, end: 22, color: '#dc2626', bgClass: 'bg-red-500' },
] as const;

/** Hours in the 24h timeline */
const HOURS = Array.from({ length: 25 }, (_, i) => i);

/* ── Helpers ──────────────────────────────────────────────────────────────── */

const madFmt = new Intl.NumberFormat('fr-MA', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

function fmtMAD(value: number): string {
  return `${madFmt.format(value)} MAD`;
}

function fmtNum(value: number, decimals = 1): string {
  return value.toLocaleString('fr-MA', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/**
 * Convert hour to left percentage on a 24h bar.
 * Handles wrap-around (e.g. 22h start, 7h end = wraps past midnight).
 */
function hourToPct(hour: number): number {
  return (hour / 24) * 100;
}

/**
 * Get the ONEE window background color for a given hour.
 */
function getWindowColorForHour(hour: number): string {
  // pointe: 17-22
  if (hour >= 17 && hour < 22) return 'rgba(220, 38, 38, 0.15)';
  // pleine: 7-17
  if (hour >= 7 && hour < 17) return 'rgba(217, 119, 6, 0.15)';
  // creuse: 22-7 (wraps midnight)
  return 'rgba(22, 163, 74, 0.15)';
}

/**
 * Resolve a charging window's position on the 24h timeline.
 * Returns array of {leftPct, widthPct} segments (may be 2 if wrapping midnight).
 */
function resolveWindowSegments(
  startHour: number,
  endHour: number,
): Array<{ leftPct: number; widthPct: number }> {
  if (startHour < endHour) {
    return [{ leftPct: hourToPct(startHour), widthPct: hourToPct(endHour - startHour) }];
  }
  // Wraps midnight
  return [
    { leftPct: hourToPct(startHour), widthPct: hourToPct(24 - startHour) },
    { leftPct: 0, widthPct: hourToPct(endHour) },
  ];
}

/**
 * Map a schedule window_name to a display color.
 */
function scheduleWindowColor(name: string): string {
  if (name.includes('creuse')) return '#16a34a';
  if (name.includes('pointe')) return '#dc2626';
  return '#d97706';
}

/* ── Timeline bar ─────────────────────────────────────────────────────────── */

function TimelineBar({ schedule }: { schedule: ChargingWindowSchedule[] }) {
  /* Build 24 hour-wide background segments for ONEE windows */
  const hourSegments = useMemo(
    () =>
      Array.from({ length: 24 }, (_, h) => ({
        hour: h,
        leftPct: hourToPct(h),
        widthPct: hourToPct(1),
        bg: getWindowColorForHour(h),
      })),
    [],
  );

  return (
    <div className="space-y-2">
      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
        Planning de charge (24h)
      </p>

      {/* Timeline container */}
      <div className="relative h-12 rounded-lg overflow-hidden border border-outline-variant/10">
        {/* ONEE background bands */}
        {hourSegments.map((seg) => (
          <div
            key={seg.hour}
            className="absolute top-0 bottom-0"
            style={{
              left: `${seg.leftPct}%`,
              width: `${seg.widthPct}%`,
              backgroundColor: seg.bg,
            }}
          />
        ))}

        {/* Charging windows overlays */}
        {schedule.map((window) => {
          const segments = resolveWindowSegments(window.start_hour, window.end_hour);
          const color = scheduleWindowColor(window.window_name);
          return segments.map((seg, idx) => (
            <div
              key={`${window.window_name}-${idx}`}
              className="absolute top-1 bottom-1 rounded flex items-center justify-center"
              style={{
                left: `${seg.leftPct}%`,
                width: `${seg.widthPct}%`,
                backgroundColor: color,
                opacity: 0.7,
              }}
              title={`${window.window_name}: ${fmtNum(window.energy_kwh, 1)} kWh — ${fmtMAD(window.cost_mad)}`}
            >
              {seg.widthPct > 8 && (
                <span className="text-white text-[10px] font-semibold truncate px-1">
                  {fmtNum(window.energy_kwh, 0)} kWh
                </span>
              )}
            </div>
          ));
        })}
      </div>

      {/* Hour labels */}
      <div className="relative h-4">
        {HOURS.filter((h) => h % 3 === 0).map((h) => (
          <span
            key={h}
            className="absolute text-[9px] text-on-surface-variant font-medium -translate-x-1/2"
            style={{ left: `${hourToPct(h)}%` }}
          >
            {h}h
          </span>
        ))}
      </div>

      {/* ONEE legend */}
      <div className="flex items-center gap-4 mt-1">
        {ONEE_WINDOWS.map((w) => (
          <div key={w.name} className="flex items-center gap-1.5">
            <span
              className="inline-block w-2.5 h-2.5 rounded-full flex-shrink-0"
              style={{ backgroundColor: w.color }}
            />
            <span className="text-[10px] text-on-surface-variant">{w.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ── Schedule detail table ────────────────────────────────────────────────── */

function ScheduleDetail({ schedule }: { schedule: ChargingWindowSchedule[] }) {
  if (schedule.length === 0) return null;

  return (
    <div className="overflow-hidden rounded-lg border border-outline-variant/10">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-surface-container-low/50">
            <th className="text-left px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
              Fenetre
            </th>
            <th className="text-right px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
              Duree
            </th>
            <th className="text-right px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
              Energie
            </th>
            <th className="text-right px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
              Cout
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-outline-variant/10">
          {schedule.map((window) => (
            <tr key={window.window_name} className="hover:bg-surface-bright">
              <td className="px-3 py-2 font-medium text-on-surface">
                <div className="flex items-center gap-2">
                  <span
                    className="inline-block w-2 h-2 rounded-full flex-shrink-0"
                    style={{ backgroundColor: scheduleWindowColor(window.window_name) }}
                  />
                  {window.window_name}
                  <span className="text-xs text-on-surface-variant">
                    ({window.start_hour}h-{window.end_hour}h)
                  </span>
                </div>
              </td>
              <td className="px-3 py-2 text-right text-on-surface-variant">
                {fmtNum(window.duration_hours, 1)}h
              </td>
              <td className="px-3 py-2 text-right text-on-surface-variant">
                {fmtNum(window.energy_kwh, 1)} kWh
              </td>
              <td className="px-3 py-2 text-right font-medium text-on-surface">
                {fmtMAD(window.cost_mad)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ── Main component ───────────────────────────────────────────────────────── */

export function ChargingScheduleTimeline() {
  /* Form state */
  const [batteryCapacity, setBatteryCapacity] = useState(60);
  const [currentSoc, setCurrentSoc] = useState(20);
  const [targetSoc, setTargetSoc] = useState(62);
  const [chargerPower, setChargerPower] = useState(50);

  /* Async state */
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ChargingOptimizationResponse | null>(null);

  /* ── Handlers ───────────────────────────────────────────────────────────── */

  const handleOptimize = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const req: ChargingOptimizationRequest = {
        battery_capacity_kwh: batteryCapacity,
        current_soc_pct: currentSoc,
        target_soc_pct: targetSoc,
        charger_power_kw: chargerPower,
      };
      const res = await computeChargingOptimization(req);
      setResult(res);
    } catch (err) {
      setError(extractApiError(err, 'Erreur lors de l\'optimisation de charge'));
    } finally {
      setLoading(false);
    }
  }, [batteryCapacity, currentSoc, targetSoc, chargerPower]);

  /* ── Derived ────────────────────────────────────────────────────────────── */

  const noChargingNeeded = result !== null && result.energy_needed_kwh === 0;

  /* ── Render ─────────────────────────────────────────────────────────────── */

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 font-sans">
      {/* Header */}
      <div className="flex items-center gap-2 mb-5">
        <span className="material-symbols-outlined text-primary text-xl">
          schedule
        </span>
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Planification de charge
        </h3>
      </div>

      {/* Compact form */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
        <div>
          <label
            htmlFor="cs-battery"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Batterie (kWh)
          </label>
          <input
            id="cs-battery"
            type="number"
            min={10}
            max={500}
            value={batteryCapacity}
            onChange={(e) => setBatteryCapacity(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>

        <div>
          <label
            htmlFor="cs-current-soc"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            SOC actuel (%)
          </label>
          <input
            id="cs-current-soc"
            type="number"
            min={0}
            max={100}
            value={currentSoc}
            onChange={(e) => setCurrentSoc(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>

        <div>
          <label
            htmlFor="cs-target-soc"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            SOC cible (%)
          </label>
          <input
            id="cs-target-soc"
            type="number"
            min={0}
            max={100}
            value={targetSoc}
            onChange={(e) => setTargetSoc(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>

        <div>
          <label
            htmlFor="cs-charger-power"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Puissance (kW)
          </label>
          <input
            id="cs-charger-power"
            type="number"
            min={3}
            max={350}
            value={chargerPower}
            onChange={(e) => setChargerPower(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>
      </div>

      {/* Optimize button */}
      <button
        type="button"
        onClick={handleOptimize}
        disabled={loading}
        className="inline-flex items-center gap-2 bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-lg shadow-lg shadow-primary/20 px-5 py-2.5 text-sm font-medium transition-opacity hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <>
            <span className="material-symbols-outlined animate-spin text-base">
              progress_activity
            </span>
            Optimisation en cours...
          </>
        ) : (
          <>
            <span className="material-symbols-outlined text-base">
              bolt
            </span>
            Optimiser
          </>
        )}
      </button>

      {/* Error state */}
      {error && (
        <div className="mt-4 flex items-start gap-2 bg-error-container/30 text-error rounded-lg px-4 py-3">
          <span className="material-symbols-outlined text-base mt-0.5">
            error
          </span>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* ── No charging needed ────────────────────────────────────────────── */}
      {noChargingNeeded && !loading && (
        <div className="mt-6 flex flex-col items-center justify-center py-8">
          <span className="material-symbols-outlined text-4xl text-green-500 mb-3">
            check_circle
          </span>
          <p className="font-sans text-sm font-medium text-on-surface">
            Aucune recharge necessaire
          </p>
          <p className="font-sans text-xs text-on-surface-variant mt-1">
            Le SOC actuel ({currentSoc}%) atteint deja la cible ({targetSoc}%).
          </p>
        </div>
      )}

      {/* ── Results ───────────────────────────────────────────────────────── */}
      {result && !noChargingNeeded && !loading && (
        <div className="mt-6 space-y-5">
          {/* SOC summary */}
          <div className="flex items-center justify-center gap-4 py-3">
            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
                SOC actuel
              </p>
              <p className="font-sans text-2xl font-bold text-amber-600">
                {currentSoc}%
              </p>
            </div>

            <span className="material-symbols-outlined text-2xl text-on-surface-variant">
              arrow_forward
            </span>

            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
                SOC cible
              </p>
              <p className="font-sans text-2xl font-bold text-green-600">
                {result.target_soc_pct}%
              </p>
            </div>

            <div className="h-10 w-px bg-outline-variant/20 mx-2" />

            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
                Energie requise
              </p>
              <p className="font-sans text-2xl font-bold text-on-surface">
                {fmtNum(result.energy_needed_kwh, 1)}
                <span className="text-sm font-normal text-on-surface-variant ml-1">kWh</span>
              </p>
            </div>

            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
                Duree
              </p>
              <p className="font-sans text-2xl font-bold text-on-surface">
                {fmtNum(result.charging_duration_hours, 1)}
                <span className="text-sm font-normal text-on-surface-variant ml-1">h</span>
              </p>
            </div>
          </div>

          {/* Timeline visualization */}
          <TimelineBar schedule={result.schedule} />

          {/* Schedule detail table */}
          <ScheduleDetail schedule={result.schedule} />

          {/* Cost summary cards */}
          <div>
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">
              Synthese des couts
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="bg-surface-container-low rounded-lg p-4 flex flex-col items-center gap-1.5">
                <span className="material-symbols-outlined text-xl text-on-surface-variant">
                  payments
                </span>
                <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant text-center">
                  Cout total energie
                </p>
                <p className="font-sans text-lg font-semibold text-on-surface">
                  {fmtMAD(result.total_energy_cost_mad)}
                </p>
              </div>

              <div className="bg-surface-container-low rounded-lg p-4 flex flex-col items-center gap-1.5">
                <span className="material-symbols-outlined text-xl text-on-surface-variant">
                  electric_meter
                </span>
                <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant text-center">
                  Appel de puissance
                </p>
                <p className="font-sans text-lg font-semibold text-on-surface">
                  {fmtNum(result.peak_demand_kw, 1)} kW
                </p>
              </div>

              <div className="bg-primary/10 border border-primary/15 rounded-lg p-4 flex flex-col items-center gap-1.5">
                <span className="material-symbols-outlined text-xl text-primary">
                  receipt_long
                </span>
                <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant text-center">
                  Prime mensuelle
                </p>
                <p className="font-sans text-lg font-semibold text-primary">
                  {fmtMAD(result.monthly_demand_charge_mad)}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
