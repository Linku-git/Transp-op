/**
 * DriverRiskHeatmap — Sortable driver list with risk color coding.
 *
 * Supports category filtering (low/medium/high/critical),
 * expandable detail rows showing infraction breakdown.
 *
 * Session 122 — M8 Real-Time Operations.
 */
import { useMemo, useState } from 'react';
import type { DriverRisk } from '../../stores/operationsStore';

interface DriverRiskHeatmapProps {
  drivers: DriverRisk[];
  filterCategory: string | null;
  onFilterChange: (cat: string | null) => void;
}

const RISK_COLORS: Record<string, { bg: string; text: string; label: string; dot: string }> = {
  low: { bg: 'bg-green-50', text: 'text-green-700', label: 'Faible', dot: '#22c55e' },
  medium: { bg: 'bg-amber-50', text: 'text-amber-700', label: 'Moyen', dot: '#f59e0b' },
  high: { bg: 'bg-orange-50', text: 'text-orange-700', label: 'Eleve', dot: '#f97316' },
  critical: { bg: 'bg-red-50', text: 'text-red-700', label: 'Critique', dot: '#ef4444' },
};

export function DriverRiskHeatmap({
  drivers,
  filterCategory,
  onFilterChange,
}: DriverRiskHeatmapProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const filtered = useMemo(() => {
    const list = [...drivers].sort((a, b) => a.riskScore - b.riskScore);
    if (filterCategory) return list.filter((d) => d.riskCategory === filterCategory);
    return list;
  }, [drivers, filterCategory]);

  return (
    <div
      className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-5"
      data-testid="driver-risk-heatmap"
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Risque Conducteurs ({filtered.length})
        </h3>
        <div className="flex gap-1">
          {(['low', 'medium', 'high', 'critical'] as const).map((cat) => {
            const c = RISK_COLORS[cat];
            return (
              <button
                key={cat}
                onClick={() => onFilterChange(filterCategory === cat ? null : cat)}
                className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                  filterCategory === cat
                    ? `${c.bg} ${c.text}`
                    : 'bg-surface-container-high/50 text-on-surface-variant'
                }`}
              >
                {c.label}
              </button>
            );
          })}
        </div>
      </div>

      {filtered.length === 0 ? (
        <p className="text-sm text-on-surface-variant text-center py-4">Aucun conducteur</p>
      ) : (
        <div className="space-y-1 max-h-[300px] overflow-y-auto">
          {filtered.map((d) => {
            const c = RISK_COLORS[d.riskCategory];
            const expanded = expandedId === d.driverId;
            return (
              <div key={d.driverId}>
                <button
                  onClick={() => setExpandedId(expanded ? null : d.driverId)}
                  className="w-full flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-surface-bright text-left"
                >
                  <span
                    className="w-2 h-2 rounded-full shrink-0"
                    style={{ backgroundColor: c.dot }}
                  />
                  <span className="text-xs font-medium text-on-surface flex-1">{d.name}</span>
                  <span
                    className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${c.bg} ${c.text}`}
                  >
                    {d.riskScore.toFixed(0)}
                  </span>
                </button>
                {expanded && (
                  <div className="ml-7 px-3 py-2 text-[10px] text-on-surface-variant grid grid-cols-3 gap-2">
                    <span>Vitesse: {d.infractions.speed}</span>
                    <span>Accel.: {d.infractions.acceleration}</span>
                    <span>Freinage: {d.infractions.braking}</span>
                    <span>Geofence: {d.infractions.geofence}</span>
                    <span>Temps: {d.infractions.drivingTime}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
