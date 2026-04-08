interface Incident {
  id: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  date: string;
  type: string;
}

const SEVERITY_COLORS = {
  low: 'bg-green-500',
  medium: 'bg-amber-400',
  high: 'bg-red-500',
  critical: 'bg-red-800',
};

export function IncidentTimeline({ incidents }: { incidents: Incident[] }) {
  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
        Historique des incidents
      </p>
      {incidents.length === 0 ? (
        <p className="text-sm text-on-surface-variant text-center py-8">Aucun incident</p>
      ) : (
        <div className="space-y-4">
          {incidents.map((inc, i) => (
            <div key={inc.id} className="flex gap-3">
              <div className="flex flex-col items-center">
                <div className={`w-3 h-3 rounded-full ${SEVERITY_COLORS[inc.severity]}`} />
                {i < incidents.length - 1 && <div className="w-px flex-1 bg-outline-variant/20 mt-1" />}
              </div>
              <div className="pb-4">
                <p className="text-sm font-medium">{inc.title}</p>
                <p className="text-xs text-on-surface-variant mt-0.5">{inc.description}</p>
                <p className="text-[10px] text-outline mt-1">{inc.date} · {inc.type}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
