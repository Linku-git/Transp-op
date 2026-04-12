/**
 * RouteOptimizationPanel — Strategy selector with launch button.
 *
 * Allows switching between OR-Tools CVRP, Clarke & Wright, and
 * Genetic Algorithm solvers before launching optimization.
 *
 * Session 122 — M8 Real-Time Operations.
 */
import type { SolverStrategy } from '../../stores/operationsStore';

interface RouteOptimizationPanelProps {
  strategy: SolverStrategy;
  onStrategyChange: (s: SolverStrategy) => void;
  isOptimizing: boolean;
  onOptimize: () => void;
}

const STRATEGIES: { value: SolverStrategy; label: string; icon: string; desc: string }[] = [
  {
    value: 'ortools',
    label: 'OR-Tools CVRP',
    icon: 'precision_manufacturing',
    desc: 'Solveur exact, meilleure qualite',
  },
  {
    value: 'cw',
    label: 'Clarke & Wright',
    icon: 'savings',
    desc: 'Heuristique rapide, bonne qualite',
  },
  {
    value: 'ga',
    label: 'Algorithme Genetique',
    icon: 'genetics',
    desc: 'Metaheuristique, flexible',
  },
];

export function RouteOptimizationPanel({
  strategy,
  onStrategyChange,
  isOptimizing,
  onOptimize,
}: RouteOptimizationPanelProps) {
  return (
    <div
      className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-5"
      data-testid="route-optimization-panel"
    >
      <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">
        Optimisation Routes
      </h3>

      <div className="space-y-2 mb-4">
        {STRATEGIES.map((s) => (
          <button
            key={s.value}
            onClick={() => onStrategyChange(s.value)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-all ${
              strategy === s.value
                ? 'bg-primary/10 border border-primary/20 text-primary'
                : 'bg-surface-container-high/30 border border-transparent text-on-surface-variant hover:bg-surface-container-high/50'
            }`}
          >
            <span className="material-symbols-outlined text-lg">{s.icon}</span>
            <div>
              <p className="text-xs font-medium">{s.label}</p>
              <p className="text-[10px] opacity-70">{s.desc}</p>
            </div>
          </button>
        ))}
      </div>

      <button
        onClick={onOptimize}
        disabled={isOptimizing}
        className="w-full bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-lg py-2.5 text-sm font-semibold shadow-lg shadow-primary/20 disabled:opacity-50 flex items-center justify-center gap-2"
      >
        {isOptimizing ? (
          <>
            <span className="material-symbols-outlined animate-spin text-lg">
              progress_activity
            </span>
            Optimisation...
          </>
        ) : (
          <>
            <span className="material-symbols-outlined text-lg">route</span>
            Lancer l&apos;optimisation
          </>
        )}
      </button>
    </div>
  );
}
