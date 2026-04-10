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

const UnifiedMapPage = lazy(() =>
  import('@/pages/map/UnifiedMapPage').then((m) => ({
    default: m.UnifiedMapPage,
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

const OptimizationHubPage = lazy(() =>
  import('@/pages/optimization/OptimizationHubPage').then((m) => ({
    default: m.OptimizationHubPage,
  }))
);

const OptimizationStopsPage = lazy(() =>
  import('@/pages/optimization/OptimizationStopsPage').then((m) => ({
    default: m.OptimizationStopsPage,
  }))
);

const OptimizationFleetPage = lazy(() =>
  import('@/pages/optimization/OptimizationFleetPage').then((m) => ({
    default: m.OptimizationFleetPage,
  }))
);

const OptimizationRoutesPage = lazy(() =>
  import('@/pages/optimization/OptimizationRoutesPage').then((m) => ({
    default: m.OptimizationRoutesPage,
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

const ScenarioListPage = lazy(() =>
  import('@/pages/scenarios/ScenarioListPage').then((m) => ({
    default: m.ScenarioListPage,
  }))
);

const ScenarioComparePage = lazy(() =>
  import('@/pages/scenarios/ScenarioComparePage').then((m) => ({
    default: m.ScenarioComparePage,
  }))
);

const SettingsPage = lazy(() =>
  import('@/pages/settings/SettingsPage').then((m) => ({
    default: m.SettingsPage,
  }))
);

const ConstraintsPage = lazy(() =>
  import('@/pages/settings/ConstraintsPage').then((m) => ({
    default: m.ConstraintsPage,
  }))
);

const HRDashboardPage = lazy(() =>
  import('@/pages/dashboard/HRDashboardPage').then((m) => ({
    default: m.HRDashboardPage,
  }))
);

const RSEDashboardPage = lazy(() =>
  import('@/pages/dashboard/RSEDashboardPage').then((m) => ({
    default: m.RSEDashboardPage,
  }))
);

const RTIMonitoringDashboard = lazy(() =>
  import('@/pages/dashboard/RTIMonitoringDashboard').then((m) => ({
    default: m.RTIMonitoringDashboard,
  }))
);

const SecurityDashboard = lazy(() =>
  import('@/pages/dashboard/SecurityDashboard').then((m) => ({
    default: m.SecurityDashboard,
  }))
);

const FinancialDashboardPage = lazy(() =>
  import('@/pages/financial/FinancialDashboardPage').then((m) => ({
    default: m.FinancialDashboardPage,
  }))
);

const TCOCalculatorPage = lazy(() =>
  import('@/pages/financial/TCOCalculatorPage').then((m) => ({
    default: m.TCOCalculatorPage,
  }))
);

const ReportListPage = lazy(() =>
  import('@/pages/reports/ReportListPage').then((m) => ({
    default: m.ReportListPage,
  }))
);

const ReportGeneratorPage = lazy(() =>
  import('@/pages/reports/ReportGeneratorPage').then((m) => ({
    default: m.ReportGeneratorPage,
  }))
);

const VehicleListPage = lazy(() =>
  import('@/pages/vehicles/VehicleListPage').then((m) => ({
    default: m.VehicleListPage,
  }))
);

const VehicleCreatePage = lazy(() =>
  import('@/pages/vehicles/VehicleCreatePage').then((m) => ({
    default: m.VehicleCreatePage,
  }))
);

const VehicleDetailPage = lazy(() =>
  import('@/pages/vehicles/VehicleDetailPage').then((m) => ({
    default: m.VehicleDetailPage,
  }))
);

const VehicleEditPage = lazy(() =>
  import('@/pages/vehicles/VehicleEditPage').then((m) => ({
    default: m.VehicleEditPage,
  }))
);

const KmConsommationPage = lazy(() =>
  import('@/pages/fleet/KmConsommationPage').then((m) => ({
    default: m.KmConsommationPage,
  }))
);

const PointArretPage = lazy(() =>
  import('@/pages/fleet/PointArretPage').then((m) => ({
    default: m.PointArretPage,
  }))
);

const ConfigurationTransportPage = lazy(() =>
  import('@/pages/fleet/ConfigurationTransportPage').then((m) => ({
    default: m.ConfigurationTransportPage,
  }))
);

const HoraireTravailPage = lazy(() =>
  import('@/pages/fleet/HoraireTravailPage').then((m) => ({
    default: m.HoraireTravailPage,
  }))
);

const ContentListPage = lazy(() =>
  import('@/pages/content/ContentListPage').then((m) => ({
    default: m.ContentListPage,
  }))
);

const ContentCreatePage = lazy(() =>
  import('@/pages/content/ContentCreatePage').then((m) => ({
    default: m.ContentCreatePage,
  }))
);

const ContentDetailPage = lazy(() =>
  import('@/pages/content/ContentDetailPage').then((m) => ({
    default: m.ContentDetailPage,
  }))
);

const ContentEditPage = lazy(() =>
  import('@/pages/content/ContentEditPage').then((m) => ({
    default: m.ContentEditPage,
  }))
);

const ContentAnalyticsPage = lazy(() =>
  import('@/pages/content/ContentAnalyticsPage').then((m) => ({
    default: m.ContentAnalyticsPage,
  }))
);

const SIRHConnectionsPage = lazy(() =>
  import('@/pages/admin/SIRHConnectionsPage').then((m) => ({
    default: m.SIRHConnectionsPage,
  }))
);

const SIRHSyncDashboardPage = lazy(() =>
  import('@/pages/admin/SIRHSyncDashboardPage').then((m) => ({
    default: m.SIRHSyncDashboardPage,
  }))
);

const DiagnosticDashboardPage = lazy(() =>
  import('@/pages/sotreg/DiagnosticDashboardPage').then((m) => ({
    default: m.DiagnosticDashboardPage,
  }))
);

const LigneListPage = lazy(() =>
  import('@/pages/sotreg/LigneListPage').then((m) => ({
    default: m.LigneListPage,
  }))
);

const LigneFormPage = lazy(() =>
  import('@/pages/sotreg/LigneFormPage').then((m) => ({
    default: m.LigneFormPage,
  }))
);

const TechnologiesDashboardPage = lazy(() =>
  import('@/pages/sotreg/TechnologiesDashboardPage').then((m) => ({
    default: m.TechnologiesDashboardPage,
  }))
);

const InfrastructureDashboardPage = lazy(() =>
  import('@/pages/sotreg/InfrastructureDashboardPage').then((m) => ({
    default: m.InfrastructureDashboardPage,
  }))
);

const AdvancedFinanceDashboardPage = lazy(() =>
  import('@/pages/sotreg/AdvancedFinanceDashboardPage').then((m) => ({
    default: m.AdvancedFinanceDashboardPage,
  }))
);

const OperatorDashboardPage = lazy(() =>
  import('@/pages/operator/OperatorDashboardPage').then((m) => ({
    default: m.OperatorDashboardPage,
  }))
);

const SizingPlanDetailPage = lazy(() =>
  import('@/pages/operator/SizingPlanDetailPage').then((m) => ({
    default: m.SizingPlanDetailPage,
  }))
);

const ReportIssuePage = lazy(() =>
  import('@/pages/operator/ReportIssuePage').then((m) => ({
    default: m.ReportIssuePage,
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
        path: 'map',
        element: (
          <SuspenseWrapper>
            <UnifiedMapPage />
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
        element: <Navigate to="/optimization/stops" replace />,
      },
      {
        path: 'optimization/stops',
        element: (
          <SuspenseWrapper>
            <OptimizationStopsPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'optimization/fleet',
        element: (
          <SuspenseWrapper>
            <OptimizationFleetPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'optimization/routes',
        element: (
          <SuspenseWrapper>
            <OptimizationRoutesPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'optimization/hub',
        element: (
          <SuspenseWrapper>
            <OptimizationHubPage />
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
        path: 'scenarios',
        element: (
          <SuspenseWrapper>
            <ScenarioListPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'scenarios/compare',
        element: (
          <SuspenseWrapper>
            <ScenarioComparePage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'settings',
        element: (
          <SuspenseWrapper>
            <SettingsPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'settings/constraints',
        element: (
          <SuspenseWrapper>
            <ConstraintsPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'dashboard/hr',
        element: (
          <SuspenseWrapper>
            <HRDashboardPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'dashboard/rse',
        element: (
          <SuspenseWrapper>
            <RSEDashboardPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'dashboard/rti',
        element: (
          <SuspenseWrapper>
            <RTIMonitoringDashboard />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'dashboard/security',
        element: (
          <SuspenseWrapper>
            <SecurityDashboard />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'financial',
        element: (
          <SuspenseWrapper>
            <FinancialDashboardPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'financial/tco',
        element: (
          <SuspenseWrapper>
            <TCOCalculatorPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'reports',
        element: (
          <SuspenseWrapper>
            <ReportListPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'reports/generate',
        element: (
          <SuspenseWrapper>
            <ReportGeneratorPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'vehicles',
        element: (
          <SuspenseWrapper>
            <VehicleListPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'vehicles/new',
        element: (
          <SuspenseWrapper>
            <VehicleCreatePage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'vehicles/:id',
        element: (
          <SuspenseWrapper>
            <VehicleDetailPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'vehicles/:id/edit',
        element: (
          <SuspenseWrapper>
            <VehicleEditPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'fleet/consumption',
        element: (
          <SuspenseWrapper>
            <KmConsommationPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'fleet/stops',
        element: (
          <SuspenseWrapper>
            <PointArretPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'fleet/config',
        element: (
          <SuspenseWrapper>
            <ConfigurationTransportPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'fleet/horaires',
        element: (
          <SuspenseWrapper>
            <HoraireTravailPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'content',
        element: (
          <SuspenseWrapper>
            <ContentListPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'content/new',
        element: (
          <SuspenseWrapper>
            <ContentCreatePage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'content/analytics',
        element: (
          <SuspenseWrapper>
            <ContentAnalyticsPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'content/:id',
        element: (
          <SuspenseWrapper>
            <ContentDetailPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'content/:id/edit',
        element: (
          <SuspenseWrapper>
            <ContentEditPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'sotreg',
        element: (
          <SuspenseWrapper>
            <DiagnosticDashboardPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'sotreg/lignes',
        element: (
          <SuspenseWrapper>
            <LigneListPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'sotreg/lignes/new',
        element: (
          <SuspenseWrapper>
            <LigneFormPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'sotreg/lignes/:id/edit',
        element: (
          <SuspenseWrapper>
            <LigneFormPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'sotreg/technologies',
        element: (
          <SuspenseWrapper>
            <TechnologiesDashboardPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'sotreg/infrastructure',
        element: (
          <SuspenseWrapper>
            <InfrastructureDashboardPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'sotreg/finance',
        element: (
          <SuspenseWrapper>
            <AdvancedFinanceDashboardPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'operator',
        element: (
          <SuspenseWrapper>
            <OperatorDashboardPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'operator/plans/:id',
        element: (
          <SuspenseWrapper>
            <SizingPlanDetailPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'operator/report-issue',
        element: (
          <SuspenseWrapper>
            <ReportIssuePage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'admin/sirh',
        element: (
          <SuspenseWrapper>
            <SIRHConnectionsPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'admin/sirh/sync',
        element: (
          <SuspenseWrapper>
            <SIRHSyncDashboardPage />
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
