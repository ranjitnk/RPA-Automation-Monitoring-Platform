import { AgGridReact } from 'ag-grid-react';
import type { ColDef } from 'ag-grid-community';
import { Box } from '@mui/material';

interface DataGridProps<T> {
  rowData: T[];
  columnDefs: ColDef<T>[];
  height?: number;
}

export function DataGrid<T>({ rowData, columnDefs, height = 480 }: DataGridProps<T>) {
  return (
    <Box className="ag-theme-quartz" sx={{ height, width: '100%' }}>
      <AgGridReact rowData={rowData} columnDefs={columnDefs} />
    </Box>
  );
}
