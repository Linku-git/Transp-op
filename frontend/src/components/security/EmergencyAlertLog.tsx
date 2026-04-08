import { useState } from 'react';

interface Alert {
  id: string;
  employee_name: string;
  time: string;
  location: string;
  alert_type: string;
  status: 'triggered' | 'resolved' | 'pending';
  response_time_minutes: number | null;
}

const STATUS_BADGE = {
  triggered: 'bg-red-50 text-red-700',
  resolved: 'bg-green-50 text-green-700',
  pending: 'bg-amber-50 text-amber-700',
};
const STATUS_LABEL = { triggered: 'Déclenché', resolved: 'Résolu', pending: 'En attente' };

export function EmergencyAlertLog({ alerts }: { alerts: Alert[] }) {
  const [filter, setFilter] = useState<string>('all');

  const filtered = filter === 'all' ? alerts : alerts.filter((a) => a.status === filter);

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
      <div className="px-6 py-4 flex items-center justify-between">
        <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Journal des alertes d'urgence
        </p>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="text-xs bg-surface-container-high/50 border-none rounded-lg px-2 py-1"
        >
          <option value="all">Tous</option>
          <option value="triggered">Déclenchés</option>
          <option value="pending">En attente</option>
          <option value="resolved">Résolus</option>
        </select>
      </div>
      {filtered.length === 0 ? (
        <p className="text-sm text-on-surface-variant text-center py-8 px-6">Aucune alerte</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-surface-container-low/50">
                <th className="text-left px-4 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">Employé</th>
                <th className="text-left px-4 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">Heure</th>
                <th className="text-left px-4 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">Lieu</th>
                <th className="text-left px-4 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">Type</th>
                <th className="text-left px-4 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">Statut</th>
                <th className="text-left px-4 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">Réponse</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {filtered.map((a) => (
                <tr key={a.id} className="hover:bg-surface-bright">
                  <td className="px-4 py-3">{a.employee_name}</td>
                  <td className="px-4 py-3 text-on-surface-variant">{a.time}</td>
                  <td className="px-4 py-3">{a.location}</td>
                  <td className="px-4 py-3">{a.alert_type}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${STATUS_BADGE[a.status]}`}>
                      {STATUS_LABEL[a.status]}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-on-surface-variant">
                    {a.response_time_minutes != null ? `${a.response_time_minutes} min` : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
