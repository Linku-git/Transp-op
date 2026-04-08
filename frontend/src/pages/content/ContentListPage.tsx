import { useState, useEffect, useMemo, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useContentStore } from '@/stores/contentStore';
import {
  deriveStatus,
  CONTENT_TYPE_LABELS,
  CONTENT_TYPE_ICONS,
  type ContentType,
  type ContentStatus,
  type Content,
} from '@/types/content';

const PAGE_SIZE = 20;

const STATUS_LABELS: Record<ContentStatus, string> = {
  draft: 'Brouillon',
  published: 'Publié',
  archived: 'Archivé',
};

const STATUS_STYLES: Record<ContentStatus, string> = {
  draft: 'bg-surface-container-high text-on-surface-variant',
  published: 'bg-green-50 text-green-700',
  archived: 'bg-error-container/30 text-error',
};

export function ContentListPage() {
  const navigate = useNavigate();
  const { contents, meta, isLoading, error, fetchContents, deleteContent, publishContent } =
    useContentStore();

  const [page, setPage] = useState(1);
  const [typeFilter, setTypeFilter] = useState<ContentType | ''>('');
  const [statusFilter, setStatusFilter] = useState<ContentStatus | ''>('');
  const [search, setSearch] = useState('');

  useEffect(() => {
    const params: Record<string, unknown> = { page, page_size: PAGE_SIZE };
    if (typeFilter) params.content_type = typeFilter;
    fetchContents(params);
  }, [fetchContents, page, typeFilter]);

  const filtered = useMemo(() => {
    let list = contents;
    if (statusFilter) {
      list = list.filter((c) => deriveStatus(c) === statusFilter);
    }
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter((c) => c.title.toLowerCase().includes(q));
    }
    return list;
  }, [contents, statusFilter, search]);

  const handleDelete = useCallback(
    async (id: string) => {
      if (!confirm('Supprimer ce contenu ?')) return;
      await deleteContent(id);
    },
    [deleteContent],
  );

  const handleTogglePublish = useCallback(
    async (c: Content) => {
      const isPublished = deriveStatus(c) === 'published';
      await publishContent(c.id, !isPublished);
    },
    [publishContent],
  );

  const formatDate = (d: string | null) => {
    if (!d) return '—';
    return new Date(d).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  const formatAudience = (c: Content) => {
    const parts: string[] = [];
    if (c.target_sites?.length) parts.push(`${c.target_sites.length} site(s)`);
    if (c.target_departments?.length)
      parts.push(`${c.target_departments.length} dép.`);
    if (c.target_shifts?.length)
      parts.push(`${c.target_shifts.length} éq.`);
    return parts.length > 0 ? parts.join(', ') : 'Tous';
  };

  /* ── Stats ── */
  const stats = useMemo(() => {
    const total = contents.length;
    const published = contents.filter(
      (c) => deriveStatus(c) === 'published',
    ).length;
    const drafts = contents.filter(
      (c) => deriveStatus(c) === 'draft',
    ).length;
    return { total, published, drafts };
  }, [contents]);

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-on-surface">
            Gestion du contenu
          </h1>
          <p className="text-sm text-on-surface-variant mt-1">
            Créez et gérez le contenu de valorisation des trajets
          </p>
        </div>
        <Link
          to="/content/new"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-gradient-to-br from-primary to-primary-container text-on-primary text-sm font-medium shadow-lg shadow-primary/20 hover:shadow-xl transition-all"
        >
          <span className="material-symbols-outlined text-[18px]">add</span>
          Créer du contenu
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Total', value: stats.total, icon: 'article' },
          { label: 'Publiés', value: stats.published, icon: 'check_circle' },
          { label: 'Brouillons', value: stats.drafts, icon: 'edit_note' },
        ].map((s) => (
          <div
            key={s.label}
            className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 px-5 py-4 flex items-center gap-4"
          >
            <span className="material-symbols-outlined text-2xl text-primary/60">
              {s.icon}
            </span>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                {s.label}
              </p>
              <p className="text-xl font-bold text-on-surface">{s.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant/50 text-[18px]">
            search
          </span>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Rechercher par titre..."
            className="w-full pl-10 pr-4 py-2.5 bg-surface-container-high/50 border-none rounded-lg text-sm text-on-surface outline-none focus:ring-1 focus:ring-primary/20"
          />
        </div>
        <select
          value={typeFilter}
          onChange={(e) => {
            setTypeFilter(e.target.value as ContentType | '');
            setPage(1);
          }}
          className="bg-surface-container-high/50 border-none rounded-lg px-3 py-2.5 text-sm text-on-surface outline-none focus:ring-1 focus:ring-primary/20 appearance-none min-w-[140px]"
        >
          <option value="">Tous les types</option>
          {(
            Object.entries(CONTENT_TYPE_LABELS) as [ContentType, string][]
          ).map(([val, label]) => (
            <option key={val} value={val}>
              {label}
            </option>
          ))}
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as ContentStatus | '')}
          className="bg-surface-container-high/50 border-none rounded-lg px-3 py-2.5 text-sm text-on-surface outline-none focus:ring-1 focus:ring-primary/20 appearance-none min-w-[140px]"
        >
          <option value="">Tous les statuts</option>
          {(
            Object.entries(STATUS_LABELS) as [ContentStatus, string][]
          ).map(([val, label]) => (
            <option key={val} value={val}>
              {label}
            </option>
          ))}
        </select>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-lg bg-error-container/30 px-4 py-3 text-sm text-error">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center py-16 text-on-surface-variant text-sm">
            Chargement...
          </div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 gap-2">
            <span className="material-symbols-outlined text-4xl text-on-surface-variant/40">
              article
            </span>
            <p className="text-sm text-on-surface-variant">Aucun contenu trouvé</p>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="bg-surface-container-low/50">
                <th className="text-left text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-3">
                  Titre
                </th>
                <th className="text-left text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-3">
                  Type
                </th>
                <th className="text-left text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-3">
                  Statut
                </th>
                <th className="text-left text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-3">
                  Publié le
                </th>
                <th className="text-left text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-3">
                  Audience
                </th>
                <th className="text-right text-[10px] font-bold uppercase tracking-widest text-on-surface-variant px-5 py-3">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {filtered.map((c) => {
                const status = deriveStatus(c);
                return (
                  <tr
                    key={c.id}
                    className="hover:bg-surface-bright transition-colors group"
                  >
                    <td className="px-5 py-3.5">
                      <Link
                        to={`/content/${c.id}`}
                        className="text-sm font-medium text-on-surface hover:text-primary transition-colors"
                      >
                        {c.title}
                      </Link>
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="inline-flex items-center gap-1.5 text-xs text-on-surface-variant">
                        <span className="material-symbols-outlined text-[14px]">
                          {CONTENT_TYPE_ICONS[c.content_type]}
                        </span>
                        {CONTENT_TYPE_LABELS[c.content_type]}
                      </span>
                    </td>
                    <td className="px-5 py-3.5">
                      <span
                        className={[
                          'inline-block px-2.5 py-0.5 rounded-full text-xs font-medium',
                          STATUS_STYLES[status],
                        ].join(' ')}
                      >
                        {STATUS_LABELS[status]}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-xs text-on-surface-variant">
                      {formatDate(c.published_at)}
                    </td>
                    <td className="px-5 py-3.5 text-xs text-on-surface-variant">
                      {formatAudience(c)}
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          type="button"
                          onClick={() => navigate(`/content/${c.id}`)}
                          title="Voir"
                          className="inline-flex items-center justify-center w-8 h-8 rounded-md text-on-surface-variant hover:bg-surface-container-high/50 transition-colors"
                        >
                          <span className="material-symbols-outlined text-[18px]">
                            visibility
                          </span>
                        </button>
                        <button
                          type="button"
                          onClick={() => navigate(`/content/${c.id}/edit`)}
                          title="Modifier"
                          className="inline-flex items-center justify-center w-8 h-8 rounded-md text-on-surface-variant hover:bg-surface-container-high/50 transition-colors"
                        >
                          <span className="material-symbols-outlined text-[18px]">
                            edit
                          </span>
                        </button>
                        <button
                          type="button"
                          onClick={() => handleTogglePublish(c)}
                          title={
                            status === 'published' ? 'Dépublier' : 'Publier'
                          }
                          className="inline-flex items-center justify-center w-8 h-8 rounded-md text-on-surface-variant hover:bg-surface-container-high/50 transition-colors"
                        >
                          <span className="material-symbols-outlined text-[18px]">
                            {status === 'published'
                              ? 'unpublished'
                              : 'publish'}
                          </span>
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDelete(c.id)}
                          title="Supprimer"
                          className="inline-flex items-center justify-center w-8 h-8 rounded-md text-error hover:bg-error-container/20 transition-colors"
                        >
                          <span className="material-symbols-outlined text-[18px]">
                            delete
                          </span>
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {meta && meta.pages > 1 && (
        <div className="flex items-center justify-between text-sm text-on-surface-variant">
          <span>
            Page {meta.page} / {meta.pages} ({meta.total} éléments)
          </span>
          <div className="flex gap-2">
            <button
              type="button"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="px-3 py-1.5 rounded-lg bg-surface-container-lowest border border-outline-variant/15 text-sm hover:bg-surface-container-low transition-colors disabled:opacity-40"
            >
              Précédent
            </button>
            <button
              type="button"
              disabled={page >= meta.pages}
              onClick={() => setPage((p) => p + 1)}
              className="px-3 py-1.5 rounded-lg bg-surface-container-lowest border border-outline-variant/15 text-sm hover:bg-surface-container-low transition-colors disabled:opacity-40"
            >
              Suivant
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
