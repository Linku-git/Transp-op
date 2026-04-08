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
  title: 'Contenu existant',
  body: '<p>Corps du contenu</p>',
  content_type: 'news' as const,
  media_url: 'https://example.com/image.jpg',
  target_sites: ['site-1'],
  target_departments: ['RH'],
  target_shifts: ['Matin'],
  published_at: '2026-04-08T10:00:00Z',
  expires_at: null,
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
    updateContent: vi.fn(),
  }),
}));

vi.mock('@/api/sites', () => ({
  listSites: vi.fn().mockResolvedValue({ data: [] }),
}));

vi.mock('@tiptap/react', () => ({
  useEditor: () => ({
    getHTML: () => mockContent.body,
    commands: { setContent: vi.fn() },
    chain: () => ({ focus: () => ({ toggleBold: () => ({ run: vi.fn() }), toggleItalic: () => ({ run: vi.fn() }), toggleBulletList: () => ({ run: vi.fn() }), toggleOrderedList: () => ({ run: vi.fn() }), toggleHeading: () => ({ run: vi.fn() }) }) }),
    isActive: () => false,
  }),
  EditorContent: () => <div data-testid="editor-content" />,
}));

vi.mock('@tiptap/starter-kit', () => ({ default: {} }));
vi.mock('@tiptap/extension-placeholder', () => ({
  default: { configure: () => ({}) },
}));

describe('ContentEditPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('loads content and pre-fills form', async () => {
    const { ContentEditPage } = await import('../ContentEditPage');
    render(
      <MemoryRouter initialEntries={['/content/abc-123/edit']}>
        <Routes>
          <Route path="/content/:id/edit" element={<ContentEditPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText('Modifier le contenu')).toBeDefined();
    expect(mockFetchContent).toHaveBeenCalledWith('abc-123');
  });

  it('pre-fills title from existing content', async () => {
    const { ContentEditPage } = await import('../ContentEditPage');
    render(
      <MemoryRouter initialEntries={['/content/abc-123/edit']}>
        <Routes>
          <Route path="/content/:id/edit" element={<ContentEditPage />} />
        </Routes>
      </MemoryRouter>,
    );

    const titleInput = screen.getByPlaceholderText('Titre du contenu') as HTMLInputElement;
    expect(titleInput.value).toBe('Contenu existant');
  });

  it('shows breadcrumb with content title', async () => {
    const { ContentEditPage } = await import('../ContentEditPage');
    render(
      <MemoryRouter initialEntries={['/content/abc-123/edit']}>
        <Routes>
          <Route path="/content/:id/edit" element={<ContentEditPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText('Contenu existant')).toBeDefined();
    expect(screen.getByText('Modifier')).toBeDefined();
  });
});
