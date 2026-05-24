# Modern Enterprise React Dashboard - UiPath Monitoring

## 📋 Overview

A production-grade React dashboard for UiPath automation monitoring with Material-UI, AG Grid, Recharts, and real-time WebSocket support.

---

## 📁 Folder Structure

```
frontend/src/
├── components/
│   ├── KPICard.tsx                 # KPI metric card component
│   ├── Charts.tsx                  # Recharts components (Line, Bar, Pie)
│   ├── DataGrid.tsx                # AG Grid wrapper with pagination
│   ├── DataTableFilter.tsx         # Search, filter, export controls
│   ├── DrillDownModal.tsx          # Detail view modal
│   └── layout/
│       └── AppLayout.tsx           # Main layout with sidebar, header
│
├── context/
│   ├── AuthContext.tsx             # Authentication state + RBAC
│   └── ThemeContext.tsx            # Dark/light theme toggle
│
├── hooks/
│   └── useWebSocket.ts             # Real-time WebSocket hook
│
├── services/
│   ├── apiClient.ts                # Axios API client
│   ├── jobsService.ts              # Jobs API service
│   ├── queuesService.ts            # Queues API service
│   ├── robotsService.ts            # Robots API service
│   ├── alertsService.ts            # Alerts API service
│   ├── logsService.ts              # Logs API service
│   ├── slaService.ts               # SLA API service
│   ├── auditService.ts             # Audit logs API service
│   └── aiMonitoringService.ts      # AI metrics API service
│
├── theme/
│   ├── themeConfig.ts              # Theme configuration
│   └── index.ts                    # (existing)
│
├── features/
│   ├── dashboard/pages/
│   │   └── DashboardPage.tsx       # Main dashboard with KPIs + charts
│   ├── jobs/pages/
│   │   └── JobsPage.tsx            # Job management and tracking
│   ├── queues/pages/
│   │   └── QueuesPage.tsx          # Queue monitoring
│   ├── robots/pages/
│   │   └── RobotsPage.tsx          # Robot status and management
│   ├── logs/pages/
│   │   └── LogsPage.tsx            # Execution logs with search
│   ├── ai-workflows/pages/
│   │   └── AIWorkflowsPage.tsx     # AI metrics and monitoring
│   ├── alerts/pages/
│   │   └── AlertsPage.tsx          # Alert management
│   ├── sla/pages/
│   │   └── SLAPage.tsx             # SLA tracking and metrics
│   ├── audit/pages/
│   │   └── AuditPage.tsx           # Audit trail logging
│   ├── environments/pages/
│   │   └── EnvironmentsPage.tsx    # Orchestrator configuration
│   └── auth/pages/
│       └── LoginPage.tsx           # (existing)
│
├── routes/
│   └── index.tsx                   # React Router configuration
│
├── stores/
│   ├── authStore.ts                # (existing)
│   └── environmentStore.ts         # (existing)
│
├── api/
│   ├── client.ts                   # (existing)
│   └── websocket.ts                # (existing)
│
├── main.tsx                        # App entry point
└── App.tsx                         # (existing)
```

---

## 🎨 Key Components

### 1. **KPICard** (`KPICard.tsx`)
- Metric display with trend indicators
- Progress bars
- Color-coded status
- Click handlers for drill-down

**Usage:**
```tsx
<KPICard
  title="Total Jobs"
  value={2541}
  unit="today"
  trend={12}
  icon={<WorkIcon />}
  progress={94.5}
  onClick={() => navigate('/jobs')}
/>
```

### 2. **Charts** (`Charts.tsx`)
- **ChartLineComponent**: Time-series line charts
- **ChartBarComponent**: Categorical bar charts
- **ChartPieComponent**: Distribution pie charts
- Theme-aware colors and responsive sizing

**Usage:**
```tsx
<ChartLineComponent
  data={data}
  xAxisKey="month"
  lines={[
    { key: 'completed', name: 'Completed', stroke: '#4caf50' },
  ]}
  height={300}
/>
```

### 3. **DataGrid** (`DataGrid.tsx`)
- AG Grid integration with column definitions
- Built-in pagination
- Loading states
- Responsive layout
- Dark/light theme support

**Usage:**
```tsx
<DataGrid
  columns={columnDefs}
  data={data}
  pagination={{ page, pageSize, total }}
  onPaginationChange={handlePaginationChange}
/>
```

### 4. **DataTableFilter** (`DataTableFilter.tsx`)
- Global search across all columns
- Advanced filtering with dropdowns
- CSV export functionality
- Active filter chips with clear buttons

**Usage:**
```tsx
<DataTableFilter
  onSearch={setSearchQuery}
  onFilter={setFilters}
  onExport={handleExport}
  filterOptions={[
    {
      key: 'status',
      label: 'Status',
      type: 'select',
      options: [...],
    },
  ]}
/>
```

### 5. **DrillDownModal** (`DrillDownModal.tsx`)
- Detailed view of selected records
- JSON rendering for complex data
- Boolean and array formatting
- Full-screen capable

### 6. **AppLayout** (`layout/AppLayout.tsx`)
- Responsive sidebar navigation
- Mobile-friendly drawer
- Top app bar with search, notifications, theme toggle
- User profile menu
- Role-based navigation

---

## 🔐 Authentication & Authorization

### **AuthContext** (`context/AuthContext.tsx`)

**Features:**
- User authentication state management
- JWT token storage
- Role-based access control (RBAC)
- Permission checking

**Roles:**
- `admin`: Full access (read, write, delete, manage users)
- `manager`: Read/write + manage alerts/jobs
- `user`: Read/write own + manage own resources
- `viewer`: Read-only access

**Usage:**
```tsx
const { user, hasRole, hasPermission, login, logout } = useAuth();

if (!hasRole('admin')) return <AccessDenied />;
if (!hasPermission('write:all')) return <ReadOnly />;
```

---

## 🌓 Theme Management

### **ThemeContext** (`context/ThemeContext.tsx`)

**Features:**
- Light/dark theme toggle
- Persistent theme selection
- Material-UI theme integration
- Custom color palette

**Theme Colors:**
- Primary: `#0067DF` (light), `#4DA6FF` (dark)
- Secondary: `#FA4616` (orange accent)
- Status: Success, Warning, Error, Info

**Usage:**
```tsx
const { mode, toggleTheme } = useThemeMode();

return (
  <IconButton onClick={toggleTheme}>
    {mode === 'light' ? <Brightness4Icon /> : <Brightness7Icon />}
  </IconButton>
);
```

---

## 🔌 API Services

### **ApiClient** (`services/apiClient.ts`)

Base client with request/response handling:
```tsx
apiClient.get('/endpoint', { filters, page, pageSize });
apiClient.post('/endpoint', data);
apiClient.put('/endpoint', data);
apiClient.delete('/endpoint');
apiClient.getPaginated('/endpoint', page, pageSize, filters, sort);
```

### **Service Pattern**

Each module has a dedicated service:
- `jobsService`: Job CRUD + export
- `queuesService`: Queue management + stats
- `robotsService`: Robot tracking + status
- `alertsService`: Alert lifecycle (acknowledge, resolve)
- `logsService`: Log retrieval + search
- `slaService`: SLA metrics + history
- `aiMonitoringService`: ML metrics + anomalies
- `auditService`: Audit trail + user activity

**DTOs (Type-Safe Models):**
```tsx
interface JobDTO {
  id: number;
  name: string;
  status: 'Running' | 'Completed' | 'Failed' | 'Stopped' | 'Pending';
  state: string;
  createdTime: string;
  duration?: number;
  inputArguments?: Record<string, unknown>;
  outputArguments?: Record<string, unknown>;
}
```

---

## 📊 Pages

### **Dashboard** (`DashboardPage.tsx`)
- 6 KPI cards (Jobs, Success Rate, Robots, Queues, Alerts, System Health)
- Job execution trend (line chart)
- Robot status distribution (pie chart)
- Queue processing status (bar chart)
- Recent jobs & alerts cards

### **Jobs** (`JobsPage.tsx`)
- AG Grid with 8 columns (ID, Name, State, Status, etc.)
- Search + filter by status
- Drill-down modal with full job details
- CSV export
- Pagination support

### **Queues** (`QueuesPage.tsx`)
- Queue list with item counts
- Pending/processing/successful breakdown
- Max retries configuration
- Alert banner with aggregate stats

### **Robots** (`RobotsPage.tsx`)
- Robot inventory with machine mapping
- Status indicators (Available/Executing/Unavailable)
- Session count tracking
- Job statistics per robot
- Multi-filter support (status, type)

### **Logs** (`LogsPage.tsx`)
- High-performance log viewer
- Level filtering (Debug, Info, Warning, Error)
- 50 items per page (larger dataset)
- Global search
- Syntax-highlighted drill-down

### **AI Workflows** (`AIWorkflowsPage.tsx`)
- Accuracy & confidence metrics
- Performance KPIs (precision, recall, F1)
- Anomaly detection tracking
- 5-day trend chart
- Status indicators (Normal/Degraded/Anomaly)

### **Alerts** (`AlertsPage.tsx`)
- Severity-based color coding
- Status workflow (New → Acknowledged → Resolved)
- Critical alert KPI counter
- Distribution by severity (bar chart)
- Quick acknowledgment/resolution actions

### **SLA** (`SLAPage.tsx`)
- Process-level SLA tracking
- Success rate monitoring
- Average processing time vs. target
- 4-week compliance trend
- Status indicators (On Track/At Risk/Breached)

### **Audit Logs** (`AuditPage.tsx`)
- User action history
- Resource change tracking (delta view)
- IP address logging
- Multi-filter (action, resource)
- 50-item default page size

### **Environments** (`EnvironmentsPage.tsx`)
- Orchestrator connection management
- Connection test endpoint
- Data sync triggers
- Last sync timestamp tracking
- Add/edit environment form

---

## 🔄 WebSocket Support

### **useWebSocket** (`hooks/useWebSocket.ts`)

Real-time data updates:
```tsx
const { isConnected, send } = useWebSocket({
  url: '/ws/jobs',
  onMessage: (message) => updateJobData(message),
  reconnect: true,
  reconnectInterval: 3000,
});

// Send real-time filters
send({ type: 'filter', data: { status: 'Running' } });
```

**Message Format:**
```tsx
interface WebSocketMessage<T> {
  type: string;
  data: T;
  timestamp: number;
}
```

---

## 🔑 Features Summary

| Feature | Implementation |
|---------|-----------------|
| **Dark/Light Theme** | ThemeContext + Material-UI |
| **Responsive Layout** | MUI Grid + useMediaQuery |
| **Data Pagination** | AG Grid + custom pagination |
| **Search & Filter** | DataTableFilter + API params |
| **Export CSV** | Blob generation + download |
| **Drill-Down Modals** | DrillDownModal component |
| **Real-Time Updates** | useWebSocket hook |
| **Charts & Analytics** | Recharts library |
| **Role-Based Access** | AuthContext + RBAC system |
| **Global Error Handling** | API client error boundaries |
| **Mobile Responsive** | MUI breakpoints + drawer |

---

## 🚀 Getting Started

### Setup

```bash
cd frontend

# Install dependencies
npm install

# Environment variables
cp .env.example .env.local
# Edit VITE_API_BASE_URL=http://localhost:8000/api/v1

# Start dev server
npm run dev

# Build for production
npm run build

# Type checking
npm run lint
```

### Configuration

**Backend Integration** (`frontend/.env.local`):
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_NAME=UiPath Monitor
```

---

## 📦 Dependencies

```json
{
  "dependencies": {
    "@mui/material": "^6.1.9",
    "@mui/icons-material": "^6.1.9",
    "@emotion/react": "^11.13.5",
    "@emotion/styled": "^11.13.5",
    "ag-grid-react": "^32.3.3",
    "ag-grid-community": "^32.3.3",
    "recharts": "^2.14.1",
    "react-router-dom": "^6.28.0",
    "@tanstack/react-query": "^5.62.2",
    "zustand": "^5.0.2",
    "axios": "^1.7.9",
    "jwt-decode": "^4.0.0"
  }
}
```

---

## 🔗 API Integration

**Expected Backend Endpoints:**

```
GET  /api/v1/jobs                    # List jobs with pagination
GET  /api/v1/jobs/{id}               # Get job details
GET  /api/v1/queues                  # List queues
GET  /api/v1/queues/{id}/items       # Get queue items
GET  /api/v1/robots                  # List robots
GET  /api/v1/logs                    # Get logs with search
GET  /api/v1/sla                     # SLA metrics
GET  /api/v1/alerts                  # List alerts
PUT  /api/v1/alerts/{id}/acknowledge # Acknowledge alert
GET  /api/v1/ai-monitoring           # AI metrics
GET  /api/v1/audit                   # Audit logs
POST /api/v1/auth/login              # User login
WS   /ws/jobs                        # Real-time job updates
WS   /ws/alerts                      # Real-time alerts
```

---

## 🎯 Best Practices

1. **Type Safety**: All DTOs are fully typed with Pydantic equivalents
2. **Error Handling**: Global API error handler with user feedback
3. **Performance**: Lazy loading, memoization, pagination
4. **Accessibility**: ARIA labels, keyboard navigation
5. **Responsive**: Mobile-first design with breakpoint-based layouts
6. **Security**: JWT tokens, RBAC, XSS protection
7. **Caching**: React Query for intelligent caching
8. **Real-Time**: WebSocket with auto-reconnect

---

## 📈 Scalability Considerations

- **Large Datasets**: AG Grid handles 10K+ rows with virtualization
- **Real-Time**: WebSocket connection pooling recommended
- **Caching**: React Query with stale-while-revalidate
- **State Management**: Zustand for lightweight global state
- **Code Splitting**: Route-based lazy loading

---

## 🔒 Security

- **JWT Authentication**: Stored in localStorage (consider secure httpOnly cookies)
- **RBAC**: Role-based access control with permission checks
- **CORS**: Configured in backend via environment
- **API Rate Limiting**: Implement on backend
- **Input Validation**: Pydantic schemas on backend enforce types
- **XSS Protection**: React's built-in escaping + Content Security Policy

---

## 📝 Notes

- All services follow the repository pattern for consistency
- Components are fully reusable and composable
- Theme supports both light and dark modes with proper contrast
- Pagination defaults to 20 items (except logs at 50, audit at 50)
- Modal drill-downs auto-format nested JSON
- WebSocket messages include timestamp for ordering
- Export generates CSV with headers from column definitions

