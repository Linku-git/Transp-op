import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import type { WeatherForecast, WeatherSuggestions } from '@/types/scenario';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (_key: string, defaultValue?: string) => defaultValue ?? _key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

const mockForecasts: WeatherForecast[] = [
  {
    id: 'wf-1',
    site_id: 'site-1',
    date: '2026-04-02',
    condition_summary: 'Clear',
    precipitation_mm: 0,
    temp_min_c: 14,
    temp_max_c: 26,
    wind_kph: 12,
  },
  {
    id: 'wf-2',
    site_id: 'site-1',
    date: '2026-04-03',
    condition_summary: 'Rain',
    precipitation_mm: 8.5,
    temp_min_c: 10,
    temp_max_c: 18,
    wind_kph: 25,
  },
  {
    id: 'wf-3',
    site_id: 'site-1',
    date: '2026-04-04',
    condition_summary: 'Clouds',
    precipitation_mm: 1.2,
    temp_min_c: 12,
    temp_max_c: 20,
    wind_kph: 15,
  },
];

const mockSuggestions: WeatherSuggestions = {
  site_id: 'site-1',
  suggestions: [
    {
      date: '2026-04-03',
      condition_summary: 'Rain',
      suggested_condition_type: 'rain',
      reason: 'Heavy rain expected',
    },
  ],
};

const mockGetWeatherForecasts = vi.fn();
const mockGetWeatherSuggestions = vi.fn();
const mockRefreshWeather = vi.fn();

vi.mock('@/api/scenarios', () => ({
  getWeatherForecasts: (...args: unknown[]) => mockGetWeatherForecasts(...args),
  getWeatherSuggestions: (...args: unknown[]) => mockGetWeatherSuggestions(...args),
  refreshWeather: (...args: unknown[]) => mockRefreshWeather(...args),
}));

describe('WeatherWidget', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetWeatherForecasts.mockResolvedValue(mockForecasts);
    mockGetWeatherSuggestions.mockResolvedValue(mockSuggestions);
    mockRefreshWeather.mockResolvedValue({ site_id: 'site-1', forecasts_updated: 3 });
  });

  it('shows empty state when no siteId is provided', async () => {
    const { WeatherWidget } = await import('../WeatherWidget');
    render(<WeatherWidget siteId="" />);

    expect(screen.getByText('Select a site to view weather forecast')).toBeInTheDocument();
  });

  it('renders forecast data for a selected site', async () => {
    const { WeatherWidget } = await import('../WeatherWidget');
    render(<WeatherWidget siteId="site-1" />);

    await waitFor(() => {
      expect(mockGetWeatherForecasts).toHaveBeenCalledWith('site-1');
    });

    // Should display temperature values (26° / 14° rendered in nested elements)
    await waitFor(() => {
      expect(screen.getByText(/26/)).toBeInTheDocument();
    });

    // Should show the title
    expect(screen.getByText('Weather Forecast')).toBeInTheDocument();
  });

  it('displays condition summaries', async () => {
    const { WeatherWidget } = await import('../WeatherWidget');
    render(<WeatherWidget siteId="site-1" />);

    await waitFor(() => {
      expect(screen.getByText('Clear')).toBeInTheDocument();
    });
    expect(screen.getByText('Rain')).toBeInTheDocument();
    expect(screen.getByText('Clouds')).toBeInTheDocument();
  });

  it('displays precipitation values', async () => {
    const { WeatherWidget } = await import('../WeatherWidget');
    render(<WeatherWidget siteId="site-1" />);

    await waitFor(() => {
      expect(screen.getByText(/8\.5 mm/)).toBeInTheDocument();
    });
  });

  it('shows scenario suggestion chip for matching dates', async () => {
    const { WeatherWidget } = await import('../WeatherWidget');
    render(<WeatherWidget siteId="site-1" />);

    await waitFor(() => {
      expect(screen.getByText('rain')).toBeInTheDocument();
    });
  });

  it('calls onCreateScenario when Apply button is clicked', async () => {
    const user = userEvent.setup();
    const onCreateScenario = vi.fn();
    const { WeatherWidget } = await import('../WeatherWidget');
    render(<WeatherWidget siteId="site-1" onCreateScenario={onCreateScenario} />);

    await waitFor(() => {
      expect(screen.getByText('Apply')).toBeInTheDocument();
    });

    await user.click(screen.getByText('Apply'));
    expect(onCreateScenario).toHaveBeenCalledWith('rain');
  });

  it('shows error state when API fails', async () => {
    mockGetWeatherForecasts.mockRejectedValue(new Error('Network error'));
    const { WeatherWidget } = await import('../WeatherWidget');
    render(<WeatherWidget siteId="site-1" />);

    await waitFor(() => {
      expect(screen.getByText('Unable to load weather data')).toBeInTheDocument();
    });

    expect(screen.getByText('Retry')).toBeInTheDocument();
  });

  it('shows no data state when forecasts are empty', async () => {
    mockGetWeatherForecasts.mockResolvedValue([]);
    mockGetWeatherSuggestions.mockResolvedValue({ site_id: 'site-1', suggestions: [] });
    const { WeatherWidget } = await import('../WeatherWidget');
    render(<WeatherWidget siteId="site-1" />);

    await waitFor(() => {
      expect(screen.getByText('No forecast data available')).toBeInTheDocument();
    });
  });

  it('calls refreshWeather when refresh button is clicked', async () => {
    const user = userEvent.setup();
    const { WeatherWidget } = await import('../WeatherWidget');
    render(<WeatherWidget siteId="site-1" />);

    await waitFor(() => {
      expect(screen.getByText('Weather Forecast')).toBeInTheDocument();
    });

    // Wait for initial load to complete
    await waitFor(() => {
      expect(screen.getByText('Clear')).toBeInTheDocument();
    });

    const refreshButton = screen.getByTitle('Refresh');
    await user.click(refreshButton);

    await waitFor(() => {
      expect(mockRefreshWeather).toHaveBeenCalledWith('site-1');
    });
  });

  it('displays wind speed values', async () => {
    const { WeatherWidget } = await import('../WeatherWidget');
    render(<WeatherWidget siteId="site-1" />);

    await waitFor(() => {
      expect(screen.getByText(/25 km\/h/)).toBeInTheDocument();
    });
  });
});
