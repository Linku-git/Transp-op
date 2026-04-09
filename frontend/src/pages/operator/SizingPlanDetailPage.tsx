import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getSizingPlan, type OperatorSizingPlan } from '@/api/operator';

export function SizingPlanDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [plan, setPlan] = useState<OperatorSizingPlan | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    getSizingPlan(id)
      .then(setPlan)
      .catch(() => {})
      .finally(() => setIsLoading(false));
  }, [id]);

  if (isLoading) return <div className="text-center py-12 text-sm text-on-surface-variant">Chargement...</div>;
  if (!plan) return <div className="text-center py-12 text-sm text-on-surface-variant">Plan introuvable</div>;

  const summary = plan.content_summary ?? {};

  return (
    <div className="flex flex-col gap-6 max-w-4xl">
      <nav className="flex items-center gap-2 text-sm text-on-surface-variant">
        <Link to="/operator" className="hover:text-primary">Portail</Link>
        <span className="material-symbols-outlined text-[14px]">chevron_right</span>
        <span className="text-on-surface font-medium">Plan v{plan.version}</span>
      </nav>

      <h1 className="font-display text-2xl font-bold text-on-surface">
        Plan de dimensionnement v{plan.version}
      </h1>

      {/* Route details */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">Routes et arrêts</h3>
        <div className="grid grid-cols-3 gap-4">
          <InfoCard label="Routes" value={String(summary.routes ?? 0)} icon="route" />
          <InfoCard label="Distance" value={`${summary.distance_km ?? 0} km`} icon="straighten" />
          <InfoCard label="Passagers" value={String(summary.passengers ?? 0)} icon="group" />
        </div>
      </div>

      {/* Vehicle specs */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">Véhicules</h3>
        <div className="grid grid-cols-3 gap-4">
          <InfoCard label="Total véhicules" value={String(summary.vehicles ?? 0)} icon="directions_bus" />
          <InfoCard label="PMR" value={String(summary.pmr ?? 0)} icon="accessible" />
          <InfoCard label="Format" value={plan.format.toUpperCase()} icon="description" />
        </div>
      </div>

      {/* Status */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">Statut</h3>
        <p className="text-sm text-on-surface">
          {plan.acknowledged ? '✅ Plan confirmé' : '⏳ En attente de confirmation'}
        </p>
      </div>
    </div>
  );
}

function InfoCard({ label, value, icon }: { label: string; value: string; icon: string }) {
  return (
    <div className="flex items-center gap-3">
      <span className="material-symbols-outlined text-xl text-primary/60">{icon}</span>
      <div>
        <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">{label}</p>
        <p className="text-lg font-bold text-on-surface">{value}</p>
      </div>
    </div>
  );
}
