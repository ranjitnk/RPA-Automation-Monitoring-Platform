import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';
import { LoginPage } from '@/features/auth/pages/LoginPage';
import { DashboardPage } from '@/features/dashboard/pages/DashboardPage';
import { QueuesPage } from '@/features/queues/pages/QueuesPage';
import { JobsPage } from '@/features/jobs/pages/JobsPage';
import { RobotsPage } from '@/features/robots/pages/RobotsPage';
import { AIWorkflowsPage } from '@/features/ai-workflows/pages/AIWorkflowsPage';
import { SLAPage } from '@/features/sla/pages/SLAPage';
import { AuditPage } from '@/features/audit/pages/AuditPage';
import { EnvironmentsPage } from '@/features/environments/pages/EnvironmentsPage';

export const router = createBrowserRouter([
  { path: '/login', element: <LoginPage /> },
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: 'dashboard', element: <DashboardPage /> },
      { path: 'queues', element: <QueuesPage /> },
      { path: 'jobs', element: <JobsPage /> },
      { path: 'robots', element: <RobotsPage /> },
      { path: 'ai-workflows', element: <AIWorkflowsPage /> },
      { path: 'sla', element: <SLAPage /> },
      { path: 'audit', element: <AuditPage /> },
      { path: 'environments', element: <EnvironmentsPage /> },
    ],
  },
]);
