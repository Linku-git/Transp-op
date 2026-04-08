import { api } from './client';

export interface EngagementOverview {
  total_deliveries: number;
  total_views: number;
  total_completions: number;
  view_rate: number;
  completion_rate: number;
  avg_quiz_score: number | null;
  avg_time_spent_seconds: number | null;
  training_hours_recovered: number;
}

export interface ContentRankingItem {
  content_id: string;
  title: string;
  content_type: string;
  deliveries: number;
  views: number;
  completions: number;
  avg_quiz_score: number | null;
  avg_time_seconds: number | null;
}

export interface TypeStats {
  deliveries: number;
  views: number;
  completions: number;
}

export interface AnalyticsResponse {
  overview: EngagementOverview;
  content_ranking: ContentRankingItem[];
  by_type: Record<string, TypeStats>;
}

export const getContentAnalytics = async (): Promise<AnalyticsResponse> => {
  const response = await api.get<AnalyticsResponse>('/api/v1/content/analytics');
  return response.data;
};
