import { useCallback, useEffect, useState } from 'react';
import { listHorairesTravail } from '@/api/vehicles';
import type { HoraireTravail } from '@/types/vehicle';

interface Props {
  activeIds: string[];
  onChange: (ids: string[]) => void;
}

function TimeCell({ value }: { value: string | null | undefined }) {
  if (!value) return <span className="text-on-surface-variant/40 text-xs">—</span>;
  return <span className="font-mono text-[13px] font-semibold text-on-surface">{value}</span>;
}

export function SiteShiftSelector({ activeIds, onChange }: Props) {
  const [shifts, setShifts] = useState<HoraireTravail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listHorairesTravail({ page_size: 200 });
      const companyWide = (res.items ?? []).filter((i) => !i.site_id);
      setShifts(companyWide);
    } catch {
      setError('Impossible de charger les shifts');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const toggle = (id: string) => {
    if (activeIds.includes(id)) {
      onChange(activeIds.filter((x) => x !== id));
    } else {
      onChange([...activeIds, id]);
    }
  };

  const allSelected = shifts.length > 0 && shifts.every((s) => activeIds.includes(s.id));

  const toggleAll = () => {
    if (allSelected) {
      onChange([]);
    } else {
      onChange(shifts.map((s) => s.id));
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8 text-on-surface-variant text-sm gap-2">
        <span className="material-symbols-outlined text-xl animate-spin">refresh</span>
        Chargement des shifts…
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center gap-2 rounded-lg bg-error-container/20 px-3 py-2 text-sm text-error">
        <span className="material-symbols-outlined text-sm">error</span>
        {error}
      </div>
    );
  }

  if (shifts.length === 0) {
    return (
      <div className="flex flex-col items-center gap-2 py-8 text-center">
        <span className="material-symbols-outlined text-3xl text-on-surface-variant/40">schedule</span>
        <p className="text-sm text-on-surface-variant">Aucun shift défini.</p>
        <p className="text-xs text-on-surface-variant/60">
          Ajoutez des shifts dans <strong>Paramètres → Shifts</strong> avant d'en activer sur ce site.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="rounded-xl overflow-hidden border border-outline-variant/30 bg-surface">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-surface-container-low border-b border-outline-variant/20">
              <th className="w-10 px-3 py-2.5 text-center">
                <input
                  type="checkbox"
                  checked={allSelected}
                  onChange={toggleAll}
                  className="w-4 h-4 rounded accent-primary cursor-pointer"
                  title="Tout sélectionner"
                />
              </th>
              <th className="px-3 py-2.5 text-left text-[10px] font-bold uppercase tracking-widest text-on-surface-variant w-[22%]">
                Type de Shift
              </th>
              <th className="px-3 py-2.5 text-center text-[10px] font-bold uppercase tracking-widest text-on-surface-variant" colSpan={2}>
                Premier Horaire
              </th>
              <th className="px-3 py-2.5 text-center text-[10px] font-bold uppercase tracking-widest text-on-surface-variant" colSpan={2}>
                Deuxième Horaire
              </th>
            </tr>
            <tr className="bg-surface-container-lowest border-b border-outline-variant/10 text-[10px] text-on-surface-variant/70">
              <th />
              <th />
              <th className="px-3 pb-1.5 text-center font-medium">Départ</th>
              <th className="px-3 pb-1.5 text-center font-medium">Retour</th>
              <th className="px-3 pb-1.5 text-center font-medium">Départ</th>
              <th className="px-3 pb-1.5 text-center font-medium">Retour</th>
            </tr>
          </thead>
          <tbody>
            {shifts.map((shift, idx) => {
              const active = activeIds.includes(shift.id);
              return (
                <tr
                  key={shift.id}
                  onClick={() => toggle(shift.id)}
                  className={[
                    'border-b border-outline-variant/10 cursor-pointer transition-colors',
                    active
                      ? 'bg-primary/5 hover:bg-primary/10'
                      : idx % 2 === 1
                        ? 'bg-surface-container-lowest/30 hover:bg-surface-container-low/60'
                        : 'hover:bg-surface-container-low/60',
                  ].join(' ')}
                >
                  <td className="px-3 py-3 text-center" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="checkbox"
                      checked={active}
                      onChange={() => toggle(shift.id)}
                      className="w-4 h-4 rounded accent-primary cursor-pointer"
                    />
                  </td>
                  <td className="px-3 py-3">
                    <span className={`font-semibold ${active ? 'text-primary' : 'text-on-surface'}`}>
                      {shift.type_horaire}
                    </span>
                    {active && (
                      <span className="ml-2 inline-flex items-center gap-0.5 text-[10px] font-bold bg-primary/10 text-primary px-1.5 py-0.5 rounded-full">
                        <span className="material-symbols-outlined text-[10px]">check</span>
                        Actif
                      </span>
                    )}
                  </td>
                  <td className="px-3 py-3 text-center"><TimeCell value={shift.depart_h1} /></td>
                  <td className="px-3 py-3 text-center"><TimeCell value={shift.retour_h1} /></td>
                  <td className="px-3 py-3 text-center"><TimeCell value={shift.depart_h2} /></td>
                  <td className="px-3 py-3 text-center"><TimeCell value={shift.retour_h2} /></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <p className="text-[10px] text-on-surface-variant/60 font-sans">
        {activeIds.length === 0
          ? 'Aucun shift activé pour ce site. Cochez les shifts applicables.'
          : `${activeIds.length} shift${activeIds.length > 1 ? 's' : ''} activé${activeIds.length > 1 ? 's' : ''} pour ce site.`}
      </p>
    </div>
  );
}
