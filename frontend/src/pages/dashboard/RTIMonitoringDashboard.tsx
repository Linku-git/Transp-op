import { useEffect, useState } from 'react';
import { getRtiKpis, getRiskStops, type RTIKpiData, type RiskStop } from '../../api/rti';
import { ComplianceGauge } from '../../components/rti/ComplianceGauge';
import { WaitTimeHeatmap } from '../../components/rti/WaitTimeHeatmap';
import { RiskStopMapOverlay } from '../../components/rti/RiskStopMapOverlay';
import { ViolationAlertList } from '../../components/rti/ViolationAlertList';
import { ComplianceTrendChart } from '../../components/rti/ComplianceTrendChart';

export function RTIMonitoringDashboard() {
  const [kpis, setKpis] = useState<RTIKpiData | null>(null);
  const [stops, setStops] = useState<RiskStop[]>([]);
  const [period, setPeriod] = useState('day');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async (p: string = period) => {
    try {
      setLoading(true);
      setError(null);
      const [kpiData, stopsData] = await Promise.all([
        getRtiKpis(p),
        getRiskStops(),
      ]);
      setKpis(kpiData);
      setStops(stopsData.data);
    } catch {
      setError('Erreur de chargement des données RTI');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(() => loadData(), 30000);
    return () => clearInterval(interval);
  }, []);

  const handlePeriodChange = (p: string) => {
    setPeriod(p);
    loadData(p);
  };

  if (loading && !kpis) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="mt-3 text-sm text-on-surface-variant">Chargement RTI...</p>
        </div>
      </div>
    );
  }

  if (error && !kpis) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <span className="material-symbols-outlined text-4xl text-error/50">error</span>
          <p className="mt-2 text-sm text-on-surface-variant">{error}</p>
          <button onClick={() => loadData()} className="mt-3 text-primary text-sm font-medium">
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">Monitoring RTI</h1>
          <p className="text-sm text-on-surface-variant mt-1">Suivi en temps réel de la conformité transport</p>
        </div>
        <button
          onClick={() => loadData()}
          className="flex items-center gap-2 px-4 py-2 bg-surface-container-lowest rounded-lg shadow-sm border border-outline-variant/10 text-sm font-medium hover:bg-surface-container-low transition-colors"
        >
          <span className="material-symbols-outlined text-base">refresh</span>
          Actualiser
        </button>
      </div>

      {/* KPI Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <ComplianceGauge value={kpis?.compliance_pct ?? 0} />
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 flex flex-col justify-center">
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">Temps d'attente moyen</p>
          <p className="text-3xl font-bold text-on-surface mt-2">{kpis?.avg_wait_seconds ?? 0}s</p>
        </div>
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 flex flex-col justify-center">
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">Violations actives</p>
          <p className={`text-3xl font-bold mt-2 ${(kpis?.active_violations ?? 0) > 0 ? 'text-error' : 'text-green-600'}`}>
            {kpis?.active_violations ?? 0}
          </p>
        </div>
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 flex flex-col justify-center">
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">Événements totaux</p>
          <p className="text-3xl font-bold text-on-surface mt-2">{kpis?.total_events ?? 0}</p>
        </div>
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ComplianceTrendChart
          data={kpis?.trend ?? []}
          period={period}
          onPeriodChange={handlePeriodChange}
        />
        <WaitTimeHeatmap stops={stops} />
      </div>

      {/* Map + Violations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RiskStopMapOverlay stops={stops} />
        <ViolationAlertList violations={[]} />
      </div>
    </div>
  );
}
