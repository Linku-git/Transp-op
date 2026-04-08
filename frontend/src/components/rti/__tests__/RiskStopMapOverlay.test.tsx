import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { RiskStopMapOverlay } from '../RiskStopMapOverlay';

describe('RiskStopMapOverlay', () => {
  it('renders stop count', () => {
    const stops = [
      { id: '1', stop_name: 'Test', lat: 33.58, lng: -7.63, composite_risk_score: 0.8, is_critical: true, isolation_score: 0.9, lighting_score: 0.2 },
    ];
    render(<RiskStopMapOverlay stops={stops} />);
    expect(screen.getByText('1 arrêts affichés sur la carte')).toBeInTheDocument();
  });

  it('renders critical count', () => {
    const stops = [
      { id: '1', stop_name: 'Critical', lat: 33, lng: -7, composite_risk_score: 0.9, is_critical: true, isolation_score: 0.9, lighting_score: 0.1 },
      { id: '2', stop_name: 'Normal', lat: 33, lng: -7, composite_risk_score: 0.4, is_critical: false, isolation_score: 0.3, lighting_score: 0.7 },
    ];
    render(<RiskStopMapOverlay stops={stops} />);
    expect(screen.getByText(/Critique \(1\)/)).toBeInTheDocument();
    expect(screen.getByText(/Normal \(1\)/)).toBeInTheDocument();
  });

  it('shows critical stop names', () => {
    const stops = [
      { id: '1', stop_name: 'Zone Dangereuse', lat: 33, lng: -7, composite_risk_score: 0.85, is_critical: true, isolation_score: 0.9, lighting_score: 0.1 },
    ];
    render(<RiskStopMapOverlay stops={stops} />);
    expect(screen.getByText('Zone Dangereuse')).toBeInTheDocument();
  });
});
