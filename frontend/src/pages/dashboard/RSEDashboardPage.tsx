import { useEffect, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { getRSEKPIs, exportDPEF } from '@/api/rse';
import type { RSEKPIsResponse } from '@/types/rse';
import { Card } from '@/components/ui/Card';
import { PieChart } from '@/components/charts/PieChart';
import { CO2TrendLine } from '@/components/dashboard/CO2TrendLine';
import { ZFEComplianceGauge } from '@/components/dashboard/ZFEComplianceGauge';
import { ModalShiftComparison } from '@/components/dashboard/ModalShiftComparison';

export function RSEDashboardPage() {
  const { t } = useTranslation();
  const [data, setData] = useState<RSEKPIsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getRSEKPIs();
      setData(result);
    } catch {
      setError(t('common.error'));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    void fetchData();
  }, [fetchData]);

  const handleExportDPEF = useCallback(async () => {
    setExporting(true);
    try {
      const blob = await exportDPEF();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'rapport-dpef.pdf';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch {
      // Silently handle export errors
    } finally {
      setExporting(false);
    }
  }, []);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center" data-testid="rse-loading">
        <div className="flex items-center gap-3">
          <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <span className="font-sans text-sm text-on-surface-variant">
            {t('common.loading')}
          </span>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-4">
        <span className="material-symbols-outlined text-4xl text-error">error</span>
        <p className="font-sans text-sm text-on-surface-variant">
          {error ?? t('common.error')}
        </p>
        <button
          type="button"
          onClick={() => void fetchData()}
          className="bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-lg shadow-lg shadow-primary/20 px-4 py-2 font-sans text-sm font-medium"
        >
          {t('rse.retry', 'Reessayer')}
        </button>
      </div>
    );
  }

  const modalPieData = data.modal_distribution.by_mode.map((entry) => ({
    name: entry.mode,
    value: entry.count,
  }));

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* Page header */}
      <div>
        <h1 className="font-sans text-xl font-bold text-on-surface">
          {t('rse.title', 'Tableau de bord RSE / Environnement')}
        </h1>
        <p className="font-sans text-sm text-on-surface-variant mt-1">
          {t('rse.subtitle', 'Impact environnemental et conformite mobilite durable.')}
        </p>
      </div>

      {/* Row 1: Summary cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <div className="flex flex-col items-center justify-center h-full">
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">
              {t('rse.co2_saved_label', 'CO2 economise')}
            </p>
            <p
              className="font-sans text-4xl font-bold text-green-600"
              data-testid="co2-saved-card"
            >
              {data.co2_savings.co2_saved_kg.toLocaleString('fr-FR')}
              <span className="text-lg ml-1">kg</span>
            </p>
            <p className="font-sans text-xs text-on-surface-variant mt-1">
              {data.co2_savings.co2_saved_pct.toFixed(1)}% {t('rse.reduction', 'de reduction')}
            </p>
          </div>
        </Card>
        <Card>
          <div className="flex flex-col items-center justify-center h-full">
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">
              {t('rse.vehicles_avoided_label', 'Vehicules personnels evites')}
            </p>
            <p
              className="font-sans text-4xl font-bold text-primary"
              data-testid="vehicles-avoided-card"
            >
              {data.private_vehicles_avoided.vehicles_avoided}
            </p>
            <p className="font-sans text-xs text-on-surface-variant mt-1">
              {t('rse.adoption', 'Adoption')}: {data.private_vehicles_avoided.adoption_pct.toFixed(1)}%
            </p>
          </div>
        </Card>
        <Card>
          <div className="flex flex-col items-center justify-center h-full">
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">
              {t('rse.zfe_compliance_label', 'Conformite ZFE')}
            </p>
            <p
              className={`font-sans text-4xl font-bold ${data.zfe_compliance.compliance_pct >= 80 ? 'text-green-600' : data.zfe_compliance.compliance_pct >= 50 ? 'text-amber-600' : 'text-error'}`}
              data-testid="zfe-compliance-card"
            >
              {data.zfe_compliance.compliance_pct.toFixed(0)}%
            </p>
            <p className="font-sans text-xs text-on-surface-variant mt-1">
              {data.zfe_compliance.compliant_count}/{data.zfe_compliance.total_count} {t('rse.vehicles', 'vehicules')}
            </p>
          </div>
        </Card>
      </div>

      {/* Row 2: CO2 trend */}
      <Card title={t('rse.co2_trend_title', 'Evolution des economies CO2')}>
        <CO2TrendLine
          trend={data.co2_savings.trend}
          totalSaved={data.co2_savings.co2_saved_kg}
        />
      </Card>

      {/* Row 3: Modal distribution + ZFE gauge */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title={t('rse.modal_distribution_title', 'Distribution modale')}>
          <PieChart data={modalPieData} height={280} showLegend />
          <div className="mt-4 grid grid-cols-2 gap-3">
            <div className="bg-surface-container-low rounded-lg p-3">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                {t('rse.soft_mobility', 'Mobilite douce')}
              </p>
              <p className="font-sans text-lg font-bold text-green-600">
                {data.modal_distribution.soft_pct}%
              </p>
            </div>
            <div className="bg-surface-container-low rounded-lg p-3">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                {t('rse.shared_mobility', 'Mobilite partagee')}
              </p>
              <p className="font-sans text-lg font-bold text-primary">
                {data.modal_distribution.shared_pct}%
              </p>
            </div>
            <div className="bg-surface-container-low rounded-lg p-3">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                {t('rse.electric', 'Electrique')}
              </p>
              <p className="font-sans text-lg font-bold text-blue-500">
                {data.modal_distribution.electric_pct}%
              </p>
            </div>
            <div className="bg-surface-container-low rounded-lg p-3">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                {t('rse.individual', 'Individuel')}
              </p>
              <p className="font-sans text-lg font-bold text-on-surface-variant">
                {data.modal_distribution.individual_pct}%
              </p>
            </div>
          </div>
        </Card>
        <Card title={t('rse.zfe_gauge_title', 'Conformite flotte ZFE')}>
          <div className="flex flex-col items-center justify-center py-6">
            <ZFEComplianceGauge
              compliantCount={data.zfe_compliance.compliant_count}
              totalCount={data.zfe_compliance.total_count}
              compliancePct={data.zfe_compliance.compliance_pct}
            />
          </div>
        </Card>
      </div>

      {/* Row 4: Before/After comparison */}
      <Card title={t('rse.modal_shift_title', 'Report modal avant/apres')}>
        <ModalShiftComparison beforeAfter={data.modal_distribution.before_after} />
      </Card>

      {/* DPEF export button */}
      <div className="flex justify-end">
        <button
          type="button"
          onClick={() => void handleExportDPEF()}
          disabled={exporting}
          className="bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-lg shadow-lg shadow-primary/20 px-6 py-3 font-sans text-sm font-medium flex items-center gap-2 disabled:opacity-50"
          data-testid="dpef-export-btn"
        >
          <span className="material-symbols-outlined text-lg">download</span>
          {exporting
            ? t('common.loading')
            : t('rse.export_dpef', 'Exporter rapport DPEF')}
        </button>
      </div>
    </div>
  );
}
