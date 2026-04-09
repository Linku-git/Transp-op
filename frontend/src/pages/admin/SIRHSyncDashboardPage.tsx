import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
  getSyncStatus,
  getUnresolvedConflicts,
  resolveConflict,
  type SyncLog,
  type SyncConflict,
} from '@/api/sirh';

const STATUS_STYLES: Record<string, string> = {
  running: 'bg-blue-50 text-blue-700',
  completed: 'bg-green-50 text-green-700',
  completed_with_errors: 'bg-amber-50 text-amber-700',
  failed: 'bg-error-container/30 text-error',
};

export function SIRHSyncDashboardPage() {
  const [logs, setLogs] = useState<SyncLog[]>([]);
  const [conflicts, setConflicts] = useState<SyncConflict[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedLog, setExpandedLog] = useState<string | null>(null);

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      const [logsRes, conflictsRes] = await Promise.all([
        getSyncStatus(),
        getUnresolvedConflicts(),
      ]);
      setLogs(logsRes.data);
      setConflicts(conflictsRes);
    } catch {
      // Silent fail — dashboard shows empty state
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(load, 30000);
    return () => clearInterval(interval);
  }, [load]);

  const handleResolve = async (conflictId: string, resolution: string) => {
    await resolveConflict(conflictId, resolution);
    setConflicts((prev) => prev.filter((c) => c.id !== conflictId));
  };

  const formatDate = (d: string | null) => {
    if (!d) return '—';
    return new Date(d).toLocaleString('fr-FR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <nav className="flex items-center gap-2 text-sm text-on-surface-variant mb-2">
            <Link to="/admin/sirh" className="hover:text-primary transition-colors">Connexions SIRH</Link>
            <span className="material-symbols-outlined text-[14px]">chevron_right</span>
            <span className="text-on-surface font-medium">Synchronisation</span>
          </nav>
          <h1 className="font-display text-2xl font-bold text-on-surface">
            Tableau de bord synchronisation
          </h1>
        </div>
        <button onClick={load} className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-surface-container-lowest text-on-surface text-sm font-medium border border-outline-variant/15 shadow-sm hover:bg-surface-container-low transition-colors">
          <span className="material-symbols-outlined text-[18px]">refresh</span>
          Actualiser
        </button>
      </div>

      {/* Conflict queue */}
      {conflicts.length > 0 && (
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
          <div className="px-5 py-4 flex items-center gap-2">
            <span className="material-symbols-outlined text-amber-600 text-[20px]">warning</span>
            <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
              Conflits non résolus ({conflicts.length})
            </h3>
          </div>
          <table className="w-full">
            <thead>
              <tr className="bg-surface-container-low/50">
                <th className="text-left text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-2">Employé</th>
                <th className="text-left text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-2">Champ</th>
                <th className="text-left text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-2">Plateforme</th>
                <th className="text-left text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-2">SIRH</th>
                <th className="text-right text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-2">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {conflicts.map((c) => (
                <tr key={c.id} className="hover:bg-surface-bright transition-colors">
                  <td className="px-5 py-2 text-xs text-on-surface">{c.employee_id.slice(0, 8)}</td>
                  <td className="px-5 py-2 text-xs text-on-surface">{c.field_name}</td>
                  <td className="px-5 py-2 text-xs text-on-surface-variant">{c.platform_value ?? '—'}</td>
                  <td className="px-5 py-2 text-xs text-on-surface-variant">{c.sirh_value ?? '—'}</td>
                  <td className="px-5 py-2 text-right">
                    <div className="flex justify-end gap-1">
                      <button onClick={() => handleResolve(c.id, 'platform_wins')} title="Garder plateforme" className="px-2 py-1 rounded text-[10px] font-medium bg-blue-50 text-blue-700 hover:bg-blue-100">Plateforme</button>
                      <button onClick={() => handleResolve(c.id, 'sirh_wins')} title="Garder SIRH" className="px-2 py-1 rounded text-[10px] font-medium bg-green-50 text-green-700 hover:bg-green-100">SIRH</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Sync history */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
        <div className="px-5 py-4">
          <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
            Historique de synchronisation
          </h3>
        </div>
        {isLoading ? (
          <div className="text-center py-12 text-on-surface-variant text-sm">Chargement...</div>
        ) : logs.length === 0 ? (
          <div className="text-center py-12">
            <span className="material-symbols-outlined text-3xl text-on-surface-variant/40">sync</span>
            <p className="text-sm text-on-surface-variant mt-2">Aucun historique de sync</p>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="bg-surface-container-low/50">
                <th className="text-left text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-3">Début</th>
                <th className="text-left text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-3">Fin</th>
                <th className="text-right text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-3">Créés</th>
                <th className="text-right text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-3">Maj.</th>
                <th className="text-right text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-3">Échoués</th>
                <th className="text-left text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-3">Statut</th>
                <th className="text-right text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-3">Détails</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {logs.map((log) => (
                <>
                  <tr key={log.id} className="hover:bg-surface-bright transition-colors">
                    <td className="px-5 py-3 text-xs text-on-surface">{formatDate(log.started_at)}</td>
                    <td className="px-5 py-3 text-xs text-on-surface-variant">{formatDate(log.completed_at)}</td>
                    <td className="px-5 py-3 text-xs text-on-surface text-right tabular-nums">{log.records_created}</td>
                    <td className="px-5 py-3 text-xs text-on-surface text-right tabular-nums">{log.records_updated}</td>
                    <td className="px-5 py-3 text-xs text-right tabular-nums">
                      <span className={log.records_failed > 0 ? 'text-error font-medium' : 'text-on-surface'}>
                        {log.records_failed}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      <span className={['px-2 py-0.5 rounded-full text-[10px] font-medium', STATUS_STYLES[log.status] ?? ''].join(' ')}>
                        {log.status}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-right">
                      {log.errors && log.errors.length > 0 && (
                        <button
                          onClick={() => setExpandedLog(expandedLog === log.id ? null : log.id)}
                          className="text-xs text-primary hover:underline"
                        >
                          {expandedLog === log.id ? 'Masquer' : `${log.errors.length} erreur(s)`}
                        </button>
                      )}
                    </td>
                  </tr>
                  {expandedLog === log.id && log.errors && (
                    <tr key={`${log.id}-errors`}>
                      <td colSpan={7} className="px-5 py-3 bg-surface-container-low/30">
                        <ul className="space-y-1">
                          {log.errors.map((err, i) => (
                            <li key={i} className="text-xs text-error">{err}</li>
                          ))}
                        </ul>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
