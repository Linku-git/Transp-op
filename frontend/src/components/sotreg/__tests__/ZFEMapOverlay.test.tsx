import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

vi.mock('@vis.gl/react-google-maps', () => ({
  APIProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Map: ({ children }: { children?: React.ReactNode }) => <div data-testid="zfe-map">{children}</div>,
  AdvancedMarker: () => <div data-testid="zfe-marker" />,
  InfoWindow: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Polyline: () => <div data-testid="zfe-polyline" />,
  Pin: () => <div />,
}));

describe('ZFEMapOverlay', () => {
  it('renders map with ZFE data', async () => {
    const { ZFEMapOverlay } = await import('../ZFEMapOverlay');
    render(
      <ZFEMapOverlay
        zfeResults={[
          {
            ligne_id: 'l1',
            ligne_code: 'L001',
            ligne_name: 'Navette Casa Nord',
            origin: {
              lat: 33.6,
              lng: -7.5,
              is_in_zfe: true,
              zone_name: 'ZFE Casablanca',
              restriction_level: 'Crit\'Air 2',
              allowed_crit_air: [0, 1, 2],
            },
            dest: {
              lat: 33.55,
              lng: -7.6,
              is_in_zfe: false,
              zone_name: null,
              restriction_level: null,
              allowed_crit_air: null,
            },
            any_endpoint_in_zfe: true,
            checked_at: '2026-04-10T08:00:00Z',
          },
        ]}
      />,
    );

    expect(screen.getByTestId('zfe-map')).toBeDefined();
  });

  it('renders empty state when no results', async () => {
    const { ZFEMapOverlay } = await import('../ZFEMapOverlay');
    render(<ZFEMapOverlay zfeResults={[]} />);

    expect(screen.getByText(/Aucune donn.e ZFE/i)).toBeDefined();
  });
});
