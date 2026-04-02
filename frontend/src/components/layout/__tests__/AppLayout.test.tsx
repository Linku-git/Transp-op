import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { AppLayout } from '../AppLayout'

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}))

describe('AppLayout', () => {
  it('renders sidebar and header', () => {
    render(
      <MemoryRouter>
        <AppLayout />
      </MemoryRouter>
    )

    expect(screen.getByText('Transpop')).toBeInTheDocument()
    expect(screen.getByRole('navigation')).toBeInTheDocument()
    expect(screen.getByRole('banner')).toBeInTheDocument()
  })
})
