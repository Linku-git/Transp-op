import type { MilestoneResult } from '@/types/sotreg';

/* ── Helpers ──────────────────────────────────────────────────────────────── */

const madFmt = new Intl.NumberFormat('fr-MA', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
});

/* ── Main component ───────────────────────────────────────────────────────── */

export function MilestoneTracker({
  milestones,
}: {
  milestones: MilestoneResult[];
}) {
  if (milestones.length === 0) {
    return (
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
        <div className="flex flex-col items-center justify-center py-12 text-on-surface-variant">
          <span className="material-symbols-outlined text-4xl mb-2 opacity-40">
            flag
          </span>
          <p className="text-sm">Aucun jalon disponible.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 font-sans">
      {/* Header */}
      <div className="flex items-center gap-2 mb-6">
        <span className="material-symbols-outlined text-primary text-xl">
          flag
        </span>
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Jalons de Transition
        </h3>
      </div>

      {/* Vertical timeline */}
      <div className="relative pl-8">
        {/* Connecting vertical line */}
        <div
          className="absolute left-[15px] top-2 bottom-2 w-0.5 bg-outline-variant/20 rounded-full"
          aria-hidden="true"
        />

        <div className="space-y-6">
          {milestones.map((milestone, index) => {
            const isActive = milestone.target_pct > 0;
            const isLast = index === milestones.length - 1;

            return (
              <div key={`${milestone.year}-${index}`} className="relative">
                {/* Timeline node */}
                <div
                  className={[
                    'absolute -left-8 top-1 flex items-center justify-center w-[30px] h-[30px] rounded-full border-2 transition-colors',
                    isActive
                      ? 'bg-green-50 border-green-500'
                      : 'bg-surface-container-high/50 border-outline-variant/30',
                  ].join(' ')}
                >
                  <span
                    className={[
                      'material-symbols-outlined text-sm',
                      isActive ? 'text-green-600' : 'text-on-surface-variant',
                    ].join(' ')}
                  >
                    {isLast ? 'flag' : isActive ? 'check_circle' : 'circle'}
                  </span>
                </div>

                {/* Content card */}
                <div
                  className={[
                    'rounded-lg p-4 border transition-colors',
                    isActive
                      ? 'bg-green-50/50 border-green-200/50'
                      : 'bg-surface-container-low border-outline-variant/10',
                  ].join(' ')}
                >
                  {/* Year badge + description */}
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1.5">
                        <span
                          className={[
                            'inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-bold',
                            isActive
                              ? 'bg-green-100 text-green-800'
                              : 'bg-surface-container-high/50 text-on-surface-variant',
                          ].join(' ')}
                        >
                          {milestone.year}
                        </span>
                        {milestone.target_pct > 0 && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-primary/10 text-primary">
                            {milestone.target_pct}% electrique
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-on-surface font-medium">
                        {milestone.description}
                      </p>
                    </div>

                    {/* Vehicles converted cumulative */}
                    <div className="text-right flex-shrink-0">
                      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-0.5">
                        Vehicules convertis
                      </p>
                      <p className="font-sans text-lg font-semibold text-on-surface">
                        {madFmt.format(milestone.vehicles_converted_cumulative)}
                      </p>
                    </div>
                  </div>

                  {/* Progress bar */}
                  {milestone.target_pct > 0 && (
                    <div className="mt-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                          Progression
                        </span>
                        <span className="text-xs font-medium text-on-surface">
                          {milestone.target_pct}%
                        </span>
                      </div>
                      <div className="w-full h-2 bg-outline-variant/10 rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all duration-500 bg-gradient-to-r from-green-500 to-green-400"
                          style={{
                            width: `${Math.min(milestone.target_pct, 100)}%`,
                          }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
