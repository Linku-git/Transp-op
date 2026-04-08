import { create } from 'zustand';
import {
  listContent as apiListContent,
  getContent as apiGetContent,
  createContent as apiCreateContent,
  updateContent as apiUpdateContent,
  deleteContent as apiDeleteContent,
  publishContent as apiPublishContent,
} from '../api/content';
import type {
  Content,
  ContentCreate,
  ContentUpdate,
  ContentListParams,
} from '../types/content';
import type { AxiosError } from 'axios';
import type { ApiError } from '../types';

interface PaginationMeta {
  page: number;
  pages: number;
  total: number;
}

interface ContentState {
  contents: Content[];
  currentContent: Content | null;
  meta: PaginationMeta | null;
  isLoading: boolean;
  error: string | null;

  fetchContents: (params?: ContentListParams) => Promise<void>;
  fetchContent: (id: string) => Promise<void>;
  createContent: (data: ContentCreate) => Promise<Content>;
  updateContent: (id: string, data: ContentUpdate) => Promise<Content>;
  deleteContent: (id: string) => Promise<void>;
  publishContent: (id: string, publish: boolean) => Promise<Content>;
  clearError: () => void;
}

const extractErrorMessage = (err: unknown): string => {
  const axiosError = err as AxiosError<ApiError>;
  const detail = axiosError.response?.data?.detail;
  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((d: { msg?: string }) => d.msg ?? JSON.stringify(d))
      .join('; ');
  }
  if (typeof detail === 'string' && detail.length > 0) return detail;
  return 'An unexpected error occurred';
};

export const useContentStore = create<ContentState>((set, get) => ({
  contents: [],
  currentContent: null,
  meta: null,
  isLoading: false,
  error: null,

  fetchContents: async (params?: ContentListParams) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiListContent(params);
      set({
        contents: response.data,
        meta: { page: response.page, pages: response.pages, total: response.total },
        isLoading: false,
      });
    } catch (err: unknown) {
      set({ error: extractErrorMessage(err), isLoading: false });
    }
  },

  fetchContent: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const content = await apiGetContent(id);
      set({ currentContent: content, isLoading: false });
    } catch (err: unknown) {
      set({ error: extractErrorMessage(err), isLoading: false });
    }
  },

  createContent: async (data: ContentCreate) => {
    set({ isLoading: true, error: null });
    try {
      const content = await apiCreateContent(data);
      const { contents } = get();
      set({ contents: [content, ...contents], isLoading: false });
      return content;
    } catch (err: unknown) {
      set({ error: extractErrorMessage(err), isLoading: false });
      throw err;
    }
  },

  updateContent: async (id: string, data: ContentUpdate) => {
    set({ isLoading: true, error: null });
    try {
      const updated = await apiUpdateContent(id, data);
      const { contents, currentContent } = get();
      set({
        contents: contents.map((c) => (c.id === id ? updated : c)),
        currentContent: currentContent?.id === id ? updated : currentContent,
        isLoading: false,
      });
      return updated;
    } catch (err: unknown) {
      set({ error: extractErrorMessage(err), isLoading: false });
      throw err;
    }
  },

  deleteContent: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await apiDeleteContent(id);
      const { contents, currentContent, meta } = get();
      set({
        contents: contents.filter((c) => c.id !== id),
        currentContent: currentContent?.id === id ? null : currentContent,
        meta: meta ? { ...meta, total: meta.total - 1 } : null,
        isLoading: false,
      });
    } catch (err: unknown) {
      set({ error: extractErrorMessage(err), isLoading: false });
      throw err;
    }
  },

  publishContent: async (id: string, publish: boolean) => {
    set({ isLoading: true, error: null });
    try {
      const updated = await apiPublishContent(id, publish);
      const { contents, currentContent } = get();
      set({
        contents: contents.map((c) => (c.id === id ? updated : c)),
        currentContent: currentContent?.id === id ? updated : currentContent,
        isLoading: false,
      });
      return updated;
    } catch (err: unknown) {
      set({ error: extractErrorMessage(err), isLoading: false });
      throw err;
    }
  },

  clearError: () => {
    set({ error: null });
  },
}));
