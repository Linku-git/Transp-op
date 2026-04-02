import { Link } from 'react-router-dom';
import { ShiftsEditorTable } from '@/components/shifts/ShiftsEditorTable';

export function HoraireTravailPage() {
  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-on-surface">Horaires de Travail</h1>
        <p className="text-sm text-on-surface-variant mt-0.5">
          Configuration des postes et horaires de l'entreprise
        </p>
      </div>

      {/* Sub-nav */}
      <div className="flex gap-2 border-b border-surface-container-high pb-3 flex-wrap">
        <Link to="/vehicles" className="text-sm font-medium text-on-surface-variant hover:text-on-surface px-1 pb-1">
          Parc Véhicule
        </Link>
        <Link to="/fleet/consumption" className="text-sm font-medium text-on-surface-variant hover:text-on-surface px-1 pb-1">
          Km & Consommation
        </Link>
        <Link to="/fleet/stops" className="text-sm font-medium text-on-surface-variant hover:text-on-surface px-1 pb-1">
          Points d'Arrêt
        </Link>
        <Link to="/fleet/config" className="text-sm font-medium text-on-surface-variant hover:text-on-surface px-1 pb-1">
          Config. Transport
        </Link>
        <Link to="/fleet/horaires" className="text-sm font-medium text-primary border-b-2 border-primary pb-1 px-1">
          Horaires de Travail
        </Link>
      </div>

      {/* Info banner */}
      <div className="flex items-start gap-3 rounded-xl bg-blue-50 px-4 py-3 border border-blue-100">
        <span className="material-symbols-outlined text-blue-500 text-lg mt-0.5">info</span>
        <div>
          <p className="text-sm font-semibold text-blue-900">Horaires partagés par tous les sites</p>
          <p className="text-xs text-blue-700 mt-0.5">
            Ces postes sont définis au niveau entreprise et s'appliquent à l'ensemble des sites.
            Ils seront associables aux employés et aux routes véhicules.
          </p>
        </div>
      </div>

      {/* Inline-editable shifts table */}
      <ShiftsEditorTable siteId={null} />
    </div>
  );
}
