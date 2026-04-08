import { useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useContentStore } from '@/stores/contentStore';
import {
  deriveStatus,
  CONTENT_TYPE_LABELS,
  CONTENT_TYPE_ICONS,
  type ContentStatus,
} from '@/types/content';

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

export function ContentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const {
    currentContent,
    isLoading,
    error,
    fetchContent,
    deleteContent,
    publishContent,
  } = useContentStore();

  useEffect(() => {
    if (id) fetchContent(id);
  }, [id, fetchContent]);

  const handleDelete = useCallback(async () => {
    if (!id || !confirm('Supprimer ce contenu ?')) return;
    await deleteContent(id);
    navigate('/content');
  }, [id, deleteContent, navigate]);

  const handleTogglePublish = useCallback(async () => {
    if (!currentContent) return;
    const isPublished = deriveStatus(currentContent) === 'published';
    await publishContent(currentContent.id, !isPublished);
  }, [currentContent, publishContent]);

  const formatDate = (d: string | null) => {
    if (!d) return '—';
    return new Date(d).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16 text-on-surface-variant text-sm">
        Chargement...
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg bg-error-container/30 px-4 py-3 text-sm text-error">
        {error}
      </div>
    );
  }

  if (!currentContent) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-2">
        <span className="material-symbols-outlined text-4xl text-on-surface-variant/40">
          error
        </span>
        <p className="text-sm text-on-surface-variant">Contenu introuvable</p>
        <Link to="/content" className="text-sm text-primary hover:underline">
          Retour à la liste
        </Link>
      </div>
    );
  }

  const status = deriveStatus(currentContent);

  return (
    <div className="flex flex-col gap-6 max-w-4xl">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm text-on-surface-variant">
        <Link to="/content" className="hover:text-primary transition-colors">
          Contenu
        </Link>
        <span className="material-symbols-outlined text-[14px]">
          chevron_right
        </span>
        <span className="text-on-surface font-medium">
          {currentContent.title}
        </span>
      </nav>

      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <h1 className="font-display text-2xl font-bold text-on-surface">
            {currentContent.title}
          </h1>
          <div className="flex items-center gap-3 mt-2">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-primary/10 text-primary text-xs font-medium">
              <span className="material-symbols-outlined text-[14px]">
                {CONTENT_TYPE_ICONS[currentContent.content_type]}
              </span>
              {CONTENT_TYPE_LABELS[currentContent.content_type]}
            </span>
            <span
              className={[
                'inline-block px-2.5 py-0.5 rounded-full text-xs font-medium',
                STATUS_STYLES[status],
              ].join(' ')}
            >
              {STATUS_LABELS[status]}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleTogglePublish}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-surface-container-lowest text-on-surface text-sm font-medium border border-outline-variant/15 shadow-sm hover:bg-surface-container-low transition-colors"
          >
            <span className="material-symbols-outlined text-[18px]">
              {status === 'published' ? 'unpublished' : 'publish'}
            </span>
            {status === 'published' ? 'Dépublier' : 'Publier'}
          </button>
          <Link
            to={`/content/${id}/edit`}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-gradient-to-br from-primary to-primary-container text-on-primary text-sm font-medium shadow-lg shadow-primary/20 hover:shadow-xl transition-all"
          >
            <span className="material-symbols-outlined text-[18px]">edit</span>
            Modifier
          </Link>
          <button
            type="button"
            onClick={handleDelete}
            className="inline-flex items-center justify-center w-10 h-10 rounded-lg text-error hover:bg-error-container/20 transition-colors"
            title="Supprimer"
          >
            <span className="material-symbols-outlined text-[20px]">
              delete
            </span>
          </button>
        </div>
      </div>

      {/* Content body */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 space-y-5">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Contenu
        </h3>
        {currentContent.body ? (
          <div
            className="prose prose-sm max-w-none text-on-surface"
            dangerouslySetInnerHTML={{ __html: currentContent.body }}
          />
        ) : (
          <p className="text-sm text-on-surface-variant italic">
            Aucun contenu rédigé
          </p>
        )}
      </div>

      {/* Media */}
      {currentContent.media_url && (
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 space-y-3">
          <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
            Média
          </h3>
          {currentContent.media_url.match(/\.(jpg|jpeg|png|gif|webp|svg)$/i) ? (
            <img
              src={currentContent.media_url}
              alt="Média"
              className="max-h-64 rounded-lg object-cover"
            />
          ) : (
            <a
              href={currentContent.media_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-primary hover:underline"
            >
              {currentContent.media_url}
            </a>
          )}
        </div>
      )}

      {/* Details grid */}
      <div className="grid grid-cols-2 gap-4">
        {/* Audience */}
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 space-y-3">
          <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
            Audience ciblée
          </h3>
          <div className="space-y-2">
            <InfoRow
              label="Sites"
              value={
                currentContent.target_sites?.length
                  ? currentContent.target_sites.join(', ')
                  : 'Tous'
              }
            />
            <InfoRow
              label="Départements"
              value={
                currentContent.target_departments?.length
                  ? currentContent.target_departments.join(', ')
                  : 'Tous'
              }
            />
            <InfoRow
              label="Équipes"
              value={
                currentContent.target_shifts?.length
                  ? currentContent.target_shifts.join(', ')
                  : 'Toutes'
              }
            />
          </div>
        </div>

        {/* Dates */}
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 space-y-3">
          <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
            Dates
          </h3>
          <div className="space-y-2">
            <InfoRow label="Créé le" value={formatDate(currentContent.created_at)} />
            <InfoRow label="Mis à jour" value={formatDate(currentContent.updated_at)} />
            <InfoRow label="Publié le" value={formatDate(currentContent.published_at)} />
            <InfoRow label="Expire le" value={formatDate(currentContent.expires_at)} />
          </div>
        </div>
      </div>

      {/* Engagement metrics placeholder */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">
          Métriques d&apos;engagement
        </h3>
        <div className="flex items-center justify-center py-8 gap-2 text-on-surface-variant/50">
          <span className="material-symbols-outlined text-2xl">analytics</span>
          <p className="text-sm">
            Les métriques d&apos;engagement seront disponibles après la session 69
          </p>
        </div>
      </div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-4">
      <span className="text-xs text-on-surface-variant">{label}</span>
      <span className="text-sm text-on-surface text-right">{value}</span>
    </div>
  );
}
