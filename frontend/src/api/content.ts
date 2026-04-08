import { api } from './client';
import type {
  Content,
  ContentCreate,
  ContentUpdate,
  ContentListParams,
  ContentListResponse,
} from '../types/content';

const BASE = '/api/v1/content';

export const listContent = async (
  params: ContentListParams = {},
): Promise<ContentListResponse> => {
  const response = await api.get<ContentListResponse>(BASE, { params });
  return response.data;
};

export const getContent = async (id: string): Promise<Content> => {
  const response = await api.get<Content>(`${BASE}/${id}`);
  return response.data;
};

export const createContent = async (data: ContentCreate): Promise<Content> => {
  const response = await api.post<Content>(BASE, data);
  return response.data;
};

export const updateContent = async (
  id: string,
  data: ContentUpdate,
): Promise<Content> => {
  const response = await api.put<Content>(`${BASE}/${id}`, data);
  return response.data;
};

export const deleteContent = async (id: string): Promise<void> => {
  await api.delete(`${BASE}/${id}`);
};

export const publishContent = async (
  id: string,
  publish: boolean = true,
): Promise<Content> => {
  const response = await api.post<Content>(
    `${BASE}/${id}/publish`,
    null,
    { params: { publish } },
  );
  return response.data;
};
