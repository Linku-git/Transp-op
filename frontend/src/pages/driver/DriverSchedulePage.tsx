import { useState, useEffect } from 'react';
import { useDriverStore } from '@/stores/driverStore';
import type { ScheduleDay } from '@/api/driver';

/* ── Demo data ─────────────────────────────────────────────────────────── */

function buildDemoSchedule(weekOffset: number): ScheduleDay[] {
  const base = new Date('2026-04-13'); // Sunday
  base.setDate(base.getDate() + weekOffset * 7);

  // Find Monday of that week
  const monday = new Date(base);
  const dayOfWeek = monday.getDay();
  const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
  monday.setDate(monday.getDate() + diff);

  const dayNames = [
    'Lundi',
    'Mardi',
    'Mercredi',
    'Jeudi',
    'Vendredi',
    'Samedi',
    'Dimanche',
  ];

  const schedule: ScheduleDay[] = [];

  for (let i = 0; i < 7; i++) {
    const d = new Date(monday);
    d.setDate(d.getDate() + i);
    const dateStr = d.toISOString().slice(0, 10);
    const isRestDay = i >= 5; // Saturday and Sunday off

    if (isRestDay) {
      schedule.push({
        date: dateStr,
        day_name: dayNames[i],
        trips: [],
        rest_hours: 24,
        is_rest_day: true,
      });
    } else {
      const trips = [
        {
          ligne_name: 'Ligne A1 - Ain Sebaa',
          vehicle_plate: '12345-A-78',
          shift: 'Matin',
          departure: '06:00',
          arrival: '07:15',
          is_lto_optimized: i === 0 || i === 2,
        },
        {
          ligne_name: 'Ligne B2 - Bernoussi',
          vehicle_plate: '12345-A-78',
          shift: 'Apres-midi',
          departure: '13:30',
          arrival: '14:45',
          is_lto_optimized: false,
        },
      ];

      // Add evening trip on some days
      if (i === 1 || i === 3) {
        trips.push({
          ligne_name: 'Ligne C3 - Hay Hassani',
          vehicle_plate: '12345-A-78',
          shift: 'Soir',
          departure: '18:00',
          arrival: '19:30',
          is_lto_optimized: true,
        });
      }

      schedule.push({
        date: dateStr,
        day_name: dayNames[i],
        trips,
        rest_hours: i === 1 || i === 3 ? 10.5 : 13.25,
        is_rest_day: false,
      });
    }
  }

  return schedule;
}

/* ── Component ─────────────────────────────────────────────────────────── */

export function DriverSchedulePage() {
  const { setSchedule } = useDriverStore();
  const [schedule, setLocalSchedule] = useState<ScheduleDay[]>([]);
  const [weekOffset, setWeekOffset] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showSwapModal, setShowSwapModal] = useState(false);
  const [swapTarget, setSwapTarget] = useState<{
    day: string;
    trip: string;
  } | null>(null);
  const [swapReason, setSwapReason] = useState('');
  const [swapSubmitted, setSwapSubmitted] = useState(false);

  useEffect(() => {
    setLoading(true);
    const timer = setTimeout(() => {
      const data = buildDemoSchedule(weekOffset);
      setLocalSchedule(data);
      setSchedule(data);
      setLoading(false);
    }, 300);
    return () => clearTimeout(timer);
  }, [weekOffset, setSchedule]);

  const weekLabel = (() => {
    if (schedule.length === 0) return '';
    const first = schedule[0];
    const last = schedule[schedule.length - 1];
    const f = new Date(first.date).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
    });
    const l = new Date(last.date).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
    return `${f} - ${l}`;
  })();

  const handleSwapRequest = (dayName: string, tripName: string) => {
    setSwapTarget({ day: dayName, trip: tripName });
    setShowSwapModal(true);
  };

  const handleSwapSubmit = () => {
    setSwapSubmitted(true);
    setTimeout(() => {
      setShowSwapModal(false);
      setSwapSubmitted(false);
      setSwapTarget(null);
      setSwapReason('');
    }, 1500);
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center text-on-surface-variant text-sm">
        <span className="material-symbols-outlined animate-spin mr-2">
          progress_activity
        </span>
        Chargement du planning...
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="driver-schedule-page">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">Planning</h1>
          <p className="text-sm text-on-surface-variant mt-1">
            Planning hebdomadaire des trajets
          </p>
        </div>

        {/* Week navigation */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setWeekOffset((w) => w - 1)}
            className="w-9 h-9 rounded-lg flex items-center justify-center text-on-surface-variant hover:bg-surface-container-high transition-colors"
            data-testid="prev-week-btn"
          >
            <span className="material-symbols-outlined">chevron_left</span>
          </button>
          <span className="text-sm font-semibold text-on-surface min-w-[180px] text-center">
            {weekLabel}
          </span>
          <button
            onClick={() => setWeekOffset((w) => w + 1)}
            className="w-9 h-9 rounded-lg flex items-center justify-center text-on-surface-variant hover:bg-surface-container-high transition-colors"
            data-testid="next-week-btn"
          >
            <span className="material-symbols-outlined">chevron_right</span>
          </button>
          {weekOffset !== 0 && (
            <button
              onClick={() => setWeekOffset(0)}
              className="text-xs font-medium text-primary hover:text-primary-container transition-colors ml-1"
            >
              Cette semaine
            </button>
          )}
        </div>
      </div>

      {/* Weekly grid */}
      <div
        className="grid grid-cols-7 gap-3"
        data-testid="schedule-grid"
      >
        {schedule.map((day) => {
          const isToday =
            day.date === new Date().toISOString().slice(0, 10);

          return (
            <div
              key={day.date}
              className={[
                'bg-surface-container-lowest rounded-xl shadow-sm border p-4 min-h-[280px] flex flex-col',
                isToday
                  ? 'border-primary/30 ring-1 ring-primary/10'
                  : 'border-outline-variant/10',
                day.is_rest_day ? 'bg-surface-container-low/50' : '',
              ].join(' ')}
              data-testid={`schedule-day-${day.day_name}`}
            >
              {/* Day header */}
              <div className="flex items-center justify-between mb-3">
                <div>
                  <p
                    className={[
                      'text-xs font-bold uppercase tracking-widest',
                      isToday ? 'text-primary' : 'text-on-surface-variant',
                    ].join(' ')}
                  >
                    {day.day_name}
                  </p>
                  <p className="text-[10px] text-on-surface-variant mt-0.5">
                    {new Date(day.date).toLocaleDateString('fr-FR', {
                      day: 'numeric',
                      month: 'short',
                    })}
                  </p>
                </div>
                {isToday && (
                  <span className="inline-flex w-2 h-2 rounded-full bg-primary" />
                )}
              </div>

              {/* Content */}
              {day.is_rest_day ? (
                <div className="flex-1 flex flex-col items-center justify-center gap-2">
                  <span className="material-symbols-outlined text-2xl text-on-surface-variant/40">
                    hotel
                  </span>
                  <p className="text-xs font-medium text-on-surface-variant">
                    Jour de repos
                  </p>
                </div>
              ) : (
                <div className="flex-1 flex flex-col gap-2">
                  {day.trips.map((trip, idx) => (
                    <div
                      key={idx}
                      className="bg-surface-container-low rounded-lg p-2.5 group"
                    >
                      <div className="flex items-start justify-between">
                        <div className="min-w-0 flex-1">
                          <p className="text-xs font-semibold text-on-surface truncate">
                            {trip.ligne_name}
                          </p>
                          <p className="text-[10px] text-on-surface-variant mt-0.5">
                            {trip.departure} - {trip.arrival}
                          </p>
                          <p className="text-[10px] text-on-surface-variant">
                            {trip.vehicle_plate}
                          </p>
                        </div>
                        <div className="flex flex-col items-end gap-1 shrink-0 ml-1">
                          {trip.is_lto_optimized && (
                            <span
                              className="inline-flex items-center rounded px-1.5 py-0.5 text-[9px] font-bold bg-green-50 text-green-700"
                              title="Depart optimise LTO"
                            >
                              LTO
                            </span>
                          )}
                          <button
                            onClick={() =>
                              handleSwapRequest(day.day_name, trip.ligne_name)
                            }
                            className="opacity-0 group-hover:opacity-100 transition-opacity w-5 h-5 rounded flex items-center justify-center text-on-surface-variant hover:bg-surface-container-high"
                            title="Demander un echange"
                          >
                            <span className="material-symbols-outlined text-xs">
                              swap_horiz
                            </span>
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Rest hours */}
              {!day.is_rest_day && (
                <div className="mt-2 pt-2 border-t border-outline-variant/10">
                  <p className="text-[10px] text-on-surface-variant">
                    <span className="material-symbols-outlined text-[10px] align-middle mr-0.5">
                      bedtime
                    </span>
                    Repos: {day.rest_hours}h
                  </p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-6 text-xs text-on-surface-variant">
        <div className="flex items-center gap-1.5">
          <span className="inline-flex items-center rounded px-1.5 py-0.5 text-[9px] font-bold bg-green-50 text-green-700">
            LTO
          </span>
          <span>Depart optimise (Leave Time Optimization)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="material-symbols-outlined text-sm text-on-surface-variant">
            swap_horiz
          </span>
          <span>Echange disponible (survoler un trajet)</span>
        </div>
      </div>

      {/* Swap request modal */}
      {showSwapModal && swapTarget && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="bg-surface-container-lowest rounded-xl shadow-2xl border border-outline-variant/10 p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-on-surface">
                Demander un echange
              </h3>
              <button
                onClick={() => setShowSwapModal(false)}
                className="w-8 h-8 rounded-lg flex items-center justify-center text-on-surface-variant hover:bg-surface-container-high transition-colors"
              >
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            {swapSubmitted ? (
              <div className="flex flex-col items-center gap-3 py-8">
                <span className="material-symbols-outlined text-green-600 text-4xl">
                  check_circle
                </span>
                <p className="text-sm font-medium text-on-surface">
                  Demande d&apos;echange envoyee
                </p>
              </div>
            ) : (
              <>
                <div className="bg-surface-container-low rounded-lg p-3 mb-4">
                  <p className="text-xs text-on-surface-variant">
                    Trajet: <span className="font-semibold text-on-surface">{swapTarget.trip}</span>
                  </p>
                  <p className="text-xs text-on-surface-variant">
                    Jour: <span className="font-semibold text-on-surface">{swapTarget.day}</span>
                  </p>
                </div>

                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-widest text-outline mb-1.5">
                    Motif de la demande
                  </label>
                  <textarea
                    value={swapReason}
                    onChange={(e) => setSwapReason(e.target.value)}
                    rows={3}
                    placeholder="Expliquez la raison de votre demande d'echange..."
                    className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2.5 text-sm text-on-surface placeholder:text-on-surface-variant/60 focus:ring-2 focus:ring-primary/20 outline-none resize-none"
                  />
                </div>

                <div className="flex items-center gap-3 mt-6">
                  <button
                    onClick={() => setShowSwapModal(false)}
                    className="flex-1 bg-surface-container-lowest text-primary border border-outline-variant/15 rounded-lg shadow-sm px-4 py-2.5 text-sm font-semibold transition-colors hover:bg-surface-container-low"
                  >
                    Annuler
                  </button>
                  <button
                    onClick={handleSwapSubmit}
                    disabled={!swapReason.trim()}
                    className="flex-1 bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-lg shadow-lg shadow-primary/20 px-4 py-2.5 text-sm font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-transform hover:scale-[1.02] active:scale-[0.98]"
                  >
                    Envoyer la demande
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
