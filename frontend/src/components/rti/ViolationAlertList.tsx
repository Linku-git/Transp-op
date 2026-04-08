import { useState } from 'react';

interface Violation {
  id: string;
  stop_name: string;
  vehicle_label: string;
  scheduled_time: string;
  wait_seconds: number;
  severity: 'low' | 'medium' | 'high';
}

export function ViolationAlertList({ violations }: { violations: Violation[] }) {
  const [sortField, setSortField] = useState<keyof Violation>('wait_seconds');
  const [sortAsc, setSortAsc] = useState(false);

  const sorted = [...violations].sort((a, b) => {
    const aVal = a[sortField];
    const bVal = b[sortField];
    if (typeof aVal === 'number' && typeof bVal === 'number') {
      return sortAsc ? aVal - bVal : bVal - aVal;
    }
    return sortAsc
      ? String(aVal).localeCompare(String(bVal))
      : String(bVal).localeCompare(String(aVal));
  });

  const handleSort = (field: keyof Violation) => {
    if (sortField === field) setSortAsc(!sortAsc);
    else { setSortField(field); setSortAsc(false); }
  };

  const severityBadge = (s: string) => {
    const cls = s === 'high' ? 'bg-red-50 text-red-700' : s === 'medium' ? 'bg-amber-50 text-amber-700' : 'bg-green-50 text-green-700';
    const label = s === 'high' ? 'Élevé' : s === 'medium' ? 'Moyen' : 'Faible';
    return <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${cls}`}>{label}</span>;
  };

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
      <div className="px-6 py-4">
        <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Violations récentes
        </p>
      </div>
      {violations.length === 0 ? (
        <p className="text-sm text-on-surface-variant text-center py-8 px-6">Aucune violation</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-surface-container-low/50">
                {[
                  { key: 'stop_name' as const, label: 'Arrêt' },
                  { key: 'vehicle_label' as const, label: 'Véhicule' },
                  { key: 'scheduled_time' as const, label: 'Horaire prévu' },
                  { key: 'wait_seconds' as const, label: 'Attente' },
                  { key: 'severity' as const, label: 'Sévérité' },
                ].map(({ key, label }) => (
                  <th
                    key={key}
                    className="text-left px-4 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant cursor-pointer hover:text-on-surface"
                    onClick={() => handleSort(key)}
                  >
                    {label} {sortField === key && (sortAsc ? '↑' : '↓')}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {sorted.map((v) => (
                <tr key={v.id} className="hover:bg-surface-bright">
                  <td className="px-4 py-3">{v.stop_name}</td>
                  <td className="px-4 py-3">{v.vehicle_label}</td>
                  <td className="px-4 py-3 text-on-surface-variant">{v.scheduled_time}</td>
                  <td className="px-4 py-3 font-semibold">{v.wait_seconds}s</td>
                  <td className="px-4 py-3">{severityBadge(v.severity)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
