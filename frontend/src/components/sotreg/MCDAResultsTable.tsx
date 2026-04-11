import { useCallback, useState } from 'react';
import type { MCDAResponse, NormalizedAlternative } from '../../types/sotreg';
import { MCDA_ALT_COLORS, MCDA_CRITERIA, MCDA_CRITERIA_LABELS } from '../../types/sotreg';

interface MCDAResultsTableProps {
  results: MCDAResponse;
}

type SortKey = 'score' | 'rank' | typeof MCDA_CRITERIA[number];

export function MCDAResultsTable({ results }: MCDAResultsTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>('rank');
  const [sortAsc, setSortAsc] = useState(true);

  const handleSort = useCallback(
    (key: SortKey) => {
      if (sortKey === key) {
        setSortAsc((prev) => !prev);
      } else {
        setSortKey(key);
        setSortAsc(key === 'rank');
      }
    },
    [sortKey],
  );

  const sorted = [...results.ranked_alternatives].sort((a, b) => {
    let va: number, vb: number;
    if (sortKey === 'score') {
      va = a.score;
      vb = b.score;
    } else if (sortKey === 'rank') {
      va = a.rank;
      vb = b.rank;
    } else {
      va = a.normalized_values[sortKey] ?? 0;
      vb = b.normalized_values[sortKey] ?? 0;
    }
    return sortAsc ? va - vb : vb - va;
  });

  const maxScore = Math.max(...results.ranked_alternatives.map((a) => a.score), 1);

  const arrow = (key: SortKey) => {
    if (sortKey !== key) return '';
    return sortAsc ? ' \u25B2' : ' \u25BC';
  };

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
      <div className="px-5 py-3 bg-surface-container-low/50">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Classement des alternatives
        </h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-surface-container-low/30">
              <SortHeader label="Rang" sortKey="rank" current={sortKey} arrow={arrow} onClick={handleSort} />
              <th className="text-left px-3 py-2 text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                Alternative
              </th>
              <SortHeader label="Score" sortKey="score" current={sortKey} arrow={arrow} onClick={handleSort} />
              <th className="text-left px-3 py-2 text-[10px] font-bold uppercase tracking-widest text-on-surface-variant min-w-[160px]">
                Barre
              </th>
              {MCDA_CRITERIA.map((c) => (
                <SortHeader
                  key={c}
                  label={MCDA_CRITERIA_LABELS[c]}
                  sortKey={c}
                  current={sortKey}
                  arrow={arrow}
                  onClick={handleSort}
                />
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/10">
            {sorted.map((alt, idx) => (
              <AltRow key={alt.name} alt={alt} idx={idx} maxScore={maxScore} isBest={alt.rank === 1} />
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary */}
      <div className="px-5 py-3 bg-surface-container-low/30 flex gap-6 text-xs text-on-surface-variant">
        <span>
          Meilleure :{' '}
          <span className="font-bold text-green-700">{results.best_alternative}</span>
        </span>
        <span>
          Plus faible :{' '}
          <span className="font-bold text-red-700">{results.worst_alternative}</span>
        </span>
      </div>
    </div>
  );
}

function SortHeader({
  label,
  sortKey,
  current,
  arrow,
  onClick,
}: {
  label: string;
  sortKey: SortKey;
  current: SortKey;
  arrow: (k: SortKey) => string;
  onClick: (k: SortKey) => void;
}) {
  return (
    <th
      className={`text-center px-2 py-2 text-[10px] font-bold uppercase tracking-widest cursor-pointer select-none ${
        current === sortKey ? 'text-primary' : 'text-on-surface-variant'
      }`}
      onClick={() => onClick(sortKey)}
    >
      {label}
      {arrow(sortKey)}
    </th>
  );
}

function AltRow({
  alt,
  idx,
  maxScore,
  isBest,
}: {
  alt: NormalizedAlternative;
  idx: number;
  maxScore: number;
  isBest: boolean;
}) {
  const pct = maxScore > 0 ? (alt.score / maxScore) * 100 : 0;
  const color = MCDA_ALT_COLORS[idx % MCDA_ALT_COLORS.length];

  return (
    <tr className={isBest ? 'bg-green-50/60' : 'hover:bg-surface-bright'}>
      <td className="text-center px-3 py-2.5 font-bold text-on-surface">{alt.rank}</td>
      <td className="px-3 py-2.5">
        <div className="flex items-center gap-2">
          <span
            className="inline-block w-3 h-3 rounded-full flex-shrink-0"
            style={{ backgroundColor: color }}
          />
          <span className="font-medium text-on-surface">{alt.name}</span>
          {isBest && (
            <span className="bg-green-100 text-green-700 text-[10px] font-bold px-1.5 py-0.5 rounded">
              #1
            </span>
          )}
        </div>
      </td>
      <td className="text-center px-3 py-2.5 font-bold text-on-surface">{alt.score.toFixed(2)}</td>
      <td className="px-3 py-2.5">
        <div className="h-4 bg-surface-container-high rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{ width: `${pct}%`, backgroundColor: color }}
          />
        </div>
      </td>
      {MCDA_CRITERIA.map((c) => {
        const val = alt.normalized_values[c] ?? 0;
        return (
          <td key={c} className="text-center px-2 py-2.5">
            <span className={`text-xs font-medium ${scoreColor(val)}`}>{val.toFixed(2)}</span>
          </td>
        );
      })}
    </tr>
  );
}

function scoreColor(val: number): string {
  if (val >= 4) return 'text-green-700';
  if (val >= 3) return 'text-amber-700';
  return 'text-red-700';
}
