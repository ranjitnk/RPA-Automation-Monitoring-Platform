import React, { useState } from 'react';
import { AgGridReact } from 'ag-grid-react';
import {
  ColDef,
  GridApi,
  GridReadyEvent,
  PaginationChangedEvent,
} from 'ag-grid-community';
import {
  Box,
  Paper,
  Pagination,
  Stack,
  Typography,
  CircularProgress,
} from '@mui/material';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-quartz.css';

interface DataGridProps {
  columns: ColDef[];
  data: unknown[];
  loading?: boolean;
  pagination?: {
    page: number;
    pageSize: number;
    total: number;
  };
  onPaginationChange?: (page: number, pageSize: number) => void;
  rowHeight?: number;
  enablePagination?: boolean;
  theme?: 'light' | 'dark';
}

export const DataGrid: React.FC<DataGridProps> = ({
  columns,
  data,
  loading = false,
  pagination,
  onPaginationChange,
  rowHeight = 40,
  enablePagination = true,
  theme = 'light',
}) => {
  const [gridApi, setGridApi] = useState<GridApi | null>(null);

  const onGridReady = (event: GridReadyEvent) => {
    setGridApi(event.api);
  };

  const handlePaginationChange = (event: React.ChangeEvent<unknown>, newPage: number) => {
    onPaginationChange?.(newPage, pagination?.pageSize || 20);
  };

  const totalPages = pagination ? Math.ceil(pagination.total / pagination.pageSize) : 1;

  return (
    <Paper sx={{ height: '100%', position: 'relative' }}>
      <Box
        className={`ag-theme-quartz${theme === 'dark' ? '-dark' : ''}`}
        sx={{
          height: enablePagination ? 'calc(100% - 60px)' : '100%',
          width: '100%',
        }}
      >
        {loading && (
          <Box
            sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              zIndex: 10,
            }}
          >
            <CircularProgress />
          </Box>
        )}
        <AgGridReact
          rowData={data}
          columnDefs={columns}
          pagination={false}
          rowHeight={rowHeight}
          onGridReady={onGridReady}
          suppressPaginationPanel={true}
          suppressScrollOnNewData={false}
        />
      </Box>

      {enablePagination && pagination && (
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="center"
          sx={{
            height: 60,
            p: 2,
            borderTop: '1px solid',
            borderColor: 'divider',
          }}
        >
          <Typography variant="caption" color="textSecondary">
            Showing {(pagination.page - 1) * pagination.pageSize + 1} to{' '}
            {Math.min(pagination.page * pagination.pageSize, pagination.total)} of{' '}
            {pagination.total} results
          </Typography>
          <Pagination
            count={totalPages}
            page={pagination.page}
            onChange={handlePaginationChange}
            size="small"
          />
        </Stack>
      )}
    </Paper>
  );
};
