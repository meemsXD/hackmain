import { Navigate, Route, Routes } from 'react-router-dom';
import { AuthGuard } from '@/auth/AuthGuard';
import { RoleGuard } from '@/auth/RoleGuard';
import { useAuth } from '@/auth/useAuth';
import { getDefaultHomePath } from '@/utils/roles';
import { AppLayout } from '@/layouts/AppLayout';
import { LoginPage } from '@/pages/public/LoginPage';
import { RegisterPage } from '@/pages/public/RegisterPage';
import { DriverAccessTokenPage } from '@/pages/public/DriverAccessTokenPage';
import { ProfilePage } from '@/pages/common/ProfilePage';
import { EducatorBatchesPage } from '@/pages/educator/EducatorBatchesPage';
import { EducatorBatchNewPage } from '@/pages/educator/EducatorBatchNewPage';
import { EducatorBatchDetailPage } from '@/pages/educator/EducatorBatchDetailPage';
import { EducatorReportsPage } from '@/pages/educator/EducatorReportsPage';
import { DriverAccessPage } from '@/pages/driver/DriverAccessPage';
import { DriverBatchesPage } from '@/pages/driver/DriverBatchesPage';
import { DriverBatchDetailPage } from '@/pages/driver/DriverBatchDetailPage';
import { ProcessorBatchesPage } from '@/pages/processor/ProcessorBatchesPage';
import { ProcessorBatchDetailPage } from '@/pages/processor/ProcessorBatchDetailPage';
import { ProcessorDriversPage } from '@/pages/processor/ProcessorDriversPage';
import { InspectorJournalPage } from '@/pages/inspector/InspectorJournalPage';
import { InspectorReportsPage } from '@/pages/inspector/InspectorReportsPage';
import { NotFoundPage } from '@/pages/system/NotFoundPage';

function HomeRedirect() {
  const { roles } = useAuth();
  return <Navigate to={getDefaultHomePath(roles)} replace />;
}

export function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/driver-access/:token" element={<DriverAccessTokenPage />} />

      <Route path="/app" element={<AuthGuard />}>
        <Route element={<AppLayout />}>
          <Route index element={<HomeRedirect />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route path="profile/roles" element={<Navigate to="/app/profile" replace />} />

          <Route path="educator" element={<RoleGuard allow={['RECYCLER']} />}>
            <Route path="batches" element={<EducatorBatchesPage />} />
            <Route path="batches/new" element={<EducatorBatchNewPage />} />
            <Route path="batches/add" element={<Navigate to="/app/educator/batches/new" replace />} />
            <Route path="batches/create" element={<Navigate to="/app/educator/batches/new" replace />} />
            <Route path="batches/:id" element={<EducatorBatchDetailPage />} />
            <Route path="reports" element={<EducatorReportsPage />} />
          </Route>

          <Route path="driver" element={<RoleGuard allow={['DRIVER']} />}>
            <Route path="access" element={<DriverAccessPage />} />
            <Route path="batches" element={<DriverBatchesPage />} />
            <Route path="batches/:id" element={<DriverBatchDetailPage />} />
          </Route>

          <Route path="processor" element={<RoleGuard allow={['MEDICAL']} />}>
            <Route path="batches" element={<ProcessorBatchesPage />} />
            <Route path="batches/:id" element={<ProcessorBatchDetailPage />} />
            <Route path="drivers" element={<ProcessorDriversPage />} />
          </Route>

          <Route path="inspector" element={<RoleGuard allow={['INSPECTOR']} />}>
            <Route path="journal" element={<InspectorJournalPage />} />
            <Route path="reports" element={<InspectorReportsPage />} />
          </Route>
        </Route>
      </Route>

      <Route path="/" element={<Navigate to="/app" replace />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}


