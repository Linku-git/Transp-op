import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ViolationAlertList } from '../ViolationAlertList';

describe('ViolationAlertList', () => {
  it('shows empty state when no violations', () => {
    render(<ViolationAlertList violations={[]} />);
    expect(screen.getByText('Aucune violation')).toBeInTheDocument();
  });

  it('renders violations table', () => {
    const violations = [
      {
        id: '1',
        stop_name: 'Arrêt A',
        vehicle_label: 'BUS-001',
        scheduled_time: '08:30',
        wait_seconds: 120,
        severity: 'high' as const,
      },
    ];
    render(<ViolationAlertList violations={violations} />);
    expect(screen.getByText('Arrêt A')).toBeInTheDocument();
    expect(screen.getByText('BUS-001')).toBeInTheDocument();
    expect(screen.getByText('120s')).toBeInTheDocument();
    expect(screen.getByText('Élevé')).toBeInTheDocument();
  });

  it('renders section header', () => {
    render(<ViolationAlertList violations={[]} />);
    expect(screen.getByText('Violations récentes')).toBeInTheDocument();
  });
});
