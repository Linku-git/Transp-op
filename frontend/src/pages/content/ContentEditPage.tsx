import { useState, useCallback, useEffect } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { useContentStore } from '@/stores/contentStore';
import { ContentForm, type ContentFormData } from './ContentForm';
import { extractApiError } from '@/lib/apiError';

export function ContentEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentContent, isLoading, error, fetchContent, updateContent } =
    useContentStore();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  useEffect(() => {
    if (id) fetchContent(id);
  }, [id, fetchContent]);

  const handleSubmit = useCallback(
    async (data: ContentFormData) => {
      if (!id) return;
      setIsSubmitting(true);
      setApiError(null);
      try {
        await updateContent(id, data);
        navigate(`/content/${id}`);
      } catch (err: unknown) {
        setApiError(extractApiError(err, 'Erreur lors de la mise à jour'));
      } finally {
        setIsSubmitting(false);
      }
    },
    [id, updateContent, navigate],
  );

  const handleCancel = useCallback(() => {
    navigate(id ? `/content/${id}` : '/content');
  }, [navigate, id]);

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

  return (
    <div className="flex flex-col gap-6 max-w-3xl">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm text-on-surface-variant">
        <Link to="/content" className="hover:text-primary transition-colors">
          Contenu
        </Link>
        <span className="material-symbols-outlined text-[14px]">
          chevron_right
        </span>
        <Link
          to={`/content/${id}`}
          className="hover:text-primary transition-colors"
        >
          {currentContent.title}
        </Link>
        <span className="material-symbols-outlined text-[14px]">
          chevron_right
        </span>
        <span className="text-on-surface font-medium">Modifier</span>
      </nav>

      <h1 className="font-display text-2xl font-bold text-on-surface">
        Modifier le contenu
      </h1>

      <ContentForm
        initialData={currentContent}
        onSubmit={handleSubmit}
        onCancel={handleCancel}
        isSubmitting={isSubmitting}
        apiError={apiError}
      />
    </div>
  );
}
