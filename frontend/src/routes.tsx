import { createBrowserRouter, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';

const LoginPage = lazy(() =>
  import('@/pages/LoginPage').then((m) => ({ default: m.LoginPage }))
);

const DashboardPage = lazy(() =>
  import('@/pages/dashboard/DashboardPage').then((m) => ({
    default: m.DashboardPage,
  }))
);

function SuspenseWrapper({ children }: { children: React.ReactNode }) {
  return (
    <Suspense
      fallback={
        <div className="flex-1 flex items-center justify-center text-on-surface-variant text-sm">
          Chargement...
        </div>
      }
    >
      {children}
    </Suspense>
  );
}

function NotFoundPage() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center gap-2">
      <span className="font-display text-4xl font-bold text-on-surface-variant">
        404
      </span>
      <span className="text-sm text-on-surface-variant">Page introuvable</span>
    </div>
  );
}

export const router = createBrowserRouter([
  {
    path: '/login',
    element: (
      <SuspenseWrapper>
        <LoginPage />
      </SuspenseWrapper>
    ),
  },
  {
    path: '/',
    element: <AppLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: (
          <SuspenseWrapper>
            <DashboardPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: '*',
        element: <NotFoundPage />,
      },
    ],
  },
]);
