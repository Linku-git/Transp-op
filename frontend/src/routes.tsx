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

const SiteListPage = lazy(() =>
  import('@/pages/sites/SiteListPage').then((m) => ({
    default: m.SiteListPage,
  }))
);

const SiteCreatePage = lazy(() =>
  import('@/pages/sites/SiteCreatePage').then((m) => ({
    default: m.SiteCreatePage,
  }))
);

const SiteDetailPage = lazy(() =>
  import('@/pages/sites/SiteDetailPage').then((m) => ({
    default: m.SiteDetailPage,
  }))
);

const SiteEditPage = lazy(() =>
  import('@/pages/sites/SiteEditPage').then((m) => ({
    default: m.SiteEditPage,
  }))
);

const EmployeeListPage = lazy(() =>
  import('@/pages/employees/EmployeeListPage').then((m) => ({
    default: m.EmployeeListPage,
  }))
);

const EmployeeCreatePage = lazy(() =>
  import('@/pages/employees/EmployeeCreatePage').then((m) => ({
    default: m.EmployeeCreatePage,
  }))
);

const EmployeeDetailPage = lazy(() =>
  import('@/pages/employees/EmployeeDetailPage').then((m) => ({
    default: m.EmployeeDetailPage,
  }))
);

const EmployeeEditPage = lazy(() =>
  import('@/pages/employees/EmployeeEditPage').then((m) => ({
    default: m.EmployeeEditPage,
  }))
);

const EmployeeMapPage = lazy(() =>
  import('@/pages/employees/EmployeeMapPage').then((m) => ({
    default: m.EmployeeMapPage,
  }))
);

const ExcelImportPage = lazy(() =>
  import('@/pages/import/ExcelImportPage').then((m) => ({
    default: m.ExcelImportPage,
  }))
);

const ModalAnalysisPage = lazy(() =>
  import('@/pages/modal/ModalAnalysisPage').then((m) => ({
    default: m.ModalAnalysisPage,
  }))
);

const OptimizationPage = lazy(() =>
  import('@/pages/optimization/OptimizationPage').then((m) => ({
    default: m.OptimizationPage,
  }))
);

const OptimizationResultPage = lazy(() =>
  import('@/pages/optimization/OptimizationResultPage').then((m) => ({
    default: m.OptimizationResultPage,
  }))
);

const OptimizationHistoryPage = lazy(() =>
  import('@/pages/optimization/OptimizationHistoryPage').then((m) => ({
    default: m.OptimizationHistoryPage,
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
        path: 'sites',
        element: (
          <SuspenseWrapper>
            <SiteListPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'sites/new',
        element: (
          <SuspenseWrapper>
            <SiteCreatePage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'sites/:id',
        element: (
          <SuspenseWrapper>
            <SiteDetailPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'sites/:id/edit',
        element: (
          <SuspenseWrapper>
            <SiteEditPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'employees',
        element: (
          <SuspenseWrapper>
            <EmployeeListPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'employees/new',
        element: (
          <SuspenseWrapper>
            <EmployeeCreatePage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'employees/map',
        element: (
          <SuspenseWrapper>
            <EmployeeMapPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'employees/:id',
        element: (
          <SuspenseWrapper>
            <EmployeeDetailPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'employees/:id/edit',
        element: (
          <SuspenseWrapper>
            <EmployeeEditPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'import',
        element: (
          <SuspenseWrapper>
            <ExcelImportPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'modal-analysis',
        element: (
          <SuspenseWrapper>
            <ModalAnalysisPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'optimization',
        element: (
          <SuspenseWrapper>
            <OptimizationPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'optimization/history',
        element: (
          <SuspenseWrapper>
            <OptimizationHistoryPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'optimization/:id',
        element: (
          <SuspenseWrapper>
            <OptimizationResultPage />
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
