import React, { useState, useMemo } from 'react';
import { Box, Stack, Paper, useTheme, Grid } from '@mui/material';
import { DataGrid } from '@/components/DataGrid';
import { DataTableFilter } from '@/components/DataTableFilter';
import { DrillDownModal } from '@/components/DrillDownModal';
import { ChartBarComponent } from '@/components/Charts';
import { ColDef } from 'ag-grid-community';
import { AlertDTO } from '@/services/alertsService';
import WarningIcon from '@mui/icons-material/Warning';
import ErrorIcon from '@mui/icons-material/Error';
import { KPICard } from '@/components/KPICard';

const mockAlertsData: AlertDTO[] = [
  {
    id: '1',
    title: 'High CPU Usage',
    description: 'Robot CPU usage exceeded 90%',
    severity: 'High',
    status: 'New',
    source: 'Robot',
    sourceId: 5,
    createdTime: '2025-05-23T14:30:00Z',
    metadata: { robotId: 5, robotName: 'Bot-01', cpuUsage: 95 },
  },
  {
    id: '2',
    title: 'Job Failed',
    description: 'Invoice processing job failed',
    severity: 'Critical',
    status: 'Acknowledged',
    source: 'Job',
    sourceId: 100,
    createdTime: '2025-05-23T14:35:00Z',
    metadata: { jobId: 100, error: 'Connection timeout' },
  },
];

const severityColors: Record<string, string> = {
  Critical: '#f44336',
  High: '#ff9800',
  Medium: '#ffc107',
  Low: '#2196f3',
  Info: '#4caf50',
};

const mockSeverityData = [
  { severity: 'Critical', count: 3 },
  { severity: 'High', count: 8 },
  { severity: 'Medium', count: 15 },
  { severity: 'Low', count: 24 },
];

export const AlertsPage: React.FC = () => {
  const theme = useTheme();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [selectedAlert, setSelectedAlert] = useState<AlertDTO | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<Record<string, unknown>>({});

  const columnDefs: ColDef[] = useMemo(
    () => [
      { field: 'id', headerName: 'ID', width: 80 },
      { field: 'title', headerName: 'Title', flex: 1, minWidth: 200 },
      { field: 'description', headerName: 'Description', flex: 1, minWidth: 250 },
      {
        field: 'severity',
        headerName: 'Severity',
        width: 120,
        cellStyle: (params) => ({
          color: severityColors[params.value] || '#000',
          fontWeight: 600,
        }),
      },
      {
        field: 'status',
        headerName: 'Status',
        width: 120,
        cellStyle: (params) => ({
          color: params.value === 'Resolved' ? '#4caf50' : '#ff9800',
        }),
      },
      { field: 'createdTime', headerName: 'Created', width: 180 },
      {
        headerName: 'Actions',
        width: 100,
        cellRenderer: (params) => (
          <button onClick={() => setSelectedAlert(params.data)}>View</button>
        ),
      },
    ],
    []
  );

  const filteredData = useMemo(
    () =>
      mockAlertsData.filter((alert) => {
        if (searchQuery) {
          return alert.title.toLowerCase().includes(searchQuery.toLowerCase());
        }
        if (filters.severity && alert.severity !== filters.severity) return false;
        if (filters.status && alert.status !== filters.status) return false;
        return true;
      }),
    [searchQuery, filters]
  );

  const criticalAlerts = mockAlertsData.filter((a) => a.severity === 'Critical').length;
  const unacknowledged = mockAlertsData.filter((a) => a.status === 'New').length;

  return (
    <Stack spacing={2}>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={4}>
          <KPICard
            title="Critical Alerts"
            value={criticalAlerts}
            icon={<ErrorIcon sx={{ color: 'error.main' }} />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <KPICard
            title="Unacknowledged"
            value={unacknowledged}
            icon={<WarningIcon sx={{ color: 'warning.main' }} />}
          />
        </Grid>
      </Grid>

      <Paper sx={{ p: 2 }}>
        <Box sx={{ mb: 2 }}>Alerts by Severity</Box>
        <ChartBarComponent
          data={mockSeverityData}
          xAxisKey="severity"
          bars={[{ key: 'count', fill: theme.palette.primary.main }]}
          height={250}
        />
      </Paper>

      <DataTableFilter
        onSearch={setSearchQuery}
        onFilter={setFilters}
        filterOptions={[
          {
            key: 'severity',
            label: 'Severity',
            type: 'select',
            options: [
              { label: 'Critical', value: 'Critical' },
              { label: 'High', value: 'High' },
              { label: 'Medium', value: 'Medium' },
              { label: 'Low', value: 'Low' },
            ],
          },
          {
            key: 'status',
            label: 'Status',
            type: 'select',
            options: [
              { label: 'New', value: 'New' },
              { label: 'Acknowledged', value: 'Acknowledged' },
              { label: 'Resolved', value: 'Resolved' },
            ],
          },
        ]}
      />

      <Paper sx={{ height: 600 }}>
        <DataGrid
          columns={columnDefs}
          data={filteredData}
          pagination={{ page, pageSize, total: filteredData.length }}
          onPaginationChange={(newPage, newPageSize) => {
            setPage(newPage);
            setPageSize(newPageSize);
          }}
        />
      </Paper>

      <DrillDownModal
        open={!!selectedAlert}
        title={`Alert Details: ${selectedAlert?.title}`}
        data={selectedAlert || {}}
        onClose={() => setSelectedAlert(null)}
      />
    </Stack>
  );
};
