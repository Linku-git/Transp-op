import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
  listConnections,
  createConnection,
  deleteConnection,
  triggerSync,
  type SIRHConnection,
  type ConnectionCreate,
} from '@/api/sirh';

const PROVIDERS = [
  { value: 'sap', label: 'SAP SuccessFactors', icon: 'business' },
  { value: 'workday', label: 'Workday', icon: 'work' },
  { value: 'talentsoft', label: 'Talentsoft', icon: 'school' },
  { value: 'sage', label: 'Sage HR', icon: 'account_balance' },
];

const STATUS_STYLES: Record<string, string> = {
  active: 'bg-green-50 text-green-700',
  paused: 'bg-amber-50 text-amber-700',
  error: 'bg-error-container/30 text-error',
  deleted: 'bg-surface-container-high text-on-surface-variant',
};

export function SIRHConnectionsPage() {
  const [connections, setConnections] = useState<SIRHConnection[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showWizard, setShowWizard] = useState(false);
  const [wizardStep, setWizardStep] = useState(0);
  const [formData, setFormData] = useState<ConnectionCreate>({
    provider: 'sap',
    name: '',
    sync_frequency: 'daily',
    conflict_strategy: 'sirh_wins',
  });

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await listConnections();
      setConnections(res.data);
    } catch {
      setError('Impossible de charger les connexions');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleCreate = async () => {
    try {
      await createConnection(formData);
      setShowWizard(false);
      setWizardStep(0);
      setFormData({ provider: 'sap', name: '', sync_frequency: 'daily', conflict_strategy: 'sirh_wins' });
      await load();
    } catch {
      setError('Erreur lors de la création');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Supprimer cette connexion ?')) return;
    await deleteConnection(id);
    await load();
  };

  const handleSync = async (id: string) => {
    try {
      await triggerSync(id);
      await load();
    } catch {
      setError('Erreur de synchronisation');
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-on-surface">
            Connexions SIRH
          </h1>
          <p className="text-sm text-on-surface-variant mt-1">
            Gérez les intégrations avec vos systèmes RH
          </p>
        </div>
        <div className="flex gap-3">
          <Link
            to="/admin/sirh/sync"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-surface-container-lowest text-on-surface text-sm font-medium border border-outline-variant/15 shadow-sm hover:bg-surface-container-low transition-colors"
          >
            <span className="material-symbols-outlined text-[18px]">sync</span>
            Tableau de bord sync
          </Link>
          <button
            onClick={() => setShowWizard(true)}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-gradient-to-br from-primary to-primary-container text-on-primary text-sm font-medium shadow-lg shadow-primary/20 hover:shadow-xl transition-all"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            Ajouter une connexion
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-lg bg-error-container/30 px-4 py-3 text-sm text-error">
          {error}
        </div>
      )}

      {/* Connection list */}
      <div className="grid gap-4">
        {isLoading ? (
          <div className="text-center py-12 text-on-surface-variant text-sm">Chargement...</div>
        ) : connections.length === 0 ? (
          <div className="text-center py-12">
            <span className="material-symbols-outlined text-4xl text-on-surface-variant/40">link</span>
            <p className="text-sm text-on-surface-variant mt-2">Aucune connexion configurée</p>
          </div>
        ) : (
          connections.map((conn) => (
            <div key={conn.id} className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-5 flex items-center gap-4">
              <span className="material-symbols-outlined text-2xl text-primary/60">
                {PROVIDERS.find((p) => p.value === conn.provider)?.icon ?? 'link'}
              </span>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-medium text-on-surface">{conn.name}</h3>
                  <span className={['px-2 py-0.5 rounded-full text-xs font-medium', STATUS_STYLES[conn.status] ?? ''].join(' ')}>
                    {conn.status}
                  </span>
                </div>
                <p className="text-xs text-on-surface-variant mt-0.5">
                  {PROVIDERS.find((p) => p.value === conn.provider)?.label} · {conn.sync_frequency} · Dernière sync: {conn.last_sync_at ? new Date(conn.last_sync_at).toLocaleDateString('fr-FR') : 'Jamais'}
                </p>
              </div>
              <div className="flex gap-2">
                <button onClick={() => handleSync(conn.id)} title="Synchroniser" className="p-2 rounded-lg hover:bg-surface-container-high/50 text-on-surface-variant">
                  <span className="material-symbols-outlined text-[18px]">sync</span>
                </button>
                <button onClick={() => handleDelete(conn.id)} title="Supprimer" className="p-2 rounded-lg hover:bg-error-container/20 text-error">
                  <span className="material-symbols-outlined text-[18px]">delete</span>
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Wizard modal */}
      {showWizard && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-surface-container-lowest rounded-xl shadow-lg p-6 w-full max-w-md space-y-4">
            <h2 className="text-lg font-semibold text-on-surface">
              {wizardStep === 0 ? 'Choisir le fournisseur' : wizardStep === 1 ? 'Configuration' : 'Fréquence de sync'}
            </h2>

            {wizardStep === 0 && (
              <div className="grid grid-cols-2 gap-3">
                {PROVIDERS.map((p) => (
                  <button
                    key={p.value}
                    onClick={() => { setFormData({ ...formData, provider: p.value, name: p.label }); setWizardStep(1); }}
                    className={['p-4 rounded-lg border text-center transition-all', formData.provider === p.value ? 'border-primary bg-primary/5' : 'border-outline-variant/15 hover:bg-surface-container-low'].join(' ')}
                  >
                    <span className="material-symbols-outlined text-2xl text-primary">{p.icon}</span>
                    <p className="text-xs font-medium mt-1">{p.label}</p>
                  </button>
                ))}
              </div>
            )}

            {wizardStep === 1 && (
              <div className="space-y-3">
                <input type="text" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} placeholder="Nom de la connexion" className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2.5 text-sm outline-none focus:ring-1 focus:ring-primary/20" />
                <select value={formData.conflict_strategy} onChange={(e) => setFormData({ ...formData, conflict_strategy: e.target.value })} className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2.5 text-sm outline-none focus:ring-1 focus:ring-primary/20 appearance-none">
                  <option value="sirh_wins">SIRH prioritaire</option>
                  <option value="platform_wins">Plateforme prioritaire</option>
                  <option value="manual">Résolution manuelle</option>
                </select>
              </div>
            )}

            {wizardStep === 2 && (
              <select value={formData.sync_frequency} onChange={(e) => setFormData({ ...formData, sync_frequency: e.target.value })} className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2.5 text-sm outline-none focus:ring-1 focus:ring-primary/20 appearance-none">
                <option value="hourly">Toutes les heures</option>
                <option value="daily">Quotidien</option>
                <option value="weekly">Hebdomadaire</option>
                <option value="manual">Manuel</option>
              </select>
            )}

            <div className="flex justify-between pt-2">
              <button onClick={() => { if (wizardStep === 0) setShowWizard(false); else setWizardStep(wizardStep - 1); }} className="text-sm text-on-surface-variant hover:text-on-surface">
                {wizardStep === 0 ? 'Annuler' : 'Retour'}
              </button>
              <button onClick={() => { if (wizardStep < 2) setWizardStep(wizardStep + 1); else handleCreate(); }} className="px-4 py-2 rounded-lg bg-primary text-on-primary text-sm font-medium">
                {wizardStep < 2 ? 'Suivant' : 'Créer'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
