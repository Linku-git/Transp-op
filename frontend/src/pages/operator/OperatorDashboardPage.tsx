import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
  listSizingPlans,
  acknowledgePlan,
  type OperatorSizingPlan,
} from '@/api/operator';

const STATUS_STYLES: Record<string, string> = {
  completed: 'bg-blue-50 text-blue-700',
  acknowledged: 'bg-green-50 text-green-700',
  pending: 'bg-amber-50 text-amber-700',
};

export function OperatorDashboardPage() {
  const [plans, setPlans] = useState<OperatorSizingPlan[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await listSizingPlans();
      setPlans(res.data);
    } catch {
      setError('Impossible de charger les plans');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleAcknowledge = async (planId: string) => {
    if (!confirm('Confirmer la réception de ce plan ?')) return;
    try {
      await acknowledgePlan(planId);
      await load();
    } catch {
      setError('Erreur lors de la confirmation');
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-on-surface">
            Portail Opérateur
          </h1>
          <p className="text-sm text-on-surface-variant mt-1">
            Plans de dimensionnement assignés
          </p>
        </div>
        <Link
          to="/operator/report-issue"
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-surface-container-lowest text-on-surface text-sm font-medium border border-outline-variant/15 shadow-sm hover:bg-surface-container-low transition-colors"
        >
          <span className="material-symbols-outlined text-[18px]">report_problem</span>
          Signaler un incident
        </Link>
      </div>

      {error && (
        <div className="rounded-lg bg-error-container/30 px-4 py-3 text-sm text-error">{error}</div>
      )}

      {isLoading ? (
        <div className="text-center py-12 text-on-surface-variant text-sm">Chargement...</div>
      ) : plans.length === 0 ? (
        <div className="text-center py-12">
          <span className="material-symbols-outlined text-4xl text-on-surface-variant/40">assignment</span>
          <p className="text-sm text-on-surface-variant mt-2">Aucun plan assigné</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {plans.map((plan) => (
            <div key={plan.id} className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-5">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-medium text-on-surface">
                      Plan v{plan.version}
                    </h3>
                    <span className={['px-2 py-0.5 rounded-full text-xs font-medium', STATUS_STYLES[plan.status] ?? ''].join(' ')}>
                      {plan.status === 'acknowledged' ? 'Confirmé' : plan.status}
                    </span>
                    <span className="px-2 py-0.5 rounded-full bg-surface-container-high text-on-surface-variant text-xs">
                      {plan.format.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-xs text-on-surface-variant mt-1">
                    Créé le {new Date(plan.created_at).toLocaleDateString('fr-FR')}
                  </p>
                  {plan.content_summary && (
                    <div className="flex gap-4 mt-2 text-xs text-on-surface-variant">
                      <span>{plan.content_summary.vehicles ?? 0} véhicules</span>
                      <span>{plan.content_summary.routes ?? 0} routes</span>
                      <span>{plan.content_summary.passengers ?? 0} passagers</span>
                    </div>
                  )}
                </div>
                <div className="flex gap-2">
                  <Link
                    to={`/operator/plans/${plan.id}`}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium text-primary hover:bg-primary/5 transition-colors"
                  >
                    Détails
                  </Link>
                  {!plan.acknowledged && (
                    <button
                      onClick={() => handleAcknowledge(plan.id)}
                      className="px-3 py-1.5 rounded-lg text-xs font-medium bg-primary text-on-primary hover:bg-primary-container transition-colors"
                    >
                      Confirmer
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
