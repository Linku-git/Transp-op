import { useCallback, useState } from 'react';
import type {
  MCDAAlternative,
  MCDAResponse,
  MCDAWeights,
} from '../../types/sotreg';
import { computeMCDA, downloadMCDAReportExcel, downloadMCDAReportPdf } from '../../api/sotreg';
import { extractApiError } from '../../lib/apiError';
import { MCDAInputForm } from '../../components/sotreg/MCDAInputForm';
import { MCDAResultsTable } from '../../components/sotreg/MCDAResultsTable';
import { RadarComparisonChart } from '../../components/sotreg/RadarComparisonChart';
import { SensitivitySliders } from '../../components/sotreg/SensitivitySliders';
import { ModalChoicePanel } from '../../components/sotreg/ModalChoicePanel';

type TabKey = 'mcda' | 'modal' | 'reports';

const TABS: { key: TabKey; label: string; icon: string }[] = [
  { key: 'mcda', label: 'Analyse MCDA', icon: 'analytics' },
  { key: 'modal', label: 'Choix Modal', icon: 'psychology' },
  { key: 'reports', label: 'Rapports', icon: 'description' },
];

export default function ScoringDashboardPage() {
  const [activeTab, setActiveTab] = useState<TabKey>('mcda');

  return (
    <div className="flex flex-col gap-6 p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-on-surface">Scoring & MCDA</h1>
        <p className="text-sm text-on-surface-variant mt-1">
          Module M7 — Analyse multicritère, choix modal et rapports de comparaison
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-surface-container-high/50 rounded-xl p-1">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            type="button"
            onClick={() => setActiveTab(tab.key)}
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
              activeTab === tab.key
                ? 'bg-surface-container-lowest shadow-sm text-primary'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            <span className="material-symbols-outlined text-lg">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {activeTab === 'mcda' && <MCDATab />}
      {activeTab === 'modal' && <ModalTab />}
      {activeTab === 'reports' && <ReportsTab />}
    </div>
  );
}

/* ─── MCDA Tab ─────────────────────────────────────────────────────────── */

function MCDATab() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<MCDAResponse | null>(null);
  const [alternatives, setAlternatives] = useState<MCDAAlternative[]>([]);
  const [scenarioId, setScenarioId] = useState<string | null>(null);

  const handleSubmit = useCallback(
    async (alts: MCDAAlternative[], weights: MCDAWeights, scenarioName: string) => {
      setLoading(true);
      setError(null);
      setAlternatives(alts);
      try {
        const res = await computeMCDA({
          alternatives: alts,
          weights,
          scenario_name: scenarioName,
        });
        setResults(res);
        // Extract scenario ID from the response headers or derive it
        // For now we won't have an ID until the backend returns it
        setScenarioId(null);
      } catch (err) {
        setError(extractApiError(err, 'Erreur lors du calcul MCDA'));
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  return (
    <div className="space-y-6">
      <MCDAInputForm onSubmit={handleSubmit} loading={loading} />

      {error && (
        <div className="bg-error-container/30 text-error rounded-lg px-4 py-3 text-sm flex items-center gap-2">
          <span className="material-symbols-outlined text-lg">error</span>
          {error}
        </div>
      )}

      {results && (
        <>
          {/* Results table */}
          <MCDAResultsTable results={results} />

          {/* Radar + Sensitivity side by side */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <RadarComparisonChart alternatives={results.ranked_alternatives} />
            <SensitivitySliders
              alternatives={alternatives}
              baseResults={results}
              onResultsChange={setResults}
            />
          </div>

          {/* Download buttons */}
          {scenarioId && <DownloadButtons scenarioId={scenarioId} />}
        </>
      )}
    </div>
  );
}

/* ─── Modal Choice Tab ─────────────────────────────────────────────────── */

function ModalTab() {
  return <ModalChoicePanel />;
}

/* ─── Reports Tab ──────────────────────────────────────────────────────── */

function ReportsTab() {
  const [scenarioId, setScenarioId] = useState('');

  return (
    <div className="space-y-6">
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
          Télécharger un rapport MCDA
        </h3>
        <p className="text-sm text-on-surface-variant mb-4">
          Entrez l'identifiant d'un scénario MCDA enregistré pour générer un rapport PDF ou Excel.
        </p>
        <div className="flex gap-3 items-end">
          <div className="flex-1">
            <label className="text-xs font-medium text-on-surface-variant block mb-1">
              ID du scénario
            </label>
            <input
              type="text"
              value={scenarioId}
              onChange={(e) => setScenarioId(e.target.value)}
              placeholder="UUID du scénario..."
              className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
            />
          </div>
        </div>
        {scenarioId.trim() && <DownloadButtons scenarioId={scenarioId.trim()} />}
      </div>

      {/* Info */}
      <div className="bg-primary/5 rounded-xl p-5 flex gap-3">
        <span className="material-symbols-outlined text-primary text-xl flex-shrink-0">info</span>
        <div className="text-sm text-on-surface-variant">
          <p className="font-medium text-on-surface mb-1">Comment obtenir l'ID ?</p>
          <p>
            Lancez une analyse dans l'onglet MCDA. Le scénario est automatiquement
            sauvegardé en base de données. L'identifiant est affiché après le calcul.
          </p>
        </div>
      </div>
    </div>
  );
}

/* ─── Download Buttons ─────────────────────────────────────────────────── */

function DownloadButtons({ scenarioId }: { scenarioId: string }) {
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [downloadingExcel, setDownloadingExcel] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const handleDownload = useCallback(
    async (format: 'pdf' | 'excel') => {
      const setLoading = format === 'pdf' ? setDownloadingPdf : setDownloadingExcel;
      setLoading(true);
      setDownloadError(null);
      try {
        const blob =
          format === 'pdf'
            ? await downloadMCDAReportPdf(scenarioId)
            : await downloadMCDAReportExcel(scenarioId);

        const ext = format === 'pdf' ? 'pdf' : 'xlsx';
        const mime =
          format === 'pdf'
            ? 'application/pdf'
            : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';

        const url = URL.createObjectURL(new Blob([blob], { type: mime }));
        const a = document.createElement('a');
        a.href = url;
        a.download = `mcda_report_${scenarioId.slice(0, 8)}.${ext}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } catch (err) {
        setDownloadError(extractApiError(err, `Erreur lors du téléchargement ${format.toUpperCase()}`));
      } finally {
        setLoading(false);
      }
    },
    [scenarioId],
  );

  return (
    <div className="mt-4 space-y-2">
      <div className="flex gap-3">
        <button
          type="button"
          onClick={() => handleDownload('pdf')}
          disabled={downloadingPdf}
          className="flex items-center gap-2 bg-error/10 text-error px-4 py-2 rounded-lg text-sm font-medium hover:bg-error/20 disabled:opacity-50"
        >
          {downloadingPdf ? (
            <span className="material-symbols-outlined animate-spin text-lg">progress_activity</span>
          ) : (
            <span className="material-symbols-outlined text-lg">picture_as_pdf</span>
          )}
          Télécharger PDF
        </button>
        <button
          type="button"
          onClick={() => handleDownload('excel')}
          disabled={downloadingExcel}
          className="flex items-center gap-2 bg-green-50 text-green-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-100 disabled:opacity-50"
        >
          {downloadingExcel ? (
            <span className="material-symbols-outlined animate-spin text-lg">progress_activity</span>
          ) : (
            <span className="material-symbols-outlined text-lg">table_chart</span>
          )}
          Télécharger Excel
        </button>
      </div>
      {downloadError && (
        <p className="text-xs text-error">{downloadError}</p>
      )}
    </div>
  );
}
