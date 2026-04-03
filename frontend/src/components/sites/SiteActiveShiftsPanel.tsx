import { useCallback, useEffect, useState } from 'react';
import { listHorairesTravail } from '@/api/vehicles';
import type { HoraireTravail } from '@/types/vehicle';

interface Props {
  activeIds: string[];
}

function TimeCell({ value }: { value: string | null | undefined }) {
  if (!value) return <span className="text-on-surface-variant/40 text-xs">—</span>;
  return <span className="font-mono text-[13px] font-semibold text-on-surface">{value}</span>;
}

export function SiteActiveShiftsPanel({ activeIds }: Props) {
  const [shifts, setShifts] = useState<HoraireTravail[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await listHorairesTravail({ page_size: 200 });
      const companyWide = (res.items ?? []).filter((i) => !i.site_id);
      setShifts(companyWide);
    } catch {
      /* non-critical */
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const activeShifts = shifts.filter((s) => activeIds.includes(s.id));

  return (
    <div>
      <div className="flex items-center gap-2 mb-5">
        <span className="material-symbols-outlined text-lg text-primary">schedule</span>
        <h3 className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant font-sans">
          Shifts Actifs
        </h3>
        {!loading && (
          <span className="ml-auto text-xs text-on-surface-variant bg-surface-container px-2 py-0.5 rounded-full font-sans">
            {activeShifts.length} shift{activeShifts.length !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {loading ? (
        <div className="flex items-center gap-2 text-sm text-on-surface-variant py-4">
          <span className="material-symbols-outlined text-base animate-spin">refresh</span>
          Chargement…
        </div>
      ) : activeShifts.length === 0 ? (
        <div className="flex flex-col items-center gap-1.5 py-6 text-center">
          <span className="material-symbols-outlined text-2xl text-on-surface-variant/40">schedule_off</span>
          <p className="text-sm text-on-surface-variant font-sans">
            Aucun shift activé pour ce site
          </p>
          <p className="text-xs text-on-surface-variant/60 font-sans">
            Modifiez le site pour configurer les shifts applicables.
          </p>
        </div>
      ) : (
        <div className="rounded-xl overflow-hidden border border-outline-variant/30 bg-surface">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-surface-container-low border-b border-outline-variant/20">
                <th className="px-3 py-2.5 text-left text-[10px] font-bold uppercase tracking-widest text-on-surface-variant w-[28%]">
                  Shift
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
                <th className="px-3 pb-1.5 text-center font-medium">Départ</th>
                <th className="px-3 pb-1.5 text-center font-medium">Retour</th>
                <th className="px-3 pb-1.5 text-center font-medium">Départ</th>
                <th className="px-3 pb-1.5 text-center font-medium">Retour</th>
              </tr>
            </thead>
            <tbody>
              {activeShifts.map((shift, idx) => (
                <tr
                  key={shift.id}
                  className={`border-b border-outline-variant/10 ${idx % 2 === 1 ? 'bg-surface-container-lowest/30' : ''}`}
                >
                  <td className="px-3 py-3 font-semibold text-on-surface">{shift.type_horaire}</td>
                  <td className="px-3 py-3 text-center"><TimeCell value={shift.depart_h1} /></td>
                  <td className="px-3 py-3 text-center"><TimeCell value={shift.retour_h1} /></td>
                  <td className="px-3 py-3 text-center"><TimeCell value={shift.depart_h2} /></td>
                  <td className="px-3 py-3 text-center"><TimeCell value={shift.retour_h2} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
