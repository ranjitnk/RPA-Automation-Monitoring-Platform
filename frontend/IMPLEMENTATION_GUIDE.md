# React Dashboard - Implementation Checklist & Quick Start

## ✅ Completed Components

### Context & State Management
- ✅ `AuthContext.tsx` - Authentication + RBAC
- ✅ `ThemeContext.tsx` - Dark/light theme toggle
- ✅ `useWebSocket.ts` - Real-time WebSocket support

### API Services
- ✅ `apiClient.ts` - Base HTTP client
- ✅ `jobsService.ts` - Job operations
- ✅ `queuesService.ts` - Queue management
- ✅ `robotsService.ts` - Robot tracking
- ✅ `alertsService.ts` - Alert lifecycle
- ✅ `logsService.ts` - Log search & retrieval
- ✅ `slaService.ts` - SLA metrics
- ✅ `aiMonitoringService.ts` - AI metrics
- ✅ `auditService.ts` - Audit trails

### UI Components
- ✅ `KPICard.tsx` - Metric display with trends
- ✅ `Charts.tsx` - Line, Bar, Pie charts
- ✅ `DataGrid.tsx` - AG Grid wrapper
- ✅ `DataTableFilter.tsx` - Search/filter/export
- ✅ `DrillDownModal.tsx` - Detail modals
- ✅ `AppLayout.tsx` - Main layout + navigation

### Pages
- ✅ `DashboardPage.tsx` - Main dashboard
- ✅ `JobsPage.tsx` - Job management
- ✅ `QueuesPage.tsx` - Queue monitoring
- ✅ `RobotsPage.tsx` - Robot management
- ✅ `LogsPage.tsx` - Log viewer
- ✅ `AIWorkflowsPage.tsx` - AI metrics
- ✅ `AlertsPage.tsx` - Alert management
- ✅ `SLAPage.tsx` - SLA tracking
- ✅ `AuditPage.tsx` - Audit logs
- ✅ `EnvironmentsPage.tsx` - Configuration

### Theme
- ✅ `themeConfig.ts` - Enhanced theme with dark mode

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd frontend
npm install

# Ensure these are installed:
npm install @mui/material @mui/icons-material
npm install ag-grid-react ag-grid-community
npm install recharts
npm install axios
npm install @tanstack/react-query
npm install zustand
npm install react-router-dom
```

### 2. Update Main App Entry

**`frontend/src/main.tsx`:**
```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { CssBaseline } from '@mui/material';
import { RouterProvider } from 'react-router-dom';
import { AuthProvider } from '@/context/AuthContext';
import { ThemeModeProvider } from '@/context/ThemeContext';
import { router } from '@/routes';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-quartz.css';

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AuthProvider>
      <ThemeModeProvider>
        <QueryClientProvider client={queryClient}>
          <CssBaseline />
          <RouterProvider router={router} />
        </QueryClientProvider>
      </ThemeModeProvider>
    </AuthProvider>
  </React.StrictMode>,
);
```

### 3. Update Router Configuration

**`frontend/src/routes/index.tsx`:**
```tsx
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';
import { LoginPage } from '@/features/auth/pages/LoginPage';
import { DashboardPage } from '@/features/dashboard/pages/DashboardPage';
import { JobsPage } from '@/features/jobs/pages/JobsPage';
import { QueuesPage } from '@/features/queues/pages/QueuesPage';
import { RobotsPage } from '@/features/robots/pages/RobotsPage';
import { LogsPage } from '@/features/logs/pages/LogsPage';
import { AIWorkflowsPage } from '@/features/ai-workflows/pages/AIWorkflowsPage';
import { AlertsPage } from '@/features/alerts/pages/AlertsPage';
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
      { path: 'jobs', element: <JobsPage /> },
      { path: 'queues', element: <QueuesPage /> },
      { path: 'robots', element: <RobotsPage /> },
      { path: 'logs', element: <LogsPage /> },
      { path: 'ai-workflows', element: <AIWorkflowsPage /> },
      { path: 'alerts', element: <AlertsPage /> },
      { path: 'sla', element: <SLAPage /> },
      { path: 'audit', element: <AuditPage /> },
      { path: 'environments', element: <EnvironmentsPage /> },
    ],
  },
]);
```

### 4. Configure Environment Variables

**`frontend/.env.local`:**
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_NAME=UiPath Automation Monitor
```

### 5. Start Development Server

```bash
npm run dev

# Visit http://localhost:5173
# Login with any credentials (mock auth)
```

---

## 🔗 Backend Integration Points

### Expected API Endpoints

The backend should provide these endpoints for full integration:

#### Jobs
```
GET    /api/v1/jobs                  # List with pagination
GET    /api/v1/jobs/{id}             # Get details
GET    /api/v1/jobs/export/csv       # Export
```

#### Queues
```
GET    /api/v1/queues                # List
GET    /api/v1/queues/{id}           # Get details
GET    /api/v1/queues/{id}/items     # Get items
GET    /api/v1/queues/stats          # Statistics
```

#### Robots
```
GET    /api/v1/robots                # List
GET    /api/v1/robots/{id}           # Get details
GET    /api/v1/robots/stats          # Statistics
```

#### Logs
```
GET    /api/v1/logs                  # List with pagination
GET    /api/v1/logs/search           # Search logs
GET    /api/v1/logs/job/{jobId}      # Logs by job
GET    /api/v1/logs/export/csv       # Export
```

#### Alerts
```
GET    /api/v1/alerts                # List
GET    /api/v1/alerts/{id}           # Get details
PUT    /api/v1/alerts/{id}/acknowledge
PUT    /api/v1/alerts/{id}/resolve
GET    /api/v1/alerts/stats          # Statistics
```

#### SLA
```
GET    /api/v1/sla                   # List metrics
GET    /api/v1/sla/{id}              # Get details
GET    /api/v1/sla/{id}/history      # Historical data
GET    /api/v1/sla/stats             # Statistics
```

#### AI Monitoring
```
GET    /api/v1/ai-monitoring         # List metrics
GET    /api/v1/ai-monitoring/{id}    # Get details
GET    /api/v1/ai-monitoring/{id}/history
GET    /api/v1/ai-monitoring/anomalies
```

#### Audit
```
GET    /api/v1/audit                 # List with pagination
GET    /api/v1/audit/export/csv      # Export
```

#### Authentication
```
POST   /api/v1/auth/login            # Login
POST   /api/v1/auth/refresh          # Refresh token
```

#### WebSocket
```
WS     /ws/jobs                      # Real-time job updates
WS     /ws/robots                    # Real-time robot status
WS     /ws/alerts                    # Real-time alerts
WS     /ws/queues                    # Real-time queue updates
```

---

## 📊 Data Models Reference

### Job
```ts
interface JobDTO {
  id: number;
  name: string;
  releaseId?: number;
  robotId?: number;
  status: 'Running' | 'Completed' | 'Failed' | 'Stopped' | 'Pending';
  state: string;
  createdTime: string;
  startTime?: string;
  endTime?: string;
  duration?: number;
  inputArguments?: Record<string, unknown>;
  outputArguments?: Record<string, unknown>;
}
```

### Robot
```ts
interface RobotDTO {
  id: number;
  name: string;
  machineId?: number;
  machineName?: string;
  type: 'Attended' | 'Unattended' | 'NonProduction';
  enabled: boolean;
  status: 'Available' | 'Unavailable' | 'Executing';
  username?: string;
  executionSessions: number;
  licenseKey?: string;
  version?: string;
  heartbeatTime?: string;
  jobsCompleted: number;
  jobsFailed: number;
}
```

### Queue
```ts
interface QueueDTO {
  id: number;
  name: string;
  maxRetries: number;
  acceptOrphanedItems: boolean;
  createdTime: string;
  itemCount: number;
  processingCount: number;
  failedCount: number;
  successCount: number;
}
```

### Alert
```ts
interface AlertDTO {
  id: string;
  title: string;
  description: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low' | 'Info';
  status: 'New' | 'Acknowledged' | 'Resolved';
  source: string;
  sourceId?: number;
  createdTime: string;
  resolvedTime?: string;
  metadata?: Record<string, unknown>;
}
```

---

## 🎯 Usage Examples

### Using KPI Card
```tsx
<KPICard
  title="Total Jobs"
  value={2541}
  unit="today"
  trend={12}
  icon={<WorkIcon />}
  progress={94}
  onClick={() => navigate('/jobs')}
/>
```

### Using DataGrid with Filters
```tsx
const [page, setPage] = useState(1);
const [filters, setFilters] = useState({});

return (
  <>
    <DataTableFilter
      onSearch={setSearchQuery}
      onFilter={setFilters}
      filterOptions={[
        {
          key: 'status',
          label: 'Status',
          type: 'select',
          options: [
            { label: 'Completed', value: 'Completed' },
            { label: 'Failed', value: 'Failed' },
          ],
        },
      ]}
    />
    <DataGrid
      columns={columnDefs}
      data={data}
      pagination={{ page, pageSize: 20, total: 500 }}
      onPaginationChange={(newPage, pageSize) => setPage(newPage)}
    />
  </>
);
```

### Using WebSocket for Real-Time Updates
```tsx
const { isConnected, send } = useWebSocket({
  url: '/ws/jobs',
  onMessage: (message) => {
    if (message.type === 'job_completed') {
      refetchJobs();
    }
  },
});
```

### Using Auth Context
```tsx
const { user, hasRole, hasPermission, logout } = useAuth();

if (!hasRole('admin')) {
  return <div>Access Denied</div>;
}

if (!hasPermission('write:all')) {
  return <div>Read-Only Mode</div>;
}
```

### Using Theme Toggle
```tsx
const { mode, toggleTheme } = useThemeMode();

return (
  <IconButton onClick={toggleTheme}>
    {mode === 'light' ? <Brightness4Icon /> : <Brightness7Icon />}
  </IconButton>
);
```

---

## 🧪 Testing

### Unit Tests (Components)
```bash
npm run test

# Run specific test file
npm run test src/components/KPICard.test.tsx

# Watch mode
npm run test -- --watch
```

### E2E Tests (Playwright)
```bash
npm run test:e2e

# UI mode
npm run test:e2e -- --ui

# Single test file
npm run test:e2e src/e2e/dashboard.spec.ts
```

### Linting & Type Checking
```bash
npm run lint

# Fix linting issues
npm run lint -- --fix

# Type checking
npm run typecheck
```

---

## 📦 Build & Deployment

### Development
```bash
npm run dev

# Runs on http://localhost:5173 with hot reload
```

### Production Build
```bash
npm run build

# Output: dist/
# Size analysis
npm run build -- --report
```

### Preview Production Build
```bash
npm run preview

# Runs production build locally
```

### Docker Build
```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY docker/nginx/default.conf /etc/nginx/conf.d/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Build and run:
```bash
docker build -t uipath-monitor-ui:latest .
docker run -p 3000:80 uipath-monitor-ui:latest
```

---

## 🔍 Troubleshooting

### Issue: Components not rendering
**Solution**: Ensure AuthProvider and ThemeModeProvider wrap the app in `main.tsx`

### Issue: AG Grid not showing correctly
**Solution**: Import AG Grid CSS files in `main.tsx`
```tsx
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-quartz.css';
```

### Issue: API calls failing
**Solution**: Check VITE_API_BASE_URL in `.env.local` and CORS headers in backend

### Issue: WebSocket connection refused
**Solution**: Ensure backend WebSocket server is running on same host

### Issue: Theme not persisting
**Solution**: Add localStorage persistence to ThemeContext

---

## 📚 Documentation Files

- **DASHBOARD_GUIDE.md**: Complete feature documentation
- **ARCHITECTURE.md** (in docs/): System architecture
- **PACKAGES.md** (in docs/): Dependency details

---

## 🎉 Success Checklist

- [ ] All dependencies installed
- [ ] `.env.local` configured
- [ ] Development server running (`npm run dev`)
- [ ] Can login with mock credentials
- [ ] Dashboard displays with KPI cards
- [ ] Navigation between pages works
- [ ] Dark/light theme toggle works
- [ ] Data Grid pagination works
- [ ] Search & filter work
- [ ] Export CSV works
- [ ] Drill-down modals open
- [ ] Backend API endpoints responding
- [ ] WebSocket real-time updates work
- [ ] Role-based access control working

---

## 🤝 Support

For issues or questions:
1. Check DASHBOARD_GUIDE.md for feature details
2. Verify backend API endpoints are implemented
3. Check browser console for error messages
4. Ensure all environment variables are set
5. Verify package.json dependencies match requirement

