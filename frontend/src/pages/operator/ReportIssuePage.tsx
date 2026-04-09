import { useState, useCallback, type FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { reportServiceIssue } from '@/api/operator';
import { extractApiError } from '@/lib/apiError';

const ISSUE_TYPES = [
  { value: 'delay', label: 'Retard' },
  { value: 'breakdown', label: 'Panne véhicule' },
  { value: 'safety', label: 'Problème sécurité' },
  { value: 'capacity', label: 'Capacité insuffisante' },
  { value: 'route', label: 'Problème de trajet' },
  { value: 'other', label: 'Autre' },
];

export function ReportIssuePage() {
  const navigate = useNavigate();
  const [issueType, setIssueType] = useState('delay');
  const [description, setDescription] = useState('');
  const [affectedRoute, setAffectedRoute] = useState('');
  const [incidentDate, setIncidentDate] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = useCallback(async (e: FormEvent) => {
    e.preventDefault();
    if (description.length < 10) {
      setError('La description doit contenir au moins 10 caractères');
      return;
    }
    setIsSubmitting(true);
    setError(null);
    try {
      await reportServiceIssue({
        issue_type: issueType,
        description,
        affected_route: affectedRoute || undefined,
        incident_date: incidentDate || undefined,
      });
      navigate('/operator');
    } catch (err) {
      setError(extractApiError(err, 'Erreur lors de la soumission'));
    } finally {
      setIsSubmitting(false);
    }
  }, [issueType, description, affectedRoute, incidentDate, navigate]);

  return (
    <div className="flex flex-col gap-6 max-w-2xl">
      <nav className="flex items-center gap-2 text-sm text-on-surface-variant">
        <Link to="/operator" className="hover:text-primary">Portail</Link>
        <span className="material-symbols-outlined text-[14px]">chevron_right</span>
        <span className="text-on-surface font-medium">Signaler un incident</span>
      </nav>

      <h1 className="font-display text-2xl font-bold text-on-surface">
        Signaler un incident
      </h1>

      {error && (
        <div className="rounded-lg bg-error-container/30 px-4 py-3 text-sm text-error">{error}</div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 space-y-4">
          <div>
            <label className="block text-xs font-medium text-on-surface-variant mb-1">Type d&apos;incident *</label>
            <select
              value={issueType}
              onChange={(e) => setIssueType(e.target.value)}
              className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2.5 text-sm outline-none focus:ring-1 focus:ring-primary/20 appearance-none"
            >
              {ISSUE_TYPES.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-on-surface-variant mb-1">Description *</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Décrivez l'incident en détail..."
              rows={4}
              className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2.5 text-sm outline-none focus:ring-1 focus:ring-primary/20 resize-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-on-surface-variant mb-1">Route affectée</label>
            <input
              type="text"
              value={affectedRoute}
              onChange={(e) => setAffectedRoute(e.target.value)}
              placeholder="Ex: Route A1"
              className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2.5 text-sm outline-none focus:ring-1 focus:ring-primary/20"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-on-surface-variant mb-1">Date de l&apos;incident</label>
            <input
              type="date"
              value={incidentDate}
              onChange={(e) => setIncidentDate(e.target.value)}
              className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2.5 text-sm outline-none focus:ring-1 focus:ring-primary/20"
            />
          </div>
        </div>

        <div className="flex justify-end gap-3">
          <Link to="/operator" className="px-4 py-2.5 rounded-lg text-on-surface-variant text-sm hover:bg-surface-container-high/50">
            Annuler
          </Link>
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-5 py-2.5 rounded-lg bg-gradient-to-br from-primary to-primary-container text-on-primary text-sm font-medium shadow-lg shadow-primary/20 disabled:opacity-60"
          >
            {isSubmitting ? 'Envoi...' : 'Soumettre'}
          </button>
        </div>
      </form>
    </div>
  );
}
