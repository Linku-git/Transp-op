import { useState, useCallback, useEffect, type FormEvent } from 'react';
import { RichTextEditor } from '@/components/content/RichTextEditor';
import { AudienceTargeting } from '@/components/content/AudienceTargeting';
import { CONTENT_TYPE_LABELS, type ContentType, type Content } from '@/types/content';
import { listSites } from '@/api/sites';

interface ContentFormProps {
  initialData?: Content | null;
  onSubmit: (data: ContentFormData) => Promise<void>;
  onCancel: () => void;
  isSubmitting: boolean;
  apiError: string | null;
}

export interface ContentFormData {
  title: string;
  body?: string;
  content_type: ContentType;
  media_url?: string;
  target_sites?: string[];
  target_departments?: string[];
  target_shifts?: string[];
  expires_at?: string;
}

interface FieldErrors {
  title?: string;
}

export function ContentForm({
  initialData,
  onSubmit,
  onCancel,
  isSubmitting,
  apiError,
}: ContentFormProps) {
  const [title, setTitle] = useState(initialData?.title ?? '');
  const [body, setBody] = useState(initialData?.body ?? '');
  const [contentType, setContentType] = useState<ContentType>(
    initialData?.content_type ?? 'news',
  );
  const [mediaUrl, setMediaUrl] = useState(initialData?.media_url ?? '');
  const [targetSites, setTargetSites] = useState<string[]>(
    initialData?.target_sites ?? [],
  );
  const [targetDepartments, setTargetDepartments] = useState<string[]>(
    initialData?.target_departments ?? [],
  );
  const [targetShifts, setTargetShifts] = useState<string[]>(
    initialData?.target_shifts ?? [],
  );
  const [expiresAt, setExpiresAt] = useState(
    initialData?.expires_at ? initialData.expires_at.slice(0, 16) : '',
  );
  const [errors, setErrors] = useState<FieldErrors>({});
  const [showPreview, setShowPreview] = useState(false);
  const [availableSites, setAvailableSites] = useState<
    { id: string; name: string }[]
  >([]);

  useEffect(() => {
    listSites({ page_size: 100 })
      .then((res) => {
        setAvailableSites(
          res.data.map((s: { id: string; name: string }) => ({
            id: s.id,
            name: s.name,
          })),
        );
      })
      .catch(() => {
        /* non-critical */
      });
  }, []);

  const validate = useCallback((): boolean => {
    const e: FieldErrors = {};
    if (!title.trim()) e.title = 'Le titre est requis';
    setErrors(e);
    return Object.keys(e).length === 0;
  }, [title]);

  const handleSubmit = useCallback(
    async (ev: FormEvent) => {
      ev.preventDefault();
      if (!validate()) return;

      const data: ContentFormData = {
        title: title.trim(),
        body: body || undefined,
        content_type: contentType,
        media_url: mediaUrl.trim() || undefined,
        target_sites: targetSites.length > 0 ? targetSites : undefined,
        target_departments:
          targetDepartments.length > 0 ? targetDepartments : undefined,
        target_shifts: targetShifts.length > 0 ? targetShifts : undefined,
        expires_at: expiresAt || undefined,
      };
      await onSubmit(data);
    },
    [
      validate,
      onSubmit,
      title,
      body,
      contentType,
      mediaUrl,
      targetSites,
      targetDepartments,
      targetShifts,
      expiresAt,
    ],
  );

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {apiError && (
        <div className="rounded-lg bg-error-container/30 px-4 py-3 text-sm text-error">
          {apiError}
        </div>
      )}

      {/* Section: Informations */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 space-y-5">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Informations
        </h3>

        {/* Title */}
        <div>
          <label className="block text-xs font-medium text-on-surface-variant mb-1">
            Titre *
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Titre du contenu"
            className={[
              'w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2.5 text-on-surface text-sm outline-none transition-all',
              errors.title
                ? 'ring-1 ring-error/40'
                : 'focus:ring-1 focus:ring-primary/20 focus:bg-surface-container-lowest',
            ].join(' ')}
          />
          {errors.title && (
            <p className="mt-1 text-xs text-error">{errors.title}</p>
          )}
        </div>

        {/* Type */}
        <div>
          <label className="block text-xs font-medium text-on-surface-variant mb-1">
            Type
          </label>
          <select
            value={contentType}
            onChange={(e) => setContentType(e.target.value as ContentType)}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2.5 text-on-surface text-sm outline-none focus:ring-1 focus:ring-primary/20 appearance-none"
          >
            {(Object.entries(CONTENT_TYPE_LABELS) as [ContentType, string][]).map(
              ([val, label]) => (
                <option key={val} value={val}>
                  {label}
                </option>
              ),
            )}
          </select>
        </div>

        {/* Body */}
        <div>
          <label className="block text-xs font-medium text-on-surface-variant mb-1">
            Contenu
          </label>
          <RichTextEditor
            value={body}
            onChange={setBody}
            placeholder="Rédigez le contenu ici..."
          />
        </div>
      </div>

      {/* Section: Media */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 space-y-5">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Média
        </h3>

        <div>
          <label className="block text-xs font-medium text-on-surface-variant mb-1">
            URL du média (image, vidéo, audio)
          </label>
          <input
            type="url"
            value={mediaUrl}
            onChange={(e) => setMediaUrl(e.target.value)}
            placeholder="https://..."
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2.5 text-on-surface text-sm outline-none focus:ring-1 focus:ring-primary/20 focus:bg-surface-container-lowest"
          />
        </div>

        {mediaUrl && (
          <div className="rounded-lg bg-surface-container/50 p-3">
            <p className="text-xs text-on-surface-variant mb-2">Aperçu :</p>
            {mediaUrl.match(/\.(jpg|jpeg|png|gif|webp|svg)$/i) ? (
              <img
                src={mediaUrl}
                alt="Aperçu"
                className="max-h-48 rounded-lg object-cover"
              />
            ) : (
              <a
                href={mediaUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-primary hover:underline"
              >
                {mediaUrl}
              </a>
            )}
          </div>
        )}
      </div>

      {/* Section: Audience */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
        <AudienceTargeting
          targetSites={targetSites}
          targetDepartments={targetDepartments}
          targetShifts={targetShifts}
          onSitesChange={setTargetSites}
          onDepartmentsChange={setTargetDepartments}
          onShiftsChange={setTargetShifts}
          availableSites={availableSites}
        />
      </div>

      {/* Section: Schedule */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 space-y-5">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Planification
        </h3>

        <div>
          <label className="block text-xs font-medium text-on-surface-variant mb-1">
            Date d&apos;expiration
          </label>
          <input
            type="datetime-local"
            value={expiresAt}
            onChange={(e) => setExpiresAt(e.target.value)}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2.5 text-on-surface text-sm outline-none focus:ring-1 focus:ring-primary/20"
          />
        </div>
      </div>

      {/* Preview */}
      {showPreview && (
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
              Aperçu
            </h3>
            <button
              type="button"
              onClick={() => setShowPreview(false)}
              className="text-xs text-on-surface-variant hover:text-on-surface"
            >
              Fermer
            </button>
          </div>
          <h2 className="text-lg font-semibold text-on-surface">{title || 'Sans titre'}</h2>
          <span className="inline-block px-2 py-0.5 rounded-full bg-primary/10 text-primary text-xs font-medium">
            {CONTENT_TYPE_LABELS[contentType]}
          </span>
          {body && (
            <div
              className="prose prose-sm max-w-none text-on-surface"
              dangerouslySetInnerHTML={{ __html: body }}
            />
          )}
          {mediaUrl && (
            <p className="text-xs text-on-surface-variant">
              Média : {mediaUrl}
            </p>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={() => setShowPreview(!showPreview)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-surface-container-lowest text-on-surface text-sm font-medium border border-outline-variant/15 shadow-sm hover:bg-surface-container-low transition-colors"
        >
          <span className="material-symbols-outlined text-[18px]">
            {showPreview ? 'visibility_off' : 'visibility'}
          </span>
          {showPreview ? 'Masquer' : 'Aperçu'}
        </button>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2.5 rounded-lg text-on-surface-variant text-sm font-medium hover:bg-surface-container-high/50 transition-colors"
          >
            Annuler
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-gradient-to-br from-primary to-primary-container text-on-primary text-sm font-medium shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/25 transition-all disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {isSubmitting && (
              <span className="material-symbols-outlined text-[16px] animate-spin">
                progress_activity
              </span>
            )}
            {initialData ? 'Mettre à jour' : 'Créer'}
          </button>
        </div>
      </div>
    </form>
  );
}
