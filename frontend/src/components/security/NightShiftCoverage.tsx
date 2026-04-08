export function NightShiftCoverage({ coveragePct }: { coveragePct: number }) {
  const color = coveragePct >= 90 ? 'text-green-600' : coveragePct >= 70 ? 'text-amber-500' : 'text-red-600';
  const bgColor = coveragePct >= 90 ? 'bg-green-50' : coveragePct >= 70 ? 'bg-amber-50' : 'bg-red-50';

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">
        Couverture équipes de nuit
      </p>
      <div className="flex items-center gap-4">
        <div className={`w-16 h-16 rounded-xl ${bgColor} flex items-center justify-center`}>
          <span className={`text-xl font-bold ${color}`}>{coveragePct}%</span>
        </div>
        <div>
          <p className="text-sm font-medium">
            {coveragePct >= 90 ? 'Couverture optimale' : coveragePct >= 70 ? 'Couverture partielle' : 'Couverture insuffisante'}
          </p>
          <p className="text-xs text-on-surface-variant mt-1">
            Taux minimum recommandé : 90%
          </p>
        </div>
      </div>
      {/* Coverage bar */}
      <div className="mt-4 w-full bg-surface-container-high rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all ${coveragePct >= 90 ? 'bg-green-500' : coveragePct >= 70 ? 'bg-amber-400' : 'bg-red-500'}`}
          style={{ width: `${Math.min(coveragePct, 100)}%` }}
        />
      </div>
    </div>
  );
}
