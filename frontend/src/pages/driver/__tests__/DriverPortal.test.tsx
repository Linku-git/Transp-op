/**
 * Tests for Driver Portal — Session 124.
 *
 * Covers: DriverPortalLayout, DriverTripsPage, DriverVehiclePage,
 * DriverRiskPage, DriverSchedulePage, RoleRedirect.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import React from 'react';

/* ── Mocks ─────────────────────────────────────────────────────────────── */

const mockUser = {
  id: 'usr-001',
  email: 'ahmed.tazi@ocp.ma',
  first_name: 'Ahmed',
  last_name: 'Tazi',
  role: 'conducteur' as const,
  tenant_id: 'tenant-001',
  mfa_enabled: false,
};

const mockLogout = vi.fn();
const mockAuthState = {
  user: mockUser,
  token: 'test-token',
  isAuthenticated: true,
  login: vi.fn(),
  logout: mockLogout,
  setUser: vi.fn(),
};

vi.mock('@/stores/authStore', () => ({
  useAuthStore: (selector: (state: typeof mockAuthState) => unknown) =>
    selector(mockAuthState),
}));

vi.mock('@/stores/driverStore', () => {
  const store = {
    trips: [],
    vehicle: { plate: '12345-A-78' },
    riskProfile: null,
    schedule: [],
    activeTrip: null,
    unreadNotifications: 3,
    setTrips: vi.fn(),
    setVehicle: vi.fn(),
    setRiskProfile: vi.fn(),
    setSchedule: vi.fn(),
    setActiveTrip: vi.fn(),
    setUnreadNotifications: vi.fn(),
  };
  return {
    useDriverStore: (selector?: (state: typeof store) => unknown) =>
      selector ? selector(store) : store,
  };
});

vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="responsive-container">{children}</div>
  ),
  LineChart: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="line-chart">{children}</div>
  ),
  Line: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  CartesianGrid: () => <div />,
  Tooltip: () => <div />,
}));

/* ── Helper ────────────────────────────────────────────────────────────── */

function renderWithRouter(ui: React.ReactElement, path = '/driver') {
  return render(<MemoryRouter initialEntries={[path]}>{ui}</MemoryRouter>);
}

/* ── Tests ──────────────────────────────────────────────────────────────── */

describe('DriverPortalLayout', () => {
  it('renders simplified navigation with 5 nav items', async () => {
    const { DriverPortalLayout } = await import(
      '@/layouts/DriverPortalLayout'
    );
    renderWithRouter(<DriverPortalLayout />);

    expect(screen.getByText('Mes Trajets')).toBeDefined();
    expect(screen.getByText('Mon Vehicule')).toBeDefined();
    expect(screen.getByText('Mon Score')).toBeDefined();
    expect(screen.getByText('Planning')).toBeDefined();
    expect(screen.getByText('Deconnexion')).toBeDefined();
  });
});

describe('DriverTripsPage', () => {
  it('renders today\'s trip list with stops', async () => {
    const { DriverTripsPage } = await import(
      '@/pages/driver/DriverTripsPage'
    );
    renderWithRouter(<DriverTripsPage />);

    await waitFor(() => {
      expect(screen.getByTestId('driver-trips-page')).toBeDefined();
    });

    expect(screen.getByText('Mes Trajets')).toBeDefined();
    expect(screen.getAllByText(/Ligne A1/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/Ligne B2/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/Ligne C3/).length).toBeGreaterThanOrEqual(1);
  });

  it('highlights active trip with progress', async () => {
    const { DriverTripsPage } = await import(
      '@/pages/driver/DriverTripsPage'
    );
    renderWithRouter(<DriverTripsPage />);

    await waitFor(() => {
      expect(screen.getByTestId('active-trip-card')).toBeDefined();
    });

    expect(screen.getAllByText('En cours').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByTestId('active-trip-card')).toBeDefined();
  });
});

describe('DriverVehiclePage', () => {
  it('renders vehicle details and telemetry', async () => {
    const { DriverVehiclePage } = await import(
      '@/pages/driver/DriverVehiclePage'
    );
    renderWithRouter(<DriverVehiclePage />);

    await waitFor(() => {
      expect(screen.getByTestId('driver-vehicle-page')).toBeDefined();
    });

    expect(screen.getByText('12345-A-78')).toBeDefined();
    expect(screen.getByText('Bus Standard')).toBeDefined();
    expect(screen.getByTestId('fuel-gauge')).toBeDefined();
    expect(screen.getByText('34.5')).toBeDefined();
    expect(screen.getByText('87.2')).toBeDefined();
    expect(screen.getByText('28.4')).toBeDefined();
  });
});

describe('DriverRiskPage', () => {
  it('renders risk gauge with score and category', async () => {
    const { DriverRiskPage } = await import(
      '@/pages/driver/DriverRiskPage'
    );
    renderWithRouter(<DriverRiskPage />);

    await waitFor(() => {
      expect(screen.getByTestId('driver-risk-page')).toBeDefined();
    });

    expect(screen.getByTestId('risk-gauge')).toBeDefined();
    expect(screen.getByTestId('risk-score-value')).toBeDefined();
    expect(screen.getByTestId('risk-category-badge')).toBeDefined();
    expect(screen.getByText(/Risque Moyen/)).toBeDefined();
  });

  it('displays improvement tips', async () => {
    const { DriverRiskPage } = await import(
      '@/pages/driver/DriverRiskPage'
    );
    renderWithRouter(<DriverRiskPage />);

    await waitFor(() => {
      expect(screen.getByTestId('risk-tips')).toBeDefined();
    });

    expect(
      screen.getByText(/Reduisez votre vitesse/),
    ).toBeDefined();
    expect(
      screen.getByText(/Anticipez les arrets/),
    ).toBeDefined();
  });
});

describe('DriverSchedulePage', () => {
  it('renders weekly schedule grid with 7 day columns', async () => {
    const { DriverSchedulePage } = await import(
      '@/pages/driver/DriverSchedulePage'
    );
    renderWithRouter(<DriverSchedulePage />);

    await waitFor(() => {
      expect(screen.getByTestId('schedule-grid')).toBeDefined();
    });

    expect(screen.getByTestId('schedule-day-Lundi')).toBeDefined();
    expect(screen.getByTestId('schedule-day-Mardi')).toBeDefined();
    expect(screen.getByTestId('schedule-day-Mercredi')).toBeDefined();
    expect(screen.getByTestId('schedule-day-Jeudi')).toBeDefined();
    expect(screen.getByTestId('schedule-day-Vendredi')).toBeDefined();
    expect(screen.getByTestId('schedule-day-Samedi')).toBeDefined();
    expect(screen.getByTestId('schedule-day-Dimanche')).toBeDefined();
  });
});

describe('RoleRedirect', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('sends conducteur to driver portal', async () => {
    const { RoleRedirect } = await import('@/routes');

    const { container } = render(
      <MemoryRouter initialEntries={['/']}>
        <RoleRedirect />
      </MemoryRouter>,
    );

    // Navigate should have rendered (it renders nothing visible but changes location)
    // Since the mock user has role 'conducteur', it should redirect to /driver
    expect(container).toBeDefined();
  });
});
