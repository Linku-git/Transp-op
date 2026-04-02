import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (_key: string, defaultValue?: string) => defaultValue ?? _key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

const mockGetSettings = vi.fn();
const mockUpdateSettings = vi.fn();

vi.mock('@/api/settings', () => ({
  getSettings: (...args: unknown[]) => mockGetSettings(...args),
  updateSettings: (...args: unknown[]) => mockUpdateSettings(...args),
}));

const mockSettings = {
  id: 'set-1',
  tenant_id: 't1',
  meeting_radius_meters: 500,
  max_walking_distance_meters: 800,
  max_route_duration_seconds: 3600,
  fuel_cost_per_liter: 12.5,
  fuel_consumption_l_per_100km: 8.0,
  co2_kg_per_liter: 2.31,
  rti_threshold_minutes: 15,
  night_mode_start: '22:00',
  night_mode_end: '06:00',
  min_night_group_size: 3,
  created_at: '2026-04-01T00:00:00Z',
  updated_at: '2026-04-01T00:00:00Z',
};

describe('SettingsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetSettings.mockResolvedValue(mockSettings);
    mockUpdateSettings.mockResolvedValue(mockSettings);
  });

  it('renders the page heading', async () => {
    const { SettingsPage } = await import('../SettingsPage');
    render(<SettingsPage />);

    expect(await screen.findByText('Parametres')).toBeInTheDocument();
  });

  it('renders the Save button', async () => {
    const { SettingsPage } = await import('../SettingsPage');
    render(<SettingsPage />);

    await screen.findByText('Parametres');
    const saveButtons = screen.getAllByText('Enregistrer');
    expect(saveButtons.length).toBeGreaterThanOrEqual(1);
  });

  it('calls getSettings on mount', async () => {
    const { SettingsPage } = await import('../SettingsPage');
    render(<SettingsPage />);

    await screen.findByText('Parametres');
    expect(mockGetSettings).toHaveBeenCalled();
  });

  it('renders section headings', async () => {
    const { SettingsPage } = await import('../SettingsPage');
    render(<SettingsPage />);

    expect(
      await screen.findByText("Parametres d'optimisation"),
    ).toBeInTheDocument();
    expect(screen.getByText('Parametres de cout')).toBeInTheDocument();
    expect(
      screen.getByText('Information Temps Reel (RTI)'),
    ).toBeInTheDocument();
    expect(screen.getByText('Mode Nuit')).toBeInTheDocument();
  });

  it('renders field labels', async () => {
    const { SettingsPage } = await import('../SettingsPage');
    render(<SettingsPage />);

    expect(
      await screen.findByText('Rayon de rencontre (m)'),
    ).toBeInTheDocument();
    expect(
      screen.getByText('Cout du carburant (MAD/L)'),
    ).toBeInTheDocument();
    expect(screen.getByText('Seuil RTI (min)')).toBeInTheDocument();
    expect(screen.getByText('Debut mode nuit')).toBeInTheDocument();
  });

  it('shows error banner when API fails', async () => {
    mockGetSettings.mockRejectedValue({
      response: { data: { detail: 'Server error' } },
    });
    const { SettingsPage } = await import('../SettingsPage');
    render(<SettingsPage />);

    expect(await screen.findByText('Server error')).toBeInTheDocument();
  });
});
