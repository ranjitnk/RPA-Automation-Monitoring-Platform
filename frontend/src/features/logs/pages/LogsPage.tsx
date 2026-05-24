import React, { useState, useMemo } from 'react';
import { Box, Stack, Paper, Chip } from '@mui/material';
import { DataGrid } from '@/components/DataGrid';
import { DataTableFilter } from '@/components/DataTableFilter';
import { DrillDownModal } from '@/components/DrillDownModal';
import { ColDef } from 'ag-grid-community';
import { LogEntryDTO } from '@/services/logsService';

const mockLogsData: LogEntryDTO[] = [
  {
    id: '1',
    jobId: 100,
    timestamp: '2025-05-23T14:30:00Z',
    level: 'Info',
    message: 'Job execution started',
    source: 'JobExecutor',
    details: { processId: 'P001' },
  },
  {
    id: '2',
    jobId: 100,
    timestamp: '2025-05-23T14:35:00Z',
    level: 'Error',
    message: 'Database connection timeout',
    source: 'DatabaseService',
    details: { retryCount: 3 },
  },
];

const levelColors: Record<string, string> = {
  Debug: '#9e9e9e',
  Info: '#2196f3',
  Warning: '#ff9800',
  Error: '#f44336',
};

export const LogsPage: React.FC = () => {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [selectedLog, setSelectedLog] = useState<LogEntryDTO | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<Record<string, unknown>>({});

  const columnDefs: ColDef[] = useMemo(
    () => [
      { field: 'id', headerName: 'ID', width: 80 },
      { field: 'timestamp', headerName: 'Time', width: 200 },
      {
        field: 'level',
        headerName: 'Level',
        width: 100,
        cellStyle: (params) => ({
          color: levelColors[params.value] || '#000',
          fontWeight: 600,
        }),
      },
      { field: 'message', headerName: 'Message', flex: 1, minWidth: 300 },
      { field: 'source', headerName: 'Source', width: 150 },
      { field: 'jobId', headerName: 'Job ID', width: 100, type: 'numericColumn' },
      {
        headerName: 'Actions',
        width: 100,
        cellRenderer: (params) => (
          <button onClick={() => setSelectedLog(params.data)}>View</button>
        ),
      },
    ],
    []
  );

  const filteredData = useMemo(
    () =>
      mockLogsData.filter((log) => {
        if (searchQuery) {
          return log.message.toLowerCase().includes(searchQuery.toLowerCase());
        }
        if (filters.level && log.level !== filters.level) return false;
        return true;
      }),
    [searchQuery, filters]
  );

  return (
    <Stack spacing={2}>
      <DataTableFilter
        onSearch={setSearchQuery}
        onFilter={setFilters}
        filterOptions={[
          {
            key: 'level',
            label: 'Log Level',
            type: 'select',
            options: [
              { label: 'Debug', value: 'Debug' },
              { label: 'Info', value: 'Info' },
              { label: 'Warning', value: 'Warning' },
              { label: 'Error', value: 'Error' },
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
        open={!!selectedLog}
        title={`Log Details: ${selectedLog?.id}`}
        data={selectedLog || {}}
        onClose={() => setSelectedLog(null)}
      />
    </Stack>
  );
};
