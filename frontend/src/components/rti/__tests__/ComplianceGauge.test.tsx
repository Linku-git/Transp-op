import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ComplianceGauge } from '../ComplianceGauge';

describe('ComplianceGauge', () => {
  it('renders percentage value', () => {
    render(<ComplianceGauge value={95.5} />);
    expect(screen.getByText('95.5%')).toBeInTheDocument();
  });

  it('renders label', () => {
    render(<ComplianceGauge value={90} label="Test Label" />);
    expect(screen.getByText('Test Label')).toBeInTheDocument();
  });

  it('renders default label', () => {
    render(<ComplianceGauge value={90} />);
    expect(screen.getByText('Conformité RTI')).toBeInTheDocument();
  });
});
