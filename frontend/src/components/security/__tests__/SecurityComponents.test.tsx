import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ScoreDistributionChart } from '../ScoreDistributionChart';
import { NightShiftCoverage } from '../NightShiftCoverage';
import { IncidentTimeline } from '../IncidentTimeline';
import { EmergencyAlertLog } from '../EmergencyAlertLog';
import { RiskStopMap } from '../RiskStopMap';

describe('ScoreDistributionChart', () => {
  it('renders section title', () => {
    render(<ScoreDistributionChart distribution={{ low: 10, medium: 5, high: 3, critical: 1 }} />);
    expect(screen.getByText('Distribution des scores de sécurité')).toBeInTheDocument();
  });

  it('renders empty state', () => {
    render(<ScoreDistributionChart distribution={{ low: 0, medium: 0, high: 0, critical: 0 }} />);
    expect(screen.getByText('Aucune donnée')).toBeInTheDocument();
  });
});

describe('NightShiftCoverage', () => {
  it('renders optimal coverage', () => {
    render(<NightShiftCoverage coveragePct={95} />);
    expect(screen.getByText('95%')).toBeInTheDocument();
    expect(screen.getByText('Couverture optimale')).toBeInTheDocument();
  });

  it('renders insufficient coverage', () => {
    render(<NightShiftCoverage coveragePct={60} />);
    expect(screen.getByText('60%')).toBeInTheDocument();
    expect(screen.getByText('Couverture insuffisante')).toBeInTheDocument();
  });
});

describe('IncidentTimeline', () => {
  it('renders empty state', () => {
    render(<IncidentTimeline incidents={[]} />);
    expect(screen.getByText('Aucun incident')).toBeInTheDocument();
  });

  it('renders incidents', () => {
    render(
      <IncidentTimeline
        incidents={[
          { id: '1', title: 'Test Incident', description: 'Description', severity: 'high', date: '2026-04-08', type: 'security' },
        ]}
      />,
    );
    expect(screen.getByText('Test Incident')).toBeInTheDocument();
  });
});

describe('EmergencyAlertLog', () => {
  it('renders empty state', () => {
    render(<EmergencyAlertLog alerts={[]} />);
    expect(screen.getByText('Aucune alerte')).toBeInTheDocument();
  });

  it('renders section title', () => {
    render(<EmergencyAlertLog alerts={[]} />);
    expect(screen.getByText("Journal des alertes d'urgence")).toBeInTheDocument();
  });
});

describe('RiskStopMap', () => {
  it('renders stop count', () => {
    const stops = [
      { id: '1', stop_name: 'Stop A', lat: 33, lng: -7, composite_risk_score: 0.8, is_critical: true, isolation_score: 0.9, lighting_score: 0.1, tc_frequency_score: 0.2, employee_perception_avg: 0.3 },
    ];
    render(<RiskStopMap stops={stops} />);
    expect(screen.getByText('1 arrêts sur la carte')).toBeInTheDocument();
    expect(screen.getByText('Stop A')).toBeInTheDocument();
  });
});
