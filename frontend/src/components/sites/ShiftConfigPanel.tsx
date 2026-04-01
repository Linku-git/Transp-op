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

  return (
    <div className="flex items-center gap-4">
      <span className="text-sm font-medium text-on-surface font-sans w-24 shrink-0">
        {t('sites.form.shift_n', 'Equipe {{n}}', { n: shiftNumber })}
      </span>
      <div className="flex-1">
        {hasValidTimes ? (
          <div className="relative bg-secondary/20 rounded h-8">
            <div
              className="absolute top-0 bottom-0 bg-secondary/60 rounded"
              style={{
                left: `${leftPercent}%`,
                width: `${widthPercent}%`,
              }}
            />
            <span className="absolute left-1 top-1/2 -translate-y-1/2 text-xs text-on-surface-variant font-sans tabular-nums">
              {entryTime}
            </span>
            <span className="absolute right-1 top-1/2 -translate-y-1/2 text-xs text-on-surface-variant font-sans tabular-nums">
              {exitTime}
            </span>
          </div>
        ) : (
          <div className="bg-surface-container-high rounded h-8 flex items-center px-3">
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
      <h3 className="font-display text-lg font-semibold text-on-surface mb-4">
        {t('sites.detail.shifts', 'Horaires')}
      </h3>
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
