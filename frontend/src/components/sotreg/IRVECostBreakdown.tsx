import { useState } from 'react';

export function IRVECostBreakdown() {
  const [isLoading] = useState(false);

  if (isLoading) {
    return (
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 animate-pulse">
        <div className="h-4 w-48 rounded bg-surface-container-high mb-4" />
        <div className="space-y-3">
          <div className="h-3 w-full rounded bg-surface-container-high" />
          <div className="h-3 w-3/4 rounded bg-surface-container-high" />
          <div className="h-40 w-full rounded bg-surface-container-high" />
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
      <div className="flex items-center gap-2 mb-4">
        <span className="material-symbols-outlined text-lg text-primary">
          payments
        </span>
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Couts IRVE
        </h3>
      </div>
      <p className="text-sm text-on-surface-variant">
        Calculateur de couts d'infrastructure de recharge — A implementer.
      </p>
    </div>
  );
}
