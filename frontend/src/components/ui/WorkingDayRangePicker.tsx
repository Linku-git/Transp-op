import { useCallback } from 'react';

const DAYS_SHORT = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];
const DAYS_FULL = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'];

const DAY_ALIASES: string[][] = [
  ['lundi', 'lun'],
  ['mardi', 'mar'],
  ['mercredi', 'mer'],
  ['jeudi', 'jeu'],
  ['vendredi', 'ven'],
  ['samedi', 'sam'],
  ['dimanche', 'dim'],
];

function findDayIdx(name: string): number {
  const lower = name.toLowerCase().trim();
  return DAY_ALIASES.findIndex((aliases) => aliases.includes(lower));
}

export function workingDaysToRange(working_days: string): { startIdx: number; endIdx: number } {
  const parts = working_days.split('-');
  if (parts.length >= 2) {
    const s = findDayIdx(parts[0]);
    const e = findDayIdx(parts[parts.length - 1]);
    if (s >= 0 && e >= 0 && s <= e) return { startIdx: s, endIdx: e };
  }
  return { startIdx: 0, endIdx: 4 };
}

export function rangeToWorkingDays(startIdx: number, endIdx: number): string {
  return `${DAYS_FULL[startIdx]}-${DAYS_FULL[endIdx]}`;
}

export function rangeToDaysPerWeek(startIdx: number, endIdx: number): number {
  return endIdx - startIdx + 1;
}

interface Props {
  startIdx: number;
  endIdx: number;
  onChange: (startIdx: number, endIdx: number) => void;
}

export function WorkingDayRangePicker({ startIdx, endIdx, onChange }: Props) {
  const moveStart = useCallback(
    (dir: -1 | 1) => {
      const next = startIdx + dir;
      if (next < 0 || next > endIdx) return;
      onChange(next, endIdx);
    },
    [startIdx, endIdx, onChange],
  );

  const moveEnd = useCallback(
    (dir: -1 | 1) => {
      const next = endIdx + dir;
      if (next > 6 || next < startIdx) return;
      onChange(startIdx, next);
    },
    [startIdx, endIdx, onChange],
  );

  const handleBubbleClick = useCallback(
    (i: number) => {
      if (i < startIdx) onChange(i, endIdx);
      else if (i > endIdx) onChange(startIdx, i);
      else if (i === startIdx && i < endIdx) onChange(i + 1, endIdx);
      else if (i === endIdx && i > startIdx) onChange(startIdx, i - 1);
    },
    [startIdx, endIdx, onChange],
  );

  const sameCol = startIdx === endIdx;

  return (
    <div className="flex flex-col gap-0 select-none">
      {/* Arrow indicators row — one cell per day */}
      <div className="grid gap-1" style={{ gridTemplateColumns: 'repeat(7, 1fr)' }}>
        {DAYS_FULL.map((_, i) => {
          const isStart = i === startIdx;
          const isEnd = i === endIdx && !sameCol;
          const isBoth = sameCol && i === startIdx;

          if (!isStart && !isEnd && !isBoth) {
            return <div key={i} className="h-12" />;
          }

          const color = isStart || isBoth ? 'blue' : 'violet';
          const label = isBoth ? 'Deb/Fin' : isStart ? 'Début' : 'Fin';
          const onLeft = isStart || isBoth ? () => moveStart(-1) : () => moveEnd(-1);
          const onRight = isStart || isBoth ? () => moveStart(1) : () => moveEnd(1);

          return (
            <div key={i} className="flex flex-col items-center h-12 justify-end pb-0.5">
              <span
                className={`text-[8px] font-black uppercase tracking-widest leading-none mb-0.5 ${
                  color === 'blue' ? 'text-blue-500' : 'text-violet-500'
                }`}
              >
                {label}
              </span>
              <div className="flex items-center gap-0">
                <button
                  type="button"
                  onClick={onLeft}
                  className={`w-5 h-5 flex items-center justify-center rounded transition-colors ${
                    color === 'blue'
                      ? 'text-blue-500 hover:bg-blue-100'
                      : 'text-violet-500 hover:bg-violet-100'
                  }`}
                >
                  <span className="material-symbols-outlined text-[14px] leading-none">chevron_left</span>
                </button>
                <span
                  className={`material-symbols-outlined text-[16px] leading-none ${
                    color === 'blue' ? 'text-blue-600' : 'text-violet-600'
                  }`}
                  style={{ fontVariationSettings: "'FILL' 1" }}
                >
                  arrow_drop_down
                </span>
                <button
                  type="button"
                  onClick={onRight}
                  className={`w-5 h-5 flex items-center justify-center rounded transition-colors ${
                    color === 'blue'
                      ? 'text-blue-500 hover:bg-blue-100'
                      : 'text-violet-500 hover:bg-violet-100'
                  }`}
                >
                  <span className="material-symbols-outlined text-[14px] leading-none">chevron_right</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Day bubbles */}
      <div className="grid gap-1" style={{ gridTemplateColumns: 'repeat(7, 1fr)' }}>
        {DAYS_FULL.map((_, i) => {
          const inRange = i >= startIdx && i <= endIdx;
          const isStart = i === startIdx;
          const isEnd = i === endIdx;
          const isMiddle = inRange && !isStart && !isEnd;

          return (
            <button
              key={i}
              type="button"
              onClick={() => handleBubbleClick(i)}
              className={[
                'py-2.5 flex flex-col items-center justify-center rounded-xl border transition-all duration-150 cursor-pointer',
                isStart
                  ? 'bg-blue-600 text-white border-blue-700 shadow-md shadow-blue-200'
                  : isEnd
                    ? 'bg-violet-600 text-white border-violet-700 shadow-md shadow-violet-200'
                    : isMiddle
                      ? 'bg-blue-100 text-blue-800 border-blue-200'
                      : 'bg-white text-slate-400 border-slate-200 hover:border-slate-300 hover:text-slate-600',
              ].join(' ')}
            >
              <span className="text-[11px] font-black tracking-tight leading-tight">
                {DAYS_SHORT[i]}
              </span>
              <span className="text-[8px] font-medium opacity-70 leading-tight mt-0.5 px-0.5 truncate w-full text-center">
                {DAYS_FULL[i].slice(3)}
              </span>
            </button>
          );
        })}
      </div>

      {/* Gradient track */}
      <div className="mt-2 relative h-1 rounded-full bg-slate-100 mx-0.5">
        <div
          className="absolute h-full rounded-full bg-gradient-to-r from-blue-500 to-violet-500 transition-all duration-200"
          style={{
            left: `${(startIdx / 6) * 100}%`,
            right: `${((6 - endIdx) / 6) * 100}%`,
          }}
        />
      </div>

      {/* Summary badges */}
      <div className="mt-2 flex items-center justify-center gap-2 flex-wrap">
        <span className="text-[10px] font-bold text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-200">
          {DAYS_FULL[startIdx]}
        </span>
        <span className="material-symbols-outlined text-[12px] text-slate-400">arrow_forward</span>
        <span className="text-[10px] font-bold text-violet-700 bg-violet-50 px-2.5 py-0.5 rounded-full border border-violet-200">
          {DAYS_FULL[endIdx]}
        </span>
      </div>
    </div>
  );
}
