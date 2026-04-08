export type ContentType = 'news' | 'training' | 'safety' | 'survey';

export type ContentStatus = 'draft' | 'published' | 'archived';

export interface Content {
  id: string;
  tenant_id: string;
  title: string;
  body: string | null;
  content_type: ContentType;
  media_url: string | null;
  target_sites: string[] | null;
  target_departments: string[] | null;
  target_shifts: string[] | null;
  published_at: string | null;
  expires_at: string | null;
  created_by: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ContentCreate {
  title: string;
  body?: string;
  content_type?: ContentType;
  media_url?: string;
  target_sites?: string[];
  target_departments?: string[];
  target_shifts?: string[];
  expires_at?: string;
}

export interface ContentUpdate {
  title?: string;
  body?: string;
  content_type?: ContentType;
  media_url?: string;
  target_sites?: string[];
  target_departments?: string[];
  target_shifts?: string[];
  expires_at?: string;
}

export interface ContentListParams {
  content_type?: ContentType;
  is_active?: boolean;
  site_id?: string;
  page?: number;
  page_size?: number;
}

export interface ContentListResponse {
  data: Content[];
  total: number;
  page: number;
  pages: number;
}

export function deriveStatus(content: Content): ContentStatus {
  if (!content.is_active) return 'archived';
  if (content.published_at) return 'published';
  return 'draft';
}

export const CONTENT_TYPE_LABELS: Record<ContentType, string> = {
  news: 'Actualité',
  training: 'Formation',
  safety: 'Sécurité',
  survey: 'Sondage',
};

export const CONTENT_TYPE_ICONS: Record<ContentType, string> = {
  news: 'newspaper',
  training: 'school',
  safety: 'shield',
  survey: 'poll',
};
