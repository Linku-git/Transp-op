import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, defaultValue?: string) => defaultValue ?? key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

describe('FileUpload', () => {
  it('renders drop zone with label', async () => {
    const { FileUpload } = await import('../FileUpload');
    render(<FileUpload onFile={vi.fn()} label="Upload Excel" description="Drag and drop here" />);

    expect(screen.getByText('Upload Excel')).toBeInTheDocument();
    expect(screen.getByText('Drag and drop here')).toBeInTheDocument();
  });
});
