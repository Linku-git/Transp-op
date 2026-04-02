import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, defaultValue?: string | Record<string, unknown>, opts?: Record<string, unknown>) => {
      if (typeof defaultValue === 'string') return defaultValue;
      if (typeof defaultValue === 'object' && opts === undefined) {
        // interpolation object passed as second arg
        return key;
      }
      return key;
    },
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

const mockGetReportHistory = vi.fn();
const mockGenerateReport = vi.fn();

vi.mock('@/api/reports', () => ({
  getReportHistory: (...args: unknown[]) => mockGetReportHistory(...args),
  generateReport: (...args: unknown[]) => mockGenerateReport(...args),
}));

const mockHistoryResponse = {
  data: [
    {
      id: 'r-1',
      report_type: 'modal_analysis',
      format: 'pdf',
      params: {},
      file_url: 'http://localhost:8000/exports/r-1.pdf',
      generated_at: '2026-04-02T10:00:00Z',
      generated_by: 'u-1',
    },
    {
      id: 'r-2',
      report_type: 'fleet_utilization',
      format: 'xlsx',
      params: {},
      file_url: null,
      generated_at: '2026-04-01T08:00:00Z',
      generated_by: 'u-1',
    },
  ],
  total: 2,
  page: 1,
  pages: 1,
};

describe('ReportListPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetReportHistory.mockResolvedValue(mockHistoryResponse);
  });

  it('renders the page with table', async () => {
    const { ReportListPage } = await import('../ReportListPage');
    render(
      <MemoryRouter>
        <ReportListPage />
      </MemoryRouter>,
    );

    expect(await screen.findByText('Rapports')).toBeInTheDocument();
    // "Analyse modale" appears in both the filter dropdown and the table row
    const modalItems = screen.getAllByText('Analyse modale');
    expect(modalItems.length).toBeGreaterThanOrEqual(2);
    const fleetItems = screen.getAllByText('Utilisation flotte');
    expect(fleetItems.length).toBeGreaterThanOrEqual(2);
  });

  it('calls getReportHistory with pagination', async () => {
    const { ReportListPage } = await import('../ReportListPage');
    render(
      <MemoryRouter>
        <ReportListPage />
      </MemoryRouter>,
    );

    await screen.findByText('Rapports');
    expect(mockGetReportHistory).toHaveBeenCalledWith(
      expect.objectContaining({ page: 1, page_size: 20 }),
    );
  });
});

describe('ReportTypeSelector', () => {
  it('renders all 7 report types', async () => {
    const { ReportTypeSelector } = await import(
      '@/components/reports/ReportTypeSelector'
    );
    render(<ReportTypeSelector selectedType={null} onSelect={vi.fn()} />);

    expect(screen.getByText('Analyse modale')).toBeInTheDocument();
    expect(screen.getByText('Utilisation flotte')).toBeInTheDocument();
    expect(screen.getByText('Conducteurs volontaires')).toBeInTheDocument();
    expect(screen.getByText('Mobilite RH')).toBeInTheDocument();
    expect(screen.getByText('TCO Financier')).toBeInTheDocument();
    expect(screen.getByText('ROI Financier')).toBeInTheDocument();
    expect(screen.getByText('DPEF/RSE')).toBeInTheDocument();
  });

  it('calls onSelect when a type is clicked', async () => {
    const onSelect = vi.fn();
    const { ReportTypeSelector } = await import(
      '@/components/reports/ReportTypeSelector'
    );
    render(<ReportTypeSelector selectedType={null} onSelect={onSelect} />);

    fireEvent.click(screen.getByText('Analyse modale'));
    expect(onSelect).toHaveBeenCalledWith('modal_analysis');
  });
});

describe('ParameterConfigPanel', () => {
  it('renders format options and generate button', async () => {
    const { ParameterConfigPanel } = await import(
      '@/components/reports/ParameterConfigPanel'
    );
    render(<ParameterConfigPanel onGenerate={vi.fn()} isGenerating={false} />);

    expect(screen.getByText('PDF')).toBeInTheDocument();
    expect(screen.getByText('Excel (.xlsx)')).toBeInTheDocument();
    expect(screen.getByText('Generer le rapport')).toBeInTheDocument();
  });
});

describe('ReportGeneratorPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGenerateReport.mockResolvedValue(new Blob(['test']));
  });

  it('renders the type selector', async () => {
    const { ReportGeneratorPage } = await import('../ReportGeneratorPage');
    render(
      <MemoryRouter>
        <ReportGeneratorPage />
      </MemoryRouter>,
    );

    expect(screen.getByText('Generer un rapport')).toBeInTheDocument();
    expect(screen.getByText('Analyse modale')).toBeInTheDocument();
  });
});
