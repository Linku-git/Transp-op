import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { createMemoryRouter, RouterProvider } from 'react-router-dom'

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'app.name': 'Transpop',
        'nav.dashboard': 'Tableau de bord',
        'nav.sites': 'Sites',
        'nav.employees': 'Employes',
        'nav.vehicles': 'Vehicules',
        'nav.optimization': 'Optimisation',
        'nav.financial': 'Finance',
        'nav.reports': 'Rapports',
        'nav.settings': 'Parametres',
        'auth.logout': 'Deconnexion',
        'auth.login': 'Connexion',
        'auth.email': 'Email',
        'auth.password': 'Mot de passe',
      }
      return translations[key] ?? key
    },
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}))

// Import routes lazily to allow mocks to apply
async function getRouter(initialPath: string) {
  const { router } = await import('../routes')
  return createMemoryRouter(router.routes, {
    initialEntries: [initialPath],
  })
}

describe('Routing', () => {
  it('redirects / to /dashboard', async () => {
    const router = await getRouter('/')
    render(<RouterProvider router={router} />)

    await waitFor(() => {
      expect(screen.getByText('Tableau de bord')).toBeInTheDocument()
    })
  })

  it('renders login page at /login', async () => {
    const router = await getRouter('/login')
    render(<RouterProvider router={router} />)

    await waitFor(() => {
      expect(screen.getByText('Connexion')).toBeInTheDocument()
    })
  })
})
