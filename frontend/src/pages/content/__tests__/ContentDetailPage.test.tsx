import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, defaultValue?: string) => defaultValue ?? key,
    i18n: { language: 'fr' },
  }),
}));

const mockContent = {
  id: 'abc-123',
  tenant_id: 't1',
  title: 'Article de test',
  body: '<p>Contenu de test</p>',
  content_type: 'news' as const,
  media_url: null,
  target_sites: ['site-1'],
  target_departments: ['IT', 'RH'],
  target_shifts: ['Matin'],
  published_at: '2026-04-08T10:00:00Z',
  expires_at: '2026-05-01T00:00:00Z',
  created_by: 'u1',
  is_active: true,
  created_at: '2026-04-08T09:00:00Z',
  updated_at: '2026-04-08T10:00:00Z',
};

const mockFetchContent = vi.fn();

vi.mock('@/stores/contentStore', () => ({
  useContentStore: () => ({
    currentContent: mockContent,
    isLoading: false,
    error: null,
    fetchContent: mockFetchContent,
    deleteContent: vi.fn(),
    publishContent: vi.fn(),
  }),
}));

describe('ContentDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders content title and type', async () => {
    const { ContentDetailPage } = await import('../ContentDetailPage');
    render(
      <MemoryRouter initialEntries={['/content/abc-123']}>
        <Routes>
          <Route path="/content/:id" element={<ContentDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getAllByText('Article de test').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Actualité')).toBeDefined();
  });

  it('shows published status badge', async () => {
    const { ContentDetailPage } = await import('../ContentDetailPage');
    render(
      <MemoryRouter initialEntries={['/content/abc-123']}>
        <Routes>
          <Route path="/content/:id" element={<ContentDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText('Publié')).toBeDefined();
  });

  it('displays audience targeting info', async () => {
    const { ContentDetailPage } = await import('../ContentDetailPage');
    render(
      <MemoryRouter initialEntries={['/content/abc-123']}>
        <Routes>
          <Route path="/content/:id" element={<ContentDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText('Audience ciblée')).toBeDefined();
    expect(screen.getByText('IT, RH')).toBeDefined();
    expect(screen.getByText('Matin')).toBeDefined();
  });

  it('shows engagement metrics placeholder', async () => {
    const { ContentDetailPage } = await import('../ContentDetailPage');
    render(
      <MemoryRouter initialEntries={['/content/abc-123']}>
        <Routes>
          <Route path="/content/:id" element={<ContentDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText("Métriques d'engagement")).toBeDefined();
  });

  it('renders action buttons', async () => {
    const { ContentDetailPage } = await import('../ContentDetailPage');
    render(
      <MemoryRouter initialEntries={['/content/abc-123']}>
        <Routes>
          <Route path="/content/:id" element={<ContentDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText('Modifier')).toBeDefined();
    expect(screen.getByText('Dépublier')).toBeDefined();
  });

  it('calls fetchContent on mount', async () => {
    const { ContentDetailPage } = await import('../ContentDetailPage');
    render(
      <MemoryRouter initialEntries={['/content/abc-123']}>
        <Routes>
          <Route path="/content/:id" element={<ContentDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(mockFetchContent).toHaveBeenCalledWith('abc-123');
  });
});
