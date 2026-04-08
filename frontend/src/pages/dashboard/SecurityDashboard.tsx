import { useEffect, useState } from 'react';
import { getSecurityKpis, getRiskMap, type SecurityKpiData, type RiskMapStop } from '../../api/security';
import { ScoreDistributionChart } from '../../components/security/ScoreDistributionChart';
import { RiskStopMap } from '../../components/security/RiskStopMap';
import { NightShiftCoverage } from '../../components/security/NightShiftCoverage';
import { IncidentTimeline } from '../../components/security/IncidentTimeline';
import { EmergencyAlertLog } from '../../components/security/EmergencyAlertLog';

export function SecurityDashboard() {
  const [kpis, setKpis] = useState<SecurityKpiData | null>(null);
  const [stops, setStops] = useState<RiskMapStop[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [kpiData, mapData] = await Promise.all([getSecurityKpis(), getRiskMap()]);
        setKpis(kpiData);
        setStops(mapData.stops);
      } catch {
        // Silent fail — components handle empty state
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-on-surface">Tableau de bord sécurité</h1>
        <p className="text-sm text-on-surface-variant mt-1">Suivi des scores de sécurité et incidents</p>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">Score moyen</p>
          <p className="text-3xl font-bold text-on-surface mt-2">{kpis?.avg_score ?? 0}</p>
          <p className="text-xs text-on-surface-variant">/100</p>
        </div>
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">Employés évalués</p>
          <p className="text-3xl font-bold text-on-surface mt-2">{kpis?.total_scored_employees ?? 0}</p>
        </div>
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">Arrêts à risque</p>
          <p className="text-3xl font-bold text-error mt-2">{stops.filter((s) => s.is_critical).length}</p>
        </div>
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">Incidents (30j)</p>
          <p className="text-3xl font-bold text-on-surface mt-2">{kpis?.incident_count_30d ?? 0}</p>
        </div>
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ScoreDistributionChart distribution={kpis?.risk_distribution ?? { low: 0, medium: 0, high: 0, critical: 0 }} />
        <NightShiftCoverage coveragePct={kpis?.night_shift_coverage_pct ?? 0} />
      </div>

      {/* Map */}
      <RiskStopMap stops={stops} />

      {/* Timeline + alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <IncidentTimeline incidents={[]} />
        <EmergencyAlertLog alerts={[]} />
      </div>
    </div>
  );
}
