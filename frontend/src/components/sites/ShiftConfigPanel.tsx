import { useTranslation } from 'react-i18next';
import type { Site } from '@/types/site';

interface ShiftConfigPanelProps {
  site: Site;
}

/**
 * Parse a time string (HH:MM or HH:MM:SS) into fractional hours (0-24).
 * Returns null if the input is null/undefined/empty.
 */
function timeToHours(time: string | null | undefined): number | null {
  if (!time) return null;
  const parts = time.split(':');
  if (parts.length < 2) return null;
  const hours = parseInt(parts[0], 10);
  const minutes = parseInt(parts[1], 10);
  if (Number.isNaN(hours) || Number.isNaN(minutes)) return null;
  return hours + minutes / 60;
}

const SHIFT_COLORS = [
  { bg: 'bg-blue-100', fill: 'bg-blue-500', badge: 'bg-blue-100 text-blue-700', letter: 'M' },
  { bg: 'bg-amber-100', fill: 'bg-amber-500', badge: 'bg-amber-100 text-amber-700', letter: 'A' },
  { bg: 'bg-indigo-100', fill: 'bg-indigo-500', badge: 'bg-indigo-100 text-indigo-700', letter: 'N' },
];

function ShiftBar({
  shiftNumber,
  entryTime,
  exitTime,
}: {
  shiftNumber: number;
  entryTime: string | null;
  exitTime: string | null;
}) {
  const { t } = useTranslation();

  const entryHours = timeToHours(entryTime);
  const exitHours = timeToHours(exitTime);

  const hasValidTimes = entryHours !== null && exitHours !== null;

  /* Calculate positions as percentage of 24h timeline */
  const leftPercent = hasValidTimes ? (entryHours / 24) * 100 : 0;
  const widthPercent = hasValidTimes
    ? ((exitHours > entryHours ? exitHours - entryHours : 24 - entryHours + exitHours) / 24) * 100
    : 0;

  const colors = SHIFT_COLORS[(shiftNumber - 1) % SHIFT_COLORS.length];

  return (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-3 w-32 shrink-0">
        <span className={`w-6 h-6 rounded-full ${colors.badge} flex items-center justify-center text-[10px] font-black`}>
          {colors.letter}
        </span>
        <span className="text-sm font-medium text-on-surface font-sans">
          {t('sites.form.shift_n', 'Equipe {{n}}', { n: shiftNumber })}
        </span>
      </div>
      <div className="flex-1">
        {hasValidTimes ? (
          <div className={`relative ${colors.bg} rounded-lg h-9`}>
            <div
              className={`absolute top-0 bottom-0 ${colors.fill}/60 rounded-lg`}
              style={{
                left: `${leftPercent}%`,
                width: `${widthPercent}%`,
              }}
            />
            <span className="absolute left-2 top-1/2 -translate-y-1/2 text-xs font-bold text-on-surface font-sans tabular-nums">
              {entryTime}
            </span>
            <span className="absolute right-2 top-1/2 -translate-y-1/2 text-xs font-bold text-on-surface font-sans tabular-nums">
              {exitTime}
            </span>
          </div>
        ) : (
          <div className="bg-surface-container-high rounded-lg h-9 flex items-center px-3">
            <span className="text-xs text-on-surface-variant font-sans italic">
              {t('sites.detail.shift_not_configured', 'Non configure')}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

export function ShiftConfigPanel({ site }: ShiftConfigPanelProps) {
  const { t } = useTranslation();

  const shifts: Array<{
    number: number;
    entry: string | null;
    exit: string | null;
  }> = [];

  for (let i = 1; i <= site.num_shifts; i++) {
    const entry =
      i === 1
        ? site.shift_1_entry
        : i === 2
          ? site.shift_2_entry
          : site.shift_3_entry;
    const exit =
      i === 1
        ? site.shift_1_exit
        : i === 2
          ? site.shift_2_exit
          : site.shift_3_exit;
    shifts.push({ number: i, entry, exit });
  }

  return (
    <div>
      <div className="flex items-center gap-2 mb-5">
        <span className="material-symbols-outlined text-lg text-primary">schedule</span>
        <h3 className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant font-sans">
          {t('sites.detail.shifts', 'Horaires')}
        </h3>
      </div>
      <div className="flex flex-col gap-3">
        {shifts.map((shift) => (
          <ShiftBar
            key={shift.number}
            shiftNumber={shift.number}
            entryTime={shift.entry}
            exitTime={shift.exit}
          />
        ))}
      </div>
    </div>
  );
}
