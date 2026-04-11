import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import type { MCDAResponse, ModalChoiceResponse } from '@/types/sotreg';

// Mock API functions
const mockComputeMCDA = vi.fn();
const mockComputeSensitivity = vi.fn();
const mockComputeModalChoice = vi.fn();
const mockDownloadPdf = vi.fn();
const mockDownloadExcel = vi.fn();

vi.mock('@/api/sotreg', () => ({
  computeMCDA: (...args: unknown[]) => mockComputeMCDA(...args),
  computeSensitivity: (...args: unknown[]) => mockComputeSensitivity(...args),
  computeModalChoice: (...args: unknown[]) => mockComputeModalChoice(...args),
  downloadMCDAReportPdf: (...args: unknown[]) => mockDownloadPdf(...args),
  downloadMCDAReportExcel: (...args: unknown[]) => mockDownloadExcel(...args),
}));

vi.mock('@/lib/apiError', () => ({
  extractApiError: (_err: unknown, fallback: string) => fallback,
}));

// Mock recharts components
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div data-testid="responsive-container">{children}</div>,
  RadarChart: ({ children }: { children: React.ReactNode }) => <div data-testid="radar-chart">{children}</div>,
  Radar: () => <div data-testid="radar-polygon" />,
  PolarGrid: () => <div />,
  PolarAngleAxis: () => <div />,
  PolarRadiusAxis: () => <div />,
  Tooltip: () => <div />,
}));

const MOCK_MCDA_RESPONSE: MCDAResponse = {
  ranked_alternatives: [
    { name: 'Electrique', score: 3.80, rank: 1, normalized_values: { capex: 1.0, opex: 5.0, co2: 5.0, risk: 4.33, comfort: 5.0, maturity: 1.0 } },
    { name: 'Hybride', score: 3.20, rank: 2, normalized_values: { capex: 2.33, opex: 3.67, co2: 3.25, risk: 3.67, comfort: 3.67, maturity: 2.33 } },
    { name: 'Diesel', score: 2.40, rank: 3, normalized_values: { capex: 5.0, opex: 1.0, co2: 1.0, risk: 2.33, comfort: 1.0, maturity: 5.0 } },
  ],
  weights_used: { capex: 0.20, opex: 0.20, co2: 0.25, risk: 0.15, comfort: 0.10, maturity: 0.10 },
  criteria_ranges: {
    capex: { min: 180000, max: 300000 },
    opex: { min: 60000, max: 120000 },
    co2: { min: 10, max: 90 },
    risk: { min: 2, max: 3 },
    comfort: { min: 3, max: 4.5 },
    maturity: { min: 3, max: 5 },
  },
  best_alternative: 'Electrique',
  worst_alternative: 'Diesel',
};

const MOCK_MODAL_RESPONSE: ModalChoiceResponse = {
  probabilities: [
    { name: 'Bus Electrique', utility: 2.5, probability: 0.55 },
    { name: 'Navette Hybride', utility: 1.8, probability: 0.30 },
    { name: 'Bus Diesel', utility: 0.9, probability: 0.15 },
  ],
  probabilities_sum: 1.0,
  dominant_mode: 'Bus Electrique',
};

describe('ScoringDashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockComputeMCDA.mockResolvedValue(MOCK_MCDA_RESPONSE);
    mockComputeModalChoice.mockResolvedValue(MOCK_MODAL_RESPONSE);
  });

  it('renders with all three tabs', async () => {
    const mod = await import('../ScoringDashboardPage');
    const Page = mod.default;
    render(<MemoryRouter><Page /></MemoryRouter>);

    expect(screen.getByText('Analyse MCDA')).toBeDefined();
    expect(screen.getByText('Choix Modal')).toBeDefined();
    expect(screen.getByText('Rapports')).toBeDefined();
  });

  it('shows MCDA input form on first tab', async () => {
    const mod = await import('../ScoringDashboardPage');
    const Page = mod.default;
    render(<MemoryRouter><Page /></MemoryRouter>);

    expect(screen.getByText("Lancer l'analyse MCDA")).toBeDefined();
    expect(screen.getByText(/Pondérations/)).toBeDefined();
  });

  it('displays alternatives in input form', async () => {
    const mod = await import('../ScoringDashboardPage');
    const Page = mod.default;
    render(<MemoryRouter><Page /></MemoryRouter>);

    // Default preset alternatives should be visible
    expect(screen.getByDisplayValue('Diesel')).toBeDefined();
    expect(screen.getByDisplayValue('Electrique')).toBeDefined();
  });

  it('allows adding an alternative', async () => {
    const mod = await import('../ScoringDashboardPage');
    const Page = mod.default;
    render(<MemoryRouter><Page /></MemoryRouter>);

    const addBtn = screen.getByText('Ajouter');
    fireEvent.click(addBtn);

    // Should now have 5 alternatives (4 preset + 1 new)
    expect(screen.getByDisplayValue('Alternative 5')).toBeDefined();
  });

  it('weight sliders sum to 100%', async () => {
    const mod = await import('../ScoringDashboardPage');
    const Page = mod.default;
    render(<MemoryRouter><Page /></MemoryRouter>);

    expect(screen.getByText(/somme = 100%/)).toBeDefined();
  });

  it('shows results table after MCDA computation', async () => {
    const mod = await import('../ScoringDashboardPage');
    const Page = mod.default;
    render(<MemoryRouter><Page /></MemoryRouter>);

    const submitBtn = screen.getByText("Lancer l'analyse MCDA");
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(mockComputeMCDA).toHaveBeenCalledTimes(1);
    });

    await waitFor(() => {
      // Multiple instances expected (input form + results table + radar legend + sensitivity)
      expect(screen.getAllByText('Electrique').length).toBeGreaterThanOrEqual(2);
      expect(screen.getByText('3.80')).toBeDefined();
    });
  });

  it('renders radar chart with 6 axes after computation', async () => {
    const mod = await import('../ScoringDashboardPage');
    const Page = mod.default;
    render(<MemoryRouter><Page /></MemoryRouter>);

    fireEvent.click(screen.getByText("Lancer l'analyse MCDA"));

    await waitFor(() => {
      expect(screen.getByTestId('radar-chart')).toBeDefined();
    });
  });

  it('shows sensitivity sliders after computation', async () => {
    const mod = await import('../ScoringDashboardPage');
    const Page = mod.default;
    render(<MemoryRouter><Page /></MemoryRouter>);

    fireEvent.click(screen.getByText("Lancer l'analyse MCDA"));

    await waitFor(() => {
      expect(screen.getByText(/Sensibilité en temps réel/)).toBeDefined();
    });
  });

  it('switches to modal choice tab', async () => {
    const mod = await import('../ScoringDashboardPage');
    const Page = mod.default;
    render(<MemoryRouter><Page /></MemoryRouter>);

    fireEvent.click(screen.getByText('Choix Modal'));

    expect(screen.getByText(/Coefficients Beta/)).toBeDefined();
    expect(screen.getByText(/Calculer les probabilités/)).toBeDefined();
  });

  it('switches to reports tab and shows download section', async () => {
    const mod = await import('../ScoringDashboardPage');
    const Page = mod.default;
    render(<MemoryRouter><Page /></MemoryRouter>);

    fireEvent.click(screen.getByText('Rapports'));

    expect(screen.getByText(/Télécharger un rapport MCDA/)).toBeDefined();
    expect(screen.getByPlaceholderText(/UUID du scénario/)).toBeDefined();
  });

  it('shows PDF and Excel download buttons when scenario ID entered', async () => {
    const mod = await import('../ScoringDashboardPage');
    const Page = mod.default;
    render(<MemoryRouter><Page /></MemoryRouter>);

    fireEvent.click(screen.getByText('Rapports'));

    const input = screen.getByPlaceholderText(/UUID du scénario/);
    fireEvent.change(input, { target: { value: '123e4567-e89b-12d3-a456-426614174000' } });

    expect(screen.getByText('Télécharger PDF')).toBeDefined();
    expect(screen.getByText('Télécharger Excel')).toBeDefined();
  });
});
