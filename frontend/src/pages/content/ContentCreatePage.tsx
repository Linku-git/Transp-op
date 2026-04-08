import { useState, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useContentStore } from '@/stores/contentStore';
import { ContentForm, type ContentFormData } from './ContentForm';
import { extractApiError } from '@/lib/apiError';

export function ContentCreatePage() {
  const navigate = useNavigate();
  const { createContent } = useContentStore();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const handleSubmit = useCallback(
    async (data: ContentFormData) => {
      setIsSubmitting(true);
      setApiError(null);
      try {
        await createContent(data);
        navigate('/content');
      } catch (err: unknown) {
        setApiError(extractApiError(err, 'Erreur lors de la création'));
      } finally {
        setIsSubmitting(false);
      }
    },
    [createContent, navigate],
  );

  const handleCancel = useCallback(() => {
    navigate('/content');
  }, [navigate]);

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
        <span className="text-on-surface font-medium">Nouveau</span>
      </nav>

      <h1 className="font-display text-2xl font-bold text-on-surface">
        Créer du contenu
      </h1>

      <ContentForm
        onSubmit={handleSubmit}
        onCancel={handleCancel}
        isSubmitting={isSubmitting}
        apiError={apiError}
      />
    </div>
  );
}
