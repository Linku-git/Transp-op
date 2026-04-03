import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { extractApiError } from '@/lib/apiError';
import {
  listConstraints,
  createConstraint,
  updateConstraint,
  deleteConstraint,
} from '@/api/settings';
import { Button } from '@/components/ui/Button';
import type {
  ConstraintParam,
  ConstraintCreate,
  ConstraintUpdate,
} from '@/types/settings';

interface EditingState {
  id: string;
  value: string;
  category: string;
  description: string;
  is_active: boolean;
}

export function ConstraintsPage() {
  const { t } = useTranslation();

  const [constraints, setConstraints] = useState<ConstraintParam[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [editingRow, setEditingRow] = useState<EditingState | null>(null);
  const [savingId, setSavingId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  // New constraint form
  const [showAddForm, setShowAddForm] = useState(false);
  const [newKey, setNewKey] = useState('');
  const [newValue, setNewValue] = useState('');
  const [newCategory, setNewCategory] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  const loadConstraints = useCallback(async (category?: string) => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await listConstraints(category || undefined);
      setConstraints(data);
    } catch (err: unknown) {
      setError(extractApiError(err, 'An error occurred'));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadConstraints(categoryFilter || undefined);
  }, [loadConstraints, categoryFilter]);

  const categories = useMemo(() => {
    const set = new Set<string>();
    for (const c of constraints) {
      if (c.category) set.add(c.category);
    }
    return Array.from(set).sort();
  }, [constraints]);

  const handleStartEdit = useCallback((constraint: ConstraintParam) => {
    setEditingRow({
      id: constraint.id,
      value: constraint.value,
      category: constraint.category,
      description: constraint.description ?? '',
      is_active: constraint.is_active,
    });
  }, []);

  const handleCancelEdit = useCallback(() => {
    setEditingRow(null);
  }, []);

  const handleSaveEdit = useCallback(async () => {
    if (!editingRow) return;

    const original = constraints.find((c) => c.id === editingRow.id);
    if (!original) return;

    const updates: ConstraintUpdate = {};
    if (editingRow.value !== original.value) updates.value = editingRow.value;
    if (editingRow.category !== original.category)
      updates.category = editingRow.category;
    if (editingRow.description !== (original.description ?? ''))
      updates.description = editingRow.description;
    if (editingRow.is_active !== original.is_active)
      updates.is_active = editingRow.is_active;

    if (Object.keys(updates).length === 0) {
      setEditingRow(null);
      return;
    }

    try {
      setSavingId(editingRow.id);
      const updated = await updateConstraint(editingRow.id, updates);
      setConstraints((prev) =>
        prev.map((c) => (c.id === updated.id ? updated : c)),
      );
      setEditingRow(null);
    } catch (err: unknown) {
      setError(extractApiError(err, 'Failed to update constraint'));
    } finally {
      setSavingId(null);
    }
  }, [editingRow, constraints]);

  const handleDelete = useCallback(
    async (constraint: ConstraintParam) => {
      const confirmed = window.confirm(
        t(
          'constraints.delete_confirm',
          'Supprimer la contrainte "{{key}}" ?',
          { key: constraint.key },
        ),
      );
      if (!confirmed) return;

      try {
        setDeletingId(constraint.id);
        await deleteConstraint(constraint.id);
        setConstraints((prev) => prev.filter((c) => c.id !== constraint.id));
      } catch (err: unknown) {
        setError(extractApiError(err, 'Failed to delete constraint'));
      } finally {
        setDeletingId(null);
      }
    },
    [t],
  );

  const handleCreate = useCallback(async () => {
    if (!newKey.trim() || !newValue.trim()) return;

    const data: ConstraintCreate = {
      key: newKey.trim(),
      value: newValue.trim(),
    };
    if (newCategory.trim()) data.category = newCategory.trim();
    if (newDescription.trim()) data.description = newDescription.trim();

    try {
      setIsCreating(true);
      setError(null);
      const created = await createConstraint(data);
      setConstraints((prev) => [created, ...prev]);
      setNewKey('');
      setNewValue('');
      setNewCategory('');
      setNewDescription('');
      setShowAddForm(false);
    } catch (err: unknown) {
      setError(extractApiError(err, 'Failed to create constraint'));
    } finally {
      setIsCreating(false);
    }
  }, [newKey, newValue, newCategory, newDescription]);

  const handleToggleActive = useCallback(
    async (constraint: ConstraintParam) => {
      try {
        setSavingId(constraint.id);
        const updated = await updateConstraint(constraint.id, {
          is_active: !constraint.is_active,
        });
        setConstraints((prev) =>
          prev.map((c) => (c.id === updated.id ? updated : c)),
        );
      } catch (err: unknown) {
        setError(extractApiError(err, 'Failed to toggle constraint'));
      } finally {
        setSavingId(null);
      }
    },
    [],
  );

  const inputClasses =
    'bg-surface-container-high/50 border-none rounded-lg p-2 text-on-surface font-sans text-sm outline-none focus:ring-2 focus:ring-primary/20';

  // Loading state
  if (isLoading && constraints.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <svg
            className="animate-spin h-8 w-8 text-primary"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
          <span className="text-sm font-sans text-on-surface-variant">
            {t('common.loading', 'Chargement...')}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="font-sans text-3xl font-black tracking-tight text-on-surface">
          {t('constraints.title', 'Contraintes')}
        </h1>
        <Button
          variant="primary"
          size="md"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          {showAddForm
            ? t('common.cancel', 'Annuler')
            : t('constraints.add', 'Ajouter une contrainte')}
        </Button>
      </div>

      {/* Category filter */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 mb-6">
        <div className="flex flex-wrap items-end gap-4">
          <div className="w-64">
            <label className="block text-[10px] font-bold uppercase tracking-widest text-outline mb-1.5">
              {t('constraints.filter_category', 'Filtrer par categorie')}
            </label>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="w-full bg-surface-container-high/50 border-none rounded-lg p-3 text-on-surface font-sans text-sm outline-none focus:ring-2 focus:ring-primary/20 appearance-none cursor-pointer"
            >
              <option value="">
                {t('constraints.all_categories', 'Toutes les categories')}
              </option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>
          <p className="text-xs font-sans text-on-surface-variant py-3">
            {t('constraints.count', '{{count}} contrainte(s)', {
              count: constraints.length,
            })}
          </p>
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="bg-error-container rounded-xl p-4 mb-4 flex items-center justify-between">
          <p className="text-error text-sm font-sans">{error}</p>
          <button
            onClick={() => setError(null)}
            className="text-error text-sm font-sans font-medium hover:underline ml-4 cursor-pointer"
          >
            {t('common.dismiss', 'Fermer')}
          </button>
        </div>
      )}

      {/* Add form */}
      {showAddForm && (
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 mb-6">
          <h2 className="text-sm font-bold uppercase tracking-widest text-on-surface-variant mb-4">
            {t('constraints.new_title', 'Nouvelle contrainte')}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] font-bold uppercase tracking-widest text-outline">
                {t('constraints.col_key', 'Cle')} *
              </label>
              <input
                type="text"
                value={newKey}
                onChange={(e) => setNewKey(e.target.value)}
                placeholder="max_vehicles_per_route"
                className={inputClasses}
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] font-bold uppercase tracking-widest text-outline">
                {t('constraints.col_value', 'Valeur')} *
              </label>
              <input
                type="text"
                value={newValue}
                onChange={(e) => setNewValue(e.target.value)}
                placeholder="10"
                className={inputClasses}
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] font-bold uppercase tracking-widest text-outline">
                {t('constraints.col_category', 'Categorie')}
              </label>
              <input
                type="text"
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                placeholder="routing"
                className={inputClasses}
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] font-bold uppercase tracking-widest text-outline">
                {t('constraints.col_description', 'Description')}
              </label>
              <input
                type="text"
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
                placeholder={t(
                  'constraints.desc_placeholder',
                  'Description optionnelle...',
                )}
                className={inputClasses}
              />
            </div>
          </div>
          <div className="flex justify-end">
            <Button
              variant="primary"
              size="md"
              isLoading={isCreating}
              disabled={!newKey.trim() || !newValue.trim()}
              onClick={handleCreate}
            >
              {t('common.create', 'Creer')}
            </Button>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!isLoading && constraints.length === 0 && (
        <div className="flex-1 flex flex-col items-center justify-center">
          <svg
            className="mx-auto mb-3 w-12 h-12 text-primary/30"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75"
            />
          </svg>
          <p className="font-sans text-base font-semibold text-on-surface mb-1">
            {t('constraints.empty_title', 'Aucune contrainte')}
          </p>
          <p className="text-sm font-sans text-on-surface-variant mb-4">
            {t(
              'constraints.empty_desc',
              'Ajoutez des parametres de contrainte pour personnaliser l\'optimisation.',
            )}
          </p>
          <Button
            variant="primary"
            size="md"
            onClick={() => setShowAddForm(true)}
          >
            {t('constraints.add', 'Ajouter une contrainte')}
          </Button>
        </div>
      )}

      {/* Table */}
      {constraints.length > 0 && (
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-auto">
            <table className="w-full text-sm font-sans">
              <thead>
                <tr className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant bg-surface-container-low/50">
                  <th className="text-left py-3 px-4">
                    {t('constraints.col_key', 'Cle')}
                  </th>
                  <th className="text-left py-3 px-4">
                    {t('constraints.col_value', 'Valeur')}
                  </th>
                  <th className="text-left py-3 px-4">
                    {t('constraints.col_category', 'Categorie')}
                  </th>
                  <th className="text-left py-3 px-4">
                    {t('constraints.col_description', 'Description')}
                  </th>
                  <th className="text-left py-3 px-4">
                    {t('constraints.col_active', 'Actif')}
                  </th>
                  <th className="text-right py-3 px-4">
                    {t('constraints.col_actions', 'Actions')}
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/10">
                {constraints.map((constraint) => {
                  const isEditing = editingRow?.id === constraint.id;
                  const isDeleting = deletingId === constraint.id;
                  const isSavingThis = savingId === constraint.id;

                  if (isEditing && editingRow) {
                    return (
                      <tr
                        key={constraint.id}
                        className="bg-primary/5"
                      >
                        <td className="py-3 px-4 text-on-surface font-medium">
                          {constraint.key}
                        </td>
                        <td className="py-3 px-4">
                          <input
                            type="text"
                            value={editingRow.value}
                            onChange={(e) =>
                              setEditingRow({
                                ...editingRow,
                                value: e.target.value,
                              })
                            }
                            className={`${inputClasses} w-full`}
                          />
                        </td>
                        <td className="py-3 px-4">
                          <input
                            type="text"
                            value={editingRow.category}
                            onChange={(e) =>
                              setEditingRow({
                                ...editingRow,
                                category: e.target.value,
                              })
                            }
                            className={`${inputClasses} w-full`}
                          />
                        </td>
                        <td className="py-3 px-4">
                          <input
                            type="text"
                            value={editingRow.description}
                            onChange={(e) =>
                              setEditingRow({
                                ...editingRow,
                                description: e.target.value,
                              })
                            }
                            className={`${inputClasses} w-full`}
                          />
                        </td>
                        <td className="py-3 px-4">
                          <input
                            type="checkbox"
                            checked={editingRow.is_active}
                            onChange={(e) =>
                              setEditingRow({
                                ...editingRow,
                                is_active: e.target.checked,
                              })
                            }
                            className="w-4 h-4 rounded accent-primary cursor-pointer"
                          />
                        </td>
                        <td className="py-3 px-4 text-right">
                          <div className="flex items-center gap-2 justify-end">
                            <Button
                              variant="primary"
                              size="sm"
                              isLoading={isSavingThis}
                              onClick={handleSaveEdit}
                            >
                              {t('common.save', 'Enregistrer')}
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={handleCancelEdit}
                            >
                              {t('common.cancel', 'Annuler')}
                            </Button>
                          </div>
                        </td>
                      </tr>
                    );
                  }

                  return (
                    <tr
                      key={constraint.id}
                      className="transition-colors hover:bg-surface-bright"
                    >
                      <td className="py-3 px-4 text-on-surface font-medium">
                        {constraint.key}
                      </td>
                      <td className="py-3 px-4 text-on-surface tabular-nums">
                        {constraint.value}
                      </td>
                      <td className="py-3 px-4">
                        {constraint.category && (
                          <span className="inline-block rounded-md px-2.5 py-0.5 text-xs font-sans font-medium bg-surface-container-high text-on-surface-variant">
                            {constraint.category}
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-on-surface-variant text-xs">
                        {constraint.description ?? '—'}
                      </td>
                      <td className="py-3 px-4">
                        <button
                          onClick={() => handleToggleActive(constraint)}
                          disabled={isSavingThis}
                          className="cursor-pointer disabled:cursor-not-allowed disabled:opacity-50"
                          aria-label={
                            constraint.is_active
                              ? t('constraints.deactivate', 'Desactiver')
                              : t('constraints.activate', 'Activer')
                          }
                        >
                          <span
                            className={[
                              'inline-block rounded-md px-2.5 py-0.5 text-xs font-sans font-medium',
                              constraint.is_active
                                ? 'bg-green-50 text-green-700'
                                : 'bg-surface-container-high text-on-surface-variant',
                            ].join(' ')}
                          >
                            {constraint.is_active
                              ? t('common.yes', 'Oui')
                              : t('common.no', 'Non')}
                          </span>
                        </button>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center gap-2 justify-end">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleStartEdit(constraint)}
                          >
                            {t('common.edit', 'Modifier')}
                          </Button>
                          <Button
                            variant="danger"
                            size="sm"
                            isLoading={isDeleting}
                            disabled={isDeleting}
                            onClick={() => handleDelete(constraint)}
                          >
                            {t('common.delete', 'Supprimer')}
                          </Button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
