import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, defaultValue?: string) => defaultValue ?? key,
    i18n: { language: 'fr' },
  }),
}));

const mockData = {
  overview: {
    total_deliveries: 500,
    total_views: 400,
    total_completions: 250,
    view_rate: 80.0,
    completion_rate: 50.0,
    avg_quiz_score: 78.5,
    avg_time_spent_seconds: 180,
    training_hours_recovered: 12.5,
  },
  content_ranking: [
    {
      content_id: '1',
      title: 'Formation sécurité',
      content_type: 'training',
      deliveries: 100,
      views: 80,
      completions: 60,
      avg_quiz_score: 85.0,
      avg_time_seconds: 300,
    },
    {
      content_id: '2',
      title: 'Actualité du mois',
      content_type: 'news',
      deliveries: 200,
      views: 180,
      completions: 120,
      avg_quiz_score: null,
      avg_time_seconds: 60,
    },
  ],
  by_type: {
    news: { deliveries: 200, views: 180, completions: 120 },
    training: { deliveries: 100, views: 80, completions: 60 },
    safety: { deliveries: 150, views: 100, completions: 50 },
    survey: { deliveries: 50, views: 40, completions: 20 },
  },
};

vi.mock('@/api/analytics', () => ({
  getContentAnalytics: vi.fn().mockResolvedValue(mockData),
}));

describe('ContentAnalyticsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders engagement overview KPIs', async () => {
    const { ContentAnalyticsPage } = await import('../ContentAnalyticsPage');
    render(
      <MemoryRouter>
        <ContentAnalyticsPage />
      </MemoryRouter>,
    );

    // Wait for async load
    const heading = await screen.findByText('Engagement Analytics');
    expect(heading).toBeDefined();

    expect(screen.getByText('Vues totales')).toBeDefined();
    expect(screen.getByText('Compléments')).toBeDefined();
    expect(screen.getByText('Score moyen')).toBeDefined();
    expect(screen.getByText('Temps moyen')).toBeDefined();
  });

  it('renders training hours recovered', async () => {
    const { ContentAnalyticsPage } = await import('../ContentAnalyticsPage');
    render(
      <MemoryRouter>
        <ContentAnalyticsPage />
      </MemoryRouter>,
    );

    const hours = await screen.findByText('12.5h');
    expect(hours).toBeDefined();
    expect(screen.getByText('Heures de formation récupérées')).toBeDefined();
  });

  it('renders content ranking table', async () => {
    const { ContentAnalyticsPage } = await import('../ContentAnalyticsPage');
    render(
      <MemoryRouter>
        <ContentAnalyticsPage />
      </MemoryRouter>,
    );

    const title = await screen.findByText('Formation sécurité');
    expect(title).toBeDefined();
    expect(screen.getByText('Actualité du mois')).toBeDefined();
    expect(screen.getByText('Classement par engagement')).toBeDefined();
  });

  it('renders engagement by type section', async () => {
    const { ContentAnalyticsPage } = await import('../ContentAnalyticsPage');
    render(
      <MemoryRouter>
        <ContentAnalyticsPage />
      </MemoryRouter>,
    );

    const section = await screen.findByText('Engagement par type');
    expect(section).toBeDefined();
  });

  it('renders engagement rates', async () => {
    const { ContentAnalyticsPage } = await import('../ContentAnalyticsPage');
    render(
      <MemoryRouter>
        <ContentAnalyticsPage />
      </MemoryRouter>,
    );

    const rates = await screen.findByText("Taux d'engagement");
    expect(rates).toBeDefined();
    expect(screen.getByText('80%')).toBeDefined();
    expect(screen.getByText('50%')).toBeDefined();
  });
});
