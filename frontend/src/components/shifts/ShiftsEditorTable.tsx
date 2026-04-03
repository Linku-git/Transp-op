import { useCallback, useEffect, useState } from 'react';
import {
  listHorairesTravail,
  createHoraireTravail,
  updateHoraireTravail,
  deleteHoraireTravail,
  seedDefaultHoraires,
} from '@/api/vehicles';
import type { HoraireTravail } from '@/types/vehicle';

interface RowState {
  type_horaire: string;
  depart_h1: string;
  retour_h1: string;
  depart_h2: string;
  retour_h2: string;
}

function emptyRow(): RowState {
  return { type_horaire: '', depart_h1: '', retour_h1: '', depart_h2: '', retour_h2: '' };
}

function rowFromItem(item: HoraireTravail): RowState {
  return {
    type_horaire: item.type_horaire,
    depart_h1: item.depart_h1 ?? '',
    retour_h1: item.retour_h1 ?? '',
    depart_h2: item.depart_h2 ?? '',
    retour_h2: item.retour_h2 ?? '',
  };
}

function TimeDisplay({ value }: { value: string | null | undefined }) {
  if (!value) return <span className="text-on-surface-variant/40 text-xs">—</span>;
  return <span className="font-mono text-[13px] font-semibold text-on-surface">{value}</span>;
}

function TimeInput({
  value, onChange, placeholder,
}: { value: string; onChange: (v: string) => void; placeholder?: string }) {
  return (
    <input
      type="time"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className="w-full h-8 bg-surface rounded-md border border-outline-variant/50 px-2 text-sm font-mono text-on-surface focus:outline-none focus:ring-1 focus:ring-primary/40 focus:border-primary/60"
    />
  );
}

interface Props {
  siteId?: string | null;
}

export function ShiftsEditorTable({ siteId = null }: Props) {
  const [items, setItems] = useState<HoraireTravail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editRow, setEditRow] = useState<RowState>(emptyRow());
  const [addingNew, setAddingNew] = useState(false);
  const [newRow, setNewRow] = useState<RowState>(emptyRow());
  const [saving, setSaving] = useState(false);
  const [seeding, setSeeding] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params: Record<string, unknown> = { page_size: 200 };
      if (siteId !== undefined) {
        if (siteId) params.site_id = siteId;
      }
      const res = await listHorairesTravail(params);
      const all = res.items ?? [];
      const filtered = siteId ? all.filter((i) => i.site_id === siteId) : all.filter((i) => !i.site_id);
      setItems(filtered);
    } catch {
      setError('Impossible de charger les horaires');
    } finally {
      setLoading(false);
    }
  }, [siteId]);

  useEffect(() => { load(); }, [load]);

  const startEdit = (item: HoraireTravail) => {
    setEditingId(item.id);
    setEditRow(rowFromItem(item));
    setAddingNew(false);
  };

  const cancelEdit = () => { setEditingId(null); };

  const saveEdit = async () => {
    if (!editingId) return;
    setSaving(true);
    try {
      await updateHoraireTravail(editingId, {
        type_horaire: editRow.type_horaire || undefined,
        depart_h1: editRow.depart_h1 || null,
        retour_h1: editRow.retour_h1 || null,
        depart_h2: editRow.depart_h2 || null,
        retour_h2: editRow.retour_h2 || null,
      });
      setEditingId(null);
      await load();
    } catch {
      setError('Erreur lors de la sauvegarde');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Supprimer cet horaire ?')) return;
    try {
      await deleteHoraireTravail(id);
      await load();
    } catch {
      setError('Erreur lors de la suppression');
    }
  };

  const startAdd = () => {
    setAddingNew(true);
    setNewRow(emptyRow());
    setEditingId(null);
  };

  const cancelAdd = () => { setAddingNew(false); };

  const saveNew = async () => {
    if (!newRow.type_horaire.trim()) return;
    setSaving(true);
    try {
      await createHoraireTravail({
        type_horaire: newRow.type_horaire.trim(),
        site_id: siteId ?? null,
        depart_h1: newRow.depart_h1 || null,
        retour_h1: newRow.retour_h1 || null,
        depart_h2: newRow.depart_h2 || null,
        retour_h2: newRow.retour_h2 || null,
      });
      setAddingNew(false);
      await load();
    } catch {
      setError('Erreur lors de la création');
    } finally {
      setSaving(false);
    }
  };

  const handleSeed = async () => {
    setSeeding(true);
    try {
      await seedDefaultHoraires();
      await load();
    } catch {
      setError('Erreur lors de l\'initialisation');
    } finally {
      setSeeding(false);
    }
  };

  const setEdit = (k: keyof RowState, v: string) => setEditRow((r) => ({ ...r, [k]: v }));
  const setNew = (k: keyof RowState, v: string) => setNewRow((r) => ({ ...r, [k]: v }));

  return (
    <div className="flex flex-col gap-3">
      {error && (
        <div className="flex items-center gap-2 rounded-lg bg-error-container/20 px-3 py-2 text-sm text-error">
          <span className="material-symbols-outlined text-sm">error</span>
          {error}
          <button className="ml-auto text-xs underline" onClick={() => setError(null)}>Fermer</button>
        </div>
      )}

      <div className="rounded-xl overflow-hidden border border-outline-variant/30 bg-surface">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-surface-container-low border-b border-outline-variant/20">
              <th className="px-3 py-2.5 text-left text-[10px] font-bold uppercase tracking-widest text-on-surface-variant w-[22%]">
                Shift
              </th>
              <th className="px-3 py-2.5 text-center text-[10px] font-bold uppercase tracking-widest text-on-surface-variant" colSpan={2}>
                Premier Horaire
              </th>
              <th className="px-3 py-2.5 text-center text-[10px] font-bold uppercase tracking-widest text-on-surface-variant" colSpan={2}>
                Deuxième Horaire
              </th>
              <th className="w-16" />
            </tr>
            <tr className="bg-surface-container-lowest border-b border-outline-variant/10 text-[10px] text-on-surface-variant/70">
              <th />
              <th className="px-3 pb-1.5 text-center font-medium">Départ</th>
              <th className="px-3 pb-1.5 text-center font-medium">Retour</th>
              <th className="px-3 pb-1.5 text-center font-medium">Départ</th>
              <th className="px-3 pb-1.5 text-center font-medium">Retour</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={6} className="py-10 text-center text-sm text-on-surface-variant">
                  <span className="material-symbols-outlined text-2xl animate-spin inline-block mb-1">refresh</span>
                  <br />Chargement…
                </td>
              </tr>
            )}

            {!loading && items.length === 0 && !addingNew && (
              <tr>
                <td colSpan={6} className="py-8 text-center">
                  <p className="text-sm text-on-surface-variant mb-3">Aucun horaire défini</p>
                  <button
                    type="button"
                    onClick={handleSeed}
                    disabled={seeding}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-primary bg-primary/10 hover:bg-primary/20 px-3 py-1.5 rounded-lg transition-colors"
                  >
                    <span className="material-symbols-outlined text-sm">auto_fix_high</span>
                    {seeding ? 'Initialisation…' : 'Initialiser les horaires standards'}
                  </button>
                </td>
              </tr>
            )}

            {items.map((item, idx) =>
              editingId === item.id ? (
                <tr key={item.id} className="bg-primary/5 border-b border-outline-variant/20">
                  <td className="px-2 py-2">
                    <input
                      type="text"
                      value={editRow.type_horaire}
                      onChange={(e) => setEdit('type_horaire', e.target.value)}
                      className="w-full h-8 bg-surface rounded-md border border-outline-variant/50 px-2 text-sm font-medium text-on-surface focus:outline-none focus:ring-1 focus:ring-primary/40"
                      placeholder="Nom du poste"
                    />
                  </td>
                  <td className="px-2 py-2"><TimeInput value={editRow.depart_h1} onChange={(v) => setEdit('depart_h1', v)} /></td>
                  <td className="px-2 py-2"><TimeInput value={editRow.retour_h1} onChange={(v) => setEdit('retour_h1', v)} /></td>
                  <td className="px-2 py-2"><TimeInput value={editRow.depart_h2} onChange={(v) => setEdit('depart_h2', v)} /></td>
                  <td className="px-2 py-2"><TimeInput value={editRow.retour_h2} onChange={(v) => setEdit('retour_h2', v)} /></td>
                  <td className="px-2 py-2">
                    <div className="flex items-center gap-1 justify-end">
                      <button
                        type="button"
                        onClick={saveEdit}
                        disabled={saving}
                        className="p-1.5 rounded-lg bg-primary text-on-primary hover:bg-primary/90 transition-colors"
                        title="Enregistrer"
                      >
                        <span className="material-symbols-outlined text-sm">check</span>
                      </button>
                      <button
                        type="button"
                        onClick={cancelEdit}
                        className="p-1.5 rounded-lg bg-surface-container hover:bg-surface-container-high transition-colors text-on-surface-variant"
                        title="Annuler"
                      >
                        <span className="material-symbols-outlined text-sm">close</span>
                      </button>
                    </div>
                  </td>
                </tr>
              ) : (
                <tr key={item.id} className={`border-b border-outline-variant/10 hover:bg-surface-container-low/60 transition-colors ${idx % 2 === 1 ? 'bg-surface-container-lowest/30' : ''}`}>
                  <td className="px-3 py-3 font-semibold text-on-surface">{item.type_horaire}</td>
                  <td className="px-3 py-3 text-center"><TimeDisplay value={item.depart_h1} /></td>
                  <td className="px-3 py-3 text-center"><TimeDisplay value={item.retour_h1} /></td>
                  <td className="px-3 py-3 text-center"><TimeDisplay value={item.depart_h2} /></td>
                  <td className="px-3 py-3 text-center"><TimeDisplay value={item.retour_h2} /></td>
                  <td className="px-3 py-3">
                    <div className="flex items-center gap-1 justify-end">
                      <button
                        type="button"
                        onClick={() => startEdit(item)}
                        className="p-1 rounded hover:bg-surface-container text-on-surface-variant hover:text-on-surface transition-colors"
                        title="Modifier"
                      >
                        <span className="material-symbols-outlined text-[16px]">edit</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDelete(item.id)}
                        className="p-1 rounded hover:bg-error-container/20 text-on-surface-variant hover:text-error transition-colors"
                        title="Supprimer"
                      >
                        <span className="material-symbols-outlined text-[16px]">delete</span>
                      </button>
                    </div>
                  </td>
                </tr>
              )
            )}

            {/* New row */}
            {addingNew && (
              <tr className="bg-green-50/60 border-b border-outline-variant/20">
                <td className="px-2 py-2">
                  <input
                    type="text"
                    value={newRow.type_horaire}
                    onChange={(e) => setNew('type_horaire', e.target.value)}
                    className="w-full h-8 bg-surface rounded-md border border-outline-variant/50 px-2 text-sm font-medium text-on-surface focus:outline-none focus:ring-1 focus:ring-primary/40"
                    placeholder="Nom du poste *"
                    autoFocus
                  />
                </td>
                <td className="px-2 py-2"><TimeInput value={newRow.depart_h1} onChange={(v) => setNew('depart_h1', v)} /></td>
                <td className="px-2 py-2"><TimeInput value={newRow.retour_h1} onChange={(v) => setNew('retour_h1', v)} /></td>
                <td className="px-2 py-2"><TimeInput value={newRow.depart_h2} onChange={(v) => setNew('depart_h2', v)} /></td>
                <td className="px-2 py-2"><TimeInput value={newRow.retour_h2} onChange={(v) => setNew('retour_h2', v)} /></td>
                <td className="px-2 py-2">
                  <div className="flex items-center gap-1 justify-end">
                    <button
                      type="button"
                      onClick={saveNew}
                      disabled={saving || !newRow.type_horaire.trim()}
                      className="p-1.5 rounded-lg bg-green-600 text-white hover:bg-green-700 transition-colors disabled:opacity-40"
                      title="Ajouter"
                    >
                      <span className="material-symbols-outlined text-sm">check</span>
                    </button>
                    <button
                      type="button"
                      onClick={cancelAdd}
                      className="p-1.5 rounded-lg bg-surface-container hover:bg-surface-container-high transition-colors text-on-surface-variant"
                      title="Annuler"
                    >
                      <span className="material-symbols-outlined text-sm">close</span>
                    </button>
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Footer actions */}
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={startAdd}
          disabled={addingNew}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-primary bg-primary/10 hover:bg-primary/20 px-3 py-1.5 rounded-lg transition-colors disabled:opacity-40"
        >
          <span className="material-symbols-outlined text-sm">add</span>
          Ajouter un poste
        </button>

        {items.length > 0 && (
          <button
            type="button"
            onClick={handleSeed}
            disabled={seeding}
            className="inline-flex items-center gap-1.5 text-xs text-on-surface-variant hover:text-on-surface transition-colors"
            title="Ajouter les postes standards manquants"
          >
            <span className="material-symbols-outlined text-sm">auto_fix_high</span>
            {seeding ? 'Initialisation…' : 'Compléter avec les standards'}
          </button>
        )}
      </div>

      <p className="text-[10px] text-on-surface-variant/60 font-sans">
        Ces horaires sont partagés par tous les sites de l'entreprise et s'appliquent aux employés et aux routes véhicules.
      </p>
    </div>
  );
}
